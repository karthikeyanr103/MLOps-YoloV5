# Model Conversion Guide

## Why ONNX

ONNX provides a stable serving format between PyTorch training code and the
FastAPI application. ONNX Runtime can execute the exported graph without
installing the complete training repository in the production image.

## Convert a Compatible Checkpoint

Install conversion-only dependencies:

```bash
python -m pip install -r requirements-conversion.txt
python scripts/convert_to_onnx.py \
  --input best.pt \
  --output models/object_detection/model.onnx \
  --task object_detection
```

The script supports TorchScript files and checkpoints that contain a serialized
`torch.nn.Module`. A plain `state_dict` cannot be reconstructed without the
model class; update `load_model()` to instantiate that architecture first.

## YOLOv5 Export

For a checkpoint produced by the upstream YOLOv5 repository, its native
`export.py` is generally the best conversion route because it knows the exact
architecture and output contract:

```bash
python export.py --weights best.pt --include onnx --opset 17 --simplify
```

Copy the result to the appropriate task folder as `model.onnx`.

## Integration Contract

The default preprocessor creates a normalized `float32` tensor shaped
`[1, 3, 640, 640]`. If the model expects different dimensions, channel order,
mean/std normalization, or integer input, update
`app/services/preprocessing.py`.

The generic postprocessor reports tensor shapes and a small output preview.
Implement labels, non-maximum suppression, counts, masks, and coordinate
rescaling in `app/services/postprocessing.py` according to the export.

## Validate

```bash
python -c "import onnx; onnx.checker.check_model(onnx.load('model.onnx'))"
uvicorn app.main:app
python scripts/run_local_inference.py sample.jpg --task object-detection
```

Compare ONNX predictions against the original PyTorch model on a fixed
validation set before promoting the image.
