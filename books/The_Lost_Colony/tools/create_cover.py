#!/usr/bin/env python3
"""Generate a 1600x2560 cover for The Lost Colony using PIL."""

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



WIDTH, HEIGHT = 1600, 2560
TITLE_PANEL_Y = 1920
TITLE_PANEL_H = HEIGHT - TITLE_PANEL_Y

FONT_DIR = Path("C:/Windows/Fonts")


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def draw_sky(draw: ImageDraw, width: int, height: int) -> None:
    """Gradient sky from muted blue-gray to pale taupe."""
    top = hex_to_rgb("#5C6B73")
    bottom = hex_to_rgb("#A8A89A")
    for y in range(height):
        r = top[0] + (bottom[0] - top[0]) * y // height
        g = top[1] + (bottom[1] - top[1]) * y // height
        b = top[2] + (bottom[2] - top[2]) * y // height
        draw.line([(0, y), (width, y)], fill=(r, g, b))


def draw_ocean(draw: ImageDraw, width: int, y_start: int, y_end: int) -> None:
    """Muted ocean gradient."""
    top = hex_to_rgb("#4A5D5C")
    bottom = hex_to_rgb("#2F403F")
    h = y_end - y_start
    for y in range(y_start, y_end):
        t = (y - y_start) / h
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        draw.line([(0, y), (width, y)], fill=(r, g, b))


def draw_ship(draw: ImageDraw, x: int, y: int) -> None:
    """Small ship silhouette on the horizon."""
    # Hull
    draw.polygon([(x - 12, y), (x + 12, y), (x + 8, y + 6), (x - 8, y + 6)], fill=(20, 20, 20))
    # Mast
    draw.line([(x, y), (x, y - 20)], fill=(20, 20, 20), width=2)
    # Sails
    draw.polygon([(x, y - 18), (x + 10, y - 4), (x, y - 4)], fill=(30, 30, 30))
    draw.polygon([(x, y - 18), (x - 8, y - 4), (x, y - 4)], fill=(25, 25, 25))
    # Flag
    draw.polygon([(x, y - 20), (x, y - 16), (x + 6, y - 18)], fill=(180, 50, 40))


