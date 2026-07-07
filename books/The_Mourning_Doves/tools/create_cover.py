#!/usr/bin/env python3
"""Cover: The Mourning Doves — crumbling manor on violet-moonlit gradient, mourning doves in flight over frozen fountain."""

from __future__ import annotations
import argparse, json, math, random
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
    candidates = [FONT_DIR / name, FONT_DIR / "georgia.ttf", FONT_DIR / "arial.ttf"]
    for c in candidates:
        if c.exists():
            return ImageFont.truetype(str(c), size)
    return ImageFont.load_default()


def wrap(draw: ImageDraw, text: str, font: ImageFont, max_w: int) -> list[str]:
    words = text.split()
    lines, current = [], []
    for w in words:
        test = " ".join([*current, w])
        if draw.textbbox((0, 0), test, font=font)[2] <= max_w:
            current.append(w)
        else:
            if current:
                lines.append(" ".join(current))
            current = [w]
    if current:
        lines.append(" ".join(current))
    return lines


def centered(
    draw: ImageDraw, y: int, lines: list[str], font: ImageFont, fill, gap: int
) -> int:
    for line in lines:
        bb = draw.textbbox((0, 0), line, font=font)
        draw.text(((W - (bb[2] - bb[0])) // 2, y), line, font=font, fill=fill)
        y += bb[3] - bb[1] + gap
    return y


def make_cover(metadata_path: Path, output_path: Path) -> None:
    meta = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = meta["title"]
    author = meta.get("author", "Barış Kısır")
    model = meta.get("model", "")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Violet-moonlit gradient
    for y in range(H):
        t = y / H
        r = int(28 + 8 * t); g = int(14 + 6 * t); b = int(40 + 12 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # Moon glow behind manor
    moon = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(moon)
    md.ellipse((W-380, 60, W-140, 340), fill=(200,195,180,100))
    moon = moon.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, moon)
    draw = ImageDraw.Draw(img)

    # Crumbling manor silhouette
    cx, cy = W//2, 1050
    draw.polygon([(cx-450,cy+200),(cx-450,cy-100),(cx-250,cy-100),(cx-250,cy-300),
                  (cx+250,cy-300),(cx+250,cy-100),(cx+450,cy-100),(cx+450,cy+200)], fill=(8,5,12,230))
    draw.rectangle((cx-400,cy-450,cx-250,cy-300), fill=(8,5,12,230))
    draw.polygon([(cx-430,cy-450),(cx-220,cy-450),(cx-325,cy-520)], fill=(8,5,12,230))
    draw.rectangle((cx+250,cy-480,cx+400,cy-300), fill=(8,5,12,230))
    draw.polygon([(cx+220,cy-480),(cx+430,cy-480),(cx+325,cy-560)], fill=(8,5,12,230))
    draw.polygon([(cx-250,cy-300),(cx-150,cy-260),(cx-50,cy-310),
                  (cx+50,cy-270),(cx+150,cy-250),(cx+250,cy-300)], fill=(8,5,12,230))
    # Lit window
    draw.rectangle((cx-30,cy-180,cx+30,cy-120), fill=(160,130,70,100))
    # Broken edges
    for dx in [-460,-440,440,460]:
        draw.polygon([(dx,cy+200),(dx+20,cy+200),(dx+10,cy+240)], fill=(12,8,16,200))

    # Twisted bare trees
    for tx in [cx-500,cx-380,cx+380,cx+500]:
        for _ in range(6):
            sx=tx+random.randint(-20,20); ex=sx+random.randint(-80,80)
            ey=cy+50-random.randint(0,100)
            draw.line((sx,cy+100,ex,ey), fill=(3,2,5,200), width=random.randint(2,4))
            for _ in range(3):
                bx=ex+random.randint(-40,40); by=ey-random.randint(20,60)
                draw.line((ex,ey,bx,by), fill=(3,2,5,180), width=2)

    # Mourning doves in flight
    for i in range(6):
        dx=180+i*260+random.randint(-20,20); dy=200+i*50+random.randint(-15,15)
        draw.ellipse((dx-14,dy-7,dx+14,dy+7), fill=(165,160,155,90))
        draw.polygon([(dx+14,dy),(dx+28,dy-7),(dx+22,dy+2)], fill=(165,160,155,90))
        draw.polygon([(dx-14,dy),(dx-28,dy-5),(dx-22,dy+2)], fill=(165,160,155,90))

    # Fog layers over grounds and frozen fountain
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog)
    fd.ellipse((-300,1400,W+300,1900), fill=(170,165,160,30))
    fd.ellipse((-200,1600,W+200,2100), fill=(180,175,170,25))
    fog = fog.filter(ImageFilter.GaussianBlur(50))
    img = Image.alpha_composite(img, fog)
    draw = ImageDraw.Draw(img)

    # Frozen fountain silhouette
    draw.ellipse((cx-80,cy+300,cx+80,cy+360), fill=(25,20,30,180))
    draw.line((cx,cy+300,cx,cy+220), fill=(60,55,65,120), width=6)
    draw.ellipse((cx-40,cy+200,cx+40,cy+240), fill=(50,45,55,100))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(str(output_path), "PNG", optimize=True)



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    mp = ROOT / args.metadata if not args.metadata.is_absolute() else args.metadata
    op = ROOT / args.out if not args.out.is_absolute() else args.out
    make_cover(mp, op)


if __name__ == "__main__":
    main()