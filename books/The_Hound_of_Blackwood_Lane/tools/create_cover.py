#!/usr/bin/env python3
"""Cover: The Hound of Blackwood Lane — a cozy English village mystery."""

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
        if c.exists(): return ImageFont.truetype(str(c), size)
    return ImageFont.load_default()

def wrap(draw, text, fnt, mw):
    words, lines, cur = text.split(), [], []
    for w in words:
        p = " ".join([*cur, w])
        if draw.textbbox((0,0), p, font=fnt)[2] <= mw: cur.append(w)
        else: lines.append(" ".join(cur)); cur = [w]
    if cur: lines.append(" ".join(cur))
    return lines

def centered(draw, y, lines, fnt, fill, gap):
    for line in lines:
        bb = draw.textbbox((0,0), line, font=fnt)
        draw.text(((W-(bb[2]-bb[0]))//2, y), line, font=fnt, fill=fill)
        y += bb[3]-bb[1] + gap
    return y

def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title, author = m["title"], m.get("author", "Barış Kısır")
    model = m.get("model", "")
    img = Image.new("RGBA", (W, H), (0,0,0,255)); draw = ImageDraw.Draw(img, "RGBA")

    # Warm countryside gradient: golden yellow to soft green to sky blue
    for y in range(H):
        t = y / H
        if t < 0.4:
            # Sky: pale blue to warm yellow
            r = int(180 + 60 * (t / 0.4))
            g = int(190 + 40 * (t / 0.4))
            b = int(220 - 40 * (t / 0.4))
        elif t < 0.7:
            # Hills: warm green-yellow
            r = int(200 - 60 * ((t - 0.4) / 0.3))
            g = int(210 - 40 * ((t - 0.4) / 0.3))
            b = int(140 - 40 * ((t - 0.4) / 0.3))
        else:
            # Lower: deeper green
            r = int(120 - 40 * ((t - 0.7) / 0.3))
            g = int(150 - 30 * ((t - 0.7) / 0.3))
            b = int(80 - 20 * ((t - 0.7) / 0.3))
        draw.line((0,y,W,y), fill=(max(0,r),max(0,g),max(0,b),255))

    # Rolling hills in background
    hill = Image.new("RGBA", (W, H), (0,0,0,0)); hd = ImageDraw.Draw(hill)
    # Far hills
    for i, (cy, cw, ch, col) in enumerate([
        (780, 1800, 200, (140, 170, 90, 120)),
        (820, 1600, 180, (120, 155, 80, 130)),
        (850, 1400, 160, (100, 140, 70, 140)),
    ]):
        hd.ellipse(((W-cw)//2, cy, (W+cw)//2, cy+ch*2), fill=col)
    hill = hill.filter(ImageFilter.GaussianBlur(12))
    img = Image.alpha_composite(img, hill); draw = ImageDraw.Draw(img, "RGBA")

    # Village buildings silhouette
    build = Image.new("RGBA", (W,H), (0,0,0,0)); bd = ImageDraw.Draw(build)
    # Church spire
    bx, by = W//2, 1050
    bd.polygon([(bx-15, by+120), (bx-15, by), (bx, by-60), (bx+15, by), (bx+15, by+120)], fill=(70, 55, 45, 200))
    bd.rectangle((bx-40, by+20, bx+40, by+120), fill=(80, 65, 55, 200))
    # Cross on spire
    bd.line((bx, by-60, bx, by-75), fill=(60, 45, 35, 200), width=3)
    bd.line((bx-10, by-68, bx+10, by-68), fill=(60, 45, 35, 200), width=3)
    # Cottages
    for i, (ox, ow, oh, ol) in enumerate([
        (bx-200, 120, 80, (70, 58, 48)),
        (bx-250, 100, 70, (75, 62, 50)),
        (bx+130, 110, 75, (72, 60, 48)),
        (bx+180, 130, 85, (68, 55, 45)),
        (bx-320, 90, 65, (78, 65, 52)),
        (bx+250, 95, 70, (74, 60, 48)),
    ]):
        bd.rectangle((ox, by+120-oh, ox+ow, by+120), fill=(*ol, 200))
        # Roof
        bd.polygon([(ox-5, by+120-oh), (ox+ox, by+120-oh-25), (ox+ow+5, by+120-oh)], fill=(55, 42, 35, 200))

    # Bookshop window (warm glow)
    bswx, bswy = bx-100, by+10
    bd.rectangle((bswx, bswy, bswx+60, bswy+70), fill=(180, 150, 70, 150))
    bd.rectangle((bswx-8, bswy-10, bswx+68, bswy-5), fill=(55, 42, 35, 200))
    bd.text((bswx+5, bswy+5), "BOOKS", font=font("arial.ttf", 14), fill=(50, 35, 25, 200))

    build = build.filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(img, build); draw = ImageDraw.Draw(img, "RGBA")

    # Trees silhouette
    tree = Image.new("RGBA", (W,H), (0,0,0,0)); td = ImageDraw.Draw(tree)
    for tx in range(80, W, 250):
        th = 200 + int(80 * math.sin(tx * 0.01))
        td.polygon([(tx-30, by+120), (tx, by+120-th), (tx+30, by+120)], fill=(40, 55, 30, 100))
        td.rectangle((tx-5, by+120-20, tx+5, by+120), fill=(50, 40, 30, 100))
    tree = tree.filter(ImageFilter.GaussianBlur(5))
    img = Image.alpha_composite(img, tree); draw = ImageDraw.Draw(img, "RGBA")

    # Warm sun glow in sky
    sun = Image.new("RGBA", (W,H), (0,0,0,0)); sd = ImageDraw.Draw(sun)
    sd.ellipse((W-400, 100, W-100, 400), fill=(255, 220, 120, 100))
    sun = sun.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img, sun); draw = ImageDraw.Draw(img, "RGBA")

    # Light rectangle title panel
    draw.rectangle((0, 1920, W, H), fill=(255, 248, 235, 240))
    # Decorative lines
    draw.line((200, 1960, W-200, 1960), fill=(140, 120, 80, 150), width=2)
    draw.line((200, H-180, W-200, H-180), fill=(140, 120, 80, 100), width=1)

    # Title
    tf = font("georgiab.ttf", 100)
    wrapped = wrap(draw, title, tf, 1200)
    y = centered(draw, 2000, wrapped, tf, (40, 35, 30), 8)
    y += 40

    # Location subtitle
    lf = font("arial.ttf", 30)
    centered(draw, y, ["A BLACKWOOD LANE MYSTERY"], lf, (120, 100, 70), 4)
    y += 60

    # Author
    af = font("arialbd.ttf", 42)
    centered(draw, y, [author], af, (60, 50, 40), 4)

    # Small decorative dog silhouette at bottom
    hound = Image.new("RGBA", (W,H), (0,0,0,0)); hd = ImageDraw.Draw(hound)
    hx, hy = W//2, H-120
    col = (60, 50, 40, 80)
    # Body
    hd.ellipse((hx-20, hy-8, hx+20, hy+8), fill=col)
    # Head
    hd.ellipse((hx-28, hy-14, hx-12, hy), fill=col)
    # Legs
    hd.rectangle((hx-14, hy+2, hx-8, hy+18), fill=col)
    hd.rectangle((hx+4, hy+2, hx+10, hy+18), fill=col)
    # Tail
    hd.polygon([(hx+18, hy-2), (hx+30, hy-12), (hx+22, hy)], fill=col)
    hound = hound.filter(ImageFilter.GaussianBlur(1))
    img = Image.alpha_composite(img, hound)

    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op, "PNG", optimize=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", required=True, type=Path); p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    make_cover(ROOT/a.metadata if not a.metadata.is_absolute() else a.metadata, ROOT/a.out if not a.out.is_absolute() else a.out)

if __name__ == "__main__": main()