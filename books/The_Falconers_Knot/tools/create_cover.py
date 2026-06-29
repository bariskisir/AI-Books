#!/usr/bin/env python3
"""Generate a 1600x2560 cover for The Falconer's Knot."""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

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


def _draw_stone_wall(draw, w, h, color, mortar_color):
    """Draw a faint stone-block pattern suggesting monastery walls."""
    rng = random.Random(77)
    block_h = 48
    for row in range(0, h, block_h):
        offset = rng.randint(0, 120)
        block_w = rng.randint(80, 160)
        x = offset
        while x < w:
            alpha = rng.randint(12, 30)
            draw.rectangle(
                [x + 2, row + 2, x + block_w - 2, row + block_h - 2],
                fill=(color[0], color[1], color[2], alpha),
            )
            # mortar lines
            draw.line([(x, row), (x, row + block_h)], fill=(mortar_color[0], mortar_color[1], mortar_color[2], 15), width=1)
            x += block_w
        draw.line([(0, row), (w, row)], fill=(mortar_color[0], mortar_color[1], mortar_color[2], 15), width=1)


def _draw_romanesque_arch(draw, cx, cy_base, w_arch, h_arch, stroke_color, fill_color):
    """Draw a rounded Romanesque archway (semicircular top)."""
    x_left = cx - w_arch // 2
    x_right = cx + w_arch // 2
    arch_top = cy_base - h_arch

    # Vertical walls
    draw.rectangle([x_left - 20, arch_top + w_arch // 2, x_left, cy_base], fill=stroke_color)
    draw.rectangle([x_right, arch_top + w_arch // 2, x_right + 20, cy_base], fill=stroke_color)

    # Fill inside
    draw.rectangle([x_left, arch_top + w_arch // 2, x_right, cy_base], fill=fill_color)

    # Semicircular top
    draw.ellipse(
        [x_left, arch_top, x_right, arch_top + w_arch],
        fill=fill_color,
    )
    # Arch border
    draw.arc(
        [x_left, arch_top, x_right, arch_top + w_arch],
        180, 0,
        fill=stroke_color,
        width=12,
    )
    draw.line([(x_left, arch_top + w_arch // 2), (x_left, cy_base)], fill=stroke_color, width=12)
    draw.line([(x_right, arch_top + w_arch // 2), (x_right, cy_base)], fill=stroke_color, width=12)


def _draw_falcon_silhouette(draw, cx, cy, scale, color):
    """Draw a stylized falcon silhouette in flight."""
    s = scale
    # Body
    body_points = [
        (cx, cy - int(10 * s)),           # head
        (cx + int(6 * s), cy),            # chest
        (cx + int(4 * s), cy + int(25 * s)),  # tail start
        (cx + int(12 * s), cy + int(35 * s)), # tail tip right
        (cx - int(12 * s), cy + int(35 * s)), # tail tip left
        (cx - int(4 * s), cy + int(25 * s)),  # tail start left
        (cx - int(6 * s), cy),            # back
    ]
    draw.polygon(body_points, fill=color)

    # Left wing
    wing_l = [
        (cx - int(6 * s), cy + int(2 * s)),
        (cx - int(60 * s), cy - int(30 * s)),
        (cx - int(70 * s), cy - int(25 * s)),
        (cx - int(50 * s), cy + int(5 * s)),
        (cx - int(4 * s), cy + int(12 * s)),
    ]
    draw.polygon(wing_l, fill=color)

    # Right wing
    wing_r = [
        (cx + int(6 * s), cy + int(2 * s)),
        (cx + int(60 * s), cy - int(30 * s)),
        (cx + int(70 * s), cy - int(25 * s)),
        (cx + int(50 * s), cy + int(5 * s)),
        (cx + int(4 * s), cy + int(12 * s)),
    ]
    draw.polygon(wing_r, fill=color)


def _draw_cross(draw, cx, cy, size, color, width=6):
    """Draw a simple cross."""
    draw.line([(cx, cy - size), (cx, cy + size)], fill=color, width=width)
    draw.line([(cx - size * 2 // 3, cy - size // 3), (cx + size * 2 // 3, cy - size // 3)], fill=color, width=width)


def _draw_candle_flame(draw, cx, cy, scale, glow_color):
    """Draw a single candle with warm glow."""
    s = scale
    # Candle body
    draw.rectangle(
        [cx - int(4 * s), cy, cx + int(4 * s), cy + int(40 * s)],
        fill=(210, 195, 160),
    )
    # Glow
    for r in range(int(30 * s), 0, -3):
        alpha = max(0, int(20 * (1 - r / (30 * s))))
        draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            fill=(glow_color[0], glow_color[1], glow_color[2], alpha),
        )
    # Flame core
    points = [
        (cx, cy - int(12 * s)),
        (cx + int(4 * s), cy),
        (cx - int(4 * s), cy),
    ]
    draw.polygon(points, fill=(255, 230, 150))


def create_cover(metadata_path: str, output_path: str) -> None:
    """Create the cover image."""
    meta = {}
    if metadata_path:
        meta = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    title = meta.get("title", "The Falconer's Knot")
    author = meta.get("author", "Barış Kısır")
    model = meta.get("model", "opus-4.6")

    img = Image.new("RGB", (WIDTH, HEIGHT), (18, 12, 8))
    draw = ImageDraw.Draw(img, "RGBA")

    # Warm dark gradient — burnt umber to deep brown-black (medieval parchment feel)
    _draw_gradient(draw, WIDTH, HEIGHT, (32, 22, 14), (8, 5, 3))

    # Faint stone-wall texture across the upper portion
    _draw_stone_wall(draw, WIDTH, int(HEIGHT * 0.7), (45, 35, 25), (60, 50, 35))

    # Floor plane
    floor_y = int(HEIGHT * 0.70)
    draw.rectangle([0, floor_y, WIDTH, HEIGHT], fill=(12, 8, 5))
    draw.line([(0, floor_y), (WIDTH, floor_y)], fill=(55, 40, 28), width=3)

    # Perspective floor tiles
    rng = random.Random(1348)
    for i in range(14):
        x_start = WIDTH // 2 + (i - 6.5) * 70
        x_end = WIDTH // 2 + (i - 6.5) * 300
        draw.line([(x_start, floor_y), (x_end, HEIGHT)], fill=(25, 18, 12, 80), width=2)

    # Large Romanesque archway — the monastery cloister
    arch_cx = WIDTH // 2
    arch_base_y = floor_y
    _draw_romanesque_arch(
        draw, arch_cx, arch_base_y, 480, 850,
        stroke_color=(50, 38, 26),
        fill_color=(6, 4, 2),
    )

    # Warm golden light emanating from within the archway
    for r in range(300, 0, -8):
        alpha = max(0, int(12 * (1 - r / 300)))
        draw.ellipse(
            [arch_cx - r, arch_base_y - 350 - r // 2, arch_cx + r, arch_base_y - 350 + r // 2],
            fill=(220, 160, 80, alpha),
        )

    # A falcon silhouette soaring high above the archway
    _draw_falcon_silhouette(draw, arch_cx + 80, 280, 3.0, (20, 14, 8))
    # Smaller second falcon in the distance
    _draw_falcon_silhouette(draw, arch_cx - 180, 200, 1.5, (25, 18, 10))

    # Stone cross atop the archway
    _draw_cross(draw, arch_cx, floor_y - 880, 40, (65, 50, 35), width=8)

    # Candle flames on either side of the archway (wall sconces)
    _draw_candle_flame(draw, arch_cx - 340, floor_y - 200, 1.8, (240, 170, 80))
    _draw_candle_flame(draw, arch_cx + 340, floor_y - 200, 1.8, (240, 170, 80))

    # A cloaked figure standing inside the archway, turned away
    figure_cx = arch_cx + 15
    figure_base_y = arch_base_y - 30
    figure_h = 340
    head_r = int(figure_h * 0.07)
    # Head
    draw.ellipse(
        [figure_cx - head_r, figure_base_y - figure_h,
         figure_cx + head_r, figure_base_y - figure_h + 2 * head_r],
        fill=(10, 7, 4),
    )
    # Hooded robe / cowl
    draw.polygon(
        [
            (figure_cx - 18, figure_base_y - figure_h + 2 * head_r),
            (figure_cx + 18, figure_base_y - figure_h + 2 * head_r),
            (figure_cx + 55, figure_base_y),
            (figure_cx - 55, figure_base_y),
        ],
        fill=(14, 10, 6),
    )

    # Dust motes / floating particles in candlelight
    for _ in range(80):
        x = rng.randint(100, WIDTH - 100)
        y = rng.randint(80, floor_y - 50)
        size = rng.choice([1, 1, 2, 2, 3])
        alpha = rng.randint(15, 50)
        draw.ellipse(
            [x, y, x + size, y + size],
            fill=(220, 190, 130, alpha),
        )

    # A thin rope/knot symbol in the lower foreground — the falconer's knot
    knot_cx = arch_cx - 350
    knot_cy = floor_y + 60
    # Simple overhand knot suggestion
    draw.arc([knot_cx - 25, knot_cy - 25, knot_cx + 25, knot_cy + 25], 0, 300, fill=(90, 70, 45, 120), width=4)
    draw.arc([knot_cx - 15, knot_cy - 15, knot_cx + 15, knot_cy + 15], 30, 330, fill=(80, 60, 40, 100), width=3)
    # Trailing rope ends
    draw.line([(knot_cx + 20, knot_cy + 15), (knot_cx + 50, knot_cy + 45)], fill=(85, 65, 42, 100), width=3)
    draw.line([(knot_cx - 20, knot_cy + 15), (knot_cx - 45, knot_cy + 50)], fill=(85, 65, 42, 100), width=3)

    # Standard title panel at the bottom
    _draw_standard_cover_title_panel(img, title, author, model)

    output_path_p = Path(output_path)
    output_path_p.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path_p, "PNG")
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
