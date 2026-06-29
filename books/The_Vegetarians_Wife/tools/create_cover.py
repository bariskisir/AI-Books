#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Vegetarian's Wife."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import (
    _standard_cover_font,
    _standard_cover_repair_text,
    _standard_cover_wrap,
    _standard_cover_center,
    _standard_cover_title_font,
    _standard_cover_metadata_from_locals,
    _standard_cover_resolve_title,
    _standard_cover_resolve_author,
    _draw_standard_cover_title_panel,
)



ROOT = Path(__file__).resolve().parents[3]
FONTS_DIR = Path("C:/Windows/Fonts")

WIDTH, HEIGHT = 1600, 2560
TITLE_PANEL_TOP = 1920


def rel(path: str | Path) -> Path:
    p = Path(path)
    return ROOT / p if not p.is_absolute() else p


def lerp_color(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def draw_gradient(draw: ImageDraw, width: int, height: int) -> None:
    """Cream to plum gradient for the psychological literary feel."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((245, 235, 220), (200, 180, 190), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((200, 180, 190), (120, 80, 110), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((120, 80, 110), (40, 20, 45), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_empty_dining_table(draw: ImageDraw, width: int, height: int) -> None:
    """Draw an empty dining table with a single chair and a bowl of fruit."""
    cx, cy = width // 2, int(height * 0.55)

    # Table surface (oval)
    draw.ellipse([cx - 240, cy - 20, cx + 240, cy + 20], fill=(140, 110, 100))
    draw.ellipse([cx - 240, cy - 20, cx + 240, cy + 20], outline=(100, 75, 65), width=2)

    # Table leg
    draw.rectangle([cx - 6, cy + 15, cx + 6, cy + 80], fill=(100, 75, 65))

    # Chair (empty, pushed back)
    chair_x = cx + 180
    chair_y = cy + 10
    # Chair seat
    draw.rectangle([chair_x - 30, chair_y - 5, chair_x + 30, chair_y + 15], fill=(80, 55, 65))
    # Chair back
    draw.rectangle([chair_x - 25, chair_y - 70, chair_x + 25, chair_y - 5], fill=(80, 55, 65))
    # Chair legs
    for lx in [chair_x - 25, chair_x + 25]:
        draw.rectangle([lx - 3, chair_y + 10, lx + 3, chair_y + 50], fill=(70, 45, 55))

    # Bowl of fruit on the table
    bx, by = cx, cy - 15
    # Bowl
    draw.ellipse([bx - 35, by - 5, bx + 35, by + 20], fill=(180, 160, 140))
    draw.ellipse([bx - 35, by - 5, bx + 35, by + 20], outline=(120, 100, 85), width=2)
    # Fruits (apples and an orange)
    draw.ellipse([bx - 20, by - 30, bx - 5, by - 10], fill=(180, 50, 50))
    draw.ellipse([bx + 5, by - 28, bx + 20, by - 8], fill=(100, 160, 80))
    draw.ellipse([bx - 5, by - 22, bx + 10, by - 2], fill=(220, 140, 40))

    # Place setting (empty plate)
    dx, dy = cx - 120, cy - 5
    draw.ellipse([dx - 30, dy - 30, dx + 30, dy + 30], fill=(220, 210, 195))
    draw.ellipse([dx - 30, dy - 30, dx + 30, dy + 30], outline=(180, 170, 155), width=1)
    # Fork and knife
    draw.line([dx - 40, dy - 10, dx - 45, dy + 25], fill=(180, 180, 190), width=3)
    draw.line([dx + 40, dy - 10, dx + 45, dy + 25], fill=(180, 180, 190), width=3)
    # Glass
    draw.rectangle([dx + 55, dy - 40, dx + 63, dy - 5], fill=(200, 210, 220, 100))
    draw.rectangle([dx + 53, dy - 45, dx + 65, dy - 40], fill=(180, 190, 200))


def draw_shadowed_figure(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a shadowed human figure standing in the background doorway."""
    cx = width // 2
    fy = int(height * 0.35)

    # Figure silhouette
    # Head
    draw.ellipse([cx - 20, fy - 50, cx + 20, fy - 10], fill=(20, 10, 25))
    # Body
    draw.polygon([(cx - 30, fy - 5), (cx + 30, fy - 5), (cx + 35, fy + 90), (cx - 35, fy + 90)], fill=(20, 10, 25))
    # Arms
    draw.line([cx - 30, fy + 5, cx - 55, fy + 40], fill=(20, 10, 25), width=8)
    draw.line([cx + 30, fy + 5, cx + 55, fy + 40], fill=(20, 10, 25), width=8)

    # Faint glow around figure
    for i in range(3):
        glow_alpha = 20 - i * 5
        draw.ellipse(
            [cx - 60 - i * 5, fy - 60 - i * 5, cx + 60 + i * 5, fy + 100 + i * 5],
            outline=(200, 180, 190, glow_alpha),
            width=2,
        )


def draw_doorway(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a rectangular darkened doorway frame behind the figure."""
    cx = width // 2
    door_top = int(height * 0.2)
    door_bottom = int(height * 0.6)
    door_left = cx - 100
    door_right = cx + 100

    # Door frame
    draw.rectangle([door_left, door_top, door_right, door_bottom], fill=(30, 15, 35))
    # Door frame outline
    draw.rectangle([door_left, door_top, door_right, door_bottom], outline=(60, 40, 55), width=4)
    # Door frame top
    draw.rectangle([door_left - 5, door_top - 8, door_right + 5, door_top], fill=(60, 40, 55))


def draw_empty_chair_foreground(draw: ImageDraw, width: int, height: int) -> None:
    """Draw an empty chair in the foreground, facing away."""
    cx = width // 2 + 120
    cy = int(height * 0.78)

    # Chair back (facing away from viewer)
    draw.rectangle([cx - 25, cy - 90, cx + 25, cy - 5], fill=(50, 30, 45))
    # Chair seat
    draw.rectangle([cx - 30, cy - 5, cx + 30, cy + 10], fill=(60, 40, 55))
    # Chair legs
    for lx in [cx - 28, cx + 28]:
        draw.rectangle([lx - 3, cy + 8, lx + 3, cy + 50], fill=(45, 25, 40))


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom of the cover."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark semi-transparent rectangle
    draw.rectangle([(0, panel_top), (width, height)], fill=(20, 10, 25, 220))

    # Add a subtle border at top of panel
    draw.line([(0, panel_top), (width, panel_top)], fill=(100, 70, 90), width=2)

    # Title text
    title = "The Vegetarian's\nWife"
    title_font_size = 80
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered
    lines = title.split("\n")
    y_offset = panel_top + 100
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 0
        tx = (width - tw) // 2
        draw.text((tx, y_offset), line, fill=(255, 255, 255), font=title_font)
        y_offset += 95

    # Author name
    author = "Barış Kısır"
    author_font_size = 36
    try:
        author_font = ImageFont.truetype(str(font_paths["author"]), author_font_size)
    except Exception:
        author_font = ImageFont.load_default()

    try:
        abbox = draw.textbbox((0, 0), author, font=author_font)
        aw = abbox[2] - abbox[0]
    except Exception:
        aw = 0
    ax = (width - aw) // 2
    ay = y_offset + 50
    draw.text((ax, ay), author, fill=(200, 180, 190), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Vegetarian's Wife")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Doorway frame
    draw_doorway(draw, WIDTH, HEIGHT)

    # Step 3: Shadowed figure
    draw_shadowed_figure(draw, WIDTH, HEIGHT)

    # Step 4: Empty dining table with bowl of fruit
    draw_empty_dining_table(draw, WIDTH, HEIGHT)

    # Step 5: Empty foreground chair
    draw_empty_chair_foreground(draw, WIDTH, HEIGHT)

    # Step 6: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arial.ttf"),
    }
    draw_title_panel(draw, WIDTH, HEIGHT, font_paths)

    # Soften the image slightly
    img = img.filter(ImageFilter.SMOOTH)

    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")



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