"""Image validation and YOLOv5 tensor preparation utilities."""

from __future__ import annotations

from io import BytesIO
from typing import NamedTuple

import numpy as np
from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
YOLO_IMAGE_SIZE = 640


class LetterboxResult(NamedTuple):
    """Tensor and geometry required to map YOLOv5 boxes to the source image."""

    tensor: np.ndarray
    scale: float
    pad_x: float
    pad_y: float


async def read_uploaded_image(file: UploadFile) -> Image.Image:
    """Validate an uploaded image and return it in RGB format."""
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail="Upload a JPEG, PNG, or WebP image.",
        )

    payload = await file.read(MAX_UPLOAD_BYTES + 1)
    if not payload:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    if len(payload) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Images must be 10 MB or smaller.")

    try:
        image = Image.open(BytesIO(payload))
        image.load()
    except (UnidentifiedImageError, OSError) as exc:
        raise HTTPException(status_code=400, detail="The file is not a valid image.") from exc

    return image.convert("RGB")


def prepare_yolov5_input(
    image: Image.Image,
    size: int = YOLO_IMAGE_SIZE,
) -> LetterboxResult:
    """Resize with aspect ratio preserved and create a normalized NCHW tensor."""
    scale = min(size / image.width, size / image.height)
    resized_width = max(1, round(image.width * scale))
    resized_height = max(1, round(image.height * scale))
    resized = image.resize(
        (resized_width, resized_height),
        Image.Resampling.BILINEAR,
    )

    pad_x = round((size - resized_width) / 2)
    pad_y = round((size - resized_height) / 2)
    canvas = Image.new("RGB", (size, size), color=(114, 114, 114))
    canvas.paste(resized, (pad_x, pad_y))

    array = np.asarray(canvas, dtype=np.float32) / 255.0
    tensor = np.transpose(array, (2, 0, 1))[None, ...]
    return LetterboxResult(
        tensor=np.ascontiguousarray(tensor),
        scale=scale,
        pad_x=pad_x,
        pad_y=pad_y,
    )
