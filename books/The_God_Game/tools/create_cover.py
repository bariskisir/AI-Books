#!/usr/bin/env python3
"""Cover: The God Game — Cracked clay amphora on stone shelf in dark Vatican sub-basement, shaft of light, terra cotta/stone gray/sacred gold."""

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



WIDTH, HEIGHT = 1600, 2560
PANEL_TOP = 1920
FONTS_DIR = Path("C:/Windows/Fonts")


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def make_gradient(draw: ImageDraw, width: int, height: int) -> None:
    """Vertical gradient: deep crimson (top) to very dark red (mid) to near-black (bottom)."""
    colors = [
        (30, 5, 8),     # near-black
        (60, 10, 15),   # very dark red
        (90, 15, 20),   # dark maroon
        (140, 25, 35),  # deep crimson
        (180, 40, 50),  # rich red
        (140, 25, 35),  # deep crimson
        (80, 12, 18),   # dark maroon
        (40, 6, 10),    # very dark
        (20, 3, 5),     # near-black
    ]
    band_height = height // len(colors)
    for i, (r, g, b) in enumerate(colors):
        for y in range(i * band_height, (i + 1) * band_height if i < len(colors) - 1 else height):
            draw.line([(0, y), (width, y)], fill=(r, g, b))


def draw_arches(draw: ImageDraw, width: int, height: int) -> None:
    """Draw arched library windows / alcoves suggesting the Vatican library."""
    arch_color = (60, 50, 40, 40)
    for i in range(4):
        cx = width // 5 * (i + 1)
        top_y = height // 6
        arch_width = 180
        arch_height = 300
        left = cx - arch_width // 2
        right = cx + arch_width // 2
        # Arch top (semicircle)
        draw.arc([left, top_y, right, top_y + arch_width], 0, 180, fill=(80, 65, 55, 40), width=3)
        # Pillars
        draw.line([left, top_y + arch_width // 2, left, top_y + arch_width // 2 + arch_height], fill=(70, 55, 45), width=4)
        draw.line([right, top_y + arch_width // 2, right, top_y + arch_width // 2 + arch_height], fill=(70, 55, 45), width=4)
        # Faint glow inside arch
        glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow)
        gdraw.ellipse([left + 10, top_y + 20, right - 10, top_y + arch_width - 10], fill=(200, 160, 80, 15))
        draw.bitmap((0, 0), glow, fill=None)


def draw_scroll(draw: ImageDraw, width: int, height: int) -> None:
    """Draw an ancient scroll in the center of the image."""
    cx = width // 2
    cy = height // 2 - 100
    scroll_width = 500
    scroll_height = 200
    left = cx - scroll_width // 2
    right = cx + scroll_width // 2
    top = cy - scroll_height // 2
    bottom = cy + scroll_height // 2

    # Scroll body
    draw.rectangle([left, top, right, bottom], fill=(180, 160, 120, 60), outline=(200, 180, 140, 80))
    # Rolled top edge
    draw.ellipse([left - 10, top - 15, left + 20, top + 15], fill=(160, 140, 100, 80))
    draw.ellipse([right - 20, top - 15, right + 10, top + 15], fill=(160, 140, 100, 80))
    # Rolled bottom edge
    draw.ellipse([left - 10, bottom - 15, left + 20, bottom + 15], fill=(160, 140, 100, 80))
    draw.ellipse([right - 20, bottom - 15, right + 10, bottom + 15], fill=(160, 140, 100, 80))
    # Script lines
    script_y = top + 30
    while script_y < bottom - 20:
        draw.line([left + 25, script_y, right - 25, script_y], fill=(100, 85, 60, 40), width=2)
        script_y += 18


def draw_candlelight(draw: ImageDraw, width: int, height: int) -> None:
    """Draw candle glow effects at the bottom and sides."""
    # Bottom candle glow
    for radius in range(200, 50, -10):
        alpha = max(0, 30 - (200 - radius) // 7)
        if alpha <= 0:
            continue
        draw.ellipse(
            [width // 2 - radius, height - radius * 2, width // 2 + radius, height + radius],
            fill=(220, 180, 80, alpha),
        )
    # Small candle flame near bottom-left
    candle_x, candle_y = 250, HEIGHT - 300
    draw.ellipse([candle_x - 8, candle_y - 20, candle_x + 8, candle_y], fill=(255, 220, 100, 180))
    draw.ellipse([candle_x - 5, candle_y - 35, candle_x + 5, candle_y - 20], fill=(255, 200, 80, 160))
    # Candle body
    draw.rectangle([candle_x - 6, candle_y, candle_x + 6, candle_y + 80], fill=(220, 200, 170, 200))
    # Light pool from candle
    for r in range(150, 10, -10):
        a = max(0, 12 - (150 - r) // 15)
        if a <= 0:
            continue
        draw.ellipse(
            [candle_x - r, candle_y - r * 2, candle_x + r, candle_y + r],
            fill=(255, 200, 100, a),
        )
    # Second candle right side
    candle2_x, candle2_y = WIDTH - 250, HEIGHT - 400
    draw.ellipse([candle2_x - 8, candle2_y - 20, candle2_x + 8, candle2_y], fill=(255, 220, 100, 180))
    draw.ellipse([candle2_x - 5, candle2_y - 35, candle2_x + 5, candle2_y - 20], fill=(255, 200, 80, 160))
    draw.rectangle([candle2_x - 6, candle2_y, candle2_x + 6, candle2_y + 80], fill=(220, 200, 170, 200))
    for r in range(120, 10, -10):
        a = max(0, 10 - (120 - r) // 15)
        if a <= 0:
            continue
        draw.ellipse(
            [candle2_x - r, candle2_y - r * 2, candle2_x + r, candle2_y + r],
            fill=(255, 200, 100, a),
        )


def draw_title_panel(img: Image, draw: ImageDraw, title: str, author: str) -> None:
    """Draw the bottom title panel with light rectangle."""
    # Light rectangle panel
    draw.rectangle([0, PANEL_TOP, WIDTH, HEIGHT], fill=(240, 230, 215, 220))
    # Top border line
    draw.line([0, PANEL_TOP, WIDTH, PANEL_TOP], fill=(180, 160, 130, 200), width=3)

    try:
        title_font = ImageFont.truetype(str(FONTS_DIR / "georgiab.ttf"), 72)
        title_small = ImageFont.truetype(str(FONTS_DIR / "georgiab.ttf"), 56)
        author_font = ImageFont.truetype(str(FONTS_DIR / "arialbd.ttf"), 40)
        small_font = ImageFont.truetype(str(FONTS_DIR / "arial.ttf"), 28)
    except (IOError, OSError):
        try:
            title_font = ImageFont.truetype(str(FONTS_DIR / "georgia.ttf"), 72)
            title_small = ImageFont.truetype(str(FONTS_DIR / "georgia.ttf"), 56)
            author_font = ImageFont.truetype(str(FONTS_DIR / "arialbd.ttf"), 40)
            small_font = ImageFont.truetype(str(FONTS_DIR / "arial.ttf"), 28)
        except (IOError, OSError):
            title_font = ImageFont.load_default()
            title_small = ImageFont.load_default()
            author_font = ImageFont.load_default()
            small_font = ImageFont.load_default()

    y = PANEL_TOP + 40
    genre_line = "A Religious Thriller"
    try:
        bbox = small_font.getbbox(genre_line)
        tw = bbox[2] - bbox[0] if bbox else small_font.getlength(genre_line)
        draw.text(((WIDTH - tw) / 2, y), genre_line, fill=(120, 100, 80), font=small_font)
    except AttributeError:
        draw.text((WIDTH // 2, y), genre_line, fill=(120, 100, 80), font=small_font, anchor="mt")

    y += 50

    # Title - wrap if too long
    title_text = title.upper()
    try:
        bbox = title_font.getbbox(title_text)
        tw = bbox[2] - bbox[0] if bbox else title_font.getlength(title_text)
    except AttributeError:
        tw = 0

    if tw > WIDTH - 100:
        # Split title into words and wrap
        words = title_text.split()
        line1 = ""
        line2 = ""
        half = len(words) // 2
        line1 = " ".join(words[:half])
        line2 = " ".join(words[half:])
        try:
            bbox = title_small.getbbox(line1)
            tw1 = bbox[2] - bbox[0] if bbox else title_small.getlength(line1)
            draw.text(((WIDTH - tw1) / 2, y), line1, fill=(40, 20, 15), font=title_small)
        except AttributeError:
            draw.text((WIDTH // 2, y), line1, fill=(40, 20, 15), font=title_small, anchor="mt")
        y += title_small.size + 10 if hasattr(title_small, 'size') else 66
        try:
            bbox = title_small.getbbox(line2)
            tw2 = bbox[2] - bbox[0] if bbox else title_small.getlength(line2)
            draw.text(((WIDTH - tw2) / 2, y), line2, fill=(40, 20, 15), font=title_small)
        except AttributeError:
            draw.text((WIDTH // 2, y), line2, fill=(40, 20, 15), font=title_small, anchor="mt")
    else:
        try:
            bbox = title_font.getbbox(title_text)
            tw = bbox[2] - bbox[0] if bbox else title_font.getlength(title_text)
            draw.text(((WIDTH - tw) / 2, y), title_text, fill=(40, 20, 15), font=title_font)
        except AttributeError:
            draw.text((WIDTH // 2, y), title_text, fill=(40, 20, 15), font=title_font, anchor="mt")

    if hasattr(title_font, 'size'):
        y += title_font.size + 30
    else:
        y += 102

    # Author
    author_text = f"by {author}"
    try:
        bbox = author_font.getbbox(author_text)
        tw = bbox[2] - bbox[0] if bbox else author_font.getlength(author_text)
        draw.text(((WIDTH - tw) / 2, y), author_text, fill=(80, 60, 50), font=author_font)
    except AttributeError:
        draw.text((WIDTH // 2, y), author_text, fill=(80, 60, 50), font=author_font, anchor="mt")


def create_cover(title: str, author: str, output_path: Path) -> None:
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Dark basement background — stone gray/black
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(20 + 15 * t)
        g = int(18 + 12 * t)
        b = int(15 + 10 * t)
        draw.line((0, y, WIDTH, y), fill=(min(255, r), min(255, g), min(255, b), 255))

    # Stone walls — rough texture
    for x in range(0, WIDTH, 60):
        r = random.randint(5, 10)
        draw.rectangle((x, 0, x + r, HEIGHT), fill=(30, 28, 25, 100))
    for y in range(0, HEIGHT, 60):
        r = random.randint(5, 10)
        draw.rectangle((0, y, WIDTH, y + r), fill=(30, 28, 25, 80))

    # Archway behind — Vatican sub-basement
    draw.arc((200, 200, WIDTH - 200, 800), 0, 180, fill=(50, 45, 40, 150), width=15)
    draw.rectangle((200, 500, 215, 1800), fill=(40, 38, 35, 150))
    draw.rectangle((WIDTH - 215, 500, WIDTH - 200, 1800), fill=(40, 38, 35, 150))

    # Stone shelf
    draw.rectangle((200, 1100, WIDTH - 200, 1140), fill=(55, 50, 45, 200))
    draw.rectangle((190, 1140, WIDTH - 190, 1155), fill=(45, 42, 38, 200))

    # Cracked clay amphora on shelf
    amph_cx, amph_by = WIDTH // 2, 1100
    amph_h = 250
    amph_w = 140
    # Body
    draw.ellipse((amph_cx - amph_w, amph_by - amph_h, amph_cx + amph_w, amph_by + 20), fill=(150, 90, 50, 220))
    # Neck
    draw.rectangle((amph_cx - 30, amph_by - amph_h - 60, amph_cx + 30, amph_by - amph_h), fill=(140, 85, 45, 220))
    # Rim
    draw.ellipse((amph_cx - 35, amph_by - amph_h - 70, amph_cx + 35, amph_by - amph_h - 50), fill=(160, 100, 55, 220))
    # Handles
    draw.arc((amph_cx - amph_w - 15, amph_by - amph_h + 50, amph_cx - amph_w + 15, amph_by - amph_h + 130), 0, 180, fill=(140, 85, 45, 200), width=8)
    draw.arc((amph_cx + amph_w - 15, amph_by - amph_h + 50, amph_cx + amph_w + 15, amph_by - amph_h + 130), 0, 180, fill=(140, 85, 45, 200), width=8)
    # Crack
    draw.line((amph_cx - 30, amph_by - 80, amph_cx + 20, amph_by - 120), fill=(80, 45, 20, 180), width=3)
    draw.line((amph_cx + 20, amph_by - 120, amph_cx + 40, amph_by - 160), fill=(80, 45, 20, 180), width=2)

    # Shaft of light from above — sacred gold
    light = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    ld = ImageDraw.Draw(light)
    ld.polygon([(amph_cx - 80, 0), (amph_cx + 80, 0), (amph_cx + 200, amph_by), (amph_cx - 200, amph_by)], fill=(200, 180, 100, 20))
    ld.polygon([(amph_cx - 40, 0), (amph_cx + 40, 0), (amph_cx + 100, amph_by), (amph_cx - 100, amph_by)], fill=(220, 200, 120, 15))
    light = light.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, light)

    # Gold glow on amphora from light shaft
    for gr in range(60, 5, -5):
        alpha = max(0, 30 - (60 - gr) // 2)
        draw.ellipse((amph_cx - gr, amph_by - amph_h - gr, amph_cx + gr, amph_by + gr), fill=(200, 180, 80, alpha))

    # Dust motes in light shaft
    for _ in range(60):
        dx = amph_cx + random.randint(-150, 150)
        dy = random.randint(50, amph_by)
        ds = random.randint(1, 3)
        draw.ellipse((dx, dy, dx + ds, dy + ds), fill=(200, 190, 160, random.randint(20, 80)))

    # Vignette
    vignette = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(vignette)
    for r in range(max(WIDTH, HEIGHT) // 2, 0, -10):
        alpha = max(0, 80 - (max(WIDTH, HEIGHT) // 2 - r) // 5)
        if alpha <= 0:
            continue
        vdraw.ellipse([WIDTH // 2 - r, HEIGHT // 2 - r, WIDTH // 2 + r, HEIGHT // 2 + r], fill=(0, 0, 0, alpha))
    img = Image.alpha_composite(img, vignette)

    rgb = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
    rgb.paste(img, (0, 0), img)
    draw = ImageDraw.Draw(rgb)

    draw_title_panel(rgb, draw, title, author)

    # Subtle noise filter for texture
    _draw_standard_cover_title_panel(rgb, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), _standard_cover_metadata_from_locals(locals()).get("model", ""))
    rgb.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    title = metadata.get("title", "The God Game")
    author = metadata.get("author", "Barış Kısır")
    model = _standard_cover_metadata_from_locals(locals()).get("model", "")
    output_path = args.out.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    create_cover(title, author, output_path)


if __name__ == "__main__":
    main()