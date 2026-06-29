#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Garden of Unearthly Delights."""

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



FONT_DIR = Path("C:/Windows/Fonts")
WIDTH, HEIGHT = 1600, 2560
TITLE_PANEL_TOP = 1920


def wrap_text(draw, text, font, max_width):
    """Wrap text to fit within max_width pixels. Returns list of lines."""
    words = text.split()
    if not words:
        return [""]
    lines = []
    current = ""
    for word in words:
        test = current + (" " if current else "") + word
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_gradient(draw, width, height, colors):
    """Draw a vertical gradient from top to bottom through the given colors."""
    n_colors = len(colors)
    for y in range(height):
        ratio = y / max(height - 1, 1)
        color_idx = ratio * (n_colors - 1)
        idx_a = int(color_idx)
        idx_b = min(idx_a + 1, n_colors - 1)
        frac = color_idx - idx_a
        r = int(colors[idx_a][0] * (1 - frac) + colors[idx_b][0] * frac)
        g = int(colors[idx_a][1] * (1 - frac) + colors[idx_b][1] * frac)
        b = int(colors[idx_a][2] * (1 - frac) + colors[idx_b][2] * frac)
        draw.line([(0, y), (width, y)], fill=(r, g, b))


def add_noise(draw, width, height, intensity=20):
    """Add subtle noise for texture."""
    for _ in range(2000):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        c = random.randint(-intensity, intensity)
        px = draw.im.getpixel((x, y))
        if px and len(px) >= 3:
            r = max(0, min(255, px[0] + c))
            g = max(0, min(255, px[1] + c))
            b = max(0, min(255, px[2] + c))
            draw.point((x, y), fill=(r, g, b))


def draw_glowing_flowers(draw, width, height, seed=42):
    """Draw bioluminescent glowing flowers in the upper 75% of the cover."""
    random.seed(seed)
    for _ in range(30):
        cx = random.randint(100, width - 100)
        cy = random.randint(100, int(height * 0.72))
        radius = random.randint(15, 45)
        glow_radius = radius * 3

        # Glow halo
        for i in range(glow_radius, 0, -1):
            alpha = int(30 * (1 - i / glow_radius))
            color_choice = random.choice([
                (100, 255, 150, alpha),   # green
                (150, 255, 255, alpha),   # cyan
                (200, 100, 255, alpha),   # purple
                (255, 200, 100, alpha),   # gold
            ])
            glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            glow_draw = ImageDraw.Draw(glow)
            glow_draw.ellipse(
                [cx - i, cy - i, cx + i, cy + i],
                fill=color_choice,
            )
            draw._image.paste(glow, (0, 0), glow)

        # Flower petals
        n_petals = random.randint(5, 8)
        for p in range(n_petals):
            angle = 2 * math.pi * p / n_petals + random.uniform(0, 0.3)
            petal_len = radius * random.uniform(0.6, 1.0)
            px = cx + int(math.cos(angle) * petal_len)
            py = cy + int(math.sin(angle) * petal_len)
            petal_color = random.choice([
                (60, 220, 120),    # bright green
                (100, 200, 255),   # sky blue
                (180, 80, 255),    # violet
                (255, 180, 60),    # warm gold
            ])
            draw.ellipse(
                [px - 8, py - 8, px + 8, py + 8],
                fill=petal_color,
            )
        # Center
        draw.ellipse(
            [cx - 6, cy - 6, cx + 6, cy + 6],
            fill=(255, 255, 200),
        )


def draw_dna_helix(draw, width, height):
    """Draw a stylized DNA helix on the right side."""
    center_x = width - 200
    start_y = 300
    end_y = 1500
    n_steps = 80
    amplitude = 60
    color_a = (100, 255, 180)
    color_b = (180, 100, 255)

    for i in range(n_steps):
        t = i / n_steps
        y = start_y + (end_y - start_y) * t
        angle = t * 6 * math.pi

        x1 = center_x + int(math.sin(angle) * amplitude)
        x2 = center_x + int(math.sin(angle + math.pi) * amplitude)

        # Strand dots
        draw.ellipse([x1 - 4, y - 4, x1 + 4, y + 4], fill=color_a)
        draw.ellipse([x2 - 4, y - 4, x2 + 4, y + 4], fill=color_b)

        # Rungs
        if i % 3 == 0:
            rung_color = (200, 255, 220)
            draw.line([(x1, y), (x2, y)], fill=rung_color, width=2)


def draw_iridescence(draw, width, height):
    """Add iridescent sparkle dots scattered in the upper area."""
    random.seed(123)
    for _ in range(150):
        x = random.randint(50, width - 50)
        y = random.randint(50, int(height * 0.7))
        size = random.randint(2, 6)
        colors = [
            (255, 180, 180, 180),
            (180, 255, 180, 180),
            (180, 180, 255, 180),
            (255, 255, 180, 180),
            (180, 255, 255, 180),
        ]
        c = random.choice(colors)
        sparkle = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        sparkle_draw = ImageDraw.Draw(sparkle)
        sparkle_draw.ellipse(
            [x - size, y - size, x + size, y + size],
            fill=c,
        )
        draw._image.paste(sparkle, (0, 0), sparkle)


