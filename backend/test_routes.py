import io
from PIL import Image


def make_test_image():
    """Create a small in-memory valid PNG for upload tests."""
    buf = io.BytesIO()
    Image.new("RGB", (10, 10), color="red").save(buf, format="PNG")
    buf.seek(0)
    return buf


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_upload_valid_image(client):
    img = make_test_image()
    response = client.post(
        "/buildings/upload",
        files={"file": ("test.png", img, "image/png")},
    )
    assert response.status_code == 200
    body = response.json()
    assert "building_id" in body
    assert body["status"] == "pending"
    assert body["image_url"].startswith("/uploads/")


def test_upload_rejects_bad_content_type(client):
    bad_file = io.BytesIO(b"not an image")
    response = client.post(
        "/buildings/upload",
        files={"file": ("test.txt", bad_file, "text/plain")},
    )
    assert response.status_code == 400
    assert "error" in response.json()


def test_upload_rejects_oversized_file(client):
    big_file = io.BytesIO(b"0" * (11 * 1024 * 1024))  # 11MB, over the 10MB limit
    response = client.post(
        "/buildings/upload",
        files={"file": ("big.png", big_file, "image/png")},
    )
    assert response.status_code == 413
    assert "error" in response.json()


def test_analyze_nonexistent_building_returns_404(client):
    response = client.post("/buildings/9999/analyze")
    assert response.status_code == 404
    assert "error" in response.json()


def test_analyze_building_with_no_image(client, db_session):
    from db.database import Building

    building = Building(image_path="", status="pending")
    db_session.add(building)
    db_session.commit()
    db_session.refresh(building)

    response = client.post(f"/buildings/{building.id}/analyze")
    assert response.status_code == 400
    assert "error" in response.json()


def test_list_buildings_empty(client):
    response = client.get("/buildings")
    assert response.status_code == 200
    assert response.json() == []


def test_list_and_get_building_after_upload(client):
    img = make_test_image()
    upload_resp = client.post(
        "/buildings/upload",
        files={"file": ("test.png", img, "image/png")},
    )
    building_id = upload_resp.json()["building_id"]

    list_resp = client.get("/buildings")
    assert list_resp.status_code == 200
    listed = list_resp.json()
    assert len(listed) == 1
    assert listed[0]["id"] == building_id
    assert listed[0]["status"] == "pending"

    detail_resp = client.get(f"/buildings/{building_id}")
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert detail["id"] == building_id
    assert detail["analysis_json"] is None  # not analyzed yet


def test_get_nonexistent_building_returns_404(client):
    response = client.get("/buildings/9999")
    assert response.status_code == 404
    assert "error" in response.json()