#!/usr/bin/env python3
"""Cover: The Last Taxi — Yellow taxi on cobblestone street under crescent moon, walnut tree branches over street, taxi yellow/midnight blue/cobblestone gray."""

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

def draw_night_sky(draw):
    for y in range(H):
        t = y / H
        if t < 0.3:
            r = int(15 - 5 * (t / 0.3))
            g = int(10 - 3 * (t / 0.3))
            b = int(40 - 5 * (t / 0.3))
        elif t < 0.6:
            r = int(10 + 10 * ((t - 0.3) / 0.3))
            g = int(7 + 15 * ((t - 0.3) / 0.3))
            b = int(35 + 10 * ((t - 0.3) / 0.3))
        else:
            r = int(20 + 15 * ((t - 0.6) / 0.4))
            g = int(22 + 18 * ((t - 0.6) / 0.4))
            b = int(45 + 15 * ((t - 0.6) / 0.4))
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

def draw_stars(draw):
    rng = random.Random(137)
    for _ in range(120):
        x = rng.randint(0, W)
        y = rng.randint(0, int(H * 0.35))
        s = rng.randint(1, 3)
        b = rng.randint(160, 255)
        draw.ellipse([x - s, y - s, x + s, y + s], fill=(b, b, b, b))

def draw_crescent_moon(draw):
    mx, my = 1200, 120
    r = 40
    draw.ellipse([mx - r, my - r, mx + r, my + r], fill=(240, 235, 220, 220))
    draw.ellipse([mx + 15, my - r - 5, mx + r + 15, my + r + 5], fill=(15, 12, 40))

