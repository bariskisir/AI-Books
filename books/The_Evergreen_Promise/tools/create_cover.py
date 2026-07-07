#!/usr/bin/env python3
"""Cover: The Evergreen Promise — Snow-covered noble fir rows at dawn, warm-lit farmhouse, Cascade foothills, pine green/snow white/warm amber."""

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

    img = Image.new("RGBA", (W, H), (26, 42, 58, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(900):
        t = y / 900
        r = int(26 + 40 * t)
        g = int(42 + 30 * t)
        b = int(58 + 50 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    mt_pts = [(0, 550), (100, 480), (200, 440), (280, 320), (340, 260), (400, 290),
              (480, 200), (530, 160), (580, 180), (640, 230), (720, 160), (780, 130),
              (840, 180), (920, 240), (1000, 180), (1060, 150), (1120, 200),
              (1200, 280), (1280, 220), (1340, 180), (1400, 240), (1480, 300),
              (1550, 360), (W, 420)]
    draw.polygon(mt_pts + [(W, 900), (0, 900)], fill=(90, 110, 130))
    for x1, y1, x2, y2 in [(480, 200, 560, 240), (720, 160, 800, 200), (1000, 180, 1080, 220), (1340, 180, 1400, 220)]:
        draw.polygon([(x1 - 18, y1 + 28), (x1 + 8, y1 - 8), (x2 - 8, y1 - 8), (x2 + 18, y1 + 28)], fill=(220, 230, 240))

    tree_cols = [(25, 55, 30), (30, 65, 35), (35, 70, 40), (40, 75, 45), (30, 60, 35)]
    for ri, bc in enumerate(tree_cols):
        ry = 500 + ri * 80
        spacing = 70 + (ri % 3) * 10
        off = (ri % 4) * 15
        for col in range(0, W + 40, spacing):
            tx = col + off
            ty = ry
            h = 50 + (ri % 5) * 12
            r1, g1, b1 = bc
            draw.polygon([(tx, ty - h), (tx - 13, ty), (tx + 13, ty)], fill=(r1 + 5, g1 + 5, b1 + 5))
            draw.polygon([(tx, ty - h // 2 - 7), (tx - 9, ty - 7), (tx + 9, ty - 7)], fill=(r1, g1, b1))
            draw.polygon([(tx, ty - h - 2), (tx - 4, ty - h + 7), (tx + 4, ty - h + 7)], fill=(210, 220, 225))

    sg = Image.new("RGBA", (W, 300), (0, 0, 0, 0))
    sgd = ImageDraw.Draw(sg)
    sgd.ellipse((-100, 700, W + 100, 1000), fill=(230, 235, 240, 255))
    img.paste(sg, (0, 500), sg)

    house = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(house)
    hd.rectangle((700, 600, 840, 750), fill=(80, 60, 40, 240))
    hd.polygon([(680, 600), (770, 530), (860, 600)], fill=(100, 30, 30, 240))
    hd.rectangle((750, 650, 790, 720), fill=(60, 50, 40, 240))
    hd.rectangle((710, 630, 740, 670), fill=(180, 160, 80, 200))
    hd.rectangle((800, 630, 830, 670), fill=(180, 160, 80, 200))
    img = Image.alpha_composite(img, house)

    for _ in range(150):
        sx = random.randint(0, W)
        sy = random.randint(0, H // 2 + 200)
        sr = random.randint(1, 3)
        draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=(255, 255, 255, random.randint(100, 200)))

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
