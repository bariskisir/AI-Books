#!/usr/bin/env python3
"""Cover: The Palermo Exchange — warm stone, Vespa, shadowed doorway."""

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


def font(n, s):
    for c in [FONT_DIR / n, FONT_DIR / "georgia.ttf", FONT_DIR / "arial.ttf"]:
        if c.exists():
            return ImageFont.truetype(str(c), s)
    return ImageFont.load_default()


def wrap(d, t, f, w):
    wo = t.split()
    li = []
    cu = []
    for wd in wo:
        p = " ".join([*cu, wd])
        if d.textbbox((0, 0), p, font=f)[2] <= w:
            cu.append(wd)
        else:
            li.append(" ".join(cu))
            cu = [wd]
    if cu:
        li.append(" ".join(cu))
    return li


def centered(d, y, li, f, fl, g):
    for l in li:
        bb = d.textbbox((0, 0), l, font=f)
        d.text(((W - (bb[2] - bb[0])) // 2, y), l, font=f, fill=fl)
        y += bb[3] - bb[1] + g
    return y


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    ti = m["title"]
    au = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (180, 140, 100, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Warm stone gradient background
    for y in range(H):
        t = y / H
        r = int(180 - 40 * t)
        g = int(140 - 30 * t)
        b = int(100 - 20 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # Narrow street perspective (vicolo) — converging walls
    wall_color = (160, 120, 80, 120)
    draw.polygon([(0, 0), (300, 600), (300, 1400), (0, 1800)], fill=wall_color)  # left wall
    draw.polygon([(W, 0), (1300, 600), (1300, 1400), (W, 1800)], fill=wall_color)  # right wall

    # Stone texture lines on walls
    for i in range(8):
        x1 = int(300 + i * 30)
        x2 = int(1300 - i * 30)
        draw.line((x1, 600 + i * 100, x2, 600 + i * 100), fill=(140, 100, 65, 80), width=2)

    # Shadowed doorway on left wall
    door_x = 120
    door_y = 900
    draw.rectangle((door_x, door_y, door_x + 160, door_y + 280), fill=(30, 25, 20, 220))
    draw.arc((door_x - 10, door_y - 10, door_x + 170, door_y + 30), 180, 360, fill=(50, 40, 30, 200), width=8)

    # Arch above doorway
    draw.arc((door_x - 20, door_y - 40, door_x + 180, door_y + 40), 180, 0, fill=(100, 75, 50, 180), width=6)

    # Warm light spilling from doorway
    for i in range(5):
        alpha = 20 - i * 3
        draw.ellipse((door_x - 30 - i * 10, door_y + 260, door_x + 190 + i * 10, door_y + 300 + i * 30),
                     fill=(220, 180, 100, max(0, alpha)))

    # Vespa silhouette on right side
    vx, vy = 1250, 1100
    # Body
    draw.ellipse((vx - 60, vy - 40, vx + 60, vy + 60), fill=(50, 45, 40, 200))
    # Handlebars
    draw.line((vx - 40, vy - 50, vx + 20, vy - 60), fill=(60, 55, 50, 200), width=6)
    # Front shield
    draw.polygon([(vx + 10, vy - 30), (vx + 50, vy - 10), (vx + 50, vy + 30), (vx + 10, vy + 10)],
                 fill=(55, 50, 45, 200))
    # Wheels
    draw.ellipse((vx - 30, vy + 50, vx + 10, vy + 80), fill=(40, 35, 30, 200))
    draw.ellipse((vx + 20, vy + 50, vx + 60, vy + 80), fill=(40, 35, 30, 200))
    # Seat
    draw.rectangle((vx - 30, vy - 20, vx + 10, vy + 5), fill=(45, 40, 35, 200))

    # Shuttered window on right wall above
    wx, wy = 1350, 750
    draw.rectangle((wx, wy, wx + 120, wy + 160), fill=(80, 60, 40, 150))
    # Shutter slats
    for i in range(6):
        draw.line((wx, wy + 20 + i * 24, wx + 120, wy + 20 + i * 24), fill=(60, 45, 30, 180), width=3)

    # Wrought iron balcony railing
    bx, by = 500, 700
    draw.rectangle((bx, by, bx + 200, by + 20), fill=(40, 35, 30, 160))
    for i in range(8):
        draw.line((bx + 20 + i * 24, by + 20, bx + 20 + i * 24, by + 60), fill=(40, 35, 30, 140), width=3)
    draw.line((bx, by + 60, bx + 200, by + 60), fill=(40, 35, 30, 140), width=4)

    # Cobblestone texture on ground
    for gx in range(0, W, 50):
        for gy in range(1400, 1920, 30):
            if ((gx // 50) + (gy // 30)) % 2:
                draw.ellipse((gx, gy, gx + 20, gy + 10), fill=(130, 95, 65, 50))

    # Title panel
    draw.line((240, H - 150, W - 240, H - 150), fill=(200, 160, 100, 100), width=1)

    tf = font("georgiab.ttf", 100)
    af = font("arialbd.ttf", 40)
    sf = font("arial.ttf", 28)

    # Genre tag
    centered(draw, 2000, ["A CRIME THRILLER"], sf, (200, 160, 100), 6)

    # Title
    y = 2060
    title_lines = wrap(draw, ti.upper(), tf, 1200)
    y = centered(draw, y, title_lines, tf, (210, 195, 170), 10)
    y += 50

    # Author
    centered(draw, y, [au], af, (180, 175, 160), 6)

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