#!/usr/bin/env python3
"""Cover: Red Phoenix Rising — city skyline at sunset with hero silhouette."""

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

    # Sunset gradient: deep red -> orange -> yellow -> dark purple sky
    for y in range(H):
        t = y / H
        if t < 0.3:
            # Upper sky: deep purple to red
            r = int(180 - 80 * (t / 0.3))
            g = int(60 - 40 * (t / 0.3))
            b = int(120 - 60 * (t / 0.3))
        elif t < 0.55:
            # Mid sky: red to orange
            lt = (t - 0.3) / 0.25
            r = int(100 + 155 * lt)
            g = int(20 + 120 * lt)
            b = int(60 - 50 * lt)
        else:
            # Lower sky: orange to dark
            lt = (t - 0.55) / 0.45
            r = int(255 - 180 * lt)
            g = int(140 - 110 * lt)
            b = int(10 - 10 * lt)
        draw.line((0,y,W,y), fill=(max(0,min(255,r)),max(0,min(255,g)),max(0,min(255,b)),255))

    # Sun glow
    sun = Image.new("RGBA", (W,H), (0,0,0,0)); sd = ImageDraw.Draw(sun)
    sd.ellipse((W//2-250, 900, W//2+250, 1400), fill=(255,200,80,180))
    sd.ellipse((W//2-150, 950, W//2+150, 1350), fill=(255,220,120,220))
    sun = sun.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img, sun); draw = ImageDraw.Draw(img, "RGBA")

    # City skyline silhouette
    buildings = [
        (200, 1300, 80, 400), (280, 1280, 60, 350), (340, 1350, 100, 300),
        (440, 1200, 70, 500), (510, 1250, 90, 450), (600, 1300, 80, 380),
        (680, 1150, 100, 550), (780, 1180, 70, 480), (850, 1220, 60, 400),
        (910, 1300, 90, 350), (1000, 1250, 100, 400), (1100, 1200, 80, 500),
        (1180, 1280, 70, 380), (1250, 1320, 90, 320), (1340, 1300, 80, 350),
    ]
    skyline_color = (10, 8, 15, 230)
    for bx, by, bw, bh in buildings:
        draw.rectangle((bx, by, bx+bw, by+bh), fill=skyline_color)
        # Windows
        for wy in range(by+20, by+bh-20, 45):
            for wx in range(bx+10, bx+bw-10, 25):
                if (wx // 25 + wy // 45) % 3 == 0:
                    draw.rectangle((wx, wy, wx+8, wy+12), fill=(255,200,100,80))

    # Tallest tower with spire
    tx, ty, tw, th = 740, 950, 80, 750
    draw.rectangle((tx, ty, tx+tw, ty+th), fill=skyline_color)
    # Spire
    draw.polygon([(tx+tw//2, ty-120), (tx+tw//2-15, ty), (tx+tw//2+15, ty)], fill=skyline_color)

    # Hero silhouette on rooftop
    hx, hy = 760, 950
    # Body
    draw.line((hx, hy, hx, hy+100), fill=(5,5,10,255), width=8)
    # Arms outstretched
    draw.line((hx-60, hy+20, hx+60, hy+20), fill=(5,5,10,255), width=6)
    # Head
    draw.ellipse((hx-12, hy-30, hx+12, hy-6), fill=(5,5,10,255))
    # Cape billowing
    draw.polygon([(hx-50, hy-10), (hx-120, hy+60), (hx-80, hy+100), (hx-40, hy+40)], fill=(60,15,15,200))
    draw.polygon([(hx+50, hy-10), (hx+120, hy+60), (hx+80, hy+100), (hx+40, hy+40)], fill=(60,15,15,200))
    # Phoenix emblem on chest (small circle)
    draw.ellipse((hx-10, hy+30, hx+10, hy+50), fill=(220,80,30,200))

    # Smoke/ash particles
    for _ in range(80):
        x = int(W * __import__('random').random())
        y = int(800 + 600 * __import__('random').random())
        r = int(2 + 5 * __import__('random').random())
        a = int(20 + 40 * __import__('random').random())
        draw.ellipse((x-r, y-r, x+r, y+r), fill=(200,150,80,a))

    # Title panel — light rectangle at bottom
    draw.line((300, H-150, W-300, H-150), fill=(255, 180, 60, 120), width=2)

    # Title
    tf = font("georgiab.ttf", 110)
    af = font("arialbd.ttf", 42)
    sf = font("arial.ttf", 28)

    y = 2010
    tw_lines = wrap(draw, title.upper(), tf, 1200)
    if len(tw_lines) > 1:
        tf2 = font("georgiab.ttf", 80)
        tw_lines = wrap(draw, title.upper(), tf2, 1200)
        y = centered(draw, y, tw_lines, tf2, (255, 190, 80), 8)
    else:
        y = centered(draw, y, tw_lines, tf, (255, 190, 80), 8)

    y += 30
    centered(draw, y, ["SUPERHERO NOVEL"], sf, (200, 180, 160), 4)
    y += 35
    centered(draw, y, [author], af, (220, 200, 180), 6)

    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op, "PNG", optimize=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", required=True, type=Path); p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    make_cover(ROOT/a.metadata if not a.metadata.is_absolute() else a.metadata, ROOT/a.out if not a.out.is_absolute() else a.out)

if __name__ == "__main__": main()