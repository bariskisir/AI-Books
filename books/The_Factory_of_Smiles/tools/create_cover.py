#!/usr/bin/env python3
"""Cover: The Factory of Smiles — Industrial pipes/hoppers, theatrical happy/sad masks, conveyor belt with glowing pills, steel gray/mask white/amber."""

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

    img = Image.new("RGBA", (W, H), (200, 195, 180, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        if t < 0.4:
            c = (240 - 20 * (t / 0.4), 240 - 30 * (t / 0.4), 235 - 55 * (t / 0.4))
        elif t < 0.7:
            s = (t - 0.4) / 0.3
            c = (220 - 30 * s, 210 - 25 * s, 180 - 10 * s)
        else:
            s = (t - 0.7) / 0.3
            c = (190 - 140 * s, 185 - 140 * s, 170 - 130 * s)
        draw.line((0, y, W, y), fill=(int(c[0]), int(c[1]), int(c[2]), 255))

    for hx in [int(W * 0.15), int(W * 0.5), int(W * 0.85)]:
        hy = 40
        draw.polygon([(hx - 45, hy), (hx + 45, hy), (hx + 25, hy + 110), (hx - 25, hy + 110)], fill=(150, 145, 135, 200))
    for px in [int(W * 0.15), int(W * 0.5), int(W * 0.85)]:
        draw.rectangle((px - 5, 150, px + 5, int(H * 0.52)), fill=(130, 125, 115, 200))

    mx, my = int(W * 0.25), int(H * 0.32)
    draw.ellipse((mx - 70, my - 70, mx + 70, my + 70), fill=(230, 215, 190, 200))
    draw.ellipse((mx - 70, my - 70, mx + 70, my + 70), outline=(180, 165, 140), width=3)
    draw.ellipse((mx - 25, my - 22, mx - 8, my - 4), fill=(50, 45, 40))
    draw.ellipse((mx + 8, my - 22, mx + 25, my - 4), fill=(50, 45, 40))
    draw.arc((mx - 30, my - 8, mx + 30, my + 35), 10, 170, fill=(180, 50, 50, 200), width=5)

    mx2, my2 = int(W * 0.75), int(H * 0.32)
    draw.ellipse((mx2 - 70, my2 - 70, mx2 + 70, my2 + 70), fill=(200, 190, 175, 200))
    draw.ellipse((mx2 - 70, my2 - 70, mx2 + 70, my2 + 70), outline=(160, 150, 135), width=3)
    draw.ellipse((mx2 - 25, my2 - 22, mx2 - 8, my2 - 4), fill=(50, 45, 40))
    draw.ellipse((mx2 + 8, my2 - 22, mx2 + 25, my2 - 4), fill=(50, 45, 40))
    draw.arc((mx2 - 30, my2 + 8, mx2 + 30, my2 + 35), 190, 350, fill=(100, 80, 80, 200), width=5)

    belt_y = int(H * 0.55)
    draw.rectangle((0, belt_y - 15, W, belt_y + 15), fill=(75, 70, 65))
    for x in range(0, W, 110):
        draw.ellipse((x - 7, belt_y - 10, x + 7, belt_y + 10), fill=(55, 55, 55))

    for i, cx in enumerate(range(90, W - 60, 130)):
        cy = belt_y - 22
        col = [(255, 230, 100, 220), (255, 210, 80, 200), (240, 220, 120, 210)][i % 3]
        draw.rectangle((cx - 14, cy - 14, cx + 14, cy + 14), fill=col)
        draw.rectangle((cx - 11, cy - 11, cx + 11, cy + 11), fill=(255, 255, 200, 180))
        draw.ellipse((cx - 5, cy - 5, cx - 2, cy - 2), fill=(80, 60, 20, 200))
        draw.ellipse((cx + 2, cy - 5, cx + 5, cy - 2), fill=(80, 60, 20, 200))
        draw.arc((cx - 6, cy - 2, cx + 6, cy + 5), 0, 180, fill=(80, 60, 20, 200), width=2)

    for i in range(5):
        wx = 60 + i * 300
        wy = belt_y - 70
        col = (175, 170, 160, 180)
        draw.rectangle((wx - 16, wy - 8, wx + 16, wy + 45), fill=col)
        draw.ellipse((wx - 12, wy - 35, wx + 12, wy - 12), fill=col)
        draw.arc((wx - 7, wy - 26, wx + 7, wy - 15), 0, 180, fill=(100, 95, 85, 220), width=2)
        draw.line((wx + 16, wy + 8, wx + 50, wy + 18), fill=col, width=5)

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
