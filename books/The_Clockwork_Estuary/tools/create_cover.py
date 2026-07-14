#!/usr/bin/env python3
"""Build only The Clockwork Estuary cover from its generated artwork."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel


ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560
ART_PATH = Path(__file__).with_name("cover_art.png")


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    with Image.open(ART_PATH) as source:
        image = ImageOps.fit(
            source.convert("RGB"), (W, H),
            method=Image.Resampling.LANCZOS, centering=(0.5, 0.5),
        ).convert("RGBA")

    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(shade, "RGBA")
    for y in range(680):
        draw.line((0, y, W, y), fill=(3, 10, 17, int(155 * (1 - y / 680))))
    for y in range(2060, H):
        draw.line((0, y, W, y), fill=(3, 9, 14, int(25 + 120 * ((y - 2060) / 500))))
    image = Image.alpha_composite(image, shade.filter(ImageFilter.GaussianBlur(2)))
    _draw_standard_cover_title_panel(
        image, metadata["title"], metadata.get("author", "Barış Kısır"), metadata.get("model", "")
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(output_path, "PNG", optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    metadata_path = ROOT / args.metadata if not args.metadata.is_absolute() else args.metadata
    output_path = ROOT / args.out if not args.out.is_absolute() else args.out
    make_cover(metadata_path, output_path)


if __name__ == "__main__":
    main()
