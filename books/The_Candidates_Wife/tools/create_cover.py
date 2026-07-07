#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Candidate's Wife."""

from __future__ import annotations

import argparse
import json
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



WIDTH, HEIGHT = 1600, 2560
TITLE_PANEL_Y = 1920


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> list[str]:
    """Wrap text to fit within max_width pixels."""
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines


def draw_gradient(draw: ImageDraw.ImageDraw, colors: list[tuple[int, int, int]]) -> None:
    """Draw a vertical gradient background."""
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        segments = len(colors) - 1
        seg = min(int(ratio * segments), segments - 1)
        local_ratio = (ratio * segments) - seg
        r = int(colors[seg][0] * (1 - local_ratio) + colors[seg + 1][0] * local_ratio)
        g = int(colors[seg][1] * (1 - local_ratio) + colors[seg + 1][1] * local_ratio)
        b = int(colors[seg][2] * (1 - local_ratio) + colors[seg + 1][2] * local_ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def draw_phone_screen(draw: ImageDraw.ImageDraw) -> None:
    """Draw a phone screen with tweet text."""
    phone_x, phone_y = WIDTH // 2 - 100, 380
    phone_w, phone_h = 200, 340
    draw.rounded_rectangle(
        [phone_x, phone_y, phone_x + phone_w, phone_y + phone_h],
        radius=16,
        fill=(30, 30, 35),
        outline=(80, 80, 90),
        width=3,
    )
    # Screen area
    screen_x = phone_x + 12
    screen_y = phone_y + 40
    screen_w = phone_w - 24
    screen_h = phone_h - 50
    draw.rectangle([screen_x, screen_y, screen_x + screen_w, screen_y + screen_h], fill=(20, 25, 35))
    # Tweet text lines
    tweet_lines = [
        "Mark's speechwriter",
        "thinks 'compassion'",
        "is a noun you",
        "conjugate like a",
        "verb. The",
        "teleprompter is",
        "the real",
        "candidate tonight.",
    ]
    try:
        font_small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 14)
    except (OSError, IOError):
        font_small = ImageFont.load_default()
    ty = screen_y + 10
    for line in tweet_lines:
        draw.text((screen_x + 10, ty), line, fill=(200, 220, 255), font=font_small)
        ty += 18
    # Send button
    draw.rounded_rectangle(
        [screen_x + screen_w - 50, screen_y + screen_h - 30, screen_x + screen_w - 10, screen_y + screen_h - 10],
        radius=6,
        fill=(29, 155, 240),
    )
    try:
        font_tiny = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 11)
    except (OSError, IOError):
        font_tiny = ImageFont.load_default()
    draw.text((screen_x + screen_w - 38, screen_y + screen_h - 26), "Send", fill=(255, 255, 255), font=font_tiny)


