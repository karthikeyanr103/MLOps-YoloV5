# Project Overview

## The Problem

Computer vision teams often train models successfully but release them through
manual file copies and one-off server changes. That process is difficult to
repeat, audit, or explain to stakeholders.

## The Solution

MLOps-YoloV5 treats a model upload as a deployment event. AWS services validate
and package the new model, Docker provides a reproducible runtime, and FastAPI
serves four computer vision use cases through one application.

## Audience

- **Recruiters and HR:** a concise example of cloud, machine learning, and
  software engineering skills applied to a business workflow.
- **Technical interviewers:** an inspectable design with separate route,
  inference, infrastructure, and deployment responsibilities.
- **Engineers:** a starter repository that can be connected to a real model by
  adding ONNX decoding and provisioned cloud resources.

## Portfolio Talking Points

- The pipeline is event-driven instead of being manually started.
- Model artifacts and application images are versioned independently.
- The application works in placeholder mode for demonstrations and documents
  exactly where production model logic belongs.
- Credentials are externalized, IAM roles are preferred, and large model
  artifacts are excluded from Git.
- Failure notifications and immutable image tags make releases observable and
  recoverable.

## Definition of Done

A deployment is complete when CodeBuild has validated the model, pushed a
versioned image to ECR, optionally released it to Heroku, and SNS has delivered
the final status. Application readiness is verified with `GET /health`.
