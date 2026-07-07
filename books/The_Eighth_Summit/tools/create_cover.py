#!/usr/bin/env python3
"""Cover: The Eighth Summit — White/granite summit against steel-blue sky, pink alpenglow, tiny roped climbers, gray/steel blue/coral pink."""

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

    img = Image.new("RGBA", (W, H), (18, 34, 58, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        if t < 0.30:
            c = (18 + 22 * (t / 0.30), 34 + 36 * (t / 0.30), 58 + 46 * (t / 0.30))
        elif t < 0.50:
            s = (t - 0.30) / 0.20
            c = (40 + 56 * s, 70 + 56 * s, 104 + 54 * s)
        elif t < 0.60:
            s = (t - 0.50) / 0.10
            c = (96 + 118 * s, 126 + 30 * s, 158 + 4 * s)
        elif t < 0.70:
            s = (t - 0.60) / 0.10
            c = (214 - 18 * s, 156 + 44 * s, 162 + 52 * s)
        else:
            s = (t - 0.70) / 0.30
            c = (196 + 32 * s, 200 + 34 * s, 214 + 26 * s)
        draw.line((0, y, W, y), fill=(int(c[0]), int(c[1]), int(c[2]), 255))

    apex = (int(W * 0.60), int(H * 0.10))
    base_left = (int(W * 0.05), int(H * 0.72))
    base_right = (W + 80, int(H * 0.80))
    draw.polygon([apex, base_left, base_right], fill=(214, 222, 232))
    draw.polygon([apex, base_right, (int(W * 0.66), int(H * 0.48))], fill=(186, 196, 210))
    draw.polygon([apex, (int(W * 0.30), int(H * 0.38)), (int(W * 0.20), int(H * 0.56)), (int(W * 0.42), int(H * 0.32))], fill=(84, 90, 102))
    draw.polygon([(int(W * 0.34), int(H * 0.28)), (int(W * 0.46), int(H * 0.44)), (int(W * 0.30), int(H * 0.50)), (int(W * 0.26), int(H * 0.38))], fill=(60, 64, 74))

    ridge_x0, ridge_y0 = int(W * 0.18), int(H * 0.56)
    rx, ry = ridge_x0, ridge_y0
    for i in range(22):
        t = i / 22
        nx = int(ridge_x0 + (apex[0] - ridge_x0) * t)
        ny = int(ridge_y0 + (apex[1] - ridge_y0) * t)
        jag = (i % 2) * int(14 * (1 - t)) - int(6 * (1 - t))
        draw.line([(rx, ry), (nx, ny + jag)], fill=(238, 244, 250), width=max(2, int(7 * (1 - t)) + 2))
        rx, ry = nx, ny + jag

    cx, cy = int(W * 0.40), int(H * 0.38)
    draw.line([(cx - 60, cy + 44), (cx - 25, cy + 26), (cx - 6, cy + 12)], fill=(196, 70, 60), width=2)
    draw.line([(cx - 3, cy + 12), (cx - 7, cy + 24)], fill=(20, 24, 30), width=3)
    draw.line([(cx + 2, cy + 12), (cx + 4, cy + 24)], fill=(20, 24, 30), width=3)
    draw.line([(cx - 1, cy - 2), (cx, cy + 12)], fill=(24, 30, 40), width=5)
    draw.line([(cx, cy + 2), (cx + 8, cy - 6)], fill=(24, 30, 40), width=3)
    draw.line([(cx + 8, cy - 6), (cx + 12, cy - 18)], fill=(150, 150, 156), width=2)
    draw.line([(cx + 12, cy - 18), (cx + 6, cy - 20)], fill=(150, 150, 156), width=2)
    draw.line([(cx - 1, cy + 2), (cx - 7, cy + 5)], fill=(24, 30, 40), width=3)
    draw.ellipse([cx - 4, cy - 8, cx + 4, cy], fill=(214, 96, 72))
    draw.ellipse([cx - 5, cy, cx + 1, cy + 7], fill=(40, 48, 60))

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
