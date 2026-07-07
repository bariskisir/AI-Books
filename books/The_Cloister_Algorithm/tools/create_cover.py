#!/usr/bin/env python3
"""Cover: The Cloister Algorithm — Abbey cloister with scanner light on medieval parchment, meadow/millstream, parchment sepia/muted green/blue glow."""

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
W, H = 1600, 2560
FONT_DIR = Path("C:/Windows/Fonts")

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

    img = Image.new("RGBA", (W, H), (120, 108, 82, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        r = int(120 + (88 - 120) * t)
        g = int(108 + (96 - 108) * t)
        b = int(82 + (78 - 82) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    cloister = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cloister)
    cd.rectangle((0, 650, W, 1500), fill=(55, 72, 60, 220))
    for x in range(80, 1530, 220):
        cd.rectangle((x, 450, x + 100, 1300), fill=(46, 58, 48, 230))
        cd.arc((x - 20, 360, x + 120, 560), 180, 360, fill=(120, 150, 125, 180), width=12)
    cd.rectangle((0, 1310, W, 1500), fill=(42, 62, 52, 240))
    img = Image.alpha_composite(img, cloister)
    draw = ImageDraw.Draw(img, "RGBA")

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.rounded_rectangle((300, 950, 1300, 1250), radius=24, fill=(80, 200, 220, 40))
    gd.rounded_rectangle((380, 1000, 1220, 1200), radius=18, fill=(60, 220, 240, 30))
    glow = glow.filter(ImageFilter.GaussianBlur(12))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    draw.rounded_rectangle((340, 1020, 1260, 1180), radius=16, fill=(220, 208, 168, 230), outline=(88, 72, 52, 160), width=3)
    for i in range(10):
        y0 = 1060 + i * 32
        draw.line((380, y0, 1220, y0), fill=(50, 108, 74, 80), width=2)
    for i in range(8):
        y0 = 1075 + i * 34
        draw.line((400, y0, 1200, y0), fill=(108, 64, 40, 100), width=2)
    draw.text((460, 1130), "COMMUNIS AQUA", font=font("arialbd.ttf", 34), fill=(98, 62, 42, 220))

    for x, y, lab in [(150, 860, "SCANNER"), (1150, 820, "PARCHMENT"), (1000, 1460, "MILLSTREAM")]:
        draw.rounded_rectangle((x, y, x + 200, y + 60), radius=12, fill=(235, 226, 192, 215), outline=(92, 76, 54, 150), width=3)
        draw.text((x + 20, y + 18), lab, font=font("arialbd.ttf", 24), fill=(78, 58, 40, 225))

    draw.line((160, 1440, 1440, 1350), fill=(90, 180, 200, 180), width=6)
    for x in range(200, 1400, 130):
        draw.arc((x, 1420, x + 80, 1480), 0, 180, fill=(120, 200, 215, 120), width=4)

    tagline = "ABBOT SCANNER  PALIMPSEST  COMMON PASTURE"
    bb = draw.textbbox((0, 0), tagline, font=font("georgia.ttf", 32))
    draw.text(((W - (bb[2] - bb[0])) // 2, 280), tagline, font=font("georgia.ttf", 32), fill=(215, 200, 162, 230))

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
