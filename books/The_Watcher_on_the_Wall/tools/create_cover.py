#!/usr/bin/env python3
"""Cover: The Watcher on the Wall — Solitary figure on black-ice wall under cold alien sky, endless frozen plain stretching before him."""

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

    for y in range(H):
        t = y / H
        r = int(20 + 15 * (1 - t) + 10 * t)
        g = int(30 + 20 * (1 - t) + 15 * t)
        b = int(50 + 40 * (1 - t) + 30 * t)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    stars = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stars)
    for _ in range(150):
        sx = random.randint(0, W)
        sy = random.randint(0, 800)
        sr = random.randint(1, 2)
        sa = random.randint(80, 200)
        sd.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=(180, 200, 255, sa))
    stars = stars.filter(ImageFilter.GaussianBlur(1))
    img = Image.alpha_composite(img, stars)
    draw = ImageDraw.Draw(img, "RGBA")

    alien_moon_cx, alien_moon_cy = W // 2 + 200, 250
    for i in range(5):
        mr = 100 + i * 30
        ma = 20 - i * 4
        draw.ellipse((alien_moon_cx - mr, alien_moon_cy - mr, alien_moon_cx + mr, alien_moon_cy + mr), fill=(50, 80, 120, ma))
    draw.ellipse((alien_moon_cx - 60, alien_moon_cy - 60, alien_moon_cx + 60, alien_moon_cy + 60), fill=(60, 90, 140, 200))

    plain_y = 1000
    for y in range(plain_y, H):
        t = (y - plain_y) / (H - plain_y)
        r = int(10 + 20 * t)
        g = int(15 + 25 * t)
        b = int(30 + 40 * t)
        wave = int(3 * math.sin(y / 60))
        draw.line((0, y + wave, W, y), fill=(r, g, b))

    for x in range(0, W, 4):
        mh = 750 + 60 * math.sin(x / 150) + 40 * math.sin(x / 60) + random.randint(-5, 5)
        draw.rectangle((x, mh, x + 4, H), fill=(20, 28, 45, 200))
    for x in range(0, W, 5):
        mh2 = 650 + 50 * math.sin(x / 120 + 1) + 30 * math.sin(x / 40)
        draw.rectangle((x, mh2, x + 5, H), fill=(30, 38, 55, 120))

    wall_left = 250
    wall_right = 1350
    wall_base = 1000
    wall_top = 750
    draw.polygon([(wall_left, wall_base), (wall_left + 50, wall_top), (wall_right - 50, wall_top), (wall_right, wall_base)], fill=(35, 40, 55, 230))
    for bx in range(wall_left + 50, wall_right - 50, 50):
        draw.rectangle((bx, wall_top - 25, bx + 25, wall_top), fill=(50, 55, 70, 180))
    for wx in range(wall_left + 70, wall_right - 70, 35):
        draw.line((wx, wall_top + 15, wx, wall_base - 30), fill=(28, 32, 45, 80), width=2)

    figure_x = (wall_left + wall_right) // 2
    figure_y = wall_base
    draw.ellipse((figure_x - 10, figure_y - 90, figure_x + 10, figure_y - 65), fill=(8, 8, 12, 220))
    draw.polygon([(figure_x - 20, figure_y - 65), (figure_x + 20, figure_y - 65), (figure_x + 22, figure_y), (figure_x - 22, figure_y)], fill=(8, 8, 12, 220))
    draw.line((figure_x, figure_y, figure_x, figure_y + 30), fill=(8, 8, 12, 220), width=5)

    for x in range(0, W, 3):
        sh = wall_base + 15 + 4 * math.sin(x / 80) + 3 * math.sin(x / 25) + random.randint(-2, 2)
        draw.rectangle((x, sh, x + 3, H), fill=(25, 35, 55, 200))

    for _ in range(20):
        ix = random.randint(50, W - 50)
        iy = random.randint(wall_base + 50, wall_base + 300)
        isz = random.randint(3, 8)
        draw.polygon([(ix, iy - isz), (ix + isz // 2, iy), (ix, iy + isz), (ix - isz // 2, iy)], fill=(100, 140, 190, 100 if random.random() < 0.5 else 100))

    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog)
    for _ in range(25):
        fx = random.randint(-200, W + 200)
        fy = random.randint(300, 1200)
        fd.ellipse((fx, fy, fx + random.randint(400, 1000), fy + random.randint(100, 300)), fill=(100, 130, 180, random.randint(3, 8)))
    fog = fog.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img, fog)
    draw = ImageDraw.Draw(img, "RGBA")

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