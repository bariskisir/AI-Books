#!/usr/bin/env python3
"""Cover: The Long Exposure — Observatory dome against deep navy sky, single blue star flare, cream/beige tones, navy blue/star blue/cream."""

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
        if t < 0.5:
            r = int(10 - 5 * (t / 0.5))
            g = int(15 - 10 * (t / 0.5))
            b = int(50 - 20 * (t / 0.5))
        else:
            r = int(5 + 40 * ((t - 0.5) / 0.5))
            g = int(5 + 50 * ((t - 0.5) / 0.5))
            b = int(30 + 40 * ((t - 0.5) / 0.5))
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    rng = random.Random(148)
    for _ in range(150):
        sx = rng.randint(0, W)
        sy = rng.randint(0, int(H * 0.5))
        sr = rng.randint(1, 2)
        sb = rng.randint(180, 255)
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(sb, sb, sb))

    flare_cx, flare_cy = W // 2, int(H * 0.25)
    flare_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(flare_layer, "RGBA")
    for r in range(300, 0, -10):
        a = int(15 * (1 - r / 300))
        fd.ellipse([flare_cx - r, flare_cy - r, flare_cx + r, flare_cy + r],
                    fill=(100, 180, 255, max(0, a)))
    for r in range(100, 0, -5):
        a = int(40 * (1 - r / 100))
        fd.ellipse([flare_cx - r, flare_cy - r, flare_cx + r, flare_cy + r],
                    fill=(150, 220, 255, max(0, a)))
    fd.ellipse([flare_cx - 8, flare_cy - 8, flare_cx + 8, flare_cy + 8],
                fill=(255, 255, 255, 230))
    flare_layer = flare_layer.filter(ImageFilter.GaussianBlur(10))
    img = Image.alpha_composite(img, flare_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        for i in range(8):
            x1 = flare_cx + int(30 * i * math.cos(rad))
            y1 = flare_cy + int(30 * i * math.sin(rad))
            x2 = flare_cx + int((30 * i + 20) * math.cos(rad))
            y2 = flare_cy + int((30 * i + 20) * math.sin(rad))
            draw.line([(x1, y1), (x2, y2)], fill=(200, 230, 255, max(0, 80 - i * 10)), width=2)

    dome_cx, dome_cy = W // 2, int(H * 0.62)
    dome_color = (210, 205, 195)
    draw.arc([dome_cx - 200, dome_cy - 200, dome_cx + 200, dome_cy + 200],
             0, 180, fill=dome_color, width=4)
    draw.ellipse([dome_cx - 200, dome_cy - 200, dome_cx + 200, dome_cy + 20],
                  fill=dome_color)
    draw.ellipse([dome_cx - 200, dome_cy - 200, dome_cx + 200, dome_cy + 20],
                  outline=(180, 175, 165), width=2)

    draw.rectangle([dome_cx - 210, dome_cy + 10, dome_cx + 210, dome_cy + 30],
                    fill=(190, 185, 175))
    draw.rectangle([dome_cx - 190, dome_cy + 30, dome_cx + 190, dome_cy + 300],
                    fill=(200, 195, 185))
    for wx in [dome_cx - 160, dome_cx - 80, dome_cx, dome_cx + 80, dome_cx + 160]:
        draw.rectangle([wx - 15, dome_cy + 50, wx + 15, dome_cy + 90],
                        fill=(60, 65, 75, 180))

    slit_x1, slit_x2 = dome_cx - 12, dome_cx + 12
    slit_y = dome_cy - 180
    draw.rectangle([slit_x1, slit_y, slit_x2, dome_cy - 10],
                    fill=(20, 25, 35))

    draw.rectangle([dome_cx - 20, dome_cy + 240, dome_cx + 20, dome_cy + 300],
                    fill=(80, 75, 70))
    draw.rectangle([dome_cx - 25, dome_cy + 260, dome_cx + 25, dome_cy + 265],
                    fill=(50, 48, 45))

    hills = [
        (100, int(H * 0.7), 300),
        (400, int(H * 0.72), 350),
        (800, int(H * 0.68), 400),
        (1200, int(H * 0.71), 350),
        (1500, int(H * 0.73), 300),
    ]
    for hx, hy, hr in hills:
        draw.ellipse([hx - hr, hy - hr // 2, hx + hr, hy + hr // 2],
                      fill=(60, 65, 70, 120))

    draw.rectangle((0, 1920, W, H), fill=(15, 15, 25, 235))
    draw.line((300, 1960, W - 300, 1960), fill=(100, 180, 255, 150), width=2)

    tf = font("arialbd.ttf", 80)
    af = font("arialbd.ttf", 36)
    title_lines = wrap(draw, ti.upper(), tf, 1300)
    y = centered(draw, 1980, title_lines, tf, (220, 220, 230), 10)
    y += 50
    bb = draw.textbbox((0, 0), au, font=af)
    draw.text(((W - (bb[2] - bb[0])) // 2, y), au, font=af, fill=(190, 190, 200))

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
