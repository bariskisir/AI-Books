#!/usr/bin/env python3
"""Generate a book cover using PIL for The Astronomer's Daughter."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont


except ImportError:
    raise SystemExit("Pillow is required. Install with: pip install Pillow")

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
FONT_DIR = Path("C:/Windows/Fonts")


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def star_points(cx: float, cy: float, outer: float, inner: float, n: int = 5) -> list[tuple[float, float]]:
    pts = []
    for i in range(n * 2):
        angle = -90 + i * (360 / (n * 2))
        r = outer if i % 2 == 0 else inner
        import math
        pts.append((cx + r * math.cos(math.radians(angle)), cy + r * math.sin(math.radians(angle))))
    return pts


def create_cover(metadata_path: Path, output_path: Path) -> None:
    with open(metadata_path, encoding="utf-8") as f:
        meta = json.load(f)
    model = meta.get("model", "")

    title = meta["title"]
    author = meta["author"]

    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)

    # Deep navy-to-charcoal gradient background
    navy = hex_to_rgb("0a1628")  # Deep night
    star_gold = hex_to_rgb("d4af37")  # Star gold accent
    dark_panel = hex_to_rgb("0a0d14")  # Very dark for bottom panel

    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(navy[0] * (1 - ratio) + 15 * ratio)
        g = int(navy[1] * (1 - ratio) + 18 * ratio)
        b = int(navy[2] * (1 - ratio) + 30 * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Star chart circles
    import math
    cx, cy = WIDTH // 2, HEIGHT // 2 - 120
    for r in [300, 450, 600]:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(100, 110, 130, 80), width=1)

    # Grid lines (declination/right-ascension)
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        x2 = cx + 700 * math.cos(rad)
        y2 = cy + 700 * math.sin(rad)
        draw.line([(cx, cy), (x2, y2)], fill=(60, 70, 90, 60), width=1)

    # Observatory dome silhouette
    dome_cx, dome_cy = cx, cy + 80
    dome_r = 180
    draw.arc([dome_cx - dome_r, dome_cy - dome_r, dome_cx + dome_r, dome_cy + dome_r], 0, 180, fill=(180, 185, 195), width=3)
    draw.rectangle([dome_cx - dome_r, dome_cy, dome_cx + dome_r, dome_cy + 60], fill=(180, 185, 195))
    # Slit in dome
    draw.rectangle([dome_cx - 6, dome_cy - dome_r + 20, dome_cx + 6, dome_cy], fill=(10, 15, 30))

    # Telescope silhouette
    telescope_x = dome_cx + 280
    telescope_y = dome_cy - 40
    draw.line([(telescope_x, telescope_y), (telescope_x + 120, telescope_y - 200)], fill=(200, 205, 215), width=6)
    draw.line([(telescope_x + 120, telescope_y - 200), (telescope_x + 135, telescope_y - 220)], fill=(200, 205, 215), width=8)
    # Tripod
    draw.line([(telescope_x, telescope_y), (telescope_x - 30, telescope_y + 80)], fill=(160, 165, 175), width=3)
    draw.line([(telescope_x, telescope_y), (telescope_x + 30, telescope_y + 80)], fill=(160, 165, 175), width=3)
    draw.line([(telescope_x - 30, telescope_y + 80), (telescope_x + 30, telescope_y + 80)], fill=(160, 165, 175), width=3)

    # Stars scattered across sky
    import random
    random.seed(42)
    for _ in range(200):
        sx = random.randint(0, WIDTH)
        sy = random.randint(0, HEIGHT // 2 + 200)
        size = random.randint(1, 3)
        brightness = random.randint(160, 255)
        draw.ellipse([sx, sy, sx + size, sy + size], fill=(brightness, brightness, int(brightness * 0.9)))

    # Bright stars with cross
    bright_stars = [(200, 180), (400, 100), (1200, 250), (1400, 150), (100, 500), (1500, 400)]
    for sx, sy in bright_stars:
        draw.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(255, 245, 220))
        for arm in range(4):
            rad = math.radians(arm * 45)
            dx = 8 * math.cos(rad)
            dy = 8 * math.sin(rad)
            draw.line([(sx - dx, sy - dy), (sx + dx, sy + dy)], fill=(255, 245, 220, 120), width=1)

    # Comet with tail
    comet_x, comet_y = 1100, 350
    draw.ellipse([comet_x - 6, comet_y - 6, comet_x + 6, comet_y + 6], fill=(255, 240, 200))
    # Tail
    tail_points = []
    for t in range(60):
        tx = comet_x - t * 18 + random.randint(-4, 4)
        ty = comet_y - t * 5 + random.randint(-8, 8)
        tw = max(1, 20 - t // 3)
        alpha = max(10, 180 - t * 3)
        draw.ellipse([tx - tw, ty - tw // 2, tx + tw, ty + tw // 2], fill=(255, 235, 180, alpha))
    draw.ellipse([comet_x - 8, comet_y - 8, comet_x + 8, comet_y + 8], fill=(255, 250, 230))

    # Additional constellation lines
    const_stars = [(300, 400), (450, 350), (550, 420), (480, 500), (350, 480)]
    for i in range(len(const_stars) - 1):
        draw.line([const_stars[i], const_stars[i + 1]], fill=(120, 130, 160, 100), width=1)
    for sx, sy in const_stars:
        draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(200, 210, 240))

    # Dark bottom panel for title
    draw.rectangle([(0, 1880), (WIDTH, 2240)], fill=dark_panel)
    # Gold accent line above panel
    draw.rectangle([(200, 1876), (WIDTH - 200, 1880)], fill=star_gold)

    # Title text
    title_font_path = FONT_DIR / "arialbd.ttf"
    try:
        title_font = ImageFont.truetype(str(title_font_path), 84)
    except (IOError, OSError):
        title_font = ImageFont.load_default()

    author_font_path = FONT_DIR / "ariali.ttf"
    try:
        author_font = ImageFont.truetype(str(author_font_path), 44)
    except (IOError, OSError):
        author_font = ImageFont.load_default()

    # Draw title centered in panel
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_w = title_bbox[2] - title_bbox[0]
    title_x = (WIDTH - title_w) // 2
    draw.text((title_x, 1920), title, fill=(255, 255, 255), font=title_font)

    # Author below title
    author_bbox = draw.textbbox((0, 0), author, font=author_font)
    author_w = author_bbox[2] - author_bbox[0]
    author_x = (WIDTH - author_w) // 2
    draw.text((author_x, 2040), author, fill=(212, 175, 55), font=author_font)

    # Gold accent line below author area
    draw.rectangle([(400, 2160), (WIDTH - 400, 2164)], fill=star_gold)

    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")



def main() -> None:
    parser = argparse.ArgumentParser(description="Generate book cover")
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    create_cover(args.metadata, args.out)


if __name__ == "__main__":
    main()