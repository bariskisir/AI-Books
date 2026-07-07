#!/usr/bin/env python3
"""Cover: The Open Gate — dawn landscape with rolling green hills, winding path to shimmering ethereal gate."""

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
    """Draw a vertical gradient from color1 to color2 between y1 and y2."""
    for y in range(y1, y2):
        ratio = (y - y1) / max(y2 - y1 - 1, 1)
        r = int(color1[0] + (color2[0] - color1[0]) * ratio)
        g = int(color1[1] + (color2[1] - color1[1]) * ratio)
        b = int(color1[2] + (color2[2] - color1[2]) * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def _draw_landscape(draw):
    """Draw a vast open landscape with rolling hills and distant horizon."""
    # Sky gradient - from pale dawn blue to warm horizon
    _make_gradient(draw, 0, 900, (180, 210, 230), (230, 195, 160))
    # Upper sky - deeper blue
    _make_gradient(draw, 0, 600, (100, 140, 180), (180, 210, 230))

    # Distant hills
    for i in range(5):
        offset_y = 820 + i * 15
        offset_x = i * 60
        amplitude = 60 + i * 10
        points = []
        for x in range(0, WIDTH + 2, 4):
            y = offset_y + int(math.sin((x + offset_x) * 0.002) * amplitude * 0.5)
            y += int(math.sin((x + offset_x) * 0.005) * amplitude * 0.25)
            y += int(math.sin((x + offset_x) * 0.01) * amplitude * 0.1)
            points.append((x, y))
        hill_color = (80 + i * 15, 110 + i * 10, 70 + i * 5)
        draw.polygon([(0, HEIGHT)] + points + [(WIDTH, HEIGHT)], fill=hill_color)

    # Mid-ground plains
    _make_gradient(draw, 900, 1300, (100, 130, 80), (120, 150, 90))

    # Rolling plains with grass texture
    for x in range(0, WIDTH, 6):
        h = int(math.sin(x * 0.008) * 30 + math.sin(x * 0.015) * 15 + 960)
        draw.line([(x, h), (x, h + 300)], fill=(110 + int(math.sin(x * 0.01) * 10), 140 + int(math.sin(x * 0.005) * 10), 80))

    # Foreground ground
    _make_gradient(draw, 1300, 1765, (100, 120, 70), (70, 90, 50))

    # Some grass tufts in foreground
    for _ in range(200):
        x = int(_get_random() * WIDTH)
        y = 1400 + int(_get_random() * 350)
        h = 10 + int(_get_random() * 30)
        for i in range(3):
            draw.line([(x, y), (x + int(_get_random() * 6 - 3), y - h + int(_get_random() * 10))],
                      fill=(60 + int(_get_random() * 40), 100 + int(_get_random() * 40), 40 + int(_get_random() * 30)),
                      width=1)


def _get_random(seed=0):
    """Simple deterministic pseudo-random."""
    import hashlib
    seed = hashlib.md5(str(seed).encode()).hexdigest()
    return int(seed[:8], 16) / 0xFFFFFFFF


def _draw_shimmering_gate(draw):
    """Draw a mysterious shimmering gate on the horizon."""
    cx, cy = WIDTH // 2 + 60, 780

    # Glow behind the gate
    for radius in range(180, 0, -6):
        alpha = max(0, 180 - radius)
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                     fill=(200, 240, 255, alpha // 4))

    # Gate pillars
    pillar_w = 18
    pillar_h = 400
    # Left pillar
    draw.rectangle([cx - 80 - pillar_w, cy - pillar_h // 2, cx - 80, cy + pillar_h // 2],
                   fill=(180, 220, 240, 180))
    # Right pillar
    draw.rectangle([cx + 80, cy - pillar_h // 2, cx + 80 + pillar_w, cy + pillar_h // 2],
                   fill=(180, 220, 240, 180))

    # Arch
    arch_points = []
    for angle in range(0, 181, 2):
        rad = math.radians(angle)
        ax = cx + math.cos(rad) * 120
        ay = cy - pillar_h // 2 + math.sin(rad) * (-120)
        arch_points.append((ax, ay))
    draw.line(arch_points, fill=(180, 220, 240, 180), width=14)

    # Inner arch (shimmering)
    inner_arch = []
    for angle in range(0, 181, 2):
        rad = math.radians(angle)
        ax = cx + math.cos(rad) * 105
        ay = cy - pillar_h // 2 + math.sin(rad) * (-105)
        inner_arch.append((ax, ay))
    draw.line(inner_arch, fill=(140, 200, 240, 120), width=6)

    # Shimmer particles
    for i in range(120):
        px = cx + int((_get_random(i * 3 + 1) - 0.5) * 260)
        py = cy + int((_get_random(i * 3 + 2) - 0.5) * 260)
        size = int(_get_random(i * 3 + 3) * 4) + 1
        alpha = int(_get_random(i * 3 + 4) * 200) + 55
        draw.ellipse([px - size, py - size, px + size, py + size],
                     fill=(200, 240, 255, alpha))

    # Light beam from the gate
    for i in range(30):
        y = cy - 200 + i * 8
        fade = max(0, 1.0 - i / 30)
        beam_width = int(fade * 300 + 20)
        alpha = int(fade * 30)
        draw.rectangle([cx - beam_width // 2, y, cx + beam_width // 2, y + 4],
                       fill=(220, 245, 255, alpha))

    # Gate floor reflection
    for i in range(40):
        y = cy + pillar_h // 2 + i * 10
        fade = max(0, 1.0 - i / 40)
        beam_width = int(fade * 150 + 10)
        alpha = int(fade * 20)
        draw.rectangle([cx - beam_width // 2, y, cx + beam_width // 2, y + 4],
                       fill=(180, 220, 240, alpha))


def _draw_path(draw):
    """Draw a winding path leading toward the gate."""
    points = []
    for t in range(0, 101):
        frac = t / 100.0
        x = WIDTH // 2 + 60 + int(math.sin(frac * 6) * 80 * frac)
        y = 1765 + int(frac * -900)
        points.append((x, y))

    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        w = max(4, int(48 * (1 - i / len(points))))
        draw.line([(x1, y1), (x2, y2)], fill=(160, 180, 140, 120), width=w)


def _draw_sky_details(draw):
    """Draw clouds and birds in the sky."""
    # Clouds - soft white shapes
    for cloud_idx in range(6):
        cx = int(_get_random(cloud_idx * 7 + 1) * WIDTH)
        cy = 100 + int(_get_random(cloud_idx * 7 + 2) * 500)
        size = 60 + int(_get_random(cloud_idx * 7 + 3) * 120)
        alpha = int(_get_random(cloud_idx * 7 + 4) * 80) + 30
        for i in range(8):
            ox = int(math.sin(i * 1.2) * size * 0.5)
            oy = int(math.cos(i * 1.8) * size * 0.2)
            r = int(size * (0.3 + _get_random(i * 13) * 0.4))
            draw.ellipse([cx + ox - r, cy + oy - r, cx + ox + r, cy + oy + r],
                         fill=(255, 255, 255, alpha))

    # Birds
    for bird_idx in range(8):
        bx = 100 + int(_get_random(bird_idx * 11 + 1) * (WIDTH - 200))
        by = 150 + int(_get_random(bird_idx * 11 + 2) * 400)
        size = 6 + int(_get_random(bird_idx * 11 + 3) * 8)
        # Simple V shape
        draw.line([(bx - size, by), (bx, by - size)], fill=(60, 60, 80, 150), width=2)
        draw.line([(bx, by - size), (bx + size, by)], fill=(60, 60, 80, 150), width=2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    metadata_path = Path(args.metadata)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Open Gate")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (70, 90, 50, 255))
    draw = ImageDraw.Draw(img)

    # Dawn landscape with rolling green hills
    _draw_landscape(draw)
    # Sky with clouds and birds
    _draw_sky_details(draw)
    # Winding path leading toward gate
    _draw_path(draw)
    # Shimmering ethereal gate on horizon
    _draw_shimmering_gate(draw)

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
