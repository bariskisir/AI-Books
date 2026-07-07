#!/usr/bin/env python3
"""Cover: The Last Lighthouse — Solitary white lighthouse on rocky island, bright beam cutting across dark swirling sea."""

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
    """Steel gray to storm dark gradient for dystopian coastal feel."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((180, 185, 190), (120, 125, 130), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((120, 125, 130), (60, 65, 70), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((60, 65, 70), (15, 18, 22), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_sea(draw: ImageDraw, width: int, height: int) -> None:
    """Draw rough sea with whitecaps at the base of the lighthouse."""
    sea_top = int(height * 0.65)
    rng = random.Random(13)

    for y in range(sea_top, height):
        t = (y - sea_top) / (height - sea_top)
        if t < 0.3:
            c = lerp_color((40, 45, 55), (25, 30, 40), t / 0.3)
        else:
            c = lerp_color((25, 30, 40), (10, 12, 18), (t - 0.3) / 0.7)
        draw.line([(0, y), (width, y)], fill=c)

    # Whitecaps
    for _ in range(60):
        wx = rng.randint(0, width)
        wy = sea_top + rng.randint(0, int(height * 0.25))
        wlen = rng.randint(10, 40)
        wh = rng.randint(1, 3)
        draw.line([(wx, wy), (wx + wlen, wy)], fill=(220, 225, 230, 120), width=wh)

    # Foam line at shore
    shore_y = int(height * 0.62)
    for i in range(width):
        offset = int(math.sin(i * 0.05) * 3 + math.sin(i * 0.02) * 5)
        draw.line(
            [(i, shore_y + offset), (i, shore_y + offset + rng.randint(2, 5))],
            fill=(240, 245, 250, 100),
        )


def draw_lighthouse(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the lighthouse standing against the storm."""
    base_x = width // 2
    base_y = int(height * 0.68)
    tower_w = 60
    tower_h = int(height * 0.55)
    top_y = base_y - tower_h

    # Main tower body (slightly tapered)
    for y in range(top_y, base_y):
        t = (y - top_y) / tower_h
        tw = int(tower_w * (1 - t * 0.3))
        x1 = base_x - tw // 2
        x2 = base_x + tw // 2
        # Shadow side
        shade = int(40 * t)
        color = (180 - shade, 185 - shade, 190 - shade)
        draw.line([(x1, y), (x2, y)], fill=color)

    # Red stripes on lighthouse
    stripe_y = base_y - int(tower_h * 0.25)
    stripe_h = int(tower_h * 0.06)
    for s in range(3):
        sy = stripe_y - s * int(tower_h * 0.18)
        t = (sy - top_y) / tower_h
        tw = int(tower_w * (1 - t * 0.3))
        x1 = base_x - tw // 2
        x2 = base_x + tw // 2
        for y in range(sy, sy + stripe_h):
            draw.line([(x1, y), (x2, y)], fill=(160, 40, 40))

    # Lantern room
    lantern_top = top_y - int(height * 0.03)
    lantern_bottom = top_y
    lantern_w = int(tower_w * 0.8)
    for y in range(lantern_top, lantern_bottom):
        x1 = base_x - lantern_w // 2
        x2 = base_x + lantern_w // 2
        draw.line([(x1, y), (x2, y)], fill=(40, 42, 45))

    # Lantern glass (glowing)
    glass_top = lantern_top + int(height * 0.01)
    glass_bottom = lantern_bottom - int(height * 0.005)
    glass_w = int(lantern_w * 0.6)
    for y in range(glass_top, glass_bottom):
        x1 = base_x - glass_w // 2
        x2 = base_x + glass_w // 2
        glow = random.randint(200, 255)
        draw.line([(x1, y), (x2, y)], fill=(glow, glow - 40, 50, 200))

    # Light beam (triangle extending right)
    beam_center = (glass_top + glass_bottom) // 2
    beam_points = [
        (base_x + glass_w // 2, beam_center - 5),
        (base_x + glass_w // 2, beam_center + 5),
        (width + 100, beam_center - int(height * 0.3)),
        (width + 100, beam_center + int(height * 0.3)),
    ]
    draw.polygon(beam_points, fill=(255, 220, 100, 30))

    # Second beam to left
    beam_points2 = [
        (base_x - glass_w // 2, beam_center - 5),
        (base_x - glass_w // 2, beam_center + 5),
        (-100, beam_center - int(height * 0.2)),
        (-100, beam_center + int(height * 0.2)),
    ]
    draw.polygon(beam_points2, fill=(255, 220, 100, 20))

    # Lighthouse base/platform
    for y in range(base_y, base_y + int(height * 0.02)):
        x1 = base_x - int(tower_w * 0.6)
        x2 = base_x + int(tower_w * 0.6)
        draw.line([(x1, y), (x2, y)], fill=(50, 52, 55))


def draw_storm_clouds(draw: ImageDraw, width: int, height: int) -> None:
    """Draw storm clouds gathering above the lighthouse."""
    rng = random.Random(17)
    for _ in range(40):
        cx = rng.randint(0, width)
        cy = rng.randint(0, int(height * 0.25))
        rx = rng.randint(100, 300)
        ry = rng.randint(30, 80)
        shade = rng.randint(30, 80)
        draw.ellipse(
            [cx - rx, cy - ry, cx + rx, cy + ry],
            fill=(shade, shade + 5, shade + 10, 150),
        )

    # Lightning bolt
    lx = rng.randint(width // 3, width * 2 // 3)
    ly = rng.randint(0, int(height * 0.15))
    points = [(lx, ly)]
    for i in range(6):
        lx += rng.randint(-30, 30)
        ly += rng.randint(30, 80)
        points.append((lx, ly))
    draw.line(points, fill=(255, 255, 200), width=3)
    # Glow around lightning
    draw.line(points, fill=(255, 255, 200, 60), width=8)


def draw_rising_water(draw: ImageDraw, width: int, height: int) -> None:
    """Draw submerged structures — rooftops, poles — emerging from the water."""
    rng = random.Random(23)

    # Submerged rooftops
    for _ in range(5):
        rx = rng.randint(100, width - 100)
        ry = int(height * 0.62) + rng.randint(-20, 30)
        rw = rng.randint(40, 80)
        draw.polygon(
            [(rx - rw // 2, ry), (rx, ry - 20), (rx + rw // 2, ry)],
            fill=(50, 45, 40, 120),
        )
        draw.rectangle([rx - rw // 4, ry, rx + rw // 4, ry + 10], fill=(50, 45, 40, 120))

    # Sunken telephone poles
    for _ in range(3):
        px = rng.randint(80, width - 80)
        py = int(height * 0.65) + rng.randint(-10, 20)
        draw.line(
            [(px, py), (px, py - rng.randint(30, 60))],
            fill=(40, 35, 30),
            width=4,
        )

    # Cross arm on pole
    for _ in range(2):
        px = rng.randint(80, width - 80)
        py = int(height * 0.62) + rng.randint(-10, 10)
        if rng.random() < 0.5:
            draw.line(
                [(px - 15, py), (px + 15, py)],
                fill=(40, 35, 30),
                width=3,
            )


def draw_lone_figure(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a small lone figure on the rocks at the base of the lighthouse."""
    fig_x = width // 2 - 100
    fig_y = int(height * 0.65)

    # Body
    draw.ellipse([fig_x - 8, fig_y - 20, fig_x + 8, fig_y + 10], fill=(15, 15, 18))
    # Head
    draw.ellipse([fig_x - 5, fig_y - 28, fig_x + 5, fig_y - 18], fill=(25, 25, 30))
    # Coat
    draw.polygon(
        [(fig_x - 8, fig_y - 5), (fig_x - 12, fig_y + 15), (fig_x + 12, fig_y + 15), (fig_x + 8, fig_y - 5)],
        fill=(20, 20, 25),
    )


def draw_rocks(draw: ImageDraw, width: int, height: int) -> None:
    """Draw rocky shoreline at the base of the lighthouse."""
    rng = random.Random(31)
    shore_y = int(height * 0.62)
    for _ in range(30):
        rx = rng.randint(100, width - 100)
        ry = shore_y + rng.randint(-5, 20)
        rw = rng.randint(15, 50)
        rh = rng.randint(10, 25)
        shade = rng.randint(40, 80)
        draw.ellipse([rx - rw // 2, ry, rx + rw // 2, ry + rh], fill=(shade, shade + 2, shade + 5))


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom of the cover with white text."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark semi-transparent
    for y in range(panel_top, height):
        t = (y - panel_top) / (height - panel_top)
        shade = int(15 + t * 10)
        draw.line([(0, y), (width, y)], fill=(shade, shade + 1, shade + 3, 240))

    # Top border line
    for i in range(3):
        draw.line([(0, panel_top + i), (width, panel_top + i)], fill=(100, 110, 120, 200), width=1)

    # Title text
    title = "The Last\nLighthouse"
    title_font_size = 80
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered in white
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

    # Subtitle text
    subtitle = "A Dystopian Survival Novel"
    subtitle_font_size = 26
    try:
        subtitle_font = ImageFont.truetype(str(font_paths["small"]), subtitle_font_size)
    except Exception:
        subtitle_font = ImageFont.load_default()

    try:
        sbbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        sw = sbbox[2] - sbbox[0]
    except Exception:
        sw = 0
    sx = (width - sw) // 2
    draw.text((sx, y_offset + 10), subtitle, fill=(180, 185, 190), font=subtitle_font)

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
    ay = y_offset + 70
    draw.text((ax, ay), author, fill=(200, 205, 210), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Last Lighthouse")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    rng = __import__("random").Random(19)

    # Gray dawn sky gradient
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(120 + 40 * t)
        g = int(125 + 35 * t)
        b = int(130 + 30 * t)
        draw.line([(0, y), (WIDTH, y)], fill=(max(0, int(r)), max(0, int(g)), max(0, int(b)), 255))

    # Storm clouds
    for _ in range(30):
        cx = int(rng.random() * WIDTH)
        cy = int(rng.random() * int(HEIGHT * 0.25))
        rx = int(100 + rng.random() * 250)
        ry = int(30 + rng.random() * 70)
        shade = rng.randint(40, 80)
        draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(shade, shade + 3, shade + 6, 150))

    # Dark swirling sea
    sea_top = int(HEIGHT * 0.62)
    for y in range(sea_top, HEIGHT):
        t = (y - sea_top) / (HEIGHT - sea_top)
        r = int(30 - 20 * t)
        g = int(35 - 25 * t)
        b = int(45 - 30 * t)
        draw.line([(0, y), (WIDTH, y)], fill=(max(0, r), max(0, g), max(0, b), 255))
    # Sea swirls
    for y in range(sea_top + 20, int(HEIGHT * 0.85), 30):
        for x in range(0, WIDTH, 40):
            off = int(8 * __import__("math").sin((x + y) * 0.03))
            draw.line([(x, y + off), (x + 30, y + off)], fill=(50, 60, 75, 60), width=2)

    # Rocky island
    for i in range(20):
        rx = WIDTH // 2 - 80 + rng.randint(0, 160)
        ry = sea_top - 30 + rng.randint(-10, 20)
        rs = rng.randint(20, 60)
        draw.ellipse([rx - rs // 2, ry, rx + rs // 2, ry + rs // 2], fill=(45, 42, 38))
    for i in range(15):
        rx = WIDTH // 2 - 60 + rng.randint(0, 120)
        ry = sea_top + rng.randint(5, 40)
        rs = rng.randint(10, 30)
        draw.ellipse([rx - rs // 2, ry, rx + rs // 2, ry + rs // 2], fill=(35, 32, 28))

    # Solitary white lighthouse
    lx, ly = WIDTH // 2, sea_top - 350
    # Tapered tower
    for y in range(ly, sea_top - 20):
        t = (y - ly) / (sea_top - 20 - ly)
        tw = int(50 * (1 + t * 0.6))
        color = (200 - int(30 * t), 205 - int(30 * t), 210 - int(30 * t))
        draw.line([(lx - tw // 2, y), (lx + tw // 2, y)], fill=color)
    # Red stripes
    stripe_h = 25
    for s in range(3):
        stripe_y = ly + 80 + s * 90
        t = (stripe_y - ly) / (sea_top - 20 - ly)
        tw = int(50 * (1 + t * 0.6))
        for y in range(stripe_y, stripe_y + stripe_h):
            draw.line([(lx - tw // 2, y), (lx + tw // 2, y)], fill=(160, 40, 40))

    # Lantern room
    lr_top = ly - 30
    lr_bot = ly
    for y in range(lr_top, lr_bot):
        tw = int(40 * (1 + ((y - lr_top) / 30) * 0.3))
        draw.line([(lx - tw // 2, y), (lx + tw // 2, y)], fill=(35, 38, 42))
    # Lantern glass (glowing)
    for y in range(lr_top + 8, lr_bot - 3):
        tw = int(30 * (1 + ((y - lr_top) / 30) * 0.3))
        glow_b = rng.randint(200, 255)
        draw.line([(lx - tw // 2, y), (lx + tw // 2, y)], fill=(glow_b, glow_b - 30, 50, 200))

    # Light beam cutting across sea
    beam_center = (lr_top + lr_bot) // 2
    beam = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam)
    bd.polygon([(lx + 15, beam_center), (WIDTH + 100, beam_center - 400), (WIDTH + 100, beam_center + 400)], fill=(255, 230, 150, 25))
    bd.polygon([(lx - 15, beam_center), (-100, beam_center - 300), (-100, beam_center + 300)], fill=(255, 230, 150, 15))
    beam = beam.filter(ImageFilter.GaussianBlur(12))
    img = Image.alpha_composite(img, beam)
    draw = ImageDraw.Draw(img, "RGBA")

    # Foam at shore
    shore_y = sea_top
    for i in range(WIDTH):
        off = int(__import__("math").sin(i * 0.05) * 3 + __import__("math").sin(i * 0.02) * 5)
        draw.line([(i, shore_y + off), (i, shore_y + off + rng.randint(2, 4))], fill=(240, 245, 250, 80))

    # Sea whitecaps
    for _ in range(40):
        wx = int(rng.random() * WIDTH)
        wy = sea_top + rng.randint(0, int(HEIGHT * 0.2))
        wl = rng.randint(10, 30)
        draw.line([(wx, wy), (wx + wl, wy)], fill=(220, 225, 230, rng.randint(60, 120)), width=2)

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