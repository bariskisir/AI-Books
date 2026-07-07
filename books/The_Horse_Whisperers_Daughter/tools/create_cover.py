#!/usr/bin/env python3
"""Cover: The Horse Whisperer's Daughter — Black horse and woman silhouetted against sunset at Churchill Downs twin spires, dusk purple/amber/black."""

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


def draw_sky_gradient(draw: ImageDraw, width: int, height: int) -> None:
    """Dusk purple/amber sunset gradient — Churchill Downs."""
    for y in range(height):
        if y < height * 0.30:
            t = y / (height * 0.30)
            c = lerp_color((40, 20, 60), (80, 40, 80), t)
        elif y < height * 0.50:
            t = (y - height * 0.30) / (height * 0.20)
            c = lerp_color((80, 40, 80), (180, 80, 60), t)
        elif y < height * 0.70:
            t = (y - height * 0.50) / (height * 0.20)
            c = lerp_color((180, 80, 60), (220, 160, 80), t)
        else:
            t = (y - height * 0.70) / (height * 0.30)
            c = lerp_color((220, 160, 80), (60, 50, 40), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_pasture(draw: ImageDraw, width: int, height: int) -> None:
    """Draw rolling green pasture with grass texture."""
    # Gentle hills
    for hx in range(0, width, 2):
        hy1 = int(height * 0.48 + 30 * (hx / width) + 20 * (hx * 3 / width % 1))
        hy2 = int(height * 0.55 + 20 * ((hx + 100) / width) + 30 * ((hx * 2 / width) % 1))
        shade = 60 + int(20 * (hx / width))
        draw.line([(hx, hy1), (hx, hy2)], fill=(shade, shade + 50, shade + 20), width=1)

    # Distant rolling hills
    for hx in range(0, width, 3):
        hy = int(height * 0.42 + 25 * ((hx + 50) / width) + 15 * ((hx * 4 / width) % 1))
        shade = 90 + int(15 * (hx / width))
        draw.line([(hx, height * 0.38), (hx, hy)], fill=(shade, shade + 40, shade + 15), width=1)


def draw_white_fence(draw: ImageDraw, width: int, height: int) -> None:
    """Draw white board fence across the middle distance."""
    fence_y = int(height * 0.52)
    # Horizontal boards
    for row in range(3):
        y_offset = fence_y + row * 14
        draw.line([(0, y_offset), (width, y_offset)], fill=(240, 240, 235), width=4)
        # Shadow under each board
        draw.line([(0, y_offset + 4), (width, y_offset + 4)], fill=(200, 200, 190), width=2)

    # Vertical posts
    for px in range(0, width, 120):
        draw.rectangle([px, fence_y - 10, px + 10, fence_y + 42], fill=(220, 220, 210))
        # Post cap
        draw.rectangle([px - 2, fence_y - 14, px + 12, fence_y - 10], fill=(230, 230, 220))
        # Post shadow
        draw.rectangle([px + 10, fence_y - 8, px + 12, fence_y + 42], fill=(180, 180, 170))


def draw_horse_silhouette(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a thoroughbred horse silhouette in the pasture."""
    cx, cy = width // 2, int(height * 0.48)
    # Horse body - simple polygon silhouette
    body_pts = [
        (cx - 80, cy - 20),   # chest
        (cx - 60, cy - 50),   # neck top
        (cx - 30, cy - 65),   # head
        (cx - 25, cy - 60),   # nose
        (cx - 40, cy - 50),   # jaw
        (cx - 50, cy - 30),   # throat
        (cx - 70, cy - 15),   # neck bottom
        (cx + 40, cy - 15),   # back
        (cx + 80, cy - 25),   # rump
        (cx + 90, cy - 10),   # tail start
        (cx + 100, cy),       # tail
        (cx + 105, cy + 5),   # tail tip
        (cx + 88, cy + 5),    # tail underside
        (cx + 75, cy),        # behind rump
        (cx + 65, cy + 5),    # hind leg top
        (cx + 60, cy + 30),   # hind leg bottom
        (cx + 55, cy + 33),   # hoof
        (cx + 45, cy + 28),   # leg back
        (cx + 40, cy + 5),    # belly
        (cx, cy + 5),         # belly front
        (cx - 10, cy + 30),   # front leg bottom
        (cx - 15, cy + 33),   # front hoof
        (cx - 25, cy + 28),   # front leg back
        (cx - 30, cy),        # chest bottom
    ]
    draw.polygon(body_pts, fill=(20, 20, 25))  # Near-black silhouette

    # Second horse smaller, distant
    cx2 = cx - 220
    cy2 = cy - 5
    body_pts2 = [
        (cx2 - 40, cy2 - 10), (cx2 - 30, cy2 - 25), (cx2 - 15, cy2 - 33),
        (cx2 - 12, cy2 - 30), (cx2 - 20, cy2 - 25), (cx2 - 25, cy2 - 15),
        (cx2 + 20, cy2 - 8), (cx2 + 40, cy2 - 12), (cx2 + 45, cy2 - 5),
        (cx2 + 50, cy2), (cx2 + 52, cy2 + 3), (cx2 + 44, cy2 + 3),
        (cx2 + 38, cy2), (cx2 + 33, cy2 + 3), (cx2 + 30, cy2 + 15),
        (cx2 + 28, cy2 + 17), (cx2 + 23, cy2 + 14), (cx2 + 20, cy2 + 3),
        (cx2, cy2 + 3), (cx2 - 5, cy2 + 15), (cx2 - 8, cy2 + 17),
        (cx2 - 12, cy2 + 14), (cx2 - 15, cy2),
    ]
    draw.polygon(body_pts2, fill=(30, 30, 35))


def draw_churchill_spires(draw: ImageDraw, width: int, height: int) -> None:
    """Draw Churchill Downs twin spires in the distance."""
    # Twin spires
    spire_color = (40, 35, 45, 200)
    for sx in [width // 2 - 80, width // 2 + 80]:
        draw.rectangle((sx - 6, 450, sx + 6, 900), fill=spire_color)
        draw.polygon([(sx - 12, 450), (sx + 12, 450), (sx, 400)], fill=spire_color)
        # Cross on top
        draw.line((sx, 390, sx, 410), fill=(60, 55, 65, 180), width=2)
        draw.line((sx - 6, 400, sx + 6, 400), fill=(60, 55, 65, 180), width=2)

    # Grandstand silhouette between spires
    draw.rectangle((width // 2 - 120, 700, width // 2 + 120, 900), fill=(35, 30, 40, 200))
    # Roofline
    draw.polygon([(width // 2 - 130, 700), (width // 2 + 130, 700), (width // 2 + 150, 680), (width // 2 - 150, 680)], fill=(35, 30, 40, 200))


def draw_main_barn(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a traditional Kentucky horse barn on the right side."""
    bx = width - 500
    by = int(height * 0.32)
    bw = 350
    bh = int(height * 0.18)

    # Barn body - red
    draw.rectangle([bx, by, bx + bw, by + bh], fill=(120, 30, 25))

    # Barn roofline
    draw.polygon(
        [(bx - 20, by), (bx + bw // 2, by - 60), (bx + bw + 20, by)],
        fill=(80, 25, 20),
    )

    # Cupola on roof
    cup_w, cup_h = 40, 30
    cup_x = bx + bw // 2 - cup_w // 2
    cup_y = by - 60 - cup_h
    draw.rectangle([cup_x, cup_y, cup_x + cup_w, cup_y + cup_h], fill=(60, 20, 15))
    # Cupola roof
    draw.polygon(
        [(cup_x - 5, cup_y), (cup_x + cup_w // 2, cup_y - 15), (cup_x + cup_w + 5, cup_y)],
        fill=(50, 15, 10),
    )
    # Weather vane
    vane_x = cup_x + cup_w // 2
    draw.line([(vane_x, cup_y - 15), (vane_x, cup_y - 30)], fill=(100, 100, 95), width=2)

    # Barn door (dark opening)
    door_w, door_h = bw // 3, int(bh * 0.6)
    door_x = bx + (bw - door_w) // 2
    door_y = by + bh - door_h
    draw.rectangle([door_x, door_y, door_x + door_w, door_y + door_h], fill=(40, 15, 10))

    # Hayloft window
    win_w, win_h = 50, 40
    win_x = bx + (bw - win_w) // 2
    win_y = by + 20
    draw.rectangle([win_x, win_y, win_x + win_w, win_y + win_h], fill=(30, 12, 8))
    draw.rectangle([win_x, win_y, win_x + win_w, win_y + win_h], outline=(80, 25, 20), width=2)
    # Cross in window
    draw.line([(win_x + win_w // 2, win_y), (win_x + win_w // 2, win_y + win_h)], fill=(60, 18, 15), width=2)
    draw.line([(win_x, win_y + win_h // 2), (win_x + win_w, win_y + win_h // 2)], fill=(60, 18, 15), width=2)


def draw_small_barn(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a secondary tobacco barn on the left."""
    bx = 80
    by = int(height * 0.36)
    bw = 200
    bh = int(height * 0.14)

    draw.rectangle([bx, by, bx + bw, by + bh], fill=(90, 35, 30))
    draw.polygon(
        [(bx - 10, by), (bx + bw // 2, by - 35), (bx + bw + 10, by)],
        fill=(60, 25, 20),
    )
    # Tobacco slats (vertical dark lines)
    for sx in range(bx + 15, bx + bw - 15, 25):
        draw.line([(sx, by + 5), (sx, by + bh - 5)], fill=(60, 22, 18), width=3)


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at bottom with white text."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    draw.rectangle([(0, panel_top), (width, height)], fill=(20, 15, 18))

    # Thin gold border at top of panel
    draw.line([(0, panel_top), (width, panel_top)], fill=(180, 130, 70), width=3)
    draw.line([(0, panel_top + 4), (width, panel_top + 4)], fill=(180, 130, 70, 80), width=1)

    # Title text
    title = "The Horse\nWhisperer's\nDaughter"
    title_font_size = 68
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered, white text
    lines = title.split("\n")
    y_offset = panel_top + 80
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 0
        tx = (width - tw) // 2
        # Shadow for readability
        shadow_offset = 2
        draw.text((tx + shadow_offset, y_offset + shadow_offset), line, fill=(0, 0, 0, 120), font=title_font)
        draw.text((tx, y_offset), line, fill=(255, 255, 255), font=title_font)
        y_offset += 80

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
    ay = y_offset + 40
    draw.text((ax + 1, ay + 1), author, fill=(0, 0, 0, 100), font=author_font)
    draw.text((ax, ay), author, fill=(200, 190, 180), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Horse Whisperer's Daughter")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Sunset gradient: deep purple at top, amber at horizon, black at bottom
    for y in range(HEIGHT):
        t = y / HEIGHT
        if t < 0.5:
            r = int(80 + 175 * (t / 0.5))
            g = int(60 + 120 * (t / 0.5))
            b = int(120 - 60 * (t / 0.5))
        else:
            r = int(255 - 155 * ((t - 0.5) / 0.5))
            g = int(180 - 130 * ((t - 0.5) / 0.5))
            b = int(60 - 50 * ((t - 0.5) / 0.5))
        draw.line([(0, y), (WIDTH, y)], fill=(max(0, r), max(0, g), max(0, b), 255))

    # Sun disc
    sun_x, sun_y = WIDTH // 2, int(HEIGHT * 0.42)
    for r in range(80, 0, -2):
        draw.ellipse([sun_x - r, sun_y - r, sun_x + r, sun_y + r], fill=(255, 200 + int(55 * (1 - r / 80)), 80, max(0, 60 - r)))
    draw.ellipse([sun_x - 50, sun_y - 50, sun_x + 50, sun_y + 50], fill=(255, 220, 100))

    # Churchill Downs twin spires
    spire_base = int(HEIGHT * 0.40)
    # Left spire
    for s in [(WIDTH // 2 - 150, 180), (WIDTH // 2 - 110, 200)]:
        sx, sh = s
        draw.polygon([(sx - 12, spire_base), (sx + 12, spire_base), (sx + 4, spire_base - sh), (sx - 4, spire_base - sh)], fill=(15, 10, 8, 200))
        draw.polygon([(sx - 16, spire_base - sh), (sx + 16, spire_base - sh), (sx, spire_base - sh - 30)], fill=(15, 10, 8, 200))
    # Roof between spires
    draw.line((WIDTH // 2 - 160, spire_base, WIDTH // 2 - 100, spire_base), fill=(15, 10, 8, 200), width=6)
    draw.line((WIDTH // 2 + 100, spire_base, WIDTH // 2 + 160, spire_base), fill=(15, 10, 8, 200), width=6)
    # Grandstand
    draw.rectangle([WIDTH // 2 - 180, spire_base - 30, WIDTH // 2 - 80, spire_base], fill=(15, 10, 8, 180))
    draw.rectangle([WIDTH // 2 + 80, spire_base - 30, WIDTH // 2 + 180, spire_base], fill=(15, 10, 8, 180))

    # Black horse silhouette
    hx, hy = WIDTH // 2 - 60, int(HEIGHT * 0.55)
    # Horse body
    draw.polygon([
        (hx - 80, hy - 20), (hx - 60, hy - 50), (hx - 30, hy - 65),
        (hx - 25, hy - 60), (hx - 40, hy - 50), (hx - 50, hy - 30),
        (hx - 70, hy - 15), (hx + 40, hy - 15), (hx + 80, hy - 25),
        (hx + 90, hy - 10), (hx + 100, hy), (hx + 105, hy + 5),
        (hx + 88, hy + 5), (hx + 75, hy), (hx + 65, hy + 5),
        (hx + 60, hy + 30), (hx + 55, hy + 33), (hx + 45, hy + 28),
        (hx + 40, hy + 5), (hx, hy + 5), (hx - 10, hy + 30),
        (hx - 15, hy + 33), (hx - 25, hy + 28), (hx - 30, hy),
    ], fill=(8, 6, 5))

    # Woman silhouette beside horse
    wx, wy = hx + 110, hy - 30
    draw.ellipse((wx - 8, wy - 60, wx + 8, wy), fill=(8, 6, 5))
    draw.ellipse((wx - 6, wy - 72, wx + 6, wy - 58), fill=(8, 6, 5))

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