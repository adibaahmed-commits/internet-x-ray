import google.generativeai as genai
from PIL import Image
import json
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("AQ.Ab8RN6J4EwsuFlpI0aC_3x5RB9EZ4uaCmKlzritXDKqhaW2-Mg"))
model = genai.GenerativeModel("gemini-3.5-flash-lite")

image = Image.open("building.jpg.png")

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
print(data)
