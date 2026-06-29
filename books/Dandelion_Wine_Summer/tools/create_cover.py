#!/usr/bin/env python3
"""Generate a 1600x2560 cover for Dandelion Wine Summer using PIL."""

from __future__ import annotations

import argparse
import json
import math
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

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
PANEL_TOP = 1920
PANEL_BOTTOM = HEIGHT

FONTS_DIR = Path("C:/Windows/Fonts")
TITLE_FONT_PATH = FONTS_DIR / "georgiab.ttf"
AUTHOR_FONT_PATH = FONTS_DIR / "arialbd.ttf"
SMALL_FONT_PATH = FONTS_DIR / "arial.ttf"


def draw_sky(draw: ImageDraw.ImageDraw) -> None:
    """Draw a golden hour sky gradient."""
    for y in range(0, PANEL_TOP):
        progress = y / PANEL_TOP
        if progress < 0.3:
            r = int(255 - progress * 100)
            g = int(180 - progress * 80)
            b = int(80 - progress * 30)
        elif progress < 0.7:
            r = int(225 - (progress - 0.3) * 40)
            g = int(156 - (progress - 0.3) * 60)
            b = int(71 - (progress - 0.3) * 50)
        else:
            r = int(213 - (progress - 0.7) * 100)
            g = int(126 - (progress - 0.7) * 60)
            b = int(56 - (progress - 0.7) * 40)
        draw.line([(0, y), (WIDTH, y)], fill=(max(0, r), max(0, g), max(0, b)))


def draw_sun(draw: ImageDraw.ImageDraw) -> None:
    """Draw a glowing sun near the horizon."""
    cx, cy = 800, 1500
    for radius in range(200, 0, -1):
        alpha = int(255 * (1 - radius / 200))
        color = (255, 220, 100, alpha) if radius > 100 else (255, 200, 80, alpha)
        draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            fill=color[:3] if radius <= 100 else None,
            outline=None,
        )
    draw.ellipse([cx - 80, cy - 80, cx + 80, cy + 80], fill=(255, 220, 100))


