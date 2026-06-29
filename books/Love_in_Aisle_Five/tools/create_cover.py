#!/usr/bin/env python3
"""Cover: Love in Aisle Five — bright grocery romance."""

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
    img=Image.new("RGBA",(W,H),(255,200,210,255)); draw=ImageDraw.Draw(img,"RGBA")
    # Pink-to-warm gradient
    for y in range(H):
        t=y/H; r=int(255-40*t); g=int(200-60*t); b=int(210-80*t)
        draw.line((0,y,W,y), fill=(max(0,r),max(0,g),max(0,b),255))
    # Heart shapes
    for (hx,hy,hs,ha) in [(W//2, 1000, 180, 60), (400, 1100, 100, 35), (1200, 900, 130, 40)]:
        h=Image.new("RGBA",(W,H),(0,0,0,0)); hd=ImageDraw.Draw(h)
        hd.ellipse((hx-hs,hy-hs//2,hx,hy+hs//2), fill=(240,120,140,ha))
        hd.ellipse((hx,hy-hs//2,hx+hs,hy+hs//2), fill=(240,120,140,ha))
        hd.polygon([(hx-hs-10,hy+10),(hx+hs+10,hy+10),(hx,hy+hs+60)],fill=(240,120,140,ha))
        h=h.filter(ImageFilter.GaussianBlur(8)); img=Image.alpha_composite(img,h)
    draw=ImageDraw.Draw(img,"RGBA")
    # Aisle shelf lines
    for sy in [1400, 1460, 1520, 1580]:
        draw.line((W//2-700,sy,W//2+700,sy), fill=(200,160,170,100), width=3)
    # Small produce items
    for col in range(5):
        cx = W//2 - 450 + col*220
        draw.ellipse((cx-20,1420-20,cx+20,1420+20), fill=(250,80,80,150))  # tomato
        draw.ellipse((cx-15,1475-15,cx+15,1475+15), fill=(100,200,80,150))  # green
        draw.ellipse((cx-18,1535-18,cx+18,1535+18), fill=(255,180,50,150))  # orange
    # Title panel
    draw.line((240,2000,W-240,2000), fill=(200,80,100,200), width=3)
    draw.line((240,H-150,W-240,H-150), fill=(200,80,100,100), width=2)
    tf=font("georgiab.ttf", 100); af=font("arialbd.ttf", 40); sf=font("arial.ttf", 30)
    y=centered(draw,2030,["A ROMANTIC COMEDY"],sf,(180,60,80),6)
    y+=40; y=centered(draw,y,wrap(draw,ti.upper(),tf,1200),tf,(120,30,50),10); y+=60
    centered(draw,y,[au],af,(150,50,70),6)
    op.parent.mkdir(parents=True,exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op,"PNG",optimize=True)


def main():
    p=argparse.ArgumentParser(); p.add_argument("--metadata",type=Path,required=True); p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    make_cover(ROOT/a.metadata if not a.metadata.is_absolute() else a.metadata, ROOT/a.out if not a.out.is_absolute() else a.out)

if __name__=="__main__": main()