#!/usr/bin/env python3
"""Cover: The Deep Between Stars — Black/deep blue/teal abyssal gradient, bioluminescent particles, research sub silhouette, deep blue/cyan/white."""

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

def font(name: str, size: int):
    for candidate in (FONT_DIR / name, FONT_DIR / "arialbd.ttf", FONT_DIR / "arial.ttf"):
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()

def wrap(draw, text, fnt, max_width):
    words, lines, cur = text.split(), [], []
    for w in words:
        p = " ".join([*cur, w])
        if draw.textbbox((0, 0), p, font=fnt)[2] <= max_width:
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
    author = m.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        if t < 0.3:
            v = int(5 + 10 * (t / 0.3))
            r, g, b = v, v, v + 8
        elif t < 0.7:
            s = (t - 0.3) / 0.4
            r = int(5 + 15 * s)
            g = int(5 + 30 * s)
            b = int(13 + 80 * s)
        else:
            s2 = (t - 0.7) / 0.3
            r = int(20 - 10 * s2)
            g = int(35 - 20 * s2)
            b = int(93 - 50 * s2)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    for _ in range(30):
        x = int(W * random.random())
        y = int(200 + 1400 * random.random())
        rad = int(20 + 80 * random.random())
        alpha = int(15 + 40 * random.random())
        gdraw.ellipse((x - rad, y - rad, x + rad, y + rad), fill=(60, 180, 220, alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    for _ in range(200):
        x = int(W * random.random())
        y = int(300 + 1400 * random.random())
        r = int(2 + 5 * random.random())
        alpha = int(20 + 80 * random.random())
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(100 + int(100 * random.random()), 200, 220, alpha))

    pts_left = [(0, 400)]
    for y in range(400, 1600, 10):
        offset = int(80 + 40 * (1 + math.sin(y * 0.02 + 1.3)) * 0.5)
        x = 100 + offset + int(30 * (1 + math.sin(y * 0.015)))
        pts_left.append((x, y))
    pts_left += [(0, 1600)]
    draw.polygon(pts_left, fill=(10, 15, 30, 220))

    pts_right = [(W, 400)]
    for y in range(400, 1600, 10):
        offset = int(80 + 40 * (1 + math.sin(y * 0.018 + 2.1)) * 0.5)
        x = W - 100 - offset - int(30 * (1 + math.sin(y * 0.012 + 0.7)))
        pts_right.append((x, y))
    pts_right += [(W, 1600)]
    draw.polygon(pts_right, fill=(8, 12, 25, 220))

    station_x, station_y = W // 2, 1100
    draw.rectangle((station_x - 35, station_y - 55, station_x + 35, station_y + 55), fill=(55, 65, 85, 200), outline=(100, 140, 180, 180), width=2)
    draw.rectangle((station_x - 48, station_y - 25, station_x - 35, station_y + 25), fill=(45, 55, 75, 200))
    draw.rectangle((station_x + 35, station_y - 35, station_x + 48, station_y + 35), fill=(45, 55, 75, 200))

    for ang in [-1, 0, 1]:
        lx = station_x + ang * 25
        ly = station_y + 55
        for i in range(6):
            alpha_f = 35 - 5 * i
            w = 6 + i * 5
            draw.ellipse((lx - w, ly + i * 7 - 2, lx + w, ly + i * 7 + 2), fill=(180, 220, 255, alpha_f))

    for wy in range(-35, 36, 18):
        draw.rectangle((station_x - 4, station_y + wy - 3, station_x + 4, station_y + wy + 3), fill=(200, 230, 255, 220))

    slayer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(slayer)
    sdraw.ellipse((station_x - 100, station_y - 80, station_x + 100, station_y + 80), fill=(80, 150, 220, 25))
    slayer = slayer.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(img, slayer)
    draw = ImageDraw.Draw(img, "RGBA")

    draw.line((station_x, station_y + 55, W // 2 + 25, 1700), fill=(40, 50, 70, 150), width=2)
    draw.ellipse((W // 2 + 8, 1480, W // 2 + 45, 1510), fill=(50, 65, 90, 200))

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
