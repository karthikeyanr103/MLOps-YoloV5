"""Publish the built FastAPI application and ONNX model to a Docker Space."""

from __future__ import annotations

import argparse
import os
import shutil
import tempfile
from pathlib import Path

from huggingface_hub import HfApi

PROJECT_ROOT = Path(__file__).parents[1]
REQUIRED_UI_FILES = {
    "app/static/samples/classification.jpg",
    "app/static/samples/counting.jpg",
    "app/static/samples/object-detection.jpg",
    "app/static/samples/segmentation.jpg",
    "app/templates/index.html",
    "app/static/css/style.css",
    "app/static/js/main.js",
}
REQUIRED_MODEL_FILES = {
    "models/object_detection/yolov5s.onnx",
    "models/segmentation/yolov5s-seg.onnx",
}


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
    parser.add_argument(
        "--segmentation-model",
        type=Path,
        default=PROJECT_ROOT / "models/segmentation/yolov5s-seg.onnx",
    )
    parser.add_argument(
        "--reuse-space-model",
        action="store_true",
        help="Update application files without replacing the model in the Space.",
    )
    args = parser.parse_args()
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise ValueError("HF_TOKEN must be supplied through the environment.")

    if not args.reuse_space_model:
        missing_models = [
            model
            for model in (args.model, args.segmentation_model)
            if not model.is_file()
        ]
        if missing_models:
            raise FileNotFoundError(
                "Generated ONNX model not found: "
                + ", ".join(str(model) for model in missing_models)
            )
    missing_ui_files = [
        relative_path
        for relative_path in REQUIRED_UI_FILES
        if not (PROJECT_ROOT / relative_path).is_file()
    ]
    if missing_ui_files:
        raise FileNotFoundError(
            f"Required UI files are missing: {', '.join(sorted(missing_ui_files))}"
        )

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

        delete_patterns = [
            "app/**",
            "Dockerfile",
            "requirements.txt",
            "README.md",
        ]
        if not args.reuse_space_model:
            destination_model = bundle / "models/object_detection/yolov5s.onnx"
            destination_model.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(args.model, destination_model)
            destination_segmentation_model = (
                bundle / "models/segmentation/yolov5s-seg.onnx"
            )
            destination_segmentation_model.parent.mkdir(
                parents=True,
                exist_ok=True,
            )
            shutil.copy2(args.segmentation_model, destination_segmentation_model)
            delete_patterns.append("models/**")

        api.upload_folder(
            repo_id=args.repo_id,
            repo_type="space",
            folder_path=bundle,
            commit_message=(
                "Deploy application update from AWS CodeBuild"
                if args.reuse_space_model
                else "Deploy YOLOv5s model and application from AWS CodeBuild"
            ),
            delete_patterns=delete_patterns,
        )

    remote_files = set(api.list_repo_files(args.repo_id, repo_type="space"))
    required_remote_files = set(REQUIRED_UI_FILES)
    if not args.reuse_space_model:
        required_remote_files.update(REQUIRED_MODEL_FILES)
    missing_remote_files = required_remote_files - remote_files
    if missing_remote_files:
        raise RuntimeError(
            "Hugging Face deployment is missing required UI files: "
            + ", ".join(sorted(missing_remote_files))
        )

    print(f"Published Docker Space: https://huggingface.co/spaces/{args.repo_id}")


if __name__ == "__main__":
    main()
