#!/usr/bin/env python3
"""Generate a project-local raster cover for The Paper Moon Conspiracy."""

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
TITLE = "The Paper Moon Conspiracy"
PALETTE = [tuple(c) for c in [[22, 21, 31], [68, 60, 73], [155, 133, 99], [236, 214, 169]]]
SEED = 2538


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

    _gradient(draw, (19, 18, 29), (72, 62, 72))
    draw.ellipse((575, 175, 1065, 665), fill=(236, 214, 169, 230))
    draw.ellipse((690, 145, 1165, 630), fill=(22, 21, 31, 238))
    draw.rectangle((265, 910, 1335, 1375), fill=(42, 37, 44, 240), outline=(236, 214, 169, 140), width=8)
    for i in range(8):
        x = 300 + i * 130
        draw.rectangle((x, 930, x + 62, 990), fill=(236, 214, 169, 120))
        draw.rectangle((x, 1295, x + 62, 1355), fill=(236, 214, 169, 120))
    for r in [120, 210, 300]:
        draw.ellipse((800-r, 1140-r, 800+r, 1140+r), outline=(236, 214, 169, 90), width=8)
    draw.ellipse((748, 1088, 852, 1192), fill=(236, 214, 169, 120))
    draw.polygon([(330, 1510), (800, 820), (1270, 1510)], outline=(236, 214, 169, 115), width=8)
    draw.rectangle((470, 1450, 1130, 1545), fill=(33, 29, 34, 230), outline=(236, 214, 169, 120), width=5)
    draw.line((490, 1450, 640, 1545), fill=(236, 214, 169, 95), width=5)
    _label(draw, "ARCHIVE REEL", 800, 1510, 42, (236, 214, 169, 185))
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
