#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Salt Wife."""

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
    """Cold sea-grey to dark heather-purple to near-black gradient for folk horror feel."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((50, 55, 60), (35, 30, 45), t)
        elif y < height * 0.75:
            t = (y - height * 0.4) / (height * 0.35)
            c = lerp_color((35, 30, 45), (20, 15, 30), t)
        else:
            t = (y - height * 0.75) / (height * 0.25)
            c = lerp_color((20, 15, 30), (5, 5, 10), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_sea(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a dark sea with white-capped waves at the horizon."""
    sea_y = int(height * 0.35)
    # Sea band
    for y in range(sea_y, int(height * 0.48)):
        t = (y - sea_y) / (height * 0.13)
        c = lerp_color((25, 30, 40), (40, 45, 55), t)
        draw.line([(0, y), (width, y)], fill=c)

    # Wave crests
    import random

    rng = random.Random(13)
    for _ in range(60):
        wx = rng.randint(0, width)
        wy = rng.randint(sea_y, int(height * 0.46))
        wlen = rng.randint(20, 80)
        for dx in range(wlen):
            alpha = int(120 * (1 - abs(dx - wlen / 2) / (wlen / 2)))
            h = int(3 * math.sin(dx * 0.3))
            draw.point((wx + dx, wy + h), fill=(180, 190, 200, alpha))


