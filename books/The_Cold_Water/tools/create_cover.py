#!/usr/bin/env python3
"""Cover: The Cold Water — Boy on Laundromat steps, bruised purple-green hurricane sky, bent palm, yellow trailer, muted beige/gray/amber."""

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

    img = Image.new("RGBA", (W, H), (98, 88, 72, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        if t < 0.4:
            r = int(70 + 40 * t * 2.5)
            g = int(55 + 30 * t * 2.5)
            b = int(85 + 20 * t * 2.5)
        elif t < 0.7:
            r = int(110 + 20 * (t - 0.4) * 3.3)
            g = int(85 + 30 * (t - 0.4) * 3.3)
            b = int(93 + 10 * (t - 0.4) * 3.3)
        else:
            r = int(130 - 40 * (t - 0.7) * 3.3)
            g = int(115 - 30 * (t - 0.7) * 3.3)
            b = int(103 - 35 * (t - 0.7) * 3.3)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    draw.rectangle((900, 400, 1100, 850), fill=(180, 165, 80, 200))
    draw.line((920, 420, W, 420), fill=(190, 175, 90, 180), width=3)

    draw.rectangle((100, 600, 400, 1300), fill=(140, 128, 108, 220))
    draw.rectangle((100, 600, 400, 620), fill=(160, 148, 128, 240))
    draw.rectangle((100, 1300, 400, 1350), fill=(160, 148, 128, 240))
    draw.rectangle((110, 720, 390, 740), fill=(130, 118, 98, 220))
    draw.rectangle((110, 850, 390, 870), fill=(130, 118, 98, 220))
    draw.rectangle((110, 980, 390, 1000), fill=(130, 118, 98, 220))
    draw.rectangle((110, 1110, 390, 1130), fill=(130, 118, 98, 220))

    palm_x, palm_y = 700, 350
    draw.line((palm_x, palm_y, palm_x, 800), fill=(92, 74, 48, 230), width=10)
    draw.line((palm_x, palm_y, palm_x + 80, 220), fill=(92, 74, 48, 230), width=6)
    draw.line((palm_x, palm_y, palm_x - 60, 250), fill=(92, 74, 48, 230), width=6)
    draw.line((palm_x, palm_y, palm_x + 120, 300), fill=(92, 74, 48, 230), width=5)
    for bx, by in [(palm_x + 80, 220), (palm_x - 60, 250), (palm_x + 120, 300), (palm_x + 40, 200), (palm_x - 30, 210)]:
        draw.ellipse((bx - 30, by - 20, bx + 30, by + 20), fill=(48, 80, 48, 220))

    draw.rectangle((150, 1320, 300, 1540), fill=(168, 155, 130, 230))
    for s in range(5):
        sy = 1340 + s * 40
        draw.line((150, sy, 300, sy), fill=(148, 135, 110, 200), width=3)
    draw.polygon([(140, 1300), (150, 1320), (300, 1320), (310, 1300)], fill=(150, 140, 115, 230))

    cx, cy = 230, 1480
    draw.ellipse((cx - 12, cy - 28, cx + 12, cy + 4), fill=(120, 100, 80, 240))
    draw.rectangle((cx - 12, cy + 2, cx + 12, cy + 40), fill=(100, 82, 62, 240))
    draw.line((cx, cy - 28, cx - 6, cy - 48), fill=(140, 120, 100, 230), width=3)
    draw.line((cx, cy - 28, cx + 6, cy - 48), fill=(140, 120, 100, 230), width=3)
    draw.line((cx - 6, cy - 48, cx + 6, cy - 48), fill=(160, 140, 120, 230), width=3)
    draw.line((cx - 8, cy + 40, cx - 12, cy + 70), fill=(100, 82, 62, 230), width=5)
    draw.line((cx + 8, cy + 40, cx + 12, cy + 70), fill=(100, 82, 62, 230), width=5)

    for _ in range(50):
        x = random.randint(0, W)
        y = random.randint(0, 600)
        r = random.randint(1, 3)
        alpha = random.randint(30, 120)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(180, 170, 150, alpha))

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
