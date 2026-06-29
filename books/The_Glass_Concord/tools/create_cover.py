#!/usr/bin/env python3
"""Generate the cover for The Glass Concord — a crystalline glass city at dawn."""

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
DAWN_SKY_TOP = (40, 30, 60)
DAWN_SKY_MID = (120, 80, 100)
DAWN_SKY_BOTTOM = (250, 180, 140)
GLASS_HIGHLIGHT = (220, 200, 180)
GLASS_MID = (160, 180, 200)
GLASS_SHADOW = (80, 100, 130)
GLASS_WARM = (240, 210, 160)
FIGURE_DARK = (40, 45, 55)
BUILDING_FRAME = (60, 70, 90)
SUN_GLOW = (255, 220, 150)
GROUND_COLOR = (30, 35, 50)


def _draw_gradient(draw, y_start, y_end, color_top, color_bot):
    for y in range(y_start, y_end):
        ratio = (y - y_start) / max(1, y_end - y_start - 1)
        r = int(color_top[0] + (color_bot[0] - color_top[0]) * ratio)
        g = int(color_top[1] + (color_bot[1] - color_top[1]) * ratio)
        b = int(color_top[2] + (color_bot[2] - color_top[2]) * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def _draw_sun(draw):
    # Rising sun on the horizon
    cx = WIDTH // 2 + 100
    cy = 750
    r = 100

    # Outer glow layers
    for i in range(15, 0, -1):
        alpha = max(0, 60 - i * 3)
        draw.ellipse(
            [cx - r - i * 20, cy - r - i * 20, cx + r + i * 20, cy + r + i * 20],
            fill=(SUN_GLOW[0], SUN_GLOW[1], SUN_GLOW[2], alpha),
        )

    # Sun disc
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SUN_GLOW)

    # Horizon glow rays
    for angle_deg in range(-30, 31, 5):
        angle = math.radians(angle_deg)
        for dist in range(0, 200, 20):
            px = cx + int(math.cos(angle) * (r + dist))
            py = cy + int(math.sin(angle) * (r + dist))
            alpha = max(0, 40 - dist // 5)
            if alpha > 0:
                draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 220, 150, alpha))


