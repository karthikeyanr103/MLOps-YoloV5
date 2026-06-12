# Troubleshooting

## API Does Not Start

**Symptom:** `ModuleNotFoundError` or multipart upload errors.

Install the pinned dependencies in the active environment:

```bash
python -m pip install -r requirements-dev.txt
```

Start from the repository root with `uvicorn app.main:app --reload`.

## Endpoint Says YOLOv5s Is Not Installed

Run `scripts/bootstrap_yolov5_to_s3.ps1` to create the first deployment. The
resulting image must contain
`models/object_detection/yolov5s.onnx`. Check `GET /health` and confirm
`MODEL_ROOT` points to the parent model directory.

## ONNX Input Shape Error

The included preprocessor emits `[1, 3, 640, 640]` float32 input. Inspect the
model with Netron or `session.get_inputs()`, then update size, layout, and
normalization in `app/services/preprocessing.py`.

## Segmentation Model Is Not Installed

Segmentation uses a separate `yolov5s-seg` export and prototype-mask decoder.
Run a new full CodeBuild deployment after pulling the latest repository
changes; a UI-only deployment intentionally reuses the models already stored
in the Space and cannot add a missing segmentation model.

## Lambda Does Not Run

- Confirm the S3 event uses the `models/` prefix.
- Confirm S3 has permission to invoke the function.
- Inspect Lambda CloudWatch logs.
- Verify that upload and Lambda resources are in compatible regions.
- Do not test with an unsupported file extension.

## CodeBuild Cannot Build Docker

Enable privileged mode on the CodeBuild environment. Ensure the service role
can request an ECR authorization token and push image layers. Confirm Docker is
available with `docker version` in the build log.

## Docker Hub Returns 429 Too Many Requests

CodeBuild workers share public IP addresses and can exhaust Docker Hub's
anonymous pull quota. The project uses the Docker Official Images mirror at
`public.ecr.aws/docker/library/python:3.11-slim`, so no Docker Hub login is
required. Push the current Dockerfile to GitHub and start a new build.

## YOLOv5 Export Cannot Import pkg_resources

YOLOv5 v7.0 imports `pkg_resources`, which was removed from newer setuptools
releases. The build pins `setuptools<81` for compatibility. Confirm the latest
`aws/codebuild/buildspec.yml` and `requirements-conversion.txt` are pushed to
GitHub before starting another build.

## ECR Login or Push Fails

Check `AWS_DEFAULT_REGION`, the repository URI, IAM permissions, and whether the
repository exists. The registry and repository region must match the login
command.

## SNS Email Never Arrives

Open the subscription confirmation email and confirm it. Check spam filtering,
the topic ARN in CodeBuild, and `sns:Publish` on the build role.

## Hugging Face Space Deployment Fails

- Confirm `HF_SPACE_ID` uses `username/space-name`.
- Confirm `HF_TOKEN` is a write-capable token supplied from Secrets Manager.
- Confirm the Space SDK is Docker and `app_port` is `8000`.
- Review the Space build and container logs.
- Remember that free Spaces sleep when unused and can have a cold start.

## Upload Script Has No Credentials

Configure an AWS profile with `aws configure` or use an IAM role. Never paste
access keys into `.env.example`, source files, issues, or screenshots.
