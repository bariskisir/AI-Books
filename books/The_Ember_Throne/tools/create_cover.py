#!/usr/bin/env python3
"""Generate 1600x2560 book cover for The Ember Throne using PIL."""

import argparse
import json
import os
import textwrap
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

FONT_DIR = "C:/Windows/Fonts"
TITLE_FONT = os.path.join(FONT_DIR, "georgiab.ttf")
AUTHOR_FONT = os.path.join(FONT_DIR, "arialbd.ttf")
SMALL_FONT = os.path.join(FONT_DIR, "arial.ttf")


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def create_gradient(width: int, height: int, colors: list[tuple[int, int, int]]) -> Image.Image:
    img = Image.new("RGB", (width, height))
    pix = img.load()
    n = len(colors) - 1
    for y in range(height):
        ratio = y / height
        idx = min(int(ratio * n), n - 1)
        local_ratio = (ratio * n) - idx
        c1 = colors[idx]
        c2 = colors[idx + 1]
        r = int(c1[0] + (c2[0] - c1[0]) * local_ratio)
        g = int(c1[1] + (c2[1] - c1[1]) * local_ratio)
        b = int(c1[2] + (c2[2] - c1[2]) * local_ratio)
        for x in range(width):
            pix[x, y] = (r, g, b)
    return img


