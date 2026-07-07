#!/usr/bin/env python3
"""Cover: The Ferrite Ledger — Sera Kade holding fractured bridge bolt beside open green ledger, river sparkle, steel blue/rusted orange/document green."""

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

    img = Image.new("RGBA", (W, H), (28, 35, 42, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        if t < 0.4:
            c = (28 + 20 * (t / 0.4), 35 + 15 * (t / 0.4), 42 + 8 * (t / 0.4))
        elif t < 0.7:
            s = (t - 0.4) / 0.3
            c = (48 + 20 * s, 50 + 15 * s, 50 + 5 * s)
        else:
            s = (t - 0.7) / 0.3
            c = (68 - 30 * s, 65 - 25 * s, 55 - 20 * s)
        draw.line((0, y, W, y), fill=(int(c[0]), int(c[1]), int(c[2]), 255))

    river = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(river)
    for y in range(800, 1500, 2):
        t = (y - 800) / 700
        alpha = int(40 + 60 * (1 - t))
        w = 300 + int(200 * t)
        rd.line((W // 2 - w // 2, y, W // 2 + w // 2, y), fill=(60, 100, 120, alpha))
    for _ in range(80):
        sx = random.randint(W // 2 - 250, W // 2 + 250)
        sy = random.randint(800, 1450)
        rd.ellipse((sx - 2, sy - 2, sx + 2, sy + 2), fill=(180, 220, 240, random.randint(30, 100)))
    img = Image.alpha_composite(img, river)
    draw = ImageDraw.Draw(img, "RGBA")

    beam_pts = [(150, 700), (400, 350), (700, 300), (1000, 320), (1300, 370), (1550, 500)]
    draw.line(beam_pts, fill=(48, 58, 65, 240), width=22)
    for i in range(len(beam_pts) - 1):
        draw.line([beam_pts[i], beam_pts[i + 1]], fill=(55, 65, 72, 240), width=18)

    bolt_x, bolt_y = 400, 600
    draw.line((bolt_x, bolt_y, bolt_x + 140, bolt_y - 30), fill=(160, 80, 40, 240), width=14)
    draw.line((bolt_x + 140, bolt_y - 30, bolt_x + 160, bolt_y - 20), fill=(160, 80, 40, 240), width=10)
    draw.ellipse((bolt_x + 140 - 12, bolt_y - 42, bolt_x + 140 + 12, bolt_y - 18), fill=(180, 100, 50, 240))

    ledger = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(ledger)
    ld.rectangle((800, 600, 1200, 950), fill=(60, 85, 55, 240))
    ld.rectangle((810, 610, 1190, 940), fill=(50, 72, 46, 240))
    for r in range(4):
        ly = 650 + r * 65
        ld.line((830, ly, 1170, ly), fill=(80, 110, 70, 200), width=2)
    ld.text((870, 660), "BRIDGE 417", font=font("arialbd.ttf", 28), fill=(200, 220, 180, 230))
    ld.text((870, 725), "LOT F-19", font=font("arialbd.ttf", 28), fill=(200, 220, 180, 230))
    ld.text((870, 790), "PIER FOUR", font=font("arialbd.ttf", 28), fill=(200, 220, 180, 230))
    ld.text((870, 855), "STATUS: FAIL", font=font("arialbd.ttf", 26), fill=(255, 100, 80, 240))
    img = Image.alpha_composite(img, ledger)

    hand = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hand)
    hx, hy = 500, 520
    hd.ellipse((hx - 30, hy - 20, hx + 50, hy + 25), fill=(195, 165, 135, 230))
    hd.ellipse((hx + 35, hy - 12, hx + 70, hy + 20), fill=(195, 165, 135, 230))
    for fx, fy in [(hx - 15, hy - 18), (hx + 5, hy - 24), (hx + 25, hy - 24), (hx + 45, hy - 18)]:
        hd.ellipse((fx - 8, fy - 40, fx + 8, fy), fill=(195, 165, 135, 230))
    hd.rectangle((hx - 3, hy + 20, hx + 3, hy + 60), fill=(60, 50, 40, 230))
    hd.rectangle((hx + 20, hy + 15, hx + 26, hy + 55), fill=(60, 50, 40, 230))
    img = Image.alpha_composite(img, hand)

    for _ in range(40):
        x = random.randint(200, 1400)
        y = random.randint(300, 1200)
        r = random.randint(1, 3)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(180, 220, 240, random.randint(20, 80)))

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
