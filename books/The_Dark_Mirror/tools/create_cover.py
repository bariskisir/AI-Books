#!/usr/bin/env python3
"""Cover: The Dark Mirror — Dark blue/black mirror surface, face silhouette reflection, dim lighting, cold blue/charcoal/white."""

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

    img = Image.new("RGBA", (W, H), (12, 14, 22, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        r = int(12 + (8 - 12) * t)
        g = int(14 + (10 - 14) * t)
        b = int(22 + (30 - 22) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    mx, my = W // 2, 400
    mw, mh = 450, 640
    for y in range(my, my + mh):
        half_w = int(mw / 2 * math.sqrt(max(0, 1 - ((y - (my + mh / 2)) / (mh / 2)) ** 2)))
        if half_w > 0:
            t = (y - my) / mh
            r = int(15 + (25 - 15) * t)
            g = int(12 + (18 - 12) * t)
            b = int(28 + (35 - 28) * t)
            draw.line((mx - half_w, y, mx + half_w, y), fill=(r, g, b))

    face = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(face)
    fc_x, fc_y = mx, my + mh // 2
    fd.ellipse((fc_x - 60, fc_y - 90, fc_x + 60, fc_y + 30), fill=(8, 6, 14, 200))
    fd.ellipse((fc_x - 40, fc_y - 60, fc_x + 40, fc_y + 10), fill=(10, 8, 16, 200))
    fd.ellipse((fc_x - 15, fc_y - 45, fc_x - 5, fc_y - 32), fill=(4, 3, 8, 240))
    fd.ellipse((fc_x + 5, fc_y - 45, fc_x + 15, fc_y - 32), fill=(4, 3, 8, 240))
    fd.line((fc_x - 12, fc_y - 10, fc_x + 12, fc_y - 10), fill=(6, 5, 10, 200), width=2)
    img = Image.alpha_composite(img, face)

    for step in range(30):
        alpha = max(0, 28 - step * 1.2)
        glow_y = my + mh + step * 12
        glow_w = mw // 2 + step * 6
        draw.ellipse((mx - glow_w, glow_y - 10, mx + glow_w, glow_y + 10), fill=(60, 50, 40, int(alpha)))

    for thick in range(10):
        pts = [(mx + (mw // 2 + 8 + thick) * math.cos(math.radians(a)), (my + mh // 2) + (mh // 2 + 8 + thick) * math.sin(math.radians(a))) for a in range(361)]
        draw.line(pts + [pts[0]] if pts else pts, fill=(100 - thick * 4, 90 - thick * 3, 65 - thick * 2), width=2)

    for i in range(4):
        sx = mx - mw // 2 + 25 + i * 4
        draw.line((sx, my + 35 + i * 10, sx + 12, my + 160 + i * 12), fill=(140, 135, 150, 160), width=1)

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
