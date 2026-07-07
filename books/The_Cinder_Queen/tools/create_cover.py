#!/usr/bin/env python3
"""Cover: The Cinder Queen — Dark fantasy with ash crown and ember glow."""

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

    # Dark gradient: black at top -> crimson -> dark red at bottom
    for y in range(H):
        t = y / H
        if t < 0.4:
            # Black to deep crimson
            r = int(10 + 60 * (t / 0.4))
            g = int(5 + 15 * (t / 0.4))
            b = int(5 + 10 * (t / 0.4))
        elif t < 0.7:
            # Crimson to dark red
            r = int(70 + 80 * ((t - 0.4) / 0.3))
            g = int(20 + 20 * ((t - 0.4) / 0.3))
            b = int(15 + 10 * ((t - 0.4) / 0.3))
        else:
            # Dark red to near-black
            r = int(150 - 120 * ((t - 0.7) / 0.3))
            g = int(40 - 30 * ((t - 0.7) / 0.3))
            b = int(25 - 20 * ((t - 0.7) / 0.3))
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # --- Background: Ruined throne room arch ---
    # Left pillar
    draw.polygon(
        [(80, 400), (180, 400), (200, 2200), (60, 2200)],
        fill=(25, 15, 15, 200),
    )
    # Right pillar
    draw.polygon(
        [(W - 80, 400), (W - 180, 400), (W - 200, 2200), (W - 60, 2200)],
        fill=(25, 15, 15, 200),
    )
    # Arch
    for i in range(20):
        a = math.pi * (0.5 + i / 40)
        x = W // 2 + int(600 * math.cos(a))
        y0 = 400 + int(200 * math.sin(a))
        draw.ellipse((x - 8, y0 - 8, x + 8, y0 + 8), fill=(40 + i * 3, 20 + i * 2, 15, 180))
    # Arch connecting line
    draw.arc(
        [W // 2 - 620, 200, W // 2 + 620, 600],
        start=0, end=180, fill=(50, 25, 20, 180), width=12,
    )

    # Cracked stone floor
    for i in range(12):
        x0 = random.randint(100, W - 100)
        draw.line(
            (x0, 1900 + random.randint(0, 200), x0 + random.randint(-40, 40), 2200),
            fill=(15, 8, 8, 150),
            width=random.randint(2, 5),
        )

    # --- Crown: ash-covered, floating above a throne silhouette ---
    # Throne silhouette (lower center, ruins)
    tx, ty = W // 2, 1550
    draw.polygon(
        [(tx - 120, ty), (tx - 100, ty - 200), (tx - 80, ty - 180),
         (tx - 60, ty - 250), (tx - 40, ty - 230), (tx - 30, ty - 280),
         (tx, ty - 300), (tx + 30, ty - 280), (tx + 40, ty - 230),
         (tx + 60, ty - 250), (tx + 80, ty - 180), (tx + 100, ty - 200),
         (tx + 120, ty)],
        fill=(20, 12, 10, 220),
    )

    # Crown above throne
    crown_cx, crown_cy = W // 2, 1150
    crown_color = (60, 55, 50, 220)  # Ash-gray iron

    # Crown base band
    draw.rectangle(
        (crown_cx - 140, crown_cy + 40, crown_cx + 140, crown_cy + 80),
        fill=crown_color,
    )
    # Crown points (uneven like the description)
    points_heights = [160, 200, 140, 220, 180, 240, 170, 210, 150, 190, 160, 230, 170]
    for i, ph in enumerate(points_heights):
        px = crown_cx - 130 + i * 22
        draw.polygon(
            [(px, crown_cy + 40), (px + 6, crown_cy - ph), (px + 12, crown_cy + 40)],
            fill=(65 + random.randint(-10, 10), 58 + random.randint(-10, 10),
                  50 + random.randint(-10, 10), 230),
        )

    # Ash overlay on crown (darker patches)
    for _ in range(30):
        ax = crown_cx - 130 + random.randint(0, 260)
        ay = crown_cy - 200 + random.randint(0, 240)
        ar = random.randint(2, 8)
        draw.ellipse(
            (ax - ar, ay - ar, ax + ar, ay + ar),
            fill=(30, 25, 22, random.randint(80, 160)),
        )

    # --- Ember glow around crown ---
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    # Large soft glow
    gdraw.ellipse(
        (crown_cx - 300, crown_cy - 300, crown_cx + 300, crown_cy + 300),
        fill=(200, 50, 20, 40),
    )
    gdraw.ellipse(
        (crown_cx - 180, crown_cy - 180, crown_cx + 180, crown_cy + 180),
        fill=(255, 80, 30, 60),
    )
    glow = glow.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Ember particles floating upward
    for _ in range(80):
        ex = crown_cx + random.randint(-200, 200)
        ey = crown_cy - random.randint(100, 600)
        er = random.randint(1, 4)
        eo = random.randint(80, 200)
        draw.ellipse(
            (ex - er, ey - er, ex + er, ey + er),
            fill=(255, random.randint(60, 180), random.randint(10, 60), eo),
        )

    # -- Bottom panel: light title panel --
    panel_y = 1920
    panel_h = H - panel_y
    draw.rectangle((0, panel_y, W, H), fill=(18, 15, 14, 240))

    # Decorative lines
    draw.line((220, panel_y + 30, W - 220, panel_y + 30), fill=(180, 80, 40, 200), width=2)
    draw.line((220, H - 120, W - 220, H - 120), fill=(180, 80, 40, 120), width=2)

    # Title
    tf = font("georgiab.ttf", 100)
    title_lines = wrap(draw, title.upper(), tf, 1100)
    if len(title_lines) > 2:
        tf = font("georgiab.ttf", 80)
        title_lines = wrap(draw, title.upper(), tf, 1100)
    y = centered(draw, panel_y + 80, title_lines, tf, (210, 170, 140), 10)

    # Author
    y += 40
    af = font("arialbd.ttf", 42)
    centered(draw, y, [author], af, (180, 160, 140), 6)

    # Small ember accents at bottom
    for _ in range(20):
        ex = random.randint(100, W - 100)
        ey = H - random.randint(50, 150)
        er = random.randint(1, 3)
        draw.ellipse(
            (ex - er, ey - er, ex + er, ey + er),
            fill=(255, random.randint(40, 120), 10, random.randint(60, 160)),
        )

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