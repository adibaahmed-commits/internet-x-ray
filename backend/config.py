import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./buildings.db")
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not set in .env")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)