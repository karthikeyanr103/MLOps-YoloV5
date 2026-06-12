"""Unit tests for the S3-to-CodeBuild Lambda function."""

import importlib.util
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

TRIGGER_PATH = (
    Path(__file__).parents[1] / "aws" / "lambda" / "trigger_codebuild.py"
)


def load_trigger():
    """Import the Lambda module from its deployment-oriented directory."""
    spec = importlib.util.spec_from_file_location("trigger_codebuild", TRIGGER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@patch.dict(os.environ, {"CODEBUILD_PROJECT_NAME": "portfolio-deploy"})
@patch("boto3.client")
def test_supported_model_starts_build(client_factory) -> None:
    client = MagicMock()
    client.start_build.return_value = {"build": {"id": "build-123"}}
    client_factory.return_value = client
    trigger = load_trigger()

    event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "model-bucket"},
                    "object": {
                        "key": "models/best%20model.onnx",
                        "versionId": "version-1",
                    },
                }
            }
        ]
    }
    result = trigger.handler(event, None)

    assert result["started_builds"] == ["build-123"]
    overrides = client.start_build.call_args.kwargs["environmentVariablesOverride"]
    assert overrides[1]["value"] == "models/best model.onnx"
    assert overrides[2]["value"] == "version-1"


@patch.dict(os.environ, {"CODEBUILD_PROJECT_NAME": "portfolio-deploy"})
@patch("boto3.client")
def test_unsupported_object_is_ignored(client_factory) -> None:
    trigger = load_trigger()
    event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "model-bucket"},
                    "object": {"key": "models/readme.txt"},
                }
            }
        ]
    }
    result = trigger.handler(event, None)

    assert result == {
        "started_builds": [],
        "ignored_objects": ["models/readme.txt"],
    }
    client_factory.assert_not_called()
