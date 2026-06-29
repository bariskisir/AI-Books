#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The House of Many Windows."""

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
    """Sky blue to concrete gray to dark gradient for brutalist feel."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((135, 175, 210), (160, 165, 170), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((160, 165, 170), (110, 115, 120), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((110, 115, 120), (55, 58, 62), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_city_skyline(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a silhouette city skyline in the lower background."""
    rng = random.Random(42)
    base_y = int(height * 0.75)
    buildings = []

    # Generate building blocks
    x = 0
    while x < width:
        bw = rng.randint(40, 120)
        bh = rng.randint(60, 200)
        bx = x
        by = base_y - bh
        buildings.append((bx, by, bw, bh))
        x += bw + rng.randint(5, 20)

    # Draw buildings as dark silhouettes
    for bx, by, bw, bh in buildings:
        draw.rectangle([bx, by, bx + bw, base_y], fill=(35, 38, 42))
        # Window dots on some buildings
        if rng.random() < 0.6:
            for wy in range(by + 10, base_y - 10, 20):
                for wx in range(bx + 8, bx + bw - 8, 18):
                    if rng.random() < 0.5:
                        draw.rectangle([wx, wy, wx + 4, wy + 4], fill=(180, 180, 140, 120))


def draw_blueprint_lines(draw: ImageDraw, width: int, height: int) -> None:
    """Draw faint blueprint grid lines across the upper portion."""
    # Grid lines
    for x in range(0, width, 60):
        draw.line([(x, 0), (x, int(height * 0.7))], fill=(70, 120, 180, 30), width=1)
    for y in range(0, int(height * 0.7), 60):
        draw.line([(0, y), (width, y)], fill=(70, 120, 180, 30), width=1)

    # Faint dimension lines
    for i in range(5):
        lx = 100 + i * 350
        draw.line([(lx, 50), (lx, int(height * 0.3))], fill=(70, 120, 180, 20), width=1)
        draw.line([(lx + 30, 50), (lx + 30, int(height * 0.3))], fill=(70, 120, 180, 20), width=1)


