#!/usr/bin/env python3
"""Cover: The Tenth Resident — a brutalist facade of a thousand windows, one dark window, ledgers, red stamp."""

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
rng.seed(2013008)

# Palette: concrete grey, bureaucratic teal, the red stamp, the dark window
CONCRETE_TOP = (128, 132, 138)
CONCRETE_BOT = (96, 100, 106)
TEAL = (58, 120, 124)
RED = (196, 46, 40)
DARK = (30, 32, 36)
PAPER = (232, 228, 214)

def _facade(img):
    """A brutalist wall of windows; the deleted are the dark ones."""
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(H):
        t = y / H
        r = int(CONCRETE_TOP[0] + (CONCRETE_BOT[0] - CONCRETE_TOP[0]) * t)
        g = int(CONCRETE_TOP[1] + (CONCRETE_BOT[1] - CONCRETE_TOP[1]) * t)
        b = int(CONCRETE_TOP[2] + (CONCRETE_BOT[2] - CONCRETE_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))
    # window grid
    rows, cols = 14, 6
    margin_x, margin_y = 80, 90
    gap_x = (W - 2 * margin_x) // cols
    gap_y = (H - 2 * margin_y) // rows
    for row in range(rows):
        for col in range(cols):
            wx0 = margin_x + col * gap_x + 8
            wy0 = margin_y + row * gap_y + 8
            lit = (row * 7 + col * 13) % 11 != 0  # most lit, some dark
            colr = TEAL if lit else DARK
            draw.rectangle((wx0, wy0, wx0 + gap_x - 16, wy0 + gap_y - 16), fill=(*colr, 235))
            draw.rectangle((wx0, wy0, wx0 + gap_x - 16, wy0 + gap_y - 16), outline=(*DARK, 200), width=2)
    # one window red-lit (the protagonist's)
    rx0 = margin_x + 4 * gap_x + 8
    ry0 = margin_y + 9 * gap_y + 8
    draw.rectangle((rx0, ry0, rx0 + gap_x - 16, ry0 + gap_y - 16), fill=(*RED, 255))
    del draw

def _ledger(img):
    """A paper ledger at the bottom with a red stamp."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    ly0 = int(H * 0.80)
    d.polygon([(int(W * 0.18), ly0), (int(W * 0.82), ly0), (int(W * 0.80), ly0 + 300), (int(W * 0.20), ly0 + 300)], fill=(*PAPER, 245), outline=(*DARK, 200), width=3)
    # ruled lines
    for k in range(8):
        d.line((int(W * 0.24), ly0 + 40 + k * 30, int(W * 0.76), ly0 + 40 + k * 30), fill=(*DARK, 120), width=2)
    # red stamp: a circle with a cross (the deletion mark)
    sx, sy, sr = int(W * 0.62), ly0 + 170, 70
    d.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), outline=(*RED, 230), width=8)
    d.line((sx - sr + 18, sy - sr + 18, sx + sr - 18, sy + sr - 18), fill=(*RED, 210), width=8)
    d.line((sx + sr - 18, sy - sr + 18, sx - sr + 18, sy + sr - 18), fill=(*RED, 210), width=8)
    layer = layer.filter(ImageFilter.GaussianBlur(1))
    return Image.alpha_composite(img, layer)

def _make_cover(mp, op):
    m = json.loads(Path(mp).read_text(encoding="utf-8"))
    title = m["title"]; author = m.get("author", "Barış Kısır"); model = m.get("model", "")
    img = Image.new("RGBA", (W, H), CONCRETE_BOT + (255,))
    _facade(img)
    img = _ledger(img)
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
