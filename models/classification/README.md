# Classification Model

The default classification endpoint summarizes the unique COCO object labels
detected by the shared `models/object_detection/yolov5s.onnx` model. It is
therefore scene-object classification, not whole-image ImageNet
classification. A dedicated `yolov5s-cls` model can be added later if required.

Model binaries are intentionally ignored by Git.
