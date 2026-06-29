#!/usr/bin/env python3
"""Generate a project-local raster cover for The Silent Observatory."""

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
TITLE = "The Silent Observatory"
PALETTE = [tuple(c) for c in [[8, 17, 29], [23, 48, 68], [89, 124, 139], [219, 226, 216]]]
SEED = 2286


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

    _gradient(draw, (6, 12, 24), (28, 58, 78))
    for _ in range(140):
        x, y = rng.randint(60, 1540), rng.randint(70, 830)
        draw.ellipse((x, y, x + 4, y + 4), fill=(219, 226, 216, rng.randint(90, 230)))
    draw.polygon([(0, 1480), (410, 1050), (740, 1420), (1020, 980), (WIDTH, 1460), (WIDTH, 1765), (0, 1765)], fill=(15, 31, 46, 245))
    draw.polygon([(95, 1460), (420, 1120), (690, 1450)], fill=(80, 111, 126, 110))
    draw.rectangle((520, 1040, 1080, 1500), fill=(194, 203, 199, 225), outline=(30, 49, 58, 210), width=9)
    draw.pieslice((440, 720, 1160, 1440), 180, 360, fill=(207, 216, 212, 230), outline=(34, 52, 62, 220), width=10)
    draw.line((795, 860, 1300, 520), fill=(222, 230, 222, 230), width=34)
    draw.line((805, 872, 1314, 535), fill=(83, 112, 126, 180), width=10)
    draw.rectangle((660, 1190, 940, 1500), fill=(18, 33, 47, 230))
    draw.arc((260, 390, 1340, 1470), 215, 325, fill=(219, 226, 216, 55), width=7)
    _label(draw, "HALDEN OBSERVATORY", 800, 1540, 40, (219, 226, 216, 185))
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
