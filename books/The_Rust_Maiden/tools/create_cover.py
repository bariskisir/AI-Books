#!/usr/bin/env python3
"""Cover: The Rust Maiden — Dieselpunk Dust Bowl with giant walker."""

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
    # Rust / bronze / dust gradient
    for y in range(H):
        t = y/H
        r = int(180-80*t); g = int(100-60*t); b = int(30-20*t)
        draw.line((0,y,W,y), fill=(max(0,r),max(0,g),max(0,b),255))
    # Dust storm haze layer
    haze = Image.new("RGBA", (W, H), (0,0,0,0)); hd = ImageDraw.Draw(haze)
    for _ in range(80):
        x = int(random.random()*W); y = int(random.random()*H*0.75)
        s = int(10+30*random.random()); a = int(20+40*random.random())
        hd.ellipse((x-s,y-s,x+s,y+s), fill=(200,160,100,a))
    haze = haze.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, haze); draw = ImageDraw.Draw(img, "RGBA")
    # Giant walker silhouette (Iron Judge)
    wx, wy = W//2, int(H*0.45)
    # Body
    draw.polygon([(wx-120,wy-180),(wx+120,wy-180),(wx+160,wy),(wx-160,wy)], fill=(25,20,15,200))
    # Head / cockpit
    draw.rectangle((wx-40,wy-240,wx+40,wy-180), fill=(25,20,15,200))
    # Gun barrel
    draw.line((wx+120,wy-150,wx+280,wy-200), fill=(25,20,15,200), width=14)
    draw.line((wx+120,wy-150,wx+280,wy-200), fill=(60,50,40,100), width=10)
    # Legs
    draw.line((wx-80,wy,wx-120,wy+320), fill=(25,20,15,200), width=28)
    draw.line((wx+80,wy,wx+120,wy+320), fill=(25,20,15,200), width=28)
    draw.line((wx-120,wy+320,wx-160,wy+380), fill=(25,20,15,200), width=22)
    draw.line((wx+120,wy+320,wx+160,wy+380), fill=(25,20,15,200), width=22)
    # Knee joints glow (orange)
    draw.ellipse((wx-145,wy+140,wx-95,wy+190), fill=(220,120,40,150))
    draw.ellipse((wx+95,wy+140,wx+145,wy+190), fill=(220,120,40,150))
    # Small mechanic figure in front of walker
    mx, my = wx, wy+80
    draw.line((mx-12,my+40,mx,my,mx+12,my+40), fill=(30,25,20,255), width=5)
    draw.ellipse((mx-6,my-30,mx+6,my-18), fill=(30,25,20,255))
    # Wrench in hand
    draw.line((mx+12,my+10,mx+30,my-10), fill=(180,120,60,255), width=4)
    draw.ellipse((mx+28,my-16,mx+32,my-4), fill=(180,120,60,255))
    # Dust particles / debris around walker
    for _ in range(40):
        x = int(wx-300+600*random.random()); y = int(wy+100+200*random.random())
        r = int(2+6*random.random()); a = int(30+60*random.random())
        draw.ellipse((x-r,y-r,x+r,y+r), fill=(180,140,80,a))
    # Sun through dust
    sun_x, sun_y = W//2, int(H*0.15)
    sun = Image.new("RGBA", (W,H), (0,0,0,0)); sd = ImageDraw.Draw(sun)
    sd.ellipse((sun_x-120,sun_y-120,sun_x+120,sun_y+120), fill=(255,200,100,80))
    sun = sun.filter(ImageFilter.GaussianBlur(25))
    img = Image.alpha_composite(img, sun); draw = ImageDraw.Draw(img, "RGBA")
    # Title panel at bottom
    draw.line((200,H-160,W-200,H-160), fill=(200,150,70,120), width=2)
    # Rust ornament lines in panel
    for i in range(10):
        yp = 1980 + i*50
        draw.line((100,yp,W-100,yp), fill=(120,60,30,int(10+15*random.random())), width=1)
    tf = font("georgiab.ttf", 120); af = font("arialbd.ttf", 44)
    sf = font("arial.ttf", 28)
    y = centered(draw, 2030, ["DIESELPUNK NOVEL"], sf, (200,150,70), 6)
    y += 50
    y = centered(draw, y, wrap(draw, title.upper(), tf, 1300), tf, (220,180,110), 10)
    y += 70
    centered(draw, y, [f"by {author}"], af, (200,180,150), 6)
    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op, "PNG", optimize=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", required=True, type=Path); p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    make_cover(ROOT/a.metadata if not a.metadata.is_absolute() else a.metadata, ROOT/a.out if not a.out.is_absolute() else a.out)

if __name__ == "__main__": main()