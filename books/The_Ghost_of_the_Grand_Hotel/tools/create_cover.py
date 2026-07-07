#!/usr/bin/env python3
"""Cover: The Ghost of the Grand Hotel — Dim corridor with old mirror, 1920s woman silhouette inside, gothic foggy ambience, dark wood/gold/ghost white."""

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
    """Dark wood/gold gradient for haunted hotel corridor."""
    for y in range(height):
        if y < height * 0.5:
            t = y / (height * 0.5)
            c = lerp_color((15, 10, 8), (30, 20, 15), t)
        else:
            t = (y - height * 0.5) / (height * 0.5)
            c = lerp_color((30, 20, 15), (60, 45, 30), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_mirror_scene(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a corridor with an ornate old mirror showing a woman silhouette."""
    cx = width // 2

    # Corridor walls — dark wood paneling
    wall_color = (25, 18, 12)
    draw.polygon([(0, 0), (cx - 200, 200), (cx - 200, 1200), (0, 1400)], fill=wall_color)
    draw.polygon([(width, 0), (cx + 200, 200), (cx + 200, 1200), (width, 1400)], fill=wall_color)

    # Floor
    for y in range(1200, 1800):
        t = (y - 1200) / 600
        r = int(30 + 20 * t)
        g = int(22 + 15 * t)
        b = int(15 + 10 * t)
        draw.line((0, y, width, y), fill=(r, g, b))

    # Ceiling
    for y in range(0, 200):
        t = y / 200
        r = int(10 + 15 * t)
        g = int(8 + 12 * t)
        b = int(6 + 10 * t)
        draw.line((0, y, width, y), fill=(r, g, b))

    # Ornate mirror frame — gold, oval
    mirror_cx, mirror_cy = cx, 550
    mirror_rx, mirror_ry = 150, 220

    # Frame outer
    draw.ellipse((mirror_cx - mirror_rx - 15, mirror_cy - mirror_ry - 15,
                  mirror_cx + mirror_rx + 15, mirror_cy + mirror_ry + 15),
                 fill=(60, 45, 20, 200), outline=(140, 110, 60, 220), width=6)
    # Frame inner
    draw.ellipse((mirror_cx - mirror_rx - 5, mirror_cy - mirror_ry - 5,
                  mirror_cx + mirror_rx + 5, mirror_cy + mirror_ry + 5),
                 fill=(80, 60, 30, 200), outline=(180, 150, 80, 200), width=3)

    # Mirror surface — dark reflective
    draw.ellipse((mirror_cx - mirror_rx, mirror_cy - mirror_ry,
                  mirror_cx + mirror_rx, mirror_cy + mirror_ry),
                 fill=(160, 150, 130, 100))

    # 1920s woman silhouette INSIDE the mirror
    woman_color = (20, 15, 12, 200)
    wx, wy = mirror_cx, mirror_cy + 40
    # Flapper dress silhouette
    draw.polygon([
        (wx - 30, wy - 30), (wx + 30, wy - 30),
        (wx + 45, wy + 60), (wx - 45, wy + 60),
    ], fill=woman_color)
    # Head
    draw.ellipse((wx - 15, wy - 70, wx + 15, wy - 40), fill=woman_color)
    # Cloche hat
    draw.ellipse((wx - 20, wy - 80, wx + 20, wy - 55), fill=woman_color)
    # Headband / fringe
    draw.ellipse((wx - 12, wy - 55, wx + 12, wy - 48), fill=(100, 80, 50, 200))

    # Mirror reflection highlights
    draw.arc((mirror_cx - mirror_rx + 10, mirror_cy - mirror_ry + 10,
              mirror_cx + mirror_rx - 10, mirror_cy + mirror_ry - 10),
             30, 150, fill=(200, 200, 210, 40), width=2)

    # Sconces on walls with candle glow
    for sc_x in [cx - 250, cx + 250]:
        sc_y = 450
        draw.polygon([(sc_x - 5, sc_y), (sc_x + 5, sc_y), (sc_x, sc_y - 30)], fill=(180, 150, 80, 180))
        for r in range(40, 5, -5):
            alpha = max(0, 30 - (40 - r) // 2)
            draw.ellipse((sc_x - r, sc_y - 40 - r, sc_x + r, sc_y - 40 + r), fill=(200, 160, 80, alpha))

    # Gothic fog
    for fy in range(600, 1400, 30):
        fx = int(width * 0.2 + math.sin(fy * 0.03) * 100)
        draw.ellipse((fx, fy, fx + 200, fy + 40), fill=(180, 180, 190, 20))


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
    room_text = "Room 1925"
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

    # Step 2: Mirror scene with corridor and woman silhouette
    draw_mirror_scene(draw, WIDTH, HEIGHT)

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