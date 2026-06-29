#!/usr/bin/env python3
"""Generate a project-local raster cover for The Rainmaker's Ledger."""

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
TITLE = "The Rainmaker's Ledger"
PALETTE = [tuple(c) for c in [[32, 27, 20], [92, 70, 43], [158, 122, 70], [190, 194, 170]]]
SEED = 2111


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

    _gradient(draw, (37, 32, 24), (122, 92, 55))
    for x in range(80, 1540, 105):
        draw.line((x, 170, x - 95, 1210), fill=(190, 194, 170, 95), width=4)
    draw.polygon([(0, 1210), (WIDTH, 1110), (WIDTH, 1650), (0, 1650)], fill=(84, 64, 38, 235))
    for y in range(1230, 1620, 58):
        draw.line((0, y, WIDTH, y - 95), fill=(174, 139, 83, 70), width=3)
    draw.rounded_rectangle((365, 520, 1235, 1260), radius=22, fill=(204, 177, 122, 232), outline=(61, 42, 26, 220), width=12)
    draw.line((800, 540, 800, 1240), fill=(83, 55, 31, 150), width=8)
    for i in range(11):
        y = 620 + i * 48
        draw.line((450, y, 735, y + rng.randint(-6, 6)), fill=(57, 42, 28, 145), width=4)
        draw.line((865, y, 1160, y + rng.randint(-6, 6)), fill=(57, 42, 28, 145), width=4)
    draw.polygon([(1080, 350), (1340, 420), (1130, 485)], fill=(210, 210, 190, 185), outline=(58, 48, 35, 120))
    draw.line((1110, 420, 960, 710), fill=(210, 210, 190, 105), width=4)
    draw.rectangle((1080, 835, 1150, 1185), outline=(54, 42, 29, 170), width=7)
    _label(draw, "DROUGHT LEDGER", 800, 1450, 42, (224, 201, 143, 180))
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
