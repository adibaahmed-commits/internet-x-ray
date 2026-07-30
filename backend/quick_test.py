from services.gemini_service import analyze_building_image
import json

image_path = "test_building.jpg"  # change this to your photo's filename

result = analyze_building_image(image_path)
print(json.dumps(result, indent=2))