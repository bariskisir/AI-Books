#!/usr/bin/env python3
"""Cover: Lighthouse of the Ninth Tide — the last keeper lights the lamp nine times against a once-a-generation storm."""

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
rng.seed(9112024)

# Bruised-storm palette — violet tempest, foam white, lamp gold, wet rock
STORM_TOP = (40, 30, 70)      # deep violet zenith
STORM_MID = (90, 60, 110)
STORM_BOT = (150, 110, 140)   # bruised horizon
SEA = (50, 60, 80)
FOAM = (220, 225, 230)
LAMP = (255, 200, 110)
ROCK = (45, 48, 55)

def _make_sky():
    img = Image.new("RGBA", (W, H), (15, 10, 30, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(H):
        t = y / H
        if t < 0.4:
            lt = t / 0.4
            r = int(STORM_TOP[0] + (STORM_MID[0] - STORM_TOP[0]) * lt)
            g = int(STORM_TOP[1] + (STORM_MID[1] - STORM_TOP[1]) * lt)
            b = int(STORM_TOP[2] + (STORM_MID[2] - STORM_TOP[2]) * lt)
        elif t < 0.52:
            lt = (t - 0.4) / 0.12
            r = int(STORM_MID[0] + (STORM_BOT[0] - STORM_MID[0]) * lt)
            g = int(STORM_MID[1] + (STORM_BOT[1] - STORM_MID[1]) * lt)
            b = int(STORM_MID[2] + (STORM_BOT[2] - STORM_MID[2]) * lt)
        else:
            gt = min(1, (t - 0.52) / 0.48)
            r = int(STORM_BOT[0] - gt * 60)
            g = int(STORM_BOT[1] - gt * 55)
            b = int(STORM_BOT[2] - gt * 45)
        draw.line((0, y, W, y), fill=(r, g, b, 255))
    return img

def _draw_clouds(base):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(20):
        x = rng.randint(0, W); y = rng.randint(0, int(H * 0.4))
        w = rng.randint(120, 320); h = rng.randint(30, 70)
        col = tuple(int(c * rng.uniform(0.8, 1.2)) for c in STORM_MID) + (rng.randint(30, 90),)
        d.ellipse((x - w//2, y - h//2, x + w//2, y + h//2), fill=col)
    layer = layer.filter(ImageFilter.GaussianBlur(22))
    return Image.alpha_composite(base, layer)

def _draw_waves(draw, base_y, amp, freq, phase, color, alpha):
    pts = []
    for x in range(0, W + 6, 6):
        y = base_y + int(amp * math.sin(freq * x + phase))
        pts.append((x, y))
    pts.extend([(W, H), (0, H)])
    draw.polygon(pts, fill=(*color, alpha))

def _draw_rock(draw):
    pts = [(W//2 - 150, H), (W//2 - 110, int(H*0.74)), (W//2 - 40, int(H*0.7)),
           (W//2 + 60, int(H*0.71)), (W//2 + 130, int(H*0.75)), (W//2 + 160, H)]
    draw.polygon(pts, fill=(*ROCK, 255))

def _draw_lighthouse(base):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx = W // 2
    base_y = int(H * 0.72)
    top_y = int(H * 0.40)
    # tower (tapered)
    d.polygon([(cx - 34, base_y), (cx + 34, base_y), (cx + 20, top_y), (cx - 20, top_y)], fill=(*ROCK, 255))
    d.polygon([(cx - 34, base_y), (cx + 34, base_y), (cx + 20, top_y), (cx - 20, top_y)], outline=(20, 22, 26, 200))
    # stripes
    for k in range(4):
        yy = base_y - (base_y - top_y) * (k + 0.5) / 4
        d.line((cx - 32 + 2*k, yy - 14, cx + 32 - 2*k, yy - 14), fill=(225, 225, 220, 180), width=10)
    # lantern room
    d.rectangle((cx - 24, top_y - 44, cx + 24, top_y), fill=(30, 30, 34, 255))
    # lamp glow
    d.ellipse((cx - 14, top_y - 34, cx + 14, top_y - 6), fill=(*LAMP, 255))
    d.ellipse((cx - 60, top_y - 80, cx + 60, top_y + 40), fill=(*LAMP, 30))
    d.ellipse((cx - 120, top_y - 140, cx + 120, top_y + 100), fill=(*LAMP, 12))
    # roof
    d.polygon([(cx - 28, top_y - 44), (cx + 28, top_y - 44), (cx, top_y - 70)], fill=(20, 20, 24, 255))
    layer = layer.filter(ImageFilter.GaussianBlur(1))
    return Image.alpha_composite(base, layer)

def _draw_rain(base):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(260):
        x = rng.randint(0, W); y = rng.randint(0, H)
        ln = rng.randint(20, 60)
        a = rng.randint(20, 90)
        d.line((x, y, x - 8, y + ln), fill=(*FOAM, a), width=1)
    return Image.alpha_composite(base, layer)

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
    img = _make_sky(); draw = ImageDraw.Draw(img, "RGBA")
    img = _draw_clouds(img); draw = ImageDraw.Draw(img, "RGBA")
    _draw_waves(draw, int(H * 0.66), 26, 0.004, 0.0, SEA, 240)
    _draw_waves(draw, int(H * 0.74), 30, 0.003, 1.4, (40, 50, 70), 245)
    img = _draw_rain(img); draw = ImageDraw.Draw(img, "RGBA")
    _draw_rock(draw)
    img = _draw_lighthouse(img); draw = ImageDraw.Draw(img, "RGBA")
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
