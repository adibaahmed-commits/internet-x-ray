import os
import logging
from google import genai

logger = logging.getLogger(__name__)

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


def answer_building_question(analysis_json: dict, question: str) -> str:
    prompt = f"""
You are a helpful assistant answering questions about a specific building,
based only on the analysis data below. Be concise and direct. If the data
doesn't cover something, say so honestly instead of guessing.

Building analysis data:
{analysis_json}

User question: {question}
"""
    logger.info("Chat request received for building")
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[prompt],
    )
    return response.text.strip()