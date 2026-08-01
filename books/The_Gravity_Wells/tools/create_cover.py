#!/usr/bin/env python3
"""Cover: The Gravity Wells — twin rotating rings against deep space, a ship spine connecting them, stars."""

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
rng.seed(1912007)

# Palette: deep space, ring metal, spine warm, star white
SPACE_TOP = (4, 6, 16)
SPACE_BOT = (10, 14, 26)
RING = (150, 160, 180)
SPINE = (226, 178, 96)
STAR = (240, 244, 250)
DARK = (8, 10, 16)

def _space(img):
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(H):
        t = y / H
        r = int(SPACE_TOP[0] + (SPACE_BOT[0] - SPACE_TOP[0]) * t)
        g = int(SPACE_TOP[1] + (SPACE_BOT[1] - SPACE_TOP[1]) * t)
        b = int(SPACE_TOP[2] + (SPACE_BOT[2] - SPACE_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))
    # stars
    for k in range(260):
        x = int(rng.uniform(0, W)); y = int(rng.uniform(0, H))
        r = int(rng.uniform(1, 3))
        a = int(rng.uniform(80, 220))
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(*STAR, a))
    # nebula glow
    for k in range(3):
        nx, ny, nr = int(rng.uniform(0, W)), int(rng.uniform(0, H)), int(rng.uniform(120, 320))
        draw.ellipse((nx - nr, ny - nr, nx + nr, ny + nr), fill=(120, 90, 200, 16))
    del draw

def _rings(img):
    """Two rotating habitat rings connected by the spine, viewed from space."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = W // 2, int(H * 0.44)
    # spine
    d.rectangle((cx - 30, cy - 260, cx + 30, cy + 260), fill=(*SPINE, 230))
    for k in range(6):
        d.rectangle((cx - 30, cy - 220 + k * 90, cx + 30, cy - 220 + k * 90 + 22), fill=(*DARK, 160))
    # ring 1 (upper) — ellipse, perspective
    for off, rad, thick, col in [
        (0, 300, 60, RING), (0, 300, 14, SPINE),
    ]:
        d.ellipse((cx - rad, cy - 200 - off - 60, cx + rad, cy - 200 + off + 60), outline=(*col, 220), width=thick)
    # ring 2 (lower)
    for off, rad, thick, col in [
        (0, 380, 70, RING), (0, 380, 16, SPINE),
    ]:
        d.ellipse((cx - rad, cy + 160 - off - 70, cx + rad, cy + 160 + off + 70), outline=(*col, 210), width=thick)
    # landing lights on the rings
    for k in range(8):
        ang = k * math.pi / 4
        x1 = cx + 300 * math.cos(ang); y1 = cy - 200 + 60 * math.sin(ang)
        x2 = cx + 380 * math.cos(ang); y2 = cy + 160 + 70 * math.sin(ang)
        d.ellipse((x1 - 6, y1 - 6, x1 + 6, y1 + 6), fill=(*SPINE, 255))
        d.ellipse((x2 - 6, y2 - 6, x2 + 6, y2 + 6), fill=(*SPINE, 255))
    layer = layer.filter(ImageFilter.GaussianBlur(1))
    return Image.alpha_composite(img, layer)

def _make_cover(mp, op):
    m = json.loads(Path(mp).read_text(encoding="utf-8"))
    title = m["title"]; author = m.get("author", "Barış Kısır"); model = m.get("model", "")
    img = Image.new("RGBA", (W, H), SPACE_BOT + (255,))
    _space(img)
    img = _rings(img)
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
