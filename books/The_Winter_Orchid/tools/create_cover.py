#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Winter Orchid."""

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
    """Burgundy to cream to deep navy gradient for dark academia feel."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((80, 20, 25), (120, 40, 45), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((120, 40, 45), (60, 50, 70), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((60, 50, 70), (15, 10, 30), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_gothic_arches(draw: ImageDraw, width: int, height: int) -> None:
    """Draw Gothic arches framing the cover like a cathedral window."""
    # Left arch
    draw.arc([-200, -100, 400, 1200], 180, 270, fill=(40, 30, 50, 80), width=8)
    draw.arc([-180, -80, 380, 1180], 180, 270, fill=(60, 40, 60, 60), width=4)

    # Right arch
    draw.arc([width - 400, -100, width + 200, 1200], 270, 360, fill=(40, 30, 50, 80), width=8)
    draw.arc([width - 380, -80, width + 180, 1180], 270, 360, fill=(60, 40, 60, 60), width=4)

    # Top arch (rose window suggestion)
    cx, cy = width // 2, int(height * 0.25)
    r = 250
    draw.arc([cx - r, cy - r, cx + r, cy + r], 0, 360, fill=(100, 60, 70, 60), width=6)
    draw.arc([cx - r + 30, cy - r + 30, cx + r - 30, cy + r - 30], 0, 360, fill=(140, 80, 90, 50), width=4)
    draw.arc([cx - r + 60, cy - r + 60, cx + r - 60, cy + r - 60], 0, 360, fill=(180, 100, 110, 40), width=3)

    # Rose window spokes
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        ex = cx + int((r - 60) * math.cos(rad))
        ey = cy + int((r - 60) * math.sin(rad))
        draw.line([(cx, cy), (ex, ey)], fill=(120, 70, 80, 40), width=2)

    # Inner rose circle
    draw.ellipse([cx - 60, cy - 60, cx + 60, cy + 60], outline=(160, 100, 110, 60), width=3)
    draw.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], outline=(200, 140, 150, 50), width=2)


def draw_stained_glass(draw: ImageDraw, width: int, height: int) -> None:
    """Draw stained glass fragments in the upper portion."""
    rng = random.Random(17)
    cx, cy = width // 2, int(height * 0.25)

    colors = [(180, 40, 50, 60), (200, 160, 60, 50), (50, 80, 160, 50), (160, 60, 120, 50), (60, 140, 80, 50)]
    for _ in range(40):
        x = cx + rng.randint(-220, 220)
        y = cy + rng.randint(-220, 220)
        size = rng.randint(15, 50)
        color = rng.choice(colors)
        # Draw faceted shapes
        pts = []
        for _ in range(rng.randint(4, 6)):
            pts.append((x + rng.randint(-size, size), y + rng.randint(-size, size)))
        draw.polygon(pts, fill=color, outline=(200, 200, 200, 30), width=1)


def draw_library_building(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a Gothic library facade in the midground."""
    cx, cy = width // 2, int(height * 0.55)
    w, h = 500, 400

    # Building body
    draw.rectangle([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2], fill=(25, 20, 35))
    draw.rectangle([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2], outline=(50, 40, 60), width=2)

    # Gothic windows on facade
    window_w, window_h = 50, 90
    for i, wx in enumerate(range(cx - 150, cx + 160, 70)):
        wy = cy - h // 4
        # Window arch
        draw.rectangle([wx, wy, wx + window_w, wy + window_h], fill=(180, 160, 100, 120))
        draw.rectangle([wx, wy, wx + window_w, wy + window_h], outline=(60, 50, 70), width=1)
        # Arch top
        draw.arc([wx, wy - window_w // 2, wx + window_w, wy + window_w // 2], 0, 180, fill=(180, 160, 100, 100), width=2)
        # Cross bar
        draw.line([(wx + window_w // 2, wy), (wx + window_w // 2, wy + window_h)], fill=(60, 50, 70), width=1)
        draw.line([(wx, wy + window_h // 2), (wx + window_w, wy + window_h // 2)], fill=(60, 50, 70), width=1)

    # Central doorway
    door_w, door_h = 60, 120
    draw.rectangle([cx - door_w // 2, cy + h // 2 - door_h, cx + door_w // 2, cy + h // 2], fill=(15, 10, 20))
    draw.rectangle([cx - door_w // 2, cy + h // 2 - door_h, cx + door_w // 2, cy + h // 2], outline=(50, 40, 60), width=1)
    # Door arch
    draw.arc([cx - door_w // 2, cy + h // 2 - door_h - door_w // 2, cx + door_w // 2, cy + h // 2 - door_h + door_w // 2], 0, 180, fill=(60, 50, 70), width=2)

    # Towers
    for sign in [-1, 1]:
        tx = cx + sign * 280
        tw, th = 60, 200
        draw.rectangle([tx - tw // 2, cy - h // 2 - th + 100, tx + tw // 2, cy + h // 2], fill=(30, 25, 40))
        draw.rectangle([tx - tw // 2, cy - h // 2 - th + 100, tx + tw // 2, cy + h // 2], outline=(50, 40, 60), width=1)
        # Spire
        draw.polygon([(tx - tw // 2, cy - h // 2 - th + 100), (tx, cy - h // 2 - th + 20), (tx + tw // 2, cy - h // 2 - th + 100)], fill=(40, 30, 50))
        # Tower window
        draw.rectangle([tx - 10, cy - h // 4, tx + 10, cy - h // 4 + 40], fill=(180, 160, 100, 80))


def draw_orchid(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a winter orchid in snow near the bottom-center."""
    cx, cy = width // 2, int(height * 0.8)

    # Stem
    draw.line([(cx, cy + 80), (cx, cy - 60)], fill=(60, 100, 60), width=4)
    draw.line([(cx, cy - 20), (cx - 40, cy - 60)], fill=(60, 100, 60), width=3)

    # Leaves
    draw.polygon([(cx, cy + 40), (cx - 30, cy + 20), (cx - 15, cy + 60)], fill=(50, 90, 50))
    draw.polygon([(cx, cy + 40), (cx + 30, cy + 20), (cx + 15, cy + 60)], fill=(50, 90, 50))

    # Petals (white with purple veins)
    petal_offsets = [(0, -40), (-30, -20), (30, -20), (-20, -50), (20, -50)]
    for px, py in petal_offsets:
        draw.ellipse([cx + px - 25, cy + py - 15, cx + px + 25, cy + py + 15], fill=(240, 235, 230, 220))
        draw.ellipse([cx + px - 25, cy + py - 15, cx + px + 25, cy + py + 15], outline=(180, 160, 200, 120), width=1)

    # Purple veining on petals
    for px, py in petal_offsets:
        for v in range(3):
            vx = cx + px + (v - 1) * 10
            draw.line([(vx, cy + py - 8), (vx + 5, cy + py + 8)], fill=(120, 80, 160, 60), width=1)

    # Center
    draw.ellipse([cx - 8, cy - 68, cx + 8, cy - 52], fill=(200, 180, 100))

    # Snow around base
    rng = random.Random(13)
    for _ in range(30):
        sx = cx + rng.randint(-80, 80)
        sy = cy + 60 + rng.randint(-20, 40)
        sr = rng.randint(3, 10)
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(220, 220, 230, 100))


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom with white text."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark burgundy
    draw.rectangle([(0, panel_top), (width, height)], fill=(40, 15, 20, 240))
    # Panel border at top
    draw.line([(0, panel_top), (width, panel_top)], fill=(120, 60, 70), width=3)
    # Inner border
    draw.line([(0, panel_top + 6), (width, panel_top + 6)], fill=(80, 30, 40), width=1)

    # Ornamental line
    draw.line([(200, panel_top + 50), (width - 200, panel_top + 50)], fill=(160, 100, 110), width=1)

    # Title text - use arialbd.ttf
    title = "The Winter\nOrchid"
    title_font_size = 80
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

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
        y_offset += 100

    # Subtitle line (smaller, decorative)
    y_offset += 10

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
    ay = y_offset + 30
    draw.text((ax, ay), author, fill=(200, 180, 170), font=author_font)

    # Bottom ornamental line
    draw.line([(300, ay + 50), (width - 300, ay + 50)], fill=(100, 50, 60), width=1)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Winter Orchid")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background (burgundy/cream/navy)
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Gothic arches framing the cover
    draw_gothic_arches(draw, WIDTH, HEIGHT)

    # Step 3: Stained glass fragments
    draw_stained_glass(draw, WIDTH, HEIGHT)

    # Step 4: Gothic library building
    draw_library_building(draw, WIDTH, HEIGHT)

    # Step 5: Winter orchid in snow
    draw_orchid(draw, WIDTH, HEIGHT)

    # Step 6: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arial.ttf"),
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