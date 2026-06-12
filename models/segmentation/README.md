# Segmentation Model

Place the exported artifact at `models/segmentation/model.onnx`.

The final adapter should decode masks, resize them to the original image, and
return polygons, run-length encoding, or a generated overlay URL. Keep large
binary masks out of ordinary JSON responses unless the API client requires
them.

Model binaries are intentionally ignored by Git.
