#!/usr/bin/env python3
"""Create a project-local raster cover for The Atlas of Lost Worlds."""

from __future__ import annotations

import argparse
import json
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

    img = Image.new("RGB", (W, H), (12, 15, 25))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / (H - 1)
        r = int(8 + 35 * t)
        g = int(12 + 28 * t)
        b = int(30 + 20 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    stars = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stars, "RGBA")
    for _ in range(200):
        x = rng.randrange(0, W)
        y = rng.randrange(0, 800)
        alpha = rng.randrange(80, 200)
        size = rng.randrange(1, 4)
        sd.ellipse((x, y, x + size, y + size), fill=(255, 255, 240, alpha))
    img = Image.alpha_composite(img.convert("RGBA"), stars)
    draw = ImageDraw.Draw(img, "RGBA")

    draw.rectangle((0, 1000, W, 1650), fill=(18, 22, 45, 200))
    for y in range(1050, 1640, 25):
        draw.line((0, y, W, y + rng.randrange(-10, 11)), fill=(45, 55, 90, 40), width=3)

    for x in range(80, W, 140):
        h = rng.randrange(100, 280)
        draw.rectangle((x, 1000 - h, x + rng.randrange(50, 100), 1000), fill=(10, 12, 30, 230))
        if rng.random() < 0.4:
            draw.rectangle((x + 15, 1050 - h // 2, x + 30, 1065 - h // 2), fill=(200, 180, 120, 90))

    draw.polygon([(0, H), (700, 1620), (900, 1620), (W, H)], fill=(5, 8, 15, 240))
    path = [(300 + i * 16, 1950 + int(45 * rng.random()) + int(70 * (i / 50))) for i in range(51)]
    draw.line(path, fill=(180, 160, 100, 180), width=6)
    draw.line([(x, y + 8) for x, y in path], fill=(220, 210, 180, 100), width=2)

    compass_x, compass_y = 1350, 500
    draw.ellipse((compass_x - 60, compass_y - 60, compass_x + 60, compass_y + 60), outline=(180, 160, 100, 150), width=4)
    draw.line((compass_x, compass_y - 50, compass_x, compass_y + 50), fill=(180, 160, 100, 120), width=3)
    draw.line((compass_x - 50, compass_y, compass_x + 50, compass_y), fill=(180, 160, 100, 120), width=3)
    draw.polygon([(compass_x, compass_y - 45), (compass_x - 8, compass_y - 15), (compass_x + 8, compass_y - 15)], fill=(200, 50, 50, 180))
    draw.polygon([(compass_x, compass_y + 45), (compass_x - 8, compass_y + 15), (compass_x + 8, compass_y + 15)], fill=(100, 100, 120, 120))

    draw.rectangle((0, 1765, W, H), fill=(5, 8, 15, 255))
    draw.line((190, 1782, W - 190, 1782), fill=(180, 160, 100, 120), width=3)
    title_font = font("georgiab.ttf", 120)
    author_font = font("arialbd.ttf", 52)
    subtitle_font = font("arial.ttf", 34)
    y = 1840
    y = centered(draw, y, ["A CARTOGRAPHIC FANTASY"], subtitle_font, (180, 160, 100), 16)
    y += 60
    y = centered(draw, y, wrap(draw, title.upper(), title_font, 1250), title_font, (240, 235, 220), 20)
    y += 100
    centered(draw, y, [author], author_font, (200, 195, 180), 12)

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