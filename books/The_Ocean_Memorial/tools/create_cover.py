#!/usr/bin/env python3
"""Cover: The Ocean Memorial — a deep-sea dive: a descending submersible, a wreck on the ridge, light shafts."""

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
rng.seed(1811006)

# Palette: abyssal blues, shaft light, wreck rust, sub yellow
DEEP_TOP = (20, 40, 60)
DEEP_BOT = (6, 12, 20)
SHAFT = (140, 200, 220)
RUST = (120, 70, 44)
SUB = (226, 176, 66)
DARK = (10, 14, 22)

def _deep(img):
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(H):
        t = y / H
        r = int(DEEP_TOP[0] + (DEEP_BOT[0] - DEEP_TOP[0]) * t)
        g = int(DEEP_TOP[1] + (DEEP_BOT[1] - DEEP_TOP[1]) * t)
        b = int(DEEP_TOP[2] + (DEEP_BOT[2] - DEEP_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))
    # light shafts from above
    for k in range(6):
        x0 = int(rng.uniform(0, W))
        draw.polygon([(x0, 0), (x0 + int(rng.uniform(60, 160)), 0), (x0 + int(rng.uniform(200, 380)), int(H * 0.55))], fill=(*SHAFT, 16))
    del draw

def _wreck(img):
    """The Lucida on the ridge: hull, mast, rusting, half-buried."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    y0 = int(H * 0.78)
    # sea floor
    d.rectangle((0, y0, W, H), fill=(*DARK, 245))
    # ridge bumps
    for k in range(12):
        rx = int(rng.uniform(0, W))
        d.ellipse((rx, y0 + int(rng.uniform(-20, 30)), rx + int(rng.uniform(120, 300)), y0 + int(rng.uniform(40, 90))), fill=(*DARK, 200))
    # hull
    hx0, hy0 = int(W * 0.30), y0 - int(H * 0.14)
    d.polygon([(hx0, hy0 + 80), (hx0 + 300, hy0), (hx0 + 620, hy0 + 60), (hx0 + 560, hy0 + 160), (hx0 + 60, hy0 + 170)], fill=(*RUST, 230))
    # cabin
    d.rectangle((hx0 + 180, hy0 - 40, hx0 + 400, hy0 + 40), fill=(*RUST, 210))
    # portholes (dark)
    for k in range(4):
        d.ellipse((hx0 + 220 + k * 50, hy0 - 20, hx0 + 250 + k * 50, hy0 + 10), fill=(*DARK, 255))
    # mast fallen
    d.line((hx0 + 500, hy0 + 40, hx0 + 720, hy0 + 150), fill=(*RUST, 190), width=10)
    # weed fronds
    for k in range(10):
        wx = int(rng.uniform(hx0, hx0 + 620))
        d.line((wx, hy0 + 160, wx + int(rng.uniform(-30, 30)), hy0 + 220), fill=(*RUST, 120), width=3)
    layer = layer.filter(ImageFilter.GaussianBlur(1))
    return Image.alpha_composite(img, layer)

def _sub(img):
    """A small bright submersible descending, headlights on."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    sx, sy = int(W * 0.62), int(H * 0.42)
    d.ellipse((sx - 55, sy - 30, sx + 55, sy + 30), fill=(*SUB, 240), outline=(*DARK, 220), width=4)
    d.ellipse((sx - 20, sy - 14, sx + 16, sy + 14), fill=(*DARK, 220))
    d.ellipse((sx - 12, sy - 7, sx + 8, sy + 7), fill=(*SHAFT, 255))
    # manipulator arms
    d.line((sx + 40, sy + 10, sx + 90, sy + 40), fill=(*DARK, 220), width=6)
    d.line((sx + 40, sy - 10, sx + 90, sy - 40), fill=(*DARK, 220), width=6)
    # headlight beam
    d.polygon([(sx - 55, sy - 10), (sx - 55, sy + 10), (sx - 240, sy + 90), (sx - 240, sy - 90)], fill=(*SHAFT, 26))
    # tether
    d.line((sx, sy - 26, sx + 30, sy - 120), fill=(*SHAFT, 140), width=3)
    layer = layer.filter(ImageFilter.GaussianBlur(1))
    return Image.alpha_composite(img, layer)

def _make_cover(mp, op):
    m = json.loads(Path(mp).read_text(encoding="utf-8"))
    title = m["title"]; author = m.get("author", "Barış Kısır"); model = m.get("model", "")
    img = Image.new("RGBA", (W, H), DEEP_BOT + (255,))
    _deep(img)
    img = _wreck(img)
    img = _sub(img)
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
