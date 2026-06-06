#!/usr/bin/env python3
"""Generate a project-local raster cover for The Driftwood Court."""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH = 1600
HEIGHT = 2560
TITLE = "The Driftwood Court"
PALETTE = [tuple(c) for c in [[18, 34, 42], [41, 78, 88], [108, 126, 111], [221, 199, 149]]]
SEED = 1950


def _gradient(draw, top, bottom):
    for y in range(HEIGHT):
        t = y / max(1, HEIGHT - 1)
        draw.line((0, y, WIDTH, y), fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))


def _label(draw, text, cx, y, size, fill):
    font = _standard_cover_font("arialbd.ttf", size)
    box = draw.textbbox((0, 0), text, font=font)
    draw.text((cx - (box[2] - box[0]) // 2, y), text, font=font, fill=fill)


def _draw_scene(draw, image):
    rng = random.Random(SEED)

    _gradient(draw, (16, 36, 45), (54, 91, 96))
    for y in range(970, 1620, 26):
        draw.line((0, y, WIDTH, y + int(10 * math.sin(y / 44))), fill=(166, 206, 210, 38), width=3)
    draw.polygon([(0, 1420), (WIDTH, 1345), (WIDTH, 1620), (0, 1620)], fill=(15, 30, 37, 210))
    for x in range(120, 1540, 180):
        draw.rectangle((x, 1320, x + 34, 1660), fill=(41, 47, 42, 230))
    draw.rectangle((310, 965, 1290, 1325), fill=(78, 73, 60, 240), outline=(221, 199, 149, 165), width=8)
    draw.polygon([(260, 965), (800, 700), (1340, 965)], fill=(112, 91, 61, 245), outline=(221, 199, 149, 160))
    for x in range(430, 1180, 190):
        draw.rectangle((x, 1060, x + 95, 1245), fill=(22, 44, 50, 230), outline=(194, 176, 131, 115), width=5)
    draw.rectangle((715, 1045, 885, 1325), fill=(32, 39, 39, 245), outline=(194, 176, 131, 160), width=6)
    draw.line((180, 1390, 1420, 1305), fill=(221, 199, 149, 85), width=9)
    draw.arc((560, 450, 1040, 930), 205, 335, fill=(222, 218, 190, 160), width=12)
    _label(draw, "GULL COURT", 800, 1515, 42, (221, 199, 149, 185))
    draw.rectangle((0, 1600, WIDTH, 1765), fill=(10, 8, 7, 92))


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
