#!/usr/bin/env python3
"""Cover: The Wolves of Winter — Grey-white alpha wolf on snowy ridge overlooking frozen plain, lone huntress with spear below."""

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
    for y in range(height):
        t = y / height
        if t < 0.4:
            t2 = t / 0.4
            c = lerp_color((40, 50, 60), (80, 90, 100), t2)
        elif t < 0.7:
            t2 = (t - 0.4) / 0.3
            c = lerp_color((80, 90, 100), (140, 150, 160), t2)
        else:
            t2 = (t - 0.7) / 0.3
            c = lerp_color((140, 150, 160), (200, 210, 220), t2)
        draw.line([(0, y), (width, y)], fill=c)


def draw_mountains(draw: ImageDraw, width: int, height: int) -> None:
    rng = random.Random("winter-mountains")
    for x in range(0, width, 3):
        mh = 600 + 80 * math.sin(x / 120) + 50 * math.sin(x / 50) + 30 * math.sin(x / 20)
        mh += rng.randint(-8, 8)
        draw.line([(x, int(mh)), (x, height)], fill=(60, 70, 80, 180))


def draw_frozen_plain(draw: ImageDraw, width: int, height: int) -> None:
    rng = random.Random("frozen-plain")
    plain_y = 1100
    for y in range(plain_y, height, 4):
        t = (y - plain_y) / (height - plain_y)
        wave = int(3 * math.sin(y / 60 + 1))
        r = int(160 + 60 * t)
        g = int(170 + 55 * t)
        b = int(185 + 50 * t)
        draw.line([(0, y + wave), (width, y)], fill=(r, g, b))
    for _ in range(40):
        sx = rng.randint(0, width)
        sy = rng.randint(plain_y + 50, plain_y + 400)
        sw = rng.randint(20, 80)
        draw.arc((sx, sy, sx + sw, sy + 8), 180, 0, fill=(180, 190, 200, 60), width=2)


def draw_ridge(draw: ImageDraw, width: int, height: int) -> None:
    rng = random.Random("snow-ridge")
    ridge_y = 700
    points = []
    for x in range(0, width, 10):
        ry = ridge_y + 30 * math.sin(x / 80) + 20 * math.sin(x / 30) + rng.randint(-10, 10)
        points.append((x, ry))
    draw.polygon(points + [(width, height), (0, height)], fill=(140, 150, 160, 200))
    for x in range(0, width, 2):
        rx = x
        idx = x // 10
        if idx < len(points) - 1:
            ry = points[idx][1] + (points[idx + 1][1] - points[idx][1]) * ((x % 10) / 10)
            draw.line([(rx, ry), (rx, height)], fill=(180, 190, 200))


def draw_alpha_wolf(draw: ImageDraw, width: int, height: int) -> None:
    rng = random.Random("alpha-wolf")
    cx, cy = width // 2 + 80, 650
    body_color = (150, 155, 160)
    dark_color = (80, 85, 90)
    body_w, body_h = 70, 35
    draw.ellipse([cx - body_w, cy - body_h, cx + body_w, cy + body_h], fill=body_color)
    neck_pts = [(cx + 50, cy - 5), (cx + 80, cy - 25), (cx + 90, cy + 5), (cx + 60, cy + 10)]
    draw.polygon(neck_pts, fill=body_color)
    head_cx = cx + 90
    head_cy = cy - 20
    draw.ellipse([head_cx - 18, head_cy - 15, head_cx + 18, head_cy + 15], fill=body_color)
    snout_pts = [(head_cx + 10, head_cy - 5), (head_cx + 35, head_cy + 2), (head_cx + 10, head_cy + 10)]
    draw.polygon(snout_pts, fill=body_color)
    draw.ellipse([head_cx - 10, head_cy - 10, head_cx - 2, head_cy - 2], fill=(200, 210, 220))
    draw.ellipse([head_cx - 8, head_cy - 8, head_cx - 4, head_cy - 4], fill=(30, 30, 35))
    draw.ellipse([head_cx + 15, head_cy - 3, head_cx + 22, head_cy + 3], fill=(20, 20, 25))
    ear_pts = [(head_cx - 12, head_cy - 14), (head_cx - 5, head_cy - 30), (head_cx + 2, head_cy - 14)]
    draw.polygon(ear_pts, fill=body_color)
    ear2_pts = [(head_cx + 5, head_cy - 14), (head_cx + 12, head_cy - 28), (head_cx + 18, head_cy - 14)]
    draw.polygon(ear2_pts, fill=body_color)
    leg_positions = [(cx - 40, cy + 10), (cx - 15, cy + 10), (cx + 15, cy + 10), (cx + 40, cy + 10)]
    for lx, ly in leg_positions:
        draw.line([(lx, ly), (lx + 5, ly + 60)], fill=dark_color, width=8)
        draw.ellipse([lx, ly + 55, lx + 10, ly + 65], fill=dark_color)
    tail_pts = [(cx - 70, cy - 5), (cx - 100, cy - 25), (cx - 105, cy - 15), (cx - 80, cy)]
    draw.polygon(tail_pts, fill=body_color)


def draw_huntress(draw: ImageDraw, width: int, height: int) -> None:
    cx, cy = width // 2 - 80, 1000
    h = 180
    skin = (180, 160, 140)
    fur = (100, 80, 60)
    draw.ellipse([cx - 10, cy - h, cx + 10, cy - h + 25], fill=skin)
    draw.polygon([(cx - 20, cy - h + 25), (cx + 20, cy - h + 25), (cx + 22, cy - 30), (cx - 22, cy - 30)], fill=fur)
    draw.polygon([(cx - 18, cy - 30), (cx + 18, cy - 30), (cx + 22, cy - 10), (cx - 22, cy - 10)], fill=fur)
    draw.line([(cx, cy - 10), (cx, cy + 20)], fill=skin, width=6)
    draw.line([(cx - 22, cy + 10), (cx - 60, cy + 30)], fill=skin, width=5)
    draw.line([(cx + 22, cy + 10), (cx + 55, cy - 20)], fill=skin, width=5)
    spear_y1 = cy - h - 20
    spear_y2 = cy + 40
    draw.line([(cx + 55, spear_y1), (cx + 55, spear_y2)], fill=(120, 100, 80), width=4)
    draw.polygon([(cx + 55, spear_y1), (cx + 50, spear_y1 + 15), (cx + 60, spear_y1 + 15)], fill=(180, 170, 150))
    draw.line([(cx - 22, cy + 20), (cx - 22, cy + 60)], fill=skin, width=6)
    draw.line([(cx + 2, cy + 20), (cx + 2, cy + 60)], fill=skin, width=6)


def draw_snowflakes(draw: ImageDraw, width: int, height: int) -> None:
    rng = random.Random("winter-snow")
    for _ in range(180):
        x = rng.randint(0, width)
        y = rng.randint(0, 1800)
        sr = rng.randint(1, 4)
        sa = rng.randint(80, 200)
        draw.ellipse([x - sr, y - sr, x + sr, y + sr], fill=(255, 255, 255, sa))


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Wolves of Winter")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    draw_gradient(draw, WIDTH, HEIGHT)
    draw_mountains(draw, WIDTH, HEIGHT)
    draw_frozen_plain(draw, WIDTH, HEIGHT)
    draw_ridge(draw, WIDTH, HEIGHT)
    draw_alpha_wolf(draw, WIDTH, HEIGHT)
    draw_huntress(draw, WIDTH, HEIGHT)
    draw_snowflakes(draw, WIDTH, HEIGHT)

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
