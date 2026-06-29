#!/usr/bin/env python3
"""Generate a project-local raster cover for The Amber Signal."""

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
TITLE = "The Amber Signal"
PALETTE = [tuple(c) for c in [[10, 13, 16], [51, 42, 34], [197, 125, 42], [237, 198, 109]]]
SEED = 1572


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

    _gradient(draw, (7, 10, 14), (46, 38, 33))
    for x in range(80, 1580, 140):
        draw.rectangle((x, 1050 + (x % 280), x + 64, 1595), fill=(15, 18, 21, 220))
        if x % 280 == 0:
            draw.rectangle((x + 14, 1100 + (x % 280), x + 48, 1130 + (x % 280)), fill=(237, 198, 109, 90))
    draw.line((800, 1320, 800, 420), fill=(225, 151, 56, 230), width=18)
    draw.polygon([(800, 420), (615, 1320), (985, 1320)], outline=(225, 151, 56, 130), width=8)
    for r in range(150, 850, 115):
        draw.arc((800-r, 600-r, 800+r, 600+r), 212, 328, fill=(237, 198, 109, 150), width=10)
    draw.rounded_rectangle((500, 1080, 1100, 1420), radius=35, fill=(37, 31, 27, 245), outline=(225, 151, 56, 170), width=10)
    for i in range(5):
        x = 590 + i * 95
        draw.ellipse((x, 1160, x + 52, 1212), fill=(237, 198, 109, 95), outline=(237, 198, 109, 170))
    draw.line((585, 1300, 1015, 1300), fill=(237, 198, 109, 120), width=5)
    _label(draw, "DEAD FREQUENCY", 800, 1515, 40, (237, 198, 109, 180))
    draw.rectangle((0, 1600, WIDTH, 1765), fill=(10, 8, 7, 92))


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
