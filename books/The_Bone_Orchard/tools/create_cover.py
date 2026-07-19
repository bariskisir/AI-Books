#!/usr/bin/env python3
"""Cover: The Bone Orchard — a drowned Southern grove where the standing dead root and fruit."""

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
rng.seed(9102024)

# Sickly-sweet gothic palette — black water, bone white, pale fruit, moonlit green
WATER_TOP = (18, 26, 30)
WATER_BOT = (30, 48, 52)
MIST = (120, 140, 140)
BONE = (220, 216, 200)
FRUIT = (230, 210, 215)
FRUIT_GLOW = (255, 235, 240)
MOON = (220, 228, 222)

def _draw_sky(draw):
    for y in range(int(H * 0.42)):
        t = y / (H * 0.42)
        r = int(WATER_TOP[0] + (MIST[0] - WATER_TOP[0]) * t * 0.5)
        g = int(WATER_TOP[1] + (MIST[1] - WATER_TOP[1]) * t * 0.5)
        b = int(WATER_TOP[2] + (MIST[2] - WATER_TOP[2]) * t * 0.5)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

def _make_water():
    img = Image.new("RGBA", (W, H), (10, 14, 16, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    _draw_sky(draw)
    for y in range(int(H * 0.42), H):
        t = (y - H * 0.42) / (H * 0.58)
        r = int(MIST[0] + (WATER_BOT[0] - MIST[0]) * t)
        g = int(MIST[1] + (WATER_BOT[1] - MIST[1]) * t)
        b = int(MIST[2] + (WATER_BOT[2] - MIST[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))
    return img

def _draw_moon(base):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    mx, my = 420, 220
    d.ellipse((mx - 46, my - 46, mx + 46, my + 46), fill=(*MOON, 215))
    d.ellipse((mx - 56, my - 56, mx + 56, my + 56), fill=(*MOON, 16))
    layer = layer.filter(ImageFilter.GaussianBlur(5))
    return Image.alpha_composite(base, layer)

def _draw_trees(base):
    """Standing-dead trees rising from the flooded grove, each bearing pale fruit."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    base_y = int(H * 0.46)
    for _ in range(22):
        x = rng.randint(40, W - 40)
        hgt = rng.randint(260, 620)
        lean = rng.randint(-30, 30)
        top_y = base_y - hgt
        # trunk
        d.line((x, base_y, x + lean, top_y), fill=(*BONE, rng.randint(120, 200)), width=rng.randint(6, 16))
        # bare branches
        for _ in range(rng.randint(3, 6)):
            bx = x + rng.randint(-int(hgt*0.25), int(hgt*0.25))
            by = top_y + rng.randint(20, int(hgt*0.5))
            ex = bx + rng.randint(-90, 90); ey = by - rng.randint(40, 130)
            d.line((bx, by, ex, ey), fill=(*BONE, rng.randint(100, 180)), width=rng.randint(2, 5))
        # pale fruit
        for _ in range(rng.randint(2, 5)):
            fx = x + rng.randint(-60, 60); fy = top_y + rng.randint(40, int(hgt*0.7))
            fr = rng.randint(7, 14)
            d.ellipse((fx - fr, fy - fr, fx + fr, fy + fr), fill=(*FRUIT, 200))
            d.ellipse((fx - fr//2, fy - fr//2, fx + fr//2, fy + fr//2), fill=(*FRUIT_GLOW, 150))
    return Image.alpha_composite(base, layer)

def _draw_reflection(base):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(40):
        x = rng.randint(0, W); y = rng.randint(int(H * 0.5), H)
        fr = rng.randint(4, 9); a = rng.randint(20, 70)
        d.ellipse((x - fr, y - fr//2, x + fr, y + fr//2), fill=(*FRUIT, a))
    layer = layer.filter(ImageFilter.GaussianBlur(3))
    return Image.alpha_composite(base, layer)

def _draw_vignette(draw):
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(50 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 55))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 55))

def make_cover(mp, op):
    m = json.loads(Path(mp).read_text(encoding="utf-8"))
    title = m["title"]; author = m.get("author", "Barış Kısır"); model = m.get("model", "")
    img = _make_water(); draw = ImageDraw.Draw(img, "RGBA")
    img = _draw_moon(img); draw = ImageDraw.Draw(img, "RGBA")
    img = _draw_trees(img); draw = ImageDraw.Draw(img, "RGBA")
    img = _draw_reflection(img); draw = ImageDraw.Draw(img, "RGBA")
    _draw_vignette(draw)
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
