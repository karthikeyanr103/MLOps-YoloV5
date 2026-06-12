"""Lazy ONNX Runtime loading for the default pretrained YOLOv5s model."""

from __future__ import annotations

import ast
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import onnxruntime as ort
from PIL import Image

from app.services.postprocessing import (
    COCO_NAMES,
    decode_yolov5,
    decode_yolov5_segmentation,
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


@lru_cache(maxsize=1)
def get_segmentation_session() -> ort.InferenceSession | None:
    """Load the shared YOLOv5s-seg model once per application process."""
    if not SEGMENTATION_MODEL_PATH.is_file():
        return None
    return ort.InferenceSession(
        str(SEGMENTATION_MODEL_PATH),
        providers=["CPUExecutionProvider"],
    )


def model_class_names(session: ort.InferenceSession) -> tuple[str, ...]:
    """Read class labels embedded by the YOLOv5 exporter and validate them."""
    metadata = session.get_modelmeta().custom_metadata_map
    raw_names = metadata.get("names")
    if not raw_names:
        return COCO_NAMES
    try:
        parsed = ast.literal_eval(raw_names)
        if isinstance(parsed, dict):
            normalized = {int(index): str(name) for index, name in parsed.items()}
            names = tuple(normalized[index] for index in sorted(normalized))
        else:
            names = tuple(str(name) for name in parsed)
        return names or COCO_NAMES
    except (ValueError, SyntaxError, TypeError, KeyError):
        return COCO_NAMES


def predict(task: str, image: Image.Image) -> dict[str, Any]:
    """Run YOLOv5s for detection-based tasks with an honest fallback."""
    if task == "segmentation":
        session = get_segmentation_session()
        if session is None:
            return sample_response(task, image)
        prepared = prepare_yolov5_input(image)
        outputs = session.run(
            None,
            {session.get_inputs()[0].name: prepared.tensor},
        )
        segments, overlay = decode_yolov5_segmentation(
            outputs[0],
            outputs[1],
            image,
            prepared,
            model_class_names(session),
        )
        return {
            "task": task,
            "model_status": "yolov5s-seg",
            "image": {"width": image.width, "height": image.height},
            "segments": segments,
            "overlay": overlay,
        }

    session = get_yolov5_session()
    if session is None:
        return sample_response(task, image)

    prepared = prepare_yolov5_input(image)
    input_name = session.get_inputs()[0].name
    outputs = session.run(None, {input_name: prepared.tensor})
    detections = decode_yolov5(outputs[0], image, prepared)
    names = model_class_names(session)
    for detection in detections:
        class_id = detection["class_id"]
        detection["label"] = (
            names[class_id] if class_id < len(names) else f"class_{class_id}"
        )
    return format_yolov5_response(task, detections, image)


def model_status() -> dict[str, str]:
    """Report which endpoints are powered by the shared default detector."""
    detector_status = "ready:yolov5s" if YOLOV5_MODEL_PATH.is_file() else "not_installed"
    return {
        "classification": detector_status,
        "counting": detector_status,
        "segmentation": (
            "ready:yolov5s-seg"
            if SEGMENTATION_MODEL_PATH.is_file()
            else "not_installed"
        ),
        "object_detection": detector_status,
    }
