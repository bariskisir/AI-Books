#!/usr/bin/env python3
"""Cover: The Chrome Gospel — a neon-soaked flooded megacity at night, a chrome chip motif, wet reflections."""

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
rng.seed(1407002)

# Palette: night wet, cyan neon, magenta neon, chrome
NIGHT_TOP = (10, 16, 26)
NIGHT_BOT = (16, 22, 34)
CYAN = (80, 220, 230)
MAGENTA = (230, 80, 190)
CHROME = (190, 210, 215)
DARK = (12, 14, 22)

def _night(img):
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(H):
        t = y / H
        r = int(NIGHT_TOP[0] + (NIGHT_BOT[0] - NIGHT_TOP[0]) * t)
        g = int(NIGHT_TOP[1] + (NIGHT_BOT[1] - NIGHT_TOP[1]) * t)
        b = int(NIGHT_TOP[2] + (NIGHT_BOT[2] - NIGHT_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))
    del draw

def _stilt_city(img):
    """Flooded city: stilt-houses with neon lines and a big data-tower."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # water line
    d.rectangle((0, int(H * 0.66), W, H), fill=(8, 12, 20, 235))
    # stilt houses (two rows)
    for row in (0, 1):
        y0 = int(H * (0.52 + 0.16 * row))
        for k in range(10):
            x0 = int(rng.uniform(20, W - 160))
            wdt = int(rng.uniform(90, 160)); hgt = int(rng.uniform(60, 120))
            # stilts
            d.line((x0 + 14, y0 + hgt, x0 + 14, y0 + hgt + 60), fill=(*DARK, 200), width=6)
            d.line((x0 + wdt - 14, y0 + hgt, x0 + wdt - 14, y0 + hgt + 60), fill=(*DARK, 200), width=6)
            d.rectangle((x0, y0, x0 + wdt, y0 + hgt), fill=(*DARK, 225))
            # neon window
            col = CYAN if k % 2 else MAGENTA
            d.rectangle((x0 + 20, y0 + 20, x0 + wdt - 20, y0 + 50), fill=(*col, 200))
            # reflection
            d.line((x0 + 14, y0 + hgt + 60, x0 + 10, y0 + hgt + 140), fill=(*col, 70), width=4)
    # data-tower (the Spire)
    tx = int(W * 0.70)
    tw = 90
    d.rectangle((tx - tw // 2, int(H * 0.18), tx + tw // 2, int(H * 0.66)), fill=(*DARK, 240))
    for k in range(7):
        d.rectangle((tx - tw // 2 + 8, int(H * 0.20) + k * 52, tx + tw // 2 - 8, int(H * 0.20) + k * 52 + 16), fill=(*CYAN, 190))
    d.ellipse((tx - tw // 2 - 40, int(H * 0.16), tx + tw // 2 + 40, int(H * 0.24)), fill=(*CYAN, 120))
    layer = layer.filter(ImageFilter.GaussianBlur(1))
    return Image.alpha_composite(img, layer)

def _chip(img):
    """A large chrome memory chip floating lower-left, wired to the city."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy, s = int(W * 0.24), int(H * 0.80), 150
    d.rounded_rectangle((cx - s, cy - s, cx + s, cy + s), radius=24, fill=(*CHROME, 235), outline=(*CYAN, 220), width=6)
    # pins
    for k in range(8):
        d.rectangle((cx - s + 12 + k * 36, cy - s - 22, cx - s + 34 + k * 36, cy - s - 4), fill=(*CYAN, 230))
        d.rectangle((cx - s + 12 + k * 36, cy + s + 4, cx - s + 34 + k * 36, cy + s + 22), fill=(*CYAN, 230))
    # circuit traces
    d.line((cx - 90, cy, cx + 90, cy), fill=(*MAGENTA, 220), width=6)
    d.line((cx, cy - 90, cx, cy + 90), fill=(*MAGENTA, 220), width=6)
    d.ellipse((cx - 26, cy - 26, cx + 26, cy + 26), fill=(*DARK, 255))
    d.ellipse((cx - 12, cy - 12, cx + 12, cy + 12), fill=(*CYAN, 255))
    return Image.alpha_composite(img, layer)

def _rain(draw):
    for k in range(160):
        x = int(rng.uniform(0, W)); y = int(rng.uniform(0, H))
        ln = int(rng.uniform(10, 30))
        draw.line((x, y, x - 3, y + ln), fill=(*CHROME, 60), width=1)

def make_cover(mp, op):
    m = json.loads(Path(mp).read_text(encoding="utf-8"))
    title = m["title"]; author = m.get("author", "Barış Kısır"); model = m.get("model", "")
    img = Image.new("RGBA", (W, H), NIGHT_BOT + (255,))
    _night(img)
    img = _stilt_city(img)
    img = _chip(img); draw = ImageDraw.Draw(img, "RGBA")
    _rain(draw)
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
