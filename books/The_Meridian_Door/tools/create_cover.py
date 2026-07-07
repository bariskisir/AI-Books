#!/usr/bin/env python3
"""Cover: The Meridian Door — warm brass compass on dark wood, violet light spilling from cracked open door."""

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
    img=Image.new("RGBA",(W,H),(0,0,0,255)); draw=ImageDraw.Draw(img,"RGBA")
    # Dark wood background
    for y in range(H):
        t=y/H; draw.line((0,y,W,y), fill=(int(22+15*t),int(14+8*t),int(10+5*t),255))
    # Warm brass compass — centered
    cx, cy = W//2, 520
    draw.ellipse((cx-220,cy-220,cx+220,cy+220), fill=(90,70,35,255))
    draw.ellipse((cx-210,cy-210,cx+210,cy+210), fill=(170,140,75,255))
    draw.ellipse((cx-195,cy-195,cx+195,cy+195), fill=(130,105,55,255))
    draw.ellipse((cx-180,cy-180,cx+180,cy+180), fill=(215,195,155,255))
    draw.ellipse((cx-165,cy-165,cx+165,cy+165), fill=(235,220,185,255))
    # Cardinal marks
    for angle, label in [(0,"N"),(90,"E"),(180,"S"),(270,"W")]:
        rad=math.radians(angle)
        lx=cx+int(130*math.cos(rad)); ly=cy+int(130*math.sin(rad))
        draw.text((lx-12,ly-12),label,fill=(55,35,15,255),font=font("arialbd.ttf",44))
    # Compass needle — red pointing right toward crack
    draw.polygon([(cx-6,cy-90),(cx+6,cy-90),(cx+2,cy+35),(cx-2,cy+35)], fill=(200,45,45,255))
    draw.polygon([(cx-6,cy+90),(cx+6,cy+90),(cx+2,cy-35),(cx-2,cy-35)], fill=(35,35,35,255))
    draw.ellipse((cx-14,cy-14,cx+14,cy+14), fill=(230,185,65,255))
    # Cracked open door on right — violet light spilling
    dx, dy = W//2+200, 650
    glow=Image.new("RGBA",(W,H),(0,0,0,0)); gd=ImageDraw.Draw(glow)
    gd.polygon([(dx-8,dy-280),(dx+8,dy-280),(dx+40,dy+250),(dx-40,dy+250)], fill=(160,100,255,120))
    glow=glow.filter(ImageFilter.GaussianBlur(25))
    img=Image.alpha_composite(img,glow); draw=ImageDraw.Draw(img,"RGBA")
    for i in range(16):
        rad=math.radians(i*22-75)
        lx=dx+int(350*math.cos(rad)); ly=dy+int(350*math.sin(rad))
        draw.line((dx,dy,lx,ly), fill=(190,130,255,35+15*(i%4)), width=3)
    # Dark wood grain texture
    rng=__import__('random').Random(42)
    for _ in range(80):
        gx=rng.randint(0,W); gy=rng.randint(700,1600)
        gw=rng.randint(50,220); gh=rng.randint(2,5)
        draw.line((gx,gy,gx+gw,gy+gh), fill=(45,30,20,35+rng.randint(0,25)), width=2)
    # Compass glow
    cg=Image.new("RGBA",(W,H),(0,0,0,0)); cgd=ImageDraw.Draw(cg)
    cgd.ellipse((cx-350,cy-350,cx+350,cy+350), fill=(210,190,110,25))
    cg=cg.filter(ImageFilter.GaussianBlur(35))
    img=Image.alpha_composite(img,cg); draw=ImageDraw.Draw(img,"RGBA")
    # Shadow beneath compass
    draw.ellipse((cx-240,cy+180,cx+240,cy+250), fill=(0,0,0,120))
    op.parent.mkdir(parents=True,exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op,"PNG",optimize=True)


def main():
    p=argparse.ArgumentParser(); p.add_argument("--metadata",type=Path,required=True); p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    make_cover(ROOT/a.metadata if not a.metadata.is_absolute() else a.metadata, ROOT/a.out if not a.out.is_absolute() else a.out)

if __name__=="__main__": main()