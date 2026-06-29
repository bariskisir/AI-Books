#!/usr/bin/env python3
"""Generate a 1600x2560 PNG book cover for The Ferryman's Daughter."""

from __future__ import annotations

import argparse
import json
import math
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


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def draw_gradient(draw: ImageDraw, colors: list[tuple[int, int, int]]) -> None:
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        segments = len(colors) - 1
        seg = min(int(ratio * segments), segments - 1)
        local = (ratio * segments) - seg
        r = int(colors[seg][0] * (1 - local) + colors[seg + 1][0] * local)
        g = int(colors[seg][1] * (1 - local) + colors[seg + 1][1] * local)
        b = int(colors[seg][2] * (1 - local) + colors[seg + 1][2] * local)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def draw_star_field(draw: ImageDraw) -> None:
    """Draw scattered stars in the upper portion of the sky."""
    import random
    random.seed(42)
    for _ in range(120):
        x = random.randint(0, WIDTH)
        y = random.randint(0, 600)
        size = random.randint(1, 3)
        alpha = random.randint(80, 200)
        draw.ellipse([x, y, x + size, y + size], fill=(200, 200, 220, alpha))


def draw_moon(draw: ImageDraw) -> None:
    """Draw a crescent moon in the upper right."""
    cx, cy = 1300, 150
    r = 60
    # Full moon base
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(180, 185, 195, 60))
    # Crescent by drawing a slightly offset darker circle over it
    draw.ellipse([cx + 15, cy - r - 10, cx + r + 30, cy + r + 10], fill=(40, 42, 55, 255))
    # Glow
    for gr in range(r + 20, r, -2):
        alpha = max(0, int(40 * (1 - (gr - r) / 20)))
        draw.ellipse([cx - gr, cy - gr, cx + gr, cy + gr], fill=(150, 160, 180, alpha))


def draw_styx_shore(draw: ImageDraw) -> None:
    """Draw the near shore of the Styx with asphodel stalks."""
    # Shore bank
    shore_y = 1100
    for y in range(shore_y, shore_y + 80):
        ratio = (y - shore_y) / 80
        r = int(20 + ratio * 15)
        g = int(18 + ratio * 12)
        b = int(30 + ratio * 20)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Asphodel stalks on the shore
    stalk_color = (55, 60, 65)
    for sx in range(60, WIDTH, 40):
        sh = int(40 + (sx % 7) * 8)
        draw.line([(sx, shore_y - 5), (sx, shore_y - sh)], fill=stalk_color, width=2)
        # Small pale flowers at top
        for fx in [-4, 0, 4]:
            draw.ellipse([sx + fx - 2, shore_y - sh - 4, sx + fx + 2, shore_y - sh + 2], fill=(70, 70, 80))


def draw_styx_river(draw: ImageDraw) -> None:
    """Draw the River Styx with dark flowing water."""
    # River surface
    for y in range(1180, 1600):
        ratio = (y - 1180) / 420
        r = int(10 + ratio * 8)
        g = int(10 + ratio * 6)
        b = int(25 + ratio * 15)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # River ripples/current lines
    for ry in range(1200, 1580, 12):
        offset = (ry * 7) % 100
        line_color = (25, 25, 45, 80)
        for rx in range(offset, WIDTH, 120):
            rw = 60 + (ry % 40)
            draw.line([(rx, ry), (rx + rw, ry)], fill=line_color, width=1)

    # Silver highlights on water
    for hy in range(1220, 1560, 20):
        hx = (hy * 13) % WIDTH
        draw.line([(hx, hy), (hx + 30, hy)], fill=(60, 65, 90, 100), width=1)


