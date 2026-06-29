#!/usr/bin/env python3
"""Cover: The Quiet Room — sensory deprivation, white void, psychological."""

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
    img=Image.new("RGBA",(W,H),(240,240,235,255)); draw=ImageDraw.Draw(img,"RGBA")
    # Faint grid lines
    for x in range(0,W,60): draw.line((x,0,x,H), fill=(220,220,215,100), width=1)
    for y in range(0,H,60): draw.line((0,y,W,y), fill=(220,220,215,100), width=1)
    # Central figure - silhouette in grey
    cx, cy = W//2, 1200
    draw.ellipse((cx-40, cy-100, cx+40, cy-20), fill=(180,180,175,120))  # head
    draw.polygon([(cx-60,cy-10),(cx-40,cy-10),(cx-40,cy+260),(cx-60,cy+260)], fill=(180,180,175,100))  # left leg
    draw.polygon([(cx+40,cy-10),(cx+60,cy-10),(cx+60,cy+260),(cx+40,cy+260)], fill=(180,180,175,100))  # right leg
    draw.polygon([(cx-80,cy-10),(cx-20,cy-10),(cx-10,cy+140),(cx-70,cy+140)], fill=(180,180,175,100))  # left arm
    draw.polygon([(cx+80,cy-10),(cx+20,cy-10),(cx+10,cy+140),(cx+70,cy+140)], fill=(180,180,175,100))  # right arm
    # Room box
    draw.rectangle((cx-500,cy-300,cx+500,cy+400), outline=(150,150,145,150), width=4)
    # Title panel
    draw.line((260,H-160,W-260,H-160), fill=(120,120,115,100), width=1)
    tf=font("georgiab.ttf", 100); af=font("arialbd.ttf", 40); sf=font("arial.ttf", 28)
    y=centered(draw,2000,["A PSYCHOLOGICAL THRILLER"],sf,(140,140,135),6)
    y+=40; y=centered(draw,y,wrap(draw,ti.upper(),tf,1100),tf,(60,60,55),10); y+=60
    centered(draw,y,[au],af,(100,100,95),6)
    op.parent.mkdir(parents=True,exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op,"PNG",optimize=True)


def main():
    p=argparse.ArgumentParser(); p.add_argument("--metadata",type=Path,required=True); p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    make_cover(ROOT/a.metadata if not a.metadata.is_absolute() else a.metadata, ROOT/a.out if not a.out.is_absolute() else a.out)

if __name__=="__main__": main()