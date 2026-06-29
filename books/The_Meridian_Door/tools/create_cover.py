#!/usr/bin/env python3
"""Cover: The Meridian Door — portal fantasy, luminous doorway."""

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
    img=Image.new("RGBA",(W,H),(10,10,25,255)); draw=ImageDraw.Draw(img,"RGBA")
    for y in range(H):
        t=y/H; draw.line((0,y,W,y), fill=(int(10+60*t),int(10+40*t),int(25+80*t),255))
    # Doorway glow
    gl=Image.new("RGBA",(W,H),(0,0,0,0)); gd=ImageDraw.Draw(gl)
    gd.ellipse((W//2-300,900,W//2+300,1500), fill=(200,200,255,80))
    gl=gl.filter(ImageFilter.GaussianBlur(40)); img=Image.alpha_composite(img,gl)
    draw=ImageDraw.Draw(img,"RGBA")
    # Door frame
    door_color=(40,35,55,220)
    draw.polygon([(W//2-200,850),(W//2+200,850),(W//2+200,1550),(W//2-200,1550)], fill=None, outline=door_color, width=12)
    draw.arc((W//2-200,750,W//2+200,950), 180, 360, fill=door_color, width=12)
    # Portal light inside door
    pl=Image.new("RGBA",(W,H),(0,0,0,0)); pd=ImageDraw.Draw(pl)
    pd.rectangle((W//2-190,860,W//2+190,1540), fill=(180,180,255,60))
    for r in range(0, 190, 30):
        pd.rectangle((W//2-r,860+r//2,W//2+r,1540-r//2), outline=(200,200,255,120-r//3), width=2)
    pl=pl.filter(ImageFilter.GaussianBlur(4)); img=Image.alpha_composite(img,pl)
    draw=ImageDraw.Draw(img,"RGBA")
    # Stars
    for _ in range(80):
        sx,sy=int(W*__import__('random').random()),int(700*__import__('random').random())
        sr=int(1+2*__import__('random').random())
        draw.ellipse((sx-sr,sy-sr,sx+sr,sy+sr), fill=(200,200,255,int(100+80*__import__('random').random())))
    # Title panel
    draw.line((240,H-150,W-240,H-150), fill=(180,180,220,100), width=1)
    tf=font("georgiab.ttf", 100); af=font("arialbd.ttf", 40); sf=font("arial.ttf", 28)
    y=centered(draw,2000,["A PORTAL FANTASY"],sf,(180,180,220),6)
    y+=40; y=centered(draw,y,wrap(draw,ti.upper(),tf,1200),tf,(200,200,240),10); y+=60
    centered(draw,y,[au],af,(180,180,210),6)
    op.parent.mkdir(parents=True,exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op,"PNG",optimize=True)


def main():
    p=argparse.ArgumentParser(); p.add_argument("--metadata",type=Path,required=True); p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    make_cover(ROOT/a.metadata if not a.metadata.is_absolute() else a.metadata, ROOT/a.out if not a.out.is_absolute() else a.out)

if __name__=="__main__": main()