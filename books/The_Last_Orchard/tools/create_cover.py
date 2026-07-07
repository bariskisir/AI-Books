#!/usr/bin/env python3
"""Cover: The Last Orchard — Gray valley in haze, single gnarled apple tree beside crumbling stone wall, one ripe fruit."""

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
    img=Image.new("RGBA",(W,H),(80,70,55,255)); draw=ImageDraw.Draw(img,"RGBA")
    rng=__import__("random").Random(13)

    # Gray valley in haze
    for y in range(H):
        t=y/H; draw.line((0,y,W,y), fill=(int(80-30*t),int(70-25*t),int(55-15*t),255))

    # Haze overlay
    haze=Image.new("RGBA",(W,H),(0,0,0,0)); hd=ImageDraw.Draw(haze)
    for _ in range(30):
        hx=int(rng.random()*W); hy=int(500+1000*rng.random())
        hw=int(200+500*rng.random()); hh=int(30+80*rng.random())
        hd.ellipse((hx-hw//2,hy-hh//2,hx+hw//2,hy+hh//2), fill=(140,130,120,10))
    haze=haze.filter(ImageFilter.GaussianBlur(35))
    img=Image.alpha_composite(img,haze)
    draw=ImageDraw.Draw(img,"RGBA")

    # Rolling hills in background
    for layer, by in [(1, 650), (2, 780), (3, 900)]:
        pts=[(0,H)]
        for x in range(0,W+10,10):
            y=by+int(40*__import__("math").sin(x*0.006+layer*0.5)+25*__import__("math").sin(x*0.015+layer*1.1))
            pts.append((x,y))
        pts.append((W,H))
        draw.polygon(pts, fill=(60-layer*5,58-layer*5,50-layer*5,200))

    # Crumbling stone wall
    for wx in range(100, W-100, 35):
        wy=int(H*0.60)+rng.randint(-10,15)
        wh=15+rng.randint(0,15)
        draw.rectangle((wx,wy,wx+28,wy+wh), fill=(90,85,78))
        draw.rectangle((wx+2,wy+2,wx+26,wy+wh-2), fill=(80,75,68))
    # Wall gaps
    for gx in [W//2-30, W//2+100, W//2-150]:
        draw.rectangle((gx,int(H*0.60),gx+20,int(H*0.60)+25), fill=(60,58,55))

    # Single gnarled apple tree
    tx,ty=W//2-40,int(H*0.48)
    # Trunk (gnarled)
    draw.line((tx,ty,tx-5,int(H*0.62)), fill=(30,25,20), width=16)
    draw.line((tx-5,int(H*0.62),tx-10,int(H*0.68)), fill=(30,25,20), width=12)
    draw.line((tx-10,int(H*0.68),tx-15,int(H*0.72)), fill=(30,25,20), width=8)
    # Gnarled knots
    for kx,ky in [(tx-5,int(H*0.55)),(tx-8,int(H*0.60)),(tx-12,int(H*0.65))]:
        draw.ellipse((kx-5,ky-3,kx+5,ky+3), fill=(25,20,15))
    # Branches
    draw.line((tx,ty,tx-60,ty-50), fill=(30,25,20), width=8)
    draw.line((tx,ty,tx+40,ty-40), fill=(30,25,20), width=6)
    draw.line((tx-60,ty-50,tx-100,ty-80), fill=(30,25,20), width=5)
    draw.line((tx-60,ty-50,tx-80,ty-30), fill=(30,25,20), width=5)
    # Sparse leaves (muted green)
    for lx,ly in [(tx-80,ty-85),(tx-100,ty-75),(tx-60,ty-55),(tx-90,ty-40),(tx+30,ty-45)]:
        draw.ellipse((lx-15,ly-10,lx+15,ly+10), fill=(50,70,45,150))
        draw.ellipse((lx-10,ly-6,lx+10,ly+6), fill=(60,80,55,120))

    # One ripe apple
    ax,ay=tx-90,ty-85
    draw.ellipse((ax-12,ay-12,ax+12,ay+12), fill=(160,40,35))
    draw.ellipse((ax-9,ay-9,ax+9,ay+9), fill=(190,50,40))
    draw.ellipse((ax-5,ay-5,ax+5,ay+5), fill=(210,70,50,200))
    # Apple stem
    draw.line((ax,ay-12,ax+3,ay-18), fill=(40,30,20), width=2)

    # Muted ground cover
    for _ in range(40):
        gx=int(rng.random()*W); gy=int(H*0.62+rng.random()*200)
        gr=5+rng.randint(0,10); gs=int(40+rng.random()*30)
        draw.ellipse((gx-gr,gy-gr//2,gx+gr,gy+gr//2), fill=(gs,gs+5,gs-5,80))

    op.parent.mkdir(parents=True,exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op,"PNG",optimize=True)


def main():
    p=argparse.ArgumentParser(); p.add_argument("--metadata",type=Path,required=True); p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    make_cover(ROOT/a.metadata if not a.metadata.is_absolute() else a.metadata, ROOT/a.out if not a.out.is_absolute() else a.out)

if __name__=="__main__": main()