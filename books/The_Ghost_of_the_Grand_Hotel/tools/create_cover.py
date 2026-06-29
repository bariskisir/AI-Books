#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Ghost of the Grand Hotel."""

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
    """Dark teal-to-ivory gradient for the haunted hotel atmosphere."""
    for y in range(height):
        if y < height * 0.6:
            t = y / (height * 0.6)
            c = lerp_color((5, 25, 30), (15, 50, 55), t)
        else:
            t = (y - height * 0.6) / (height * 0.4)
            c = lerp_color((15, 50, 55), (210, 200, 185), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_hotel_facade(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the grand hotel facade with dome, wings, and lit windows."""
    cx = width // 2
    base_y = int(height * 0.55)

    # Central building
    cw, ch = 320, 280
    draw.rectangle([cx - cw // 2, base_y - ch, cx + cw // 2, base_y], fill=(25, 35, 40))

    # Central dome
    dome_top = base_y - ch - 60
    draw.ellipse([cx - 80, dome_top, cx + 80, dome_top + 100], fill=(30, 45, 50))
    draw.ellipse([cx - 40, dome_top - 30, cx + 40, dome_top + 30], fill=(35, 50, 55))

    # Left wing
    lw, lh = 200, 200
    draw.rectangle([cx - cw // 2 - lw, base_y - lh, cx - cw // 2, base_y], fill=(20, 30, 35))

    # Right wing
    draw.rectangle([cx + cw // 2, base_y - lh, cx + cw // 2 + lw, base_y], fill=(20, 30, 35))

    # Roof details on wings
    for wing_x in [cx - cw // 2 - lw, cx + cw // 2]:
        draw.rectangle([wing_x + 10, base_y - lh - 20, wing_x + 190, base_y - lh], fill=(25, 38, 42))
        # Small dormers
        for d in range(3):
            dx = wing_x + 20 + d * 60
            draw.rectangle([dx, base_y - lh - 40, dx + 30, base_y - lh - 10], fill=(30, 45, 50))

    # Windows on main building
    win_color = (180, 160, 120)
    for row in range(5):
        for col in range(7):
            wx = cx - cw // 2 + 20 + col * 42
            wy = base_y - ch + 20 + row * 50
            alpha = 120 if row < 3 and col % 2 == 0 else 60
            draw.rectangle([wx, wy, wx + 25, wy + 30], fill=win_color + (alpha,))

    # Windows on wings
    for wing_x in [cx - cw // 2 - lw, cx + cw // 2]:
        for row in range(3):
            for col in range(4):
                wx = wing_x + 15 + col * 45
                wy = base_y - lh + 20 + row * 55
                draw.rectangle([wx, wy, wx + 25, wy + 30], fill=win_color + (60,))

    # Entrance
    door_w, door_h = 60, 80
    draw.rectangle([cx - door_w // 2 - 5, base_y - door_h, cx + door_w // 2 + 5, base_y], fill=(40, 30, 20))
    # Door arch
    draw.ellipse([cx - door_w // 2 - 5, base_y - door_h - 20, cx + door_w // 2 + 5, base_y - door_h + 20], fill=(40, 30, 20))
    # Door light
    draw.ellipse([cx - 12, base_y - door_h - 8, cx + 12, base_y - door_h + 16], fill=(220, 200, 150, 100))

    # Columns at entrance
    for col_x in [cx - 35, cx + 35]:
        draw.rectangle([col_x - 3, base_y - door_h - 10, col_x + 3, base_y], fill=(50, 60, 65))

    # Balconies
    for bal_y in [base_y - ch + 60, base_y - ch + 130]:
        draw.line([(cx - 100, bal_y), (cx + 100, bal_y)], fill=(40, 55, 60), width=3)
        for pillar in range(5):
            px = cx - 100 + pillar * 50
            draw.rectangle([px, bal_y - 8, px + 4, bal_y], fill=(40, 55, 60))


def draw_lake_mountains(draw: ImageDraw, width: int, height: int) -> None:
    """Draw Lake Geneva and mountains in the background behind the hotel."""
    # Mountains
    for i, (mtn_x, mtn_h, mtn_w) in enumerate([
        (100, 60, 200), (350, 90, 180), (600, 50, 150),
        (900, 100, 220), (1200, 55, 160), (1450, 70, 190),
    ]):
        color = (60, 75, 85) if i % 2 == 0 else (70, 85, 95)
        draw.polygon([
            (mtn_x, int(height * 0.25)),
            (mtn_x + mtn_w // 2, int(height * 0.25) - mtn_h),
            (mtn_x + mtn_w, int(height * 0.25)),
        ], fill=color)

    # Lake surface
    lake_top = int(height * 0.25)
    lake_bottom = int(height * 0.42)
    for y in range(lake_top, lake_bottom):
        t = (y - lake_top) / (lake_bottom - lake_top)
        c = lerp_color((70, 85, 95), (20, 45, 55), t)
        draw.line([(0, y), (width, y)], fill=c)

    # Lake ripples
    for rx in range(100, width - 100, 80):
        for ry in range(lake_top + 20, lake_bottom - 10, 25):
            draw.line([(rx, ry), (rx + 40, ry - 2)], fill=(100, 130, 140, 40), width=1)


def draw_vintage_key(draw: ImageDraw, width: int, height: int) -> None:
    """Draw an ornate vintage key on the left side."""
    kx, ky = width // 2 - 280, int(height * 0.75)

    # Key shaft
    shaft_length = 120
    draw.line([(kx, ky), (kx + shaft_length, ky)], fill=(180, 160, 120), width=6)
    draw.line([(kx, ky + 8), (kx + shaft_length, ky + 8)], fill=(160, 140, 100), width=2)

    # Key bow (ornate top)
    bow_cx = kx
    bow_cy = ky - 30
    # Outer ring
    draw.ellipse([bow_cx - 25, bow_cy - 25, bow_cx + 25, bow_cy + 25], outline=(180, 160, 120), width=5)
    # Inner hole
    draw.ellipse([bow_cx - 10, bow_cy - 10, bow_cx + 10, bow_cy + 10], outline=(180, 160, 120), width=3)
    # Decorative notches on bow
    for angle in [45, 135, 225, 315]:
        rad = math.radians(angle)
        nx = bow_cx + int(22 * math.cos(rad))
        ny = bow_cy + int(22 * math.sin(rad))
        draw.ellipse([nx - 4, ny - 4, nx + 4, ny + 4], fill=(200, 180, 140))

    # Key teeth at the end
    tooth_start = kx + shaft_length - 30
    for t in range(3):
        tx = tooth_start + t * 12
        draw.rectangle([tx, ky + 8, tx + 4, ky + 22], fill=(180, 160, 120))
    # Bottom tooth
    draw.rectangle([tx, ky + 8, tx + 4, ky + 28], fill=(180, 160, 120))


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark title panel at the bottom with white text."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    draw.rectangle([(0, panel_top), (width, height)], fill=(10, 20, 25, 230))

    # Thin accent line at top of panel
    draw.line([(0, panel_top), (width, panel_top)], fill=(180, 160, 120), width=3)

    # Ornamental line below accent
    for x in range(200, width - 200, 40):
        draw.line([(x, panel_top + 15), (x + 20, panel_top + 15)], fill=(100, 130, 140, 80), width=1)

    # Title text - use arialbd.ttf (available)
    title = "The Ghost of\nthe Grand Hotel"
    title_font_size = 72
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    lines = title.split("\n")
    y_offset = panel_top + 80
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 0
        tx = (width - tw) // 2
        draw.text((tx, y_offset), line, fill=(255, 255, 255), font=title_font)
        y_offset += 85

    # Decorative divider
    div_y = y_offset - 45
    for x in range(width // 2 - 80, width // 2 + 80, 20):
        draw.line([(x, div_y), (x + 10, div_y)], fill=(180, 160, 120), width=1)

    # Author name
    author = "Barış Kısır"
    author_font_size = 32
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
    draw.text((ax, div_y + 30), author, fill=(200, 190, 170), font=author_font)

    # Room number detail
    room_text = "Room 307"
    room_font_size = 20
    try:
        room_font = ImageFont.truetype(str(font_paths["small"]), room_font_size)
    except Exception:
        room_font = ImageFont.load_default()
    try:
        rbbox = draw.textbbox((0, 0), room_text, font=room_font)
        rw = rbbox[2] - rbbox[0]
    except Exception:
        rw = 0
    draw.text(((width - rw) // 2, height - 50), room_text, fill=(120, 150, 155), font=room_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Ghost of the Grand Hotel")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Lake and mountains (behind hotel)
    draw_lake_mountains(draw, WIDTH, HEIGHT)

    # Step 3: Hotel facade
    draw_hotel_facade(draw, WIDTH, HEIGHT)

    # Step 4: Vintage key
    draw_vintage_key(draw, WIDTH, HEIGHT)

    # Step 5: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
        "small": str(FONTS_DIR / "arial.ttf"),
    }
    draw_title_panel(draw, WIDTH, HEIGHT, font_paths)

    # Soften slightly
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