#!/usr/bin/env python3
"""Cover: The Fermentation Master — Onggi clay jars on stone platform in hanok courtyard, elderly woman's hands, earthy browns/dark green/pale cream."""

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

    img = Image.new("RGBA", (W, H), (190, 175, 140, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(480):
        t = y / 480
        r = int(195 + 15 * t)
        g = int(205 + 10 * t)
        b = int(215 - 15 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    draw.polygon([(0, 90), (W, 90), (W - 40, 130), (40, 130), (0, 90)], fill=(58, 48, 40))
    for y in range(90, 400, 14):
        draw.line((10, y, W - 10, y), fill=(48, 40, 32), width=1)
    draw.arc((-60, 360, 100, 480), 270, 360, fill=(38, 32, 24), width=6)
    draw.arc((W - 100, 360, W + 60, 480), 180, 270, fill=(38, 32, 24), width=6)

    for y in range(400, 1765):
        t = (y - 400) / (1765 - 400)
        r = int(175 + (145 - 175) * t)
        g = int(158 + (130 - 158) * t)
        b = int(118 + (95 - 118) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    pt, pb = 650, 1740
    draw.rectangle((60, pt, W - 60, pb), fill=(130, 118, 100))
    for sy in range(680, pb, 55):
        draw.line((60, sy, W - 60, sy), fill=(108, 98, 82), width=2)
    for i, sy in enumerate(range(680, pb, 55)):
        cols = [180, 350, 520, 700, 880, 1060, 1240, 1420] if i % 2 == 0 else [120, 280, 450, 620, 800, 980, 1160, 1340, 1520]
        next_sy = min(sy + 55, pb)
        for sx in cols:
            if 60 < sx < W - 60:
                draw.line((sx, sy, sx, next_sy), fill=(108, 98, 82), width=2)

    rack_x = 50
    draw.rectangle((rack_x, 420, rack_x + 14, 650), fill=(90, 68, 44))
    draw.rectangle((rack_x - 8, 425, rack_x + 150, 440), fill=(80, 60, 38))
    for bx in [rack_x + 8, rack_x + 35, rack_x + 65, rack_x + 95, rack_x + 122]:
        for j in range(6):
            cy = 448 + j * 28
            draw.ellipse((bx, cy - 10, bx + 12, cy + 2), fill=(180, 40, 20))
            draw.polygon([(bx + 6, cy + 2), (bx + 10, cy + 12), (bx + 2, cy + 2)], fill=(165, 35, 18))

    jar_cols = [(142, 88, 58), (128, 76, 50), (155, 96, 62), (135, 82, 55), (148, 91, 60), (122, 74, 48)]
    for jx, jy, jw, jh, col in [(180, 900, 100, 240, jar_cols[0]), (320, 900, 100, 240, jar_cols[1]),
                                 (500, 900, 100, 240, jar_cols[2]), (680, 900, 100, 240, jar_cols[3]),
                                 (860, 900, 100, 240, jar_cols[4]), (1040, 900, 100, 240, jar_cols[5]),
                                 (1220, 900, 100, 240, jar_cols[0]), (1400, 900, 100, 240, jar_cols[1])]:
        draw.polygon([(jx - jw // 2, jy), (jx - jw // 3, jy - jh // 2), (jx - jw // 4, jy - jh * 3 // 4), (jx + jw // 4, jy - jh * 3 // 4), (jx + jw // 3, jy - jh // 2), (jx + jw // 2, jy)], fill=col)
        draw.ellipse((jx - jw // 4, jy - jh * 3 // 4 - 15, jx + jw // 4, jy - jh * 3 // 4 + 5), fill=(max(0, col[0] - 35), max(0, col[1] - 28), max(0, col[2] - 20)))

    jar_cx, jar_cy = 560, 1400
    draw.polygon([(jar_cx - 80, jar_cy), (jar_cx - 55, jar_cy - 180), (jar_cx - 40, jar_cy - 260), (jar_cx + 40, jar_cy - 260), (jar_cx + 55, jar_cy - 180), (jar_cx + 80, jar_cy)], fill=(148, 91, 60))
    draw.ellipse((jar_cx - 40, jar_cy - 275, jar_cx + 40, jar_cy - 250), fill=(113, 63, 40))

    skin = (195, 148, 110)
    lcy = jar_cy - 260
    draw.ellipse((jar_cx - 80, lcy - 18, jar_cx + 8, lcy + 22), fill=skin)
    draw.ellipse((jar_cx - 88, lcy - 8, jar_cx - 58, lcy + 12), fill=skin)
    for fx, fy in [(jar_cx - 64, lcy - 18), (jar_cx - 46, lcy - 24), (jar_cx - 28, lcy - 24), (jar_cx - 10, lcy - 18)]:
        draw.ellipse((fx - 8, fy - 46, fx + 8, fy + 4), fill=skin)

    draw.ellipse((jar_cx + 46, lcy - 18, jar_cx + 72, lcy + 22), fill=skin)
    for fx, fy in [(jar_cx + 54, lcy - 18), (jar_cx + 38, lcy - 23), (jar_cx + 22, lcy - 23), (jar_cx + 6, lcy - 18)]:
        draw.ellipse((fx - 7, fy - 44, fx + 7, fy + 4), fill=skin)

    light = Image.new("RGBA", (W, 1765), (0, 0, 0, 0))
    ld = ImageDraw.Draw(light)
    for step in range(35):
        alpha = int(15 - step * 0.4)
        if alpha <= 0:
            break
        ld.ellipse(((W - 250 - step * 25), (-120 - step * 15), (W + 150 + step * 15), (500 + step * 25)), fill=(255, 220, 140, alpha))
    art = Image.alpha_composite(img.crop((0, 0, W, 1765)).convert("RGBA"), light)
    img.paste(art.convert("RGB"), (0, 0))

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
