#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Bone Orchard Trail."""

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
    """Blood-dusk desert sky: deep violet night above, rust and sickly amber at the horizon."""
    for y in range(height):
        f = y / height
        if f < 0.45:
            t = f / 0.45
            c = lerp_color((22, 14, 30), (70, 28, 36), t)
        elif f < 0.62:
            t = (f - 0.45) / 0.17
            c = lerp_color((70, 28, 36), (150, 70, 40), t)
        elif f < 0.70:
            t = (f - 0.62) / 0.08
            c = lerp_color((150, 70, 40), (190, 120, 60), t)
        else:
            t = (f - 0.70) / 0.30
            c = lerp_color((120, 80, 55), (40, 28, 26), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_blood_moon(draw, width, height):
    mx, my, r = width - 360, height * 0.20, 150
    for rr in range(int(r * 1.8), r, -6):
        a = max(0, 60 - (rr - r))
        draw.ellipse([mx - rr, my - rr, mx + rr, my + rr], outline=(150, 60, 45, a), width=2)
    draw.ellipse([mx - r, my - r, mx + r, my + r], fill=(165, 75, 55))
    draw.ellipse([mx - r + 18, my - r + 10, mx + r - 24, my + r - 16], fill=(150, 66, 48))


def draw_mesa(draw, width, height):
    base = height * 0.70
    # distant flat-topped mesas
    draw.polygon([(0, base), (0, base - 120), (260, base - 150), (520, base - 110),
                  (520, base)], fill=(58, 36, 38))
    draw.polygon([(900, base), (900, base - 170), (1180, base - 200), (width, base - 140),
                  (width, base)], fill=(50, 32, 34))


def draw_orchard(draw, width, height):
    """Pale, bare, twisted dead trees along the foreground ridge."""
    rng = random.Random(7)
    ground = height * 0.74
    trees = [(140, 2.4), (340, 1.8), (560, 2.1), (1040, 1.9), (1280, 2.5), (1470, 1.7)]
    for tx, scale in trees:
        h = int(360 * scale)
        top = int(ground - h)
        # trunk
        draw.line([(tx, ground), (tx + rng.randint(-12, 12), top)], fill=(214, 208, 196), width=int(10 * scale))
        # twisted branches
        for _ in range(int(5 * scale)):
            by = rng.randint(top, int(ground - 60))
            bx = tx + rng.randint(-8, 8)
            ex = bx + rng.randint(-90, 90)
            ey = by - rng.randint(30, 110)
            draw.line([(bx, by), (ex, ey)], fill=(200, 194, 182), width=max(2, int(5 * scale)))


def draw_rider(draw, width, height):
    """A lone rider silhouette on the trail."""
    rx, ground = width // 2 - 60, int(height * 0.735)
    body = (18, 12, 14)
    # horse
    draw.ellipse([rx - 70, ground - 70, rx + 70, ground - 20], fill=body)
    draw.rectangle([rx - 60, ground - 60, rx - 50, ground], fill=body)
    draw.rectangle([rx - 20, ground - 60, rx - 10, ground], fill=body)
    draw.rectangle([rx + 40, ground - 60, rx + 50, ground], fill=body)
    draw.rectangle([rx + 58, ground - 58, rx + 68, ground], fill=body)
    # neck and head
    draw.polygon([(rx + 60, ground - 60), (rx + 96, ground - 110), (rx + 110, ground - 96),
                  (rx + 74, ground - 48)], fill=body)
    # rider
    draw.ellipse([rx - 18, ground - 120, rx + 18, ground - 64], fill=body)
    draw.ellipse([rx - 12, ground - 150, rx + 14, ground - 116], fill=body)
    # hat brim
    draw.ellipse([rx - 24, ground - 152, rx + 26, ground - 140], fill=body)
    draw.rectangle([rx - 8, ground - 168, rx + 10, ground - 146], fill=body)


def draw_dust(draw, width, height):
    rng = random.Random(21)
    for _ in range(120):
        x = rng.randint(0, width)
        y = rng.randint(int(height * 0.5), int(height * 0.78))
        s = rng.randint(1, 3)
        a = rng.randint(20, 70)
        draw.ellipse([x - s, y - s, x + s, y + s], fill=(200, 170, 130, a))


def create_cover(metadata_path, output_path):
    metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    title = metadata.get("title", "The Bone Orchard Trail")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    draw_gradient(draw, WIDTH, HEIGHT)
    draw_blood_moon(draw, WIDTH, HEIGHT)
    draw_mesa(draw, WIDTH, HEIGHT)
    draw_dust(draw, WIDTH, HEIGHT)
    draw_orchard(draw, WIDTH, HEIGHT)
    draw_rider(draw, WIDTH, HEIGHT)

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
