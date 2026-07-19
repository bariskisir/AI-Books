#!/usr/bin/env python3
"""Cover: A Cartography of Small Fires — a cartographer mapping a village stitched from a hundred minor combustions."""

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
rng.seed(3302024)

# Quiet dusk palette — parchment, ember, ink, warm hearth
PARCH_TOP = (225, 214, 188)
PARCH_BOT = (200, 182, 150)
EMBER = (200, 90, 50)
EMBER_SOFT = (230, 150, 90)
INK = (60, 52, 44)
HEARTH = (180, 70, 45)

def _make_parchment():
    img = Image.new("RGBA", (W, H), (20, 18, 14, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(H):
        t = y / H
        r = int(PARCH_TOP[0] + (PARCH_BOT[0] - PARCH_TOP[0]) * t)
        g = int(PARCH_TOP[1] + (PARCH_BOT[1] - PARCH_TOP[1]) * t)
        b = int(PARCH_TOP[2] + (PARCH_BOT[2] - PARCH_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))
    return img

def _draw_contour_lines(draw):
    """Topographic map contours of the valley."""
    for k in range(14):
        cy = int(H * (0.12 + 0.052 * k))
        amp = 60 + 18 * k
        pts = []
        for x in range(0, W + 8, 8):
            y = cy + int(amp * math.sin(x * 0.0023 + k * 0.5) + 22 * math.sin(x * 0.007 + k))
            pts.append((x, y))
        a = int(120 - 6 * k)
        draw.line(pts, fill=(*INK, a), width=2)

def _draw_fires(base):
    """Small deliberate fires scattered like map markers."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    spots = [(260, 760), (520, 980), (880, 700), (1180, 930), (1380, 680),
             (400, 1220), (700, 1380), (1040, 1280), (1300, 1180), (240, 1080)]
    for (x, y) in spots:
        flick = rng.uniform(0.8, 1.2)
        # glow
        d.ellipse((x - 34 * flick, y - 34 * flick, x + 34 * flick, y + 34 * flick), fill=(*EMBER_SOFT, 30))
        # flame body
        d.polygon([(x, y - 46 * flick), (x - 16 * flick, y + 12 * flick), (x + 16 * flick, y + 12 * flick)], fill=(*EMBER, 200))
        d.polygon([(x, y - 26 * flick), (x - 8 * flick, y + 10 * flick), (x + 8 * flick, y + 10 * flick)], fill=(255, 210, 140, 220))
        # marker ring
        d.ellipse((x - 20, y - 20, x + 20, y + 20), outline=(*INK, 90), width=2)
    layer = layer.filter(ImageFilter.GaussianBlur(1))
    return Image.alpha_composite(base, layer)

def _draw_compass(base):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = 1280, 1700
    r = 90
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(*INK, 120), width=3)
    d.polygon([(cx, cy - r), (cx - 14, cy), (cx, cy), (cx + 14, cy)], fill=(*HEARTH, 200))
    d.polygon([(cx, cy + r), (cx - 14, cy), (cx, cy), (cx + 14, cy)], fill=(*INK, 160))
    d.line((cx, cy - r, cx, cy + r), fill=(*INK, 120), width=2)
    d.line((cx - r, cy, cx + r, cy), fill=(*INK, 120), width=2)
    return Image.alpha_composite(base, layer)

def _draw_vignette(draw):
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(40 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(40, 30, 20, 45))
            draw.line((W - vv, vy, W, vy), fill=(40, 30, 20, 45))

def make_cover(mp, op):
    m = json.loads(Path(mp).read_text(encoding="utf-8"))
    title = m["title"]; author = m.get("author", "Barış Kısır"); model = m.get("model", "")
    img = _make_parchment(); draw = ImageDraw.Draw(img, "RGBA")
    _draw_contour_lines(draw)
    img = _draw_fires(img); draw = ImageDraw.Draw(img, "RGBA")
    img = _draw_compass(img); draw = ImageDraw.Draw(img, "RGBA")
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
