#!/usr/bin/env python3
"""Cover: The Silk Road Deception — desert caravan silhouettes against amber horizon with ancient ruins."""

from __future__ import annotations
import argparse, json
from pathlib import Path
import random

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


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    for c in [FONT_DIR / name, FONT_DIR / "georgia.ttf", FONT_DIR / "arial.ttf"]:
        if c.exists():
            return ImageFont.truetype(str(c), size)
    return ImageFont.load_default()


def wrap(draw, text, fnt, mw):
    words, lines, cur = text.split(), [], []
    for w in words:
        p = " ".join([*cur, w])
        if draw.textbbox((0, 0), p, font=fnt)[2] <= mw:
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
    title, author = m["title"], m.get("author", "Barış Kısır")
    model = m.get("model", "")
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Desert sky gradient: orange-amber to pale yellow to warm sand
    for y in range(H):
        t = y / H
        if t < 0.25:
            r, g, b = 220, 180, 100
        elif t < 0.50:
            r, g, b = 200, 150, 80
        elif t < 0.70:
            r, g, b = 180, 120, 65
        else:
            r, g, b = 150, 90, 50
        draw.line((0, y, W, y), fill=(int(r * (1 - max(0, y - 1800) / 760)), int(g * (1 - max(0, y - 1800) / 760)), int(b * (1 - max(0, y - 1800) / 760)), 255))

    # Hazy desert sun disc
    sun = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sun)
    sd.ellipse((W // 2 - 200, 350, W // 2 + 200, 750), fill=(255, 200, 120, 160))
    sun = sun.filter(ImageFilter.GaussianBlur(45))
    img = Image.alpha_composite(img, sun)
    draw = ImageDraw.Draw(img, "RGBA")

    # Heat haze near horizon
    haze = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(haze)
    hd.rectangle((0, 1150, W, 1350), fill=(240, 200, 150, 18))
    haze = haze.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, haze)
    draw = ImageDraw.Draw(img, "RGBA")

    # Ancient ruins on the horizon
    # Main gate arch
    draw.arc((600, 1050, 1000, 1450), 180, 0, fill=(130, 90, 55, 200), width=18)
    draw.rectangle((600, 1300, 615, 1500), fill=(130, 90, 55, 200))
    draw.rectangle((985, 1300, 1000, 1500), fill=(130, 90, 55, 200))
    # Side columns
    draw.rectangle((450, 1200, 470, 1500), fill=(120, 85, 50, 200))
    draw.rectangle((1130, 1200, 1150, 1500), fill=(120, 85, 50, 200))
    # Cross beams
    draw.rectangle((440, 1200, 1160, 1220), fill=(140, 100, 60, 200))
    draw.rectangle((440, 1260, 1160, 1280), fill=(140, 100, 60, 200))
    # Weathered texture on ruins
    for _ in range(40):
        rx = random.randint(450, 1150)
        ry = random.randint(1050, 1480)
        draw.rectangle((rx, ry, rx + random.randint(3, 8), ry + random.randint(3, 8)), fill=(100, 70, 40, random.randint(40, 100)))

    # Desert caravan silhouettes
    caravans = [
        (250, 1550, 1.2), (380, 1560, 1.0), (520, 1555, 1.1), (700, 1570, 0.9), (850, 1575, 0.8)
    ]
    for ccx, ccy, scale in caravans:
        w, h = int(30 * scale), int(25 * scale)
        # Body
        draw.ellipse((ccx, ccy - h // 2, ccx + w, ccy + h // 2), fill=(50, 35, 22, 230))
        # Neck / head
        draw.ellipse((ccx + w - 5, ccy - h - 5, ccx + w + 8, ccy - h // 2 + 3), fill=(50, 35, 22, 230))
        # Legs
        draw.line((ccx + 5, ccy + h // 2, ccx + 3, ccy + h // 2 + 18), fill=(50, 35, 22, 230), width=max(2, int(3 * scale)))
        draw.line((ccx + w - 5, ccy + h // 2, ccx + w - 7, ccy + h // 2 + 18), fill=(50, 35, 22, 230), width=max(2, int(3 * scale)))
        # Rider (tiny figure on top)
        draw.ellipse((ccx + w // 2 - 3, ccy - h - 12, ccx + w // 2 + 4, ccy - h - 2), fill=(40, 28, 18, 230))

    # Foreground sand dunes
    for i in range(6):
        dx = random.randint(-100, W - 200)
        dy = 1650 + i * random.randint(20, 50)
        dw = random.randint(300, 700)
        dh = random.randint(60, 120)
        shade = 110 + i * 10
        draw.pieslice((dx, dy, dx + dw, dy + dh * 2), 180, 0, fill=(shade, shade - 15, shade - 30, 220))

    # Dust motes in the air
    for _ in range(100):
        x = random.randint(0, W)
        y = random.randint(500, 1700)
        r = random.randint(1, 4)
        a = random.randint(15, 40)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(200, 180, 140, a))

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