#!/usr/bin/env python3
"""Cover: The Porcelain Doll — night scene, Japanese doll shop, moon, cherry blossoms, porcelain doll in kimono, night blue/cherry pink/porcelain white."""

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

ROOT = Path(__file__).resolve().parents[3]
FONTS_DIR = Path("C:/Windows/Fonts")
WIDTH, HEIGHT = 1600, 2560

def rel(path: str | Path) -> Path:
    p = Path(path)
    return ROOT / p if not p.is_absolute() else p

def lerp_color(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))

def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Porcelain Doll")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Night sky
    for y in range(HEIGHT):
        t = y / HEIGHT
        if t < 0.5:
            c = lerp_color((18, 14, 48), (38, 28, 58), t * 2)
        else:
            c = lerp_color((38, 28, 58), (14, 10, 24), (t - 0.5) * 2)
        draw.line([(0, y), (WIDTH, y)], fill=(*c, 255))

    # Moon
    mx, my = WIDTH // 2, int(HEIGHT * 0.12)
    for r in range(120, 80, -2):
        draw.ellipse([mx - r, my - r, mx + r, my + r], fill=(255, 240, 220, max(0, 35 - (r - 80) * 2)))
    draw.ellipse([mx - 80, my - 80, mx + 80, my + 80], fill=(245, 235, 215, 255))

    # Cherry blossoms framing top
    rng = random.Random(55)
    for b in range(3):
        x = (b + 1) * WIDTH // 4
        pts = [(x, 0)]
        cx, cy = x, 0
        for _ in range(8):
            cx += rng.randint(-20, 30)
            cy += rng.randint(30, 55)
            pts.append((cx, cy))
        draw.line(pts, fill=(55, 28, 18, 255), width=rng.randint(4, 7))
        for px, py in pts[2::2]:
            for _ in range(rng.randint(1, 2)):
                bx = px + rng.randint(-10, 10)
                by = py + rng.randint(-5, 10)
                br = rng.randint(5, 10)
                draw.ellipse([bx - br, by - br, bx + br, by + br], fill=(230, 180, 180, 180))
                draw.ellipse([bx - 3, by - 3, bx + 3, by + 3], fill=(200, 80, 80, 240))

    # Japanese doll shop
    st, sb = int(HEIGHT * 0.35), int(HEIGHT * 0.70)
    draw.polygon([(-100, st + 20), (WIDTH + 100, st + 20), (WIDTH + 160, st), (WIDTH // 2, st - 50), (-160, st)], fill=(48, 28, 24, 255))
    draw.rectangle([int(WIDTH * 0.12), st + 40, int(WIDTH * 0.88), sb], fill=(68, 48, 38, 255))
    # Shoji
    for i in range(4):
        sx = int(WIDTH * 0.12) + int(WIDTH * 0.76) * i // 4
        ex = int(WIDTH * 0.12) + int(WIDTH * 0.76) * (i + 1) // 4
        draw.rectangle([sx + 8, st + 50, ex - 8, sb - 10], fill=(175, 170, 155, 200))
        for gx in range(int(sx + 25), int(ex - 8), 35):
            draw.line([(gx, st + 50), (gx, sb - 10)], fill=(155, 145, 130, 255), width=2)
        for gy in range(int(st + 80), int(sb - 10), 50):
            draw.line([(sx + 8, gy), (ex - 8, gy)], fill=(155, 145, 130, 255), width=2)

    # Warm lantern glow
    for r in range(180, 30, -10):
        draw.ellipse([WIDTH // 2 - r, int(HEIGHT * 0.52) - r, WIDTH // 2 + r, int(HEIGHT * 0.52) + r], fill=(255, 200, 100, max(0, 22 - (180 - r) // 9)))

    # Porcelain doll in kimono
    doll_x, doll_y = WIDTH // 2 - 30, int(HEIGHT * 0.42)
    # Kimono body
    draw.polygon([(doll_x - 25, doll_y + 40), (doll_x - 35, doll_y + 120), (doll_x + 35, doll_y + 120), (doll_x + 25, doll_y + 40)], fill=(200, 50, 60, 230))
    draw.polygon([(doll_x - 10, doll_y + 40), (doll_x, doll_y + 10), (doll_x + 10, doll_y + 40)], fill=(220, 60, 70, 230))
    # Obi (sash)
    draw.rectangle([doll_x - 22, doll_y + 55, doll_x + 22, doll_y + 70], fill=(180, 160, 40, 230))
    # Head
    draw.ellipse([doll_x - 15, doll_y - 5, doll_x + 15, doll_y + 25], fill=(235, 225, 210, 255))
    draw.arc([doll_x - 17, doll_y - 18, doll_x + 17, doll_y + 8], 180, 360, fill=(30, 20, 15, 255), width=5)
    # Face
    draw.ellipse([doll_x - 6, doll_y + 5, doll_x - 3, doll_y + 8], fill=(40, 30, 25, 255))
    draw.ellipse([doll_x + 3, doll_y + 5, doll_x + 6, doll_y + 8], fill=(40, 30, 25, 255))
    draw.arc([doll_x - 4, doll_y + 12, doll_x + 4, doll_y + 18], 0, 180, fill=(140, 60, 50, 255), width=2)
    # Hair
    draw.arc([doll_x - 20, doll_y - 14, doll_x - 8, doll_y + 8], 240, 120, fill=(20, 15, 12, 255), width=6)
    draw.arc([doll_x + 8, doll_y - 14, doll_x + 20, doll_y + 8], 60, 300, fill=(20, 15, 12, 255), width=6)

    # Shelf with more doll faces
    draw.rectangle([int(WIDTH * 0.2), int(HEIGHT * 0.50), int(WIDTH * 0.8), int(HEIGHT * 0.50) + 6], fill=(75, 55, 42, 255))
    for i in range(4):
        dx = int(WIDTH * 0.25) + i * 130 + rng.randint(-10, 10)
        dy = int(HEIGHT * 0.50) - 40 + rng.randint(-8, 8)
        draw.ellipse([dx - 16, dy - 18, dx + 16, dy + 12], fill=(235, 225, 210, 255))
        draw.ellipse([dx - 5, dy - 3, dx - 2, dy], fill=(40, 30, 25, 255))
        draw.ellipse([dx + 2, dy - 3, dx + 5, dy], fill=(40, 30, 25, 255))
        draw.arc([dx - 4, dy + 6, dx + 4, dy + 12], 0, 180, fill=(130, 55, 45, 255), width=2)

    # Petals falling
    for _ in range(30):
        px = random.randint(0, WIDTH)
        py = random.randint(0, HEIGHT)
        draw.ellipse([px - 2, py - 3, px + 2, py + 3], fill=(230, 180, 180, random.randint(100, 200)))

    img = img.filter(ImageFilter.SMOOTH)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    metadata_path = rel(args.metadata)
    output_path = rel(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    create_cover(metadata_path, output_path)


if __name__ == "__main__":
    main()