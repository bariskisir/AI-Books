#!/usr/bin/env python3
"""Cover: The Parachute Regiment — paratrooper silhouettes descending at dawn over Normandy, C-47s overhead, church steeple."""

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


ROOT = Path(__file__).resolve().parents[3]
FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    for c in [FONT_DIR / name, FONT_DIR / "georgia.ttf", FONT_DIR / "arial.ttf"]:
        if c.exists():
            return ImageFont.truetype(str(c), size)
    return ImageFont.load_default()


def wrap(draw, text, fnt, mw):
    words, lines, cur = text.split(), [], []
    for w in words:
        p = " ".join([*cur, w])
        if draw.textbbox((0, 0), p, font=fnt)[2] <= mw:
            cur.append(w)
        else:
            lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def centered(draw, y, lines, fnt, fill, gap):
    for line in lines:
        bb = draw.textbbox((0, 0), line, font=fnt)
        draw.text(((W - (bb[2] - bb[0])) // 2, y), line, font=fnt, fill=fill)
        y += bb[3] - bb[1] + gap
    return y


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title, author = m["title"], m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Dawn sky gradient
    for y in range(H):
        t=y/H
        if t<0.4: r=int(40+60*(t/0.4)); g=int(30+80*(t/0.4)); b=int(80+100*(t/0.4))
        elif t<0.6: lt=(t-0.4)/0.2; r=int(100+120*lt); g=int(110+80*lt); b=int(180-140*lt)
        else: lt=(t-0.6)/0.4; r=int(220-60*lt); g=int(190-100*lt); b=int(40-20*lt)
        draw.line((0,y,W,y), fill=(max(0,r),max(0,g),max(0,b),255))

    # Sun glow
    sun=Image.new("RGBA",(W,H),(0,0,0,0)); sd=ImageDraw.Draw(sun)
    sd.ellipse((W//2-300,600,W//2+300,1000), fill=(255,200,80,180))
    sun=sun.filter(ImageFilter.GaussianBlur(50))
    img=Image.alpha_composite(img,sun); draw=ImageDraw.Draw(img,"RGBA")

    # Horizon — French countryside
    draw.rectangle((0,1400,W,1420), fill=(60,80,40,180))
    # Church steeple silhouette
    sx,sy=W//2-200,1350
    draw.polygon([(sx-10,sy+50),(sx-10,sy),(sx,sy-40),(sx+10,sy),(sx+10,sy+50)], fill=(25,30,20,220))
    draw.rectangle((sx-20,sy+50,sx+20,sy+70), fill=(25,30,20,220))
    # Rolling hills
    for i,(cy,cw,ch) in enumerate([(1450,2000,180),(1500,1600,140),(1550,1200,100)]):
        olive=int(70+30*i)
        draw.polygon([(W//2-cw//2,cy+ch),(W//2-cw//2,cy),(W//2,cy-ch//2),(W//2+cw//2,cy),(W//2+cw//2,cy+ch)], fill=(olive,olive+20,int(30+15*i),200))

    # C-47 silhouettes overhead
    for px,py,s in [(200,150,1.0),(1300,200,0.7)]:
        draw.polygon([(px,py),(px+int(120*s),py-int(10*s)),(px+int(180*s),py+int(5*s)),(px+int(200*s),py+int(8*s)),(px+int(180*s),py+int(12*s)),(px+int(120*s),py+int(12*s)),(px,py+int(8*s))], fill=(15,12,10,int(160*s)))
        draw.polygon([(px+int(40*s),py-int(5*s)),(px+int(100*s),py-int(5*s)),(px+int(100*s),py+int(3*s)),(px+int(40*s),py+int(3*s))], fill=(15,12,10,int(140*s)))

    # Paratrooper silhouettes descending
    for cx,cy,fl in [(400,450,True),(700,300,False),(1050,500,True),(500,650,False),(1200,350,True),(850,700,False),(300,550,True)]:
        for j in range(3):
            off=j*10
            draw.ellipse((cx-40+off,cy-30-off*2,cx+40-off,cy-off), outline=(180,190,170,120), width=2)
        for rx in [-12,0,12]:
            draw.line((cx+rx,cy-3,cx+rx,cy+15), fill=(160,160,150,100), width=1)
        d=-1 if fl else 1
        draw.line((cx,cy+15,cx+d*10,cy+35), fill=(20,18,15,220), width=4)
        draw.line((cx+d*10,cy+35,cx+d*7,cy+50), fill=(20,18,15,220), width=3)
        draw.ellipse((cx-4,cy+8,cx+4,cy+18), fill=(20,18,15,220))

    # Hedge rows
    for fx in range(100,W,250):
        draw.rectangle((fx,1480,fx+6,1700), fill=(50,65,35,160))

    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op, "PNG", optimize=True)



def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    make_cover(
        ROOT / a.metadata if not a.metadata.is_absolute() else a.metadata,
        ROOT / a.out if not a.out.is_absolute() else a.out,
    )


if __name__ == "__main__":
    main()