"""Start an AWS CodeBuild deployment when a model is uploaded to S3."""

from __future__ import annotations

import json
import logging
import os
from urllib.parse import unquote_plus

import boto3

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
SUPPORTED_MODEL_SUFFIXES = (".pt", ".pth", ".onnx")


def _codebuild_client():
    """Create the client lazily to keep local tests independent from AWS."""
    return boto3.client("codebuild")


def handler(event: dict, _context) -> dict:
    """Start one CodeBuild execution per supported S3 model record."""
    project_name = os.environ["CODEBUILD_PROJECT_NAME"]
    started_builds: list[str] = []
    ignored_objects: list[str] = []

    for record in event.get("Records", []):
        bucket = record["s3"]["bucket"]["name"]
        key = unquote_plus(record["s3"]["object"]["key"])
        version_id = record["s3"]["object"].get("versionId", "")

        if not key.lower().endswith(SUPPORTED_MODEL_SUFFIXES):
            ignored_objects.append(key)
            continue

        response = _codebuild_client().start_build(
            projectName=project_name,
            environmentVariablesOverride=[
                {"name": "SOURCE_MODEL_BUCKET", "value": bucket, "type": "PLAINTEXT"},
                {"name": "SOURCE_MODEL_KEY", "value": key, "type": "PLAINTEXT"},
                {"name": "SOURCE_MODEL_VERSION", "value": version_id, "type": "PLAINTEXT"},
            ],
        )
        build_id = response["build"]["id"]
        started_builds.append(build_id)
        LOGGER.info("Started build %s for s3://%s/%s", build_id, bucket, key)

    result = {"started_builds": started_builds, "ignored_objects": ignored_objects}
    LOGGER.info("Invocation result: %s", json.dumps(result))
    return result
