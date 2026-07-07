#!/usr/bin/env python3
"""Cover: The Crimson Waste — Red sand dunes under copper sun, lone silhouette with sword, crimson glow from below, deep red/amber/charcoal."""

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

    img = Image.new("RGBA", (W, H), (120, 30, 20, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        if t < 0.4:
            r = int(180 + 75 * t * 2.5)
            g = int(15 + 25 * t * 2.5)
            b = int(15 + 10 * t * 2.5)
        elif t < 0.7:
            r = int(255 - 30 * (t - 0.4) * 3.3)
            g = int(40 + 80 * (t - 0.4) * 3.3)
            b = int(20 + 15 * (t - 0.4) * 3.3)
        else:
            r = int(220 - 60 * (t - 0.7) * 3.3)
            g = int(120 - 40 * (t - 0.7) * 3.3)
            b = int(35 - 10 * (t - 0.7) * 3.3)
        draw.line((0, y, W, y), fill=(min(255, r), min(255, g), min(255, b), 255))

    sun_cx, sun_cy = 600, 250
    for r in range(250, 40, -10):
        alpha = max(5, 180 - r)
        draw.ellipse((sun_cx - r, sun_cy - r, sun_cx + r, sun_cy + r), fill=(200, 60, 30, alpha))
    draw.ellipse((sun_cx - 70, sun_cy - 70, sun_cx + 70, sun_cy + 70), fill=(255, 120, 50, 220))
    draw.ellipse((sun_cx - 50, sun_cy - 50, sun_cx + 50, sun_cy + 50), fill=(255, 180, 80, 240))

    for base_y, col in [(1400, (120, 35, 25, 200)), (1550, (140, 45, 30, 180)), (1700, (160, 55, 35, 160))]:
        pts = [(0, base_y)]
        for x in range(0, W + 50, 50):
            pts.append((x, base_y + math.sin(x / 200 + base_y / 100) * 40 + math.sin(x / 80) * 15))
        pts.extend([(W, H), (0, H)])
        draw.polygon(pts, fill=col)

    silh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(silh)
    scx, scy = 800, 900
    sd.ellipse((scx - 14, scy - 50, scx + 14, scy - 10), fill=(10, 8, 5, 230))
    sd.rectangle((scx - 8, scy - 10, scx + 8, scy + 60), fill=(10, 8, 5, 230))
    sd.polygon([(scx - 5, scy - 200), (scx - 2, scy - 40), (scx + 2, scy - 40), (scx + 5, scy - 200)], fill=(10, 8, 5, 230))
    sd.polygon([(scx - 30, scy - 50), (scx - 8, scy - 20), (scx - 8, scy + 10)], fill=(10, 8, 5, 230))
    sd.polygon([(scx + 8, scy - 20), (scx + 30, scy - 50), (scx + 8, scy + 10)], fill=(10, 8, 5, 230))
    sd.rectangle((scx - 30, scy - 55, scx + 30, scy - 45), fill=(10, 8, 5, 230))
    sd.rectangle((scx - 4, scy + 60, scx + 4, scy + 100), fill=(10, 8, 5, 230))
    sd.ellipse((scx - 7, scy + 95, scx + 7, scy + 110), fill=(10, 8, 5, 230))
    img = Image.alpha_composite(img, silh)

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((scy + 40, 1450, scy + 120, 1550), fill=(200, 30, 20, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, glow)

    for _ in range(150):
        x = random.randint(0, W)
        y = random.randint(900, 1900)
        s = random.randint(2, 6)
        alpha = random.randint(20, 60)
        draw.ellipse((x, y, x + s, y + s), fill=(120, 35, 25, alpha))

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
