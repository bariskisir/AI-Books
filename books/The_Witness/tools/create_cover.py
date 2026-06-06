#!/usr/bin/env python3
"""Generate a 1600x2560 cover for The Witness."""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH = 1600
HEIGHT = 2560


def _hex(r, g, b):
    return (r, g, b)


def _gradient(draw, w, h, top_color, bottom_color):
    for y in range(h):
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * y / h)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * y / h)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * y / h)
        draw.line([(0, y), (w, y)], fill=(r, g, b))


def _draw_crystalline_pillar(draw, cx, y_base, height, width, colors, seed):
    """Draw a crystalline data pillar at center-x cx, extending upward from y_base."""
    rng = random.Random(seed)
    segments = 6
    seg_h = height / segments

    # Main pillar body
    for i in range(segments):
        seg_y = y_base - (i + 1) * seg_h
        seg_w = width * (1.0 - i * 0.08)
        x0 = cx - seg_w / 2
        x1 = cx + seg_w / 2
        color = colors[i % len(colors)]
        draw.rectangle([x0, seg_y, x1, seg_y + seg_h + 1], fill=color)

    # Glowing core line
    draw.line([(cx, y_base), (cx, y_base - height)], fill=(200, 240, 255, 180), width=3)

    # Facet lines
    for i in range(segments):
        seg_y = y_base - (i + 1) * seg_h
        seg_w = width * (1.0 - i * 0.08)
        x0 = cx - seg_w / 2
        x1 = cx + seg_w / 2
        draw.line([(x0, seg_y), (cx, y_base - (i + 0.5) * seg_h)], fill=(100, 200, 230, 60), width=1)
        draw.line([(x1, seg_y), (cx, y_base - (i + 0.5) * seg_h)], fill=(100, 200, 230, 60), width=1)

    # Top crystal point
    top_y = y_base - height
    point_h = seg_h * 0.8
    draw.polygon([(cx - width * 0.15, top_y), (cx, top_y - point_h), (cx + width * 0.15, top_y)], fill=colors[-1])
    draw.line([(cx, top_y), (cx, top_y - point_h)], fill=(220, 250, 255, 200), width=2)


def _draw_glowing_record(draw, cx, cy, size, angle, color_primary, color_glow):
    """Draw a glowing record disc at the given position."""
    # Outer glow
    for r in range(int(size * 0.7), 0, -1):
        alpha = int(20 * (1 - r / (size * 0.7)))
        draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            outline=(color_glow[0], color_glow[1], color_glow[2], alpha),
            width=1,
        )

    # Main disc
    draw.ellipse(
        [cx - size, cy - size, cx + size, cy + size],
        fill=(color_primary[0], color_primary[1], color_primary[2], 180),
        outline=(180, 230, 255, 200),
        width=2,
    )

    # Inner ring
    inner = int(size * 0.3)
    draw.ellipse(
        [cx - inner, cy - inner, cx + inner, cy + inner],
        outline=(150, 220, 255, 150),
        width=1,
    )

    # Data traces (arcs)
    for i in range(6):
        ang = angle + i * 60
        rad = math.radians(ang)
        x1 = cx + int(size * 0.4 * math.cos(rad))
        y1 = cy + int(size * 0.4 * math.sin(rad))
        x2 = cx + int(size * 0.9 * math.cos(rad))
        y2 = cy + int(size * 0.9 * math.sin(rad))
        draw.line([(x1, y1), (x2, y2)], fill=(100, 200, 255, 120), width=1)

    # Center dot
    draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 255, 255, 200))