def draw_ferry(draw: ImageDraw) -> None:
    """Draw Charon's skeletal ferry boat on the Styx."""
    # Hull
    hull_color = (35, 30, 20)
    hull_top = 1350
    ferry_center = 700
    # Bottom curve of hull
    points = []
    for i in range(21):
        t = i / 20
        x = ferry_center - 160 + t * 320
        y = hull_top + 40 * math.sin(t * math.pi)
        points.append((x, y))
    # Top edge
    points.append((ferry_center + 160, hull_top - 10))
    points.append((ferry_center - 160, hull_top - 10))
    draw.polygon(points, fill=hull_color, outline=(50, 45, 35))

    # Skeletal ribs of the ferry
    rib_color = (55, 50, 40)
    for rib in range(-120, 121, 30):
        rx = ferry_center + rib
        draw.arc([rx - 8, hull_top - 25, rx + 8, hull_top + 5], 0, 180, fill=rib_color, width=2)
        draw.line([(rx, hull_top - 25), (rx, hull_top + 5)], fill=rib_color, width=1)

    # Lantern on the ferry
    lantern_x = ferry_center + 80
    lantern_y = hull_top - 45
    draw.rectangle([lantern_x - 6, lantern_y - 10, lantern_x + 6, lantern_y + 5], fill=(40, 38, 30))
    # Lantern glow
    for gr in range(25, 5, -2):
        alpha = int(40 * (1 - gr / 25))
        draw.ellipse([lantern_x - gr, lantern_y - gr, lantern_x + gr, lantern_y + gr], fill=(180, 150, 80, alpha))
    # Lantern flame
    draw.ellipse([lantern_x - 3, lantern_y - 6, lantern_x + 3, lantern_y + 1], fill=(220, 180, 60))

    # Ferryman's pole (standing upright in boat)
    draw.line([(ferry_center - 40, hull_top - 70), (ferry_center - 40, hull_top + 20)], fill=(60, 55, 40), width=4)


