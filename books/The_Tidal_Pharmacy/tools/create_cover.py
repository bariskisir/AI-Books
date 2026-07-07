#!/usr/bin/env python3
"""Cover: Woman in white coat holds cloudy insulin vial up to rain-streaked window, harbor and ferry visible beyond, pharmacy white/harbor gray/rain blue."""

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
W, H = 1600, 2560
FONT_DIR = Path("C:/Windows/Fonts")


def lerp_color(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def font(name: str, size: int):
    for candidate in (FONT_DIR / name, FONT_DIR / "arialbd.ttf", FONT_DIR / "arial.ttf"):
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def draw_tidal_pharmacy(draw: ImageDraw.ImageDraw) -> None:
    random.seed("the-tidal-pharmacy-cover")
    # Gradient: pale ceiling to cool interior wall to dark floor
    for y in range(H):
        t = y / H
        if t < 0.15:
            c = lerp_color((200, 210, 215), (180, 190, 195), t / 0.15)
        elif t < 0.5:
            c = lerp_color((180, 190, 195), (140, 155, 160), (t - 0.15) / 0.35)
        else:
            c = lerp_color((140, 155, 160), (60, 70, 75), (t - 0.5) / 0.5)
        draw.line([(0, y), (W, y)], fill=c)

    # Window frame (rain-streaked, showing harbor)
    win_x, win_y = 200, 300
    win_w, win_h = 600, 700
    # Window frame
    draw.rectangle([win_x - 10, win_y - 10, win_x + win_w + 10, win_y + win_h + 10], fill=(90, 85, 80))
    draw.rectangle([win_x, win_y, win_x + win_w, win_y + win_h], fill=(100, 130, 150))

    # Harbor scene through window
    # Sky through window
    for y in range(win_y, win_y + int(win_h * 0.4)):
        t = (y - win_y) / (win_h * 0.4)
        r = int(80 + 60 * t)
        g = int(110 + 50 * t)
        b = int(140 + 30 * t)
        draw.line([(win_x, y), (win_x + win_w, y)], fill=(r, g, b))
    # Sea through window
    sea_y = win_y + int(win_h * 0.4)
    for y in range(sea_y, win_y + win_h):
        t = (y - sea_y) / (win_h * 0.6)
        r = int(50 + 20 * t)
        g = int(80 + 30 * t)
        b = int(110 + 20 * t)
        draw.line([(win_x, y), (win_x + win_w, y)], fill=(r, g, b))
    # Waves
    for x in range(win_x, win_x + win_w, 8):
        wy = sea_y + int(10 * math.sin(x * 0.05))
        draw.line([(x, wy), (x + 4, wy + 2)], fill=(120, 160, 180, 100), width=2)
    # Ferry silhouette through window
    ferry_x = win_x + 350
    ferry_y = sea_y + 80
    draw.rectangle([ferry_x, ferry_y, ferry_x + 120, ferry_y + 30], fill=(30, 40, 50))
    draw.rectangle([ferry_x + 20, ferry_y - 30, ferry_x + 100, ferry_y], fill=(35, 45, 55))
    # Ferry windows
    for fwx in range(ferry_x + 25, ferry_x + 100, 18):
        draw.rectangle([fwx, ferry_y - 25, fwx + 10, ferry_y - 8], fill=(200, 180, 100, 150))
    # Distant island silhouettes
    for ix in range(win_x + 50, win_x + win_w - 50, 150):
        iy = sea_y + int(20 * math.sin(ix * 0.02))
        draw.polygon([(ix, iy), (ix + 30, iy - 40), (ix + 60, iy)], fill=(40, 55, 60, 120))

    # Rain streaks on window
    for _ in range(40):
        rx = win_x + random.randint(20, win_w - 20)
        ry = win_y + random.randint(10, win_h - 20)
        rl = random.randint(30, 120)
        rw = random.randint(1, 2)
        draw.line([(rx, ry), (rx + random.randint(-5, 5), ry + rl)],
                  fill=(180, 200, 220, random.randint(60, 140)), width=rw)
    # Rain droplets
    for _ in range(30):
        rx = win_x + random.randint(15, win_w - 15)
        ry = win_y + random.randint(10, win_h - 10)
        rr = random.randint(2, 5)
        draw.ellipse([rx - rr, ry - rr, rx + rr, ry + rr], fill=(200, 220, 240, random.randint(40, 100)))

    # Window cross
    draw.line([(win_x + win_w // 2, win_y), (win_x + win_w // 2, win_y + win_h)], fill=(80, 75, 70), width=8)
    draw.line([(win_x, win_y + win_h // 2), (win_x + win_w, win_y + win_h // 2)], fill=(80, 75, 70), width=8)

    # Woman in white coat (foreground, silhouetted against window)
    woman_cx = win_x + win_w + 120
    woman_base = 1050
    # White coat body
    draw.ellipse([woman_cx - 35, woman_base - 180, woman_cx + 35, woman_base - 40], fill=(200, 200, 205))
    draw.line([(woman_cx, woman_base - 40), (woman_cx, woman_base)], fill=(200, 200, 205), width=30)
    # Head
    draw.ellipse([woman_cx - 18, woman_base - 230, woman_cx + 18, woman_base - 185], fill=(60, 55, 50))
    # Hair
    draw.ellipse([woman_cx - 20, woman_base - 235, woman_cx + 20, woman_base - 210], fill=(40, 35, 30))
    # Arm raising vial to window
    draw.line([(woman_cx + 17, woman_base - 100), (woman_cx + 80, woman_base - 160)], fill=(200, 200, 205), width=10)
    draw.line([(woman_cx - 17, woman_base - 80), (woman_cx - 60, woman_base - 50)], fill=(200, 200, 205), width=10)

    # Cloudy insulin vial held up to window
    vial_x, vial_y = woman_cx + 80, woman_base - 170
    # Vial body
    draw.rectangle([vial_x - 12, vial_y, vial_x + 12, vial_y + 50], fill=(180, 200, 200, 180))
    draw.rectangle([vial_x - 10, vial_y + 2, vial_x + 10, vial_y + 48], fill=(200, 220, 220, 150))
    # Cloudiness inside vial
    for _ in range(20):
        cx = vial_x + random.randint(-8, 8)
        cy = vial_y + random.randint(5, 45)
        cr = random.randint(2, 6)
        draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(220, 235, 235, random.randint(60, 130)))
    # Vial cap
    draw.rectangle([vial_x - 8, vial_y - 12, vial_x + 8, vial_y], fill=(150, 160, 170))
    # Vial label
    draw.rectangle([vial_x - 8, vial_y + 15, vial_x + 8, vial_y + 30], fill=(200, 190, 170))
    # Light catching the vial (glow from window)
    for r in range(20, 0, -3):
        a = max(3, 30 - (20 - r) * 2)
        draw.ellipse([vial_x - r, vial_y - r, vial_x + r, vial_y + r + 50],
                     fill=(200, 220, 240, a))

    # Interior pharmacy elements (shelves in background)
    for sx in [900, 1100, 1350]:
        draw.rectangle([sx, 400, sx + 8, 1000], fill=(70, 60, 50))
        for sy in range(450, 1000, 80):
            draw.rectangle([sx - 60, sy, sx + 8, sy + 6], fill=(80, 70, 60))
            # Small bottles on shelves
            for bx in range(sx - 55, sx - 5, 12):
                bh = random.randint(15, 30)
                draw.rectangle([bx, sy - bh, bx + 8, sy], fill=(random.randint(140, 200), random.randint(140, 200), random.randint(140, 200), 150))

    # Harbor book / manifest on desk
    desk_x, desk_y = 400, 1200
    draw.rectangle([desk_x, desk_y, desk_x + 250, desk_y + 10], fill=(70, 60, 50))
    draw.rectangle([desk_x + 20, desk_y - 30, desk_x + 120, desk_y], fill=(180, 170, 150))
    draw.rectangle([desk_x + 130, desk_y - 20, desk_x + 200, desk_y], fill=(160, 150, 130))
    draw.rectangle([desk_x + 160, desk_y - 40, desk_x + 240, desk_y - 20], fill=(200, 190, 170))
    draw.text((desk_x + 25, desk_y - 25), "HARBOR BOOK", font=font("arialbd.ttf", 12), fill=(50, 45, 40))
    draw.text((desk_x + 165, desk_y - 38), "MANIFEST", font=font("arialbd.ttf", 12), fill=(50, 45, 40))

    tagline = "COLD CHAIN  TIDE LOGS  PUBLIC MEDICINE"
    tag_font = font("georgia.ttf", 34)
    bb = draw.textbbox((0, 0), tagline, font=tag_font)
    draw.text(((W - (bb[2] - bb[0])) // 2, 220), tagline, font=tag_font, fill=(230, 216, 178, 230))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Tidal Pharmacy")
    author = metadata.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = metadata.get("model", "")
    image = Image.new("RGBA", (W, H), (18, 52, 72, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw_tidal_pharmacy(draw)
    _draw_standard_cover_title_panel(image, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(output_path, "PNG", optimize=True)



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
