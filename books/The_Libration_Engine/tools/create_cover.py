#!/usr/bin/env python3
"""Cover: The Libration Engine — Woman engineer before observation window, ring habitat curving against starfield, space black/habitat green/star white."""

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
        r = int(3 + 2 * t)
        g = int(3 + 4 * t)
        b = int(8 + 5 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    rng = random.Random(143)
    for _ in range(200):
        sx = rng.randint(0, W)
        sy = rng.randint(0, int(H * 0.7))
        sr = rng.randint(1, 3)
        sb = rng.randint(180, 255)
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(sb, sb, sb))

    for _ in range(20):
        sx = rng.randint(50, W - 50)
        sy = rng.randint(50, int(H * 0.6))
        for i in range(4):
            a = rng.randint(20, 60)
            draw.line([(sx - i * 5, sy), (sx + i * 5, sy)], fill=(sb, sb, sb, a), width=1)
            draw.line([(sx, sy - i * 5), (sx, sy + i * 5)], fill=(sb, sb, sb, a), width=1)

    ring_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring_layer, "RGBA")
    rx, ry = W // 2, int(H * 0.35)
    r_major, r_minor = 600, 150
    points = []
    for a in range(0, 360, 3):
        rad = math.radians(a)
        px = rx + r_major * math.cos(rad)
        py = ry + r_minor * math.sin(rad)
        points.append((int(px), int(py)))
    for i in range(len(points) - 1):
        rd.line([points[i], points[i + 1]], fill=(60, 120, 80, 120), width=6)
    for i in range(len(points) - 1):
        rd.line([points[i], points[i + 1]], fill=(80, 160, 100, 60), width=3)

    for a in range(0, 360, 12):
        rad = math.radians(a)
        px = int(rx + r_major * math.cos(rad))
        py = int(ry + r_minor * math.sin(rad))
        rd.line([(px - 8, py), (px + 8, py)], fill=(100, 200, 120, 100), width=2)
    ring_layer = ring_layer.filter(ImageFilter.SMOOTH)
    img = Image.alpha_composite(img, ring_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    window_x, window_y = W // 2 - 200, int(H * 0.55)
    draw.rectangle([window_x, window_y, window_x + 400, window_y + 300],
                    fill=(20, 25, 35, 200), outline=(60, 70, 90), width=4)
    draw.rectangle([window_x + 5, window_y + 5, window_x + 395, window_y + 295],
                    fill=(10, 15, 25, 180))
    for gx in range(window_x, window_x + 401, 80):
        draw.line([(gx, window_y), (gx, window_y + 300)], fill=(40, 45, 60, 100), width=2)

    figure_x, figure_y = window_x + 60, window_y + 80
    draw.ellipse([figure_x - 12, figure_y - 30, figure_x + 12, figure_y - 8],
                  fill=(40, 35, 50))
    draw.polygon([
        (figure_x - 20, figure_y - 8), (figure_x + 20, figure_y - 8),
        (figure_x + 18, figure_y + 60), (figure_x - 18, figure_y + 60),
    ], fill=(30, 40, 60))
    draw.ellipse([figure_x - 14, figure_y - 20, figure_x + 14, figure_y + 5],
                  fill=(50, 60, 80, 150))

    for _ in range(5):
        px = window_x + 280 + rng.randint(0, 100)
        py = window_y + 100 + rng.randint(0, 150)
        draw.rectangle([px, py, px + 20, py + 30], fill=(40, 80, 50, 200))

    earth_r = 40
    ex, ey = W // 2 + 300, int(H * 0.15)
    draw.ellipse([ex - earth_r, ey - earth_r, ex + earth_r, ey + earth_r],
                  fill=(30, 80, 160))
    draw.ellipse([ex - earth_r, ey - earth_r, ex + earth_r, ey + earth_r],
                  fill=(50, 120, 200, 100))
    draw.ellipse([ex - earth_r + 5, ey - earth_r // 2, ex + earth_r // 2, ey + earth_r // 2],
                  fill=(40, 100, 80, 100))
    draw.ellipse([ex - earth_r // 2, ey - earth_r // 3, ex + earth_r // 3, ey + earth_r // 3],
                  fill=(60, 140, 100, 80))

    draw.rectangle((0, 1920, W, H), fill=(5, 5, 15, 235))
    draw.line((300, 1960, W - 300, 1960), fill=(80, 160, 100, 150), width=2)

    tf = font("arialbd.ttf", 80)
    af = font("arialbd.ttf", 36)
    title_lines = wrap(draw, ti.upper(), tf, 1300)
    y = centered(draw, 1980, title_lines, tf, (200, 220, 240), 10)
    y += 50
    bb = draw.textbbox((0, 0), au, font=af)
    draw.text(((W - (bb[2] - bb[0])) // 2, y), au, font=af, fill=(160, 180, 200))

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
