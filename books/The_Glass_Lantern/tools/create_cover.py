#!/usr/bin/env python3
"""Generate a project-local raster cover for The Glass Lantern."""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH = 1600
HEIGHT = 2560
TITLE = "The Glass Lantern"
PALETTE = [tuple(c) for c in [[12, 10, 18], [28, 22, 42], [82, 52, 28], [212, 168, 68]]]
SEED = 1925


def _gradient(draw, top, bottom):
    for y in range(HEIGHT):
        t = y / max(1, HEIGHT - 1)
        draw.line((0, y, WIDTH, y), fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))


def _label(draw, text, cx, y, size, fill):
    font = _standard_cover_font("arialbd.ttf", size)
    box = draw.textbbox((0, 0), text, font=font)
    draw.text((cx - (box[2] - box[0]) // 2, y), text, font=font, fill=fill)


def _draw_glow(draw, cx, cy, radius, color, alpha):
    """Draw a radial glow gradient."""
    for r in range(radius, 0, -4):
        a = int(alpha * (r / radius))
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(*color[:3], a))


def _draw_scene(draw, image):
    rng = random.Random(SEED)

    # Night sky gradient — deep indigo to warm horizon
    _gradient(draw, (8, 6, 18), (32, 24, 48))
    # Warm horizon glow
    for y in range(600, 1300, 3):
        t = (y - 600) / 700.0
        alpha = int(40 * (1 - t))
        if alpha > 0:
            draw.line((0, y, WIDTH, y), fill=(212, 168, 68, alpha), width=3)

    # Stars
    for _ in range(120):
        x = rng.randint(80, 1520)
        y = rng.randint(80, 900)
        sz = rng.randint(1, 4)
        bright = rng.randint(90, 220)
        draw.ellipse((x - sz, y - sz, x + sz, y + sz), fill=(255, 242, 200, bright))

    # Crescent moon
    draw.ellipse((1180, 120, 1400, 340), fill=(255, 248, 220, 210))
    draw.ellipse((1220, 100, 1430, 360), fill=(12, 10, 30, 240))

    # Istanbul skyline silhouettes — minarets and domes
    skyline_color = (10, 8, 16, 240)
    # Ground base
    draw.rectangle((0, 1120, WIDTH, 1280), fill=skyline_color)

    # Mosque domes
    for cx, r in [(200, 80), (500, 110), (850, 95), (1200, 85), (1450, 70)]:
        draw.ellipse((cx - r, 1120 - r * 2, cx + r, 1120), fill=skyline_color)
    # Minarets
    for x, h in [(120, 380), (290, 420), (420, 350), (590, 450), (750, 390), (960, 440), (1100, 370), (1300, 400), (1400, 340), (1520, 380)]:
        draw.rectangle((x - 6, 1120 - h, x + 6, 1120), fill=skyline_color)
        # Balcony
        draw.rectangle((x - 14, 1120 - h + 80, x + 14, 1120 - h + 86), fill=skyline_color)
        # Spire
        draw.polygon([(x, 1120 - h - 30), (x - 4, 1120 - h), (x + 4, 1120 - h)], fill=skyline_color)

    # Golden Horn water reflection
    for y in range(1280, 1500, 2):
        alpha = int(50 * (1 - (y - 1280) / 220.0))
        if alpha > 0:
            draw.line((0, y, WIDTH, y), fill=(160, 120, 40, alpha), width=2)

    # Glass lantern hanging in the center — the focal point
    lx, ly = 800, 650
    # Chain
    for cy in range(100, ly - 110, 6):
        draw.ellipse((lx - 3, cy, lx + 3, cy + 8), fill=(180, 150, 80, 200))
    # Chain glow
    _draw_glow(draw, lx, ly, 320, (212, 168, 68), 100)

    # Lantern body — bell shape
    lantern_top = ly - 100
    lantern_bot = ly + 120
    lantern_wide = 90
    draw.ellipse((lx - 50, lantern_top - 30, lx + 50, lantern_top + 20), fill=(80, 55, 30, 220))
    # Main glass body
    glass_color = (180, 145, 60, 200)
    draw.polygon([
        (lx - 70, lantern_top),
        (lx - lantern_wide, lantern_bot - 20),
        (lx - lantern_wide + 10, lantern_bot),
        (lx + lantern_wide - 10, lantern_bot),
        (lx + lantern_wide, lantern_bot - 20),
        (lx + 70, lantern_top),
    ], fill=(200, 170, 80, 160), outline=(220, 190, 120, 200))

    # Internal glow
    for i in range(8):
        gr = 130 + i * 5
        alpha = 180 - i * 18
        draw.ellipse((lx - gr, ly - gr + 10, lx + gr, ly + gr - 10), fill=(255, 220, 120, max(alpha, 15)))

    # Flame
    _draw_glow(draw, lx, ly + 10, 50, (255, 200, 60), 220)
    draw.ellipse((lx - 16, ly - 5, lx + 16, ly + 25), fill=(255, 230, 130, 180))
    draw.ellipse((lx - 8, ly + 2, lx + 8, ly + 20), fill=(255, 250, 200, 200))

    # Glass panels — vertical lines suggesting the lantern structure
    for i in range(-2, 3):
        dx = i * 28
        draw.line((lx + dx, lantern_top + 10, lx + dx, lantern_bot - 10), fill=(140, 110, 50, 100), width=2)

    # Light rays from lantern
    for angle in range(0, 360, 18):
        rad = math.radians(angle)
        for d in range(60, 400, 40):
            alpha = int(25 * (1 - d / 400))
            sx = lx + math.cos(rad) * d
            sy = ly + math.sin(rad) * d * 0.6
            draw.ellipse((sx - 1, sy - 1, sx + 1, sy + 1), fill=(255, 210, 100, max(alpha, 0)))

    # Bosphorus boats — small dhow silhouettes on the water
    for bx in [250, 620, 1050, 1380]:
        draw.polygon([(bx - 20, 1350), (bx + 20, 1350), (bx + 12, 1370), (bx - 12, 1370)], fill=(8, 6, 12, 200))
        draw.polygon([(bx, 1330), (bx + 4, 1350), (bx, 1350)], fill=(8, 6, 12, 180))

    # Location label
    _label(draw, "ISTANBUL", 800, 1520, 42, (200, 170, 100, 170))

    # Divider above title panel
    draw.rectangle((0, 1600, WIDTH, 1765), fill=(8, 6, 12, 80))


def create_cover(metadata_path, out_path):
    metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    title = metadata.get("title", TITLE)
    author = metadata.get("author", "Barış Kısır")
    image = Image.new("RGB", (WIDTH, HEIGHT), PALETTE[0])
    draw = ImageDraw.Draw(image, "RGBA")
    _draw_scene(draw, image)
    _draw_standard_cover_title_panel(image, title, author, metadata.get("model", ""))
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    image.save(out_path)


def _standard_cover_font(name, size):
    candidates = [name, "arial.ttf", "Arial.ttf", "DejaVuSans.ttf"]
    if "bd" in name.lower() or "bold" in name.lower():
        candidates = [name, "arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans.ttf"]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _standard_cover_repair_text(text):
    try:
        return text.encode("latin1").decode("utf-8")
    except Exception:
        return text


def _standard_cover_wrap(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = []
    for word in words:
        trial = " ".join(current + [word])
        box = draw.textbbox((0, 0), trial, font=font)
        if current and box[2] - box[0] > max_width:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return lines or [text]


def _standard_cover_center(draw, y, lines, font, fill, gap, width):
    for line in lines:
        box = draw.textbbox((0, 0), line, font=font)
        draw.text(((width - (box[2] - box[0])) // 2, y), line, font=font, fill=fill)
        y += box[3] - box[1] + gap
    return y


def _standard_cover_title_font(draw, title, max_width):
    for size in (116, 104, 96, 88, 80, 72, 66, 60):
        font = _standard_cover_font("arialbd.ttf", size)
        lines = _standard_cover_wrap(draw, title.upper(), font, max_width)
        heights = [draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in lines]
        if len(lines) <= 4 and sum(heights) + max(0, len(lines) - 1) * 18 <= 430:
            return font, lines, 18
    font = _standard_cover_font("arialbd.ttf", 58)
    return font, _standard_cover_wrap(draw, title.upper(), font, max_width), 14


def _standard_cover_metadata_from_locals(local_vars):
    for key in ("metadata", "meta", "data", "book", "book_data"):
        value = local_vars.get(key)
        if isinstance(value, dict):
            return value
    return {}


def _standard_cover_resolve_title(local_vars):
    for key in ("title", "book_title", "TITLE"):
        value = local_vars.get(key)
        if value:
            return value
    metadata = _standard_cover_metadata_from_locals(local_vars)
    return metadata.get("title", "")


def _standard_cover_resolve_author(local_vars):
    for key in ("author", "AUTHOR"):
        value = local_vars.get(key)
        if value:
            return value
    metadata = _standard_cover_metadata_from_locals(local_vars)
    return metadata.get("author", "Barış Kısır")


def _standard_cover_resolve_model(local_vars):
    for key in ("model", "mo", "MODEL"):
        value = local_vars.get(key)
        if value:
            return value
    metadata = _standard_cover_metadata_from_locals(local_vars)
    value = metadata.get("model")
    if value:
        return value
    return ""


def _draw_standard_cover_title_panel(image, title="", author="", model=""):
    title = _standard_cover_repair_text(str(title or "")).strip()
    author = _standard_cover_repair_text(str(author or "Bar?? K?s?r")).strip()
    draw = ImageDraw.Draw(image, "RGBA")
    py = 1765
    draw.rectangle((0, py, WIDTH, HEIGHT), fill=(12, 10, 8, 255))
    draw.line((180, py + 17, WIDTH - 180, py + 17), fill=(218, 181, 107, 125), width=3)
    title_font, lines, gap = _standard_cover_title_font(draw, title, 1260)
    author_font = _standard_cover_font("arialbd.ttf", 52)
    title_height = sum(draw.textbbox((0, 0), line, font=title_font)[3] - draw.textbbox((0, 0), line, font=title_font)[1] for line in lines) + max(0, len(lines) - 1) * gap
    author_height = draw.textbbox((0, 0), author, font=author_font)[3] - draw.textbbox((0, 0), author, font=author_font)[1]
    y = py + 120 + max(0, (HEIGHT - py - 230 - (title_height + 118 + author_height)) // 2)
    y = _standard_cover_center(draw, y, lines, title_font, (242, 228, 198), gap, WIDTH) + 118
    _standard_cover_center(draw, y, [author], author_font, (208, 190, 154), 12, WIDTH)
    if not model:
        model = _standard_cover_resolve_model(locals())
    if model:
        model_font = _standard_cover_font("arial.ttf", 36)
        _standard_cover_center(draw, HEIGHT - 110, [model], model_font, (140, 120, 100), 12, WIDTH)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    create_cover(args.metadata, args.out)


if __name__ == "__main__":
    main()
