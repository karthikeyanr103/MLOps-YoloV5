# Counting Model

Counting uses the shared
`models/object_detection/yolov5s.onnx` detector. Retained COCO detections are
grouped by class and returned as both `total_count` and `counts_by_class`.

Model binaries are intentionally ignored by Git.
