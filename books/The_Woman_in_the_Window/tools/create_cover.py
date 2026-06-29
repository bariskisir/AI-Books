#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Woman in the Window."""

from __future__ import annotations

import argparse
import json
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
    """Deep night blue to dark indigo gradient for the neon-noir feel."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((5, 5, 30), ((10, 10, 50)), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((10, 10, 50), ((20, 15, 60)), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((20, 15, 60), ((5, 5, 20)), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_city_skyline(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a dark city skyline silhouette across the middle."""
    rng = random.Random(17)
    buildings = []
    x = 0
    while x < width:
        bw = rng.randint(40, 120)
        bh = rng.randint(80, 250)
        bx = x
        by = int(height * 0.65) - bh
        buildings.append((bx, by, bw, bh))
        # Windows on each building
        for wy in range(by + 15, int(height * 0.65) - 10, 20):
            for wx in range(bx + 8, bx + bw - 8, 18):
                if rng.random() < 0.35:
                    win_color = (255, 220, 100, 80) if rng.random() < 0.6 else (200, 150, 50, 60)
                    draw.rectangle([wx, wy, wx + 6, wy + 10], fill=win_color)
        x += bw + rng.randint(5, 20)
    for bx, by, bw, bh in buildings:
        draw.rectangle([bx, by, bx + bw, int(height * 0.65)], fill=(8, 8, 25))
        # Subtle outline
        draw.rectangle([bx, by, bx + bw, int(height * 0.65)], outline=(15, 15, 40), width=1)


def draw_apartment_window(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the focal apartment window with a woman silhouette."""
    cx, cy = width // 2, int(height * 0.38)
    ww, wh = 320, 420

    # Window frame
    draw.rectangle([cx - ww // 2, cy - wh // 2, cx + ww // 2, cy + wh // 2], fill=(20, 15, 50))
    draw.rectangle([cx - ww // 2 - 8, cy - wh // 2 - 8, cx + ww // 2 + 8, cy + wh // 2 + 8], fill=(30, 25, 40))

    # Interior glow
    inner_color = (40, 35, 60, 200)
    draw.rectangle([cx - ww // 2 + 4, cy - wh // 2 + 4, cx + ww // 2 - 4, cy + wh // 2 - 4], fill=inner_color)

    # Warm lamp glow through window
    glow_center = (cx + 60, cy + 40)
    for r in range(100, 10, -10):
        alpha = max(5, 40 - r // 3)
        draw.ellipse(
            [glow_center[0] - r, glow_center[1] - r, glow_center[0] + r, glow_center[1] + r],
            fill=(255, 200, 100, alpha),
        )

    # Window cross-frames (mullions)
    draw.line(
        [cx - ww // 2 + 4, cy, cx + ww // 2 - 4, cy], fill=(25, 20, 50), width=4
    )
    draw.line(
        [cx, cy - wh // 2 + 4, cx, cy + wh // 2 - 4], fill=(25, 20, 50), width=4
    )

    # Woman silhouette in the window
    # Body
    wx, wy = cx + 20, cy + 40
    draw.polygon(
        [
            (wx - 15, wy + 100),  # bottom left of dress
            (wx + 15, wy + 100),  # bottom right of dress
            (wx + 12, wy + 30),   # waist right
            (wx + 8, wy),         # shoulder right
            (wx + 5, wy - 40),   # head top right
            (wx - 5, wy - 40),   # head top left
            (wx - 8, wy),        # shoulder left
            (wx - 12, wy + 30),  # waist left
        ],
        fill=(180, 30, 30, 220),
    )
    # Head
    draw.ellipse([wx - 8, wy - 55, wx + 8, wy - 35], fill=(180, 30, 30, 220))
    # Arm raised (pressing against glass)
    draw.line([(wx - 8, wy + 5), (wx - 40, wy - 20)], fill=(180, 30, 30, 220), width=6)

    # Window glass reflection
    for i in range(3):
        rx = cx - ww // 2 + 10 + i * 100
        draw.line(
            [(rx, cy - wh // 2 + 10), (rx + 20, cy - wh // 2 + 40)],
            fill=(100, 100, 180, 20),
            width=2,
        )


def draw_neon_signs(draw: ImageDraw, width: int, height: int) -> None:
    """Draw neon signs and reflections in the cityscape."""
    rng = random.Random(42)
    neon_colors = [
        (255, 50, 100, 180),   # hot pink
        (50, 200, 255, 180),   # cyan
        (255, 200, 50, 180),   # amber
        (200, 50, 255, 180),   # purple
    ]

    # Scattered neon signs on buildings
    for _ in range(12):
        x = rng.randint(30, width - 30)
        y = rng.randint(int(height * 0.45), int(height * 0.60))
        color = rng.choice(neon_colors)
        sw = rng.randint(30, 80)
        sh = rng.randint(8, 16)

        # Glow
        for g in range(3):
            draw.rectangle(
                [x - g * 2, y - g * 2, x + sw + g * 2, y + sh + g * 2],
                outline=(color[0], color[1], color[2], color[3] // (g + 2)),
                width=1,
            )
        # Sign
        draw.rectangle([x, y, x + sw, y + sh], fill=color)

    # Street-level neon glow
    for _ in range(6):
        x = rng.randint(50, width - 50)
        y = int(height * 0.72)
        color = rng.choice(neon_colors)
        for r in range(30, 5, -5):
            draw.ellipse(
                [x - r, y - r, x + r, y + r],
                fill=(color[0], color[1], color[2], 10),
            )


def draw_camera_lens(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a camera lens in the lower portion of the image as a visual motif."""
    cx, cy = width // 2 - 200, int(height * 0.55)
    radius = 50

    # Outer ring
    for r in range(radius, radius - 8, -1):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(40, 40, 50))
    # Inner ring
    draw.ellipse([cx - radius + 8, cy - radius + 8, cx + radius - 8, cy + radius - 8], fill=(15, 15, 25))
    # Glass
    draw.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=(60, 60, 100, 200))
    # Reflection on glass
    draw.ellipse([cx - 12, cy - 12, cx + 5, cy + 5], fill=(150, 150, 200, 60))


