#!/usr/bin/env python3
"""Cover: The Salt Bells — a drowned chapel visible through green water, a girl diver, bells rising, moonlight."""

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
rng.seed(2215010)

# Palette: sea-green water, moonlight silver, bell bronze, chapel stone
SEA_TOP = (60, 120, 110)
SEA_BOT = (16, 44, 48)
MOON = (226, 240, 236)
BRONZE = (196, 140, 74)
STONE = (96, 108, 104)
SILVER = (200, 220, 216)

def _sea(img):
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(H):
        t = y / H
        r = int(SEA_TOP[0] + (SEA_BOT[0] - SEA_TOP[0]) * t)
        g = int(SEA_TOP[1] + (SEA_BOT[1] - SEA_TOP[1]) * t)
        b = int(SEA_TOP[2] + (SEA_BOT[2] - SEA_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))
    # moonlight shaft from above
    d = ImageDraw.Draw(img, "RGBA")
    d.polygon([(int(W * 0.36), 0), (int(W * 0.64), 0), (int(W * 0.80), H)], fill=(*MOON, 22))
    # bubbles
    for k in range(120):
        x = int(rng.uniform(0, W)); y = int(rng.uniform(0, H))
        r = int(rng.uniform(2, 7))
        d.ellipse((x - r, y - r, x + r, y + r), outline=(*SILVER, int(rng.uniform(40, 110))), width=2)
    del draw

def _chapel(img):
    """The drowned chapel on the seabed: tower, arched windows, a great bell."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    y0 = int(H * 0.78)
    # seabed
    d.rectangle((0, y0, W, H), fill=(20, 40, 42, 250))
    # chapel body
    d.rectangle((int(W * 0.30), y0 - int(H * 0.20), int(W * 0.70), y0), fill=(*STONE, 220))
    # tower
    d.rectangle((int(W * 0.64), y0 - int(H * 0.34), int(W * 0.76), y0), fill=(*STONE, 230))
    # tower top
    d.polygon([(int(W * 0.62), y0 - int(H * 0.34)), (int(W * 0.70), y0 - int(H * 0.42)), (int(W * 0.78), y0 - int(H * 0.34))], fill=(*STONE, 230))
    # arched windows (dark)
    for k in range(3):
        wx0 = int(W * 0.34) + k * int(W * 0.12)
        d.polygon([(wx0, y0 - int(H * 0.18)), (wx0 + 40, y0 - int(H * 0.18)), (wx0 + 40, y0 - int(H * 0.12)), (wx0 + 20, y0 - int(H * 0.09)), (wx0, y0 - int(H * 0.12))], fill=(10, 20, 22, 255))
    # the great bell, fallen by the door
    bx, by, br = int(W * 0.52), y0 - int(H * 0.08), 60
    d.arc((bx - br, by - br, bx + br, by + br), 180, 360, fill=(*BRONZE, 240), width=14)
    d.rectangle((bx - 8, by, bx + 8, by + 30), fill=(*BRONZE, 230))
    # seaweed
    for k in range(9):
        wx = int(rng.uniform(int(W * 0.26), int(W * 0.76)))
        d.line((wx, y0, wx + int(rng.uniform(-20, 20)), y0 - int(rng.uniform(30, 90))), fill=(*SEA_TOP, 160), width=4)
    layer = layer.filter(ImageFilter.GaussianBlur(1))
    return Image.alpha_composite(img, layer)

def _diver(img):
    """A girl diver descending, reaching toward the bell, silver light on her."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    sx, sy = int(W * 0.40), int(H * 0.52)
    # body
    d.line((sx, sy, sx, sy + 60), fill=(*SILVER, 235), width=10)
    # head
    d.ellipse((sx - 12, sy - 34, sx + 12, sy - 8), fill=(*SILVER, 235))
    # arms reaching down-forward
    d.line((sx, sy + 6, sx + 40, sy + 46), fill=(*SILVER, 220), width=7)
    d.line((sx, sy + 6, sx - 34, sy + 40), fill=(*SILVER, 220), width=7)
    # legs
    d.line((sx, sy + 60, sx + 22, sy + 96), fill=(*SILVER, 210), width=8)
    d.line((sx, sy + 60, sx - 22, sy + 96), fill=(*SILVER, 210), width=8)
    # hair trailing up
    d.line((sx, sy - 20, sx + 18, sy - 56), fill=(*SILVER, 180), width=6)
    d.line((sx, sy - 20, sx - 16, sy - 54), fill=(*SILVER, 180), width=6)
    # a bubble ring around her
    d.ellipse((sx - 90, sy - 90, sx + 90, sy + 90), outline=(*SILVER, 70), width=3)
    layer = layer.filter(ImageFilter.GaussianBlur(1))
    return Image.alpha_composite(img, layer)

def _make_cover(mp, op):
    m = json.loads(Path(mp).read_text(encoding="utf-8"))
    title = m["title"]; author = m.get("author", "Barış Kısır"); model = m.get("model", "")
    img = Image.new("RGBA", (W, H), SEA_BOT + (255,))
    _sea(img)
    img = _chapel(img)
    img = _diver(img)
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
