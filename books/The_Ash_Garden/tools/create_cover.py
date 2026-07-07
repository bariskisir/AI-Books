#!/usr/bin/env python3
"""Cover: The Ash Garden — literary fiction, post-internment California."""

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

    # Sepia gradient background
    for y in range(H):
        t = y / H
        r = int(160 - 80 * t)
        g = int(130 - 60 * t)
        b = int(80 - 40 * t)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Sky glow
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((W // 2 - 300, 100, W // 2 + 300, 500), fill=(220, 190, 140, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Distant barbed wire fence line
    wire_y = 1100
    draw.line((0, wire_y, W, wire_y), fill=(40, 30, 20, 200), width=3)
    for wx in range(0, W, 80):
        # Post
        draw.line((wx, wire_y - 60, wx, wire_y + 20), fill=(50, 40, 30, 220), width=6)
        # Barb wire diagonals
        draw.line((wx - 10, wire_y - 10, wx + 10, wire_y + 10), fill=(60, 50, 40, 200), width=2)
        draw.line((wx - 10, wire_y + 5, wx + 10, wire_y - 5), fill=(60, 50, 40, 200), width=2)

    # Empty garden beds in foreground
    for bx in [200, 500, 800, 1100, 1400]:
        draw.rectangle((bx, 1450, bx + 120, 1580), fill=(100, 80, 55, 180))
        draw.rectangle((bx + 5, 1455, bx + 115, 1575), fill=(80, 60, 40, 200))
        # Dead plant stalks
        for _ in range(4):
            sx = bx + 15 + int(25 * __import__("random").random())
            sy = 1460 + int(100 * __import__("random").random())
            draw.line((sx, sy, sx, sy - 40), fill=(60, 50, 35, 180), width=2)
            draw.line((sx, sy - 40, sx - 8, sy - 50), fill=(60, 50, 35, 180), width=2)
            draw.line((sx, sy - 40, sx + 8, sy - 50), fill=(60, 50, 35, 180), width=2)

    # Lone figure silhouette
    fx, fy = W // 2, 1180
    # Body
    draw.ellipse((fx - 15, fy - 60, fx + 15, fy), fill=(30, 25, 20, 220))
    # Head
    draw.ellipse((fx - 12, fy - 85, fx + 12, fy - 60), fill=(30, 25, 20, 220))
    # Skirt
    draw.polygon(
        [(fx - 16, fy), (fx - 35, fy + 50), (fx + 35, fy + 50), (fx + 16, fy)],
        fill=(30, 25, 20, 220),
    )

    # Bare tree silhouette (left side)
    tx, ty = 250, 900
    draw.line((tx, ty, tx, ty + 400), fill=(40, 30, 20, 200), width=12)
    for angle in range(-60, 80, 30):
        rad = math.radians(angle)
        bx = tx + 100 * math.cos(rad)
        by = ty + 100 * math.sin(rad)
        draw.line((tx, ty + 20, bx, by), fill=(40, 30, 20, 200), width=6)
        if angle % 60 == 0:
            rad2 = math.radians(angle + 20)
            cx = bx + 50 * math.cos(rad2)
            cy = by + 50 * math.sin(rad2)
            draw.line((bx, by, cx, cy), fill=(40, 30, 20, 200), width=3)

    # Faint dust particles in the air
    for _ in range(40):
        px = int(W * __import__("random").random())
        py = int(600 + 600 * __import__("random").random())
        pr = int(2 + 4 * __import__("random").random())
        draw.ellipse(
            (px - pr, py - pr, px + pr, py + pr),
            fill=(200, 180, 140, int(20 + 30 * __import__("random").random())),
        )

    # Title panel at bottom
    draw.line((300, 2500, W - 300, 2500), fill=(200, 170, 120, 120), width=1)

    tf = font("georgiab.ttf", 100)
    af = font("arialbd.ttf", 40)
    sf = font("arial.ttf", 28)

    y = 2000
    y = centered(draw, y, wrap(draw, title.upper(), tf, 1100), tf, (210, 180, 130), 8)
    y += 60
    centered(draw, y, [author], af, (190, 170, 150), 6)

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