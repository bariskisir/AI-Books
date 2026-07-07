#!/usr/bin/env python3
"""Cover: The Last Hunt — Elderly Comanche tracker on dun mare facing empty plain at dawn, lone mesa on horizon."""

from __future__ import annotations
import argparse, json, math
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

def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    for c in [FONT_DIR / name, FONT_DIR / "arialbd.ttf", FONT_DIR / "arial.ttf"]:
        if c.exists(): return ImageFont.truetype(str(c), size)
    return ImageFont.load_default()

def wrap(draw, text, fnt, mw):
    words, lines, cur = text.split(), [], []
    for w in words:
        p = " ".join([*cur, w])
        if draw.textbbox((0,0), p, font=fnt)[2] <= mw: cur.append(w)
        else: lines.append(" ".join(cur)); cur = [w]
    if cur: lines.append(" ".join(cur))
    return lines

def centered(draw, y, lines, fnt, fill, gap):
    for line in lines:
        bb = draw.textbbox((0,0), line, font=fnt)
        draw.text(((W-(bb[2]-bb[0]))//2, y), line, font=fnt, fill=fill)
        y += bb[3]-bb[1] + gap
    return y

def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title, author = m["title"], m.get("author", "Barış Kısır")
    model = m.get("model", "")
    img = Image.new("RGBA", (W, H), (0,0,0,255)); draw = ImageDraw.Draw(img, "RGBA")
    rng = __import__("random").Random(17)

    # Dawn gradient: dusty brown to pale gold to dawn pink
    for y in range(H):
        t = y / H
        if t < 0.3:
            r, g, b = 60 + 80 * (t / 0.3), 45 + 60 * (t / 0.3), 30 + 40 * (t / 0.3)
        elif t < 0.5:
            r, g, b = 140 + 60 * ((t - 0.3) / 0.2), 105 + 50 * ((t - 0.3) / 0.2), 70 + 35 * ((t - 0.3) / 0.2)
        elif t < 0.7:
            r, g, b = 200 + 30 * ((t - 0.5) / 0.2), 155 + 25 * ((t - 0.5) / 0.2), 105 + 20 * ((t - 0.5) / 0.2)
        else:
            r, g, b = 230 - 50 * ((t - 0.7) / 0.3), 180 - 40 * ((t - 0.7) / 0.3), 125 - 30 * ((t - 0.7) / 0.3)
        draw.line((0, y, W, y), fill=(max(0, int(r)), max(0, int(g)), max(0, int(b)), 255))

    # Dawn glow on horizon
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    gd.ellipse((W // 2 - 250, 900, W // 2 + 250, 1150), fill=(255, 200, 120, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Lone mesa on horizon
    mesa_w, mesa_h = 300, 250
    mesa_x = W // 2 - mesa_w // 2
    mesa_y = 1000
    draw.polygon([(mesa_x - 30, mesa_y), (mesa_x, mesa_y - mesa_h), (mesa_x + mesa_w, mesa_y - mesa_h), (mesa_x + mesa_w + 30, mesa_y),
                  (mesa_x + mesa_w + 10, mesa_y + 20), (mesa_x - 10, mesa_y + 20)], fill=(35, 28, 22))
    # Flat top
    draw.line((mesa_x, mesa_y - mesa_h, mesa_x + mesa_w, mesa_y - mesa_h), fill=(45, 38, 32), width=4)

    # Empty plain
    draw.rectangle((0, mesa_y + 20, W, 1900), fill=(55, 45, 32, 220))
    draw.rectangle((0, mesa_y + 60, W, 1900), fill=(45, 38, 28, 220))

    # Dun mare
    rx, ry = W // 2 - 100, mesa_y + 60
    # Horse body
    draw.ellipse((rx - 35, ry - 25, rx + 35, ry + 15), fill=(60, 48, 35))
    # Neck
    draw.polygon([(rx - 8, ry - 25), (rx + 8, ry - 25), (rx + 4, ry - 65), (rx - 4, ry - 65)], fill=(60, 48, 35))
    # Head
    draw.ellipse((rx - 7, ry - 75, rx + 7, ry - 58), fill=(60, 48, 35))
    # Legs
    for lx in [rx - 22, rx - 8, rx + 8, rx + 22]:
        draw.rectangle((lx - 3, ry + 12, lx + 3, ry + 40), fill=(55, 43, 30))

    # Elderly Comanche tracker
    # Body
    draw.polygon([(rx - 12, ry - 35), (rx + 12, ry - 35), (rx + 6, ry - 95), (rx - 6, ry - 95)], fill=(20, 18, 15))
    # Head
    draw.ellipse((rx - 8, ry - 108, rx + 8, ry - 92), fill=(35, 30, 25))
    # Hair (long, dark)
    draw.polygon([(rx - 8, ry - 100), (rx - 14, ry - 80), (rx - 8, ry - 90)], fill=(15, 12, 10))
    draw.polygon([(rx + 8, ry - 100), (rx + 14, ry - 80), (rx + 8, ry - 90)], fill=(15, 12, 10))
    # Blanket over shoulders
    draw.polygon([(rx - 18, ry - 40), (rx + 18, ry - 40), (rx + 18, ry - 60), (rx - 18, ry - 60)], fill=(40, 25, 15))

    # Dust haze
    for _ in range(60):
        dx = int(rng.random() * W)
        dy = int(mesa_y + rng.random() * 500)
        dr = int(3 + 8 * rng.random())
        draw.ellipse((dx - dr, dy - dr // 2, dx + dr, dy + dr // 2), fill=(180, 150, 100, rng.randint(10, 30)))

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