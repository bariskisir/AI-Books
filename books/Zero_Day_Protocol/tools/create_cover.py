#!/usr/bin/env python3
"""Cover: Zero Day Protocol — Neon green terminal screen with \"00:00:00\" countdown, darkened city silhouette, ghost icon above."""

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
PANEL_Y = 1920

COLORS = {
    "bg_top": (5, 20, 5),
    "bg_mid": (10, 35, 10),
    "bg_bot": (0, 5, 0),
    "accent_green": (0, 180, 60),
    "accent_red": (220, 30, 30),
    "accent_dark_red": (140, 10, 10),
    "circuit_line": (0, 200, 80),
    "circuit_node": (0, 220, 100),
    "circuit_dim": (0, 100, 40),
    "warning_text": (255, 50, 50),
    "panel_bg": (240, 240, 248),
    "title_text": (5, 20, 5),
    "author_text": (60, 60, 80),
}


def make_gradient(draw: ImageDraw.ImageDraw) -> None:
    for y in range(PANEL_Y):
        t = y / PANEL_Y
        if t < 0.5:
            t2 = t * 2
            r = int(COLORS["bg_top"][0] + (COLORS["bg_mid"][0] - COLORS["bg_top"][0]) * t2)
            g = int(COLORS["bg_top"][1] + (COLORS["bg_mid"][1] - COLORS["bg_top"][1]) * t2)
            b = int(COLORS["bg_top"][2] + (COLORS["bg_mid"][2] - COLORS["bg_top"][2]) * t2)
        else:
            t2 = (t - 0.5) * 2
            r = int(COLORS["bg_mid"][0] + (COLORS["bg_bot"][0] - COLORS["bg_mid"][0]) * t2)
            g = int(COLORS["bg_mid"][1] + (COLORS["bg_bot"][1] - COLORS["bg_mid"][1]) * t2)
            b = int(COLORS["bg_mid"][2] + (COLORS["bg_bot"][2] - COLORS["bg_mid"][2]) * t2)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def draw_scan_lines(draw: ImageDraw.ImageDraw) -> None:
    """Draw horizontal scan lines across the upper portion."""
    for y in range(0, PANEL_Y, 4):
        alpha = random.randint(2, 6)
        draw.line([(0, y), (WIDTH, y)], fill=(0, 255, 0, alpha))


def draw_circuit_traces(draw: ImageDraw.ImageDraw) -> None:
    """Draw circuit-board style traces."""
    for _ in range(30):
        x = random.randint(50, WIDTH - 50)
        y = random.randint(50, PANEL_Y - 200)
        length = random.randint(60, 300)
        direction = random.choice(["h", "v", "L", "7"])
        color = random.choice([COLORS["circuit_line"], COLORS["circuit_dim"], COLORS["circuit_line"]])
        line_w = random.choice([1, 2])

        if direction == "h":
            draw.line([(x, y), (x + length, y)], fill=color, width=line_w)
            draw.ellipse([x + length - 3, y - 3, x + length + 3, y + 3], fill=COLORS["circuit_node"])
        elif direction == "v":
            draw.line([(x, y), (x, y + length)], fill=color, width=line_w)
            draw.ellipse([x - 3, y + length - 3, x + 3, y + length + 3], fill=COLORS["circuit_node"])
        elif direction == "L":
            mid = length // 2
            draw.line([(x, y), (x + mid, y)], fill=color, width=line_w)
            draw.line([(x + mid, y), (x + mid, y + mid)], fill=color, width=line_w)
            draw.ellipse([x + mid - 3, y + mid - 3, x + mid + 3, y + mid + 3], fill=COLORS["circuit_node"])
        else:
            mid = length // 2
            draw.line([(x, y), (x, y + mid)], fill=color, width=line_w)
            draw.line([(x, y + mid), (x + mid, y + mid)], fill=color, width=line_w)
            draw.ellipse([x + mid - 3, y + mid - 3, x + mid + 3, y + mid + 3], fill=COLORS["circuit_node"])

    # Add some IC-like rectangles
    for _ in range(6):
        x = random.randint(100, WIDTH - 150)
        y = random.randint(100, PANEL_Y - 300)
        w = random.randint(40, 100)
        h = random.randint(30, 60)
        draw.rectangle([x, y, x + w, y + h], fill=(5, 30, 10), outline=COLORS["circuit_line"], width=1)
        # Pins
        for px in range(x + 5, x + w, 12):
            draw.line([(px, y - 6), (px, y)], fill=COLORS["circuit_line"], width=1)
            draw.line([(px, y + h), (px, y + h + 6)], fill=COLORS["circuit_line"], width=1)


