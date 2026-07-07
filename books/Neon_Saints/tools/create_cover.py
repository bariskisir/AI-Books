#!/usr/bin/env python3
"""Cover: Neon Saints — a cyberpunk city at night with neon and rain."""

from __future__ import annotations
import argparse, json
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

    # Night sky gradient: dark blue to deep purple to black
    for y in range(H):
        t = y / H
        if t < 0.4:
            r = int(8 + 5 * t * 2.5)
            g = int(5 + 10 * t * 2.5)
            b = int(25 + 20 * t * 2.5)
        elif t < 0.7:
            r = int(13 + 20 * (t - 0.4) * 3.3)
            g = int(15 + 5 * (t - 0.4) * 3.3)
            b = int(45 - 15 * (t - 0.4) * 3.3)
        else:
            r = int(33 - 25 * (t - 0.7) * 3.3)
            g = int(20 - 15 * (t - 0.7) * 3.3)
            b = int(30 - 25 * (t - 0.7) * 3.3)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # City skyline silhouette
    buildings = [
        (80, 800, 130, 1400),
        (160, 700, 200, 1400),
        (220, 900, 260, 1400),
        (300, 600, 150, 1400),
        (390, 750, 180, 1400),
        (480, 850, 120, 1400),
        (540, 650, 220, 1400),
        (650, 550, 160, 1400),
        (730, 700, 140, 1400),
        (800, 800, 180, 1400),
        (880, 600, 200, 1400),
        (970, 750, 130, 1400),
        (1030, 650, 170, 1400),
        (1110, 550, 150, 1400),
        (1180, 700, 190, 1400),
        (1270, 800, 120, 1400),
        (1330, 650, 160, 1400),
        (1400, 750, 180, 1400),
        (1480, 850, 130, 1400),
    ]
    for bx, bh, bw, by2 in buildings:
        draw.rectangle((bx, bh, bx + bw, by2), fill=(10, 8, 15, 220))

    # Spire (tallest building)
    spire_x = W // 2
    draw.polygon(
        [
            (spire_x - 40, 1400),
            (spire_x - 40, 450),
            (spire_x - 20, 300),
            (spire_x, 250),
            (spire_x + 20, 300),
            (spire_x + 40, 450),
            (spire_x + 40, 1400),
        ],
        fill=(8, 6, 12, 240),
    )
    # Spire tip glow
    draw.ellipse((spire_x - 15, 220, spire_x + 15, 260), fill=(0, 255, 255, 80))

    # Neon window lights on buildings
    for _ in range(120):
        import random

        bx = random.randint(20, W - 20)
        by = random.randint(500, 1350)
        color = random.choice(
            [
                (0, 255, 255, random.randint(40, 150)),
                (255, 0, 255, random.randint(40, 150)),
                (255, 100, 0, random.randint(30, 100)),
                (0, 200, 255, random.randint(30, 120)),
            ]
        )
        draw.rectangle((bx, by, bx + random.randint(4, 10), by + random.randint(4, 10)), fill=color)

    # Rain streaks (diagonal)
    for _ in range(200):
        import random

        rx = random.randint(0, W)
        ry = random.randint(0, min(1900, int(H * 0.75)))
        rlen = random.randint(20, 80)
        ralpha = random.randint(10, 40)
        draw.line(
            (rx, ry, rx - int(rlen * 0.3), ry + rlen),
            fill=(150, 180, 255, ralpha),
            width=1,
        )

    # Ground reflection / rain-slicked street
    for y in range(1420, 1500):
        t = (y - 1420) / 80
        r = int(5 + 15 * t)
        g = int(4 + 10 * t)
        b = int(12 + 20 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 200))

    # Cyan ground line glow
    draw.line((0, 1420, W, 1420), fill=(0, 255, 255, 60), width=2)

    # Holographic figure representation
    holox = W // 2 - 100
    # Body outline (glowing cyan)
    body_points = [
        (holox, 950),
        (holox - 20, 1050),
        (holox - 30, 1150),
        (holox, 1180),
        (holox + 30, 1150),
        (holox + 20, 1050),
        (holox, 950),
    ]
    draw.polygon(body_points, fill=None, outline=(0, 255, 255, 120), width=3)
    # Head
    draw.ellipse((holox - 20, 900, holox + 20, 945), fill=None, outline=(255, 0, 255, 150), width=3)
    # Arms
    draw.line((holox - 30, 1150, holox - 60, 1250), fill=(255, 0, 255, 100), width=3)
    draw.line((holox + 30, 1150, holox + 60, 1250), fill=(255, 0, 255, 100), width=3)
    # Legs
    draw.line((holox - 10, 1180, holox - 20, 1350), fill=(0, 255, 255, 100), width=3)
    draw.line((holox + 10, 1180, holox + 20, 1350), fill=(0, 255, 255, 100), width=3)
    # Holographic noise lines
    for _ in range(15):
        import random

        nx = holox + random.randint(-50, 50)
        ny = 900 + random.randint(0, 400)
        draw.line(
            (nx, ny, nx + random.randint(-10, 10), ny + random.randint(5, 15)),
            fill=(0, 255, 255, random.randint(20, 50)),
            width=1,
        )

    # Neon signs / holographic billboards
    sign_texts = ["NEON", "NULL", "DREAM"]
    for i, st in enumerate(sign_texts):
        sf = font("arialbd.ttf", 40)
        sx = 200 + i * 500
        sy = 700 + (i % 2) * 100
        col = (255, 0, 255, 60) if i % 2 == 0 else (0, 255, 255, 50)
        sbb = draw.textbbox((0, 0), st, font=sf)
        draw.rectangle(
            (sx - 10, sy - 5, sx + (sbb[2] - sbb[0]) + 10, sy + (sbb[3] - sbb[1]) + 5),
            fill=(0, 0, 0, 120),
        )
        draw.text((sx, sy), st, font=sf, fill=col)

    # Title panel at the bottom
    draw.line((150, H - 120, W - 150, H - 120), fill=(0, 255, 255, 80), width=2)

    # Title
    tf = font("georgiab.ttf", 110)
    title_lines = wrap(draw, title.upper(), tf, 1200)
    af = font("arialbd.ttf", 44)

    y = centered(draw, 2020, ["A CYBERPUNK NOVEL"], font("arial.ttf", 28), (180, 180, 220), 4)
    y += 50
    y = centered(draw, y, title_lines, tf, (0, 255, 255), 10)
    y += 50
    centered(draw, y, [author], af, (255, 200, 200), 6)

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