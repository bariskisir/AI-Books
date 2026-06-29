#!/usr/bin/env python3
"""Cover: The Time-Binder's Apprentice — clockwork gears, Edwardian London, timeline threads."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[3]
FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560


def font(name: str, size: int):
    for c in [FONT_DIR / name, FONT_DIR / "georgia.ttf", FONT_DIR / "arial.ttf"]:
        if c.exists():
            try:
                from PIL import ImageFont
                return ImageFont.truetype(str(c), size)
            except Exception:
                pass
    from PIL import ImageFont

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


def wrap(draw, text, fnt, mw):
    words, lines, cur = text.split(), [], []
    for w in words:
        p = " ".join([*cur, w])
        bb = draw.textbbox((0, 0), p, font=fnt)
        if bb[2] <= mw:
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


def draw_gear(draw, cx, cy, inner_r, outer_r, teeth, angle_offset=0, fill=None, outline=None):
    """Draw a gear shape."""
    points = []
    for i in range(teeth * 2):
        a = angle_offset + (math.pi * i) / teeth
        r = outer_r if i % 2 == 0 else inner_r
        x = cx + r * math.cos(a)
        y = cy + r * math.sin(a)
        points.append((x, y))
    if fill:
        draw.polygon(points, fill=fill, outline=outline)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title, author = m["title"], m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Gradient background: deep teal to amber-gold
    for y in range(H):
        t = y / H
        r = int(10 + 220 * max(0, t - 0.3))
        g = int(15 + 180 * max(0, t - 0.3))
        b = int(50 + 100 * max(0, t - 0.3))
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Glowing timeline threads (horizontal flowing lines)
    thread_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(thread_layer)
    for i in range(15):
        y_base = int(100 + 1400 * (i / 15) + random.randint(-30, 30))
        r = random.randint(0, 255)
        g = random.randint(180, 255)
        b = random.randint(50, 200)
        alpha = random.randint(60, 120)
        for x in range(0, W, 4):
            wave = int(8 * math.sin(x / 80 + i * 1.5))
            td.point((x, y_base + wave), fill=(r, g, b, alpha))
    thread_layer = thread_layer.filter(ImageFilter.GaussianBlur(2))
    img = Image.alpha_composite(img, thread_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # Large gear behind (center, semitransparent)
    gear_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gear_layer)
    draw_gear(gd, W // 2, 700, 200, 280, 24, angle_offset=0,
              fill=(200, 150, 60, 60), outline=(220, 180, 80, 100))
    draw_gear(gd, W // 2, 700, 80, 140, 12, angle_offset=0.3,
              fill=(180, 120, 40, 80), outline=(200, 160, 70, 100))
    gear_layer = gear_layer.filter(ImageFilter.GaussianBlur(4))
    img = Image.alpha_composite(img, gear_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # Small gears scattered
    for cx, cy, outer, inner, teeth, off in [
        (300, 500, 60, 40, 8, 0.5),
        (1300, 400, 50, 32, 6, 1.2),
        (250, 1000, 40, 25, 6, 0.8),
        (1350, 950, 55, 35, 8, 0.2),
        (400, 300, 30, 18, 5, 0.9),
        (1200, 600, 45, 28, 6, 1.5),
        (800, 300, 35, 20, 5, 0.4),
    ]:
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gld = ImageDraw.Draw(glow)
        draw_gear(gld, cx, cy, inner, outer, teeth, off,
                  fill=(180, 140, 60, 80), outline=(220, 180, 80, 120))
        glow = glow.filter(ImageFilter.GaussianBlur(3))
        img = Image.alpha_composite(img, glow)

    draw = ImageDraw.Draw(img, "RGBA")
    for cx, cy, outer, inner, teeth, off in [
        (300, 500, 60, 40, 8, 0.5),
        (1300, 400, 50, 32, 6, 1.2),
        (250, 1000, 40, 25, 6, 0.8),
        (1350, 950, 55, 35, 8, 0.2),
        (400, 300, 30, 18, 5, 0.9),
        (1200, 600, 45, 28, 6, 1.5),
        (800, 300, 35, 20, 5, 0.4),
    ]:
        draw_gear(draw, cx, cy, inner, outer, teeth, off,
                  fill=None, outline=(230, 190, 100, 200))

    # Edwardian city silhouette
    silhouette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(silhouette)

    # Buildings
    buildings = [
        (100, 1100, 140, 500),
        (260, 1150, 100, 450),
        (380, 1050, 150, 550),
        (550, 1100, 80, 500),
        (650, 1080, 120, 520),
        (790, 1120, 100, 480),
        (910, 1060, 130, 540),
        (1060, 1100, 90, 500),
        (1170, 1090, 110, 510),
        (1300, 1070, 140, 530),
        (1460, 1110, 80, 490),
    ]
    for bx, by, bw, bh in buildings:
        sd.rectangle((bx, by, bx + bw, by + bh), fill=(15, 12, 10, 220))
        # windows
        wy = by + 30
        while wy < by + bh - 20:
            for wx in range(bx + 15, bx + bw - 15, 25):
                if random.random() > 0.4:
                    alpha = random.randint(80, 200)
                    sd.rectangle((wx, wy, wx + 10, wy + 14), fill=(255, 200, 80, alpha))
            wy += 25

    # Church spire
    spire_x = 750
    sd.polygon([(spire_x, 1060), (spire_x - 50, 1550), (spire_x + 50, 1550)], fill=(15, 12, 10, 220))
    sd.rectangle((spire_x - 80, 1500, spire_x + 80, 1580), fill=(15, 12, 10, 220))

    clock_tower = 1200
    sd.rectangle((clock_tower - 30, 1000, clock_tower + 30, 1600), fill=(15, 12, 10, 220))
    sd.rectangle((clock_tower - 45, 1000, clock_tower + 45, 1050), fill=(15, 12, 10, 220))
    # clock face
    sd.ellipse((clock_tower - 20, 1060, clock_tower + 20, 1100), fill=(200, 160, 60, 180))

    img = Image.alpha_composite(img, silhouette)

    # Glowing light burst from center
    burst = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(burst)
    for i in range(30):
        a = random.uniform(0, 2 * math.pi)
        length = random.randint(400, 800)
        for t_int in range(0, length, 20):
            t = float(t_int)
            x = W // 2 + t * math.cos(a)
            y = 700 + t * math.sin(a)
            if 0 <= x < W and 0 <= y < H:
                alpha = max(0, 60 - t // 15)
                bd.point((x, y), fill=(255, 200, 80, int(alpha)))
    burst = burst.filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(img, burst)
    draw = ImageDraw.Draw(img, "RGBA")

    # Title panel at bottom
    draw.line((220, H - 160, W - 220, H - 160), fill=(220, 180, 100, 120), width=2)

    # Decorative gear icons on title panel sides
    for side_x in [100, W - 100]:
        for r_mult, sz in [(0, 10), (1, 6)]:
            draw_gear(draw, side_x, 2150 + r_mult * 30, sz - 3, sz, 6, angle_offset=r_mult * 0.5,
                      fill=(180, 140, 60, 100), outline=(200, 160, 70, 150))

    ttf = font("georgiab.ttf", 90)
    ttf2 = font("georgia.ttf", 80)
    af = font("arialbd.ttf", 36)

    y = centered(draw, 1980, ["TIME TRAVEL NOVEL"], font("arial.ttf", 28), (200, 160, 100), 6)
    y += 30

    title_text = title.upper()
    title_lines = wrap(draw, title_text, ttf, 1200)
    y = centered(draw, y, title_lines, ttf2, (220, 185, 120), 8)
    y += 40

    centered(draw, y, [author], af, (200, 190, 170), 6)

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