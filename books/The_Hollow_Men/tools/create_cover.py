#!/usr/bin/env python3
"""Cover: The Hollow Men — foggy Appalachian forest with shadowy figures."""

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

    # Muted green-gray gradient: dark top to lighter foggy bottom
    for y in range(H):
        t = y / H
        r = int(60 - 20 * t)
        g = int(70 - 15 * t)
        b = int(55 - 10 * t)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Fog layer — lighter mist rising from bottom
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fdraw = ImageDraw.Draw(fog)
    for y in range(H // 2, H):
        t = (y - H // 2) / (H // 2)
        alpha = int(80 * t)
        gray = 140 + int(60 * t)
        fdraw.line((0, y, W, y), fill=(gray, gray, gray, min(alpha, 120)))
    fog = fog.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img, fog)
    draw = ImageDraw.Draw(img, "RGBA")

    # Bare tree trunks on left and right
    tree_color = (25, 20, 18, 200)
    for side, base_x in [("L", 80), ("L", 200), ("L", 350), ("R", 1250), ("R", 1400), ("R", 1520)]:
        trunk_w = 18 + int(math.sin(base_x) * 8)
        trunk_h = 800 + int(math.cos(base_x) * 200)
        top_y = 400 + int(math.sin(base_x * 2) * 100)
        draw.rectangle((base_x, top_y, base_x + trunk_w, top_y + trunk_h), fill=tree_color)
        # Branches
        for b_off in [150, 350, 550]:
            bx = base_x + trunk_w // 2
            by = top_y + b_off
            b_len = 60 + int(math.sin(b_off) * 30)
            draw.line((bx, by, bx - b_len, by - 40), fill=tree_color, width=6)
            draw.line((bx, by, bx + b_len, by - 30), fill=tree_color, width=5)

    # Shadowy figure at center-left
    fig_color = (10, 8, 8, 200)
    fx, fy = 600, 1100
    # Body
    draw.ellipse((fx - 50, fy - 180, fx + 50, fy), fill=fig_color)
    # Head
    draw.ellipse((fx - 25, fy - 230, fx + 25, fy - 180), fill=fig_color)
    # Arms
    draw.line((fx - 50, fy - 140, fx - 100, fy - 80), fill=fig_color, width=14)
    draw.line((fx + 50, fy - 140, fx + 100, fy - 100), fill=fig_color, width=14)

    # Second shadowy figure at right, smaller
    fx2, fy2 = 1200, 1300
    draw.ellipse((fx2 - 35, fy2 - 120, fx2 + 35, fy2), fill=fig_color)
    draw.ellipse((fx2 - 18, fy2 - 155, fx2 + 18, fy2 - 120), fill=fig_color)
    draw.line((fx2 - 35, fy2 - 90, fx2 - 70, fy2 - 50), fill=fig_color, width=10)
    draw.line((fx2 + 35, fy2 - 90, fx2 + 70, fy2 - 60), fill=fig_color, width=10)

    # Empty house silhouette left background
    house_color = (20, 18, 15, 160)
    hx, hy = 250, 950
    draw.polygon([(hx, hy), (hx + 120, hy), (hx + 120, hy + 180), (hx, hy + 180)], fill=house_color)
    draw.polygon([(hx - 10, hy), (hx + 130, hy), (hx + 60, hy - 80)], fill=house_color)
    # Dark window
    draw.rectangle((hx + 30, hy + 30, hx + 60, hy + 70), fill=(5, 5, 5, 180))
    draw.rectangle((hx + 75, hy + 30, hx + 105, hy + 70), fill=(5, 5, 5, 180))
    draw.rectangle((hx + 30, hy + 100, hx + 60, hy + 140), fill=(5, 5, 5, 180))
    draw.rectangle((hx + 75, hy + 100, hx + 105, hy + 140), fill=(5, 5, 5, 180))

    # Faint mist streaks
    for _ in range(25):
        mx = int(W * __import__("random").random())
        my = int(800 + 1200 * __import__("random").random())
        mw2 = int(80 + 160 * __import__("random").random())
        mh2 = int(8 + 16 * __import__("random").random())
        a = int(15 + 25 * __import__("random").random())
        draw.ellipse((mx - mw2 // 2, my - mh2 // 2, mx + mw2 // 2, my + mh2 // 2),
                     fill=(180, 190, 180, a))

    # Title panel
    draw.rectangle((0, 1920, W, 1930), fill=(60, 80, 65, 200))

    # Title
    tf = font("georgiab.ttf", 100)
    af = font("arialbd.ttf", 40)
    sf = font("arial.ttf", 28)

    y = 2010
    y = centered(draw, y, wrap(draw, title.upper(), tf, 1300), tf, (200, 215, 200), 12)
    y += 50
    centered(draw, y, [author], af, (170, 185, 170), 8)

    # Decorative line below author
    draw.line((600, y + 60, W - 600, y + 60), fill=(100, 120, 100, 120), width=1)

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