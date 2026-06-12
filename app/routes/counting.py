"""Object counting endpoint."""

from fastapi import APIRouter, File, UploadFile

from app.services.onnx_inference import predict
from app.services.preprocessing import read_uploaded_image

router = APIRouter(prefix="/counting", tags=["Counting"])


@router.post("/predict", summary="Count objects in an uploaded image")
async def count_objects(file: UploadFile = File(...)) -> dict:
    """Return total and per-class object counts."""
    image = await read_uploaded_image(file)
    return predict("counting", image)
