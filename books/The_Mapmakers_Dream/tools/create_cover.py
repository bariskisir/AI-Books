#!/usr/bin/env python3
"""Generate a book cover for The Mapmaker's Dream using PIL."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1600, 2560


def gradient(draw: ImageDraw, top: tuple, bottom: tuple) -> None:
    for y in range(HEIGHT):
        r = int(top[0] + (bottom[0] - top[0]) * y / HEIGHT)
        g = int(top[1] + (bottom[1] - top[1]) * y / HEIGHT)
        b = int(top[2] + (bottom[2] - top[2]) * y / HEIGHT)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def draw_river(draw: ImageDraw) -> None:
    river_color = (42, 95, 70)
    pts = []
    x = 0
    y = 400
    for i in range(60):
        x = int(800 + 500 * math.sin(i * 0.08 + 0.5))
        y = 400 + i * 25
        pts.append((x, y))
    draw.line(pts, fill=river_color, width=40)
    draw.line(pts, fill=(70, 140, 100), width=20)


def draw_jungle(draw: ImageDraw) -> None:
    greens = [(25, 60, 30), (30, 80, 35), (20, 50, 25)]
    for _ in range(200):
        x = int(200 + 1200 * 0.5)  # will be randomized
    for _ in range(120):
        x = int(100 + 1400 * (__import__('random').random()))
        y = int(200 + 1600 * (__import__('random').random()))
        size = int(20 + 60 * (__import__('random').random()))
        shade = greens[__import__('random').randint(0, 2)]
        draw.ellipse([x - size, y - size, x + size, y + size], fill=shade, outline=None)


def draw_stone_city(draw: ImageDraw) -> None:
    wall_color = (180, 150, 110)
    tower_color = (200, 170, 130)
    # City wall on the far shore
    for i in range(12):
        bx = 600 + i * 35
        by = 850
        draw.rectangle([bx, by - 200, bx + 25, by], fill=wall_color, outline=(140, 110, 70))
    # Towers
    draw.rectangle([580, 580, 610, 850], fill=tower_color, outline=(140, 110, 70))
    draw.rectangle([970, 620, 1000, 850], fill=tower_color, outline=(140, 110, 70))
    # Central tower (the source)
    draw.rectangle([760, 500, 810, 850], fill=(210, 180, 140), outline=(140, 110, 70))
    # Gate
    draw.rectangle([700, 720, 740, 850], fill=(120, 90, 60))
    # Window arches on central tower
    for wy in range(520, 720, 40):
        draw.arc([775, wy, 795, wy + 30], 0, 180, fill=(100, 70, 40), width=3)


def draw_title_panel(draw: ImageDraw, title_font, author_font) -> None:
    # Dark panel at bottom
    draw.rectangle([0, 1920, WIDTH, HEIGHT], fill=(20, 15, 10, 220))

    # Title
    title = "THE MAPMAKER'S"
    title2 = "DREAM"
    # Center title
    tbbox = draw.textbbox((0, 0), title, font=title_font)
    tw = tbbox[2] - tbbox[0]
    tx = (WIDTH - tw) // 2
    draw.text((tx, 1960), title, fill=(255, 255, 255), font=title_font)

    tbbox2 = draw.textbbox((0, 0), title2, font=title_font)
    tw2 = tbbox2[2] - tbbox2[0]
    tx2 = (WIDTH - tw2) // 2
    draw.text((tx2, 2040), title2, fill=(255, 255, 255), font=title_font)

    # Decorative line
    draw.rectangle([650, 2150, 950, 2155], fill=(200, 170, 130))

    # Author
    author = "Barış Kısır"
    abbox = draw.textbbox((0, 0), author, font=author_font)
    aw = abbox[2] - abbox[0]
    ax = (WIDTH - aw) // 2
    draw.text((ax, 2200), author, fill=(255, 255, 255), font=author_font)



def _standard_cover_font(name: str, size: int):
    font_dir = globals().get("FONT_DIR", globals().get("FONTS_DIR", None))
    candidates = []
    if font_dir is not None:
        candidates.append(Path(font_dir) / name)
    candidates.extend([
        Path("C:/Windows/Fonts") / name,
        Path("C:/Windows/Fonts") / "arialbd.ttf",
        Path("C:/Windows/Fonts") / "arial.ttf",
    ])
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def _standard_cover_repair_text(text: str) -> str:
    try:
        return text.encode("latin1").decode("utf-8")
    except UnicodeError:
        return text


def _standard_cover_wrap(draw, text: str, selected_font, max_width: int) -> list[str]:
    words = text.split()
    lines = []
    current = []
    for word in words:
        proposed = " ".join([*current, word])
        if draw.textbbox((0, 0), proposed, font=selected_font)[2] <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def _standard_cover_center(draw, y: int, lines: list[str], selected_font, fill, line_gap: int, width: int) -> int:
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=selected_font)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), line, font=selected_font, fill=fill)
        y += bbox[3] - bbox[1] + line_gap
    return y


def _standard_cover_title_font(draw, title: str, max_width: int):
    for size in (116, 104, 96, 88, 80, 72):
        selected = _standard_cover_font("arialbd.ttf", size)
        lines = _standard_cover_wrap(draw, title.upper(), selected, max_width)
        heights = [draw.textbbox((0, 0), line, font=selected)[3] - draw.textbbox((0, 0), line, font=selected)[1] for line in lines]
        total = sum(heights) + max(0, len(lines) - 1) * 18
        if len(lines) <= 4 and total <= 430:
            return selected, lines, 18
    selected = _standard_cover_font("arialbd.ttf", 68)
    return selected, _standard_cover_wrap(draw, title.upper(), selected, max_width), 16


def _standard_cover_metadata_from_locals(local_vars):
    for key in ("metadata", "meta", "data", "m", "book", "book_data"):
        value = local_vars.get(key)
        if isinstance(value, dict):
            return value

    candidates = []
    args = local_vars.get("args")
    if args is not None:
        candidates.append(getattr(args, "metadata", None))
    for key in ("metadata_path", "meta_path", "mp"):
        candidates.append(local_vars.get(key))

    for metadata_path in candidates:
        if not metadata_path:
            continue
        try:
            json_mod = __import__("json")
            path_cls = __import__("pathlib").Path
            return json_mod.loads(path_cls(metadata_path).read_text(encoding="utf-8"))
        except Exception:
            continue
    return {}


def _standard_cover_resolve_title(local_vars):
    for key in ("title", "ti", "book_title", "TITLE"):
        value = local_vars.get(key)
        if value:
            return value

    metadata = _standard_cover_metadata_from_locals(local_vars)
    for key in ("title", "book_title", "name"):
        value = metadata.get(key)
        if value:
            return value

    args = local_vars.get("args")
    candidates = []
    if args is not None:
        candidates.append(getattr(args, "out", None))
    for key in ("output_path", "out_path", "op", "out"):
        candidates.append(local_vars.get(key))

    for output_path in candidates:
        if not output_path:
            continue
        try:
            path_cls = __import__("pathlib").Path
            stem = path_cls(output_path).stem.replace("_", " ").strip()
            if stem:
                return stem
        except Exception:
            continue
    return ""


def _standard_cover_resolve_author(local_vars):
    for key in ("author", "au", "AUTHOR"):
        value = local_vars.get(key)
        if value:
            return value

    metadata = _standard_cover_metadata_from_locals(local_vars)
    value = metadata.get("author")
    if value:
        return value
    return "Barış Kısır"

def _draw_standard_cover_title_panel(image, title: str = "", author: str = "") -> None:
    width = int(globals().get("W", globals().get("WIDTH", 1600)))
    height = int(globals().get("H", globals().get("HEIGHT", 2560)))
    panel_y = 1765
    title = _standard_cover_repair_text(str(title or "")).strip()
    author = _standard_cover_repair_text(str(author or "Barış Kısır")).strip()

    draw = ImageDraw.Draw(image, "RGBA")
    draw.rectangle((0, panel_y, width, height), fill=(3, 5, 8, 255))
    draw.line((180, panel_y + 17, width - 180, panel_y + 17), fill=(160, 225, 209, 105), width=3)

    title_font, title_lines, title_gap = _standard_cover_title_font(draw, title, 1260)
    author_font = _standard_cover_font("arialbd.ttf", 50)
    title_height = sum(draw.textbbox((0, 0), line, font=title_font)[3] - draw.textbbox((0, 0), line, font=title_font)[1] for line in title_lines)
    title_height += max(0, len(title_lines) - 1) * title_gap
    author_bbox = draw.textbbox((0, 0), author, font=author_font)
    author_height = author_bbox[3] - author_bbox[1]
    block_height = title_height + 120 + author_height
    y = panel_y + 120 + max(0, (height - panel_y - 210 - block_height) // 2)
    y = _standard_cover_center(draw, y, title_lines, title_font, (244, 249, 238), title_gap, width)
    y += 120
    _standard_cover_center(draw, y, [author], author_font, (210, 229, 221), 12, width)
def main() -> None:
    parser = argparse.ArgumentParser(description="Generate cover for The Mapmaker's Dream")
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Gradient: deep green (top) to terracotta/emerald (bottom)
    gradient(draw, (15, 40, 25), (110, 65, 45))

    # Jungle canopy silhouettes
    draw_jungle(draw)

    # River
    draw_river(draw)

    # Stone city
    draw_stone_city(draw)

    # River highlights (reflection)
    draw.rectangle([0, 860, WIDTH, 880], fill=(60, 130, 90, 80))

    # Load fonts
    try:
        title_font = ImageFont.truetype("arialbd.ttf", 80)
        author_font = ImageFont.truetype("arial.ttf", 36)
    except (OSError, IOError):
        title_font = ImageFont.load_default()
        author_font = ImageFont.load_default()

    # Title panel
    draw_title_panel(draw, title_font, author_font)

    # Save
    args.out.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()))
    img.save(args.out, "PNG")
    print(f"Cover saved to {args.out}")


if __name__ == "__main__":
    main()