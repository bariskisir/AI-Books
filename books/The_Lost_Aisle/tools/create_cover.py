#!/usr/bin/env python3
"""Cover: The Lost Aisle — an academic mystery with hidden library stacks."""

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
    candidates = [
        FONT_DIR / name,
        FONT_DIR / "georgiab.ttf",
        FONT_DIR / "georgia.ttf",
        FONT_DIR / "arialbd.ttf",
        FONT_DIR / "arial.ttf",
    ]
    for c in candidates:
        if c.exists():
            return ImageFont.truetype(str(c), size)
    return ImageFont.load_default()


def wrap(draw, text, fnt, mw):
    words = text.split()
    lines = []
    cur = []
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
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Deep mahogany-to-dark gradient — library atmosphere
    for y in range(H):
        t = y / H
        # Dark mahogany at top, deepening to near-black at bottom
        r = int(80 - 40 * t)
        g = int(30 - 15 * t)
        b = int(15 - 8 * t)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Candlelight glow — warm amber from upper center
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for i in range(5):
        cx = W // 2 + random.randint(-100, 100)
        cy = 400 + random.randint(-80, 80)
        radius = 300 + i * 60
        alpha = 40 - i * 6
        gd.ellipse(
            (cx - radius, cy - radius, cx + radius, cy + radius),
            fill=(240, 200, 120, max(0, alpha)),
        )
    glow = glow.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Bookshelf stacks — tall rectangles with spine lines
    shelf_y_base = 250
    shelf_colors = [
        (140, 60, 30, 200),
        (120, 50, 25, 200),
        (100, 80, 40, 200),
        (150, 70, 35, 200),
        (110, 55, 28, 200),
        (90, 70, 30, 200),
    ]
    # Left side shelves
    for col in range(5):
        sx = 100 + col * 160
        shelf_h = 1300 + random.randint(-200, 100)
        color = shelf_colors[col % len(shelf_colors)]
        draw.rectangle((sx, shelf_y_base, sx + 100, shelf_y_base + shelf_h), fill=color)
        # Spine lines on books
        for bk in range(8):
            by = shelf_y_base + bk * (shelf_h // 8)
            draw.rectangle(
                (sx + 8, by + 4, sx + 92, by + (shelf_h // 8) - 4),
                fill=(
                    max(0, color[0] - 30 + bk * 5),
                    max(0, color[1] - 10 + bk * 3),
                    max(0, color[2] - 5 + bk * 2),
                    color[3],
                ),
            )
        # Book edges (horizontal lines)
        for bk in range(9):
            by = shelf_y_base + bk * (shelf_h // 8)
            draw.line(
                (sx + 8, by, sx + 92, by),
                fill=(200, 160, 80, 60),
                width=1,
            )

    # Right side shelves
    for col in range(5):
        sx = W - 200 - col * 160
        shelf_h = 1200 + random.randint(-150, 150)
        color = shelf_colors[(col + 2) % len(shelf_colors)]
        draw.rectangle((sx, shelf_y_base + 50, sx + 100, shelf_y_base + 50 + shelf_h), fill=color)
        for bk in range(7):
            by = shelf_y_base + 50 + bk * (shelf_h // 7)
            draw.rectangle(
                (sx + 8, by + 4, sx + 92, by + (shelf_h // 7) - 4),
                fill=(
                    max(0, color[0] - 20 + bk * 4),
                    max(0, color[1] - 8 + bk * 2),
                    max(0, color[2] - 3 + bk * 1),
                    color[3],
                ),
            )
        for bk in range(8):
            by = shelf_y_base + 50 + bk * (shelf_h // 7)
            draw.line(
                (sx + 8, by, sx + 92, by),
                fill=(200, 160, 80, 50),
                width=1,
            )

    # Hidden door between shelves — center, slightly ajar, glowing edge
    door_x, door_y = W // 2 - 80, 500
    door_w, door_h = 160, 900
    # Door frame
    draw.rectangle(
        (door_x - 8, door_y - 8, door_x + door_w + 8, door_y + door_h + 8),
        fill=(60, 40, 20, 220),
    )
    # Door itself — dark wood
    draw.rectangle((door_x, door_y, door_x + door_w, door_y + door_h), fill=(45, 30, 15, 240))
    # Door panels
    draw.rectangle(
        (door_x + 15, door_y + 30, door_x + door_w - 15, door_y + door_h // 2 - 20),
        fill=(55, 38, 20, 230),
    )
    draw.rectangle(
        (door_x + 15, door_y + door_h // 2 + 20, door_x + door_w - 15, door_y + door_h - 30),
        fill=(55, 38, 20, 230),
    )
    # Crack of light from slightly open door
    draw.rectangle(
        (door_x + door_w - 4, door_y + 60, door_x + door_w + 6, door_y + door_h - 60),
        fill=(200, 170, 100, 180),
    )
    # Light spill on floor
    spill = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(spill)
    sd.polygon(
        [
            (door_x + door_w - 4, door_y + door_h),
            (door_x + door_w + 260, door_y + door_h + 150),
            (door_x + door_w + 200, door_y + door_h + 200),
            (door_x + door_w - 4, door_y + door_h + 80),
        ],
        fill=(200, 170, 100, 40),
    )
    spill = spill.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, spill)
    draw = ImageDraw.Draw(img, "RGBA")

    # Gold decorative lines on sides
    for side_x in [60, W - 60]:
        draw.line((side_x, 120, side_x, H - 200), fill=(200, 160, 80, 120), width=2)

    # Subtle arch at top
    for i in range(0, W, 4):
        arch_y = 80 + int(40 * math.sin(math.pi * i / W))
        draw.point((i, arch_y), fill=(200, 160, 80, 100))

    # Light rectangle title panel at bottom
    draw.rectangle((0, 1920, W, H), fill=(30, 25, 20, 230))
    # Gold accent lines
    draw.line((200, 1960, W - 200, 1960), fill=(200, 160, 80, 200), width=3)
    draw.line((200, H - 160, W - 200, H - 160), fill=(200, 160, 80, 150), width=2)

    # Subtitle: small text
    sf = font("arial.ttf", 28)
    centered(draw, 1980, ["AN ACADEMIC MYSTERY"], sf, (180, 150, 100), 6)

    # Title
    tf = font("georgiab.ttf", 100)
    title_lines = wrap(draw, title.upper(), tf, 1200)
    y = centered(draw, 2070, title_lines, tf, (220, 185, 130), 10)

    # Author
    y += 50
    af = font("arialbd.ttf", 42)
    centered(draw, y, [author], af, (200, 190, 170), 6)

    # Faint gold sparkles/fireflies
    for _ in range(30):
        sx = int(random.random() * W)
        sy = int(200 + 1600 * random.random())
        sr = int(1 + 3 * random.random())
        sa = int(40 + 60 * random.random())
        draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=(240, 210, 120, sa))

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