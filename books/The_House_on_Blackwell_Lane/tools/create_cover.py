#!/usr/bin/env python3
"""Cover: The House on Blackwell Lane — a dark Victorian with rows of lit windows, moon, fog, an open door."""

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
rng.seed(1710005)

# Palette: night purple, sickly window glow, fog grey
NIGHT_TOP = (16, 14, 26)
NIGHT_BOT = (28, 24, 38)
WINDOW = (214, 190, 120)
FOG = (150, 150, 160)
DARK = (24, 20, 30)
MOON = (226, 224, 214)

def _night(img):
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(H):
        t = y / H
        r = int(NIGHT_TOP[0] + (NIGHT_BOT[0] - NIGHT_TOP[0]) * t)
        g = int(NIGHT_TOP[1] + (NIGHT_BOT[1] - NIGHT_TOP[1]) * t)
        b = int(NIGHT_TOP[2] + (NIGHT_BOT[2] - NIGHT_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))
    # moon
    mx, my, mr = int(W * 0.78), int(H * 0.13), 60
    draw.ellipse((mx - mr, my - mr, mx + mr, my + mr), fill=(*MOON, 220))
    # dead trees
    for k in range(5):
        tx = int(rng.uniform(60, W - 60))
        d2 = ImageDraw.Draw(img, "RGBA")
        d2.line((tx, int(H * 0.5), tx, int(H * 0.28)), fill=(*DARK, 190), width=6)
        for b in range(3):
            bx = tx + int(rng.uniform(-40, 40))
            d2.line((tx, int(H * 0.32) + b * 30, bx, int(H * 0.30) + b * 40 - 60), fill=(*DARK, 180), width=4)
    del draw

def _house(img):
    """The Victorian: gabled, rows of windows, one open door leaking light."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    hx0, hy0 = int(W * 0.22), int(H * 0.40)
    hw, hh = int(W * 0.56), int(H * 0.52)
    # body
    d.rectangle((hx0, hy0, hx0 + hw, hy0 + hh), fill=(*DARK, 245))
    # gable
    d.polygon([(hx0 - 40, hy0), (hx0 + hw // 2, hy0 - int(H * 0.16)), (hx0 + hw + 40, hy0)], fill=(*DARK, 245))
    # rows of windows (locked rooms)
    for row in range(4):
        for col in range(3):
            wx0 = hx0 + 40 + col * (hw - 80) // 3
            wy0 = hy0 + 50 + row * ((hh - 120) // 4)
            lit = (row + col) % 2 == 0
            d.rectangle((wx0, wy0, wx0 + (hw - 80) // 3 - 30, wy0 + 60), fill=(*(WINDOW if lit else (12, 10, 16)), 255))
            d.line((wx0 + ((hw - 80) // 3 - 30) // 2, wy0, wx0 + ((hw - 80) // 3 - 30) // 2, wy0 + 60), fill=(*DARK, 200), width=3)
            d.line((wx0, wy0 + 30, wx0 + (hw - 80) // 3 - 30, wy0 + 30), fill=(*DARK, 200), width=3)
    # the open door — light leaking
    dx0, dy0 = hx0 + hw // 2 - 40, hy0 + hh - 120
    d.rectangle((dx0, dy0, dx0 + 80, hy0 + hh), fill=(*WINDOW, 255))
    d.line((dx0 + 40, dy0, dx0 + 40, hy0 + hh), fill=(*DARK, 230), width=4)
    # light pool on the lawn
    d.ellipse((dx0 - 90, hy0 + hh - 20, dx0 + 170, hy0 + hh + 80), fill=(*WINDOW, 60))
    # fence
    for k in range(14):
        fx = hx0 - 60 + k * 60
        d.line((fx, hy0 + hh, fx, hy0 + hh + 60), fill=(*DARK, 170), width=4)
    d.line((hx0 - 60, hy0 + hh + 30, hx0 + hw + 60, hy0 + hh + 30), fill=(*DARK, 170), width=4)
    layer = layer.filter(ImageFilter.GaussianBlur(1))
    return Image.alpha_composite(img, layer)

def _fog(img):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for k in range(10):
        y = int(H * 0.55) + k * int(H * 0.04)
        d.rectangle((0, y, W, y + int(H * 0.03)), fill=(*FOG, 26))
    layer = layer.filter(ImageFilter.GaussianBlur(12))
    return Image.alpha_composite(img, layer)

def _make_cover(mp, op):
    m = json.loads(Path(mp).read_text(encoding="utf-8"))
    title = m["title"]; author = m.get("author", "Barış Kısır"); model = m.get("model", "")
    img = Image.new("RGBA", (W, H), NIGHT_BOT + (255,))
    _night(img)
    img = _house(img)
    img = _fog(img)
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