def draw_warning_elements(draw: ImageDraw.ImageDraw) -> None:
    """Draw red warning symbols and countdown elements."""
    # Central warning triangle
    cx, cy = WIDTH // 2, PANEL_Y // 2 - 50
    size = 120

    # Triangle warning sign
    points = [(cx, cy - size), (cx - size, cy + size), (cx + size, cy + size)]
    draw.polygon(points, outline=COLORS["accent_red"], width=4)
    draw.polygon(points, fill=None)

    # Inner exclamation mark
    bar_x = cx - 6
    draw.rectangle([bar_x, cy - size + 40, bar_x + 12, cy + 10], fill=COLORS["accent_red"])
    draw.ellipse([cx - 8, cy + 25, cx + 8, cy + 45], fill=COLORS["accent_red"])

    # Pulsing rings around warning
    for i in range(3):
        radius = 160 + i * 40
        alpha = 40 - i * 10
        draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            outline=(COLORS["accent_red"][0], COLORS["accent_red"][1], COLORS["accent_red"][2], alpha),
            width=2,
        )

    # Horizontal warning bars
    for i, y_pos in enumerate([150, 190, 230]):
        draw.rectangle([0, y_pos, WIDTH, y_pos + 3], fill=COLORS["accent_dark_red"])

    # Glitch lines (random red/bright-green horizontal streaks)
    for _ in range(15):
        y = random.randint(250, PANEL_Y - 100)
        x_start = random.randint(0, WIDTH - 200)
        x_end = x_start + random.randint(40, 300)
        glitch_color = random.choice([
            COLORS["accent_red"],
            COLORS["accent_green"],
            (255, 255, 255),
        ])
        draw.line([(x_start, y), (x_end, y)], fill=glitch_color, width=random.randint(1, 3))


def draw_digital_grid(draw: ImageDraw.ImageDraw) -> None:
    """Draw a subtle digital grid overlay."""
    # Vertical lines
    for x in range(0, WIDTH, 80):
        alpha = random.randint(3, 8)
        for y in range(0, PANEL_Y, 4):
            draw.point((x, y), fill=(0, 255, 0, alpha))

    # Horizontal lines
    for y in range(0, PANEL_Y, 80):
        alpha = random.randint(3, 8)
        for x in range(0, WIDTH, 3):
            draw.point((x, y), fill=(0, 255, 0, alpha))


