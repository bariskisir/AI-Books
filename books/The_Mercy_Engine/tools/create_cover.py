#!/usr/bin/env python3
"""Generate a project-local raster cover for The Mercy Engine."""

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
TITLE = "The Mercy Engine"
PALETTE = [tuple(c) for c in [[18, 22, 25], [39, 75, 82], [156, 187, 177], [232, 238, 229]]]
SEED = 1589


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

    _gradient(draw, (18, 22, 25), (42, 80, 86))
    for x in range(160, 1500, 220):
        draw.rectangle((x, 500, x + 120, 1600), fill=(226, 235, 231, 18))
    draw.rounded_rectangle((330, 520, 1270, 1360), radius=46, fill=(224, 234, 229, 215), outline=(63, 105, 110, 210), width=14)
    draw.rounded_rectangle((430, 650, 1170, 1120), radius=26, fill=(15, 27, 30, 245), outline=(156, 187, 177, 180), width=8)
    points = [(455, 910), (575, 910), (625, 815), (690, 1010), (760, 875), (830, 910), (1170, 910)]
    draw.line(points, fill=(156, 235, 203, 235), width=9, joint="curve")
    for i, text in enumerate(["04:12", "07:35", "02:09"]):
        y = 1190 + i * 55
        draw.rectangle((500, y, 1110, y + 36), fill=(39, 75, 82, 150))
        _label(draw, text, 1180, y - 4, 34, (35, 68, 74, 210))
    for a in range(0, 360, 30):
        x = 800 + math.cos(math.radians(a)) * 500
        y = 940 + math.sin(math.radians(a)) * 500
        draw.line((800, 940, x, y), fill=(232, 238, 229, 28), width=5)
    draw.rectangle((690, 1360, 910, 1540), fill=(50, 92, 96, 220))
    _label(draw, "TRIAGE BAY", 800, 1510, 42, (232, 238, 229, 185))
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
