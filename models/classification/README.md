# Classification Model

Place the exported artifact at `models/classification/model.onnx`.

Expected default input: `float32 [batch, 3, 640, 640]`, RGB, values in
`[0, 1]`. Update preprocessing for the training model's image size and
normalization. Add a versioned class label file and implement softmax/top-k
decoding in `app/services/postprocessing.py`.

Model binaries are intentionally ignored by Git.
