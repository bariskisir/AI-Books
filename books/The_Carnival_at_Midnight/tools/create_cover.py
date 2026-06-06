#!/usr/bin/env python3
"""Generate a cover image for The Carnival at Midnight."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH = 1600
HEIGHT = 2560


def get_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    """Try to load arialbd/arial, falling back to default."""
    paths = [
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def draw_gradient(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a vertical gradient from deep purple (top) to midnight blue (bottom)."""
    for y in range(height):
        ratio = y / height
        r = int(15 + ratio * 10)
        g = int(5 + ratio * 5)
        b = int(40 + ratio * 30)
        draw.line([(0, y), (width, y)], fill=(r, g, b))


def draw_stars(draw: ImageDraw, width: int, height: int) -> None:
    """Draw scattered stars in the upper portion."""
    import random

    random.seed(42)
    for _ in range(200):
        x = random.randint(0, width)
        y = random.randint(0, height // 2)
        size = random.randint(1, 3)
        brightness = random.randint(150, 255)
        draw.ellipse(
            [x - size, y - size, x + size, y + size],
            fill=(brightness, brightness, min(255, brightness + 20), 200),
        )


def draw_moon(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a crescent moon."""
    cx, cy = width - 300, 250
    r = 80
    # Full moon base
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(220, 200, 160, 200))
    # Crescent cutout
    draw.ellipse(
        [cx - r + 25, cy - r - 20, cx + r + 10, cy + r - 10],
        fill=(15, 5, 40),
    )


def draw_tents(draw: ImageDraw, width: int, height: int) -> None:
    """Draw carnival tent silhouettes at the bottom third."""
    # Big top tent - center
    tent_data = [
        # (center_x, width, height, color)
        (width // 2, 500, 350, (180, 30, 50)),  # main tent red
        (width // 2 - 300, 250, 200, (140, 25, 90)),  # left tent purple
        (width // 2 + 320, 250, 200, (140, 25, 90)),  # right tent purple
        (width // 2 - 150, 180, 140, (200, 40, 60)),  # small red
        (width // 2 + 180, 180, 140, (200, 40, 60)),  # small red
        (width // 2 - 480, 200, 160, (100, 20, 70)),  # far left
        (width // 2 + 480, 200, 160, (100, 20, 70)),  # far right
    ]

    base_y = height - 800

    for cx, tw, th, color in tent_data:
        # Tent body - triangle
        draw.polygon(
            [(cx - tw // 2, base_y), (cx, base_y - th), (cx + tw // 2, base_y)],
            fill=color,
        )
        # Tent stripes
        stripe_color = tuple(min(c + 40, 255) for c in color)
        for i in range(1, 5):
            x_offset = int(tw // 2 * (i / 5))
            draw.line(
                [(cx - x_offset, base_y), (cx, base_y - th + int(th * (i / 5)))],
                fill=stripe_color,
                width=3,
            )
            draw.line(
                [(cx + x_offset, base_y), (cx, base_y - th + int(th * (i / 5)))],
                fill=stripe_color,
                width=3,
            )
        # Flag on top
        draw.polygon(
            [(cx, base_y - th), (cx + 20, base_y - th + 30), (cx, base_y - th + 15)],
            fill=(255, 200, 50),
        )


def draw_ferris_wheel(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a ferris wheel on the right side."""
    cx = width - 200
    cy = height - 1100
    r = 200

    # Wheel frame
    draw.ellipse(
        [cx - r, cy - r, cx + r, cy + r],
        outline=(200, 180, 150),
        width=4,
    )
    # Spokes
    for angle_deg in range(0, 360, 30):
        rad = math.radians(angle_deg)
        x1 = cx + int(r * math.cos(rad))
        y1 = cy + int(r * math.sin(rad))
        draw.line([(cx, cy), (x1, y1)], fill=(180, 160, 130), width=2)

    # Carriages
    for angle_deg in range(0, 360, 30):
        rad = math.radians(angle_deg)
        cx_c = cx + int(r * math.cos(rad))
        cy_c = cy + int(r * math.sin(rad))
        draw.rectangle(
            [cx_c - 12, cy_c - 8, cx_c + 12, cy_c + 8],
            fill=(60, 40, 80),
            outline=(200, 180, 150),
        )
        # Light in carriage
        draw.ellipse(
            [cx_c - 4, cy_c - 4, cx_c + 4, cy_c + 4],
            fill=(255, 200, 50),
        )

    # Support legs
    draw.line([(cx - 20, cy + r), (cx - 40, cy + r + 300)], fill=(100, 90, 80), width=8)
    draw.line([(cx + 20, cy + r), (cx + 40, cy + r + 300)], fill=(100, 90, 80), width=8)
    draw.line([(cx - 40, cy + r + 300), (cx + 40, cy + r + 300)], fill=(100, 90, 80), width=6)


def draw_title_panel(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the dark title panel at the bottom with white text."""
    panel_top = 1920
    panel_bottom = 2560

    # Dark gradient panel
    for y in range(panel_top, panel_bottom):
        ratio = (y - panel_top) / (panel_bottom - panel_top)
        alpha = int(180 + 75 * ratio)
        r = int(10 * (1 - ratio) + 20 * ratio)
        g = int(5 * (1 - ratio) + 10 * ratio)
        b = int(20 * (1 - ratio) + 35 * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Gold border line at top of panel
    draw.line([(200, panel_top + 5), (width - 200, panel_top + 5)], fill=(210, 175, 60), width=2)

    # Load fonts
    font_large = get_font(72)
    font_small = get_font(36)

    # Title text
    title = "The Carnival"
    subtitle = "at Midnight"

    # Use textbbox for center alignment
    bbox1 = draw.textbbox((0, 0), title, font=font_large)
    tw1 = bbox1[2] - bbox1[0]
    tx = (width - tw1) // 2
    ty = panel_top + 80
    draw.text((tx, ty), title, fill=(255, 255, 255), font=font_large)

    bbox2 = draw.textbbox((0, 0), subtitle, font=font_large)
    tw2 = bbox2[2] - bbox2[0]
    tx2 = (width - tw2) // 2
    ty2 = ty + 90
    draw.text((tx2, ty2), subtitle, fill=(255, 255, 255), font=font_large)

    # Author name
    author = "Barış Kısır"
    bbox3 = draw.textbbox((0, 0), author, font=font_small)
    tw3 = bbox3[2] - bbox3[0]
    tx3 = (width - tw3) // 2
    ty3 = ty2 + 100
    draw.text((tx3, ty3), author, fill=(210, 175, 60), font=font_small)

    # Bottom gold border
    draw.line([(200, panel_bottom - 20), (width - 200, panel_bottom - 20)], fill=(210, 175, 60), width=2)

    # Genre tag
    genre_tag = "Weird Fiction"
    font_tag = get_font(28, bold=False)
    bbox4 = draw.textbbox((0, 0), genre_tag, font=font_tag)
    tw4 = bbox4[2] - bbox4[0]
    tx4 = (width - tw4) // 2
    ty4 = panel_bottom - 85
    draw.text((tx4, ty4), genre_tag, fill=(180, 180, 180), font=font_tag)


def generate_cover(metadata_path: str, output_path: str) -> None:
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    draw_gradient(draw, WIDTH, HEIGHT)
    draw_stars(draw, WIDTH, HEIGHT)
    draw_moon(draw, WIDTH, HEIGHT)
    draw_tents(draw, WIDTH, HEIGHT)
    draw_ferris_wheel(draw, WIDTH, HEIGHT)
    draw_title_panel(draw, WIDTH, HEIGHT)

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
    parser.add_argument("--metadata", required=True, help="Path to metadata JSON")
    parser.add_argument("--out", required=True, help="Output PNG path")
    args = parser.parse_args()
    generate_cover(args.metadata, args.out)


if __name__ == "__main__":
    main()