#!/usr/bin/env python3
"""Cover: The Last Caravan — Single camel train snakes across golden dunes under copper sunset, blue-robed merchant in foreground."""

from __future__ import annotations

import argparse
import json
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
    """Gold to deep indigo desert gradient."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((210, 170, 80), (180, 130, 50), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((180, 130, 50), (120, 80, 60), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((120, 80, 60), (20, 10, 40), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_dunes(draw: ImageDraw, width: int, height: int) -> None:
    """Draw sweeping sand dune shapes across the lower portion."""
    # Background dune
    points_bg = []
    for x in range(0, width + 10, 10):
        y = int(height * 0.55 + 60 * __import__("math").sin(x * 0.004 + 1.2) + 40 * __import__("math").sin(x * 0.008))
        points_bg.append((x, y))
    points_bg.append((width, height))
    points_bg.append((0, height))
    draw.polygon(points_bg, fill=(160, 110, 50, 180))

    # Mid dune
    points_mid = []
    for x in range(0, width + 10, 10):
        y = int(height * 0.62 + 50 * __import__("math").sin(x * 0.005 + 0.5) + 30 * __import__("math").sin(x * 0.009 + 2.0))
        points_mid.append((x, y))
    points_mid.append((width, height))
    points_mid.append((0, height))
    draw.polygon(points_mid, fill=(120, 75, 45, 200))

    # Foreground dune
    points_fg = []
    for x in range(0, width + 10, 10):
        y = int(height * 0.70 + 40 * __import__("math").sin(x * 0.006 + 3.0) + 25 * __import__("math").sin(x * 0.011 + 0.7))
        points_fg.append((x, y))
    points_fg.append((width, height))
    points_fg.append((0, height))
    draw.polygon(points_fg, fill=(80, 50, 30, 220))


def draw_caravan(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a small camel caravan silhouette on the dunes."""
    import math

    caravan_y = int(height * 0.50)
    base_x = int(width * 0.25)

    # Draw 5 camels in silhouette
    for i in range(5):
        cx = base_x + i * 55 + int(15 * math.sin(i * 0.7))
        cy = caravan_y + int(10 * math.sin(i * 1.3))

        # Body
        draw.ellipse([cx - 18, cy - 12, cx + 18, cy + 8], fill=(40, 25, 15))

        # Hump
        draw.ellipse([cx - 8, cy - 22, cx + 8, cy - 2], fill=(40, 25, 15))

        # Neck and head
        draw.line([cx + 14, cy - 5, cx + 22, cy - 28, cx + 26, cy - 30], fill=(40, 25, 15), width=3)

        # Legs
        draw.line([cx - 12, cy + 8, cx - 14, cy + 30], fill=(40, 25, 15), width=2)
        draw.line([cx + 10, cy + 8, cx + 12, cy + 30], fill=(40, 25, 15), width=2)

        # Rider (small figure)
        draw.ellipse([cx - 5, cy - 28, cx + 5, cy - 20], fill=(40, 25, 15))


