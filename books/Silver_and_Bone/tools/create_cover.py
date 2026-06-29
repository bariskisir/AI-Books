#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for Silver and Bone."""

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



WIDTH = 1600
HEIGHT = 2560
TITLE_PANEL_Y = 1920


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype(path, size)
    except (IOError, OSError):
        return ImageFont.load_default()


def draw_rain(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    """Draw rain streaks across the image."""
    import random
    random.seed(42)
    for _ in range(600):
        x = random.randint(0, width)
        y = random.randint(0, height)
        length = random.randint(10, 40)
        opacity = random.randint(30, 100)
        draw.line(
            [(x, y), (x - 2, y + length)],
            fill=(180, 200, 230, opacity),
            width=1,
        )


def draw_buildings(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    """Draw Chicago skyline silhouette."""
    buildings = [
        (0, 600, 120, 900),
        (80, 450, 180, 900),
        (140, 550, 220, 900),
        (200, 400, 280, 900),
        (260, 500, 340, 900),
        (320, 350, 420, 900),
        (380, 480, 460, 900),
        (440, 520, 520, 900),
        (500, 380, 600, 900),
        (570, 450, 650, 900),
        (630, 550, 710, 900),
        (690, 420, 780, 900),
        (750, 350, 850, 900),
        (820, 500, 920, 900),
        (890, 400, 980, 900),
        (950, 550, 1050, 900),
        (1020, 450, 1120, 900),
        (1090, 380, 1190, 900),
        (1150, 520, 1250, 900),
        (1220, 600, 1320, 900),
        (1300, 480, 1400, 900),
        (1380, 420, 1480, 900),
        (1450, 550, 1550, 900),
        (1500, 650, 1600, 900),
    ]
    for x1, y1, x2, y2 in buildings:
        draw.rectangle([x1, y1, x2, y2], fill=(15, 18, 30))


def draw_street(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    """Draw street and sidewalk at bottom of scene area."""
    # Street
    draw.rectangle([0, 850, width, 950], fill=(25, 28, 40))
    # Sidewalk
    draw.rectangle([0, 950, width, 1000], fill=(50, 53, 65))
    # Street line
    draw.rectangle([0, 895, width, 900], fill=(180, 180, 140, 80))


def draw_lamp(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    """Draw a streetlamp with light cone."""
    # Pole
    draw.rectangle([x - 2, y - 120, x + 2, y], fill=(60, 60, 70))
    # Lamp head
    draw.ellipse([x - 6, y - 130, x + 6, y - 118], fill=(220, 220, 200))
    # Light cone
    light = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    light_draw = ImageDraw.Draw(light)
    light_draw.polygon(
        [(x, y - 118), (x - 100, y + 30), (x + 100, y + 30)],
        fill=(180, 200, 220, 25),
    )
    draw.bitmap((0, 0), light, fill=None)


def draw_alley(draw: ImageDraw.ImageDraw) -> None:
    """Draw an alleyway with a glowing portal on the left side."""
    # Alley entrance
    draw.rectangle([100, 700, 280, 950], fill=(8, 8, 15))
    # Alley walls
    draw.rectangle([100, 700, 120, 950], fill=(25, 20, 30))
    draw.rectangle([260, 700, 280, 950], fill=(25, 20, 30))
    # Brick texture hints
    for y in range(720, 940, 30):
        for x in range(120, 260, 40):
            draw.rectangle([x, y, x + 35, y + 25], outline=(35, 30, 40), width=1)

    # Glowing portal at the end of alley
    portal_center = (190, 780)
    # Outer glow
    for r in range(60, 10, -5):
        alpha = max(10, 200 - r * 3)
        draw.ellipse(
            [portal_center[0] - r, portal_center[1] - r,
             portal_center[0] + r, portal_center[1] + r],
            fill=(100, 180, 255, alpha),
        )
    # Inner portal
    draw.ellipse(
        [portal_center[0] - 12, portal_center[1] - 12,
         portal_center[0] + 12, portal_center[1] + 12],
        fill=(180, 220, 255, 200),
    )
    # Light rays from portal
    ray = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    ray_draw = ImageDraw.Draw(ray)
    for angle in range(0, 360, 30):
        import math
        rad = math.radians(angle)
        ex = portal_center[0] + math.cos(rad) * 200
        ey = portal_center[1] + math.sin(rad) * 200
        ray_draw.line(
            [portal_center, (ex, ey)],
            fill=(150, 200, 255, 15),
            width=3,
        )
    draw.bitmap((0, 0), ray, fill=None)


def draw_detective(draw: ImageDraw.ImageDraw) -> None:
    """Draw a detective silhouette in the foreground."""
    # Silhouette figure
    x_center = 1050
    y_base = 890
    # Body
    body_coords = [
        (x_center - 20, y_base),      # left foot
        (x_center - 15, y_base - 40), # left leg
        (x_center - 18, y_base - 70), # hip
        (x_center - 25, y_base - 100),# left shoulder
        (x_center - 30, y_base - 125),# left arm
        (x_center - 25, y_base - 150),# hand
        (x_center - 15, y_base - 140),# arm inner
        (x_center - 8, y_base - 130), # shoulder
        (x_center - 5, y_base - 150), # neck
        (x_center - 8, y_base - 170), # top of head
        (x_center + 8, y_base - 170), # top of head right
        (x_center + 10, y_base - 150),# right neck
        (x_center + 15, y_base - 130),# right shoulder
        (x_center + 20, y_base - 140),# arm inner
        (x_center + 25, y_base - 150),# hand
        (x_center + 30, y_base - 125),# right arm
        (x_center + 25, y_base - 100),# right shoulder lower
        (x_center + 20, y_base - 70), # right hip
        (x_center + 15, y_base - 40), # right leg
        (x_center + 20, y_base),      # right foot
    ]
    draw.polygon(body_coords, fill=(5, 5, 10))
    # Hat brim
    draw.rectangle([x_center - 18, y_base - 175, x_center + 18, y_base - 168], fill=(5, 5, 10))
    # Hat top
    draw.rectangle([x_center - 10, y_base - 195, x_center + 10, y_base - 175], fill=(5, 5, 10))


def draw_moon(draw: ImageDraw.ImageDraw) -> None:
    """Draw a partial moon behind clouds."""
    # Moon
    draw.ellipse([1300, 80, 1480, 260], fill=(200, 210, 230, 40))
    draw.ellipse([1320, 100, 1460, 240], fill=(220, 225, 240, 60))
    draw.ellipse([1340, 120, 1440, 220], fill=(235, 240, 250, 80))
    # Cloud wisps over moon
    draw.ellipse([1280, 140, 1400, 200], fill=(25, 28, 45, 180))
    draw.ellipse([1380, 110, 1500, 180], fill=(25, 28, 45, 160))


def draw_title_panel(draw: ImageDraw.ImageDraw, title: str, author: str) -> None:
    """Draw the bottom title panel area."""
    # Light rectangle panel
    draw.rectangle([0, TITLE_PANEL_Y, WIDTH, HEIGHT], fill=(220, 222, 228))
    # Subtle border line at top of panel
    draw.rectangle([0, TITLE_PANEL_Y, WIDTH, TITLE_PANEL_Y + 3], fill=(180, 185, 195))

    title_font = load_font("C:/Windows/Fonts/georgiab.ttf", 72)
    author_font = load_font("C:/Windows/Fonts/arialbd.ttf", 36)

    # Title
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_w = title_bbox[2] - title_bbox[0]
    title_x = (WIDTH - title_w) // 2
    draw.text((title_x, TITLE_PANEL_Y + 60), title, fill=(30, 30, 45), font=title_font)

    # Author
    author_bbox = draw.textbbox((0, 0), author, font=author_font)
    author_w = author_bbox[2] - author_bbox[0]
    author_x = (WIDTH - author_w) // 2
    draw.text((author_x, TITLE_PANEL_Y + 190), author, fill=(80, 80, 90), font=author_font)



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    with open(args.metadata, encoding="utf-8") as f:
        meta = json.load(f)

    title = meta.get("title", "Silver and Bone")
    author = meta.get("author", "Barış Kısır")
    model = meta.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, "RGBA")

    # Night sky gradient background (silver-blue to dark)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(10 + ratio * 15)
        g = int(12 + ratio * 18)
        b = int(35 + ratio * 30)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Dark city silhouette at top
    draw_moon(draw)
    draw_buildings(draw, WIDTH, HEIGHT)
    draw_street(draw, WIDTH, HEIGHT)
    draw_alley(draw)
    draw_lamp(draw, 400, 870)
    draw_lamp(draw, 1200, 870)
    draw_detective(draw)
    draw_rain(draw, WIDTH, HEIGHT)

    # Apply subtle gaussian blur for atmospheric feel
    img = img.filter(ImageFilter.GaussianBlur(radius=1))

    # Re-draw sharp elements on top of the blurred base
    draw = ImageDraw.Draw(img, "RGBA")
    draw_buildings(draw, WIDTH, HEIGHT)
    draw_street(draw, WIDTH, HEIGHT)
    draw_alley(draw)
    draw_detective(draw)
    draw_lamp(draw, 400, 870)
    draw_lamp(draw, 1200, 870)
    # Moon needs to be above blur
    draw_moon(draw)
    # Redraw portal glow sharper
    portal_center = (190, 780)
    draw.ellipse(
        [portal_center[0] - 50, portal_center[1] - 50,
         portal_center[0] + 50, portal_center[1] + 50],
        fill=(120, 190, 255, 60),
    )
    draw.ellipse(
        [portal_center[0] - 20, portal_center[1] - 20,
         portal_center[0] + 20, portal_center[1] + 20],
        fill=(180, 220, 255, 150),
    )
    draw.ellipse(
        [portal_center[0] - 8, portal_center[1] - 8,
         portal_center[0] + 8, portal_center[1] + 8],
        fill=(220, 240, 255, 220),
    )

    # Title panel - drawn after blur
    draw_title_panel(draw, title, author)

    # Save as RGB
    rgb_img = img.convert("RGB")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(rgb_img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    rgb_img.save(args.out, "PNG")
    print(f"Cover saved to {args.out}")


if __name__ == "__main__":
    main()