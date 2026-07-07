#!/usr/bin/env python3
"""Cover: The Lantern Index — Stormy harbor at night, scattered index cards, lighthouse beam sweeping dark water."""

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
    rng = __import__("random").Random(17)

    # Storm gradient: dark gray to near-black
    for y in range(H):
        t = y / H
        r = int(20 - 12 * t)
        g = int(30 - 18 * t)
        b = int(45 - 28 * t)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Stormy sea
    sea_top = 1150
    draw.rectangle((0, sea_top, W, 1500), fill=(8, 15, 22, 220))
    # Waves
    for y in range(sea_top, 1500, 20):
        wobble = int(10 * __import__("math").sin(y / 35))
        draw.line((0, y + wobble, W, y + wobble), fill=(100, 160, 180, 25), width=3)

    # Lighthouse on rocky island
    lx, ly = W - 300, sea_top - 180
    # Tower
    draw.rectangle((lx - 30, ly, lx + 30, sea_top), fill=(25, 32, 40, 220))
    draw.rectangle((lx - 38, ly - 30, lx + 38, ly), fill=(40, 48, 55, 220))
    draw.ellipse((lx - 25, ly - 50, lx + 25, ly - 20), fill=(60, 70, 80, 220))
    # Light beam
    beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam)
    bd.polygon([(lx, ly - 35), (lx + W, ly - 300), (W, ly + 200)], fill=(255, 240, 180, 20))
    bd.polygon([(lx, ly - 35), (lx - 500, ly - 200), (lx - 500, ly + 150)], fill=(255, 240, 180, 12))
    beam = beam.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, beam)
    draw = ImageDraw.Draw(img, "RGBA")
    # Lantern glow
    draw.ellipse((lx - 25, ly - 55, lx + 25, ly - 15), fill=(255, 230, 150, 200))

    # Rocky island base
    for i in range(12):
        rx = lx - 60 + rng.randint(0, 120)
        ry = sea_top - 20 + rng.randint(-10, 15)
        rs = rng.randint(15, 40)
        draw.ellipse([rx - rs // 2, ry, rx + rs // 2, ry + rs // 2], fill=(35, 32, 28, 200))

    # Scattered index cards (foreground)
    for i, (cx, cy, tilt) in enumerate([(150, 1550, -15), (350, 1480, 8), (550, 1600, -10), (750, 1520, 12), (950, 1620, -8), (1150, 1490, 10)]):
        card = Image.new("RGBA", (200, 110), (0, 0, 0, 0))
        cd = ImageDraw.Draw(card)
        cd.rounded_rectangle((0, 0, 200, 110), radius=6, fill=(230, 225, 215, 230))
        cd.line((12, 20, 188, 20), fill=(130, 125, 118, 80), width=2)
        cd.line((12, 42, 160, 42), fill=(130, 125, 118, 60), width=2)
        cd.line((12, 64, 175, 64), fill=(130, 125, 118, 60), width=2)
        cd.line((12, 86, 140, 86), fill=(130, 125, 118, 60), width=2)
        card = card.rotate(tilt, expand=1, resample=Image.Resampling.BICUBIC)
        glow = card.filter(ImageFilter.GaussianBlur(6))
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        layer.alpha_composite(glow, (cx - card.size[0] // 2, cy - card.size[1] // 2))
        layer.alpha_composite(card, (cx - card.size[0] // 2, cy - card.size[1] // 2))
        img.alpha_composite(layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # Rain
    for x in range(0, W, 25):
        for y in range(0, 1700, 60):
            draw.line((x, y, x + 6, y + 30), fill=(200, 215, 230, 15), width=1)

    # Wooden pier/dock lines
    for x in range(80, W, 200):
        draw.line((x, 1480, x + 40, 1550), fill=(20, 35, 45, 60), width=4)

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
