#!/usr/bin/env python3
"""Cover: The Common Breath — Dark industrial hall with conveyor belts, glowing dashboards, teal/grey with hazmat yellow accents."""

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

    img = Image.new("RGBA", (W, H), (38, 50, 55, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        r = int(38 + (50 - 38) * t)
        g = int(50 + (58 - 50) * t)
        b = int(55 + (48 - 55) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    for x in range(0, W, 100):
        draw.rectangle((x, 0, x + 18, 300), fill=(55, 65, 75, 200))
        for y in range(40, 300, 70):
            draw.rectangle((x - 8, y, x + 26, y + 5), fill=(65, 75, 85, 180))
    draw.rectangle((0, 180, W, 195), fill=(45, 55, 62, 220))

    belts = [(700, 720, 0, W, (55, 72, 65)), (770, 790, 0, W, (58, 75, 68)), (840, 860, 0, W, (52, 68, 62)), (910, 930, 0, W, (56, 72, 65))]
    for ys, ye, xs, xe, col in belts:
        draw.rectangle((xs, ys, xe, ye), fill=col)
        for bx in range(0, W, 14):
            draw.ellipse((bx, ys - 6, bx + 10, ye + 6), fill=(42, 60, 52))

    panels = [(80, 400, 320, 520), (550, 380, 880, 500), (1100, 410, 1450, 510)]
    for px1, py1, px2, py2 in panels:
        draw.rectangle((px1, py1, px2, py2), fill=(18, 28, 38, 200), outline=(60, 180, 200, 100))
        for dl in range(4):
            dly = py1 + 18 + dl * 22
            pts = [(dx, dly + int(math.sin((dx - px1) * 0.03 + dl * 1.5) * 6)) for dx in range(px1 + 8, px2 - 8, 6)]
            for i in range(len(pts) - 1):
                draw.line([pts[i], pts[i + 1]], fill=(50, 200, 220, random.randint(60, 140)), width=2)
        for dot in range(5):
            dx = px1 + 18 + dot * ((px2 - px1 - 36) // 4)
            dy = py2 - 10
            draw.ellipse((dx - 3, dy - 3, dx + 3, dy + 3), fill=random.choice([(80, 220, 80), (240, 220, 60), (60, 200, 220)]))

    for lx in range(80, W, 240):
        ly = 200
        for i in range(25):
            fade = 1.0 - i / 25
            bw = int(fade * 180 + 20)
            alpha = int(fade * 20)
            draw.rectangle((lx - bw // 2, ly + i * 8, lx + bw // 2, ly + i * 8 + 5), fill=(255, 240, 200, alpha))
        draw.rectangle((lx - 12, ly - 4, lx + 12, ly + 4), fill=(200, 200, 180, 150))
        draw.ellipse((lx - 6, ly - 2, lx + 6, ly + 5), fill=(255, 250, 220, 100))

    for _ in range(120):
        px = int(math.sin(_ * 7.1) * 500 + W // 2)
        py = 350 + int(math.cos(_ * 5.3) * 700)
        s = 1 + int(math.sin(_ * 3.7) * 2)
        alpha_p = int(math.sin(_ * 2.3) * 50 + 60)
        draw.ellipse((px - s, py - s, px + s, py + s), fill=(200, 220, 240, alpha_p))

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
