---
title: MLOps YoloV5
emoji: 🚀
colorFrom: green
colorTo: blue
sdk: docker
app_port: 8000
pinned: false
---

# MLOps-YoloV5 Demo

This Docker Space is automatically published by AWS CodeBuild from the
GitHub-based MLOps-YoloV5 project.

The included `yolov5s.onnx` model is generated from official pretrained
YOLOv5s v7.0 weights and serves object detection, object counting, and
detected-scene classification through FastAPI.

- Application: `/`
- Swagger API: `/docs`
- Health endpoint: `/health`

Segmentation is reserved for a future `yolov5s-seg` integration.
