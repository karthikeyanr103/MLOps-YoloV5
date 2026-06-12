"""Lazy ONNX Runtime model loading with a portfolio-friendly fallback mode."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import onnxruntime as ort
from PIL import Image

from app.services.postprocessing import format_onnx_response, sample_response
from app.services.preprocessing import image_to_tensor

MODEL_ROOT = Path(os.getenv("MODEL_ROOT", "models"))
MODEL_FILENAMES = {
    "classification": MODEL_ROOT / "classification" / "model.onnx",
    "counting": MODEL_ROOT / "counting" / "model.onnx",
    "segmentation": MODEL_ROOT / "segmentation" / "model.onnx",
    "object_detection": MODEL_ROOT / "object_detection" / "model.onnx",
}


@lru_cache(maxsize=4)
def get_session(task: str) -> ort.InferenceSession | None:
    """Load a task model once, or return None while the repository is in demo mode."""
    model_path = MODEL_FILENAMES[task]
    if not model_path.is_file():
        return None

    providers = ["CPUExecutionProvider"]
    return ort.InferenceSession(str(model_path), providers=providers)


def predict(task: str, image: Image.Image) -> dict[str, Any]:
    """Run an installed ONNX model or return the documented placeholder response."""
    session = get_session(task)
    if session is None:
        return sample_response(task, image)

    input_metadata = session.get_inputs()[0]
    tensor = image_to_tensor(image)
    outputs = session.run(None, {input_metadata.name: tensor})
    return format_onnx_response(task, outputs, image)


def model_status() -> dict[str, str]:
    """Report whether each task has a deployable ONNX model available."""
    return {
        task: "ready" if path.is_file() else "placeholder"
        for task, path in MODEL_FILENAMES.items()
    }
