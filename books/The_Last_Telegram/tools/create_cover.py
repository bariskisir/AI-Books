#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Last Telegram."""

from __future__ import annotations

import argparse
import json
import textwrap
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



WIDTH, HEIGHT = 1600, 2560
TITLE_PANEL_TOP = 1920
FONTS_DIR = Path("C:/Windows/Fonts")
TITLE_FONT_PATH = FONTS_DIR / "georgiab.ttf"
AUTHOR_FONT_PATH = FONTS_DIR / "arialbd.ttf"
SMALL_FONT_PATH = FONTS_DIR / "arial.ttf"


def wrap_title(title: str, max_chars: int = 14) -> str:
    return "\n".join(textwrap.wrap(title, width=max_chars))


def draw_morse(draw: ImageDraw, x: int, y: int, scale: float = 1.0) -> None:
    """Draw a decorative Morse code pattern."""
    dots = [(0, 0), (2, 0), (0, 1), (2, 2), (1, 3)]
    dashes = [(5, 0), (7, 0), (5, 1), (7, 2), (7, 3)]
    for dx, dy in dots:
        cx = x + int(dx * 6 * scale)
        cy = y + int(dy * 6 * scale)
        draw.ellipse([cx, cy, cx + int(4 * scale), cy + int(4 * scale)], fill=(220, 200, 170, 60))
    for dx, dy in dashes:
        rx = x + int(dx * 6 * scale)
        ry = y + int(dy * 6 * scale)
        rw = int(12 * scale)
        rh = int(4 * scale)
        draw.rectangle([rx, ry, rx + rw, ry + rh], fill=(220, 200, 170, 60))


def draw_telegram_machine(draw: ImageDraw, cx: int, base_y: int) -> None:
    """Draw a simplified telegram / teleprinter machine."""
    # Main body
    body_w, body_h = 300, 160
    x1 = cx - body_w // 2
    y1 = base_y
    draw.rectangle([x1, y1, x1 + body_w, y1 + body_h], fill=(60, 55, 50), outline=(140, 130, 110), width=2)

    # Paper feed slot
    slot_w, slot_h = 200, 12
    sx = cx - slot_w // 2
    sy = y1 + 20
    draw.rectangle([sx, sy, sx + slot_w, sy + slot_h], fill=(230, 215, 190))
    # Paper curl
    for i in range(3):
        curl_y = sy + slot_h + 2 + i * 8
        draw.line([sx + 10, curl_y, sx + slot_w - 10, curl_y], fill=(200, 185, 160), width=1)

    # Keys area
    key_area_y = sy + slot_h + 30
    key_w, key_h = 18, 10
    for row in range(4):
        for col in range(12):
            kx = x1 + 15 + col * (key_w + 4)
            ky = key_area_y + row * (key_h + 4)
            draw.rectangle([kx, ky, kx + key_w, ky + key_h], fill=(45, 42, 38), outline=(100, 95, 85))
            if row == 0 and col < 6:
                draw.rectangle([kx + 2, ky + 2, kx + key_w - 2, ky + key_h - 2], fill=(200, 50, 50, 80))

    # Roller at the top
    roller_y = y1 - 10
    draw.rectangle([cx - 120, roller_y, cx + 120, roller_y + 10], fill=(80, 75, 70))


def draw_microphone(draw: ImageDraw, x: int, y: int) -> None:
    """Draw a vintage microphone silhouette."""
    head_r = 20
    draw.ellipse([x - head_r, y - head_r, x + head_r, y + head_r], outline=(140, 130, 110), width=3)
    draw.line([x, y + head_r, x, y + head_r + 40], fill=(140, 130, 110), width=4)
    draw.arc([x - 15, y + 50, x + 15, y + 70], 0, 180, fill=(140, 130, 110), width=2)


