#!/usr/bin/env python3
"""Generate a book cover for The Glass Prison using PIL."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont



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
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    title = metadata["title"]
    author = metadata["author"]

    W, H = 1600, 2560
    img = Image.new("RGB", (W, H), "#1a1a2e")
    draw = ImageDraw.Draw(img)

    # Gradient background: dark steel gray to burnt orange
    for y in range(H):
        ratio = y / H
        r = int(26 + 180 * ratio)
        g = int(26 + 60 * ratio)
        b = int(46 + 20 * ratio)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    vanish_x, vanish_y = W // 2, H // 3

    # Floor perspective polygons
    for i in range(8):
        x1 = int(W * (0.1 + 0.1 * i))
        x2 = int(W * (0.1 + 0.1 * (i + 1)))
        gray = int(60 + 20 * i)
        draw.polygon(
            [(vanish_x, vanish_y), (x1, H), (x2, H)],
            fill=(gray, gray, gray + 10),
        )

    # Glass wall vertical struts - perspective lines
    strut_color = (200, 200, 210)
    for i in range(10):
        x = int(W * (0.05 + 0.1 * i))
        # Top section
        top_x2 = vanish_x + (x - vanish_x) * 2 // 3
        draw.line(
            [(x, 0), (top_x2, vanish_y)],
            fill=strut_color,
            width=3,
        )
        # Bottom section
        if x > vanish_x:
            bot_x1 = vanish_x + (x - vanish_x) * 2 // 3
            draw.line(
                [(bot_x1, vanish_y), (x, H)],
                fill=strut_color,
                width=3,
            )
        else:
            bot_x2 = vanish_x - (vanish_x - x) * 2 // 3
            draw.line(
                [(x, vanish_y), (bot_x2, H)],
                fill=strut_color,
                width=3,
            )

    # Horizontal glass panel lines
    for i in range(6):
        y_pos = int(H * 0.05 + i * 100)
        draw.line(
            [(int(W * 0.15), y_pos), (int(W * 0.85), y_pos)],
            fill=(180, 180, 200),
            width=2,
        )

    # Watchtower silhouette (right side)
    tower_x = W - 250
    tower_base_y = int(H * 0.5)
    # Tower body
    draw.rectangle(
        [tower_x, tower_base_y - 300, tower_x + 80, tower_base_y],
        fill=(30, 30, 40),
        outline=(100, 100, 110),
        width=2,
    )
    # Tower top
    draw.rectangle(
        [tower_x - 20, tower_base_y - 320, tower_x + 100, tower_base_y - 300],
        fill=(40, 40, 50),
        outline=(120, 120, 130),
        width=2,
    )
    # Tower light (glow)
    draw.ellipse(
        [tower_x + 15, tower_base_y - 290, tower_x + 65, tower_base_y - 270],
        fill=(255, 200, 50),
    )
    draw.ellipse(
        [tower_x + 20, tower_base_y - 285, tower_x + 60, tower_base_y - 275],
        fill=(255, 255, 200),
    )

    # Light beam from tower
    beam_points = [
        (tower_x + 40, tower_base_y - 280),
        (tower_x + 400, tower_base_y - 420),
        (tower_x + 200, tower_base_y - 50),
    ]
    draw.polygon(beam_points, fill=(80, 60, 20))

    # Floor grid lines
    for y in range(int(H * 0.5), H, 60):
        draw.line(
            [(0, y), (W, y)],
            fill=(100, 100, 110),
            width=1,
        )

    # Title panel at bottom
    panel_top = 1920
    draw.rectangle(
        [(0, panel_top), (W, H)],
        fill=(20, 20, 30),
    )

    # Accent line at top of panel
    draw.line(
        [(0, panel_top), (W, panel_top)],
        fill=(230, 120, 30),
        width=4,
    )

    # Load fonts
    title_font = ImageFont.truetype("arialbd.ttf", 72)
    author_font = ImageFont.truetype("arial.ttf", 36)

    # Title text
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_w = title_bbox[2] - title_bbox[0]
    title_x = (W - title_w) // 2
    title_y = panel_top + 100
    draw.text((title_x, title_y), title, font=title_font, fill=(255, 255, 255))

    # Author text
    author_bbox = draw.textbbox((0, 0), author, font=author_font)
    author_w = author_bbox[2] - author_bbox[0]
    author_x = (W - author_w) // 2
    author_y = title_y + 100
    draw.text((author_x, author_y), author, font=author_font, fill=(220, 220, 220))

    # Save
    args.out.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()))
    img.save(args.out, "PNG")
    print(f"Cover saved to {args.out}")


if __name__ == "__main__":
    main()