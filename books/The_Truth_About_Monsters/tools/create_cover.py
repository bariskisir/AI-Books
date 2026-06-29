#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Truth About Monsters."""

from __future__ import annotations

import argparse
import json
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
    """Deep purple to warm gold gradient for a cozy nighttime feel."""
    for y in range(height):
        if y < height * 0.45:
            t = y / (height * 0.45)
            c = lerp_color((25, 10, 45), ((80, 30, 80)), t)
        elif y < height * 0.7:
            t = (y - height * 0.45) / (height * 0.25)
            c = lerp_color((80, 30, 80), ((120, 60, 100)), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((120, 60, 100), ((180, 130, 80)), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_bedroom(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a child's bedroom at night with bed, nightlight, and window."""
    # Floor
    draw.rectangle([(0, int(height * 0.7)), (width, height)], fill=(60, 35, 25))

    # Wall - bottom half
    draw.rectangle([(0, int(height * 0.3)), (width, int(height * 0.7))], fill=(70, 45, 55))

    # Wall - top half
    draw.rectangle([(0, 0), (width, int(height * 0.3))], fill=(45, 25, 50))

    # Window with moonlight
    wx, wy = width // 2 - 100, int(height * 0.08)
    draw.rectangle([(wx, wy), (wx + 200, wy + 260)], fill=(180, 200, 220, 60))
    draw.rectangle([(wx, wy), (wx + 200, wy + 260)], outline=(100, 80, 100), width=3)
    # Window cross
    draw.line([(wx + 100, wy), (wx + 100, wy + 260)], fill=(80, 60, 80), width=3)
    draw.line([(wx, wy + 130), (wx + 200, wy + 130)], fill=(80, 60, 80), width=3)

    # Moon through window
    mx, my = wx + 140, wy + 60
    draw.ellipse([(mx - 25, my - 25), (mx + 25, my + 25)], fill=(220, 220, 200, 80))
    draw.ellipse([(mx + 8, my - 20), (mx + 20, my + 5)], fill=(70, 45, 55))

    # Bed frame
    bx, by = width // 2 - 180, int(height * 0.42)
    bw, bh = 360, 220
    # Headboard
    draw.rectangle([(bx, by - 30), (bx + 30, by + bh)], fill=(50, 30, 25))
    # Footboard
    draw.rectangle([(bx + bw - 30, by), (bx + bw, by + bh)], fill=(50, 30, 25))
    # Bed base
    draw.rectangle([(bx + 30, by), (bx + bw - 30, by + bh)], fill=(80, 55, 45))
    # Mattress
    draw.rectangle([(bx + 30, by - 10), (bx + bw - 30, by + bh - 60)], fill=(100, 80, 70))
    # Blanket
    draw.rectangle([(bx + 35, by + 60), (bx + bw - 35, by + bh - 60)], fill=(120, 40, 60))

    # Pillow
    draw.ellipse([(bx + 45, by + 10), (bx + 120, by + 55)], fill=(180, 170, 160))

    # Elodie (sleeping girl - just a suggestion under the blanket)
    # Head on pillow
    draw.ellipse([(bx + 55, by + 15), (bx + 105, by + 50)], fill=(220, 190, 170))
    # Hair
    draw.ellipse([(bx + 50, by + 10), (bx + 110, by + 40)], fill=(60, 35, 25))


def draw_nightlight(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a glowing nightlight on the wall or nightstand."""
    nx, ny = int(width * 0.78), int(height * 0.5)
    # Nightstand
    draw.rectangle([(nx - 30, ny + 20), (nx + 30, ny + 60)], fill=(55, 35, 30))
    draw.rectangle([(nx - 35, ny + 60), (nx + 35, ny + 65)], fill=(45, 25, 20))

    # Nightlight body (crescent moon shape)
    draw.ellipse([(nx - 15, ny - 5), (nx + 15, ny + 25)], fill=(255, 200, 80))
    draw.ellipse([(nx - 5, ny), (nx + 10, ny + 20)], fill=(255, 220, 120))

    # Glow effect
    for r in range(20, 60, 10):
        alpha = max(5, 30 - r)
        draw.ellipse([(nx - r, ny - r + 10), (nx + r, ny + r + 10)], fill=(255, 200, 80, alpha))


def draw_monster(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a friendly furry monster peeking from under the bed."""
    bx = width // 2 - 180
    by = int(height * 0.42)
    bh = 220

    # Monster body under the bed
    mx = bx + 180
    my = by + bh - 30

    # Main body (partially visible from under bed)
    draw.ellipse([(mx - 100, my - 20), (mx + 100, my + 80)], fill=(80, 50, 100))
    draw.ellipse([(mx - 90, my - 15), (mx + 90, my + 75)], fill=(100, 65, 120))
    draw.ellipse([(mx - 80, my - 10), (mx + 80, my + 70)], fill=(120, 80, 140))

    # Head
    draw.ellipse([(mx - 65, my - 55), (mx + 65, my + 25)], fill=(140, 95, 160))

    # Ears
    draw.ellipse([(mx - 55, my - 80), (mx - 20, my - 45)], fill=(130, 85, 150))
    draw.ellipse([(mx + 20, my - 80), (mx + 55, my - 45)], fill=(130, 85, 150))
    draw.ellipse([(mx - 48, my - 73), (mx - 27, my - 52)], fill=(160, 110, 175))
    draw.ellipse([(mx + 27, my - 73), (mx + 48, my - 52)], fill=(160, 110, 175))

    # Eyes (big, friendly)
    draw.ellipse([(mx - 30, my - 40), (mx - 5, my - 15)], fill=(250, 240, 200))
    draw.ellipse([(mx + 5, my - 40), (mx + 30, my - 15)], fill=(250, 240, 200))
    draw.ellipse([(mx - 25, my - 35), (mx - 10, my - 20)], fill=(30, 20, 50))
    draw.ellipse([(mx + 10, my - 35), (mx + 25, my - 20)], fill=(30, 20, 50))
    # Eye shine
    draw.ellipse([(mx - 22, my - 32), (mx - 18, my - 28)], fill=(255, 255, 255))
    draw.ellipse([(mx + 13, my - 32), (mx + 17, my - 28)], fill=(255, 255, 255))

    # Nose
    draw.ellipse([(mx - 8, my - 18), (mx + 8, my - 5)], fill=(60, 35, 70))

    # Mouth (gentle smile)
    draw.arc([(mx - 20, my - 15), (mx + 20, my + 10)], 0, 180, fill=(60, 35, 70), width=3)

    # Paws peeking out
    draw.ellipse([(mx - 90, my + 50), (mx - 60, my + 80)], fill=(100, 65, 120))
    draw.ellipse([(mx + 60, my + 50), (mx + 90, my + 80)], fill=(100, 65, 120))


def draw_stars(draw: ImageDraw, width: int, height: int) -> None:
    """Draw scattered stars in the sky/upper portion."""
    import random

    rng = random.Random(42)
    for _ in range(60):
        x = rng.randint(20, width - 20)
        y = rng.randint(10, int(height * 0.28))
        size = rng.randint(1, 3)
        bright = rng.randint(150, 255)
        draw.ellipse([x - size, y - size, x + size, y + size], fill=(bright, bright, bright - 30, 180))


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom of the cover with white text."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark semi-transparent rectangle
    draw.rectangle([(0, panel_top), (width, height)], fill=(20, 10, 30, 220))

    # Add a subtle border at top of panel
    draw.line([(0, panel_top), (width, panel_top)], fill=(100, 70, 130), width=3)

    # Title text
    title = "The Truth About\nMonsters"
    title_font_size = 72
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered - WHITE text on dark panel
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
    ay = y_offset + 40
    draw.text((ax, ay), author, fill=(200, 180, 220), font=author_font)

    # Tagline
    tagline = "A Children's Fantasy"
    try:
        tag_font = ImageFont.truetype(str(font_paths["small"]), 24)
    except Exception:
        tag_font = ImageFont.load_default()

    try:
        tbbox = draw.textbbox((0, 0), tagline, font=tag_font)
        tw = tbbox[2] - tbbox[0]
    except Exception:
        tw = 0
    tx = (width - tw) // 2
    draw.text((tx, ay + 55), tagline, fill=(180, 160, 200), font=tag_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Truth About Monsters")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Stars in the sky
    draw_stars(draw, WIDTH, HEIGHT)

    # Step 3: Bedroom scene
    draw_bedroom(draw, WIDTH, HEIGHT)

    # Step 4: Nightlight glow
    draw_nightlight(draw, WIDTH, HEIGHT)

    # Step 5: Friendly monster
    draw_monster(draw, WIDTH, HEIGHT)

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