def draw_title_panel(draw: ImageDraw.ImageDraw, title: str, author: str) -> None:
    draw.rectangle([0, PANEL_Y, WIDTH, HEIGHT], fill=COLORS["panel_bg"])

    separator_y = PANEL_Y + 8
    draw.rectangle([60, separator_y, WIDTH - 60, separator_y + 3], fill=(0, 120, 40))

    georgia_bold_path = FONT_DIR / "georgiab.ttf"
    arial_bold_path = FONT_DIR / "arialbd.ttf"

    try:
        title_font = ImageFont.truetype(str(georgia_bold_path), 72)
    except Exception:
        title_font = ImageFont.load_default()

    try:
        author_font = ImageFont.truetype(str(arial_bold_path), 32)
    except Exception:
        author_font = ImageFont.load_default()

    # Split title into two lines
    words = title.split()
    if len(words) <= 3:
        lines = [title]
    elif len(words) <= 4:
        mid = len(words) // 2
        lines = [" ".join(words[:mid]), " ".join(words[mid:])]
    else:
        mid = len(words) // 2 + len(words) % 2
        lines = [" ".join(words[:mid]), " ".join(words[mid:])]

    center_x = WIDTH // 2

    # Calculate total height of title block
    title_heights = []
    title_widths = []
    for line_text in lines:
        try:
            bbox = draw.textbbox((0, 0), line_text, font=title_font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
        except Exception:
            w, h = title_font.getsize(line_text)
        title_widths.append(w)
        title_heights.append(h)

    total_title_h = sum(title_heights) + (len(lines) - 1) * 10
    title_start_y = PANEL_Y + (HEIGHT - PANEL_Y - total_title_h) // 2 - 40

    for i, line_text in enumerate(lines):
        y_pos = title_start_y + sum(title_heights[:i]) + i * 10
        draw.text((center_x - title_widths[i] // 2, y_pos), line_text, fill=COLORS["title_text"], font=title_font)

    # Author name
    author_y = HEIGHT - 80
    try:
        abbox = draw.textbbox((0, 0), author, font=author_font)
        aw = abbox[2] - abbox[0]
    except Exception:
        aw, _ = author_font.getsize(author)
    draw.text((center_x - aw // 2, author_y), author, fill=COLORS["author_text"], font=author_font)

    # Small text line
    bottom_line = "A Techno-Thriller"
    try:
        small_font = ImageFont.truetype(str(FONT_DIR / "arial.ttf"), 16)
        sbbox = draw.textbbox((0, 0), bottom_line, font=small_font)
        sw = sbbox[2] - sbbox[0]
    except Exception:
        small_font = ImageFont.load_default()
        sw, _ = small_font.getsize(bottom_line)
    draw.text((center_x - sw // 2, HEIGHT - 115), bottom_line, fill=(140, 140, 160), font=small_font)



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    title = metadata["title"]
    author = metadata["author"]
    model = metadata.get("model", "")

    img = Image.new("RGB", (WIDTH, HEIGHT), COLORS["bg_top"])
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(PANEL_Y):
        t = y / PANEL_Y
        if t < 0.5:
            t2 = t * 2
            r = int(5 + (10 - 5) * t2)
            g = int(20 + (35 - 20) * t2)
            b = int(5 + (10 - 5) * t2)
        else:
            t2 = (t - 0.5) * 2
            r = int(10 + (0 - 10) * t2)
            g = int(35 + (5 - 35) * t2)
            b = int(10 + (0 - 10) * t2)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    for _ in range(20):
        x = random.randint(50, WIDTH - 50)
        y = random.randint(50, PANEL_Y - 200)
        length = random.randint(60, 300)
        color = random.choice([(0, 200, 80), (0, 100, 40)])
        lw = random.choice([1, 2])
        draw.line([(x, y), (x + length, y)], fill=color, width=lw)
        draw.ellipse([x + length - 3, y - 3, x + length + 3, y + 3], fill=(0, 220, 100))
        draw.line([(x, y), (x, y + length // 2)], fill=color, width=lw)

    cx, cy = WIDTH // 2, PANEL_Y // 2 - 50
    tf = ImageFont.load_default()
    tf_big = ImageFont.load_default()
    try:
        tf_big = ImageFont.truetype(str(FONT_DIR / "courbd.ttf"), 120)
    except Exception:
        pass
    countdown_text = "00:00:00"
    try:
        cbbox = draw.textbbox((0, 0), countdown_text, font=tf_big)
        cw = cbbox[2] - cbbox[0]
    except Exception:
        cw = 0
    draw.text((cx - cw // 2, cy - 60), countdown_text, fill=(0, 255, 0), font=tf_big)

    for i in range(3):
        radius = 200 + i * 40
        draw.ellipse([cx - radius, cy + 80 - radius, cx + radius, cy + 80 + radius], outline=(0, 255, 0, 40 - i * 10), width=2)

    ghost_cx, ghost_cy = cx, cy + 230
    draw.ellipse([ghost_cx - 15, ghost_cy - 25, ghost_cx + 15, ghost_cy + 5], fill=(0, 255, 0, 100))
    draw.polygon([(ghost_cx - 18, ghost_cy + 5), (ghost_cx + 18, ghost_cy + 5), (ghost_cx + 20, ghost_cy + 80), (ghost_cx - 20, ghost_cy + 80)], fill=(0, 255, 0, 80))

    city = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    cd = ImageDraw.Draw(city)
    for _ in range(20):
        bx = random.randint(50, WIDTH - 50)
        bh = random.randint(40, 200)
        bw = random.randint(30, 80)
        cd.rectangle([bx, PANEL_Y - bh, bx + bw, PANEL_Y], fill=(5, 8, 10, 200))
        for _ in range(3):
            wx = bx + random.randint(5, bw - 10)
            wy = PANEL_Y - bh + random.randint(10, bh - 20)
            cd.rectangle([wx, wy, wx + 6, wy + 8], fill=(20, 30, 20, 180))
    city = city.filter(ImageFilter.GaussianBlur(2))
    img = Image.alpha_composite(img.convert("RGBA"), city)

    for _ in range(10):
        y = random.randint(250, PANEL_Y - 100)
        xs = random.randint(0, WIDTH - 200)
        xe = xs + random.randint(40, 300)
        gc = random.choice([(0, 255, 0), (255, 50, 50), (255, 255, 255)])
        draw.line([(xs, y), (xe, y)], fill=gc, width=random.randint(1, 3))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.save(args.out, "PNG")
    print(f"Cover saved to {args.out}")


if __name__ == "__main__":
    main()