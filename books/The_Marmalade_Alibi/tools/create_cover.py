#!/usr/bin/env python3
"""Cover: The Marmalade Alibi — a warm kitchen scene: mason jars, a jam label, a knitting needle, a sugar thermometer."""

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
rng.seed(1104006)

# Palette: warm cream kitchen, marmalade orange, deep jam red, ink
KITCHEN_TOP = (232, 214, 182)
KITCHEN_BOT = (196, 160, 120)
MARMALADE = (214, 118, 40)
JAM = (150, 46, 34)
INK = (60, 48, 36)
CREAM = (246, 238, 220)

def _kitchen(img):
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(int(H * 0.62)):
        t = y / (H * 0.62)
        r = int(KITCHEN_TOP[0] + (KITCHEN_BOT[0] - KITCHEN_TOP[0]) * t)
        g = int(KITCHEN_TOP[1] + (KITCHEN_BOT[1] - KITCHEN_TOP[1]) * t)
        b = int(KITCHEN_TOP[2] + (KITCHEN_BOT[2] - KITCHEN_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))
    sq = 56
    y0 = int(H * 0.60)
    for row in range((H - y0) // sq + 2):
        for col in range(W // sq + 2):
            if (row + col) % 2 == 0:
                x0 = col * sq; yy = y0 + row * sq
                draw.rectangle((x0, yy, x0 + sq, yy + sq), fill=(*CREAM, 235))
    del draw

def _jars(img):
    """Row of preserve jars with labels on the table."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    jar_pos = [(240, 800), (520, 880), (820, 760), (1080, 840), (1340, 780)]
    for i, (cx, cy) in enumerate(jar_pos):
        jw = int(rng.uniform(150, 190)); jh = int(rng.uniform(210, 260))
        x0, y0 = cx - jw // 2, cy
        col = MARMALADE if i % 2 == 0 else JAM
        d.rounded_rectangle((x0, y0, x0 + jw, y0 + jh), radius=24, fill=(*col, 240))
        d.rounded_rectangle((x0 - 8, y0 - 26, x0 + jw + 8, y0 + 6), radius=12, fill=(*INK, 235))
        d.rectangle((x0 + 24, y0 + jh // 2 - 34, x0 + jw - 24, y0 + jh // 2 + 34), fill=(*CREAM, 255))
        d.rectangle((x0 + 24, y0 + jh // 2 - 34, x0 + jw - 24, y0 + jh // 2 + 34), outline=(*INK, 160), width=2)
        d.rounded_rectangle((x0 + 20, y0 + 24, x0 + 52, y0 + jh - 30), radius=10, fill=(255, 255, 255, 70))
    return Image.alpha_composite(img, layer)

def _props(img):
    """Knitting needles + wool ball, and a sugar thermometer leaning against a jar."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    bx, by, br = 240, int(H * 0.80), 70
    d.ellipse((bx - br, by - br, bx + br, by + br), fill=(*JAM, 220))
    for k in range(6):
        ang = k * math.pi / 3
        d.arc((bx - br, by - br, bx + br, by + br), math.degrees(ang), math.degrees(ang + 50), fill=(*JAM, 130), width=4)
    d.line((bx + br, by - 20, bx + br + 320, by + 40), fill=(*INK, 230), width=10)
    d.line((bx + br + 20, by - 10, bx + br + 340, by + 70), fill=(*INK, 230), width=10)
    tx, ty = int(W * 0.82), int(H * 0.72)
    d.rounded_rectangle((tx - 14, ty, tx + 14, ty + 400), radius=12, fill=(230, 232, 236, 255), outline=(*INK, 160), width=3)
    d.ellipse((tx - 14, ty + 380, tx + 14, ty + 420), fill=(255, 90, 70, 255))
    d.rectangle((tx - 5, ty + 20, tx + 5, ty + 340), fill=(255, 70, 60, 230))
    for k in range(9):
        d.line((tx + 8, ty + 40 + k * 38, tx + 24, ty + 40 + k * 38), fill=(*INK, 180), width=2)
    return Image.alpha_composite(img, layer)

def _spice_stars(draw):
    """Tiny citrus/cinnamon star specks floating in the air."""
    for k in range(70):
        x = int(rng.uniform(0, W)); y = int(rng.uniform(0, int(H * 0.6)))
        r = int(rng.uniform(1, 3))
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(*MARMALADE, 140))

def make_cover(mp, op):
    m = json.loads(Path(mp).read_text(encoding="utf-8"))
    title = m["title"]; author = m.get("author", "Barış Kısır"); model = m.get("model", "")
    img = Image.new("RGBA", (W, H), KITCHEN_BOT + (255,))
    _kitchen(img)
    img = _jars(img)
    img = _props(img); draw = ImageDraw.Draw(img, "RGBA")
    _spice_stars(draw)
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
