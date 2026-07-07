#!/usr/bin/env python3
"""Cover: The Ice Below — Dark ice shelf under starry polar night, blue-green bioluminescent glow bleeding through fissure."""

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


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    candidates = [FONT_DIR / name, FONT_DIR / "georgia.ttf", FONT_DIR / "arial.ttf"]
    for c in candidates:
        if c.exists():
            return ImageFont.truetype(str(c), size)
    return ImageFont.load_default()


def wrap(draw, text, fnt, mw):
    """Wrap text to fit within mw pixels."""
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
    """Draw each line centered horizontally, return final y."""
    for line in lines:
        bb = draw.textbbox((0, 0), line, font=fnt)
        x = (W - (bb[2] - bb[0])) // 2
        draw.text((x, y), line, font=fnt, fill=fill)
        y += bb[3] - bb[1] + gap
    return y


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title, author = m["title"], m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    rng = __import__("random").Random(13)

    # Polar night gradient: black to deep ice blue
    for y in range(H):
        t = y / H
        if t < 0.5:
            r, g, b = 2, 3 + int(10 * (t / 0.5)), 8 + int(30 * (t / 0.5))
        else:
            r, g, b = int(5 - 3 * ((t - 0.5) / 0.5)), int(13 - 10 * ((t - 0.5) / 0.5)), int(38 - 28 * ((t - 0.5) / 0.5))
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Starry polar sky
    for _ in range(250):
        sx = int(rng.random() * W)
        sy = int(rng.random() * 1000)
        sr = 1 + int(2 * rng.random())
        sb = int(180 + 75 * rng.random())
        draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=(sb, sb, sb, int(100 + 155 * rng.random())))

    # Aurora bands
    aurora = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ad = ImageDraw.Draw(aurora)
    for i in range(5):
        base_y = 80 + i * 100
        for j in range(10):
            x_start = int(-200 + i * 60 + rng.gauss(0, 50))
            x_end = int(W + 200 - i * 50 + rng.gauss(0, 50))
            y_center = base_y + int(rng.gauss(0, 35))
            ww = int(60 + rng.gauss(0, 25))
            alpha = 35 - j * 3
            if alpha <= 0: continue
            pts = []
            for s in range(50):
                frac = s / 50
                x = x_start + (x_end - x_start) * frac
                wobble = __import__("math").sin(frac * __import__("math").pi * 3 + i) * 35 + __import__("math").sin(frac * __import__("math").pi * 7 + i * 2) * 12
                y = y_center + wobble
                pts.append((x, y))
            ad.line(pts, fill=(0, 180 - i * 20, 100 + i * 20, alpha), width=ww)
    aurora = aurora.filter(ImageFilter.GaussianBlur(10))
    img = Image.alpha_composite(img, aurora)
    draw = ImageDraw.Draw(img, "RGBA")

    # Ice shelf horizon
    horizon = 1050
    for x in range(0, W, 2):
        off = int(__import__("math").sin(x * 0.02) * 12 + __import__("math").sin(x * 0.07) * 4)
        h = int(50 + __import__("math").sin(x * 0.01) * 25 + off)
        draw.rectangle((x, horizon - h, x + 3, horizon), fill=(180, 205, 225, int(35 + 25 * abs(__import__("math").sin(x * 0.015)))))

    # Main fissure in the ice with bioluminescent glow
    fissure_pts = []
    for x in range(W // 2 - 80, W // 2 + 80, 5):
        fy = horizon + 50 + int(20 * __import__("math").sin(x * 0.1) + 10 * __import__("math").sin(x * 0.25))
        fissure_pts.append((x, fy))
    for i in range(len(fissure_pts) - 1):
        draw.line([fissure_pts[i], fissure_pts[i + 1]], fill=(5, 8, 12, 200), width=6)
        draw.line([fissure_pts[i], fissure_pts[i + 1]], fill=(5, 8, 12, 200), width=10)

    # Bioluminescent glow bleeding from fissure
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gx, gy = W // 2, horizon + 60
    for r in range(120, 0, -5):
        a = int(80 * (1 - r / 120))
        gd.ellipse((gx - r, gy - r // 2, gx + r, gy + r // 2), fill=(0, 200 - int(100 * (1 - r / 120)), 180, a))
    for r in range(60, 0, -3):
        a = int(120 * (1 - r / 60))
        gd.ellipse((gx - r, gy - r // 3, gx + r, gy + r // 3), fill=(100, 255, 220, a))
    glow = glow.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Secondary smaller fissures
    for i in range(6):
        fx = int(W // 2 - 150 + rng.random() * 300)
        fy = int(horizon + 100 + rng.random() * 200)
        fl = int(30 + rng.random() * 80)
        draw.line((fx, fy, fx + int(rng.gauss(0, 30)), fy + int(fl * 0.3)), fill=(100, 140, 180, int(15 + 25 * rng.random())), width=2)

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