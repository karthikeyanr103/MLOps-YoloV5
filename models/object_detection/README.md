# Object Detection Model

The default deployment exports official pretrained YOLOv5s v7.0 to
`models/object_detection/yolov5s.onnx`.

The application decodes standard YOLOv5 output, applies class-aware
non-maximum suppression, maps COCO class IDs, and rescales boxes to the
original image dimensions. Object counting and scene-label classification
reuse these detections.

Model binaries are intentionally ignored by Git.
