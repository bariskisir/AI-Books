#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Last Shot."""

from __future__ import annotations

import argparse
import json
import math
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



ROOT = Path(__file__).resolve().parents[3]
FONTS_DIR = Path("C:/Windows/Fonts")

WIDTH, HEIGHT = 1600, 2560
TITLE_PANEL_TOP = 1920


def rel(path: str | Path) -> Path:
    p = Path(path)
    return ROOT / p if not p.is_absolute() else p


def lerp_color(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def draw_gradient(draw: ImageDraw, width: int, height: int) -> None:
    """Sky blue to grass green gradient for Wimbledon feel."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((70, 140, 210), ((100, 180, 230)), t)
        else:
            t = (y - height * 0.4) / (height * 0.6)
            c = lerp_color((100, 180, 230), ((20, 100, 40)), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_grass_court(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a tennis court from a perspective view."""
    # Court surface (trapezoid for perspective)
    court_top = int(height * 0.25)
    court_bottom = int(height * 0.78)
    court_left = int(width * 0.15)
    court_right = int(width * 0.85)
    center_x = width // 2

    # Main court area - green rectangle (grass)
    court_color = (40, 130, 60)
    court_poly = [
        (court_left + 120, court_top),
        (court_right - 120, court_top),
        (court_right, court_bottom),
        (court_left, court_bottom),
    ]
    draw.polygon(court_poly, fill=court_color)

    # Court lines - white
    line_color = (240, 240, 240)

    # Singles sidelines
    draw.line([(court_left + 160, court_top), (court_left + 30, court_bottom)], fill=line_color, width=3)
    draw.line([(court_right - 160, court_top), (court_right - 30, court_bottom)], fill=line_color, width=3)

    # Doubles sidelines
    draw.line([(court_left + 120, court_top), (court_left, court_bottom)], fill=line_color, width=2)
    draw.line([(court_right - 120, court_top), (court_right, court_bottom)], fill=line_color, width=2)

    # Baseline
    draw.line([(court_left + 30, court_bottom), (court_right - 30, court_bottom)], fill=line_color, width=3)

    # Service line (top)
    service_y = court_top + int((court_bottom - court_top) * 0.35)
    draw.line([(court_left + 135, service_y), (court_right - 135, service_y)], fill=line_color, width=3)

    # Center service line
    center_top_x = court_left + (court_right - court_left) // 2
    center_bottom_x = court_left + 30 + (court_right - court_left - 60) // 2
    draw.line([(center_top_x, court_top), (center_bottom_x, court_bottom)], fill=line_color, width=3)

    # Center hash at baseline
    hash_left = center_bottom_x - 15
    hash_right = center_bottom_x + 15
    draw.line([(hash_left, court_bottom), (hash_right, court_bottom)], fill=line_color, width=3)


def draw_net(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the tennis net across the middle of the court."""
    net_y = int(height * 0.42)
    net_left = int(width * 0.12)
    net_right = int(width * 0.88)

    # Net band (top)
    draw.line([(net_left, net_y), (net_right, net_y)], fill=(200, 200, 200), width=4)

    # Net posts
    post_height = 40
    draw.rectangle([net_left - 4, net_y - post_height, net_left, net_y], fill=(180, 180, 180))
    draw.rectangle([net_right, net_y - post_height, net_right + 4, net_y], fill=(180, 180, 180))

    # Net mesh (vertical lines)
    for x in range(net_left, net_right, 8):
        draw.line([(x, net_y - 35), (x, net_y + 15)], fill=(180, 180, 180, 80), width=1)

    # Net white tape at top
    draw.line([(net_left, net_y - 2), (net_right, net_y - 2)], fill=(255, 255, 255), width=5)
    draw.line([(net_left, net_y + 14), (net_right, net_y + 14)], fill=(200, 200, 200), width=2)


def draw_tennis_ball(draw: ImageDraw, x: int, y: int, size: int = 20) -> None:
    """Draw a tennis ball."""
    # Ball shadow/glow
    draw.ellipse([x - size - 5, y - size - 5, x + size + 5, y + size + 5], fill=(100, 200, 100, 40))

    # Ball body
    ball_color = (210, 210, 100)
    draw.ellipse([x - size, y - size, x + size, y + size], fill=ball_color)

    # Ball line (seam)
    draw.arc([x - size, y - size, x + size, y + size], 0, 360, fill=(180, 180, 80), width=2)
    draw.arc([x - size + 2, y - size + 2, x + size - 2, y + size - 2], 200, 340, fill=(180, 180, 80), width=1)

    # Highlight
    draw.ellipse([x - size // 3, y - size // 3, x + size // 8, y + size // 8], fill=(255, 255, 200, 100))


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark title panel at the bottom with white text."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    draw.rectangle([(0, panel_top), (width, height)], fill=(15, 40, 20))

    # Subtle top border
    draw.line([(0, panel_top), (width, panel_top)], fill=(30, 80, 40), width=3)

    # Title text
    title = "The Last Shot"
    title_font_size = 80
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    try:
        bbox = draw.textbbox((0, 0), title, font=title_font)
        tw = bbox[2] - bbox[0]
    except Exception:
        tw = 0
    tx = (width - tw) // 2
    ty = panel_top + 80
    # Shadow
    draw.text((tx + 2, ty + 2), title, fill=(0, 0, 0), font=title_font)
    draw.text((tx, ty), title, fill=(255, 255, 255), font=title_font)

    # Decorative line
    line_y = ty + 100
    draw.line([(width // 2 - 120, line_y), (width // 2 + 120, line_y)], fill=(60, 180, 80), width=2)

    # Author name
    author = "Barış Kısır"
    author_font_size = 36
    try:
        author_font = ImageFont.truetype(str(font_paths["author"]), author_font_size)
    except Exception:
        author_font = ImageFont.load_default()

    try:
        abbox = draw.textbbox((0, 0), author, font=author_font)
        aw = abbox[2] - abbox[0]
    except Exception:
        aw = 0
    ax = (width - aw) // 2
    ay = line_y + 40
    draw.text((ax + 1, ay + 1), author, fill=(0, 0, 0), font=author_font)
    draw.text((ax, ay), author, fill=(200, 230, 200), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Last Shot")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Sky-to-grass gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Grass court with white lines
    draw_grass_court(draw, WIDTH, HEIGHT)

    # Step 3: Tennis net
    draw_net(draw, WIDTH, HEIGHT)

    # Step 4: Tennis balls scattered on court
    draw_tennis_ball(draw, WIDTH // 2 + 200, int(HEIGHT * 0.55), 18)
    draw_tennis_ball(draw, WIDTH // 2 - 250, int(HEIGHT * 0.35), 14)
    draw_tennis_ball(draw, WIDTH // 2 + 300, int(HEIGHT * 0.70), 12)

    # Step 5: Centre Court roof/outline silhouette at top
    roof_color = (50, 60, 70, 180)
    roof_points = [
        (int(WIDTH * 0.3), int(HEIGHT * 0.08)),
        (int(WIDTH * 0.4), int(HEIGHT * 0.02)),
        (int(WIDTH * 0.6), int(HEIGHT * 0.02)),
        (int(WIDTH * 0.7), int(HEIGHT * 0.08)),
        (int(WIDTH * 0.7), int(HEIGHT * 0.15)),
        (int(WIDTH * 0.3), int(HEIGHT * 0.15)),
    ]
    draw.polygon(roof_points, fill=roof_color)

    # Roof support lines
    for rx in range(int(WIDTH * 0.33), int(WIDTH * 0.68), int(WIDTH * 0.07)):
        draw.line(
            [(rx, int(HEIGHT * 0.10)), (rx + 30, int(HEIGHT * 0.04))],
            fill=(100, 110, 120, 120), width=2
        )

    # Step 6: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
        "small": str(FONTS_DIR / "arial.ttf"),
    }
    draw_title_panel(draw, WIDTH, HEIGHT, font_paths)

    # Soften slightly
    img = img.filter(ImageFilter.SMOOTH)

    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    metadata_path = rel(args.metadata)
    output_path = rel(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    create_cover(metadata_path, output_path)


if __name__ == "__main__":
    main()