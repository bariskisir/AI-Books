#!/usr/bin/env python3
"""Generate a cover image for The Carnival at Midnight."""

from __future__ import annotations

import argparse
import json
import math
import os
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


def get_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    """Try to load arialbd/arial, falling back to default."""
    paths = [
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def draw_gradient(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a vertical gradient from deep purple (top) to midnight blue (bottom)."""
    for y in range(height):
        ratio = y / height
        r = int(15 + ratio * 10)
        g = int(5 + ratio * 5)
        b = int(40 + ratio * 30)
        draw.line([(0, y), (width, y)], fill=(r, g, b))


def draw_stars(draw: ImageDraw, width: int, height: int) -> None:
    """Draw scattered stars in the upper portion."""
    import random

    random.seed(42)
    for _ in range(200):
        x = random.randint(0, width)
        y = random.randint(0, height // 2)
        size = random.randint(1, 3)
        brightness = random.randint(150, 255)
        draw.ellipse(
            [x - size, y - size, x + size, y + size],
            fill=(brightness, brightness, min(255, brightness + 20), 200),
        )


def draw_moon(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a crescent moon."""
    cx, cy = width - 300, 250
    r = 80
    # Full moon base
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(220, 200, 160, 200))
    # Crescent cutout
    draw.ellipse(
        [cx - r + 25, cy - r - 20, cx + r + 10, cy + r - 10],
        fill=(15, 5, 40),
    )


def draw_tents(draw: ImageDraw, width: int, height: int) -> None:
    """Draw carnival tent silhouettes at the bottom third."""
    # Big top tent - center
    tent_data = [
        # (center_x, width, height, color)
        (width // 2, 500, 350, (180, 30, 50)),  # main tent red
        (width // 2 - 300, 250, 200, (140, 25, 90)),  # left tent purple
        (width // 2 + 320, 250, 200, (140, 25, 90)),  # right tent purple
        (width // 2 - 150, 180, 140, (200, 40, 60)),  # small red
        (width // 2 + 180, 180, 140, (200, 40, 60)),  # small red
        (width // 2 - 480, 200, 160, (100, 20, 70)),  # far left
        (width // 2 + 480, 200, 160, (100, 20, 70)),  # far right
    ]

    base_y = height - 800

    for cx, tw, th, color in tent_data:
        # Tent body - triangle
        draw.polygon(
            [(cx - tw // 2, base_y), (cx, base_y - th), (cx + tw // 2, base_y)],
            fill=color,
        )
        # Tent stripes
        stripe_color = tuple(min(c + 40, 255) for c in color)
        for i in range(1, 5):
            x_offset = int(tw // 2 * (i / 5))
            draw.line(
                [(cx - x_offset, base_y), (cx, base_y - th + int(th * (i / 5)))],
                fill=stripe_color,
                width=3,
            )
            draw.line(
                [(cx + x_offset, base_y), (cx, base_y - th + int(th * (i / 5)))],
                fill=stripe_color,
                width=3,
            )
        # Flag on top
        draw.polygon(
            [(cx, base_y - th), (cx + 20, base_y - th + 30), (cx, base_y - th + 15)],
            fill=(255, 200, 50),
        )


def draw_ferris_wheel(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a ferris wheel on the right side."""
    cx = width - 200
    cy = height - 1100
    r = 200

    # Wheel frame
    draw.ellipse(
        [cx - r, cy - r, cx + r, cy + r],
        outline=(200, 180, 150),
        width=4,
    )
    # Spokes
    for angle_deg in range(0, 360, 30):
        rad = math.radians(angle_deg)
        x1 = cx + int(r * math.cos(rad))
        y1 = cy + int(r * math.sin(rad))
        draw.line([(cx, cy), (x1, y1)], fill=(180, 160, 130), width=2)

    # Carriages
    for angle_deg in range(0, 360, 30):
        rad = math.radians(angle_deg)
        cx_c = cx + int(r * math.cos(rad))
        cy_c = cy + int(r * math.sin(rad))
        draw.rectangle(
            [cx_c - 12, cy_c - 8, cx_c + 12, cy_c + 8],
            fill=(60, 40, 80),
            outline=(200, 180, 150),
        )
        # Light in carriage
        draw.ellipse(
            [cx_c - 4, cy_c - 4, cx_c + 4, cy_c + 4],
            fill=(255, 200, 50),
        )

    # Support legs
    draw.line([(cx - 20, cy + r), (cx - 40, cy + r + 300)], fill=(100, 90, 80), width=8)
    draw.line([(cx + 20, cy + r), (cx + 40, cy + r + 300)], fill=(100, 90, 80), width=8)
    draw.line([(cx - 40, cy + r + 300), (cx + 40, cy + r + 300)], fill=(100, 90, 80), width=6)


def draw_title_panel(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the dark title panel at the bottom with white text."""
    panel_top = 1920
    panel_bottom = 2560

    # Dark gradient panel
    for y in range(panel_top, panel_bottom):
        ratio = (y - panel_top) / (panel_bottom - panel_top)
        alpha = int(180 + 75 * ratio)
        r = int(10 * (1 - ratio) + 20 * ratio)
        g = int(5 * (1 - ratio) + 10 * ratio)
        b = int(20 * (1 - ratio) + 35 * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Gold border line at top of panel
    draw.line([(200, panel_top + 5), (width - 200, panel_top + 5)], fill=(210, 175, 60), width=2)

    # Load fonts
    font_large = get_font(72)
    font_small = get_font(36)

    # Title text
    title = "The Carnival"
    subtitle = "at Midnight"

    # Use textbbox for center alignment
    bbox1 = draw.textbbox((0, 0), title, font=font_large)
    tw1 = bbox1[2] - bbox1[0]
    tx = (width - tw1) // 2
    ty = panel_top + 80
    draw.text((tx, ty), title, fill=(255, 255, 255), font=font_large)

    bbox2 = draw.textbbox((0, 0), subtitle, font=font_large)
    tw2 = bbox2[2] - bbox2[0]
    tx2 = (width - tw2) // 2
    ty2 = ty + 90
    draw.text((tx2, ty2), subtitle, fill=(255, 255, 255), font=font_large)

    # Author name
    author = "Barış Kısır"
    bbox3 = draw.textbbox((0, 0), author, font=font_small)
    tw3 = bbox3[2] - bbox3[0]
    tx3 = (width - tw3) // 2
    ty3 = ty2 + 100
    draw.text((tx3, ty3), author, fill=(210, 175, 60), font=font_small)

    # Bottom gold border
    draw.line([(200, panel_bottom - 20), (width - 200, panel_bottom - 20)], fill=(210, 175, 60), width=2)

    # Genre tag
    genre_tag = "Weird Fiction"
    font_tag = get_font(28, bold=False)
    bbox4 = draw.textbbox((0, 0), genre_tag, font=font_tag)
    tw4 = bbox4[2] - bbox4[0]
    tx4 = (width - tw4) // 2
    ty4 = panel_bottom - 85
    draw.text((tx4, ty4), genre_tag, fill=(180, 180, 180), font=font_tag)


def generate_cover(metadata_path: str, output_path: str) -> None:
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    draw_gradient(draw, WIDTH, HEIGHT)
    draw_stars(draw, WIDTH, HEIGHT)
    draw_moon(draw, WIDTH, HEIGHT)
    draw_tents(draw, WIDTH, HEIGHT)
    draw_ferris_wheel(draw, WIDTH, HEIGHT)
    draw_title_panel(draw, WIDTH, HEIGHT)

    model = _standard_cover_metadata_from_locals(locals()).get("model", "")
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, help="Path to metadata JSON")
    parser.add_argument("--out", required=True, help="Output PNG path")
    args = parser.parse_args()
    generate_cover(args.metadata, args.out)


if __name__ == "__main__":
    main()