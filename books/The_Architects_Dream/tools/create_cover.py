#!/usr/bin/env python3
"""Generate a 1600x2560 cover for The Architect's Dream."""

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


def _hex(r, g, b):
    return (r, g, b)


def _gradient(draw, w, h, top_color, bottom_color):
    for y in range(h):
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * y / h)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * y / h)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * y / h)
        draw.line([(0, y), (w, y)], fill=(r, g, b))


def _draw_crystal_dome(draw, cx, cy, radius, color, seed):
    """Draw a crystalline dome structure at center (cx, cy)."""
    rng = random.Random(seed)

    # Draw the dome silhouette
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                 outline=color, width=3)

    # Fill with gradient transparency
    for r in range(radius, 0, -4):
        alpha = max(10, int(60 * (1 - r / radius)))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                     fill=(color[0], color[1], color[2], alpha))

    # Geometric facet lines inside the dome
    for i in range(12):
        angle = i * 30 + rng.randint(0, 5)
        rad = math.radians(angle)
        x1 = cx + int(radius * 0.2 * math.cos(rad))
        y1 = cy + int(radius * 0.2 * math.sin(rad))
        x2 = cx + int(radius * 0.95 * math.cos(rad))
        y2 = cy + int(radius * 0.95 * math.sin(rad))
        draw.line([(x1, y1), (x2, y2)], fill=(color[0] // 2, color[1] // 2, color[2] // 2, 80), width=1)

    # Concentric rings
    for r in range(int(radius * 0.3), int(radius * 0.9), int(radius * 0.1)):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                     outline=(color[0] - 30, color[1] - 30, color[2] - 30, 60), width=1)


def _draw_crystalline_tower(draw, x, y_base, height, width, colors, seed):
    """Draw a crystalline tower at position x, rising from y_base."""
    rng = random.Random(seed)
    segments = 8
    seg_h = height / segments

    for i in range(segments):
        seg_y = y_base - (i + 1) * seg_h
        seg_w = width * (1.0 - i * 0.06)
        color = colors[i % len(colors)]
        x0 = x - seg_w / 2
        x1 = x + seg_w / 2
        draw.rectangle([x0, seg_y, x1, seg_y + seg_h + 1], fill=color)

    # Top spire
    top_y = y_base - height
    spire_h = seg_h
    draw.polygon([(x - width * 0.12, top_y), (x, top_y - spire_h), (x + width * 0.12, top_y)],
                 fill=colors[-1])

    # Glow line up center
    draw.line([(x, y_base), (x, top_y - spire_h)], fill=(180, 220, 255, 150), width=2)


def _draw_hairline_crack(draw, cx, cy, radius, extent):
    """Draw a hairline crack through the central dome."""
    # Main crack line - arcs through the dome
    points = []
    steps = 20
    for i in range(steps + 1):
        t = i / steps
        angle = -30 + t * 60
        rad = math.radians(angle)
        # Crack deviates randomly from perfect arc
        jitter = random.randint(-8, 8) * (1 + math.sin(t * 15) * 0.5)
        r = radius * (0.3 + t * extent) + jitter
        x = cx + int(r * math.cos(rad))
        y = cy - radius * 0.5 + int(r * math.sin(rad)) + t * radius * 0.8
        points.append((x, y))

    # Draw crack segments
    for i in range(len(points) - 1):
        # Varying width and brightness
        w = 1 if random.random() > 0.3 else 2
        brightness = 180 + random.randint(0, 75)
        draw.line([points[i], points[i + 1]], fill=(brightness, brightness, brightness, 200), width=w)

    # Branching micro-cracks
    for _ in range(8):
        idx = random.randint(1, len(points) - 2)
        px, py = points[idx]
        angle = random.uniform(30, 150)
        length = random.randint(10, 40)
        ex = px + int(length * math.cos(math.radians(angle)))
        ey = py + int(length * math.sin(math.radians(angle)))
        draw.line([(px, py), (ex, ey)], fill=(180, 180, 180, 150), width=1)

    # Glowing breach point at crack center
    mid_idx = len(points) // 2
    mx, my = points[mid_idx]
    for r in range(12, 0, -2):
        alpha = int(30 * (1 - r / 12))
        draw.ellipse([mx - r, my - r, mx + r, my + r], fill=(255, 220, 100, alpha))


def create_cover(metadata_path: str, output_path: str) -> None:
    """Create the cover image."""
    meta = {}
    if metadata_path:
        meta = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    title = meta.get("title", "The Architect's Dream")
    author = meta.get("author", "Barış Kısır")
    model = meta.get("model", "")

    img = Image.new("RGB", (WIDTH, HEIGHT), (10, 14, 28))
    draw = ImageDraw.Draw(img)

    # Gradient background - sunset utopia
    _gradient(draw, WIDTH, HEIGHT, (15, 12, 35), (60, 50, 80))

    # Sky glow
    for i in range(2):
        cx = WIDTH // 2 + random.randint(-100, 100)
        cy = 400 + i * 300
        for r in range(400, 0, -8):
            alpha = max(0, int(5 * (1 - r / 400)))
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(100, 130, 200, alpha))

    # Background towers (distant skyline)
    tower_colors = [
        (40, 80, 130, 150),
        (50, 100, 150, 150),
        (60, 120, 170, 150),
        (50, 110, 160, 160),
        (70, 140, 190, 160),
    ]

    for i in range(12):
        x = 50 + i * 130 + random.randint(-20, 20)
        y_base = 1600 + random.randint(-50, 50)
        height = 300 + random.randint(100, 400)
        width = 40 + random.randint(10, 30)
        _draw_crystalline_tower(draw, x, y_base, height, width, tower_colors, i + 100)

    # Foreground towers
    for i in range(6):
        x = 80 + i * 280 + random.randint(-15, 15)
        y_base = 1500 + random.randint(-30, 30)
        height = 500 + random.randint(100, 250)
        width = 50 + random.randint(15, 35)
        _draw_crystalline_tower(draw, x, y_base, height, width, tower_colors, i)

    # Central grand dome
    dome_cx, dome_cy, dome_r = WIDTH // 2, 1350, 420
    _draw_crystal_dome(draw, dome_cx, dome_cy, dome_r, (80, 150, 210, 180), 42)

    # Hairline crack through the dome
    _draw_hairline_crack(draw, dome_cx, dome_cy, dome_r, 0.9)

    # Glow emanating from the crack
    crack_glow_cx = dome_cx + 30
    crack_glow_cy = dome_cy + 50
    for r in range(60, 0, -3):
        alpha = int(15 * (1 - r / 60))
        draw.ellipse([crack_glow_cx - r, crack_glow_cy - r, crack_glow_cx + r, crack_glow_cy + r],
                     fill=(255, 200, 80, alpha))

    # Ground reflection glow at base
    for r in range(200, 0, -5):
        alpha = int(8 * (1 - r / 200))
        draw.ellipse([dome_cx - r, 1520 - r // 2, dome_cx + r, 1520 + r // 2],
                     fill=(100, 180, 255, alpha))

    # Draw standard title panel
    _draw_standard_cover_title_panel(img, title, author, model)

    img.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")


# ---- Standard helper functions ----



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    create_cover(args.metadata, args.out)


if __name__ == "__main__":
    main()
