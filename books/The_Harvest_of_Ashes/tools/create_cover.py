#!/usr/bin/env python3
"""Generate a project-local raster cover for The Harvest of Ashes."""

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
TITLE = "The Harvest of Ashes"
PALETTE = [tuple(c) for c in [[25, 24, 20], [73, 67, 54], [125, 113, 83], [205, 185, 135]]]
SEED = 2020


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

    _gradient(draw, (30, 30, 27), (95, 86, 68))
    draw.ellipse((1060, 245, 1375, 560), fill=(202, 166, 96, 90))
    for _ in range(320):
        x, y = rng.randint(0, WIDTH), rng.randint(60, 1580)
        draw.rectangle((x, y, x + rng.randint(1, 4), y + rng.randint(1, 4)), fill=(210, 202, 180, rng.randint(25, 95)))
    draw.polygon([(0, 1030), (WIDTH, 900), (WIDTH, 1765), (0, 1765)], fill=(69, 62, 49, 250))
    for x in range(-200, 1800, 160):
        draw.line((x, 1710, 800, 1030), fill=(150, 132, 90, 75), width=5)
    draw.rectangle((1040, 650, 1210, 1340), fill=(49, 48, 43, 245), outline=(189, 166, 112, 120), width=6)
    draw.pieslice((1010, 560, 1240, 790), 180, 360, fill=(73, 69, 58, 245), outline=(189, 166, 112, 100), width=5)
    draw.rectangle((450, 880, 780, 1320), fill=(74, 54, 39, 240))
    draw.polygon([(410, 880), (615, 700), (820, 880)], fill=(104, 79, 52, 230))
    draw.line((515, 1030, 710, 1250), fill=(204, 185, 135, 145), width=10)
    _label(draw, "GRAIN OFFICE", 800, 1515, 42, (218, 198, 146, 175))
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
