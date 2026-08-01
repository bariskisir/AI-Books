#!/usr/bin/env python3
"""Cover: The Dust Reckoning — a dust-storm horizon over a ploughed field, a lone windbreak, sepia tones."""

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
rng.seed(1306001)

# Palette: dust sepia, storm brown, dry sky, seed-sack green
SKY_TOP = (214, 196, 162)
SKY_BOT = (176, 150, 112)
STORM = (122, 92, 60)
DRY = (148, 118, 82)
SEED = (96, 108, 66)
DARK = (58, 46, 34)

def _sky(img):
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(int(H * 0.46)):
        t = y / (H * 0.46)
        r = int(SKY_TOP[0] + (SKY_BOT[0] - SKY_TOP[0]) * t)
        g = int(SKY_TOP[1] + (SKY_BOT[1] - SKY_TOP[1]) * t)
        b = int(SKY_TOP[2] + (SKY_BOT[2] - SKY_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))
    del draw

def _dust_wall(img):
    """The oncoming dust storm: a tall brown wall on the right horizon."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    base_y = int(H * 0.46)
    wall = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dw = ImageDraw.Draw(wall)
    for k in range(46):
        x0 = int(W * (0.42 + 0.012 * k))
        hgt = int(H * (0.10 + 0.010 * k))
        alpha = int(90 + 3.2 * k)
        dw.rectangle((x0, base_y - hgt, W, base_y + int(H * 0.2)), fill=(*STORM, min(alpha, 255)))
    wall = wall.filter(ImageFilter.GaussianBlur(14))
    layer = Image.alpha_composite(layer, wall)
    # dust motes
    d = ImageDraw.Draw(layer)
    for k in range(240):
        x = int(rng.uniform(0, W)); y = int(rng.uniform(0, int(H * 0.7)))
        r = int(rng.uniform(1, 4))
        d.ellipse((x - r, y - r, x + r, y + r), fill=(*DRY, int(rng.uniform(40, 120))))
    return Image.alpha_composite(img, layer)

def _field(img):
    """Ploughed furrows converging to the horizon; a windbreak line of young trees."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    y0 = int(H * 0.46)
    for k in range(16):
        x_center = W // 2 + int((k - 7.5) * 46)
        pts = []
        for y in range(y0, H, 14):
            t = (y - y0) / (H - y0)
            x = W // 2 + (x_center - W // 2) * t
            pts.append((x, y))
        d.line(pts, fill=(*DARK, int(150 - 5 * k)), width=3)
    # windbreak: a thin row of tiny tree silhouettes across mid-field
    for k in range(14):
        x = 120 + k * 100
        y = y0 + int(H * 0.16)
        hgt = int(rng.uniform(40, 70))
        d.rectangle((x - 4, y - hgt, x + 4, y), fill=(*SEED, 200))
        d.ellipse((x - 16, y - hgt - 14, x + 16, y - hgt + 10), fill=(*SEED, 200))
    layer = layer.filter(ImageFilter.GaussianBlur(1))
    return Image.alpha_composite(img, layer)

def _seed_sack(img):
    """A small seed sack at the lower left, leaning on the frame."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    sx, sy = 120, int(H * 0.86)
    d.polygon([(sx, sy), (sx + 200, sy - 20), (sx + 230, sy + 60), (sx + 40, sy + 80)], fill=(*SEED, 230), outline=(*DARK, 220), width=4)
    d.line((sx + 200, sy - 20, sx + 240, sy - 60), fill=(*DARK, 220), width=5)
    d.text = None
    # stitch line
    d.line((sx + 60, sy + 18, sx + 210, sy + 30), fill=(*DARK, 160), width=2)
    return Image.alpha_composite(img, layer)

def _vignette(draw):
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(45 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(40, 30, 20, 40))
            draw.line((W - vv, vy, W, vy), fill=(40, 30, 20, 40))

def make_cover(mp, op):
    m = json.loads(Path(mp).read_text(encoding="utf-8"))
    title = m["title"]; author = m.get("author", "Barış Kısır"); model = m.get("model", "")
    img = Image.new("RGBA", (W, H), SKY_BOT + (255,))
    _sky(img)
    img = _field(img)
    img = _dust_wall(img)
    img = _seed_sack(img); draw = ImageDraw.Draw(img, "RGBA")
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
