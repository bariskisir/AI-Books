#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Book of Dirt."""

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
    """Terracotta-to-ochre gradient for the Australian outback feel."""
    for y in range(height):
        if y < height * 0.6:
            t = y / (height * 0.6)
            c = lerp_color((180, 90, 50), (200, 120, 60), t)
        else:
            t = (y - height * 0.6) / (height * 0.4)
            c = lerp_color((200, 120, 60), (140, 70, 35), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_cracked_earth(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a network of cracks across the foreground, like dry mud."""
    rng = random.Random(42)
    base_y_start = int(height * 0.45)

    # Main crack network
    for _ in range(60):
        start_x = rng.randint(50, width - 50)
        start_y = rng.randint(base_y_start, height - 100)
        length = rng.randint(40, 250)
        angle = rng.uniform(0, 2 * math.pi)
        end_x = start_x + int(length * math.cos(angle))
        end_y = start_y + int(length * math.sin(angle))

        # Crack color: darker than background
        crack_color = (90, 45, 20)
        crack_width = rng.randint(1, 4)

        # Draw crack with slight curve
        points = []
        steps = 10
        for s in range(steps + 1):
            t = s / steps
            x = start_x + (end_x - start_x) * t + rng.randint(-5, 5)
            y = start_y + (end_y - start_y) * t + rng.randint(-3, 3)
            points.append((x, y))

        draw.line(points, fill=crack_color, width=crack_width)

    # Add some broader polygon cracks (larger plates)
    for _ in range(15):
        cx = rng.randint(100, width - 100)
        cy = rng.randint(base_y_start + 50, height - 150)
        sides = rng.randint(4, 7)
        radius = rng.randint(30, 80)
        polygon = []
        for s in range(sides):
            a = 2 * math.pi * s / sides + rng.uniform(-0.2, 0.2)
            r = radius * rng.uniform(0.7, 1.3)
            polygon.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        draw.polygon(polygon, outline=(100, 50, 25), width=2)


def draw_lone_tree(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a solitary, drought-stricken tree on the horizon."""
    tx, ty = width // 2, int(height * 0.42)

    # Trunk - dark, twisted
    trunk_color = (50, 30, 15)
    draw.line([(tx, ty), (tx, ty + 180)], fill=trunk_color, width=14)

    # Branches - skeletal, reaching
    branches = [
        (0, -1.2, 100, 0.5),
        (0.3, -1.0, 70, 0.4),
        (-0.3, -0.9, 80, 0.4),
        (0.5, -0.7, 50, 0.3),
        (-0.5, -0.6, 60, 0.3),
        (0.15, -1.1, 90, 0.35),
        (-0.15, -1.0, 85, 0.35),
    ]

    for x_dir, y_dir, length, thickness in branches:
        bx = tx + int(x_dir * length)
        by = int(ty + y_dir * length)
        draw.line([(tx, ty - 20), (bx, by)], fill=trunk_color, width=int(12 * thickness))

        # Smaller sub-branches
        if length > 50:
            for sub in range(2):
                sub_x = bx + int(x_dir * length * 0.3 * (1 if sub == 0 else -1))
                sub_y = by - int(length * 0.25)
                draw.line([(bx, by), (sub_x, sub_y)], fill=trunk_color, width=int(6 * thickness))

    # No leaves - dead tree


def draw_sun(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a harsh sun bleaching the sky."""
    cx, cy = width // 2, int(height * 0.12)
    radius = 80

    # Sun glow
    for i in range(10):
        r = radius + i * 20
        alpha = max(0, 60 - i * 6)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 200, 120, alpha))

    # Sun disc
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(255, 220, 140))

    # Bright center
    draw.ellipse([cx - radius // 2, cy - radius // 2, cx + radius // 2, cy + radius // 2], fill=(255, 240, 200))


def draw_hills(draw: ImageDraw, width: int, height: int) -> None:
    """Draw distant red hills on the horizon."""
    horizon_y = int(height * 0.38)

    for i in range(3):
        shade = (170, 85, 45 - i * 10)
        hill_y = horizon_y - 30 + i * 15
        points = [(0, hill_y + 60)]
        for x in range(0, width + 10, 20):
            h = math.sin(x * 0.003 + i * 1.5) * 40 + math.sin(x * 0.007 + i * 2.0) * 20
            points.append((x, hill_y + h))
        points.append((width, hill_y + 60))
        points.append((0, hill_y + 60))
        draw.polygon(points, fill=shade)


def draw_dust_motes(draw: ImageDraw, width: int, height: int) -> None:
    """Draw tiny dust particles floating in the air."""
    rng = random.Random(17)
    for _ in range(80):
        x = rng.randint(0, width)
        y = rng.randint(0, height)
        size = rng.randint(1, 3)
        alpha = rng.randint(30, 100)
        draw.ellipse([x, y, x + size, y + size], fill=(220, 180, 140, alpha))


def draw_title_panel(draw: ImageDraw, draw_img: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom with WHITE text."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark, semi-transparent
    for y in range(panel_top, height):
        t = (y - panel_top) / (height - panel_top)
        c = lerp_color((30, 18, 8), ((15, 8, 4)), t)
        draw.line([(0, y), (width, y)], fill=c)

    # Add a thin ochre line at top of panel
    draw.line([(0, panel_top), (width, panel_top)], fill=(200, 120, 60), width=3)

    # Title text
    title = "The Book of\nDirt"
    title_font_size = 80
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered, white text
    lines = title.split("\n")
    y_offset = panel_top + 80
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 0
        tx = (width - tw) // 2
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
    ay = y_offset + 40
    draw.text((ax, ay), author, fill=(220, 180, 140), font=author_font)


def draw_low_scrub(draw: ImageDraw, width: int, height: int) -> None:
    """Draw sparse dry scrub bushes at ground level."""
    rng = random.Random(33)
    horizon_y = int(height * 0.38)

    for _ in range(40):
        bx = rng.randint(20, width - 20)
        by = rng.randint(horizon_y + 30, height - 300)
        bush_size = rng.randint(8, 20)

        # Bush color - dry brown-green
        bush_color = (90, 65, 30)
        for s in range(3):
            ox = rng.randint(-bush_size, bush_size)
            oy = rng.randint(-bush_size // 2, bush_size // 2)
            draw.ellipse(
                [bx + ox - bush_size // 2, by + oy - bush_size // 3, bx + ox + bush_size // 2, by + oy + bush_size // 3],
                fill=bush_color,
            )


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Book of Dirt")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Harsh sun
    draw_sun(draw, WIDTH, HEIGHT)

    # Step 3: Distant hills
    draw_hills(draw, WIDTH, HEIGHT)

    # Step 4: Lone dead tree
    draw_lone_tree(draw, WIDTH, HEIGHT)

    # Step 5: Low scrub
    draw_low_scrub(draw, WIDTH, HEIGHT)

    # Step 6: Dust motes
    draw_dust_motes(draw, WIDTH, HEIGHT)

    # Step 7: Cracked earth
    draw_cracked_earth(draw, WIDTH, HEIGHT)

    # Step 8: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
    }
    draw_title_panel(draw, draw, WIDTH, HEIGHT, font_paths)

    # Soften image slightly
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