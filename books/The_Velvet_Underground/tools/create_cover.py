#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Velvet Underground."""

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
    """Black to deep violet gradient for the music mystery feel."""
    for y in range(height):
        if y < height * 0.5:
            t = y / (height * 0.5)
            c = lerp_color((5, 0, 10), ((40, 5, 50)), t)
        else:
            t = (y - height * 0.5) / (height * 0.5)
            c = lerp_color((40, 5, 50), ((10, 0, 20)), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_cassette(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a cassette tape at the center of the cover."""
    cx, cy = width // 2, int(height * 0.40)
    w, h = 360, 240

    # Cassette body
    draw.rectangle([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2], fill=(20, 15, 25))
    # Cassette border
    for i in range(3):
        draw.rectangle(
            [cx - w // 2 - i, cy - h // 2 - i, cx + w // 2 + i, cy + h // 2 + i],
            outline=(60, 50, 70),
            width=1,
        )

    # Label area
    draw.rectangle([cx - 130, cy - 80, cx + 130, cy + 30], fill=(25, 20, 35))

    # Reel hubs
    hub_y = cy - 50
    for hub_x in (cx - 80, cx + 80):
        # Outer hub
        draw.ellipse([hub_x - 30, hub_y - 30, hub_x + 30, hub_y + 30], fill=(15, 10, 20))
        # Inner hub
        draw.ellipse([hub_x - 15, hub_y - 15, hub_x + 15, hub_y + 15], fill=(40, 35, 50))
        # Center hole
        draw.ellipse([hub_x - 5, hub_y - 5, hub_x + 5, hub_y + 5], fill=(10, 5, 15))

    # Tape between reels
    draw.rectangle([cx - 50, hub_y - 2, cx + 50, hub_y + 2], fill=(60, 55, 70))

    # Bottom edge of cassette
    draw.rectangle([cx - w // 2, cy + h // 2 - 15, cx + w // 2, cy + h // 2], fill=(15, 10, 20))

    # Head window
    draw.rectangle([cx - 45, cy + h // 2 - 25, cx + 45, cy + h // 2 - 5], fill=(10, 5, 15))

    # Glow behind cassette
    for r in range(20, 100, 5):
        alpha = max(0, 60 - r * 2)
        draw.ellipse(
            [cx - w // 2 - r, cy - h // 2 - r, cx + w // 2 + r, cy + h // 2 + r],
            outline=(100, 50, 120, alpha),
            width=1,
        )


def draw_vinyl(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a vinyl record behind the cassette."""
    cx, cy = width // 2, int(height * 0.55)
    radius = 200

    # Dark vinyl disc
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(15, 10, 20))
    # Grooves
    for r in range(30, radius, 15):
        color_val = 20 + ((r // 15) % 3) * 5
        draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            outline=(color_val, color_val - 5, color_val + 5),
            width=1,
        )
    # Label
    draw.ellipse([cx - 50, cy - 50, cx + 50, cy + 50], fill=(30, 25, 40))
    # Spindle hole
    draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(10, 5, 15))

    # Highlight on vinyl
    for i in range(3):
        angle = math.radians(45 + i * 120)
        hx = cx + int(radius * 0.6 * math.cos(angle))
        hy = cy + int(radius * 0.6 * math.sin(angle))
        draw.ellipse(
            [hx - 40, hy - 20, hx + 40, hy + 20],
            fill=(100, 80, 120, 15),
        )


def draw_amplifier_glow(draw: ImageDraw, width: int, height: int) -> None:
    """Draw amplifier glow effect at the bottom of the image area."""
    cx = width // 2
    gy = int(height * 0.75)

    # Vacuum tube glow
    for i in range(5):
        tx = cx - 120 + i * 60
        for g in range(4):
            glow_radius = 30 - g * 5
            alpha = 40 - g * 8
            if g == 0:
                fill = (255, 150, 50, alpha)
            elif g == 1:
                fill = (200, 80, 40, alpha)
            elif g == 2:
                fill = (150, 40, 60, alpha)
            else:
                fill = (100, 20, 80, alpha)
            draw.ellipse(
                [tx - glow_radius, gy - glow_radius, tx + glow_radius, gy + glow_radius],
                fill=fill,
            )

    # Tube bodies
    for i in range(5):
        tx = cx - 120 + i * 60
        draw.rectangle([tx - 12, gy - 40, tx + 12, gy + 30], fill=(40, 35, 45))
        draw.rectangle([tx - 8, gy - 35, tx + 8, gy + 25], fill=(60, 50, 65))

    # Warm light pool
    for g in range(8, 0, -1):
        alpha = 8 - g
        draw.ellipse(
            [cx - g * 80, gy + 30, cx + g * 80, gy + 80 + g * 20],
            fill=(255, 200, 100, alpha),
        )


def draw_sound_waves(draw: ImageDraw, width: int, height: int) -> None:
    """Draw abstract sound wave lines across the cover."""
    import random

    rng = random.Random(17)
    for _ in range(20):
        y = rng.randint(int(height * 0.15), int(height * 0.68))
        x_start = rng.randint(100, 400)
        x_end = rng.randint(width - 400, width - 100)
        amplitude = rng.randint(5, 20)
        frequency = 0.02 + rng.random() * 0.03
        points = []
        for x in range(x_start, x_end, 4):
            y_offset = math.sin(x * frequency) * amplitude
            points.append((x, y + y_offset))
        alpha = rng.randint(15, 35)
        draw.line(points, fill=(150, 100, 200, alpha), width=1)


def draw_speaker_grill(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a subtle speaker grill pattern behind the vinyl."""
    cx, cy = width // 2, int(height * 0.55)
    grill_w, grill_h = 420, 420
    sx, sy = cx - grill_w // 2, cy - grill_h // 2

    for y in range(sy, sy + grill_h, 6):
        draw.line(
            [(sx, y), (sx + grill_w, y)],
            fill=(20, 15, 25, 40),
            width=1,
        )


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark title panel at the bottom with white text for readability."""
    panel_top = TITLE_PANEL_TOP

    # Dark semi-transparent panel
    draw.rectangle([(0, panel_top), (width, height)], fill=(10, 5, 18, 220))

    # Subtle top border
    draw.line([(0, panel_top), (width, panel_top)], fill=(80, 50, 100), width=2)

    # Draw a simple decorative line
    line_y = panel_top + 30
    draw.rectangle([(width // 2 - 100, line_y), (width // 2 + 100, line_y + 1)], fill=(150, 100, 180, 100))

    # Title text
    title = "The Velvet\nUnderground"
    title_font_size = 80
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

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
    draw.text((ax, ay), author, fill=(200, 200, 200), font=author_font)

    # Decorative line below author
    line_y2 = ay + 50
    draw.rectangle([(width // 2 - 60, line_y2), (width // 2 + 60, line_y2 + 1)], fill=(150, 100, 180, 80))


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Velvet Underground")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Speaker grill pattern behind vinyl
    draw_speaker_grill(draw, WIDTH, HEIGHT)

    # Step 3: Sound waves across the cover
    draw_sound_waves(draw, WIDTH, HEIGHT)

    # Step 4: Amplifier glow
    draw_amplifier_glow(draw, WIDTH, HEIGHT)

    # Step 5: Vinyl record
    draw_vinyl(draw, WIDTH, HEIGHT)

    # Step 6: Cassette tape
    draw_cassette(draw, WIDTH, HEIGHT)

    # Step 7: Title panel at bottom
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arial.ttf"),
        "small": str(FONTS_DIR / "arialbd.ttf"),
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