def draw_sun(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a large hot sun in the upper portion."""
    cx, cy = int(width * 0.65), int(height * 0.15)
    radius = 80

    # Glow layers
    for r in range(radius * 3, radius, -8):
        alpha = max(0, min(60, 60 - (radius * 3 - r) // 8))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 200, 100, alpha))

    # Sun body
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(255, 180, 50))


def draw_oasis(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a small oasis with palm trees in the distance."""
    import math

    ox, oy = int(width * 0.72), int(height * 0.48)

    # Water pool
    draw.ellipse([ox - 40, oy - 8, ox + 40, oy + 8], fill=(80, 140, 180, 120))
    draw.ellipse([ox - 35, oy - 5, ox + 35, oy + 5], fill=(60, 120, 160, 100))

    # Palm trees
    for i in range(3):
        px = ox - 25 + i * 25
        py = oy - 5

        # Trunk
        trunk_points = []
        for s in range(10):
            t = s / 10
            px_t = px - int(4 * t * t) + int(3 * math.sin(t * 3))
            py_t = py - int(60 * t)
            trunk_points.append((px_t, py_t))
        draw.line(trunk_points, fill=(50, 35, 20), width=4)

        # Fronds
        top_x, top_y = trunk_points[-1]
        for angle in range(-60, 90, 30):
            rad = math.radians(angle - 90)
            end_x = top_x + int(25 * math.cos(rad))
            end_y = top_y + int(25 * math.sin(rad))
            draw.line([top_x, top_y, end_x, end_y], fill=(30, 80, 30), width=2)


def draw_stars(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a scattering of stars in the upper sky."""
    import random

    rng = random.Random(13)
    for _ in range(80):
        x = rng.randint(0, width)
        y = rng.randint(0, int(height * 0.35))
        size = rng.randint(1, 3)
        brightness = rng.randint(180, 255)
        draw.ellipse([x - size, y - size, x + size, y + size], fill=(brightness, brightness, brightness, 200))


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom with white text."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    for y in range(panel_top, height):
        t = (y - panel_top) / (height - panel_top)
        c = lerp_color((15, 10, 30), (5, 3, 15), t)
        draw.line([(0, y), (width, y)], fill=c)

    # Top border accent - gold line
    draw.line([(0, panel_top), (width, panel_top)], fill=(210, 170, 80), width=3)

    # Decorative lines on sides
    for offset in [50, width - 50]:
        draw.line([(offset, panel_top + 15), (offset, panel_top + 25)], fill=(210, 170, 80), width=2)

    # Title text
    title = "The Last\nCaravan"
    title_font_size = 82
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    y_offset = panel_top + 80
    lines = title.split("\n")
    for idx, line in enumerate(lines):
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 0
        tx = (width - tw) // 2
        # Shadow for readability
        draw.text((tx + 2, y_offset + 2), line, fill=(0, 0, 0), font=title_font)
        draw.text((tx, y_offset), line, fill=(255, 255, 255), font=title_font)
        y_offset += 100

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
    ay = y_offset + 30

    # Author shadow
    draw.text((ax + 2, ay + 2), author, fill=(0, 0, 0), font=author_font)
    draw.text((ax, ay), author, fill=(255, 200, 100), font=author_font)

    # Bottom decorative line
    draw.line([(int(width * 0.35), ay + 55), (int(width * 0.65), ay + 55)], fill=(210, 170, 80), width=1)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Last Caravan")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    rng = __import__("random").Random(7)

    # Copper sunset gradient: gold to deep copper
    for y in range(HEIGHT):
        t = y / HEIGHT
        if t < 0.3:
            r, g, b = 210 + 45 * (t / 0.3), 170 + 30 * (t / 0.3), 80 + 10 * (t / 0.3)
        elif t < 0.55:
            r, g, b = 255 - 60 * ((t - 0.3) / 0.25), 200 - 70 * ((t - 0.3) / 0.25), 90 - 30 * ((t - 0.3) / 0.25)
        else:
            r, g, b = 195 - 170 * ((t - 0.55) / 0.45), 130 - 120 * ((t - 0.55) / 0.45), 60 - 50 * ((t - 0.55) / 0.45)
        draw.line([(0, y), (WIDTH, y)], fill=(max(0, int(r)), max(0, int(g)), max(0, int(b)), 255))

    # Copper sun
    sun_x, sun_y = int(WIDTH * 0.6), int(HEIGHT * 0.22)
    for rr in range(100, 0, -3):
        draw.ellipse([sun_x - rr, sun_y - rr, sun_x + rr, sun_y + rr], fill=(255, 200 + int(55 * (1 - rr / 100)), 80, max(0, 70 - rr)))
    draw.ellipse([sun_x - 60, sun_y - 60, sun_x + 60, sun_y + 60], fill=(255, 220, 100))

    # Golden dunes
    for layer, (base_y, color) in enumerate([(int(HEIGHT * 0.50), (180, 140, 60)), (int(HEIGHT * 0.58), (140, 100, 45)), (int(HEIGHT * 0.66), (100, 70, 35))]):
        pts = [(0, HEIGHT)]
        for x in range(0, WIDTH + 10, 10):
            y = base_y + int(40 * __import__("math").sin(x * 0.005 + layer * 0.7) + 25 * __import__("math").sin(x * 0.012 + layer * 1.3))
            pts.append((x, y))
        pts.append((WIDTH, HEIGHT))
        draw.polygon(pts, fill=color + (180 - layer * 30,))

    # Camel train snaking across dunes
    for i in range(8):
        cx = int(WIDTH * 0.1 + i * 65 + 15 * __import__("math").sin(i * 0.7))
        cy = int(HEIGHT * 0.48 + 15 * __import__("math").sin(i * 1.3) - i * 3)
        # Body
        draw.ellipse([cx - 18, cy - 10, cx + 18, cy + 8], fill=(35, 22, 12))
        # Hump
        draw.ellipse([cx - 8, cy - 20, cx + 8, cy - 2], fill=(35, 22, 12))
        # Neck & head
        draw.line([cx + 14, cy - 5, cx + 22, cy - 26, cx + 26, cy - 28], fill=(35, 22, 12), width=3)
        # Legs
        draw.line([cx - 12, cy + 8, cx - 14, cy + 28], fill=(35, 22, 12), width=2)
        draw.line([cx + 10, cy + 8, cx + 12, cy + 28], fill=(35, 22, 12), width=2)

    # Blue-robed merchant in foreground
    mx, my = int(WIDTH * 0.72), int(HEIGHT * 0.56)
    # Robe
    draw.polygon([(mx - 20, my), (mx + 20, my), (mx + 15, my + 100), (mx - 15, my + 100)], fill=(20, 40, 120))
    # Head
    draw.ellipse([mx - 10, my - 25, mx + 10, my - 5], fill=(25, 20, 18))
    # Turban
    draw.ellipse([mx - 14, my - 32, mx + 14, my - 22], fill=(15, 30, 100))
    draw.rectangle([mx - 12, my - 35, mx + 12, my - 28], fill=(15, 30, 100))
    # Staff
    draw.line([mx + 25, my + 20, mx + 25, my + 140], fill=(60, 40, 25), width=4)
    # Arm holding staff
    draw.line([mx + 15, my, mx + 25, my + 20], fill=(20, 40, 120), width=5)

    # Stars
    for _ in range(60):
        sx = int(rng.random() * WIDTH)
        sy = int(rng.random() * int(HEIGHT * 0.3))
        ss = rng.randint(1, 2)
        draw.ellipse([sx - ss, sy - ss, sx + ss, sy + ss], fill=(255, 255, 255, rng.randint(150, 220)))

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