#!/usr/bin/env python3
"""Cover: The Long Count — a boxing ring in amber light."""

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

    # Amber-charcoal gradient: dark floor, amber sky
    for y in range(H):
        t = y / H
        if y < 1600:
            r = int(180 - 60 * t)
            g = int(120 - 40 * t)
            b = int(40 - 20 * t)
        else:
            # dark floor gradient
            r = int(60 - 40 * (y - 1600) / 960)
            g = int(40 - 30 * (y - 1600) / 960)
            b = int(20 - 15 * (y - 1600) / 960)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Arena light beams from above (radial glow)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    for cx in range(400, W, 400):
        for layer in range(3):
            r = 200 + layer * 80
            a = 20 - layer * 6
            gdraw.ellipse((cx - r, -r, cx + r, r), fill=(255, 220, 150, max(0, a)))
    glow = glow.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Boxing ring (trapezoid perspective from above-angle)
    ring_color = (180, 140, 100, 220)
    ring_floor = [(300, 1700), (1300, 1700), (1200, 1500), (400, 1500)]
    draw.polygon(ring_floor, fill=(100, 70, 40, 200), outline=(200, 160, 100, 255), width=3)

    # Rope posts
    posts = [(400, 1400), (1200, 1400), (300, 1680), (1300, 1680)]
    for px, py in posts:
        draw.rectangle((px - 6, py - 20, px + 6, py + 60), fill=(60, 50, 40, 255))
        # ropes
        for ry in range(py - 10, py + 30, 12):
            draw.line((px - 6, ry, px + 6, ry), fill=(200, 180, 160, 200), width=2)

    # Top ropes (between posts)
    rope_y1 = 1390
    rope_y2 = 1420
    rope_y3 = 1450
    for r in [rope_y1, rope_y2, rope_y3]:
        draw.arc((370, r, 1230, r + 80), 180, 0, fill=(220, 200, 180, 200), width=5)

    # Single figure silhouette — fighter mid-punch
    fx, fy = 800, 1620
    # Body
    draw.ellipse((fx - 20, fy - 80, fx + 20, fy + 10), fill=(15, 12, 10, 240))
    # Head
    draw.ellipse((fx - 18, fy - 115, fx + 18, fy - 80), fill=(15, 12, 10, 240))
    # Left arm (jabbing forward)
    draw.line((fx - 15, fy - 60, fx - 120, fy - 100), fill=(15, 12, 10, 240), width=10)
    # Left glove
    draw.ellipse((fx - 130, fy - 110, fx - 110, fy - 90), fill=(200, 40, 40, 230))
    # Right arm (cocked back)
    draw.line((fx + 15, fy - 55, fx + 80, fy - 100), fill=(15, 12, 10, 240), width=10)
    # Right glove
    draw.ellipse((fx + 70, fy - 110, fx + 90, fy - 90), fill=(200, 40, 40, 230))
    # Legs
    draw.line((fx - 8, fy + 10, fx - 30, fy + 80), fill=(15, 12, 10, 240), width=12)
    draw.line((fx + 8, fy + 10, fx + 30, fy + 80), fill=(15, 12, 10, 240), width=12)

    # Shadow on canvas
    draw.ellipse((fx - 70, fy + 75, fx + 70, fy + 95), fill=(15, 12, 10, 80))

    # Sweat droplets (sparkle dots)
    for _ in range(40):
        sx = int(600 + 400 * __import__("random").random())
        sy = int(1400 + 350 * __import__("random").random())
        sr = int(1 + 3 * __import__("random").random())
        sa = int(60 + 100 * __import__("random").random())
        draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=(255, 240, 200, sa))

    # Title panel at bottom
    # Top accent line
    # Bottom accent line
    draw.line((200, H - 180, W - 200, H - 180), fill=(220, 180, 100, 120), width=2)

    tf = font("georgiab.ttf", 110)
    af = font("arialbd.ttf", 42)
    sf = font("arial.ttf", 30)

    # Genre tag
    y = centered(draw, 1980, ["SPORTS DRAMA"], sf, (200, 160, 100), 6)
    y += 30

    # Title (wrapped if needed)
    title_lines = wrap(draw, title.upper(), tf, 1200)
    y = centered(draw, y, title_lines, tf, (220, 185, 120), 10)
    y += 40

    # Author
    centered(draw, y, [author], af, (200, 190, 170), 6)

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