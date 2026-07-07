#!/usr/bin/env python3
"""Cover: The Iron Lung — Silver iron lungs in white hospital room, morning light through window, trembling hands on chrome."""

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
    """Sterile white-to-steel-blue gradient like a hospital ward."""
    for y in range(height):
        if y < height * 0.5:
            t = y / (height * 0.5)
            c = lerp_color((240, 245, 250), (200, 210, 220), t)
        else:
            t = (y - height * 0.5) / (height * 0.5)
            c = lerp_color((200, 210, 220), (60, 70, 85), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_iron_lung(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a large iron lung machine as the central image."""
    cx, cy = width // 2, int(height * 0.45)
    w, h = 400, 250

    # Main cylinder body
    draw.rounded_rectangle(
        [cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2],
        radius=30,
        fill=(180, 190, 200),
    )
    # Darker cylinder band
    draw.rounded_rectangle(
        [cx - w // 2 + 20, cy - h // 2 + 20, cx + w // 2 - 20, cy + h // 2 - 20],
        radius=25,
        fill=(160, 170, 180),
    )
    # Porthole window
    draw.ellipse(
        [cx - 60, cy - 60, cx + 60, cy + 60],
        fill=(200, 220, 240),
        outline=(120, 130, 140),
        width=4,
    )
    # Reflection in porthole
    draw.ellipse(
        [cx - 30, cy - 40, cx + 10, cy - 5],
        fill=(220, 235, 255, 120),
    )
    # Collar ring
    draw.rectangle(
        [cx - w // 2 - 10, cy - 30, cx - w // 2 + 15, cy + 30],
        fill=(140, 150, 160),
    )
    # Bellows housing
    draw.rectangle(
        [cx - w // 2 - 80, cy - 40, cx - w // 2 - 10, cy + 40],
        fill=(120, 130, 140),
    )
    # Pressure gauge
    draw.ellipse(
        [cx + w // 2 - 60, cy - 30, cx + w // 2 - 10, cy + 20],
        fill=(220, 225, 230),
        outline=(100, 110, 120),
        width=2,
    )
    # Gauge needle
    draw.line(
        [(cx + w // 2 - 35, cy - 5), (cx + w // 2 - 25, cy - 15)],
        fill=(60, 60, 70),
        width=3,
    )
    # Base/stand
    draw.rectangle(
        [cx - 30, cy + h // 2, cx + 30, cy + h // 2 + 60],
        fill=(100, 110, 120),
    )
    draw.rectangle(
        [cx - 60, cy + h // 2 + 60, cx + 60, cy + h // 2 + 70],
        fill=(80, 90, 100),
    )
    # Wheels
    for wx in [cx - 40, cx + 40]:
        draw.ellipse(
            [wx - 15, cy + h // 2 + 70, wx + 15, cy + h // 2 + 95],
            fill=(60, 65, 70),
        )


def draw_windows(draw: ImageDraw, width: int, height: int) -> None:
    """Draw tall hospital windows in the background."""
    for wx in [200, 500, 1100, 1400]:
        # Window frame
        draw.rectangle(
            [wx, int(height * 0.15), wx + 120, int(height * 0.55)],
            fill=(200, 215, 230),
            outline=(160, 170, 180),
            width=3,
        )
        # Window cross
        draw.line(
            [(wx + 60, int(height * 0.15)), (wx + 60, int(height * 0.55))],
            fill=(160, 170, 180),
            width=2,
        )
        draw.line(
            [(wx, int(height * 0.35)), (wx + 120, int(height * 0.35))],
            fill=(160, 170, 180),
            width=2,
        )
        # Glass reflection
        draw.rectangle(
            [wx + 5, int(height * 0.15) + 5, wx + 55, int(height * 0.34)],
            fill=(220, 235, 250, 80),
        )


def draw_hospital_lines(draw: ImageDraw, width: int, height: int) -> None:
    """Subtle horizontal lines evoking the sterile hospital environment."""
    # Floor line
    draw.line(
        [(0, int(height * 0.65)), (width, int(height * 0.65))],
        fill=(160, 170, 180),
        width=2,
    )
    # Baseboard
    draw.rectangle(
        [(0, int(height * 0.65)), (width, int(height * 0.67))],
        fill=(140, 150, 160),
    )


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark title panel at the bottom with white text for readability."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    draw.rectangle([(0, panel_top), (width, height)], fill=(25, 30, 40))

    # Subtle top border line
    draw.line([(0, panel_top), (width, panel_top)], fill=(80, 90, 110), width=2)

    # Title text
    title = "The Iron\nLung"
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
        y_offset += 95

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
    ay = y_offset + 50
    draw.text((ax, ay), author, fill=(200, 210, 220), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Iron Lung")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Sterile white hospital room: white to pale silver gradient
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(240 - 180 * t)
        g = int(245 - 190 * t)
        b = int(250 - 200 * t)
        draw.line([(0, y), (WIDTH, y)], fill=(max(0, r), max(0, g), max(0, b), 255))

    # Tall hospital windows with morning light
    for wx in [200, 500, 1100, 1400]:
        draw.rectangle([wx, int(HEIGHT * 0.12), wx + 130, int(HEIGHT * 0.50)], fill=(200, 215, 235), outline=(160, 170, 180), width=3)
        draw.line([(wx + 65, int(HEIGHT * 0.12)), (wx + 65, int(HEIGHT * 0.50))], fill=(160, 170, 180), width=2)
        draw.line([(wx, int(HEIGHT * 0.31)), (wx + 130, int(HEIGHT * 0.31))], fill=(160, 170, 180), width=2)
        # Morning light glow
        draw.rectangle([wx + 5, int(HEIGHT * 0.12) + 5, wx + 60, int(HEIGHT * 0.30)], fill=(255, 240, 200, 60))

    # Warm morning light shaft from window
    light = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    ld = ImageDraw.Draw(light)
    ld.polygon([(500, 0), (800, 0), (WIDTH, HEIGHT), (0, HEIGHT)], fill=(255, 240, 200, 12))
    light = light.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, light)
    draw = ImageDraw.Draw(img, "RGBA")

    # Floor line
    draw.line([(0, int(HEIGHT * 0.60)), (WIDTH, int(HEIGHT * 0.60))], fill=(160, 170, 180), width=2)
    draw.rectangle([(0, int(HEIGHT * 0.60)), (WIDTH, int(HEIGHT * 0.62))], fill=(140, 150, 160))

    # Silver iron lung machine (central)
    cx, cy = WIDTH // 2, int(HEIGHT * 0.42)
    w, h = 420, 260
    # Main cylinder
    draw.rounded_rectangle([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2], radius=30, fill=(180, 190, 200))
    draw.rounded_rectangle([cx - w // 2 + 20, cy - h // 2 + 20, cx + w // 2 - 20, cy + h // 2 - 20], radius=25, fill=(160, 170, 180))
    # Porthole
    draw.ellipse([cx - 65, cy - 65, cx + 65, cy + 65], fill=(200, 220, 240), outline=(120, 130, 140), width=4)
    draw.ellipse([cx - 35, cy - 45, cx + 10, cy - 5], fill=(220, 235, 255, 120))
    # Collar
    draw.rectangle([cx - w // 2 - 12, cy - 35, cx - w // 2 + 15, cy + 35], fill=(140, 150, 160))
    # Bellows
    draw.rectangle([cx - w // 2 - 85, cy - 45, cx - w // 2 - 12, cy + 45], fill=(120, 130, 140))
    # Pressure gauge
    draw.ellipse([cx + w // 2 - 65, cy - 35, cx + w // 2 - 10, cy + 25], fill=(220, 225, 230), outline=(100, 110, 120), width=2)
    draw.line([(cx + w // 2 - 38, cy - 5), (cx + w // 2 - 28, cy - 18)], fill=(60, 60, 70), width=3)
    # Chrome base
    draw.rectangle([cx - 35, cy + h // 2, cx + 35, cy + h // 2 + 65], fill=(100, 110, 120))
    draw.rectangle([cx - 65, cy + h // 2 + 65, cx + 65, cy + h // 2 + 75], fill=(80, 90, 100))
    for wx2 in [cx - 45, cx + 45]:
        draw.ellipse([wx2 - 15, cy + h // 2 + 75, wx2 + 15, cy + h // 2 + 100], fill=(60, 65, 70))

    # Trembling hands on chrome (foreground silhouette)
    # Left hand
    lhx, lhy = cx - 100, cy + 50
    draw.ellipse([lhx - 5, lhy - 15, lhx + 5, lhy + 5], fill=(200, 195, 190, 180))
    for i in range(4):
        draw.line((lhx - 3 + i * 2, lhy - 15, lhx - 3 + i * 2, lhy - 30), fill=(200, 195, 190, 180), width=2)
    # Right hand
    rhx, rhy = cx + 100, cy + 50
    draw.ellipse([rhx - 5, rhy - 15, rhx + 5, rhy + 5], fill=(200, 195, 190, 180))
    for i in range(4):
        draw.line((rhx - 3 + i * 2, rhy - 15, rhx - 3 + i * 2, rhy - 30), fill=(200, 195, 190, 180), width=2)
    # Tremor lines
    for _ in range(6):
        tx = cx + int(__import__("random").Random(_).gauss(0, 100))
        ty = cy + 60 + int(__import__("random").Random(_ * 2).gauss(0, 10))
        draw.line((tx - 5, ty, tx + 5, ty), fill=(180, 185, 190, 60), width=1)

    # Tree branch outside window (hope)
    draw.line((200, int(HEIGHT * 0.12), 220, int(HEIGHT * 0.08)), fill=(60, 55, 45, 150), width=4)
    draw.line((210, int(HEIGHT * 0.10), 240, int(HEIGHT * 0.12)), fill=(60, 55, 45, 150), width=3)
    # Tiny leaf buds
    for bx, by in [(218, 78), (238, 118)]:
        draw.ellipse([bx - 3, by - 3, bx + 3, by + 3], fill=(100, 160, 80, 150))

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