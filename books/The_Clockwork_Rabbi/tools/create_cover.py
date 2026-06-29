#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Clockwork Rabbi using PIL."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

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
TITLE_PANEL_Y = 1920


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def gradient(draw: ImageDraw, width: int, height: int, colors: list[tuple[int, int, int]]) -> None:
    """Draw a vertical gradient across the image."""
    n = len(colors) - 1
    for y in range(height):
        frac = y / height
        idx = frac * n
        i = int(idx)
        t = idx - i
        i = min(i, n - 1)
        r = int(colors[i][0] * (1 - t) + colors[i + 1][0] * t)
        g = int(colors[i][1] * (1 - t) + colors[i + 1][1] * t)
        b = int(colors[i][2] * (1 - t) + colors[i + 1][2] * t)
        draw.line([(0, y), (width, y)], fill=(r, g, b))


def draw_castle(draw: ImageDraw, x: int, base_y: int):
    """Draw a simplified Prague castle silhouette."""
    # Main body
    draw.rectangle([x - 120, base_y - 200, x + 120, base_y], fill=(80, 70, 55))
    # Towers
    for dx in (-140, -80, 80, 140):
        draw.rectangle([x + dx - 20, base_y - 260, x + dx + 20, base_y], fill=(90, 80, 65))
        # Roof peaks
        draw.polygon(
            [(x + dx - 22, base_y - 260), (x + dx, base_y - 300), (x + dx + 22, base_y - 260)],
            fill=(100, 85, 70),
        )
    # Central tower taller
    draw.rectangle([x - 40, base_y - 320, x + 40, base_y], fill=(100, 90, 75))
    draw.polygon(
        [(x - 42, base_y - 320), (x, base_y - 370), (x + 42, base_y - 320)],
        fill=(110, 95, 80),
    )
    # Windows
    for wx in range(x - 100, x + 101, 40):
        draw.rectangle([wx - 6, base_y - 140, wx + 6, base_y - 110], fill=(220, 180, 100))
    for wx in range(x - 60, x + 61, 60):
        draw.rectangle([wx - 5, base_y - 250, wx + 5, base_y - 220], fill=(220, 180, 100))
    # Gate arch
    draw.arc(
        [x - 30, base_y - 50, x + 30, base_y + 10],
        start=0, end=180, fill=(40, 35, 25), width=6
    )
    draw.rectangle([x - 30, base_y - 30, x + 30, base_y], fill=(40, 35, 25))


def draw_golem(draw: ImageDraw, x: int, base_y: int):
    """Draw a golem silhouette."""
    # Head
    draw.ellipse([x - 25, base_y - 160, x + 25, base_y - 120], fill=(50, 50, 55))
    # Body
    draw.rectangle([x - 30, base_y - 120, x + 30, base_y - 30], fill=(55, 55, 60))
    # Chest gear detail
    draw.ellipse([x - 14, base_y - 100, x + 14, base_y - 72], outline=(120, 110, 90), width=3)
    draw.ellipse([x - 8, base_y - 94, x + 8, base_y - 78], outline=(120, 110, 90), width=2)
    # Arms
    draw.rectangle([x - 55, base_y - 115, x - 30, base_y - 40], fill=(50, 50, 55))
    draw.rectangle([x + 30, base_y - 115, x + 55, base_y - 40], fill=(50, 50, 55))
    # Legs
    draw.rectangle([x - 28, base_y - 30, x - 5, base_y + 10], fill=(50, 50, 55))
    draw.rectangle([x + 5, base_y - 30, x + 28, base_y + 10], fill=(50, 50, 55))


