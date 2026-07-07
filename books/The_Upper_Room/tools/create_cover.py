#!/usr/bin/env python3
"""Cover: The Upper Room — Sepia Boston brownstone hallway, translucent woman in green dress at top of stairs, brass key fob on floor."""

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
    rng = random.Random("upper-room")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        r = int(70 + 25 * (1 - t) + 15 * t)
        g = int(55 + 20 * (1 - t) + 12 * t)
        b = int(40 + 18 * (1 - t) + 10 * t)
        draw.line((0, y, W, y), fill=(min(255, r), min(255, g), min(255, b), 255))

    wall_top = 180
    wall_bot = 1750
    wall_left = 80
    wall_right = 1520
    draw.rectangle((wall_left, wall_top, wall_right, wall_bot), fill=(90, 75, 60, 240))
    for x in range(wall_left, wall_right, 50):
        draw.line((x, wall_top, x, wall_bot), fill=(100, 85, 70, 120), width=2)

    stair_bottom = wall_bot
    stair_top = 550
    stair_left = 350
    stair_right = 1250
    for s in range(20):
        sy = stair_bottom - s * 55
        sx1 = stair_left + s * 28
        sx2 = stair_right - s * 28
        draw.polygon([(sx1, sy), (sx2, sy), (sx2 + 18, sy + 55), (sx1 - 18, sy + 55)], fill=(70, 60, 50))
        draw.line((sx1, sy, sx2, sy), fill=(100, 85, 70), width=2)

    banister_x = stair_left - 25
    draw.line((banister_x, stair_bottom, banister_x, stair_top), fill=(60, 50, 40), width=7)
    for s in range(20):
        sy = stair_bottom - s * 55
        draw.line((banister_x, sy, stair_left + s * 28, sy), fill=(60, 50, 40), width=4)

    banister_rx = stair_right + 25
    draw.line((banister_rx, stair_bottom, banister_rx, stair_top), fill=(60, 50, 40), width=7)
    for s in range(20):
        sy = stair_bottom - s * 55
        draw.line((banister_rx, sy, stair_right - s * 28, sy), fill=(60, 50, 40), width=4)

    woman_cx = W // 2
    woman_cy = 650
    woman = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(woman)
    wd.ellipse((woman_cx - 14, woman_cy - 32, woman_cx + 14, woman_cy), fill=(80, 180, 80, 100))
    wd.polygon([(woman_cx - 22, woman_cy), (woman_cx + 22, woman_cy), (woman_cx + 20, woman_cy + 140), (woman_cx - 20, woman_cy + 140)], fill=(60, 160, 60, 90))
    wd.line((woman_cx - 22, woman_cy + 35, woman_cx - 45, woman_cy + 55), fill=(60, 160, 60, 70), width=5)
    wd.line((woman_cx + 22, woman_cy + 35, woman_cx + 45, woman_cy + 55), fill=(60, 160, 60, 70), width=5)
    woman = woman.filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(img, woman)
    draw = ImageDraw.Draw(img, "RGBA")

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((woman_cx - 70, woman_cy - 50, woman_cx + 70, woman_cy + 170), fill=(130, 240, 130, 20))
    glow = glow.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    key_x, key_y = W // 2 - 60, stair_bottom - 40
    draw.ellipse((key_x - 6, key_y - 4, key_x + 6, key_y + 4), fill=(180, 160, 100))
    draw.rectangle((key_x - 2, key_y - 12, key_x + 2, key_y - 4), fill=(180, 160, 100))
    draw.rectangle((key_x - 8, key_y - 12, key_x + 8, key_y - 10), fill=(180, 160, 100))

    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog)
    for _ in range(15):
        fx = rng.randint(0, W)
        fy = rng.randint(300, 1400)
        fd.ellipse((fx, fy, fx + rng.randint(200, 500), fy + rng.randint(50, 120)), fill=(180, 170, 160, rng.randint(8, 20)))
    fog = fog.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, fog)
    draw = ImageDraw.Draw(img, "RGBA")

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