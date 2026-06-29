#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Seventh Chamber."""

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
    """Desert gold at top to deep tomb darkness at bottom."""
    for y in range(height):
        if y < height * 0.35:
            t = y / (height * 0.35)
            c = lerp_color((210, 170, 90), (180, 130, 60), t)
        elif y < height * 0.65:
            t = (y - height * 0.35) / (height * 0.30)
            c = lerp_color((180, 130, 60), (100, 70, 40), t)
        else:
            t = (y - height * 0.65) / (height * 0.35)
            c = lerp_color((100, 70, 40), (20, 15, 10), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_dunes(draw: ImageDraw, width: int, height: int) -> None:
    """Draw undulating desert sand dunes across the middle ground."""
    import random

    rng = random.Random(3)

    base_y = int(height * 0.55)
    for dune_idx in range(6):
        points = []
        dune_height = rng.randint(30, 80)
        dune_width = rng.randint(200, 500)
        start_x = rng.randint(-100, width - 100)

        for x in range(0, width + 20, 10):
            rel_x = x - start_x
            peak = math.sin(rel_x * math.pi / dune_width) * dune_height
            if peak < 0:
                peak *= 0.3
            y = base_y + dune_idx * 20 + peak
            points.append((x, y))

        shade = 60 + dune_idx * 10
        draw.polygon(points + [(width, height), (0, height)], fill=(shade, shade - 10, shade - 20))


def draw_rock_face(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the cliff face and tomb entrance."""
    cx = width // 2

    # Cliff face - large irregular shape
    cliff_points = [
        (cx - 350, int(height * 0.20)),
        (cx - 280, int(height * 0.18)),
        (cx - 150, int(height * 0.15)),
        (cx + 150, int(height * 0.15)),
        (cx + 280, int(height * 0.18)),
        (cx + 380, int(height * 0.22)),
        (cx + 400, int(height * 0.40)),
        (cx + 390, int(height * 0.50)),
        (cx + 360, int(height * 0.58)),
        (cx + 320, int(height * 0.65)),
        (cx - 320, int(height * 0.65)),
        (cx - 360, int(height * 0.58)),
        (cx - 390, int(height * 0.50)),
        (cx - 400, int(height * 0.40)),
    ]
    draw.polygon(cliff_points, fill=(130, 110, 80))

    # Cliff face shading - vertical striations
    for sx in range(cx - 350, cx + 380, 15):
        shade_offset = (sx % 30) - 15
        draw.line(
            [(sx, int(height * 0.18)), (sx, int(height * 0.65))],
            fill=(max(0, 130 + shade_offset), max(0, 110 + shade_offset), max(0, 80 + shade_offset)),
            width=2,
        )

    # Tomb entrance - dark rectangle
    door_w, door_h = 120, 180
    door_x = cx - door_w // 2
    door_y = int(height * 0.35)
    draw.rectangle([door_x, door_y, door_x + door_w, door_y + door_h], fill=(10, 8, 5))

    # Doorframe
    frame_color = (160, 140, 100)
    draw.rectangle([door_x - 8, door_y - 8, door_x + door_w + 8, door_y], fill=frame_color)
    draw.rectangle([door_x - 8, door_y, door_x, door_y + door_h], fill=frame_color)
    draw.rectangle([door_x + door_w, door_y, door_x + door_w + 8, door_y + door_h], fill=frame_color)
    draw.rectangle([door_x - 8, door_y + door_h, door_x + door_w + 8, door_y + door_h + 8], fill=frame_color)

    # Door arch
    draw.arc(
        [door_x - 8, door_y - 60, door_x + door_w + 8, door_y + 20],
        start=180, end=0, fill=frame_color, width=8,
    )

    # Carved hieroglyphs above door
    glyph_positions = [(cx - 100, int(height * 0.28)), (cx + 30, int(height * 0.26)), (cx - 50, int(height * 0.30))]
    for gx, gy in glyph_positions:
        # Ankh-like shapes
        draw.ellipse([gx, gy, gx + 12, gy + 6], fill=(170, 150, 110))
        draw.rectangle([gx + 5, gy + 6, gx + 7, gy + 20], fill=(170, 150, 110))


def draw_torchlight(draw: ImageDraw, width: int, height: int) -> None:
    """Draw torchlight glow emanating from the tomb entrance."""
    cx = width // 2
    door_y = int(height * 0.35)
    door_h = 180

    # Torch glow - multiple semi-transparent layers
    for radius in [250, 180, 120, 70]:
        alpha = max(10, 60 - radius // 5)
        draw.ellipse(
            [cx - radius, door_y + door_h // 2 - radius, cx + radius, door_y + door_h // 2 + radius],
            fill=(255, 200, 100, alpha),
        )

    # Torch flame inside door
    flame_points = [
        (cx - 8, door_y + 10),
        (cx, door_y - 15),
        (cx + 8, door_y + 10),
    ]
    draw.polygon(flame_points, fill=(255, 180, 50, 200))
    draw.polygon([(cx - 4, door_y + 5), (cx, door_y - 5), (cx + 4, door_y + 5)], fill=(255, 255, 200, 220))

    # Light ray emanating from door
    for angle in range(-20, 25, 5):
        rad = math.radians(angle)
        x_end = int(cx + math.sin(rad) * 300)
        y_end = int(door_y + door_h // 2 + math.cos(rad) * 200)
        draw.line([(cx, door_y + door_h // 2), (x_end, y_end)], fill=(255, 220, 150, 15), width=6)


def draw_stars(draw: ImageDraw, width: int, height: int) -> None:
    """Draw stars in the upper portion of the cover."""
    import random

    rng = random.Random(17)
    star_y_max = int(height * 0.25)

    for _ in range(80):
        x = rng.randint(50, width - 50)
        y = rng.randint(10, star_y_max)
        size = rng.randint(1, 3)
        brightness = rng.randint(180, 255)
        draw.ellipse([x - size, y - size, x + size, y + size], fill=(brightness, brightness, brightness, 200))


def draw_hieroglyphic_border(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a decorative border of Egyptian-style symbols along the sides."""
    import random

    rng = random.Random(42)
    symbols = [
        (0, 0, 15, 8),
        (0, 0, 8, 15),
        (0, 0, 12, 12),
        (0, 0, 6, 18),
    ]

    for side in range(2):
        x_base = 15 if side == 0 else width - 25
        for sy in range(100, height - 100, 80):
            sx, sy_off, sw, sh = symbols[rng.randint(0, len(symbols) - 1)]
            draw.ellipse(
                [x_base + sx, sy + sy_off, x_base + sx + sw, sy + sy_off + sh],
                fill=(180, 160, 120, 80),
            )


def draw_title_panel(draw: ImageDraw, draw_img: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark title panel at the bottom with white text."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark semi-transparent rectangle
    draw.rectangle([(0, panel_top), (width, height)], fill=(15, 12, 8, 220))

    # Gold border at top of panel
    draw.line([(200, panel_top), (width - 200, panel_top)], fill=(180, 150, 70), width=3)
    draw.line([(200, panel_top + 1), (width - 200, panel_top + 1)], fill=(100, 80, 40), width=1)

    # Title text
    title = "The Seventh\nChamber"
    title_font_size = 76
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered
    lines = title.split("\n")
    y_offset = panel_top + 90
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 0
        tx = (width - tw) // 2
        draw.text((tx, y_offset), line, fill=(255, 255, 240), font=title_font)
        y_offset += 100

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
    draw.text((ax, ay), author, fill=(200, 180, 140), font=author_font)

    # Gold line below author
    draw.line([(400, ay + 50), (width - 400, ay + 50)], fill=(180, 150, 70, 150), width=1)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Sand dunes
    draw_dunes(draw, WIDTH, HEIGHT)

    # Step 3: Rock face and tomb entrance
    draw_rock_face(draw, WIDTH, HEIGHT)

    # Step 4: Torchlight
    draw_torchlight(draw, WIDTH, HEIGHT)

    # Step 5: Stars
    draw_stars(draw, WIDTH, HEIGHT)

    # Step 6: Hieroglyphic border elements
    draw_hieroglyphic_border(draw, WIDTH, HEIGHT)

    # Step 7: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arial.ttf"),
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