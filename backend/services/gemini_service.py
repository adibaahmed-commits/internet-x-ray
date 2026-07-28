"""
Interface contract for building image analysis.
TODO(ai-team): replace the body of analyze_building_image() with the real
Gemini call. Keep the function signature and return shape exactly as-is —
the rest of the backend (routes/building.py) is built against this contract.
"""
import logging

logger = logging.getLogger("gemini")


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
    logger.info(f"Gemini analysis started for image_path={image_path}")

    # --- STUB IMPLEMENTATION (placeholder until AI side is wired in) ---
    try:
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
    except Exception as e:
        logger.error(f"Gemini analysis failed for image_path={image_path}: {e}")
        raise BuildingAnalysisError(str(e)) from e


if __name__ == "__main__":
    result = analyze_building_image("some/fake/path.jpg")
    print(result)
    assert "condition" in result
    assert "notable_features" in result