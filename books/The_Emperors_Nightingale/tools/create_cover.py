#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Emperor's Nightingale."""

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
FONT_PATH = "C:/Windows/Fonts/arialbd.ttf"
FG_COLOR = (0, 0, 0)  # black
MID_COLOR = (28, 50, 28)  # deep forest green
BG_COLOR = (10, 12, 5)  # very dark green-black

PALACE_GOLD = (212, 175, 55)
PALACE_RED = (155, 30, 30)
GEAR_BRASS = (184, 134, 11)
JADE_GREEN = (0, 168, 107)
SILVER = (192, 192, 192)
DARK_PANEL = (10, 8, 6)
STAR_COLOR = (255, 230, 180)

TITLE = "The Emperor's\nNightingale"
AUTHOR = "Barış Kısır"


def draw_palace_silhouette(draw: ImageDraw) -> None:
    """Draw an imperial palace skyline across the middle distance."""
    # Main hall
    points = [
        (100, 1200), (200, 900), (300, 900), (300, 850), (320, 850), (320, 800),
        (360, 800), (360, 750), (400, 750), (400, 700), (440, 700),
        (440, 750), (480, 750), (480, 800), (520, 800), (520, 850),
        (540, 850), (540, 900), (640, 900), (740, 900),
        (740, 850), (760, 850), (760, 800), (800, 800), (800, 750),
        (840, 750), (840, 700), (880, 700), (880, 750), (920, 750),
        (920, 800), (960, 800), (960, 850), (980, 850), (980, 900),
        (1080, 900), (1180, 900), (1180, 950), (1500, 950), (1500, 1200),
    ]
    draw.polygon(points, fill=FG_COLOR, outline=None)

    # Left pagoda
    pagoda = [
        (50, 1200), (50, 1050), (70, 1050), (70, 1000), (90, 1000), (90, 960),
        (130, 960), (130, 1050), (150, 1050), (150, 1200),
    ]
    draw.polygon(pagoda, fill=FG_COLOR)

    # Right pagoda
    pagoda2 = [
        (1150, 1200), (1150, 1050), (1170, 1050), (1170, 1000), (1190, 1000),
        (1190, 960), (1230, 960), (1230, 1050), (1250, 1050), (1250, 1200),
    ]
    draw.polygon(pagoda2, fill=FG_COLOR)


def draw_clockwork_garden(draw: ImageDraw) -> None:
    """Draw clockwork flowers and vines in the foreground."""
    positions = [
        (100, 1450), (300, 1520), (550, 1480), (750, 1550),
        (1000, 1470), (1250, 1530), (1450, 1490),
    ]
    for x, y in positions:
        # Stem
        draw.line([(x, y), (x + 20, y - 80)], fill=GEAR_BRASS, width=3)
        # Flower head (gear-like circles)
        draw.ellipse([(x + 8, y - 100), (x + 32, y - 76)], fill=GEAR_BRASS, outline=PALACE_GOLD, width=2)
        # Petals as small gear teeth
        for angle in range(0, 360, 45):
            import math
            px = x + 20 + int(18 * math.cos(math.radians(angle)))
            py = y - 88 + int(18 * math.sin(math.radians(angle)))
            draw.ellipse([(px - 4, py - 4), (px + 4, py + 4)], fill=PALACE_GOLD)

    # Clockwork vines
    for base_x in [200, 600, 1000, 1400]:
        vine_y = 1400
        for i in range(6):
            draw.arc(
                [(base_x + i * 30, vine_y - 30), (base_x + (i + 1) * 30, vine_y)],
                0, 180, fill=JADE_GREEN, width=2
            )
            vine_y -= 15


