#!/usr/bin/env python3
"""Generate a 1600×2560 PNG cover for The Tobacco Fields of Virginia."""

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
FONT_PATH = Path("C:/Windows/Fonts/arialbd.ttf")
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "covers"


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def draw_gradient(draw: ImageDraw, top_color: tuple, bottom_color: tuple) -> None:
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def draw_tobacco_rows(draw: ImageDraw) -> None:
    """Draw stylized tobacco rows receding into the distance."""
    base_y = 1400
    for row in range(18):
        x_start = int(WIDTH * (0.1 + 0.044 * row))
        x_end = int(WIDTH * (0.9 - 0.044 * row))
        y = base_y - row * 12
        for plant in range(8 + row):
            px = int(x_start + (x_end - x_start) * plant / (7 + row))
            py = y + int(math.sin(plant * 1.3 + row) * 6)
            h = max(6, 22 - row)
            w = max(4, 12 - row // 2)
            color = (50 + row * 3, 70 + row * 2, 30 + row)
            draw.ellipse([px - w, py - h, px + w, py + h], fill=color)


def draw_oak_tree(draw: ImageDraw) -> None:
    """Draw a live oak tree silhouette on the left."""
    trunk_x = 200
    trunk_y = 1100
    draw.polygon(
        [(trunk_x - 20, trunk_y), (trunk_x + 20, trunk_y), (trunk_x + 12, 1400), (trunk_x - 12, 1400)],
        fill=(15, 12, 8),
    )
    branches = [
        (trunk_x, trunk_y, trunk_x - 180, trunk_y - 80),
        (trunk_x, trunk_y, trunk_x - 140, trunk_y - 140),
        (trunk_x, trunk_y, trunk_x - 60, trunk_y - 180),
        (trunk_x, trunk_y, trunk_x + 60, trunk_y - 170),
        (trunk_x, trunk_y, trunk_x + 150, trunk_y - 100),
        (trunk_x, trunk_y, trunk_x + 180, trunk_y - 50),
    ]
    for bx, by, ex, ey in branches:
        draw.line([(bx, by), (ex, ey)], fill=(15, 12, 8), width=8)

    def draw_canopy(cx, cy, radius):
        for _ in range(180):
            angle = math.radians(_ * 2)
            r = radius * (0.6 + 0.4 * math.sin(_ * 0.7))
            px = int(cx + r * math.cos(angle))
            py = int(cy + r * math.sin(angle) * 0.7)
            shade = 25 + int(15 * math.sin(_ * 0.5))
            draw.ellipse([px - 18, py - 14, px + 18, py + 14], fill=(shade, shade - 5, shade - 8))

    draw_canopy(trunk_x - 100, trunk_y - 180, 180)
    draw_canopy(trunk_x + 100, trunk_y - 160, 160)
    draw_canopy(trunk_x, trunk_y - 220, 150)


def draw_plantation_house(draw: ImageDraw) -> None:
    """Draw a distant plantation house silhouette on the right."""
    cx = 1150
    cy = 800
    # Main building
    main_w, main_h = 200, 120
    draw.rectangle([cx - main_w // 2, cy - main_h, cx + main_w // 2, cy], fill=(70, 50, 35))
    # Columns
    for col in range(6):
        col_x = int(cx - main_w // 2 + 30 + col * 28)
        draw.rectangle([col_x, cy - main_h - 30, col_x + 8, cy], fill=(80, 60, 45))
    # Roof
    draw.polygon(
        [(cx - main_w // 2 - 10, cy - main_h), (cx, cy - main_h - 50), (cx + main_w // 2 + 10, cy - main_h)],
        fill=(50, 35, 20),
    )
    # Second floor
    draw.rectangle([cx - main_w // 2 + 10, cy - main_h - 30, cx + main_w // 2 - 10, cy - main_h], fill=(65, 45, 30))


def draw_ground(draw: ImageDraw) -> None:
    """Draw the ground / dirt foreground."""
    draw.rectangle([0, 1400, WIDTH, 1920], fill=(80, 40, 20))
    # Red dirt texture
    for _ in range(300):
        x = int(WIDTH * (0.05 + 0.9 * (_ % 30) / 29))
        y = 1420 + int(420 * (_ // 30) / 9)
        shade = 85 + int(20 * math.sin(_ * 7.3))
        draw.point((x, y), fill=(shade, 40 + int(10 * math.sin(_ * 5.1)), 20))


def draw_title_panel(draw: ImageDraw, title: str, author: str) -> None:
    """Draw the dark panel at bottom with title and author in white."""
    panel_top = 1920
    draw.rectangle([0, panel_top, WIDTH, HEIGHT], fill=(15, 12, 10))
    # Subtle line at top of panel
    draw.line([(100, panel_top), (WIDTH - 100, panel_top)], fill=(180, 140, 60), width=2)

    # Title
    title_font_size = 80
    title_font = ImageFont.truetype(str(FONT_PATH), title_font_size)
    bbox = draw.textbbox((0, 0), title, font=title_font)
    title_w = bbox[2] - bbox[0]
    title_x = (WIDTH - title_w) // 2
    title_y = panel_top + 120
    draw.text((title_x, title_y), title, fill=(255, 255, 255), font=title_font)

    # Decorative line under title
    draw.line([(int(WIDTH * 0.35), title_y + 105), (int(WIDTH * 0.65), title_y + 105)], fill=(180, 140, 60), width=1)

    # Author
    author_font_size = 40
    author_font = ImageFont.truetype(str(FONT_PATH), author_font_size)
    bbox = draw.textbbox((0, 0), author, font=author_font)
    author_w = bbox[2] - bbox[0]
    author_x = (WIDTH - author_w) // 2
    author_y = title_y + 140
    draw.text((author_x, author_y), author, fill=(200, 190, 180), font=author_font)

    # Genre tag at very bottom
    genre_font = ImageFont.truetype(str(FONT_PATH), 22)
    genre_text = "A Southern Gothic Novel"
    bbox = draw.textbbox((0, 0), genre_text, font=genre_font)
    genre_w = bbox[2] - bbox[0]
    genre_x = (WIDTH - genre_w) // 2
    draw.text((genre_x, 2480), genre_text, fill=(140, 130, 120), font=genre_font)



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    if args.metadata:
        meta = json.loads(args.metadata.read_text(encoding="utf-8"))
        title = meta.get("title", "The Tobacco Fields of Virginia")
        author = meta.get("author", "Barış Kısır")
        model = meta.get("model", "")
    else:
        title = "The Tobacco Fields of Virginia"
        author = "Barış Kısır"

    output_path = args.out or (OUTPUT_DIR / "The_Tobacco_Fields_of_Virginia.png")

    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)

    # Gradient: deep indigo at top to warm sepia at bottom
    top_color = hex_to_rgb("#1a0a2e")
    mid_color = hex_to_rgb("#5c3a2e")
    bottom_color = hex_to_rgb("#8b5e3c")
    draw_gradient(draw, top_color, mid_color)

    # Mid-section transition
    for y in range(800, 1400):
        ratio = (y - 800) / 600
        r = int(mid_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(mid_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(mid_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Sky elements - muted sun/moon
    draw.ellipse([1200, 120, 1400, 320], fill=(200, 160, 80, 30))
    draw.ellipse([1220, 140, 1380, 300], fill=(220, 190, 120, 20))

    # Plantation house in background
    draw_plantation_house(draw)

    # Oak tree
    draw_oak_tree(draw)

    # Ground
    draw_ground(draw)

    # Tobacco rows
    draw_tobacco_rows(draw)

    # Title panel
    draw_title_panel(draw, title, author)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")


if __name__ == "__main__":
    main()