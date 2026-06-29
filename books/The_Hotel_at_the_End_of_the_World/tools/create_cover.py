#!/usr/bin/env python3
"""Generate a cover image for The Hotel at the End of the World."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

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


def resolve_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Try to load arialbd/arial, fall back to default."""
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for path in candidates:
        p = Path(path)
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except Exception:
                continue
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


def draw_gradient(draw: ImageDraw.Draw) -> None:
    """Deep midnight-blue-to-gold gradient background."""
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        # midnight blue (10, 10, 50) -> deep navy -> dark gold -> gold accent
        r = int(10 + ratio * 180)
        g = int(10 + ratio * 130)
        b = int(50 + ratio * 30)
        if ratio > 0.6:
            # warm gold toward bottom
            r = int(120 + (ratio - 0.6) / 0.4 * 100)
            g = int(80 + (ratio - 0.6) / 0.4 * 60)
            b = int(20 + (ratio - 0.6) / 0.4 * 10)
        draw.line([(0, y), (WIDTH, y)], fill=(min(r, 255), min(g, 255), min(b, 255)))


def draw_mountains(draw: ImageDraw.Draw) -> None:
    """Patagonian mountain silhouettes."""
    peaks = [
        (0, 1400, 200, 1100, 400, 1300),
        (300, 1300, 500, 950, 700, 1200),
        (600, 1200, 800, 850, 1000, 1150),
        (900, 1150, 1100, 900, 1300, 1200),
        (1200, 1200, 1400, 1000, 1600, 1250),
    ]
    for x1, y1, x2, y2, x3, y3 in peaks:
        draw.polygon([(x1, y1), (x2, y2), (x3, y3)], fill=(20, 15, 40, 180))


def draw_hotel_facade(draw: ImageDraw.Draw) -> None:
    """Vintage hotel facade against the mountains."""
    # Main building
    hotel_left = 400
    hotel_top = 800
    hotel_width = 800
    hotel_height = 600

    # Building body
    draw.rectangle(
        [hotel_left, hotel_top, hotel_left + hotel_width, hotel_top + hotel_height],
        fill=(30, 25, 50, 200),
        outline=(180, 160, 100),
        width=3,
    )

    # Roof
    draw.polygon(
        [
            (hotel_left - 40, hotel_top),
            (hotel_left + hotel_width // 2, hotel_top - 120),
            (hotel_left + hotel_width + 40, hotel_top),
        ],
        fill=(40, 35, 60),
        outline=(180, 160, 100),
        width=3,
    )

    # Windows - rows and columns
    win_w, win_h = 60, 100
    gap_x, gap_y = 30, 50
    margin_x = 80
    margin_y = 60
    cols = (hotel_width - 2 * margin_x + gap_x) // (win_w + gap_x)
    rows = (hotel_height - 2 * margin_y + gap_y) // (win_h + gap_y)
    for row in range(rows):
        for col in range(cols):
            x = hotel_left + margin_x + col * (win_w + gap_x)
            y = hotel_top + margin_y + row * (win_h + gap_y)
            # Warm lit windows
            brightness = 200 + 55 * math.sin(row * 1.2 + col * 0.8)
            draw.rectangle(
                [x, y, x + win_w, y + win_h],
                fill=(int(brightness), int(brightness * 0.8), 60),
                outline=(100, 90, 50),
            )

    # Entrance door
    door_x = hotel_left + hotel_width // 2 - 50
    door_y = hotel_top + hotel_height - 160
    draw.rectangle(
        [door_x, door_y, door_x + 100, door_y + 160],
        fill=(60, 55, 80),
        outline=(180, 160, 100),
        width=3,
    )
    # Door arch
    draw.arc(
        [door_x, door_y - 40, door_x + 100, door_y + 10],
        start=180, end=0,
        fill=(180, 160, 100),
        width=3,
    )

    # Sign above entrance
    sign_y = door_y - 120
    draw.text(
        (WIDTH // 2, sign_y),
        "HOTEL",
        fill=(200, 180, 120),
        font=resolve_font(28, bold=True),
        anchor="mm",
    )


def draw_vintage_lobby(draw: ImageDraw.Draw) -> None:
    """Subtle vintage lobby elements at the bottom."""
    # Chandelier silhouette
    cx, cy = WIDTH // 2, 720
    draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(200, 180, 100))
    # Chains
    for offset in [-30, 0, 30]:
        for i in range(5):
            draw.ellipse(
                [cx + offset - 3, cy + 10 + i * 12 - 3, cx + offset + 3, cy + 10 + i * 12 + 3],
                fill=(180, 160, 90),
            )
    # Light glow
    draw.ellipse(
        [cx - 100, cy - 100, cx + 100, cy + 100],
        fill=(200, 180, 60, 20),
    )


def draw_title_panel(draw: ImageDraw.Draw) -> None:
    """Dark panel at bottom with white title text."""
    panel_top = 1920
    panel_height = 640

    # Semi-transparent dark panel
    for y in range(panel_top, HEIGHT):
        alpha = int(120 + (y - panel_top) / panel_height * 60)
        draw.line(
            [(0, y), (WIDTH, y)],
            fill=(10, 8, 25, min(alpha, 180)),
        )

    # Title
    title_font = resolve_font(64, bold=True)
    title = "The Hotel at the\nEnd of the World"
    draw.multiline_text(
        (WIDTH // 2, panel_top + 100),
        title,
        fill=(255, 255, 255),
        font=title_font,
        anchor="mm",
        align="center",
        spacing=10,
    )

    # Author
    author_font = resolve_font(32, bold=False)
    draw.text(
        (WIDTH // 2, panel_top + 240),
        "Barış Kısır",
        fill=(200, 180, 120),
        font=author_font,
        anchor="mm",
    )

    # Decorative line
    line_y = panel_top + 280
    draw.line(
        [(WIDTH // 2 - 150, line_y), (WIDTH // 2 + 150, line_y)],
        fill=(180, 160, 100),
        width=2,
    )



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    if args.metadata:
        metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
        title = metadata.get("title", "The Hotel at the End of the World")
    else:
        title = "The Hotel at the End of the World"

    out_path = args.out or Path("The_Hotel_at_the_End_of_the_World/covers/The_Hotel_at_the_End_of_the_World.png")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (10, 10, 50, 255))
    draw = ImageDraw.Draw(img)

    # Gradient background
    draw_gradient(draw)

    # Mountain silhouettes
    draw_mountains(draw)

    # Hotel facade
    draw_hotel_facade(draw)

    # Vintage lobby elements
    draw_vintage_lobby(draw)

    # Title panel
    draw_title_panel(draw)

    # Soft glow filter
    img = img.filter(ImageFilter.GaussianBlur(radius=1))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()))
    img.save(out_path, "PNG")
    print(f"Cover saved: {out_path}")


if __name__ == "__main__":
    main()