def draw_street(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a wet street with reflections at the bottom."""
    street_top = int(height * 0.68)
    # Street surface
    draw.rectangle([(0, street_top), (width, height)], fill=(10, 8, 18))

    # Horizontal lane lines
    for lx in range(50, width, 200):
        draw.rectangle([lx, street_top + 30, lx + 80, street_top + 34], fill=(80, 80, 90))

    # Wet reflection of window light
    for _ in range(40):
        rx = random.randint(0, width)
        ry = random.randint(street_top, height)
        rw = random.randint(10, 60)
        rh = 2
        draw.rectangle([rx, ry, rx + rw, ry + rh], fill=(30, 25, 60, 60))

    # Neon reflections on wet street
    for _ in range(15):
        rx = random.randint(0, width)
        ry = random.randint(street_top + 20, height - 20)
        rw = random.randint(5, 30)
        color = random.choice([
            (255, 50, 100, 40),
            (50, 200, 255, 40),
            (255, 200, 50, 40),
        ])
        draw.rectangle([rx, ry, rx + rw, ry + 3], fill=color)


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom with white text."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark
    draw.rectangle([(0, panel_top), (width, height)], fill=(5, 5, 20))

    # Subtle border at top
    draw.line([(0, panel_top), (width, panel_top)], fill=(255, 50, 100, 100), width=2)

    # Title text
    title = "The Woman in\nthe Window"
    title_font_size = 72
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered - WHITE text
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
        y_offset += 95

    # Author name - WHITE
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
    draw.text((ax, ay), author, fill=(200, 200, 200), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Woman in the Window")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Night gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: City skyline
    draw_city_skyline(draw, WIDTH, HEIGHT)

    # Step 3: Wet street with reflections
    draw_street(draw, WIDTH, HEIGHT)

    # Step 4: Neon signs
    draw_neon_signs(draw, WIDTH, HEIGHT)

    # Step 5: The apartment window with woman silhouette
    draw_apartment_window(draw, WIDTH, HEIGHT)

    # Step 6: Camera lens element
    draw_camera_lens(draw, WIDTH, HEIGHT)

    # Step 7: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arial.ttf"),
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