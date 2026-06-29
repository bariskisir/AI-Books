#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Memory Merchant."""

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
    """A dim near-future shop: deep grey-blue above, faint teal haze below."""
    for y in range(height):
        f = y / height
        if f < 0.5:
            t = f / 0.5
            c = lerp_color((12, 16, 26), (18, 28, 40), t)
        else:
            t = (f - 0.5) / 0.5
            c = lerp_color((18, 28, 40), (26, 44, 52), t)
        draw.line([(0, y), (width, y)], fill=c)


def _glow_dot(draw, x, y, r, color):
    rr = int(r)
    for i in range(rr, 0, -1):
        a = int(color[3] * (i / rr) ** 2)
        draw.ellipse([x - i, y - i, x + i, y + i], fill=(color[0], color[1], color[2], a))


def draw_shelves(draw, width, height):
    """Rows of softly glowing memory vials on dim shelves."""
    rng = random.Random(11)
    palettes = [
        (90, 220, 210),   # teal
        (170, 130, 240),  # violet
        (240, 190, 110),  # amber
        (120, 180, 245),  # cool blue
    ]
    shelf_ys = [560, 880, 1200, 1520]
    for sy in shelf_ys:
        # shelf board
        draw.rectangle([120, sy + 150, width - 120, sy + 172], fill=(40, 48, 60))
        draw.rectangle([120, sy + 172, width - 120, sy + 184], fill=(22, 28, 38))
        n = 9
        for i in range(n):
            x = 200 + i * ((width - 400) // (n - 1))
            color = palettes[(i + sy) % len(palettes)]
            vh = rng.randint(96, 134)
            top = sy + 150 - vh
            # vial body (glass)
            draw.rounded_rectangle([x - 26, top, x + 26, sy + 150], radius=20,
                                   fill=(color[0] // 4 + 16, color[1] // 4 + 18, color[2] // 4 + 22, 235),
                                   outline=(color[0], color[1], color[2], 120), width=2)
            # neck and cap
            draw.rectangle([x - 12, top - 26, x + 12, top], fill=(60, 70, 84))
            draw.rectangle([x - 16, top - 38, x + 16, top - 26], fill=(80, 92, 108))
            # luminous memory inside
            _glow_dot(draw, x, top + vh // 2, 30, (color[0], color[1], color[2], 150))
            # reflection on shelf
            _glow_dot(draw, x, sy + 158, 18, (color[0], color[1], color[2], 60))


def draw_figure(draw, width, height):
    """A dim silhouette of the broker standing among the shelves, lower right."""
    fx, base = width - 360, 1680
    body = (8, 12, 18)
    # coat / torso
    draw.polygon([(fx - 70, base), (fx - 50, base - 300), (fx + 50, base - 300), (fx + 70, base)], fill=body)
    # head
    draw.ellipse([fx - 30, base - 380, fx + 30, base - 300], fill=body)
    # faint rim light from the vials
    draw.arc([fx - 30, base - 380, fx + 30, base - 300], 200, 320, fill=(90, 200, 200, 120), width=3)
    draw.line([(fx + 50, base - 300), (fx + 64, base)], fill=(70, 150, 170, 90), width=4)


def draw_motes(draw, width, height):
    """Drifting motes of light, like loose memories."""
    rng = random.Random(5)
    for _ in range(90):
        x = rng.randint(0, width)
        y = rng.randint(0, int(height * 0.72))
        r = rng.randint(2, 6)
        col = rng.choice([(120, 220, 215), (180, 150, 240), (240, 200, 130)])
        _glow_dot(draw, x, y, r * 3, (col[0], col[1], col[2], rng.randint(40, 110)))


def create_cover(metadata_path, output_path):
    metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    title = metadata.get("title", "The Memory Merchant")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    draw_gradient(draw, WIDTH, HEIGHT)
    draw_shelves(draw, WIDTH, HEIGHT)
    draw_figure(draw, WIDTH, HEIGHT)
    draw_motes(draw, WIDTH, HEIGHT)

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