def draw_cobblestone_street(draw):
    street_top = int(H * 0.62)
    street_bot = int(H * 0.78)
    for y in range(street_top, street_bot):
        t = (y - street_top) / (street_bot - street_top)
        c = (
            int(80 + 30 * t),
            int(75 + 28 * t),
            int(70 + 25 * t),
        )
        draw.line((0, y, W, y), fill=c)
    rng = random.Random(42)
    for _ in range(80):
        cx = rng.randint(50, W - 50)
        cy = rng.randint(street_top + 10, street_bot - 10)
        cs = rng.randint(15, 35)
        draw.ellipse([cx - cs // 2, cy - cs // 4, cx + cs // 2, cy + cs // 4],
                      fill=(100, 95, 88, 80), outline=(90, 85, 78, 100), width=1)

def draw_taxi(draw):
    cx, cy = W // 2 - 30, int(H * 0.62)
    tw, th = 280, 130
    taxi_color = (240, 200, 30)
    dark_color = (40, 35, 30)
    glass_color = (120, 150, 190, 200)

    # Shadow
    draw.ellipse([cx - tw // 2 - 10, cy + th - 10, cx + tw // 2 + 10, cy + th + 15],
                  fill=(20, 18, 25, 100))

    # Main body
    draw.rounded_rectangle([cx - tw // 2, cy + 30, cx + tw // 2, cy + th],
                           radius=20, fill=taxi_color, outline=dark_color, width=3)

    # Hood
    draw.rounded_rectangle([cx - tw // 2, cy + 30, cx + tw // 2, cy + 55],
                           radius=8, fill=(220, 185, 25))

    # Cabin
    draw.rounded_rectangle([cx - tw // 4, cy - 30, cx + tw // 4, cy + 35],
                           radius=10, fill=taxi_color, outline=dark_color, width=3)

    # Windows
    draw.rounded_rectangle([cx - tw // 4 + 8, cy - 20, cx - 15, cy + 25],
                           radius=6, fill=glass_color)
    draw.rounded_rectangle([cx + 15, cy - 20, cx + tw // 4 - 8, cy + 25],
                           radius=6, fill=glass_color)

    # Roof light
    draw.rectangle([cx - 20, cy - 50, cx + 20, cy - 38], fill=(40, 35, 30))
    draw.rectangle([cx - 12, cy - 48, cx + 12, cy - 40], fill=(255, 220, 80, 200))

    # Headlights
    draw.ellipse([cx - tw // 2, cy + 55, cx - tw // 2 + 20, cy + 80],
                  fill=(255, 250, 220, 200))
    draw.ellipse([cx + tw // 2 - 20, cy + 55, cx + tw // 2, cy + 80],
                  fill=(255, 250, 220, 200))

    # Headlight beams
    for angle in range(-20, 25, 5):
        rad = math.radians(angle - 90)
        ex = cx - tw // 2 + 10
        ey = cy + 68
        draw.line([(ex, ey), (ex + int(300 * math.cos(rad)), ey + int(300 * math.sin(rad)))],
                   fill=(255, 250, 220, 15), width=8)

    # Wheels
    for wx in [cx - tw // 4, cx + tw // 4]:
        draw.ellipse([wx - 22, cy + th - 10, wx + 22, cy + th + 30],
                      fill=(30, 28, 25))
        draw.ellipse([wx - 14, cy + th - 2, wx + 14, cy + th + 22],
                      fill=(50, 48, 45))
        draw.ellipse([wx - 5, cy + th + 4, wx + 5, cy + th + 16],
                      fill=(40, 38, 35))

    # Grille
    for gx in range(cx - 12, cx + 15, 6):
        draw.line([(gx, cy + 55), (gx, cy + 75)], fill=(60, 55, 50), width=2)

def draw_buildings(draw):
    rng = random.Random(73)
    for i in range(8):
        bx = 100 + i * 200
        bh = rng.randint(200, 500)
        bw = rng.randint(120, 180)
        by = int(H * 0.62) - bh
        draw.rectangle([bx, by, bx + bw, int(H * 0.62)], fill=(35, 32, 40))
        for wy in range(by + 30, int(H * 0.62) - 20, 50):
            for wx in range(bx + 15, bx + bw - 15, 30):
                if rng.random() < 0.4:
                    draw.rectangle([wx, wy, wx + 16, wy + 22], fill=(220, 200, 140, 80))

def draw_walnut_branches(draw):
    for side in [-1, 1]:
        bx = W // 2 + side * 200
        for _ in range(5):
            x = bx + random.randint(-80, 80)
            y = random.randint(0, 200)
            for seg in range(6):
                nx = x + side * random.randint(30, 80)
                ny = y + seg * random.randint(40, 80)
                draw.line([(x, y), (nx, ny)], fill=(25, 20, 15, 180), width=random.randint(3, 8))
                x, y = nx, ny
            for _ in range(3):
                lx = x + side * random.randint(10, 30)
                ly = y + random.randint(-15, 15)
                draw.line([(x, y), (lx, ly)], fill=(25, 20, 15, 120), width=2)

def draw_light_pool(draw):
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow, "RGBA")
    gd.ellipse([W // 2 - 250, int(H * 0.62) - 30, W // 2 + 250, int(H * 0.78) + 30],
                fill=(255, 220, 80, 30))
    glow = glow.filter(ImageFilter.GaussianBlur(30))
    draw.bitmap((0, 0), glow, fill=None)

def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    ti = m["title"]
    au = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    draw_night_sky(draw)
    draw_stars(draw)
    draw_crescent_moon(draw)
    draw_buildings(draw)
    draw_cobblestone_street(draw)
    draw_taxi(draw)
    draw_light_pool(draw)
    draw_walnut_branches(draw)

    draw.rectangle((0, 1920, W, H), fill=(15, 12, 25, 235))
    draw.line((200, 1960, W - 200, 1960), fill=(240, 200, 30, 200), width=3)

    tf = font("arialbd.ttf", 90)
    af = font("arialbd.ttf", 36)
    sf = font("arial.ttf", 28)

    title_lines = wrap(draw, ti.upper(), tf, 1300)
    y = centered(draw, 1980, title_lines, tf, (255, 255, 255), 10)

    y += 50
    bb = draw.textbbox((0, 0), au, font=af)
    draw.text(((W - (bb[2] - bb[0])) // 2, y), au, font=af, fill=(220, 200, 180))

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
