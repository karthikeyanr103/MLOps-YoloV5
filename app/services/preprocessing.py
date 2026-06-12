"""Image validation and tensor preparation utilities."""

from __future__ import annotations

from io import BytesIO

import numpy as np
from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


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


def image_to_tensor(image: Image.Image, size: tuple[int, int] = (640, 640)) -> np.ndarray:
    """Convert a PIL image to a normalized NCHW float32 tensor."""
    resized = image.resize(size, Image.Resampling.BILINEAR)
    array = np.asarray(resized, dtype=np.float32) / 255.0
    return np.transpose(array, (2, 0, 1))[None, ...]
