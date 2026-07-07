#!/usr/bin/env python3
"""Cover: The Radio Operator — woman in WAC uniform with radio headphones, green glow of vacuum tubes on face, dark sepia tones."""

from __future__ import annotations

import argparse
import json
import math
import random
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

WIDTH, HEIGHT = 1600, 2560

def create_cover(metadata_path: Path, output_path: Path) -> None:
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    title = metadata["title"]
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (30, 28, 20, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Dark sepia gradient
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(75 * (1 - ratio) + 40 * ratio)
        g = int(65 * (1 - ratio) + 30 * ratio)
        b = int(42 * (1 - ratio) + 18 * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255))

    # Vignette
    for r2 in range(900, 0, -20):
        draw.ellipse([WIDTH // 2 - r2, HEIGHT // 2 - r2, WIDTH // 2 + r2, HEIGHT // 2 + r2], outline=(0, 0, 0, max(0, 30 - r2 // 30)), width=15)

    # Radio equipment
    rx, ry = 350, 800
    draw.rounded_rectangle([rx, ry, rx + 900, ry + 550], radius=12, fill=(55, 50, 40, 255), outline=(130, 120, 95, 255), width=3)
    for i in range(12):
        draw.rectangle([rx + 60, ry + 40 + i * 16, rx + 200, ry + 40 + i * 16 + 5], fill=(90, 85, 72, 255))
        draw.rectangle([rx + 220, ry + 40 + i * 16, rx + 360, ry + 40 + i * 16 + 5], fill=(90, 85, 72, 255))
    for dcx, dcy in [(rx + 500, ry + 80), (rx + 680, ry + 80), (rx + 500, ry + 280), (rx + 680, ry + 280)]:
        draw.ellipse([dcx - 50, dcy - 50, dcx + 50, dcy + 50], fill=(28, 26, 22, 255), outline=(150, 140, 115, 255), width=3)
        draw.ellipse([dcx - 38, dcy - 38, dcx + 38, dcy + 38], fill=(48, 46, 38, 255), outline=(110, 100, 85, 255), width=2)

    # Green glow from vacuum tubes
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([rx + 40, ry + 440, rx + 80, ry + 500], fill=(40, 220, 80, 150))
    gd.ellipse([rx + 840, ry + 440, rx + 880, ry + 500], fill=(40, 220, 80, 150))
    gd.ellipse([rx + 20, ry + 410, rx + 100, ry + 530], fill=(40, 200, 70, 60))
    gd.ellipse([rx + 820, ry + 410, rx + 900, ry + 530], fill=(40, 200, 70, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Woman in WAC uniform with headphones
    wx, wy = WIDTH // 2 - 280, 700
    # Head
    draw.ellipse([wx - 28, wy - 38, wx + 28, wy + 18], fill=(18, 16, 10, 235))
    # WAC cap
    draw.polygon([(wx - 30, wy - 33), (wx + 30, wy - 33), (wx + 36, wy - 48), (wx - 36, wy - 48)], fill=(38, 52, 32, 235))
    draw.ellipse([wx - 28, wy - 52, wx + 28, wy - 33], fill=(38, 52, 32, 235))
    # Headphones
    draw.arc([wx - 48, wy - 48, wx + 48, wy + 28], 180, 360, fill=(48, 42, 32, 235), width=10)
    draw.ellipse([wx - 42, wy - 8, wx - 14, wy + 22], fill=(38, 36, 28, 235))
    draw.ellipse([wx + 14, wy - 8, wx + 42, wy + 22], fill=(38, 36, 28, 235))
    # Body in uniform
    draw.polygon([(wx - 32, wy + 18), (wx + 32, wy + 18), (wx + 45, wy + 280), (wx - 45, wy + 280)], fill=(50, 65, 42, 235))
    draw.polygon([(wx - 32, wy + 18), (wx + 32, wy + 18), (wx + 28, wy + 55), (wx - 28, wy + 55)], fill=(60, 75, 52, 235))

    # Green glow on face
    fg = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    fgd = ImageDraw.Draw(fg)
    fgd.ellipse([wx - 35, wy - 28, wx + 35, wy + 14], fill=(40, 220, 80, 50))
    fg = fg.filter(ImageFilter.GaussianBlur(14))
    img = Image.alpha_composite(img, fg)

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
