#!/usr/bin/env python3
"""Cover: The Saltmarsh Kings — a tide-born daughter, a contested estuary, and a marsh that chooses its own king."""

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
rng.seed(7172024)

# Estuary palette — tidal greys, reed green, salt white, bruised copper sky
SKY_TOP = (70, 78, 92)       # bruised slate at zenith
SKY_MID = (120, 130, 132)
SKY_BOT = (190, 196, 188)    # pale salt haze at horizon
WATER = (90, 110, 120)
REED = (110, 122, 86)
SALT = (225, 228, 220)
COPPER = (180, 120, 70)
BONE = (210, 205, 190)

def _draw_stars(draw):
    for _ in range(120):
        sx = rng.randint(0, W); sy = rng.randint(0, int(H * 0.28))
        sr = rng.uniform(0.4, 2.0); a = rng.randint(40, 170)
        b = rng.randint(200, 255)
        draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=(b, b - 8, b - 20, a))

def _make_sky():
    img = Image.new("RGBA", (W, H), (20, 24, 30, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(H):
        t = y / H
        if t < 0.42:
            lt = t / 0.42
            r = int(SKY_TOP[0] + (SKY_MID[0] - SKY_TOP[0]) * lt)
            g = int(SKY_TOP[1] + (SKY_MID[1] - SKY_TOP[1]) * lt)
            b = int(SKY_TOP[2] + (SKY_MID[2] - SKY_TOP[2]) * lt)
        elif t < 0.55:
            lt = (t - 0.42) / 0.13
            r = int(SKY_MID[0] + (SKY_BOT[0] - SKY_MID[0]) * lt)
            g = int(SKY_MID[1] + (SKY_BOT[1] - SKY_MID[1]) * lt)
            b = int(SKY_MID[2] + (SKY_BOT[2] - SKY_MID[2]) * lt)
        else:
            gt = min(1, (t - 0.55) / 0.45)
            r = int(SKY_BOT[0] - gt * 70)
            g = int(SKY_BOT[1] - gt * 70)
            b = int(SKY_BOT[2] - gt * 55)
        draw.line((0, y, W, y), fill=(r, g, b, 255))
    return img

def _draw_tide(draw, base_y, amp, freq, phase, color, alpha):
    pts = []
    for x in range(0, W + 6, 6):
        y = base_y + int(amp * math.sin(freq * x + phase))
        pts.append((x, y))
    pts.extend([(W, H), (0, H)])
    draw.polygon(pts, fill=(*color, alpha))

def _draw_moon(base):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    mx, my = 1230, 200
    d.ellipse((mx - 50, my - 50, mx + 50, my + 50), fill=(235, 230, 210, 220))
    d.ellipse((mx - 60, my - 60, mx + 60, my + 60), fill=(235, 230, 210, 14))
    layer = layer.filter(ImageFilter.GaussianBlur(5))
    return Image.alpha_composite(base, layer)

def _draw_reeds(base):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(160):
        x = rng.randint(0, W); y = rng.randint(int(H * 0.62), H)
        hgt = rng.randint(40, 130)
        sway = rng.randint(-12, 12)
        col = tuple(int(c * rng.uniform(0.7, 1.1)) for c in REED) + (rng.randint(120, 210),)
        d.line((x, y, x + sway, y - hgt), fill=col, width=rng.randint(1, 3))
        d.ellipse((x + sway - 2, y - hgt - 3, x + sway + 2, y - hgt + 3), fill=(*COPPER, 120))
    return Image.alpha_composite(base, layer)

def _draw_child(base):
    """The tide-born daughter standing at the waterline, water in her chest, no fear."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx = W // 2; cy = int(H * 0.66)
    # body
    d.ellipse((cx - 9, cy - 34, cx + 9, cy - 18), fill=(30, 34, 38, 235))   # head
    d.rectangle((cx - 7, cy - 18, cx + 7, cy + 4), fill=(30, 34, 38, 235))  # torso
    d.polygon([(cx - 12, cy + 4), (cx + 12, cy + 4), (cx + 8, cy + 26), (cx - 8, cy + 26)], fill=(30, 34, 38, 220))  # skirt
    # faint glow at the chest — the tide within
    d.ellipse((cx - 6, cy - 14, cx + 6, cy - 2), fill=(*WATER, 80))
    d.ellipse((cx - 3, cy - 11, cx + 3, cy - 5), fill=(200, 220, 230, 120))
    return Image.alpha_composite(base, layer)

def _draw_runes(base):
    """Salt-crystal kings' marks drifting on the water."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(26):
        x = rng.randint(60, W - 60); y = rng.randint(int(H * 0.58), int(H * 0.86))
        r = rng.randint(3, 9); a = rng.randint(30, 110)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(*SALT, a))
    layer = layer.filter(ImageFilter.GaussianBlur(1))
    return Image.alpha_composite(base, layer)

def _draw_vignette(draw):
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(45 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 50))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 50))

def make_cover(mp, op):
    m = json.loads(Path(mp).read_text(encoding="utf-8"))
    title = m["title"]; author = m.get("author", "Barış Kısır"); model = m.get("model", "")
    img = _make_sky(); draw = ImageDraw.Draw(img, "RGBA")
    _draw_stars(draw)
    img = _draw_moon(img); draw = ImageDraw.Draw(img, "RGBA")
    # water layers
    _draw_tide(draw, int(H * 0.56), 22, 0.004, 0.0, WATER, 235)
    _draw_tide(draw, int(H * 0.64), 30, 0.003, 1.6, (110, 130, 138), 240)
    img = _draw_runes(img); draw = ImageDraw.Draw(img, "RGBA")
    img = _draw_reeds(img); draw = ImageDraw.Draw(img, "RGBA")
    img = _draw_child(img); draw = ImageDraw.Draw(img, "RGBA")
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
