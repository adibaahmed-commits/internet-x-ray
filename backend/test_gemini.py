from unittest.mock import patch
from services.gemini_service import analyze_building_image, BuildingAnalysisError


def make_test_image():
    import io
    from PIL import Image

    buf = io.BytesIO()
    Image.new("RGB", (10, 10), color="blue").save(buf, format="PNG")
    buf.seek(0)
    return buf


def test_analyze_building_image_returns_expected_shape():
    """Tests the current stub implementation directly — no mocking needed
    since analyze_building_image() doesn't call the real API yet."""
    result = analyze_building_image("some/fake/path.jpg")

    expected_keys = {
        "building_type", "estimated_year_built", "estimated_stories",
        "condition", "notable_features",
        "architectural_style", "estimated_rental_price",
        "visible_amenities", "nearby_hospitals", "nearby_schools",
        "network_coverage", "confidence", "summary",
    }
    assert expected_keys.issubset(result.keys())
    assert result["condition"] in {"excellent", "good", "fair", "poor"}
    assert isinstance(result["notable_features"], list)
    assert isinstance(result["visible_amenities"], list)
    assert isinstance(result["nearby_hospitals"], list)
    assert isinstance(result["nearby_schools"], list)


@patch("routes.building.analyze_building_image")
def test_analyze_route_returns_gemini_result(mock_analyze, client):
    """Full route-level test: upload an image, then analyze it,
    with the Gemini call mocked so no real API is hit."""
    mock_analyze.return_value = {
        "building_type": "test type",
        "estimated_year_built": "2000-2010",
        "estimated_stories": 3,
        "condition": "good",
        "notable_features": ["test feature"],
        "architectural_style": "modern",
        "estimated_rental_price": "₹20,000/mo",
        "visible_amenities": ["parking"],
        "nearby_hospitals": ["Test Hospital - 1km"],
        "nearby_schools": ["Test School - 0.5km"],
        "network_coverage": "Jio - Strong",
        "confidence": "high",
        "summary": "mocked analysis",
    }

    img = make_test_image()
    upload_resp = client.post(
        "/buildings/upload",
        files={"file": ("test.png", img, "image/png")},
    )
    building_id = upload_resp.json()["building_id"]

    analyze_resp = client.post(f"/buildings/{building_id}/analyze")
    assert analyze_resp.status_code == 200
    body = analyze_resp.json()
    assert body["status"] == "complete"
    assert body["analysis"]["summary"] == "mocked analysis"
    mock_analyze.assert_called_once()


@patch("routes.building.analyze_building_image")
def test_analyze_route_handles_gemini_failure(mock_analyze, client):
    """When Gemini analysis fails, the route should return 502
    with the standard {error: ...} shape, not a raw traceback."""
    mock_analyze.side_effect = BuildingAnalysisError("Gemini timeout")

    img = make_test_image()
    upload_resp = client.post(
        "/buildings/upload",
        files={"file": ("test.png", img, "image/png")},
    )
    building_id = upload_resp.json()["building_id"]

    analyze_resp = client.post(f"/buildings/{building_id}/analyze")
    assert analyze_resp.status_code == 502
    assert "error" in analyze_resp.json()