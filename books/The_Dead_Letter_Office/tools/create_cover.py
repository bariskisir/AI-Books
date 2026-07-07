#!/usr/bin/env python3
"""Cover: The Dead Letter Office — Wooden mail shelves, sorting desk with cream envelopes, green desk lamp, warm brown/cream/forest green."""

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

    img = Image.new("RGBA", (W, H), (60, 40, 30, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        if t < 0.5:
            c = (60 + 60 * (t * 2), 40 + 50 * (t * 2), 30 + 30 * (t * 2))
        else:
            c = (120 + 80 * ((t - 0.5) * 2), 90 + 90 * ((t - 0.5) * 2), 60 + 100 * ((t - 0.5) * 2))
        draw.line((0, y, W, y), fill=(int(c[0]), int(c[1]), int(c[2]), 255))

    shelf_col = (72, 48, 30)
    for row in range(8):
        ys = int(H * 0.05) + row * 75
        draw.rectangle((20, ys, 240, ys + 6), fill=shelf_col)
        for v in range(5):
            vx = 20 + v * 44
            draw.rectangle((vx, ys - 55, vx + 3, ys), fill=shelf_col)
        for l in range(4):
            lx = 28 + l * 52
            ly = ys - 46
            draw.rectangle((lx, ly, lx + 36, ly + 24), fill=(220, 200, 170))
            draw.rectangle((lx + 2, ly + 2, lx + 34, ly + 22), fill=(240, 225, 200), outline=(180, 160, 130))

    for row in range(8):
        ys = int(H * 0.05) + row * 75
        draw.rectangle((W - 240, ys, W - 20, ys + 6), fill=shelf_col)
        for v in range(5):
            vx = W - 240 + v * 44
            draw.rectangle((vx, ys - 55, vx + 3, ys), fill=shelf_col)
        for l in range(4):
            lx = W - 232 + l * 52
            ly = ys - 46
            draw.rectangle((lx, ly, lx + 36, ly + 24), fill=(220, 200, 170))
            draw.rectangle((lx + 2, ly + 2, lx + 34, ly + 22), fill=(240, 225, 200), outline=(180, 160, 130))

    cx, cy = W // 2, int(H * 0.55)
    draw.rectangle((cx - 250, cy - 100, cx + 250, cy + 100), fill=(90, 60, 40))
    draw.rectangle((cx - 245, cy - 95, cx + 245, cy + 95), fill=(110, 75, 50))

    for i in range(6):
        lx = cx - 200 + i * 85 + random.randint(-10, 10)
        ly = cy - 60 + random.randint(-20, 20)
        draw.rectangle((lx, ly, lx + 50, ly + 34), fill=(230, 210, 185), outline=(160, 130, 100))
        draw.line((lx + 8, ly + 8, lx + 40, ly + 8), fill=(100, 80, 60), width=1)
        draw.line((lx + 8, ly + 14, lx + 40, ly + 14), fill=(100, 80, 60), width=1)
        draw.rectangle((lx + 30, ly + 3, lx + 42, ly + 14), fill=(180, 100, 80))

    lamp_cx = cx + 220
    lamp_cy = int(H * 0.35)
    draw.ellipse((lamp_cx - 12, lamp_cy + 50, lamp_cx + 12, lamp_cy + 68), fill=(55, 48, 38))
    draw.line((lamp_cx, lamp_cy + 50, lamp_cx - 35, lamp_cy - 15), fill=(55, 48, 38), width=5)
    draw.polygon([(lamp_cx - 45, lamp_cy - 35), (lamp_cx - 18, lamp_cy + 8), (lamp_cx + 18, lamp_cy + 8), (lamp_cx + 45, lamp_cy - 35)], fill=(45, 72, 55))

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((lamp_cx - 220, lamp_cy - 80, lamp_cx + 180, lamp_cy + 180), fill=(255, 230, 180, 15))
    img.paste(glow, (0, 0), glow)

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
