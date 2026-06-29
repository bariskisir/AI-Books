#!/usr/bin/env python3
"""Create a project-local raster cover for The Lantern Index."""

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
FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560


def rel(path: Path) -> Path:
    return ROOT / path if not path.is_absolute() else path


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


def centered(
    draw: ImageDraw.ImageDraw,
    y: int,
    lines: list[str],
    selected_font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
    gap: int,
) -> int:
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=selected_font)
        x = (W - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), line, font=selected_font, fill=fill)
        y += bbox[3] - bbox[1] + gap
    return y


def draw_gradient(draw: ImageDraw.ImageDraw) -> None:
    top = (12, 23, 34)
    middle = (24, 59, 78)
    horizon = (48, 84, 92)
    lower = (6, 12, 20)
    for y in range(H):
        if y < 900:
            t = y / 900
            c = tuple(int(a + (b - a) * t) for a, b in zip(top, middle))
        elif y < 1650:
            t = (y - 900) / 750
            c = tuple(int(a + (b - a) * t) for a, b in zip(middle, horizon))
        else:
            t = (y - 1650) / (H - 1650)
            c = tuple(int(a + (b - a) * t) for a, b in zip(horizon, lower))
        draw.line((0, y, W, y), fill=c + (255,))


def draw_rain(draw: ImageDraw.ImageDraw) -> None:
    for x in range(0, W, 32):
        for y in range(0, 1700, 70):
            draw.line((x, y, x + 10, y + 38), fill=(220, 240, 255, 18), width=2)


def draw_harbor(draw: ImageDraw.ImageDraw) -> Image.Image:
    draw.rectangle((0, 1180, W, 1540), fill=(12, 19, 28, 220))
    draw.polygon([(0, 1440), (180, 1360), (360, 1390), (520, 1320), (760, 1360), (980, 1290), (1210, 1340), (1450, 1305), (W, 1360), (W, 1540), (0, 1540)], fill=(7, 12, 18, 240))
    for x in range(30, W, 120):
        deck = 40 + (x // 120) % 3 * 12
        draw.rectangle((x, 1260 - deck, x + 54, 1360 - deck), fill=(16, 23, 31, 255))
        if x % 240 == 0:
            draw.rectangle((x + 14, 1280 - deck, x + 38, 1308 - deck), fill=(210, 180, 112, 120))

    water = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(water, "RGBA")
    for y in range(1180, 1580, 26):
        wobble = int(10 * math.sin(y / 42))
        wd.line((0, y, W, y + wobble), fill=(120, 185, 205, 32), width=3)
        wd.line((0, y + 6, W, y + 6 + wobble), fill=(40, 90, 110, 28), width=2)
    water = water.filter(ImageFilter.GaussianBlur(0.6))
    return water


def draw_lights(draw: ImageDraw.ImageDraw) -> None:
    lantern_positions = [(210, 1040), (360, 980), (520, 1015), (690, 940), (860, 980), (1020, 920), (1210, 960), (1370, 905)]
    for x, y in lantern_positions:
        draw.ellipse((x - 20, y - 20, x + 20, y + 20), fill=(255, 224, 140, 140))
        draw.ellipse((x - 46, y - 46, x + 46, y + 46), fill=(255, 224, 140, 30))
        draw.line((x, y + 20, x, y + 120), fill=(250, 225, 150, 50), width=2)


def draw_lighthouse(img: Image.Image, draw: ImageDraw.ImageDraw) -> None:
    base_x = 1250
    base_y = 1380
    tower = [(base_x - 65, base_y), (base_x + 65, base_y), (base_x + 48, 980), (base_x - 48, 980)]
    draw.polygon(tower, fill=(28, 35, 42, 255))
    draw.rectangle((base_x - 78, 950, base_x + 78, 988), fill=(46, 54, 61, 255))
    draw.rectangle((base_x - 52, 910, base_x + 52, 950), fill=(64, 74, 82, 255))
    draw.ellipse((base_x - 32, 886, base_x + 32, 932), fill=(196, 204, 210, 255))
    beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam, "RGBA")
    bd.polygon([(base_x, 909), (base_x + 420, 770), (W, 820), (W, 1110), (base_x + 350, 1110)], fill=(255, 240, 180, 30))
    bd.polygon([(base_x, 909), (base_x - 440, 790), (0, 840), (0, 1090), (base_x - 360, 1100)], fill=(255, 240, 180, 18))
    beam = beam.filter(ImageFilter.GaussianBlur(18))
    img.alpha_composite(beam)


def draw_index_cards(img: Image.Image, draw: ImageDraw.ImageDraw) -> None:
    cards = [
        (190, 1640, -18),
        (360, 1550, 11),
        (530, 1685, -9),
        (720, 1600, 15),
        (890, 1710, -7),
        (1080, 1560, 9),
        (1270, 1675, -12),
    ]
    for x, y, tilt in cards:
        rect = Image.new("RGBA", (220, 120), (0, 0, 0, 0))
        rd = ImageDraw.Draw(rect, "RGBA")
        rd.rounded_rectangle((0, 0, 220, 120), radius=8, fill=(238, 232, 220, 230))
        rd.line((14, 22, 205, 22), fill=(140, 135, 128, 90), width=2)
        rd.line((14, 46, 178, 46), fill=(140, 135, 128, 70), width=2)
        rd.line((14, 70, 196, 70), fill=(140, 135, 128, 70), width=2)
        rd.line((14, 94, 160, 94), fill=(140, 135, 128, 70), width=2)
        rect = rect.rotate(tilt, expand=1, resample=Image.Resampling.BICUBIC)
        glow = rect.filter(ImageFilter.GaussianBlur(8))
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        layer.alpha_composite(glow, (x - rect.size[0] // 2, y - rect.size[1] // 2))
        layer.alpha_composite(rect, (x - rect.size[0] // 2, y - rect.size[1] // 2))
        img.alpha_composite(layer)


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Lantern Index")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    draw_gradient(draw)
    water = draw_harbor(draw)
    img = Image.alpha_composite(img, water)
    draw = ImageDraw.Draw(img, "RGBA")
    draw_rain(draw)
    draw_lanterns = draw_lights
    draw_lanterns(draw)
    draw_lighthouse(img, draw)
    draw_index_cards(img, draw)

    for x in range(80, W, 240):
        draw.line((x, 1510, x + 60, 1590), fill=(25, 45, 56, 60), width=3)

    title_plate = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(title_plate, "RGBA")
    pd.rounded_rectangle((70, 2050, W - 70, 2375), radius=14, fill=(8, 13, 18, 150), outline=(180, 200, 198, 90), width=2)
    title_plate = title_plate.filter(ImageFilter.GaussianBlur(0.5))
    img = Image.alpha_composite(img, title_plate)
    draw = ImageDraw.Draw(img, "RGBA")

    title_font = font("georgiab.ttf", 112)
    author_font = font("arialbd.ttf", 50)
    subtitle_font = font("arial.ttf", 32)
    y = 190
    y = centered(draw, y, ["A HARBOR OF"], subtitle_font, (175, 208, 214), 10)
    y = centered(draw, y, ["ERASED RECORDS"], subtitle_font, (175, 208, 214), 18)
    y += 12
    y = centered(draw, y, wrap(draw, title.upper(), title_font, 1210), title_font, (245, 243, 235), 18)
    y += 22
    centered(draw, y, [author], author_font, (210, 220, 219), 10)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(output_path, "PNG", optimize=True)



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    metadata_path = rel(args.metadata)
    output_path = rel(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    make_cover(metadata_path, output_path)


if __name__ == "__main__":
    main()
