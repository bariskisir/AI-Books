#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Cold Water — Florida hurricane debut novel."""

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


def draw_hurricane_sky(draw: ImageDraw, width: int, height: int) -> None:
    """Storm gray to bruised purple gradient for the hurricane sky."""
    for y in range(height):
        if y < height * 0.3:
            t = y / (height * 0.3)
            c = lerp_color((80, 85, 90), (55, 60, 70), t)
        elif y < height * 0.6:
            t = (y - height * 0.3) / (height * 0.3)
            c = lerp_color((55, 60, 70), (40, 45, 55), t)
        else:
            t = (y - height * 0.6) / (height * 0.4)
            c = lerp_color((40, 45, 55), (20, 22, 30), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_storm_clouds(draw: ImageDraw, width: int, height: int) -> None:
    """Draw layered storm clouds across the sky."""
    rng = random.Random(1)
    cloud_positions = [
        (width * 0.1, height * 0.08, 1.2),
        (width * 0.35, height * 0.05, 1.5),
        (width * 0.6, height * 0.12, 1.3),
        (width * 0.8, height * 0.06, 1.1),
        (width * 0.2, height * 0.2, 0.9),
        (width * 0.5, height * 0.18, 1.0),
        (width * 0.75, height * 0.22, 0.8),
        (width * -0.1, height * 0.15, 1.4),
    ]
    for cx, cy, scale in cloud_positions:
        w = int(400 * scale)
        h = int(120 * scale)
        # Cloud body
        for i in range(5):
            ox = rng.randint(-30, 30)
            oy = rng.randint(-20, 20)
            rw = int(w * (0.6 + rng.random() * 0.4))
            rh = int(h * (0.6 + rng.random() * 0.4))
            draw.ellipse(
                [int(cx + ox - rw // 2), int(cy + oy - rh // 2), int(cx + ox + rw // 2), int(cy + oy + rh // 2)],
                fill=(45, 50, 60, 180),
            )
        # Darker bottom
        draw.ellipse(
            [int(cx - w // 2), int(cy + h // 4), int(cx + w // 2), int(cy + h // 2 + 20)],
            fill=(30, 35, 45, 200),
        )


def draw_palmetto(draw: ImageDraw, x: int, y: int, scale: float, rng: random.Random) -> None:
    """Draw a single palmetto plant."""
    # Fronds radiating from center
    frond_count = rng.randint(6, 10)
    for i in range(frond_count):
        angle = (i / frond_count) * 360 + rng.randint(-15, 15)
        radians = math.radians(angle)
        length = int(rng.randint(60, 120) * scale)
        end_x = x + int(math.cos(radians) * length)
        end_y = y + int(math.sin(radians) * (length * 0.6))
        # Draw frond as connected line segments
        segments = 8
        points = []
        for s in range(segments + 1):
            t = s / segments
            px = x + (end_x - x) * t + rng.randint(-8, 8)
            py = y + (end_y - y) * t + rng.randint(-4, 4)
            points.append((px, py))
        draw.line(points, fill=(25, 55, 30), width=rng.randint(2, 4))
        # Leaf tips
        draw.ellipse(
            [end_x - 3, end_y - 3, end_x + 3, end_y + 3],
            fill=(35, 70, 40),
        )


def draw_trailer(draw: ImageDraw, x: int, y: int, scale: float) -> None:
    """Draw a small double-wide trailer."""
    w, h = int(280 * scale), int(140 * scale)
    # Main body
    draw.rectangle([x - w // 2, y - h // 2, x + w // 2, y + h // 2], fill=(160, 150, 130))
    # Roof line
    draw.line([(x - w // 2 - 10, y - h // 2), (x + w // 2 + 10, y - h // 2)], fill=(100, 95, 80), width=4)
    # Windows
    for wx in range(-60, 80, 50):
        draw.rectangle(
            [x + wx, y - h // 2 + 20, x + wx + 30, y - h // 2 + 55],
            fill=(30, 35, 50),
        )
    # Door
    draw.rectangle([x + 20, y - h // 2 + 20, x + 55, y + h // 2], fill=(100, 55, 35))
    # Steps
    draw.rectangle([x + 15, y + h // 2, x + 60, y + h // 2 + 15], fill=(120, 115, 100))
    # Skirting
    draw.rectangle([x - w // 2, y + h // 2, x + w // 2, y + h // 2 + 12], fill=(90, 85, 75))
    # Air conditioner in window
    draw.rectangle(
        [x - w // 2 + 10, y - h // 2 + 25, x - w // 2 + 45, y - h // 2 + 55],
        fill=(100, 100, 100),
    )


def draw_trailer_park(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a small cluster of trailers and palmettos for the landscape."""
    rng = random.Random(3)
    # Ground line
    ground_y = int(height * 0.72)
    draw.rectangle([(0, ground_y), (width, height)], fill=(55, 65, 35))

    # Trailer 1 (center, main)
    draw_trailer(draw, width // 2, ground_y - 80, 1.0)
    # Trailer 2 (left, smaller)
    draw_trailer(draw, width // 2 - 350, ground_y - 65, 0.7)
    # Trailer 3 (right, smaller)
    draw_trailer(draw, width // 2 + 320, ground_y - 60, 0.6)

    # Palmettos
    for _ in range(15):
        px = rng.randint(50, width - 50)
        py = ground_y + rng.randint(10, 60)
        sc = 0.5 + rng.random() * 0.8
        draw_palmetto(draw, px, py, sc, rng)

    # Broken tree / debris in foreground
    for _ in range(6):
        dx = rng.randint(100, width - 100)
        dy = ground_y + rng.randint(30, 100)
        # Fallen branch
        draw.line(
            [(dx, dy), (dx + rng.randint(30, 80), dy + rng.randint(10, 30))],
            fill=(40, 35, 25),
            width=rng.randint(3, 6),
        )

    # Additional ground texture
    for _ in range(20):
        gx = rng.randint(0, width)
        gy = ground_y + rng.randint(0, 200)
        draw.rectangle([gx, gy, gx + 2, gy + 2], fill=(60, 75, 40))


def draw_rain(draw: ImageDraw, width: int, height: int) -> None:
    """Draw diagonal rain streaks across the image."""
    rng = random.Random(5)
    for _ in range(200):
        x = rng.randint(0, width)
        y = rng.randint(0, int(height * 0.75))
        length = rng.randint(15, 40)
        draw.line(
            [(x, y), (x + 8, y + length)],
            fill=(180, 190, 200, 60),
            width=1,
        )


def draw_citrus_glow(draw: ImageDraw, width: int, height: int) -> None:
    """Subtle citrus color glow in the lower sky — a hint of Florida."""
    for y in range(int(height * 0.4), int(height * 0.6)):
        t = (y - height * 0.4) / (height * 0.2)
        alpha = int(20 * (1 - abs(t - 0.5) * 2))
        if alpha > 0:
            t_adj = (y - height * 0.4) / (height * 0.2)
            c = lerp_color((220, 160, 50), (240, 180, 60), t_adj)
            draw.line([(0, y), (width, y)], fill=(c[0], c[1], c[2], alpha))


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom with WHITE text."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    draw.rectangle([(0, panel_top), (width, height)], fill=(18, 20, 25, 230))

    # Subtle line at top of panel
    draw.line([(0, panel_top), (width, panel_top)], fill=(80, 85, 95), width=2)

    # Title text - use arialbd.ttf
    title = "The Cold Water"
    title_font_size = 80
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        try:
            title_font = ImageFont.truetype(str(font_paths["fallback"]), title_font_size)
        except Exception:
            title_font = ImageFont.load_default()

    # Draw title centered in white
    try:
        bbox = draw.textbbox((0, 0), title, font=title_font)
        tw = bbox[2] - bbox[0]
    except Exception:
        tw = 0
    tx = (width - tw) // 2
    ty = panel_top + 80
    draw.text((tx, ty), title, fill=(255, 255, 255), font=title_font)

    # Author name below title
    author = "Barış Kısır"
    author_font_size = 36
    try:
        author_font = ImageFont.truetype(str(font_paths["author"]), author_font_size)
    except Exception:
        try:
            author_font = ImageFont.truetype(str(font_paths["fallback"]), author_font_size)
        except Exception:
            author_font = ImageFont.load_default()

    try:
        abbox = draw.textbbox((0, 0), author, font=author_font)
        aw = abbox[2] - abbox[0]
    except Exception:
        aw = 0
    ax = (width - aw) // 2
    ay = ty + 110
    draw.text((ax, ay), author, fill=(200, 200, 200), font=author_font)

    # Genre line at bottom
    genre = "A DEBUT NOVEL"
    genre_font_size = 20
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
    gy = ay + 60
    draw.text((gx, gy), genre, fill=(150, 155, 160), font=genre_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Cold Water")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Hurricane sky gradient
    draw_hurricane_sky(draw, WIDTH, HEIGHT)

    # Step 2: Storm clouds
    draw_storm_clouds(draw, WIDTH, HEIGHT)

    # Step 3: Citrus glow in lower sky
    draw_citrus_glow(draw, WIDTH, HEIGHT)

    # Step 4: Trailer park landscape
    draw_trailer_park(draw, WIDTH, HEIGHT)

    # Step 5: Rain streaks
    draw_rain(draw, WIDTH, HEIGHT)

    # Step 6: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
        "small": str(FONTS_DIR / "arial.ttf"),
        "fallback": str(FONTS_DIR / "arial.ttf"),
    }
    draw_title_panel(draw, WIDTH, HEIGHT, font_paths)

    # Soften slightly
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