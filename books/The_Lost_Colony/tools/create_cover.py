#!/usr/bin/env python3
"""Cover: The Lost Colony — Woman in deerskin cloak on forest ridge, basket at feet, ship as dark speck on horizon, forest green/cloak brown/sky gray."""

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

def wrap(d, t, f, w):
    words, lines, cur = t.split(), [], []
    for wd in words:
        p = " ".join([*cur, wd])
        if d.textbbox((0, 0), p, font=f)[2] <= w: cur.append(wd)
        else: lines.append(" ".join(cur)); cur = [wd]
    if cur: lines.append(" ".join(cur))
    return lines

def centered(d, y, lines, f, fl, g):
    for l in lines:
        bb = d.textbbox((0, 0), l, font=f)
        d.text(((W - (bb[2] - bb[0])) // 2, y), l, font=f, fill=fl)
        y += bb[3] - bb[1] + g
    return y

def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    ti = m["title"]
    au = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        if t < 0.3:
            r = int(100 + 30 * (t / 0.3))
            g = int(110 + 20 * (t / 0.3))
            b = int(120 + 15 * (t / 0.3))
        elif t < 0.55:
            r = int(130 + 40 * ((t - 0.3) / 0.25))
            g = int(130 + 50 * ((t - 0.3) / 0.25))
            b = int(135 + 40 * ((t - 0.3) / 0.25))
        else:
            r = int(170 + 10 * ((t - 0.55) / 0.45))
            g = int(180 - 20 * ((t - 0.55) / 0.45))
            b = int(175 - 60 * ((t - 0.55) / 0.45))
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    sea_top = int(H * 0.58)
    for y in range(sea_top, H):
        t = (y - sea_top) / (H - sea_top)
        r = int(140 - 40 * t)
        g = int(150 - 50 * t)
        b = int(150 - 50 * t)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b)))

    for x in range(0, W, 4):
        o = int(3 * math.sin(x * 0.02 + 1) + 2 * math.sin(x * 0.01))
        draw.point((x, sea_top + o), fill=(180, 190, 195, 80))

    ship_x, ship_y = W // 2 + 200, sea_top - 40
    draw.polygon([
        (ship_x - 30, ship_y + 8), (ship_x + 30, ship_y + 8),
        (ship_x + 20, ship_y - 8), (ship_x - 20, ship_y - 8),
    ], fill=(40, 35, 30, 200))
    draw.line([(ship_x, ship_y - 8), (ship_x, ship_y - 25)], fill=(40, 35, 30, 180), width=2)
    draw.line([(ship_x, ship_y - 25), (ship_x - 15, ship_y - 15)], fill=(40, 35, 30, 150), width=1)
    draw.line([(ship_x, ship_y - 25), (ship_x + 15, ship_y - 15)], fill=(40, 35, 30, 150), width=1)

    forests = [
        (200, int(H * 0.5), 400, 150),
        (600, int(H * 0.48), 500, 180),
        (1100, int(H * 0.50), 450, 160),
        (1500, int(H * 0.52), 350, 140),
    ]
    for fx, fy, fw, fh in forests:
        for _ in range(30):
            tx = fx + random.randint(-fw // 2, fw // 2)
            ty = fy + random.randint(-fh // 2, fh // 2)
            ts = random.randint(15, 40)
            tg = random.randint(30, 70)
            draw.ellipse([tx - ts, ty - ts // 2, tx + ts, ty + ts // 2],
                          fill=(tg, 50 + tg // 2, tg // 3, 200))

    ridge_y = int(H * 0.45)
    ridge_color = (50, 70, 40)
    draw.polygon([
        (0, ridge_y + 30), (200, ridge_y), (400, ridge_y + 10),
        (600, ridge_y - 5), (800, ridge_y), (1000, ridge_y + 15),
        (1200, ridge_y - 5), (1400, ridge_y + 10), (W, ridge_y + 5),
        (W, ridge_y + 100), (0, ridge_y + 100),
    ], fill=ridge_color)

    figure_x, figure_y = W // 2 - 80, ridge_y - 40
    draw.ellipse([figure_x - 8, figure_y - 22, figure_x + 8, figure_y - 8],
                  fill=(50, 40, 30))
    draw.polygon([
        (figure_x - 20, figure_y - 8), (figure_x + 20, figure_y - 8),
        (figure_x + 18, figure_y + 40), (figure_x - 18, figure_y + 40),
    ], fill=(90, 60, 40))
    draw.polygon([
        (figure_x - 22, figure_y - 10), (figure_x - 10, figure_y - 5),
        (figure_x - 8, figure_y + 35), (figure_x - 20, figure_y + 30),
    ], fill=(100, 70, 45))
    draw.line([(figure_x, figure_y + 40), (figure_x, figure_y + 65)], fill=(60, 45, 35), width=4)

    basket_x, basket_y = figure_x + 15, figure_y + 35
    draw.polygon([
        (basket_x - 12, basket_y + 15), (basket_x + 12, basket_y + 15),
        (basket_x + 16, basket_y), (basket_x - 16, basket_y),
    ], fill=(100, 75, 45))
    for bi in range(-14, 16, 7):
        draw.line([(basket_x + bi, basket_y), (basket_x + bi - 3, basket_y + 15)],
                   fill=(70, 55, 35), width=2)
    draw.line([(basket_x - 16, basket_y), (basket_x + 16, basket_y)],
               fill=(80, 60, 40), width=2)

    rng = random.Random(151)
    for _ in range(30):
        bx = rng.randint(50, W - 50)
        by = rng.randint(int(H * 0.1), int(H * 0.35))
        bs = rng.randint(1, 3)
        draw.ellipse([bx - bs, by - bs, bx + bs, by + bs],
                      fill=(rng.randint(180, 255), rng.randint(180, 255), rng.randint(180, 255)))

    draw.rectangle((0, 1920, W, H), fill=(15, 20, 15, 235))
    draw.line((300, 1960, W - 300, 1960), fill=(60, 100, 60, 150), width=2)

    tf = font("arialbd.ttf", 85)
    af = font("arialbd.ttf", 36)
    title_lines = wrap(draw, ti.upper(), tf, 1300)
    y = centered(draw, 1980, title_lines, tf, (200, 210, 200), 10)
    y += 50
    bb = draw.textbbox((0, 0), au, font=af)
    draw.text(((W - (bb[2] - bb[0])) // 2, y), au, font=af, fill=(170, 180, 170))

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
        ROOT / a.out if not a.out.is_absolute() else a.out,
    )

if __name__ == "__main__":
    main()
