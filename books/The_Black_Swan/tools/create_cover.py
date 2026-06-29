#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Black Swan — ballet fiction."""

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
    """Deep crimson to dark charcoal gradient — stage velvet and shadow."""
    for y in range(height):
        if y < height * 0.5:
            t = y / (height * 0.5)
            c = lerp_color((10, 5, 5), (90, 15, 15), t)
        elif y < height * 0.75:
            t = (y - height * 0.5) / (height * 0.25)
            c = lerp_color((90, 15, 15), (160, 30, 30), t)
        else:
            t = (y - height * 0.75) / (height * 0.25)
            c = lerp_color((160, 30, 30), (20, 10, 10), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_curtains(draw: ImageDraw, width: int, height: int) -> None:
    """Draw velvet stage curtains framing the image."""
    colors = [(180, 25, 25), (150, 18, 18), (120, 12, 12), (90, 8, 8)]

    # Left curtain — cascading folds
    for i in range(8):
        x_base = i * 30
        top_w = 70 - i * 6
        fold_color = colors[i % len(colors)]
        points = [
            (x_base, 0),
            (x_base + top_w, 0),
            (x_base + 100, int(height * 0.82)),
            (x_base + 50, int(height * 0.82)),
        ]
        draw.polygon(points, fill=fold_color)
        # Vertical fold lines
        for fy in range(0, int(height * 0.78), 50):
            wave = int(12 * math.sin(fy / 35))
            draw.line(
                [(x_base + 25 + wave, fy), (x_base + 55, fy + 25)],
                fill=(80, 5, 5), width=2,
            )

    # Right curtain — mirrored
    for i in range(8):
        x_base = width - (i + 1) * 30
        top_w = 70 - i * 6
        fold_color = colors[i % len(colors)]
        points = [
            (x_base, 0),
            (x_base + top_w, 0),
            (x_base + 100, int(height * 0.82)),
            (x_base + 50, int(height * 0.82)),
        ]
        draw.polygon(points, fill=fold_color)
        for fy in range(0, int(height * 0.78), 50):
            wave = int(12 * math.sin(fy / 35))
            draw.line(
                [(x_base + 25 - wave, fy), (x_base + 55, fy + 25)],
                fill=(80, 5, 5), width=2,
            )

    # Top valance
    draw.rectangle([(0, 0), (width, 55)], fill=(170, 22, 22))
    draw.rectangle([(0, 55), (width, 60)], fill=(210, 185, 150))


def draw_stage_floor(draw: ImageDraw, width: int, height: int) -> None:
    """Draw wooden stage floorboards."""
    stage_y = int(height * 0.75)
    draw.rectangle([(0, stage_y), (width, height)], fill=(50, 35, 20))
    # Stage edge
    draw.line([(0, stage_y), (width, stage_y)], fill=(200, 180, 140), width=4)
    # Floorboard lines radiating from center
    cx = width // 2
    for i in range(-12, 13):
        x = cx + i * 50
        draw.line([(x, stage_y), (x + 80, height)], fill=(40, 28, 16), width=1)


def draw_spotlight(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a dramatic spotlight from above, centering on the stage."""
    cx = width // 2
    stage_y = int(height * 0.75)
    spot_top = 0
    spot_top_w = 300
    spot_bot_w = 700

    # Outer glow cone
    points = [
        (cx - spot_top_w // 2, spot_top),
        (cx + spot_top_w // 2, spot_top),
        (cx + spot_bot_w // 2, stage_y),
        (cx - spot_bot_w // 2, stage_y),
    ]
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.polygon(points, fill=(255, 240, 210, 25))
    draw.bitmap((0, 0), overlay, fill=None)

    # Inner beam
    points2 = [
        (cx - spot_top_w // 4, spot_top),
        (cx + spot_top_w // 4, spot_top),
        (cx + spot_bot_w // 3, stage_y),
        (cx - spot_bot_w // 3, stage_y),
    ]
    overlay2 = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    overlay2_draw = ImageDraw.Draw(overlay2)
    overlay2_draw.polygon(points2, fill=(255, 245, 220, 35))
    draw.bitmap((0, 0), overlay2, fill=None)


def draw_ballerina_silhouette(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a silhouetted ballerina in arabesque — the black swan."""
    cx = width // 2
    by = int(height * 0.48)

    # Body — torso
    body_color = (15, 10, 10)
    # Torso
    draw.polygon([
        (cx - 15, by - 20),
        (cx + 15, by - 20),
        (cx + 18, by + 40),
        (cx - 18, by + 40),
    ], fill=body_color)

    # Head
    draw.ellipse([cx - 14, by - 50, cx + 14, by - 20], fill=body_color)

    # Neck
    draw.rectangle([cx - 6, by - 50, cx + 6, by - 20], fill=body_color)

    # Left arm — extended forward in arabesque
    draw.line([
        (cx - 15, by - 5),
        (cx - 60, by - 35),
        (cx - 80, by - 45),
    ], fill=body_color, width=5)
    # Hand extension
    draw.line([cx - 80, by - 45, cx - 90, by - 50], fill=body_color, width=3)

    # Right arm — raised back
    draw.line([
        (cx + 15, by - 5),
        (cx + 55, by - 40),
        (cx + 75, by - 55),
    ], fill=body_color, width=5)
    draw.line([cx + 75, by - 55, cx + 85, by - 62], fill=body_color, width=3)

    # Standing leg
    draw.line([(cx, by + 40), (cx - 5, by + 140)], fill=body_color, width=6)
    # Pointe shoe
    draw.ellipse([cx - 12, by + 130, cx + 4, by + 145], fill=body_color)

    # Back leg — extended in arabesque
    draw.line([
        (cx, by + 40),
        (cx + 40, by + 20),
        (cx + 80, by + 5),
        (cx + 110, by - 5),
    ], fill=body_color, width=5)
    draw.line([cx + 110, by - 5, cx + 120, by - 8], fill=body_color, width=3)

    # Black tutu — layered circles
    tutu_center_x = cx
    tutu_center_y = by + 25
    for r in range(45, 20, -5):
        alpha = 180 - r * 2
        draw.ellipse(
            [tutu_center_x - r, tutu_center_y - r // 2,
             tutu_center_x + r, tutu_center_y + r // 2],
            fill=(10, 8, 8, alpha),
        )

    # Tutu highlight edge
    draw.ellipse(
        [tutu_center_x - 42, tutu_center_y - 18,
         tutu_center_x + 42, tutu_center_y + 18],
        fill=None, outline=(40, 35, 35), width=2,
    )

    # Crown / tiara hint
    crown_y = by - 48
    draw.polygon([
        (cx - 8, crown_y + 4),
        (cx - 5, crown_y - 6),
        (cx - 2, crown_y + 2),
        (cx + 1, crown_y - 8),
        (cx + 4, crown_y + 1),
        (cx + 7, crown_y - 5),
        (cx + 10, crown_y + 4),
    ], fill=(200, 180, 150))


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw dark title panel at bottom with white title text."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    draw.rectangle([(0, panel_top), (width, height)], fill=(10, 8, 8, 240))

    # Gold trim lines at top
    draw.line([(80, panel_top), (width - 80, panel_top)], fill=(200, 170, 60), width=3)
    draw.line([(80, panel_top + 4), (width - 80, panel_top + 4)], fill=(140, 110, 30), width=1)

    # Title
    title_font_size = 88
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    try:
        bbox = draw.textbbox((0, 0), "The Black Swan", font=title_font)
        tw = bbox[2] - bbox[0]
    except Exception:
        tw = 0
    tx = (width - tw) // 2
    ty = panel_top + 70
    draw.text((tx, ty), "The Black Swan", fill=(255, 255, 255), font=title_font)

    # Decorative line under title
    line_y = ty + 105
    draw.line([(int(width * 0.30), line_y), (int(width * 0.70), line_y)], fill=(200, 170, 60), width=2)

    # Small diamond ornament
    diamond_cx = width // 2
    draw.polygon([
        (diamond_cx, line_y - 5),
        (diamond_cx + 5, line_y),
        (diamond_cx, line_y + 5),
        (diamond_cx - 5, line_y),
    ], fill=(200, 170, 60))

    # Author name
    author_font_size = 34
    try:
        author_font = ImageFont.truetype(str(font_paths["author"]), author_font_size)
    except Exception:
        author_font = ImageFont.load_default()

    try:
        abbox = draw.textbbox((0, 0), "Barış Kısır", font=author_font)
        aw = abbox[2] - abbox[0]
    except Exception:
        aw = 0
    ax = (width - aw) // 2
    ay = line_y + 40
    draw.text((ax, ay), "Barış Kısır", fill=(200, 170, 60), font=author_font)

    # Corner ornaments
    cs = 20
    # Top-left corner
    draw.line([(40, panel_top + 10), (40, panel_top + 10 + cs)], fill=(200, 170, 60), width=2)
    draw.line([(40, panel_top + 10), (40 + cs, panel_top + 10)], fill=(200, 170, 60), width=2)
    # Top-right corner
    draw.line([(width - 40, panel_top + 10), (width - 40, panel_top + 10 + cs)], fill=(200, 170, 60), width=2)
    draw.line([(width - 40, panel_top + 10), (width - 40 - cs, panel_top + 10)], fill=(200, 170, 60), width=2)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Black Swan")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background — stage crimson and shadow
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Stage floor
    draw_stage_floor(draw, WIDTH, HEIGHT)

    # Step 3: Curtains
    draw_curtains(draw, WIDTH, HEIGHT)

    # Step 4: Spotlight
    draw_spotlight(draw, WIDTH, HEIGHT)

    # Step 5: Ballerina silhouette — the black swan in arabesque
    draw_ballerina_silhouette(draw, WIDTH, HEIGHT)

    # Step 6: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
    }
    draw_title_panel(draw, WIDTH, HEIGHT, font_paths)

    # Soften
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