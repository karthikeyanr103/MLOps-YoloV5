# Project Overview

## The Problem

Computer vision teams often train models successfully but release them through
manual file copies and one-off server changes. That process is difficult to
repeat, audit, or explain to stakeholders.

## The Solution

MLOps-YoloV5 treats a model upload as a deployment event. The first deployment
uses official pretrained YOLOv5s, so no training is required. AWS services
export and package the model, Docker provides a reproducible runtime, and
FastAPI serves detection and segmentation computer vision use cases through
one application.

## Audience

- **Recruiters and HR:** a concise example of cloud, machine learning, and
  software engineering skills applied to a business workflow.
- **Technical interviewers:** an inspectable design with separate route,
  inference, infrastructure, and deployment responsibilities.
- **Engineers:** a working YOLOv5 ONNX serving pattern that can later accept a
  custom checkpoint through the same S3 event.

## Portfolio Talking Points

- The pipeline is event-driven instead of being manually started.
- Model artifacts and application images are versioned independently.
- Official YOLOv5s weights provide real COCO detection without committing a
  large model binary to Git.
- Detection output is reused for object counting and detected-scene labels.
- Official YOLOv5s-seg weights provide pixel masks through a separate ONNX
  session and NumPy/Pillow mask decoder.
- ONNX metadata is validated so class IDs retain the official 80-label COCO
  order.
- Credentials are externalized, IAM roles are preferred, and large model
  artifacts are excluded from Git.
- Failure notifications and immutable image tags make releases observable and
  recoverable.

## Definition of Done

A deployment is complete when CodeBuild has validated the model, pushed a
versioned image to ECR, published the Docker Space bundle to Hugging Face, and
SNS has delivered the final status. Readiness is verified with `GET /health`.
