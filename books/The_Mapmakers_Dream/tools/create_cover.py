#!/usr/bin/env python3
"""Generate a book cover for The Mapmaker's Dream using PIL."""

from __future__ import annotations

import argparse
import json
import math
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


WIDTH, HEIGHT = 1600, 2560


def gradient(draw: ImageDraw, top: tuple, bottom: tuple) -> None:
    for y in range(HEIGHT):
        r = int(top[0] + (bottom[0] - top[0]) * y / HEIGHT)
        g = int(top[1] + (bottom[1] - top[1]) * y / HEIGHT)
        b = int(top[2] + (bottom[2] - top[2]) * y / HEIGHT)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def draw_river(draw: ImageDraw) -> None:
    river_color = (42, 95, 70)
    pts = []
    x = 0
    y = 400
    for i in range(60):
        x = int(800 + 500 * math.sin(i * 0.08 + 0.5))
        y = 400 + i * 25
        pts.append((x, y))
    draw.line(pts, fill=river_color, width=40)
    draw.line(pts, fill=(70, 140, 100), width=20)


def draw_jungle(draw: ImageDraw) -> None:
    greens = [(25, 60, 30), (30, 80, 35), (20, 50, 25)]
    for _ in range(200):
        x = int(200 + 1200 * 0.5)  # will be randomized
    for _ in range(120):
        x = int(100 + 1400 * (__import__('random').random()))
        y = int(200 + 1600 * (__import__('random').random()))
        size = int(20 + 60 * (__import__('random').random()))
        shade = greens[__import__('random').randint(0, 2)]
        draw.ellipse([x - size, y - size, x + size, y + size], fill=shade, outline=None)


def draw_stone_city(draw: ImageDraw) -> None:
    wall_color = (180, 150, 110)
    tower_color = (200, 170, 130)
    # City wall on the far shore
    for i in range(12):
        bx = 600 + i * 35
        by = 850
        draw.rectangle([bx, by - 200, bx + 25, by], fill=wall_color, outline=(140, 110, 70))
    # Towers
    draw.rectangle([580, 580, 610, 850], fill=tower_color, outline=(140, 110, 70))
    draw.rectangle([970, 620, 1000, 850], fill=tower_color, outline=(140, 110, 70))
    # Central tower (the source)
    draw.rectangle([760, 500, 810, 850], fill=(210, 180, 140), outline=(140, 110, 70))
    # Gate
    draw.rectangle([700, 720, 740, 850], fill=(120, 90, 60))
    # Window arches on central tower
    for wy in range(520, 720, 40):
        draw.arc([775, wy, 795, wy + 30], 0, 180, fill=(100, 70, 40), width=3)


def draw_title_panel(draw: ImageDraw, title_font, author_font) -> None:
    # Dark panel at bottom
    draw.rectangle([0, 1920, WIDTH, HEIGHT], fill=(20, 15, 10, 220))

    # Title
    title = "THE MAPMAKER'S"
    title2 = "DREAM"
    # Center title
    tbbox = draw.textbbox((0, 0), title, font=title_font)
    tw = tbbox[2] - tbbox[0]
    tx = (WIDTH - tw) // 2
    draw.text((tx, 1960), title, fill=(255, 255, 255), font=title_font)

    tbbox2 = draw.textbbox((0, 0), title2, font=title_font)
    tw2 = tbbox2[2] - tbbox2[0]
    tx2 = (WIDTH - tw2) // 2
    draw.text((tx2, 2040), title2, fill=(255, 255, 255), font=title_font)

    # Decorative line
    draw.rectangle([650, 2150, 950, 2155], fill=(200, 170, 130))

    # Author
    author = "Barış Kısır"
    abbox = draw.textbbox((0, 0), author, font=author_font)
    aw = abbox[2] - abbox[0]
    ax = (WIDTH - aw) // 2
    draw.text((ax, 2200), author, fill=(255, 255, 255), font=author_font)



def main() -> None:
    parser = argparse.ArgumentParser(description="Generate cover for The Mapmaker's Dream")
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Gradient: deep green (top) to terracotta/emerald (bottom)
    gradient(draw, (15, 40, 25), (110, 65, 45))

    # Jungle canopy silhouettes
    draw_jungle(draw)

    # River
    draw_river(draw)

    # Stone city
    draw_stone_city(draw)

    # River highlights (reflection)
    draw.rectangle([0, 860, WIDTH, 880], fill=(60, 130, 90, 80))

    # Load fonts
    try:
        title_font = ImageFont.truetype("arialbd.ttf", 80)
        author_font = ImageFont.truetype("arial.ttf", 36)
    except (OSError, IOError):
        title_font = ImageFont.load_default()
        author_font = ImageFont.load_default()

    # Title panel
    draw_title_panel(draw, title_font, author_font)

    # Save
    args.out.parent.mkdir(parents=True, exist_ok=True)
    model = _standard_cover_metadata_from_locals(locals()).get("model", "")
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.save(args.out, "PNG")
    print(f"Cover saved to {args.out}")


if __name__ == "__main__":
    main()