#!/usr/bin/env python3
"""Cover: The Mountain Will Not Fall — dark storm sky, K2 massif, rope zigzag, snow streaks."""

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
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Dark storm sky to gray-white gradient
    for y in range(H):
        t = y / H
        if t < 0.5:
            r = int(40 + 60 * (t * 2))
            g = int(50 + 70 * (t * 2))
            b = int(75 + 80 * (t * 2))
        else:
            r = int(100 + 155 * ((t - 0.5) * 2))
            g = int(120 + 135 * ((t - 0.5) * 2))
            b = int(155 + 100 * ((t - 0.5) * 2))
        draw.line((0, y, W, y), fill=(max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), 255))

    # Storm clouds
    cloud_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cloud_layer)
    for _ in range(30):
        cx = random.randint(0, W)
        cy = random.randint(0, 600)
        cr = random.randint(80, 250)
        ca = random.randint(15, 40)
        cd.ellipse((cx - cr, cy - cr // 2, cx + cr, cy + cr // 2), fill=(180, 185, 190, ca))
    cloud_layer = cloud_layer.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, cloud_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # K2 triangular massif
    peak_points = [(W//2-200,1400),(W//2,150),(W//2+220,1400)]
    draw.polygon(peak_points, fill=(200,200,210,180))
    draw.polygon(peak_points, fill=None, outline=(160,160,170,200), width=3)
    # Snow cap
    draw.polygon([(W//2-40,350),(W//2,150),(W//2+45,350),(W//2,380)], fill=(240,245,250,220))
    # Ridge lines
    for x1,y1,x2,y2 in [(W//2-160,800,W//2-60,500),(W//2+170,900,W//2+60,550)]:
        draw.line((x1,y1,x2,y2), fill=(180,185,195,150), width=3)
    # Secondary peaks
    draw.polygon([(100,1400),(300,400),(500,1400)], fill=(170,175,185,120))
    draw.polygon([(1100,1400),(1300,550),(1500,1400)], fill=(165,170,180,110))
    # Climbing rope zigzag
    for x1,y1,x2,y2 in [(W//2-180,1350,W//2-150,1200),(W//2-150,1200,W//2-100,1050),
                         (W//2-100,1050,W//2-120,900),(W//2-120,900,W//2-60,750),
                         (W//2-60,750,W//2-80,600),(W//2-80,600,W//2-30,450)]:
        draw.line((x1,y1,x2,y2), fill=(220,150,50,180), width=5)
    # Snow streaks
    for _ in range(60):
        sx, sy, sl = random.randint(0,W), random.randint(0,1500), random.randint(10,50)
        draw.line((sx,sy,sx+sl,sy+sl//3), fill=(255,255,255,random.randint(10,35)), width=random.randint(1,3))
    # Snow particles
    for _ in range(120):
        px, py, pr = random.randint(0,W), random.randint(0,1800), random.randint(1,4)
        draw.ellipse((px-pr,py-pr,px+pr,py+pr), fill=(255,255,255,random.randint(40,120)))
    # Crevasse lines
    for _ in range(8):
        cx, cy, cw = random.randint(100,W-100), random.randint(1300,1500), random.randint(60,150)
        draw.arc((cx,cy,cx+cw,cy+30), start=random.randint(0,180), end=random.randint(180,360), fill=(100,110,130,120), width=3)

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