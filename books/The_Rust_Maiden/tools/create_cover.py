#!/usr/bin/env python3
"""Cover: The Rust Maiden — rusty RX-7 walker silhouetted against burning refinery dawn, Iron Judge on horizon."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import (
    _standard_cover_font,
    _standard_cover_repair_text,
    _standard_cover_wrap,
    _standard_cover_center,
    _standard_cover_title_font,
    _standard_cover_metadata_from_locals,
    _standard_cover_resolve_title,
    _standard_cover_resolve_author,
    _draw_standard_cover_title_panel,
)


ROOT = Path(__file__).resolve().parents[3]
FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560

def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    for c in [FONT_DIR / name, FONT_DIR / "georgia.ttf", FONT_DIR / "arial.ttf"]:
        if c.exists(): return ImageFont.truetype(str(c), size)
    return ImageFont.load_default()

def wrap(draw, text, fnt, mw):
    words, lines, cur = text.split(), [], []
    for w in words:
        p = " ".join([*cur, w])
        if draw.textbbox((0,0), p, font=fnt)[2] <= mw: cur.append(w)
        else: lines.append(" ".join(cur)); cur = [w]
    if cur: lines.append(" ".join(cur))
    return lines

def centered(draw, y, lines, fnt, fill, gap):
    for line in lines:
        bb = draw.textbbox((0,0), line, font=fnt)
        draw.text(((W-(bb[2]-bb[0]))//2, y), line, font=fnt, fill=fill)
        y += bb[3]-bb[1] + gap
    return y

def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title, author = m["title"], m.get("author", "Barış Kısır")
    model = m.get("model", "")
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Burning refinery dawn sky
    for y in range(H):
        t = y / H
        if t < 0.3:
            r, g, b = 220 - 80 * t / 0.3, 140 - 60 * t / 0.3, 50 - 30 * t / 0.3
        elif t < 0.6:
            r, g, b = 160 - 80 * (t - 0.3) / 0.3, 90 - 60 * (t - 0.3) / 0.3, 30 - 20 * (t - 0.3) / 0.3
        else:
            r, g, b = 90 - 50 * (t - 0.6) / 0.4, 40 - 25 * (t - 0.6) / 0.4, 15 - 10 * (t - 0.6) / 0.4
        draw.line((0, y, W, y), fill=(max(0, int(r)), max(0, int(g)), max(0, int(b)), 255))

    # Burning refinery glow on horizon
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((W // 2 - 500, 200, W // 2 + 500, 600), fill=(255, 180, 80, 80))
    glow = glow.filter(ImageFilter.GaussianBlur(50))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Dust haze
    haze = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(haze)
    for _ in range(60):
        x0, y0, x1, y1 = int(random.random() * W), int(random.random() * H * 0.7), int(10 + 30 * random.random()), int(10 + 30 * random.random())
        hd.ellipse((min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)), fill=(200, 160, 100, int(15 + 35 * random.random())))
    haze = haze.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(img, haze)

    # Rusty RX-7 walker silhouette
    wx, wy = W // 2 - 100, int(H * 0.4)
    # Body - angular, weathered
    draw.polygon([(wx - 80, wy - 120), (wx + 80, wy - 120), (wx + 110, wy + 20), (wx - 110, wy + 20)], fill=(35, 25, 18, 220))
    # Cockpit/head
    draw.rectangle((wx - 30, wy - 160, wx + 30, wy - 120), fill=(35, 25, 18, 220))
    # Gun arm
    draw.line((wx + 80, wy - 80, wx + 200, wy - 120), fill=(35, 25, 18, 220), width=12)
    draw.line((wx + 80, wy - 80, wx + 200, wy - 120), fill=(60, 45, 30, 100), width=8)
    # Legs (spider-like)
    draw.line((wx - 60, wy + 20, wx - 100, wy + 300), fill=(35, 25, 18, 220), width=22)
    draw.line((wx + 60, wy + 20, wx + 100, wy + 300), fill=(35, 25, 18, 220), width=22)
    draw.line((wx - 100, wy + 300, wx - 140, wy + 380), fill=(35, 25, 18, 220), width=18)
    draw.line((wx + 100, wy + 300, wx + 140, wy + 380), fill=(35, 25, 18, 220), width=18)
    # Knee glow (faint orange)
    draw.ellipse((wx - 115, wy + 120, wx - 75, wy + 160), fill=(200, 100, 30, 120))
    draw.ellipse((wx + 75, wy + 120, wx + 115, wy + 160), fill=(200, 100, 30, 120))

    # Iron Judge silhouette on horizon
    ijx, ijy = W // 2 + 300, int(H * 0.25)
    draw.polygon([(ijx - 60, ijy + 60), (ijx + 60, ijy + 60), (ijx + 80, ijy - 40), (ijx - 80, ijy - 40)], fill=(15, 12, 10, 180))
    draw.rectangle((ijx - 20, ijy - 70, ijx + 20, ijy - 40), fill=(15, 12, 10, 180))
    draw.line((ijx + 60, ijy - 20, ijx + 140, ijy - 50), fill=(15, 12, 10, 180), width=8)
    draw.line((ijx - 40, ijy + 60, ijx - 60, ijy + 200), fill=(15, 12, 10, 180), width=14)
    draw.line((ijx + 40, ijy + 60, ijx + 60, ijy + 200), fill=(15, 12, 10, 180), width=14)

    # Dust particles
    for _ in range(50):
        x0, y0, x1, y1 = int(wx - 300 + 600 * random.random()), int(wy + 100 + 200 * random.random()), int(2 + 5 * random.random()), int(2 + 5 * random.random())
        draw.ellipse((min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)), fill=(180, 140, 80, int(25 + 55 * random.random())))

    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op, "PNG", optimize=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", required=True, type=Path); p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    make_cover(ROOT/a.metadata if not a.metadata.is_absolute() else a.metadata, ROOT/a.out if not a.out.is_absolute() else a.out)

if __name__ == "__main__": main()