# Architecture Explanation

## Executive Summary

MLOps-YoloV5 separates model training from model delivery. A data scientist
publishes a versioned model artifact; managed AWS services perform conversion,
packaging, notification, and deployment. The FastAPI application exposes one
stable interface even as model files change.

## End-to-End Flow

1. **Model upload:** A trained `.pt`, `.pth`, or `.onnx` file is uploaded under
   the S3 `models/` prefix. S3 versioning should be enabled so every release can
   be traced and recovered.
2. **Event trigger:** S3 sends an `ObjectCreated` event to Lambda. The function
   URL-decodes the object key, rejects unsupported extensions, and passes the
   bucket, key, and version to CodeBuild.
3. **Build isolation:** CodeBuild starts a clean build environment. It downloads
   the exact model version referenced by Lambda rather than relying on a mutable
   local file.
4. **Model conversion:** Existing ONNX files are copied directly. PyTorch
   artifacts are exported with a standard image tensor contract and validated
   by the ONNX checker.
5. **Container build:** The model and FastAPI source are packaged into an
   immutable Docker image. The image uses ONNX Runtime for portable CPU
   inference and reads Heroku's dynamic `$PORT`.
6. **Image registry:** CodeBuild authenticates with ECR and pushes a tag that
   includes the build number and timestamp. This makes releases traceable and
   supports rollback to an earlier image.
7. **Notification:** SNS publishes start, success, or failure messages. Email,
   SMS, chat integrations, or operations systems can subscribe to the topic.
8. **Heroku release:** When enabled, CodeBuild tags the built image for the
   Heroku registry, pushes it, and creates a `web` process release.
9. **Inference:** Users upload an image through the web interface or REST API.
   FastAPI validates it, preprocessing creates an NCHW tensor, ONNX Runtime runs
   inference, and task-aware postprocessing formats the response.

## Why These Services

| Component | Responsibility | Design benefit |
| --- | --- | --- |
| S3 | Model artifact registry and event source | Durable, versioned, decoupled |
| Lambda | Lightweight pipeline trigger | No always-on orchestration server |
| CodeBuild | Conversion and container build | Managed, auditable build isolation |
| ONNX | Portable model format | Training and serving frameworks are decoupled |
| ECR | Container image registry | Versioning, scanning, and AWS IAM integration |
| SNS | Deployment status fan-out | Operations visibility without tight coupling |
| Heroku | Public application runtime | Simple portfolio hosting and HTTPS endpoint |
| FastAPI | HTTP and browser interface | Validation, async uploads, automatic docs |

## Failure and Recovery

Build failures stop before release and produce an SNS notification. Existing
Heroku releases remain available because a failed build never replaces the
running image. Operators can inspect CodeBuild logs, fix the model or source,
and upload a new artifact. Rollback is performed by releasing a previously
known ECR/Heroku image rather than modifying the model in a running container.

## Security Boundaries

S3 remains private, Lambda can only start the named project, and CodeBuild
receives only the S3, ECR, logging, and SNS permissions it needs. AWS workloads
use IAM roles. Heroku API credentials must be stored as secret build variables
or in AWS Secrets Manager and must never be committed.
