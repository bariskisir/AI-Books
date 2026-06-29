#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Body in the Library."""

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
    """Warm wood and cream gradient for the cozy library feel."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((180, 140, 100), (140, 90, 50), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((140, 90, 50), (100, 65, 35), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((100, 65, 35), (60, 35, 15), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_bookshelves(draw: ImageDraw, width: int, height: int) -> None:
    """Draw tall bookshelves flanking both sides of the cover."""
    shelf_colors = [(80, 50, 25), (90, 55, 30), (70, 40, 20)]
    book_colors = [
        (150, 30, 30), (30, 80, 150), (200, 170, 50),
        (30, 120, 60), (120, 50, 120), (200, 100, 30),
        (40, 40, 100), (180, 130, 70), (20, 100, 100),
        (140, 60, 40), (60, 100, 40), (100, 60, 100),
    ]

    # Left bookshelf
    for shelf_y in range(0, TITLE_PANEL_TOP, 180):
        # Shelf board
        draw.rectangle([(10, shelf_y), (220, shelf_y + 8)], fill=(100, 60, 35))
        # Books on shelf
        x = 15
        while x < 215:
            h = 120 + (hash(str(x + shelf_y)) % 50)
            w = 15 + (hash(str(x * 7 + shelf_y)) % 15)
            if x + w > 220:
                break
            color = book_colors[(x + shelf_y) % len(book_colors)]
            book_top = min(shelf_y - h + 130, shelf_y + 8)
            book_bottom = max(shelf_y - h + 130, shelf_y + 8)
            draw.rectangle([(x, book_top), (x + w, book_bottom)], fill=color)
            # Spine detail
            draw.rectangle([(x, book_top), (x + 3, book_bottom)], fill=(max(0, color[0]-30), max(0, color[1]-30), max(0, color[2]-30)))
            x += w + 4

    # Right bookshelf
    for shelf_y in range(0, TITLE_PANEL_TOP, 180):
        draw.rectangle([(width - 220, shelf_y), (width - 10, shelf_y + 8)], fill=(100, 60, 35))
        x = width - 215
        while x > width - 220:
            h = 120 + (hash(str(x * 13 + shelf_y)) % 50)
            w = 15 + (hash(str(x * 31 + shelf_y)) % 15)
            if x - w < width - 220:
                break
            color = book_colors[(x + shelf_y + 5) % len(book_colors)]
            book_top = min(shelf_y - h + 130, shelf_y + 8)
            book_bottom = max(shelf_y - h + 130, shelf_y + 8)
            draw.rectangle([(x - w, book_top), (x, book_bottom)], fill=color)
            draw.rectangle([(x - 3, book_top), (x, book_bottom)], fill=(max(0, color[0]-30), max(0, color[1]-30), max(0, color[2]-30)))
            x -= w + 4


def draw_floor_lamp(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a floor lamp casting warm light near the center-right."""
    lx = width - 320
    ly = int(height * 0.55)

    # Lamp pole
    draw.line([(lx, ly), (lx, ly + 350)], fill=(60, 40, 20), width=6)
    # Lamp base
    draw.ellipse([(lx - 30, ly + 345), (lx + 30, ly + 365)], fill=(60, 40, 20))
    # Lamp shade
    draw.polygon([(lx - 50, ly - 40), (lx + 50, ly - 40), (lx + 30, ly + 10), (lx - 30, ly + 10)], fill=(220, 200, 160))
    # Warm glow
    for i in range(3):
        alpha = 30 - i * 8
        glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.ellipse([(lx - 150 - i * 30, ly - 200 - i * 40), (lx + 150 + i * 30, ly + 50 + i * 20)], fill=(255, 220, 150, alpha))
        draw._image.paste(Image.alpha_composite(draw._image, glow))


