"""YOLOv5 detection decoding and task-aware response formatting."""

from __future__ import annotations

from collections import Counter
from typing import Any

import numpy as np
from PIL import Image

from app.services.preprocessing import LetterboxResult

COCO_NAMES = (
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train",
    "truck", "boat", "traffic light", "fire hydrant", "stop sign",
    "parking meter", "bench", "bird", "cat", "dog", "horse", "sheep", "cow",
    "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella", "handbag",
    "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite",
    "baseball bat", "baseball glove", "skateboard", "surfboard",
    "tennis racket", "bottle", "wine glass", "cup", "fork", "knife", "spoon",
    "bowl", "banana", "apple", "sandwich", "orange", "broccoli", "carrot",
    "hot dog", "pizza", "donut", "cake", "chair", "couch", "potted plant",
    "bed", "dining table", "toilet", "tv", "laptop", "mouse", "remote",
    "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
    "refrigerator", "book", "clock", "vase", "scissors", "teddy bear",
    "hair drier", "toothbrush",
)


def sample_response(task: str, image: Image.Image) -> dict[str, Any]:
    """Explain how to bootstrap the default model when ONNX is not installed."""
    return {
        "task": task,
        "model_status": "not_installed",
        "image": {"width": image.width, "height": image.height},
        "message": (
            "The default YOLOv5s ONNX model is created by the bootstrap deployment. "
            "Run scripts/bootstrap_yolov5_to_s3.ps1 to trigger the AWS pipeline."
        ),
    }


def _box_iou(box: np.ndarray, boxes: np.ndarray) -> np.ndarray:
    """Calculate IoU between one xyxy box and an array of xyxy boxes."""
    top_left = np.maximum(box[:2], boxes[:, :2])
    bottom_right = np.minimum(box[2:], boxes[:, 2:])
    intersection = np.prod(np.clip(bottom_right - top_left, 0, None), axis=1)
    box_area = np.prod(np.clip(box[2:] - box[:2], 0, None))
    boxes_area = np.prod(np.clip(boxes[:, 2:] - boxes[:, :2], 0, None), axis=1)
    return intersection / np.maximum(box_area + boxes_area - intersection, 1e-7)


def _non_max_suppression(
    boxes: np.ndarray,
    scores: np.ndarray,
    class_ids: np.ndarray,
    iou_threshold: float,
) -> list[int]:
    """Apply class-aware non-maximum suppression using NumPy."""
    kept: list[int] = []
    for class_id in np.unique(class_ids):
        indices = np.where(class_ids == class_id)[0]
        indices = indices[np.argsort(scores[indices])[::-1]]
        while indices.size:
            current = int(indices[0])
            kept.append(current)
            if indices.size == 1:
                break
            remaining = indices[1:]
            indices = remaining[
                _box_iou(boxes[current], boxes[remaining]) < iou_threshold
            ]
    return sorted(kept, key=lambda index: float(scores[index]), reverse=True)


def decode_yolov5(
    output: np.ndarray,
    image: Image.Image,
    prepared: LetterboxResult,
    confidence_threshold: float = 0.25,
    iou_threshold: float = 0.45,
) -> list[dict[str, Any]]:
    """Decode the standard YOLOv5 ONNX output shaped [1, anchors, 85]."""
    predictions = np.asarray(output)
    if predictions.ndim == 3:
        predictions = predictions[0]
    if predictions.shape[0] < predictions.shape[1] and predictions.shape[0] == 85:
        predictions = predictions.T
    if predictions.ndim != 2 or predictions.shape[1] < 6:
        raise ValueError(f"Unexpected YOLOv5 output shape: {predictions.shape}")

    class_scores = predictions[:, 5:]
    class_ids = np.argmax(class_scores, axis=1)
    scores = predictions[:, 4] * class_scores[np.arange(len(predictions)), class_ids]
    selected = scores >= confidence_threshold
    if not np.any(selected):
        return []

    raw_boxes = predictions[selected, :4]
    scores = scores[selected]
    class_ids = class_ids[selected]
    boxes = np.empty_like(raw_boxes)
    boxes[:, 0] = raw_boxes[:, 0] - raw_boxes[:, 2] / 2
    boxes[:, 1] = raw_boxes[:, 1] - raw_boxes[:, 3] / 2
    boxes[:, 2] = raw_boxes[:, 0] + raw_boxes[:, 2] / 2
    boxes[:, 3] = raw_boxes[:, 1] + raw_boxes[:, 3] / 2
    kept = _non_max_suppression(boxes, scores, class_ids, iou_threshold)

    detections = []
    for index in kept[:100]:
        box = boxes[index].copy()
        box[[0, 2]] = (box[[0, 2]] - prepared.pad_x) / prepared.scale
        box[[1, 3]] = (box[[1, 3]] - prepared.pad_y) / prepared.scale
        box[[0, 2]] = np.clip(box[[0, 2]], 0, image.width)
        box[[1, 3]] = np.clip(box[[1, 3]], 0, image.height)
        class_id = int(class_ids[index])
        detections.append(
            {
                "label": COCO_NAMES[class_id]
                if class_id < len(COCO_NAMES)
                else f"class_{class_id}",
                "class_id": class_id,
                "confidence": round(float(scores[index]), 4),
                "box": {
                    "x_min": round(float(box[0]), 2),
                    "y_min": round(float(box[1]), 2),
                    "x_max": round(float(box[2]), 2),
                    "y_max": round(float(box[3]), 2),
                },
            }
        )
    return detections


def format_yolov5_response(
    task: str,
    detections: list[dict[str, Any]],
    image: Image.Image,
) -> dict[str, Any]:
    """Reuse YOLOv5 detections for detection, counting, and scene labels."""
    common = {
        "task": task,
        "model_status": "yolov5s",
        "image": {"width": image.width, "height": image.height},
    }
    if task == "counting":
        counts = Counter(item["label"] for item in detections)
        return {
            **common,
            "total_count": len(detections),
            "counts_by_class": dict(counts),
            "detections": detections,
        }
    if task == "classification":
        best_by_label: dict[str, float] = {}
        for detection in detections:
            best_by_label[detection["label"]] = max(
                best_by_label.get(detection["label"], 0),
                detection["confidence"],
            )
        predictions = sorted(
            (
                {"label": label, "confidence": confidence}
                for label, confidence in best_by_label.items()
            ),
            key=lambda item: item["confidence"],
            reverse=True,
        )
        return {
            **common,
            "prediction_type": "detected_scene_objects",
            "predictions": predictions,
        }
    return {**common, "detections": detections}
