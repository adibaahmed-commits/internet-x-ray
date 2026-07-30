<<<<<<< HEAD
import os
import json
=======
"""
Interface contract for building image analysis.
TODO(ai-team): replace the body of analyze_building_image() with the real
Gemini call. Keep the function signature and return shape exactly as-is —
the rest of the backend (routes/building.py) is built against this contract.
"""
>>>>>>> 6fde5cb43ddefcedb1337b0be8611f8619136638
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

If the image does not clearly show a building, still return this shape,
setting confidence to "low" and explaining in summary.
"""


def analyze_building_image(image_path: str) -> dict:
<<<<<<< HEAD
=======
    """
    Analyze a building image and return structured data.
    Args:
        image_path: path to the stored image file on disk.
    Returns:
        dict matching this shape:
        {
            "building_type": str,
            "estimated_year_built": str,
            "estimated_stories": int | None,
            "condition": str,           # "excellent" | "good"| "fair" | "poor"
            "notable_features": list[str],
            "architectural_style": str | None,
            "estimated_rental_price": str | None,   # e.g. "₹35,000-₹45,000/mo"
            "visible_amenities": list[str],         # e.g. ["parking", "balconies"]
            "nearby_hospitals": list[str],          # e.g. ["City Hospital - 1.2km"]
            "nearby_schools": list[str],            # e.g. ["DPS School - 0.8km"]
            "network_coverage": str | None,         # e.g. "Jio, Airtel - Strong"
            "confidence": str,          # "high" | "medium" | "low"
            "summary": str,
        }
    Raises:
        BuildingAnalysisError: if analysis fails after retries.
    """
>>>>>>> 6fde5cb43ddefcedb1337b0be8611f8619136638
    logger.info(f"Gemini analysis started for image_path={image_path}")
    try:
<<<<<<< HEAD
        uploaded_file = client.files.upload(file=image_path)
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=[PROMPT, uploaded_file],
        )

        raw_text = response.text.strip()

        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError:
            logger.error(f"Gemini returned non-JSON response: {raw_text}")
            raise BuildingAnalysisError("Gemini did not return valid JSON")

        required_fields = [
            "building_type", "estimated_year_built", "estimated_stories",
            "condition", "exterior_material", "notable_features",
            "architectural_style", "estimated_rental_price",
            "visible_amenities", "confidence", "summary"
        ]
        missing = [f for f in required_fields if f not in data]
        if missing:
            logger.error(f"Gemini response missing fields: {missing}")
            raise BuildingAnalysisError(f"Missing fields in response: {missing}")

        return data

    except BuildingAnalysisError:
        raise
=======
        result = {
            "building_type": "mid-rise apartment building",
            "estimated_year_built": "1990-2000",
            "estimated_stories": 5,
            "condition": "good",
            "notable_features": ["balconies", "flat roof"],
            "architectural_style": "unclear",
            "estimated_rental_price": "₹35,000-₹45,000/mo",
            "visible_amenities": ["parking", "balconies"],
            "nearby_hospitals": ["City Hospital - 1.2km", "Apollo Clinic - 2.5km"],
            "nearby_schools": ["DPS School - 0.8km", "St. Mary's School - 1.5km"],
            "network_coverage": "Jio, Airtel - Strong",
            "confidence": "medium",
            "summary": "This is placeholder analysis data for backend testing.",
        }
        logger.info(f"Gemini analysis succeeded for image_path={image_path}, confidence={result['confidence']}")
        return result
>>>>>>> 6fde5cb43ddefcedb1337b0be8611f8619136638
    except Exception as e:
        logger.error(f"Gemini analysis failed: {e}")
        raise BuildingAnalysisError(f"Failed to analyze image: {e}")
