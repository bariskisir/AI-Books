#!/usr/bin/env python3
"""Cover: The Quarry Season — a quarry face at dusk, water rising at the bottom, chalk survey lines."""

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
rng.seed(7002003)

# Palette: slate, dust, ochre, deep water
SLATE_TOP = (58, 66, 74)
SLATE_BOT = (84, 94, 100)
DUST = (196, 178, 148)
OCHRE = (168, 118, 58)
WATER_DEEP = (38, 60, 72)
WATER_LIGHT = (92, 130, 140)
CHALK = (232, 226, 210)

def _sky(img, draw):
    """Gradient sky: dust to slate."""
    for y in range(int(H * 0.62)):
        t = y / (H * 0.62)
        r = int(DUST[0] + (SLATE_TOP[0] - DUST[0]) * t)
        g = int(DUST[1] + (SLATE_TOP[1] - DUST[1]) * t)
        b = int(DUST[2] + (SLATE_TOP[2] - DUST[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))
    del draw

def _quarry_face(img):
    """Diagonal stratified quarry wall with ledges."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    top_y = int(H * 0.30)
    for k in range(26):
        y0 = top_y + k * 26 + int(6 * math.sin(k * 1.7))
        d.line((0, y0, W, y0), fill=(*SLATE_TOP, 140), width=2)
        x0 = int(rng.uniform(0, 400))
        d.line((x0, y0, x0 + int(rng.uniform(120, 480)), y0 + int(rng.uniform(18, 44))),
               fill=(*SLATE_BOT, 130), width=3)
    for k in range(8):
        x = int(rng.uniform(0, W))
        d.line((x, top_y + k * 70, x + rng.randint(-40, 40), int(H * 0.86)), fill=(*SLATE_TOP, 60), width=2)
    for k in range(4):
        y = top_y + 90 + k * 150
        pts = [(0, y)]
        for x in range(0, W + 40, 40):
            pts.append((x, y + int(14 * math.sin(x * 0.008 + k))))
        d.line(pts, fill=(*CHALK, 110), width=3)
    for k in range(12):
        x = int(rng.uniform(60, W - 60)); y = int(rng.uniform(top_y + 40, int(H * 0.80)))
        d.ellipse((x - 9, y - 9, x + 9, y + 9), outline=(20, 22, 24, 160), width=3)
    layer = layer.filter(ImageFilter.GaussianBlur(1))
    return Image.alpha_composite(img, layer)

def _water(img):
    """Rising water at the bottom: deep band with lit surface line."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    y_start = int(H * 0.86)
    for y in range(y_start, H):
        t = (y - y_start) / (H - y_start)
        r = int(WATER_LIGHT[0] + (WATER_DEEP[0] - WATER_LIGHT[0]) * t)
        g = int(WATER_LIGHT[1] + (WATER_DEEP[1] - WATER_LIGHT[1]) * t)
        b = int(WATER_LIGHT[2] + (WATER_DEEP[2] - WATER_LIGHT[2]) * t)
        d.line((0, y, W, y), fill=(r, g, b, 255))
    for k in range(7):
        y = y_start + 20 + k * 22
        pts = []
        for x in range(0, W + 24, 24):
            pts.append((x, y + int(6 * math.sin(x * 0.01 + k * 2.1))))
        d.line(pts, fill=(*CHALK, 70), width=2)
    layer = layer.filter(ImageFilter.GaussianBlur(2))
    return Image.alpha_composite(img, layer)

def _vignette(draw):
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(50 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(24, 26, 28, 50))
            draw.line((W - vv, vy, W, vy), fill=(24, 26, 28, 50))

def make_cover(mp, op):
    m = json.loads(Path(mp).read_text(encoding="utf-8"))
    title = m["title"]; author = m.get("author", "Barış Kısır"); model = m.get("model", "")
    img = Image.new("RGBA", (W, H), SLATE_BOT + (255,))
    draw = ImageDraw.Draw(img, "RGBA")
    _sky(img, draw)
    img = _quarry_face(img); draw = ImageDraw.Draw(img, "RGBA")
    img = _water(img); draw = ImageDraw.Draw(img, "RGBA")
    _vignette(draw)
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
