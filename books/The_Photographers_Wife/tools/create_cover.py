#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Photographer's Wife."""

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
    """Amber to deep shadow gradient for the postwar darkroom feel."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((80, 55, 30), (40, 25, 15), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((40, 25, 15), (20, 15, 12), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((20, 15, 12), (8, 5, 4), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_hanging_negatives(draw: ImageDraw, width: int, height: int) -> None:
    """Draw film negatives hanging from a wire across the upper portion."""
    rng = random.Random(17)
    wire_y = int(height * 0.25)
    # Draw the wire
    draw.line([(0, wire_y), (width, wire_y)], fill=(160, 140, 120), width=2)

    for x in range(100, width - 50, 120):
        neg_height = rng.randint(80, 160)
        neg_width = 35
        clip_offset = rng.randint(-15, 15)

        # Clothespin
        draw.rectangle([x - 4, wire_y - 6, x + 4, wire_y + 8], fill=(120, 100, 80))

        # Negative strip
        nx = x - neg_width // 2
        ny = wire_y + 8
        draw.rectangle([nx, ny, nx + neg_width, ny + neg_height], fill=(30, 25, 20))

        # Frames on the negative
        for frame_i in range(neg_height // 35):
            fy = ny + 8 + frame_i * 35
            draw.rectangle([nx + 4, fy, nx + neg_width - 4, fy + 24], fill=(50, 40, 30))
            # Tiny image suggestion inside each frame
            if frame_i % 2 == 0:
                draw.rectangle([nx + 8, fy + 4, nx + neg_width - 8, fy + 20], fill=(60, 45, 35))
            else:
                draw.ellipse([nx + 8, fy + 4, nx + neg_width - 8, fy + 20], fill=(55, 40, 32))

        # Wire sag between clips
        next_x = x + 120 if x + 120 < width - 50 else width - 50
        if next_x > x:
            sag_y = wire_y + rng.randint(3, 8)
            draw.line([(x, wire_y), ((x + next_x) // 2, sag_y), (next_x, wire_y)], fill=(160, 140, 120), width=2)


def draw_tokyo_street(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a low Tokyo street scene at the horizon level."""
    horizon = int(height * 0.55)

    # Low buildings in silhouette
    for bx in range(0, width, 80):
        bh = horizon - rng.randint(30, 90)
        bw = rng.randint(60, 90)
        draw.rectangle([bx, bh, bx + bw, horizon], fill=(25, 18, 12))

        # Roof details
        draw.line([(bx, bh), (bx + bw // 2, bh - 8), (bx + bw, bh)], fill=(20, 14, 10), width=2)

        # Window suggestions
        for wy in range(bh + 10, horizon - 10, 20):
            for wx in range(bx + 5, bx + bw - 10, 18):
                if rng.random() < 0.4:
                    draw.rectangle([wx, wy, wx + 10, wy + 12], fill=(60, 45, 30))

    # Street / road at base of buildings
    draw.rectangle([(0, horizon - 2), (width, horizon + 4)], fill=(15, 10, 8))

    # Lantern posts
    for lx in [150, 500, 850, 1200, 1450]:
        draw.rectangle([lx, horizon - 100, lx + 4, horizon], fill=(40, 35, 30))
        glow = rng.choice([(180, 130, 60, 40), (200, 150, 70, 30)])
        draw.ellipse([lx - 15, horizon - 115, lx + 19, horizon - 95], fill=glow)


def draw_darkroom_glow(draw: ImageDraw, width: int, height: int) -> None:
    """Add a subtle red safelight glow from the right side."""
    glow_center_x = width + 100
    glow_center_y = int(height * 0.5)
    for r in range(200, 50, -10):
        alpha = max(0, 30 - (200 - r) // 7)
        if alpha > 0:
            draw.ellipse(
                [glow_center_x - r, glow_center_y - r, glow_center_x + r, glow_center_y + r],
                fill=(120, 30, 20, alpha),
            )


def draw_amber_dust(draw: ImageDraw, width: int, height: int) -> None:
    """Scatter small amber light specks in the air, like dust in a darkroom beam."""
    rng = random.Random(42)
    for _ in range(80):
        x = rng.randint(0, width)
        y = rng.randint(0, int(height * 0.7))
        size = rng.randint(1, 3)
        alpha = rng.randint(20, 60)
        draw.ellipse([x - size, y - size, x + size, y + size], fill=(200, 150, 80, alpha))


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom with white text."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    draw.rectangle([(0, panel_top), (width, height)], fill=(15, 10, 8))

    # Subtle top border
    draw.line([(0, panel_top), (width, panel_top)], fill=(60, 40, 30), width=2)

    # Horizontal rule decoration
    rule_y = panel_top + 50
    draw.line([(400, rule_y), (1200, rule_y)], fill=(160, 130, 100), width=1)

    # Title text - use arialbd.ttf
    title = "The Photographer's\nWife"
    title_font_size = 68
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
        draw.text((tx, y_offset), line, fill=(240, 235, 225), font=title_font)
        y_offset += 95

    # Subtle horizontal rule
    rule_y2 = y_offset + 10
    draw.line([(550, rule_y2), (1050, rule_y2)], fill=(100, 80, 65), width=1)

    # Author name
    author = "Barış Kısır"
    author_font_size = 34
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
    ay = y_offset + 30
    draw.text((ax, ay), author, fill=(180, 170, 155), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Photographer's Wife")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    global rng
    rng = random.Random(23)

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background - amber to deep shadow
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Darkroom red safelight glow
    draw_darkroom_glow(draw, WIDTH, HEIGHT)

    # Step 3: Tokyo street scene at horizon
    draw_tokyo_street(draw, WIDTH, HEIGHT)

    # Step 4: Hanging film negatives
    draw_hanging_negatives(draw, WIDTH, HEIGHT)

    # Step 5: Amber dust motes
    draw_amber_dust(draw, WIDTH, HEIGHT)

    # Step 6: Title panel at bottom
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arial.ttf"),
        "small": str(FONTS_DIR / "arial.ttf"),
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