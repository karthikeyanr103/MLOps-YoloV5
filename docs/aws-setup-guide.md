# AWS Setup Guide

This guide describes the resources required by the repository. Use one AWS
Region consistently and replace every example identifier.

## 1. Create Storage and Registries

Create a private S3 bucket with versioning, server-side encryption, and public
access blocking. Create an ECR repository with scan-on-push and an image
retention rule. Create an SNS topic and confirm the email subscription before
expecting notifications.

```bash
aws s3api create-bucket --bucket YOUR_UNIQUE_BUCKET --region us-east-1
aws s3api put-bucket-versioning --bucket YOUR_UNIQUE_BUCKET \
  --versioning-configuration Status=Enabled
aws ecr create-repository --repository-name mlops-yolov5 \
  --image-scanning-configuration scanOnPush=true
aws sns create-topic --name mlops-yolov5-deployments
```

For regions other than `us-east-1`, include the appropriate S3 location
constraint during bucket creation.

## 2. Create CodeBuild

Connect the project to this GitHub repository or upload a source archive.

- Build image: current AWS managed Linux standard image
- Environment type: Linux EC2
- Privileged mode: enabled for Docker builds
- Buildspec path: `aws/codebuild/buildspec.yml`
- Service role: permissions from `aws/iam/required-permissions.md`

Set these environment variables:

```text
ECR_REPOSITORY_URI=<your ECR repository URI>
SNS_TOPIC_ARN=<your SNS topic ARN>
MODEL_OUTPUT_PATH=models/object_detection/yolov5s.onnx
YOLOV5_REF=v7.0
ENABLE_HF_DEPLOY=true
HF_SPACE_ID=<your-hf-user>/mlops-yolov5
```

Store `HF_TOKEN` as a Secrets Manager-backed variable. Do not use a plaintext
build variable for a real credential.

## 3. Create Lambda

Package `aws/lambda/trigger_codebuild.py` as the function code. Configure:

```text
Runtime: Python 3.12
Handler: trigger_codebuild.handler
Environment: CODEBUILD_PROJECT_NAME=<project name>
Timeout: 30 seconds
```

Attach a role that permits CloudWatch logging and `codebuild:StartBuild` only
for the deployment project.

## 4. Add the S3 Event

Add an `ObjectCreated` event notification from the model bucket to Lambda.
Filter on the `models/` prefix. S3 only supports one suffix per notification,
so create separate filtered notifications for `.pt`, `.pth`, and `.onnx`, or
leave suffix filtering to the Lambda code.

Grant S3 permission to invoke the function and avoid configuring a trigger on a
bucket that the same function writes into, which can create recursive events.

## 5. Bootstrap YOLOv5s and Observe

No trained model is required. From Windows PowerShell:

```powershell
.\scripts\bootstrap_yolov5_to_s3.ps1 `
  -Bucket "YOUR_UNIQUE_BUCKET" `
  -Region "us-east-1"
```

Then inspect:

1. Lambda CloudWatch logs for the CodeBuild build ID.
2. CodeBuild phase logs for conversion and Docker output.
3. ECR for the immutable image tag.
4. SNS email for the final status.
5. Hugging Face Space build logs.

The script downloads official YOLOv5s v7.0 weights to the temporary directory,
uploads them as `models/yolov5s.pt`, and removes the local temporary file.

## Official References

- [AWS Lambda with S3 events](https://docs.aws.amazon.com/lambda/latest/dg/with-s3.html)
- [CodeBuild Docker image to ECR sample](https://docs.aws.amazon.com/codebuild/latest/userguide/sample-docker.html)
- [SNS email subscriptions](https://docs.aws.amazon.com/sns/latest/dg/sns-email-notifications.html)