def draw_mechanical_bird(draw: ImageDraw) -> None:
    """Draw the mechanical nightingale in center sky."""
    cx, cy = 800, 650
    # Body
    draw.ellipse([(cx - 40, cy - 20), (cx + 40, cy + 25)], fill=GEAR_BRASS, outline=PALACE_GOLD, width=2)
    # Head
    draw.ellipse([(cx + 30, cy - 40), (cx + 55, cy - 15)], fill=GEAR_BRASS, outline=PALACE_GOLD, width=2)
    # Eye
    draw.ellipse([(cx + 42, cy - 33), (cx + 48, cy - 27)], fill=PALACE_GOLD)
    draw.ellipse([(cx + 44, cy - 31), (cx + 46, cy - 29)], fill=(255, 255, 255))
    # Beak
    draw.polygon([(cx + 55, cy - 30), (cx + 75, cy - 28), (cx + 55, cy - 22)], fill=PALACE_GOLD)
    # Wings (spread)
    draw.polygon([(cx - 20, cy - 10), (cx - 120, cy - 80), (cx - 60, cy - 5)], fill=(160, 120, 20), outline=PALACE_GOLD, width=1)
    draw.polygon([(cx + 10, cy - 10), (cx + 100, cy - 70), (cx + 50, cy - 5)], fill=(160, 120, 20), outline=PALACE_GOLD, width=1)
    # Tail
    draw.polygon([(cx - 30, cy + 15), (cx - 80, cy + 60), (cx - 15, cy + 20)], fill=(160, 120, 20), outline=PALACE_GOLD, width=1)
    # Gear detail on body
    draw.ellipse([(cx - 15, cy - 5), (cx + 15, cy + 5)], fill=PALACE_GOLD, outline=None)
    for a in range(0, 360, 60):
        import math
        gx = cx + int(14 * math.cos(math.radians(a)))
        gy = cy + int(4 * math.sin(math.radians(a)))
        draw.ellipse([(gx - 3, gy - 3), (gx + 3, gy + 3)], fill=PALACE_RED)


def draw_stars(draw: ImageDraw) -> None:
    """Draw scattered stars in the sky."""
    import random
    random.seed(42)
    for _ in range(120):
        x = random.randint(0, WIDTH - 1)
        y = random.randint(0, 800)
        r = random.randint(1, 3)
        draw.ellipse([(x - r, y - r), (x + r, y + r)], fill=STAR_COLOR)


def draw_moon(draw: ImageDraw) -> None:
    """Draw a crescent moon."""
    cx, cy, r = 1300, 200, 60
    draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill=STAR_COLOR)
    # Inner cutout for crescent
    draw.ellipse([(cx - 20, cy - r - 10), (cx + r + 10, cy + r + 10)], fill=BG_COLOR)


def draw_title_panel(draw: ImageDraw, font_title, font_author) -> None:
    """Draw the dark title panel at the bottom of the cover."""
    panel_top = 1920
    draw.rectangle([(0, panel_top), (WIDTH, HEIGHT)], fill=DARK_PANEL)

    # Border line at top of panel
    draw.line([(100, panel_top), (WIDTH - 100, panel_top)], fill=PALACE_GOLD, width=3)

    # Title - multiline handling
    lines = TITLE.split("\n")
    y_offset = panel_top + 120
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_title)
        tw = bbox[2] - bbox[0]
        tx = (WIDTH - tw) // 2
        draw.text((tx, y_offset), line, fill=(255, 255, 255), font=font_title)
        y_offset += 130

    # Author name
    bbox = draw.textbbox((0, 0), AUTHOR, font=font_author)
    aw = bbox[2] - bbox[0]
    ax = (WIDTH - aw) // 2
    draw.text((ax, panel_top + 420), AUTHOR, fill=PALACE_GOLD, font=font_author)

    # Decorative line below author
    draw.line([(400, panel_top + 490), (WIDTH - 400, panel_top + 490)], fill=PALACE_GOLD, width=1)

    # Genre/subtitle at very bottom
    genre_font = ImageFont.truetype(FONT_PATH, 24)
    genre_text = "A Fairytale Fantasy"
    bbox = draw.textbbox((0, 0), genre_text, font=genre_font)
    gw = bbox[2] - bbox[0]
    draw.text(
        ((WIDTH - gw) // 2, panel_top + 520),
        genre_text,
        fill=(180, 180, 180),
        font=genre_font,
    )



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--out", type=Path, default="The_Emperors_Nightingale/covers/The_Emperors_Nightingale.png")
    args = parser.parse_args()

    # Build gradient background
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Vertical gradient
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(BG_COLOR[0] * (1 - t) + MID_COLOR[0] * t)
        g = int(BG_COLOR[1] * (1 - t) + MID_COLOR[1] * t)
        b = int(BG_COLOR[2] * (1 - t) + MID_COLOR[2] * t)
        draw.line([(0, y), (WIDTH - 1, y)], fill=(r, g, b))

    # Re-create draw for layers on top
    draw = ImageDraw.Draw(img)

    draw_stars(draw)
    draw_moon(draw)
    draw_mechanical_bird(draw)
    draw_palace_silhouette(draw)
    draw_clockwork_garden(draw)

    # Load fonts
    font_title = ImageFont.truetype(FONT_PATH, 80)
    font_author = ImageFont.truetype(FONT_PATH, 42)

    draw_title_panel(draw, font_title, font_author)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    model = _standard_cover_metadata_from_locals(locals()).get("model", "")
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.save(out_path)
    print(f"Cover saved to {out_path.resolve()}")


if __name__ == "__main__":
    main()