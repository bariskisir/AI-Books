#!/usr/bin/env python3
"""Generate a genre-appropriate cover image for The House on the Cliff."""

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


WIDTH = 1600
HEIGHT = 2560
TITLE_FONT_SIZE = 96
AUTHOR_FONT_SIZE = 48
GENRE_FONT_SIZE = 28


def hex_to_rgb(hex_color: str) -> tuple[int, ...]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def draw_gradient(draw: ImageDraw.Draw, top_color: str, bottom_color: str) -> None:
    top_rgb = hex_to_rgb(top_color)
    bottom_rgb = hex_to_rgb(bottom_color)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(top_rgb[0] * (1 - ratio) + bottom_rgb[0] * ratio)
        g = int(top_rgb[1] * (1 - ratio) + bottom_rgb[1] * ratio)
        b = int(top_rgb[2] * (1 - ratio) + bottom_rgb[2] * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def load_font(size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype("arialbd.ttf", size)
    except (OSError, IOError):
        try:
            return ImageFont.truetype("/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf", size)
        except (OSError, IOError):
            return ImageFont.load_default()


def draw_house(draw: ImageDraw.Draw) -> None:
    """Draw a clifftop house silhouette with glass walls using PIL primitives."""
    # Cliff face
    cliff_color = (90, 85, 80)
    cliff_points = [
        (0, 1400),
        (0, 1600),
        (400, 1500),
        (600, 1450),
        (850, 1480),
        (1100, 1420),
        (1400, 1500),
        (1600, 1450),
        (1600, 1700),
        (0, 1700),
    ]
    draw.polygon(cliff_points, fill=cliff_color)

    # Cliff top
    cliff_top_color = (110, 100, 90)
    cliff_top_points = [
        (0, 1400),
        (400, 1500),
        (600, 1450),
        (850, 1480),
        (1100, 1420),
        (1400, 1500),
        (1600, 1450),
        (1600, 1400),
        (1400, 1380),
        (1100, 1360),
        (850, 1400),
        (600, 1380),
        (400, 1420),
        (0, 1350),
    ]
    draw.polygon(cliff_top_points, fill=cliff_top_color)

    # House structure - modern glass box design
    house_color = (70, 70, 80)
    glass_color = (160, 190, 210, 180)

    # Main house body
    house_x, house_y = 550, 1050
    house_w, house_h = 500, 350

    # Steel frame outline
    draw.rectangle([house_x, house_y, house_x + house_w, house_y + house_h], outline=house_color, width=4)

    # Glass panels (left side)
    glass_left = house_x + 10
    glass_top = house_y + 10
    glass_w = (house_w - 30) // 2
    glass_h = (house_h - 30) // 2

    draw.rectangle(
        [glass_left, glass_top, glass_left + glass_w, glass_top + glass_h],
        fill=glass_color,
        outline=(100, 130, 160),
        width=2,
    )
    draw.rectangle(
        [glass_left, glass_top + glass_h + 10, glass_left + glass_w, glass_top + 2 * glass_h + 10],
        fill=glass_color,
        outline=(100, 130, 160),
        width=2,
    )

    # Glass panels (right side)
    glass_right = glass_left + glass_w + 10
    draw.rectangle(
        [glass_right, glass_top, glass_right + glass_w, glass_top + glass_h],
        fill=glass_color,
        outline=(100, 130, 160),
        width=2,
    )
    draw.rectangle(
        [glass_right, glass_top + glass_h + 10, glass_right + glass_w, glass_top + 2 * glass_h + 10],
        fill=glass_color,
        outline=(100, 130, 160),
        width=2,
    )

    # Cross beams
    draw.line(
        [house_x, house_y + house_h // 2, house_x + house_w, house_y + house_h // 2],
        fill=house_color,
        width=2,
    )
    draw.line(
        [house_x + house_w // 2, house_y, house_x + house_w // 2, house_y + house_h],
        fill=house_color,
        width=2,
    )

    # Roof line - flat modern roof
    draw.line(
        [house_x - 20, house_y, house_x + house_w + 20, house_y],
        fill=house_color,
        width=6,
    )

    # Second smaller structure to the right
    house2_x = house_x + house_w + 40
    house2_y = house_y + 50
    house2_w = 200
    house2_h = 250
    draw.rectangle([house2_x, house2_y, house2_x + house2_w, house2_y + house2_h], outline=house_color, width=4)
    draw.rectangle(
        [house2_x + 10, house2_y + 10, house2_x + house2_w - 10, house2_y + house2_h - 10],
        fill=glass_color,
        outline=(100, 130, 160),
        width=2,
    )
    draw.line(
        [house2_x + house2_w // 2, house2_y, house2_x + house2_w // 2, house2_y + house2_h],
        fill=house_color,
        width=2,
    )

    # Deck / balcony extending from house
    deck_color = (80, 78, 75)
    draw.rectangle([house_x - 30, house_y + house_h, house_x + 120, house_y + house_h + 15], fill=deck_color)
    draw.rectangle([house_x + house_w - 80, house_y + house_h, house_x + house_w, house_y + house_h + 15], fill=deck_color)

    # Railings
    for x_pos in range(house_x - 20, house_x + 130, 25):
        draw.line([(x_pos, house_y + house_h), (x_pos, house_y + house_h + 15)], fill=(100, 100, 100), width=2)
    for x_pos in range(house_x + house_w - 70, house_x + house_w + 10, 25):
        draw.line([(x_pos, house_y + house_h), (x_pos, house_y + house_h + 15)], fill=(100, 100, 100), width=2)


def draw_ocean(draw: ImageDraw.Draw) -> None:
    """Draw the Pacific Ocean in the background."""
    ocean_top = 1050
    # Ocean gradient
    for y in range(ocean_top, 1400):
        ratio = (y - ocean_top) / 350
        r = int(30 * (1 - ratio) + 20 * ratio)
        g = int(80 * (1 - ratio) + 60 * ratio)
        b = int(140 * (1 - ratio) + 110 * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Horizon line
    draw.line([(0, ocean_top), (WIDTH, ocean_top)], fill=(180, 200, 220), width=1)

    # Waves
    wave_color = (100, 140, 180, 60)
    for i in range(20):
        wx = i * 80
        wy = ocean_top + 100 + (i % 3) * 30
        draw.arc([wx, wy, wx + 60, wy + 20], 0, 180, fill=wave_color, width=1)


def draw_sky(draw: ImageDraw.Draw) -> None:
    """Draw the sky with clouds."""
    # Sun glow
    sun_x, sun_y = 1200, 400
    for r in range(120, 0, -5):
        alpha = max(0, 255 - r * 2)
        draw.ellipse(
            [sun_x - r, sun_y - r, sun_x + r, sun_y + r],
            fill=(255, 200, 100, alpha),
            outline=None,
        )

    # Sun
    draw.ellipse([sun_x - 30, sun_y - 30, sun_x + 30, sun_y + 30], fill=(255, 220, 120))

    # Clouds
    cloud_color = (220, 225, 230)
    clouds = [
        (200, 300, 150, 50),
        (500, 250, 200, 40),
        (900, 350, 120, 35),
        (1400, 280, 180, 45),
    ]
    for cx, cy, cw, ch in clouds:
        draw.ellipse([cx, cy, cx + cw, cy + ch], fill=cloud_color)
        draw.ellipse([cx - 30, cy + 10, cx + cw - 30, cy + ch - 10], fill=cloud_color)
        draw.ellipse([cx + 40, cy - 10, cx + cw + 40, cy + ch - 20], fill=cloud_color)


def draw_bottom_panel(draw: ImageDraw.Draw) -> None:
    """Draw the dark bottom panel with title and author."""
    panel_y = 1920
    panel_height = HEIGHT - panel_y

    # Dark semi-transparent panel
    draw.rectangle([0, panel_y, WIDTH, HEIGHT], fill=(20, 20, 30, 220))

    # Decorative line
    line_y = panel_y + 30
    draw.line([(WIDTH // 2 - 150, line_y), (WIDTH // 2 + 150, line_y)], fill=(100, 120, 150), width=2)

    # Title
    try:
        title_font = load_font(TITLE_FONT_SIZE)
    except Exception:
        title_font = ImageFont.load_default()

    title = "The House on the Cliff"
    bbox = draw.textbbox((0, 0), title, font=title_font)
    tw = bbox[2] - bbox[0]
    tx = (WIDTH - tw) // 2
    ty = panel_y + 60
    draw.text((tx, ty), title, fill=(255, 255, 255), font=title_font)

    # Author
    try:
        author_font = load_font(AUTHOR_FONT_SIZE)
    except Exception:
        author_font = ImageFont.load_default()

    author = "Barış Kısır"
    bbox = draw.textbbox((0, 0), author, font=author_font)
    aw = bbox[2] - bbox[0]
    ax = (WIDTH - aw) // 2
    ay = ty + TITLE_FONT_SIZE + 40
    draw.text((ax, ay), author, fill=(200, 200, 200), font=author_font)

    # Genre label
    try:
        genre_font = load_font(GENRE_FONT_SIZE)
    except Exception:
        genre_font = ImageFont.load_default()

    genre = "Domestic Suspense"
    bbox = draw.textbbox((0, 0), genre, font=genre_font)
    gw = bbox[2] - bbox[0]
    gx = (WIDTH - gw) // 2
    gy = ay + AUTHOR_FONT_SIZE + 20
    draw.text((gx, gy), genre, fill=(150, 160, 180), font=genre_font)



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    title = metadata.get("title", "The House on the Cliff")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")
    genre = metadata.get("genre", "Domestic Suspense")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Ocean blue to cliff gray gradient background
    draw_gradient(draw, "#1a3a5c", "#5a5a5a")

    # Sky
    draw_sky(draw)

    # Ocean
    draw_ocean(draw)

    # Cliff and house
    draw_house(draw)

    # Bottom panel with text
    draw_bottom_panel(draw)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.save(args.out, "PNG")
    print(f"Cover saved to {args.out}")


if __name__ == "__main__":
    main()