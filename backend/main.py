from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from PIL import Image
import json
import io
import os
from dotenv import load_dotenv

from db.database import init_db
from routes import building
from routes import image
from fastapi.staticfiles import StaticFiles

load_dotenv()

app = FastAPI(title="Building Analyzer API")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this once you know your frontend's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(building.router)
app.include_router(image.router)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-3.5-flash-lite")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def home():
    return {"message": "Hello World!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/analyze")
async def analyze_building(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes))

    prompt = """Analyze this photo of an apartment building. Based on visible cues 
    (architecture style, condition, materials, signage, surroundings), return ONLY 
    a JSON object with these fields: estimated_age, condition_notes, building_type, 
    notable_features, estimated_neighborhood_class. Be clear this is a visual 
    estimate, not verified data."""

    response = model.generate_content([prompt, image])

    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()

    data = json.loads(text)
    return data