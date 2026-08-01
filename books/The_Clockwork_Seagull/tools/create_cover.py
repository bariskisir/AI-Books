#!/usr/bin/env python3
"""Cover: The Clockwork Seagull — a brass seagull in flight before a fog city of gears and a clocktower."""

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
rng.seed(1205007)

# Palette: steam fog, brass, copper, slate roof
FOG_TOP = (208, 208, 196)
FOG_BOT = (150, 152, 148)
BRASS = (196, 152, 74)
BRASS_DARK = (140, 106, 52)
COPPER = (176, 96, 52)
SLATE = (74, 82, 92)
STEAM = (236, 236, 228)

def _fog_city(img):
    """Layered fog and rooftop silhouettes with a clocktower."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for y in range(H):
        t = y / H
        r = int(FOG_TOP[0] + (FOG_BOT[0] - FOG_TOP[0]) * t)
        g = int(FOG_TOP[1] + (FOG_BOT[1] - FOG_TOP[1]) * t)
        b = int(FOG_TOP[2] + (FOG_BOT[2] - FOG_TOP[2]) * t)
        d.line((0, y, W, y), fill=(r, g, b, 255))
    for row in (0, 1):
        y_base = int(H * (0.66 + 0.16 * row))
        for k in range(9):
            x0 = int(rng.uniform(-40, W - 140))
            wdt = int(rng.uniform(120, 240)); hgt = int(rng.uniform(60, 140))
            d.polygon([(x0, y_base), (x0 + wdt // 2, y_base - hgt), (x0 + wdt, y_base)],
                      fill=(*SLATE, 200 - 60 * row))
            cx = x0 + int(wdt * 0.7)
            d.rectangle((cx - 14, y_base - hgt - 34, cx + 14, y_base - hgt), fill=(*SLATE, 190))
            d.ellipse((cx - 26, y_base - hgt - 70, cx + 26, y_base - hgt - 28), fill=(*STEAM, 130))
    tx = int(W * 0.62)
    tw = 240
    d.rectangle((tx - tw // 2, int(H * 0.40), tx + tw // 2, H), fill=(*SLATE, 235))
    d.polygon([(tx - tw // 2 - 40, int(H * 0.40)), (tx, int(H * 0.24)), (tx + tw // 2 + 40, int(H * 0.40))],
              fill=(*SLATE, 235))
    cx, cy, cr = tx, int(H * 0.36), 70
    d.ellipse((cx - cr, cy - cr, cx + cr, cy + cr), fill=(*STEAM, 240), outline=(*BRASS_DARK, 255), width=8)
    d.line((cx, cy, cx, cy - cr + 14), fill=(*BRASS_DARK, 255), width=6)
    d.line((cx, cy, cx + cr - 14, cy), fill=(*BRASS_DARK, 255), width=6)
    d.ellipse((cx - 10, cy - 10, cx + 10, cy + 10), fill=(*BRASS_DARK, 255))
    layer = layer.filter(ImageFilter.GaussianBlur(2))
    return Image.alpha_composite(img, layer)

def _seagull(img):
    """Brass clockwork seagull in flight, upper-left, with gear motifs."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    gx, gy = int(W * 0.30), int(H * 0.30)
    d.ellipse((gx - 60, gy - 26, gx + 60, gy + 30), fill=(*BRASS, 255))
    d.ellipse((gx - 60, gy - 26, gx + 60, gy + 30), outline=(*BRASS_DARK, 255), width=4)
    d.ellipse((gx + 46, gy - 44, gx + 86, gy - 6), fill=(*BRASS, 255), outline=(*BRASS_DARK, 255), width=4)
    d.polygon([(gx + 80, gy - 30), (gx + 116, gy - 26), (gx + 82, gy - 18)], fill=(*COPPER, 255))
    d.ellipse((gx + 62, gy - 34, gx + 74, gy - 22), fill=(*COPPER, 255))
    d.ellipse((gx + 65, gy - 31, gx + 71, gy - 25), fill=(*STEAM, 255))
    d.polygon([(gx - 30, gy - 6), (gx - 190, gy - 90), (gx - 210, gy - 60), (gx - 60, gy + 8)], fill=(*BRASS, 235), outline=(*BRASS_DARK, 255), width=3)
    d.polygon([(gx + 20, gy - 8), (gx + 200, gy - 70), (gx + 214, gy - 38), (gx + 50, gy + 10)], fill=(*BRASS, 235), outline=(*BRASS_DARK, 255), width=3)
    for (rx, ry) in [(gx - 90, gy - 44), (gx + 100, gy - 36), (gx - 140, gy - 68), (gx + 150, gy - 54)]:
        d.ellipse((rx - 5, ry - 5, rx + 5, ry + 5), fill=(*COPPER, 255))
    d.ellipse((gx + 108, gy - 12, gx + 140, gy + 22), outline=(*BRASS_DARK, 255), width=5)
    d.ellipse((gx + 118, gy - 2, gx + 130, gy + 10), fill=(*BRASS, 255))
    return Image.alpha_composite(img, layer)

def _gears(draw):
    """Scattered tiny gears drifting in the fog."""
    for k in range(24):
        x = int(rng.uniform(0, W)); y = int(rng.uniform(0, H * 0.7))
        r = int(rng.uniform(8, 20))
        draw.ellipse((x - r, y - r, x + r, y + r), outline=(*BRASS_DARK, 150), width=3)
        draw.ellipse((x - r // 3, y - r // 3, x + r // 3, y + r // 3), fill=(*BRASS_DARK, 150))

def make_cover(mp, op):
    m = json.loads(Path(mp).read_text(encoding="utf-8"))
    title = m["title"]; author = m.get("author", "Barış Kısır"); model = m.get("model", "")
    img = Image.new("RGBA", (W, H), FOG_BOT + (255,))
    img = _fog_city(img)
    img = _seagull(img); draw = ImageDraw.Draw(img, "RGBA")
    _gears(draw)
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
