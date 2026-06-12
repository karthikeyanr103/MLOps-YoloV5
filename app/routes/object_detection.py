"""Object detection endpoint."""

from fastapi import APIRouter, File, UploadFile

from app.services.onnx_inference import predict
from app.services.preprocessing import read_uploaded_image

router = APIRouter(prefix="/object-detection", tags=["Object Detection"])


@router.post("/predict", summary="Detect objects in an uploaded image")
async def detect_objects(file: UploadFile = File(...)) -> dict:
    """Return detected classes, confidence scores, and bounding boxes."""
    image = await read_uploaded_image(file)
    return predict("object_detection", image)
