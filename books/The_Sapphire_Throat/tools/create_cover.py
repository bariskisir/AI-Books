#!/usr/bin/env python3
"""Cover: The Sapphire Throat — 1920s speakeasy, jazz silhouette, sapphire necklace."""

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
    for c in [FONT_DIR / name, FONT_DIR / "arial.ttf", FONT_DIR / "georgia.ttf"]:
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

    # Midnight blue to gold gradient
    for y in range(H):
        t = y / H
        if t < 0.5:
            # Deep midnight blue at top
            r = int(10 + 5 * (t * 2))
            g = int(5 + 10 * (t * 2))
            b = int(40 + 15 * (t * 2))
        elif t < 0.75:
            # Transition to gold
            r = int(15 + 60 * ((t - 0.5) * 4))
            g = int(15 + 40 * ((t - 0.5) * 4))
            b = int(55 - 20 * ((t - 0.5) * 4))
        else:
            # Warm gold/brown at bottom
            r = int(75 + 40 * ((t - 0.75) * 4))
            g = int(55 + 30 * ((t - 0.75) * 4))
            b = int(35 - 15 * ((t - 0.75) * 4))
        draw.line((0, y, W, y), fill=(max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), 255))

    # Warm amber glow from stage light (top center)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse((W // 2 - 400, -200, W // 2 + 400, 600), fill=(255, 200, 100, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Light beam from top
    beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(beam)
    bdraw.polygon(
        [(W // 2 - 30, 0), (W // 2 + 30, 0), (W // 2 + 200, 900), (W // 2 - 200, 900)],
        fill=(255, 220, 150, 18),
    )
    beam = beam.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, beam)
    draw = ImageDraw.Draw(img, "RGBA")

    # Speakeasy curtains on sides (velvet red/maroon)
    curtain_color = (80, 15, 20, 220)
    curtain_dark = (50, 8, 12, 230)
    # Left curtain
    for i in range(8):
        cx = i * 25
        cy_top = 0
        cy_bottom = 1900
        curve = int(30 * math.sin(i * 0.5))
        draw.rectangle((cx, cy_top, cx + 25, cy_bottom + curve), fill=curtain_dark if i % 2 == 0 else curtain_color)
        # Curtain fold
        if i < 7:
            draw.line((cx + 25, cy_top, cx + 25, cy_bottom + curve), fill=(100, 25, 30, 200), width=2)
    # Right curtain
    for i in range(8):
        cx = W - (i + 1) * 25
        cy_top = 0
        cy_bottom = 1900
        curve = int(30 * math.sin(i * 0.5 + 1.5))
        draw.rectangle((cx, cy_top, cx + 25, cy_bottom + curve), fill=curtain_dark if i % 2 == 0 else curtain_color)
        if i < 7:
            draw.line((cx, cy_top, cx, cy_bottom + curve), fill=(100, 25, 30, 200), width=2)

    # Curtain top valance
    draw.rectangle((0, 0, W, 80), fill=(60, 10, 15, 240))
    draw.rectangle((0, 75, W, 85), fill=(150, 120, 50, 180), width=2)

    # Jazz singer silhouette (center, backlit)
    # Head
    sx, sy = W // 2, 800
    # Hair / head shape
    draw.ellipse((sx - 35, sy - 55, sx + 35, sy + 5), fill=(8, 5, 10, 220))
    # Neck
    draw.rectangle((sx - 12, sy + 5, sx + 12, sy + 40), fill=(8, 5, 10, 220))
    # Body / dress shape
    body_points = [
        (sx - 25, sy + 40),
        (sx - 80, sy + 220),
        (sx - 60, sy + 350),
        (sx, sy + 380),
        (sx + 60, sy + 350),
        (sx + 80, sy + 220),
        (sx + 25, sy + 40),
    ]
    draw.polygon(body_points, fill=(8, 5, 10, 220))
    # Arm holding microphone (left arm raised)
    draw.line((sx - 25, sy + 60, sx - 70, sy + 10), fill=(8, 5, 10, 220), width=10)
    # Right arm down
    draw.line((sx + 25, sy + 60, sx + 60, sy + 120), fill=(8, 5, 10, 220), width=10)

    # Microphone stand
    draw.line((sx - 70, sy + 10, sx - 70, sy + 200), fill=(180, 160, 120, 200), width=4)
    draw.line((sx - 70, sy + 200, sx - 50, sy + 250), fill=(180, 160, 120, 200), width=3)
    # Mic head
    draw.ellipse((sx - 80, sy - 10, sx - 60, sy + 10), fill=(200, 180, 140, 220))
    draw.ellipse((sx - 78, sy - 8, sx - 62, sy + 8), fill=(220, 200, 160, 150))

    # Sapphire necklace on the silhouette
    # Necklace chain
    draw.arc((sx - 40, sy + 10, sx + 40, sy + 50), 200, 340, fill=(200, 180, 100, 200), width=3)
    # Sapphire gemstones
    gem_positions = [(sx - 30, sy + 25), (sx - 15, sy + 30), (sx, sy + 33), (sx + 15, sy + 30), (sx + 30, sy + 25)]
    for gx, gy in gem_positions:
        draw.ellipse((gx - 4, gy - 4, gx + 4, gy + 4), fill=(60, 100, 255, 230))
        draw.ellipse((gx - 2, gy - 2, gx + 2, gy + 2), fill=(120, 180, 255, 200))

    # Center sapphire (larger, hanging)
    draw.polygon(
        [(sx, sy + 38), (sx - 8, sy + 50), (sx, sy + 65), (sx + 8, sy + 50)],
        fill=(40, 80, 230, 240),
    )
    draw.polygon(
        [(sx, sy + 42), (sx - 4, sy + 50), (sx, sy + 60), (sx + 4, sy + 50)],
        fill=(100, 160, 255, 200),
    )
    # Gemini sparkle on center gem
    draw.line((sx - 2, sy + 48, sx + 2, sy + 55), fill=(200, 220, 255, 180), width=1)

    # Small stage / floor line
    draw.rectangle((100, 1380, W - 100, 1395), fill=(120, 100, 60, 200))
    draw.rectangle((100, 1395, W - 100, 1420), fill=(80, 65, 40, 200))

    # Decorative art deco patterns (period-appropriate)
    deco_color = (200, 180, 120, 80)
    # Left side deco
    for i in range(6):
        yy = 1500 + i * 60
        draw.line((50, yy, 150, yy), fill=deco_color, width=2)
        draw.line((50, yy, 80, yy - 15), fill=deco_color, width=2)
        draw.line((150, yy, 120, yy - 15), fill=deco_color, width=2)
    # Right side deco
    for i in range(6):
        yy = 1500 + i * 60
        draw.line((W - 50, yy, W - 150, yy), fill=deco_color, width=2)
        draw.line((W - 50, yy, W - 80, yy - 15), fill=deco_color, width=2)
        draw.line((W - 150, yy, W - 120, yy - 15), fill=deco_color, width=2)

    # Scattered sparkle/star effects (like light on sapphire)
    for _ in range(30):
        sx2 = random.randint(100, W - 100)
        sy2 = random.randint(100, 1800)
        size = random.randint(1, 3)
        alpha = random.randint(30, 100)
        draw.ellipse(
            (sx2 - size, sy2 - size, sx2 + size, sy2 + size),
            fill=(180, 220, 255, alpha),
        )

    # Title panel at bottom (y=1920-2560)
    # Gold border at top of panel
    draw.rectangle((0, 1918, W, 1925), fill=(180, 160, 80, 220))
    # Bottom gold border
    draw.rectangle((0, H - 10, W, H), fill=(180, 160, 80, 180))

    # Decorative gold lines around title
    draw.line((300, 1975, W - 300, 1975), fill=(180, 160, 80, 60), width=1)

    # Title using arialbd.ttf (WHITE text, NOT georgiab.ttf)
    tf = font("arialbd.ttf", 100)
    af = font("arialbd.ttf", 40)

    y = 2020
    title_lines = wrap(draw, title.upper(), tf, 1300)
    y = centered(draw, y, title_lines, tf, (255, 255, 255), 8)
    y += 50

    # Gold decorative line below title
    draw.line((400, y, W - 400, y), fill=(180, 160, 80, 150), width=1)

    y += 30
    # Author name in white
    centered(draw, y, [author], af, (255, 255, 255), 6)

    # Bottom decorative element - small sapphire gem
    gem_y = 2400
    draw.ellipse((W // 2 - 12, gem_y - 12, W // 2 + 12, gem_y + 12), fill=(40, 60, 180, 200))
    draw.ellipse((W // 2 - 6, gem_y - 6, W // 2 + 6, gem_y + 6), fill=(80, 130, 255, 180))
    draw.ellipse((W // 2 - 3, gem_y - 3, W // 2 + 3, gem_y + 3), fill=(180, 210, 255, 150))

    # Genre line at very bottom
    sf = font("arial.ttf", 22)
    bb = draw.textbbox((0, 0), "A JAZZ AGE CRIME NOVEL", font=sf)
    draw.text(
        ((W - (bb[2] - bb[0])) // 2, 2440),
        "A JAZZ AGE CRIME NOVEL",
        font=sf,
        fill=(180, 160, 80, 180),
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