"""Focused tests for the default YOLOv5 output decoder."""

import numpy as np
from PIL import Image

from app.services.postprocessing import decode_yolov5, format_yolov5_response
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
