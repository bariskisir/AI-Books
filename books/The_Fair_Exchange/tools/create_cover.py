#!/usr/bin/env python3
"""Cover: The Fair Exchange — Twilight marketplace, contribution board, clock tower, barterers under warm lanterns, dusk blue/gold/terracotta."""

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

    img = Image.new("RGBA", (W, H), (50, 55, 70, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(1000):
        t = y / 1000
        r = int(50 + 70 * t)
        g = int(55 + 55 * t)
        b = int(70 + 25 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    for y in range(1000, 1800):
        t = (y - 1000) / 800
        r = int(120 - 30 * t)
        g = int(110 - 25 * t)
        b = int(95 - 20 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    building_col = (90, 85, 75)
    for x1, y1, x2, y2 in [(100, 500, 220, 750), (260, 480, 380, 750), (420, 520, 540, 750),
                            (580, 460, 700, 750), (740, 500, 860, 750), (900, 490, 1020, 750),
                            (1060, 510, 1180, 750), (1220, 470, 1340, 750), (1380, 500, 1520, 750)]:
        draw.rectangle((x1, y1, x2, y2), fill=building_col)
        draw.polygon([(x1 - 8, y1), ((x1 + x2) // 2, y1 - 55), (x2 + 8, y1)], fill=(130, 80, 60))

    tower_x = W // 2
    draw.rectangle((tower_x - 14, 650, tower_x + 14, 800), fill=(155, 135, 115))
    draw.polygon([(tower_x - 22, 650), (tower_x, 610), (tower_x + 22, 650)], fill=(175, 75, 55))
    draw.ellipse((tower_x - 8, 670, tower_x + 8, 688), fill=(255, 230, 180))

    stalls = [(150, 1050, 260, 1300), (320, 1070, 430, 1320), (510, 1030, 620, 1280),
              (710, 1060, 820, 1310), (910, 1040, 1020, 1290), (1110, 1050, 1220, 1300),
              (1310, 1070, 1420, 1320)]
    colors = [(180, 100, 60), (60, 130, 100), (160, 120, 50), (80, 100, 140), (140, 90, 110)]
    for idx, (sx1, sy1, sx2, sy2) in enumerate(stalls):
        c = colors[idx % len(colors)]
        draw.rectangle((sx1, sy1, sx2, sy2), fill=(160, 140, 110))
        draw.arc([(sx1 - 15, sy1 - 25), (sx2 + 15, sy1 + 15)], 0, 180, fill=(c[0] + 40, c[1] + 40, c[2] + 40), width=7)

    board_left = (W - 380) // 2
    board_top = 790
    draw.rectangle((board_left, board_top, board_left + 380, board_top + 260), fill=(60, 50, 40))
    draw.rectangle((board_left + 8, board_top + 8, board_left + 372, board_top + 252), fill=(100, 90, 75))
    entries = ["Anna - bread, 40 loaves", "Hugh - wool, 6 fleeces", "Eli - cart, 1 day",
               "Mara - water, 8 hrs", "Orin - barley, 17 bush", "Jory - archive, 6 hrs"]
    for i, entry in enumerate(entries):
        ey = board_top + 20 + i * 36
        draw.text((board_left + 16, ey), entry, font=font("arial.ttf", 14), fill=(220, 210, 190))
        draw.text((board_left + 340, ey), "/", font=font("arial.ttf", 14), fill=(160, 225, 160))

    def draw_person(cx, cy, sc=1.0):
        s = sc
        r = 7 * s
        draw.ellipse((cx - r, cy - r * 2, cx + r, cy), fill=(58, 53, 48))
        draw.line((cx, cy, cx, cy + 28 * s), fill=(58, 53, 48), width=int(3 * s))
        draw.line((cx, cy + 8 * s, cx - 10 * s, cy + 16 * s), fill=(58, 53, 48), width=int(2 * s))
        draw.line((cx, cy + 8 * s, cx + 10 * s, cy + 16 * s), fill=(58, 53, 48), width=int(2 * s))
        draw.line((cx, cy + 28 * s, cx - 5 * s, cy + 38 * s), fill=(58, 53, 48), width=int(2 * s))
        draw.line((cx, cy + 28 * s, cx + 5 * s, cy + 38 * s), fill=(58, 53, 48), width=int(2 * s))

    for px, py, sc in [(180, 1330, 0.9), (380, 1350, 0.8), (680, 1320, 1.0), (950, 1340, 0.85),
                       (1150, 1310, 0.95), (1350, 1330, 0.9), (580, 1370, 0.75), (1050, 1360, 0.8)]:
        draw_person(px, py, sc)

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for lx, ly in [(230, 1050), (530, 1030), (830, 1060), (1130, 1040)]:
        for r in range(130, 40, -10):
            alpha = max(0, 6 - (130 - r) // 15)
            gd.ellipse((lx - r, ly - r, lx + r, ly + r), fill=(255, 200, 120, alpha))
    img = Image.alpha_composite(img, glow)

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
