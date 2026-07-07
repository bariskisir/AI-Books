#!/usr/bin/env python3
"""Cover: Child silhouetted against twilight, shadowy monster figure fading into mist, twilight purple/monster shadow/mist gray."""

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
    """Deep twilight gradient: dark purple to warm horizon glow."""
    for y in range(height):
        t = y / height
        if t < 0.3:
            c = lerp_color((15, 8, 30), (40, 15, 50), t / 0.3)
        elif t < 0.55:
            c = lerp_color((40, 15, 50), (80, 30, 70), (t - 0.3) / 0.25)
        elif t < 0.75:
            c = lerp_color((80, 30, 70), (120, 60, 90), (t - 0.55) / 0.2)
        else:
            c = lerp_color((120, 60, 90), (60, 40, 50), (t - 0.75) / 0.25)
        draw.line([(0, y), (width, y)], fill=c)


def draw_twilight_landscape(draw: ImageDraw, width: int, height: int) -> None:
    """Twilight landscape with distant hills and fading light."""
    # Distant hills
    hill_pts = []
    for x in range(0, width + 10, 8):
        hy = 600 + int(30 * math.sin(x * 0.005) + 20 * math.sin(x * 0.012))
        hill_pts.append((x, hy))
    hill_pts.append((width, height))
    hill_pts.append((0, height))
    draw.polygon(hill_pts, fill=(20, 12, 25))

    # Nearer hills
    hill2_pts = []
    for x in range(0, width + 10, 6):
        hy = 800 + int(20 * math.sin(x * 0.008 + 1) + 15 * math.sin(x * 0.015))
        hill2_pts.append((x, hy))
    hill2_pts.append((width, height))
    hill2_pts.append((0, height))
    draw.polygon(hill2_pts, fill=(30, 18, 35))

    # Ground
    draw.rectangle([(0, 1000), (width, height)], fill=(35, 22, 30))


def draw_child_silhouette(draw: ImageDraw, width: int, height: int) -> None:
    """Child silhouetted against twilight sky."""
    cx, base = width // 2, 1000
    dark = (15, 10, 18)

    # Shadow on ground
    draw.ellipse([cx - 20, base - 3, cx + 20, base + 3], fill=(20, 14, 22, 100))

    # Legs
    draw.line([(cx - 8, base), (cx - 10, base - 80)], fill=dark, width=10)
    draw.line([(cx + 8, base), (cx + 10, base - 80)], fill=dark, width=10)

    # Body
    draw.ellipse([cx - 22, base - 160, cx + 22, base - 85], fill=dark)

    # Arms
    draw.line([(cx - 22, base - 130), (cx - 50, base - 100)], fill=dark, width=7)
    draw.line([(cx + 22, base - 130), (cx + 50, base - 100)], fill=dark, width=7)

    # Head
    draw.ellipse([cx - 16, base - 205, cx + 16, base - 165], fill=dark)

    # Hair tufts
    for i in range(6):
        hx = cx - 15 + i * 6
        hy = base - 210 + int(5 * math.sin(i * 1.5))
        draw.ellipse([hx - 4, hy - 4, hx + 4, hy + 4], fill=(12, 8, 15))

    # Glow around child (rim light from twilight)
    for r in range(30, 0, -3):
        a = max(2, 25 - (30 - r) * 2)
        draw.ellipse([cx - r - 5, base - 210 - r, cx + r + 5, base - 100 + r],
                     fill=(120, 60, 90, a))


def draw_monster_fading(draw: ImageDraw, width: int, height: int) -> None:
    """Shadowy monster figure fading into mist at the forest edge."""
    mx, my = 1200, 850
    dark = (25, 18, 30)
    faint = 80  # alpha value for fading effect

    # Tall looming shape fading into mist
    draw.ellipse([mx - 50, my - 200, mx + 50, my - 60], fill=(*dark, faint))
    draw.line([(mx, my - 60), (mx, my + 20)], fill=(*dark, faint - 20), width=30)
    # Head / horns
    draw.ellipse([mx - 30, my - 250, mx + 30, my - 200], fill=(*dark, faint))
    # Horns
    draw.polygon([(mx - 20, my - 240), (mx - 30, my - 280), (mx - 10, my - 250)],
                 fill=(*dark, faint - 10))
    draw.polygon([(mx + 20, my - 240), (mx + 30, my - 280), (mx + 10, my - 250)],
                 fill=(*dark, faint - 10))
    # Glowing eyes
    draw.ellipse([mx - 15, my - 235, mx - 5, my - 225], fill=(180, 200, 220, faint))
    draw.ellipse([mx + 5, my - 235, mx + 15, my - 225], fill=(180, 200, 220, faint))

    # Mist rising around the monster
    mist_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    md = ImageDraw.Draw(mist_layer)
    for _ in range(25):
        mcx = mx + random.randint(-80, 80)
        mcy = my + random.randint(-60, 40)
        mr = random.randint(20, 60)
        md.ellipse([mcx - mr, mcy - mr, mcx + mr, mcy + mr],
                   fill=(120, 100, 130, random.randint(15, 35)))
    mist_layer = mist_layer.filter(ImageFilter.GaussianBlur(8))
    draw.bitmap((0, 0), mist_layer, fill=None)

    # Extra wisps of mist
    for _ in range(10):
        wx = mx + random.randint(-100, 100)
        wy = my + random.randint(-80, 60)
        wr = random.randint(15, 35)
        draw.ellipse([wx - wr, wy - wr, wx + wr, wy + wr], fill=(130, 110, 140, random.randint(10, 25)))


def draw_stars(draw: ImageDraw, width: int, height: int) -> None:
    """Draw scattered stars in the twilight sky."""
    rng = random.Random(42)
    for _ in range(80):
        x = rng.randint(20, width - 20)
        y = rng.randint(10, int(height * 0.35))
        size = rng.randint(1, 3)
        bright = rng.randint(100, 200)
        draw.ellipse([x - size, y - size, x + size, y + size], fill=(bright, bright, bright, 150))


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom of the cover with white text."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark semi-transparent rectangle
    draw.rectangle([(0, panel_top), (width, height)], fill=(20, 10, 30, 220))

    # Add a subtle border at top of panel
    draw.line([(0, panel_top), (width, panel_top)], fill=(100, 70, 130), width=3)

    # Title text
    title = "The Truth About\nMonsters"
    title_font_size = 72
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered - WHITE text on dark panel
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
    draw.text((ax, ay), author, fill=(200, 180, 220), font=author_font)

    # Tagline
    tagline = "A Children's Fantasy"
    try:
        tag_font = ImageFont.truetype(str(font_paths["small"]), 24)
    except Exception:
        tag_font = ImageFont.load_default()

    try:
        tbbox = draw.textbbox((0, 0), tagline, font=tag_font)
        tw = tbbox[2] - tbbox[0]
    except Exception:
        tw = 0
    tx = (width - tw) // 2
    draw.text((tx, ay + 55), tagline, fill=(180, 160, 200), font=tag_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Truth About Monsters")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Twilight gradient
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Stars in the sky
    draw_stars(draw, WIDTH, HEIGHT)

    # Step 3: Twilight landscape
    draw_twilight_landscape(draw, WIDTH, HEIGHT)

    # Step 4: Child silhouette
    draw_child_silhouette(draw, WIDTH, HEIGHT)

    # Step 5: Shadowy monster fading into mist
    draw_monster_fading(draw, WIDTH, HEIGHT)

    # Step 6: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
        "small": str(FONTS_DIR / "arial.ttf"),
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