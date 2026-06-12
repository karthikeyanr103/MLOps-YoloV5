"""Focused tests for the default YOLOv5 output decoders."""

import base64

import numpy as np
from PIL import Image

from app.services.postprocessing import (
    COCO_NAMES,
    decode_yolov5,
    decode_yolov5_segmentation,
    format_yolov5_response,
)
from app.services.preprocessing import prepare_yolov5_input


def test_decoder_filters_overlap_and_rescales_boxes() -> None:
    image = Image.new("RGB", (640, 480))
    prepared = prepare_yolov5_input(image)
    output = np.zeros((1, 3, 85), dtype=np.float32)

    output[0, 0, :4] = [320, 320, 200, 200]
    output[0, 0, 4] = 0.9
    output[0, 0, 5] = 0.9
    output[0, 1, :4] = [322, 322, 200, 200]
    output[0, 1, 4] = 0.8
    output[0, 1, 5] = 0.8
    output[0, 2, :4] = [100, 180, 60, 80]
    output[0, 2, 4] = 0.95
    output[0, 2, 7] = 0.9

    detections = decode_yolov5(output, image, prepared)

    assert len(detections) == 2
    assert detections[0]["label"] in {"person", "car"}
    assert all(item["box"]["y_min"] >= 0 for item in detections)


def test_counting_groups_yolov5_detections() -> None:
    image = Image.new("RGB", (100, 100))
    detections = [
        {"label": "person", "confidence": 0.9, "box": {}},
        {"label": "person", "confidence": 0.8, "box": {}},
        {"label": "car", "confidence": 0.7, "box": {}},
    ]

    response = format_yolov5_response("counting", detections, image)

    assert response["total_count"] == 3
    assert response["counts_by_class"] == {"person": 2, "car": 1}


def test_segmentation_decoder_returns_mask_and_valid_coco_label() -> None:
    image = Image.new("RGB", (640, 640))
    prepared = prepare_yolov5_input(image)
    output = np.zeros((1, 2, 117), dtype=np.float32)
    prototypes = np.full((1, 32, 160, 160), -8, dtype=np.float32)

    output[0, 0, :4] = [320, 320, 240, 280]
    output[0, 0, 4] = 0.95
    output[0, 0, 5 + 16] = 0.9
    output[0, 0, 85] = 1
    prototypes[0, 0, 45:115, 50:110] = 8

    segments, overlay = decode_yolov5_segmentation(
        output,
        prototypes,
        image,
        prepared,
    )

    assert len(segments) == 1
    assert segments[0]["label"] == COCO_NAMES[16] == "dog"
    assert segments[0]["coverage_percent"] > 0
    assert overlay.startswith("data:image/png;base64,")
    assert base64.b64decode(overlay.split(",", 1)[1]).startswith(b"\x89PNG")
