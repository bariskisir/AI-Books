#!/usr/bin/env python3
"""Generate a 1600x2560 cover for The Whispering Gallery."""

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
    model = meta.get("model", "gemini-3.5-flash")

    img = Image.new("RGB", (WIDTH, HEIGHT), (6, 8, 14))
    draw = ImageDraw.Draw(img, "RGBA")

    # Deep vertical gothic gradient (midnight blue to deep charcoal black)
    _draw_gradient(draw, WIDTH, HEIGHT, (12, 16, 28), (4, 4, 8))

    # Draw vertical wall textures/pillars faintly in background
    for x in (200, 400, WIDTH - 400, WIDTH - 200):
        # A faint vertical line/shadow
        draw.rectangle([x - 10, 0, x + 10, int(HEIGHT * 0.75)], fill=(8, 10, 18, 50))
        draw.line(
            [(x, 0), (x, int(HEIGHT * 0.75))],
            fill=(30, 35, 50, 40),
            width=2,
        )

    # Floor plane at the bottom
    floor_y = int(HEIGHT * 0.72)
    draw.rectangle([0, floor_y, WIDTH, HEIGHT], fill=(8, 8, 12))
    draw.line([(0, floor_y), (WIDTH, floor_y)], fill=(45, 50, 68), width=3)

    # Perspective lines on floor
    rng = random.Random(42)
    for i in range(12):
        x_start = WIDTH // 2 + (i - 5.5) * 80
        x_end = WIDTH // 2 + (i - 5.5) * 320
        draw.line([(x_start, floor_y), (x_end, HEIGHT)], fill=(20, 24, 34, 120), width=2)

    # Dramatic large Gothic Archway in the center (representing the whispering corridor)
    arch_cx = WIDTH // 2
    arch_base_y = floor_y
    arch_w = 460
    arch_h = 920
    _draw_archway(
        draw,
        arch_cx,
        arch_base_y,
        arch_w,
        arch_h,
        stroke_color=(20, 26, 38),
        fill_color=(5, 6, 10),
    )

    # Inside the arch: a soft golden light emanating from the floor/background
    # representing the source of the mystery
    for r in range(250, 0, -10):
        alpha = max(0, int(15 * (1 - r / 250)))
        draw.ellipse(
            [arch_cx - r, arch_base_y - 120 - r, arch_cx + r, arch_base_y - 120 + r],
            fill=(230, 180, 100, alpha),
        )

    # Concentric acoustic waves / ripples expanding from the archway
    # representing the whispers carried across the masonry
    _draw_soundwaves(draw, arch_cx, arch_base_y - 450, num_waves=6, color=(160, 220, 240))

    # A delicate candelabra on a wooden stand in the foreground to the right
    _draw_candelabra(
        draw,
        cx=WIDTH // 2 + 380,
        cy=floor_y + 80,
        scale=1.6,
        color=(25, 20, 15),
        flame_color=(240, 180, 100),
    )

    # A faint, shadowy figure silhouette standing in the archway, looking away
    # head
    figure_cx = arch_cx - 20
    figure_base_y = arch_base_y - 40
    figure_h = 320
    head_r = int(figure_h * 0.08)
    draw.ellipse(
        [
            figure_cx - head_r,
            figure_base_y - figure_h + head_r,
            figure_cx + head_r,
            figure_base_y - figure_h + 3 * head_r,
        ],
        fill=(12, 10, 14),
    )
    # torso/cloak
    draw.polygon(
        [
            (figure_cx - 15, figure_base_y - figure_h + 3 * head_r),
            (figure_cx + 15, figure_base_y - figure_h + 3 * head_r),
            (figure_cx + 45, figure_base_y),
            (figure_cx - 45, figure_base_y),
        ],
        fill=(10, 8, 12),
    )

    # Faint atmospheric dust / light rays
    for _ in range(60):
        x = rng.randint(150, WIDTH - 150)
        y = rng.randint(100, floor_y)
        size = rng.choice([1, 1, 2, 3])
        alpha = rng.randint(15, 60)
        draw.ellipse(
            [x, y, x + size, y + size],
            fill=(220, 230, 255, alpha),
        )

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
