#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Bone Orchard Trail."""

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
    """Blood-dusk desert sky: deep violet night above, rust and sickly amber at the horizon."""
    for y in range(height):
        f = y / height
        if f < 0.45:
            t = f / 0.45
            c = lerp_color((22, 14, 30), (70, 28, 36), t)
        elif f < 0.62:
            t = (f - 0.45) / 0.17
            c = lerp_color((70, 28, 36), (150, 70, 40), t)
        elif f < 0.70:
            t = (f - 0.62) / 0.08
            c = lerp_color((150, 70, 40), (190, 120, 60), t)
        else:
            t = (f - 0.70) / 0.30
            c = lerp_color((120, 80, 55), (40, 28, 26), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_blood_moon(draw, width, height):
    mx, my, r = width - 360, height * 0.20, 150
    for rr in range(int(r * 1.8), r, -6):
        a = max(0, 60 - (rr - r))
        draw.ellipse([mx - rr, my - rr, mx + rr, my + rr], outline=(150, 60, 45, a), width=2)
    draw.ellipse([mx - r, my - r, mx + r, my + r], fill=(165, 75, 55))
    draw.ellipse([mx - r + 18, my - r + 10, mx + r - 24, my + r - 16], fill=(150, 66, 48))


def draw_mesa(draw, width, height):
    base = height * 0.70
    # distant flat-topped mesas
    draw.polygon([(0, base), (0, base - 120), (260, base - 150), (520, base - 110),
                  (520, base)], fill=(58, 36, 38))
    draw.polygon([(900, base), (900, base - 170), (1180, base - 200), (width, base - 140),
                  (width, base)], fill=(50, 32, 34))


def draw_orchard(draw, width, height):
    """Pale, bare, twisted dead trees along the foreground ridge."""
    rng = random.Random(7)
    ground = height * 0.74
    trees = [(140, 2.4), (340, 1.8), (560, 2.1), (1040, 1.9), (1280, 2.5), (1470, 1.7)]
    for tx, scale in trees:
        h = int(360 * scale)
        top = int(ground - h)
        # trunk
        draw.line([(tx, ground), (tx + rng.randint(-12, 12), top)], fill=(214, 208, 196), width=int(10 * scale))
        # twisted branches
        for _ in range(int(5 * scale)):
            by = rng.randint(top, int(ground - 60))
            bx = tx + rng.randint(-8, 8)
            ex = bx + rng.randint(-90, 90)
            ey = by - rng.randint(30, 110)
            draw.line([(bx, by), (ex, ey)], fill=(200, 194, 182), width=max(2, int(5 * scale)))


def draw_rider(draw, width, height):
    """A lone rider silhouette on the trail."""
    rx, ground = width // 2 - 60, int(height * 0.735)
    body = (18, 12, 14)
    # horse
    draw.ellipse([rx - 70, ground - 70, rx + 70, ground - 20], fill=body)
    draw.rectangle([rx - 60, ground - 60, rx - 50, ground], fill=body)
    draw.rectangle([rx - 20, ground - 60, rx - 10, ground], fill=body)
    draw.rectangle([rx + 40, ground - 60, rx + 50, ground], fill=body)
    draw.rectangle([rx + 58, ground - 58, rx + 68, ground], fill=body)
    # neck and head
    draw.polygon([(rx + 60, ground - 60), (rx + 96, ground - 110), (rx + 110, ground - 96),
                  (rx + 74, ground - 48)], fill=body)
    # rider
    draw.ellipse([rx - 18, ground - 120, rx + 18, ground - 64], fill=body)
    draw.ellipse([rx - 12, ground - 150, rx + 14, ground - 116], fill=body)
    # hat brim
    draw.ellipse([rx - 24, ground - 152, rx + 26, ground - 140], fill=body)
    draw.rectangle([rx - 8, ground - 168, rx + 10, ground - 146], fill=body)


def draw_dust(draw, width, height):
    rng = random.Random(21)
    for _ in range(120):
        x = rng.randint(0, width)
        y = rng.randint(int(height * 0.5), int(height * 0.78))
        s = rng.randint(1, 3)
        a = rng.randint(20, 70)
        draw.ellipse([x - s, y - s, x + s, y + s], fill=(200, 170, 130, a))


def create_cover(metadata_path, output_path):
    metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    title = metadata.get("title", "The Bone Orchard Trail")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    draw_gradient(draw, WIDTH, HEIGHT)
    draw_blood_moon(draw, WIDTH, HEIGHT)
    draw_mesa(draw, WIDTH, HEIGHT)
    draw_dust(draw, WIDTH, HEIGHT)
    draw_orchard(draw, WIDTH, HEIGHT)
    draw_rider(draw, WIDTH, HEIGHT)

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
