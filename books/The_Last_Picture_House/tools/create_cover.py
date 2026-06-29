#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Last Picture House."""

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


def draw_dusk_gradient(draw: ImageDraw, width: int, height: int) -> None:
    """Amber sky to dusty rose to purple dusk gradient for a small-town evening feel."""
    for y in range(height):
        if y < height * 0.35:
            t = y / (height * 0.35)
            c = lerp_color((255, 200, 120), (220, 140, 100), t)
        elif y < height * 0.6:
            t = (y - height * 0.35) / (height * 0.25)
            c = lerp_color((220, 140, 100), (180, 90, 100), t)
        elif y < height * 0.8:
            t = (y - height * 0.6) / (height * 0.2)
            c = lerp_color((180, 90, 100), (80, 40, 60), t)
        else:
            t = (y - height * 0.8) / (height * 0.2)
            c = lerp_color((80, 40, 60), (20, 10, 20), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_main_street(draw: ImageDraw, width: int, height: int) -> None:
    """Draw an empty main street receding into the distance."""
    # Road - perspective trapezoid
    road_top_w = 80
    road_bot_w = 600
    road_top_y = int(height * 0.50)
    road_bot_y = int(height * 0.75)

    # Draw road surface
    draw.polygon(
        [
            (width // 2 - road_top_w // 2, road_top_y),
            (width // 2 + road_top_w // 2, road_top_y),
            (width // 2 + road_bot_w // 2, road_bot_y),
            (width // 2 - road_bot_w // 2, road_bot_y),
        ],
        fill=(60, 55, 50),
    )

    # Center line dashes
    for dy in range(0, road_bot_y - road_top_y, 30):
        t = dy / (road_bot_y - road_top_y)
        line_w = max(2, int(road_top_w + (road_bot_w - road_top_w) * t) // 30)
        cx = width // 2
        ly = road_top_y + dy
        draw.line([(cx - line_w, ly), (cx + line_w, ly)], fill=(200, 190, 160), width=2)

    # Street lamps (simple poles with glowing bulbs)
    lamp_positions = [
        (width // 2 - 250, 0.65),
        (width // 2 + 250, 0.65),
        (width // 2 - 400, 0.58),
        (width // 2 + 400, 0.58),
    ]
    for lx, lyt in lamp_positions:
        ly = int(height * lyt)
        pole_h = int(height * 0.18)
        # Pole
        draw.rectangle([lx - 3, ly - pole_h, lx + 3, ly], fill=(40, 40, 45))
        # Lamp head
        draw.ellipse([lx - 10, ly - pole_h - 8, lx + 10, ly - pole_h + 8], fill=(255, 220, 150))
        # Glow
        for r in range(3):
            alpha = max(0, 80 - r * 25)
            draw.ellipse(
                [lx - 30 - r * 20, ly - pole_h - 30 - r * 20, lx + 30 + r * 20, ly - pole_h + 30 + r * 20],
                fill=(255, 220, 150, alpha),
            )


def draw_storefronts(draw: ImageDraw, width: int, height: int) -> None:
    """Draw empty storefronts lining Main Street."""
    # Left side buildings
    for i, (bx, by, bw, bh) in enumerate([
        (30, int(height * 0.38), 220, int(height * 0.37)),
        (280, int(height * 0.40), 180, int(height * 0.35)),
        (490, int(height * 0.42), 150, int(height * 0.33)),
    ]):
        # Building facade
        facade_color = (70 + i * 10, 60 + i * 5, 55 - i * 5)
        draw.rectangle([bx, by, bx + bw, by + bh], fill=facade_color)
        # Roofline
        draw.polygon(
            [(bx - 10, by), (bx + bw // 2, by - 25), (bx + bw + 10, by)],
            fill=(40 + i * 8, 35 + i * 5, 30),
        )
        # Dark windows
        for wx in range(bx + 20, bx + bw - 20, 35):
            for wy in range(by + 30, by + bh // 3, 40):
                draw.rectangle([wx, wy, wx + 25, wy + 30], fill=(15, 15, 20))
                draw.rectangle([wx, wy, wx + 25, wy + 30], outline=(40, 40, 45), width=1)
        # Dark display window at bottom
        draw.rectangle([bx + 15, by + bh - 80, bx + bw - 15, by + bh - 10], fill=(20, 18, 22))
        # Signage rectangle (empty)
        sign_y = by + bh // 3 + 10
        draw.rectangle([bx + 10, sign_y, bx + bw - 10, sign_y + 20], fill=(40, 35, 38))

    # Right side buildings
    for i, (bx, by, bw, bh) in enumerate([
        (width - 220, int(height * 0.37), 200, int(height * 0.38)),
        (width - 450, int(height * 0.41), 160, int(height * 0.34)),
        (width - 640, int(height * 0.43), 140, int(height * 0.32)),
    ]):
        facade_color = (65 + i * 12, 55 + i * 8, 50 - i * 3)
        draw.rectangle([bx, by, bx + bw, by + bh], fill=facade_color)
        # Roofline
        draw.polygon(
            [(bx - 10, by), (bx + bw // 2, by - 20), (bx + bw + 10, by)],
            fill=(35 + i * 10, 30 + i * 8, 25),
        )
        # Dark windows
        for wx in range(bx + 20, bx + bw - 20, 35):
            for wy in range(by + 30, by + bh // 3, 40):
                draw.rectangle([wx, wy, wx + 25, wy + 30], fill=(12, 12, 18))
                draw.rectangle([wx, wy, wx + 25, wy + 30], outline=(38, 38, 42), width=1)
        # Display window
        draw.rectangle([bx + 15, by + bh - 75, bx + bw - 15, by + bh - 10], fill=(18, 16, 20))
        # Sign
        sign_y = by + bh // 3 + 10
        draw.rectangle([bx + 10, sign_y, bx + bw - 10, sign_y + 18], fill=(38, 33, 36))


def draw_marquee(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the art deco theater marquee as the focal point."""
    mx, mw = width // 2, 340
    my = int(height * 0.20)
    mh = int(height * 0.18)

    # Main marquee body - trapezoid for perspective
    top_mw, bot_mw = mw, mw + 60
    draw.polygon(
        [
            (mx - top_mw // 2, my),
            (mx + top_mw // 2, my),
            (mx + bot_mw // 2, my + mh),
            (mx - bot_mw // 2, my + mh),
        ],
        fill=(180, 100, 60),
    )

    # Art deco border
    border_color = (220, 160, 80)
    draw.polygon(
        [
            (mx - top_mw // 2, my),
            (mx + top_mw // 2, my),
            (mx + bot_mw // 2, my + mh),
            (mx - bot_mw // 2, my + mh),
        ],
        outline=border_color,
        width=4,
    )

    # Decorative lines (art deco chevrons)
    for i in range(5):
        y_off = my + 15 + i * 22
        chev_w = int(mw * 0.6 * (1 - i * 0.03))
        draw.line(
            [(mx - chev_w // 2, y_off), (mx, y_off + 8), (mx + chev_w // 2, y_off)],
            fill=border_color,
            width=2,
        )

    # Marquee sign area
    sign_top = my + 15
    sign_bot = my + mh - 15
    draw.rectangle(
        [mx - int(top_mw * 0.35), sign_top, mx + int(top_mw * 0.35), sign_bot],
        fill=(40, 35, 30),
    )

    # Lights along the marquee edge
    for lx in range(mx - bot_mw // 2 + 5, mx + bot_mw // 2 - 5, 20):
        ly = my + mh - 5
        draw.ellipse([lx - 4, ly - 4, lx + 4, ly + 4], fill=(255, 220, 100))
        draw.ellipse([lx - 4, ly - 4, lx + 4, ly + 4], fill=(255, 220, 100, 60))

    # Theater entrance below marquee
    ent_top = my + mh
    ent_w = 180
    ent_h = int(height * 0.08)
    draw.rectangle(
        [mx - ent_w // 2, ent_top, mx + ent_w // 2, ent_top + ent_h],
        fill=(25, 20, 18),
    )
    # Doorways
    for dx in [-50, 0, 50]:
        draw.rectangle(
            [mx + dx - 25, ent_top + 5, mx + dx + 25, ent_top + ent_h - 5],
            fill=(15, 12, 10),
        )
        # Door glow
        draw.rectangle(
            [mx + dx - 22, ent_top + 8, mx + dx + 22, ent_top + ent_h - 8],
            fill=(255, 200, 100, 30),
        )


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at bottom with white text."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    draw.rectangle([(0, panel_top), (width, height)], fill=(20, 15, 18))

    # Thin gold border at top of panel
    draw.line([(0, panel_top), (width, panel_top)], fill=(180, 130, 70), width=2)
    draw.line([(0, panel_top + 4), (width, panel_top + 4)], fill=(180, 130, 70, 80), width=1)

    # Title text - use arialbd.ttf
    title = "The Last\nPicture House"
    title_font_size = 76
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered, white text
    lines = title.split("\n")
    y_offset = panel_top + 100
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
    draw.text((ax + 1, ay + 1), author, fill=(0, 0, 0, 100), font=author_font)
    draw.text((ax, ay), author, fill=(200, 190, 180), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Last Picture House")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Dusk gradient background
    draw_dusk_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Storefronts (background buildings)
    draw_storefronts(draw, WIDTH, HEIGHT)

    # Step 3: Main street
    draw_main_street(draw, WIDTH, HEIGHT)

    # Step 4: Theater marquee (focal point)
    draw_marquee(draw, WIDTH, HEIGHT)

    # Step 5: Title panel at bottom
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arial.ttf"),
    }
    draw_title_panel(draw, WIDTH, HEIGHT, font_paths)

    # Soften slightly
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