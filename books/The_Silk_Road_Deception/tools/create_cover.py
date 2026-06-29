#!/usr/bin/env python3
"""Cover: The Silk Road Deception — desert caravan, ancient ruins, amber and sand."""

from __future__ import annotations
import argparse, json
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

    # Amber-to-sand-to-terracotta gradient
    for y in range(H):
        t = y / H
        if t < 0.4:
            r, g, b = 210, 170, 100
        elif t < 0.7:
            r, g, b = 195, 140, 80
        else:
            r, g, b = 170, 100, 60
        fade = 1.0 - (max(0, y - 1920) / 640) * 0.4
        draw.line(
            (0, y, W, y),
            fill=(int(r * fade), int(g * fade), int(b * fade), 255),
        )

    # Sun disc (hazy desert sun)
    sun = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sun)
    sd.ellipse((W // 2 - 180, 400, W // 2 + 180, 760), fill=(240, 210, 140, 180))
    sun = sun.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img, sun)
    draw = ImageDraw.Draw(img, "RGBA")

    # Distant ruins on the horizon (arches and pillars)
    # Arch 1
    rx, ry = 300, 1300
    draw.arc((rx, ry, rx + 160, ry + 280), 180, 0, fill=(140, 100, 60, 200), width=14)
    draw.rectangle((rx - 10, ry + 240, rx + 10, ry + 360), fill=(140, 100, 60, 200))
    draw.rectangle((rx + 150, ry + 240, rx + 170, ry + 360), fill=(140, 100, 60, 200))
    # Arch 2 (larger, center)
    rx2, ry2 = 680, 1180
    draw.arc((rx2, ry2, rx2 + 240, ry2 + 380), 180, 0, fill=(160, 115, 70, 200), width=16)
    draw.rectangle((rx2 - 10, ry2 + 320, rx2 + 10, ry2 + 460), fill=(160, 115, 70, 200))
    draw.rectangle((rx2 + 230, ry2 + 320, rx2 + 250, ry2 + 460), fill=(160, 115, 70, 200))
    # Broken pillar
    px, py = 1200, 1250
    draw.rectangle((px, py, px + 30, py + 350), fill=(150, 105, 60, 200))
    draw.rectangle((px - 15, py + 300, px + 45, py + 320), fill=(150, 105, 60, 200))
    # Partial column
    px2, py2 = 1050, 1350
    draw.rectangle((px2, py2, px2 + 20, py2 + 200), fill=(130, 90, 50, 180))

    # Desert caravan silhouette (camels and riders)
    camel_color = (60, 40, 25, 220)
    # Camel 1
    cx, cy = 400, 1550
    draw.ellipse((cx, cy, cx + 40, cy + 25), fill=camel_color)
    draw.ellipse((cx + 50, cy - 40, cx + 90, cy - 5), fill=camel_color)
    draw.arc((cx - 30, cy - 55, cx + 10, cy - 10), 240, 120, fill=camel_color, width=5)
    draw.line((cx + 20, cy - 5, cx + 60, cy + 25), fill=camel_color, width=4)  # legs
    draw.line((cx + 40, cy, cx + 80, cy + 25), fill=camel_color, width=4)
    # Rider on camel 1
    draw.ellipse((cx + 50, cy - 80, cx + 70, cy - 55), fill=(40, 30, 20, 230))
    draw.line((cx + 60, cy - 55, cx + 55, cy - 20), fill=(40, 30, 20, 230), width=4)

    # Camel 2
    cx2, cy2 = 550, 1530
    draw.ellipse((cx2, cy2, cx2 + 35, cy2 + 22), fill=camel_color)
    draw.ellipse((cx2 + 45, cy2 - 35, cx2 + 80, cy2 - 3), fill=camel_color)
    draw.arc((cx2 - 25, cy2 - 48, cx2 + 8, cy2 - 8), 240, 120, fill=camel_color, width=5)
    draw.line((cx2 + 15, cy2 - 3, cx2 + 50, cy2 + 22), fill=camel_color, width=4)
    draw.line((cx2 + 35, cy2 - 2, cx2 + 70, cy2 + 22), fill=camel_color, width=4)

    # Camel 3 (further, smaller)
    cx3, cy3 = 750, 1540
    draw.ellipse((cx3, cy3, cx3 + 30, cy3 + 18), fill=camel_color)
    draw.ellipse((cx3 + 38, cy3 - 30, cx3 + 68, cy3 - 2), fill=camel_color)
    draw.line((cx3 + 15, cy3, cx3 + 42, cy3 + 18), fill=camel_color, width=3)
    draw.line((cx3 + 30, cy3, cx3 + 58, cy3 + 18), fill=camel_color, width=3)

    # Sand dunes in foreground
    for i, (dx, dy, dw, dh) in enumerate(
        [
            (0, 1750, 800, 120),
            (500, 1780, 600, 100),
            (200, 1800, 500, 90),
            (1000, 1760, 700, 110),
            (1300, 1790, 400, 85),
        ]
    ):
        shade = 100 + i * 15
        draw.pieslice(
            (dx, dy, dx + dw, dy + dh * 2),
            180,
            0,
            fill=(shade, shade - 20, shade - 40, 200),
        )

    # Parchment map effect in lower sky area (a faint scroll-like shape)
    map_color = (200, 180, 140, 60)
    draw.rectangle((200, 900, 1400, 1120), fill=map_color)
    draw.rectangle((180, 900, 200, 1120), fill=(190, 170, 130, 70))
    draw.rectangle((1400, 900, 1420, 1120), fill=(190, 170, 130, 70))
    # Faint route line on map
    draw.line((300, 960, 600, 1000, 900, 950, 1200, 1020), fill=(160, 120, 70, 80), width=3)
    # Tiny marker dots on the map route
    for mx, my in [(300, 960), (600, 1000), (900, 950), (1200, 1020)]:
        draw.ellipse((mx - 4, my - 4, mx + 4, my + 4), fill=(180, 80, 40, 100))

    # Dust particles scattered
    import random as _rng

    for _ in range(80):
        x = int(W * _rng.random())
        y = int(800 + 1200 * _rng.random())
        r = int(2 + 5 * _rng.random())
        a = int(20 + 40 * _rng.random())
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(220, 200, 160, a))

    # Title panel — light rectangle at bottom
    # Decorative lines
    draw.line((200, H - 160, W - 200, H - 160), fill=(180, 140, 90, 140), width=2)

    # Title text
    tf = font("georgiab.ttf", 100)
    af = font("arialbd.ttf", 40)
    sf = font("arial.ttf", 28)

    # Genre line
    y = centered(draw, 2000, ["A HISTORICAL THRILLER"], sf, (160, 120, 70), 4)
    y += 30

    # Title (wrapped if needed)
    title_lines = wrap(draw, title.upper(), tf, 1200)
    y = centered(draw, y, title_lines, tf, (40, 35, 30), 10)
    y += 40

    # Author
    centered(draw, y, [author], af, (100, 75, 50), 6)

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