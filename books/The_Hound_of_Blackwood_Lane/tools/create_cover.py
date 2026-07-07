#!/usr/bin/env python3
"""Cover: The Hound of Blackwood Lane — Misty autumn lane with dark manor silhouette, hound shadow in foreground."""

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
FONTS_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    for c in [FONTS_DIR / name, FONTS_DIR / "georgia.ttf", FONTS_DIR / "arial.ttf"]:
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


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    mp = ROOT / a.metadata if not a.metadata.is_absolute() else a.metadata
    op = ROOT / a.out if not a.out.is_absolute() else a.out

    m = json.loads(mp.read_text(encoding="utf-8"))
    title, author = m["title"], m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Misty autumn gradient: copper/amber sky to fog gray ground
    for y in range(H):
        t = y / H
        if t < 0.4:
            r = int(180 + 40 * (t / 0.4))
            g = int(100 + 30 * (t / 0.4))
            b = int(40 + 20 * (t / 0.4))
        elif t < 0.65:
            r = int(220 - 80 * ((t - 0.4) / 0.25))
            g = int(130 - 50 * ((t - 0.4) / 0.25))
            b = int(60 - 30 * ((t - 0.4) / 0.25))
        else:
            r = int(140 - 100 * ((t - 0.65) / 0.35))
            g = int(80 - 55 * ((t - 0.65) / 0.35))
            b = int(30 - 20 * ((t - 0.65) / 0.35))
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Autumn lane with trees on both sides
    rng = __import__("random").Random(13)
    for side, base_x in [(0, 0), (1, W)]:
        for i in range(10):
            tx = base_x + rng.randint(20, 180) if side == 0 else base_x - rng.randint(20, 180)
            th = int(200 + rng.random() * 300)
            # Trunk
            draw.rectangle((tx - 6, H - th - 200, tx + 6, H - 400), fill=(40, 25, 15, 200))
            # Branches
            for _ in range(4):
                bx = tx + rng.randint(-80, 80)
                by = H - th - 200 + rng.randint(50, th - 100)
                draw.line((tx, by, bx, by - 40), fill=(40, 25, 15, 180), width=4)
            # Autumn leaves (sparse)
            for _ in range(10):
                lx = tx + rng.randint(-60, 60)
                ly = H - th - 200 + rng.randint(30, th - 100)
                draw.ellipse((lx - 8, ly - 8, lx + 8, ly + 8), fill=(180, 80, 30, rng.randint(40, 100)))

    # Dark manor silhouette
    manor_x = W // 2 - 120
    manor_y = int(H * 0.30)
    draw.rectangle((manor_x, manor_y, manor_x + 240, manor_y + 300), fill=(15, 12, 10, 220))
    # Roof
    draw.polygon([(manor_x - 20, manor_y), (manor_x + 120, manor_y - 80), (manor_x + 260, manor_y)], fill=(10, 8, 6, 220))
    # Towers
    for tx in [manor_x - 30, manor_x + 210]:
        draw.rectangle((tx, manor_y - 120, tx + 60, manor_y), fill=(12, 10, 8, 220))
        draw.polygon([(tx - 5, manor_y - 120), (tx + 30, manor_y - 160), (tx + 65, manor_y - 120)], fill=(10, 8, 6, 220))
    # Lit window
    draw.rectangle((manor_x + 100, manor_y + 80, manor_x + 140, manor_y + 120), fill=(180, 160, 80, 100))

    # Hound shadow in foreground
    hx, hy = W // 2, int(H * 0.72)
    # Body
    draw.ellipse((hx - 100, hy - 40, hx + 60, hy + 30), fill=(5, 5, 5, 150))
    # Head
    draw.ellipse((hx + 50, hy - 35, hx + 100, hy + 5), fill=(5, 5, 5, 150))
    # Ears
    draw.polygon([(hx + 60, hy - 35), (hx + 70, hy - 55), (hx + 75, hy - 30)], fill=(5, 5, 5, 140))
    draw.polygon([(hx + 80, hy - 35), (hx + 90, hy - 50), (hx + 95, hy - 30)], fill=(5, 5, 5, 140))
    # Legs
    for lx in [hx - 80, hx - 40, hx, hx + 40]:
        draw.line((lx, hy + 30, lx, hy + 70), fill=(5, 5, 5, 150), width=8)
    # Tail
    draw.line((hx - 100, hy - 10, hx - 140, hy - 50), fill=(5, 5, 5, 140), width=6)

    # Fog layer
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog)
    for _ in range(40):
        fx = int(rng.random() * W)
        fy = int(500 + 1200 * rng.random())
        fw = int(200 + 400 * rng.random())
        fh = int(40 + 80 * rng.random())
        fd.ellipse((fx - fw // 2, fy - fh // 2, fx + fw // 2, fy + fh // 2), fill=(200, 190, 180, 12))
    fog = fog.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, fog)

    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op, "PNG", optimize=True)


if __name__ == "__main__":
    main()
