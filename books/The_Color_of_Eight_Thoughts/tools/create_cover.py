#!/usr/bin/env python3
"""Cover: The Color of Eight Thoughts — Octopus with warm chromatophores on amphorae in sand, gold ring, shafts of morning light, deep teal/turquoise/amber."""

from __future__ import annotations

import argparse
import json
import math
import random
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

def font(name: str, size: int):
    for candidate in (FONT_DIR / name, FONT_DIR / "arialbd.ttf", FONT_DIR / "arial.ttf"):
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()

def wrap(draw, text, fnt, max_width):
    words, lines, cur = text.split(), [], []
    for w in words:
        p = " ".join([*cur, w])
        if draw.textbbox((0, 0), p, font=fnt)[2] <= max_width:
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
    author = m.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (14, 68, 78, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(1765):
        t = y / 1765
        r = int(14 + (8 - 14) * t)
        g = int(68 + (32 - 68) * t)
        b = int(78 + (50 - 78) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    light = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(light)
    for i in range(180, 0, -2):
        a = int(40 * (1 - i / 180))
        ld.polygon([(700 - i // 3, 0), (700 + i // 3, 0), (700 + 220 + i, 1765), (700 + 40 - i, 1765)], fill=(255, 236, 180, a))
    light = light.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(img, light)

    draw = ImageDraw.Draw(img)
    jars = [(200, 1360, 0.9, 20), (380, 1480, 1.1, -10), (1250, 1390, 1.0, 12), (1440, 1500, 1.2, 6), (1060, 1340, 0.8, -18)]
    for jx, jy, js, jrot in jars:
        w = int(110 * js)
        h = int(280 * js)
        col = (58, 72, 66)
        draw.ellipse((jx - w // 2, jy - h // 2, jx + w // 2, jy + h // 4), fill=col)
        draw.rectangle((jx - w // 6, jy - h // 2 - h // 6, jx + w // 6, jy - h // 4), fill=col)
        draw.ellipse((jx - w // 5, jy - h // 2 - h // 5, jx + w // 5, jy - h // 3), fill=(50, 64, 60))
        draw.arc((jx - w // 2 - 12, jy - h // 2 - 4, jx - w // 6, jy - h // 6), 250, 30, fill=col, width=7)
        draw.arc((jx + w // 6, jy - h // 2 - 4, jx + w // 2 + 12, jy - h // 6), 150, 290, fill=col, width=7)

    rx, ry = 1080, 1580
    for r in range(32, 0, -2):
        a = int(100 * (1 - r / 32))
        draw.ellipse((rx - r, ry - r, rx + r, ry + r), fill=(255, 226, 140, max(0, a // 3)))
    draw.ellipse((rx - 28, ry - 28, rx + 28, ry + 28), outline=(255, 232, 150, 240), width=8)

    octo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(octo)
    cx, cy = 800, 880
    skin = (150, 96, 78)
    rng = random.Random(11)
    for a in [200, 230, 255, 280, 305, 330, 150, 120]:
        ang = math.radians(a)
        x, y = cx + math.cos(ang) * 110, cy + math.sin(ang) * 110
        wd = 42
        da = 0.0
        for i in range(14):
            ang2 = ang + da
            nx = x + math.cos(ang2) * 42
            ny = y + math.sin(ang2) * 42
            w2 = max(4, int(wd * (1 - i / 14)))
            od.line([(x, y), (nx, ny)], fill=skin, width=w2)
            od.ellipse((nx - w2 // 2, ny - w2 // 2, nx + w2 // 2, ny + w2 // 2), fill=skin)
            x, y = nx, ny
            da += rng.uniform(-0.16, 0.16) + rng.uniform(-0.04, 0.04)
    od.ellipse((cx - 150, cy - 220, cx + 150, cy + 80), fill=skin)
    od.ellipse((cx - 168, cy - 60, cx + 168, cy + 140), fill=skin)

    mottle = Image.new("RGBA", octo.size, (0, 0, 0, 0))
    md = ImageDraw.Draw(mottle)
    palette = [(196, 120, 70, 90), (210, 150, 60, 80), (150, 60, 50, 90), (120, 70, 100, 70), (220, 170, 90, 70)]
    for _ in range(250):
        mx = cx + rng.randint(-160, 160)
        my = cy + rng.randint(-220, 140)
        mr = rng.randint(10, 34)
        md.ellipse((mx - mr, my - mr, mx + mr, my + mr), fill=rng.choice(palette))
    mottle = mottle.filter(ImageFilter.GaussianBlur(6))
    body_mask = octo.split()[3]
    octo.alpha_composite(Image.composite(mottle, Image.new("RGBA", mottle.size, (0, 0, 0, 0)), body_mask))

    od2 = ImageDraw.Draw(octo)
    ex, ey = cx + 60, cy - 110
    od2.ellipse((ex - 55, ey - 40, ex + 55, ey + 40), fill=(230, 214, 150, 255))
    od2.ellipse((ex - 55, ey - 40, ex + 55, ey + 40), outline=(120, 80, 60, 255), width=4)
    od2.rectangle((ex - 40, ey - 8, ex + 40, ey + 8), fill=(16, 18, 16, 255))
    od2.ellipse((ex + 18, ey - 12, ex + 30, ey), fill=(255, 250, 230, 230))
    img.paste(Image.alpha_composite(img.convert("RGBA"), octo).convert("RGB"), (0, 0))

    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op, "PNG", optimize=True)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    make_cover(args.metadata, args.out)

if __name__ == "__main__":
    main()
