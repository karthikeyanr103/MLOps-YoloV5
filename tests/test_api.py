"""Behavior tests for the public FastAPI interface."""

from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

client = TestClient(app)


def image_bytes() -> bytes:
    """Create a small in-memory image without committing binary test fixtures."""
    output = BytesIO()
    Image.new("RGB", (64, 48), color=(30, 90, 60)).save(output, format="PNG")
    return output.getvalue()


def test_health_reports_all_tasks() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert set(response.json()["models"]) == {
        "classification",
        "counting",
        "segmentation",
        "object_detection",
    }


def test_all_prediction_routes_accept_images() -> None:
    expectations = {
        "classification": "not_installed",
        "counting": "not_installed",
        "segmentation": "not_configured",
        "object-detection": "not_installed",
    }
    for route, expected_status in expectations.items():
        response = client.post(
            f"/api/v1/{route}/predict",
            files={"file": ("sample.png", image_bytes(), "image/png")},
        )
        assert response.status_code == 200
        assert response.json()["model_status"] == expected_status


def test_rejects_unsupported_upload_type() -> None:
    response = client.post(
        "/api/v1/classification/predict",
        files={"file": ("notes.txt", b"not an image", "text/plain")},
    )
    assert response.status_code == 415