def draw_body_silhouette(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a subtle body silhouette on the floor near the center."""
    bx, by = width // 2, int(height * 0.7)

    # Body outline on floor
    draw.ellipse([(bx - 80, by + 20), (bx + 80, by + 80)], fill=(40, 20, 10, 180))
    # Torso
    draw.rectangle([(bx - 30, by - 20), (bx + 30, by + 30)], fill=(40, 20, 10, 180))
    # Head
    draw.ellipse([(bx - 18, by - 55), (bx + 18, by - 20)], fill=(40, 20, 10, 180))
    # Paper on chest (the Shakespeare quote)
    draw.rectangle([(bx - 15, by - 5), (bx + 15, by + 5)], fill=(200, 190, 170, 200))


def draw_reading_table(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a reading table with an open book and lamp."""
    tx, ty = width // 2 + 120, int(height * 0.68)

    # Table
    draw.rectangle([(tx - 80, ty), (tx + 80, ty + 120)], fill=(90, 55, 30))
    draw.rectangle([(tx - 80, ty - 5), (tx + 80, ty + 5)], fill=(110, 70, 40))
    # Table legs
    draw.rectangle([(tx - 75, ty + 120), (tx - 65, ty + 160)], fill=(70, 40, 20))
    draw.rectangle([(tx + 65, ty + 120), (tx + 75, ty + 160)], fill=(70, 40, 20))

    # Open book on table
    draw.rectangle([(tx - 40, ty - 25), (tx + 40, ty + 1)], fill=(200, 190, 170))
    # Pages
    draw.line([(tx, ty - 25), (tx, ty + 1)], fill=(100, 90, 70), width=1)
    draw.rectangle([(tx - 35, ty - 22), (tx - 2, ty - 3)], fill=(220, 210, 190))
    draw.rectangle([(tx + 2, ty - 22), (tx + 35, ty - 3)], fill=(220, 210, 190))


def draw_arch_window(draw: ImageDraw, width: int, height: int) -> None:
    """Draw an arched window in the background center, showing night sky."""
    wx, wy = width // 2, int(height * 0.15)

    # Arch window frame
    draw.arc([(wx - 120, wy), (wx + 120, wy + 240)], 0, 180, fill=(60, 40, 20), width=8)
    draw.line([(wx - 120, wy + 120), (wx - 120, wy + 240)], fill=(60, 40, 20), width=8)
    draw.line([(wx + 120, wy + 120), (wx + 120, wy + 240)], fill=(60, 40, 20), width=8)
    draw.line([(wx - 120, wy + 240), (wx + 120, wy + 240)], fill=(60, 40, 20), width=8)

    # Glass area - night sky visible through window
    draw.rectangle([(wx - 112, wy + 4), (wx + 112, wy + 232)], fill=(15, 15, 40))

    # Moon through window
    draw.ellipse([(wx + 30, wy + 30), (wx + 70, wy + 70)], fill=(220, 220, 200, 180))

    # Window cross bars
    draw.line([(wx, wy + 4), (wx, wy + 232)], fill=(60, 40, 20), width=4)
    draw.line([(wx - 112, wy + 120), (wx + 112, wy + 120)], fill=(60, 40, 20), width=4)


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark title panel at the bottom of the cover with white text."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    draw.rectangle([(0, panel_top), (width, height)], fill=(30, 25, 20))

    # Subtle top border
    draw.line([(0, panel_top), (width, panel_top)], fill=(180, 150, 100), width=3)

    # Title text
    title = "The Body in\nthe Library"
    title_font_size = 76
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered with white text
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

    # Genre line
    genre = "A Classic Whodunit"
    genre_font_size = 28
    try:
        genre_font = ImageFont.truetype(str(font_paths["small"]), genre_font_size)
    except Exception:
        genre_font = ImageFont.load_default()

    try:
        gbbox = draw.textbbox((0, 0), genre, font=genre_font)
        gw = gbbox[2] - gbbox[0]
    except Exception:
        gw = 0
    gx = (width - gw) // 2
    gy = y_offset + 20
    draw.text((gx, gy), genre, fill=(200, 180, 150), font=genre_font)

    # Author name
    author = "Barış Kısır"
    author_font_size = 38
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
    ay = gy + 55
    draw.text((ax, ay), author, fill=(255, 255, 255), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Body in the Library")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Arched window in background
    draw_arch_window(draw, WIDTH, HEIGHT)

    # Step 3: Bookshelves flanking sides
    draw_bookshelves(draw, WIDTH, HEIGHT)

    # Step 4: Floor lamp with warm glow
    draw_floor_lamp(draw, WIDTH, HEIGHT)

    # Step 5: Reading table with open book
    draw_reading_table(draw, WIDTH, HEIGHT)

    # Step 6: Body silhouette
    draw_body_silhouette(draw, WIDTH, HEIGHT)

    # Step 7: Title panel
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
