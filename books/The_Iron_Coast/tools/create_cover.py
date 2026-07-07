#!/usr/bin/env python3
"""Cover: The Iron Coast — Pirate fleet maneuvering through reef passage, giant chain splitting British warship's hull."""

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
    model=m.get("model","")
    img=Image.new("RGBA",(W,H),(20,40,70,255)); draw=ImageDraw.Draw(img,"RGBA")
    rng=__import__("random").Random(7)

    # Ocean gradient: deep blue to iron gray
    for y in range(H):
        t=y/H; draw.line((0,y,W,y), fill=(int(20+30*t),int(40+25*t),int(70+15*t),255))

    # Rocky reef passage
    for side in [0, W]:
        for i in range(15):
            rx=side+(rng.randint(0,200) if side==0 else -rng.randint(0,200))
            ry=int(H*0.4+rng.random()*H*0.3)
            rs=rng.randint(30,120)
            draw.ellipse((rx-rs,ry-rs//2,rx+rs,ry+rs//2), fill=(40,35,30,200))

    # Giant chain stretching across channel
    chain_color=(100,95,90)
    for x in range(0, W, 8):
        cy=int(H*0.48+5*__import__("math").sin(x*0.03))
        draw.line((x,cy,x+4,cy+2), fill=chain_color, width=3)
    # Chain links
    for x in range(0, W, 40):
        chain_y=int(H*0.48+5*__import__("math").sin(x*0.03))
        draw.ellipse((x-5,chain_y-4,x+5,chain_y+4), fill=None, outline=(120,115,110), width=2)

    # British warship (larger) with chain splitting its hull
    wx,wy=W//2+100,int(H*0.55)
    # Hull
    draw.polygon([(wx-200,wy),(wx-250,wy+60),(wx+250,wy+60),(wx+200,wy)], fill=(15,12,10,230))
    # Masts
    for (mx,mh) in [(wx-80,-280),(wx,-320),(wx+80,-250)]:
        draw.line((mx,wy,mx,wy+mh), fill=(15,12,10,230), width=7)
    # Sails
    for (mx,mh,sw,sh) in [(wx-80,-260,70,130),(wx,-300,90,150),(wx+80,-230,60,110)]:
        draw.ellipse((mx-sw,wy+mh,mx+sw,wy+mh+sh), fill=(18,15,12,200))
    # Union Jack
    draw.polygon([(wx,wy-320),(wx,wy-290),(wx+45,wy-305)], fill=(180,30,30,220))

    # Chain cutting through hull
    cut_y=wy+25
    draw.line((wx-160,cut_y-5,wx+160,cut_y+5), fill=(120,115,110), width=6)
    # Splinter effect
    draw.polygon([(wx-30,wy+10),(wx-30,wy+50),(wx+30,wy+45),(wx+30,wy+5)], fill=(10,8,6,230))
    draw.line((wx-40,wy+20,wx-40,wy+40), fill=(8,6,5,230), width=4)

    # Cannon flash
    flash=Image.new("RGBA",(W,H),(0,0,0,0)); fd=ImageDraw.Draw(flash)
    fx,fy=wx+200,wy+30
    for r in range(40,0,-3):
        fd.ellipse((fx-r,fy-r//2,fx+r,fy+r//2), fill=(255,200,50,max(0,80-r*2)))
    flash=flash.filter(ImageFilter.GaussianBlur(5))
    img=Image.alpha_composite(img,flash)
    draw=ImageDraw.Draw(img,"RGBA")

    # Pirate fleet (smaller ships in background)
    for i in range(4):
        px=int(100+i*350+rng.randint(-30,30))
        py=int(H*0.5+rng.randint(-20,20))
        draw.polygon([(px-60,py),(px-70,py+20),(px+70,py+20),(px+60,py)], fill=(12,10,8,180))
        draw.line((px,py,px,py-100), fill=(12,10,8,180), width=4)
        draw.polygon([(px,py-100),(px,py-85),(px+30,py-90)], fill=(40,40,50,180))

    # Waves
    for wy in range(int(H*0.5), 2000, 30):
        wv=Image.new("RGBA",(W,H),(0,0,0,0)); wd=ImageDraw.Draw(wv)
        for wx in range(0,W,8):
            wh=int(12*__import__("math").sin((wx+wy)*0.025)+8)
            wd.line((wx,wy-wh,wx+8,wy-wh+4), fill=(30,60,100,int(30+20*rng.random())), width=2)
        img=Image.alpha_composite(img,wv)

    op.parent.mkdir(parents=True,exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op,"PNG",optimize=True)


def main():
    p=argparse.ArgumentParser(); p.add_argument("--metadata",type=Path,required=True); p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    make_cover(ROOT/a.metadata if not a.metadata.is_absolute() else a.metadata, ROOT/a.out if not a.out.is_absolute() else a.out)

if __name__=="__main__": main()