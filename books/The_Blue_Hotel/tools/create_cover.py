#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Blue Hotel."""

from __future__ import annotations

import argparse
import json
import math
import random
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
    """Deep blue-gray to storm-dark gradient for the blizzard Western feel."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((20, 30, 50), ((40, 50, 75)), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((40, 50, 75), ((60, 65, 85)), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((60, 65, 85), ((25, 30, 45)), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_hotel(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a two-story frontier hotel in the blizzard."""
    cx, cy = width // 2, int(height * 0.38)
    hotel_w, hotel_h = 340, 280

    rng = random.Random(101)
    rng.seed(101)

    # Main building body
    draw.rectangle(
        [cx - hotel_w // 2, cy - hotel_h // 2, cx + hotel_w // 2, cy + hotel_h // 2],
        fill=(55, 50, 45),
    )

    # Roof line
    draw.polygon(
        [(cx - hotel_w // 2 - 20, cy - hotel_h // 2), (cx, cy - hotel_h // 2 - 50), (cx + hotel_w // 2 + 20, cy - hotel_h // 2)],
        fill=(40, 35, 30),
    )

    # Second floor windows (dark)
    for i in range(4):
        wx = cx - 120 + i * 75
        wy = cy - 80
        draw.rectangle([wx, wy, wx + 35, wy + 45], fill=(15, 15, 20))
        # Window frame
        draw.rectangle([wx, wy, wx + 35, wy + 45], outline=(80, 75, 70), width=2)

    # First floor windows (some lit)
    for i in range(3):
        wx = cx - 100 + i * 90
        wy = cy + 15
        if i == 0:
            draw.rectangle([wx, wy, wx + 40, wy + 55], fill=(180, 160, 100))
            # Warm glow
            for g in range(2):
                draw.rectangle(
                    [wx - g, wy - g, wx + 40 + g, wy + 55 + g],
                    outline=(180, 160, 100, 30),
                    width=1,
                )
        else:
            draw.rectangle([wx, wy, wx + 40, wy + 55], fill=(15, 15, 20))
        draw.rectangle([wx, wy, wx + 40, wy + 55], outline=(80, 75, 70), width=2)

    # Door
    door_x, door_y = cx - 15, cy + 40
    draw.rectangle([door_x, door_y, door_x + 30, door_y + 70], fill=(40, 35, 30))
    draw.rectangle([door_x + 22, door_y + 25, door_x + 28, door_y + 31], fill=(200, 180, 100))

    # Porch
    draw.rectangle(
        [cx - hotel_w // 2 - 30, cy + hotel_h // 2 - 10, cx + hotel_w // 2 + 30, cy + hotel_h // 2 + 10],
        fill=(50, 45, 40),
    )

    # Porch posts
    for p in range(-3, 4):
        px = cx + p * 80
        if abs(px - cx) > hotel_w // 2:
            continue
        draw.rectangle([px - 4, cy + hotel_h // 2 - 60, px + 4, cy + hotel_h // 2 + 5], fill=(50, 45, 40))

    # Porch roof
    draw.polygon(
        [(cx - hotel_w // 2 - 35, cy + hotel_h // 2 - 60), (cx, cy + hotel_h // 2 - 75), (cx + hotel_w // 2 + 35, cy + hotel_h // 2 - 60)],
        fill=(40, 35, 30),
    )

    # Sign
    sign_w, sign_h = 180, 35
    draw.rectangle(
        [cx - sign_w // 2, cy - hotel_h // 2 - 70, cx + sign_w // 2, cy - hotel_h // 2 - 35],
        fill=(45, 55, 95),
    )
    # Sign text placeholder
    try:
        sign_font = ImageFont.truetype(str(FONTS_DIR / "arial.ttf"), 20)
        draw.text((cx - 55, cy - hotel_h // 2 - 65), "BLUE HOTEL", fill=(200, 200, 210), font=sign_font)
    except Exception:
        pass


def draw_blizzard(draw: ImageDraw, width: int, height: int) -> None:
    """Draw falling snow and wind effects."""
    rng = random.Random(42)
    rng.seed(42)

    for _ in range(300):
        x = rng.randint(0, width)
        y = rng.randint(0, int(height * 0.8))
        size = rng.randint(1, 4)
        alpha = rng.randint(100, 220)
        draw.ellipse([x, y, x + size, y + size], fill=(220, 230, 255, alpha))

    # Wind streaks
    for _ in range(20):
        x = rng.randint(0, width)
        y = rng.randint(0, int(height * 0.7))
        length = rng.randint(30, 100)
        draw.line(
            [(x, y), (x + length, y - length // 3)],
            fill=(200, 210, 230, 40),
            width=1,
        )


def draw_poker_table(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a faint poker table in the lower portion, suggesting the saloon theme."""
    cx, cy = width // 2, int(height * 0.65)

    # Table surface (ellipse)
    draw.ellipse(
        [cx - 140, cy - 50, cx + 140, cy + 50],
        fill=(20, 60, 30),
        outline=(40, 80, 50),
        width=2,
    )

    # Chips
    rng = random.Random(77)
    rng.seed(77)
    chip_colors = [(200, 50, 50), (50, 50, 200), (200, 200, 50), (200, 200, 200)]
    for _ in range(12):
        cx_chip = cx + rng.randint(-100, 100)
        cy_chip = cy + rng.randint(-30, 30)
        color = chip_colors[rng.randint(0, 3)]
        draw.ellipse([cx_chip - 6, cy_chip - 6, cx_chip + 6, cy_chip + 6], fill=color)

    # Cards
    for i in range(3):
        cx_card = cx - 50 + i * 40
        cy_card = cy - 15
        draw.rectangle(
            [cx_card, cy_card, cx_card + 18, cy_card + 26],
            fill=(220, 215, 200),
            outline=(100, 95, 85),
            width=1,
        )


def draw_snow_ground(draw: ImageDraw, width: int, height: int) -> None:
    """Draw snow-covered ground at the bottom."""
    ground_top = int(height * 0.78)
    for y in range(ground_top, height):
        t = (y - ground_top) / (height - ground_top)
        c = lerp_color((180, 195, 210), ((200, 210, 225)), t)
        draw.line([(0, y), (width, y)], fill=c)

    # Snowdrifts
    for i in range(6):
        dx = i * 300 + random.randint(-50, 50)
        dy = ground_top + random.randint(-20, 20)
        draw.ellipse(
            [dx - 100, dy - 20, dx + 150, dy + 30],
            fill=(195, 210, 225, 100),
        )


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom of the cover with white text."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    draw.rectangle([(0, panel_top), (width, height)], fill=(15, 15, 25))

    # Subtle blue border at top
    draw.line([(0, panel_top), (width, panel_top)], fill=(45, 55, 95), width=3)

    # Title text
    title = "The Blue\nHotel"
    title_font_size = 78
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered in WHITE
    lines = title.split("\n")
    y_offset = panel_top + 70
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
    author_font_size = 42
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
    ay = y_offset + 30
    draw.text((ax, ay), author, fill=(180, 190, 220), font=author_font)

    # Genre line
    genre_text = "A Suspense Western"
    genre_font_size = 24
    try:
        genre_font = ImageFont.truetype(str(font_paths["small"]), genre_font_size)
    except Exception:
        genre_font = ImageFont.load_default()

    try:
        gbbox = draw.textbbox((0, 0), genre_text, font=genre_font)
        gw = gbbox[2] - gbbox[0]
    except Exception:
        gw = 0
    gx = (width - gw) // 2
    gy = ay + 55
    draw.text((gx, gy), genre_text, fill=(120, 130, 160), font=genre_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Blue Hotel")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Snow ground
    draw_snow_ground(draw, WIDTH, HEIGHT)

    # Step 3: Hotel in blizzard
    draw_hotel(draw, WIDTH, HEIGHT)

    # Step 4: Poker table suggestion
    draw_poker_table(draw, WIDTH, HEIGHT)

    # Step 5: Blizzard effects (snow + wind)
    draw_blizzard(draw, WIDTH, HEIGHT)

    # Step 6: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
        "small": str(FONTS_DIR / "arial.ttf"),
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