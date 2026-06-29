#!/usr/bin/env python3
"""Create a project-local raster cover for The Salt Road — Anatolia landscape."""

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

    img = Image.new("RGBA", (W, H), (200, 175, 140, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Warm earth sky gradient — Anatolian sunset.
    for y in range(H):
        t = y / (H - 1)
        r = int(200 - 80 * t)
        g = int(175 - 90 * t)
        b = int(140 - 100 * t)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Distant mountain silhouette.
    for _ in range(8):
        mx = rng.randrange(-100, 1700)
        mh = rng.randrange(80, 250)
        mw = rng.randrange(200, 600)
        draw.polygon([(mx, 1100), (mx + mw // 2, 1100 - mh), (mx + mw, 1100)],
                     fill=(90, 65, 45, 60))

    # Fairy chimney rock formations.
    for _ in range(25):
        cx = rng.randrange(50, 1550)
        cy = rng.randrange(850, 1400)
        cw = rng.randrange(15, 50)
        ch = rng.randrange(60, 200)
        draw.polygon([(cx - cw // 2, cy), (cx, cy - ch), (cx + cw // 2, cy)],
                     fill=(160, 130, 95, 220))
        cap_w = cw + rng.randrange(4, 14)
        draw.ellipse((cx - cap_w // 2, cy - ch - 8, cx + cap_w // 2, cy - ch + 4),
                     fill=(110, 85, 60, 240))

    # Salt pan — white cracked earth.
    pan_y = 1765
    draw.rectangle((0, pan_y, W, H), fill=(230, 225, 210, 230))
    for _ in range(60):
        px = rng.randrange(0, W)
        py = rng.randrange(pan_y, H)
        pl = rng.randrange(20, 80)
        angle = rng.uniform(0, 6.28)
        ex = int(px + pl * rng.choice([-1, 1]) * 0.8)
        ey = int(py + pl * rng.choice([-1, 1]) * 0.3)
        draw.line((px, py, ex, ey), fill=(190, 182, 168, 140), width=2)

    # Dried grass tufts.
    for _ in range(40):
        gx = rng.randrange(0, W)
        gy = rng.randrange(pan_y + 20, H - 40)
        gh = rng.randrange(8, 20)
        draw.line((gx, gy, gx - 3, gy - gh), fill=(160, 145, 110, 120), width=2)
        draw.line((gx, gy, gx + 3, gy - gh), fill=(160, 145, 110, 120), width=2)

    # Stone bridge silhouette.
    bridge_x = rng.randrange(500, 1100)
    bridge_y = pan_y - rng.randrange(60, 120)
    for arch in range(3):
        ax = bridge_x + arch * 60
        draw.arc((ax, bridge_y - 30, ax + 60, bridge_y + 10), 180, 0,
                 fill=(100, 75, 55, 100), width=6)

    # Warm haze.
    haze = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(haze)
    for _ in range(20):
        hx = rng.randrange(-200, W + 200)
        hy = rng.randrange(1200, 1800)
        hd.ellipse((hx, hy, hx + rng.randrange(400, 1000), hy + rng.randrange(60, 150)),
                   fill=(210, 190, 160, rng.randrange(5, 15)))
    haze = haze.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, haze)

    draw = ImageDraw.Draw(img, "RGBA")

    # Lower panel.
    draw.rectangle((0, 2100, W, H), fill=(40, 30, 20, 220))
    draw.line((250, 2130, W - 250, 2130), fill=(180, 165, 140, 80), width=1)

    # Typography.
    title_font = font("georgiab.ttf", 115)
    author_font = font("arialbd.ttf", 42)
    subtitle_font = font("arial.ttf", 30)

    y = 2180
    y = centered(draw, y, ["AN ANATOLIAN ROAD"], subtitle_font, (170, 158, 140), 8)
    y += 60
    y = centered(draw, y, wrap(draw, title.upper(), title_font, 1200), title_font, (220, 215, 200), 18)
    y += 110
    centered(draw, y, [author], author_font, (190, 182, 168), 8)

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