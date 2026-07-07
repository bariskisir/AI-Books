#!/usr/bin/env python3
"""Cover: The Lost Aisle — Dark wood door flush in concrete sub-basement wall, warm yellow light bleeding through crack, concrete gray/wood brown/warm yellow."""

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
    candidates = [
        FONT_DIR / name,
        FONT_DIR / "georgiab.ttf",
        FONT_DIR / "georgia.ttf",
        FONT_DIR / "arialbd.ttf",
        FONT_DIR / "arial.ttf",
    ]
    for c in candidates:
        if c.exists():
            return ImageFont.truetype(str(c), size)
    return ImageFont.load_default()


def wrap(draw, text, fnt, mw):
    words = text.split()
    lines = []
    cur = []
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
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        r = int(60 + 30 * t)
        g = int(55 + 25 * t)
        b = int(50 + 20 * t)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    for y in range(800, 1800):
        t = (y - 800) / 1000
        r = int(55 + 20 * t)
        g = int(50 + 18 * t)
        b = int(45 + 15 * t)
        draw.line((0, y, W, y), fill=(r, g, b))

    for x in range(0, W, 30):
        for y in range(800, 1800, 40):
            draw.line([(x, y), (x + 20, y)], fill=(70, 65, 58, 60), width=1)
            draw.line([(x, y), (x, y + 20)], fill=(70, 65, 58, 60), width=1)

    pipe_x = 100
    for py in range(600, 1800, 80):
        draw.ellipse([pipe_x - 10, py - 6, pipe_x + 10, py + 6], fill=(80, 75, 68, 180))
        draw.line([(pipe_x, py - 6), (pipe_x, py - 20)], fill=(80, 75, 68, 120), width=3)

    for px in [W - 120]:
        for py in range(700, 1800, 60):
            draw.ellipse([px - 6, py - 4, px + 6, py + 4], fill=(75, 70, 63, 180))

    door_x, door_y = W // 2 - 90, 600
    door_w, door_h = 180, 1000

    draw.rectangle([door_x - 15, door_y - 15, door_x + door_w + 15, door_y + door_h + 15],
                    fill=(55, 50, 45, 240))
    draw.rectangle([door_x - 8, door_y - 8, door_x + door_w + 8, door_y + door_h + 8],
                    fill=(40, 35, 30, 245))

    draw.rectangle([door_x, door_y, door_x + door_w, door_y + door_h],
                    fill=(50, 35, 20, 250))
    draw.rectangle([door_x + 15, door_y + 40, door_x + door_w - 15, door_y + door_h // 2 - 20],
                    fill=(58, 42, 25, 240))
    draw.rectangle([door_x + 15, door_y + door_h // 2 + 20, door_x + door_w - 15, door_y + door_h - 40],
                    fill=(58, 42, 25, 240))

    light_pts = [
        (door_x + door_w - 6, door_y + 80),
        (door_x + door_w + 8, door_y + 80),
        (door_x + door_w + 8, door_y + door_h - 80),
        (door_x + door_w - 6, door_y + door_h - 80),
    ]
    draw.polygon(light_pts, fill=(255, 220, 100, 220))

    spill = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(spill)
    sd.polygon([
        (door_x + door_w, door_y + door_h),
        (door_x + door_w + 350, door_y + door_h + 200),
        (door_x + door_w + 200, door_y + door_h + 280),
        (door_x + door_w, door_y + door_h + 100),
    ], fill=(255, 220, 100, 30))
    sd.polygon([
        (door_x + door_w - 6, door_y + door_h),
        (door_x + door_w + 200, door_y + door_h + 120),
        (door_x + door_w + 100, door_y + door_h + 180),
        (door_x + door_w - 6, door_y + door_h + 60),
    ], fill=(255, 220, 100, 50))
    spill = spill.filter(ImageFilter.GaussianBlur(20))
    img = Image.alpha_composite(img, spill)
    draw = ImageDraw.Draw(img, "RGBA")

    mist = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(mist, "RGBA")
    for _ in range(40):
        mx = random.randint(0, W)
        my = random.randint(500, 1700)
        mr = random.randint(100, 300)
        ma = random.randint(5, 15)
        md.ellipse([mx - mr, my - mr // 2, mx + mr, my + mr // 2],
                    fill=(100, 100, 100, ma))
    mist = mist.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, mist)
    draw = ImageDraw.Draw(img, "RGBA")

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([door_x + door_w - 20, door_y + door_h // 2 - 120,
                 door_x + door_w + 400, door_y + door_h // 2 + 120],
                fill=(255, 220, 100, 15))
    glow = glow.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    draw.rectangle((0, 1920, W, H), fill=(25, 22, 20, 235))
    draw.line((250, 1960, W - 250, 1960), fill=(200, 170, 100, 180), width=3)

    sf = font("arial.ttf", 28)
    centered(draw, 1980, ["A SUBSURFACE MYSTERY"], sf, (160, 150, 130), 6)

    tf = font("georgiab.ttf", 95)
    title_lines = wrap(draw, title.upper(), tf, 1200)
    y = centered(draw, 2060, title_lines, tf, (200, 180, 150), 10)

    y += 50
    af = font("arialbd.ttf", 42)
    centered(draw, y, [author], af, (180, 170, 160), 6)

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