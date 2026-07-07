#!/usr/bin/env python3
"""Cover: The Piano Tuner — dark Edinburgh night, grand piano silhouette in warm-lit parlor, gas lamps and rain, Edinburgh gray/piano black/parlor gold."""

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

def lerp_color(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Piano Tuner")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Edinburgh night gradient
    for y in range(HEIGHT):
        if y < HEIGHT * 0.45:
            t = y / (HEIGHT * 0.45)
            c = lerp_color((10, 10, 18), (38, 30, 28), t)
        elif y < HEIGHT * 0.7:
            t = (y - HEIGHT * 0.45) / (HEIGHT * 0.25)
            c = lerp_color((38, 30, 28), (72, 58, 45), t)
        else:
            t = (y - HEIGHT * 0.7) / (HEIGHT * 0.3)
            c = lerp_color((72, 58, 45), (48, 40, 32), t)
        draw.line([(0, y), (WIDTH, y)], fill=(*c, 255))

    # Edinburgh skyline
    rng = random.Random(5)
    by = int(HEIGHT * 0.4)
    x = 0
    while x < WIDTH:
        h = rng.randint(60, 160)
        w = rng.randint(70, 200)
        draw.polygon([(x, by), (x + w // 2, by - h), (x + w, by)], fill=(6, 6, 8, 255))
        x += w - rng.randint(10, 30)

    # Rain
    for _ in range(180):
        rx = random.randint(0, WIDTH)
        ry = random.randint(0, HEIGHT)
        rl = random.randint(15, 40)
        draw.line((rx, ry, rx - 1, ry + rl), fill=(160, 165, 180, random.randint(20, 50)), width=1)

    # Gas lamp (left)
    lx, ly = int(WIDTH * 0.15), int(HEIGHT * 0.38)
    draw.rectangle([lx - 3, ly - 150, lx + 3, ly], fill=(25, 22, 18, 255))
    draw.rectangle([lx - 14, ly - 190, lx + 14, ly - 150], fill=(35, 30, 25, 255))
    for r in range(50, 5, -5):
        draw.ellipse([lx - r, ly - 180 - r, lx + r, ly - 180 + r], fill=(255, 200, 100, max(0, 100 - r * 2)))
    draw.rectangle([lx - 10, ly - 182, lx + 10, ly - 158], fill=(255, 230, 150, 200))

    # Gas lamp (right)
    rlx, rly = int(WIDTH * 0.85), int(HEIGHT * 0.38)
    draw.rectangle([rlx - 3, rly - 150, rlx + 3, rly], fill=(25, 22, 18, 255))
    draw.rectangle([rlx - 14, rly - 190, rlx + 14, rly - 150], fill=(35, 30, 25, 255))
    for r in range(50, 5, -5):
        draw.ellipse([rlx - r, rly - 180 - r, rlx + r, rly - 180 + r], fill=(255, 200, 100, max(0, 100 - r * 2)))
    draw.rectangle([rlx - 10, rly - 182, rlx + 10, rly - 158], fill=(255, 230, 150, 200))

    # Warm-lit parlor window
    wx, wy = WIDTH // 2 + 150, int(HEIGHT * 0.38) - 180
    draw.rectangle([wx - 80, wy, wx + 80, wy + 240], fill=(60, 50, 38, 120))
    draw.rectangle([wx - 70, wy + 10, wx + 70, wy + 230], fill=(255, 210, 120, 180))
    draw.line((wx, wy, wx, wy + 240), fill=(35, 30, 25, 255), width=4)
    draw.line((wx - 80, wy + 120, wx + 80, wy + 120), fill=(35, 30, 25, 255), width=4)
    draw.rectangle([wx - 80, wy, wx + 80, wy + 240], outline=(28, 24, 20, 255), width=4)

    # Grand piano silhouette
    px, py = wx, wy + 150
    draw.ellipse([px - 120, py - 80, px + 120, py + 80], fill=(8, 6, 5, 255))
    draw.polygon([(px, py - 80), (px + 90, py - 60), (px + 120, py)], fill=(12, 10, 8, 255))
    draw.rectangle([px - 55, py + 60, px + 55, py + 80], fill=(195, 190, 180, 255))
    for i in range(14):
        kx = px - 50 + int(i * 100 / 14)
        draw.line([(kx, py + 60), (kx, py + 80)], fill=(175, 170, 160, 255), width=1)

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