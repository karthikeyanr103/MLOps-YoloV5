# YOLOv5 Model Guide

## Default Model

The project defaults to official pretrained `yolov5s.pt` from the YOLOv5 v7.0
release. It is a small COCO object detector suitable for a CPU-hosted portfolio
demo and requires no training.

The repository does not commit the checkpoint or generated ONNX file. Instead:

1. `scripts/bootstrap_yolov5_to_s3.ps1` downloads official `yolov5s.pt`.
2. The script uploads it to the S3 `models/` prefix.
3. Lambda starts CodeBuild.
4. CodeBuild clones the pinned YOLOv5 v7.0 source.
5. YOLOv5's native `export.py` creates `yolov5s.onnx`.
6. The ONNX model is copied into the Docker image.

Bootstrap from Windows PowerShell:

```powershell
.\scripts\bootstrap_yolov5_to_s3.ps1 `
  -Bucket "YOUR_UNIQUE_MODEL_BUCKET" `
  -Region "us-east-1"
```

## Why Native YOLOv5 Export

YOLOv5 `.pt` checkpoints contain architecture objects from the YOLOv5 source
tree. The upstream exporter knows how to load those objects, fuse layers,
validate the graph, add model metadata, and produce the expected
`[1, 25200, 85]` detection output. A generic `torch.load()` exporter is not as
reliable for these checkpoints.

The equivalent export command used by CodeBuild is:

```bash
python export.py \
  --weights yolov5s.pt \
  --include onnx \
  --opset 17 \
  --imgsz 640 \
  --device cpu
```

## Inference Contract

The application:

- Resizes and letterboxes RGB images to `640 x 640`.
- Normalizes pixels to `[0, 1]`.
- Creates an NCHW `float32` tensor.
- Multiplies objectness and class confidence.
- Applies class-aware non-maximum suppression.
- Maps class IDs to the 80 COCO labels.
- Rescales boxes to the original image.

Detection results also power object counting and detected-scene classification.

## Custom Model Later

After training your own YOLOv5 model, upload `best.pt` to the same S3 prefix:

```powershell
aws s3 cp best.pt s3://YOUR_BUCKET/models/best.pt
```

The same native exporter will package it. If it uses custom classes, replace
the built-in COCO names with labels stored in model metadata or a versioned
labels file.

## Segmentation

The full build also downloads official `yolov5s-seg.pt`, exports it through
YOLOv5 v7.0, and packages `models/segmentation/yolov5s-seg.onnx`. The service
decodes its detection tensor and 32-channel prototype-mask tensor into a
transparent overlay and per-object segment metadata.

YOLOv5 code and pretrained weights are third-party artifacts governed by
Ultralytics' applicable license. Review that license before commercial use.
