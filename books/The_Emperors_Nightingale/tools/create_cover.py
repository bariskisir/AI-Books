#!/usr/bin/env python3
"""Cover: The Emperor's Nightingale — Dark night sky with moon/stars, brass mechanical nightingale in flight, palace silhouette, midnight blue/gold/brass."""

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

    img = Image.new("RGBA", (W, H), (10, 12, 5, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        r = int(10 + 18 * t)
        g = int(12 + 22 * t)
        b = int(5 + 20 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    for _ in range(100):
        x = random.randint(0, W)
        y = random.randint(0, 700)
        r = random.randint(1, 2)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(240, 220, 180))

    moon_cx, moon_cy = 1200, 180
    draw.ellipse((moon_cx - 55, moon_cy - 55, moon_cx + 55, moon_cy + 55), fill=(240, 230, 210))
    draw.ellipse((moon_cx + 15, moon_cy - 55, moon_cx + 65, moon_cy + 15), fill=(10, 12, 5))

    palace = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(palace)
    pts = [
        (80, 1100), (160, 820), (240, 820), (240, 780), (260, 780), (260, 740),
        (300, 740), (300, 690), (340, 690), (340, 650), (380, 650),
        (380, 690), (420, 690), (420, 740), (460, 740), (460, 780),
        (480, 780), (480, 820), (560, 820), (660, 820),
        (660, 780), (680, 780), (680, 740), (720, 740), (720, 690),
        (760, 690), (760, 650), (800, 650), (800, 690), (840, 690),
        (840, 740), (880, 740), (880, 780), (900, 780), (900, 820),
        (980, 820), (1080, 820), (1080, 860), (1400, 860), (1400, 1100),
    ]
    pd.polygon(pts, fill=(0, 0, 0))
    pd.polygon([(40, 1100), (40, 960), (60, 960), (60, 920), (80, 920), (80, 880), (120, 880), (120, 960), (140, 960), (140, 1100)], fill=(0, 0, 0))
    pd.polygon([(1100, 1100), (1100, 960), (1120, 960), (1120, 920), (1140, 920), (1140, 880), (1180, 880), (1180, 960), (1200, 960), (1200, 1100)], fill=(0, 0, 0))
    img = Image.alpha_composite(img, palace)

    bird = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bird)
    bx, by = 750, 550
    bd.ellipse((bx - 35, by - 18, bx + 35, by + 22), fill=(184, 134, 11), outline=(212, 175, 55), width=2)
    bd.ellipse((bx + 25, by - 35, bx + 48, by - 12), fill=(184, 134, 11), outline=(212, 175, 55), width=2)
    bd.ellipse((bx + 36, by - 28, bx + 42, by - 22), fill=(212, 175, 55))
    bd.ellipse((bx + 38, by - 26, bx + 40, by - 24), fill=(255, 255, 255))
    bd.polygon([(bx + 48, by - 26), (bx + 65, by - 24), (bx + 48, by - 18)], fill=(212, 175, 55))
    bd.polygon([(bx - 15, by - 8), (bx - 100, by - 70), (bx - 50, by - 3)], fill=(160, 120, 20), outline=(212, 175, 55), width=1)
    bd.polygon([(bx + 8, by - 8), (bx + 85, by - 60), (bx + 42, by - 3)], fill=(160, 120, 20), outline=(212, 175, 55), width=1)
    bd.polygon([(bx - 25, by + 12), (bx - 70, by + 50), (bx - 12, by + 18)], fill=(160, 120, 20), outline=(212, 175, 55), width=1)
    bd.ellipse((bx - 12, by - 4, bx + 12, by + 4), fill=(212, 175, 55))
    for a in range(0, 360, 60):
        gx = bx + int(12 * math.cos(math.radians(a)))
        gy = by + int(3 * math.sin(math.radians(a)))
        bd.ellipse((gx - 3, gy - 3, gx + 3, gy + 3), fill=(155, 30, 30))
    img = Image.alpha_composite(img, bird)

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
