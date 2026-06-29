#!/usr/bin/env python3
"""Cover: The Glass Maker — 17th-century Venice, amber and ruby glass."""

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
    for c in [FONT_DIR/n, FONT_DIR/"arial.ttf"]:
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
    img=Image.new("RGBA",(W,H),(50,30,25,255)); draw=ImageDraw.Draw(img,"RGBA")

    # Warm Venetian gradient — amber to deep crimson
    for y in range(H):
        t=y/H
        r=int(50+80*t)
        g=int(30+20*t)
        b=int(25-10*t)
        draw.line((0,y,W,y), fill=(min(r,255),min(g,255),max(b,0),255))

    # Canal at midground — dark water band
    for y in range(900, 1300):
        t=(y-900)/400
        draw.line((0,y,W,y), fill=(int(40-20*t),int(35-15*t),int(45-10*t),200))

    # Gondola silhouette
    gx, gy = 400, 1150
    draw.arc((gx,gy-120,gx+400,gy+40), 180, 360, fill=(15,15,20,200), width=6)
    draw.polygon([(gx+380,gy-38),(gx+420,gy-60),(gx+420,gy-20)], fill=(15,15,20,200))
    # Gondolier
    draw.ellipse((gx+200,gy-100,gx+240,gy-60), fill=(20,20,25,180))
    draw.polygon([(gx+200,gy-60),(gx+240,gy-60),(gx+220,gy-15)], fill=(15,15,20,180))

    # Building silhouettes on right
    for i in range(4):
        bx = 1100 + i*80
        bh = 700 + i*30
        draw.rectangle((bx,1300-bh,bx+70,1300), fill=(40,30,25,100))

    # Palace arches on left
    for i in range(3):
        ax=100+i*120; ay=950
        draw.arc((ax,ay,ax+100,ay+120), 180, 360, fill=(60,50,40,80), width=5)
        draw.rectangle((ax,ay+60,ax+100,ay+150), fill=(40,35,30,80))

    # Furnace glow — lower left
    fx, fy = 250, 1600
    # Glow circle
    for r in range(150,0,-1):
        a=min(60,int(40*(1-r/150)))
        draw.ellipse((fx-r,fy-r-100,fx+r,fy+r-100), fill=(200,int(100*(1-r/150)),int(20*(1-r/150)),a))
    # Furnace opening
    draw.rectangle((fx-60,fy-80,fx+60,fy+50), fill=(180,60,20,200))
    draw.rectangle((fx-50,fy-70,fx+50,fy+40), fill=(255,120,30,220))
    # Fire within
    draw.ellipse((fx-30,fy-40,fx+30,fy+10), fill=(255,180,50,200))

    # Ruby glass goblet silhouette above furnace
    gfx, gfy = fx, fy-300
    draw.polygon([(gfx-35,gfy),(gfx+35,gfy),(gfx+20,gfy-120),(gfx-20,gfy-120)], fill=(180,40,30,180))  # bowl
    draw.rectangle((gfx-5,gfy-180,gfx+5,gfy-120), fill=(180,40,30,180))  # stem
    draw.ellipse((gfx-25,gfy-200,gfx+25,gfy-180), fill=(180,40,30,180))  # base

    # Chandelier silhouette above
    cx, cy = 1200, 500
    draw.line((cx,cy-80,cx,cy), fill=(50,40,30,150), width=3)
    draw.arc((cx-80,cy,cx+80,cy+100), 180, 360, fill=(60,50,40,120), width=4)
    for a in range(0,360,45):
        rad=math.radians(a)
        lx=cx+int(80*math.cos(rad)); ly=cy+int(80*math.sin(rad))
        draw.line((lx,ly,lx+int(30*math.cos(rad)),ly+int(30*math.sin(rad))), fill=(60,50,40,80), width=2)

    # Title panel
    draw.line((200,H-120,W-200,H-120), fill=(180,40,30,100), width=1)

    # Ruby glow accent dots along bottom line
    for i in range(0,W,80):
        draw.ellipse((i-3,H-126,i+3,H-120), fill=(255,100,50,80))

    tf=font("arialbd.ttf", 100); af=font("arialbd.ttf", 40); sf=font("arial.ttf", 28)

    ypos=2000
    ypos=centered(draw,ypos,wrap(draw,ti.upper(),tf,1200),tf,(230,225,215),10); ypos+=60
    centered(draw,ypos,[au],af,(200,195,185),6)

    op.parent.mkdir(parents=True,exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op,"PNG",optimize=True)


def main():
    p=argparse.ArgumentParser(); p.add_argument("--metadata",type=Path,required=True); p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    make_cover(ROOT/a.metadata if not a.metadata.is_absolute() else a.metadata, ROOT/a.out if not a.out.is_absolute() else a.out)

if __name__=="__main__": main()