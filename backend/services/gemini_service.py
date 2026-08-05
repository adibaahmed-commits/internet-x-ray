import os
import json
import time
import logging
from dotenv import load_dotenv
from google import genai

load_dotenv()

logger = logging.getLogger(__name__)

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


class BuildingAnalysisError(Exception):
    pass


PROMPT = """
You are analyzing an image for a construction/building assessment app.

Return ONLY valid JSON (no backticks, no extra text) matching exactly this shape:

{
  "building_type": string,
  "estimated_year_built": string,
  "estimated_stories": integer or null,
  "condition": "excellent" | "good" | "fair" | "poor",
  "exterior_material": string or null,
  "notable_features": list of strings,
  "architectural_style": string or null,
  "estimated_rental_price": string or null,
  "visible_amenities": list of strings,
  "confidence": "high" | "medium" | "low",
  "summary": string
}

"estimated_rental_price": string or null,
  "visible_amenities": list of strings,
  "confidence": "high" | "medium" | "low",
  "summary": string
}

All monetary estimates (such as estimated_rental_price) must be given in
Indian Rupees, formatted like "₹15,000/month". Do not use dollars or any
other currency.

If the image does not clearly show a building, still return this shape,
setting confidence to "low" and explaining in summary.
"""
REQUIRED_FIELDS = [
    "building_type", "estimated_year_built", "estimated_stories",
    "condition", "exterior_material", "notable_features",
    "architectural_style", "estimated_rental_price",
    "visible_amenities", "confidence", "summary"
]

MAX_ATTEMPTS = 5


def _is_transient(error: Exception) -> bool:
    msg = str(error)
    return "UNAVAILABLE" in msg or "503" in msg or "overloaded" in msg.lower()


def analyze_building_image(image_path: str) -> dict:
    logger.info(f"Gemini analysis started for image_path={image_path}")
    last_error = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            uploaded_file = client.files.upload(file=image_path)
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=[PROMPT, uploaded_file],
            )

            raw_text = response.text.strip()

            try:
                data = json.loads(raw_text)
            except json.JSONDecodeError:
                logger.error(f"Gemini returned non-JSON response: {raw_text}")
                raise BuildingAnalysisError("Gemini did not return valid JSON")

            missing = [f for f in REQUIRED_FIELDS if f not in data]
            if missing:
                logger.error(f"Gemini response missing fields: {missing}")
                raise BuildingAnalysisError(f"Missing fields in response: {missing}")

            return data

        except BuildingAnalysisError:
            raise
        except Exception as e:
            last_error = e
            if _is_transient(e) and attempt < MAX_ATTEMPTS:
                wait = 2 ** (attempt - 1)  # 1s, 2s, 4s
                logger.warning(
                    f"Gemini transient error (attempt {attempt}/{MAX_ATTEMPTS}), "
                    f"retrying in {wait}s: {e}"
                )
                time.sleep(wait)
                continue
            logger.error(f"Gemini analysis failed: {e}")
            raise BuildingAnalysisError(f"Failed to analyze image: {e}")

    raise BuildingAnalysisError(f"Failed to analyze image after retries: {last_error}")