def draw_far_shore(draw: ImageDraw) -> None:
    """Draw the far shore of the Styx with torches."""
    # Distant shore
    for y in range(1050, 1100):
        ratio = (y - 1050) / 50
        r = int(30 + ratio * 10)
        g = int(25 + ratio * 8)
        b = int(40 + ratio * 10)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Torches on far shore
    torch_positions = [180, 400, 650, 900, 1150, 1400]
    for tx in torch_positions:
        # Torch pole
        draw.line([(tx, 1050), (tx, 980)], fill=(50, 45, 35), width=3)
        # Flame glow
        for fr in range(30, 5, -3):
            alpha = int(50 * (1 - fr / 30))
            draw.ellipse([tx - fr, 970 - fr // 2, tx + fr, 970 + fr // 2], fill=(200, 120, 40, alpha))
        # Flame core
        draw.ellipse([tx - 5, 968, tx + 5, 980], fill=(240, 180, 60))
        draw.ellipse([tx - 3, 972, tx + 3, 978], fill=(255, 220, 100))


def draw_skull_motif(draw: ImageDraw) -> None:
    """Draw a subtle skull motif in the sky."""
    cx, cy = 300, 350
    # Eyes
    draw.ellipse([cx - 20, cy - 12, cx - 5, cy + 3], fill=(35, 35, 50, 180))
    draw.ellipse([cx + 5, cy - 12, cx + 20, cy + 3], fill=(35, 35, 50, 180))
    # Nose cavity
    draw.polygon([(cx - 5, cy + 8), (cx + 5, cy + 8), (cx, cy + 20)], fill=(35, 35, 50, 180))
    # Mouth
    draw.rectangle([cx - 18, cy + 24, cx + 18, cy + 32], fill=(35, 35, 50, 150))


def draw_title_panel(draw: ImageDraw) -> None:
    """Draw the bottom title panel — dark panel with white text."""
    # Dark gradient panel from y=1920 to bottom
    panel_color_top = (25, 23, 35)
    panel_color_bot = (15, 13, 22)

    for y in range(TITLE_PANEL_Y, HEIGHT):
        ratio = (y - TITLE_PANEL_Y) / (HEIGHT - TITLE_PANEL_Y)
        r = int(panel_color_top[0] * (1 - ratio) + panel_color_bot[0] * ratio)
        g = int(panel_color_top[1] * (1 - ratio) + panel_color_bot[1] * ratio)
        b = int(panel_color_top[2] * (1 - ratio) + panel_color_bot[2] * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Silver decorative line at top of panel
    draw.line([(150, TITLE_PANEL_Y + 15), (WIDTH - 150, TITLE_PANEL_Y + 15)], fill=(160, 160, 180), width=2)
    draw.line([(200, TITLE_PANEL_Y + 20), (WIDTH - 200, TITLE_PANEL_Y + 20)], fill=(100, 100, 120), width=1)

    # Small skull decorations on decorative line
    for sx in [250, WIDTH - 250]:
        draw.ellipse([sx - 4, TITLE_PANEL_Y + 11, sx + 4, TITLE_PANEL_Y + 19], fill=(160, 160, 180))

    # Title
    title_text = "The Ferryman's\nDaughter"
    font_size = 100
    try:
        title_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", font_size)
    except (IOError, OSError):
        title_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)

    # Draw title — WHITE text centered in the dark panel
    lines = title_text.split("\n")
    total_height = 0
    line_heights = []
    for line in lines:
        bbox = title_font.getbbox(line)
        lh = bbox[3] - bbox[1]
        line_heights.append(lh)
        total_height += lh + 10

    title_y_start = TITLE_PANEL_Y + 320 - total_height // 2
    for i, line in enumerate(lines):
        bbox = title_font.getbbox(line)
        tw = bbox[2] - bbox[0]
        tx = (WIDTH - tw) // 2
        ty = title_y_start + sum(line_heights[:i]) + i * 10
        draw.text((tx, ty), line, fill=(255, 255, 255), font=title_font)

    # Author name
    author_text = "Barış Kısır"
    try:
        author_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 36)
    except (IOError, OSError):
        author_font = ImageFont.load_default()

    bbox_a = author_font.getbbox(author_text)
    aw = bbox_a[2] - bbox_a[0]
    ax = (WIDTH - aw) // 2
    ay = TITLE_PANEL_Y + 340 + total_height
    draw.text((ax, ay), author_text, fill=(200, 200, 210), font=author_font)

    # Genre line
    genre_text = "Mythic Fantasy"
    try:
        small_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 22)
    except (IOError, OSError):
        small_font = ImageFont.load_default()

    bbox_g = small_font.getbbox(genre_text)
    gw = bbox_g[2] - bbox_g[0]
    gx = (WIDTH - gw) // 2
    gy = ay + 45
    draw.text((gx, gy), genre_text, fill=(140, 140, 155), font=small_font)

    # Bottom decorative line
    draw.line([(300, gy + 40), (WIDTH - 300, gy + 40)], fill=(100, 100, 120), width=1)


def create_cover() -> Image.Image:
    """Create the full cover image."""
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # 1. Gradient background: deep black-blue to dark purple
    draw_gradient(draw, [(10, 8, 20), (20, 18, 35), (30, 25, 45), (15, 12, 28)])

    # 2. Star field in upper portion
    draw_star_field(draw)

    # 3. Crescent moon
    draw_moon(draw)

    # 4. Subtle skull motif in sky
    draw_skull_motif(draw)

    # 5. Far shore with torches
    draw_far_shore(draw)

    # 6. River Styx
    draw_styx_river(draw)

    # 7. Near shore with asphodel
    draw_styx_shore(draw)

    # 8. The skeletal ferry
    draw_ferry(draw)

    # 9. Title panel at bottom
    draw_title_panel(draw)

    # Soft sharpen filter for print-like quality
    img = img.filter(ImageFilter.SMOOTH)

    return img



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    model = metadata.get("model", "")
    output_path = args.out

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cover = create_cover()
    _draw_standard_cover_title_panel(cover, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    cover.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")


if __name__ == "__main__":
    main()