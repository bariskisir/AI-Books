#!/usr/bin/env python3
"""Generate a project-local raster cover for The Driftwood Court."""

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
TITLE = "The Driftwood Court"
PALETTE = [tuple(c) for c in [[18, 34, 42], [41, 78, 88], [108, 126, 111], [221, 199, 149]]]
SEED = 1950


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

    _gradient(draw, (16, 36, 45), (54, 91, 96))
    for y in range(970, 1620, 26):
        draw.line((0, y, WIDTH, y + int(10 * math.sin(y / 44))), fill=(166, 206, 210, 38), width=3)
    draw.polygon([(0, 1420), (WIDTH, 1345), (WIDTH, 1620), (0, 1620)], fill=(15, 30, 37, 210))
    for x in range(120, 1540, 180):
        draw.rectangle((x, 1320, x + 34, 1660), fill=(41, 47, 42, 230))
    draw.rectangle((310, 965, 1290, 1325), fill=(78, 73, 60, 240), outline=(221, 199, 149, 165), width=8)
    draw.polygon([(260, 965), (800, 700), (1340, 965)], fill=(112, 91, 61, 245), outline=(221, 199, 149, 160))
    for x in range(430, 1180, 190):
        draw.rectangle((x, 1060, x + 95, 1245), fill=(22, 44, 50, 230), outline=(194, 176, 131, 115), width=5)
    draw.rectangle((715, 1045, 885, 1325), fill=(32, 39, 39, 245), outline=(194, 176, 131, 160), width=6)
    draw.line((180, 1390, 1420, 1305), fill=(221, 199, 149, 85), width=9)
    draw.arc((560, 450, 1040, 930), 205, 335, fill=(222, 218, 190, 160), width=12)
    _label(draw, "GULL COURT", 800, 1515, 42, (221, 199, 149, 185))
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
