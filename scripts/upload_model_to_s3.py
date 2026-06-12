"""Upload a model artifact to the S3 prefix monitored by Lambda."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import boto3


def main() -> None:
    """Validate and upload the model with useful deployment metadata."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", type=Path, help="Path to a .pt, .pth, or .onnx model")
    parser.add_argument("--bucket", required=True, help="Destination S3 bucket")
    parser.add_argument("--prefix", default="models", help="Trigger prefix in S3")
    parser.add_argument("--region", default=None, help="Optional AWS region override")
    args = parser.parse_args()

    model = args.model.resolve()
    if not model.is_file():
        raise FileNotFoundError(f"Model not found: {model}")
    if model.suffix.lower() not in {".pt", ".pth", ".onnx"}:
        raise ValueError("Model must use the .pt, .pth, or .onnx extension.")

    checksum = hashlib.sha256(model.read_bytes()).hexdigest()
    key = f"{args.prefix.strip('/')}/{model.name}"
    boto3.client("s3", region_name=args.region).upload_file(
        str(model),
        args.bucket,
        key,
        ExtraArgs={"Metadata": {"sha256": checksum}},
    )
    print(f"Uploaded {model.name} to s3://{args.bucket}/{key}")
    print(f"SHA-256: {checksum}")


if __name__ == "__main__":
    main()
