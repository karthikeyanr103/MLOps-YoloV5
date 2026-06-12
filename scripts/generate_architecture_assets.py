"""Generate lightweight static and animated architecture diagrams."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = Path(__file__).parents[1] / "architecture"
WIDTH, HEIGHT = 1600, 720
NODES = [
    ("MODEL\nUPLOAD", "S3", "#e85d3f"),
    ("EVENT", "LAMBDA", "#ef9f36"),
    ("BUILD", "CODEBUILD", "#337a68"),
    ("MODEL", "ONNX", "#315b76"),
    ("IMAGE", "DOCKER", "#287fbe"),
    ("REGISTRY", "ECR", "#8856a7"),
    ("STATUS", "SNS", "#bf4778"),
    ("DEPLOY", "HF SPACE", "#7053a0"),
    ("INFERENCE", "FASTAPI", "#168f79"),
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a common Windows font and fall back to Pillow's bundled font."""
    name = "arialbd.ttf" if bold else "arial.ttf"
    try:
        return ImageFont.truetype(name, size=size)
    except OSError:
        return ImageFont.load_default()


def draw_frame(active_index: int | None = None) -> Image.Image:
    """Draw the full pipeline and optionally highlight one stage."""
    image = Image.new("RGB", (WIDTH, HEIGHT), "#f4f1e9")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, WIDTH, 140), fill="#123f35")
    draw.text((70, 40), "MLOps-YoloV5", fill="white", font=font(48, bold=True))
    draw.text(
        (70, 99),
        "EVENT-DRIVEN MODEL DELIVERY  |  AWS + ONNX + DOCKER + HUGGING FACE",
        fill="#e8b09e",
        font=font(19, bold=True),
    )

    margin, gap = 55, 18
    node_width = (WIDTH - 2 * margin - gap * (len(NODES) - 1)) // len(NODES)
    top, bottom = 265, 470
    centers = []

    for index, (eyebrow, label, color) in enumerate(NODES):
        left = margin + index * (node_width + gap)
        right = left + node_width
        center = ((left + right) // 2, (top + bottom) // 2)
        centers.append(center)
        if index == active_index:
            draw.rounded_rectangle(
                (left - 8, top - 8, right + 8, bottom + 8),
                radius=16,
                fill="#f3c45b",
            )
        draw.rounded_rectangle((left, top, right, bottom), radius=12, fill=color)
        draw.multiline_text(
            (center[0], top + 35),
            eyebrow,
            fill="#ffffff",
            font=font(14, bold=True),
            anchor="ma",
            align="center",
            spacing=4,
        )
        draw.text(
            (center[0], bottom - 60),
            label,
            fill="#ffffff",
            font=font(19, bold=True),
            anchor="mm",
        )

    for start, end in zip(centers, centers[1:]):
        draw.line((start[0] + node_width // 2, start[1], end[0] - node_width // 2, end[1]), fill="#263d37", width=5)
        draw.polygon(
            [
                (end[0] - node_width // 2, end[1]),
                (end[0] - node_width // 2 - 12, end[1] - 8),
                (end[0] - node_width // 2 - 12, end[1] + 8),
            ],
            fill="#263d37",
        )

    draw.text(
        (WIDTH // 2, 565),
        "Upload model  >  convert and package  >  publish image  >  notify  >  serve predictions",
        fill="#183a32",
        font=font(24, bold=True),
        anchor="mm",
    )
    draw.text(
        (WIDTH // 2, 625),
        "Classification  |  Counting  |  Segmentation  |  Object Detection",
        fill="#5f6d68",
        font=font(21),
        anchor="mm",
    )
    return image


def main() -> None:
    """Write the PNG overview and a compact looping GIF animation."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    draw_frame().save(OUTPUT_DIR / "workflow-diagram.png", optimize=True)
    frames = [draw_frame(index) for index in range(len(NODES))]
    frames[0].save(
        OUTPUT_DIR / "animated-workflow.gif",
        save_all=True,
        append_images=frames[1:],
        duration=550,
        loop=0,
        optimize=True,
    )
    print(f"Generated architecture assets in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
