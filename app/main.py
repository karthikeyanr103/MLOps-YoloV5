"""FastAPI entry point for the multi-task computer vision application."""

import hashlib
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routes import classification, counting, object_detection, segmentation
from app.services.onnx_inference import model_status

BASE_DIR = Path(__file__).resolve().parent


def static_asset_version() -> str:
    """Create a short content hash so browsers refresh CSS and JavaScript."""
    digest = hashlib.sha256()
    for relative_path in ("static/css/style.css", "static/js/main.js"):
        digest.update((BASE_DIR / relative_path).read_bytes())
    return digest.hexdigest()[:12]


ASSET_VERSION = static_asset_version()

app = FastAPI(
    title="MLOps-YoloV5 Inference API",
    version="1.0.0",
    description=(
        "Portfolio-ready FastAPI service for classification, counting, "
        "segmentation, and object detection with ONNX Runtime."
    ),
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

app.include_router(classification.router, prefix="/api/v1")
app.include_router(counting.router, prefix="/api/v1")
app.include_router(segmentation.router, prefix="/api/v1")
app.include_router(object_detection.router, prefix="/api/v1")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home(request: Request) -> HTMLResponse:
    """Render the browser-based image inference demo."""
    response = templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "model_status": model_status(),
            "asset_version": ASSET_VERSION,
        },
    )
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


@app.get("/health", tags=["Operations"])
async def health() -> dict:
    """Provide a lightweight readiness endpoint for Docker deployments."""
    return {"status": "healthy", "models": model_status()}
