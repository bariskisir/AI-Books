#!/usr/bin/env python3
"""Create a project-local raster cover for The Wintering — Antarctic ice shelf under aurora."""

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
FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    for candidate in [FONT_DIR / name, FONT_DIR / "georgia.ttf", FONT_DIR / "arial.ttf"]:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def wrap(draw: ImageDraw.ImageDraw, text: str, selected_font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        proposed = " ".join([*current, word])
        if draw.textbbox((0, 0), proposed, font=selected_font)[2] <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def centered(draw: ImageDraw.ImageDraw, y: int, lines: list[str], selected_font: ImageFont.FreeTypeFont, fill: tuple[int, int, int], gap: int) -> int:
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=selected_font)
        x = (W - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), line, font=selected_font, fill=fill)
        y += bbox[3] - bbox[1] + gap
    return y


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata["title"]
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")
    rng = random.Random(title)

    img = Image.new("RGBA", (W, H), (2, 3, 8, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Night sky gradient — polar winter darkness.
    for y in range(H):
        t = y / (H - 1)
        draw.line((0, y, W, y), fill=(int(1 + 6 * t), int(2 + 8 * t), int(6 + 14 * t), 255))

    # Stars — bright, numerous, hard.
    for _ in range(400):
        x = rng.randrange(0, W)
        yy = rng.randrange(0, 1200)
        rad = rng.choice([1, 1, 1, 2])
        alpha = rng.randrange(120, 230)
        draw.ellipse((x - rad, yy - rad, x + rad, yy + rad), fill=(230, 235, 245, alpha))

    # Aurora borealis — green curtains.
    aurora = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ad = ImageDraw.Draw(aurora)
    for i in range(6):
        ax = rng.randrange(200, 1400)
        ay = rng.randrange(80, 500)
        aw = rng.randrange(400, 1000)
        ah = rng.randrange(200, 500)
        green = rng.randint(40, 100)
        red = rng.randint(0, 30)
        blue = rng.randint(60, 120)
        ad.ellipse((ax, ay, ax + aw, ay + ah),
                   fill=(red, green + 80, blue, rng.randrange(8, 20)))
        ad.ellipse((ax - 200, ay + 100, ax + aw + 200, ay + ah + 100),
                   fill=(red, green + 60, blue, rng.randrange(6, 14)))
    aurora = aurora.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img, aurora)

    # Ice shelf — cracked, ancient, stretching to darkness.
    ice_y = 1500
    for y in range(ice_y, H, 3):
        t = (y - ice_y) / (H - ice_y)
        r, g, b = int(8 + 6 * t), int(14 + 8 * t), int(28 + 12 * t)
        wave = rng.randrange(-2, 3)
        draw.line((0, y + wave, W, y), fill=(r, g, b, 200))

    # Pressure ridges — angular, fractured.
    for _ in range(12):
        rx = rng.randrange(0, W)
        ry = rng.randrange(ice_y, ice_y + 300)
        rh = rng.randrange(30, 120)
        rw = rng.randrange(8, 40)
        # Dark ridge.
        draw.polygon([(rx, ry), (rx + rw, ry - rh), (rx + rw * 2, ry)],
                     fill=(12, 16, 22, 230))
        # Highlight edge.
        draw.line([(rx, ry), (rx + rw, ry - rh)], fill=(60, 68, 80, 100), width=2)

    # The hut — small, dark, fragile.
    hut_x = 720
    hut_y = 1450
    hut_w = 120
    hut_h = 80
    # Body.
    draw.rectangle((hut_x, hut_y, hut_x + hut_w, hut_y + hut_h),
                   fill=(10, 12, 15, 250))
    # Roof.
    draw.polygon([(hut_x - 10, hut_y), (hut_x + hut_w // 2, hut_y - 30), (hut_x + hut_w + 10, hut_y)],
                 fill=(8, 10, 12, 250))
    # Window — small, lit.
    win_w, win_h = 20, 16
    win_x = hut_x + (hut_w - win_w) // 2
    draw.rectangle((win_x, hut_y + 20, win_x + win_w, hut_y + 20 + win_h),
                   fill=(220, 180, 80, 200))
    # Window glow.
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((win_x - 40, hut_y + 10, win_x + win_w + 40, hut_y + 40 + win_h),
               fill=(220, 180, 60, 8))
    glow = glow.filter(ImageFilter.GaussianBlur(20))
    img = Image.alpha_composite(img, glow)

    # Sastrugi — wind-carved ice ripples.
    for _ in range(30):
        sx = rng.randrange(0, W)
        sy = rng.randrange(ice_y + 100, ice_y + 500)
        sw = rng.randrange(60, 200)
        draw.arc((sx, sy, sx + sw, sy + 12), 180, 0,
                 fill=(30, 36, 44, rng.randrange(30, 70)), width=2)

    # Distant mountain profile (nunataks).
    for _ in range(3):
        mx = rng.randrange(100, 1500)
        mh = rng.randrange(80, 200)
        draw.polygon([(mx - 60, ice_y), (mx, ice_y - mh), (mx + 80, ice_y)],
                     fill=(4, 5, 8, 200))

    # Fog layer.
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog)
    for _ in range(30):
        fy = rng.randrange(800, 1700)
        fx = rng.randrange(-200, W + 200)
        fd.ellipse((fx, fy, fx + rng.randrange(400, 1200), fy + rng.randrange(80, 200)),
                   fill=(180, 190, 200, rng.randrange(4, 12)))
    fog = fog.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img, fog)

    draw = ImageDraw.Draw(img, "RGBA")

    # Lower panel for text.
    draw.rectangle((0, 1900, W, H), fill=(1, 2, 5, 210))
    # Subtle line.
    draw.line((200, 1925, W - 200, 1925), fill=(140, 150, 160, 60), width=1)

    # Typography.
    title_font = font("georgiab.ttf", 100)
    author_font = font("arialbd.ttf", 40)
    subtitle_font = font("arial.ttf", 28)

    y = 1960
    y = centered(draw, y, ["ANTARCTIC DARK"], subtitle_font, (140, 150, 160), 8)
    y += 60
    y = centered(draw, y, wrap(draw, title.upper(), title_font, 1200), title_font, (220, 225, 230), 16)
    y += 100
    centered(draw, y, [author], author_font, (180, 188, 195), 8)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(output_path, "PNG", optimize=True)



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    metadata_path = ROOT / args.metadata if not args.metadata.is_absolute() else args.metadata
    output_path = ROOT / args.out if not args.out.is_absolute() else args.out
    make_cover(metadata_path, output_path)


if __name__ == "__main__":
    main()