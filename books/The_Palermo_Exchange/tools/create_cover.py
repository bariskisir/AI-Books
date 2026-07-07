#!/usr/bin/env python3
"""Cover: The Palermo Exchange — narrow Sicilian vicolo, shadowed arch with warm light, Vespa silhouette, wrought-iron balcony."""

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


def font(n, s):
    for c in [FONT_DIR / n, FONT_DIR / "georgia.ttf", FONT_DIR / "arial.ttf"]:
        if c.exists():
            return ImageFont.truetype(str(c), s)
    return ImageFont.load_default()


def wrap(d, t, f, w):
    wo = t.split()
    li = []
    cu = []
    for wd in wo:
        p = " ".join([*cu, wd])
        if d.textbbox((0, 0), p, font=f)[2] <= w:
            cu.append(wd)
        else:
            li.append(" ".join(cu))
            cu = [wd]
    if cu:
        li.append(" ".join(cu))
    return li


def centered(d, y, li, f, fl, g):
    for l in li:
        bb = d.textbbox((0, 0), l, font=f)
        d.text(((W - (bb[2] - bb[0])) // 2, y), l, font=f, fill=fl)
        y += bb[3] - bb[1] + g
    return y


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    ti = m["title"]
    au = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (180, 140, 100, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Warm stone gradient
    for y in range(H):
        t = y/H
        draw.line((0,y,W,y), fill=(int(180-40*t),int(140-30*t),int(100-20*t),255))

    # Narrow vicolo — converging walls
    draw.polygon([(0,0),(350,500),(350,1400),(0,1800)], fill=(160,120,80,120))
    draw.polygon([(W,0),(1250,500),(1250,1400),(W,1800)], fill=(160,120,80,120))
    for i in range(8):
        x1=int(350+i*25); x2=int(1250-i*25)
        draw.line((x1,500+i*100,x2,500+i*100), fill=(140,100,65,80), width=2)

    # Shadowed arch with warm light spilling out — left wall
    door_x, door_y = 100, 850
    draw.arc((door_x-20,door_y-40,door_x+180,door_y+40), 180,360, fill=(80,60,40,180), width=8)
    draw.rectangle((door_x,door_y,door_x+160,door_y+280), fill=(25,20,15,230))
    # Warm light spilling from doorway
    for i in range(6):
        alpha=25-i*4
        draw.ellipse((door_x-30-i*8,door_y+260,door_x+190+i*8,door_y+300+i*25), fill=(240,200,120,max(0,alpha)))

    # Vespa silhouette on right
    vx, vy = 1280, 1080
    draw.ellipse((vx-55,vy-35,vx+55,vy+55), fill=(50,45,40,200))
    draw.line((vx-35,vy-45,vx+15,vy-55), fill=(55,50,45,200), width=5)
    draw.polygon([(vx+15,vy-25),(vx+45,vy-5),(vx+45,vy+25),(vx+15,vy+10)], fill=(55,50,45,200))
    draw.ellipse((vx-25,vy+45,vx+15,vy+75), fill=(40,35,30,200))
    draw.ellipse((vx+25,vy+45,vx+65,vy+75), fill=(40,35,30,200))
    draw.rectangle((vx-25,vy-15,vx+15,vy+5), fill=(45,40,35,200))

    # Wrought-iron balcony — mid-left wall
    bx, by = 450, 650
    draw.rectangle((bx,by,bx+180,by+15), fill=(40,35,30,160))
    for i in range(7):
        draw.line((bx+15+i*26,by+15,bx+15+i*26,by+50), fill=(40,35,30,140), width=3)
    draw.line((bx,by+50,bx+180,by+50), fill=(40,35,30,140), width=4)

    # Cobblestone texture
    for gx in range(0,W,45):
        for gy in range(1400,1900,25):
            if ((gx//45)+(gy//25))%2:
                draw.ellipse((gx,gy,gx+18,gy+10), fill=(130,95,65,50))

    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op, "PNG", optimize=True)



def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    make_cover(
        ROOT / a.metadata if not a.metadata.is_absolute() else a.metadata,
        ROOT / a.out if not a.out.is_absolute() else a.out,
    )


if __name__ == "__main__":
    main()