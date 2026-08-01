#!/usr/bin/env python3
"""Cover: The Last Wrangler — a lone rider and longhorns before a high pass at golden hour, Montana."""

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
rng.seed(1609004)

# Palette: golden prairie, dusk purple mountains, leather brown
PRAIRIE_TOP = (236, 196, 132)
PRAIRIE_BOT = (206, 152, 92)
MOUNTAIN = (84, 62, 84)
LEATHER = (96, 62, 40)
DARK = (52, 36, 26)
HORN = (232, 220, 200)

def _prairie(img):
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(int(H * 0.55)):
        t = y / (H * 0.55)
        r = int(PRAIRIE_TOP[0] + (PRAIRIE_BOT[0] - PRAIRIE_TOP[0]) * t)
        g = int(PRAIRIE_TOP[1] + (PRAIRIE_BOT[1] - PRAIRIE_TOP[1]) * t)
        b = int(PRAIRIE_TOP[2] + (PRAIRIE_BOT[2] - PRAIRIE_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))
    del draw

def _mountains(img):
    """The Beartooth Pass: layered purple silhouettes with a snow cap."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for row in range(3):
        alpha = 120 + 40 * row
        pts = []
        y_base = int(H * (0.24 + 0.09 * row))
        for x in range(0, W + 40, 40):
            y = y_base - int(90 * math.sin(x * 0.006 + row * 2.1)) - int(30 * math.sin(x * 0.02 + row))
            pts.append((x, y))
        pts += [(W, H), (0, H)]
        d.polygon(pts, fill=(*MOUNTAIN, alpha))
    # snow cap on the far peak
    d.polygon([(int(W * 0.58), int(H * 0.155)), (int(W * 0.64), int(H * 0.19)), (int(W * 0.56), int(H * 0.20))], fill=(*HORN, 200))
    layer = layer.filter(ImageFilter.GaussianBlur(1))
    return Image.alpha_composite(img, layer)

def _herd(img):
    """Longhorn silhouettes crossing the mid-distance."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    y0 = int(H * 0.62)
    for k in range(7):
        x = int(W * 0.15) + k * int(W * 0.10) + int(rng.uniform(-20, 20))
        s = int(rng.uniform(30, 44))
        # body
        d.ellipse((x - s, y0 - s // 2, x + s, y0 + s // 2), fill=(*DARK, 210))
        # head with horns
        d.ellipse((x + s - 8, y0 - 12, x + s + 22, y0 + 12), fill=(*DARK, 210))
        d.arc((x + s - 6, y0 - 26, x + s + 26, y0 + 2), 200, 340, fill=(*HORN, 190), width=4)
        # legs
        for lx in (x - s + 6, x + s - 14):
            d.line((lx, y0 + s // 2, lx - 6, y0 + s // 2 + 26), fill=(*DARK, 190), width=5)
    return Image.alpha_composite(img, layer)

def _rider(img):
    """The lone rider on the rise, hat tipped, toward the pass."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rx, ry = int(W * 0.68), int(H * 0.50)
    # horse
    d.ellipse((rx - 60, ry - 20, rx + 50, ry + 40), fill=(*LEATHER, 235))
    d.line((rx + 30, ry - 8, rx + 78, ry - 34), fill=(*LEATHER, 235), width=14)
    d.ellipse((rx + 66, ry - 44, rx + 96, ry - 16), fill=(*LEATHER, 235))
    for lx in (rx - 40, rx - 8, rx + 18, rx + 42):
        d.line((lx, ry + 30, lx - 8, ry + 62), fill=(*LEATHER, 200), width=6)
    # rider
    d.line((rx + 6, ry - 30, rx + 10, ry - 66), fill=(*DARK, 235), width=12)
    d.ellipse((rx - 10, ry - 86, rx + 26, ry - 58), fill=(*DARK, 235))
    d.line((rx + 6, ry - 72, rx + 46, ry - 48), fill=(*DARK, 220), width=8)
    # hat
    d.line((rx - 20, ry - 88, rx + 34, ry - 84), fill=(*DARK, 255), width=8)
    d.rectangle((rx - 6, ry - 90, rx + 20, ry - 82), fill=(*DARK, 255))
    return Image.alpha_composite(img, layer)

def _grass(draw):
    for k in range(180):
        x = int(rng.uniform(0, W)); y = int(rng.uniform(int(H * 0.55), H))
        ln = int(rng.uniform(4, 12))
        draw.line((x, y, x + 3, y - ln), fill=(*LEATHER, int(rng.uniform(60, 140))), width=2)

def _make_cover(mp, op):
    m = json.loads(Path(mp).read_text(encoding="utf-8"))
    title = m["title"]; author = m.get("author", "Barış Kısır"); model = m.get("model", "")
    img = Image.new("RGBA", (W, H), PRAIRIE_BOT + (255,))
    _prairie(img)
    img = _mountains(img)
    img = _herd(img)
    img = _rider(img); draw = ImageDraw.Draw(img, "RGBA")
    _grass(draw)
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