def draw_press_conference(draw: ImageDraw.ImageDraw) -> None:
    """Draw a podium and microphones."""
    # Podium
    podium_x, podium_y = WIDTH // 2 - 120, 850
    draw.rectangle([podium_x, podium_y, podium_x + 240, podium_y + 100], fill=(40, 40, 50), outline=(60, 60, 70), width=2)
    # Seal on podium
    draw.ellipse([podium_x + 80, podium_y + 15, podium_x + 160, podium_y + 55], fill=(30, 70, 130), outline=(60, 120, 200), width=2)
    # Microphones
    for mx_offset in [-30, 0, 30]:
        mx = WIDTH // 2 + mx_offset
        draw.rectangle([mx - 3, podium_y - 50, mx + 3, podium_y], fill=(100, 100, 110))
        draw.ellipse([mx - 8, podium_y - 65, mx + 8, podium_y - 50], fill=(80, 80, 90))
    # Camera flashes right side
    flash_x = WIDTH - 200
    for f_i in range(5):
        fx = flash_x + (f_i % 3) * 40
        fy = 900 + (f_i // 3) * 30
        draw.rectangle([fx, fy, fx + 20, fy + 15], fill=(50, 50, 60))
        flash_color = (200, 200, 100) if f_i % 2 == 0 else (180, 180, 80)
        draw.polygon([(fx + 10, fy - 8), (fx + 4, fy), (fx + 16, fy)], fill=flash_color)
    # Light beams from flashes
    for _ in range(3):
        lx = flash_x + 10
        ly = 870
        draw.polygon(
            [(lx, ly), (lx - 100, ly + 200), (lx + 100, ly + 200)],
            fill=(200, 200, 100, 20),
        )


def draw_chaos_elements(draw: ImageDraw.ImageDraw) -> None:
    """Draw abstract chaos elements - tweets, symbols, sparks."""
    # Floating tweet bubbles
    bubble_positions = [(100, 600), (1300, 500), (200, 1100), (1350, 1000)]
    for bx, by in bubble_positions:
        draw.rounded_rectangle([bx, by, bx + 100, by + 50], radius=8, fill=(30, 40, 60), outline=(60, 80, 120), width=1)
        draw.text((bx + 10, by + 10), "@voter", fill=(100, 150, 255), font=ImageFont.load_default())
        draw.text((bx + 10, by + 28), "...wait, what?", fill=(200, 200, 220), font=ImageFont.load_default())
    # Alert/warning symbols
    draw.polygon([(800, 450), (780, 500), (820, 500)], fill=(255, 200, 50))
    draw.polygon([(780, 1400), (760, 1450), (800, 1450)], fill=(255, 200, 50))
    # Trend lines
    for tx in range(0, WIDTH, WIDTH // 6):
        ty_base = 1200
        draw.line(
            [(tx, ty_base + 50), (tx + WIDTH // 12, ty_base + 30), (tx + WIDTH // 6, ty_base + 60)],
            fill=(255, 100, 100, 80),
            width=2,
        )


def create_cover(metadata: dict, output_path: Path) -> None:
    """Generate the cover image."""
    img = Image.new("RGB", (WIDTH, HEIGHT), (10, 10, 30))
    draw = ImageDraw.Draw(img)

    # Background gradient: dark blue -> red -> dark
    draw_gradient(draw, [(10, 15, 45), (60, 20, 30), (15, 10, 25)])

    # Apply slight blur for depth
    img = img.filter(ImageFilter.GaussianBlur(radius=2))
    draw = ImageDraw.Draw(img)

    # Draw press conference elements
    draw_press_conference(draw)

    # Draw phone screen
    draw_phone_screen(draw)

    # Draw chaos elements
    draw_chaos_elements(draw)

    # Title panel at bottom
    draw.rectangle([0, TITLE_PANEL_Y, WIDTH, HEIGHT], fill=(240, 240, 245, 230))

    # Add a subtle red/blue stripe at top of panel
    draw.rectangle([0, TITLE_PANEL_Y, WIDTH // 2, TITLE_PANEL_Y + 6], fill=(200, 50, 50))
    draw.rectangle([WIDTH // 2, TITLE_PANEL_Y, WIDTH, TITLE_PANEL_Y + 6], fill=(50, 80, 180))

    # Load fonts
    try:
        font_title = ImageFont.truetype("C:/Windows/Fonts/georgiab.ttf", 80)
        font_title_small = ImageFont.truetype("C:/Windows/Fonts/georgiab.ttf", 56)
        font_author = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 40)
        font_tagline = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 22)
    except (OSError, IOError) as e:
        print(f"Warning: Could not load fonts: {e}")
        font_title = ImageFont.load_default()
        font_title_small = ImageFont.load_default()
        font_author = ImageFont.load_default()
        font_tagline = ImageFont.load_default()

    # Title text
    title_text = metadata.get("title", "The Candidate's Wife")
    title_lines = wrap_text(title_text, font_title, WIDTH - 120, draw)

    # Draw title centered in the panel
    title_panel_center_y = TITLE_PANEL_Y + (HEIGHT - TITLE_PANEL_Y) // 2 - 40

    if len(title_lines) == 1:
        bbox = draw.textbbox((0, 0), title_lines[0], font=font_title)
        tw = bbox[2] - bbox[0]
        draw.text(((WIDTH - tw) // 2, title_panel_center_y - 30), title_lines[0], fill=(20, 20, 30), font=font_title)
    else:
        total_h = 0
        for i, line in enumerate(title_lines):
            if i == 0:
                bbox = draw.textbbox((0, 0), line, font=font_title_small)
            else:
                bbox = draw.textbbox((0, 0), line, font=font_title_small)
            total_h += (bbox[3] - bbox[1]) + 10
        current_y = title_panel_center_y - total_h // 2
        for line in title_lines:
            bbox = draw.textbbox((0, 0), line, font=font_title_small)
            tw = bbox[2] - bbox[0]
            draw.text(((WIDTH - tw) // 2, current_y), line, fill=(20, 20, 30), font=font_title_small)
            current_y += (bbox[3] - bbox[1]) + 10

    # Author name
    author_name = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")
    bbox = draw.textbbox((0, 0), author_name, font=font_author)
    aw = bbox[2] - bbox[0]
    draw.text(((WIDTH - aw) // 2, TITLE_PANEL_Y + (HEIGHT - TITLE_PANEL_Y) - 80), author_name, fill=(60, 60, 70), font=font_author)

    # Genre tagline
    genre = metadata.get("genre", "")
    if genre:
        bbox = draw.textbbox((0, 0), f"A {genre} Novel", font=font_tagline)
        gw = bbox[2] - bbox[0]
        draw.text(((WIDTH - gw) // 2, TITLE_PANEL_Y + (HEIGHT - TITLE_PANEL_Y) - 130), f"A {genre} Novel", fill=(120, 120, 130), font=font_tagline)

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.save(output_path, "PNG")
    print(f"Cover saved: {output_path}")



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    create_cover(metadata, args.out)


if __name__ == "__main__":
    main()