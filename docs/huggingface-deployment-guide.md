# Hugging Face Deployment Guide

The public portfolio application runs on a free Hugging Face Docker Space.
AWS CodeBuild publishes a minimal Space bundle containing the FastAPI source,
Dockerfile, dependencies, model documentation, and generated YOLOv5s ONNX
artifact.

## Create an Account and Token

Create a Hugging Face account and a fine-grained user access token with write
permission for the target Space. Store the token in AWS Secrets Manager; never
commit it or add it as a plaintext CodeBuild variable.

## Space Configuration

CodeBuild can create the Space automatically through `HfApi.create_repo()`.
Alternatively, create it manually with:

```text
Name: mlops-yolov5
SDK: Docker
Hardware: CPU Basic (Free)
Visibility: Public
```

The deployment README sets `sdk: docker` and `app_port: 8000`. The Docker
container runs as user ID 1000, matching the Docker Spaces permission guidance.

## CodeBuild Variables

```text
ENABLE_HF_DEPLOY=true
HF_SPACE_ID=YOUR_HF_USERNAME/mlops-yolov5
HF_TOKEN=<Secrets Manager reference>
```

After the YOLOv5 ONNX export and ECR push, CodeBuild executes:

```bash
python scripts/deploy_to_huggingface.py \
  --repo-id "$HF_SPACE_ID" \
  --model models/object_detection/yolov5s.onnx
```

Uploading the Space bundle creates a new Hub commit, which automatically
rebuilds and restarts the Space.

## Verify

Open:

```text
https://YOUR_HF_USERNAME-mlops-yolov5.hf.space/
https://YOUR_HF_USERNAME-mlops-yolov5.hf.space/health
https://YOUR_HF_USERNAME-mlops-yolov5.hf.space/docs
```

Free Spaces sleep after a period of inactivity and wake when accessed. The
first request after sleeping can take longer.

Official references:

- [Docker Spaces](https://huggingface.co/docs/hub/spaces-sdks-docker)
- [Space hardware](https://huggingface.co/docs/hub/spaces-overview#hardware-resources)
- [Uploading Hub files](https://huggingface.co/docs/huggingface_hub/guides/upload)
- [User access tokens](https://huggingface.co/docs/hub/security-tokens)
