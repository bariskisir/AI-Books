#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Dead Letter Office."""

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
    """Warm brown to cream gradient for the dead letter office feel."""
    for y in range(height):
        if y < height * 0.5:
            t = y / (height * 0.5)
            c = lerp_color((60, 40, 30), (120, 90, 60), t)
        else:
            t = (y - height * 0.5) / (height * 0.5)
            c = lerp_color((120, 90, 60), (200, 180, 160), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_shelves(draw: ImageDraw, width: int, height: int) -> None:
    """Draw rows of mail shelves along the left and right edges."""
    shelf_color = (80, 55, 35)
    # Left shelves
    for row in range(8):
        y_start = int(height * 0.05) + row * 80
        # Shelf plank
        draw.rectangle([20, y_start, 280, y_start + 8], fill=shelf_color)
        # Vertical dividers
        for v in range(5):
            vx = 20 + v * 52
            draw.rectangle([vx, y_start - 60, vx + 4, y_start], fill=shelf_color)
        # Letters on shelf
        for l in range(4):
            lx = 30 + l * 60
            ly = y_start - 50
            env_w, env_h = 40, 28
            draw.rectangle([lx, ly, lx + env_w, ly + env_h], fill=(220, 200, 170))
            draw.rectangle([lx + 2, ly + 2, lx + env_w - 2, ly + env_h - 2], fill=(240, 225, 200), outline=(180, 160, 130))

    # Right shelves
    for row in range(8):
        y_start = int(height * 0.05) + row * 80
        draw.rectangle([width - 280, y_start, width - 20, y_start + 8], fill=shelf_color)
        for v in range(5):
            vx = width - 280 + v * 52
            draw.rectangle([vx, y_start - 60, vx + 4, y_start], fill=shelf_color)
        for l in range(4):
            lx = width - 270 + l * 60
            ly = y_start - 50
            env_w, env_h = 40, 28
            draw.rectangle([lx, ly, lx + env_w, ly + env_h], fill=(220, 200, 170))
            draw.rectangle([lx + 2, ly + 2, lx + env_w - 2, ly + env_h - 2], fill=(240, 225, 200), outline=(180, 160, 130))


def draw_sorting_desk(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a central sorting desk with scattered letters."""
    cx, cy = width // 2, int(height * 0.55)
    desk_w, desk_h = 500, 200

    # Desk surface
    draw.rectangle([cx - desk_w // 2, cy - desk_h // 2, cx + desk_w // 2, cy + desk_h // 2], fill=(90, 60, 40))
    draw.rectangle([cx - desk_w // 2 + 5, cy - desk_h // 2 + 5, cx + desk_w // 2 - 5, cy + desk_h // 2 - 5], fill=(110, 75, 50))

    # Scattered letters on desk
    letter_positions = [
        (cx - 150, cy - 50, 0),
        (cx - 50, cy - 30, 15),
        (cx + 40, cy - 60, -10),
        (cx + 120, cy - 20, 5),
        (cx - 100, cy + 20, -5),
        (cx + 60, cy + 10, 20),
    ]
    for lx, ly, angle in letter_positions:
        env_w, env_h = 55, 38
        rect = Image.new("RGBA", (env_w, env_h), (230, 210, 185, 220))
        rdraw = ImageDraw.Draw(rect)
        rdraw.rectangle([0, 0, env_w - 1, env_h - 1], fill=(230, 210, 185), outline=(160, 130, 100))
        # Stamp
        rdraw.rectangle([env_w - 22, 4, env_w - 5, 17], fill=(180, 100, 80))
        # Address lines
        rdraw.line([(8, 12), (env_w - 28, 12)], fill=(100, 80, 60), width=1)
        rdraw.line([(8, 18), (env_w - 28, 18)], fill=(100, 80, 60), width=1)
        rdraw.line([(8, 24), (env_w - 28, 24)], fill=(100, 80, 60), width=1)
        rotated = rect.rotate(angle, expand=True, resample=Image.BICUBIC)
        draw_img = ImageDraw.Draw(img)
        img.paste(rotated, (lx, ly), rotated)

    # Letter opener on desk
    opener_x = cx + 180
    opener_y = cy + 40
    draw.line(
        [(opener_x, opener_y), (opener_x + 60, opener_y - 15)],
        fill=(180, 160, 140), width=4,
    )
    draw.ellipse([opener_x - 3, opener_y - 3, opener_x + 3, opener_y + 3], fill=(180, 160, 140))

    # Stack of sorted letters
    for i in range(8):
        sx = cx - 200 + i * 2
        sy = cy + 50 - i * 3
        stack_w, stack_h = 50, 35
        draw.rectangle([sx, sy, sx + stack_w, sy + stack_h], fill=(235 - i * 5, 215 - i * 5, 190 - i * 5), outline=(150, 120, 90))


def draw_scattered_envelopes_floor(draw: ImageDraw, width: int, height: int) -> None:
    """Draw scattered envelopes on the floor at the bottom of the scene."""
    import random

    rng = random.Random(77)
    for _ in range(30):
        lx = rng.randint(50, width - 50)
        ly = rng.randint(int(height * 0.68), int(height * 0.72))
        env_w, env_h = 35, 25
        angle = rng.randint(-30, 30)
        rect = Image.new("RGBA", (env_w, env_h), (210, 190, 165, 150))
        rdraw = ImageDraw.Draw(rect)
        rdraw.rectangle([0, 0, env_w - 1, env_h - 1], fill=(210, 190, 165), outline=(160, 130, 100))
        # Stamp smudge
        rdraw.rectangle([env_w - 18, 3, env_w - 5, 14], fill=(170, 90, 70))
        rotated = rect.rotate(angle, expand=True, resample=Image.BICUBIC)
        img.paste(rotated, (lx, ly), rotated)


def draw_lamp(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a desk lamp casting a warm glow over the sorting desk."""
    cx = width // 2 + 200
    cy = int(height * 0.35)

    # Lamp base
    draw.ellipse([cx - 15, cy + 60, cx + 15, cy + 80], fill=(60, 50, 40))

    # Lamp arm
    draw.line([(cx, cy + 60), (cx - 40, cy - 20)], fill=(60, 50, 40), width=6)

    # Lamp shade
    draw.polygon(
        [(cx - 50, cy - 40), (cx - 20, cy + 10), (cx + 20, cy + 10), (cx + 50, cy - 40)],
        fill=(50, 80, 60),
    )

    # Light glow
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse(
        [cx - 250, cy - 100, cx + 200, cy + 200],
        fill=(255, 230, 180, 20),
    )
    gdraw.ellipse(
        [cx - 150, cy - 50, cx + 100, cy + 150],
        fill=(255, 230, 180, 12),
    )
    img.paste(glow, (0, 0), glow)


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom of the cover."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark rectangle
    draw.rectangle([(0, panel_top), (width, height)], fill=(45, 35, 30, 230))

    # Subtle border at top of panel
    draw.line([(0, panel_top), (width, panel_top)], fill=(120, 90, 60), width=3)

    # Title text - use arialbd.ttf
    title = "The Dead\nLetter Office"
    title_font_size = 76
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    lines = title.split("\n")
    y_offset = panel_top + 100
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 0
        tx = (width - tw) // 2
        # White text
        draw.text((tx, y_offset), line, fill=(255, 255, 255), font=title_font)
        y_offset += 100

    # Subtitle line
    subtitle = "An Epistolary Mystery"
    sub_font_size = 30
    try:
        sub_font = ImageFont.truetype(str(font_paths["subtitle"]), sub_font_size)
    except Exception:
        sub_font = ImageFont.load_default()

    try:
        sbbox = draw.textbbox((0, 0), subtitle, font=sub_font)
        sw = sbbox[2] - sbbox[0]
    except Exception:
        sw = 0
    sx = (width - sw) // 2
    draw.text((sx, y_offset + 10), subtitle, fill=(200, 180, 160), font=sub_font)

    # Author name - white
    author = "Barış Kısır"
    author_font_size = 34
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
    ay = y_offset + 80
    draw.text((ax, ay), author, fill=(255, 255, 255), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    global img
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Dead Letter Office")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Mail shelves along edges
    draw_shelves(draw, WIDTH, HEIGHT)

    # Step 3: Central sorting desk
    draw_sorting_desk(draw, WIDTH, HEIGHT)

    # Step 4: Floor envelopes
    draw_scattered_envelopes_floor(draw, WIDTH, HEIGHT)

    # Step 5: Desk lamp with glow
    draw_lamp(draw, WIDTH, HEIGHT)

    # Step 6: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
        "subtitle": str(FONTS_DIR / "arial.ttf"),
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