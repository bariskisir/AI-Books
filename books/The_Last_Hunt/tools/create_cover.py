#!/usr/bin/env python3
"""Cover: The Last Hunt — Western Literary. Texas plains, lone rider, mountain silhouette."""

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
    for c in [FONT_DIR / name, FONT_DIR / "arialbd.ttf", FONT_DIR / "arial.ttf"]:
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

    # Sky gradient — deep turquoise to dusty orange
    for y in range(H):
        t = y / H
        # Top: turquoise/desert sky (#1A4A5A to #C4844A)
        r = int(26 + (196 - 26) * t)
        g = int(74 + (132 - 74) * t)
        b = int(90 + (74 - 90) * t)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Sun disc — low and hazy
    sun = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sun)
    sd.ellipse((W // 2 - 180, 700, W // 2 + 180, 1060), fill=(235, 200, 120, 180))
    sun = sun.filter(ImageFilter.GaussianBlur(25))
    img = Image.alpha_composite(img, sun)
    draw = ImageDraw.Draw(img, "RGBA")

    # Distant mountain silhouette
    mt_pts = [
        (0, 1550), (100, 1380), (200, 1420), (350, 1250), (500, 1300),
        (650, 1180), (800, 1220), (950, 1150), (1100, 1190),
        (1250, 1080), (1400, 1120), (1550, 1050), (1600, 1100), (1600, 1550)
    ]
    draw.polygon(mt_pts, fill=(25, 20, 18, 230))

    # Secondary ridge
    rd_pts = [(0, 1480), (200, 1430), (400, 1450), (600, 1390), (800, 1410),
              (1000, 1360), (1200, 1380), (1400, 1320), (1600, 1350), (1600, 1550)]
    draw.polygon(rd_pts, fill=(18, 15, 13, 200))

    # Texas plains — flat ground
    draw.rectangle((0, 1450, W, 1960), fill=(55, 48, 38, 200))
    draw.rectangle((0, 1500, W, 1960), fill=(45, 38, 30, 200))

    # Lone rider on horseback — silhouette
    rx, ry = W // 2 - 150, 1480
    # Horse body
    draw.ellipse((rx - 40, ry - 30, rx + 40, ry + 20), fill=(8, 6, 5, 255))
    # Horse neck
    draw.polygon([(rx - 10, ry - 30), (rx + 10, ry - 30), (rx + 5, ry - 80), (rx - 5, ry - 80)], fill=(8, 6, 5, 255))
    # Horse head
    draw.ellipse((rx - 8, ry - 90, rx + 8, ry - 70), fill=(8, 6, 5, 255))
    # Horse legs
    for lx in [rx - 25, rx - 10, rx + 10, rx + 25]:
        draw.rectangle((lx - 3, ry + 15, lx + 3, ry + 50), fill=(8, 6, 5, 255))
    # Rider body
    draw.polygon([(rx - 15, ry - 40), (rx + 15, ry - 40), (rx + 8, ry - 120), (rx - 8, ry - 120)], fill=(8, 6, 5, 255))
    # Rider head
    draw.ellipse((rx - 10, ry - 135, rx + 10, ry - 115), fill=(8, 6, 5, 255))
    # Rider hat
    draw.rectangle((rx - 16, ry - 142, rx + 16, ry - 132), fill=(8, 6, 5, 255))
    draw.rectangle((rx - 8, ry - 148, rx + 8, ry - 140), fill=(8, 6, 5, 255))

    # Dust particles across the plains
    import random
    random.seed(42)
    for _ in range(80):
        x = int(random.random() * W)
        y = int(1300 + 600 * random.random())
        r = int(2 + 5 * random.random())
        a = int(20 + 40 * random.random())
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(180, 140, 90, a))

    # Heat shimmer / dust haze — subtle horizontal lines
    for _ in range(40):
        y = int(1400 + 400 * random.random())
        x1 = int(random.random() * W)
        x2 = min(W, x1 + int(100 + 200 * random.random()))
        a = int(5 + 15 * random.random())
        draw.line((x1, y, x2, y), fill=(200, 170, 130, a), width=1)

    # Title panel at bottom
    # Decorative lines
    draw.line((260, H - 160, W - 260, H - 160), fill=(180, 140, 80, 140), width=2)

    # Title text — use arialbd.ttf, WHITE text
    ttf = font("arialbd.ttf", 120)
    y = centered(draw, 2000, wrap(draw, title.upper(), ttf, 1100), ttf, (255, 255, 255), 8)
    y += 50

    # Author
    af = font("arialbd.ttf", 44)
    centered(draw, y, [author], af, (220, 200, 180), 6)

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