"""Lazy ONNX Runtime loading for the default pretrained YOLOv5s model."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import onnxruntime as ort
from PIL import Image

from app.services.postprocessing import (
    decode_yolov5,
    format_yolov5_response,
    sample_response,
)
from app.services.preprocessing import prepare_yolov5_input

MODEL_ROOT = Path(os.getenv("MODEL_ROOT", "models"))
YOLOV5_MODEL_PATH = MODEL_ROOT / "object_detection" / "yolov5s.onnx"
SEGMENTATION_MODEL_PATH = MODEL_ROOT / "segmentation" / "yolov5s-seg.onnx"
YOLOV5_TASKS = {"classification", "counting", "object_detection"}


@lru_cache(maxsize=1)
def get_yolov5_session() -> ort.InferenceSession | None:
    """Load the shared YOLOv5s detector once per application process."""
    if not YOLOV5_MODEL_PATH.is_file():
        return None
    return ort.InferenceSession(
        str(YOLOV5_MODEL_PATH),
        providers=["CPUExecutionProvider"],
    )


def predict(task: str, image: Image.Image) -> dict[str, Any]:
    """Run YOLOv5s for detection-based tasks with an honest fallback."""
    if task == "segmentation":
        return {
            "task": task,
            "model_status": (
                "model_present_decoder_pending"
                if SEGMENTATION_MODEL_PATH.is_file()
                else "not_configured"
            ),
            "image": {"width": image.width, "height": image.height},
            "message": (
                "YOLOv5s is a detector and cannot return masks. Add yolov5s-seg "
                "and its mask decoder to enable this endpoint."
            ),
        }

    session = get_yolov5_session()
    if session is None:
        return sample_response(task, image)

    prepared = prepare_yolov5_input(image)
    input_name = session.get_inputs()[0].name
    outputs = session.run(None, {input_name: prepared.tensor})
    detections = decode_yolov5(outputs[0], image, prepared)
    return format_yolov5_response(task, detections, image)


def model_status() -> dict[str, str]:
    """Report which endpoints are powered by the shared default detector."""
    detector_status = "ready:yolov5s" if YOLOV5_MODEL_PATH.is_file() else "not_installed"
    return {
        "classification": detector_status,
        "counting": detector_status,
        "segmentation": (
            "decoder_pending"
            if SEGMENTATION_MODEL_PATH.is_file()
            else "not_configured"
        ),
        "object_detection": detector_status,
    }
