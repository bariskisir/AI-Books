#!/usr/bin/env python3
"""Generate a 1600x2560 cover for The Train in the Snow."""

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


WIDTH, HEIGHT = 1600, 2560


def draw_gradient(draw: ImageDraw.ImageDraw) -> None:
    """Draw a vertical gradient from midnight blue (top) to icy white (bottom)."""
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(10 + ratio * 200)
        g = int(15 + ratio * 210)
        b = int(50 + ratio * 230)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def draw_mountains(draw: ImageDraw.ImageDraw) -> None:
    """Draw stylized alpine landscape with snow-capped peaks."""
    # Background mountains (lighter blue)
    peaks = [
        (0, 1400, 250, 920, 500, 1400),
        (300, 1400, 600, 860, 900, 1400),
        (700, 1400, 1000, 800, 1300, 1400),
        (1100, 1400, 1400, 900, 1600, 1400),
    ]
    for x1, y1, x2, y2, x3, y3 in peaks:
        draw.polygon([(x1, y1), (x2, y2), (x3, y3)], fill=(70, 90, 140, 180))

    # Foreground mountains (deeper blue)
    fg_peaks = [
        (-50, 1500, 200, 1050, 450, 1500),
        (400, 1500, 650, 1000, 900, 1500),
        (800, 1500, 1050, 980, 1300, 1500),
        (1200, 1500, 1450, 1020, 1650, 1500),
    ]
    for x1, y1, x2, y2, x3, y3 in fg_peaks:
        draw.polygon([(x1, y1), (x2, y2), (x3, y3)], fill=(30, 45, 90))

    # Snow caps on foreground peaks
    snow_caps = [
        (160, 1080, 200, 1050, 240, 1080),
        (610, 1030, 650, 1000, 690, 1030),
        (1010, 1010, 1050, 980, 1090, 1010),
        (1410, 1050, 1450, 1020, 1490, 1050),
    ]
    for x1, y1, x2, y2, x3, y3 in snow_caps:
        draw.polygon([(x1, y1), (x2, y2), (x3, y3)], fill=(220, 230, 245))


def draw_train(draw: ImageDraw.ImageDraw) -> None:
    """Draw a stylized snowbound train on the tracks."""
    # Snow-covered ground
    draw.rectangle([(0, 1400), (WIDTH, 1550)], fill=(230, 240, 250))

    # Train body
    train_x, train_y = 450, 1280
    train_w, train_h = 700, 180

    # Locomotive body
    draw.rectangle([(train_x, train_y), (train_x + train_w, train_y + train_h)], fill=(20, 30, 60))
    # Locomotive cabin
    draw.rectangle([(train_x + 50, train_y - 40), (train_x + 180, train_y)], fill=(25, 35, 70))
    # Smokestack
    draw.rectangle([(train_x + 90, train_y - 70), (train_x + 120, train_y - 40)], fill=(40, 40, 40))
    # Smokestack top
    draw.ellipse([(train_x + 85, train_y - 80), (train_x + 125, train_y - 65)], fill=(50, 50, 50))

    # Boiler door on front
    draw.ellipse([(train_x + train_w - 60, train_y + 40), (train_x + train_w - 10, train_y + 90)], fill=(80, 60, 40))
    # Headlight
    draw.ellipse([(train_x + train_w - 10, train_y + 20), (train_x + train_w + 10, train_y + 50)], fill=(255, 240, 180))

    # Cowcatcher
    draw.polygon(
        [
            (train_x + train_w, train_y + train_h - 20),
            (train_x + train_w + 40, train_y + train_h + 10),
            (train_x + train_w, train_y + train_h),
        ],
        fill=(40, 40, 40),
    )

    # Carriages
    for i in range(3):
        cx = train_x - 190 * (i + 1)
        draw.rectangle([(cx, train_y + 10), (cx + 170, train_y + train_h - 10)], fill=(25, 35, 70))
        # Windows
        for j in range(4):
            wx = cx + 15 + j * 38
            draw.rectangle([(wx, train_y + 30), (wx + 25, train_y + 70)], fill=(100, 120, 180))
            # Warm window glow
            draw.rectangle([(wx + 2, train_y + 32), (wx + 23, train_y + 68)], fill=(200, 180, 120))

    # Wheels
    for wx in [train_x + 50, train_x + 200, train_x + 350, train_x + 550, train_x + 650]:
        draw.ellipse([(wx, train_y + train_h - 15), (wx + 35, train_y + train_h + 20)], fill=(50, 50, 50))

    # Tracks
    draw.line([(0, train_y + train_h + 15), (WIDTH, train_y + train_h + 15)], fill=(80, 80, 80), width=4)
    draw.line([(0, train_y + train_h + 30), (WIDTH, train_y + train_h + 30)], fill=(80, 80, 80), width=4)

    # Snow on top of train
    snow_y = train_y - 5
    for i in range(-3, 4):
        sx = train_x + i * 100
        sw = 120
        draw.ellipse([(sx, snow_y - 8), (sx + sw, snow_y + 3)], fill=(240, 245, 255))


