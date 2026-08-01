#!/usr/bin/env python3
"""Cover: The Signal Garden — a dark spruce forest grid with glowing root/signal filaments running through the soil."""

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
rng.seed(8012044)

# Palette: deep spruce green, snow grey, phosphor green glow, resin amber
FOREST_TOP = (12, 26, 22)
FOREST_BOT = (26, 42, 34)
SNOW = (178, 186, 182)
PHOSPHOR = (128, 232, 152)
AMBER = (212, 168, 96)

def _forest(img):
    """Vertical spruce trunks receding into dark; snow ground."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for y in range(H):
        t = y / H
        r = int(FOREST_TOP[0] + (FOREST_BOT[0] - FOREST_TOP[0]) * t)
        g = int(FOREST_TOP[1] + (FOREST_BOT[1] - FOREST_TOP[1]) * t)
        b = int(FOREST_TOP[2] + (FOREST_BOT[2] - FOREST_TOP[2]) * t)
        d.line((0, y, W, y), fill=(r, g, b, 255))
    for k in range(26):
        x = int(rng.uniform(0, W))
        wdt = int(rng.uniform(10, 34))
        top = int(rng.uniform(0, H * 0.1))
        d.rectangle((x - wdt // 2, top, x + wdt // 2, H), fill=(8, 16, 13, 235))
        for b in range(5):
            by = top + b * int(H * 0.16) + int(rng.uniform(0, 60))
            bl = int(rng.uniform(30, 120))
            d.line((x, by, x - bl, by + int(rng.uniform(-20, 30))), fill=(10, 20, 16, 200), width=int(wdt * 0.35))
            d.line((x, by, x + bl, by + int(rng.uniform(-20, 30))), fill=(10, 20, 16, 200), width=int(wdt * 0.35))
    d.rectangle((0, int(H * 0.84), W, H), fill=(*SNOW, 190))
    layer = layer.filter(ImageFilter.GaussianBlur(1))
    return Image.alpha_composite(img, layer)

def _signals(img):
    """Glowing mycelial filaments through soil: branching phosphor paths."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for k in range(9):
        x, y = rng.uniform(100, W - 100), rng.uniform(H * 0.35, H * 0.9)
        pts = [(x, y)]
        segs = int(rng.uniform(8, 18))
        for s in range(segs):
            x += rng.uniform(-110, 110)
            y += rng.uniform(-40, 140)
            pts.append((x, y))
        col = PHOSPHOR if k % 3 else AMBER
        d.line(pts, fill=(*col, 170), width=int(rng.uniform(2, 5)))
        for (nx, ny) in pts[::3]:
            rr = int(rng.uniform(5, 12))
            d.ellipse((nx - rr, ny - rr, nx + rr, ny + rr), fill=(*col, 90))
    cx, cy = int(W * 0.78), int(H * 0.14)
    d.ellipse((cx - 90, cy - 90, cx + 90, cy + 90), outline=(*SNOW, 200), width=6)
    d.line((cx, cy, cx + 60, cy + 140), fill=(*SNOW, 200), width=10)
    layer = layer.filter(ImageFilter.GaussianBlur(2))
    return Image.alpha_composite(img, layer)

def _snowfall(draw):
    for k in range(180):
        x = int(rng.uniform(0, W)); y = int(rng.uniform(0, H))
        r = int(rng.uniform(1, 3))
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(*SNOW, 120))

def make_cover(mp, op):
    m = json.loads(Path(mp).read_text(encoding="utf-8"))
    title = m["title"]; author = m.get("author", "Barış Kısır"); model = m.get("model", "")
    img = Image.new("RGBA", (W, H), FOREST_BOT + (255,))
    img = _forest(img)
    img = _signals(img); draw = ImageDraw.Draw(img, "RGBA")
    _snowfall(draw)
    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, title, author, model)
    img.convert("RGB").save(op, "PNG", optimize=True)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    make_cover(
        ROOT / a.metadata if not a.metadata.is_absolute() else a.metadata,
        ROOT / a.out if not a.out.is_absolute() else a.out,
    )

if __name__ == "__main__":
    main()
