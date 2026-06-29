#!/usr/bin/env python3
"""Cover: The Burden of Proof — legal thriller, dark wood tones."""

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
    img=Image.new("RGBA",(W,H),(35,25,20,255)); draw=ImageDraw.Draw(img,"RGBA")
    for y in range(H):
        t=y/H; draw.line((0,y,W,y), fill=(int(35+30*t),int(25+20*t),int(20+15*t),255))
    # Gavel silhouette
    gx, gy = W//2, 800
    draw.rectangle((gx-30,gy-40,gx+30,gy+120), fill=(60,45,35,200))  # handle
    draw.rectangle((gx-100,gy+80,gx+100,gy+140), fill=(60,45,35,200))  # head
    draw.rectangle((gx-120,gy-60,gx+120,gy-20), fill=(60,45,35,200))  # block
    # Scales of justice
    sx, sy = W//2, 1100
    draw.line((sx,sy-80,sx,sy+20), fill=(80,65,55,150), width=6)
    draw.arc((sx-150,sy-80,sx+150,sy+80), 200, 340, fill=(80,65,55,150), width=5)  # beam
    draw.ellipse((sx-130,sy-150,sx-70,sy-90), outline=(80,65,55,150), width=4)  # left pan
    draw.ellipse((sx+70,sy-150,sx+130,sy-90), outline=(80,65,55,150), width=4)  # right pan
    # Law book stack
    for i in range(3):
        draw.rectangle((W//2-120,1500+i*30,W//2+120,1530+i*30), fill=(50,38,30,180), width=2)
    draw.text((W//2-20,1505), "LAW", font=font("arialbd.ttf", 28), fill=(120,100,80,150))
    # Title panel
    draw.line((240,H-150,W-240,H-150), fill=(200,160,100,100), width=1)
    tf=font("georgiab.ttf", 105); af=font("arialbd.ttf", 40); sf=font("arial.ttf", 28)
    y=centered(draw,2000,["A LEGAL THRILLER"],sf,(200,160,100),6)
    y+=40; y=centered(draw,y,wrap(draw,ti.upper(),tf,1200),tf,(220,195,160),10); y+=60
    centered(draw,y,[au],af,(200,190,170),6)
    op.parent.mkdir(parents=True,exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op,"PNG",optimize=True)


def main():
    p=argparse.ArgumentParser(); p.add_argument("--metadata",type=Path,required=True); p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    make_cover(ROOT/a.metadata if not a.metadata.is_absolute() else a.metadata, ROOT/a.out if not a.out.is_absolute() else a.out)

if __name__=="__main__": main()