def draw_throne(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    """Draw a volcanic throne room scene using basic shapes."""
    cx, cy = width // 2, height // 3

    # Distant volcano/mountain silhouette
    mountain_color = (20, 10, 5)
    points = [(0, cy + 200), (200, cy - 50), (350, cy + 50), (cx, cy - 150),
              (width - 350, cy + 50), (width - 200, cy - 50), (width, cy + 200)]
    draw.polygon(points, fill=mountain_color, outline=None)

    # Lava glow at peak
    draw.ellipse([cx - 60, cy - 200, cx + 60, cy - 100], fill=(220, 80, 20))
    draw.ellipse([cx - 40, cy - 190, cx + 40, cy - 120], fill=(255, 150, 30))
    draw.ellipse([cx - 20, cy - 180, cx + 20, cy - 140], fill=(255, 220, 80))

    # Lava streams down the mountain
    for offset_x in [-30, -10, 10, 30]:
        for i in range(5):
            y1 = cy - 120 + i * 30
            x1 = cx + offset_x + i * 8
            draw.line([(x1, y1), (x1 + 15, y1 + 25)], fill=(200, 60, 10), width=3)
            draw.line([(x1, y1), (x1 + 15, y1 + 25)], fill=(255, 180, 40), width=1)

    # Throne silhouette in foreground
    throne_color = (15, 10, 8)
    throne_x = cx - 100
    throne_y = cy + 80
    # Back of throne
    draw.rectangle([throne_x - 20, throne_y - 60, throne_x + 220, throne_y + 180], fill=throne_color)
    # Throne top arch
    draw.ellipse([throne_x - 30, throne_y - 80, throne_x + 230, throne_y + 20], fill=throne_color)
    # Seat
    draw.rectangle([throne_x + 10, throne_y + 80, throne_x + 190, throne_y + 180], fill=(25, 18, 12))
    # Arm rests
    draw.rectangle([throne_x - 10, throne_y + 40, throne_x + 10, throne_y + 120], fill=(10, 8, 5))
    draw.rectangle([throne_x + 190, throne_y + 40, throne_x + 210, throne_y + 120], fill=(10, 8, 5))

    # Crown floating above throne
    crown_y = throne_y - 100
    draw.polygon([(cx - 50, crown_y + 30), (cx - 40, crown_y), (cx - 20, crown_y + 15),
                  (cx, crown_y - 10), (cx + 20, crown_y + 15), (cx + 40, crown_y),
                  (cx + 50, crown_y + 30)], fill=(200, 160, 40))
    draw.polygon([(cx - 50, crown_y + 30), (cx - 40, crown_y), (cx - 20, crown_y + 15),
                  (cx, crown_y - 10), (cx + 20, crown_y + 15), (cx + 40, crown_y),
                  (cx + 50, crown_y + 30)], fill=(255, 215, 60), outline=(255, 180, 20))

    # Ash particles
    for _ in range(80):
        ax = int(cx + (__import__("random").random() - 0.5) * width * 0.8)
        ay = int(cy - 100 + __import__("random").random() * height * 0.3)
        ar = int(__import__("random").random() * 3 + 1)
        ag = 180 + int(__import__("random").random() * 75)
        draw.ellipse([ax - ar, ay - ar, ax + ar, ay + ar], fill=(ag, ag - 40, ag - 80))


def draw_title_panel(draw: ImageDraw.ImageDraw, width: int, height: int, title: str, author: str) -> None:
    """Draw the bottom title panel with a semi-transparent background."""
    panel_top = 1920
    panel_bottom = 2560

    # Panel background
    draw.rectangle([0, panel_top, width, panel_bottom], fill=(20, 15, 12, 220))

    # Subtle line at top of panel
    draw.line([(100, panel_top + 5), (width - 100, panel_top + 5)], fill=(180, 140, 60), width=2)

    # Load fonts
    title_font = None
    for size in [72, 64, 56]:
        try:
            title_font = ImageFont.truetype(TITLE_FONT, size)
            break
        except OSError:
            continue
    if title_font is None:
        title_font = ImageFont.load_default()

    author_font = None
    try:
        author_font = ImageFont.truetype(AUTHOR_FONT, 36)
    except OSError:
        author_font = ImageFont.load_default()

    # Wrap title if needed
    wrapped = textwrap.fill(title, width=20)
    lines = wrapped.split("\n")

    title_y = panel_top + 60
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        tw = bbox[2] - bbox[0]
        tx = (width - tw) // 2
        # Shadow
        draw.text((tx + 2, title_y + 2), line, fill=(0, 0, 0), font=title_font)
        # Main text
        draw.text((tx, title_y), line, fill=(255, 215, 60), font=title_font)
        title_y += bbox[3] - bbox[1] + 10

    # Author name
    author_y = panel_top + 220
    try:
        author_bbox = draw.textbbox((0, 0), author, font=author_font)
        aw = author_bbox[2] - author_bbox[0]
    except AttributeError:
        aw = len(author) * 20
    draw.text(((width - aw) // 2 + 2, author_y + 2), author, fill=(0, 0, 0), font=author_font)
    draw.text(((width - aw) // 2, author_y), author, fill=(220, 220, 220), font=author_font)

    # Subtitle line
    subtitle = "Epic Fantasy"
    try:
        small_font = ImageFont.truetype(SMALL_FONT, 22)
    except OSError:
        small_font = ImageFont.load_default()
    try:
        s_bbox = draw.textbbox((0, 0), subtitle, font=small_font)
        sw = s_bbox[2] - s_bbox[0]
    except AttributeError:
        sw = len(subtitle) * 12
    draw.text(((width - sw) // 2, author_y + 50), subtitle, fill=(150, 150, 150), font=small_font)


def build_cover(title: str, author: str, output_path: Path) -> None:
    # Gradient background: dark red/black/orange for volcanic theme
    bg_colors = [
        hex_to_rgb("#0a0505"),  # near black
        hex_to_rgb("#1a0808"),  # very dark red
        hex_to_rgb("#2a0a05"),  # dark maroon
        hex_to_rgb("#3a0a00"),  # deep red
        hex_to_rgb("#1a0505"),  # back to dark
    ]
    img = create_gradient(WIDTH, HEIGHT, bg_colors)
    draw = ImageDraw.Draw(img)

    # Draw volcanic throne scene
    draw_throne(draw, WIDTH, HEIGHT)

    # Apply slight blur for atmosphere
    img = img.filter(ImageFilter.GaussianBlur(radius=2))

    # Redraw sharp elements on top
    draw = ImageDraw.Draw(img)
    draw_throne(draw, WIDTH, HEIGHT)

    # Title panel at bottom
    draw_title_panel(draw, WIDTH, HEIGHT, title, author)

    # Border
    draw.rectangle([10, 10, WIDTH - 10, HEIGHT - 10], outline=(180, 140, 60), width=3)

    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), _standard_cover_metadata_from_locals(locals()).get("model", ""))
    img.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=str, required=True)
    parser.add_argument("--out", type=str, required=True)
    args = parser.parse_args()

    with open(args.metadata, "r") as f:
        metadata = json.load(f)

    title = metadata.get("title", "The Ember Throne")
    author = metadata.get("author", "Barış Kısır")
    model = _standard_cover_metadata_from_locals(locals()).get("model", "")
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    build_cover(title, author, output_path)


if __name__ == "__main__":
    main()