#!/usr/bin/env python3
"""Cover: The Overburden — Alpine tunnel interior with collapse debris, rescue lights in darkness."""

import argparse
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageColor

# Import shared helpers
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import (
    _standard_cover_font, _standard_cover_repair_text, _standard_cover_wrap,
    _standard_cover_center, _standard_cover_title_font,
    _standard_cover_resolve_title, _standard_cover_resolve_author,
    _draw_standard_cover_title_panel,
)


def make_cover(metadata: dict) -> Image.Image:
    title = _standard_cover_resolve_title(locals())
    author = _standard_cover_resolve_author(locals())
    model = metadata.get("model", "")

    W, H = 1600, 2560
    img = Image.new("RGB", (W, H), (10, 10, 18))
    draw = ImageDraw.Draw(img)

    # Alpine tunnel interior — dark concrete walls
    for y in range(H):
        t = y/H
        r = int(15+10*t); g = int(15+10*t); b = int(22+12*t)
        draw.line([(0,y),(W,y)], fill=(r,g,b))

    # Tunnel arch walls converging inward
    draw.polygon([(0,0),(W,0),(W,600),(0,600)], fill=(25,25,32))
    draw.polygon([(0,0),(W,0),(W,200),(0,200)], fill=(35,35,42))
    # Tunnel ceiling
    draw.arc([(100,-200),(W-100,600)], 180, 360, fill=(30,30,38), width=40)
    # Concrete ribs
    for rx in range(0,W,300):
        draw.arc([(rx-50,-250),(rx+350,650)], 180, 360, fill=(40,40,48), width=12)
    # Side walls converging
    draw.polygon([(0,200),(120,200),(120,1800),(0,1800)], fill=(22,22,28))
    draw.polygon([(W,200),(W-120,200),(W-120,1800),(W,1800)], fill=(22,22,28))

    # Collapse debris — broken concrete and rock pile
    rng=__import__('random').Random(42)
    for _ in range(80):
        x=rng.randint(200,W-200); y=rng.randint(800,1400)
        s=rng.randint(10,60); sh=rng.randint(20,45)
        draw.polygon([(x,y),(x+s,y-s//2),(x+s*2,y),(x+s,y+s//2)], fill=(sh,sh,sh+5))
    # Large boulders
    for _ in range(15):
        x=rng.randint(200,W-200); y=rng.randint(700,1300)
        sr=rng.randint(30,80)
        draw.ellipse((x-sr,y-sr//2,x+sr,y+sr//2), fill=(rng.randint(25,40),rng.randint(25,40),rng.randint(28,45)))

    # Rescue lights in darkness — multiple small orange/white glows
    for i in range(8):
        lx=rng.randint(300,W-300); ly=rng.randint(800,1200)
        glow=Image.new("RGBA",(W,H),(0,0,0,0)); gd=ImageDraw.Draw(glow)
        gd.ellipse((lx-50,ly-50,lx+50,ly+50), fill=(255,200,80,80))
        glow=glow.filter(ImageFilter.GaussianBlur(15))
        img=Image.alpha_composite(img.convert("RGBA"),glow).convert("RGB")
        draw=ImageDraw.Draw(img)
        draw.ellipse((lx-8,ly-8,lx+8,ly+8), fill=(255,220,120))
        draw.ellipse((lx-4,ly-4,lx+4,ly+4), fill=(255,255,200))
    # Headlamp beams cutting through darkness
    for bx, by in [(500,1000),(1100,950)]:
        for angle in range(-15,16,5):
            rad=math.radians(angle)
            ex=bx+int(300*math.cos(rad)); ey=by+int(300*math.sin(rad))
            draw.line((bx,by,ex,ey), fill=(200,220,255,20), width=6)

    _draw_standard_cover_title_panel(img, title, author, model)
    return img


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate cover for The Overburden")
    parser.add_argument("--metadata", required=True, help="Path to metadata JSON")
    parser.add_argument("--out", required=True, help="Output PNG path")
    args = parser.parse_args()

    with open(args.metadata, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    img = make_cover(metadata)
    img.save(args.out)
    print(f"Cover saved to {args.out}")
