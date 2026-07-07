#!/usr/bin/env python3
"""Cover: The Fig Collector — Fig leaf specimen on archival paper, sepia tones, Aegean coastline watermark, cream/sepia/dry brown."""

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
TITLE = "The Fig Collector"
PALETTE = [tuple(c) for c in [[55, 48, 35], [85, 72, 50], [140, 120, 80], [210, 190, 150]]]
SEED = 1938


def _gradient(draw, top, bottom):
    for y in range(HEIGHT):
        t = y / max(1, HEIGHT - 1)
        draw.line((0, y, WIDTH, y), fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))


def _label(draw, text, cx, y, size, fill):
    font = _standard_cover_font("arialbd.ttf", size)
    box = draw.textbbox((0, 0), text, font=font)
    draw.text((cx - (box[2] - box[0]) // 2, y), text, font=font, fill=fill)


def _draw_fig_leaf(draw, cx, cy, size, angle, color, alpha):
    """Draw a five-lobed fig leaf shape."""
    points = []
    num_points = 40
    for i in range(num_points):
        a = angle + (i / num_points) * 2 * math.pi
        r = size * (1.0 + 0.3 * math.sin(3 * (i / num_points) * 2 * math.pi) + 0.15 * math.sin(5 * (i / num_points) * 2 * math.pi))
        x = cx + r * math.cos(a)
        y = cy + r * math.sin(a) * 0.7
        points.append((x, y))
    if len(points) >= 3:
        draw.polygon(points, fill=(*color[:3], alpha))


def _draw_scene(draw, image):
    rng = random.Random(SEED)

    # Archival paper background — cream/sepia
    _gradient(draw, (220, 205, 180), (195, 178, 150))

    # Sepia border — darker frame
    draw.rectangle((20, 20, WIDTH - 20, HEIGHT - 20), outline=(140, 120, 90, 150), width=8)
    draw.rectangle((35, 35, WIDTH - 35, HEIGHT - 35), outline=(160, 145, 120, 80), width=2)

    # Aegean coastline watermark — faint
    watermark = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    wd = ImageDraw.Draw(watermark)
    # Coastline silhouette
    coast_pts = []
    for i in range(30):
        t = i / 30
        x = t * WIDTH
        y = 1200 + 200 * math.sin(t * 4 + 0.5) + 100 * math.sin(t * 7 + 1.2)
        coast_pts.append((x, y))
    coast_pts.append((WIDTH, HEIGHT))
    coast_pts.append((0, HEIGHT))
    wd.polygon(coast_pts, fill=(180, 170, 145, 40))

    # Small islands
    for cx, cy, rx, ry in [(300, 800, 120, 60), (1200, 750, 80, 40), (800, 820, 60, 30)]:
        wd.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=(170, 160, 135, 30))

    # Wave lines
    for wy in range(900, 1300, 20):
        wx = rng.randint(0, WIDTH)
        wd.line((wx, wy, wx + 100, wy - 5), fill=(175, 165, 140, 25), width=1)

    draw.bitmap((0, 0), watermark, fill=None)

    # Pressed fig leaf specimen — center focal point
    # Stem
    draw.line((800, 600, 800, 680), fill=(100, 80, 50, 200), width=3)

    # Leaf body — five-lobed fig leaf shape
    leaf_pts = []
    for i in range(50):
        a = i / 50 * 2 * math.pi
        r = 140 * (1.0 + 0.3 * math.sin(3 * a) + 0.12 * math.sin(5 * a))
        x = 800 + r * math.cos(a)
        y = 700 + r * math.sin(a) * 0.75
        leaf_pts.append((x, y))
    draw.polygon(leaf_pts, fill=(160, 140, 105, 200), outline=(130, 110, 80, 220), width=2)

    # Leaf veins
    draw.line((800, 700, 800, 580), fill=(120, 100, 75, 180), width=2)
    for vein_angle in [-0.4, -0.2, 0.2, 0.4]:
        for d in range(20, 100, 15):
            vx = 800 + d * math.sin(vein_angle)
            vy = 700 - d * 0.8
            draw.line((800, 700 - d * 0.8, vx, vy + 15), fill=(130, 110, 80, 120), width=1)

    # Specimen label — botanical style
    _label(draw, "FICUS CARICA", 800, 900, 36, (100, 85, 60, 200))
    _label(draw, "Fig Leaf — Pressed Specimen", 800, 940, 24, (130, 115, 90, 160))

    # Dried fig halves in the corner
    for fx, fy, fa in [(150, 1300, 0), (280, 1340, 0.5), (1300, 1280, 1.2)]:
        draw.ellipse((fx - 40, fy - 30, fx + 40, fy + 30), fill=(110, 75, 50, 200), outline=(90, 60, 40, 220), width=2)
        draw.ellipse((fx - 25, fy - 20, fx + 25, fy + 20), fill=(150, 110, 70, 180))
        for s in range(30):
            sx = fx + rng.randint(-20, 20)
            sy = fy + rng.randint(-15, 15)
            draw.point((sx, sy), fill=(180, 140, 80, rng.randint(100, 200)))

    # Archival notes — handwritten style text
    _label(draw, "Collected: Summer 1927", 800, 1050, 22, (140, 120, 90, 140))
    _label(draw, "Locality: Aegean Coast, Izmir", 800, 1085, 22, (140, 120, 90, 140))

    # Age spots / foxing on paper
    for _ in range(40):
        sx = rng.randint(30, WIDTH - 30)
        sy = rng.randint(30, HEIGHT - 30)
        sr = rng.randint(2, 8)
        sa = rng.randint(20, 60)
        draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=(150, 130, 100, sa))

    # Bottom fade
    draw.rectangle((0, 1600, WIDTH, 1765), fill=(180, 165, 140, 60))


def create_cover(metadata_path, out_path):
    metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    title = metadata.get("title", TITLE)
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")
    image = Image.new("RGB", (WIDTH, HEIGHT), PALETTE[0])
    draw = ImageDraw.Draw(image, "RGBA")
    _draw_scene(draw, image)
    _draw_standard_cover_title_panel(image, title, author, metadata.get("model", ""))
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    image.save(out_path)



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    create_cover(args.metadata, args.out)


if __name__ == "__main__":
    main()
