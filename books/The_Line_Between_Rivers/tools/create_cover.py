#!/usr/bin/env python3
"""Cover: The Line Between Rivers — Desert night, rusted border wall, thin river below, warm-lit panaderia, desert indigo/rusted orange/warm yellow."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import (
    _standard_cover_font,
    _standard_cover_metadata_from_locals,
    _standard_cover_resolve_title,
    _standard_cover_resolve_author,
    _draw_standard_cover_title_panel,
)


WIDTH, HEIGHT = 1600, 2560


def draw_desert_sky(draw) -> None:
    """Gradient from deep crimson at top to burnt orange at horizon."""
    for y in range(1500):
        t = y / 1500
        r = int(140 + 80 * t)
        g = int(50 + 60 * t)
        b = int(30 + 20 * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def draw_mountains(draw) -> None:
    """Distant mountain silhouettes at the horizon."""
    # Back range
    points = [(0, 1250)]
    for x in range(0, WIDTH + 40, 40):
        h = 1210 - 40 * (abs((x % 320) - 160) / 160)
        points.append((x, int(h)))
    points.append((WIDTH, 1250))
    draw.polygon(points, fill=(60, 40, 35, 200))

    # Front range
    points2 = [(0, 1250)]
    for x in range(0, WIDTH + 40, 30):
        h = 1230 - 25 * (abs((x % 240) - 120) / 120)
        points2.append((x, int(h)))
    points2.append((WIDTH, 1250))
    draw.polygon(points2, fill=(80, 55, 45, 200))


def draw_wall(draw) -> None:
    """Rusted border wall spanning the cover."""
    # Wall base
    wall_color = (130, 100, 80)
    wall_top = 1120
    bollard_w = 18
    gap = 8
    total_w = bollard_w + gap
    start_x = (WIDTH - (total_w * 55)) // 2

    for i in range(55):
        x = start_x + i * total_w
        # Main bollard
        draw.rectangle([x, wall_top, x + bollard_w, 1400], fill=wall_color)
        # Rust streaks
        for j in range(3):
            ry = wall_top + 50 + j * 80
            draw.line([(x + 3, ry), (x + 5, ry + 30)], fill=(160, 100, 60, 100), width=2)
        # Top cap
        draw.rectangle([x - 2, wall_top - 10, x + bollard_w + 2, wall_top], fill=(100, 75, 60))
        # Razor wire suggestion
        for wx in (x, x + bollard_w // 2, x + bollard_w):
            draw.line([(wx, wall_top - 18), (wx + 4, wall_top - 25), (wx + 8, wall_top - 18)], fill=(160, 140, 130, 150), width=1)


def draw_river(draw) -> None:
    """Thin trickle of river at the base of the wall."""
    river_y = 1350
    # Mud bank
    draw.rectangle([(0, river_y), (WIDTH, 1470)], fill=(100, 85, 70))
    # Water trickle
    water_y = 1390
    draw.rectangle([(0, water_y), (WIDTH, water_y + 20)], fill=(70, 90, 100, 180))
    # Rivulets
    for rx in range(0, WIDTH, 60):
        rw = 2
        rh = 5 + (rx % 15)
        draw.rectangle([(rx, water_y + 22), (rx + rw, water_y + 22 + rh)], fill=(65, 80, 90, 150))
    # Dry cracked mud pattern
    for cx in range(0, WIDTH, 40):
        for cy in range(1420, 1470, 15):
            draw.line([(cx, cy), (cx + 15, cy + 5)], fill=(85, 72, 58, 80), width=1)
            draw.line([(cx + 15, cy + 5), (cx + 30, cy)], fill=(85, 72, 58, 80), width=1)


def draw_panaderia(draw) -> None:
    """Small warm-lit bakery on the American side of the wall."""
    cx = 300
    by = 1400
    # Building
    draw.rectangle([(cx - 60, by - 100), (cx + 60, by)], fill=(180, 160, 130))
    # Roof
    draw.polygon([(cx - 65, by - 100), (cx, by - 130), (cx + 65, by - 100)], fill=(150, 130, 100))
    # Window (warm light)
    draw.rectangle([(cx - 40, by - 80), (cx - 10, by - 40)], fill=(240, 200, 130, 180))
    draw.rectangle([(cx + 10, by - 80), (cx + 40, by - 40)], fill=(240, 200, 130, 180))
    # Door
    draw.rectangle([(cx - 8, by - 50), (cx + 8, by)], fill=(120, 90, 70))
    # Sign
    draw.rectangle([(cx - 35, by - 120), (cx + 35, by - 108)], fill=(100, 70, 50))
    if _standard_cover_font("arial.ttf", 12):
        font = _standard_cover_font("arial.ttf", 10)
        draw.text((cx - 20, by - 118), "PANADERIA", font=font, fill=(240, 220, 180))


def draw_cross(draw) -> None:
    """Small cross on a hill, suggesting the cemetery."""
    cx, cy = 1380, 1280
    draw.line([(cx, cy - 30), (cx, cy + 10)], fill=(180, 160, 140, 120), width=3)
    draw.line([(cx - 15, cy - 15), (cx + 15, cy - 15)], fill=(180, 160, 140, 120), width=3)


def draw_fence_crossers(draw) -> None:
    """Small silhouettes suggesting people separated by the wall."""
    # On American side
    for i, (fx, fy) in enumerate([(700, 1145), (1100, 1150), (900, 1140)]):
        # Head
        draw.ellipse([(fx - 4, fy - 16), (fx + 4, fy - 8)], fill=(40, 35, 30, 120))
        # Body
        draw.line([(fx, fy - 8), (fx, fy + 8)], fill=(40, 35, 30, 120), width=2)
        if i == 0:
            draw.line([(fx - 5, fy), (fx + 5, fy)], fill=(40, 35, 30, 120), width=2)


def create_cover(title: str, author: str, output_path: Path) -> None:
    img = Image.new("RGBA", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)

    # Deep border-night sky
    for y in range(HEIGHT):
        p = y / HEIGHT
        r = int(35 + 80 * p)
        g = int(25 + 50 * p)
        b = int(40 + 30 * p)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Stars in upper portion
    import random
    rng = random.Random("line-between-rivers-cover")
    for _ in range(120):
        sx = rng.randint(0, WIDTH)
        sy = rng.randint(0, 500)
        brightness = rng.randint(160, 220)
        draw.point((sx, sy), fill=(brightness, brightness, brightness, 200))

    # Crescent moon
    moon_x, moon_y, moon_r = 1250, 150, 35
    draw.ellipse([(moon_x - moon_r, moon_y - moon_r), (moon_x + moon_r, moon_y + moon_r)], fill=(220, 210, 190, 180))
    draw.ellipse([(moon_x + 12, moon_y - moon_r - 5), (moon_x + moon_r + 15, moon_y + moon_r + 5)], fill=(60, 50, 55))

    draw_desert_sky(draw)
    draw_mountains(draw)
    draw_wall(draw)
    draw_river(draw)
    draw_panaderia(draw)
    draw_cross(draw)
    draw_fence_crossers(draw)

    # Subtle ground shadow in front
    draw.rectangle([(0, 1470), (WIDTH, 1765)], fill=(70, 58, 48))

    # Vignette
    vignette = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    v_draw = ImageDraw.Draw(vignette)
    v_draw.ellipse([-300, -300, WIDTH + 300, HEIGHT + 300], fill=(0, 0, 0, 0))
    v_draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(0, 0, 0, 90))
    img = Image.alpha_composite(img, vignette)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img = img.convert("RGB")
    _draw_standard_cover_title_panel(
        img,
        _standard_cover_resolve_title(locals()),
        _standard_cover_resolve_author(locals()),
        _standard_cover_metadata_from_locals(locals()).get("model", ""),
    )
    img.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    title = metadata["title"]
    author = metadata.get("author", "Barış Kısır")

    create_cover(title, author, args.out)


if __name__ == "__main__":
    main()
