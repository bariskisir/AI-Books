#!/usr/bin/env python3
"""Cover: The Whaling Wife — Gray Nantucket sky-to-navy sea gradient, pale moon, whaling ship silhouette on horizon, diagonal harpoon."""

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
    """Nantucket gray sky to dark navy sea gradient."""
    for y in range(height):
        if y < height * 0.45:
            t = y / (height * 0.45)
            c = lerp_color((140, 145, 150), (80, 85, 95), t)
        elif y < height * 0.55:
            c = (60, 65, 75)
        else:
            t = (y - height * 0.55) / (height * 0.45)
            c = lerp_color((60, 65, 75), (10, 15, 40), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_waves(draw: ImageDraw, width: int, height: int) -> None:
    """Draw stylized ocean waves in the lower portion."""
    wave_color = (200, 210, 220, 40)
    for row in range(12):
        y_base = int(height * 0.52) + row * 20
        for x in range(0, width, 8):
            offset = int(6 * (x / 80 + row * 1.5))
            y = y_base + offset
            if y < height:
                draw.point((x, y), fill=wave_color)


def draw_ship(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a whaling ship silhouette on the horizon."""
    cx = width // 2
    ship_y = int(height * 0.48)

    # Hull
    hull_points = [
        (cx - 160, ship_y),
        (cx - 140, ship_y + 50),
        (cx + 100, ship_y + 50),
        (cx + 120, ship_y),
    ]
    draw.polygon(hull_points, fill=(25, 28, 35))

    # Hull line detail
    draw.line(
        [(cx - 150, ship_y + 10), (cx + 110, ship_y + 10)],
        fill=(50, 55, 65),
        width=2,
    )

    # Masts
    masts = [cx - 70, cx, cx + 60]
    for mx in masts:
        draw.line(
            [(mx, ship_y - 180), (mx, ship_y - 10)],
            fill=(30, 33, 40),
            width=4,
        )

    # Cross spars
    spars = [
        (cx - 70, ship_y - 160, cx - 60, ship_y - 50),
        (cx, ship_y - 170, cx, ship_y - 50),
        (cx + 60, ship_y - 150, cx + 60, ship_y - 50),
    ]
    for mx, top, bot, _ in zip(
        [cx - 70, cx, cx + 60],
        [ship_y - 160, ship_y - 170, ship_y - 150],
        [ship_y - 50, ship_y - 50, ship_y - 50],
        spars,
    ):
        for y_level in range(top, bot, 30):
            spar_w = 60 + (y_level - top) * 2
            draw.line(
                [(mx - spar_w, y_level), (mx + spar_w, y_level)],
                fill=(35, 38, 45),
                width=2,
            )

    # Foreshortened sails (squares)
    draw.polygon(
        [(cx - 70 - 50, ship_y - 130), (cx - 70 + 50, ship_y - 130), (cx - 70 + 50, ship_y - 60), (cx - 70 - 50, ship_y - 60)],
        fill=(80, 85, 95, 180),
    )
    draw.polygon(
        [(cx - 50, ship_y - 140), (cx + 50, ship_y - 140), (cx + 50, ship_y - 60), (cx - 50, ship_y - 60)],
        fill=(90, 95, 105, 180),
    )
    draw.polygon(
        [(cx + 60 - 40, ship_y - 120), (cx + 60 + 40, ship_y - 120), (cx + 60 + 40, ship_y - 60), (cx + 60 - 40, ship_y - 60)],
        fill=(75, 80, 90, 180),
    )

    # Bowsprit
    draw.line(
        [(cx + 120, ship_y - 5), (cx + 190, ship_y - 40)],
        fill=(30, 33, 40),
        width=3,
    )

    # Flag
    draw.polygon(
        [(cx + 190, ship_y - 40), (cx + 190, ship_y - 25), (cx + 160, ship_y - 32)],
        fill=(60, 70, 90),
    )


def draw_harpoon(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a large harpoon diagonally crossing the composition."""
    start_x = int(width * 0.72)
    start_y = int(height * 0.18)
    end_x = int(width * 0.55)
    end_y = int(height * 0.38)

    # Shaft
    draw.line(
        [(start_x, start_y), (end_x, end_y)],
        fill=(160, 150, 130),
        width=5,
    )

    # Harpoon head (toggle iron)
    head_x = end_x
    head_y = end_y
    head_len = 18

    # Point
    draw.polygon(
        [(head_x, head_y), (head_x - head_len, head_y - head_len // 2), (head_x - head_len, head_y + head_len // 2)],
        fill=(180, 170, 150),
    )

    # Toggle barbs
    draw.line(
        [(head_x - 10, head_y - 10), (head_x - 18, head_y - 6)],
        fill=(180, 170, 150),
        width=3,
    )
    draw.line(
        [(head_x - 10, head_y + 10), (head_x - 18, head_y + 6)],
        fill=(180, 170, 150),
        width=3,
    )

    # Rope wrapped at base
    for i in range(3):
        rx = head_x - 20 - i * 4
        draw.ellipse(
            [rx - 4, head_y - 5, rx + 4, head_y + 5],
            fill=(140, 120, 90),
        )


def draw_moon(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a pale moon behind the ship."""
    mx = int(width * 0.35)
    my = int(height * 0.22)
    r = 50

    # Outer glow
    for i in range(6):
        glow_r = r + i * 12
        alpha = 15 - i * 2
        draw.ellipse(
            [mx - glow_r, my - glow_r, mx + glow_r, my + glow_r],
            fill=(200, 210, 230, alpha),
        )

    # Moon body
    draw.ellipse(
        [mx - r, my - r, mx + r, my + r],
        fill=(220, 225, 235, 180),
    )

    # Moon highlight
    draw.ellipse(
        [mx - r + 10, my - r + 10, mx + r - 15, my + r - 15],
        fill=(240, 242, 248, 100),
    )

    # Moon shadow (crescent effect)
    draw.ellipse(
        [mx - r + 20, my - r - 5, mx + r + 10, my + r + 5],
        fill=(140, 145, 150, 60),
    )


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom with white text."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    draw.rectangle([(0, panel_top), (width, height)], fill=(15, 18, 30))

    # Subtle top border line
    draw.line([(0, panel_top), (width, panel_top)], fill=(60, 70, 100), width=2)

    # Title text
    title = "The Whaling Wife"
    title_font_size = 80
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    try:
        bbox = draw.textbbox((0, 0), title, font=title_font)
        tw = bbox[2] - bbox[0]
    except Exception:
        tw = 0
    tx = (width - tw) // 2
    ty = panel_top + 100
    draw.text((tx, ty), title, fill=(255, 255, 255), font=title_font)

    # Divider line
    divider_y = ty + 85
    divider_w = 80
    draw.line(
        [(width // 2 - divider_w, divider_y), (width // 2 + divider_w, divider_y)],
        fill=(100, 120, 160),
        width=2,
    )

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
    ay = divider_y + 40
    draw.text((ax, ay), author, fill=(180, 190, 210), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Whaling Wife")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    for y in range(HEIGHT):
        if y < HEIGHT * 0.45:
            t = y / (HEIGHT * 0.45)
            c = lerp_color((140, 145, 150), (80, 85, 95), t)
        elif y < HEIGHT * 0.55:
            c = (60, 65, 75)
        else:
            t = (y - HEIGHT * 0.55) / (HEIGHT * 0.45)
            c = lerp_color((60, 65, 75), (10, 15, 40), t)
        draw.line([(0, y), (WIDTH, y)], fill=c)

    mx, my = int(WIDTH * 0.35), int(HEIGHT * 0.22)
    mr = 50
    for i in range(6):
        gr = mr + i * 12
        ga = 15 - i * 2
        draw.ellipse([mx - gr, my - gr, mx + gr, my + gr], fill=(200, 210, 230, ga))
    draw.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(220, 225, 235, 180))
    draw.ellipse([mx - mr + 10, my - mr + 10, mx + mr - 15, my + mr - 15], fill=(240, 242, 248, 100))

    cx = WIDTH // 2
    ship_y = int(HEIGHT * 0.48)
    draw.polygon([(cx - 160, ship_y), (cx - 140, ship_y + 50), (cx + 100, ship_y + 50), (cx + 120, ship_y)], fill=(25, 28, 35))
    draw.line([(cx - 150, ship_y + 10), (cx + 110, ship_y + 10)], fill=(50, 55, 65), width=2)
    for mx2 in [cx - 70, cx, cx + 60]:
        draw.line([(mx2, ship_y - 180), (mx2, ship_y - 10)], fill=(30, 33, 40), width=4)
    for mx2, top in [(cx - 70, ship_y - 160), (cx, ship_y - 170), (cx + 60, ship_y - 150)]:
        for y_level in range(top, ship_y - 50, 30):
            sw = 60 + (y_level - top) * 2
            draw.line([(mx2 - sw, y_level), (mx2 + sw, y_level)], fill=(35, 38, 45), width=2)

    hx, hy = int(WIDTH * 0.72), int(HEIGHT * 0.18)
    hex, hey = int(WIDTH * 0.55), int(HEIGHT * 0.38)
    draw.line([(hx, hy), (hex, hey)], fill=(160, 150, 130), width=5)
    draw.polygon([(hex, hey), (hex - 18, hey - 9), (hex - 18, hey + 9)], fill=(180, 170, 150))

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