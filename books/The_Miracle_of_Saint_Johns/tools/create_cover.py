#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Miracle of Saint John's."""

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
    """Warm stone gray to deep blue gradient for the inspirational/spiritual feel."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((120, 110, 100), (90, 75, 65), t)
        elif y < height * 0.75:
            t = (y - height * 0.4) / (height * 0.35)
            c = lerp_color((90, 75, 65), (50, 45, 60), t)
        else:
            t = (y - height * 0.75) / (height * 0.25)
            c = lerp_color((50, 45, 60), (20, 15, 30), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_church(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a stylized church facade with stained glass window and bell tower."""
    cx = width // 2
    base_y = int(height * 0.65)

    # Church body
    body_w, body_h = 400, 300
    draw.rectangle(
        [cx - body_w // 2, base_y - body_h, cx + body_w // 2, base_y],
        fill=(100, 90, 85),
        outline=(70, 60, 55),
        width=2,
    )

    # Bell tower
    tower_w, tower_h = 100, 200
    tower_x = cx - body_w // 2 - tower_w + 20
    draw.rectangle(
        [tower_x, base_y - body_h - tower_h + 60, tower_x + tower_w, base_y - body_h + 60],
        fill=(105, 95, 88),
        outline=(70, 60, 55),
        width=2,
    )

    # Tower spire
    spire_h = 80
    draw.polygon(
        [
            (tower_x - 10, base_y - body_h - tower_h + 60),
            (tower_x + tower_w // 2, base_y - body_h - tower_h + 60 - spire_h),
            (tower_x + tower_w + 10, base_y - body_h - tower_h + 60),
        ],
        fill=(80, 70, 65),
    )

    # Cross on spire
    cx_tower = tower_x + tower_w // 2
    cross_top = base_y - body_h - tower_h + 60 - spire_h - 30
    draw.line([(cx_tower, cross_top), (cx_tower, cross_top + 25)], fill=(200, 180, 120), width=4)
    draw.line([(cx_tower - 12, cross_top + 10), (cx_tower + 12, cross_top + 10)], fill=(200, 180, 120), width=4)

    # Roof
    draw.polygon(
        [
            (cx - body_w // 2 - 20, base_y - body_h),
            (cx, base_y - body_h - 80),
            (cx + body_w // 2 + 20, base_y - body_h),
        ],
        fill=(80, 70, 60),
    )

    # Stained glass window (central, large)
    win_w, win_h = 140, 200
    win_x, win_y = cx - win_w // 2, base_y - body_h + 30

    # Window arch shape
    draw.arc(
        [win_x, win_y, win_x + win_w, win_y + win_h],
        start=0, end=180, fill=(130, 110, 100), width=3,
    )
    draw.rectangle(
        [win_x, win_y + win_h // 2, win_x + win_w, win_y + win_h],
        fill=None, outline=(130, 110, 100), width=3,
    )

    # Stained glass colors - draw segments
    import random
    rng = random.Random(17)

    colors = [
        (200, 50, 50, 180),    # red
        (50, 80, 200, 180),    # blue
        (200, 180, 50, 180),   # gold
        (50, 180, 80, 180),    # green
        (180, 100, 50, 180),   # amber
        (150, 50, 180, 180),   # violet
    ]

    # Fill window with stained glass segments
    segments = 6
    seg_h = win_h // segments
    for s in range(segments):
        sy = win_y + s * seg_h
        color = rng.choice(colors)
        draw.rectangle(
            [win_x + 3, sy + 2, win_x + win_w - 3, sy + seg_h - 2],
            fill=color,
        )

    # Window glow effect
    for i in range(5):
        glow_color = (255, 200, 100, 30 - i * 5)
        draw.rectangle(
            [win_x - i, win_y - i, win_x + win_w + i, win_y + win_h + i],
            outline=None,
            width=0,
        )

    # Rose window above
    rose_r = 40
    rose_cx = cx
    rose_cy = win_y - 60
    draw.ellipse(
        [rose_cx - rose_r, rose_cy - rose_r, rose_cx + rose_r, rose_cy + rose_r],
        fill=(100, 90, 85),
        outline=(70, 60, 55),
        width=2,
    )

    # Rose window segments
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        x1 = rose_cx + 5 * math.cos(rad)
        y1 = rose_cy + 5 * math.sin(rad)
        x2 = rose_cx + (rose_r - 5) * math.cos(rad)
        y2 = rose_cy + (rose_r - 5) * math.sin(rad)
        draw.line([(x1, y1), (x2, y2)], fill=rng.choice(colors), width=3)

    # Door
    door_w, door_h = 60, 100
    draw.arc(
        [cx - door_w // 2, base_y - door_h, cx + door_w // 2, base_y],
        start=0, end=180, fill=(60, 50, 45), width=3,
    )
    draw.rectangle(
        [cx - door_w // 2, base_y - door_h // 2, cx + door_w // 2, base_y],
        fill=(50, 40, 35),
    )


def draw_city_skyline(draw: ImageDraw, width: int, height: int) -> None:
    """Draw faint city skyline in the background."""
    import random
    rng = random.Random(42)

    base_y = int(height * 0.65)
    buildings = []

    # Left side buildings
    for i in range(8):
        bw = rng.randint(30, 60)
        bh = rng.randint(60, 180)
        bx = i * 80 - 20
        by = base_y - bh
        buildings.append((bx, by, bw, bh))

    # Right side buildings
    for i in range(8):
        bw = rng.randint(30, 60)
        bh = rng.randint(60, 180)
        bx = width - 160 + i * 80
        by = base_y - bh
        buildings.append((bx, by, bw, bh))

    for bx, by, bw, bh in buildings:
        draw.rectangle([bx, by, bx + bw, base_y], fill=(60, 55, 50, 150))

        # Windows on buildings
        for wy in range(by + 5, base_y - 5, 15):
            for wx in range(bx + 4, bx + bw - 4, 12):
                if rng.random() < 0.6:
                    win_brightness = rng.randint(30, 60)
                    draw.rectangle(
                        [wx, wy, wx + 6, wy + 8],
                        fill=(win_brightness + 180, win_brightness + 170, win_brightness + 100, 100),
                    )


def draw_stained_glass_light(draw: ImageDraw, width: int, height: int) -> None:
    """Draw colored light beams from the window onto the ground."""
    cx = width // 2
    window_top = int(height * 0.25)
    window_bottom = int(height * 0.48)
    ground_y = int(height * 0.65)

    colors = [
        (200, 50, 50, 20),
        (50, 80, 200, 20),
        (200, 180, 50, 15),
        (50, 180, 80, 15),
        (180, 100, 50, 15),
        (150, 50, 180, 15),
    ]

    import random
    rng = random.Random(17)

    for i in range(6):
        angle_offset = rng.uniform(-0.3, 0.3)
        left_ratio = i / 6 + angle_offset * 0.1
        right_ratio = (i + 1) / 6 + angle_offset * 0.1

        src_left = cx - 70 + int(140 * left_ratio)
        src_right = cx - 70 + int(140 * right_ratio)

        spread = 200
        dst_left = cx - spread + int(spread * 2 * left_ratio)
        dst_right = cx - spread + int(spread * 2 * right_ratio)

        draw.polygon(
            [
                (src_left, window_top),
                (src_right, window_top),
                (dst_right, ground_y),
                (dst_left, ground_y),
            ],
            fill=rng.choice(colors),
        )


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom of the cover with white text."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark semi-transparent
    draw.rectangle([(0, panel_top), (width, height)], fill=(20, 15, 30, 220))

    # Subtle top border
    draw.line([(0, panel_top), (width, panel_top)], fill=(200, 180, 120), width=3)

    # Title text
    title = "The Miracle of\nSaint John's"
    title_font_size = 72
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
        y_offset += 90

    # Author name in white
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
    draw.text((ax, ay), author, fill=(200, 180, 120), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Miracle of Saint John's")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Faint city skyline
    draw_city_skyline(draw, WIDTH, HEIGHT)

    # Step 3: Stained glass light beams
    draw_stained_glass_light(draw, WIDTH, HEIGHT)

    # Step 4: Church facade
    draw_church(draw, WIDTH, HEIGHT)

    # Step 5: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
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