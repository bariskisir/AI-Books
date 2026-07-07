#!/usr/bin/env python3
"""Cover: The Whispering Gallery — Blind anatomist in high-backed chair beneath domed octagonal library, concentric stone tiles, sea mist."""

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


WIDTH = 1600
HEIGHT = 2560


def _draw_gradient(draw, w, h, top_color, bottom_color):
    for y in range(h):
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * y / h)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * y / h)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * y / h)
        draw.line([(0, y), (w, y)], fill=(r, g, b))


def _draw_archway(draw, cx, cy_base, w_arch, h_arch, stroke_color, fill_color):
    """Draw a gothic pointed archway."""
    # Top arch is formed by two intersecting circles
    # Bottom is vertical lines
    r = w_arch
    # Left curve center is cx + w_arch//2 - r = cx - w_arch//2
    # Right curve center is cx - w_arch//2 + r = cx + w_arch//2
    # Let's draw it as a polygon/outline
    points = []
    # Left base
    x_left = cx - w_arch // 2
    x_right = cx + w_arch // 2
    y_straight = cy_base - h_arch + w_arch // 2

    # Draw vertical walls
    for y in range(cy_base, y_straight, -5):
        points.append((x_left, y))

    # Pointed arch curves
    # Left side curve: (x - (cx - w_arch/2))^2 + (y - y_straight)^2 = r^2
    # Right side curve: (x - (cx + w_arch/2))^2 + (y - y_straight)^2 = r^2
    # We trace from left wall top up to the point, then down to right wall top
    steps = 40
    # Left curve: x goes from cx - w_arch/2 to cx
    for i in range(steps + 1):
        x = x_left + (w_arch // 2) * i // steps
        # y = y_straight - sqrt(r^2 - (x - (cx - w_arch/2))^2)
        dx = x - (cx - w_arch // 2)
        dy = math.sqrt(max(0.0, r * r - dx * dx))
        points.append((x, int(y_straight - dy)))

    # Right curve: x goes from cx to cx + w_arch/2
    for i in range(1, steps + 1):
        x = cx + (w_arch // 2) * i // steps
        dx = x - (cx + w_arch // 2)
        dy = math.sqrt(max(0.0, r * r - dx * dx))
        points.append((x, int(y_straight - dy)))

    for y in range(y_straight, cy_base + 1, 5):
        points.append((x_right, y))

    # Close the polygon at base
    points.append((x_right, cy_base))
    points.append((x_left, cy_base))

    # Draw background fill
    draw.polygon(points, fill=fill_color)

    # Draw thick stone border
    draw.polygon(points, outline=stroke_color, width=8)


def _draw_soundwaves(draw, cx, cy, num_waves, color):
    """Draw concentric ripples representing soundwaves (whispers)."""
    for i in range(num_waves):
        r_x = 100 + i * 80
        r_y = 50 + i * 40
        # Draw dotted/dashed ellipse
        # PIL doesn't do native dashed lines easily, so we draw small segments
        # or ellipses with decreasing alpha
        alpha = max(10, 160 - i * 30)
        draw.ellipse(
            [cx - r_x, cy - r_y, cx + r_x, cy + r_y],
            outline=(color[0], color[1], color[2], alpha),
            width=2,
        )


def _draw_candelabra(draw, cx, cy, scale, color, flame_color):
    """Draw a gothic candelabra with a glowing flame."""
    s = scale
    # Base
    draw.line([(cx - int(30 * s), cy), (cx + int(30 * s), cy)], fill=color, width=int(8 * s))
    # Shaft
    draw.line([(cx, cy), (cx, cy - int(100 * s))], fill=color, width=int(6 * s))
    # Arms
    draw.arc(
        [cx - int(40 * s), cy - int(80 * s), cx + int(40 * s), cy - int(40 * s)],
        0,
        180,
        fill=color,
        width=int(4 * s),
    )
    # Candles
    candle_positions = [cx - int(40 * s), cx, cx + int(40 * s)]
    for px in candle_positions:
        # Candle wax
        draw.rectangle(
            [px - int(4 * s), cy - int(95 * s), px + int(4 * s), cy - int(75 * s)],
            fill=(220, 210, 190),
        )
        # Flame glow
        for r in range(int(24 * s), 0, -4):
            alpha = max(0, int(25 * (1 - r / (24 * s))))
            draw.ellipse(
                [px - r, cy - int(105 * s) - r, px + r, cy - int(105 * s) + r],
                fill=(flame_color[0], flame_color[1], flame_color[2], alpha),
            )
        # Flame core
        draw.ellipse(
            [
                px - int(2 * s),
                cy - int(108 * s),
                px + int(2 * s),
                cy - int(98 * s),
            ],
            fill=(255, 240, 180),
        )


def create_cover(metadata_path: str, output_path: str) -> None:
    """Create the cover image."""
    meta = {}
    if metadata_path:
        meta = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    title = meta.get("title", "The Whispering Gallery")
    author = meta.get("author", "Barış Kısır")
    model = meta.get("model", "deepseek-v4-flash")

    img = Image.new("RGB", (WIDTH, HEIGHT), (10, 12, 22))
    draw = ImageDraw.Draw(img, "RGBA")

    _draw_gradient(draw, WIDTH, HEIGHT, (18, 20, 35), (6, 6, 12))

    dome_cx, dome_cy = WIDTH // 2, 400
    dome_r = 500
    draw.arc([dome_cx - dome_r, dome_cy - dome_r, dome_cx + dome_r, dome_cy + dome_r], 0, 180, fill=(40, 45, 65, 100), width=8)
    draw.arc([dome_cx - dome_r + 30, dome_cy - dome_r + 30, dome_cx + dome_r - 30, dome_cy + dome_r - 30], 0, 180, fill=(50, 55, 75, 80), width=4)
    for a in range(0, 180, 15):
        rad = math.radians(a - 90)
        x1 = dome_cx + math.cos(rad) * (dome_r - 40)
        y1 = dome_cy + dome_r - math.sin(rad) * (dome_r - 40)
        x2 = dome_cx + math.cos(rad) * (dome_r - 20)
        y2 = dome_cy + dome_r - math.sin(rad) * (dome_r - 20)
        draw.line([(x1, y1), (x2, y2)], fill=(60, 65, 85, 80), width=2)

    oct_size = 350
    for i in range(8):
        angle = math.radians(i * 45 - 90)
        px = dome_cx + math.cos(angle) * oct_size
        py = dome_cy + dome_r - math.sin(angle) * oct_size
        px2 = dome_cx + math.cos(math.radians((i + 1) * 45 - 90)) * oct_size
        py2 = dome_cy + dome_r - math.sin(math.radians((i + 1) * 45 - 90)) * oct_size
        draw.line([(px, py), (px2, py2)], fill=(50, 55, 75, 120), width=3)

    floor_y = int(HEIGHT * 0.72)
    draw.rectangle([0, floor_y, WIDTH, HEIGHT], fill=(8, 8, 12))
    draw.line([(0, floor_y), (WIDTH, floor_y)], fill=(45, 50, 68), width=3)

    rng = random.Random(42)
    for i in range(16):
        x_start = WIDTH // 2 + (i - 7.5) * 60
        x_end = WIDTH // 2 + (i - 7.5) * 300
        draw.line([(x_start, floor_y), (x_end, HEIGHT)], fill=(25, 28, 40, 100), width=2)

    chair_cx, chair_cy = WIDTH // 2, floor_y - 60
    ch_w, ch_h = 160, 280
    draw.rectangle([chair_cx - ch_w // 2, chair_cy - ch_h, chair_cx + ch_w // 2, chair_cy], fill=(25, 22, 30, 230))
    draw.rectangle([chair_cx - ch_w // 2 - 6, chair_cy - ch_h - 10, chair_cx + ch_w // 2 + 6, chair_cy + 10], fill=(30, 28, 38, 240), outline=(50, 50, 65, 150), width=4)
    draw.polygon([(chair_cx - ch_w // 2 - 20, chair_cy - ch_h - 10), (chair_cx, chair_cy - ch_h - 50), (chair_cx + ch_w // 2 + 20, chair_cy - ch_h - 10)], fill=(35, 32, 42, 240))

    figure_cx = chair_cx
    figure_cy = chair_cy
    draw.ellipse([figure_cx - 16, figure_cy - ch_h + 50, figure_cx + 16, figure_cy - ch_h + 85], fill=(30, 28, 38, 200))
    draw.polygon([(figure_cx - 20, figure_cy - ch_h + 85), (figure_cx + 20, figure_cy - ch_h + 85), (figure_cx + 25, figure_cy - 30), (figure_cx - 25, figure_cy - 30)], fill=(28, 26, 36, 200))
    draw.line([(figure_cx - 20, figure_cy - 50), (figure_cx - 55, figure_cy - 20)], fill=(28, 26, 36, 200), width=6)
    draw.line([(figure_cx + 20, figure_cy - 50), (figure_cx + 55, figure_cy - 20)], fill=(28, 26, 36, 200), width=6)

    for _ in range(60):
        x = rng.randint(150, WIDTH - 150)
        y = rng.randint(100, floor_y)
        size = rng.choice([1, 2, 3])
        alpha = rng.randint(15, 50)
        draw.ellipse([x, y, x + size, y + size], fill=(220, 230, 255, alpha))

    mist = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    md = ImageDraw.Draw(mist)
    for _ in range(20):
        mx = rng.randint(0, WIDTH)
        my = rng.randint(200, 1400)
        mw = rng.randint(300, 800)
        md.ellipse([mx - mw, my - 40, mx + mw, my + 40], fill=(180, 190, 210, rng.randint(3, 10)))
    mist = mist.filter(ImageFilter.GaussianBlur(35))
    img = Image.alpha_composite(img.convert("RGBA"), mist)

    _draw_standard_cover_title_panel(img, title, author, model)

    output_path_p = Path(output_path)
    output_path_p.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(output_path_p, "PNG")
    print(f"Cover saved to {output_path}")


# ---- Standard helper functions (required by AGENTS.md) ----



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    create_cover(args.metadata, args.out)


if __name__ == "__main__":
    main()
