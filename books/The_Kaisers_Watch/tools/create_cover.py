#!/usr/bin/env python3
"""Cover: The Kaiser's Watch — Berlin silhouettes at night, mist, imperial flags, floating clock face over Reichstag, iron-blue sky."""

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
    rng = __import__("random").Random(19)

    # Iron-blue night sky
    for y in range(H):
        t = y / H
        r = int(70 - 40 * t); g = int(85 - 45 * t); b = int(110 - 55 * t)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Berlin building silhouettes
    buildings = [
        (0, 880, 160, 1400), (140, 850, 130, 1430), (260, 900, 180, 1380),
        (420, 840, 110, 1450), (520, 880, 170, 1410), (680, 850, 150, 1440),
        (810, 890, 130, 1390), (930, 860, 190, 1420), (1080, 840, 140, 1450),
        (1200, 880, 160, 1410), (1340, 850, 130, 1430), (1460, 880, 110, 1400),
    ]
    for bx, by, bw, bh in buildings:
        draw.rectangle((bx, by, bx + bw, by + bh), fill=(20, 25, 35, 220))
        for wy in range(by + 25, by + bh - 35, 45):
            for wx in range(bx + 12, bx + bw - 12, 30):
                if rng.random() > 0.3:
                    draw.rectangle((wx, wy, wx + 10, wy + 15), fill=(200, 180, 120, 50))

    # Reichstag silhouette (center, with dome)
    rx, ry = W // 2 - 100, 750
    draw.polygon([(rx, ry + 200), (rx, ry), (rx + 200, ry), (rx + 200, ry + 200)], fill=(18, 22, 30, 220))
    # Dome
    draw.ellipse((rx + 60, ry - 60, rx + 140, ry + 20), fill=(18, 22, 30, 220))
    draw.polygon([(rx + 80, ry - 60), (rx + 120, ry - 60), (rx + 100, ry - 100)], fill=(18, 22, 30, 220))

    # Imperial flags
    for fx, fy in [(180, 850), (480, 840), (780, 890), (1030, 860)]:
        draw.rectangle((fx, fy - 100, fx + 3, fy), fill=(90, 80, 70, 220))
        fw, fh = 45, 25
        draw.rectangle((fx + 3, fy - 100, fx + 3 + fw, fy - 100 + fh // 3), fill=(25, 25, 25, 220))
        draw.rectangle((fx + 3, fy - 100 + fh // 3, fx + 3 + fw, fy - 100 + 2 * fh // 3), fill=(210, 210, 210, 220))
        draw.rectangle((fx + 3, fy - 100 + 2 * fh // 3, fx + 3 + fw, fy - 100 + fh), fill=(170, 25, 25, 220))

    # Cobblestone street
    for y in range(1380, 1500, 6):
        shade = 45 + int(18 * __import__("math").sin(y * 0.1))
        draw.line((0, y, W, y), fill=(shade, shade - 3, shade - 8, 200))

    # Floating clock face over Reichstag
    cx, cy = W // 2, 520
    cr = 180
    draw.ellipse((cx - cr, cy - cr, cx + cr, cy + cr), fill=(170, 160, 130, 200))
    draw.ellipse((cx - cr + 10, cy - cr + 10, cx + cr - 10, cy + cr - 10), fill=(210, 205, 180, 230))
    draw.ellipse((cx - cr + 18, cy - cr + 18, cx + cr - 18, cy + cr - 18), fill=(235, 230, 210, 240))
    # Roman numerals (hour markers)
    for i in range(12):
        ang = __import__("math").radians(i * 30 - 90)
        x1 = cx + 140 * __import__("math").cos(ang)
        y1 = cy + 140 * __import__("math").sin(ang)
        x2 = cx + 162 * __import__("math").cos(ang)
        y2 = cy + 162 * __import__("math").sin(ang)
        draw.line((x1, y1, x2, y2), fill=(35, 35, 45, 220), width=5)
    # Hands
    ha = __import__("math").radians(35)
    ma = __import__("math").radians(168)
    draw.line((cx, cy, cx + 80 * __import__("math").cos(ha), cy + 80 * __import__("math").sin(ha)), fill=(35, 35, 45, 220), width=7)
    draw.line((cx, cy, cx + 120 * __import__("math").cos(ma), cy + 120 * __import__("math").sin(ma)), fill=(35, 35, 45, 220), width=4)
    draw.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), fill=(35, 35, 45, 220))

    # Clock glow
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    gd.ellipse((cx - cr - 25, cy - cr - 25, cx + cr + 25, cy + cr + 25), fill=(200, 190, 160, 18))
    glow = glow.filter(ImageFilter.GaussianBlur(20))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Mist overlay
    mist = Image.new("RGBA", (W, H), (0, 0, 0, 0)); md = ImageDraw.Draw(mist)
    for _ in range(20):
        mx = int(rng.random() * W)
        my = int(400 + 400 * rng.random())
        mw = int(300 + 500 * rng.random())
        mh = int(40 + 60 * rng.random())
        md.ellipse((mx - mw // 2, my - mh // 2, mx + mw // 2, my + mh // 2), fill=(180, 190, 210, 15))
    mist = mist.filter(ImageFilter.GaussianBlur(35))
    img = Image.alpha_composite(img, mist)

    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op, "PNG", optimize=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", required=True, type=Path); p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    make_cover(ROOT / a.metadata if not a.metadata.is_absolute() else a.metadata,
               ROOT / a.out if not a.out.is_absolute() else a.out)

if __name__ == "__main__":
    main()