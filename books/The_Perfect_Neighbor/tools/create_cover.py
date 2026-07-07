#!/usr/bin/env python3
"""Cover: The Perfect Neighbor — woman's silhouette at window watching neighbor's house across lawn, twilight blue sky, window warm gold, shadow."""

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import (
    _standard_cover_font,
    _standard_cover_repair_text,
    _standard_cover_wrap,
    _standard_cover_center,
    _standard_cover_title_font,
    _standard_cover_metadata_from_locals,
    _standard_cover_resolve_title,
    _standard_cover_resolve_author,
    _draw_standard_cover_title_panel,
)

W, H = 1600, 2560

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def create_cover(metadata_path: Path, output_path: Path) -> None:
    with open(metadata_path, encoding="utf-8") as f:
        metadata = json.load(f)
    title = metadata["title"]
    author = metadata["author"]
    model = metadata.get("model", "")

    img = Image.new("RGBA", (W, H), (20, 18, 40, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Twilight sky gradient
    for y in range(1300):
        t = y / 1300
        if t < 0.55:
            c = lerp((12, 10, 42), (40, 30, 60), t / 0.55)
        else:
            c = lerp((40, 30, 60), (155, 95, 55), (t - 0.55) / 0.45)
        draw.line((0, y, W, y), fill=(*c, 255))

    # Lawn
    draw.rectangle((0, 1300, W, 1800), fill=(28, 52, 32, 255))
    draw.rectangle((0, 1300, W, 1350), fill=(38, 36, 40, 255))

    # Neighbor's house
    hx, hy = 880, 1000
    draw.rectangle((hx, hy, hx + 440, hy + 320), fill=(68, 60, 50, 255))
    draw.polygon([(hx - 30, hy), (hx + 220, hy - 90), (hx + 470, hy)], fill=(52, 45, 38, 255))
    for wx in [hx + 40, hx + 180, hx + 320]:
        draw.rectangle((wx, hy + 60, wx + 60, hy + 120), fill=(255, 210, 120, 230))
        draw.rectangle((wx, hy + 200, wx + 60, hy + 260), fill=(255, 210, 120, 230))
    for wx in [hx + 40, hx + 180, hx + 320]:
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(g)
        gd.ellipse((wx - 40, hy + 40, wx + 100, hy + 140), fill=(255, 210, 120, 30))
        gd.ellipse((wx - 40, hy + 180, wx + 100, hy + 280), fill=(255, 210, 120, 30))
        g = g.filter(ImageFilter.GaussianBlur(14))
        img = Image.alpha_composite(img, g)
    draw = ImageDraw.Draw(img, "RGBA")

    # POV window frame
    draw.rectangle((0, 300, 500, 1150), fill=(52, 46, 40, 255))
    draw.rectangle((40, 380, 400, 1050), fill=(20, 18, 35, 200))
    draw.line((220, 380, 220, 1050), fill=(58, 52, 48, 255), width=5)
    draw.line((40, 715, 400, 715), fill=(58, 52, 48, 255), width=5)
    draw.rectangle((36, 376, 404, 1054), outline=(48, 42, 38, 255), width=6)

    # Woman silhouette at window
    sx, sy = 260, 650
    draw.ellipse((sx - 20, sy - 32, sx + 20, sy + 10), fill=(6, 4, 10, 235))
    draw.polygon([(sx - 24, sy + 10), (sx + 24, sy + 10), (sx + 32, sy + 190), (sx - 32, sy + 190)], fill=(6, 4, 10, 235))
    draw.line((sx + 24, sy + 40, sx + 60, sy + 85), fill=(6, 4, 10, 235), width=9)
    draw.line((sx - 24, sy + 40, sx - 55, sy + 65), fill=(6, 4, 10, 235), width=7)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(output_path, "PNG")
    print(f"Cover saved to {output_path}")



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    create_cover(args.metadata, args.out)


if __name__ == "__main__":
    main()