# Object Detection Model

Place the exported artifact at `models/object_detection/model.onnx`.

The final adapter should decode YOLO predictions, apply confidence filtering
and non-maximum suppression, map class IDs to labels, and rescale boxes to the
original image dimensions. Use a model-specific contract test before release.

Model binaries are intentionally ignored by Git.
