# Segmentation Model

The default `yolov5s` detector cannot produce masks. Add the official
`yolov5s-seg` export at `models/segmentation/yolov5s-seg.onnx` and implement
its prototype-mask decoder before presenting this endpoint as active.

The final adapter should decode masks, resize them to the original image, and
return polygons, run-length encoding, or a generated overlay URL. Keep large
binary masks out of ordinary JSON responses unless the API client requires
them.

Model binaries are intentionally ignored by Git.
