#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Milkman's Son."""

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


def draw_dublin_sky(draw: ImageDraw, width: int, height: int) -> None:
    """Morning gray gradient from pale sky to emerald ground to dark street."""
    for y in range(height):
        if y < height * 0.3:
            t = y / (height * 0.3)
            c = lerp_color((200, 200, 195), (160, 170, 165), t)
        elif y < height * 0.55:
            t = (y - height * 0.3) / (height * 0.25)
            c = lerp_color((160, 170, 165), (100, 125, 110), t)
        elif y < height * 0.75:
            t = (y - height * 0.55) / (height * 0.2)
            c = lerp_color((100, 125, 110), (45, 55, 50), t)
        else:
            t = (y - height * 0.75) / (height * 0.25)
            c = lerp_color((45, 55, 50), (20, 25, 22), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_georgian_doors(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a row of Georgian doorways along the street level."""
    door_colors = [
        (180, 50, 40),   # red
        (50, 80, 50),    # green
        (40, 50, 80),    # blue
        (100, 60, 40),   # brown
        (60, 40, 60),    # purple
    ]

    door_y_base = int(height * 0.72)
    door_h = int(height * 0.10)
    door_w = 50
    spacing = 140
    start_x = (width - (len(door_colors) * spacing)) // 2

    for i, dcolor in enumerate(door_colors):
        x = start_x + i * spacing

        # Door frame (dark)
        draw.rectangle(
            [x - door_w // 2 - 4, door_y_base - door_h - 4, x + door_w // 2 + 4, door_y_base + 4],
            fill=(30, 25, 20),
        )

        # Door panel
        draw.rectangle(
            [x - door_w // 2, door_y_base - door_h, x + door_w // 2, door_y_base],
            fill=dcolor,
        )

        # Fanlight (semi-circular window above door)
        fan_center = (x, door_y_base - door_h)
        fan_radius = door_w // 2 + 8
        draw.pieslice(
            [fan_center[0] - fan_radius, fan_center[1] - fan_radius, fan_center[0] + fan_radius, fan_center[1]],
            0, 180, fill=(180, 200, 210),
        )

        # Fanlight divisions
        for angle in range(30, 180, 30):
            rad = math.radians(angle)
            ex = fan_center[0] + int(fan_radius * math.cos(rad))
            ey = fan_center[1] - int(fan_radius * math.sin(rad))
            draw.line([fan_center, (ex, ey)], fill=(200, 210, 220), width=1)

        # Step
        draw.rectangle(
            [x - door_w // 2 - 10, door_y_base, x + door_w // 2 + 10, door_y_base + 12],
            fill=(80, 75, 70),
        )

        # Number plaque
        plaque_x = x - 12
        plaque_y = door_y_base - door_h + 15
        draw.rectangle([plaque_x, plaque_y, plaque_x + 24, plaque_y + 16], fill=(180, 170, 140))
        draw.rectangle([plaque_x, plaque_y, plaque_x + 24, plaque_y + 16], outline=(60, 50, 40), width=1)


def draw_milk_float(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a milk float (horse and cart) on the street."""
    float_x = width // 2 + 100
    float_y = int(height * 0.78)

    # Cart body
    cart_w, cart_h = 140, 60
    draw.rectangle(
        [float_x - cart_w // 2, float_y - cart_h, float_x + cart_w // 2, float_y],
        fill=(50, 55, 50),
    )
    draw.rectangle(
        [float_x - cart_w // 2, float_y - cart_h, float_x + cart_w // 2, float_y],
        outline=(80, 85, 80),
        width=2,
    )

    # Milk bottles on cart
    for bx in range(float_x - 40, float_x + 45, 22):
        for by in range(float_y - cart_h + 8, float_y - 5, 18):
            draw.rectangle([bx, by, bx + 10, by + 12], fill=(220, 230, 240))
            draw.rectangle([bx + 2, by + 2, bx + 8, by + 10], fill=(200, 215, 230))

    # Wheels
    wheel_radius = 20
    for wx in [float_x - 45, float_x + 45]:
        draw.ellipse(
            [wx - wheel_radius, float_y - 3, wx + wheel_radius, float_y + wheel_radius * 2 - 3],
            fill=(40, 35, 30),
        )
        draw.ellipse(
            [wx - wheel_radius + 3, float_y, wx + wheel_radius - 3, float_y + wheel_radius * 2 - 6],
            fill=(60, 55, 50),
        )
        # Spokes
        for angle in range(0, 360, 60):
            rad = math.radians(angle)
            sx = wx + int((wheel_radius - 5) * math.cos(rad))
            sy = float_y + wheel_radius - 3 + int((wheel_radius - 5) * math.sin(rad))
            draw.line([(wx, float_y + wheel_radius - 3), (sx, sy)], fill=(30, 25, 20), width=2)

    # Horse body
    hx = float_x - 120
    hy = float_y - 15

    # Body
    draw.ellipse([hx - 40, hy - 30, hx + 20, hy + 10], fill=(60, 65, 60))
    # Neck
    draw.polygon([(hx - 10, hy - 25), (hx - 20, hy - 55), (hx + 5, hy - 50), (hx + 10, hy - 20)], fill=(60, 65, 60))
    # Head
    draw.ellipse([hx - 35, hy - 60, hx - 10, hy - 35], fill=(65, 70, 65))
    # Eye
    draw.ellipse([hx - 28, hy - 52, hx - 23, hy - 47], fill=(20, 20, 20))
    draw.ellipse([hx - 27, hy - 51, hx - 24, hy - 48], fill=(50, 50, 50))
    # Ear
    draw.polygon([(hx - 20, hy - 58), (hx - 18, hy - 68), (hx - 12, hy - 58)], fill=(50, 55, 50))
    # Legs
    for lx in [hx - 30, hx - 10, hx, hx + 15]:
        draw.line([(lx, hy + 5), (lx - 3, hy + 35)], fill=(50, 55, 50), width=6)
    # Tail
    draw.line([(hx + 15, hy - 10), (hx + 35, hy - 5), (hx + 30, hy + 10)], fill=(45, 50, 45), width=4)
    # Shaft
    draw.line([(hx + 10, hy), (float_x - 50, float_y - 20)], fill=(60, 55, 45), width=5)


def draw_lampposts(draw: ImageDraw, width: int, height: int) -> None:
    """Draw period lampposts along the street."""
    for lx in [width * 0.15, width * 0.55, width * 0.85]:
        lx = int(lx)
        ly = int(height * 0.72)

        # Post
        draw.rectangle([lx - 3, ly - 120, lx + 3, ly], fill=(40, 40, 45))

        # Lamp housing
        draw.polygon(
            [(lx - 15, ly - 120), (lx + 15, ly - 120), (lx + 12, ly - 105), (lx - 12, ly - 105)],
            fill=(50, 50, 55),
        )
        # Glow
        draw.ellipse(
            [lx - 10, ly - 118, lx + 10, ly - 107],
            fill=(240, 220, 150, 100),
        )

        # Base
        draw.rectangle([lx - 8, ly, lx + 8, ly + 15], fill=(40, 40, 45))
        draw.rectangle([lx - 15, ly + 12, lx + 15, ly + 18], fill=(35, 35, 40))

        # Light cone faint glow
        glow_alpha = 30
        for i in range(3):
            gx = lx
            gy = ly - 105
            gw = 80 + i * 40
            draw.ellipse(
                [gx - gw // 2, gy, gx + gw // 2, gy + 40 + i * 20],
                fill=(240, 230, 180, glow_alpha // (i + 1)),
            )


def draw_cobbles(draw: ImageDraw, width: int, height: int) -> None:
    """Draw cobblestone texture on the street."""
    y_start = int(height * 0.72)
    rng = __import__("random").Random(42)

    for row in range(8):
        y = y_start + row * 14
        offset = 7 if row % 2 else 0
        for col in range(width // 16 + 2):
            x = col * 16 + offset
            brightness = rng.randint(40, 60)
            shape = rng.choice(["round", "rect"])
            if shape == "round":
                draw.ellipse([x, y, x + 12, y + 10], fill=(brightness, brightness + 2, brightness - 2))
            else:
                draw.rectangle([x, y, x + 11, y + 9], fill=(brightness, brightness + 2, brightness - 2))


def draw_morning_light(draw: ImageDraw, width: int, height: int) -> None:
    """Add a subtle light effect from upper left."""
    import math

    cx, cy = width * 0.3, height * 0.1
    for r in range(200, 600, 30):
        alpha = max(0, 25 - (r - 200) // 16)
        if alpha <= 0:
            continue
        draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            fill=(240, 230, 200, alpha),
        )


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom with WHITE text."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    draw.rectangle([(0, panel_top), (width, height)], fill=(20, 22, 25, 230))

    # Subtle top border - emerald line
    draw.line([(0, panel_top), (width, panel_top)], fill=(70, 130, 90), width=3)

    # Title text
    title = "The Milkman's\nSon"
    title_font_size = 80
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    lines = title.split("\n")
    y_offset = panel_top + 70
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 0
        tx = (width - tw) // 2
        draw.text((tx, y_offset), line, fill=(255, 255, 255), font=title_font)
        y_offset += 100

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
    draw.text((ax, ay), author, fill=(200, 200, 200), font=author_font)

    # Subtitle line: "DUBLIN 1980s"
    subtitle = "DUBLIN 1980s"
    sub_font_size = 22
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
    sy = ay + 50
    draw.text((sx, sy), subtitle, fill=(120, 180, 140), font=sub_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Milkman's Son")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background - Dublin morning sky
    draw_dublin_sky(draw, WIDTH, HEIGHT)

    # Step 2: Cobblestone street
    draw_cobbles(draw, WIDTH, HEIGHT)

    # Step 3: Georgian doors
    draw_georgian_doors(draw, WIDTH, HEIGHT)

    # Step 4: Lampposts
    draw_lampposts(draw, WIDTH, HEIGHT)

    # Step 5: Milk float with horse
    draw_milk_float(draw, WIDTH, HEIGHT)

    # Step 6: Morning light effect
    draw_morning_light(draw, WIDTH, HEIGHT)

    # Step 7: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
        "small": str(FONTS_DIR / "arial.ttf"),
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