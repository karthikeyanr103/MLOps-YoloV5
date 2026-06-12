# UI-Only Hugging Face Deployment

Use this path for HTML, CSS, JavaScript, FastAPI route, preprocessing,
postprocessing, or dependency changes that remain compatible with the existing
YOLOv5s ONNX model.

The UI build:

- Pulls the latest source from GitHub.
- Reuses `models/object_detection/yolov5s.onnx` already stored in the Space.
- Uploads the application, Dockerfile, requirements, and Space README.
- Skips S3, Lambda, YOLO export, Docker build, ECR, and SNS.

## Create the CodeBuild Project

Create a second project:

```text
Project name: mlops-yolov5-ui-deploy
Source: same GitHub repository and connection
Branch: main
Buildspec: aws/codebuild/buildspec-ui.yml
Privileged mode: disabled
Service role: existing mlops-yolov5-codebuild-role
```

Environment variables:

```text
HF_SPACE_ID=YOUR_HF_USERNAME/mlops-yolov5
HF_TOKEN=<Secrets Manager reference>
```

## Automatic GitHub Deployment

Enable a webhook on this UI project:

```text
Event type: PUSH
Branch filter: ^refs/heads/main$
```

Every push to `main` will then update the Hugging Face Space without rebuilding
YOLOv5.

## Important Limitation

Run the full S3-triggered pipeline at least once before using the UI-only
project. The Space must already contain `yolov5s.onnx`.

Use the full pipeline whenever model weights, model input/output structure, or
the generated ONNX artifact changes.
