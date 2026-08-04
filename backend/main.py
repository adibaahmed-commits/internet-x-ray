from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from db.database import init_db
from routes import building
from routes import image
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from fastapi import UploadFile, File, HTTPException
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import io
import json
import os
import google.generativeai as genai

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("uvicorn.error")


def get_gps_from_image(image_bytes):
    """Extracts Latitude and Longitude from image EXIF data."""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        exif_data = image._getexif()

        if not exif_data:
            return None

        gps_info = None
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == "GPSInfo":
                gps_info = value
                break

        if not gps_info:
            return None

        def convert_to_degrees(value):
            d, m, s = value
            return d + (m / 60.0) + (s / 3600.0)

        lat = None
        lon = None

        if 'GPSLatitude' in gps_info and 'GPSLatitudeRef' in gps_info:
            lat = convert_to_degrees(gps_info['GPSLatitude'])
            if gps_info['GPSLatitudeRef'] != 'N':
                lat = -lat

        if 'GPSLongitude' in gps_info and 'GPSLongitudeRef' in gps_info:
            lon = convert_to_degrees(gps_info['GPSLongitude'])
            if gps_info['GPSLongitudeRef'] != 'E':
                lon = -lon

        if lat is not None and lon is not None:
            return {"latitude": lat, "longitude": lon}
        return None
    except Exception as e:
        logger.error(f"Error reading GPS: {e}")
        return None


app = FastAPI(title="Building Analyzer API")

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://super-babka-6aa76c.netlify.app",
        "https://celebrated-biscotti-f91d69.netlify.app",
        "https://adibaahmed-commits.github.io",   # GitHub Pages frontend
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(building.router)
app.include_router(image.router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"error": "Invalid request data", "details": exc.errors()})


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def home():
    return {"message": "Hello World!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/analyze-with-gps")
async def analyze_with_gps(file: UploadFile = File(...)):
    # 1. Read image bytes
    contents = await file.read()

    # 2. Extract GPS
    gps_data = get_gps_from_image(contents)

    # 3. Configure Gemini
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Gemini API Key missing in backend")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # 4. Build Prompt
    if gps_data:
        location_context = f"This photo was taken at GPS Coordinates: Latitude {gps_data['latitude']}, Longitude {gps_data['longitude']}."
    else:
        location_context = "No GPS data found in this image. Please rely ONLY on visual clues (signs, landmarks) visible in the picture."

    prompt = f"""
    {location_context}

    Analyze this image to identify nearby facilities.
    Return a STRICT JSON object with no markdown formatting, no code blocks, just raw JSON.
    Format:
    {{
        "schools": ["Name of nearest school visible or inferred"],
        "hospitals": ["Name of nearest hospital visible or inferred"],
        "shopping_centers": ["Name of nearest shopping center visible or inferred"]
    }}
    If nothing is found for a category, return an empty list [].
    """

    try:
        # 5. Send to Gemini
        response = model.generate_content([prompt, contents])
        text = response.text.strip()

        # Clean up markdown if Gemini adds it anyway
        if text.startswith("```json"):
            text = text.replace("```json", "").replace("```", "")
        if text.startswith("```"):
            text = text.replace("```", "")

        result = json.loads(text)
        return result

    except Exception as e:
        logger.error(f"Gemini Error: {e}")
        raise HTTPException(status_code=500, detail=f"AI Analysis failed: {str(e)}")