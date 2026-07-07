#!/usr/bin/env python3
"""Cover: The Lighthouse Keeper's Wife — Stormy Scottish coast, white lighthouse on dark cliff with golden beams, small rowboat, storm gray/cliff black/beacon gold."""

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
    """Storm gray to dark slate gradient for a Scottish coastal feel."""
    for y in range(height):
        if y < height * 0.3:
            t = y / (height * 0.3)
            c = lerp_color((100, 105, 115), (75, 80, 90), t)
        elif y < height * 0.6:
            t = (y - height * 0.3) / (height * 0.3)
            c = lerp_color((75, 80, 90), (50, 55, 65), t)
        else:
            t = (y - height * 0.6) / (height * 0.4)
            c = lerp_color((50, 55, 65), (20, 25, 35), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_storm_clouds(draw: ImageDraw, width: int, height: int) -> None:
    """Draw layered storm clouds overhead."""
    rng = random.Random(19)
    for _ in range(50):
        cx = rng.randint(0, width)
        cy = rng.randint(0, int(height * 0.20))
        rx = rng.randint(120, 350)
        ry = rng.randint(30, 70)
        shade = rng.randint(35, 80)
        draw.ellipse(
            [cx - rx, cy - ry, cx + rx, cy + ry],
            fill=(shade, shade + 3, shade + 8, 180),
        )
    # Lighter clouds in the distance
    for _ in range(15):
        cx = rng.randint(0, width)
        cy = rng.randint(int(height * 0.15), int(height * 0.28))
        rx = rng.randint(80, 200)
        ry = rng.randint(20, 40)
        shade = rng.randint(100, 140)
        draw.ellipse(
            [cx - rx, cy - ry, cx + rx, cy + ry],
            fill=(shade, shade + 5, shade + 10, 100),
        )


def draw_sea(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a stormy sea with whitecaps and foam."""
    sea_top = int(height * 0.55)
    rng = random.Random(17)

    for y in range(sea_top, height):
        t = (y - sea_top) / (height - sea_top)
        if t < 0.3:
            c = lerp_color((45, 50, 60), (30, 35, 45), t / 0.3)
        elif t < 0.6:
            c = lerp_color((30, 35, 45), (20, 25, 35), (t - 0.3) / 0.3)
        else:
            c = lerp_color((20, 25, 35), (12, 15, 22), (t - 0.6) / 0.4)
        draw.line([(0, y), (width, y)], fill=c)

    # Whitecaps
    for _ in range(80):
        wx = rng.randint(0, width)
        wy = sea_top + rng.randint(0, int(height * 0.2))
        wlen = rng.randint(10, 50)
        wh = rng.randint(1, 3)
        alpha = rng.randint(100, 180)
        draw.line([(wx, wy), (wx + wlen, wy)], fill=(230, 235, 240, alpha), width=wh)

    # Foam along the cliff edge
    shore_y = int(height * 0.52)
    for i in range(width):
        offset = int(math.sin(i * 0.03) * 4 + math.sin(i * 0.015) * 6 + rng.randint(-2, 2))
        if 200 < i < width - 200:
            draw.line(
                [(i, shore_y + offset), (i, shore_y + offset + rng.randint(2, 6))],
                fill=(240, 245, 250, 80),
            )


def draw_cliff(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the cliff that supports the lighthouse."""
    rng = random.Random(23)
    cliff_top = int(height * 0.50)
    cliff_base = int(height * 0.55)

    # Cliff face
    for y in range(cliff_top, cliff_base):
        t = (y - cliff_top) / (cliff_base - cliff_top)
        shade = int(40 + t * 20)
        # Irregular left edge
        left_edge = 100 + int(math.sin(y * 0.05) * 30 + math.sin(y * 0.02) * 20) + rng.randint(-5, 5)
        right_edge = width - 100 + int(math.sin(y * 0.03) * 20 + math.cos(y * 0.04) * 15) + rng.randint(-5, 5)
        draw.line([(left_edge, y), (right_edge, y)], fill=(shade, shade + 2, shade + 5))

    # Cliff top grass
    grass_line = cliff_top - 2
    for i in range(width):
        if i % 3 == 0:
            gh = rng.randint(1, 6)
            draw.line(
                [(i, grass_line), (i + rng.randint(-2, 2), grass_line - gh)],
                fill=(35, 50, 30),
                width=1,
            )


def draw_lighthouse(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the lighthouse on the cliff."""
    rng = random.Random(29)
    base_x = width // 2
    base_y = int(height * 0.50)
    tower_w = 55
    tower_h = int(height * 0.48)
    top_y = base_y - tower_h

    # Main tower
    for y in range(top_y, base_y):
        t = (y - top_y) / tower_h
        tw = int(tower_w * (1 - t * 0.25))
        x1 = base_x - tw // 2
        x2 = base_x + tw // 2
        shade = int(30 * t)
        # Darker on left side for shadow
        for x in range(x1, x2 + 1):
            shadow_factor = 1.0 - ((x - x1) / (x2 - x1)) * 0.3
            r = int((180 - shade) * shadow_factor)
            g = int((185 - shade) * shadow_factor)
            b = int((192 - shade) * shadow_factor)
            draw.point((x, y), fill=(r, g, b))

    # Red stripe near top
    stripe_y = base_y - int(tower_h * 0.22)
    stripe_h = int(tower_h * 0.05)
    for s in range(2):
        sy = stripe_y - s * int(tower_h * 0.16)
        t = (sy - top_y) / tower_h
        tw = int(tower_w * (1 - t * 0.25))
        x1 = base_x - tw // 2
        x2 = base_x + tw // 2
        for y in range(sy, sy + stripe_h):
            draw.line([(x1, y), (x2, y)], fill=(170, 50, 50))

    # Lantern room
    lantern_top = top_y - int(height * 0.04)
    lantern_bottom = top_y
    lantern_w = int(tower_w * 0.85)
    for y in range(lantern_top, lantern_bottom):
        x1 = base_x - lantern_w // 2
        x2 = base_x + lantern_w // 2
        draw.line([(x1, y), (x2, y)], fill=(35, 38, 42))

    # Lantern glass with warm golden glow
    glass_top = lantern_top + int(height * 0.012)
    glass_bottom = lantern_bottom - int(height * 0.008)
    glass_w = int(lantern_w * 0.65)
    for y in range(glass_top, glass_bottom):
        x1 = base_x - glass_w // 2
        x2 = base_x + glass_w // 2
        glow = rng.randint(220, 255)
        draw.line([(x1, y), (x2, y)], fill=(glow, glow - 60, 30, 220))

    # Golden light beams radiating outward
    beam_center = (glass_top + glass_bottom) // 2
    # Right beam
    beam_points = [
        (base_x + glass_w // 2, beam_center - 8),
        (base_x + glass_w // 2, beam_center + 8),
        (width + 100, beam_center - int(height * 0.35)),
        (width + 100, beam_center + int(height * 0.35)),
    ]
    draw.polygon(beam_points, fill=(255, 200, 80, 25))

    # Left beam
    beam_points2 = [
        (base_x - glass_w // 2, beam_center - 8),
        (base_x - glass_w // 2, beam_center + 8),
        (-100, beam_center - int(height * 0.25)),
        (-100, beam_center + int(height * 0.25)),
    ]
    draw.polygon(beam_points2, fill=(255, 200, 80, 18))

    # Light halo around lantern
    halo_radius = int(lantern_w * 1.5)
    for r in range(halo_radius, 0, -1):
        alpha = int(15 * (1 - r / halo_radius))
        draw.ellipse(
            [base_x - r, beam_center - r, base_x + r, beam_center + r],
            outline=(255, 200, 80, alpha),
        )

    # Windows on tower
    window_positions = [
        base_y - int(tower_h * 0.35),
        base_y - int(tower_h * 0.55),
        base_y - int(tower_h * 0.75),
    ]
    for wy in window_positions:
        t = (wy - top_y) / tower_h
        tw = int(tower_w * (1 - t * 0.25))
        x1 = base_x - tw // 2
        x2 = base_x + tw // 2
        win_x = base_x
        win_w = 8
        win_h = 12
        # Warm window glow
        draw.rectangle(
            [win_x - win_w // 2, wy - win_h // 2, win_x + win_w // 2, wy + win_h // 2],
            fill=(255, 200, 80, 180),
        )
        # Window frame
        draw.rectangle(
            [win_x - win_w // 2, wy - win_h // 2, win_x + win_w // 2, wy + win_h // 2],
            outline=(40, 42, 45),
            width=1,
        )


def draw_rocks(draw: ImageDraw, width: int, height: int) -> None:
    """Draw jagged rocks at the base of the cliff."""
    rng = random.Random(31)
    cliff_base_y = int(height * 0.50)

    for _ in range(20):
        rx = rng.randint(80, width - 80)
        ry = cliff_base_y + rng.randint(-3, 12)
        rw = rng.randint(20, 60)
        rh = rng.randint(10, 30)
        shade = rng.randint(40, 75)
        # Irregular rock shape
        points = [
            (rx - rw // 2 + rng.randint(-5, 5), ry + rng.randint(0, 5)),
            (rx, ry - rh + rng.randint(-3, 3)),
            (rx + rw // 2 + rng.randint(-5, 5), ry + rng.randint(0, 5)),
            (rx + rw // 4 + rng.randint(-3, 3), ry + rh),
            (rx - rw // 4 + rng.randint(-3, 3), ry + rh),
        ]
        draw.polygon(points, fill=(shade, shade + 2, shade + 5))


def draw_figure(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a small female figure standing on the cliff looking at the lighthouse."""
    fig_x = width // 2 - 130
    fig_y = int(height * 0.48)

    # Dress/skirt (dark blue-gray)
    draw.polygon(
        [
            (fig_x - 6, fig_y),
            (fig_x - 12, fig_y + 20),
            (fig_x + 12, fig_y + 20),
            (fig_x + 6, fig_y),
        ],
        fill=(30, 35, 45),
    )
    # Torso (lighter for a shawl)
    draw.ellipse([fig_x - 6, fig_y - 18, fig_x + 6, fig_y + 2], fill=(45, 50, 60))
    # Head
    draw.ellipse([fig_x - 4, fig_y - 26, fig_x + 4, fig_y - 17], fill=(55, 50, 45))
    # Hair/bonnet
    draw.ellipse([fig_x - 5, fig_y - 28, fig_x + 5, fig_y - 22], fill=(25, 20, 20))


def draw_gulls(draw: ImageDraw, width: int, height: int) -> None:
    """Draw distant seabirds."""
    rng = random.Random(37)
    for _ in range(12):
        gx = rng.randint(100, width - 100)
        gy = rng.randint(int(height * 0.15), int(height * 0.35))
        span = rng.randint(8, 16)
        # Simple V shape for birds
        draw.line(
            [(gx - span, gy), (gx, gy - span // 2), (gx + span, gy)],
            fill=(40, 45, 50),
            width=1,
        )


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom of the cover with white text."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark gradient
    for y in range(panel_top, height):
        t = (y - panel_top) / (height - panel_top)
        shade = int(12 + t * 12)
        draw.line([(0, y), (width, y)], fill=(shade, shade + 1, shade + 3, 245))

    # Top accent line
    for i in range(2):
        draw.line([(0, panel_top + i), (width, panel_top + i)], fill=(180, 150, 80, 200), width=1)

    # Title text
    title = "The Lighthouse\nKeeper's Wife"
    title_font_size = 78
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered in white
    lines = title.split("\n")
    y_offset = panel_top + 70
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 0
        tx = (width - tw) // 2
        draw.text((tx, y_offset), line, fill=(255, 255, 255), font=title_font)
        y_offset += 100

    # Author name
    author = "Barış Kısır"
    author_font_size = 36
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
    ay = y_offset + 40
    draw.text((ax, ay), author, fill=(220, 200, 170), font=author_font)

    # Decorative line below author
    line_y = ay + 50
    line_w = 200
    draw.line(
        [(width // 2 - line_w // 2, line_y), (width // 2 + line_w // 2, line_y)],
        fill=(180, 150, 80, 150),
        width=1,
    )


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Storm clouds
    draw_storm_clouds(draw, WIDTH, HEIGHT)

    # Step 3: Sea
    draw_sea(draw, WIDTH, HEIGHT)

    # Step 4: Cliff
    draw_cliff(draw, WIDTH, HEIGHT)

    # Step 5: Rocks
    draw_rocks(draw, WIDTH, HEIGHT)

    # Step 6: Lighthouse
    draw_lighthouse(draw, WIDTH, HEIGHT)

    # Step 7: Figure
    draw_figure(draw, WIDTH, HEIGHT)

    # Step 8: Gulls
    draw_gulls(draw, WIDTH, HEIGHT)

    # Step 9: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
    }
    draw_title_panel(draw, WIDTH, HEIGHT, font_paths)

    # Soften slightly
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