def create_cover(metadata_path: str, output_path: str) -> None:
    """Create the cover image."""
    # Load metadata
    meta = {}
    if metadata_path:
        meta = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    title = meta.get("title", "The Witness")
    author = meta.get("author", "Barış Kısır")

    img = Image.new("RGB", (WIDTH, HEIGHT), (10, 14, 28))
    draw = ImageDraw.Draw(img)

    # Deep space gradient background
    _gradient(draw, WIDTH, HEIGHT, (10, 14, 28), (5, 25, 45))

    # Starburst glow behind everything
    for i in range(3):
        cx = WIDTH // 2 + random.randint(-200, 200)
        cy = HEIGHT // 2 - 200 + i * 100
        for r in range(300, 0, -5):
            alpha = max(0, int(8 * (1 - r / 300)))
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(40, 100, 180, alpha))

    # Draw crystalline data pillars (endless library)
    pillar_colors = [
        (20, 60, 100, 180),
        (30, 90, 140, 180),
        (40, 120, 170, 180),
        (30, 100, 150, 200),
        (50, 150, 200, 200),
    ]

    # Background pillars (darker, further away)
    for i in range(15):
        cx = 100 + i * 100 + random.randint(-20, 20)
        y_base = 1600 + random.randint(-100, 100)
        height = 300 + random.randint(100, 400)
        width = 30 + random.randint(10, 30)
        colors = [(c[0] // 2, c[1] // 2, c[2] // 2, 100) for c in pillar_colors]
        _draw_crystalline_pillar(draw, cx, y_base, height, width, colors, i + 100)

    # Foreground pillars (brighter, larger)
    for i in range(8):
        cx = 80 + i * 210 + random.randint(-15, 15)
        y_base = 1500 + random.randint(-50, 50)
        height = 500 + random.randint(100, 300)
        width = 50 + random.randint(10, 30)
        _draw_crystalline_pillar(draw, cx, y_base, height, width, pillar_colors, i)

    # Large central pillar
    _draw_crystalline_pillar(draw, WIDTH // 2, 1550, 700, 70, pillar_colors, 99)

    # Glowing records floating in the scene
    _draw_glowing_record(draw, 650, 1200, 60, 15, (30, 120, 200), (60, 150, 220))
    _draw_glowing_record(draw, 950, 1180, 55, 45, (40, 140, 210), (70, 160, 230))

    # Lone figure (small, comparing records)
    fx, fy = WIDTH // 2, 1480
    # Body
    draw.rectangle([fx - 4, fy - 15, fx + 4, fy + 5], fill=(180, 200, 220, 200))
    # Head
    draw.ellipse([fx - 5, fy - 25, fx + 5, fy - 15], fill=(200, 215, 230, 200))
    # Arms reaching toward records
    draw.line([(fx + 4, fy - 8), (fx + 60, fy - 20)], fill=(180, 200, 220, 180), width=2)
    draw.line([(fx - 4, fy - 8), (fx - 60, fy - 18)], fill=(180, 200, 220, 180), width=2)

    # Light beams from records to figure
    draw.line([(650, 1170), (fx, fy - 20)], fill=(100, 200, 255, 30), width=1)
    draw.line([(950, 1150), (fx, fy - 20)], fill=(100, 200, 255, 30), width=1)

    # Draw standard title panel
    _draw_standard_cover_title_panel(img, title, author)

    img.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")


# ---- Standard helper functions ----


def _standard_cover_font(name, size):
    font_dir = "C:/Windows/Fonts"
    candidates = [
        Path(font_dir) / name,
        Path("C:/Windows/Fonts") / "arialbd.ttf",
        Path("C:/Windows/Fonts") / "arial.ttf",
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def _standard_cover_repair_text(text):
    try:
        return text.encode("latin1").decode("utf-8")
    except UnicodeError:
        return text


def _standard_cover_wrap(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = []
    for word in words:
        proposed = " ".join([*current, word])
        if draw.textbbox((0, 0), proposed, font=font)[2] <= max_width:
            current.append(word)
        else:
            lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def _standard_cover_center(draw, y, lines, font, fill, gap, width):
    for line in lines:
        bb = draw.textbbox((0, 0), line, font=font)
        x = (width - (bb[2] - bb[0])) // 2
        draw.text((x, y), line, font=font, fill=fill)
        y += bb[3] - bb[1] + gap
    return y


def _standard_cover_title_font(draw, title, max_width):
    for size in (116, 104, 96, 88, 80, 72):
        f = _standard_cover_font("arialbd.ttf", size)
        lines = _standard_cover_wrap(draw, title.upper(), f, max_width)
        heights = [
            draw.textbbox((0, 0), l, font=f)[3] - draw.textbbox((0, 0), l, font=f)[1] for l in lines
        ]
        total = sum(heights) + max(0, len(lines) - 1) * 18
        if len(lines) <= 4 and total <= 430:
            return f, lines, 18
    f = _standard_cover_font("arialbd.ttf", 68)
    return f, _standard_cover_wrap(draw, title.upper(), f, max_width), 16


def _standard_cover_resolve_title(local_vars):
    for k in ("title", "ti", "book_title", "TITLE"):
        v = local_vars.get(k)
        if v:
            return v
    import json
    import pathlib

    mp = local_vars.get("args")
    if mp and getattr(mp, "metadata", None):
        try:
            return json.loads(pathlib.Path(mp.metadata).read_text(encoding="utf-8")).get("title", "")
        except Exception:
            pass
    for k in ("output_path", "out_path", "op", "out"):
        v = local_vars.get(k)
        if v:
            return pathlib.Path(v).stem.replace("_", " ").strip()
    return ""


def _standard_cover_resolve_author(local_vars):
    for k in ("author", "au", "AUTHOR"):
        v = local_vars.get(k)
        if v:
            return v
    import json
    import pathlib

    mp = local_vars.get("args")
    if mp and getattr(mp, "metadata", None):
        try:
            return json.loads(pathlib.Path(mp.metadata).read_text(encoding="utf-8")).get("author", "Barış Kısır")
        except Exception:
            pass
    return "Barış Kısır"


def _draw_standard_cover_title_panel(image, title="", author=""):
    W = int(globals().get("WIDTH", 1600))
    H = int(globals().get("HEIGHT", 2560))
    PY = 1765
    title = _standard_cover_repair_text(str(title or "")).strip()
    author = _standard_cover_repair_text(str(author or "Barış Kısır")).strip()
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rectangle((0, PY, W, H), fill=(3, 5, 8, 255))
    draw.line((180, PY + 17, W - 180, PY + 17), fill=(160, 225, 209, 105), width=3)
    tf, lines, tg = _standard_cover_title_font(draw, title, 1260)
    af = _standard_cover_font("arialbd.ttf", 50)
    th = sum(
        draw.textbbox((0, 0), l, font=tf)[3] - draw.textbbox((0, 0), l, font=tf)[1] for l in lines
    ) + max(0, len(lines) - 1) * tg
    ab = draw.textbbox((0, 0), author, font=af)
    ah = ab[3] - ab[1]
    y = PY + 120 + max(0, (H - PY - 210 - (th + 120 + ah)) // 2)
    y = _standard_cover_center(draw, y, lines, tf, (244, 249, 238), tg, W)
    y += 120
    _standard_cover_center(draw, y, [author], af, (210, 229, 221), 12, W)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    create_cover(args.metadata, args.out)


if __name__ == "__main__":
    main()
