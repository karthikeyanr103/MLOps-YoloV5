"""Image classification endpoint."""

from fastapi import APIRouter, File, UploadFile

from app.services.onnx_inference import predict
from app.services.preprocessing import read_uploaded_image

router = APIRouter(prefix="/classification", tags=["Classification"])


@router.post("/predict", summary="Classify an uploaded image")
async def classify_image(file: UploadFile = File(...)) -> dict:
    """Return ranked classes from the classification model."""
    image = await read_uploaded_image(file)
    return predict("classification", image)
