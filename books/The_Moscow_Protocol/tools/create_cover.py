#!/usr/bin/env python3
"""Cover: The Moscow Protocol — Kremlin silhouette, gray winter, red accents."""

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
    # Gray winter gradient — cold steel sky fading to dirty snow
    for y in range(H):
        t = y/H
        r = int(90 - 50*t); g = int(95 - 50*t); b = int(105 - 50*t)
        draw.line((0,y,W,y), fill=(max(0,r),max(0,g),max(0,b),255))
    # Red accent glow low on horizon
    glow = Image.new("RGBA", (W,H), (0,0,0,0)); gd = ImageDraw.Draw(glow)
    gd.ellipse((W//2-400, 1400, W//2+400, 1800), fill=(180,30,30,60))
    glow = glow.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img, glow); draw = ImageDraw.Draw(img, "RGBA")
    # Kremlin wall silhouette
    wall_y = 1300
    draw.rectangle((100, wall_y, W-100, wall_y+180), fill=(25, 25, 30, 220))
    # Crenellations (merlons) along top of wall
    for x in range(100, W-100, 45):
        draw.rectangle((x, wall_y-40, x+30, wall_y), fill=(25, 25, 30, 220))
    # Kremlin towers
    towers = [
        (200, 1200, 60, 120),   # left tower
        (W//2-40, 1150, 80, 150), # central Savior Tower
        (W-200, 1200, 60, 120)   # right tower
    ]
    for tx, ty, tw, th in towers:
        draw.rectangle((tx-tw//2, ty, tx+tw//2, ty+th), fill=(20, 20, 25, 220))
        # Spire
        spire_h = 60
        draw.polygon([(tx-tw//4, ty), (tx, ty-spire_h), (tx+tw//4, ty)], fill=(25, 25, 30, 220))
        # Red star at top of central tower
        if abs(tx - W//2) < 10:
            draw.polygon([(tx, ty-spire_h-25), (tx-12, ty-spire_h-5), (tx+12, ty-spire_h-5)], fill=(180,20,20,200))
            draw.polygon([(tx, ty-spire_h-25), (tx-10, ty-spire_h-15), (tx+10, ty-spire_h-15)], fill=(200,25,25,200))
    # Snowy ground
    draw.rectangle((0, wall_y+180, W, H), fill=(60, 65, 70, 200))
    # Coat silhouette — a figure in a long winter coat
    fx, fy = W//2 + 200, 1350
    # Coat body
    draw.polygon([(fx-35, fy), (fx+35, fy), (fx+30, fy+200), (fx-30, fy+200)], fill=(15, 12, 10, 200))
    # Head
    draw.ellipse((fx-15, fy-50, fx+15, fy-10), fill=(10, 10, 12, 200))
    # Hat
    draw.rectangle((fx-20, fy-70, fx+20, fy-45), fill=(10, 10, 12, 200))
    # Coat collar lifted
    draw.polygon([(fx-35, fy), (fx-25, fy+30), (fx+25, fy+30), (fx+35, fy)], fill=(20, 18, 15, 200))
    # Breath mist
    for _ in range(8):
        bx = fx + random.randint(-20, 20)
        by = fy + random.randint(-60, -30)
        br = random.randint(8, 20)
        draw.ellipse((bx-br, by-br, bx+br, by+br), fill=(200,200,210,15+random.randint(0,15)))
    # Snowflakes
    for _ in range(80):
        sx = random.randint(0, W)
        sy = random.randint(0, H)
        sr = random.randint(1, 3)
        draw.ellipse((sx-sr, sy-sr, sx+sr, sy+sr), fill=(220,220,230,40+random.randint(0,60)))
    # Red accent line across lower third
    draw.line((0, 1920, W, 1920), fill=(180, 40, 40, 200), width=3)
    # Title panel
    draw.line((240, 2000, W-240, 2000), fill=(180, 40, 40, 180), width=2)
    draw.line((240, H-180, W-240, H-180), fill=(180, 40, 40, 80), width=1)
    tf = font("georgiab.ttf", 100); af = font("arialbd.ttf", 40); sf = font("arial.ttf", 28)
    y = centered(draw, 2020, ["A SPY THRILLER"], sf, (180, 40, 40), 6)
    y += 30
    y = centered(draw, y, wrap(draw, title.upper(), tf, 1200), tf, (210, 205, 200), 10)
    y += 50
    centered(draw, y, [author], af, (190, 185, 180), 6)
    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op, "PNG", optimize=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", required=True, type=Path); p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    make_cover(ROOT/a.metadata if not a.metadata.is_absolute() else a.metadata, ROOT/a.out if not a.out.is_absolute() else a.out)

if __name__ == "__main__": main()