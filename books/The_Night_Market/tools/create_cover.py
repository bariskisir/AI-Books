#!/usr/bin/env python3
"""Generate a 1600x2560 cover image for The Night Market."""

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



def wrap_text(draw, text, font, max_width):
    """Wrap text to fit within max_width."""
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test = current_line + " " + word if current_line else word
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line = test
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines


def create_cover(metadata_path, output_path):
    with open(metadata_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    model = meta.get("model", "")

    title = meta["title"]
    author = meta["author"]

    W, H = 1600, 2560

    img = Image.new("RGB", (W, H), (20, 10, 30))
    draw = ImageDraw.Draw(img)

    # Gradient background: deep purple to midnight blue to dark teal
    for y in range(H):
        r = int(20 + (y / H) * 15)
        g = int(5 + (y / H) * 20)
        b = int(40 + (y / H) * 30)
        for x in range(W):
            noise = random.randint(-3, 3)
            draw.point((x, y), fill=(r + noise, g + noise, b + noise))

    # Draw starry sky in upper portion
    random.seed(42)
    star_colors = [(255, 255, 200), (255, 200, 150), (200, 200, 255)]
    for _ in range(300):
        x = random.randint(0, W)
        y = random.randint(0, int(H * 0.5))
        size = random.choice([1, 1, 2, 2, 3])
        color = random.choice(star_colors)
        draw.ellipse([x, y, x + size, y + size], fill=color)
        if size > 1:
            draw.ellipse([x - 1, y - 1, x + size + 1, y + size + 1],
                         fill=(color[0], color[1], color[2], 60))

    # Draw moon
    moon_center = (W // 2, 180)
    moon_radius = 100
    draw.ellipse([
        moon_center[0] - moon_radius, moon_center[1] - moon_radius,
        moon_center[0] + moon_radius, moon_center[1] + moon_radius
    ], fill=(255, 240, 200))
    # Moon glow
    for r in range(moon_radius + 10, moon_radius + 50, 5):
        alpha = max(0, 60 - r)
        draw.ellipse([
            moon_center[0] - r, moon_center[1] - r,
            moon_center[0] + r, moon_center[1] + r
        ], fill=(255, 240, 200, alpha // 10))

    # Draw stall structures
    random.seed(123)
    stall_colors = [(80, 40, 30), (60, 50, 40), (70, 35, 25), (90, 55, 35)]
    for i in range(6):
        sx = 100 + i * 250 + random.randint(-30, 30)
        sy = int(H * 0.35)
        sw = 180 + random.randint(-20, 30)
        sh = 250 + random.randint(-30, 30)

        # Stall post
        post_color = random.choice(stall_colors)
        draw.rectangle([sx, sy, sx + 12, sy + sh], fill=post_color)
        draw.rectangle([sx + sw - 12, sy, sx + sw, sy + sh], fill=post_color)

        # Stall roof
        roof_color = (139, 69, 19)
        draw.polygon([
            (sx - 20, sy),
            (sx + sw + 20, sy),
            (sx + sw + 10, sy - 30),
            (sx - 10, sy - 30)
        ], fill=roof_color)

        # Stall counter
        counter_color = (101, 67, 33)
        draw.rectangle([sx + 12, sy + sh - 40, sx + sw - 12, sy + sh],
                       fill=counter_color)

        # Canopy
        canopy_color = (180, 50, 50) if i % 2 == 0 else (50, 80, 150)
        draw.rectangle([sx, sy + 20, sx + sw, sy + 50], fill=canopy_color)

    # Draw lanterns hanging from strings
    random.seed(456)
    lantern_colors = [(255, 200, 50), (255, 150, 50), (255, 100, 50),
                      (150, 200, 255), (200, 100, 200)]
    for x in range(100, W - 100, 40):
        lantern_y = int(H * 0.32) + random.randint(-10, 10)
        lantern_color = random.choice(lantern_colors)
        # String
        draw.line([x, int(H * 0.28), x, lantern_y], fill=(100, 80, 60), width=1)
        # Lantern body
        lw = 16
        lh = 24
        draw.ellipse([x - lw // 2, lantern_y - 5, x + lw // 2, lantern_y + lh - 5],
                     fill=lantern_color)
        # Glow
        glow_r = 30
        for g in range(glow_r, 0, -5):
            a = int(40 * (1 - g / glow_r))
            draw.ellipse([
                x - g, lantern_y - g,
                x + g, lantern_y + g
            ], fill=(lantern_color[0], lantern_color[1], lantern_color[2], a // 4))

    # Draw mysterious wares on counters
    random.seed(789)
    for i in range(8):
        wx = 140 + i * 200 + random.randint(-20, 20)
        wy = int(H * 0.62) + random.randint(-10, 10)
        # Jars
        jar_color = (100, 200, 255)
        draw.rectangle([wx - 10, wy - 30, wx + 10, wy], fill=(200, 220, 255, 100))
        draw.rectangle([wx - 10, wy - 30, wx + 10, wy], outline=jar_color, width=2)
        # Inner glow
        glow_h = random.randint(5, 20)
        glow_color = random.choice([(255, 200, 100), (200, 255, 200), (255, 150, 150)])
        draw.ellipse([wx - 5, wy - 10 - glow_h, wx + 5, wy - 10], fill=glow_color)

    # Ground/earth boundary
    ground_y = int(H * 0.7)
    for x in range(W):
        noise = random.randint(-3, 3)
        draw.point((x, ground_y + noise), fill=(40, 30, 20))

    # Title panel at bottom
    panel_y1 = int(H * 0.78)
    panel_y2 = H
    for y in range(panel_y1, panel_y2):
        alpha = (y - panel_y1) / (panel_y2 - panel_y1)
        r = int(15 * (1 - alpha) + 10 * alpha)
        g = int(10 * (1 - alpha) + 5 * alpha)
        b = int(25 * (1 - alpha) + 15 * alpha)
        for x in range(W):
            n = random.randint(-2, 2)
            draw.point((x, y), fill=(r + n, g + n, b + n))

    # Border line above panel
    draw.line([(30, panel_y1-3), (W-30, panel_y1-3)], fill=(180, 160, 100), width=2)

    # Load fonts
    font_dirs = [
        "C:/Windows/Fonts",
        "/System/Library/Fonts",
        "/usr/share/fonts/truetype",
    ]

    title_font = None
    author_font = None
    small_font = None

    for fd in font_dirs:
        p = Path(fd)
        if title_font is None:
            tf = p / "georgiab.ttf"
            if tf.exists():
                title_font = ImageFont.truetype(str(tf), 72)
            else:
                tf2 = p / "Georgia Bold.ttf"
                if tf2.exists():
                    title_font = ImageFont.truetype(str(tf2), 72)
        if author_font is None:
            af = p / "arialbd.ttf"
            if af.exists():
                author_font = ImageFont.truetype(str(af), 36)
            else:
                af2 = p / "Arial Bold.ttf"
                if af2.exists():
                    author_font = ImageFont.truetype(str(af2), 36)
        if small_font is None:
            sf = p / "arial.ttf"
            if sf.exists():
                small_font = ImageFont.truetype(str(sf), 20)
            else:
                sf2 = p / "Arial.ttf"
                if sf2.exists():
                    small_font = ImageFont.truetype(str(sf2), 20)

    if title_font is None:
        title_font = ImageFont.load_default()
    if author_font is None:
        author_font = ImageFont.load_default()
    if small_font is None:
        small_font = ImageFont.load_default()

    # Draw title text, wrapped
    max_text_width = W - 100
    title_lines = wrap_text(draw, title, title_font, max_text_width)
    title_y = panel_y1 + 80
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        tw = bbox[2] - bbox[0]
        tx = (W - tw) // 2
        # Title shadow
        draw.text((tx + 2, title_y + 2), line, fill=(0, 0, 0), font=title_font)
        draw.text((tx, title_y), line, fill=(255, 220, 150), font=title_font)
        title_y += bbox[3] - bbox[1] + 10

    # Draw author name
    author_y = panel_y2 - 120
    abox = draw.textbbox((0, 0), author, font=author_font)
    aw = abox[2] - abox[0]
    ax = (W - aw) // 2
    draw.text((ax + 2, author_y + 2), author, fill=(0, 0, 0), font=author_font)
    draw.text((ax, author_y), author, fill=(200, 200, 200), font=author_font)

    # Decorative line above author
    line_y = author_y - 20
    draw.line([(W//2 - 100, line_y), (W//2 + 100, line_y)], fill=(180, 160, 100), width=1)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    create_cover(args.metadata, args.out)


if __name__ == "__main__":
    main()