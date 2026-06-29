#!/usr/bin/env python3
"""Generate cover image for The Last Tram — 1600x2560 slipstream cover."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
except ImportError:
    raise SystemExit("Pillow required: pip install Pillow")

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
BG_COLOR = (35, 25, 20)
SEPIA_LIGHT = (210, 180, 140)
SEPIA_DARK = (60, 45, 35)
YELLOW_TRAM = (220, 175, 55)
COBBLE_GRAY = (110, 105, 100)
FONT_DIR = Path("C:/Windows/Fonts")


def hex_to_rgb(h: str) -> tuple[int, ...]:
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def make_gradient(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a vertical sepia-to-dark gradient."""
    for y in range(height):
        ratio = y / height
        r = int(BG_COLOR[0] * (1 - ratio) + SEPIA_LIGHT[0] * ratio * 0.3)
        g = int(BG_COLOR[1] * (1 - ratio) + SEPIA_LIGHT[1] * ratio * 0.3)
        b = int(BG_COLOR[2] * (1 - ratio) + SEPIA_LIGHT[2] * ratio * 0.3)
        draw.line([(0, y), (width, y)], fill=(r, g, b))


def draw_stars(draw: ImageDraw, width: int, height: int, count: int = 80) -> None:
    """Scatter faint star-like dots in the upper portion."""
    import random

    random.seed(42)
    for _ in range(count):
        x = random.randint(0, width)
        y = random.randint(0, height // 3)
        r = random.randint(1, 3)
        alpha = random.randint(30, 100)
        shade = 200 + random.randint(0, 55)
        draw.ellipse(
            [x - r, y - r, x + r, y + r],
            fill=(shade, shade, shade, alpha),
        )


def draw_cobblestones(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a cobblestone street receding into the distance."""
    # Street base
    street_left = width // 4
    street_right = width * 3 // 4
    # Slight perspective: converging toward center
    for y_off in range(height // 3, height - 400, 12):
        ratio = (y_off - height // 3) / (height - 400 - height // 3)
        left_x = int(street_left + (width // 2 - street_left) * ratio)
        right_x = int(street_right - (street_right - width // 2) * ratio)
        # Base line
        gray_v = int(COBBLE_GRAY[0] * (0.4 + 0.6 * (1 - ratio)))
        draw.line([(left_x, y_off), (right_x, y_off)], fill=(gray_v, gray_v - 5, gray_v - 10), width=1)
        # Cobble curves
        spacing = max(8, int(20 * (1 - ratio * 0.7)))
        for x in range(left_x, right_x, spacing):
            rx = x + int((spacing // 3) * (1 if (x // spacing) % 2 == 0 else -1))
            ry = y_off + 2
            draw.arc(
                [rx, ry - 5, rx + spacing // 2, ry + 5],
                start=0,
                end=180,
                fill=(gray_v + 15, gray_v + 10, gray_v + 5),
                width=1,
            )


def draw_tram(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a vintage Lisbon tram in silhouette with yellow highlights."""
    cx, cy = width // 2, height // 3
    # Tram body
    tram_w, tram_h = 320, 180
    x0 = cx - tram_w // 2
    y0 = cy - tram_h // 2

    # Main body (dark silhouette with sepia tint)
    body_color = (55, 45, 35)
    draw.rounded_rectangle(
        [x0, y0, x0 + tram_w, y0 + tram_h],
        radius=12,
        fill=body_color,
    )

    # Yellow stripe
    stripe_y = y0 + tram_h // 3
    draw.rectangle(
        [x0 + 10, stripe_y, x0 + tram_w - 10, stripe_y + 6],
        fill=YELLOW_TRAM,
    )
    draw.rectangle(
        [x0 + 10, stripe_y + tram_h // 3, x0 + tram_w - 10, stripe_y + tram_h // 3 + 6],
        fill=YELLOW_TRAM,
    )

    # Windows
    win_color = (180, 160, 130)
    win_w, win_h = 40, 50
    for i in range(5):
        wx = x0 + 20 + i * (win_w + 15)
        wy = y0 + 15
        # Window frame
        draw.rounded_rectangle(
            [wx, wy, wx + win_w, wy + win_h],
            radius=4,
            fill=win_color,
            outline=body_color,
            width=2,
        )
        # Warm window glow
        draw.rounded_rectangle(
            [wx + 4, wy + 4, wx + win_w - 4, wy + win_h - 4],
            radius=3,
            fill=(230, 200, 140),
        )

    # Roof
    roof_color = (45, 35, 28)
    draw.rounded_rectangle(
        [x0 + 5, y0 - 15, x0 + tram_w - 5, y0],
        radius=6,
        fill=roof_color,
    )

    # Undercarriage
    under_color = (30, 25, 20)
    draw.rectangle(
        [x0 + 30, y0 + tram_h, x0 + tram_w - 30, y0 + tram_h + 15],
        fill=under_color,
    )

    # Wheels
    for wx in [x0 + 40, x0 + tram_w - 40]:
        draw.ellipse(
            [wx - 12, y0 + tram_h + 8, wx + 12, y0 + tram_h + 32],
            fill=(35, 30, 25),
            outline=(60, 50, 40),
            width=2,
        )

    # Headlight glow
    glow_center = (x0 + tram_w + 5, y0 + tram_h // 2)
    for r in range(40, 10, -5):
        alpha = max(30, 120 - r * 3)
        draw.ellipse(
            [glow_center[0] - r, glow_center[1] - r, glow_center[0] + r, glow_center[1] + r],
            fill=(YELLOW_TRAM[0], YELLOW_TRAM[1], YELLOW_TRAM[2], alpha),
        )
    # Bright center
    draw.ellipse(
        [glow_center[0] - 8, glow_center[1] - 8, glow_center[0] + 8, glow_center[1] + 8],
        fill=(255, 230, 150),
    )

    # Overhead wire
    draw.line(
        [(x0 - 20, y0 - 30), (x0 + tram_w + 20, y0 - 30)],
        fill=(60, 55, 48),
        width=3,
    )
    # Pantograph
    draw.line(
        [(x0 + tram_w // 2 - 10, y0 - 15), (x0 + tram_w // 2, y0 - 30)],
        fill=(60, 55, 48),
        width=2,
    )


def draw_moon(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a pale moon in the upper right."""
    mx, my = width - 180, 120
    moon_r = 50
    draw.ellipse(
        [mx - moon_r, my - moon_r, mx + moon_r, my + moon_r],
        fill=(210, 200, 180),
    )
    # Soft glow
    for r in range(moon_r + 10, moon_r + 60, 10):
        draw.ellipse(
            [mx - r, my - r, mx + r, my + r],
            fill=(180, 170, 150, 15),
        )


def draw_buildings(draw: ImageDraw, width: int, height: int) -> None:
    """Draw silhouette buildings on both sides of the street."""
    # Left buildings
    for i in range(4):
        bx = 20 + i * 90
        bh = 180 + i * 30
        draw.rectangle(
            [bx, height // 3 - bh, bx + 80, height - 450],
            fill=(40 + i * 5, 35 + i * 3, 30 + i * 2),
        )
        # Windows
        for wy in range(height // 3 - bh + 20, height - 470, 35):
            draw.rectangle(
                [bx + 15, wy, bx + 30, wy + 20],
                fill=(220, 200, 160, 30),
            )
            draw.rectangle(
                [bx + 45, wy, bx + 60, wy + 20],
                fill=(220, 200, 160, 30),
            )

    # Right buildings
    for i in range(3):
        bx = width - 100 - i * 100
        bh = 200 + i * 25
        draw.rectangle(
            [bx, height // 3 - bh, bx + 90, height - 450],
            fill=(38 + i * 4, 33 + i * 3, 28 + i * 2),
        )
        for wy in range(height // 3 - bh + 20, height - 470, 35):
            draw.rectangle(
                [bx + 20, wy, bx + 35, wy + 20],
                fill=(210, 190, 150, 25),
            )
            draw.rectangle(
                [bx + 55, wy, bx + 70, wy + 20],
                fill=(210, 190, 150, 25),
            )


def draw_title_panel(
    draw: ImageDraw,
    image: Image.Image,
    width: int,
    height: int,
    title_font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    author_font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
) -> None:
    """Draw dark title panel at bottom with white text."""
    panel_top = 1920
    # Dark panel with slight gradient
    for y in range(panel_top, HEIGHT):
        ratio = (y - panel_top) / (HEIGHT - panel_top)
        r = int(20 * (1 - ratio) + 40 * ratio)
        g = int(18 * (1 - ratio) + 35 * ratio)
        b = int(15 * (1 - ratio) + 28 * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Thin gold line at top of panel
    draw.line([(100, panel_top), (width - 100, panel_top)], fill=YELLOW_TRAM, width=2)

    # Title
    title = "THE LAST TRAM"
    # Try to get bbox for centering
    bbox = draw.textbbox((0, 0), title, font=title_font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (width - tw) // 2
    ty = panel_top + 80
    draw.text((tx, ty), title, fill=(255, 255, 255), font=title_font)

    # Author
    author = "Barış Kısır"
    bbox_a = draw.textbbox((0, 0), author, font=author_font)
    aw = bbox_a[2] - bbox_a[0]
    ax = (width - aw) // 2
    ay = ty + th + 80
    draw.text((ax, ay), author, fill=(YELLOW_TRAM[0], YELLOW_TRAM[1], YELLOW_TRAM[2]), font=author_font)

    # Decorative line below author
    line_y = ay + 50
    draw.line([(width // 2 - 80, line_y), (width // 2 + 80, line_y)], fill=YELLOW_TRAM, width=1)



def main() -> None:
    parser = argparse.ArgumentParser(description="Generate cover for The Last Tram")
    parser.add_argument("--metadata", required=True, type=Path, help="Path to metadata JSON")
    parser.add_argument("--out", type=Path, default=None, help="Output PNG path")
    args = parser.parse_args()

    metadata_path = Path(args.metadata)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    out_path = Path(args.out) if args.out else Path(metadata["cover_path"])

    # Load fonts
    title_font_path = FONT_DIR / "arialbd.ttf"
    author_font_path = FONT_DIR / "arial.ttf"

    try:
        title_font = ImageFont.truetype(str(title_font_path), 72)
        author_font = ImageFont.truetype(str(author_font_path), 36)
    except (IOError, OSError):
        print("Warning: arialbd.ttf not found, using default font")
        title_font = ImageFont.load_default()
        author_font = ImageFont.load_default()

    # Create image
    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(image)

    # Build cover layers
    make_gradient(draw, WIDTH, HEIGHT)
    draw_stars(draw, WIDTH, HEIGHT)
    draw_moon(draw, WIDTH, HEIGHT)
    draw_buildings(draw, WIDTH, HEIGHT)
    draw_cobblestones(draw, WIDTH, HEIGHT)
    draw_tram(draw, WIDTH, HEIGHT)
    draw_title_panel(draw, image, WIDTH, HEIGHT, title_font, author_font)

    # Soft haze overlay for slipstream feel
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (180, 160, 130, 20))
    image = Image.alpha_composite(image, overlay)

    # Slight vignette
    vignette = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    v_draw = ImageDraw.Draw(vignette)
    for r in range(max(WIDTH, HEIGHT) // 2, 0, -20):
        alpha = max(0, 60 - r // 6)
        v_draw.ellipse(
            [WIDTH // 2 - r, HEIGHT // 2 - r, WIDTH // 2 + r, HEIGHT // 2 + r],
            outline=(0, 0, 0, alpha),
            width=20,
        )
    image = Image.alpha_composite(image, vignette)

    # Convert to RGB for saving as PNG
    final = image.convert("RGB")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(final, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()))
    final.save(out_path, "PNG")
    print(f"Cover saved: {out_path}")

    # Verify
    img = Image.open(out_path)
    print(f"Dimensions: {img.size[0]}x{img.size[1]}")


if __name__ == "__main__":
    main()