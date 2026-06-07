#!/usr/bin/env python3
"""Generate a project-local raster cover for The Pearl Lagoon."""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH = 1600
HEIGHT = 2560
TITLE = "The Pearl Lagoon"
PALETTE = [(15, 40, 50), (25, 70, 80), (35, 100, 110), (200, 160, 100)]
SEED = 1873


def _gradient(draw, top, bottom, y_start, y_end):
    for y in range(y_start, y_end):
        t = (y - y_start) / max(1, y_end - y_start - 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        draw.line((0, y, WIDTH, y), fill=(r, g, b))


def _label(draw, text, cx, y, size, fill):
    font = _standard_cover_font("arialbd.ttf", size)
    box = draw.textbbox((0, 0), text, font=font)
    draw.text((cx - (box[2] - box[0]) // 2, y), text, font=font, fill=fill)


def _draw_scene(draw, image):
    rng = random.Random(SEED)

    # Sky gradient: deep indigo to warm tropical dawn
    _gradient(draw, (10, 25, 60), (60, 120, 160), 0, 550)

    # Sun glow near horizon
    sun_x, sun_y = 800, 420
    for r, alpha in [(300, 15), (200, 25), (120, 40), (60, 60)]:
        draw.ellipse((sun_x - r, sun_y - r, sun_x + r, sun_y + r), fill=(255, 200, 100, alpha))

    # Horizon line — ocean meeting sky
    draw.rectangle((0, 440, WIDTH, 460), fill=(20, 80, 100))

    # Ocean gradient: deep teal to shallow turquoise
    _gradient(draw, (10, 50, 80), (20, 130, 150), 460, 1200)

    # Coral reef shapes below the surface — subtle
    for _ in range(15):
        cx = rng.randint(80, 1520)
        cy = rng.randint(550, 1000)
        rx = rng.randint(40, 150)
        ry = rng.randint(15, 40)
        draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=(30, 100, 110, rng.randint(20, 60)))

    # Light rays from surface into water
    for x in range(600, 1000, 30):
        alpha = rng.randint(15, 40)
        for step in range(5):
            sx = x + rng.randint(-20, 20)
            ey = 460 + rng.randint(100, 500)
            draw.line((sx, 440, sx + rng.randint(-30, 30), ey), fill=(180, 220, 200, alpha), width=rng.randint(1, 3))

    # Atoll / palm island silhouettes on horizon
    atoll_color = (8, 30, 25, 220)
    # Left atoll
    draw.ellipse((50, 380, 350, 470), fill=atoll_color)
    for px in [80, 130, 180, 230, 280]:
        trunk_h = rng.randint(30, 60)
        draw.line((px, 430, px + rng.randint(-5, 5), 430 - trunk_h), fill=(8, 20, 15), width=3)
        fronds_y = 430 - trunk_h
        for _ in range(5):
            dx = rng.randint(-20, 20)
            dy = rng.randint(-15, -5)
            draw.line((px, fronds_y, px + dx, fronds_y + dy), fill=(10, 30, 20), width=2)

    # Right atoll
    draw.ellipse((1250, 390, 1550, 465), fill=atoll_color)
    for px in [1290, 1340, 1390, 1440, 1490]:
        trunk_h = rng.randint(25, 55)
        draw.line((px, 440, px + rng.randint(-5, 5), 440 - trunk_h), fill=(8, 20, 15), width=3)
        fronds_y = 440 - trunk_h
        for _ in range(4):
            dx = rng.randint(-18, 18)
            dy = rng.randint(-14, -5)
            draw.line((px, fronds_y, px + dx, fronds_y + dy), fill=(10, 30, 20), width=2)

    # Outrigger canoe on the water
    canoe_x, canoe_y = 500, 520
    draw.ellipse((canoe_x - 50, canoe_y - 4, canoe_x + 50, canoe_y + 4), fill=(80, 50, 25, 200))
    # Outrigger float
    draw.line((canoe_x - 60, canoe_y + 18, canoe_x + 30, canoe_y + 18), fill=(60, 35, 15, 180), width=3)
    draw.line((canoe_x - 30, canoe_y + 4, canoe_x - 30, canoe_y + 18), fill=(60, 35, 15, 160), width=2)
    draw.line((canoe_x + 10, canoe_y + 4, canoe_x + 10, canoe_y + 18), fill=(60, 35, 15, 160), width=2)

    # Diver figure below surface
    diver_x, diver_y = 850, 720
    # Body
    draw.ellipse((diver_x - 14, diver_y - 10, diver_x + 14, diver_y + 12), fill=(120, 80, 50, 140))
    # Head
    draw.ellipse((diver_x - 10, diver_y - 28, diver_x + 10, diver_y - 8), fill=(120, 80, 50, 140))
    # Arms reaching forward
    draw.line((diver_x + 10, diver_y - 5, diver_x + 35, diver_y - 20), fill=(120, 80, 50, 140), width=4)
    draw.line((diver_x + 10, diver_y + 2, diver_x + 38, diver_y - 8), fill=(120, 80, 50, 140), width=4)
    # Legs
    draw.line((diver_x - 5, diver_y + 10, diver_x - 15, diver_y + 35), fill=(100, 70, 45, 120), width=5)
    draw.line((diver_x + 5, diver_y + 10, diver_x - 5, diver_y + 38), fill=(100, 70, 45, 120), width=5)

    # Pearl glow near diver's outstretched hand
    pearl_x, pearl_y = diver_x + 42, diver_y - 18
    for r, alpha in [(28, 20), (18, 40), (10, 70), (5, 120)]:
        draw.ellipse((pearl_x - r, pearl_y - r, pearl_x + r, pearl_y + r),
                      fill=(240, 230, 210, alpha))
    # Pearl core
    draw.ellipse((pearl_x - 4, pearl_y - 4, pearl_x + 4, pearl_y + 4),
                  fill=(255, 245, 230, 200))

    # More smaller pearls rising
    for px, py in [(diver_x + 30, diver_y - 35), (diver_x + 55, diver_y - 10),
                   (diver_x + 20, diver_y - 50), (diver_x + 50, diver_y - 45)]:
        for r, alpha in [(10, 25), (5, 55), (2, 100)]:
            draw.ellipse((px - r, py - r, px + r, py + r),
                          fill=(240, 230, 210, alpha))

    # Bubbles rising
    for _ in range(20):
        bx = diver_x + rng.randint(-30, 60)
        by = diver_y - rng.randint(10, 100)
        br = rng.randint(1, 3)
        draw.ellipse((bx - br, by - br, bx + br, by + br),
                     fill=(180, 210, 220, rng.randint(40, 80)))

    # Sandy lagoon floor gradient
    _gradient(draw, (25, 100, 110), (40, 70, 60), 1100, 1300)
    # Sand texture
    for _ in range(60):
        sx = rng.randint(50, 1550)
        sy = rng.randint(1100, 1280)
        draw.point((sx, sy), fill=(60, 110, 90, rng.randint(20, 60)))

    # Lagoon surface texture — gentle ripples
    for y in range(460, 1200, 15):
        alpha = rng.randint(5, 20)
        for _ in range(3):
            rx = rng.randint(100, 1500)
            draw.line((rx, y, rx + rng.randint(30, 120), y + rng.randint(-3, 3)),
                      fill=(160, 200, 190, alpha), width=1)

    # Seabed pearls scattered
    for _ in range(8):
        sx = rng.randint(150, 1450)
        sy = rng.randint(1170, 1280)
        sr = rng.randint(3, 7)
        draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr),
                     fill=(220, 210, 180, rng.randint(40, 100)))

    # Location label
    _label(draw, "AVATORU", 800, 1320, 36, (180, 200, 210, 150))

    draw.rectangle((0, 1600, WIDTH, 1765), fill=(5, 10, 12, 65))


