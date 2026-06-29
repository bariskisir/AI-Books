#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Gaslight Grimoire."""

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



def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw) -> list[str]:
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = current + " " + word if current else word
        bbox = draw.textbbox((0, 0), test, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            current = test
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    with open(args.metadata, encoding="utf-8") as f:
        metadata = json.load(f)

    title = metadata.get("title", "The Gaslight Grimoire")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    W, H = 1600, 2560
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Gradient background: dark to amber-tinged
    for y in range(H):
        ratio = y / H
        r = int(10 + ratio * 55)
        g = int(10 + ratio * 40)
        b = int(15 + ratio * 20)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

    # Fog layer
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fog_draw = ImageDraw.Draw(fog)
    fog_draw.ellipse([-200, 800, 600, 1800], fill=(60, 55, 40, 40))
    fog_draw.ellipse([400, 700, 1100, 1700], fill=(50, 48, 35, 35))
    fog_draw.ellipse([800, 900, 1600, 1900], fill=(65, 60, 45, 30))
    fog_draw.ellipse([300, 1400, 1300, 2400], fill=(45, 42, 30, 50))
    img = Image.alpha_composite(img, fog)

    # Victorian street silhouette (buildings on sides)
    buildings = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    b_draw = ImageDraw.Draw(buildings)
    # Left building cluster
    b_draw.polygon([(0, 600), (0, 1800), (120, 1800), (140, 1400), (160, 1800), (320, 1800), (300, 1200), (260, 900), (240, 700), (180, 600)], fill=(15, 12, 8, 220))
    # Right building cluster
    b_draw.polygon([(1280, 1800), (1500, 1800), (1480, 1300), (1460, 1100), (1400, 800), (1350, 750), (1300, 700), (1260, 650)], fill=(12, 10, 6, 220))
    b_draw.polygon([(1400, 1800), (1600, 1800), (1600, 900), (1550, 850), (1500, 800), (1450, 780)], fill=(18, 14, 8, 220))
    # Roof details
    b_draw.polygon([(180, 600), (240, 700), (200, 650), (150, 580)], fill=(8, 6, 3, 200))
    b_draw.polygon([(1300, 700), (1350, 750), (1320, 710), (1280, 680)], fill=(8, 6, 3, 200))
    # Windows (dim yellow rectangles)
    for wx, wy in [(80, 800), (80, 880), (80, 960), (100, 1050), (100, 1130), (240, 950), (240, 1030)]:
        b_draw.rectangle([wx, wy, wx + 25, wy + 35], fill=(40, 35, 10, 180))
    for wx, wy in [(1350, 900), (1350, 980), (1450, 1000), (1450, 1080), (1520, 950), (1520, 1030)]:
        b_draw.rectangle([wx, wy, wx + 20, wy + 30], fill=(40, 35, 10, 180))
    img = Image.alpha_composite(img, buildings)

    # Gaslamp post on the left
    lamp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    l_draw = ImageDraw.Draw(lamp)
    # Post
    l_draw.rectangle([440, 1100, 455, 1700], fill=(20, 18, 15, 240))
    # Crossbar
    l_draw.rectangle([410, 1100, 485, 1115], fill=(20, 18, 15, 240))
    # Lamp housing
    l_draw.polygon([(415, 1020), (420, 1100), (475, 1100), (480, 1020)], fill=(25, 22, 15, 240))
    # Glass glow
    glow_radius = 180
    for gr in range(glow_radius, 0, -8):
        alpha = max(0, 30 - (glow_radius - gr) // 6)
        l_draw.ellipse([448 - gr, 1000 - gr, 448 + gr, 1000 + gr], fill=(220, 180, 60, alpha))
    # Bright center
    l_draw.ellipse([435, 985, 462, 1015], fill=(255, 230, 150, 255))
    l_draw.ellipse([438, 990, 459, 1010], fill=(255, 255, 220, 200))
    img = Image.alpha_composite(img, lamp)

    # Magic sparkles/particles around the lamp
    particles = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    p_draw = ImageDraw.Draw(particles)
    sparkle_positions = [(420, 960), (470, 930), (490, 1000), (410, 1050), (440, 900), (510, 980), (400, 990)]
    for sx, sy in sparkle_positions:
        p_draw.ellipse([sx - 4, sy - 4, sx + 4, sy + 4], fill=(255, 220, 100, 200))
        p_draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 255, 200, 255))
    img = Image.alpha_composite(img, particles)

    # Cobblestone street at bottom
    street = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(street)
    s_draw.rectangle([0, 1750, W, 1920], fill=(25, 22, 18, 240))
    for cx in range(50, W, 80):
        cy = 1800
        s_draw.ellipse([cx - 20, cy - 10, cx + 20, cy + 10], fill=(35, 30, 25, 150))
        s_draw.ellipse([cx - 40, cy + 30, cx, cy + 50], fill=(30, 26, 22, 130))
        s_draw.ellipse([cx + 20, cy + 40, cx + 60, cy + 60], fill=(32, 28, 24, 130))
    img = Image.alpha_composite(img, street)

    # Title panel - lighter rectangle at bottom
    panel = Image.new("RGBA", (W, 640), (0, 0, 0, 0))
    p_draw = ImageDraw.Draw(panel)
    panel_bg = Image.new("RGBA", (W, 640), (30, 28, 25, 230))
    panel = Image.alpha_composite(panel, panel_bg)
    # Decorative border line
    p_draw.line([(100, 10), (W - 100, 10)], fill=(180, 150, 80, 200), width=3)
    p_draw.line([(100, 629), (W - 100, 629)], fill=(180, 150, 80, 200), width=3)
    img.paste(panel, (0, 1920))

    # Fonts
    try:
        title_font = ImageFont.truetype("C:/Windows/Fonts/georgiab.ttf", 72)
        author_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 42)
    except (IOError, OSError):
        title_font = ImageFont.load_default()
        author_font = ImageFont.load_default()

    # Title text - wrapped if needed
    title_lines = wrap_text(title, title_font, W - 200, draw)
    title_y = 1980
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        tw = bbox[2] - bbox[0]
        tx = (W - tw) // 2
        draw.text((tx, title_y), line, fill=(220, 210, 190, 255), font=title_font)
        title_y += 80

    # Author
    author_y = max(2220, title_y + 20)
    bbox_a = draw.textbbox((0, 0), author, font=author_font)
    aw = bbox_a[2] - bbox_a[0]
    draw.text(((W - aw) // 2, author_y), author, fill=(180, 170, 150, 255), font=author_font)

    # Apply subtle blur to the upper portion for atmosphere
    upper = img.crop((0, 0, W, 1800))
    upper = upper.filter(ImageFilter.GaussianBlur(radius=1))
    img.paste(upper, (0, 0))

    # Save
    args.out.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.save(args.out, "PNG")
    print(f"Cover saved to {args.out}")


if __name__ == "__main__":
    main()