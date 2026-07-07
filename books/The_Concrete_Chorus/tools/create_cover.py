#!/usr/bin/env python3
"""Cover: The Concrete Chorus — Grey stone statue mid-scream against London skyline, bronze shield reflecting sunset, concrete gray/amber/burnt orange."""

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

    img = Image.new("RGBA", (W, H), (58, 55, 52, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        if t < 0.35:
            r = int(180 + 40 * t * 3)
            g = int(100 + 20 * t * 3)
            b = int(50 + 10 * t * 3)
        elif t < 0.55:
            r = int(194 + 10 * (t - 0.35) * 5)
            g = int(107 + 15 * (t - 0.35) * 5)
            b = int(57 + 20 * (t - 0.35) * 5)
        else:
            r = int(210 - 60 * (t - 0.55) * 2.2)
            g = int(130 - 40 * (t - 0.55) * 2.2)
            b = int(80 - 30 * (t - 0.55) * 2.2)
        draw.line((0, y, W, y), fill=(min(255, r), min(255, g), min(255, b), 255))

    buildings = [(80, 350, 140, 550), (250, 300, 180, 600), (480, 250, 160, 650), (700, 280, 200, 620), (960, 220, 140, 680), (1160, 260, 180, 640), (1400, 300, 160, 600)]
    for bx, by, bw, bh in buildings:
        draw.rectangle((bx, by, bx + bw, by + bh), fill=(38, 42, 48, 220))
        for _ in range(6):
            wx = bx + random.randint(8, bw - 12)
            wy = by + random.randint(10, bh - 20)
            draw.rectangle((wx, wy, wx + 6, wy + 10), fill=(60, 68, 78, 180))

    draw.ellipse((680, 420, 920, 660), outline=(140, 180, 160, 120), width=5)
    for a in range(0, 360, 30):
        ex = 800 + math.cos(math.radians(a)) * 100
        ey = 540 + math.sin(math.radians(a)) * 100
        draw.ellipse((ex - 4, ey - 4, ex + 4, ey + 4), fill=(160, 210, 180, 160))

    stat = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stat)
    scx, scy = W // 2, 700
    sd.ellipse((scx - 60, scy - 180, scx + 60, scy + 40), fill=(110, 108, 105, 240))
    sd.ellipse((scx - 65, scy - 40, scx + 65, scy + 80), fill=(105, 102, 98, 240))
    sd.rectangle((scx - 55, scy + 60, scx + 55, scy + 280), fill=(100, 98, 94, 240))
    sd.polygon([(scx - 50, scy + 80), (scx - 80, scy + 160), (scx - 50, scy + 180)], fill=(108, 105, 100, 240))
    sd.polygon([(scx + 50, scy + 80), (scx + 80, scy + 180), (scx + 50, scy + 190)], fill=(108, 105, 100, 240))

    sd.ellipse((scx - 30, scy - 120, scx - 8, scy - 95), fill=(200, 180, 160, 200))
    sd.ellipse((scx + 8, scy - 120, scx + 30, scy - 95), fill=(200, 180, 160, 200))
    sd.ellipse((scx - 18, scy - 108, scx - 12, scy - 100), fill=(40, 38, 36, 240))
    sd.ellipse((scx + 12, scy - 108, scx + 18, scy - 100), fill=(40, 38, 36, 240))
    sd.ellipse((scx - 18, scy - 68, scx + 18, scy - 30), fill=(55, 52, 48, 240))
    sd.arc((scx - 25, scy - 68, scx + 25, scy - 30), 200, 340, fill=(90, 85, 80, 240), width=5)
    img = Image.alpha_composite(img, stat)

    draw = ImageDraw.Draw(img)
    draw.ellipse((scx + 140, scy + 260, scx + 240, scy + 360), outline=(200, 140, 60, 160), width=8)
    draw.ellipse((scx + 145, scy + 265, scx + 235, scy + 355), fill=(180, 120, 50, 80))

    for _ in range(80):
        x = random.randint(0, W)
        y = random.randint(700, 1700)
        s = random.randint(2, 5)
        draw.ellipse((x, y, x + s, y + s), fill=(200, 180, 160, random.randint(30, 80)))

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
