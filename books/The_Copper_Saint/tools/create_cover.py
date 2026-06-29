#!/usr/bin/env python3
"""Generate a project-local raster cover for The Copper Saint."""

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
TITLE = "The Copper Saint"
PALETTE = [tuple(c) for c in [[28, 18, 16], [82, 39, 25], [188, 92, 42], [239, 181, 101]]]
SEED = 1607


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

    _gradient(draw, (22, 16, 18), (88, 44, 30))
    for y in range(0, 1765, 90):
        draw.line((0, y, WIDTH, y + rng.randint(-18, 18)), fill=(239, 181, 101, 18), width=2)
    draw.rectangle((170, 1320, 1430, 1605), fill=(32, 24, 22, 220))
    for x in range(220, 1400, 170):
        draw.rectangle((x, 1130, x + 70, 1605), fill=(47, 30, 24, 235))
        draw.pieslice((x - 20, 1065, x + 90, 1175), 180, 360, fill=(47, 30, 24, 235))
    draw.polygon([(370, 1040), (800, 760), (1230, 1040), (1170, 1095), (800, 860), (430, 1095)], fill=(118, 63, 35, 220))
    draw.ellipse((480, 270, 1120, 910), outline=(225, 132, 58, 230), width=34)
    draw.ellipse((545, 335, 1055, 845), outline=(239, 181, 101, 115), width=12)
    draw.rounded_rectangle((570, 740, 1030, 1380), radius=42, fill=(158, 75, 38, 238), outline=(239, 181, 101, 210), width=18)
    draw.rectangle((690, 870, 910, 1295), fill=(52, 28, 22, 190))
    draw.polygon([(800, 495), (930, 1090), (670, 1090)], fill=(236, 163, 82, 88), outline=(245, 204, 134, 185))
    for i in range(7):
        x = 620 + i * 60
        draw.line((x, 780, x - 80, 1330), fill=(255, 202, 128, 55), width=4)
    _label(draw, "FLORENCE", 800, 1510, 42, (218, 170, 104, 170))
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
