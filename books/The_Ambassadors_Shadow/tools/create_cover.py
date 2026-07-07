#!/usr/bin/env python3
"""Cover: The Ambassador's Shadow — UN building, globe, dark blue and gold."""

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

    # Dark blue to navy gradient background
    for y in range(H):
        t = y / H
        r = int(15 + 10 * t)
        g = int(20 + 15 * t)
        b = int(50 + 30 * t)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Globe silhouette — faint glowing circle
    globe = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(globe)
    cx, cy, cr = W // 2, 600, 380
    gd.ellipse((cx - cr, cy - cr, cx + cr, cy + cr), fill=(40, 60, 120, 80))
    # Latitude/longitude lines on globe
    for angle in [0, 45, 90, 135]:
        rad = math.radians(angle)
        gd.ellipse(
            (cx - cr, cy - cr, cx + cr, cy + cr),
            outline=(100, 140, 200, 60),
            width=1,
        )
    gd.ellipse((cx - cr, cy - cr, cx + cr, cy + cr), outline=(150, 180, 220, 100), width=2)
    # Meridian arcs
    for i in range(-2, 3):
        lx = cx + i * cr // 3
        gd.arc(
            (lx - cr // 4, cy - cr, lx + cr // 4, cy + cr),
            -90,
            90,
            fill=(100, 140, 200, 50),
            width=1,
        )
    globe = globe.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img, globe)

    # UN building silhouette — simplified geometric facade
    un_building = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ud = ImageDraw.Draw(un_building)
    bx, bw, bh = cx - 300, 600, 600
    by = cy + 50
    # Main building block
    ud.rectangle((bx, by, bx + bw, by + bh), fill=(20, 30, 60, 200))
    # Window grid
    cols, rows = 15, 20
    cw = bw // cols
    rh = bh // rows
    for col in range(cols):
        for row in range(rows):
            wx = bx + col * cw + 4
            wy = by + row * rh + 2
            uw = cw - 8
            uh = rh - 4
            brightness = int(120 + 60 * math.sin(col * 1.7 + row * 2.3))
            ud.rectangle(
                (wx, wy, wx + uw, wy + uh),
                fill=(brightness, brightness + 20, brightness + 40, 180),
            )
    # Left wing
    ud.rectangle((bx - 80, by + 100, bx, by + bh - 50), fill=(15, 25, 55, 200))
    # Right wing
    ud.rectangle((bx + bw, by + 100, bx + bw + 80, by + bh - 50), fill=(15, 25, 55, 200))
    # Flagpole
    ud.rectangle((cx - 3, by - 120, cx + 3, by), fill=(200, 180, 100, 220))
    un_building = un_building.filter(ImageFilter.GaussianBlur(2))
    img = Image.alpha_composite(img, un_building)

    # Shadowy figures in foreground (silhouettes)
    draw = ImageDraw.Draw(img)
    figure_positions = [(200, 1400), (600, 1450), (1000, 1420), (1400, 1470)]
    for fx, fy in figure_positions:
        # Body
        draw.ellipse((fx - 15, fy - 40, fx + 15, fy + 10), fill=(10, 8, 15, 200))
        # Head
        draw.ellipse((fx - 10, fy - 55, fx + 10, fy - 35), fill=(10, 8, 15, 200))
        # Legs
        draw.line((fx - 6, fy + 10, fx - 12, fy + 50), fill=(10, 8, 15, 200), width=6)
        draw.line((fx + 6, fy + 10, fx + 12, fy + 50), fill=(10, 8, 15, 200), width=6)

    # Gold accent lines
    draw.line((100, 1600, W - 100, 1600), fill=(200, 170, 80, 150), width=2)
    draw.line((300, 1610, W - 300, 1610), fill=(180, 150, 60, 80), width=1)

    # Title panel at bottom
    draw.line((200, H - 160, W - 200, H - 160), fill=(200, 170, 80, 100), width=2)

    # Small genre tag
    sf = font("arial.ttf", 28)
    centered(draw, 1990, ["A POLITICAL THRILLER"], sf, (160, 140, 100), 4)

    # Title
    tf = font("georgiab.ttf", 105)
    af = font("arialbd.ttf", 42)
    title_lines = wrap(draw, title.upper(), tf, 1300)
    y = centered(draw, 2080, title_lines, tf, (220, 190, 130), 10)
    y += 50

    # Author
    author_lines = wrap(draw, author, af, 1200)
    centered(draw, y, author_lines, af, (200, 180, 160), 6)

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