def draw_tower(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a brutalist concrete tower as the focal point."""
    cx = width // 2
    tw = 180  # tower width
    th = int(height * 0.6)  # tower height
    ty = int(height * 0.2)  # tower top y

    # Main tower body — concrete gray
    tower_color = (145, 150, 155)
    draw.rectangle([cx - tw // 2, ty, cx + tw // 2, ty + th], fill=tower_color)

    # Vertical concrete ribs
    for rx in range(cx - tw // 2 + 15, cx + tw // 2, 30):
        draw.rectangle([rx, ty, rx + 4, ty + th], fill=(130, 135, 140))

    # Horizontal floor lines
    for fy in range(ty + 30, ty + th, 40):
        draw.line([(cx - tw // 2, fy), (cx + tw // 2, fy)], fill=(120, 125, 130), width=2)

    # Windows — small rectangles, irregular pattern
    rng = random.Random(17)
    for fy in range(ty + 50, ty + th - 20, 40):
        for fx in range(cx - tw // 2 + 20, cx + tw // 2 - 20, 28):
            if rng.random() < 0.7:
                ww = rng.randint(10, 16)
                wh = rng.randint(18, 26)
                # Slight tilt for the surveillance effect
                wx = fx + rng.randint(-3, 3)
                draw.rectangle([wx, fy, wx + ww, fy + wh], fill=(180, 190, 200))
                # Glass tint
                draw.rectangle([wx + 2, fy + 2, wx + ww - 2, fy + wh - 2], fill=(160, 180, 200, 80))
                # Warmth glow (active lenses)
                if rng.random() < 0.3:
                    draw.rectangle([wx, fy, wx + ww, fy + wh], fill=(255, 220, 100, 40))

    # Penthouse at top — glassier
    ph = 50
    draw.rectangle([cx - tw // 2, ty - 10, cx + tw // 2, ty - 10 + ph], fill=(80, 90, 100))
    for gx in range(cx - tw // 2 + 10, cx + tw // 2 - 10, 30):
        draw.rectangle([gx, ty - 5, gx + 20, ty - 10 + ph - 5], fill=(100, 140, 180, 120))

    # Ground-level entrance
    entrance_w = 40
    entrance_h = 50
    draw.rectangle(
        [cx - entrance_w // 2, ty + th - entrance_h, cx + entrance_w // 2, ty + th],
        fill=(50, 55, 60),
    )

    # Plaza / platform at base
    plaza_y = ty + th
    draw.rectangle([cx - 300, plaza_y, cx + 300, plaza_y + 15], fill=(130, 135, 140))
    draw.rectangle([cx - 300, plaza_y + 15, cx + 300, plaza_y + 20], fill=(110, 115, 120))


def draw_lens_lines(draw: ImageDraw, width: int, height: int) -> None:
    """Draw sightlines / lens rays from the tower windows outward."""
    cx = width // 2
    tower_right = cx + 90  # right edge of tower
    tower_left = cx - 90

    rng = random.Random(31)

    # Rays emanating from the tower toward the city
    for _ in range(30):
        start_x = rng.randint(tower_left + 10, tower_right - 10)
        start_y = rng.randint(int(height * 0.25), int(height * 0.7))
        angle = rng.uniform(-0.4, 0.4)
        length = rng.randint(200, 600)
        end_x = int(start_x + math.cos(angle) * length)
        end_y = int(start_y - abs(angle) * length * 0.5)

        # Faint line
        draw.line(
            [(start_x, start_y), (end_x, end_y)],
            fill=(255, 220, 100, 20),
            width=1,
        )

        # Small lens flare circles
        if rng.random() < 0.3:
            flare_x = (start_x + end_x) // 2
            flare_y = (start_y + end_y) // 2
            draw.ellipse(
                [flare_x - 4, flare_y - 4, flare_x + 4, flare_y + 4],
                fill=(255, 255, 200, 30),
            )


def draw_compass_rose(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a faint architectural compass rose in the upper right."""
    cx = width - 120
    cy = 120
    r = 50

    # Outer circle
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(70, 120, 180, 40), width=2)

    # Cross lines
    draw.line([(cx - r - 10, cy), (cx + r + 10, cy)], fill=(70, 120, 180, 40), width=1)
    draw.line([(cx, cy - r - 10), (cx, cy + r + 10)], fill=(70, 120, 180, 40), width=1)

    # Diagonal lines
    for angle in [45, 135]:
        rad = math.radians(angle)
        dx = int(math.cos(rad) * (r + 10))
        dy = int(math.sin(rad) * (r + 10))
        draw.line([(cx - dx, cy - dy), (cx + dx, cy + dy)], fill=(70, 120, 180, 30), width=1)

    # N label
    draw.text((cx - 5, cy - r - 20), "N", fill=(70, 120, 180, 50), font=ImageFont.load_default())


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark title panel at the bottom of the cover with white text."""
    panel_top = TITLE_PANEL_TOP

    # Panel background — dark semi-transparent
    draw.rectangle([(0, panel_top), (width, height)], fill=(25, 28, 32, 220))

    # Top accent line
    draw.line([(0, panel_top), (width, panel_top)], fill=(180, 150, 100), width=3)

    # Subtle horizontal rule below accent
    draw.line([(200, panel_top + 15), (width - 200, panel_top + 15)], fill=(70, 72, 76), width=1)

    # Title text using arialbd.ttf
    title = "The House of\nMany Windows"
    title_font_size = 76
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    lines = title.split("\n")
    y_offset = panel_top + 60
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 0
        tx = (width - tw) // 2
        draw.text((tx, y_offset), line, fill=(255, 255, 255), font=title_font)
        y_offset += 90

    # Author name using arial.ttf
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
    ay = y_offset + 30
    draw.text((ax, ay), author, fill=(200, 200, 200), font=author_font)

    # Small decorative line under author
    draw.line(
        [(width // 2 - 40, ay + 45), (width // 2 + 40, ay + 45)],
        fill=(140, 120, 80),
        width=1,
    )


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The House of Many Windows")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background (sky blue to concrete gray)
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Blueprint grid lines
    draw_blueprint_lines(draw, WIDTH, HEIGHT)

    # Step 3: City skyline silhouettes
    draw_city_skyline(draw, WIDTH, HEIGHT)

    # Step 4: Brutalist tower focal point
    draw_tower(draw, WIDTH, HEIGHT)

    # Step 5: Lens sightlines from tower
    draw_lens_lines(draw, WIDTH, HEIGHT)

    # Step 6: Compass rose
    draw_compass_rose(draw, WIDTH, HEIGHT)

    # Step 7: Title panel at bottom (arialbd.ttf for title, white text on dark)
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