def draw_hills(draw: ImageDraw.ImageDraw) -> None:
    """Draw rolling hills in the background."""
    hill_color = (180, 200, 140)
    for i in range(3):
        offset_x = i * 200
        offset_y = 1600 + i * 30
        for x in range(WIDTH):
            y_base = int(
                offset_y
                + math.sin((x + offset_x) * 0.003) * 60
                + math.sin((x + offset_x) * 0.007) * 30
            )
            for y in range(y_base, PANEL_TOP):
                shade = max(0, 255 - (y - 1500) // 4)
                g = min(220, hill_color[1] + (y - offset_y) // 10)
                r = max(100, hill_color[0] - (y - offset_y) // 15)
                draw.point((x, y), fill=(r, g, 120))


def draw_dandelions(draw: ImageDraw.ImageDraw) -> None:
    """Draw dandelions in the foreground field."""
    # Stems and leaves
    base_y = 1650
    stem_color = (80, 140, 60)
    for x in range(0, WIDTH, 40):
        for offset in range(0, 25, 8):
            sx = x + offset
            sy = base_y + int(math.sin(x * 0.05) * 20) + offset
            height = int(80 + math.sin(x * 0.1 + offset) * 30)
            draw.line([(sx, sy), (sx, sy - height)], fill=stem_color, width=2)

    # Dandelion flower heads (yellow dots)
    for x in range(0, WIDTH, 35):
        for offset in range(0, 30, 10):
            fx = x + offset
            fy = (
                base_y
                + int(math.sin(x * 0.05) * 20)
                + offset
                - 80
                - int(math.sin(x * 0.1 + offset) * 30)
            )
            flower_color = (255, 220, 50) if offset % 20 == 0 else (255, 200, 30)
            draw.ellipse([fx - 5, fy - 5, fx + 5, fy + 5], fill=flower_color)

    # Seed heads (white puffs) in the foreground
    for x in range(0, WIDTH, 50):
        for offset in range(5, 35, 15):
            seed_x = x + offset
            seed_y = 1800 + int(math.sin(x * 0.08 + offset) * 25)
            draw.ellipse(
                [seed_x - 8, seed_y - 8, seed_x + 8, seed_y + 8],
                fill=(255, 255, 255, 180),
                outline=(200, 200, 200),
            )
            # Tiny seed lines radiating
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                sx2 = int(seed_x + math.cos(rad) * 12)
                sy2 = int(seed_y + math.sin(rad) * 12)
                draw.line([(seed_x, seed_y), (sx2, sy2)], fill=(220, 220, 220), width=1)


def draw_field(draw: ImageDraw.ImageDraw) -> None:
    """Draw the grassy field below the hills."""
    for y in range(PANEL_TOP - 100, PANEL_TOP):
        progress = (y - (PANEL_TOP - 100)) / 100
        r = int(120 + progress * 40)
        g = int(180 - progress * 20)
        b = int(60 + progress * 10)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def draw_bicycle(draw: ImageDraw.ImageDraw) -> None:
    """Draw a simple bicycle silhouette on the horizon."""
    cx, cy = 500, 1580
    # Wheels
    draw.ellipse([cx - 25, cy - 25, cx + 25, cy + 25], outline=(60, 50, 40), width=3)
    draw.ellipse(
        [cx + 70, cy - 25, cx + 120, cy + 25], outline=(60, 50, 40), width=3
    )
    # Frame
    draw.line([cx, cy, cx + 40, cy - 40], fill=(60, 50, 40), width=3)
    draw.line([cx + 40, cy - 40, cx + 95, cy], fill=(60, 50, 40), width=3)
    draw.line([cx, cy, cx + 95, cy], fill=(60, 50, 40), width=3)
    # Seat post
    draw.line([cx + 30, cy, cx + 30, cy - 30], fill=(60, 50, 40), width=2)
    # Handlebars
    draw.line([cx + 40, cy - 40, cx + 60, cy - 50], fill=(60, 50, 40), width=2)
    # Rider silhouette
    draw.ellipse([cx + 45, cy - 75, cx + 65, cy - 55], fill=(60, 50, 40))
    draw.line([cx + 55, cy - 55, cx + 55, cy - 35], fill=(60, 50, 40), width=3)


def draw_title_panel(draw: ImageDraw.ImageDraw, title: str, author: str) -> None:
    """Draw the title panel at the bottom of the cover."""
    # Semi-transparent light background
    for y in range(PANEL_TOP, PANEL_BOTTOM):
        alpha = 220
        r = int(255 - (y - PANEL_TOP) / (PANEL_BOTTOM - PANEL_TOP) * 20)
        g = int(248 - (y - PANEL_TOP) / (PANEL_BOTTOM - PANEL_TOP) * 20)
        b = int(235 - (y - PANEL_TOP) / (PANEL_BOTTOM - PANEL_TOP) * 20)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Subtle top border line
    draw.line([(0, PANEL_TOP), (WIDTH, PANEL_TOP)], fill=(200, 180, 150), width=2)

    # Title text with wrapping
    try:
        title_font = ImageFont.truetype(str(TITLE_FONT_PATH), 72)
        small_font = ImageFont.truetype(str(TITLE_FONT_PATH), 48)
        author_font = ImageFont.truetype(str(AUTHOR_FONT_PATH), 36)
    except (OSError, IOError):
        title_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
        author_font = ImageFont.load_default()

    # Wrap title if needed
    wrapped = textwrap.wrap(title, width=18)
    title_lines = wrapped if wrapped else [title]

    total_text_height = len(title_lines) * 80 + 60
    start_y = PANEL_TOP + (PANEL_BOTTOM - PANEL_TOP - total_text_height) // 2

    for i, line in enumerate(title_lines):
        font = title_font if len(title) > 12 and i == 0 else small_font
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        tx = (WIDTH - tw) // 2
        ty = start_y + i * 80
        # Shadow
        draw.text((tx + 2, ty + 2), line, fill=(100, 90, 70), font=font)
        # Main text
        draw.text((tx, ty), line, fill=(60, 50, 30), font=font)

    # Author name
    author_y = start_y + len(title_lines) * 80 + 20
    bbox = draw.textbbox((0, 0), author, font=author_font)
    aw = bbox[2] - bbox[0]
    ax = (WIDTH - aw) // 2
    draw.text((ax + 1, author_y + 1), author, fill=(140, 130, 110), font=author_font)
    draw.text((ax, author_y), author, fill=(100, 90, 70), font=author_font)


def create_cover(metadata: dict, output_path: Path) -> None:
    """Generate the full cover image."""
    title = metadata.get("title", "Dandelion Wine Summer")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGB", (WIDTH, HEIGHT), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    draw_sky(draw)
    draw_sun(draw)
    draw_hills(draw)
    draw_field(draw)
    draw_dandelions(draw)
    draw_bicycle(draw)
    draw_title_panel(draw, title, author)

    # Soft glow filter over the whole image
    glow = img.filter(ImageFilter.GaussianBlur(radius=2))
    img = Image.blend(img, glow, 0.15)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    create_cover(metadata, args.out)


if __name__ == "__main__":
    main()