def draw_cobblestone(draw: ImageDraw, width: int, y: int):
    """Draw a cobblestone path near the bottom."""
    for i in range(0, width, 60):
        dx = (i // 60) % 2 * 30
        draw.ellipse(
            [i - 25, y + dx - 12, i + 25, y + dx + 12],
            outline=(100, 95, 85), width=2,
        )


def create_cover(metadata_path: Path | str, output_path: Path | str) -> None:
    with open(metadata_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    model = meta.get("model", "")

    title = meta["title"]
    author = meta["author"]

    img = Image.new("RGB", (WIDTH, HEIGHT), color=(20, 15, 10))
    draw = ImageDraw.Draw(img)

    # Gradient background: dark brown -> deep gold -> dark gray
    gradient(
        draw, WIDTH, HEIGHT,
        colors=[(25, 18, 10), (60, 45, 20), (30, 28, 30)],
    )

    # Cobblestone path
    draw_cobblestone(draw, WIDTH, TITLE_PANEL_Y - 80)

    # Prague castle (upper area)
    castle_x = WIDTH // 2
    castle_base = int(TITLE_PANEL_Y * 0.65)
    draw_castle(draw, castle_x, castle_base)

    # Golem silhouette in front of castle, slightly to the left
    golem_x = WIDTH // 2 - 200
    golem_base = castle_base + 40
    draw_golem(draw, golem_x, golem_base)

    # Add a subtle glow around the golem (clockwork soul)
    glow_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)
    glow_draw.ellipse(
        [golem_x - 60, golem_base - 200, golem_x + 60, golem_base + 50],
        fill=(200, 170, 80, 20),
    )
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=20))
    img = Image.alpha_composite(img.convert("RGBA"), glow_layer)
    draw = ImageDraw.Draw(img)

    # Light rectangle for title panel at bottom
    draw.rectangle([0, TITLE_PANEL_Y, WIDTH, HEIGHT], fill=(240, 235, 225, 220))

    # Try to load fonts
    try:
        title_font = ImageFont.truetype("C:/Windows/Fonts/georgiab.ttf", 80)
        title_font_small = ImageFont.truetype("C:/Windows/Fonts/georgiab.ttf", 60)
        author_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 40)
        subtitle_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 28)
    except (IOError, OSError):
        title_font = ImageFont.load_default()
        title_font_small = ImageFont.load_default()
        author_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()

    # Title text — wrap if needed
    title_text = title
    title_y_start = TITLE_PANEL_Y + 80

    if len(title_text) > 20:
        # Split into two lines
        words = title_text.split()
        mid = len(words) // 2
        line1 = " ".join(words[:mid])
        line2 = " ".join(words[mid:])
        bbox1 = draw.textbbox((0, 0), line1, font=title_font_small)
        bbox2 = draw.textbbox((0, 0), line2, font=title_font_small)
        w1 = bbox1[2] - bbox1[0]
        w2 = bbox2[2] - bbox2[0]
        draw.text(((WIDTH - w1) // 2, title_y_start), line1, fill=(40, 30, 20), font=title_font_small)
        draw.text(((WIDTH - w2) // 2, title_y_start + 75), line2, fill=(40, 30, 20), font=title_font_small)
        author_y = title_y_start + 170
    else:
        bbox = draw.textbbox((0, 0), title_text, font=title_font)
        tw = bbox[2] - bbox[0]
        draw.text(((WIDTH - tw) // 2, title_y_start), title_text, fill=(40, 30, 20), font=title_font)
        author_y = title_y_start + 120

    # Author name
    author_bbox = draw.textbbox((0, 0), author, font=author_font)
    aw = author_bbox[2] - author_bbox[0]
    draw.text(((WIDTH - aw) // 2, author_y), author, fill=(80, 70, 50), font=author_font)

    # Genre subtitle
    genre_text = "A Historical Fantasy"
    genre_bbox = draw.textbbox((0, 0), genre_text, font=subtitle_font)
    gw = genre_bbox[2] - genre_bbox[0]
    draw.text(((WIDTH - gw) // 2, author_y + 55), genre_text, fill=(130, 120, 100), font=subtitle_font)

    # Save
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(output_path, "PNG")
    print(f"Cover saved to {output_path}")



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    create_cover(args.metadata, args.out)


if __name__ == "__main__":
    main()