def _draw_glass_building(draw, x, base_y, width, height, floors=12):
    """Draw a single glass building with transparent interior revealing figures."""
    # Main glass body gradient
    for wx in range(x, x + width):
        rel_x = (wx - x) / width
        shade = GLASS_MID
        if rel_x < 0.3:
            shade = GLASS_HIGHLIGHT
        elif rel_x > 0.7:
            shade = GLASS_SHADOW
        draw.line([(wx, base_y - height), (wx, base_y)], fill=shade)

    # Building frame outline
    draw.rectangle([x, base_y - height, x + width, base_y], outline=BUILDING_FRAME, width=2)

    # Floor lines
    floor_h = height // floors
    for f in range(1, floors):
        fy = base_y - f * floor_h
        draw.line([(x + 2, fy), (x + width - 2, fy)], fill=BUILDING_FRAME, width=1)

    # Windows - transparent with interior elements
    for f in range(floors):
        cols = max(2, min(4, width // 25))
        for col in range(cols):
            col_w = (width - 12) // cols
            wx1 = x + 6 + col * col_w
            wx2 = min(wx1 + col_w - 4, x + width - 6)
            wy1 = base_y - (f + 1) * floor_h + 4
            wy2 = wy1 + floor_h - 8
            if wx2 <= wx1 or wy2 <= wy1:
                continue

            # Interior room color (warm)
            interior_warmth = random.randint(180, 240)
            draw.rectangle([wx1, wy1, wx2, wy2], fill=(interior_warmth, interior_warmth - 20, interior_warmth - 60, 180))

            # Figure silhouette inside
            if random.random() < 0.4:
                avail_h = wy2 - wy1 - 4
                avail_w = wx2 - wx1 - 8
                if avail_h >= 10 and avail_w >= 6:
                    fig_h = random.randint(8, min(20, avail_h))
                    fig_w = random.randint(4, min(10, avail_w))
                    fig_x_min = wx1 + 4
                    fig_x_max = wx2 - fig_w - 4
                    if fig_x_max > fig_x_min:
                        fig_x = random.randint(fig_x_min, fig_x_max)
                        fig_y = wy2 - fig_h
                        draw.rectangle([fig_x, fig_y, fig_x + fig_w, fig_y + fig_h], fill=FIGURE_DARK)

            # Window frame
            draw.rectangle([wx1, wy1, wx2, wy2], outline=BUILDING_FRAME, width=1)

            # Glass reflection highlight
            if random.random() < 0.3 and wy2 - wy1 > 6:
                draw.rectangle([wx1 + 2, wy1 + 2, wx1 + 6, wy2 - 2], fill=(255, 255, 255, 60))


def _draw_skyline(draw, base_y):
    """Draw a row of glass buildings forming a skyline."""
    buildings = []

    # Center tallest buildings
    cx = WIDTH // 2
    for i in range(-3, 4):
        bx = cx + i * 180 + random.randint(-20, 20)
        bw = random.randint(80, 150)
        bh = random.randint(350, 650)
        if bx < 20 or bx + bw > WIDTH - 20:
            continue
        buildings.append((bx, bw, bh))

    # Left buildings
    for i in range(6):
        bx = 20 + i * random.randint(120, 180)
        bw = random.randint(60, 120)
        bh = random.randint(200, 500)
        if bx + bw > WIDTH // 2 - 100:
            break
        buildings.append((bx, bw, bh))

    # Right buildings
    for i in range(6):
        bx = WIDTH // 2 + 200 + i * random.randint(120, 180)
        bw = random.randint(60, 120)
        bh = random.randint(200, 500)
        if bx + bw > WIDTH - 20:
            break
        buildings.append((bx, bw, bh))

    # Sort by x position
    buildings.sort()

    # Draw each building
    floors_counts = [random.randint(6, 20) for _ in buildings]
    for (bx, bw, bh), floors in zip(buildings, floors_counts):
        _draw_glass_building(draw, bx, base_y, bw, bh, floors)

    return buildings


def _draw_ground(draw, base_y, image):
    """Draw the ground/plaza area."""
    # Ground gradient
    _draw_gradient(draw, base_y, HEIGHT, GROUND_COLOR, (15, 20, 30))

    # Ground reflection of buildings
    for x in range(0, WIDTH, 4):
        pixel_color = image.getpixel((x, base_y - 1))
        if isinstance(pixel_color, tuple) and len(pixel_color) >= 3:
            for y_off in range(0, 60, 2):
                alpha = max(0, 60 - y_off)
                draw.point((x, base_y + y_off), fill=(pixel_color[0], pixel_color[1], pixel_color[2], alpha))


def _draw_reflections(draw, base_y, buildings):
    """Draw reflections of buildings on the ground."""
    for bx, bw, bh in buildings:
        # Faded reflection
        for wx in range(bx, bx + bw):
            for y_off in range(0, bh // 4, 2):
                alpha = max(0, 25 - y_off // 2)
                if alpha > 0:
                    draw.point((wx, base_y + y_off), fill=(GLASS_MID[0], GLASS_MID[1], GLASS_MID[2], alpha))


def _draw_citizens(draw, base_y):
    """Draw small figures on the streets/plaza."""
    for _ in range(15):
        x = random.randint(50, WIDTH - 50)
        # Avoid overlapping with building positions
        y = base_y + random.randint(5, 15)
        h = random.randint(14, 22)
        w = random.randint(5, 8)
        # Body
        body_color = (random.randint(30, 60), random.randint(30, 60), random.randint(40, 70))
        draw.rectangle([x - w // 2, y - h, x + w // 2, y], fill=body_color)
        # Head
        head_r = random.randint(3, 5)
        draw.ellipse([x - head_r, y - h - head_r * 2, x + head_r, y - h], fill=body_color)


def _draw_reflection_highlights(draw):
    """Add light reflection streaks on glass."""
    for _ in range(30):
        x = random.randint(100, WIDTH - 100)
        y = random.randint(200, 900)
        length = random.randint(10, 60)
        alpha = random.randint(20, 60)
        draw.line(
            [(x, y), (x + length, y - length // 2)],
            fill=(255, 255, 255, alpha),
            width=random.randint(1, 3),
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=str, default="")
    parser.add_argument("--out", type=str, default="")
    args = parser.parse_args()

    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(image, "RGBA")

    # Dawn sky gradient
    _draw_gradient(draw, 0, 800, DAWN_SKY_TOP, DAWN_SKY_BOTTOM)

    # Sun on horizon
    _draw_sun(draw)

    # Sky below sun - warm horizon glow
    _draw_gradient(draw, 700, 900, (255, 200, 150), (250, 180, 140))

    # Glass buildings
    random.seed(42)
    base_y = 900
    buildings = _draw_skyline(draw, base_y)

    # Ground
    _draw_ground(draw, base_y, image)

    # Reflections
    random.seed(43)
    _draw_reflections(draw, base_y, buildings)

    # Citizens on the plaza
    random.seed(44)
    _draw_citizens(draw, base_y)

    # Reflection highlights on glass
    random.seed(45)
    _draw_reflection_highlights(draw)

    # Title/author panel via standard helpers
    metadata = {}
    if args.metadata:
        try:
            with open(args.metadata, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        except Exception:
            pass

    model = metadata.get("model", "")

    title = metadata.get("title", "The Glass Concord")
    author = metadata.get("author", "Barış Kısır")

    _draw_standard_cover_title_panel(image, title, author, model)

    output_path = args.out or "covers/The_Glass_Concord.png"
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
