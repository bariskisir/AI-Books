#!/usr/bin/env python3
"""Cover: The Falconer's Knot — Monastery on Tuscan cliff under stormy sky, peregrine falcon circling, dark clouds/stone/candle gold."""

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

    img = Image.new("RGBA", (W, H), (18, 12, 8, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        r = int(32 + (8 - 32) * t)
        g = int(22 + (5 - 22) * t)
        b = int(14 + (3 - 14) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    for _ in range(40):
        x = int(W * random.random())
        y = int(300 * random.random())
        draw.ellipse((x - 60 - int(40 * random.random()), y - 20 - int(30 * random.random()), x + 60 + int(40 * random.random()), y + 20 + int(30 * random.random())), fill=(30, 22, 14, random.randint(30, 90)))

    cliff_pts = [(0, 800)]
    for x in range(0, W + 50, 60):
        h = 600 + random.randint(-80, 120)
        cliff_pts.append((x, h))
    cliff_pts += [(W, 1765), (0, 1765)]
    draw.polygon(cliff_pts, fill=(45, 35, 25, 240))

    arch_cx = W // 2
    arch_by = 750
    aw, ah = 380, 700
    draw.rectangle((arch_cx - aw // 2 - 16, arch_by - ah + aw // 2, arch_cx - aw // 2, arch_by), fill=(50, 38, 26))
    draw.rectangle((arch_cx + aw // 2, arch_by - ah + aw // 2, arch_cx + aw // 2 + 16, arch_by), fill=(50, 38, 26))
    draw.rectangle((arch_cx - aw // 2, arch_by - ah + aw // 2, arch_cx + aw // 2, arch_by), fill=(6, 4, 2))
    draw.ellipse((arch_cx - aw // 2, arch_by - ah, arch_cx + aw // 2, arch_by - ah + aw), fill=(6, 4, 2))
    draw.arc((arch_cx - aw // 2, arch_by - ah, arch_cx + aw // 2, arch_by - ah + aw), 180, 0, fill=(50, 38, 26), width=10)
    draw.line((arch_cx - aw // 2, arch_by - ah + aw // 2, arch_cx - aw // 2, arch_by), fill=(50, 38, 26), width=10)
    draw.line((arch_cx + aw // 2, arch_by - ah + aw // 2, arch_cx + aw // 2, arch_by), fill=(50, 38, 26), width=10)

    for r in range(250, 0, -6):
        alpha = max(0, int(10 * (1 - r / 250)))
        draw.ellipse((arch_cx - r, arch_by - 300 - r // 2, arch_cx + r, arch_by - 300 + r // 2), fill=(220, 160, 80, alpha))

    falcon = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(falcon)
    fx, fy = arch_cx + 60, 200
    s = 2.5
    fd.polygon([(fx, fy - int(10 * s)), (fx + int(6 * s), fy), (fx + int(4 * s), fy + int(22 * s)), (fx + int(10 * s), fy + int(30 * s)), (fx - int(10 * s), fy + int(30 * s)), (fx - int(4 * s), fy + int(22 * s)), (fx - int(6 * s), fy)], fill=(20, 14, 8))
    fd.polygon([(fx - int(6 * s), fy + int(2 * s)), (fx - int(55 * s), fy - int(25 * s)), (fx - int(65 * s), fy - int(20 * s)), (fx - int(45 * s), fy + int(5 * s)), (fx - int(4 * s), fy + int(10 * s))], fill=(20, 14, 8))
    fd.polygon([(fx + int(6 * s), fy + int(2 * s)), (fx + int(55 * s), fy - int(25 * s)), (fx + int(65 * s), fy - int(20 * s)), (fx + int(45 * s), fy + int(5 * s)), (fx + int(4 * s), fy + int(10 * s))], fill=(20, 14, 8))
    img = Image.alpha_composite(img, falcon)

    draw.rectangle((arch_cx - 6, arch_by - ah - 25, arch_cx + 6, arch_by - ah + 15), fill=(60, 48, 32))
    draw.line((arch_cx - 25, arch_by - ah - 2, arch_cx + 25, arch_by - ah - 2), fill=(60, 48, 32), width=7)

    for cx, cy, sc in [(arch_cx - 280, arch_by - 150, 1.6), (arch_cx + 280, arch_by - 150, 1.6)]:
        draw.rectangle((cx - int(3 * sc), cy, cx + int(3 * sc), cy + int(35 * sc)), fill=(210, 195, 160))
        for r in range(int(25 * sc), 0, -3):
            alpha = max(0, int(15 * (1 - r / (25 * sc))))
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(240, 170, 80, alpha))

    for _ in range(60):
        x = random.randint(100, W - 100)
        y = random.randint(80, 650)
        s = random.choice([1, 1, 2, 2, 3])
        draw.ellipse((x, y, x + s, y + s), fill=(220, 190, 130, random.randint(15, 45)))

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
