#!/usr/bin/env python3
"""Cover: The Mapmaker's Lament — an old nautical chart of a fictional island, compass rose, faded sea."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

rng = random.Random()
rng.seed(2114009)

# Palette: aged parchment, faded sea ink, island green, compass red
PARCH = (226, 210, 176)
INK = (74, 78, 88)
SEA = (96, 118, 132)
ISLAND = (108, 122, 74)
COMPASS = (150, 56, 44)
GOLD = (186, 150, 78)

def _parchment(img):
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(H):
        t = y / H
        r = int(PARCH[0] + (SEA[0] - PARCH[0]) * 0.25 * t)
        g = int(PARCH[1] + (SEA[1] - PARCH[1]) * 0.25 * t)
        b = int(PARCH[2] + (SEA[2] - PARCH[2]) * 0.25 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))
    # age speckles
    for k in range(700):
        x = int(rng.uniform(0, W)); y = int(rng.uniform(0, H))
        r = int(rng.uniform(1, 3))
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(120, 96, 60, int(rng.uniform(30, 90))))
    # sea texture: faint latitude/longitude grid
    for k in range(22):
        draw.line((0, k * 120, W, k * 120), fill=(*SEA, 26), width=2)
        draw.line((k * 80, 0, k * 80, H), fill=(*SEA, 26), width=2)
    del draw

def _island(img):
    """The fictional island, hand-drawn style, with a name in script."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = int(W * 0.48), int(H * 0.44)
    pts = []
    for ang in range(0, 360, 6):
        rad = int(190 + 55 * math.sin(ang * 0.02 + 1.3) + 30 * math.sin(ang * 0.05))
        x = cx + rad * math.cos(math.radians(ang))
        y = cy + rad * 0.72 * math.sin(math.radians(ang))
        pts.append((x, y))
    d.polygon(pts, fill=(*ISLAND, 210), outline=(*INK, 200), width=4)
    # island features: a peak, a cove
    d.polygon([(cx - 60, cy + 40), (cx + 10, cy - 90), (cx + 80, cy + 50)], fill=(*ISLAND, 240), outline=(*INK, 180), width=3)
    d.arc((cx - 160, cy + 60, cx + 120, cy + 260), 200, 340, fill=(*INK, 160), width=4)
    # island name in a small flourish
    d.rectangle((cx - 130, cy + 120, cx + 130, cy + 150), fill=(*PARCH, 240), outline=(*INK, 160), width=2)
    layer = layer.filter(ImageFilter.GaussianBlur(1))
    return Image.alpha_composite(img, layer)

def _compass_rose(img):
    """A classic compass rose, lower right."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy, r = int(W * 0.78), int(H * 0.70), 130
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(*INK, 200), width=4)
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        tip = (cx + r * 0.8 * math.cos(a), cy + r * 0.8 * math.sin(a))
        col = COMPASS if ang % 90 == 0 else INK
        d.polygon([(cx, cy), tip, (cx + r * 0.22 * math.cos(a + math.radians(18)), cy + r * 0.22 * math.sin(a + math.radians(18)))], fill=(*col, 210))
        d.polygon([(cx, cy), tip, (cx + r * 0.22 * math.cos(a - math.radians(18)), cy + r * 0.22 * math.sin(a - math.radians(18)))], fill=(*col, 210))
    d.ellipse((cx - 12, cy - 12, cx + 12, cy + 12), fill=(*GOLD, 255))
    layer = layer.filter(ImageFilter.GaussianBlur(1))
    return Image.alpha_composite(img, layer)

def _make_cover(mp, op):
    m = json.loads(Path(mp).read_text(encoding="utf-8"))
    title = m["title"]; author = m.get("author", "Barış Kısır"); model = m.get("model", "")
    img = Image.new("RGBA", (W, H), PARCH + (255,))
    _parchment(img)
    img = _island(img)
    img = _compass_rose(img)
    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, title, author, model)
    img.convert("RGB").save(op, "PNG", optimize=True)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    _make_cover(
        ROOT / a.metadata if not a.metadata.is_absolute() else a.metadata,
        ROOT / a.out if not a.out.is_absolute() else a.out,
    )

if __name__ == "__main__":
    main()
