#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Alchemist's Wife (Tudor Historical)."""

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
    """Deep warm gradient: rust/crimson to near-black for Tudor atmosphere."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((80, 25, 15), ((40, 12, 8)), t)
        elif y < height * 0.75:
            t = (y - height * 0.4) / (height * 0.35)
            c = lerp_color((40, 12, 8), ((20, 8, 6)), t)
        else:
            t = (y - height * 0.75) / (height * 0.25)
            c = lerp_color((20, 8, 6), ((10, 4, 3)), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_candlelight(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a warm candlelight glow in the upper-center area."""
    cx, cy = width // 2, int(height * 0.20)
    for r in range(200, 40, -5):
        alpha = max(0, 30 - (200 - r) // 7)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 200, 100, alpha))
    # Candle
    draw.rectangle([cx - 6, cy + 10, cx + 6, cy + 80], fill=(220, 200, 160))
    # Flame
    draw.ellipse([cx - 10, cy - 20, cx + 10, cy + 10], fill=(255, 220, 80))
    draw.ellipse([cx - 6, cy - 15, cx + 6, cy + 5], fill=(255, 255, 200))


def draw_alembic(draw: ImageDraw, width: int, height: int) -> None:
    """Draw an alchemical alembic (distillation apparatus) silhouette."""
    cx, cy = width // 2, int(height * 0.45)
    # Flask body
    draw.ellipse([cx - 80, cy - 40, cx + 80, cy + 80], fill=(180, 140, 60, 160))
    # Flask neck
    draw.polygon([(cx - 20, cy - 40), (cx + 20, cy - 40), (cx + 15, cy - 120), (cx - 15, cy - 120)], fill=(180, 140, 60, 160))
    # Liquid in flask
    draw.ellipse([cx - 65, cy + 10, cx + 65, cy + 70], fill=(60, 30, 15, 180))
    # Bubbles
    draw.ellipse([cx - 30, cy + 25, cx - 20, cy + 35], fill=(200, 180, 100, 100))
    draw.ellipse([cx + 20, cy + 30, cx + 30, cy + 40], fill=(200, 180, 100, 80))
    draw.ellipse([cx - 10, cy + 40, cx, cy + 50], fill=(200, 180, 100, 60))
    # Glow around alembic
    for r in range(120, 30, -15):
        draw.ellipse([cx - r, cy - r + 40, cx + r, cy + r + 40], outline=(255, 200, 80, 15), width=2)
    # Distillation tube
    draw.line([(cx + 15, cy - 100), (cx + 80, cy - 140), (cx + 120, cy - 130)], fill=(180, 140, 60, 160), width=6)
    # Receiving flask
    draw.ellipse([cx + 90, cy - 155, cx + 150, cy - 95], fill=(140, 100, 40, 140))


def draw_alchemical_symbols(draw: ImageDraw, width: int, height: int) -> None:
    """Draw alchemical symbols and sigils scattered across the cover."""
    symbols = [
        # Mercury symbol
        lambda d, x, y: d.text((x, y), "☿", fill=(200, 170, 80, 60), font=ImageFont.load_default()),
        # Salt symbol - circle with line
        lambda d, x, y: d.arc([x, y, x + 30, y + 30], 0, 360, fill=(180, 140, 60, 40), width=2),
        # Sulfur symbol
        lambda d, x, y: d.text((x, y), "△", fill=(200, 160, 40, 50), font=ImageFont.load_default()),
    ]

    positions = [
        (80, int(height * 0.30)),
        (width - 130, int(height * 0.35)),
        (120, int(height * 0.55)),
        (width - 100, int(height * 0.50)),
        (150, int(height * 0.70)),
        (width - 120, int(height * 0.65)),
    ]

    for pos, sym in zip(positions, symbols * 2):
        sym(draw, *pos)


def draw_tudor_skyline(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a silhouette of Tudor London at the horizon line."""
    y_base = int(height * 0.78)

    # Rolling hills/gallows field
    for x in range(0, width, 3):
        hill = int(10 * math.sin(x / 80) + 5 * math.sin(x / 30))
        draw.line([(x, y_base + hill), (x, y_base + 30)], fill=(15, 6, 4, 200), width=2)

    # Church spires
    spires = [
        (width // 2 - 200, y_base, 40, 140),
        (width // 2 + 150, y_base, 30, 110),
        (width // 2 - 80, y_base, 25, 90),
        (width // 2 + 300, y_base, 35, 120),
    ]
    for sx, sy, sw, sh in spires:
        # Spire body
        draw.rectangle([sx - sw // 2, sy - sh, sx + sw // 2, sy], fill=(10, 4, 3, 220))
        # Spire roof
        draw.polygon([(sx - sw // 2, sy - sh), (sx, sy - sh - 40), (sx + sw // 2, sy - sh)], fill=(10, 4, 3, 220))
        # Cross at top
        draw.line([(sx, sy - sh - 55), (sx, sy - sh - 35)], fill=(160, 140, 80, 120), width=3)
        draw.line([(sx - 8, sy - sh - 48), (sx + 8, sy - sh - 48)], fill=(160, 140, 80, 120), width=3)

    # Roof lines of buildings
    for bx in range(50, width - 50, 35):
        bh = 30 + int(20 * math.sin(bx / 20))
        draw.rectangle([bx, y_base - bh, bx + 28, y_base], fill=(8, 3, 2, 220))
        # Roof peak
        draw.polygon([(bx - 3, y_base - bh), (bx + 14, y_base - bh - 15), (bx + 31, y_base - bh)], fill=(8, 3, 2, 220))
        # Windows (warm light)
        if hash(bx) % 3 == 0:
            draw.rectangle([bx + 6, y_base - bh + 8, bx + 12, y_base - bh + 18], fill=(200, 160, 60, 70))
            draw.rectangle([bx + 16, y_base - bh + 8, bx + 22, y_base - bh + 18], fill=(200, 160, 60, 70))


def draw_gold_particles(draw: ImageDraw, width: int, height: int) -> None:
    """Draw floating gold particles and specks suggesting alchemical transformation."""
    import random

    rng = random.Random(13)
    for _ in range(60):
        x = rng.randint(100, width - 100)
        y = rng.randint(int(height * 0.15), int(height * 0.75))
        size = rng.randint(2, 6)
        alpha = rng.randint(60, 180)
        color = (220, 180, 60, alpha)
        draw.ellipse([x - size, y - size, x + size, y + size], fill=color)
        if size > 3:
            # Outer glow
            glow_color = (220, 180, 60, alpha // 3)
            draw.ellipse([x - size * 2, y - size * 2, x + size * 2, y + size * 2], fill=glow_color)


def draw_title_panel(draw: ImageDraw, draw_img: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom of the cover with white text."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    draw.rectangle([(0, panel_top), (width, height)], fill=(8, 4, 3, 220))

    # Gold border at top of panel
    draw.line([(60, panel_top), (width - 60, panel_top)], fill=(180, 140, 60), width=3)
    draw.line([(60, panel_top + 4), (width - 60, panel_top + 4)], fill=(120, 90, 40), width=1)

    # Title text
    title = "The Alchemist's\nWife"
    title_font_size = 78
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered in white
    lines = title.split("\n")
    y_offset = panel_top + 90
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 0
        tx = (width - tw) // 2
        draw.text((tx, y_offset), line, fill=(255, 255, 255), font=title_font)
        y_offset += 95

    # Decorative divider below title
    divider_y = y_offset + 15
    draw.line([(width // 2 - 80, divider_y), (width // 2 + 80, divider_y)], fill=(180, 140, 60), width=2)
    draw.ellipse([width // 2 - 5, divider_y - 5, width // 2 + 5, divider_y + 5], fill=(180, 140, 60))

    # Author name
    author = "Barış Kısır"
    author_font_size = 38
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
    ay = divider_y + 45
    draw.text((ax, ay), author, fill=(220, 200, 170), font=author_font)

    # Genre line at very bottom
    genre_font_size = 22
    try:
        genre_font = ImageFont.truetype(str(font_paths["small"]), genre_font_size)
    except Exception:
        genre_font = ImageFont.load_default()
    genre = "A TUDOR HISTORICAL NOVEL"
    try:
        gbbox = draw.textbbox((0, 0), genre, font=genre_font)
        gw = gbbox[2] - gbbox[0]
    except Exception:
        gw = 0
    gx = (width - gw) // 2
    draw.text((gx, height - 50), genre, fill=(160, 140, 100), font=genre_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Warm gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Candlelight glow
    draw_candlelight(draw, WIDTH, HEIGHT)

    # Step 3: Alembic and alchemical apparatus
    draw_alembic(draw, WIDTH, HEIGHT)

    # Step 4: Alchemical symbols
    draw_alchemical_symbols(draw, WIDTH, HEIGHT)

    # Step 5: Tudor skyline silhouette
    draw_tudor_skyline(draw, WIDTH, HEIGHT)

    # Step 6: Gold particles
    draw_gold_particles(draw, WIDTH, HEIGHT)

    # Step 7: Title panel at bottom
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
        "small": str(FONTS_DIR / "arial.ttf"),
    }
    draw_title_panel(draw, draw, WIDTH, HEIGHT, font_paths)

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