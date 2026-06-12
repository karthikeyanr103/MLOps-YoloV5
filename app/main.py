"""FastAPI entry point for the multi-task computer vision application."""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routes import classification, counting, object_detection, segmentation
from app.services.onnx_inference import model_status

BASE_DIR = Path(__file__).resolve().parent

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
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"model_status": model_status()},
    )


@app.get("/health", tags=["Operations"])
async def health() -> dict:
    """Provide a lightweight readiness endpoint for Docker deployments."""
    return {"status": "healthy", "models": model_status()}
