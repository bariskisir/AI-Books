#!/usr/bin/env python3
"""Cover: The Watcher on the Wall — fortress wall, alien landscape, night watch."""

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
    for c in [FONT_DIR / name, FONT_DIR / "arialbd.ttf", FONT_DIR / "arial.ttf"]:
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

    # Steel gray to alien blue gradient — cold, harsh, military
    for y in range(H):
        t = y / H
        r = int(55 + 25 * (1 - t) - 10 * t)
        g = int(60 + 35 * (1 - t) - 20 * t)
        b = int(75 + 60 * (1 - t) + 40 * t)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Alien sky — faint aurora bands
    aurora = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ad = ImageDraw.Draw(aurora)
    for i in range(4):
        ay = 200 + i * 250 + random.randint(-30, 30)
        for x in range(0, W, 2):
            offset = 30 * math.sin(x / 100 + i * 1.5) + 20 * math.sin(x / 40 + i * 2)
            alpha = max(0, int(20 + 15 * math.sin(x / 50 + i) + random.randint(-5, 5)))
            ad.line(
                (x, ay + offset, x, ay + offset + 40 + 20 * math.sin(x / 60)),
                fill=(80, 150, 255, alpha), width=2,
            )
    aurora = aurora.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, aurora)
    draw = ImageDraw.Draw(img, "RGBA")

    # Stars in the sky
    for _ in range(120):
        sx = random.randint(0, W)
        sy = random.randint(0, 900)
        sr = random.randint(1, 3)
        sa = random.randint(100, 220)
        draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=(200, 220, 255, sa))

    # Distant alien landscape — jagged mountain silhouette
    for x in range(0, W, 3):
        mh = 800 + 80 * math.sin(x / 180) + 40 * math.sin(x / 70) + 30 * math.sin(x / 25)
        mh += random.randint(-5, 5)
        draw.rectangle((x, mh, x + 3, H), fill=(25, 35, 55, 200))

    # Second mountain range behind
    for x in range(0, W, 4):
        mh2 = 650 + 60 * math.sin(x / 150 + 1) + 30 * math.sin(x / 50 + 2)
        draw.rectangle((x, mh2, x + 4, H), fill=(35, 45, 70, 120))

    # The Wall — massive fortress wall spanning the center
    wall_left = 200
    wall_right = 1400
    wall_base = 1300
    wall_top = 700
    wall_color = (45, 50, 65, 230)
    wall_highlight = (65, 72, 90, 180)

    # Main wall body
    draw.polygon(
        [(wall_left, wall_base), (wall_left + 40, wall_top),
         (wall_right - 40, wall_top), (wall_right, wall_base)],
        fill=wall_color,
    )

    # Wall parapets / battlements
    for bx in range(wall_left + 40, wall_right - 40, 60):
        bw = 30
        bh = wall_top - 30
        draw.rectangle((bx, bh, bx + bw, wall_top), fill=wall_highlight)
        draw.rectangle((bx + 2, bh, bx + bw - 2, bh + 20), fill=(50, 58, 78, 200))

    # Wall surface detail — vertical lines
    for wx in range(wall_left + 60, wall_right - 60, 40):
        draw.line((wx, wall_top + 20, wx, wall_base - 50),
                  fill=(38, 42, 55, 100), width=2)

    # Dark gateway at base of wall
    gate_w = 120
    gate_h = 250
    gate_x = (wall_left + wall_right) // 2 - gate_w // 2
    gate_y = wall_base - gate_h
    draw.rectangle((gate_x, gate_y, gate_x + gate_w, wall_base),
                   fill=(10, 12, 18, 255))
    # Gate arch
    draw.arc((gate_x - 30, gate_y - 80, gate_x + gate_w + 30, gate_y + 80),
             180, 0, fill=(15, 18, 25, 240), width=20)

    # Watchtower on the wall
    tw_x = wall_left + 300
    tw_w = 80
    tw_h = 200
    draw.rectangle((tw_x, wall_top - tw_h, tw_x + tw_w, wall_top),
                   fill=(50, 55, 72, 230))
    # Tower roof
    draw.polygon(
        [(tw_x - 10, wall_top - tw_h), (tw_x + tw_w // 2, wall_top - tw_h - 60),
         (tw_x + tw_w + 10, wall_top - tw_h)],
        fill=(35, 40, 55, 240),
    )
    # Light from tower window
    draw.rectangle((tw_x + 25, wall_top - tw_h + 40, tw_x + 55, wall_top - tw_h + 80),
                   fill=(255, 200, 80, 180))
    draw.ellipse((tw_x + 30, wall_top - tw_h + 45, tw_x + 50, wall_top - tw_h + 75),
                 fill=(255, 200, 80, 100))

    # Second smaller tower
    tw2_x = wall_left + 700
    draw.rectangle((tw2_x, wall_top - 120, tw2_x + 60, wall_top),
                   fill=(48, 52, 68, 230))
    draw.polygon(
        [(tw2_x - 8, wall_top - 120), (tw2_x + 30, wall_top - 160),
         (tw2_x + 68, wall_top - 120)],
        fill=(33, 38, 52, 240),
    )

    # Searchlight beam from tower
    beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam)
    bd.polygon(
        [(tw_x + 40, wall_top - tw_h + 60),
         (400, 1300), (600, 1400)],
        fill=(200, 220, 255, 15),
    )
    bd.polygon(
        [(tw_x + 40, wall_top - tw_h + 60),
         (450, 1350), (550, 1420)],
        fill=(200, 220, 255, 10),
    )
    beam = beam.filter(ImageFilter.GaussianBlur(20))
    img = Image.alpha_composite(img, beam)
    draw = ImageDraw.Draw(img, "RGBA")

    # Snow-covered ground / frozen plain
    for x in range(0, W, 2):
        sh = wall_base + 20 + 5 * math.sin(x / 100) + 3 * math.sin(x / 30) + random.randint(-2, 2)
        draw.rectangle((x, sh, x + 2, H), fill=(55, 65, 85, 180))

    # Foreground ice crystals / debris
    for _ in range(30):
        ix = random.randint(0, W)
        iy = random.randint(1450, 1850)
        isz = random.randint(3, 10)
        ia = random.randint(30, 80)
        draw.polygon(
            [(ix, iy - isz), (ix + isz // 2, iy), (ix, iy + isz), (ix - isz // 2, iy)],
            fill=(150, 180, 220, ia),
        )

    # Frozen Barrens — subtle cracks in the ice
    for _ in range(15):
        cx = random.randint(100, 1500)
        cy = random.randint(1400, 1800)
        for s in range(5):
            ex = cx + random.randint(-30, 30)
            ey = cy + random.randint(-30, 30)
            draw.line((cx, cy, ex, ey), fill=(100, 130, 180, 40), width=1)
            cx, cy = ex, ey

    # Title panel at bottom
    # Accent lines
    draw.line((250, H - 140, W - 250, H - 140), fill=(100, 150, 220, 100), width=2)

    # Title
    tf = font("arialbd.ttf", 100)
    af = font("arialbd.ttf", 40)

    wrapped_title = wrap(draw, title.upper(), tf, 1200)
    y = centered(draw, 2000, wrapped_title, tf, (255, 255, 255), 8)
    y += 50
    centered(draw, y, [author], af, (180, 200, 230), 6)

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