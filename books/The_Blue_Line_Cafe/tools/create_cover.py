#!/usr/bin/env python3
"""Cover: The Blue Line Cafe — a seaside cafe at blue hour, warm window light, a cup and cinnamon rolls."""

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
rng.seed(1508003)

# Palette: blue hour sea, sand, warm window glow, cream
SEA_TOP = (36, 52, 84)
SEA_BOT = (56, 72, 100)
SAND = (196, 176, 138)
WARM = (250, 190, 110)
CREAM = (250, 244, 228)
INK = (70, 56, 40)

def _blue_hour(img):
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(int(H * 0.52)):
        t = y / (H * 0.52)
        r = int(SEA_TOP[0] + (SEA_BOT[0] - SEA_TOP[0]) * t)
        g = int(SEA_TOP[1] + (SEA_BOT[1] - SEA_TOP[1]) * t)
        b = int(SEA_TOP[2] + (SEA_BOT[2] - SEA_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))
    # stars
    for k in range(90):
        x = int(rng.uniform(0, W)); y = int(rng.uniform(0, int(H * 0.3)))
        r = int(rng.uniform(1, 2))
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(*CREAM, int(rng.uniform(60, 160))))
    del draw

def _cafe(img):
    """The cafe on the waterline: warm glowing windows, awning, a cup on the sill."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    y_base = int(H * 0.52)
    # building
    d.rectangle((int(W * 0.14), y_base, int(W * 0.86), H), fill=(*INK, 220))
    # windows with warm light
    for k in range(4):
        wx0 = int(W * 0.20) + k * int(W * 0.16)
        d.rectangle((wx0, y_base + 60, wx0 + int(W * 0.10), y_base + int(H * 0.18)), fill=(*WARM, 255))
        # window cross
        d.line((wx0 + int(W * 0.05), y_base + 60, wx0 + int(W * 0.05), y_base + int(H * 0.18)), fill=(*INK, 200), width=4)
        d.line((wx0, y_base + 60 + (int(H * 0.18) - 60) // 2, wx0 + int(W * 0.10), y_base + 60 + (int(H * 0.18) - 60) // 2), fill=(*INK, 200), width=4)
        # light spill on sand
        d.polygon([(wx0, y_base + int(H * 0.18)), (wx0 + int(W * 0.10), y_base + int(H * 0.18)), (wx0 + int(W * 0.16), H), (wx0 - int(W * 0.06), H)], fill=(*WARM, 40))
    # awning stripes
    d.rectangle((int(W * 0.14), y_base, int(W * 0.86), y_base + 44), fill=(*CREAM, 255))
    for k in range(10):
        x0 = int(W * 0.14) + k * int(W * 0.072)
        d.rectangle((x0, y_base, x0 + int(W * 0.036), y_base + 44), fill=(*INK, 220))
    # cup and cinnamon rolls on the sill
    cx, cy = int(W * 0.72), y_base + int(H * 0.18) + 40
    d.rounded_rectangle((cx - 30, cy - 40, cx + 30, cy + 10), radius=14, fill=(*CREAM, 255), outline=(*INK, 200), width=3)
    d.ellipse((cx - 30, cy - 54, cx + 30, cy - 30), fill=(*CREAM, 255), outline=(*INK, 200), width=3)
    d.ellipse((cx - 14, cy - 44, cx + 14, cy - 16), fill=(*WARM, 220))
    for k in range(2):
        rx = cx - 110 + k * 70
        d.ellipse((rx - 26, cy + 4, rx + 26, cy + 56), fill=(*WARM, 240), outline=(*INK, 180), width=3)
    # moon path reflection on water
    d.line((int(W * 0.30), y_base, int(W * 0.70), H), fill=(*WARM, 50), width=10)
    layer = layer.filter(ImageFilter.GaussianBlur(1))
    return Image.alpha_composite(img, layer)

def _make_cover(mp, op):
    m = json.loads(Path(mp).read_text(encoding="utf-8"))
    title = m["title"]; author = m.get("author", "Barış Kısır"); model = m.get("model", "")
    img = Image.new("RGBA", (W, H), SEA_BOT + (255,))
    _blue_hour(img)
    img = _cafe(img)
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
