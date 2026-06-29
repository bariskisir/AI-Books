#!/usr/bin/env python3
"""Generate the cover for The Constant Garden — bioluminescent forest at twilight."""

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

# Colors
SKY_TOP = (10, 12, 30)
SKY_MID = (20, 30, 55)
SKY_BOTTOM = (35, 60, 85)
FOREST_TOP = (8, 20, 15)
FOREST_MID = (5, 14, 10)
FOREST_BOTTOM = (2, 8, 5)
GLOW_WARM = (140, 225, 180)
GLOW_COOL = (80, 200, 220)
MUSHROOM_CAP = (100, 220, 180)
MUSHROOM_STEM = (180, 240, 210)
STAR_COLOR = (220, 240, 255)
MOONLIGHT = (160, 190, 220)


def _draw_gradient(draw, y_start, y_end, color_top, color_bot):
    for y in range(y_start, y_end):
        ratio = (y - y_start) / max(1, y_end - y_start - 1)
        r = int(color_top[0] + (color_bot[0] - color_top[0]) * ratio)
        g = int(color_top[1] + (color_bot[1] - color_top[1]) * ratio)
        b = int(color_top[2] + (color_bot[2] - color_top[2]) * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def _draw_trees(draw, base_y, color, count=40):
    for i in range(count):
        x = random.randint(0, WIDTH)
        h = random.randint(250, 500)
        w = random.randint(6, 14)
        trunk_color = (
            max(0, color[0] + random.randint(-10, 5)),
            max(0, color[1] + random.randint(-10, 5)),
            max(0, color[2] + random.randint(-10, 5)),
        )
        # Main trunk
        draw.rectangle([x - w // 2, base_y - h, x + w // 2, base_y], fill=trunk_color)
        # Foliage - simple circles
        for _ in range(random.randint(3, 6)):
            fx = x + random.randint(-40, 40)
            fy = base_y - h + random.randint(-60, 10)
            fr = random.randint(30, 70)
            leaf_color = (
                max(0, color[0] + random.randint(0, 20)),
                max(0, color[1] + random.randint(10, 30)),
                max(0, color[2] + random.randint(0, 15)),
            )
            draw.ellipse([fx - fr, fy - fr, fx + fr, fy + fr], fill=leaf_color)


def _draw_mycelial_threads(draw, base_y):
    for _ in range(60):
        x = random.randint(0, WIDTH)
        y = base_y + random.randint(-200, 100)
        points = []
        cx, cy = x, y
        for _ in range(random.randint(8, 20)):
            cx += random.randint(-15, 15)
            cy += random.randint(-5, 20)
            points.append((cx, cy))
        glow = random.choice([GLOW_WARM, GLOW_COOL])
        alpha = random.randint(20, 80)
        glow_rgba = (glow[0], glow[1], glow[2], alpha)
        for i in range(len(points) - 1):
            draw.line([points[i], points[i + 1]], fill=glow_rgba, width=random.randint(1, 3))


def _draw_glowing_mushrooms(draw, base_y):
    for _ in range(25):
        x = random.randint(50, WIDTH - 50)
        y = base_y + random.randint(-100, 150)
        scale = random.uniform(0.3, 1.5)
        cap_h = int(25 * scale)
        cap_w = int(40 * scale)
        stem_h = int(50 * scale)
        stem_w = int(8 * scale)

        # Stem
        stem_color = (
            MUSHROOM_STEM[0] + random.randint(-20, 20),
            MUSHROOM_STEM[1] + random.randint(-20, 20),
            MUSHROOM_STEM[2] + random.randint(-20, 20),
        )
        draw.rectangle([x - stem_w, y - stem_h, x + stem_w, y], fill=stem_color)

        # Glowing cap
        cap_color = (
            MUSHROOM_CAP[0] + random.randint(-10, 30),
            MUSHROOM_CAP[1] + random.randint(-10, 20),
            MUSHROOM_CAP[2] + random.randint(-10, 20),
        )
        draw.ellipse([x - cap_w, y - stem_h - cap_h, x + cap_w, y - stem_h], fill=cap_color)

        # Glow aura
        for r in range(3, 8):
            alpha = max(0, 40 - r * 5)
            glow_color = (cap_color[0], cap_color[1], cap_color[2], alpha)
            draw.ellipse(
                [x - cap_w - r * 4, y - stem_h - cap_h - r * 4, x + cap_w + r * 4, y - stem_h + r * 4],
                fill=glow_color,
            )


def _draw_glow_spores(draw, base_y):
    for _ in range(200):
        x = random.randint(0, WIDTH)
        y = random.randint(base_y - 400, base_y + 200)
        r = random.randint(1, 4)
        alpha = random.randint(30, 150)
        color = random.choice([GLOW_WARM, GLOW_COOL])
        glow_color = (color[0], color[1], color[2], alpha)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=glow_color)


def _draw_stars(draw):
    for _ in range(120):
        x = random.randint(0, WIDTH)
        y = random.randint(0, 600)
        r = random.randint(1, 3)
        alpha = random.randint(80, 200)
        star_color = (STAR_COLOR[0], STAR_COLOR[1], STAR_COLOR[2], alpha)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=star_color)


def _draw_moon(draw):
    cx, cy = WIDTH - 300, 180
    r = 80
    # Glow
    for i in range(10, 0, -1):
        alpha = max(0, 25 - i * 2)
        draw.ellipse([cx - r - i * 8, cy - r - i * 8, cx + r + i * 8, cy + r + i * 8], fill=(160, 190, 220, alpha))
    # Moon
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=MOONLIGHT)
    # Crater detail
    for _ in range(8):
        ox = random.randint(-40, 40)
        oy = random.randint(-40, 40)
        cr = random.randint(4, 15)
        draw.ellipse(
            [cx + ox - cr, cy + oy - cr, cx + ox + cr, cy + oy + cr],
            fill=(140, 170, 200),
        )


