#!/usr/bin/env python3
"""Create cover image for The Bee Thief — Rural Noir."""

from __future__ import annotations

import argparse
import json
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
OUT = Path(__file__).resolve().parents[3] / "books" / "The_Bee_Thief" / "covers" / "The_Bee_Thief.png"


def gradient(draw: ImageDraw, top: tuple[int, int, int], bottom: tuple[int, int, int]) -> None:
    for y in range(HEIGHT):
        r = int(top[0] + (bottom[0] - top[0]) * y / HEIGHT)
        g = int(top[1] + (bottom[1] - top[1]) * y / HEIGHT)
        b = int(top[2] + (bottom[2] - top[2]) * y / HEIGHT)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def draw_field(draw: ImageDraw) -> None:
    # Rollings fields in gold/brown
    colors = [(180, 130, 60), (160, 110, 40), (140, 90, 30)]
    for i, y_base in enumerate([1400, 1550, 1700]):
        c = colors[i % len(colors)]
        for x in range(0, WIDTH, 8):
            h = 50 + int(30 * (x / WIDTH))
            y = y_base + int(20 * (x / WIDTH))
            draw.rectangle([x, y, x + 4, y + h], fill=c)


def draw_hive(draw: ImageDraw, x: int, y: int, dead: bool = True) -> None:
    # Hive body
    bw, bh = 120, 90
    base_color = (160, 130, 80) if dead else (200, 170, 100)
    draw.rectangle([x, y, x + bw, y + bh], fill=base_color, outline=(80, 60, 30), width=2)

    # Hive entrance at bottom
    entrance_color = (40, 30, 15) if dead else (60, 50, 30)
    draw.rectangle([x + 35, y + bh - 18, x + 85, y + bh - 6], fill=entrance_color)

    if dead:
        # Skull-and-crossbones style X for dead hive
        draw.line([(x + 20, y + 20), (x + 100, y + 70)], fill=(80, 30, 15), width=3)
        draw.line([(x + 100, y + 20), (x + 20, y + 70)], fill=(80, 30, 15), width=3)
    else:
        # Small dots for bees
        for _ in range(6):
            bx = x + 40 + (_ * 12)
            by = y + 30 + (_ % 3) * 15
            draw.ellipse([bx, by, bx + 6, by + 6], fill=(220, 180, 40))


def draw_single_bee(draw: ImageDraw, x: int, y: int) -> None:
    # Body
    draw.ellipse([x - 8, y - 4, x + 8, y + 4], fill=(200, 160, 40))
    # Stripes
    draw.rectangle([x - 2, y - 4, x + 2, y + 4], fill=(30, 20, 10))
    draw.rectangle([x - 6, y - 4, x - 4, y + 4], fill=(30, 20, 10))
    draw.rectangle([x + 4, y - 4, x + 6, y + 4], fill=(30, 20, 10))
    # Wings
    draw.ellipse([x - 10, y - 12, x - 2, y - 4], fill=(200, 210, 230, 160))
    draw.ellipse([x + 2, y - 12, x + 10, y - 4], fill=(200, 210, 230, 160))
    # Flight trail
    for i in range(6):
        tx = x - (i + 1) * 10
        ty = y + (i % 3) * 5 - 5
        draw.ellipse([tx - 1, ty - 1, tx + 1, ty + 1], fill=(220, 190, 80, 120))


def draw_title_panel(draw: ImageDraw) -> None:
    # Dark panel at bottom
    draw.rectangle([0, 1920, WIDTH, 2560], fill=(30, 20, 10))

    try:
        font_title = ImageFont.truetype("arialbd.ttf", 80)
        font_author = ImageFont.truetype("arialbd.ttf", 36)
    except (IOError, OSError):
        font_title = ImageFont.load_default()
        font_author = ImageFont.load_default()

    # Title text
    title = "THE BEE THIEF"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    tw = bbox[2] - bbox[0]
    tx = (WIDTH - tw) // 2
    draw.text((tx, 2040), title, fill=(255, 255, 255), font=font_title)

    # Author text
    author = "Barış Kısır"
    bbox = draw.textbbox((0, 0), author, font=font_author)
    aw = bbox[2] - bbox[0]
    ax = (WIDTH - aw) // 2
    draw.text((ax, 2180), author, fill=(200, 180, 120), font=font_author)

    # Genre line
    genre = "Rural Noir"
    try:
        font_genre = ImageFont.truetype("arialbd.ttf", 24)
    except (IOError, OSError):
        font_genre = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), genre, font=font_genre)
    gw = bbox[2] - bbox[0]
    gx = (WIDTH - gw) // 2
    draw.text((gx, 2260), genre, fill=(160, 140, 80), font=font_genre)



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()

    if args.metadata:
        meta = json.loads(args.metadata.read_text(encoding="utf-8"))
        title = meta.get("title", "The Bee Thief")
    else:
        title = "The Bee Thief"

    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img, "RGBA")

    # Gradient background: dark brown sky to gold fields
    gradient(draw, top=(60, 40, 20), bottom=(180, 140, 60))

    # Sun / moon glow
    draw.ellipse([600, 200, 1000, 600], fill=(220, 190, 120, 80))

    # Distant fields
    draw_field(draw)

    # Dead hives
    draw_hive(draw, 200, 1000, dead=True)
    draw_hive(draw, 500, 1050, dead=True)
    draw_hive(draw, 800, 1020, dead=True)
    draw_hive(draw, 1100, 1060, dead=True)

    # Scattered dead hives in distance
    draw_hive(draw, 100, 1200, dead=True)
    draw_hive(draw, 1300, 1180, dead=True)

    # Single bee flying
    draw_single_bee(draw, 850, 500)

    # Title panel
    draw_title_panel(draw)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()))
    img.save(args.out, "PNG")
    print(f"Cover saved to {args.out}")


if __name__ == "__main__":
    main()