def create_cover(metadata_path, out_path):
    metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    title = metadata.get("title", TITLE)
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")
    image = Image.new("RGBA", (WIDTH, HEIGHT), PALETTE[0])
    draw = ImageDraw.Draw(image, "RGBA")
    _draw_scene(draw, image)
    image = image.convert("RGB")
    _draw_standard_cover_title_panel(image, title, author, model)
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


def _standard_cover_resolve_title(local_vars):
    for key in ("title", "book_title", "TITLE"):
        value = local_vars.get(key)
        if value:
            return value
    return ""


def _standard_cover_resolve_author(local_vars):
    for key in ("author", "AUTHOR"):
        value = local_vars.get(key)
        if value:
            return value
    return "Barış Kısır"


def _draw_standard_cover_title_panel(image, title="", author="", model=""):
    title = _standard_cover_repair_text(str(title or "")).strip()
    author = _standard_cover_repair_text(str(author or "Barış Kısır")).strip()
    draw = ImageDraw.Draw(image, "RGBA")
    py = 1765
    draw.rectangle((0, py, 1600, 2560), fill=(12, 10, 8, 255))
    draw.line((180, py + 17, 1420, py + 17), fill=(80, 180, 200, 125), width=3)
    title_font, lines, gap = _standard_cover_title_font(draw, title, 1260)
    author_font = _standard_cover_font("arialbd.ttf", 52)
    title_height = sum(draw.textbbox((0, 0), line, font=title_font)[3] - draw.textbbox((0, 0), line, font=title_font)[1] for line in lines) + max(0, len(lines) - 1) * gap
    author_height = draw.textbbox((0, 0), author, font=author_font)[3] - draw.textbbox((0, 0), author, font=author_font)[1]
    y = py + 120 + max(0, (2560 - py - 230 - (title_height + 118 + author_height)) // 2)
    y = _standard_cover_center(draw, y, lines, title_font, (220, 215, 200), gap, 1600) + 118
    _standard_cover_center(draw, y, [author], author_font, (180, 170, 160), 12, 1600)
    if model:
        model_font = _standard_cover_font("arial.ttf", 36)
        _standard_cover_center(draw, 2560 - 110, [model], model_font, (130, 120, 140), 12, 1600)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    create_cover(args.metadata, args.out)


if __name__ == "__main__":
    main()
