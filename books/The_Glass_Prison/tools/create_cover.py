#!/usr/bin/env python3
"""Cover: The Glass Prison — Minimalist glass/steel themed black background with white title, cream panel."""

from __future__ import annotations
import argparse, json, math, random
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


ROOT = Path(__file__).resolve().parents[3]
FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    candidates = [FONT_DIR / name, FONT_DIR / "arialbd.ttf", FONT_DIR / "arial.ttf"]
    for c in candidates:
        if c.exists():
            return ImageFont.truetype(str(c), size)
    return ImageFont.load_default()


def wrap(draw: ImageDraw, text: str, font: ImageFont, max_w: int) -> list[str]:
    words = text.split()
    lines, current = [], []
    for w in words:
        test = " ".join([*current, w])
        if draw.textbbox((0, 0), test, font=font)[2] <= max_w:
            current.append(w)
        else:
            if current:
                lines.append(" ".join(current))
            current = [w]
    if current:
        lines.append(" ".join(current))
    return lines


def centered(draw: ImageDraw, y: int, lines: list[str], font: ImageFont, fill, gap: int) -> int:
    for line in lines:
        bb = draw.textbbox((0, 0), line, font=font)
        draw.text(((W - (bb[2] - bb[0])) // 2, y), line, font=font, fill=fill)
        y += bb[3] - bb[1] + gap
    return y


def make_cover(metadata_path: Path, output_path: Path) -> None:
    meta = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = meta["title"]
    author = meta.get("author", "Barış Kısır")
    model = meta.get("model", "")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Black background with subtle gradient
    for y in range(H):
        t = y / H
        r = int(5 + 15 * t)
        g = int(5 + 15 * t)
        b = int(8 + 20 * t)
        draw.line((0, y, W, y), fill=(min(255, r), min(255, g), min(255, b), 255))

    # Glass/steel grid pattern — horizontal and vertical lines
    grid_color = (60, 65, 80, 60)
    for x in range(0, W, 60):
        draw.line((x, 0, x, H), fill=grid_color, width=1)
    for y in range(0, H, 60):
        draw.line((0, y, W, y), fill=grid_color, width=1)

    # Structural steel beams — thicker verticals
    beam_color = (40, 45, 60, 150)
    for x in [200, 600, 1000, 1400]:
        draw.rectangle((x, 0, x + 8, H), fill=beam_color)

    # Horizontal truss lines
    for y in [400, 800, 1200, 1600]:
        draw.line((0, y, W, y), fill=(60, 65, 80, 100), width=4)

    # Diagonal bracing
    for start_x in [200, 600, 1000, 1400]:
        draw.line((start_x, 0, start_x + 400, 400), fill=(50, 55, 70, 80), width=2)
        draw.line((start_x + 400, 400, start_x, 800), fill=(50, 55, 70, 80), width=2)
        draw.line((start_x, 800, start_x + 400, 1200), fill=(50, 55, 70, 80), width=2)
        draw.line((start_x + 400, 1200, start_x, 1600), fill=(50, 55, 70, 80), width=2)

    # Glass reflections — diagonal white streaks
    for _ in range(12):
        sx = random.randint(100, W - 200)
        sy = random.randint(100, H - 200)
        draw.line((sx, sy, sx + 120, sy + 60), fill=(200, 210, 230, 30), width=3)

    # Central geometric form — diamond/cage
    cx, cy = W // 2, 900
    diamond_size = 200
    draw.polygon([
        (cx, cy - diamond_size),
        (cx + diamond_size, cy),
        (cx, cy + diamond_size),
        (cx - diamond_size, cy),
    ], outline=(120, 130, 150, 120), width=3)

    # Inner diamond
    draw.polygon([
        (cx, cy - diamond_size // 2),
        (cx + diamond_size // 2, cy),
        (cx, cy + diamond_size // 2),
        (cx - diamond_size // 2, cy),
    ], outline=(100, 110, 130, 100), width=2)

    # Faint figure silhouette inside the diamond
    fig_color = (30, 35, 50, 100)
    draw.ellipse((cx - 15, cy - 50, cx + 15, cy - 20), fill=fig_color)
    draw.polygon([(cx - 18, cy - 20), (cx + 18, cy - 20), (cx + 20, cy + 30), (cx - 20, cy + 30)], fill=fig_color)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(output_path, "PNG", optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    mp = ROOT / args.metadata if not args.metadata.is_absolute() else args.metadata
    op = ROOT / args.out if not args.out.is_absolute() else args.out
    make_cover(mp, op)


if __name__ == "__main__":
    main()
