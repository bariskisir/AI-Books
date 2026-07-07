#!/usr/bin/env python3
"""Cover: The Glass Shoe — Crystal slipper on black velvet in dim detective's office, rain-streaked window, cold blue/crystal sparkle/amber lamp."""

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

    # Noir detective office gradient: dark blue-black
    for y in range(H):
        t = y / H
        r = int(15 + 10 * t)
        g = int(14 + 12 * t)
        b = int(30 + 20 * t)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Amber desk lamp glow from the right
    lamp_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lamp_glow)
    ld.ellipse((1100, 800, 1500, 1500), fill=(220, 160, 60, 40))
    ld.ellipse((1200, 900, 1400, 1300), fill=(240, 180, 70, 60))
    lamp_glow = lamp_glow.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img, lamp_glow)

    # Rain-streaked window on the left
    win_x, win_y, win_w, win_h = 50, 200, 500, 800
    draw.rectangle((win_x, win_y, win_x + win_w, win_y + win_h), fill=(10, 10, 20, 200), outline=(40, 45, 60, 200), width=6)
    # Window cross
    draw.line((win_x + win_w // 2, win_y, win_x + win_w // 2, win_y + win_h), fill=(40, 45, 60, 180), width=3)
    draw.line((win_x, win_y + win_h // 2, win_x + win_w, win_y + win_h // 2), fill=(40, 45, 60, 180), width=3)
    # City lights through window
    for _ in range(20):
        lx = win_x + random.randint(10, win_w - 10)
        ly = win_y + random.randint(10, win_h - 10)
        lr = random.randint(2, 6)
        draw.ellipse((lx - lr, ly - lr, lx + lr, ly + lr), fill=(200, 180, 100, random.randint(40, 120)))
    # Rain streaks on glass
    for _ in range(30):
        rx = win_x + random.randint(10, win_w - 10)
        ry = win_y + random.randint(10, win_h - 10)
        r_angle = random.uniform(-0.2, 0.2)
        r_len = random.randint(30, 100)
        draw.line((rx, ry, rx + r_angle * r_len, ry + r_len), fill=(150, 160, 180, random.randint(30, 70)), width=1)

    # Crystal slipper on black velvet — center desk
    slipper_x, slipper_y = W // 2 - 30, 1300
    # Black velvet surface
    draw.ellipse((400, 1200, 1200, 1450), fill=(10, 8, 12, 230))
    draw.ellipse((450, 1220, 1150, 1430), fill=(15, 12, 18, 200))

    # Slipper body (pointed toe)
    draw.polygon(
        [
            (slipper_x - 120, slipper_y + 100),
            (slipper_x - 140, slipper_y + 40),
            (slipper_x - 100, slipper_y),
            (slipper_x, slipper_y - 20),
            (slipper_x + 80, slipper_y),
            (slipper_x + 100, slipper_y + 40),
            (slipper_x + 80, slipper_y + 100),
        ],
        fill=(180, 200, 230, 120),
        outline=(200, 215, 240, 200),
        width=3,
    )
    # Heel
    draw.line(
        (slipper_x + 60, slipper_y + 100, slipper_x + 40, slipper_y + 220),
        fill=(200, 215, 240, 200),
        width=8,
    )
    # Sole
    draw.arc(
        (slipper_x - 140, slipper_y + 80, slipper_x + 100, slipper_y + 120),
        0, 180,
        fill=(200, 215, 240, 140),
        width=3,
    )

    # Sparkle highlights on crystal
    for _ in range(30):
        sx = slipper_x + random.randint(-130, 100)
        sy = slipper_y + random.randint(-20, 100)
        sr = random.randint(1, 5)
        alpha = random.randint(100, 230)
        draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=(255, 255, 255, alpha))

    # Desk edge
    draw.line((200, 1500, 1400, 1500), fill=(40, 35, 45, 200), width=6)

    # Title panel at bottom
    draw.line((250, H - 120, W - 250, H - 120), fill=(80, 70, 90, 100), width=1)

    # Genre tag line
    tf_small = font("arial.ttf", 28)
    centered(draw, 1960, ["A FAIRY TALE RETELLING"], tf_small, (100, 95, 110), 4)

    # Title
    tf = font("georgiab.ttf", 100)
    title_lines = wrap(draw, title.upper(), tf, 1300)
    y_title = centered(draw, 2020, title_lines, tf, (30, 25, 35), 8)
    y_title += 20

    # Divider
    draw.line((550, y_title, W - 550, y_title), fill=(80, 70, 90, 120), width=1)
    y_title += 30

    # Author
    af = font("arialbd.ttf", 40)
    centered(draw, y_title, [author], af, (60, 55, 70), 6)

    # Small decorative line near bottom
    draw.line((500, H - 70, W - 500, H - 70), fill=(80, 70, 90, 60), width=1)

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