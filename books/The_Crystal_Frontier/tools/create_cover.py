#!/usr/bin/env python3
"""Generate a project-local raster cover for The Crystal Frontier."""

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
TITLE = "The Crystal Frontier"
PALETTE = [tuple(c) for c in [[16, 24, 35], [49, 84, 102], [111, 178, 185], [230, 238, 226]]]
SEED = 2058


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

    _gradient(draw, (12, 21, 34), (48, 92, 110))
    draw.ellipse((1080, 160, 1400, 480), fill=(230, 238, 226, 85))
    draw.polygon([(0, 1280), (WIDTH, 980), (WIDTH, 1765), (0, 1765)], fill=(30, 65, 80, 235))
    for x in range(80, 1540, 145):
        h = rng.randint(420, 920)
        draw.polygon([(x, 1485), (x + 55, 1485 - h), (x + 130, 1485), (x + 94, 1640), (x + 22, 1640)], fill=(170, 230, 232, rng.randint(80, 150)), outline=(230, 238, 226, 145))
        draw.line((x + 55, 1485 - h, x + 64, 1615), fill=(230, 238, 226, 95), width=3)
    draw.line((260, 1580, 640, 1300), fill=(234, 238, 210, 160), width=9)
    draw.line((640, 1300, 920, 1415), fill=(234, 238, 210, 160), width=9)
    draw.line((920, 1415, 1250, 1120), fill=(234, 238, 210, 160), width=9)
    draw.rectangle((590, 1180, 690, 1325), fill=(34, 72, 87, 230), outline=(230, 238, 226, 160), width=5)
    draw.polygon([(640, 1110), (555, 1180), (725, 1180)], fill=(230, 238, 226, 150))
    _label(draw, "MIRRORGLASS", 800, 1515, 44, (230, 238, 226, 185))
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
