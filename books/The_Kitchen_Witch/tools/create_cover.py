#!/usr/bin/env python3
"""Cover: The Kitchen Witch — Village square with timber buildings, bakery with glowing display of steaming bread, warm amber/timber brown/bread gold."""

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
    """Warm amber-to-sage gradient for cozy bakery feel."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((80, 50, 30), ((160, 120, 60)), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((160, 120, 60), ((100, 130, 80)), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((100, 130, 80), ((60, 80, 50)), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_village_square(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a small village square with cobblestones and buildings."""
    # Ground / cobblestones
    for i in range(20):
        cx = 100 + i * 75 + (i % 3) * 10
        cy = int(height * 0.58) + (i % 4) * 8
        r = 8 + (i % 3) * 2
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 100, 80, 150))
        draw.ellipse([cx - r // 2, cy - r // 2, cx + r // 2, cy + r // 2], fill=(100, 85, 65, 100))

    # Left building
    # Wall
    draw.rectangle([50, int(height * 0.35), 300, int(height * 0.58)], fill=(140, 110, 85))
    # Roof
    draw.polygon([(30, int(height * 0.35)), (175, int(height * 0.22)), (320, int(height * 0.35))], fill=(90, 60, 40))
    # Windows
    draw.rectangle([90, int(height * 0.40), 140, int(height * 0.48)], fill=(255, 200, 100, 200))
    draw.rectangle([200, int(height * 0.40), 250, int(height * 0.48)], fill=(255, 200, 100, 200))
    # Window glow
    for wx, wy in [(90, int(height * 0.40)), (200, int(height * 0.40))]:
        draw.rectangle([wx - 2, wy - 2, wx + 50, wy + 60], outline=(255, 220, 150, 80), width=2)

    # Right building
    draw.rectangle([width - 320, int(height * 0.38), width - 50, int(height * 0.58)], fill=(130, 100, 80))
    draw.polygon([(width - 340, int(height * 0.38)), (width - 185, int(height * 0.25)), (width - 30, int(height * 0.38))], fill=(80, 55, 35))
    # Window with warm light
    draw.rectangle([width - 250, int(height * 0.42), width - 200, int(height * 0.50)], fill=(255, 210, 120, 200))
    draw.rectangle([width - 160, int(height * 0.42), width - 110, int(height * 0.50)], fill=(255, 210, 120, 200))

    # Center fountain
    fx, fy = width // 2, int(height * 0.52)
    draw.ellipse([fx - 40, fy - 15, fx + 40, fy + 15], fill=(150, 140, 130))
    draw.ellipse([fx - 30, fy - 25, fx + 30, fy - 10], fill=(170, 200, 220, 180))
    draw.rectangle([fx - 4, fy - 35, fx + 4, fy - 25], fill=(140, 130, 120))
    draw.ellipse([fx - 8, fy - 40, fx + 8, fy - 32], fill=(160, 150, 140))


def draw_bakery_shop(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the central bakery with warm glowing windows."""
    cx, cy = width // 2, int(height * 0.50)

    # Shop front
    shop_w, shop_h = 260, 300
    sx, sy = cx - shop_w // 2, cy - shop_h // 2

    # Wall
    draw.rectangle([sx, sy, sx + shop_w, sy + shop_h], fill=(160, 120, 80))

    # Door
    draw.rectangle([cx - 25, sy + shop_h - 140, cx + 25, sy + shop_h], fill=(80, 55, 35))
    draw.ellipse([cx + 15, sy + shop_h - 70, cx + 20, sy + shop_h - 65], fill=(255, 200, 100))

    # Large display window
    draw.rectangle([sx + 20, sy + 30, sx + shop_w - 20, sy + 160], fill=(255, 220, 130, 220))
    # Window frame
    draw.rectangle([sx + 20, sy + 30, sx + shop_w - 20, sy + 160], outline=(100, 75, 50), width=3)
    draw.line([cx, sy + 30, cx, sy + 160], fill=(100, 75, 50), width=2)

    # Signboard above door
    sign_y = sy - 15
    draw.rectangle([cx - 70, sign_y - 20, cx + 70, sign_y + 5], fill=(60, 40, 25))
    draw.rectangle([cx - 70, sign_y - 20, cx + 70, sign_y + 5], outline=(200, 180, 140), width=1)

    # Awning
    for aw_x in range(sx, sx + shop_w, 30):
        draw.polygon(
            [(aw_x, sy - 5), (aw_x + 25, sy - 5), (aw_x + 12, sy - 30), (aw_x - 5, sy - 25)],
            fill=(140, 50, 40, 180),
        )


def draw_pies(draw: ImageDraw, width: int, height: int) -> None:
    """Draw steaming pies in the display window."""
    import random

    rng = random.Random(17)
    cx = width // 2
    sy = int(height * 0.41)

    pie_positions = [
        (cx - 70, sy + 20, 25),
        (cx + 20, sy + 30, 20),
        (cx - 40, sy + 50, 30),
        (cx + 50, sy + 60, 22),
    ]

    for px, py, size in pie_positions:
        # Pie body
        draw.ellipse([px - size, py - size // 2, px + size, py + size // 2], fill=(200, 150, 80))
        draw.ellipse([px - size + 3, py - size // 2 - 2, px + size - 3, py + size // 2 + 2], fill=(180, 130, 60))
        # Lattice crust (simplified)
        draw.line([px - size + 5, py, px + size - 5, py], fill=(160, 100, 40), width=2)
        draw.line([px, py - size // 4, px, py + size // 4], fill=(160, 100, 40), width=2)
        # Steam
        for s in range(3):
            sx = px + rng.randint(-8, 8)
            sy_s = py - size // 2 - 5 - s * 8
            draw.ellipse(
                [sx - 3 - s, sy_s - 2, sx + 3 + s, sy_s + 2],
                fill=(220, 210, 200, 100 - s * 25),
            )


def draw_village_lights(draw: ImageDraw, width: int, height: int) -> None:
    """Draw warm ambient light particles and stars."""
    import random

    rng = random.Random(23)

    # Warm light particles
    for _ in range(60):
        x = rng.randint(100, width - 100)
        y = rng.randint(50, int(height * 0.35))
        size = rng.randint(2, 5)
        brightness = rng.randint(100, 200)
        draw.ellipse([x - size, y - size, x + size, y + size], fill=(brightness, brightness, 180, 120))
        # Glow
        draw.ellipse([x - size * 2, y - size * 2, x + size * 2, y + size * 2], fill=(brightness, brightness, 200, 30))

    # Lamplight posts
    for lx in [120, width - 120]:
        ly = int(height * 0.48)
        draw.rectangle([lx - 3, ly, lx + 3, ly + 80], fill=(60, 55, 45))
        draw.ellipse([lx - 12, ly - 10, lx + 12, ly + 8], fill=(255, 200, 100, 200))
        # Lamp glow
        for g in range(3):
            glow_size = 20 + g * 15
            draw.ellipse(
                [lx - glow_size, ly - glow_size, lx + glow_size, ly + glow_size],
                fill=(255, 200, 100, 20 - g * 5),
            )


def draw_title_panel(draw: ImageDraw, draw_img: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom with white text."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark semi-transparent
    draw.rectangle([(0, panel_top), (width, height)], fill=(40, 30, 20, 230))

    # Subtle top border
    draw.line([(0, panel_top), (width, panel_top)], fill=(180, 150, 100), width=2)

    # Title text
    title = "The Kitchen Witch"
    title_font_size = 82
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

    # Subtitle line
    subtitle = "A Cozy Fantasy"
    sub_font_size = 30
    try:
        sub_font = ImageFont.truetype(str(font_paths["small"]), sub_font_size)
    except Exception:
        sub_font = ImageFont.load_default()

    try:
        sbbox = draw.textbbox((0, 0), subtitle, font=sub_font)
        sw = sbbox[2] - sbbox[0]
    except Exception:
        sw = 0
    sx = (width - sw) // 2
    sy = ty + 100
    draw.text((sx, sy), subtitle, fill=(200, 180, 140), font=sub_font)

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
    ay = sy + 70
    draw.text((ax, ay), author, fill=(255, 255, 255), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Kitchen Witch")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    rng = __import__("random").Random(13)

    # Warm amber to timber brown gradient
    for y in range(HEIGHT):
        t = y / HEIGHT
        if t < 0.3:
            r, g, b = 80 + 120 * (t / 0.3), 50 + 80 * (t / 0.3), 30 + 40 * (t / 0.3)
        elif t < 0.6:
            r, g, b = 200 - 60 * ((t - 0.3) / 0.3), 130 - 40 * ((t - 0.3) / 0.3), 70 - 20 * ((t - 0.3) / 0.3)
        else:
            r, g, b = 140 - 80 * ((t - 0.6) / 0.4), 90 - 50 * ((t - 0.6) / 0.4), 50 - 30 * ((t - 0.6) / 0.4)
        draw.line([(0, y), (WIDTH, y)], fill=(max(0, int(r)), max(0, int(g)), max(0, int(b)), 255))

    # Timber buildings (left and right)
    # Left building
    draw.rectangle([(50, int(HEIGHT * 0.30)), (350, int(HEIGHT * 0.55))], fill=(130, 100, 80))
    draw.polygon([(30, int(HEIGHT * 0.30)), (200, int(HEIGHT * 0.18)), (370, int(HEIGHT * 0.30))], fill=(80, 55, 40))
    # Timber frame lines
    draw.line((50, int(HEIGHT * 0.30), 350, int(HEIGHT * 0.30)), fill=(60, 40, 30), width=3)
    for lx in [100, 200, 300]:
        draw.line((lx, int(HEIGHT * 0.30), lx, int(HEIGHT * 0.55)), fill=(60, 40, 30), width=3)
    # Windows
    draw.rectangle([(90, int(HEIGHT * 0.35)), (140, int(HEIGHT * 0.42))], fill=(255, 200, 100, 200))
    draw.rectangle([(250, int(HEIGHT * 0.35)), (300, int(HEIGHT * 0.42))], fill=(255, 200, 100, 200))

    # Right building
    draw.rectangle([(WIDTH - 370, int(HEIGHT * 0.33)), (WIDTH - 50, int(HEIGHT * 0.55))], fill=(120, 90, 75))
    draw.polygon([(WIDTH - 390, int(HEIGHT * 0.33)), (WIDTH - 210, int(HEIGHT * 0.21)), (WIDTH - 30, int(HEIGHT * 0.33))], fill=(75, 50, 35))
    for lx in [WIDTH - 300, WIDTH - 200]:
        draw.line((lx, int(HEIGHT * 0.33), lx, int(HEIGHT * 0.55)), fill=(55, 35, 25), width=3)

    # Central bakery (glowing display)
    bx, by = WIDTH // 2 - 120, int(HEIGHT * 0.40)
    # Shop wall
    draw.rectangle([bx, by, bx + 240, by + 280], fill=(150, 110, 75))
    # Roof
    draw.polygon([(bx - 15, by), (bx + 120, by - 50), (bx + 255, by)], fill=(85, 55, 40))
    # Awning
    for ax in range(bx, bx + 240, 30):
        draw.polygon([(ax, by - 5), (ax + 25, by - 5), (ax + 12, by - 25), (ax - 5, by - 20)], fill=(160, 60, 50, 200))
    # Display window (steaming bread glow)
    draw.rectangle([bx + 15, by + 25, bx + 225, by + 150], fill=(255, 220, 130, 230))
    draw.rectangle([bx + 15, by + 25, bx + 225, by + 150], outline=(90, 65, 45), width=3)
    draw.line([bx + 120, by + 25, bx + 120, by + 150], fill=(90, 65, 45), width=2)
    # Bread loaves in window
    for pi, (px, py) in enumerate([(bx + 40, by + 60), (bx + 100, by + 55), (bx + 160, by + 65), (bx + 70, by + 100), (bx + 140, by + 105)]):
        draw.ellipse([px - 20, py - 12, px + 20, py + 12], fill=(200, 150, 70))
        draw.ellipse([px - 17, py - 10, px + 17, py + 10], fill=(180, 130, 55))
    # Steam from bread
    for s in range(20):
        sx = bx + 40 + int(rng.random() * 160)
        sy = by + 30 - int(rng.random() * 80)
        ss = 8 + int(rng.random() * 15)
        draw.ellipse([sx - ss // 2, sy - ss // 4, sx + ss // 2, sy + ss // 4], fill=(220, 210, 200, 30 + int(rng.random() * 40)))

    # Warm glow from bakery
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([bx - 40, by - 20, bx + 280, by + 300], fill=(255, 200, 100, 25))
    glow = glow.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Cobblestone ground
    for i in range(30):
        cx = 80 + i * 50 + rng.randint(0, 20)
        cy = int(HEIGHT * 0.55) + rng.randint(0, 40)
        r = 6 + rng.randint(0, 4)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(110, 90, 75, 120))
        draw.ellipse([cx - r // 2, cy - r // 2, cx + r // 2, cy + r // 2], fill=(90, 75, 60, 80))

    # Warm light particles
    for _ in range(50):
        lx = int(rng.random() * WIDTH)
        ly = int(rng.random() * int(HEIGHT * 0.4))
        ls = rng.randint(2, 4)
        draw.ellipse([lx - ls, ly - ls, lx + ls, ly + ls], fill=(255, 200, 100, rng.randint(60, 150)))

    # Lampposts
    for lx in [100, WIDTH - 100]:
        ly = int(HEIGHT * 0.48)
        draw.rectangle([lx - 3, ly, lx + 3, ly + 80], fill=(55, 50, 40))
        draw.ellipse([lx - 10, ly - 8, lx + 10, ly + 6], fill=(255, 200, 100, 200))
        for g in range(3):
            gs = 18 + g * 12
            draw.ellipse([lx - gs, ly - gs, lx + gs, ly + gs], fill=(255, 200, 100, 15 - g * 4))

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