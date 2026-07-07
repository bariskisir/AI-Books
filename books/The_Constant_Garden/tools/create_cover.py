#!/usr/bin/env python3
"""Cover: The Constant Garden — Bioluminescent twilight forest, glowing green mycelial threads, crescent moon, deep violet/emerald/dark blue."""

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

    img = Image.new("RGBA", (W, H), (8, 6, 20, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        r = int(8 + (15 - 8) * t)
        g = int(6 + (30 - 6) * t)
        b = int(20 + (55 - 20) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    for _ in range(100):
        x = random.randint(0, W)
        y = random.randint(0, 500)
        r = random.randint(1, 2)
        alpha = random.randint(80, 200)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(200, 220, 240, alpha))

    moon_x, moon_y = W - 200, 150
    for i in range(15, 0, -1):
        alpha = max(0, 20 - i)
        draw.ellipse((moon_x - 60 - i * 6, moon_y - 60 - i * 6, moon_x + 60 + i * 6, moon_y + 60 + i * 6), fill=(160, 200, 220, alpha))
    draw.ellipse((moon_x - 50, moon_y - 50, moon_x + 50, moon_y + 50), fill=(200, 230, 240))
    draw.ellipse((moon_x + 15, moon_y - 55, moon_x + 75, moon_y + 15), fill=(8, 6, 20))

    forest_start = 700
    for i in range(40):
        x = random.randint(0, W)
        h = random.randint(200, 450)
        w = random.randint(6, 14)
        draw.rectangle((x - w // 2, forest_start - h, x + w // 2, forest_start), fill=(5, 12, 8))
        for _ in range(random.randint(3, 5)):
            fx = x + random.randint(-35, 35)
            fy = forest_start - h + random.randint(-50, 10)
            fr = random.randint(25, 60)
            draw.ellipse((fx - fr, fy - fr, fx + fr, fy + fr), fill=(5, 18, 10))

    for _ in range(50):
        x = random.randint(0, W)
        y = forest_start + random.randint(-150, 200)
        pts = [(x + dx * random.randint(-15, 15), y + dy * random.randint(-5, 20)) for dx, dy in [(i, i) for i in range(12)]]
        alpha = random.randint(20, 70)
        for i in range(len(pts) - 1):
            draw.line([pts[i], pts[i + 1]], fill=(80, 200, 120, alpha), width=random.randint(1, 3))

    for _ in range(25):
        x = random.randint(50, W - 50)
        y = forest_start + random.randint(-50, 200)
        cap_h = int(25 * random.uniform(0.3, 1.5))
        cap_w = int(40 * random.uniform(0.3, 1.5))
        stem_h = int(50 * random.uniform(0.3, 1.5))
        draw.rectangle((x - 6, y - stem_h, x + 6, y), fill=(160, 220, 180))
        draw.ellipse((x - cap_w, y - stem_h - cap_h, x + cap_w, y - stem_h), fill=(80, 200, 140))
        for r in range(3, 8):
            alpha = max(0, 30 - r * 4)
            draw.ellipse((x - cap_w - r * 3, y - stem_h - cap_h - r * 3, x + cap_w + r * 3, y - stem_h + r * 3), fill=(80, 200, 140, alpha))

    for _ in range(150):
        x = random.randint(0, W)
        y = random.randint(forest_start - 300, forest_start + 200)
        r = random.randint(1, 3)
        alpha = random.randint(30, 120)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(100, 220, 140, alpha))

    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op, "PNG", optimize=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    metadata_path = ROOT / args.metadata if not args.metadata.is_absolute() else args.metadata
    output_path = ROOT / args.out if not args.out.is_absolute() else args.out
    make_cover(metadata_path, output_path)

if __name__ == "__main__":
    main()
