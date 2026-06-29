#!/usr/bin/env python3
"""Generate a project-local raster cover for The Fig Collector."""

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
PALETTE = [tuple(c) for c in [[18, 24, 14], [48, 40, 22], [130, 92, 38], [212, 178, 108]]]
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

    # Warm Mediterranean sky gradient — golden hour
    _gradient(draw, (62, 48, 28), (130, 102, 58))
    for y in range(400, 1100, 4):
        t = (y - 400) / 700.0
        alpha = int(35 * (1 - t))
        if alpha > 0:
            draw.line((0, y, WIDTH, y), fill=(235, 200, 130, alpha), width=4)

    # Sun glow
    sun_x, sun_y = 800, 480
    for r in range(300, 0, -5):
        a = int(50 * (r / 300))
        draw.ellipse((sun_x - r, sun_y - r, sun_x + r, sun_y + r), fill=(255, 225, 150, max(a, 0)))

    # Distant hills / mountains
    for x, peaks in [(0, [(0, 900), (300, 820), (600, 860), (900, 840), (1200, 870), (1600, 850)])]:
        draw.polygon([(0, 1100)] + peaks + [(1600, 1100)], fill=(72, 60, 38, 230))

    # Mediterranean Sea
    for y in range(1100, 1300):
        a = int(70 * (1 - (y - 1100) / 200.0))
        ripple = int(4 * math.sin(y * 0.3 + rng.random() * 2))
        draw.line((0, y + ripple, WIDTH, y + ripple), fill=(28, 55, 68, max(a, 5)), width=2)

    # Terracotta soil / foreground
    draw.rectangle((0, 1300, WIDTH, 1600), fill=(82, 50, 24, 230))
    # Texture lines
    for _ in range(30):
        x = rng.randint(0, WIDTH)
        y = rng.randint(1300, 1600)
        draw.line((x, y, x + rng.randint(-60, 60), y + 4), fill=(110, 72, 35, 80), width=1)

    # Fig tree trunk in center-left
    trunk_x, trunk_y = 480, 700
    draw.rectangle((trunk_x - 18, trunk_y, trunk_x + 18, 1500), fill=(55, 35, 18, 240))
    # Branches
    for bx, by, bw, bh, ba in [(trunk_x - 40, 720, 200, 16, 40), (trunk_x + 20, 780, 180, 14, -35), (trunk_x - 30, 850, 160, 12, 25), (trunk_x + 10, 920, 230, 11, -30)]:
        draw.ellipse((bx - bw//2, by, bx + bw//2, by + bh), fill=(55, 35, 18, 230))

    # Fig leaves on the tree
    for _ in range(50):
        lx = trunk_x + rng.randint(-200, 250)
        ly = rng.randint(680, 1050)
        ls = rng.randint(25, 60)
        la = rng.random() * 2 * math.pi
        shade = rng.randint(70, 160)
        g = rng.randint(80, 150)
        _draw_fig_leaf(draw, lx, ly, ls, la, (30, shade, g), rng.randint(80, 180))

    # Fig fruits visible among leaves
    for _ in range(20):
        fx = trunk_x + rng.randint(-180, 230)
        fy = rng.randint(720, 1000)
        fr = rng.randint(12, 22)
        color_variant = rng.choice([(140, 60, 80), (100, 50, 60), (90, 70, 35)])
        draw.ellipse((fx - fr, fy - fr, fx + fr, fy + fr), fill=(*color_variant, 200))
        draw.ellipse((fx - fr//2, fy - fr//2, fx + fr//2, fy + fr//2), fill=(*color_variant, 140))

    # Second smaller fig tree on the right
    tx2 = 1200
    draw.rectangle((tx2 - 12, 850, tx2 + 12, 1450), fill=(48, 32, 16, 220))
    for _ in range(30):
        lx = tx2 + rng.randint(-140, 160)
        ly = rng.randint(830, 1100)
        ls = rng.randint(20, 50)
        la = rng.random() * 2 * math.pi
        _draw_fig_leaf(draw, lx, ly, ls, la, (28, rng.randint(70, 140), rng.randint(70, 130)), rng.randint(70, 160))

    # Fallen figs on the ground
    for _ in range(10):
        gx = rng.randint(100, 1500)
        gy = rng.randint(1350, 1550)
        gr = rng.randint(8, 15)
        draw.ellipse((gx - gr, gy - gr//2, gx + gr, gy + gr//2), fill=(120, 55, 65, 180))

    # Large fig leaf in foreground for detail
    _draw_fig_leaf(draw, 250, 1480, 90, math.pi * 0.3, (42, 130, 60), 210)
    _draw_fig_leaf(draw, 1350, 1450, 75, math.pi * 0.7, (48, 125, 55), 200)

    # Crossed fig — halved fruit showing interior
    cx, cy = 1050, 1420
    draw.ellipse((cx - 35, cy - 25, cx + 35, cy + 25), fill=(110, 45, 60, 220))
    draw.ellipse((cx - 20, cy - 18, cx + 20, cy + 18), fill=(150, 120, 80, 200))
    draw.ellipse((cx - 8, cy - 12, cx + 8, cy + 12), fill=(180, 60, 70, 190))

    # Location label
    _label(draw, "MEDITERRANEAN", 800, 1520, 40, (225, 195, 140, 170))

    # Bottom gradient before title panel
    draw.rectangle((0, 1600, WIDTH, 1765), fill=(12, 10, 6, 70))


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
