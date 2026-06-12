"""Publish the built FastAPI application and ONNX model to a Docker Space."""

from __future__ import annotations

import argparse
import os
import shutil
import tempfile
from pathlib import Path

from huggingface_hub import HfApi

PROJECT_ROOT = Path(__file__).parents[1]


def copy_tree(source: Path, destination: Path) -> None:
    """Copy a required project directory into the temporary Space bundle."""
    shutil.copytree(source, destination, dirs_exist_ok=True)


def main() -> None:
    """Create a minimal Docker Space bundle and upload it as one Hub commit."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-id", required=True, help="HF Space ID: user/name")
    parser.add_argument(
        "--model",
        type=Path,
        default=PROJECT_ROOT / "models/object_detection/yolov5s.onnx",
    )
    args = parser.parse_args()
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise ValueError("HF_TOKEN must be supplied through the environment.")

    if not args.model.is_file():
        raise FileNotFoundError(f"Generated ONNX model not found: {args.model}")

    api = HfApi(token=token)
    api.create_repo(
        repo_id=args.repo_id,
        repo_type="space",
        space_sdk="docker",
        exist_ok=True,
    )

    with tempfile.TemporaryDirectory(prefix="mlops-yolov5-space-") as temp_dir:
        bundle = Path(temp_dir)
        copy_tree(PROJECT_ROOT / "app", bundle / "app")
        copy_tree(PROJECT_ROOT / "models", bundle / "models")
        shutil.copy2(PROJECT_ROOT / "docker/Dockerfile", bundle / "Dockerfile")
        shutil.copy2(PROJECT_ROOT / "requirements.txt", bundle / "requirements.txt")
        shutil.copy2(PROJECT_ROOT / "huggingface/README.md", bundle / "README.md")

        destination_model = bundle / "models/object_detection/yolov5s.onnx"
        destination_model.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(args.model, destination_model)

        api.upload_folder(
            repo_id=args.repo_id,
            repo_type="space",
            folder_path=bundle,
            commit_message="Deploy YOLOv5s from AWS CodeBuild",
            delete_patterns=[
                "app/**",
                "models/**",
                "Dockerfile",
                "requirements.txt",
                "README.md",
            ],
        )

    print(f"Published Docker Space: https://huggingface.co/spaces/{args.repo_id}")


if __name__ == "__main__":
    main()
