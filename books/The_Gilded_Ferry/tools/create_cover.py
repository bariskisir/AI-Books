#!/usr/bin/env python3
"""Generate a project-local raster cover for The Gilded Ferry."""

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
TITLE = "The Gilded Ferry"
PALETTE = [tuple(c) for c in [[18, 22, 29], [55, 47, 39], [150, 104, 50], [226, 182, 92]]]
SEED = 1584


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

    _gradient(draw, (15, 19, 25), (62, 54, 45))
    for x in range(0, WIDTH, 130):
        draw.rectangle((x, 870 + (x % 260), x + 26, 1540), fill=(18, 22, 25, 185))
        draw.ellipse((x - 18, 850 + (x % 260), x + 44, 912 + (x % 260)), fill=(226, 182, 92, 45))
    for y in range(1240, 1610, 32):
        draw.line((0, y, WIDTH, y + int(12 * math.sin(y / 50))), fill=(166, 139, 88, 45), width=3)
    draw.polygon([(130, 1195), (1470, 1195), (1330, 1460), (300, 1460)], fill=(117, 82, 45, 245), outline=(226, 182, 92, 160))
    draw.rectangle((260, 920, 1340, 1195), fill=(58, 43, 32, 245), outline=(226, 182, 92, 170), width=9)
    for x in range(350, 1230, 165):
        draw.rounded_rectangle((x, 980, x + 95, 1110), radius=18, fill=(16, 24, 31, 230), outline=(226, 182, 92, 130), width=5)
    draw.rectangle((690, 770, 910, 920), fill=(74, 52, 35, 240), outline=(226, 182, 92, 150), width=6)
    draw.line((270, 760, 1330, 760), fill=(226, 182, 92, 75), width=8)
    _label(draw, "FORTUNA", 800, 1350, 58, (242, 205, 123, 180))
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
