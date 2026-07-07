#!/usr/bin/env python3
"""Cover: The Last Rose of Summer — Provence garden, widow tending rare pink rose, warm Mediterranean tones, lavender purple/rose pink/stone white."""

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

def font(n, s):
    for c in [FONT_DIR / n, FONT_DIR / "arialbd.ttf", FONT_DIR / "arial.ttf"]:
        if c.exists(): return ImageFont.truetype(str(c), s)
    return ImageFont.load_default()

def wrap(d, t, f, w):
    wo = t.split(); li = []; cu = []
    for wd in wo:
        p = " ".join([*cu, wd])
        if d.textbbox((0, 0), p, font=f)[2] <= w: cu.append(wd)
        else: li.append(" ".join(cu)); cu = [wd]
    if cu: li.append(" ".join(cu))
    return li

def centered(d, y, li, f, fl, g):
    for l in li:
        bb = d.textbbox((0, 0), l, font=f)
        d.text(((W - (bb[2] - bb[0])) // 2, y), l, font=f, fill=fl)
        y += bb[3] - bb[1] + g
    return y

def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    ti = m["title"]
    au = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (255, 200, 210, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Sunset gradient: warm pink to lavender to deep purple
    for y in range(H):
        t = y / H
        if t < 0.4:
            # Top: warm sunset pinks and oranges
            r = int(255 - 60 * (t / 0.4))
            g = int(180 - 40 * (t / 0.4))
            b = int(180 + 30 * (t / 0.4))
        elif t < 0.7:
            # Middle: lavender and purple
            r = int(195 - 40 * ((t - 0.4) / 0.3))
            g = int(140 + 20 * ((t - 0.4) / 0.3))
            b = int(210 + 10 * ((t - 0.4) / 0.3))
        else:
            # Bottom: deep twilight
            r = int(155 - 60 * ((t - 0.7) / 0.3))
            g = int(160 - 50 * ((t - 0.7) / 0.3))
            b = int(220 - 30 * ((t - 0.7) / 0.3))
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    draw = ImageDraw.Draw(img, "RGBA")

    # Sun disk
    sun_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sun_layer)
    sd.ellipse((W // 2 - 200, 500, W // 2 + 200, 900), fill=(255, 200, 100, 200))
    sun_layer = sun_layer.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, sun_layer)

    # Provence villa silhouette
    draw = ImageDraw.Draw(img, "RGBA")
    villa_x = W // 2 - 180
    villa_y = 1000
    # Main house body
    draw.rectangle((villa_x, villa_y, villa_x + 360, villa_y + 300), fill=(80, 60, 100, 160))
    # Roof
    draw.polygon([(villa_x - 30, villa_y), (villa_x + 390, villa_y), (villa_x + 180, villa_y - 120)], fill=(60, 40, 80, 180))
    # Windows (lit)
    for wx, wy in [(villa_x + 40, villa_y + 60), (villa_x + 160, villa_y + 60),
                    (villa_x + 280, villa_y + 60), (villa_x + 40, villa_y + 180),
                    (villa_x + 160, villa_y + 180), (villa_x + 280, villa_y + 180)]:
        draw.rectangle((wx, wy, wx + 50, wy + 70), fill=(255, 220, 140, 200))
    # Door
    draw.rectangle((villa_x + 145, villa_y + 200, villa_x + 215, villa_y + 300), fill=(40, 30, 60, 200))

    # Cypress trees
    for cx, ch in [(W // 2 - 400, 500), (W // 2 + 400, 550)]:
        draw.rectangle((cx, villa_y + 300 - ch, cx + 30, villa_y + 300), fill=(40, 60, 40, 180))

    # Rolling hills in background
    for hx, hy, hr in [(200, 1100, 600), (600, 1150, 500), (1000, 1080, 550), (1400, 1120, 450)]:
        draw.ellipse((hx - hr, hy - hr // 2, hx + hr, hy + hr // 2), fill=(120, 80, 120, 80))

    # Rose garden — rows of rose bushes with blooms
    rose_start_y = 1350
    for row in range(6):
        ry = rose_start_y + row * 45
        for col in range(11):
            rx = 150 + col * 120
            # Bush
            draw.ellipse((rx - 25, ry - 20, rx + 25, ry + 25), fill=(40, 70, 40, 200))
            # Rose bloom — various pinks
            rose_color = (
                int(220 + 35 * math.sin(row + col)),
                int(100 + 60 * math.sin(row * 2 + col * 3)),
                int(140 + 50 * math.cos(row + col * 2)),
                220
            )
            draw.ellipse((rx - 10, ry - 25, rx + 10, ry - 5), fill=rose_color)
            # Inner highlight
            draw.ellipse((rx - 4, ry - 19, rx + 4, ry - 11), fill=(255, 200, 220, 180))

    # Lavender field in foreground
    for lx in range(0, W, 15):
        ly = 1700 + int(20 * math.sin(lx * 0.05))
        draw.ellipse((lx - 3, ly - 8, lx + 3, ly + 8), fill=(140, 100, 200, 160))

    # Title panel at bottom
    panel_y = 1920
    draw.rectangle((0, panel_y, W, H), fill=(25, 15, 40, 235))
    # Top border line
    draw.line((200, panel_y + 15, W - 200, panel_y + 15), fill=(255, 180, 200, 200), width=3)
    # Bottom border line
    draw.line((200, H - 140, W - 200, H - 140), fill=(255, 180, 200, 120), width=2)

    # Title
    tf = font("arialbd.ttf", 90)
    af = font("arialbd.ttf", 36)
    sf = font("arial.ttf", 28)

    # Title in white
    title_lines = wrap(draw, ti.upper(), tf, 1300)
    y = centered(draw, panel_y + 45, title_lines, tf, (255, 255, 255, 255), 10)

    # Author in white, slightly smaller
    y += 25
    bb = draw.textbbox((0, 0), au, font=af)
    draw.text(((W - (bb[2] - bb[0])) // 2, y), au, font=af, fill=(220, 200, 220, 255))

    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op, "PNG", optimize=True)



def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    make_cover(
        ROOT / a.metadata if not a.metadata.is_absolute() else a.metadata,
        ROOT / a.out if not a.out.is_absolute() else a.out
    )


if __name__ == "__main__":
    main()