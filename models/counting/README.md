# Counting Model

Place the exported artifact at `models/counting/model.onnx`.

Counting is typically derived from object detections after confidence filtering
and non-maximum suppression. Group retained detections by class and return both
`total_count` and `counts_by_class`. Document the confidence and IoU thresholds
used by the deployed model.

Model binaries are intentionally ignored by Git.
