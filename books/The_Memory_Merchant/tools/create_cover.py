#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Memory Merchant."""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
FONTS_DIR = Path("C:/Windows/Fonts")

WIDTH, HEIGHT = 1600, 2560
TITLE_PANEL_TOP = 1920


def rel(path: str | Path) -> Path:
    p = Path(path)
    return ROOT / p if not p.is_absolute() else p


def lerp_color(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def draw_gradient(draw, width, height):
    """A dim near-future shop: deep grey-blue above, faint teal haze below."""
    for y in range(height):
        f = y / height
        if f < 0.5:
            t = f / 0.5
            c = lerp_color((12, 16, 26), (18, 28, 40), t)
        else:
            t = (f - 0.5) / 0.5
            c = lerp_color((18, 28, 40), (26, 44, 52), t)
        draw.line([(0, y), (width, y)], fill=c)


def _glow_dot(draw, x, y, r, color):
    rr = int(r)
    for i in range(rr, 0, -1):
        a = int(color[3] * (i / rr) ** 2)
        draw.ellipse([x - i, y - i, x + i, y + i], fill=(color[0], color[1], color[2], a))


def draw_shelves(draw, width, height):
    """Rows of softly glowing memory vials on dim shelves."""
    rng = random.Random(11)
    palettes = [
        (90, 220, 210),   # teal
        (170, 130, 240),  # violet
        (240, 190, 110),  # amber
        (120, 180, 245),  # cool blue
    ]
    shelf_ys = [560, 880, 1200, 1520]
    for sy in shelf_ys:
        # shelf board
        draw.rectangle([120, sy + 150, width - 120, sy + 172], fill=(40, 48, 60))
        draw.rectangle([120, sy + 172, width - 120, sy + 184], fill=(22, 28, 38))
        n = 9
        for i in range(n):
            x = 200 + i * ((width - 400) // (n - 1))
            color = palettes[(i + sy) % len(palettes)]
            vh = rng.randint(96, 134)
            top = sy + 150 - vh
            # vial body (glass)
            draw.rounded_rectangle([x - 26, top, x + 26, sy + 150], radius=20,
                                   fill=(color[0] // 4 + 16, color[1] // 4 + 18, color[2] // 4 + 22, 235),
                                   outline=(color[0], color[1], color[2], 120), width=2)
            # neck and cap
            draw.rectangle([x - 12, top - 26, x + 12, top], fill=(60, 70, 84))
            draw.rectangle([x - 16, top - 38, x + 16, top - 26], fill=(80, 92, 108))
            # luminous memory inside
            _glow_dot(draw, x, top + vh // 2, 30, (color[0], color[1], color[2], 150))
            # reflection on shelf
            _glow_dot(draw, x, sy + 158, 18, (color[0], color[1], color[2], 60))


def draw_figure(draw, width, height):
    """A dim silhouette of the broker standing among the shelves, lower right."""
    fx, base = width - 360, 1680
    body = (8, 12, 18)
    # coat / torso
    draw.polygon([(fx - 70, base), (fx - 50, base - 300), (fx + 50, base - 300), (fx + 70, base)], fill=body)
    # head
    draw.ellipse([fx - 30, base - 380, fx + 30, base - 300], fill=body)
    # faint rim light from the vials
    draw.arc([fx - 30, base - 380, fx + 30, base - 300], 200, 320, fill=(90, 200, 200, 120), width=3)
    draw.line([(fx + 50, base - 300), (fx + 64, base)], fill=(70, 150, 170, 90), width=4)


def draw_motes(draw, width, height):
    """Drifting motes of light, like loose memories."""
    rng = random.Random(5)
    for _ in range(90):
        x = rng.randint(0, width)
        y = rng.randint(0, int(height * 0.72))
        r = rng.randint(2, 6)
        col = rng.choice([(120, 220, 215), (180, 150, 240), (240, 200, 130)])
        _glow_dot(draw, x, y, r * 3, (col[0], col[1], col[2], rng.randint(40, 110)))


def create_cover(metadata_path, output_path):
    metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    title = metadata.get("title", "The Memory Merchant")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    draw_gradient(draw, WIDTH, HEIGHT)
    draw_shelves(draw, WIDTH, HEIGHT)
    draw_figure(draw, WIDTH, HEIGHT)
    draw_motes(draw, WIDTH, HEIGHT)

    img = img.filter(ImageFilter.SMOOTH)

    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()))
    img.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")


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


def _standard_cover_wrap(draw, text: str, selected_font, max_width: int):
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


def _standard_cover_center(draw, y: int, lines, selected_font, fill, line_gap: int, width: int) -> int:
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    metadata_path = rel(args.metadata)
    output_path = rel(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    create_cover(metadata_path, output_path)


if __name__ == "__main__":
    main()
