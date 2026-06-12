# Segmentation Model

The full deployment automatically downloads official YOLOv5s-seg v7.0,
exports it to `models/segmentation/yolov5s-seg.onnx`, and packages it beside
the detector.

The service decodes the 32 prototype-mask channels, applies NMS, crops and
rescales masks, and returns a transparent PNG overlay with per-segment labels,
confidence, coverage, and bounding boxes.

The final adapter should decode masks, resize them to the original image, and
return polygons, run-length encoding, or a generated overlay URL. Keep large
binary masks out of ordinary JSON responses unless the API client requires
them.

Model binaries are intentionally ignored by Git.
