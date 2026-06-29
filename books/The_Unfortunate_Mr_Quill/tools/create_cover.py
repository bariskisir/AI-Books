#!/usr/bin/env python3
"""Cover: The Unfortunate Mr. Quill — dark comedy, droll literary style."""

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
    img=Image.new("RGBA",(W,H),(220,215,200,255)); draw=ImageDraw.Draw(img,"RGBA")
    # Aged paper gradient
    for y in range(H):
        t=y/H; draw.line((0,y,W,y), fill=(int(220-20*t),int(215-18*t),int(200-15*t),255))
    # Typewriter keys
    for ky in range(900, 1400, 60):
        for kx in range(200, W, 80):
            r=int(10+15*__import__('random').random())
            draw.ellipse((kx-r,ky-r,kx+r,ky+r), fill=(40,35,30,int(60+30*__import__('random').random())))
            if __import__('random').random() > 0.7:
                draw.ellipse((kx-8,ky-8,kx+8,ky+8), fill=(50,45,38,90))
    # Figure silhouette
    fx, fy = W//2, 1150
    draw.ellipse((fx-30,fy-40,fx+30,fy+20), fill=(60,55,48,150))  # head
    draw.polygon([(fx-55,fy+20),(fx+55,fy+20),(fx+55,fy+250),(fx-55,fy+250)], fill=(60,55,48,120))  # body
    # Hat (Homburg-ish)
    draw.rectangle((fx-60,fy-70,fx+60,fy-50), fill=(50,45,38,150))
    draw.rectangle((fx-80,fy-85,fx+80,fy-70), fill=(50,45,38,150))
    # Quill pen
    draw.line((fx+60, fy-20, fx+160, fy-160), fill=(40,35,30,150), width=4)
    draw.polygon([(fx+160,fy-160),(fx+170,fy-170),(fx+140,fy-145)], fill=(30,28,25,150))
    # Ink splatter
    for _ in range(10):
        ix, iy = fx+150+int(60*__import__('random').random()), fy-140+int(60*__import__('random').random())
        ir = int(3+8*__import__('random').random())
        draw.ellipse((ix-ir, iy-ir, ix+ir, iy+ir), fill=(20,18,15,int(120+50*__import__('random').random())))
    # Typewriter text line
    draw.text((W//2-300, 1450), "I faked my own death.", font=font("georgia.ttf", 36), fill=(40,35,30,80))
    draw.text((W//2-280, 1500), "It did not go as planned.", font=font("georgia.ttf", 32), fill=(40,35,30,60))
    # Title panel
    draw.line((240,H-150,W-240,H-150), fill=(60,50,40,100), width=1)
    tf=font("georgiab.ttf", 95); af=font("arialbd.ttf", 40); sf=font("arial.ttf", 28)
    y=centered(draw,1990,["A DARK COMEDY"],sf,(80,70,60),6)
    y+=40; y=centered(draw,y,wrap(draw,ti.upper(),tf,1200),tf,(60,50,40),10); y+=60
    centered(draw,y,[au],af,(100,90,80),6)
    op.parent.mkdir(parents=True,exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op,"PNG",optimize=True)


def main():
    p=argparse.ArgumentParser(); p.add_argument("--metadata",type=Path,required=True); p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    make_cover(ROOT/a.metadata if not a.metadata.is_absolute() else a.metadata, ROOT/a.out if not a.out.is_absolute() else a.out)

if __name__=="__main__": main()