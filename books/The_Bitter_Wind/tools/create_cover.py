#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Bitter Wind."""

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



ROOT = Path(__file__).resolve().parents[3]
FONTS_DIR = Path("C:/Windows/Fonts")

WIDTH, HEIGHT = 1600, 2560
TITLE_PANEL_TOP = 1920


def rel(path: str | Path) -> Path:
    p = Path(path)
    return ROOT / p if not p.is_absolute() else p


def lerp_color(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def draw_gradient(draw: ImageDraw, width: int, height: int) -> None:
    """Arctic white to frost blue to deep ice gradient."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((220, 230, 240), ((180, 200, 220)), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((180, 200, 220), ((120, 160, 200)), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((120, 160, 200), ((40, 60, 100)), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_ice_cap(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the ice cap surface with ridges and crevasses."""
    # Ice surface line
    ice_y = int(height * 0.55)
    points = []
    for x in range(0, width + 1, 20):
        offset = int(math.sin(x * 0.01) * 15 + math.sin(x * 0.03) * 8 + math.sin(x * 0.007) * 20)
        points.append((x, ice_y + offset))

    # Ice surface fill (snow)
    draw.polygon([(0, height)] + points + [(width, height)], fill=(200, 215, 230))

    # Ice ridge highlights
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        if abs(y2 - y1) > 10:
            draw.line([(x1, y1 - 2), (x2, y2 - 2)], fill=(230, 240, 250), width=1)


def draw_crevasses(draw: ImageDraw, width: int, height: int) -> None:
    """Draw deep crevasses in the ice."""
    rng = random.Random(13)
    for _ in range(4):
        x = rng.randint(200, width - 200)
        base_y = int(height * 0.52)
        depth = rng.randint(80, 200)
        points = []
        for i in range(10):
            px = x + rng.randint(-40, 40)
            py = base_y + (depth * i / 10) + rng.randint(-10, 10)
            points.append((px, py))
        # Left edge
        left_points = [(x - 8 - rng.randint(0, 5), base_y)]
        for i in range(10):
            px = x - 8 + rng.randint(-15, 5)
            py = base_y + (depth * i / 10) + rng.randint(-10, 10)
            left_points.append((px, py))
        left_points.append((x - 5 + rng.randint(-5, 5), base_y + depth))

        # Right edge
        right_points = [(x + 8 + rng.randint(0, 5), base_y)]
        for i in range(10):
            px = x + 8 + rng.randint(-5, 15)
            py = base_y + (depth * i / 10) + rng.randint(-10, 10)
            right_points.append((px, py))
        right_points.append((x + 5 + rng.randint(-5, 5), base_y + depth))

        # Deep ice blue fill for crevasse
        crevasse_fill = left_points + list(reversed(right_points))
        draw.polygon(crevasse_fill, fill=(30, 60, 100))


def draw_crashed_plane(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a stylized crashed plane on the ice."""
    cx, cy = width // 2, int(height * 0.48)

    # Fuselage (broken, angled)
    fuselage_points = [
        (cx - 180, cy - 10),
        (cx - 160, cy - 30),
        (cx + 160, cy - 20),
        (cx + 180, cy),
        (cx + 160, cy + 15),
        (cx - 160, cy + 10),
    ]
    draw.polygon(fuselage_points, fill=(100, 110, 120))

    # Fuselage detail lines
    draw.line([(cx - 150, cy - 15), (cx + 150, cy - 5)], fill=(140, 150, 160), width=2)
    draw.line([(cx - 150, cy + 5), (cx + 150, cy + 5)], fill=(70, 80, 90), width=1)

    # Windows
    for i in range(6):
        wx = cx - 120 + i * 45
        draw.rectangle([wx, cy - 18, wx + 20, cy - 8], fill=(180, 200, 220))

    # Torn wing (left)
    wing_points_left = [
        (cx - 160, cy - 15),
        (cx - 100, cy - 10),
        (cx - 250, cy + 30),
        (cx - 220, cy + 40),
    ]
    draw.polygon(wing_points_left, fill=(80, 90, 100))

    # Torn wing (right)
    wing_points_right = [
        (cx + 160, cy - 10),
        (cx + 100, cy - 5),
        (cx + 240, cy + 25),
        (cx + 210, cy + 35),
    ]
    draw.polygon(wing_points_right, fill=(80, 90, 100))

    # Debris scattered around
    rng = random.Random(7)
    for _ in range(15):
        dx = cx + rng.randint(-250, 250)
        dy = cy + rng.randint(10, 80)
        size = rng.randint(4, 15)
        draw.rectangle([dx, dy, dx + size, dy + size // 2], fill=(110, 120, 130))


def draw_whiteout_effect(draw: ImageDraw, width: int, height: int) -> None:
    """Draw whiteout wind/snow streaks across the image."""
    rng = random.Random(21)

    # Horizontal wind streaks
    for _ in range(60):
        x = rng.randint(0, width)
        y = rng.randint(0, int(height * 0.6))
        length = rng.randint(30, 150)
        alpha = rng.randint(30, 80)
        draw.line([(x, y), (x + length, y)], fill=(255, 255, 255, alpha), width=rng.randint(1, 3))

    # Snow particle dots
    for _ in range(200):
        x = rng.randint(0, width)
        y = rng.randint(0, int(height * 0.7))
        size = rng.randint(1, 3)
        alpha = rng.randint(40, 120)
        draw.ellipse([x, y, x + size, y + size], fill=(255, 255, 255, alpha))


def draw_mountains(draw: ImageDraw, width: int, height: int) -> None:
    """Draw distant mountains on the horizon."""
    rng = random.Random(42)
    mountain_color = (150, 170, 195)
    snow_color = (210, 220, 235)
    base_y = int(height * 0.38)

    for _ in range(5):
        mx = rng.randint(100, width - 100)
        mh = rng.randint(80, 180)
        mw = rng.randint(120, 250)

        # Mountain shape
        points = [(mx - mw, base_y), (mx, base_y - mh), (mx + mw, base_y)]
        draw.polygon(points, fill=mountain_color)

        # Snow cap
        cap_w = mw // 3
        cap_h = mh // 4
        cap_points = [
            (mx - cap_w, base_y - mh + cap_h),
            (mx, base_y - mh),
            (mx + cap_w, base_y - mh + cap_h),
        ]
        draw.polygon(cap_points, fill=snow_color)


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark title panel at the bottom of the cover with white text."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark semi-transparent rectangle
    draw.rectangle([(0, panel_top), (width, height)], fill=(15, 25, 45, 220))

    # Add a subtle frost line at top of panel
    draw.line([(0, panel_top), (width, panel_top)], fill=(180, 200, 225), width=2)

    # Title text
    title = "The Bitter\nWind"
    title_font_size = 76
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered, white
    lines = title.split("\n")
    y_offset = panel_top + 80
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 0
        tx = (width - tw) // 2
        draw.text((tx, y_offset), line, fill=(255, 255, 255), font=title_font)
        y_offset += 95

    # Genre tag
    genre_text = "An Arctic Survival Novel"
    genre_font_size = 22
    try:
        genre_font = ImageFont.truetype(str(font_paths["small"]), genre_font_size)
    except Exception:
        genre_font = ImageFont.load_default()

    try:
        gbbox = draw.textbbox((0, 0), genre_text, font=genre_font)
        gw = gbbox[2] - gbbox[0]
    except Exception:
        gw = 0
    gx = (width - gw) // 2
    gy = y_offset + 15
    draw.text((gx, gy), genre_text, fill=(180, 200, 225), font=genre_font)

    # Author name
    author = "Barış Kısır"
    author_font_size = 34
    try:
        author_font = ImageFont.truetype(str(font_paths["author"]), author_font_size)
    except Exception:
        author_font = ImageFont.load_default()

    try:
        abbox = draw.textbbox((0, 0), author, font=author_font)
        aw = abbox[2] - abbox[0]
    except Exception:
        aw = 0
    ax = (width - aw) // 2
    ay = gy + 45
    draw.text((ax, ay), author, fill=(200, 215, 235), font=author_font)

    # Thin decorative line under author
    line_y = ay + 35
    draw.line([(width // 2 - 60, line_y), (width // 2 + 60, line_y)], fill=(120, 150, 190), width=1)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Bitter Wind")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Distant mountains
    draw_mountains(draw, WIDTH, HEIGHT)

    # Step 3: Ice cap surface
    draw_ice_cap(draw, WIDTH, HEIGHT)

    # Step 4: Crevasses in the ice
    draw_crevasses(draw, WIDTH, HEIGHT)

    # Step 5: Crashed plane
    draw_crashed_plane(draw, WIDTH, HEIGHT)

    # Step 6: Whiteout wind/snow effect
    draw_whiteout_effect(draw, WIDTH, HEIGHT)

    # Step 7: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
        "small": str(FONTS_DIR / "arial.ttf"),
    }
    draw_title_panel(draw, WIDTH, HEIGHT, font_paths)

    # Soften the image slightly
    img = img.filter(ImageFilter.SMOOTH)

    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    metadata_path = rel(args.metadata)
    output_path = rel(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    create_cover(metadata_path, output_path)


if __name__ == "__main__":
    main()