#!/usr/bin/env python3
"""Cover: The Vienna Exchange — Cold gradient, caricature silhouette with briefcase on checkerboard floor, red accent line, clock."""

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


ROOT = Path(__file__).resolve().parents[3]; FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560

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

def make_cover(mp,op):
    m=json.loads(mp.read_text(encoding="utf-8")); ti=m["title"]; au=m.get("author","Barış Kısır")
    model = m.get("model", "")
    img=Image.new("RGBA",(W,H),(30,35,40,255)); draw=ImageDraw.Draw(img,"RGBA")
    for y in range(H):
        t=y/H
        r=int(40-15*t); g=int(45-20*t); b=int(55-25*t)
        draw.line((0,y,W,y), fill=(r,g,b,255))
    for gy in range(1400, 1900, 60):
        for gx in range(0, W, 60):
            if ((gx//60)+(gy//60))%2:
                draw.rectangle((gx,gy,gx+60,gy+60), fill=(35,40,45,70))
    fx, fy = W//2, 1150
    draw.polygon([(fx-28,fy-95),(fx+28,fy-95),(fx+28,fy-18),(fx-28,fy-18)], fill=(18,18,20,200))
    draw.ellipse((fx-22,fy-75,fx+22,fy-28), fill=(22,22,25,200))
    draw.polygon([(fx-38,fy-18),(fx+38,fy-18),(fx+38,fy+180),(fx-38,fy+180)], fill=(22,22,25,180))
    draw.polygon([(fx+38,fy+90),(fx+90,fy+70),(fx+90,fy+160),(fx+38,fy+180)], fill=(22,22,25,150))
    draw.line((0,1300,W,1300), fill=(180,35,35,150), width=4)
    clock_cx, clock_cy = W//2 + 200, 800
    draw.ellipse((clock_cx - 40, clock_cy - 40, clock_cx + 40, clock_cy + 40), outline=(80, 80, 90, 150), width=4)
    for a in [0, 90, 180, 270]:
        rad = math.radians(a)
        ex = clock_cx + math.cos(rad) * 35
        ey = clock_cy + math.sin(rad) * 35
        draw.line((clock_cx, clock_cy, ex, ey), fill=(80, 80, 90, 120), width=2)
    draw.line((clock_cx, clock_cy, clock_cx + 20, clock_cy - 10), fill=(180, 35, 35, 150), width=3)
    draw.line((clock_cx, clock_cy, clock_cx - 10, clock_cy - 15), fill=(180, 35, 35, 120), width=2)
    draw.ellipse((clock_cx - 3, clock_cy - 3, clock_cx + 3, clock_cy + 3), fill=(180, 35, 35, 150))
    op.parent.mkdir(parents=True,exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op,"PNG",optimize=True)


def main():
    p=argparse.ArgumentParser(); p.add_argument("--metadata",type=Path,required=True); p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    make_cover(ROOT/a.metadata if not a.metadata.is_absolute() else a.metadata, ROOT/a.out if not a.out.is_absolute() else a.out)

if __name__=="__main__": main()