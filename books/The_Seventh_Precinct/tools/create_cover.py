#!/usr/bin/env python3
"""Cover: The Seventh Precinct — dark alley, red neon SEVENTH sign, detective silhouette in fedora, rain on wet asphalt."""

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

    # Dark alley gradient
    for y in range(H):
        t = y / H
        r = int(12 + 22 * t)
        g = int(12 + 18 * t)
        b = int(22 + 38 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # Brick walls
    for bx in range(0, 180, 35):
        for by in range(0, 1800, 18):
            draw.rectangle((bx, by, bx + 33, by + 16), fill=(55, 32, 28, 55), outline=None)
    for bx in range(W - 180, W, 35):
        for by in range(0, 1800, 18):
            draw.rectangle((bx, by, bx + 33, by + 16), fill=(55, 32, 28, 55), outline=None)

    # Wet street
    for y in range(1400, 1920):
        t = (y - 1400) / 520
        draw.line((0, y, W, y), fill=(int(8 + 28 * t), int(8 + 28 * t), int(12 + 32 * t), 255))

    # Red neon SEVENTH sign
    nsx, nsy = 350, 350
    ng = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ngd = ImageDraw.Draw(ng)
    for r in range(100, 0, -3):
        ngd.ellipse((nsx - r, nsy - r, nsx + r, nsy + r), fill=(255, 30, 30, max(0, 10 - (100 - r) // 10)))
    ng = ng.filter(ImageFilter.GaussianBlur(6))
    img = Image.alpha_composite(img, ng)
    draw = ImageDraw.Draw(img, "RGBA")

    nf = font("arialbd.ttf", 75)
    ntext = "SEVENTH"
    bb = draw.textbbox((0, 0), ntext, font=nf)
    draw.text((nsx - (bb[2] - bb[0]) // 2, nsy - (bb[3] - bb[1]) // 2), ntext, font=nf, fill=(255, 40, 40, 230))
    draw.text((nsx - (bb[2] - bb[0]) // 2 + 2, nsy - (bb[3] - bb[1]) // 2 + 2), ntext, font=nf, fill=(200, 18, 18, 100))

    # Red reflection on wet street
    for y in range(1450, 1750, 3):
        alpha = int(20 * (1 - (y - 1450) / 300))
        draw.line((nsx - 80, y, nsx + 80, y), fill=(255, 40, 40, alpha))

    # Detective silhouette with fedora
    fx, fy = 1200, 700
    draw.ellipse((fx - 100, fy + 8, fx + 100, fy + 35), fill=(4, 4, 4, 235))
    draw.polygon([(fx - 60, fy + 12), (fx - 60, fy - 55), (fx + 60, fy - 55), (fx + 60, fy + 12)], fill=(4, 4, 4, 235))
    draw.rectangle((fx - 60, fy - 8, fx + 60, fy + 4), fill=(12, 8, 8, 235))
    draw.ellipse((fx - 42, fy + 12, fx + 42, fy + 80), fill=(4, 4, 4, 225))
    draw.polygon([(fx - 70, fy + 75), (fx - 100, fy + 220), (fx + 100, fy + 220), (fx + 70, fy + 75)], fill=(4, 4, 4, 215))
    draw.polygon([(fx - 100, fy + 220), (fx - 180, fy + 380), (fx + 180, fy + 380), (fx + 100, fy + 220)], fill=(4, 4, 4, 205))

    # Rain
    for _ in range(200):
        rx = int(random.random() * W)
        ry = int(random.random() * H)
        rl = int(20 + 40 * random.random())
        draw.line((rx, ry, rx + 2, ry + rl), fill=(180, 180, 200, int(15 + 35 * random.random())), width=1)

    # Light pole
    draw.rectangle((80, 550, 86, 1500), fill=(4, 4, 4, 180))
    draw.ellipse((58, 535, 108, 570), fill=(8, 8, 8, 200))

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