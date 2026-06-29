#!/usr/bin/env python3
"""Cover: The Last Orchard — post-apocalyptic, muted earth tones."""

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
    img=Image.new("RGBA",(W,H),(80,70,55,255)); draw=ImageDraw.Draw(img,"RGBA")
    # Dusty gradient
    for y in range(H):
        t=y/H; draw.line((0,y,W,y), fill=(int(80-30*t),int(70-25*t),int(55-15*t),255))
    # Dead tree silhouette
    draw.line((W//2, 400, W//2, 1500), fill=(25,22,18,200), width=20)
    for a in range(70, 290, 25):
        rad=math.radians(a)
        for d in range(0, 200, 50):
            ex, ey = W//2+int(d*math.cos(rad)), 800+int(d*math.sin(rad))
            draw.line((W//2, 800, ex, ey), fill=(25,22,18,180), width=8)
    # Single living branch with one apple
    draw.line((W//2, 900, W//2-180, 700), fill=(25,22,18,180), width=6)
    draw.ellipse((W//2-200, 680, W//2-160, 720), fill=(180,50,40,200))
    draw.ellipse((W//2-195, 685, W//2-165, 715), fill=(200,60,50,150))
    # Fence silhouettes
    for fx in range(100, W, 160):
        draw.line((fx,1500,fx,1700), fill=(40,35,28,150), width=5)
        draw.line((fx-20,1550,fx+20,1550), fill=(40,35,28,150), width=5)
    # Cracked earth
    for _ in range(20):
        cy = 1800+int(400*__import__('random').random())
        cx = int(W*__import__('random').random())
        draw.arc((cx-80,cy-20,cx+80,cy+20), 0, 180, fill=(60,50,38,100), width=2)
    # Title panel
    draw.line((240,H-150,W-240,H-150), fill=(180,120,60,100), width=1)
    tf=font("georgiab.ttf", 105); af=font("arialbd.ttf", 42); sf=font("arial.ttf", 28)
    y=centered(draw,1980,["A POST-APOCALYPTIC NOVEL"],sf,(180,120,60),6)
    y+=40; y=centered(draw,y,wrap(draw,ti.upper(),tf,1200),tf,(200,180,140),10); y+=60
    centered(draw,y,[au],af,(180,170,150),6)
    op.parent.mkdir(parents=True,exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op,"PNG",optimize=True)


def main():
    p=argparse.ArgumentParser(); p.add_argument("--metadata",type=Path,required=True); p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    make_cover(ROOT/a.metadata if not a.metadata.is_absolute() else a.metadata, ROOT/a.out if not a.out.is_absolute() else a.out)

if __name__=="__main__": main()