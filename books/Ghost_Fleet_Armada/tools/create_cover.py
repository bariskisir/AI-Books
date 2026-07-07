#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for Ghost Fleet Armada."""

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



FONT_DIR = Path("C:/Windows/Fonts")
WIDTH, HEIGHT = 1600, 2560
PANEL_Y = 1920

COLORS = {
    "bg_top": (10, 5, 30),
    "bg_mid": (15, 10, 50),
    "bg_bot": (5, 0, 20),
    "nebula_core": (80, 50, 180),
    "nebula_edge": (40, 20, 100),
    "nebula_glow": (30, 10, 60),
    "star_bright": (220, 220, 255),
    "star_dim": (150, 150, 200),
    "ship_hull": (20, 25, 40),
    "ship_glow": (60, 100, 200),
    "panel_bg": (240, 240, 248),
    "title_text": (10, 5, 30),
    "author_text": (60, 60, 80),
}


def make_gradient(draw: ImageDraw.ImageDraw) -> None:
    for y in range(HEIGHT):
        if y < HEIGHT // 2:
            t = y / (HEIGHT // 2)
            r = int(COLORS["bg_top"][0] + (COLORS["bg_mid"][0] - COLORS["bg_top"][0]) * t)
            g = int(COLORS["bg_top"][1] + (COLORS["bg_mid"][1] - COLORS["bg_top"][1]) * t)
            b = int(COLORS["bg_top"][2] + (COLORS["bg_mid"][2] - COLORS["bg_top"][2]) * t)
        else:
            t = (y - HEIGHT // 2) / (HEIGHT // 2)
            r = int(COLORS["bg_mid"][0] + (COLORS["bg_bot"][0] - COLORS["bg_mid"][0]) * t)
            g = int(COLORS["bg_mid"][1] + (COLORS["bg_bot"][1] - COLORS["bg_mid"][1]) * t)
            b = int(COLORS["bg_mid"][2] + (COLORS["bg_bot"][2] - COLORS["bg_mid"][2]) * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def draw_nebula(draw: ImageDraw.ImageDraw, img: Image.Image) -> None:
    nebula_img = Image.new("RGBA", (WIDTH, PANEL_Y), (0, 0, 0, 0))
    ndraw = ImageDraw.Draw(nebula_img)

    for _ in range(12):
        cx = random.randint(200, WIDTH - 200)
        cy = random.randint(100, PANEL_Y - 200)
        rx = random.randint(150, 400)
        ry = random.randint(100, 250)
        alpha = random.randint(15, 40)
        color = random.choice([
            COLORS["nebula_core"],
            COLORS["nebula_edge"],
            COLORS["nebula_glow"],
        ])
        ndraw.ellipse(
            [cx - rx, cy - ry, cx + rx, cy + ry],
            fill=(color[0], color[1], color[2], alpha),
        )

    nebula_img = nebula_img.filter(ImageFilter.GaussianBlur(radius=60))
    img.paste(nebula_img, (0, 0), nebula_img)


def draw_stars(draw: ImageDraw.ImageDraw) -> None:
    for _ in range(800):
        x = random.randint(0, WIDTH - 1)
        y = random.randint(0, PANEL_Y - 1)
        r = random.choice([1, 1, 1, 2, 2, 3])
        brightness = random.randint(100, 255)
        color = (brightness, brightness, min(255, brightness + 20))
        draw.ellipse([x - r, y - r, x + r, y + r], fill=color)

    for _ in range(8):
        x = random.randint(0, WIDTH - 1)
        y = random.randint(0, PANEL_Y - 1)
        r = random.randint(3, 6)
        for ring in range(r, 0, -1):
            alpha = max(0, 100 - ring * 15)
            draw.ellipse(
                [x - ring * 4, y - ring * 4, x + ring * 4, y + ring * 4],
                outline=(COLORS["star_bright"][0], COLORS["star_bright"][1], COLORS["star_bright"][2], alpha),
            )


def draw_ship(draw: ImageDraw.ImageDraw, x: int, y: int, scale: float, angle: float = 0) -> None:
    length = int(200 * scale)
    width = int(60 * scale)
    half_w = width // 2

    cos_a = math.cos(angle)
    sin_a = math.sin(angle)

    cx, cy = x, y
    nose = (cx + int(length * 0.4 * cos_a), cy + int(length * 0.4 * sin_a))
    tail = (cx - int(length * 0.4 * cos_a), cy - int(length * 0.4 * sin_a))
    wing_l = (cx - int(20 * scale * cos_a) - int(half_w * sin_a), cy - int(20 * scale * sin_a) + int(half_w * cos_a))
    wing_r = (cx - int(20 * scale * cos_a) + int(half_w * sin_a), cy - int(20 * scale * sin_a) - int(half_w * cos_a))
    tail_l = (cx - int(40 * scale * cos_a) - int(half_w * 0.6 * sin_a), cy - int(40 * scale * sin_a) + int(half_w * 0.6 * cos_a))
    tail_r = (cx - int(40 * scale * cos_a) + int(half_w * 0.6 * sin_a), cy - int(40 * scale * sin_a) - int(half_w * 0.6 * cos_a))

    hull_color = COLORS["ship_hull"]
    draw.polygon([nose, wing_l, tail_l, tail, tail_r, wing_r], fill=hull_color, outline=(40, 50, 80))

    glow_color = COLORS["ship_glow"]
    engine_l = (tail_l[0] - int(10 * scale * cos_a), tail_l[1] - int(10 * scale * sin_a))
    engine_r = (tail_r[0] - int(10 * scale * cos_a), tail_r[1] - int(10 * scale * sin_a))
    draw.ellipse(
        [engine_l[0] - 4, engine_l[1] - 4, engine_l[0] + 4, engine_l[1] + 4],
        fill=glow_color,
    )
    draw.ellipse(
        [engine_r[0] - 4, engine_r[1] - 4, engine_r[0] + 4, engine_r[1] + 4],
        fill=glow_color,
    )


def draw_ships(draw: ImageDraw.ImageDraw) -> None:
    # Main large derelict ship - center-left
    draw_ship(draw, 500, 600, 3.5, angle=-0.15)

    # Second large ship - right side, angled away
    draw_ship(draw, 1100, 450, 2.8, angle=0.25)

    # Smaller ships in background
    draw_ship(draw, 300, 300, 1.2, angle=0.5)
    draw_ship(draw, 750, 250, 0.8, angle=-0.3)
    draw_ship(draw, 1300, 700, 1.5, angle=-0.4)
    draw_ship(draw, 200, 850, 1.0, angle=0.6)
    draw_ship(draw, 1400, 300, 0.6, angle=0.1)
    draw_ship(draw, 850, 900, 1.8, angle=0.35)


def draw_title_panel(draw: ImageDraw.ImageDraw, title: str, author: str) -> None:
    draw.rectangle([0, PANEL_Y, WIDTH, HEIGHT], fill=COLORS["panel_bg"])

    separator_y = PANEL_Y + 10
    draw.rectangle([100, separator_y, WIDTH - 100, separator_y + 2], fill=(180, 180, 200))

    georgia_bold_path = FONT_DIR / "georgiab.ttf"
    arial_bold_path = FONT_DIR / "arialbd.ttf"
    arial_path = FONT_DIR / "arial.ttf"

    try:
        title_font_size = 80
        title_font = ImageFont.truetype(str(georgia_bold_path), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    try:
        author_font = ImageFont.truetype(str(arial_bold_path), 36)
    except Exception:
        author_font = ImageFont.load_default()

    words = title.split()
    line1_words = []
    line2_words = []
    mid = len(words) // 2
    if len(words) <= 3:
        line1_words = words
    else:
        line1_words = words[:mid]
        line2_words = words[mid:]

    line1 = " ".join(line1_words)
    line2 = " ".join(line2_words)

    center_x = WIDTH // 2

    try:
        bbox1 = draw.textbbox((0, 0), line1, font=title_font)
        w1 = bbox1[2] - bbox1[0]
        h1 = bbox1[3] - bbox1[1]
    except Exception:
        w1, h1 = title_font.getsize(line1)

    line1_y = PANEL_Y + 60

    if line2:
        try:
            bbox2 = draw.textbbox((0, 0), line2, font=title_font)
            w2 = bbox2[2] - bbox2[0]
            h2 = bbox2[3] - bbox2[1]
        except Exception:
            w2, h2 = title_font.getsize(line2)

        total_h = h1 + 10 + h2
        start_y = PANEL_Y + (HEIGHT - PANEL_Y - total_h) // 2 - 30
        line1_y = start_y
        line2_y = start_y + h1 + 10

        draw.text((center_x - w2 // 2, line2_y), line2, fill=COLORS["title_text"], font=title_font)

    draw.text((center_x - w1 // 2, line1_y), line1, fill=COLORS["title_text"], font=title_font)

    author_y = HEIGHT - 80
    try:
        abbox = draw.textbbox((0, 0), author, font=author_font)
        aw = abbox[2] - abbox[0]
    except Exception:
        aw, _ = author_font.getsize(author)
    draw.text((center_x - aw // 2, author_y), author, fill=COLORS["author_text"], font=author_font)

    tagline = "A Space Opera"
    try:
        small_font = ImageFont.truetype(str(arial_path), 18)
        sbbox = draw.textbbox((0, 0), tagline, font=small_font)
        sw = sbbox[2] - sbbox[0]
    except Exception:
        small_font = ImageFont.load_default()
        sw, _ = small_font.getsize(tagline)
    draw.text((center_x - sw // 2, HEIGHT - 120), tagline, fill=(140, 140, 160), font=small_font)



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    title = metadata["title"]
    author = metadata["author"]
    model = metadata.get("model", "")

    img = Image.new("RGB", (WIDTH, HEIGHT), COLORS["bg_top"])
    draw = ImageDraw.Draw(img, "RGBA")

    make_gradient(draw)
    draw_nebula(draw, img)
    draw_stars(draw)
    draw_ships(draw)

    draw_rgb = ImageDraw.Draw(img)
    draw_title_panel(draw_rgb, title, author)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.save(args.out, "PNG")
    print(f"Cover saved to {args.out}")


if __name__ == "__main__":
    main()