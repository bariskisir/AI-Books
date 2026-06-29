#!/usr/bin/env python3
"""Cover: The Vienna Exchange — Cold War spy, muted greys and red."""

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
    # Cold gradient
    for y in range(H):
        t=y/H; draw.line((0,y,W,y), fill=(int(30-10*t),int(35-15*t),int(40-10*t),255))
    # Checkerboard floor (spy meeting cliche)
    for gy in range(1400, 2100, 60):
        for gx in range(0, W, 60):
            if ((gx//60)+(gy//60))%2:
                draw.rectangle((gx,gy,gx+60,gy+60), fill=(40,45,50,80))
    # Figure silhouette
    fx, fy = W//2, 1200
    draw.polygon([(fx-30,fy-100),(fx+30,fy-100),(fx+30,fy-20),(fx-30,fy-20)], fill=(20,20,22,200))  # hat
    draw.ellipse((fx-25,fy-80,fx+25,fy-30), fill=(25,25,28,200))  # head
    draw.polygon([(fx-40,fy-20),(fx+40,fy-20),(fx+40,fy+200),(fx-40,fy+200)], fill=(25,25,28,180))  # coat
    draw.polygon([(fx+40,fy+100),(fx+100,fy+80),(fx+100,fy+180),(fx+40,fy+200)], fill=(25,25,28,150))  # arm with briefcase
    # Red accent line
    draw.line((0,1350,W,1350), fill=(180,40,40,150), width=4)
    # Title panel
    draw.line((240,H-150,W-240,H-150), fill=(180,40,40,100), width=1)
    tf=font("georgiab.ttf", 100); af=font("arialbd.ttf", 40); sf=font("arial.ttf", 28)
    y=centered(draw,2000,["A COLD WAR SPY THRILLER"],sf,(180,40,40),6)
    y+=40; y=centered(draw,y,wrap(draw,ti.upper(),tf,1200),tf,(200,195,185),10); y+=60
    centered(draw,y,[au],af,(180,175,170),6)
    op.parent.mkdir(parents=True,exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op,"PNG",optimize=True)


def main():
    p=argparse.ArgumentParser(); p.add_argument("--metadata",type=Path,required=True); p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    make_cover(ROOT/a.metadata if not a.metadata.is_absolute() else a.metadata, ROOT/a.out if not a.out.is_absolute() else a.out)

if __name__=="__main__": main()