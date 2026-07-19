#!/usr/bin/env python3
"""Cover: When the Wire Sings — a deaf linesman feels the residual hum of the fallen grid across a post-grid continent."""

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
rng.seed(1302024)

# Post-grid dusk palette — copper wire, indigo dusk, signal amber, faded teal
DUSK_TOP = (30, 34, 64)
DUSK_BOT = (90, 80, 110)
WIRE = (170, 110, 60)
WIRE_BRIGHT = (230, 170, 90)
SIGNAL = (255, 190, 90)
TEAL = (70, 110, 120)
GROUND = (40, 44, 50)

def _make_dusk():
    img = Image.new("RGBA", (W, H), (12, 14, 28, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(H):
        t = y / H
        if t < 0.6:
            lt = t / 0.6
            r = int(DUSK_TOP[0] + (DUSK_BOT[0] - DUSK_TOP[0]) * lt)
            g = int(DUSK_TOP[1] + (DUSK_BOT[1] - DUSK_TOP[1]) * lt)
            b = int(DUSK_TOP[2] + (DUSK_BOT[2] - DUSK_TOP[2]) * lt)
        else:
            gt = min(1, (t - 0.6) / 0.4)
            r = int(DUSK_BOT[0] - gt * 40)
            g = int(DUSK_BOT[1] - gt * 36)
            b = int(DUSK_BOT[2] - gt * 40)
        draw.line((0, y, W, y), fill=(r, g, b, 255))
    return img

def _draw_pylons(base):
    """Falling lattice towers carrying taut, singing wire."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # two rows of pylons receding
    def pylon(x, base_y, scale):
        top_y = base_y - int(360 * scale)
        # body
        d.line((x - 26*scale, base_y, x - 8*scale, top_y), fill=(*WIRE, 200), width=max(2, int(5*scale)))
        d.line((x + 26*scale, base_y, x + 8*scale, top_y), fill=(*WIRE, 200), width=max(2, int(5*scale)))
        d.line((x - 26*scale, base_y, x + 26*scale, base_y), fill=(*WIRE, 200), width=max(2, int(5*scale)))
        # cross arms
        d.line((x - 60*scale, top_y + 60*scale, x + 60*scale, top_y + 60*scale), fill=(*WIRE, 180), width=max(2, int(4*scale)))
        d.line((x - 44*scale, top_y + 130*scale, x + 44*scale, top_y + 130*scale), fill=(*WIRE, 160), width=max(2, int(4*scale)))
        d.line((x - 10*scale, top_y, x, top_y + 40*scale), fill=(*WIRE, 180), width=2)
        d.line((x + 10*scale, top_y, x, top_y + 40*scale), fill=(*WIRE, 180), width=2)
    for k in range(7):
        s = 0.4 + 0.09 * k
        x = int(W * (0.08 + 0.13 * k))
        pylon(x, int(H * 0.96), s)
    return Image.alpha_composite(base, layer)

def _draw_wires(base):
    """Singing transmission lines — sine hums glowing with signal."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for level in range(3):
        base_y = int(H * (0.42 + 0.10 * level))
        amp = 24 + 10 * level
        for phase in range(2):
            pts = []
            for x in range(0, W + 8, 8):
                y = base_y + int(amp * math.sin(x * 0.004 + phase * 1.7 + level))
                pts.append((x, y))
            a = 150 - 30 * level
            d.line(pts, fill=(*WIRE_BRIGHT, a), width=2)
            # signal pulses
            for px in range(120, W, 220):
                py = base_y + int(amp * math.sin(px * 0.004 + phase * 1.7 + level))
                d.ellipse((px - 5, py - 5, px + 5, py + 5), fill=(*SIGNAL, 200))
    layer = layer.filter(ImageFilter.GaussianBlur(1))
    return Image.alpha_composite(base, layer)

def _draw_linesman(base):
    """A small figure at the base of a pylon, hand on the wire, feeling the hum."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx = int(W * 0.5); cy = int(H * 0.82)
    d.ellipse((cx - 10, cy - 40, cx + 10, cy - 20), fill=(20, 20, 26, 240))   # head
    d.rectangle((cx - 8, cy - 20, cx + 8, cy + 6), fill=(20, 20, 26, 240))    # torso
    d.polygon([(cx - 13, cy + 6), (cx + 13, cy + 6), (cx + 9, cy + 34), (cx - 9, cy + 34)], fill=(20, 20, 26, 220))
    # arm reaching to wire (vibration rings)
    d.line((cx + 8, cy - 12, cx + 40, cy - 4), fill=(20, 20, 26, 240), width=5)
    for r in range(1, 5):
        d.ellipse((cx + 40 - r*6, cy - 4 - r*6, cx + 40 + r*6, cy - 4 + r*6), outline=(*SIGNAL, 200 - r*40), width=2)
    return Image.alpha_composite(base, layer)

def _draw_ground(draw):
    draw.rectangle((0, int(H * 0.9), W, H), fill=(*GROUND, 255))

def _draw_vignette(draw):
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(45 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 55))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 55))

def make_cover(mp, op):
    m = json.loads(Path(mp).read_text(encoding="utf-8"))
    title = m["title"]; author = m.get("author", "Barış Kısır"); model = m.get("model", "")
    img = _make_dusk(); draw = ImageDraw.Draw(img, "RGBA")
    img = _draw_pylons(img); draw = ImageDraw.Draw(img, "RGBA")
    img = _draw_wires(img); draw = ImageDraw.Draw(img, "RGBA")
    _draw_ground(draw)
    img = _draw_linesman(img); draw = ImageDraw.Draw(img, "RGBA")
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
