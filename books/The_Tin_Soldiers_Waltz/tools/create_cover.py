#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Tin Soldier's Waltz."""

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
TITLE_PANEL_TOP = 1920


def rel(path: str | Path) -> Path:
    p = Path(path)
    return ROOT / p if not p.is_absolute() else p


def lerp_color(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def draw_gradient(draw, width, height):
    """Deep winter-blue night, warming toward a lamplit gold near the windowsill."""
    for y in range(height):
        f = y / height
        if f < 0.55:
            t = f / 0.55
            c = lerp_color((14, 22, 46), (28, 40, 74), t)
        elif f < 0.74:
            t = (f - 0.55) / 0.19
            c = lerp_color((28, 40, 74), (96, 84, 70), t)
        else:
            t = (f - 0.74) / 0.26
            c = lerp_color((150, 116, 60), (60, 44, 30), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_window_glow(draw, width, height):
    """A warm toyshop window glowing behind the soldier."""
    wx0, wy0, wx1, wy1 = 360, 360, width - 360, 1300
    # outer glow halo
    for i in range(40, 0, -1):
        a = int(2.2 * i)
        draw.rectangle([wx0 - i * 4, wy0 - i * 4, wx1 + i * 4, wy1 + i * 4],
                       outline=(240, 200, 120, max(0, a // 3)), width=2)
    # window pane warm light
    draw.rectangle([wx0, wy0, wx1, wy1], fill=(236, 198, 120, 235))
    # muntins
    draw.line([( (wx0 + wx1) // 2, wy0), ((wx0 + wx1) // 2, wy1)], fill=(120, 86, 44), width=10)
    draw.line([(wx0, (wy0 + wy1) // 2), (wx1, (wy0 + wy1) // 2)], fill=(120, 86, 44), width=10)
    draw.rectangle([wx0, wy0, wx1, wy1], outline=(96, 66, 34), width=16)
    # frost in the corners
    for cx, cy in [(wx0, wy0), (wx1, wy0), (wx0, wy1), (wx1, wy1)]:
        for r in range(60, 0, -10):
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(220, 230, 245, 40), width=2)


def draw_gears(draw, width, height):
    """Faint clockwork gears floating in the dark sky corners."""
    def gear(cx, cy, r, teeth, color):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=6)
        draw.ellipse([cx - r // 3, cy - r // 3, cx + r // 3, cy + r // 3], outline=color, width=5)
        for k in range(teeth):
            a = 2 * math.pi * k / teeth
            x1 = cx + (r) * math.cos(a)
            y1 = cy + (r) * math.sin(a)
            x2 = cx + (r + 16) * math.cos(a)
            y2 = cy + (r + 16) * math.sin(a)
            draw.line([(x1, y1), (x2, y2)], fill=color, width=6)
    gear(200, 260, 90, 12, (90, 110, 150, 160))
    gear(width - 230, 300, 64, 10, (90, 110, 150, 140))
    gear(150, 700, 50, 9, (80, 100, 140, 120))


def draw_sill(draw, width, height):
    """The wooden windowsill the soldier stands on."""
    sill_y = 1320
    draw.rectangle([200, sill_y, width - 200, sill_y + 70], fill=(86, 58, 34))
    draw.rectangle([160, sill_y + 70, width - 160, sill_y + 130], fill=(64, 42, 24))
    # a thin line of snow on the sill edge
    draw.rectangle([200, sill_y - 8, width - 200, sill_y + 4], fill=(226, 234, 246))


def draw_tin_soldier(draw, width, height):
    """A small one-legged tin soldier standing on the sill, in silhouette with bright trim."""
    cx, base = width // 2, 1320
    blue = (40, 70, 130)
    red = (150, 50, 50)
    gold = (210, 170, 80)
    skin = (40, 36, 40)
    # single leg
    draw.rectangle([cx - 14, base - 150, cx + 6, base], fill=blue)
    draw.rectangle([cx - 20, base - 4, cx + 14, base + 10], fill=(20, 16, 18))  # boot
    # torso (red coat)
    draw.rectangle([cx - 34, base - 280, cx + 30, base - 150], fill=red)
    # gold buttons / sash
    for by in range(base - 268, base - 160, 26):
        draw.ellipse([cx - 4, by, cx + 6, by + 10], fill=gold)
    draw.line([(cx - 34, base - 256), (cx + 30, base - 230)], fill=gold, width=6)
    # arms
    draw.rectangle([cx - 48, base - 274, cx - 34, base - 168], fill=red)
    draw.rectangle([cx + 30, base - 274, cx + 44, base - 168], fill=red)
    # rifle at shoulder
    draw.line([(cx + 40, base - 300), (cx + 52, base - 150)], fill=(60, 48, 30), width=7)
    # head
    draw.ellipse([cx - 22, base - 340, cx + 18, base - 280], fill=skin)
    # tall shako hat
    draw.rectangle([cx - 22, base - 392, cx + 18, base - 332], fill=blue)
    draw.rectangle([cx - 26, base - 340, cx + 22, base - 330], fill=gold)
    draw.ellipse([cx - 6, base - 410, cx + 6, base - 396], fill=red)  # plume tip


def draw_snow(draw, width, height):
    rng = random.Random(31)
    for _ in range(260):
        x = rng.randint(0, width)
        y = rng.randint(0, int(height * 0.74))
        s = rng.randint(1, 4)
        a = rng.randint(90, 220)
        draw.ellipse([x - s, y - s, x + s, y + s], fill=(245, 248, 255, a))


def create_cover(metadata_path, output_path):
    metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    title = metadata.get("title", "The Tin Soldier's Waltz")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    draw_gradient(draw, WIDTH, HEIGHT)
    draw_gears(draw, WIDTH, HEIGHT)
    draw_window_glow(draw, WIDTH, HEIGHT)
    draw_sill(draw, WIDTH, HEIGHT)
    draw_tin_soldier(draw, WIDTH, HEIGHT)
    draw_snow(draw, WIDTH, HEIGHT)

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
