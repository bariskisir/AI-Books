#!/usr/bin/env python3
"""Cover: The Dejima Interpreter — Programmatic gradient, cream bottom panel, bold title/author/model text."""

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

    img = Image.new("RGBA", (W, H), (235, 229, 214, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H - 800):
        t = y / (H - 800)
        r = int(50 + 185 * (1 - t * 3) if t < 0.33 else (100 + 135 * (1 - (t - 0.33) * 1.5)))
        g = int(55 + 174 * (1 - t * 3) if t < 0.33 else (105 + 124 * (1 - (t - 0.33) * 1.5)))
        b = int(70 + 144 * (1 - t * 3) if t < 0.33 else (120 + 94 * (1 - (t - 0.33) * 1.5)))
        draw.line((0, y, W, y), fill=(max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), 255))

    for _ in range(20):
        x = random.randint(0, W)
        y = random.randint(0, 1500)
        r = random.randint(30, 120)
        for i in range(10, 0, -1):
            alpha = max(0, 12 - i)
            draw.ellipse((x - r - i * 5, y - r - i * 5, x + r + i * 5, y + r + i * 5), fill=random.choice([(200, 180, 150, alpha), (180, 200, 210, alpha), (160, 140, 120, alpha)]))

    for x in range(0, W, 40):
        draw.line((x, 0, x, 1600), fill=(220, 210, 190, random.randint(5, 15)), width=1)
    for y in range(0, 1600, 40):
        draw.line((0, y, W, y), fill=(220, 210, 190, random.randint(5, 15)), width=1)

    tagline = "NAGASAKI  TRADE  TRANSLATION"
    bb = draw.textbbox((0, 0), tagline, font=font("georgia.ttf", 38))
    draw.text(((W - (bb[2] - bb[0])) // 2, 400), tagline, font=font("georgia.ttf", 38), fill=(82, 70, 55, 180))

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
