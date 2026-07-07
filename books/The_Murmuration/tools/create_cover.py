#!/usr/bin/env python3
"""Cover: The Murmuration — starling murmuration forming spiral at dusk over Somerset reeds, lone figure."""

from __future__ import annotations

import argparse
import json
import math
import random
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
    """Twilight sky: deep violet at top, amber on horizon, dark at bottom."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((15, 5, 30), ((80, 20, 60)), t)
        elif y < height * 0.55:
            t = (y - height * 0.4) / (height * 0.15)
            c = lerp_color((80, 20, 60), ((200, 90, 40)), t)
        elif y < height * 0.6:
            t = (y - height * 0.55) / (height * 0.05)
            c = lerp_color((200, 90, 40), ((240, 160, 60)), t)
        else:
            t = (y - height * 0.6) / (height * 0.4)
            c = lerp_color((240, 160, 60), ((10, 8, 15)), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_starling_birds(draw: ImageDraw, width: int, height: int) -> None:
    """Draw hundreds of small bird shapes in murmuration patterns across the sky."""
    rng = random.Random(13)

    # Generate murmuration particles
    for _ in range(1200):
        x = rng.randint(100, width - 100)
        # Birds cluster between top and mid-section, thinning out
        if rng.random() < 0.7:
            y = rng.randint(50, int(height * 0.5))
        else:
            y = rng.randint(int(height * 0.5), int(height * 0.7))

        size = rng.uniform(1.5, 5.0)
        # Opacity varies
        alpha = rng.randint(60, 220)
        dark = rng.randint(10, 50)

        # Each starling is a tiny V or short line
        angle = rng.uniform(-0.3, 0.3)
        dx = int(math.cos(angle) * size * 3)
        dy = int(math.sin(angle) * size * 2)

        draw.line(
            [x - dx, y - dy, x + dx, y + dy],
            fill=(dark, dark, dark, alpha),
            width=max(1, int(size * 0.8)),
        )

        # Some with slight wing indication
        if size > 3 and rng.random() < 0.3:
            wx = int(dx * 0.6)
            wy = int(dy * 0.6 + 2)
            draw.line(
                [x - wx, y - wy, x + wx, y - wy],
                fill=(dark, dark, dark, alpha),
                width=1,
            )


def draw_murmuration_swirl(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a dense swirl of birds forming a murmuration wave."""
    rng = random.Random(7)

    cx, cy = width // 2, int(height * 0.3)
    for i in range(800):
        angle = rng.uniform(0, math.pi * 2)
        dist = rng.uniform(20, 350)
        spiral_factor = dist / 350
        x = cx + int(math.cos(angle + spiral_factor * 2) * dist)
        y = cy + int(math.sin(angle + spiral_factor * 3) * dist * 0.6) - int(spiral_factor * 80)

        if x < 0 or x >= width or y < 0 or y >= height:
            continue

        alpha = rng.randint(80, 200)
        s = rng.uniform(2, 4)
        draw.line(
            [x - int(s), y - int(s * 0.5), x + int(s), y + int(s * 0.5)],
            fill=(20, 15, 25, alpha),
            width=max(1, int(s * 0.6)),
        )


def draw_lone_figure(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a small lone figure standing on the observation platform."""
    fx = width // 2 + 60
    fy = int(height * 0.72)

    # Figure - small silhouette
    # Head
    draw.ellipse([fx - 6, fy - 18, fx + 6, fy - 8], fill=(5, 3, 10))
    # Body
    draw.rectangle([fx - 5, fy - 8, fx + 5, fy + 12], fill=(5, 3, 10))
    # Legs
    draw.line([fx - 3, fy + 12, fx - 4, fy + 24], fill=(5, 3, 10), width=3)
    draw.line([fx + 3, fy + 12, fx + 4, fy + 24], fill=(5, 3, 10), width=3)

    # Camera tripod beside figure
    draw.line([fx + 25, fy, fx + 25, fy + 28], fill=(5, 3, 10), width=2)
    draw.line([fx + 25, fy + 28, fx + 20, fy + 35], fill=(5, 3, 10), width=2)
    draw.line([fx + 25, fy + 28, fx + 30, fy + 35], fill=(5, 3, 10), width=2)
    # Camera body
    draw.rectangle([fx + 21, fy - 3, fx + 29, fy + 3], fill=(5, 3, 10))
    # Lens
    draw.rectangle([fx + 29, fy - 2, fx + 38, fy + 2], fill=(5, 3, 10))


def draw_reed_bed(draw: ImageDraw, width: int, height: int) -> None:
    """Draw dark reed silhouettes along the bottom of the sky area."""
    rng = random.Random(5)
    for x in range(0, width, 6):
        h = rng.randint(30, 90)
        base_y = int(height * 0.72)
        draw.line(
            [x, base_y - h, x, base_y],
            fill=(8, 6, 12),
            width=1,
        )
        # Slight bend
        if rng.random() < 0.3:
            draw.line(
                [x, base_y - h, x + 2, base_y - h - 5],
                fill=(8, 6, 12),
                width=1,
            )


def draw_amber_glow(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a glowing amber patch near the horizon where sun sets."""
    cx, cy = width // 2, int(height * 0.55)
    for r in range(60, 200, 5):
        alpha = max(0, 60 - r // 4)
        draw.ellipse(
            [cx - r, cy - r // 2, cx + r, cy + r // 2],
            fill=(240, 160, 60, alpha),
        )


def draw_title_panel(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a dark rectangular title panel at the bottom of the cover."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark semi-transparent
    draw.rectangle([(0, panel_top), (width, height)], fill=(10, 8, 15, 220))

    # Subtle top border line
    draw.line([(0, panel_top), (width, panel_top)], fill=(200, 100, 50), width=2)

    # Title text using arialbd.ttf
    title = "The Murmuration"
    title_font_size = 84
    try:
        title_font = ImageFont.truetype(str(FONTS_DIR / "arialbd.ttf"), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    try:
        bbox = draw.textbbox((0, 0), title, font=title_font)
        tw = bbox[2] - bbox[0]
    except Exception:
        tw = 0
    tx = (width - tw) // 2
    ty = panel_top + 80
    draw.text((tx, ty), title, fill=(255, 255, 255), font=title_font)

    # Author name
    author = "Barış Kısır"
    author_font_size = 36
    try:
        author_font = ImageFont.truetype(str(FONTS_DIR / "arialbd.ttf"), author_font_size)
    except Exception:
        author_font = ImageFont.load_default()

    try:
        abbox = draw.textbbox((0, 0), author, font=author_font)
        aw = abbox[2] - abbox[0]
    except Exception:
        aw = 0
    ax = (width - aw) // 2
    ay = ty + 110
    draw.text((ax, ay), author, fill=(200, 180, 160), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Murmuration")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Twilight sky gradient
    draw_gradient(draw, WIDTH, HEIGHT)
    # Amber glow near horizon
    draw_amber_glow(draw, WIDTH, HEIGHT)
    # Murmuration spiral in sky
    draw_murmuration_swirl(draw, WIDTH, HEIGHT)
    # Starling birds scattered
    draw_starling_birds(draw, WIDTH, HEIGHT)
    # Reed bed silhouettes
    draw_reed_bed(draw, WIDTH, HEIGHT)
    # Lone figure on observation platform
    draw_lone_figure(draw, WIDTH, HEIGHT)

    # Soften
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