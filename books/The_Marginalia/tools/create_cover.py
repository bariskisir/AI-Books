#!/usr/bin/env python3
"""Cover: The Marginalia — Weathered manuscript with cryptic marginal notes around illuminated initial, parchment cream/ink black/illumination gold."""

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
    title, author = m["title"], m.get("author", "Barış Kísır")
    model = m.get("model", "")

    # Base: aged parchment gradient
    img = Image.new("RGBA", (W, H), (245, 240, 235, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Parchment aging gradient: top lighter, bottom darker and more brown
    for y in range(H):
        t = y / H
        r = int(245 - 35 * t)
        g = int(240 - 40 * t)
        b = int(235 - 45 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # Paper stains and aging spots
    random.seed(hash((title, author)))
    for _ in range(180):
        sx = int(random.random() * W)
        sy = int(random.random() * H)
        sr = int(30 + random.random() * 80)
        stain_alpha = int(5 + random.random() * 15)
        draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=(120, 90, 60, stain_alpha))

    # Burnt edge effect on left side
    for x in range(0, 80):
        t = x / 80
        alpha = int(30 * t)
        draw.line((x, 0, x, H), fill=(60, 40, 20, alpha))

    # Candlelight glow from upper left
    candle_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cg_draw = ImageDraw.Draw(candle_glow)
    candle_x, candle_y = 200, 300
    for r in range(400, 0, -10):
        alpha = int(8 * (1 - r / 400))
        cg_draw.ellipse(
            (candle_x - r, candle_y - r, candle_x + r, candle_y + r),
            fill=(255, 200, 100, alpha),
        )
    candle_glow = candle_glow.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, candle_glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Medieval border elements: interlocking geometric patterns in corners
    border_color = (139, 69, 19, 80)
    # Top left corner: interlocking circles
    for i in range(5):
        x_offset = 30 + i * 35
        draw.ellipse((x_offset - 15, 20 - 15, x_offset + 15, 20 + 15), outline=border_color, width=2)
        if i > 0:
            draw.line((x_offset - 35, 20, x_offset - 15, 20), fill=border_color, width=2)

    # Top right corner: interlocking circles
    for i in range(5):
        x_offset = W - 30 - i * 35
        draw.ellipse((x_offset - 15, 20 - 15, x_offset + 15, 20 + 15), outline=border_color, width=2)
        if i > 0:
            draw.line((x_offset + 35, 20, x_offset + 15, 20), fill=border_color, width=2)

    # Left side: vertical ornament line
    for i in range(0, H, 60):
        draw.rectangle((40, i, 45, i + 40), fill=border_color)
        draw.ellipse((35, i + 35, 50, i + 50), outline=border_color, width=2)

    # Right side: vertical ornament line
    for i in range(0, H, 60):
        draw.rectangle((W - 45, i, W - 40, i + 40), fill=border_color)
        draw.ellipse((W - 50, i + 35, W - 35, i + 50), outline=border_color, width=2)

    # Quill pen silhouette on right
    quill_x, quill_y = 1350, 1200
    # Feather
    feather_pts = [
        (quill_x - 80, quill_y - 100),
        (quill_x - 20, quill_y - 150),
        (quill_x + 20, quill_y - 100),
        (quill_x + 40, quill_y),
        (quill_x, quill_y + 50),
        (quill_x - 40, quill_y),
    ]
    draw.polygon(feather_pts, fill=(80, 60, 40, 120))
    # Barbs on feather
    for i in range(5):
        t = i / 5
        bx = quill_x - 80 + 160 * t
        by = quill_y - 100 - 50 * math.sin(t * math.pi)
        draw.line((bx, by, bx - 30, by - 20), fill=(100, 80, 60, 100), width=2)

    # Quill shaft
    draw.rectangle((quill_x - 8, quill_y + 50, quill_x + 8, quill_y + 400), fill=(50, 30, 10, 150))
    # Nib
    draw.polygon([(quill_x - 6, quill_y + 400), (quill_x + 6, quill_y + 400), (quill_x + 3, quill_y + 430)], fill=(40, 30, 20, 200))

    # Hidden text suggestion: faint watermark-like text scattered
    hint_font = font("georgia.ttf", 20)
    hint_words = ["sealed", "sleep", "rite", "crypt", "vigil"]
    for _ in range(8):
        word = random.choice(hint_words)
        hx = int(random.random() * (W - 200)) + 100
        hy = int(random.random() * (H - 800)) + 400
        draw.text((hx, hy), word, font=hint_font, fill=(100, 80, 60, 25))

    # Illuminated capital letter style: a large decorated "M" or "A"
    illu_x, illu_y = 150, 600
    illu_font = font("georgiab.ttf", 180)
    illu_text = "M"
    illu_bb = draw.textbbox((0, 0), illu_text, font=illu_font)
    # Gold background for illuminated letter
    gold_pad = 30
    draw.rectangle(
        (illu_x - gold_pad, illu_y - gold_pad, illu_x + (illu_bb[2] - illu_bb[0]) + gold_pad, illu_y + (illu_bb[3] - illu_bb[1]) + gold_pad),
        fill=(200, 150, 50, 100),
        outline=(180, 120, 30, 180),
        width=3
    )
    # Letter with decorative color
    draw.text((illu_x, illu_y), illu_text, font=illu_font, fill=(100, 40, 20, 220))

    # Decorative frame around letter
    frame_x = illu_x - gold_pad - 10
    frame_y = illu_y - gold_pad - 10
    frame_w = (illu_bb[2] - illu_bb[0]) + 2 * (gold_pad + 10)
    frame_h = (illu_bb[3] - illu_bb[1]) + 2 * (gold_pad + 10)
    draw.rectangle((frame_x, frame_y, frame_x + frame_w, frame_y + frame_h), outline=(140, 100, 30, 150), width=2)
    draw.rectangle((frame_x + 5, frame_y + 5, frame_x + frame_w - 5, frame_y + frame_h - 5), outline=(180, 140, 60, 120), width=1)

    # Crypt staircase beneath — descending stone steps
    stair_top = 1450
    stair_color = (90, 80, 70)
    for i in range(12):
        sy = stair_top + i * 35
        sx1 = 350 + i * 25
        sx2 = W - 350 - i * 25
        if sx1 < sx2:
            draw.polygon([
                (sx1, sy), (sx2, sy),
                (sx2 + 30, sy + 35), (sx1 - 30, sy + 35),
            ], fill=(stair_color[0] - i * 3, stair_color[1] - i * 2, stair_color[2] - i * 2))
            draw.line([(sx1, sy), (sx2, sy)], fill=(70, 60, 50), width=2)
    # Stone arch at top of staircase
    arch_cx = W // 2
    arch_y = stair_top - 30
    draw.arc([arch_cx - 200, arch_y - 200, arch_cx + 200, arch_y + 200],
             0, 180, fill=(100, 85, 70, 150), width=6)
    draw.rectangle([arch_cx - 200, arch_y, arch_cx + 200, arch_y + 10],
                    fill=(90, 80, 70, 150))
    # Shadow beneath arch
    draw.polygon([
        (arch_cx - 180, arch_y), (arch_cx + 180, arch_y),
        (arch_cx + 150, stair_top + 20), (arch_cx - 150, stair_top + 20),
    ], fill=(20, 15, 10, 120))
    # Faint light at bottom of stairs
    stair_glow = ImageDraw.Draw(img, "RGBA")
    stair_glow.ellipse([W // 2 - 30, stair_top + 380, W // 2 + 30, stair_top + 440],
                        fill=(200, 180, 120, 30))

    # Title panel at bottom
    # Decorative top border
    # Decorative bottom border
    draw.line((150, H - 100, W - 150, H - 100), fill=(100, 40, 20, 180), width=3)

    # Title text
    tf = font("georgiab.ttf", 110)
    af = font("arialbd.ttf", 42)
    sf = font("arial.ttf", 28)

    y = 2010
    y = centered(draw, y, ["A MEDIEVAL MYSTERY"], sf, (80, 40, 20), 4)
    y += 30
    wrapped_title = wrap(draw, title.upper(), tf, 1200)
    y = centered(draw, y, wrapped_title, tf, (100, 50, 20), 10)
    y += 50
    centered(draw, y, [author], af, (120, 70, 30), 6)

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
