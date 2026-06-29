#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Last Migration using PIL."""

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



WIDTH = 1600
HEIGHT = 2560
TITLE_PANEL_TOP = 1920
TITLE_PANEL_BOTTOM = HEIGHT


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def make_gradient(draw: ImageDraw, width: int, height: int, colors: list[tuple[int, int, int]]) -> None:
    """Draw a vertical gradient across the full image."""
    bands = len(colors) - 1
    band_height = height // bands
    for i in range(bands):
        r1, g1, b1 = colors[i]
        r2, g2, b2 = colors[i + 1]
        for y in range(band_height * i, min(band_height * (i + 1), height)):
            t = (y - band_height * i) / band_height
            r = int(r1 + (r2 - r1) * t)
            g = int(g1 + (g2 - g1) * t)
            b = int(b1 + (b2 - b1) * t)
            draw.line([(0, y), (width, y)], fill=(r, g, b))


def draw_ash_dunes(draw: ImageDraw, width: int, height: int) -> None:
    """Draw rolling ash dune silhouettes across the lower landscape area."""
    import random
    rng = random.Random(42)
    for dune in range(6):
        base_y = 800 + dune * 130
        pts = []
        segments = 20
        for i in range(segments + 1):
            x = int(width * i / segments)
            y_var = rng.randint(-40, 40) + dune * 18
            wave = 50 * __import__("math").sin(i * 0.5 + dune)
            pts.append((x, base_y + int(wave) + y_var))
        dark = 50 + dune * 10
        draw.polygon(pts + [(width, height), (0, height)], fill=(dark, dark - 5, dark - 10), outline=None)


def draw_wall(draw: ImageDraw, width: int) -> None:
    """Draw the white wall on the horizon."""
    wall_x = int(width * 0.15)
    wall_w = int(width * 0.7)
    wall_base_y = 780
    wall_top_y = 300
    # Wall body
    draw.rectangle([wall_x, wall_top_y, wall_x + wall_w, wall_base_y], fill=(200, 195, 190))
    # Panel seams
    for i in range(1, 8):
        sx = wall_x + int(wall_w * i / 8)
        draw.line([(sx, wall_top_y + 20), (sx, wall_base_y)], fill=(170, 165, 160), width=2)
    # Gate
    gate_w = 120
    gate_x = wall_x + (wall_w - gate_w) // 2
    draw.rectangle([gate_x, wall_base_y - 200, gate_x + gate_w, wall_base_y], fill=(80, 75, 70))
    # Horizon line
    draw.line([(0, wall_base_y), (width, wall_base_y)], fill=(180, 170, 150), width=3)


def draw_figures(draw: ImageDraw, width: int) -> None:
    """Draw small walking figures in the foreground."""
    positions = [
        (int(width * 0.25), 1300),
        (int(width * 0.35), 1280),
        (int(width * 0.28), 1320),
        (int(width * 0.55), 1250),
        (int(width * 0.60), 1230),
        (int(width * 0.58), 1260),
    ]
    for x, y in positions:
        # Head
        draw.ellipse([x - 4, y - 14, x + 4, y - 6], fill=(60, 55, 50))
        # Body
        draw.line([(x, y - 6), (x, y + 10)], fill=(60, 55, 50), width=3)
        # Left leg
        draw.line([(x, y + 10), (x - 4, y + 20)], fill=(60, 55, 50), width=2)
        # Right leg
        draw.line([(x, y + 10), (x + 4, y + 22)], fill=(60, 55, 50), width=2)


