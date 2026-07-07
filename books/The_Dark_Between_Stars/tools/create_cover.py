#!/usr/bin/env python3
"""Cover: The Dark Between Stars — Abyssal black/deep green, cyclopean pillars with glowing symbols, trawler silhouette, dark teal/amber/turquoise."""

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

    img = Image.new("RGBA", (W, H), (2, 2, 5, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        if t < 0.45:
            c = (2 + 3 * (t / 0.45), 2 + 18 * (t / 0.45), 5 + 5 * (t / 0.45))
        elif t < 0.8:
            s = (t - 0.45) / 0.35
            c = (5 + 5 * s, 20 + 15 * s, 10 + 5 * s)
        else:
            s2 = (t - 0.8) / 0.2
            c = (10 - 9 * s2, 35 - 32 * s2, 15 - 14 * s2)
        draw.line((0, y, W, y), fill=(int(c[0]), int(c[1]), int(c[2]), 255))

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((W // 2 - 500, H // 2 - 300, W // 2 + 500, H // 2 + 300), fill=(0, 60, 30, 15))
    glow = glow.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    pillars = [(120, 400, 1765, 50), (320, 350, 1765, 65), (800, 180, 1765, 85), (1280, 380, 1765, 60), (1480, 450, 1765, 45)]
    for px, pt, pb, pw in pillars:
        for s in range(30):
            t = s / 30
            y = pt + (pb - pt) * t
            x_off = (-6 if px < 800 else 6) * math.sin(t * math.pi * 1.5)
            wobble = (px % 7 - 3)
            x = px + int(x_off) + wobble
            ww = pw + int(6 * math.sin(t * math.pi * 2))
            draw.rectangle((x - ww // 2, y, x + ww // 2, y + (pb - pt) / 30), fill=(8, 14, 8))
        draw.polygon([(px - pw // 2 - 8, pt), (px - pw // 2 - 14, pt + 25), (px + pw // 2 + 14, pt + 25), (px + pw // 2, pt)], fill=(10, 18, 12))
        draw.ellipse((px - 10, pt + 6, px + 10, pt + 24), fill=(0, 80, 40, 50))

    sx, sy = int(W * 0.72), int(H * 0.18)
    ship = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(ship)
    sd.polygon([(sx - 28, sy), (sx + 28, sy), (sx + 32, sy + 10), (sx - 32, sy + 10)], fill=(3, 5, 3))
    sd.rectangle((sx - 8, sy - 14, sx + 8, sy), fill=(4, 6, 4))
    sd.line((sx, sy - 14, sx, sy - 28), fill=(3, 5, 3), width=2)
    for i in range(3):
        ry = sy + 10 + i * 4
        sd.arc((sx - 38 - i * 8, ry - 2, sx + 38 + i * 8, ry + 2), 0, 180, fill=(0, 30, 15, 60 - i * 15), width=1)
    img = Image.alpha_composite(img, ship)
    draw = ImageDraw.Draw(img, "RGBA")

    for _ in range(70):
        x = random.randint(50, W - 50)
        y = random.randint(int(H * 0.15), int(H * 0.75))
        s = random.randint(2, 5)
        alpha = random.randint(40, 110)
        draw.ellipse((x - s * 3, y - s * 3, x + s * 3, y + s * 3), fill=(0, 80, 30, alpha // 3))
        draw.ellipse((x - s, y - s, x + s, y + s), fill=(0, 120, 50, alpha))
        draw.ellipse((x - 1, y - 1, x + 1, y + 1), fill=(120, 240, 120, 160))

    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op, "PNG", optimize=True)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    metadata_path = ROOT / args.metadata if not args.metadata.is_absolute() else args.metadata
    output_path = ROOT / args.out if not args.out.is_absolute() else args.out
    make_cover(metadata_path, output_path)

if __name__ == "__main__":
    main()
