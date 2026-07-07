#!/usr/bin/env python3
"""Cover: The Last Voyage of the Mermaid — Derelict white yacht glowing gold against black sea, woman in blue standing at rail, ghost white/gold/sea blue."""

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
        r = int(5 + 8 * t)
        g = int(5 + 6 * t)
        b = int(15 + 10 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    rng = random.Random(140)
    for _ in range(100):
        sx = rng.randint(0, W)
        sy = rng.randint(0, int(H * 0.3))
        sr = rng.randint(1, 2)
        sb = rng.randint(180, 255)
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(sb, sb, sb))

    sea_top = int(H * 0.55)
    for y in range(sea_top, H):
        t = (y - sea_top) / (H - sea_top)
        r = int(8 + 6 * t)
        g = int(12 + 4 * t)
        b = int(30 + 8 * t)
        draw.line((0, y, W, y), fill=(r, g, b))
    for x in range(0, W, 6):
        o = int(4 * math.sin(x * 0.03))
        draw.point((x, sea_top + o), fill=(40, 50, 70, 60))

    glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer, "RGBA")
    gd.ellipse([W // 2 - 400, int(H * 0.38) - 200, W // 2 + 400, int(H * 0.38) + 300],
                fill=(200, 180, 120, 30))
    gd.ellipse([W // 2 - 200, int(H * 0.38) - 100, W // 2 + 200, int(H * 0.38) + 150],
                fill=(220, 200, 140, 40))
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(20))
    img = Image.alpha_composite(img, glow_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    cx, cy = W // 2, int(H * 0.38)
    hull_pts = [
        (cx - 250, cy + 100), (cx - 240, cy - 40), (cx - 200, cy - 80),
        (cx - 100, cy - 110), (cx, cy - 120), (cx + 100, cy - 110),
        (cx + 200, cy - 80), (cx + 240, cy - 40), (cx + 250, cy + 100),
    ]
    draw.polygon(hull_pts, fill=(200, 195, 190, 220), outline=(160, 155, 150, 180), width=3)
    draw.polygon(hull_pts, fill=(220, 210, 180, 60))

    cabin_pts = [
        (cx - 120, cy - 120), (cx - 100, cy - 220), (cx + 100, cy - 220),
        (cx + 120, cy - 120),
    ]
    draw.polygon(cabin_pts, fill=(180, 175, 170, 200), outline=(140, 135, 130), width=2)

    for win_x in [cx - 60, cx - 20, cx + 20, cx + 60]:
        draw.rectangle([win_x - 12, cy - 200, win_x + 12, cy - 160],
                        fill=(255, 220, 150, 180))
        draw.rectangle([win_x - 12, cy - 200, win_x + 12, cy - 160],
                        outline=(200, 180, 130), width=1)

    mast_top = cy - 350
    draw.line([(cx, cy - 120), (cx, mast_top)], fill=(140, 135, 130), width=4)
    draw.line([(cx, cy - 120), (cx - 180, cy - 250)], fill=(160, 155, 150, 150), width=2)
    draw.line([(cx, cy - 120), (cx + 180, cy - 250)], fill=(160, 155, 150, 150), width=2)

    figure_x, figure_y = cx + 100, cy - 130
    draw.ellipse([figure_x - 8, figure_y - 25, figure_x + 8, figure_y - 10], fill=(20, 30, 60))
    draw.polygon([
        (figure_x - 12, figure_y - 10), (figure_x + 12, figure_y - 10),
        (figure_x + 14, figure_y + 30), (figure_x - 14, figure_y + 30),
    ], fill=(25, 35, 70))
    draw.line([(figure_x - 10, figure_y + 5), (figure_x - 25, figure_y - 10)],
               fill=(25, 35, 70), width=3)
    draw.line([(figure_x + 10, figure_y + 5), (figure_x + 25, figure_y - 10)],
               fill=(25, 35, 70), width=3)

    draw.rectangle((0, 1920, W, H), fill=(10, 8, 20, 235))
    draw.line((300, 1960, W - 300, 1960), fill=(200, 180, 120, 150), width=2)

    tf = font("arialbd.ttf", 80)
    af = font("arialbd.ttf", 36)
    title_lines = wrap(draw, ti.upper(), tf, 1300)
    y = centered(draw, 1980, title_lines, tf, (220, 215, 210), 10)
    y += 50
    bb = draw.textbbox((0, 0), au, font=af)
    draw.text(((W - (bb[2] - bb[0])) // 2, y), au, font=af, fill=(200, 190, 180))

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