def _draw_ground_glow(draw, base_y):
    for x in range(0, WIDTH, 2):
        # Horizontal gradient of subtle green glow along the ground
        intensity = random.randint(5, 20)
        for y_off in range(0, 40, 2):
            alpha = max(0, intensity - y_off)
            if alpha > 0:
                draw.point((x, base_y + y_off), fill=(50 + alpha, 120 + alpha, 80 + alpha, alpha))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=str, default="")
    parser.add_argument("--out", type=str, default="")
    args = parser.parse_args()

    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(image, "RGBA")

    # Sky gradient
    _draw_gradient(draw, 0, 1050, SKY_TOP, SKY_BOTTOM)

    # Stars
    _draw_stars(draw)

    # Moon
    _draw_moon(draw)

    # Forest gradient
    forest_start = 800
    forest_end = HEIGHT
    _draw_gradient(draw, forest_start, forest_end, FOREST_TOP, FOREST_BOTTOM)

    # Trees
    random.seed(42)
    _draw_trees(draw, forest_start + 100, FOREST_MID, count=35)

    # Additional foreground trees (darker)
    random.seed(99)
    _draw_trees(draw, forest_start + 200, FOREST_BOTTOM, count=20)

    # Ground glow
    _draw_ground_glow(draw, forest_start + 180)

    # Mycelial threads
    random.seed(77)
    _draw_mycelial_threads(draw, forest_start + 150)

    # Glowing mushrooms
    random.seed(44)
    _draw_glowing_mushrooms(draw, forest_start + 200)

    # Glow spores
    random.seed(11)
    _draw_glow_spores(draw, forest_start + 100)

    # Title/author panel via standard helpers
    metadata = {}
    if args.metadata:
        try:
            with open(args.metadata, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        except Exception:
            pass

    model = metadata.get("model", "")

    title = metadata.get("title", "The Constant Garden")
    author = metadata.get("author", "Barış Kısır")

    _draw_standard_cover_title_panel(image, title, author, model)

    output_path = args.out or "covers/The_Constant_Garden.png"
    image.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")


# ----- Standard helper functions (must be included in every cover script) -----

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    main()
