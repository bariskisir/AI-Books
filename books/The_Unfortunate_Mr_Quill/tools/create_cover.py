#!/usr/bin/env python3
"""Cover: Single shoe on rocky shore at low tide, gray sea mist, man's silhouette walking away along the tide line, shore gray/mist white/shoe brown."""

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


ROOT = Path(__file__).resolve().parents[3]; FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560

def lerp_color(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def font(n,s):
    for c in [FONT_DIR/n, FONT_DIR/"georgia.ttf", FONT_DIR/"arial.ttf"]:
        if c.exists(): return ImageFont.truetype(str(c), s)
    return ImageFont.load_default()

def wrap(d,t,f,w):
    wo=t.split(); li=[]; cu=[]
    for wd in wo:
        p=" ".join([*cu,wd])
        if d.textbbox((0,0),p,font=f)[2]<=w: cu.append(wd)
        else: li.append(" ".join(cu)); cu=[wd]
    if cu: li.append(" ".join(cu))
    return li

def centered(d,y,li,f,fl,g):
    for l in li:
        bb=d.textbbox((0,0),l,font=f)
        d.text(((W-(bb[2]-bb[0]))//2,y),l,font=f,fill=fl)
        y+=bb[3]-bb[1]+g
    return y

def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    ti = m["title"]
    au = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (60, 65, 70, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Gray sea mist gradient
    for y in range(H):
        t = y / H
        if t < 0.3:
            c = lerp_color((80, 85, 90), (100, 105, 110), t / 0.3)
        elif t < 0.6:
            c = lerp_color((100, 105, 110), (120, 125, 130), (t - 0.3) / 0.3)
        else:
            c = lerp_color((120, 125, 130), (60, 65, 70), (t - 0.6) / 0.4)
        draw.line((0, y, W, y), fill=c)

    # Sky mist layers
    mist = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(mist)
    for _ in range(30):
        mx = random.randint(0, W)
        my = random.randint(0, 800)
        mr = random.randint(50, 200)
        a = random.randint(20, 50)
        md.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(150, 155, 160, a))
    mist = mist.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, mist)

    # Sea / horizon line
    sea_y = 500
    draw.line([(0, sea_y), (W, sea_y)], fill=(90, 95, 100), width=2)
    # Sea surface
    for y in range(sea_y, sea_y + 200):
        t = (y - sea_y) / 200
        r = int(70 - 20 * t)
        g = int(75 - 20 * t)
        b = int(85 - 20 * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))
    # Wave crests
    for x in range(0, W, 10):
        wy = sea_y + int(8 * math.sin(x * 0.03) + 5 * math.sin(x * 0.07))
        draw.line([(x, wy), (x + 4, wy + 1)], fill=(140, 145, 150, 80), width=2)

    # Rocky shore at low tide (foreground)
    shore_y = 1100
    # Wet sand
    draw.rectangle([(0, shore_y), (W, H)], fill=(55, 50, 45))
    for x in range(0, W, 4):
        sy = shore_y + int(5 * math.sin(x * 0.01) + 3 * math.sin(x * 0.03))
        draw.line([(x, sy), (x, H)], fill=(50, 45, 40), width=3)

    # Tide pools (reflective patches on sand)
    for _ in range(20):
        px = random.randint(50, W - 50)
        py = shore_y + random.randint(10, 400)
        pr = random.randint(8, 30)
        draw.ellipse([px - pr, py - pr // 2, px + pr, py + pr // 2],
                     fill=(70, 75, 80, random.randint(60, 120)))

    # Rocks scattered on shore
    for _ in range(15):
        rx = random.randint(30, W - 30)
        ry = shore_y + random.randint(10, 500)
        rr = random.randint(6, 25)
        draw.ellipse([rx - rr, ry - rr, rx + rr, ry + rr],
                     fill=(40 + random.randint(-10, 10), 35 + random.randint(-10, 10), 30 + random.randint(-10, 10)))

    # Single shoe in foreground (center-left)
    shoe_x, shoe_y = 500, 1450
    # Shoe body
    draw.ellipse([shoe_x - 35, shoe_y - 20, shoe_x + 35, shoe_y + 20], fill=(55, 40, 30))
    draw.ellipse([shoe_x - 30, shoe_y - 15, shoe_x + 30, shoe_y + 15], fill=(65, 48, 35))
    # Shoe opening
    draw.ellipse([shoe_x - 10, shoe_y - 22, shoe_x + 10, shoe_y - 10], fill=(40, 30, 22))
    # Sole
    draw.ellipse([shoe_x - 32, shoe_y + 12, shoe_x + 32, shoe_y + 22], fill=(40, 30, 22))
    # Lace hole
    draw.ellipse([shoe_x + 5, shoe_y - 5, shoe_x + 10, shoe_y], fill=(30, 22, 15))
    # Shadow under shoe
    draw.ellipse([shoe_x - 40, shoe_y + 22, shoe_x + 40, shoe_y + 30], fill=(35, 30, 28, 80))

    # Man's silhouette walking away along tide line
    man_x, man_base = 900, 1150
    dark = (30, 28, 25)
    # Legs (walking pose)
    draw.line([(man_x - 5, man_base), (man_x - 15, man_base + 80)], fill=dark, width=8)
    draw.line([(man_x + 5, man_base), (man_x + 20, man_base + 75)], fill=dark, width=8)
    # Body (coat)
    draw.ellipse([man_x - 20, man_base - 110, man_x + 20, man_base], fill=dark)
    # Head
    draw.ellipse([man_x - 12, man_base - 145, man_x + 12, man_base - 115], fill=dark)
    # Hat
    draw.rectangle([man_x - 22, man_base - 165, man_x + 22, man_base - 148], fill=(25, 22, 20))
    draw.rectangle([man_x - 28, man_base - 160, man_x + 28, man_base - 155], fill=(25, 22, 20))
    # Arm (swinging)
    draw.line([(man_x + 18, man_base - 80), (man_x + 40, man_base - 40)], fill=dark, width=6)
    draw.line([(man_x - 18, man_base - 80), (man_x - 35, man_base - 50)], fill=dark, width=6)
    # Footprints behind him
    for fi in range(5):
        fx = man_x - 20 - fi * 30
        fy = man_base + 80 + int(5 * math.sin(fi * 1.5))
        draw.ellipse([fx - 6, fy - 3, fx + 6, fy + 3], fill=(45, 40, 35, 80))

    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op, "PNG", optimize=True)


def main():
    p=argparse.ArgumentParser(); p.add_argument("--metadata",type=Path,required=True); p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    make_cover(ROOT/a.metadata if not a.metadata.is_absolute() else a.metadata, ROOT/a.out if not a.out.is_absolute() else a.out)

if __name__=="__main__": main()