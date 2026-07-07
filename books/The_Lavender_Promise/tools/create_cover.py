#!/usr/bin/env python3
"""Cover: The Lavender Promise — Honey-stone Cotswold cottage at golden hour, wild lavender on stone path, rolling hills, honey gold/lavender purple/stone cream."""

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
            r = int(255 - 20 * (t / 0.3))
            g = int(200 + 10 * (t / 0.3))
            b = int(120 + 30 * (t / 0.3))
        elif t < 0.55:
            r = int(235 + 10 * ((t - 0.3) / 0.25))
            g = int(210 - 20 * ((t - 0.3) / 0.25))
            b = int(150 - 30 * ((t - 0.3) / 0.25))
        else:
            r = int(245 - 60 * ((t - 0.55) / 0.45))
            g = int(190 - 50 * ((t - 0.55) / 0.45))
            b = int(120 - 30 * ((t - 0.55) / 0.45))
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    sun_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sun_layer)
    sd.ellipse([W // 2 - 150, int(H * 0.25) - 80, W // 2 + 150, int(H * 0.25) + 80],
                fill=(255, 220, 120, 150))
    sd.ellipse([W // 2 - 60, int(H * 0.25) - 30, W // 2 + 60, int(H * 0.25) + 30],
                fill=(255, 240, 180, 200))
    sun_layer = sun_layer.filter(ImageFilter.GaussianBlur(25))
    img = Image.alpha_composite(img, sun_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    for hx, hy, hr in [(200, int(H * 0.7), 500), (600, int(H * 0.72), 450),
                        (1000, int(H * 0.68), 500), (1400, int(H * 0.71), 400)]:
        draw.ellipse([hx - hr, hy - hr // 3, hx + hr, hy + hr // 3],
                      fill=(100, 160, 80, 80))

    cottage_cx = W // 2
    cottage_y = int(H * 0.48)
    wall_color = (220, 200, 170)
    roof_color = (160, 120, 80)

    draw.rectangle([cottage_cx - 140, cottage_y - 80, cottage_cx + 140, cottage_y + 50],
                    fill=wall_color)
    draw.polygon([
        (cottage_cx - 160, cottage_y - 80), (cottage_cx, cottage_y - 160),
        (cottage_cx + 160, cottage_y - 80),
    ], fill=roof_color)

    draw.polygon([
        (cottage_cx - 60, cottage_y - 80), (cottage_cx - 60, cottage_y - 130),
        (cottage_cx + 60, cottage_y - 130), (cottage_cx + 60, cottage_y - 80),
    ], fill=(180, 140, 100))

    for wx in [cottage_cx - 100, cottage_cx - 30, cottage_cx + 40]:
        draw.rectangle([wx, cottage_y - 50, wx + 25, cottage_y - 10],
                        fill=(255, 220, 140, 180))
        draw.rectangle([wx, cottage_y - 50, wx + 25, cottage_y - 10],
                        outline=(150, 130, 100), width=2)

    draw.rectangle([cottage_cx - 18, cottage_y - 30, cottage_cx + 18, cottage_y + 50],
                    fill=(120, 80, 50))
    draw.ellipse([cottage_cx - 5, cottage_y - 5, cottage_cx + 5, cottage_y + 5],
                  fill=(200, 170, 100))

    stone_path = []
    for i in range(20):
        px = cottage_cx - 18 + i * 12 + int(8 * math.sin(i * 0.5))
        py = cottage_y + 55 + i * 18
        stone_path.append((px, py))
        draw.ellipse([px - 12, py - 5, px + 12, py + 5],
                      fill=(180, 170, 155, 200), outline=(160, 150, 135), width=1)

    for row in range(8):
        ry = cottage_y + 80 + row * 35
        for col in range(20):
            rx = 100 + col * 75 + int(20 * math.sin(row * 1.2 + col * 0.7))
            r = ry + int(10 * math.sin(col * 0.3 + row))
            draw.ellipse([rx - 15, r - 10, rx + 15, r + 10],
                          fill=(100, 80, 160, 180))
            draw.ellipse([rx - 6, r - 14, rx + 6, r - 6],
                          fill=(140, 110, 200, 200))

    rng = random.Random(141)
    for _ in range(40):
        fx = rng.randint(50, W - 50)
        fy = rng.randint(int(H * 0.3), int(H * 0.55))
        fs = rng.randint(1, 3)
        draw.ellipse([fx - fs, fy - fs, fx + fs, fy + fs],
                      fill=(255, 220, 120, rng.randint(100, 200)))

    draw.rectangle((0, 1920, W, H), fill=(25, 20, 30, 235))
    draw.line((250, 1960, W - 250, 1960), fill=(220, 180, 120, 200), width=3)

    tf = font("arialbd.ttf", 85)
    af = font("arialbd.ttf", 36)
    title_lines = wrap(draw, ti.upper(), tf, 1300)
    y = centered(draw, 1980, title_lines, tf, (255, 245, 235), 10)
    y += 50
    bb = draw.textbbox((0, 0), au, font=af)
    draw.text(((W - (bb[2] - bb[0])) // 2, y), au, font=af, fill=(210, 190, 170))

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
