#!/usr/bin/env python3
"""Cover: The Moscow Protocol — man in dark coat, breath misting in Moscow subway, red metro map reflected."""

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
    img = Image.new("RGBA", (W, H), (0,0,0,255)); draw = ImageDraw.Draw(img, "RGBA")
    # Brutalist concrete subway gradient — gray to dark
    for y in range(H):
        t = y/H
        r = int(85 - 50*t); g = int(90 - 50*t); b = int(100 - 55*t)
        draw.line((0,y,W,y), fill=(max(0,r),max(0,g),max(0,b),255))
    # Red metro map reflection glow
    red_glow = Image.new("RGBA", (W,H), (0,0,0,0)); gd = ImageDraw.Draw(red_glow)
    gd.ellipse((W//2-350, 1200, W//2+350, 1800), fill=(200,30,30,50))
    red_glow = red_glow.filter(ImageFilter.GaussianBlur(50))
    img = Image.alpha_composite(img, red_glow); draw = ImageDraw.Draw(img, "RGBA")
    # Subway platform edge
    draw.rectangle((0, 1400, W, 1440), fill=(30, 30, 32, 220))
    # Concrete columns
    for col_x in [200, 600, 1000, 1400]:
        draw.rectangle((col_x-25, 300, col_x+25, 1400), fill=(55, 55, 58, 200))
        # Column shadow
        draw.rectangle((col_x+25, 300, col_x+35, 1400), fill=(35, 35, 38, 180))
    # Red metro map reflected in window (right side)
    map_glow = Image.new("RGBA", (W,H), (0,0,0,0)); md = ImageDraw.Draw(map_glow)
    md.polygon([(W-100,500),(W,500),(W,900),(W-100,900)], fill=(200,30,30,80))
    md.polygon([(W-60,520),(W,540),(W,800),(W-60,820)], fill=(180,20,20,60))
    for i in range(5):
        ry = 560 + i*60
        md.line((W-80, ry, W, ry+10), fill=(220,180,80,50), width=2)
    map_glow = map_glow.filter(ImageFilter.GaussianBlur(5))
    img = Image.alpha_composite(img, map_glow); draw = ImageDraw.Draw(img, "RGBA")
    # Man in dark coat — center
    fx, fy = W//2, 1200
    draw.polygon([(fx-30, fy), (fx+30, fy), (fx+25, fy+200), (fx-25, fy+200)], fill=(12,10,8,230))
    draw.ellipse((fx-14, fy-45, fx+14, fy-8), fill=(10,8,8,230))
    draw.rectangle((fx-18, fy-65, fx+18, fy-42), fill=(8,6,6,230))
    draw.polygon([(fx-30, fy), (fx-22, fy+35), (fx+22, fy+35), (fx+30, fy)], fill=(18,15,12,230))
    # Breath mist
    for _ in range(10):
        bx = fx + random.randint(-15, 15)
        by = fy + random.randint(-55, -25)
        br = random.randint(6, 18)
        draw.ellipse((bx-br, by-br, bx+br, by+br), fill=(210,210,220,12+random.randint(0,12)))
    # White tile wall behind
    for tile_y in range(400, 1100, 60):
        draw.line((0, tile_y, W, tile_y), fill=(120,120,125,60), width=1)
    # Fluorescent light reflections
    for lx in range(100, W, 300):
        for ly in range(400, 800, 5):
            alpha = max(0, 30 - abs(ly-600)//10)
            draw.line((lx-15, ly, lx+15, ly), fill=(200,200,220,alpha))
    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op, "PNG", optimize=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", required=True, type=Path); p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    make_cover(ROOT/a.metadata if not a.metadata.is_absolute() else a.metadata, ROOT/a.out if not a.out.is_absolute() else a.out)

if __name__ == "__main__": main()