def draw_island(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a dark island silhouette on the horizon."""
    isle_y = int(height * 0.30)
    isle_cx = width // 2

    # Main island shape - rocky silhouette
    points = []
    import random

    rng = random.Random(17)
    for x in range(isle_cx - 300, isle_cx + 350, 5):
        rel_x = (x - (isle_cx - 300)) / 600
        base_h = 80 + 60 * math.sin(rel_x * math.pi)
        noise = rng.randint(-15, 10)
        h = base_h + noise
        points.append((x, isle_y - h))

    points.append((isle_cx + 350, isle_y))
    points.append((isle_cx - 300, isle_y))
    draw.polygon(points, fill=(15, 12, 20))

    # Hills behind
    hill_points = []
    rng = random.Random(19)
    for x in range(isle_cx - 250, isle_cx + 280, 3):
        rel_x = (x - (isle_cx - 250)) / 530
        base_h = 120 + 80 * math.sin(rel_x * math.pi)
        noise = rng.randint(-20, 15)
        h = base_h + noise
        hill_points.append((x, isle_y - h))

    hill_points.append((isle_cx + 280, isle_y))
    hill_points.append((isle_cx - 250, isle_y))
    draw.polygon(hill_points, fill=(20, 17, 28))


def draw_standing_stones(draw: ImageDraw, width: int, height: int) -> None:
    """Draw standing stones on the island silhouette."""
    stone_data = [
        (width // 2 - 180, 0.28, 1.0),
        (width // 2 - 120, 0.275, 0.8),
        (width // 2 - 50, 0.27, 1.2),
        (width // 2 + 30, 0.272, 0.9),
        (width // 2 + 100, 0.278, 1.1),
        (width // 2 + 160, 0.285, 0.7),
    ]
    for sx, base_ratio, scale in stone_data:
        base_y = int(height * base_ratio)
        stone_w = int(14 * scale)
        stone_h = int(60 * scale)
        # Draw stone
        stone_color = (25, 22, 32)
        draw.rectangle(
            [sx - stone_w // 2, base_y - stone_h, sx + stone_w // 2, base_y],
            fill=stone_color,
        )
        # Rough edges
        draw.line(
            [sx - stone_w // 2, base_y - stone_h, sx + stone_w // 2 - 2, base_y - stone_h + 5],
            fill=(30, 27, 38),
            width=2,
        )


def draw_salt_shore(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a salt-crusted shore at the bottom of the foreground."""
    shore_y = int(height * 0.85)

    # Beach band
    for y in range(shore_y, height):
        t = (y - shore_y) / (height - shore_y)
        c = lerp_color((30, 28, 25), (20, 18, 15), t)
        draw.line([(0, y), (width, y)], fill=c)

    # Salt crust - white crystalline patches
    import random

    rng = random.Random(23)
    for _ in range(200):
        sx = rng.randint(50, width - 50)
        sy = rng.randint(shore_y + 20, height - 30)
        size = rng.randint(2, 8)
        alpha = rng.randint(80, 180)
        draw.ellipse([sx - size, sy - size, sx + size, sy + size], fill=(220, 225, 230, alpha))

    # Salt crust lines
    for _ in range(30):
        sx = rng.randint(0, width)
        sy = rng.randint(shore_y + 10, height - 10)
        sw = rng.randint(30, 120)
        for dx in range(sw):
            draw.point((sx + dx, sy + int(2 * math.sin(dx * 0.2))), fill=(200, 210, 215, 100))


def draw_heather(draw: ImageDraw, width: int, height: int) -> None:
    """Draw heather patches on the lower slopes."""
    import random

    rng = random.Random(31)
    for _ in range(80):
        hx = rng.randint(100, width - 100)
        hy = rng.randint(int(height * 0.4), int(height * 0.7))
        # Heather patch - small purple dots
        for _ in range(rng.randint(5, 15)):
            ox = rng.randint(-8, 8)
            oy = rng.randint(-4, 4)
            shade = rng.randint(60, 120)
            draw.point((hx + ox, hy + oy), fill=(shade, shade - 30, shade + 10, 180))

    # Scattered individual heather blooms
    for _ in range(120):
        hx = rng.randint(50, width - 50)
        hy = rng.randint(int(height * 0.45), int(height * 0.55))
        draw.point((hx, hy), fill=(100, 60, 130, 200))
        if rng.random() < 0.3:
            draw.point((hx + 1, hy), fill=(80, 40, 110, 150))


def draw_sea_foam(draw: ImageDraw, width: int, height: int) -> None:
    """Draw sea foam and spray at the water's edge."""
    import random

    rng = random.Random(37)
    foam_y = int(height * 0.47)
    for _ in range(150):
        fx = rng.randint(0, width)
        fy = foam_y + rng.randint(-5, 15)
        alpha = rng.randint(30, 100)
        size = rng.randint(1, 4)
        draw.ellipse([fx - size, fy - size, fx + size, fy + size], fill=(200, 210, 220, alpha))


def draw_standing_stones_foreground(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a large standing stone in the foreground for scale and mood."""
    # Large standing stone on the left
    import random

    rng = random.Random(41)
    stone_x = width // 2 + 200
    stone_base = int(height * 0.78)
    stone_top = int(height * 0.30)
    stone_w = 40

    # Main stone body
    draw.polygon(
        [
            (stone_x - stone_w // 2, stone_base),
            (stone_x - stone_w // 3, stone_top + 20),
            (stone_x + stone_w // 4, stone_top),
            (stone_x + stone_w // 2, stone_base - 20),
        ],
        fill=(22, 19, 30),
    )
    # Highlight edge
    draw.line(
        [
            (stone_x - stone_w // 3, stone_top + 20),
            (stone_x + stone_w // 4, stone_top),
        ],
        fill=(40, 35, 50),
        width=2,
    )

    # Smaller stone right
    stone2_x = width // 2 + 400
    stone2_base = int(height * 0.80)
    stone2_top = int(height * 0.45)
    draw.polygon(
        [
            (stone2_x - 15, stone2_base),
            (stone2_x - 10, stone2_top + 10),
            (stone2_x + 10, stone2_top),
            (stone2_x + 15, stone2_base - 10),
        ],
        fill=(25, 22, 33),
    )


def draw_title_panel(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a dark title panel at the bottom with white text for readability."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    draw.rectangle([(0, panel_top), (width, height)], fill=(10, 8, 15, 230))

    # Subtle salt-crust line at panel top
    for x in range(0, width, 3):
        y_offset = int(2 * math.sin(x * 0.05))
        draw.point((x, panel_top + y_offset), fill=(180, 185, 190, 60))

    # Thin border line
    draw.line([(0, panel_top), (width, panel_top)], fill=(60, 55, 70), width=2)

    # Title text - use arialbd.ttf
    title = "The Salt Wife"
    title_font_size = 80
    try:
        title_font = ImageFont.truetype(str(FONTS_DIR / "arialbd.ttf"), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered
    try:
        bbox = draw.textbbox((0, 0), title, font=title_font)
        tw = bbox[2] - bbox[0]
    except Exception:
        tw = 0
    tx = (width - tw) // 2
    ty = panel_top + 100
    # Shadow for readability
    draw.text((tx + 2, ty + 2), title, fill=(0, 0, 0), font=title_font)
    draw.text((tx, ty), title, fill=(230, 230, 235), font=title_font)

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
    ay = ty + 120
    draw.text((ax + 1, ay + 1), author, fill=(0, 0, 0), font=author_font)
    draw.text((ax, ay), author, fill=(180, 185, 195), font=author_font)

    # Small decorative salt line below author
    line_y = ay + 50
    for x in range(width // 2 - 60, width // 2 + 60):
        y_off = int(2 * math.sin(x * 0.1))
        draw.point((x, line_y + y_off), fill=(150, 155, 165, 120))


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Salt Wife")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background (cold sea-grey to dark heather)
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Dark sea with waves
    draw_sea(draw, WIDTH, HEIGHT)

    # Step 3: Island silhouette
    draw_island(draw, WIDTH, HEIGHT)

    # Step 4: Standing stones on the island
    draw_standing_stones(draw, WIDTH, HEIGHT)

    # Step 5: Heather patches
    draw_heather(draw, WIDTH, HEIGHT)

    # Step 6: Sea foam
    draw_sea_foam(draw, WIDTH, HEIGHT)

    # Step 7: Salt-crusted shore
    draw_salt_shore(draw, WIDTH, HEIGHT)

    # Step 8: Foreground standing stones
    draw_standing_stones_foreground(draw, WIDTH, HEIGHT)

    # Step 9: Title panel
    draw_title_panel(draw, WIDTH, HEIGHT)

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