#!/usr/bin/env python3
"""Generate a cover image for The Common Breath."""

from __future__ import annotations

import argparse
import json
import math
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


def _make_gradient(draw, y1, y2, color1, color2):
    for y in range(y1, y2):
        ratio = (y - y1) / max(y2 - y1 - 1, 1)
        r = int(color1[0] + (color2[0] - color1[0]) * ratio)
        g = int(color1[1] + (color2[1] - color1[1]) * ratio)
        b = int(color1[2] + (color2[2] - color1[2]) * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def _draw_ceiling(draw):
    """Draw a vast industrial ceiling with conveyor supports."""
    # Ceiling gradient - dark industrial
    _make_gradient(draw, 0, 400, (40, 45, 55), (60, 68, 78))

    # Structural beams across ceiling
    for x in range(0, WIDTH, 120):
        draw.rectangle([x, 0, x + 20, 350], fill=(70, 78, 88, 200))
        # Cross beams
        for y in range(50, 350, 80):
            draw.rectangle([x - 10, y, x + 30, y + 6], fill=(80, 88, 98, 180))

    # Main cross-beam
    draw.rectangle([0, 200, WIDTH, 216], fill=(55, 63, 73, 220))


def _draw_conveyor_system(draw):
    """Draw distribution center conveyor belts and packages."""
    # Row of conveyor belts at different heights and angles
    conveyor_data = [
        # (y_start, y_end, x_start, x_end, color, package_count)
        (750, 770, 0, WIDTH, (70, 85, 75), 15),
        (820, 840, 0, WIDTH, (75, 90, 80), 12),
        (890, 910, 0, WIDTH, (68, 82, 72), 10),
        (960, 980, 0, WIDTH, (72, 87, 77), 8),
        (1030, 1050, 0, WIDTH, (65, 80, 70), 6),
        (1100, 1120, 0, WIDTH, (70, 85, 75), 5),
    ]

    for y_start, y_end, x_start, x_end, color, pcount in conveyor_data:
        # Belt surface
        draw.rectangle([x_start, y_start, x_end, y_end], fill=color)

        # Belt roller texture
        for bx in range(0, WIDTH, 16):
            draw.ellipse([bx, y_start - 8, bx + 12, y_end + 8], fill=(55, 70, 60))

        # Packages on the belt
        for pi in range(pcount):
            px = pi * (WIDTH // pcount) + 20
            py = y_start - 25 - int(math.sin(pi * 2.3) * 10)
            pw = 30 + int(math.sin(pi * 1.7) * 10)
            ph = 20 + int(math.sin(pi * 2.7) * 8)

            # Package body
            pcolors = [(120, 100, 80), (90, 110, 130), (110, 90, 70), (100, 120, 100), (130, 110, 90)]
            pc = pcolors[pi % len(pcolors)]
            draw.rectangle([px, py, px + pw, py + ph], fill=pc)
            # Package tape/line
            draw.line([(px, py + ph // 2), (px + pw, py + ph // 2)], fill=(40, 40, 50, 120), width=2)


def _draw_package_flows(draw):
    """Draw diagonal/curved chutes carrying packages between levels."""
    chute_starts = [(200, 650), (500, 620), (850, 660), (1200, 630), (1450, 640)]

    for cx, cy in chute_starts:
        # Chute path
        points = []
        for t in range(0, 51):
            frac = t / 50
            x = cx + int(frac * (WIDTH - cx - 200) * 0.7)
            y = cy + int(frac * 380) + int(math.sin(frac * 4) * 60 * frac)
            points.append((x, y))

        # Draw chute
        for i in range(len(points) - 1):
            draw.line([points[i], points[i + 1]], fill=(80, 100, 90, 150), width=12)
            draw.line([points[i], points[i + 1]], fill=(100, 120, 110, 80), width=6)

        # Packages on chutes
        for pi in range(4):
            frac = (pi + 1) / 5
            px = cx + int(frac * (WIDTH - cx - 200) * 0.7)
            py = cy + int(frac * 380) + int(math.sin(frac * 4) * 60 * frac) - 15
            draw.rectangle([px - 15, py - 10, px + 15, py + 10], fill=(130, 110, 90, 180))


def _draw_distribution_hall(draw):
    """Draw the main hall ambiance."""
    # Back wall with shelving
    _make_gradient(draw, 350, 700, (50, 60, 70), (40, 50, 60))

    # Shelving units in background
    for sx in range(30, WIDTH, 180):
        for sy in range(380, 720, 60):
            draw.rectangle([sx, sy, sx + 100, sy + 50], fill=(55, 65, 75, 150), outline=(70, 80, 90, 100))

    # Items on shelves - small colored rectangles
    for sx in range(35, WIDTH, 180):
        for sy in range(385, 720, 60):
            for item in range(3):
                ix = sx + 10 + item * 30
                iy = sy + 8
                draw.rectangle([ix, iy, ix + 20, iy + 30], fill=(80 + item * 20, 90 + item * 15, 100 + item * 10, 120))

    # Floor
    _make_gradient(draw, 700, 1450, (45, 55, 50), (35, 42, 38))

    # Floor grid lines (perspective)
    for x in range(0, WIDTH, 40):
        draw.line([(x, 700), (x + int((x - WIDTH / 2) * 0.3), 1450)], fill=(55, 62, 58, 60), width=1)


def _draw_data_wires(draw):
    """Draw data cables connecting the distribution system."""
    for wire_idx in range(12):
        x_start = int(math.sin(wire_idx * 2.1) * 600 + WIDTH // 2)
        y_start = 200 + int(math.cos(wire_idx * 1.7) * 100)
        x_end = int(math.sin(wire_idx * 3.3) * 700 + WIDTH // 2)
        y_end = 600 + int(math.cos(wire_idx * 2.5) * 150)

        points = []
        for t in range(0, 31):
            frac = t / 30
            x = x_start + (x_end - x_start) * frac
            y = y_start + (y_end - y_start) * frac + math.sin(frac * 5) * 40
            points.append((int(x), int(y)))

        alpha = 40 + int(math.sin(wire_idx) * 20)
        for i in range(len(points) - 1):
            draw.line([points[i], points[i + 1]], fill=(100, 200, 255, alpha), width=1)


def _draw_glowing_dashboard(draw):
    """Draw a futuristic data dashboard in the background."""
    # Dashboard panels
    panels = [(100, 450, 350, 580), (600, 430, 950, 560), (1100, 460, 1450, 570)]

    for px1, py1, px2, py2 in panels:
        draw.rectangle([px1, py1, px2, py2], fill=(20, 30, 40, 180), outline=(80, 200, 220, 80))

        # Data lines on dashboard
        for dl in range(5):
            dly = py1 + 20 + dl * 22
            points = []
            for dx in range(px1 + 10, px2 - 10, 8):
                dy = dly + int(math.sin((dx - px1) * 0.03 + dl * 1.5) * 8)
                points.append((dx, dy))

            for i in range(len(points) - 1):
                alpha = 100 + int(math.sin(dl * 0.8) * 40)
                draw.line([points[i], points[i + 1]], fill=(80, 200, 220, alpha), width=2)

        # Glowing dots on dashboard
        for dot in range(6):
            dx = px1 + 20 + dot * ((px2 - px1 - 40) // 5)
            dy = py2 - 15
            dot_color = [(80, 220, 80), (220, 220, 80), (80, 200, 220)][dot % 3]
            draw.ellipse([dx - 4, dy - 4, dx + 4, dy + 4], fill=dot_color)


def _draw_ambient_details(draw):
    """Draw ambient details: lights, particles, atmosphere."""
    # Overhead lights
    for lx in range(100, WIDTH, 250):
        ly = 215
        # Light beam
        for i in range(30):
            fade = 1.0 - i / 30
            beam_w = int(fade * 200 + 20)
            alpha = int(fade * 25)
            draw.rectangle([lx - beam_w // 2, ly + i * 8, lx + beam_w // 2, ly + i * 8 + 6],
                           fill=(255, 240, 200, alpha))

        # Light fixture
        draw.rectangle([lx - 15, ly - 5, lx + 15, ly + 5], fill=(200, 200, 180, 150))
        draw.ellipse([lx - 8, ly - 3, lx + 8, ly + 6], fill=(255, 250, 220, 100))

    # Floating particles/dust motes
    for _ in range(150):
        px = int(math.sin(_ * 7.1) * 600 + WIDTH // 2)
        py = 400 + int(math.cos(_ * 5.3) * 800)
        size = 1 + int(math.sin(_ * 3.7) * 2)
        alpha = int(math.sin(_ * 2.3) * 50 + 60)
        draw.ellipse([px - size, py - size, px + size, py + size], fill=(200, 220, 240, alpha))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    metadata_path = Path(args.metadata)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Common Breath")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (35, 42, 38, 255))
    draw = ImageDraw.Draw(img)

    # Build the cover elements
    _draw_ceiling(draw)
    _draw_distribution_hall(draw)
    _draw_glowing_dashboard(draw)
    _draw_conveyor_system(draw)
    _draw_package_flows(draw)
    _draw_data_wires(draw)
    _draw_ambient_details(draw)

    # Title and author panel
    _draw_standard_cover_title_panel(img, title, author, model)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    img.save(args.out, "PNG")
    print(f"Cover saved to {args.out}")


# ---- Standard helper functions (do not edit below this line) ----

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    main()
