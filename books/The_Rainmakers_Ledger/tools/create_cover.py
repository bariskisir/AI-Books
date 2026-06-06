#!/usr/bin/env python3
"""Generate a project-local raster cover for The Rainmaker's Ledger."""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH = 1600
HEIGHT = 2560
TITLE = "The Rainmaker's Ledger"
PALETTE = [tuple(c) for c in [[32, 27, 20], [92, 70, 43], [158, 122, 70], [190, 194, 170]]]
SEED = 2111


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

    _gradient(draw, (37, 32, 24), (122, 92, 55))
    for x in range(80, 1540, 105):
        draw.line((x, 170, x - 95, 1210), fill=(190, 194, 170, 95), width=4)
    draw.polygon([(0, 1210), (WIDTH, 1110), (WIDTH, 1650), (0, 1650)], fill=(84, 64, 38, 235))
    for y in range(1230, 1620, 58):
        draw.line((0, y, WIDTH, y - 95), fill=(174, 139, 83, 70), width=3)
    draw.rounded_rectangle((365, 520, 1235, 1260), radius=22, fill=(204, 177, 122, 232), outline=(61, 42, 26, 220), width=12)
    draw.line((800, 540, 800, 1240), fill=(83, 55, 31, 150), width=8)
    for i in range(11):
        y = 620 + i * 48
        draw.line((450, y, 735, y + rng.randint(-6, 6)), fill=(57, 42, 28, 145), width=4)
        draw.line((865, y, 1160, y + rng.randint(-6, 6)), fill=(57, 42, 28, 145), width=4)
    draw.polygon([(1080, 350), (1340, 420), (1130, 485)], fill=(210, 210, 190, 185), outline=(58, 48, 35, 120))
    draw.line((1110, 420, 960, 710), fill=(210, 210, 190, 105), width=4)
    draw.rectangle((1080, 835, 1150, 1185), outline=(54, 42, 29, 170), width=7)
    _label(draw, "DROUGHT LEDGER", 800, 1450, 42, (224, 201, 143, 180))
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
