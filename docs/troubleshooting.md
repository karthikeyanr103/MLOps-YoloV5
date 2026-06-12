# Troubleshooting

## API Does Not Start

**Symptom:** `ModuleNotFoundError` or multipart upload errors.

Install the pinned dependencies in the active environment:

```bash
python -m pip install -r requirements-dev.txt
```

Start from the repository root with `uvicorn app.main:app --reload`.

## Endpoint Returns Placeholder Data

This is expected when `models/<task>/model.onnx` is absent. Check `GET /health`
and confirm `MODEL_ROOT` points to the parent model directory. Restart the
process after adding a model because sessions are cached.

## ONNX Input Shape Error

The included preprocessor emits `[1, 3, 640, 640]` float32 input. Inspect the
model with Netron or `session.get_inputs()`, then update size, layout, and
normalization in `app/services/preprocessing.py`.

## ONNX Output Is Raw

The repository cannot infer a model's label map or tensor contract. Implement
model-specific decoding in `app/services/postprocessing.py`, including NMS,
coordinate scaling, masks, or class names.

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

## ECR Login or Push Fails

Check `AWS_DEFAULT_REGION`, the repository URI, IAM permissions, and whether the
repository exists. The registry and repository region must match the login
command.

## SNS Email Never Arrives

Open the subscription confirmation email and confirm it. Check spam filtering,
the topic ARN in CodeBuild, and `sns:Publish` on the build role.

## Heroku Release Fails

- Ensure the app uses the `container` stack.
- Build an `x86_64` image, not ARM64.
- Confirm `HEROKU_APP_NAME` and the API key.
- Confirm the process listens on `$PORT`.
- Run `heroku logs --tail --app <name>`.
- Keep the image small enough to start within the dyno boot limit.

## Upload Script Has No Credentials

Configure an AWS profile with `aws configure` or use an IAM role. Never paste
access keys into `.env.example`, source files, issues, or screenshots.
