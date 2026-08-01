#!/usr/bin/env python3
"""Cover: The Amber Loom — a dark loom threaded with glowing amber warps against a cold hill."""

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
rng.seed(9023055)

# Palette: cold dusk, wool grey, amber glow, deep umber
DUSK_TOP = (44, 46, 62)
DUSK_BOT = (74, 62, 74)
WOOL = (168, 160, 150)
AMBER = (216, 148, 52)
AMBER_HOT = (255, 196, 90)
UMBER = (54, 34, 26)

def _dusk(img):
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(int(H * 0.55)):
        t = y / (H * 0.55)
        r = int(DUSK_TOP[0] + (DUSK_BOT[0] - DUSK_TOP[0]) * t)
        g = int(DUSK_TOP[1] + (DUSK_BOT[1] - DUSK_TOP[1]) * t)
        b = int(DUSK_TOP[2] + (DUSK_BOT[2] - DUSK_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))
    pts = [(0, int(H * 0.55))]
    for x in range(0, W + 40, 40):
        y = int(H * 0.55) + int(90 * math.sin(x * 0.004 + 1.2)) + 60
        pts.append((x, y))
    pts += [(W, H), (0, H)]
    draw.polygon(pts, fill=(*WOOL, 60))
    draw.ellipse((int(W * 0.18), int(H * 0.10), int(W * 0.18) + 130, int(H * 0.10) + 130), fill=(*WOOL, 200))
    del draw

def _loom(img):
    """A simple upright loom frame with glowing amber warps, center stage."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    frame_w = 860; frame_h = 1300
    fx = (W - frame_w) // 2; fy = int(H * 0.46)
    d.rectangle((fx, fy, fx + frame_w, fy + 26), fill=(*UMBER, 255))
    d.rectangle((fx, fy + frame_h - 26, fx + frame_w, fy + frame_h), fill=(*UMBER, 255))
    d.rectangle((fx, fy, fx + 26, fy + frame_h), fill=(*UMBER, 255))
    d.rectangle((fx + frame_w - 26, fy, fx + frame_w, fy + frame_h), fill=(*UMBER, 255))
    for k in range(16):
        x = fx + 60 + k * (frame_w - 120) / 15
        pts = [(x, fy + 26)]
        for y in range(fy + 26, fy + frame_h - 26, 12):
            sway = 8 * math.sin((y - fy) * 0.01 + k * 0.9)
            pts.append((x + sway, y))
        d.line(pts, fill=(*AMBER, 220), width=4)
    for k in range(5):
        y = fy + 140 + k * 230
        d.line((fx + 20, y, fx + frame_w - 20, y + 30), fill=(*AMBER_HOT, 120), width=8)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dg = ImageDraw.Draw(glow)
    dg.ellipse((fx - 200, fy - 200, fx + frame_w + 200, fy + frame_h + 200), fill=(*AMBER, 40))
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    return Image.alpha_composite(Image.alpha_composite(img, glow), layer)

def _weave_strands(img):
    """Wispy thread curls rising from the loom into the sky."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for k in range(7):
        x = int(rng.uniform(300, 1300)); y = int(rng.uniform(H * 0.42, H * 0.5))
        pts = [(x, y)]
        for s in range(22):
            x += int(rng.uniform(-26, 26)); y -= int(rng.uniform(14, 40))
            pts.append((x, y))
        d.line(pts, fill=(*AMBER, 130), width=3)
    layer = layer.filter(ImageFilter.GaussianBlur(1))
    return Image.alpha_composite(img, layer)

def make_cover(mp, op):
    m = json.loads(Path(mp).read_text(encoding="utf-8"))
    title = m["title"]; author = m.get("author", "Barış Kısır"); model = m.get("model", "")
    img = Image.new("RGBA", (W, H), DUSK_BOT + (255,))
    _dusk(img)
    img = _loom(img)
    img = _weave_strands(img)
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
