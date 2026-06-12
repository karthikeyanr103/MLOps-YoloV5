"""Task-aware response formatting for model and demonstration outputs."""

from __future__ import annotations

from typing import Any

import numpy as np
from PIL import Image


def sample_response(task: str, image: Image.Image) -> dict[str, Any]:
    """Return a deterministic example response when no model is installed."""
    width, height = image.size
    common = {
        "task": task,
        "model_status": "placeholder",
        "image": {"width": width, "height": height},
    }

    if task == "classification":
        return {
            **common,
            "predictions": [
                {"label": "example_class", "confidence": 0.94},
                {"label": "alternate_class", "confidence": 0.04},
            ],
        }
    if task == "counting":
        return {
            **common,
            "total_count": 3,
            "counts_by_class": {"person": 2, "vehicle": 1},
        }
    if task == "segmentation":
        return {
            **common,
            "segments": [
                {
                    "label": "foreground",
                    "confidence": 0.91,
                    "coverage_percent": 36.7,
                }
            ],
            "mask_encoding": "Add model-specific mask or polygon output here.",
        }
    return {
        **common,
        "detections": [
            {
                "label": "example_object",
                "confidence": 0.92,
                "box": {
                    "x_min": round(width * 0.15),
                    "y_min": round(height * 0.18),
                    "x_max": round(width * 0.72),
                    "y_max": round(height * 0.81),
                },
            }
        ],
    }


def format_onnx_response(
    task: str,
    outputs: list[np.ndarray],
    image: Image.Image,
) -> dict[str, Any]:
    """Expose generic ONNX output metadata until model-specific decoding is added."""
    return {
        "task": task,
        "model_status": "onnx",
        "image": {"width": image.width, "height": image.height},
        "outputs": [
            {
                "index": index,
                "shape": list(np.asarray(output).shape),
                "preview": np.asarray(output).reshape(-1)[:10].tolist(),
            }
            for index, output in enumerate(outputs)
        ],
        "note": (
            "Raw output preview returned. Customize app/services/postprocessing.py "
            "for the exported model's labels, boxes, masks, or class scores."
        ),
    }
