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

    assert css.status_code == 200
    assert "text/css" in css.headers["content-type"]
    assert javascript.status_code == 200
    assert "javascript" in javascript.headers["content-type"]
