#!/usr/bin/env python3
"""Cover: The Coral Clock — Deep blue-green underwater, coral-encrusted chronometer at 2:38, reef surveillance, coral pink/teal/abyssal blue."""

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

    img = Image.new("RGBA", (W, H), (8, 45, 62, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        r = int(13 + (5 - 13) * t)
        g = int(92 + (35 - 92) * t)
        b = int(118 + (58 - 118) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    light = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(light)
    for x in [200, 550, 980, 1340]:
        ld.polygon([(x, 0), (x + 110, 0), (x - 160, 1765), (x - 380, 1765)], fill=(170, 224, 216, 22))
    light = light.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, light)
    draw = ImageDraw.Draw(img, "RGBA")

    draw.rectangle((0, 1300, W, 1765), fill=(16, 60, 66, 230))
    for x in range(-40, W, 90):
        h = random.randint(60, 200)
        col = random.choice([(42, 122, 108, 235), (78, 67, 105, 235), (166, 92, 84, 230), (205, 139, 92, 230)])
        draw.ellipse((x, 1350 - h, x + 140, 1450 + h // 5), fill=col)

    cx, cy = 800, 1000
    draw.ellipse((cx - 220, cy - 220, cx + 220, cy + 220), fill=(120, 85, 40, 245), outline=(220, 178, 95, 230), width=14)
    draw.ellipse((cx - 170, cy - 170, cx + 170, cy + 170), fill=(210, 198, 164, 235), outline=(80, 62, 42, 180), width=7)
    for i in range(12):
        ang = math.radians(i * 30 - 90)
        x1 = cx + math.cos(ang) * 130
        y1 = cy + math.sin(ang) * 130
        x2 = cx + math.cos(ang) * 150
        y2 = cy + math.sin(ang) * 150
        draw.line((x1, y1, x2, y2), fill=(65, 56, 44, 180), width=4)
    draw.line((cx, cy, cx + 65, cy - 28), fill=(50, 44, 36, 235), width=7)
    draw.line((cx, cy, cx - 35, cy - 110), fill=(50, 44, 36, 235), width=7)
    draw.ellipse((cx - 14, cy - 14, cx + 14, cy + 14), fill=(50, 44, 36, 235))
    draw.text((cx - 85, cy + 65), "2:38", font=font("georgia.ttf", 44), fill=(78, 60, 38, 210))

    for _ in range(80):
        ang = random.random() * math.tau
        rad = random.randint(190, 290)
        x = cx + math.cos(ang) * rad
        y = cy + math.sin(ang) * rad
        col = random.choice([(216, 114, 94, 210), (235, 178, 112, 210), (93, 151, 126, 210)])
        draw.ellipse((x - 16, y - 10, x + 16, y + 10), fill=col)

    for _ in range(50):
        x = random.randint(60, 1500)
        y = random.randint(350, 1500)
        s = random.randint(7, 20)
        draw.polygon([(x, y), (x + s * 2, y - s), (x + s * 2, y + s)], fill=(160, 200, 190, random.randint(70, 140)))
    for _ in range(80):
        x = random.randint(50, 1550)
        y = random.randint(100, 1550)
        s = random.randint(3, 9)
        draw.ellipse((x, y, x + s, y + s), outline=(200, 230, 220, random.randint(60, 130)), width=2)

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
