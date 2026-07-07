#!/usr/bin/env python3
"""Cover: The White Raven — White raven on frozen birch branch under dark Arctic sky, lone figure crossing frozen lake."""

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
    """Deep arctic night sky with aurora green tones at the top, snow white below."""
    for y in range(height):
        if y < height * 0.35:
            t = y / (height * 0.35)
            c = lerp_color((5, 25, 40), (10, 50, 60), t)
        elif y < height * 0.55:
            t = (y - height * 0.35) / (height * 0.2)
            c = lerp_color((10, 50, 60), (20, 70, 80), t)
        elif y < height * 0.75:
            t = (y - height * 0.55) / (height * 0.2)
            c = lerp_color((20, 70, 80), (180, 210, 220), t)
        else:
            t = (y - height * 0.75) / (height * 0.25)
            c = lerp_color((180, 210, 220), (220, 230, 235), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_northern_lights(draw: ImageDraw, width: int, height: int) -> None:
    """Draw aurora-like glowing bands across the sky."""
    import random

    rng = random.Random(17)

    for band in range(4):
        start_y = height * 0.1 + band * height * 0.08 + rng.randint(-10, 10)
        end_y = start_y + height * 0.12 + rng.randint(-5, 5)

        colors = [
            (50, 255, 100, 60 + band * 10),
            (30, 200, 80, 40 + band * 8),
            (20, 150, 60, 25 + band * 5),
        ]

        for i in range(3):
            offset = i * 8
            for x in range(0, width, 2):
                wave = math.sin(x * 0.002 + band * 1.5 + i) * height * 0.04
                y_center = (start_y + end_y) / 2 + wave
                y_top = int(y_center - height * 0.02 - offset)
                y_bot = int(y_center + height * 0.02 + offset)
                alpha = max(0, min(255, colors[i][3] - abs(x - width // 2) // 15))
                if alpha > 5:
                    fill = (colors[i][0], colors[i][1], colors[i][2], alpha)
                    draw.line([(x, y_top), (x, y_bot)], fill=fill)


def draw_snowy_forest(draw: ImageDraw, width: int, height: int) -> None:
    """Draw snow-laden pine trees silhouetted in the dark."""
    tree_positions = [
        (60, height * 0.35, 2.4),
        (180, height * 0.30, 2.8),
        (320, height * 0.38, 2.2),
        (480, height * 0.28, 3.0),
        (width - 60, height * 0.32, 2.6),
        (width - 180, height * 0.36, 2.4),
        (width - 320, height * 0.30, 2.8),
        (width - 480, height * 0.34, 2.5),
        (130, height * 0.50, 2.0),
        (420, height * 0.45, 2.2),
        (width - 130, height * 0.48, 2.1),
        (width - 400, height * 0.42, 2.3),
    ]

    for tx, ty, scale in tree_positions:
        trunk_h = int(200 * scale)
        trunk_w = int(15 * scale)
        # Trunk
        draw.rectangle(
            [tx - trunk_w // 2, int(ty - trunk_h), tx + trunk_w // 2, int(ty)],
            fill=(15, 12, 10),
        )
        # Three tiers of snow-covered branches
        for tier in range(3):
            t_y = int(ty - trunk_h * (0.15 + tier * 0.3))
            t_w = int(80 * scale * (1 - tier * 0.2))
            t_h = int(40 * scale)
            # Dark needle base
            draw.polygon(
                [(tx - t_w, t_y + t_h), (tx, t_y - t_h), (tx + t_w, t_y + t_h)],
                fill=(10, 25, 15),
            )
            # Snow cap on top of foliage
            draw.polygon(
                [(tx - t_w + 10, t_y + t_h // 2), (tx, t_y - t_h + 5), (tx + t_w - 10, t_y + t_h // 2)],
                fill=(200, 210, 215),
            )


def draw_white_raven(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a white raven perched on a prominent branch."""
    # Branch
    bx = width // 2 + 80
    by = height * 0.45
    draw.line(
        [(bx - 120, by + 30), (bx + 60, by + 10)],
        fill=(20, 15, 10),
        width=6,
    )
    # Branch snow
    draw.line(
        [(bx - 120, by + 28), (bx + 60, by + 8)],
        fill=(200, 210, 215),
        width=3,
    )

    # Raven body - white
    ex, ey = bx - 20, by - 15
    # Body
    draw.ellipse([ex - 20, ey - 12, ex + 20, ey + 12], fill=(230, 235, 240))
    # Head
    draw.ellipse([ex + 15, ey - 18, ex + 32, ey], fill=(230, 235, 240))
    # Beak
    draw.polygon(
        [(ex + 30, ey - 12), (ex + 45, ey - 8), (ex + 30, ey - 6)],
        fill=(10, 10, 10),
    )
    # Eye
    draw.ellipse([ex + 22, ey - 14, ex + 26, ey - 10], fill=(5, 5, 5))
    # Wing
    draw.polygon(
        [(ex - 8, ey - 2), (ex - 25, ey - 8), (ex - 15, ey + 4)],
        fill=(200, 210, 215),
    )
    # Tail
    draw.polygon(
        [(ex - 18, ey + 2), (ex - 35, ey + 10), (ex - 30, ey + 14), (ex - 15, ey + 8)],
        fill=(210, 215, 220),
    )

    # Subtle light glow around the bird
    for i in range(3):
        glow_r = 35 + i * 10
        glow_alpha = 30 - i * 8
        draw.ellipse(
            [ex - glow_r, ey - glow_r, ex + glow_r, ey + glow_r],
            outline=(200, 220, 230, glow_alpha),
            width=1,
        )


def draw_snowflakes(draw: ImageDraw, width: int, height: int) -> None:
    """Draw falling snowflakes."""
    import random

    rng = random.Random(29)
    for _ in range(200):
        x = rng.randint(10, width - 10)
        y = rng.randint(10, height - 200)
        size = rng.randint(1, 4)
        alpha = rng.randint(80, 200)
        draw.ellipse(
            [x - size, y - size, x + size, y + size],
            fill=(255, 255, 255, alpha),
        )


def draw_snow_ground(draw: ImageDraw, width: int, height: int) -> None:
    """Draw undulating snow-covered ground at the bottom of the image area."""
    import random

    rng = random.Random(13)

    points = []
    base_y = height * 0.82
    for x in range(0, width + 1, 10):
        y = base_y + math.sin(x * 0.003) * 15 + rng.randint(-5, 5)
        points.append((x, y))

    # Ground fill
    snow_color = (220, 225, 230)
    for x in range(0, width + 1, 2):
        left_idx = int(x // 10)
        right_idx = min(left_idx + 1, len(points) - 1)
        y_ground = points[left_idx][1] + (points[right_idx][1] - points[left_idx][1]) * ((x % 10) / 10) if left_idx < len(points) else base_y
        draw.line([(x, int(y_ground)), (x, height)], fill=snow_color)


def draw_moon(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a pale winter moon behind clouds."""
    mx, my = width - 150, height * 0.15
    moon_radius = 40

    # Moon glow
    for r in range(60, 10, -10):
        alpha = max(0, 40 - r)
        draw.ellipse(
            [mx - r, my - r, mx + r, my + r],
            outline=(180, 200, 210, alpha),
            width=2,
        )

    # Moon
    draw.ellipse(
        [mx - moon_radius, my - moon_radius, mx + moon_radius, my + moon_radius],
        fill=(210, 215, 220),
    )
    # Moon shadow to give texture
    draw.ellipse(
        [mx - moon_radius + 5, my - moon_radius + 5, mx + moon_radius - 5, my + moon_radius - 5],
        fill=(195, 205, 215),
    )


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark title panel at the bottom."""
    panel_top = TITLE_PANEL_TOP

    # Dark semi-transparent panel
    draw.rectangle([(0, panel_top), (width, height)], fill=(10, 15, 25, 210))

    # Panel top border line (thin aurora green glow)
    for i in range(3):
        draw.line(
            [(0, panel_top - i), (width, panel_top - i)],
            fill=(50, 180, 100, 80 - i * 20),
            width=1,
        )

    # Title text
    title = "The White\nRaven"
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
        # White text with slight shadow for readability
        draw.text((tx + 2, y_offset + 2), line, fill=(5, 10, 15), font=title_font)
        draw.text((tx, y_offset), line, fill=(220, 225, 230), font=title_font)
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
    ay = y_offset + 40
    draw.text((ax + 1, ay + 1), author, fill=(5, 10, 15), font=author_font)
    draw.text((ax, ay), author, fill=(180, 200, 210), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The White Raven")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    for y in range(HEIGHT):
        if y < HEIGHT * 0.35:
            t = y / (HEIGHT * 0.35)
            c = lerp_color((5, 25, 40), (10, 50, 60), t)
        elif y < HEIGHT * 0.55:
            t = (y - HEIGHT * 0.35) / (HEIGHT * 0.2)
            c = lerp_color((10, 50, 60), (20, 70, 80), t)
        elif y < HEIGHT * 0.75:
            t = (y - HEIGHT * 0.55) / (HEIGHT * 0.2)
            c = lerp_color((20, 70, 80), (180, 210, 220), t)
        else:
            t = (y - HEIGHT * 0.75) / (HEIGHT * 0.25)
            c = lerp_color((180, 210, 220), (220, 230, 235), t)
        draw.line([(0, y), (WIDTH, y)], fill=c)

    base_y = int(HEIGHT * 0.82)
    rng_snow = random.Random(13)
    for x in range(0, WIDTH + 1, 2):
        yg = base_y + math.sin(x * 0.003) * 15 + rng_snow.randint(-5, 5)
        draw.line([(x, int(yg)), (x, HEIGHT)], fill=(220, 225, 230))

    birch_cx = WIDTH // 2 + 80
    draw.line([(birch_cx, int(HEIGHT * 0.2)), (birch_cx, int(HEIGHT * 0.55))], fill=(40, 35, 30), width=8)
    draw.line([(birch_cx - 40, int(HEIGHT * 0.35)), (birch_cx + 40, int(HEIGHT * 0.35))], fill=(40, 35, 30), width=5)
    for bx in [birch_cx - 30, birch_cx + 20]:
        draw.line([(bx, int(HEIGHT * 0.3)), (bx + 20 if bx > birch_cx else bx - 20, int(HEIGHT * 0.25))], fill=(40, 35, 30), width=3)

    ex, ey = birch_cx - 20, int(HEIGHT * 0.42)
    draw.ellipse([ex - 18, ey - 10, ex + 18, ey + 10], fill=(230, 235, 240))
    draw.ellipse([ex + 14, ey - 16, ex + 28, ey], fill=(230, 235, 240))
    draw.polygon([(ex + 26, ey - 10), (ex + 38, ey - 6), (ex + 26, ey - 4)], fill=(10, 10, 10))
    draw.ellipse([ex + 20, ey - 12, ex + 23, ey - 8], fill=(5, 5, 5))
    draw.polygon([(ex - 6, ey), (ex - 22, ey - 6), (ex - 14, ey + 3)], fill=(200, 210, 215))

    figure_cx = WIDTH // 2 - 120
    figure_cy = int(HEIGHT * 0.68)
    draw.ellipse([figure_cx - 8, figure_cy - 50, figure_cx + 8, figure_cy - 35], fill=(20, 22, 25, 200))
    draw.polygon([(figure_cx - 14, figure_cy - 35), (figure_cx + 14, figure_cy - 35), (figure_cx + 16, figure_cy), (figure_cx - 16, figure_cy)], fill=(20, 22, 25, 200))
    draw.line([(figure_cx, figure_cy), (figure_cx, figure_cy + 30)], fill=(20, 22, 25, 200), width=4)

    rng = random.Random(29)
    for _ in range(200):
        sx = rng.randint(10, WIDTH - 10)
        sy = rng.randint(10, 1800)
        sr = rng.randint(1, 3)
        sa = rng.randint(80, 200)
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 255, 255, sa))

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