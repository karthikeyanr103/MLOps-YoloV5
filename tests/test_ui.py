"""Checks for the portfolio page and its versioned static assets."""

from fastapi.testclient import TestClient

from app.main import ASSET_VERSION, app

client = TestClient(app)


def test_home_links_versioned_css_and_javascript() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-cache, no-store, must-revalidate"
    assert f"/static/css/style.css?v={ASSET_VERSION}" in response.text
    assert f"/static/js/main.js?v={ASSET_VERSION}" in response.text
    assert "http://testserver/static/" not in response.text


def test_static_assets_are_served() -> None:
    css = client.get("/static/css/style.css")
    javascript = client.get("/static/js/main.js")
    sample = client.get("/static/samples/segmentation.jpg")

    assert css.status_code == 200
    assert "text/css" in css.headers["content-type"]
    assert javascript.status_code == 200
    assert "javascript" in javascript.headers["content-type"]
    assert sample.status_code == 200
    assert sample.headers["content-type"] == "image/jpeg"


def test_home_exposes_all_live_tasks_and_quick_samples() -> None:
    response = client.get("/")

    assert "Pixel-level masks" in response.text
    assert "ROADMAP" not in response.text
    assert "/static/samples/object-detection.jpg" in response.text


def test_home_contains_only_the_inference_workspace() -> None:
    response = client.get("/")

    assert "site-header" not in response.text
    assert "DEPLOYMENT PIPELINE" not in response.text
    assert "Model status" not in response.text
    assert "<footer>" not in response.text
    assert 'class="workbench"' in response.text
