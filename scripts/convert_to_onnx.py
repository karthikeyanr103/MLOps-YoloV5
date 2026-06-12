"""Convert a TorchScript or compatible PyTorch checkpoint to ONNX."""

from __future__ import annotations

import argparse
from pathlib import Path


def load_model(path: Path):
    """Load TorchScript first, then fall back to a checkpoint containing a module."""
    import torch

    try:
        return torch.jit.load(str(path), map_location="cpu")
    except RuntimeError:
        checkpoint = torch.load(str(path), map_location="cpu", weights_only=False)
        if isinstance(checkpoint, torch.nn.Module):
            return checkpoint
        if isinstance(checkpoint, dict) and isinstance(checkpoint.get("model"), torch.nn.Module):
            return checkpoint["model"]
        raise ValueError(
            "Unsupported checkpoint. Export TorchScript or adapt load_model() for "
            "the training repository's model class."
        )


def main() -> None:
    """Export a validated model using a standard image tensor contract."""
    import onnx
    import torch

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--task",
        choices=["classification", "counting", "segmentation", "object_detection"],
        default="object_detection",
    )
    parser.add_argument("--image-size", type=int, default=640)
    parser.add_argument("--opset", type=int, default=17)
    args = parser.parse_args()

    if not args.input.is_file():
        raise FileNotFoundError(f"Input model not found: {args.input}")
    model = load_model(args.input).float().eval()
    sample = torch.zeros(1, 3, args.image_size, args.image_size)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    torch.onnx.export(
        model,
        sample,
        str(args.output),
        input_names=["images"],
        output_names=["predictions"],
        dynamic_axes={"images": {0: "batch", 2: "height", 3: "width"}},
        opset_version=args.opset,
        do_constant_folding=True,
    )
    onnx.checker.check_model(onnx.load(str(args.output)))
    print(f"Exported {args.task} model to {args.output}")


if __name__ == "__main__":
    main()
