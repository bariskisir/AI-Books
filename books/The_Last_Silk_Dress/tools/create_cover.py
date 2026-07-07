#!/usr/bin/env python3
"""Cover: The Last Silk Dress — 1890s New York workroom, burgundy silk dress on mannequin, gaslight glow, burgundy/gold gaslight/seamstress blue."""

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
    """Rich gold-to-mahogany gradient for the Gilded Age feel."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((80, 40, 20), (140, 90, 40), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((140, 90, 40), (60, 20, 10), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((60, 20, 10), (20, 10, 5), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_skyline(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a silhouette of the 1890s New York skyline."""
    rng = random.Random(42)
    buildings = [
        (50, 550, 120),
        (120, 400, 90),
        (210, 600, 140),
        (300, 450, 100),
        (380, 500, 110),
        (450, 350, 80),
        (510, 650, 150),
        (600, 480, 100),
        (670, 380, 85),
        (730, 550, 120),
        (800, 420, 95),
        (860, 600, 130),
        (940, 500, 110),
        (1020, 450, 100),
        (1090, 550, 120),
        (1160, 380, 85),
        (1230, 600, 140),
        (1320, 450, 100),
        (1390, 350, 80),
        (1460, 500, 110),
        (1530, 400, 90),
    ]

    sky_y = int(height * 0.45)
    for bx, bh, bw in buildings:
        # Building body
        b_color = (10, 8, 5, 200)
        draw.rectangle([bx, sky_y - bh, bx + bw, sky_y], fill=b_color)
        # Windows (small lit rectangles)
        for wy in range(sky_y - bh + 15, sky_y - 10, 25):
            for wx in range(bx + 8, bx + bw - 8, 18):
                if rng.random() < 0.3:
                    win_color = (255, 220, 140, 80)
                    draw.rectangle([wx, wy, wx + 6, wy + 10], fill=win_color)

    # Church spire
    spire_x, spire_y = 350, sky_y - 600
    draw.polygon(
        [(spire_x, spire_y), (spire_x - 10, spire_y + 50), (spire_x + 10, spire_y + 50)],
        fill=(15, 10, 5),
    )
    draw.rectangle(
        [spire_x - 20, spire_y + 50, spire_x + 20, sky_y],
        fill=(15, 10, 5),
    )

    # Brooklyn Bridge silhouette suggestion
    bridge_y = sky_y - 20
    for t in range(0, width, 4):
        bridge_x = t
        bridge_y_offset = int(15 * math.sin(t / 120))
        draw.rectangle([bridge_x, bridge_y + bridge_y_offset, bridge_x + 2, bridge_y + bridge_y_offset + 3], fill=(5, 3, 2, 150))


def draw_dress_silhouette(draw: ImageDraw, width: int, height: int) -> None:
    """Draw an elegant dress silhouette in the center."""
    cx, cy = width // 2, int(height * 0.38)
    # Dress shape - bustle era silhouette
    dress_points = [
        (cx - 40, cy - 120),  # head
        (cx + 40, cy - 120),
        (cx + 50, cy - 80),   # shoulders
        (cx + 65, cy + 10),   # waist
        (cx + 120, cy + 120), # skirt right
        (cx + 140, cy + 260),
        (cx - 140, cy + 260),  # hem left
        (cx - 120, cy + 120),
        (cx - 65, cy + 10),
        (cx - 50, cy - 80),
    ]

    # Draw dress as a semi-transparent overlay
    draw.polygon(
        dress_points,
        fill=(200, 180, 160, 80),
        outline=(220, 200, 180, 150),
        width=2,
    )

    # Decorative details on the dress
    # Waistline
    draw.line(
        [(cx - 65, cy + 10), (cx + 65, cy + 10)],
        fill=(230, 210, 190, 120),
        width=2,
    )

    # Neckline detail
    draw.arc(
        [cx - 40, cy - 120, cx + 40, cy - 80],
        start=0, end=180,
        fill=(230, 210, 190, 150),
        width=2,
    )


def draw_pearls(draw: ImageDraw, width: int, height: int) -> None:
    """Draw scattered pearl decorations."""
    rng = random.Random(7)
    for _ in range(60):
        x = rng.randint(100, width - 100)
        y = rng.randint(int(height * 0.15), int(height * 0.55))
        size = rng.randint(3, 7)
        # Pearl glow
        draw.ellipse(
            [x - size, y - size, x + size, y + size],
            fill=(230, 225, 220, 60),
        )
        # Pearl body
        draw.ellipse(
            [x - size // 2, y - size // 2, x + size // 2, y + size // 2],
            fill=(240, 235, 230, 200),
        )
        # Highlight
        draw.ellipse(
            [x - size // 4, y - size // 4, x + size // 4, y + size // 4],
            fill=(255, 255, 255, 180),
        )


def draw_gold_details(draw: ImageDraw, width: int, height: int) -> None:
    """Draw decorative gold filigree near the dress."""
    cx, cy = width // 2, int(height * 0.38)
    rng = random.Random(13)

    # Decorative swirls around the dress
    for angle_start in range(0, 360, 60):
        rad = math.radians(angle_start)
        r = 180
        sx = cx + int(r * math.cos(rad))
        sy = cy + int(r * math.sin(rad))

        # Small decorative swirl
        swirl_points = []
        for t in range(21):
            st = t / 20
            s_angle = st * math.pi * 2 + rad
            s_r = 15 + st * 25
            px = sx + int(s_r * math.cos(s_angle))
            py = sy + int(s_r * math.sin(s_angle))
            swirl_points.append((px, py))

        draw.line(swirl_points, fill=(200, 170, 80, 100), width=2)


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom with white text."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark semi-transparent
    draw.rectangle([(0, panel_top), (width, height)], fill=(15, 10, 8, 230))

    # Gold border at top of panel
    draw.line([(100, panel_top), (width - 100, panel_top)], fill=(180, 150, 60), width=3)

    # Gold accent lines
    draw.line([(200, panel_top + 10), (width - 200, panel_top + 10)], fill=(180, 150, 60, 100), width=1)

    # Title text
    title = "The Last\nSilk Dress"
    title_font_size = 80
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered, in WHITE
    lines = title.split("\n")
    y_offset = panel_top + 80
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 0
        tx = (width - tw) // 2
        draw.text((tx, y_offset), line, fill=(245, 240, 235), font=title_font)
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
    draw.text((ax, ay), author, fill=(200, 185, 160), font=author_font)

    # Decorative line below author
    draw.line([(500, ay + 50), (width - 500, ay + 50)], fill=(180, 150, 60, 100), width=1)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Last Silk Dress")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: New York skyline silhouette
    draw_skyline(draw, WIDTH, HEIGHT)

    # Step 3: Pearl decorations
    draw_pearls(draw, WIDTH, HEIGHT)

    # Step 4: Gold filigree details
    draw_gold_details(draw, WIDTH, HEIGHT)

    # Step 5: Dress silhouette
    draw_dress_silhouette(draw, WIDTH, HEIGHT)

    # Step 6: Title panel at bottom
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