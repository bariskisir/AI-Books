#!/usr/bin/env python3
"""Cover: The Quiet Room — woman alone in small padded room with gray fabric walls, bolted chair with restraints, fingernail scratches."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560


def font_name(n, s):
    for c in [FONT_DIR / n, FONT_DIR / "georgia.ttf", FONT_DIR / "arial.ttf"]:
        if c.exists():
            return ImageFont.truetype(str(c), s)
    return ImageFont.load_default()


def wrap(d, t, f, mw):
    words, lines, cur = t.split(), [], []
    for w in words:
        p = " ".join([*cur, w])
        if d.textbbox((0, 0), p, font=f)[2] <= mw:
            cur.append(w)
        else:
            lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def centered(d, y, lines, f, fill, gap):
    for line in lines:
        bb = d.textbbox((0, 0), line, font=f)
        d.text(((W - (bb[2] - bb[0])) // 2, y), line, font=f, fill=fill)
        y += bb[3] - bb[1] + gap
    return y


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Gray padded room - fabric walls
    for y in range(H):
        t = y / H
        g = int(65 + 15 * (1 - abs(t - 0.5) * 2))
        draw.line((0, y, W, y), fill=(g - 5, g, g + 5, 255))

    # Fabric wall texture (vertical seams)
    for x in range(0, W, 80):
        draw.line((x, 0, x, 1800), fill=(55, 58, 62, 80), width=2)

    # Padded wall - diamond pattern
    for x in range(0, W, 60):
        for y in range(0, 1800, 60):
            draw.rectangle((x, y, x + 56, y + 56), fill=(58, 62, 66, 100), outline=(48, 52, 56, 150), width=1)
            draw.ellipse((x + 24, y + 24, x + 32, y + 32), fill=(52, 56, 60, 150))

    # Bolted chair center
    cx, cy = W // 2, 1050
    # Chair legs bolted to floor
    draw.rectangle((cx - 70, cy + 80, cx - 60, cy + 120), fill=(40, 40, 42, 255))
    draw.rectangle((cx + 60, cy + 80, cx + 70, cy + 120), fill=(40, 40, 42, 255))
    draw.rectangle((cx - 60, cy + 80, cx - 50, cy + 115), fill=(60, 60, 62, 255))
    draw.rectangle((cx + 50, cy + 80, cx + 60, cy + 115), fill=(60, 60, 62, 255))
    # Bolts
    for bx in [cx - 65, cx + 65]:
        draw.ellipse((bx - 5, cy + 115, bx + 5, cy + 125), fill=(80, 80, 82, 255))
    # Seat
    draw.rectangle((cx - 80, cy + 50, cx + 80, cy + 85), fill=(38, 38, 40, 255))
    # Backrest
    draw.rectangle((cx - 70, cy - 80, cx - 10, cy + 50), fill=(38, 38, 40, 255))
    draw.rectangle((cx + 10, cy - 80, cx + 70, cy + 50), fill=(38, 38, 40, 255))
    draw.rectangle((cx - 75, cy - 85, cx + 75, cy - 70), fill=(42, 42, 44, 255))
    # Restraints on arms
    draw.rectangle((cx - 85, cy + 10, cx - 70, cy + 25), fill=(50, 48, 46, 255))
    draw.rectangle((cx + 70, cy + 10, cx + 85, cy + 25), fill=(50, 48, 46, 255))

    # Woman silhouette sitting in chair
    wx, wy = cx, cy - 30
    # Head
    draw.ellipse((wx - 16, wy - 40, wx + 16, wy - 10), fill=(20, 20, 22, 230))
    # Body slumped
    draw.polygon([(wx - 20, wy - 10), (wx + 20, wy - 10), (wx + 25, wy + 60), (wx - 25, wy + 60)], fill=(22, 22, 24, 230))

    # Fingernail scratches on wall
    for _ in range(30):
        sx = random.randint(100, W - 100)
        sy = random.randint(200, 1500)
        draw.line((sx, sy, sx + random.randint(-8, 8), sy + random.randint(10, 30)), fill=(70, 72, 76, random.randint(80, 150)), width=1)

    # Harsh overhead light cone
    cone = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cone)
    for _ in range(40):
        cd.line((cx + random.randint(-20, 20), 0, cx + random.randint(-150, 150), cy + random.randint(-50, 50)), fill=(200, 210, 220, random.randint(3, 10)), width=random.randint(8, 25))
    cone = cone.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(img, cone)

    _draw_standard_cover_title_panel(img, title=title, author=author, model=model)
    img.save(op, "PNG")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    make_cover(a.metadata, a.out)


if __name__ == "__main__":
    main()