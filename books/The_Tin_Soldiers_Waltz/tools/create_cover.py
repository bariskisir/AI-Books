#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Tin Soldier's Waltz."""

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
    """Deep winter-blue night, warming toward a lamplit gold near the windowsill."""
    for y in range(height):
        f = y / height
        if f < 0.55:
            t = f / 0.55
            c = lerp_color((14, 22, 46), (28, 40, 74), t)
        elif f < 0.74:
            t = (f - 0.55) / 0.19
            c = lerp_color((28, 40, 74), (96, 84, 70), t)
        else:
            t = (f - 0.74) / 0.26
            c = lerp_color((150, 116, 60), (60, 44, 30), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_window_glow(draw, width, height):
    """A warm toyshop window glowing behind the soldier."""
    wx0, wy0, wx1, wy1 = 360, 360, width - 360, 1300
    # outer glow halo
    for i in range(40, 0, -1):
        a = int(2.2 * i)
        draw.rectangle([wx0 - i * 4, wy0 - i * 4, wx1 + i * 4, wy1 + i * 4],
                       outline=(240, 200, 120, max(0, a // 3)), width=2)
    # window pane warm light
    draw.rectangle([wx0, wy0, wx1, wy1], fill=(236, 198, 120, 235))
    # muntins
    draw.line([( (wx0 + wx1) // 2, wy0), ((wx0 + wx1) // 2, wy1)], fill=(120, 86, 44), width=10)
    draw.line([(wx0, (wy0 + wy1) // 2), (wx1, (wy0 + wy1) // 2)], fill=(120, 86, 44), width=10)
    draw.rectangle([wx0, wy0, wx1, wy1], outline=(96, 66, 34), width=16)
    # frost in the corners
    for cx, cy in [(wx0, wy0), (wx1, wy0), (wx0, wy1), (wx1, wy1)]:
        for r in range(60, 0, -10):
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(220, 230, 245, 40), width=2)


def draw_gears(draw, width, height):
    """Faint clockwork gears floating in the dark sky corners."""
    def gear(cx, cy, r, teeth, color):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=6)
        draw.ellipse([cx - r // 3, cy - r // 3, cx + r // 3, cy + r // 3], outline=color, width=5)
        for k in range(teeth):
            a = 2 * math.pi * k / teeth
            x1 = cx + (r) * math.cos(a)
            y1 = cy + (r) * math.sin(a)
            x2 = cx + (r + 16) * math.cos(a)
            y2 = cy + (r + 16) * math.sin(a)
            draw.line([(x1, y1), (x2, y2)], fill=color, width=6)
    gear(200, 260, 90, 12, (90, 110, 150, 160))
    gear(width - 230, 300, 64, 10, (90, 110, 150, 140))
    gear(150, 700, 50, 9, (80, 100, 140, 120))


def draw_sill(draw, width, height):
    """The wooden windowsill the soldier stands on."""
    sill_y = 1320
    draw.rectangle([200, sill_y, width - 200, sill_y + 70], fill=(86, 58, 34))
    draw.rectangle([160, sill_y + 70, width - 160, sill_y + 130], fill=(64, 42, 24))
    # a thin line of snow on the sill edge
    draw.rectangle([200, sill_y - 8, width - 200, sill_y + 4], fill=(226, 234, 246))


def draw_tin_soldier(draw, width, height):
    """A small one-legged tin soldier standing on the sill, in silhouette with bright trim."""
    cx, base = width // 2, 1320
    blue = (40, 70, 130)
    red = (150, 50, 50)
    gold = (210, 170, 80)
    skin = (40, 36, 40)
    # single leg
    draw.rectangle([cx - 14, base - 150, cx + 6, base], fill=blue)
    draw.rectangle([cx - 20, base - 4, cx + 14, base + 10], fill=(20, 16, 18))  # boot
    # torso (red coat)
    draw.rectangle([cx - 34, base - 280, cx + 30, base - 150], fill=red)
    # gold buttons / sash
    for by in range(base - 268, base - 160, 26):
        draw.ellipse([cx - 4, by, cx + 6, by + 10], fill=gold)
    draw.line([(cx - 34, base - 256), (cx + 30, base - 230)], fill=gold, width=6)
    # arms
    draw.rectangle([cx - 48, base - 274, cx - 34, base - 168], fill=red)
    draw.rectangle([cx + 30, base - 274, cx + 44, base - 168], fill=red)
    # rifle at shoulder
    draw.line([(cx + 40, base - 300), (cx + 52, base - 150)], fill=(60, 48, 30), width=7)
    # head
    draw.ellipse([cx - 22, base - 340, cx + 18, base - 280], fill=skin)
    # tall shako hat
    draw.rectangle([cx - 22, base - 392, cx + 18, base - 332], fill=blue)
    draw.rectangle([cx - 26, base - 340, cx + 22, base - 330], fill=gold)
    draw.ellipse([cx - 6, base - 410, cx + 6, base - 396], fill=red)  # plume tip


def draw_snow(draw, width, height):
    rng = random.Random(31)
    for _ in range(260):
        x = rng.randint(0, width)
        y = rng.randint(0, int(height * 0.74))
        s = rng.randint(1, 4)
        a = rng.randint(90, 220)
        draw.ellipse([x - s, y - s, x + s, y + s], fill=(245, 248, 255, a))


def create_cover(metadata_path, output_path):
    metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    title = metadata.get("title", "The Tin Soldier's Waltz")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    draw_gradient(draw, WIDTH, HEIGHT)
    draw_gears(draw, WIDTH, HEIGHT)
    draw_window_glow(draw, WIDTH, HEIGHT)
    draw_sill(draw, WIDTH, HEIGHT)
    draw_tin_soldier(draw, WIDTH, HEIGHT)
    draw_snow(draw, WIDTH, HEIGHT)

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
