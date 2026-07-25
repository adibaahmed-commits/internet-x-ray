# services/gemini_service.py
"""
Interface contract for building image analysis.

TODO(ai-team): replace the body of analyze_building_image() with the real
Gemini call. Keep the function signature and return shape exactly as-is —
the rest of the backend (routes/building.py) is built against this contract.
"""

class BuildingAnalysisError(Exception):
    """Raised when analysis fails after retries are exhausted."""
    pass


def analyze_building_image(image_path: str) -> dict:
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
            "condition": str,           # "excellent" | "good" | "fair" | "poor"
            "exterior_material": str | None,
            "notable_features": list[str],
            "architectural_style": str | None,
            "confidence": str,          # "high" | "medium" | "low"
            "summary": str,
        }

    Raises:
        BuildingAnalysisError: if analysis fails after retries.
    """
    # --- STUB IMPLEMENTATION (placeholder until AI side is wired in) ---
    return {
        "building_type": "mid-rise apartment building",
        "estimated_year_built": "1990-2000",
        "estimated_stories": 5,
        "condition": "good",
        "exterior_material": "brick",
        "notable_features": ["balconies", "flat roof"],
        "architectural_style": "unclear",
        "confidence": "medium",
        "summary": "This is placeholder analysis data for backend testing.",
    }
if __name__ == "__main__":
    result = analyze_building_image("some/fake/path.jpg")
    print(result)
    assert "condition" in result
    assert "notable_features" in result