def create_cover(title: str, author: str, output_path: Path) -> None:
    img = Image.new("RGBA", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)

    # Gradient background: navy blue -> deep sepia -> dark brown
    for y in range(HEIGHT):
        if y < HEIGHT * 0.6:
            ratio = y / (HEIGHT * 0.6)
            r = int(10 + ratio * 40)
            g = int(20 + ratio * 25)
            b = int(55 + ratio * 10)
        else:
            ratio = (y - HEIGHT * 0.6) / (HEIGHT * 0.4)
            r = int(50 + ratio * 40)
            g = int(45 + ratio * 20)
            b = int(65 - ratio * 30)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Add subtle vignette overlay
    vignette = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    v_draw = ImageDraw.Draw(vignette)
    v_draw.ellipse([-200, -200, WIDTH + 200, HEIGHT + 200], fill=(0, 0, 0, 0))
    v_draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(0, 0, 0, 120))
    img = Image.alpha_composite(img, vignette)
    draw = ImageDraw.Draw(img)

    # Decorative morse code dots scattered in the upper area
    for i in range(12):
        mx = 100 + (i * 130) % 1400
        my = 200 + (i * 97) % 900
        draw_morse(draw, mx, my, scale=1.2 if i % 2 == 0 else 0.8)

    # Draw telegram machine slightly above center
    machine_cx = WIDTH // 2
    machine_y = 550
    draw_telegram_machine(draw, machine_cx, machine_y)

    # Wavy lines suggesting morse / signal waves
    for wave in range(5):
        wy = 820 + wave * 15
        points = []
        for wx in range(200, 1401, 10):
            phase = (wx - 200) / 30 + wave * 0.8
            wavy = wy + int(8 * (phase % 6 - 3))
            points.append((wx, wavy))
        draw.line(points, fill=(200, 180, 150, 80), width=2)

    # Draw microphone
    draw_microphone(draw, 300, 400)
    draw_microphone(draw, 1300, 350)

    # Grid lines suggesting maps / signals
    for gx in range(0, WIDTH, 80):
        draw.line([(gx, 100), (gx, 700)], fill=(100, 90, 80, 30), width=1)
    for gy in range(100, 701, 60):
        draw.line([(0, gy), (WIDTH, gy)], fill=(100, 90, 80, 30), width=1)

    # Title panel (semi-transparent light rectangle at bottom)
    panel = Image.new("RGBA", (WIDTH, HEIGHT - TITLE_PANEL_TOP))
    p_draw = ImageDraw.Draw(panel)
    p_draw.rectangle([0, 0, WIDTH, HEIGHT - TITLE_PANEL_TOP], fill=(230, 220, 205, 220))
    # Subtle border at top of panel
    p_draw.line([(0, 0), (WIDTH, 0)], fill=(180, 160, 140), width=3)
    img.paste(panel, (0, TITLE_PANEL_TOP), panel)
    draw = ImageDraw.Draw(img)

    # Load fonts
    title_font_size = 80
    author_font_size = 40
    small_font_size = 24

    try:
        title_font = ImageFont.truetype(str(TITLE_FONT_PATH), title_font_size)
    except (IOError, OSError):
        title_font = ImageFont.load_default()
    try:
        author_font = ImageFont.truetype(str(AUTHOR_FONT_PATH), author_font_size)
    except (IOError, OSError):
        author_font = ImageFont.load_default()
    try:
        small_font = ImageFont.truetype(str(SMALL_FONT_PATH), small_font_size)
    except (IOError, OSError):
        small_font = ImageFont.load_default()

    # Draw small decorative text "W.R.N.S. Signal Station"
    label = "W.R.N.S. Signal Station -- Shingle Cove"
    bbox = draw.textbbox((0, 0), label, font=small_font)
    label_w = bbox[2] - bbox[0]
    draw.text(
        ((WIDTH - label_w) // 2, TITLE_PANEL_TOP + 30),
        label,
        fill=(120, 100, 80),
        font=small_font,
    )

    # Draw wrapped title
    wrapped_title = wrap_title(title, max_chars=14)
    lines = wrapped_title.split("\n")
    total_text_h = 0
    line_heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        lh = bbox[3] - bbox[1]
        line_heights.append(lh)
        total_text_h += lh
    total_text_h += (len(lines) - 1) * 10

    text_y = TITLE_PANEL_TOP + 60 + (400 - total_text_h) // 2
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=title_font)
        lw = bbox[2] - bbox[0]
        draw.text(
            ((WIDTH - lw) // 2, text_y),
            line,
            fill=(40, 35, 30),
            font=title_font,
        )
        text_y += line_heights[i] + 10

    # Draw author name
    author_label = f"by {author}"
    bbox = draw.textbbox((0, 0), author_label, font=author_font)
    aw = bbox[2] - bbox[0]
    draw.text(
        ((WIDTH - aw) // 2, TITLE_PANEL_TOP + total_text_h + 90),
        author_label,
        fill=(80, 65, 55),
        font=author_font,
    )

    # Decorative line under title area
    line_y = TITLE_PANEL_TOP + total_text_h + 75
    draw.line([(600, line_y), (1000, line_y)], fill=(140, 120, 100), width=2)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img = img.convert("RGB")
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), _standard_cover_metadata_from_locals(locals()).get("model", ""))
    img.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    title = metadata["title"]
    author = metadata.get("author", "Barış Kısır")
    model = _standard_cover_metadata_from_locals(locals()).get("model", "")

    create_cover(title, author, args.out)


if __name__ == "__main__":
    main()