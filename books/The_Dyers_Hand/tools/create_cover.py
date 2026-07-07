#!/usr/bin/env python3
"""Generate a project-local raster cover for The Dyer's Hand."""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

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


WIDTH = 1600
HEIGHT = 2560
TITLE = "The Dyer's Hand"
PALETTE = [tuple(c) for c in [[14, 18, 32], [28, 26, 52], [38, 38, 82], [120, 140, 195]]]
SEED = 1954


def _gradient(draw, top, bottom):
    for y in range(HEIGHT):
        t = y / max(1, HEIGHT - 1)
        draw.line((0, y, WIDTH, y), fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))


def _label(draw, text, cx, y, size, fill):
    font = _standard_cover_font("arialbd.ttf", size)
    box = draw.textbbox((0, 0), text, font=font)
    draw.text((cx - (box[2] - box[0]) // 2, y), text, font=font, fill=fill)


def _draw_scene(draw, image):
    rng = random.Random(SEED)

    # Deep indigo sky gradient
    _gradient(draw, (10, 12, 28), (25, 20, 55))
    for y in range(300, 900, 3):
        t = (y - 300) / 600.0
        alpha = int(30 * (1 - t))
        if alpha > 0:
            draw.line((0, y, WIDTH, y), fill=(60, 55, 110, alpha), width=3)

    # Stars
    for _ in range(80):
        x = rng.randint(80, 1520)
        y = rng.randint(60, 700)
        sz = rng.randint(1, 3)
        draw.ellipse((x - sz, y - sz, x + sz, y + sz), fill=(200, 210, 240, rng.randint(80, 200)))

    # Moon crescent
    draw.ellipse((1200, 100, 1400, 300), fill=(220, 215, 200, 180))
    draw.ellipse((1235, 80, 1435, 320), fill=(15, 14, 38, 235))

    # Fez medina skyline — minarets and flat rooftops
    skyline = (12, 10, 18, 245)
    draw.rectangle((0, 1050, WIDTH, 1220), fill=skyline)
    # Minaret
    for x, h in [(180, 350), (350, 280), (520, 390), (720, 320), (950, 360), (1150, 300), (1380, 370)]:
        draw.rectangle((x - 8, 1050 - h, x + 8, 1050), fill=skyline)
        draw.rectangle((x - 14, 1050 - h + 60, x + 14, 1050 - h + 66), fill=skyline)
        draw.polygon([(x, 1050 - h - 25), (x - 5, 1050 - h), (x + 5, 1050 - h)], fill=skyline)

    # Domes
    for cx, r in [(280, 70), (620, 90), (850, 75), (1080, 85)]:
        draw.ellipse((cx - r, 1050 - r * 2, cx + r, 1050), fill=skyline)

    # Courtyard / ground
    draw.rectangle((0, 1220, WIDTH, 1500), fill=(45, 30, 18, 235))

    # Dye vats — circular stone basins with indigo water
    vat_color = (20, 30, 80, 220)
    for cx, cy, r in [(350, 1320, 70), (650, 1280, 85), (950, 1350, 65), (1250, 1290, 75)]:
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(38, 30, 22, 240))
        draw.ellipse((cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6), fill=vat_color)
        # Indigo film shimmer on surface
        draw.ellipse((cx - r//2, cy - r//2, cx + r//2, cy + r//2), fill=(55, 50, 130, 90))
        # Reflection
        draw.ellipse((cx - r//3, cy - r//3 + 4, cx + r//3, cy + r//3 + 8), fill=(120, 130, 190, 60))

    # Blue hands emerging from a vat — the central image
    hx, hy = 800, 1220
    # Arms
    draw.rectangle((hx - 70, hy, hx - 30, hy + 80), fill=(190, 170, 140, 200))
    draw.rectangle((hx + 30, hy, hx + 70, hy + 80), fill=(190, 170, 140, 200))
    # Hands (stylized, blue)
    draw.ellipse((hx - 85, hy + 65, hx - 15, hy + 120), fill=(35, 40, 115, 220))
    draw.ellipse((hx + 15, hy + 65, hx + 85, hy + 120), fill=(35, 40, 115, 220))
    # Indigo dripping from hands
    for _ in range(25):
        dx = hx + rng.randint(-70, 70)
        dy = hy + 110 + rng.randint(0, 200)
        dw = rng.randint(1, 3)
        draw.line((dx, dy, dx, dy + rng.randint(8, 25)), fill=(40, 45, 130, rng.randint(60, 150)), width=dw)

    # Wool skeins hanging to dry
    for sx in [250, 400, 1100, 1400]:
        for sy in [1100, 1140, 1180]:
            alpha = rng.randint(80, 160)
            draw.line((sx, 1000, sx + rng.randint(-15, 15), sy + 40), fill=(35, 40, 120, alpha), width=4)

    # Location label
    _label(draw, "FEZ", 800, 1515, 40, (170, 160, 210, 170))

    draw.rectangle((0, 1600, WIDTH, 1765), fill=(8, 6, 10, 75))


def create_cover(metadata_path, out_path):
    metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    title = metadata.get("title", TITLE)
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")
    image = Image.new("RGB", (WIDTH, HEIGHT), PALETTE[0])
    draw = ImageDraw.Draw(image, "RGBA")
    _draw_scene(draw, image)
    _draw_standard_cover_title_panel(image, title, author, metadata.get("model", ""))
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    image.save(out_path)



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    create_cover(args.metadata, args.out)


if __name__ == "__main__":
    main()
