#!/usr/bin/env python3
"""Cover: The Night Market — moonlit night market from Oakland vacant lot, lanterns amber-green-blue, figure browsing."""

import argparse
import json
import math
import random
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



def wrap_text(draw, text, font, max_width):
    """Wrap text to fit within max_width."""
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test = current_line + " " + word if current_line else word
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line = test
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines


def create_cover(metadata_path, output_path):
    with open(metadata_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    model = meta.get("model", "")

    title = meta["title"]
    author = meta["author"]

    W, H = 1600, 2560

    img = Image.new("RGB", (W, H), (20, 10, 30))
    draw = ImageDraw.Draw(img)

    # Night sky gradient: deep purple to midnight blue
    for y in range(H):
        r = int(20 + (y/H)*15); g = int(5 + (y/H)*20); b = int(40 + (y/H)*30)
        for x in range(W):
            noise = random.randint(-3, 3)
            draw.point((x, y), fill=(r+noise, g+noise, b+noise))

    # Stars
    random.seed(42)
    for _ in range(300):
        x=random.randint(0,W); y=random.randint(0,int(H*0.5))
        s=random.choice([1,1,2,2,3]); c=random.choice([(255,255,200),(255,200,150),(200,200,255)])
        draw.ellipse([x,y,x+s,y+s], fill=c)

    # Moon
    mx, my = W//2, 180
    draw.ellipse([mx-100,my-100,mx+100,my+100], fill=(255,240,200))
    for r in range(110,150,5):
        draw.ellipse([mx-r,my-r,mx+r,my+r], fill=(255,240,200,max(0,60-r)//10))

    # Vacant lot ground — fence silhouette
    draw.rectangle([(0,int(H*0.7)),(W,H)], fill=(18,12,8))
    # Chain-link fence
    for fx in range(0,W,40):
        draw.line([(fx,int(H*0.55)),(fx,int(H*0.7))], fill=(25,25,28), width=3)
        draw.line([(fx,int(H*0.55)),(fx+20,int(H*0.55)-15)], fill=(25,25,28), width=3)
    # Horizontal fence wires
    for fy in range(int(H*0.58),int(H*0.7),12):
        draw.line([(0,fy),(W,fy)], fill=(20,20,22), width=1)

    # Market stalls emerging from vacant lot
    random.seed(123)
    for i in range(4):
        sx=100+i*350+random.randint(-20,20); sy=int(H*0.38)
        sw=240+random.randint(-20,30); sh=220+random.randint(-20,30)
        draw.rectangle([sx,sy,sx+12,sy+sh], fill=random.choice([(80,40,30),(60,50,40)]))
        draw.rectangle([sx+sw-12,sy,sx+sw,sy+sh], fill=random.choice([(80,40,30),(60,50,40)]))
        draw.polygon([(sx-20,sy),(sx+sw+20,sy),(sx+sw+10,sy-25),(sx-10,sy-25)], fill=(139,69,19))
        draw.rectangle([sx+12,sy+sh-35,sx+sw-12,sy+sh], fill=(101,67,33))

    # Lanterns: amber, green, blue
    random.seed(456)
    for x in range(80,W-80,50):
        ly=int(H*0.33)+random.randint(-8,8)
        lc=random.choice([(255,200,50),(255,150,50),(150,200,255),(100,200,100)])
        draw.line([x,int(H*0.28),x,ly], fill=(80,60,40), width=1)
        draw.ellipse([x-8,ly-3,x+8,ly+19], fill=lc)
        for g in range(25,0,-5):
            a=int(35*(1-g/25))
            draw.ellipse([x-g,ly-g,x+g,ly+g], fill=(lc[0],lc[1],lc[2],a//4))

    # Boy figure at fence browsing
    bx, by = W//2, int(H*0.635)
    draw.ellipse([bx-8,by-25,bx+8,by-8], fill=(15,10,8))
    draw.rectangle([bx-10,by-8,bx+10,by+12], fill=(15,10,8))
    draw.line([(bx-8,by+12),(bx-10,by+30)], fill=(15,10,8), width=4)
    draw.line([(bx+8,by+12),(bx+10,by+30)], fill=(15,10,8), width=4)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    create_cover(args.metadata, args.out)


if __name__ == "__main__":
    main()