def draw_palisade(draw: ImageDraw, x_base: int, y_base: int, count: int, height: int, spread: int) -> None:
    """Draw a wooden palisade fence."""
    for i in range(count):
        x = x_base + i * (spread // count)
        top = y_base - height - abs(i - count // 2) * 4
        draw.polygon(
            [(x - 3, y_base), (x + 3, y_base), (x + 2, top), (x - 2, top)],
            fill=(70, 55, 35),
        )
        # Highlight on each post
        draw.line([(x - 1, y_base), (x - 1, top)], fill=(90, 72, 48), width=1)


def draw_trees(draw: ImageDraw, x_base: int, y_base: int) -> None:
    """Draw a cluster of pine trees."""
    for i in range(8):
        x = x_base + i * 28 - 80
        y = y_base - 60
        h = 90 + abs(i - 4) * 15
        # Trunk
        draw.rectangle([x - 2, y + h - 20, x + 2, y + h], fill=(50, 35, 20))
        # Crown
        for layer in range(3):
            lw = 18 - layer * 4
            ly = y + layer * 18
            draw.polygon(
                [(x, ly), (x - lw, ly + 16), (x + lw, ly + 16)],
                fill=(30 + layer * 8, 55 + layer * 5, 25 + layer * 3),
            )


def draw_marsh(draw: ImageDraw, y_start: int, y_end: int, width: int) -> None:
    """Low marsh grass and sand along the bottom of the imagery section."""
    # Sand bar
    sand_band = y_end - 20
    for y in range(sand_band, y_end):
        t = (y - sand_band) / (y_end - sand_band)
        r = int(160 + (130 - 160) * t)
        g = int(140 + (110 - 140) * t)
        b = int(90 + (70 - 90) * t)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Marsh grass tufts
    for gx in range(0, width, 18):
        gh = 8 + (gx % 13)
        for blade in range(3):
            bx = gx + blade * 4
            draw.line(
                [(bx, sand_band), (bx - 2, sand_band - gh)],
                fill=(85, 95, 50),
                width=1,
            )


def draw_sun(draw: ImageDraw, cx: int, cy: int, radius: int) -> None:
    """Pale sun behind clouds."""
    for r in range(radius, 0, -1):
        alpha = max(0, 30 - (radius - r) * 2)
        draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            fill=(220, 210, 180, alpha),
        )


def draw_clouds(draw: ImageDraw, width: int, y_offset: int) -> None:
    """Diffuse horizontal cloud bands."""
    for i in range(6):
        cy = y_offset + i * 45 + (i % 3) * 10
        cw = 300 + i * 80
        for x in range(0, width, 6):
            dx = x / width
            offset_y = int(15 * (1 - abs(dx - 0.5) * 1.8))
            draw.rectangle(
                [x, cy - 4 + offset_y, x + 4, cy + 4 + offset_y],
                fill=(200, 195, 180, 40),
            )


def draw_seagulls(draw: ImageDraw) -> None:
    """A few distant bird shapes."""
    positions = [(320, 380), (360, 360), (700, 410), (1050, 370)]
    for x, y in positions:
        draw.polygon([(x, y), (x + 10, y - 6), (x + 20, y)], fill=(50, 50, 50))
        draw.polygon([(x + 20, y), (x + 14, y - 4), (x + 24, y - 2)], fill=(45, 45, 45))


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata["title"]
    author = metadata["author"]
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    # --- Sky (0 - 700) ---
    draw_sky(draw, WIDTH, 700)

    # --- Clouds ---
    draw_clouds(draw, WIDTH, 100)

    # --- Pale sun ---
    draw_sun(draw, 1100, 200, 60)

    # --- Ocean (700 - 1050) ---
    draw_ocean(draw, WIDTH, 700, 1050)

    # --- Horizon ship ---
    draw_ship(draw, 300, 700)
    draw_ship(draw, 1200, 710)

    # --- Distant forest line (950 - 1100) ---
    for i in range(60):
        tx = i * 28
        th = 90 + (i % 7) * 12
        draw_trees(draw, tx, 1050)

    # --- Palisade (center-left) ---
    draw_palisade(draw, 350, 1220, 28, 120, 320)

    # --- More trees behind palisade ---
    draw_trees(draw, 100, 1200)
    draw_trees(draw, 900, 1190)

    # --- Marsh / shoreline (1200 - 1350) ---
    draw_marsh(draw, 1200, 1350, WIDTH)

    # --- Foreground sand / earth ---
    for y in range(1350, TITLE_PANEL_Y):
        t = (y - 1350) / (TITLE_PANEL_Y - 1350)
        r = int(130 + (100 - 130) * t)
        g = int(110 + (80 - 110) * t)
        b = int(70 + (55 - 70) * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # --- Sea grass in foreground ---
    for gx in range(0, WIDTH, 7):
        gh = 15 + (gx % 11)
        draw.line(
            [(gx, TITLE_PANEL_Y), (gx - 3, TITLE_PANEL_Y - gh)],
            fill=(75, 80, 45),
            width=2,
        )

    # --- Seagulls ---
    draw_seagulls(draw)

    # --- Soften the imagery with a light blur ---
    # Apply gaussian blur to the upper section for an atmospheric feel
    try:
        upper = img.crop((0, 0, WIDTH, TITLE_PANEL_Y))
        upper = upper.filter(ImageFilter.GaussianBlur(radius=1.2))
        img.paste(upper, (0, 0))
    except Exception:
        pass

    # --- Title panel ---
    draw.rectangle(
        [(0, TITLE_PANEL_Y), (WIDTH, HEIGHT)],
        fill=(245, 240, 230, 240),
    )
    # Thin border line at top of panel
    draw.line(
        [(0, TITLE_PANEL_Y), (WIDTH, TITLE_PANEL_Y)],
        fill=(180, 170, 150),
        width=2,
    )

    # --- Title text ---
    title_font_size = 90
    title_font = None
    for size in range(90, 50, -2):
        try:
            title_font = ImageFont.truetype(str(FONT_DIR / "georgiab.ttf"), size)
        except Exception:
            continue
        # Check if it fits
        bbox = draw.textbbox((0, 0), title, font=title_font)
        tw = bbox[2] - bbox[0]
        if tw <= WIDTH - 120:
            title_font_size = size
            break

    if title_font is None:
        title_font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), title, font=title_font)
    tw = bbox[2] - bbox[0]
    tx = (WIDTH - tw) // 2
    ty = TITLE_PANEL_Y + 60
    draw.text((tx, ty), title, fill=(30, 30, 30), font=title_font)

    # --- Subtitle / location line ---
    try:
        loc_font = ImageFont.truetype(str(FONT_DIR / "georgia.ttf"), 26)
    except Exception:
        loc_font = ImageFont.load_default()
    loc_text = "ROANOKE ISLAND  ·  1587"
    bbox_l = draw.textbbox((0, 0), loc_text, font=loc_font)
    lw = bbox_l[2] - bbox_l[0]
    draw.text(
        ((WIDTH - lw) // 2, ty + 100),
        loc_text,
        fill=(120, 110, 90),
        font=loc_font,
    )

    # --- Author name ---
    try:
        author_font = ImageFont.truetype(str(FONT_DIR / "arialbd.ttf"), 40)
    except Exception:
        author_font = ImageFont.load_default()
    bbox_a = draw.textbbox((0, 0), author, font=author_font)
    aw = bbox_a[2] - bbox_a[0]
    draw.text(
        ((WIDTH - aw) // 2, TITLE_PANEL_Y + 200),
        author,
        fill=(60, 55, 45),
        font=author_font,
    )

    # --- Genre text ---
    try:
        genre_font = ImageFont.truetype(str(FONT_DIR / "arial.ttf"), 22)
    except Exception:
        genre_font = ImageFont.load_default()
    genre_text = "Historical Fiction"
    bbox_g = draw.textbbox((0, 0), genre_text, font=genre_font)
    gw = bbox_g[2] - bbox_g[0]
    draw.text(
        ((WIDTH - gw) // 2, TITLE_PANEL_Y + 260),
        genre_text,
        fill=(140, 130, 115),
        font=genre_font,
    )

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Convert to RGB before saving as PNG
    final = img.convert("RGB")
    _draw_standard_cover_title_panel(final, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    final.save(str(output_path), "PNG")
    print(f"Cover saved to {output_path}")



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    create_cover(args.metadata.resolve(), args.out.resolve())


if __name__ == "__main__":
    main()