def draw_light_particles(draw, width, height):
    """Draw floating light motes."""
    random.seed(77)
    for _ in range(80):
        x = random.randint(20, width - 20)
        y = random.randint(20, int(height * 0.65))
        r = random.randint(1, 4)
        alpha_val = random.randint(60, 180)
        color = (255, 255, 220, alpha_val)
        mote = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        mote_draw = ImageDraw.Draw(mote)
        mote_draw.ellipse([x - r, y - r, x + r, y + r], fill=color)
        draw._image.paste(mote, (0, 0), mote)


def create_cover(metadata_path, output_path):
    with open(metadata_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    model = meta.get("model", "")

    title = meta["title"]
    author = meta.get("author", "Barış Kısır")

    # Base image with RGBA for compositing
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Gradient background: deep teal -> dark blue -> dark purple
    draw_gradient(
        draw, WIDTH, HEIGHT,
        [(10, 20, 40), (20, 60, 80), (40, 10, 70), (15, 5, 35)]
    )

    # Add texture noise
    add_noise(draw, WIDTH, HEIGHT, 15)

    # Bioluminescent flowers
    draw_glowing_flowers(draw, WIDTH, HEIGHT)

    # DNA helix
    draw_dna_helix(draw, WIDTH, HEIGHT)

    # Iridescent sparkles
    draw_iridescence(draw, WIDTH, HEIGHT)

    # Light particles
    draw_light_particles(draw, WIDTH, HEIGHT)

    # Apply slight blur for atmospheric effect
    img = img.filter(ImageFilter.GaussianBlur(radius=2))
    draw = ImageDraw.Draw(img)

    # Title panel at bottom
    draw.rectangle(
        [(0, TITLE_PANEL_TOP), (WIDTH - 1, HEIGHT - 1)],
        fill=(240, 235, 225, 230),
    )
    # Thin border at top of panel
    draw.line(
        [(0, TITLE_PANEL_TOP), (WIDTH - 1, TITLE_PANEL_TOP)],
        fill=(180, 170, 150), width=3,
    )

    # Load fonts
    title_font_size = 72
    author_font_size = 36
    genre_font_size = 24

    try:
        title_font = ImageFont.truetype(str(FONT_DIR / "georgiab.ttf"), title_font_size)
    except (IOError, OSError):
        try:
            title_font = ImageFont.truetype(str(FONT_DIR / "georgia.ttf"), title_font_size)
        except (IOError, OSError):
            title_font = ImageFont.load_default()
    try:
        author_font = ImageFont.truetype(str(FONT_DIR / "arialbd.ttf"), author_font_size)
    except (IOError, OSError):
        author_font = ImageFont.load_default()
    try:
        genre_font = ImageFont.truetype(str(FONT_DIR / "arial.ttf"), genre_font_size)
    except (IOError, OSError):
        genre_font = ImageFont.load_default()

    # Draw title (wrapped)
    max_text_width = WIDTH - 160
    title_lines = wrap_text(draw, title, title_font, max_text_width)
    title_y = TITLE_PANEL_TOP + 60
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        line_w = bbox[2] - bbox[0]
        x = (WIDTH - line_w) // 2
        # Shadow
        draw.text((x + 2, title_y + 2), line, font=title_font, fill=(100, 95, 85))
        # Main text
        draw.text((x, title_y), line, font=title_font, fill=(30, 25, 20))
        title_y += bbox[3] - bbox[1] + 10

    # Author name
    author_y = title_y + 40
    bbox_a = draw.textbbox((0, 0), author, font=author_font)
    a_w = bbox_a[2] - bbox_a[0]
    draw.text(
        ((WIDTH - a_w) // 2 + 1, author_y + 1),
        author,
        font=author_font,
        fill=(140, 135, 125),
    )
    draw.text(
        ((WIDTH - a_w) // 2, author_y),
        author,
        font=author_font,
        fill=(50, 45, 40),
    )

    # Genre label below author
    genre_label = meta.get("genre", "Biopunk")
    bbox_g = draw.textbbox((0, 0), genre_label, font=genre_font)
    g_w = bbox_g[2] - bbox_g[0]
    draw.text(
        ((WIDTH - g_w) // 2, author_y + 50),
        genre_label,
        font=genre_font,
        fill=(130, 120, 110),
    )

    # Convert to RGB for saving as PNG
    final = img.convert("RGB")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(final, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    final.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    create_cover(args.metadata, args.out)


if __name__ == "__main__":
    main()