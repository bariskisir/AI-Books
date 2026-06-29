#!/usr/bin/env python3
"""Generate a book cover for The Glass Prison using PIL."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

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




def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    title = metadata["title"]
    author = metadata["author"]
    model = metadata.get("model", "")

    W, H = 1600, 2560
    img = Image.new("RGB", (W, H), "#1a1a2e")
    draw = ImageDraw.Draw(img)

    # Gradient background: dark steel gray to burnt orange
    for y in range(H):
        ratio = y / H
        r = int(26 + 180 * ratio)
        g = int(26 + 60 * ratio)
        b = int(46 + 20 * ratio)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    vanish_x, vanish_y = W // 2, H // 3

    # Floor perspective polygons
    for i in range(8):
        x1 = int(W * (0.1 + 0.1 * i))
        x2 = int(W * (0.1 + 0.1 * (i + 1)))
        gray = int(60 + 20 * i)
        draw.polygon(
            [(vanish_x, vanish_y), (x1, H), (x2, H)],
            fill=(gray, gray, gray + 10),
        )

    # Glass wall vertical struts - perspective lines
    strut_color = (200, 200, 210)
    for i in range(10):
        x = int(W * (0.05 + 0.1 * i))
        # Top section
        top_x2 = vanish_x + (x - vanish_x) * 2 // 3
        draw.line(
            [(x, 0), (top_x2, vanish_y)],
            fill=strut_color,
            width=3,
        )
        # Bottom section
        if x > vanish_x:
            bot_x1 = vanish_x + (x - vanish_x) * 2 // 3
            draw.line(
                [(bot_x1, vanish_y), (x, H)],
                fill=strut_color,
                width=3,
            )
        else:
            bot_x2 = vanish_x - (vanish_x - x) * 2 // 3
            draw.line(
                [(x, vanish_y), (bot_x2, H)],
                fill=strut_color,
                width=3,
            )

    # Horizontal glass panel lines
    for i in range(6):
        y_pos = int(H * 0.05 + i * 100)
        draw.line(
            [(int(W * 0.15), y_pos), (int(W * 0.85), y_pos)],
            fill=(180, 180, 200),
            width=2,
        )

    # Watchtower silhouette (right side)
    tower_x = W - 250
    tower_base_y = int(H * 0.5)
    # Tower body
    draw.rectangle(
        [tower_x, tower_base_y - 300, tower_x + 80, tower_base_y],
        fill=(30, 30, 40),
        outline=(100, 100, 110),
        width=2,
    )
    # Tower top
    draw.rectangle(
        [tower_x - 20, tower_base_y - 320, tower_x + 100, tower_base_y - 300],
        fill=(40, 40, 50),
        outline=(120, 120, 130),
        width=2,
    )
    # Tower light (glow)
    draw.ellipse(
        [tower_x + 15, tower_base_y - 290, tower_x + 65, tower_base_y - 270],
        fill=(255, 200, 50),
    )
    draw.ellipse(
        [tower_x + 20, tower_base_y - 285, tower_x + 60, tower_base_y - 275],
        fill=(255, 255, 200),
    )

    # Light beam from tower
    beam_points = [
        (tower_x + 40, tower_base_y - 280),
        (tower_x + 400, tower_base_y - 420),
        (tower_x + 200, tower_base_y - 50),
    ]
    draw.polygon(beam_points, fill=(80, 60, 20))

    # Floor grid lines
    for y in range(int(H * 0.5), H, 60):
        draw.line(
            [(0, y), (W, y)],
            fill=(100, 100, 110),
            width=1,
        )

    # Title panel at bottom
    panel_top = 1920
    draw.rectangle(
        [(0, panel_top), (W, H)],
        fill=(20, 20, 30),
    )

    # Accent line at top of panel
    draw.line(
        [(0, panel_top), (W, panel_top)],
        fill=(230, 120, 30),
        width=4,
    )

    # Load fonts
    title_font = ImageFont.truetype("arialbd.ttf", 72)
    author_font = ImageFont.truetype("arial.ttf", 36)

    # Title text
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_w = title_bbox[2] - title_bbox[0]
    title_x = (W - title_w) // 2
    title_y = panel_top + 100
    draw.text((title_x, title_y), title, font=title_font, fill=(255, 255, 255))

    # Author text
    author_bbox = draw.textbbox((0, 0), author, font=author_font)
    author_w = author_bbox[2] - author_bbox[0]
    author_x = (W - author_w) // 2
    author_y = title_y + 100
    draw.text((author_x, author_y), author, font=author_font, fill=(220, 220, 220))

    # Save
    args.out.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.save(args.out, "PNG")
    print(f"Cover saved to {args.out}")


if __name__ == "__main__":
    main()