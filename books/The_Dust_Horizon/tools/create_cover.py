#!/usr/bin/env python3
"""Cover: The Dust Horizon — a Western frontier at sunset."""

from __future__ import annotations
import argparse, json, math
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
    # Desert sunset gradient
    for y in range(H):
        t = y/H
        r = int(180-100*t); g = int(120-80*t); b = int(50-20*t)
        draw.line((0,y,W,y), fill=(max(0,r),max(0,g),max(0,b),255))
    # Sun disc
    sun = Image.new("RGBA", (W,H), (0,0,0,0)); sd = ImageDraw.Draw(sun)
    sd.ellipse((W//2-200, 800, W//2+200, 1200), fill=(255,200,80,200))
    sun = sun.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, sun); draw = ImageDraw.Draw(img, "RGBA")
    # Horizon mesas
    for i, (cy, cw, ch) in enumerate([(1400, 1800, 300), (1250, 1400, 250), (1350, 1000, 200)]):
        draw.polygon([(W//2-cw//2, cy+ch), (W//2-cw//2, cy), (W//2, cy-ch//2), (W//2+cw//2, cy), (W//2+cw//2, cy+ch)], fill=(30+20*i, 20+15*i, 15+10*i, 220))
    # Silhouette rider
    rx, ry = W//2 - 200, 1550
    draw.line((rx-60,ry-100,rx,ry,rx+60,ry-100), fill=(15,12,10,255), width=12)
    draw.ellipse((rx-18,ry-130,rx+18,ry-94), fill=(15,12,10,255))
    # Cacti silhouettes
    for cx in range(200, W, 300):
        draw.rectangle((cx,ry+120,cx+8,ry+280), fill=(15,12,10,180))
        draw.rectangle((cx-30,ry+150,cx+20,ry+160), fill=(15,12,10,180))
        draw.rectangle((cx+8,ry+180,cx+40,ry+190), fill=(15,12,10,180))
    # Dust particles
    for _ in range(60):
        x,y = (int(W*__import__('random').random()), int(800+800*__import__('random').random()))
        r = int(3+6*__import__('random').random())
        draw.ellipse((x-r,y-r,x+r,y+r), fill=(220,180,120,int(30+40*__import__('random').random())))
    # Title panel
    draw.line((220,2020,W-220,2020), fill=(220,180,100,200), width=3)
    draw.line((220,H-180,W-220,H-180), fill=(220,180,100,120), width=2)
    tf = font("georgiab.ttf", 110); af = font("arialbd.ttf", 42)
    y = centered(draw, 2070, ["WESTERN FRONTIER NOVEL"], font("arial.ttf",30), (200,160,100), 6)
    y += 40
    y = centered(draw, y, wrap(draw, title.upper(), tf, 1200), tf, (220,185,120), 10)
    y += 60
    centered(draw, y, [author], af, (200,190,170), 6)
    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op, "PNG", optimize=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", required=True, type=Path); p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    make_cover(ROOT/a.metadata if not a.metadata.is_absolute() else a.metadata, ROOT/a.out if not a.out.is_absolute() else a.out)

if __name__ == "__main__": main()