#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Beekeeper's War."""

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
    """Mud brown to blood red to near-black gradient for the Western Front."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((80, 60, 40), (120, 50, 40), t)
        elif y < height * 0.75:
            t = (y - height * 0.4) / (height * 0.35)
            c = lerp_color((120, 50, 40), (60, 20, 15), t)
        else:
            t = (y - height * 0.75) / (height * 0.25)
            c = lerp_color((60, 20, 15), (10, 5, 5), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_barbed_wire(draw: ImageDraw, width: int, height: int) -> None:
    """Draw barbed wire across the foreground."""
    import random

    rng = random.Random(17)
    wire_y = int(height * 0.55)
    # Main wire strands
    for strand_offset in range(-15, 20, 15):
        points = []
        for x in range(0, width, 8):
            y = wire_y + strand_offset + rng.randint(-3, 3)
            points.append((x, y))
        draw.line(points, fill=(40, 35, 30), width=2)

    # Barbs
    for i in range(width // 40):
        bx = i * 40 + rng.randint(5, 25)
        by = wire_y + rng.randint(-18, 18)
        draw.line([(bx, by), (bx - 8, by + 12)], fill=(50, 45, 40), width=2)
        draw.line([(bx, by), (bx + 8, by + 12)], fill=(50, 45, 40), width=2)
        draw.line([(bx, by), (bx, by + 14)], fill=(50, 45, 40), width=2)


def draw_trench_silhouette(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a trench line and sandbags at the horizon."""
    horizon = int(height * 0.52)
    # Trench parapet
    draw.rectangle([(0, horizon - 15), (width, horizon)], fill=(55, 45, 35))
    # Sandbags
    import random

    rng = random.Random(8)
    for x in range(0, width, 30):
        bag_h = rng.randint(8, 14)
        bag_w = rng.randint(22, 32)
        draw.rectangle([x, horizon - bag_h, x + bag_w, horizon], fill=(65, 50, 38))
        # Highlight
        draw.rectangle([x, horizon - bag_h, x + bag_w, horizon - bag_h + 3], fill=(75, 60, 45))


def draw_beehives(draw: ImageDraw, width: int, height: int) -> None:
    """Draw two beehive skeps in the middle distance."""
    import random

    rng = random.Random(42)

    # Left hive
    hx1 = int(width * 0.35)
    hy1 = int(height * 0.40)
    draw.ellipse([hx1 - 25, hy1 - 30, hx1 + 25, hy1 + 20], fill=(120, 95, 60))
    draw.ellipse([hx1 - 22, hy1 - 25, hx1 + 22, hy1 + 15], fill=(140, 110, 70))
    # Entrance
    draw.ellipse([hx1 - 6, hy1 + 8, hx1 + 6, hy1 + 18], fill=(50, 40, 30))
    # Bees around left hive
    for _ in range(6):
        bx = hx1 + rng.randint(-35, 35)
        by = hy1 + rng.randint(-40, 15)
        draw.ellipse([bx - 2, by - 2, bx + 2, by + 2], fill=(200, 160, 40))

    # Right hive
    hx2 = int(width * 0.58)
    hy2 = int(height * 0.38)
    draw.ellipse([hx2 - 28, hy2 - 32, hx2 + 28, hy2 + 22], fill=(130, 100, 65))
    draw.ellipse([hx2 - 24, hy2 - 27, hx2 + 24, hy2 + 17], fill=(150, 115, 75))
    draw.ellipse([hx2 - 6, hy2 + 10, hx2 + 6, hy2 + 20], fill=(50, 40, 30))
    # Bees around right hive
    for _ in range(5):
        bx = hx2 + rng.randint(-35, 35)
        by = hy2 + rng.randint(-40, 15)
        draw.ellipse([bx - 2, by - 2, bx + 2, by + 2], fill=(200, 160, 40))


def draw_poppies(draw: ImageDraw, width: int, height: int) -> None:
    """Draw red poppies scattered across the foreground."""
    import random

    rng = random.Random(23)

    for _ in range(40):
        x = rng.randint(50, width - 50)
        y = rng.randint(int(height * 0.50), int(height * 0.85))
        size = rng.randint(4, 10)
        # Petal (red)
        draw.ellipse([x - size, y - size, x + size, y + size], fill=(180, 25, 20))
        draw.ellipse([x - size + 2, y - size + 2, x + size - 2, y + size - 2], fill=(200, 35, 30))
        # Center (black)
        draw.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(15, 10, 8))


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom of the cover with white text."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    draw.rectangle([(0, panel_top), (width, height)], fill=(30, 25, 20))

    # Subtle top border
    draw.line([(0, panel_top), (width, panel_top)], fill=(80, 60, 40), width=3)

    # Title text
    title = "The Beekeeper's\nWar"
    title_font_size = 72
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered in white
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
    draw.text((ax, ay), author, fill=(200, 190, 180), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Beekeeper's War")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Trench silhouette
    draw_trench_silhouette(draw, WIDTH, HEIGHT)

    # Step 3: Beehives
    draw_beehives(draw, WIDTH, HEIGHT)

    # Step 4: Barbed wire
    draw_barbed_wire(draw, WIDTH, HEIGHT)

    # Step 5: Poppies
    draw_poppies(draw, WIDTH, HEIGHT)

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