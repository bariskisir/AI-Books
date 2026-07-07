#!/usr/bin/env python3
"""Cover: The Unwritten City — Snow-covered stone bridge over dark river, clock tower glowing amber through falling snow."""

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


def _draw_gradient(draw, y_start, y_end, color_top, color_bot):
    for y in range(y_start, y_end):
        ratio = (y - y_start) / max(1, y_end - y_start - 1)
        r = int(color_top[0] + (color_bot[0] - color_top[0]) * ratio)
        g = int(color_top[1] + (color_bot[1] - color_top[1]) * ratio)
        b = int(color_top[2] + (color_bot[2] - color_top[2]) * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=str, default="")
    parser.add_argument("--out", type=str, default="")
    args = parser.parse_args()

    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    rng = random.Random("unwritten-city")

    _draw_gradient(draw, 0, 900, (20, 25, 45), (45, 55, 75))

    for _ in range(120):
        x = rng.randint(0, WIDTH)
        y = rng.randint(0, 700)
        r = rng.randint(1, 3)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(200, 210, 235, rng.randint(60, 180)))

    river_y = 1550
    for y in range(river_y, river_y + 180):
        t = (y - river_y) / 180
        r = int(10 + 8 * t)
        g = int(12 + 10 * t)
        b = int(30 + 18 * t)
        wave = int(5 * math.sin(y / 25 + 3))
        draw.line([(0, y + wave), (WIDTH, y)], fill=(r, g, b))

    bridge_arch_top = 950
    bridge_road = 1320
    for x in range(WIDTH):
        dx = abs(x - WIDTH // 2)
        if dx < 680:
            arch_y = bridge_arch_top + int(450 * math.sin(dx * math.pi / 1360))
            draw.line([(x, arch_y), (x, bridge_road)], fill=(170, 175, 180, 210))

    for x in range(0, WIDTH, 45):
        dx = abs(x - WIDTH // 2)
        if dx < 660:
            draw.rectangle([x - 3, bridge_road - 25, x + 3, bridge_road], fill=(150, 155, 160))
            draw.ellipse([x - 7, bridge_road - 38, x + 7, bridge_road - 22], fill=(180, 185, 190))

    snow_cover = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    sd = ImageDraw.Draw(snow_cover)
    for _ in range(60):
        sx = rng.randint(0, WIDTH)
        sy = bridge_road - rng.randint(10, 50)
        sd.ellipse([sx - 15, sy - 6, sx + 15, sy + 6], fill=(230, 235, 240, rng.randint(60, 120)))
    for _ in range(30):
        sx = rng.randint(0, WIDTH)
        sy = bridge_arch_top + rng.randint(50, 400)
        for dx in range(-1, 2):
            sd.ellipse([sx + dx * 8 - 10, sy - 4, sx + dx * 8 + 10, sy + 4], fill=(220, 228, 235, rng.randint(40, 80)))
    snow_cover = snow_cover.filter(ImageFilter.GaussianBlur(4))
    image = Image.alpha_composite(image, snow_cover)

    tower_cx = WIDTH // 2
    tower_cy = 600
    draw.rectangle([tower_cx - 35, 420, tower_cx + 35, tower_cy], fill=(55, 50, 60))
    draw.rectangle([tower_cx - 42, 400, tower_cx + 42, 420], fill=(50, 45, 55))
    draw.polygon([(tower_cx - 45, 400), (tower_cx, 330), (tower_cx + 45, 400)], fill=(45, 40, 50))

    for i in range(4):
        rad = 50 + i * 25
        alpha = max(8, 70 - i * 15)
        draw.ellipse([tower_cx - rad, tower_cy - rad, tower_cx + rad, tower_cy + rad], fill=(255, 190, 70, alpha))
    draw.ellipse([tower_cx - 18, tower_cy - 18, tower_cx + 18, tower_cy + 18], fill=(255, 210, 90, 200))
    draw.rectangle([tower_cx - 12, tower_cy - 12, tower_cx + 12, tower_cy + 12], fill=(255, 220, 100))

    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([tower_cx - 220, tower_cy - 170, tower_cx + 220, tower_cy + 170], fill=(255, 190, 70, 25))
    gd.ellipse([tower_cx - 380, tower_cy - 280, tower_cx + 380, tower_cy + 280], fill=(255, 170, 50, 8))
    glow = glow.filter(ImageFilter.GaussianBlur(40))
    image = Image.alpha_composite(image, glow)
    draw = ImageDraw.Draw(image, "RGBA")

    for _ in range(500):
        x = rng.randint(0, WIDTH)
        y = rng.randint(0, 1800)
        r = rng.randint(1, 4)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(230, 238, 248, rng.randint(80, 230)))

    fog = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog)
    for _ in range(25):
        fx = rng.randint(0, WIDTH)
        fy = rng.randint(400, 1500)
        fr = rng.randint(200, 700)
        fd.ellipse([fx - fr, fy - fr // 3, fx + fr, fy + fr // 3], fill=(200, 210, 220, rng.randint(5, 12)))
    fog = fog.filter(ImageFilter.GaussianBlur(35))
    image = Image.alpha_composite(image, fog)
    draw = ImageDraw.Draw(image, "RGBA")

    metadata = {}
    if args.metadata:
        try:
            with open(args.metadata, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        except Exception:
            pass

    model = metadata.get("model", "")
    title = metadata.get("title", "The Unwritten City")
    author = metadata.get("author", "Barış Kısır")

    _draw_standard_cover_title_panel(image, title, author, model)

    output_path = args.out or "covers/The_Unwritten_City.png"
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
