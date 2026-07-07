#!/usr/bin/env python3
"""Cover: The Ocean Waits — dark house on pilings over black water, one warm window, faint moon through clouds, twisted trees."""

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
    """Teal-black gradient for the coastal horror atmosphere."""
    for y in range(height):
        if y < height * 0.3:
            # Sky: dark grey to deep teal
            t = y / (height * 0.3)
            c = lerp_color((30, 35, 40), (10, 50, 55), t)
        elif y < height * 0.45:
            # Horizon: teal darkens
            t = (y - height * 0.3) / (height * 0.15)
            c = lerp_color((10, 50, 55), (5, 30, 40), t)
        else:
            # Water: dark teal to near black
            t = (y - height * 0.45) / (height * 0.55)
            c = lerp_color((5, 30, 40), (2, 8, 12), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_water_surface(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the water surface with subtle wave lines."""
    water_start = int(height * 0.45)
    rng = random.Random(17)

    for y in range(water_start, int(height * 0.65), 4):
        wave_offset = math.sin(y * 0.02) * 20 + rng.uniform(-5, 5)
        alpha = max(5, 30 - int((y - water_start) * 0.08))
        color = (15, 60, 70, alpha)
        for x in range(0, width, 3):
            px = x + int(math.sin(x * 0.01 + y * 0.03) * 15 + wave_offset)
            if 0 <= px < width:
                draw.point((px, y), fill=color)


def draw_moon_glow(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a faint moon behind the clouds, just visible."""
    mx, my = width // 2 + 150, int(height * 0.15)

    # Outer glow layers
    for r in range(60, 10, -5):
        alpha = max(2, 30 - r // 2)
        draw.ellipse([mx - r, my - r, mx + r, my + r], fill=(180, 200, 210, alpha))

    # Moon disc
    draw.ellipse([mx - 25, my - 25, mx + 25, my + 25], fill=(200, 215, 225, 80))

    # Cloud wisps across moon
    rng = random.Random(23)
    for _ in range(6):
        cx = mx + rng.randint(-80, 80)
        cy = my + rng.randint(-40, 40)
        cw = rng.randint(60, 150)
        ch = rng.randint(8, 20)
        draw.ellipse([cx - cw // 2, cy - ch // 2, cx + cw // 2, cy + ch // 2], fill=(25, 30, 35, 120))


def draw_coastal_house(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a coastal house on pilings above dark water."""
    cx, cy = width // 2, int(height * 0.52)

    # Pilings
    piling_colors = [(20, 15, 12), (25, 18, 14), (18, 13, 10)]
    for px in [cx - 90, cx - 50, cx, cx + 50, cx + 90]:
        for py_off in [0, 1]:
            p_h = 60 + py_off * 20
            draw.rectangle([px - 4, cy + 20, px + 4, cy + 20 + p_h], fill=piling_colors[py_off])

    # Water ripples around pilings
    for px in [cx - 90, cx - 50, cx, cx + 50, cx + 90]:
        for r in range(2, 12, 3):
            draw.ellipse(
                [px - r, cy + 20 + 55 + r // 2, px + r, cy + 20 + 55 + r // 2 + r],
                outline=(10, 40, 50, 40),
                width=1,
            )

    # House body
    house_w, house_h = 220, 140
    draw.rectangle(
        [cx - house_w // 2, cy - house_h, cx + house_w // 2, cy + 20],
        fill=(25, 20, 18),
    )

    # Roof
    draw.polygon(
        [(cx - house_w // 2 - 15, cy - house_h), (cx, cy - house_h - 70), (cx + house_w // 2 + 15, cy - house_h)],
        fill=(20, 18, 15),
    )

    # Roof ridge line
    draw.line(
        [(cx - 5, cy - house_h - 70), (cx + 5, cy - house_h - 70)],
        fill=(35, 28, 22),
        width=3,
    )

    # Porch
    porch_w = 260
    draw.rectangle(
        [cx - porch_w // 2, cy + 5, cx + porch_w // 2, cy + 25],
        fill=(30, 25, 20),
    )
    # Porch railing
    for px in range(cx - porch_w // 2 + 10, cx + porch_w // 2, 25):
        draw.rectangle([px, cy - 10, px + 3, cy + 5], fill=(35, 28, 22))

    # Windows (dark, except one lit)
    window_positions = [
        (cx - 70, cy - house_h + 30),  # lit window
        (cx + 20, cy - house_h + 30),
        (cx - 70, cy - house_h + 85),
        (cx + 20, cy - house_h + 85),
    ]

    for i, (wx, wy) in enumerate(window_positions):
        if i == 0:
            # Lit window - warm yellow glow
            draw.rectangle([wx, wy, wx + 40, wy + 35], fill=(255, 200, 80))
            # Window glow spread
            for g in range(3, 20, 4):
                draw.rectangle(
                    [wx - g, wy - g, wx + 40 + g, wy + 35 + g],
                    outline=(255, 200, 80, 30 // (g // 3 + 1)),
                    width=1,
                )
            # Window cross
            draw.line([(wx + 20, wy), (wx + 20, wy + 35)], fill=(40, 30, 20), width=2)
            draw.line([(wx, wy + 17), (wx + 40, wy + 17)], fill=(40, 30, 20), width=2)
        else:
            # Dark windows
            draw.rectangle([wx, wy, wx + 40, wy + 35], fill=(12, 10, 8))

    # Door
    draw.rectangle([cx - 15, cy - house_h + 90, cx + 15, cy + 20], fill=(18, 14, 10))


def draw_water_reflections(draw: ImageDraw, width: int, height: int) -> None:
    """Draw light reflections on the water surface."""
    water_start = int(height * 0.45)
    cx = width // 2

    # Reflection of lit window on water
    rng = random.Random(5)
    for i in range(25):
        rx = cx - 50 + rng.randint(-20, 20)
        ry = water_start + 20 + i * 8 + rng.randint(-3, 3)
        rw = rng.randint(15, 40)
        rh = rng.randint(2, 5)
        alpha = max(5, 60 - i * 2)
        draw.ellipse([rx, ry, rx + rw, ry + rh], fill=(255, 200, 100, alpha))

    # Moon reflection
    mx = cx + 150
    for i in range(10):
        rx = mx + rng.randint(-10, 10)
        ry = water_start + 40 + i * 12
        rw = rng.randint(10, 30)
        rh = 2
        alpha = max(3, 25 - i * 2)
        draw.ellipse([rx, ry, rx + rw, ry + rh], fill=(180, 200, 220, alpha))


def draw_bare_trees(draw: ImageDraw, width: int, height: int) -> None:
    """Draw bare, twisted trees on the shoreline at the edges."""
    rng = random.Random(13)

    # Left side trees
    for base_x, base_y in [(80, int(height * 0.42)), (30, int(height * 0.46)), (140, int(height * 0.44))]:
        trunk_h = rng.randint(80, 140)
        # Trunk
        draw.line([(base_x, base_y), (base_x, base_y - trunk_h)], fill=(15, 10, 8), width=6)
        # Branches
        for _ in range(rng.randint(4, 7)):
            bx = base_x + rng.randint(-40, 40)
            by = base_y - rng.randint(20, trunk_h - 10)
            ex = bx + rng.randint(-50, 50)
            ey = by - rng.randint(20, 50)
            draw.line([(bx, by), (ex, ey)], fill=(15, 10, 8), width=rng.randint(2, 4))
            # Sub-branches
            if rng.random() < 0.6:
                sx = ex + rng.randint(-20, 20)
                sy = ey - rng.randint(10, 25)
                draw.line([(ex, ey), (sx, sy)], fill=(12, 8, 6), width=2)

    # Right side trees
    for base_x, base_y in [(width - 80, int(height * 0.42)), (width - 30, int(height * 0.47)), (width - 140, int(height * 0.44))]:
        trunk_h = rng.randint(70, 130)
        draw.line([(base_x, base_y), (base_x, base_y - trunk_h)], fill=(15, 10, 8), width=6)
        for _ in range(rng.randint(4, 6)):
            bx = base_x + rng.randint(-40, 40)
            by = base_y - rng.randint(20, trunk_h - 10)
            ex = bx + rng.randint(-50, 50)
            ey = by - rng.randint(20, 50)
            draw.line([(bx, by), (ex, ey)], fill=(15, 10, 8), width=rng.randint(2, 4))


def draw_fog(draw: ImageDraw, width: int, height: int) -> None:
    """Draw thin fog/mist near the waterline."""
    rng = random.Random(31)
    fog_y = int(height * 0.42)
    for _ in range(40):
        fx = rng.randint(0, width)
        fy = fog_y + rng.randint(-20, 40)
        fw = rng.randint(60, 180)
        fh = rng.randint(10, 25)
        alpha = rng.randint(8, 25)
        draw.ellipse([fx - fw // 2, fy - fh // 2, fx + fw // 2, fy + fh // 2], fill=(80, 100, 110, alpha))


def draw_title_panel(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a dark title panel at the bottom with white text for readability."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    draw.rectangle([(0, panel_top), (width, height)], fill=(8, 12, 16))

    # Subtle top border line
    draw.line([(0, panel_top), (width, panel_top)], fill=(20, 60, 65), width=2)

    # Title text
    title = "The Ocean Waits"
    title_font_size = 80

    font_path = FONTS_DIR / "arialbd.ttf"
    try:
        title_font = ImageFont.truetype(str(font_path), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Center title
    try:
        bbox = draw.textbbox((0, 0), title, font=title_font)
        tw = bbox[2] - bbox[0]
    except Exception:
        tw = 0
    tx = (width - tw) // 2
    ty = panel_top + 120
    draw.text((tx, ty), title, fill=(240, 240, 245), font=title_font)

    # Subtitle/descriptor line
    subtitle = "A Novel"
    sub_font_size = 28
    try:
        sub_font = ImageFont.truetype(str(font_path), sub_font_size)
    except Exception:
        sub_font = ImageFont.load_default()

    # Author name
    author = "Barış Kısır"
    author_font_size = 36
    try:
        author_font = ImageFont.truetype(str(font_path), author_font_size)
    except Exception:
        author_font = ImageFont.load_default()

    try:
        abbox = draw.textbbox((0, 0), author, font=author_font)
        aw = abbox[2] - abbox[0]
    except Exception:
        aw = 0
    ax = (width - aw) // 2
    ay = ty + 110
    draw.text((ax, ay), author, fill=(180, 190, 200), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Teal-black gradient for coastal horror atmosphere
    draw_gradient(draw, WIDTH, HEIGHT)
    # Faint moon through clouds
    draw_moon_glow(draw, WIDTH, HEIGHT)
    # Water surface with wave lines
    draw_water_surface(draw, WIDTH, HEIGHT)
    # Twisted bare trees on shoreline
    draw_bare_trees(draw, WIDTH, HEIGHT)
    # Dark house on pilings with one warm window
    draw_coastal_house(draw, WIDTH, HEIGHT)
    # Water reflections from lit window
    draw_water_reflections(draw, WIDTH, HEIGHT)
    # Thin fog
    draw_fog(draw, WIDTH, HEIGHT)

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