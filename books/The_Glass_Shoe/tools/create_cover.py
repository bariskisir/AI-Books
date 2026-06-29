#!/usr/bin/env python3
"""Cover: The Glass Shoe — a noir Cinderella with glass slipper and city shadows."""

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

    # Noir gradient: deep navy/charcoal at top to dark indigo at bottom
    for y in range(H):
        t = y / H
        r = int(25 + 10 * t)
        g = int(20 + 15 * t)
        b = int(55 + 30 * t)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Glittering ballroom glow — soft golden light radiating from center
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((W // 2 - 500, 200, W // 2 + 500, 1000), fill=(220, 180, 100, 40))
    gd.ellipse((W // 2 - 300, 300, W // 2 + 300, 900), fill=(240, 200, 120, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    img = Image.alpha_composite(img, glow)

    # City skyline silhouette in lower mid
    draw = ImageDraw.Draw(img, "RGBA")
    skyline_y = 1400
    buildings = [
        (100, skyline_y, 450, 1600),
        (130, skyline_y, 200, 1520),
        (380, skyline_y, 520, 1550),
        (500, skyline_y, 650, 1580),
        (650, skyline_y, 780, 1530),
        (800, skyline_y, 950, 1570),
        (950, skyline_y, 1100, 1540),
        (1050, skyline_y, 1250, 1590),
        (1200, skyline_y, 1350, 1520),
        (1300, skyline_y, 1500, 1560),
    ]
    for x1, y1, x2, y2 in buildings:
        draw.rectangle((x1, y1, x2, y2), fill=(15, 12, 18, 200))

    # Occasional lit windows
    for _ in range(30):
        bx = random.choice(buildings)
        wx = random.randint(bx[0] + 5, bx[2] - 5)
        wy = random.randint(bx[1] + 10, bx[3] - 10)
        draw.rectangle((wx, wy, wx + 8, wy + 12), fill=(240, 210, 120, 100 + int(50 * random.random())))

    # Glass slipper — elegant, translucent, angled
    slipper_x, slipper_y = W // 2 - 30, 940
    # Slipper body (pointed toe)
    draw.polygon(
        [
            (slipper_x - 120, slipper_y + 100),
            (slipper_x - 140, slipper_y + 40),
            (slipper_x - 100, slipper_y),
            (slipper_x, slipper_y - 20),
            (slipper_x + 80, slipper_y),
            (slipper_x + 100, slipper_y + 40),
            (slipper_x + 80, slipper_y + 100),
        ],
        fill=(200, 210, 230, 100),
        outline=(180, 190, 220, 180),
        width=3,
    )
    # Heel
    draw.line(
        (slipper_x + 60, slipper_y + 100, slipper_x + 40, slipper_y + 220),
        fill=(180, 190, 220, 180),
        width=8,
    )
    # Sole
    draw.arc(
        (slipper_x - 140, slipper_y + 80, slipper_x + 100, slipper_y + 120),
        0,
        180,
        fill=(180, 190, 220, 120),
        width=3,
    )
    # Sparkle highlights
    for _ in range(25):
        sx = slipper_x + random.randint(-130, 100)
        sy = slipper_y + random.randint(-20, 100)
        sr = random.randint(1, 4)
        draw.ellipse(
            (sx - sr, sy - sr, sx + sr, sy + sr),
            fill=(255, 255, 255, random.randint(80, 220)),
        )

    # Silver shoe shimmer lines
    for _ in range(8):
        lx = slipper_x + random.randint(-120, 90)
        ly = slipper_y + random.randint(0, 90)
        draw.line(
            (lx, ly, lx + random.randint(-20, 20), ly + random.randint(10, 30)),
            fill=(200, 210, 240, random.randint(30, 100)),
            width=1,
        )

    # Falling glass sparkles
    for _ in range(40):
        fx = random.randint(100, W - 100)
        fy = random.randint(100, H - 400)
        fs = random.randint(1, 3)
        draw.ellipse(
            (fx - fs, fy - fs, fx + fs, fy + fs),
            fill=(255, 255, 255, random.randint(40, 160)),
        )

    # Title panel at bottom
    draw.line((250, H - 120, W - 250, H - 120), fill=(80, 70, 90, 100), width=1)

    # Genre tag line
    tf_small = font("arial.ttf", 28)
    centered(draw, 1960, ["A FAIRY TALE RETELLING"], tf_small, (100, 95, 110), 4)

    # Title
    tf = font("georgiab.ttf", 100)
    title_lines = wrap(draw, title.upper(), tf, 1300)
    y_title = centered(draw, 2020, title_lines, tf, (30, 25, 35), 8)
    y_title += 20

    # Divider
    draw.line((550, y_title, W - 550, y_title), fill=(80, 70, 90, 120), width=1)
    y_title += 30

    # Author
    af = font("arialbd.ttf", 40)
    centered(draw, y_title, [author], af, (60, 55, 70), 6)

    # Small decorative line near bottom
    draw.line((500, H - 70, W - 500, H - 70), fill=(80, 70, 90, 60), width=1)

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