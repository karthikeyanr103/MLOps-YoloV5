"""Send an image to one of the local FastAPI prediction endpoints."""

from __future__ import annotations

import argparse
import json
import mimetypes
from pathlib import Path

import requests


def main() -> None:
    """Build a multipart request and print the formatted API response."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument(
        "--task",
        choices=["classification", "counting", "segmentation", "object-detection"],
        default="object-detection",
    )
    parser.add_argument("--base-url", default="http://localhost:8000")
    args = parser.parse_args()

    endpoint = f"{args.base_url.rstrip('/')}/api/v1/{args.task}/predict"
    content_type = mimetypes.guess_type(args.image.name)[0] or "application/octet-stream"
    with args.image.open("rb") as image_file:
        response = requests.post(
            endpoint,
            files={"file": (args.image.name, image_file, content_type)},
            timeout=120,
        )
    response.raise_for_status()
    print(json.dumps(response.json(), indent=2))


if __name__ == "__main__":
    main()