def draw_steam(draw: ImageDraw.ImageDraw) -> None:
    """Draw stylized steam from the locomotive."""
    steam_base = (540, 1190)
    # Multiple overlapping translucent circles for steam
    steam_positions = [
        (540, 1180, 40),
        (510, 1150, 55),
        (560, 1140, 45),
        (490, 1110, 60),
        (550, 1100, 50),
        (470, 1070, 45),
        (530, 1050, 55),
        (450, 1020, 35),
        (510, 1000, 40),
    ]
    for sx, sy, sr in steam_positions:
        draw.ellipse(
            [(sx - sr, sy - sr), (sx + sr, sy + sr)],
            fill=(200, 210, 230, 60),
        )


def draw_snowflakes(draw: ImageDraw.ImageDraw) -> None:
    """Draw scattered snowflakes in the sky."""
    flakes = [
        (100, 300, 3),
        (300, 150, 2),
        (500, 400, 4),
        (700, 200, 3),
        (900, 350, 2),
        (1100, 100, 3),
        (1300, 450, 4),
        (1500, 250, 2),
        (200, 600, 3),
        (400, 500, 2),
        (800, 550, 3),
        (1200, 600, 2),
        (1400, 400, 3),
        (600, 700, 2),
        (1000, 650, 4),
        (300, 800, 2),
        (1100, 800, 3),
        (700, 900, 2),
        (900, 750, 3),
        (150, 450, 2),
    ]
    for fx, fy, fs in flakes:
        # Draw star-like snowflake
        for i in range(4):
            angle = i * 45
            import math
            ex = fx + fs * math.cos(math.radians(angle))
            ey = fy + fs * math.sin(math.radians(angle))
            draw.line([(fx, fy), (ex, ey)], fill=(255, 255, 255, 180), width=1)


def draw_title_panel(draw: ImageDraw.ImageDraw, title: str, author: str) -> None:
    """Draw the title panel at the bottom of the cover with WHITE text on dark panel."""
    panel_top = 1920

    # Dark semi-transparent panel
    draw.rectangle([(0, panel_top), (WIDTH, HEIGHT)], fill=(15, 20, 45, 220))

    # Decorative line above title
    draw.line([(400, panel_top + 30), (1200, panel_top + 30)], fill=(180, 190, 210), width=2)
    draw.line([(600, panel_top + 36), (1000, panel_top + 36)], fill=(180, 190, 210), width=1)

    # Snowflake ornament
    draw.ellipse([(780, panel_top + 50), (820, panel_top + 70)], fill=(180, 190, 210))

    # Title - use arialbd.ttf
    try:
        font_large = ImageFont.truetype("arialbd.ttf", 72)
        font_medium = ImageFont.truetype("arialbd.ttf", 42)
        font_author = ImageFont.truetype("arialbd.ttf", 24)
    except (OSError, IOError):
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_author = ImageFont.load_default()

    # Title
    title_text = title.upper()
    bbox = draw.textbbox((0, 0), title_text, font=font_large)
    tw = bbox[2] - bbox[0]
    tx = (WIDTH - tw) // 2
    draw.text((tx, panel_top + 85), title_text, fill=(255, 255, 255), font=font_large)

    # Decorative line below title
    draw.line([(500, panel_top + 175), (1100, panel_top + 175)], fill=(140, 150, 180), width=1)

    # Genre line
    genre_text = "A Winter Mystery"
    bbox = draw.textbbox((0, 0), genre_text, font=font_medium)
    tw = bbox[2] - bbox[0]
    tx = (WIDTH - tw) // 2
    draw.text((tx, panel_top + 200), genre_text, fill=(200, 210, 230), font=font_medium)

    # Author
    author_text = f"by {author}"
    bbox = draw.textbbox((0, 0), author_text, font=font_author)
    tw = bbox[2] - bbox[0]
    tx = (WIDTH - tw) // 2
    draw.text((tx, panel_top + 270), author_text, fill=(255, 255, 255), font=font_author)

    # Decorative line at bottom
    draw.line([(400, panel_top + 320), (1200, panel_top + 320)], fill=(180, 190, 210), width=2)


def build(metadata_path: Path, output_path: Path) -> None:
    """Generate the cover image."""
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata["title"]
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    draw_gradient(draw)
    draw_mountains(draw)
    draw_train(draw)
    draw_steam(draw)
    draw_snowflakes(draw)
    draw_title_panel(draw, title, author)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    build(args.metadata, args.out)


if __name__ == "__main__":
    main()