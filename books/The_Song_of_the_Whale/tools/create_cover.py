#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Song of the Whale."""

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
    """Deep ocean gradient: surface blue to abyssal black."""
    for y in range(height):
        if y < height * 0.3:
            t = y / (height * 0.3)
            c = lerp_color((10, 60, 90), ((5, 30, 70)), t)
        elif y < height * 0.6:
            t = (y - height * 0.3) / (height * 0.3)
            c = lerp_color((5, 30, 70), ((3, 10, 40)), t)
        else:
            t = (y - height * 0.6) / (height * 0.4)
            c = lerp_color((3, 10, 40), ((1, 5, 20)), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_ocean_surface(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a stylized ocean wave line at the surface."""
    surface_y = int(height * 0.25)
    points = []
    for x in range(0, width, 2):
        wave = math.sin(x * 0.02) * 15 + math.sin(x * 0.04) * 8 + math.sin(x * 0.01) * 10
        points.append((x, surface_y + wave))
    draw.line(points, fill=(180, 220, 255, 150), width=3)
    # Second wave layer
    points2 = []
    for x in range(0, width, 2):
        wave = math.sin(x * 0.025 + 1.5) * 12 + math.sin(x * 0.05 + 0.5) * 6
        points2.append((x, surface_y + 25 + wave))
    draw.line(points2, fill=(120, 180, 220, 100), width=2)


def draw_whale_breach(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a stylized whale breaching from the water."""
    cx = width // 2
    base_y = int(height * 0.28)

    # Whale body - curved arc shape
    body_points = []
    for t in range(0, 180, 2):
        rad = math.radians(t)
        x = cx - 200 * math.cos(rad) * 0.5
        y = base_y - 120 * math.sin(rad) + 80 * math.cos(rad * 1.5)
        body_points.append((x, y))

    if len(body_points) > 2:
        draw.line(body_points, fill=(180, 200, 220), width=25)
        # Highlight on the back
        highlight = []
        for t in range(10, 160, 3):
            rad = math.radians(t)
            x = cx - 190 * math.cos(rad) * 0.5
            y = base_y - 115 * math.sin(rad) + 78 * math.cos(rad * 1.5)
            highlight.append((x, y))
        if len(highlight) > 2:
            draw.line(highlight, fill=(220, 235, 250), width=8)

    # Tail flukes
    tail_x = cx - 85
    tail_y = base_y + 40
    draw.polygon(
        [(tail_x, tail_y), (tail_x - 60, tail_y - 30), (tail_x - 50, tail_y + 10), (tail_x - 60, tail_y + 35)],
        fill=(160, 185, 210),
    )

    # Pectoral fin
    fin_x = cx + 40
    fin_y = base_y - 20
    draw.polygon(
        [(fin_x, fin_y), (fin_x + 50, fin_y + 30), (fin_x + 35, fin_y + 5)],
        fill=(150, 175, 200),
    )

    # Eye
    eye_x = cx + 80
    eye_y = base_y - 60
    draw.ellipse([eye_x - 4, eye_y - 4, eye_x + 4, eye_y + 4], fill=(40, 50, 70))

    # Spray from blowhole
    spray_x = cx + 30
    spray_y = base_y - 115
    for i in range(20):
        sx = spray_x + random.randint(-30, 30)
        sy = spray_y - random.randint(10, 60)
        size = random.randint(3, 8)
        alpha = random.randint(60, 180)
        draw.ellipse([sx - size, sy - size, sx + size, sy + size], fill=(200, 230, 255, alpha))


def draw_hydrophone(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a hydrophone descending from the left side."""
    start_x = 120
    start_y = int(height * 0.22)

    # Cable
    cable_points = []
    for y in range(start_y, int(height * 0.55), 5):
        offset = math.sin(y * 0.02) * 15
        cable_points.append((start_x + offset, y))
    draw.line(cable_points, fill=(120, 140, 160), width=3)

    # Hydrophone body
    hp_y = int(height * 0.55)
    # Metal casing
    draw.rectangle([start_x - 10, hp_y, start_x + 10, hp_y + 40], fill=(140, 160, 180))
    draw.rectangle([start_x - 8, hp_y + 5, start_x + 8, hp_y + 35], fill=(100, 120, 140))
    # Ceramic disc
    draw.ellipse([start_x - 15, hp_y + 40, start_x + 15, hp_y + 55], fill=(180, 195, 210))
    # Piezoelectric element
    draw.ellipse([start_x - 8, hp_y + 43, start_x + 8, hp_y + 52], fill=(200, 215, 230))

    # Sound waves emanating from hydrophone
    for i in range(3):
        radius = 30 + i * 25
        draw.ellipse(
            [start_x - radius, hp_y + 47 - radius, start_x + radius, hp_y + 47 + radius],
            outline=(100, 180, 220, 80 - i * 20),
            width=2,
        )


def draw_sound_waves(draw: ImageDraw, width: int, height: int) -> None:
    """Draw abstract sound wave patterns across the deep ocean section."""
    rng = random.Random(12)
    for _ in range(15):
        x = rng.randint(300, width - 100)
        y = rng.randint(int(height * 0.35), int(height * 0.65))
        amplitude = rng.randint(10, 30)
        wavelength = rng.randint(40, 100)
        points = []
        for i in range(-2, 3):
            px = x + i * wavelength * 0.5
            py = y + math.sin(i * 0.8) * amplitude
            points.append((px, py))
        alpha = rng.randint(30, 80)
        if len(points) > 2:
            draw.line(points, fill=(80, 160, 220, alpha), width=rng.randint(1, 3))


def draw_bioluminescence(draw: ImageDraw, width: int, height: int) -> None:
    """Draw small bioluminescent particles in the deep water."""
    rng = random.Random(42)
    for _ in range(80):
        x = rng.randint(50, width - 50)
        y = rng.randint(int(height * 0.3), int(height * 0.75))
        size = rng.randint(2, 5)
        brightness = rng.randint(100, 220)
        glow = (brightness, brightness, 255, 60)
        center = (brightness, brightness, 255, 180)
        draw.ellipse([x - size * 2, y - size * 2, x + size * 2, y + size * 2], fill=glow)
        draw.ellipse([x - size // 2, y - size // 2, x + size // 2, y + size // 2], fill=center)


def draw_fish_silhouettes(draw: ImageDraw, width: int, height: int) -> None:
    """Draw small fish silhouettes swimming in the deep."""
    rng = random.Random(99)
    for _ in range(12):
        x = rng.randint(200, width - 200)
        y = rng.randint(int(height * 0.35), int(height * 0.6))
        length = rng.randint(15, 35)
        direction = 1 if rng.random() < 0.5 else -1
        # Body (ensure x0 < x1)
        x0 = min(x, x + length * direction)
        x1 = max(x, x + length * direction)
        draw.ellipse(
            [x0, y - length // 4, x1, y + length // 4],
            fill=(40, 60, 80, 120),
        )
        # Tail
        tail_x = x + length * direction
        draw.polygon(
            [(tail_x, y), (tail_x + 10 * direction, y - 8), (tail_x + 10 * direction, y + 8)],
            fill=(40, 60, 80, 120),
        )


def draw_title_panel(draw: ImageDraw, draw_img: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom of the cover with WHITE text."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark semi-transparent rectangle
    draw.rectangle([(0, panel_top), (width, height)], fill=(5, 10, 30, 220))

    # Subtle silver border at top of panel
    draw.line([(0, panel_top), (width, panel_top)], fill=(100, 140, 180), width=3)

    # Title text - use arialbd.ttf
    title = "The Song\nof the Whale"
    title_font_size = 72
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
        y_offset += 90

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
    ay = y_offset + 30
    draw.text((ax, ay), author, fill=(180, 200, 230), font=author_font)

    # Decorative line below author
    line_y = ay + 45
    line_width = 120
    draw.line(
        [(width // 2 - line_width // 2, line_y), (width // 2 + line_width // 2, line_y)],
        fill=(100, 140, 180, 150),
        width=2,
    )


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Song of the Whale")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Ocean surface
    draw_ocean_surface(draw, WIDTH, HEIGHT)

    # Step 3: Whale breach
    draw_whale_breach(draw, WIDTH, HEIGHT)

    # Step 4: Hydrophone
    draw_hydrophone(draw, WIDTH, HEIGHT)

    # Step 5: Sound waves
    draw_sound_waves(draw, WIDTH, HEIGHT)

    # Step 6: Bioluminescence
    draw_bioluminescence(draw, WIDTH, HEIGHT)

    # Step 7: Fish silhouettes
    draw_fish_silhouettes(draw, WIDTH, HEIGHT)

    # Step 8: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
        "small": str(FONTS_DIR / "arial.ttf"),
    }
    draw_title_panel(draw, draw, WIDTH, HEIGHT, font_paths)

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