def draw_title_panel(draw: ImageDraw, width: int, title: str, author: str) -> None:
    """Draw the light title panel at the bottom with title and author."""
    # Light panel background
    draw.rectangle(
        [0, TITLE_PANEL_TOP, width, TITLE_PANEL_BOTTOM],
        fill=(235, 230, 220),
        outline=None,
    )
    # Subtle top border for panel
    draw.line([(0, TITLE_PANEL_TOP), (width, TITLE_PANEL_TOP)], fill=(200, 195, 185), width=2)

    font_paths = {
        "georgiab": "C:/Windows/Fonts/georgiab.ttf",
        "arialbd": "C:/Windows/Fonts/arialbd.ttf",
        "arial": "C:/Windows/Fonts/arial.ttf",
    }

    # Title
    title_font_size = 72
    title_font = None
    for fs in range(72, 40, -2):
        try:
            title_font = ImageFont.truetype(font_paths["georgiab"], fs)
            break
        except Exception:
            continue
    if title_font is None:
        title_font = ImageFont.load_default()

    # Wrap title if needed
    title_lines = [title]
    title_fallback = title_font
    for attempt_fs in range(72, 40, -2):
        try:
            tf = ImageFont.truetype(font_paths["georgiab"], attempt_fs)
            if len(title) > 18:
                mid = len(title) // 2
                space_idx = title.find(" ", mid - 5, mid + 5)
                if space_idx > 0:
                    title_lines = [title[:space_idx], title[space_idx + 1:]]
                else:
                    title_lines = [title[:mid], title[mid:]]
            try:
                lw0 = draw.textlength(title_lines[0], font=tf)
                lw1 = draw.textlength(title_lines[1], font=tf) if len(title_lines) > 1 else 0
            except Exception:
                lw0 = attempt_fs * len(title_lines[0]) * 0.6
                lw1 = attempt_fs * len(title_lines[1]) * 0.6 if len(title_lines) > 1 else 0
            if lw0 < width - 100 and lw1 < width - 100:
                title_font = tf
                break
        except Exception:
            continue
    else:
        title_font = title_fallback

    line_height = title_font_size + 10
    total_text_height = len(title_lines) * line_height
    start_y = TITLE_PANEL_TOP + (HEIGHT - TITLE_PANEL_TOP - total_text_height) // 2 - 30

    for i, line in enumerate(title_lines):
        try:
            lw = draw.textlength(line, font=title_font)
        except Exception:
            lw = title_font_size * len(line) * 0.6
        tx = (width - int(lw)) // 2
        ty = start_y + i * line_height
        draw.text((tx, ty), line, fill=(60, 55, 50), font=title_font)

    # Author
    author_y = start_y + len(title_lines) * line_height + 15
    author_font = None
    for fs in range(28, 16, -2):
        try:
            author_font = ImageFont.truetype(font_paths["arialbd"], fs)
            try:
                aw = draw.textlength(author, font=author_font)
            except Exception:
                aw = fs * len(author) * 0.55
            if aw < width - 200:
                break
        except Exception:
            continue
    if author_font is None:
        author_font = ImageFont.load_default()

    try:
        aw = draw.textlength(author, font=author_font)
    except Exception:
        aw = 28 * len(author) * 0.55
    draw.text(((width - int(aw)) // 2, author_y), author, fill=(100, 95, 90), font=author_font)


def build(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Last Migration")
    author = metadata.get("author", "Bar\305\261\305\237 K\305\261s\305\261r")
    model = metadata.get("model", "")

    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)

    # Gradient background: sepia-gray-brown tones
    colors = [
        (180, 165, 145),   # light tan sky
        (150, 135, 115),   # muted brown
        (120, 105, 90),    # dark taupe
        (90, 80, 70),      # deep gray-brown
        (70, 60, 55),      # dark ash
    ]
    make_gradient(draw, WIDTH, HEIGHT, colors)

    # Draw wall on horizon
    draw_wall(draw, WIDTH)

    # Draw ash dunes
    draw_ash_dunes(draw, WIDTH, HEIGHT)

    # Draw small walking figures
    draw_figures(draw, WIDTH)

    # Ash particles overlay (subtle noise effect)
    import random
    rng = random.Random(7)
    for _ in range(800):
        x = rng.randint(0, WIDTH - 1)
        y = rng.randint(0, TITLE_PANEL_TOP - 1)
        alpha = rng.randint(20, 60)
        draw.point((x, y), fill=(alpha, alpha, alpha))

    # Draw title panel
    draw_title_panel(draw, WIDTH, title, author)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    build(args.metadata.resolve(), args.out.resolve())


if __name__ == "__main__":
    main()