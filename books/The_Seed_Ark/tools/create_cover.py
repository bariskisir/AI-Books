#!/usr/bin/env python3
"""Cover: The Seed Ark — stone circle of moss-covered pillars under lavender sky, mist rising, oak sapling at edge."""

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


def _hex(r, g, b):
    return (r, g, b)


def _gradient(draw, w, h, top_color, bottom_color):
    for y in range(h):
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * y / h)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * y / h)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * y / h)
        draw.line([(0, y), (w, y)], fill=(r, g, b))


def _draw_starfield(draw, w, h, density, seed):
    """Draw a starfield background."""
    rng = random.Random(seed)
    for _ in range(density):
        x = rng.randint(0, w)
        y = rng.randint(0, h)
        size = rng.randint(1, 3)
        brightness = rng.randint(100, 255)
        draw.ellipse([x - size, y - size, x + size, y + size], fill=(brightness, brightness, brightness))


def _draw_cylindrical_ship(draw, cx, cy, length, radius, angle, colors, seed):
    """Draw a cylindrical generation ship at the given angle."""
    rng = random.Random(seed)
    rad = math.radians(angle)

    # Calculate endpoints
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    half_len = length // 2

    x1 = cx - int(half_len * cos_a)
    y1 = cy - int(half_len * sin_a)
    x2 = cx + int(half_len * cos_a)
    y2 = cy + int(half_len * sin_a)

    # Main cylinder body - draw as a rotated rectangle by drawing segments
    perp_rad = rad + math.pi / 2
    perp_cos = math.cos(perp_rad)
    perp_sin = math.sin(perp_rad)

    steps = max(length // 4, 20)
    for i in range(steps):
        t = i / steps
        sx = int(x1 + (x2 - x1) * t)
        sy = int(y1 + (y2 - y1) * t)
        color_variant = rng.randint(-15, 15)
        c = (
            min(255, max(0, colors[0][0] + color_variant)),
            min(255, max(0, colors[0][1] + color_variant)),
            min(255, max(0, colors[0][2] + color_variant)),
        )

        # Draw cross-section ellipse at this point
        w = radius
        h = int(radius * abs(perp_cos)) + int(radius * 0.3)
        draw.ellipse([sx - w, sy - h // 2, sx + w, sy + h // 2], fill=c, outline=(80, 140, 200, 100))

    # Hull outline - top and bottom edges
    for sign in (-1, 1):
        ox = int(perp_cos * radius * sign)
        oy = int(perp_sin * radius * sign)
        points = []
        for i in range(steps):
            t = i / steps
            sx = x1 + int((x2 - x1) * t) + ox
            sy = y1 + int((y2 - y1) * t) + oy
            points.append((sx, sy))
        for i in range(len(points) - 1):
            draw.line([points[i], points[i + 1]], fill=(100, 180, 230, 150), width=2)

    # Ring structures along the cylinder
    for i in range(5):
        t = 0.15 + i * 0.175
        rx = int(x1 + (x2 - x1) * t)
        ry = int(y1 + (y2 - y1) * t)
        ring_r = radius + 20
        draw.ellipse(
            [rx - ring_r, ry - int(ring_r * 0.3), rx + ring_r, ry + int(ring_r * 0.3)],
            outline=(120, 190, 230, 180),
            width=2,
        )

    # Glow at the aft end (engine)
    aft_x = x1
    aft_y = y1
    for r in range(60, 0, -5):
        alpha = int(30 * (1 - r / 60))
        draw.ellipse([aft_x - r, aft_y - r, aft_x + r, aft_y + r], fill=(50, 150, 255, alpha))

    # Solar panel arrays on sides
    for sign in (-1, 1):
        px = cx + int(perp_cos * (radius + 30) * sign)
        py = cy + int(perp_sin * (radius + 30) * sign)
        panel_len = length * 0.3
        p_x1 = px - int(panel_len * cos_a / 2)
        p_y1 = py - int(panel_len * sin_a / 2)
        p_x2 = px + int(panel_len * cos_a / 2)
        p_y2 = py + int(panel_len * sin_a / 2)
        draw.line([(p_x1, p_y1), (p_x2, p_y2)], fill=(60, 120, 200, 100), width=8)


def _draw_planet(draw, cx, cy, radius, colors, seed):
    """Draw a habitable planet."""
    rng = random.Random(seed)

    # Planet body
    for r in range(radius, 0, -1):
        t = 1 - r / radius
        ci = min(len(colors) - 1, int(t * (len(colors) - 1)))
        next_ci = min(len(colors) - 1, ci + 1)
        ct = (t * (len(colors) - 1)) - ci
        c = (
            int(colors[ci][0] + (colors[next_ci][0] - colors[ci][0]) * ct),
            int(colors[ci][1] + (colors[next_ci][1] - colors[ci][1]) * ct),
            int(colors[ci][2] + (colors[next_ci][2] - colors[ci][2]) * ct),
        )
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)

    # Atmosphere glow
    for r in range(radius + 20, radius, -1):
        alpha = int(40 * (1 - (r - radius) / 20))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(100, 180, 255, alpha), width=1)

    # Surface features (clouds/continents)
    for _ in range(12):
        angle = rng.uniform(0, 360)
        dist = rng.uniform(0.2, 0.8) * radius
        spot_x = cx + int(dist * math.cos(math.radians(angle)))
        spot_y = cy + int(dist * math.sin(math.radians(angle)))
        spot_r = rng.randint(10, 40)
        draw.ellipse(
            [spot_x - spot_r, spot_y - spot_r, spot_x + spot_r, spot_y + spot_r],
            fill=(30, 90, 60, 60),
        )

    # Highlight crescent
    for r in range(int(radius * 0.6), 0, -2):
        alpha = int(15 * (1 - r / (radius * 0.6)))
        draw.arc(
            [cx - radius + 20, cy - radius + 20, cx + radius - 20, cy + radius - 20],
            300,
            340,
            fill=(180, 220, 255, alpha),
            width=r // 10 + 1,
        )


def create_cover(metadata_path: str, output_path: str) -> None:
    """Create the cover image."""
    meta = {}
    if metadata_path:
        meta = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    title = meta.get("title", "The Seed Ark")
    author = meta.get("author", "Barış Kısır")
    model = meta.get("model", "")

    img = Image.new("RGB", (WIDTH, HEIGHT), (3, 5, 15))
    draw = ImageDraw.Draw(img)

    # Lavender sky gradient
    for y in range(HEIGHT):
        t = y / HEIGHT
        if t < 0.5:
            r = int(70 + 30 * t * 2)
            g = int(50 + 25 * t * 2)
            b = int(100 + 40 * t * 2)
        else:
            r = int(100 - 60 * (t - 0.5) * 2)
            g = int(75 - 50 * (t - 0.5) * 2)
            b = int(140 - 80 * (t - 0.5) * 2)
        draw.line([(0, y), (WIDTH, y)], fill=(max(0, r), max(0, g), max(0, b)))

    # Mist rising from ground
    mist = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    md = ImageDraw.Draw(mist)
    for _ in range(15):
        mx = random.randint(-100, WIDTH + 100)
        my = random.randint(1000, 1500)
        md.ellipse([mx, my, mx + random.randint(200, 500), my + random.randint(30, 80)], fill=(180, 170, 200, random.randint(15, 35)))
    mist = mist.filter(ImageFilter.GaussianBlur(25))
    img = Image.alpha_composite(img.convert("RGBA"), mist).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Stone circle - moss-covered pillars
    rng = random.Random(42)
    pillars = [
        (300, 1200), (500, 1100), (700, 1050), (900, 1080), (1100, 1120), (1300, 1180)
    ]
    for px, py in pillars:
        pw, ph = rng.randint(20, 35), rng.randint(160, 240)
        draw.rectangle([px - pw // 2, py - ph, px + pw // 2, py], fill=(70, 80, 65, 220))
        draw.rectangle([px - pw // 2 + 3, py - ph + 5, px + pw // 2 - 3, py - 2], fill=(85, 95, 78, 200))
        # Moss on top
        draw.ellipse([px - pw // 2 - 4, py - ph - 6, px + pw // 2 + 4, py - ph + 10], fill=(55, 100, 45, 180))
        draw.ellipse([px - pw // 2, py - ph - 2, px + pw // 2, py - ph + 6], fill=(70, 120, 55, 150))
        # Moss patches on sides
        for _ in range(rng.randint(2, 5)):
            mx = px - pw // 2 + rng.randint(-3, pw + 3)
            my = py - rng.randint(20, ph - 20)
            draw.ellipse([mx - 4, my - 2, mx + 4, my + 2], fill=(60, 110, 50, rng.randint(80, 160)))

    # Oak sapling at edge of stone circle
    sx, sy = 150, 1300
    # Trunk
    draw.line([(sx, sy), (sx, sy - 100)], fill=(60, 45, 30, 230), width=6)
    draw.line([(sx, sy - 60), (sx - 20, sy - 80)], fill=(60, 45, 30, 230), width=4)
    draw.line([(sx, sy - 70), (sx + 15, sy - 90)], fill=(60, 45, 30, 230), width=3)
    # Leaves
    for bx, by in [(sx, sy - 105), (sx - 25, sy - 85), (sx + 20, sy - 95)]:
        draw.ellipse([bx - 15, by - 10, bx + 15, by + 10], fill=(50, 120, 45, 200))
        draw.ellipse([bx - 8, by - 5, bx + 8, by + 5], fill=(70, 150, 60, 180))

    # Ground
    draw.polygon([(0, 1400), (WIDTH, 1350), (WIDTH, 1800), (0, 1800)], fill=(25, 35, 22, 200))

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
