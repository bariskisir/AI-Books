#!/usr/bin/env python3
"""Cover: The Iron Coast — pirate adventure, ocean and ship."""

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
    img=Image.new("RGBA",(W,H),(20,40,70,255)); draw=ImageDraw.Draw(img,"RGBA")
    # Ocean gradient
    for y in range(H):
        t=y/H; draw.line((0,y,W,y), fill=(int(20+40*t),int(40+30*t),int(70+20*t),255))
    # Waves
    for wy in range(1300, 2000, 40):
        wv=Image.new("RGBA",(W,H),(0,0,0,0)); wd=ImageDraw.Draw(wv)
        for wx in range(0, W, 10):
            wh=int(15*math.sin((wx+wy)*0.02)+10)
            wd.line((wx,wy-wh,wx+10,wy-wh+5), fill=(30,60,100,int(40+20*__import__('random').random())), width=3)
        img=Image.alpha_composite(img,wv)
    draw=ImageDraw.Draw(img,"RGBA")
    # Ship silhouette
    sx, sy = W//2, 1350
    # Hull
    draw.polygon([(sx-300,sy),(sx-350,sy+80),(sx+350,sy+80),(sx+300,sy)], fill=(10,10,15,230))
    # Masts
    for (mx, mh) in [(sx-120, -300), (sx, -360), (sx+120, -280)]:
        draw.line((mx, sy, mx, sy+mh), fill=(10,10,15,230), width=8)
    # Sails
    for (mx, mh, sw, sh) in [(sx-120, -280, 80, 140), (sx, -340, 100, 160), (sx+120, -260, 70, 120)]:
        draw.ellipse((mx-sw, sy+mh, mx+sw, sy+mh+sh), fill=(15,12,18,200))
    # Flag
    draw.polygon([(sx, sy-360), (sx, sy-320), (sx+50, sy-340)], fill=(40,40,50,220))
    # Sun/clouds
    for _ in range(8):
        cx, cy = int(W*__import__('random').random()), int(400*__import__('random').random())
        cr = int(40+80*__import__('random').random())
        draw.ellipse((cx-cr,cy-cr//2,cx+cr,cy+cr//2), fill=(60,70,90,40))
    # Title panel
    draw.line((240,H-150,W-240,H-150), fill=(200,180,100,100), width=1)
    tf=font("georgiab.ttf", 100); af=font("arialbd.ttf", 40); sf=font("arial.ttf", 28)
    y=centered(draw,2000,["A PIRATE ADVENTURE"],sf,(200,180,100),6)
    y+=40; y=centered(draw,y,wrap(draw,ti.upper(),tf,1200),tf,(220,200,130),10); y+=60
    centered(draw,y,[au],af,(200,190,160),6)
    op.parent.mkdir(parents=True,exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op,"PNG",optimize=True)


def main():
    p=argparse.ArgumentParser(); p.add_argument("--metadata",type=Path,required=True); p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    make_cover(ROOT/a.metadata if not a.metadata.is_absolute() else a.metadata, ROOT/a.out if not a.out.is_absolute() else a.out)

if __name__=="__main__": main()