"""Image segmentation endpoint."""

from fastapi import APIRouter, File, UploadFile

from app.services.onnx_inference import predict
from app.services.preprocessing import read_uploaded_image

router = APIRouter(prefix="/segmentation", tags=["Segmentation"])


@router.post("/predict", summary="Segment an uploaded image")
async def segment_image(file: UploadFile = File(...)) -> dict:
    """Return segment metadata and model output details."""
    image = await read_uploaded_image(file)
    return predict("segmentation", image)
