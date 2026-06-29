#!/usr/bin/env python3
"""Cover: Briar House — gothic haunted manor, dark and atmospheric."""

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
    img=Image.new("RGBA",(W,H),(10,8,12,255)); draw=ImageDraw.Draw(img,"RGBA")
    # Moonlit gradient
    for y in range(H):
        t=y/H; draw.line((0,y,W,y), fill=(int(10+60*t),int(8+50*t),int(12+70*t),255))
    # Moon
    moon=Image.new("RGBA",(W,H),(0,0,0,0)); md=ImageDraw.Draw(moon)
    md.ellipse((W-500, 120, W-200, 420), fill=(220,215,200,180))
    moon=moon.filter(ImageFilter.GaussianBlur(6)); img=Image.alpha_composite(img,moon)
    draw=ImageDraw.Draw(img,"RGBA")
    # Manor silhouette
    mx, my = W//2, 1300
    draw.polygon([(mx-500,my+200),(mx-500,my-100),(mx-300,my-100),(mx-300,my-300),
                  (mx-100,my-300),(mx-100,my-100),(mx+100,my-100),(mx+100,my-300),
                  (mx+300,my-300),(mx+300,my-100),(mx+500,my-100),(mx+500,my+200)], fill=(5,3,8,230))
    # Tower
    draw.rectangle((mx-120,my-500,mx+120,my-300), fill=(5,3,8,230))
    draw.polygon([(mx-160,my-500),(mx+160,my-500),(mx,my-560)], fill=(5,3,8,230))
    # Lit window
    draw.rectangle((mx-50,my-430,mx+50,my-380), fill=(180,160,100,120))
    # Bare trees
    for tx in [mx-450, mx-350, mx+350, mx+450]:
        for _ in range(5):
            draw.line((tx,my-50,tx-30+60*__import__('random').random(),my-200+100*__import__('random').random()), fill=(3,2,5,200), width=3)
    # Fog
    fog=Image.new("RGBA",(W,H),(0,0,0,0)); fd=ImageDraw.Draw(fog)
    fd.ellipse((-200,1600,W+200,2000), fill=(180,175,170,30))
    fog=fog.filter(ImageFilter.GaussianBlur(40)); img=Image.alpha_composite(img,fog)
    draw=ImageDraw.Draw(img,"RGBA")
    # Title panel
    draw.line((240,H-150,W-240,H-150), fill=(160,140,100,100), width=1)
    tf=font("georgiab.ttf", 110); af=font("arialbd.ttf", 42); sf=font("arial.ttf", 28)
    y=centered(draw,1990,["A GOTHIC NOVEL"],sf,(180,160,130),6)
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