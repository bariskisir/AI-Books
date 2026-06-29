#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Mermaid's Tear."""

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
    """Deep ocean blue to turquoise to teal gradient."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((5, 15, 40), (10, 60, 90), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((10, 60, 90), (20, 100, 110), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((20, 100, 110), (5, 40, 55), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_light_rays(draw: ImageDraw, width: int, height: int) -> None:
    """Draw sun rays filtering through water from the top center."""
    import random

    rng = random.Random(13)
    cx, cy = width // 2, 0
    for _ in range(14):
        angle = rng.uniform(-0.8, 0.8)
        length = rng.randint(int(height * 0.4), int(height * 0.8))
        end_x = cx + int(math.tan(angle) * length)
        end_y = cy + length
        alpha = rng.randint(20, 50)
        draw.line(
            [(cx, cy), (end_x, end_y)],
            fill=(180, 220, 255, alpha),
            width=rng.randint(8, 20),
        )


def draw_coral_reef(draw: ImageDraw, width: int, height: int) -> None:
    """Draw coral formations at the bottom of the image."""
    import random

    rng = random.Random(42)

    # Bottom coral silhouettes
    for i in range(20):
        x = rng.randint(0, width)
        base_y = height - rng.randint(100, 300)
        height_var = rng.randint(60, 200)
        hue = rng.choice([
            (180, 70, 80),   # red coral
            (200, 100, 60),  # orange coral
            (60, 120, 140),  # blue coral
            (200, 80, 100),  # pink coral
        ])
        # Fan coral
        points = [(x, height)]
        for s in range(1, 10):
            t = s / 10
            px = x + rng.randint(-40, 40)
            py = base_y - int(height_var * t * (1 - t) * 4)
            points.append((px, py))
        points.append((x, base_y - height_var))
        draw.polygon(points, fill=hue)

        # Branching coral
        bx = x + rng.randint(-30, 30)
        by = base_y + rng.randint(10, 40)
        for _ in range(rng.randint(3, 6)):
            bx2 = bx + rng.randint(-30, 30)
            by2 = by - rng.randint(20, 60)
            draw.line([(bx, by), (bx2, by2)], fill=hue, width=rng.randint(3, 6))
            # Small branches
            bx3 = bx2 + rng.randint(-15, 15)
            by3 = by2 - rng.randint(15, 30)
            draw.line([(bx2, by2), (bx3, by3)], fill=hue, width=rng.randint(2, 3))


def draw_schooner(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a colonial schooner silhouette on the horizon."""
    # Position at upper third, right side
    cx = int(width * 0.72)
    cy = int(height * 0.28)

    # Hull
    hull_color = (30, 25, 20)
    hull_pts = [
        (cx - 100, cy + 20),
        (cx - 80, cy + 35),
        (cx + 80, cy + 35),
        (cx + 100, cy + 20),
    ]
    draw.polygon(hull_pts, fill=hull_color)

    # Masts
    mast_color = (40, 35, 30)
    draw.rectangle([cx - 50, cy - 100, cx - 44, cy + 20], fill=mast_color)
    draw.rectangle([cx + 30, cy - 130, cx + 36, cy + 20], fill=mast_color)
    draw.rectangle([cx + 60, cy - 80, cx + 64, cy + 10], fill=mast_color)

    # Sails (slightly transparent white)
    sail_color = (200, 210, 220, 120)
    # Main sail
    draw.polygon([(cx - 44, cy - 90), (cx + 20, cy - 30), (cx - 44, cy + 15)], fill=sail_color)
    # Jib sail
    draw.polygon([(cx - 50, cy - 80), (cx - 110, cy - 20), (cx - 50, cy + 15)], fill=sail_color)
    # Second mast sails
    draw.polygon([(cx + 36, cy - 120), (cx + 90, cy - 50), (cx + 36, cy + 15)], fill=sail_color)
    draw.polygon([(cx + 36, cy - 70), (cx + 70, cy - 30), (cx + 36, cy + 10)], fill=sail_color)

    # Bowsprit
    draw.line([(cx + 100, cy + 20), (cx + 140, cy + 5)], fill=(40, 35, 30), width=3)
    # Jib on bowsprit
    draw.polygon([(cx + 140, cy + 5), (cx + 100, cy - 30), (cx + 110, cy + 15)], fill=sail_color)


def draw_pearl_glow(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a large glowing pearl near the center with radial light."""
    cx, cy = width // 2, int(height * 0.45)

    # Outer glows
    for r in range(5, 0, -1):
        radius = 40 + r * 25
        alpha = 30 - r * 5
        draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            fill=(200, 230, 255, max(0, alpha)),
        )

    # Pearl body
    draw.ellipse(
        [cx - 35, cy - 35, cx + 35, cy + 35],
        fill=(220, 235, 250, 200),
    )

    # Highlight
    draw.ellipse(
        [cx - 12, cy - 15, cx + 5, cy + 2],
        fill=(255, 255, 255, 180),
    )

    # Inner glow
    draw.ellipse(
        [cx - 20, cy - 20, cx + 20, cy + 20],
        fill=(180, 220, 255, 80),
    )


def draw_fish_school(draw: ImageDraw, width: int, height: int) -> None:
    """Draw small fish silhouettes swimming in the background."""
    import random

    rng = random.Random(99)

    for _ in range(30):
        x = rng.randint(100, width - 100)
        y = rng.randint(int(height * 0.15), int(height * 0.65))
        size = rng.randint(4, 10)
        angle = rng.uniform(-0.3, 0.3)
        color = (100, 140, 160, 80)

        # Fish body
        ex = x + int(size * math.cos(angle))
        ey = y + int(size * math.sin(angle))
        draw.line([(x, y), (ex, ey)], fill=color, width=2)
        # Tail
        tx = x - int(size * 0.5 * math.cos(angle))
        ty = y - int(size * 0.5 * math.sin(angle))
        draw.line([(tx, ty), (x, y)], fill=color, width=1)


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom of the cover."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark semi-transparent rectangle
    draw.rectangle([(0, panel_top), (width, height)], fill=(10, 20, 35, 220))

    # Add a subtle border at top of panel
    draw.line([(0, panel_top), (width, panel_top)], fill=(100, 180, 200, 120), width=2)

    # Title text
    title = "The Mermaid's\nTear"
    title_font_size = 72
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered in WHITE
    lines = title.split("\n")
    y_offset = panel_top + 80
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 0
        tx = (width - tw) // 2
        # Title in white with a subtle glow
        # Glow shadow
        for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
            draw.text((tx + dx, y_offset + dy), line, fill=(80, 150, 200, 100), font=title_font)
        draw.text((tx, y_offset), line, fill=(240, 245, 255), font=title_font)
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
    draw.text((ax, ay), author, fill=(180, 210, 230), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Mermaid's Tear")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Sun rays through water
    draw_light_rays(draw, WIDTH, HEIGHT)

    # Step 3: Fish school
    draw_fish_school(draw, WIDTH, HEIGHT)

    # Step 4: Colonial schooner silhouette
    draw_schooner(draw, WIDTH, HEIGHT)

    # Step 5: Coral reef at bottom
    draw_coral_reef(draw, WIDTH, HEIGHT)

    # Step 6: Glowing pearl
    draw_pearl_glow(draw, WIDTH, HEIGHT)

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