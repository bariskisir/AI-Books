#!/usr/bin/env python3
"""Cover: The Bone Garden — clean medical thriller with strong title readability."""

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

def font(name, size):
    candidates = [FONT_DIR / name, FONT_DIR / "arialbd.ttf",
                  FONT_DIR / "arial.ttf", FONT_DIR / "georgia.ttf"]
    for c in candidates:
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
    img = Image.new("RGBA", (W, H), (0,0,0,255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Clean gradient: dark charcoal top to clinical white bottom
    for y in range(H):
        t = y / H
        r = int(35 - 15*t)
        g = int(30 - 10*t)
        b = int(35 - 15*t)
        if t > 0.55:
            fade = (t - 0.55) / 0.45
            r = int(20 + (245-20)*fade)
            g = int(20 + (245-20)*fade)
            b = int(20 + (245-20)*fade)
        draw.line((0,y,W,y), fill=(max(0,min(255,r)),max(0,min(255,g)),max(0,min(255,b)),255))

    # Large subtle biohazard symbol (faded into background)
    cx, cy = W//2, 550
    bh = Image.new("RGBA", (W,H), (0,0,0,0))
    bd = ImageDraw.Draw(bh)
    for angle_offset in [0, 120, 240]:
        rad = math.radians(angle_offset)
        ax = cx + int(150*math.cos(rad))
        ay = cy + int(150*math.sin(rad))
        bd.pieslice([ax-220, ay-220, ax+220, ay+220],
                    -60+angle_offset, 60+angle_offset, fill=(180,30,30,60))
    bd.ellipse([cx-75, cy-75, cx+75, cy+75], fill=(180,30,30,40))
    bd.ellipse([cx-130, cy-130, cx+130, cy+130], outline=(180,30,30,50), width=6)
    bh = bh.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img, bh)
    draw = ImageDraw.Draw(img, "RGBA")

    # Clean petri dish - centered, subtle
    pd = Image.new("RGBA", (W,H), (0,0,0,0))
    pdd = ImageDraw.Draw(pd)
    dish_cx, dish_cy = cx, 950
    pdd.ellipse([dish_cx-200, dish_cy-200, dish_cx+200, dish_cy+200],
                fill=(255,255,255,20), outline=(200,200,200,80), width=3)
    # A few bacterial colonies in red
    import random
    random.seed(42)
    for _ in range(15):
        gx = dish_cx + int((random.random()-0.5)*320)
        gy = dish_cy + int((random.random()-0.5)*320)
        gr = int(12 + 30*random.random())
        pdd.ellipse([gx-gr, gy-gr, gx+gr, gy+gr],
                    fill=(160,25,25,int(100+80*random.random())))
        if gr > 15:
            pdd.ellipse([gx-gr//3, gy-gr//3, gx+gr//3, gy+gr//3],
                        fill=(200,50,50,int(80+60*random.random())))
    pd = pd.filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(img, pd)
    draw = ImageDraw.Draw(img, "RGBA")

    # DNA helix motif (left side, subtle)
    for i in range(24):
        yy = 1300 + i * 20
        xx = 200 + int(30 * math.sin(i * 0.8))
        dx = xx + 60 + int(30 * math.sin((i+1) * 0.8))
        draw.line([(xx, yy), (dx, yy+20)], fill=(180,40,40,int(60+40*math.sin(i*0.5))), width=2)

    # TITLE PANEL — dark panel with white text (high contrast)
    panel_top = 1880
    draw.rectangle((0, panel_top, W, H), fill=(25,25,30,255))

    # Accent line
    draw.line((300, panel_top+30, W-300, panel_top+30), fill=(180,40,40,255), width=5)
    draw.line((300, H-120, W-300, H-120), fill=(180,40,40,120), width=2)

    # Genre line
    gf = font("arial.ttf", 30)
    centered(draw, panel_top+55, ["A MEDICAL THRILLER"], gf, (180,40,40), 4)

    # Title — large, bold, black on white panel
    # Use Arial Bold (available) at larger size
    tf = font("arialbd.ttf", 110)
    title_lines = wrap(draw, title.upper(), tf, 1300)
    title_y = panel_top + 130
    if len(title_lines) > 1:
        # Reduce font size if wrapping
        tf = font("arialbd.ttf", 85)
        title_lines = wrap(draw, title.upper(), tf, 1300)
    centered(draw, title_y, title_lines, tf, (255,255,255), 8)

    # Author
    af = font("arialbd.ttf", 38)
    centered(draw, H-90, [author], af, (180,40,40), 6)

    # Small red accent square top-left
    draw.rectangle((40, 40, 70, 70), fill=(180,40,40,200))

    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op, "PNG", optimize=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    make_cover(ROOT/a.metadata if not a.metadata.is_absolute() else a.metadata,
               ROOT/a.out if not a.out.is_absolute() else a.out)

if __name__ == "__main__":
    main()