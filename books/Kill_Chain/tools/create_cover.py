#!/usr/bin/env python3
"""Cover: Kill Chain — Reaper drone silhouette in a burnt-orange desert sky seen through a targeting reticle with HUD ticks."""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import (
    _standard_cover_resolve_title,
    _standard_cover_resolve_author,
    _draw_standard_cover_title_panel,
)


WIDTH, HEIGHT = 1600, 2560
PANEL_Y = 1920

COLORS = {
    "sky_top": (30, 22, 18),
    "sky_mid": (120, 55, 20),
    "sky_bot": (200, 110, 40),
    "reticle": (255, 200, 90),
    "hud_dim": (220, 160, 60),
    "drone": (12, 10, 8),
    "ground": (35, 22, 12),
}


def make_gradient(draw: ImageDraw.ImageDraw) -> None:
    for y in range(PANEL_Y):
        t = y / PANEL_Y
        if t < 0.6:
            t2 = t / 0.6
            r = int(COLORS["sky_top"][0] + (COLORS["sky_mid"][0] - COLORS["sky_top"][0]) * t2)
            g = int(COLORS["sky_top"][1] + (COLORS["sky_mid"][1] - COLORS["sky_top"][1]) * t2)
            b = int(COLORS["sky_top"][2] + (COLORS["sky_mid"][2] - COLORS["sky_top"][2]) * t2)
        else:
            t2 = (t - 0.6) / 0.4
            r = int(COLORS["sky_mid"][0] + (COLORS["sky_bot"][0] - COLORS["sky_mid"][0]) * t2)
            g = int(COLORS["sky_mid"][1] + (COLORS["sky_bot"][1] - COLORS["sky_mid"][1]) * t2)
            b = int(COLORS["sky_mid"][2] + (COLORS["sky_bot"][2] - COLORS["sky_mid"][2]) * t2)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def draw_sun(draw: ImageDraw.ImageDraw) -> None:
    sx, sy, sr = WIDTH // 2 + 260, 1180, 190
    for i in range(6):
        r = sr + i * 45
        alpha = max(8, 60 - i * 10)
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 170, 70, alpha))
    draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 190, 90))


def draw_ground(draw: ImageDraw.ImageDraw) -> None:
    horizon = 1620
    draw.rectangle([0, horizon, WIDTH, PANEL_Y], fill=COLORS["ground"])
    random.seed(7)
    for _ in range(14):
        bx = random.randint(0, WIDTH - 60)
        bw = random.randint(20, 90)
        bh = random.randint(10, 55)
        draw.rectangle([bx, horizon - bh, bx + bw, horizon], fill=(25, 16, 9))
    draw.line([(0, horizon), (WIDTH, horizon)], fill=(60, 35, 18), width=2)


def draw_drone(draw: ImageDraw.ImageDraw) -> None:
    cx, cy = WIDTH // 2 - 120, 560
    s = 3.2
    c = COLORS["drone"]
    draw.polygon([
        (cx - int(20 * s), cy), (cx + int(150 * s), cy + int(6 * s)),
        (cx + int(165 * s), cy + int(14 * s)), (cx - int(10 * s), cy + int(12 * s)),
    ], fill=c)
    draw.ellipse([cx + int(140 * s), cy + int(2 * s), cx + int(172 * s), cy + int(20 * s)], fill=c)
    draw.polygon([
        (cx - int(15 * s), cy + int(4 * s)), (cx - int(190 * s), cy - int(28 * s)),
        (cx - int(185 * s), cy - int(16 * s)), (cx + int(10 * s), cy + int(10 * s)),
    ], fill=c)
    draw.polygon([
        (cx - int(15 * s), cy + int(4 * s)), (cx - int(190 * s), cy + int(40 * s)),
        (cx - int(185 * s), cy + int(28 * s)), (cx + int(10 * s), cy + int(10 * s)),
    ], fill=c)
    draw.polygon([
        (cx - int(20 * s), cy + int(2 * s)), (cx - int(60 * s), cy - int(45 * s)),
        (cx - int(48 * s), cy - int(45 * s)), (cx - int(5 * s), cy + int(4 * s)),
    ], fill=c)
    draw.polygon([
        (cx - int(20 * s), cy + int(10 * s)), (cx - int(70 * s), cy + int(50 * s)),
        (cx - int(58 * s), cy + int(52 * s)), (cx - int(5 * s), cy + int(12 * s)),
    ], fill=c)
    draw.ellipse([cx + int(120 * s), cy + int(14 * s), cx + int(138 * s), cy + int(32 * s)], fill=c)


def draw_reticle(draw: ImageDraw.ImageDraw) -> None:
    cx, cy = WIDTH // 2 - 60, 620
    r = 420
    c = COLORS["reticle"]
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=c, width=4)
    draw.ellipse([cx - r // 2, cy - r // 2, cx + r // 2, cy + r // 2], outline=COLORS["hud_dim"], width=2)
    tick = 26
    for ang in range(0, 360, 30):
        a = math.radians(ang)
        x1 = cx + int((r - tick) * math.cos(a))
        y1 = cy + int((r - tick) * math.sin(a))
        x2 = cx + int(r * math.cos(a))
        y2 = cy + int(r * math.sin(a))
        draw.line([(x1, y1), (x2, y2)], fill=c, width=3)
    draw.line([(cx - r - 60, cy), (cx - r + 60, cy)], fill=c, width=3)
    draw.line([(cx + r - 60, cy), (cx + r + 60, cy)], fill=c, width=3)
    draw.line([(cx, cy - r - 60), (cx, cy - r + 60)], fill=c, width=3)
    draw.line([(cx, cy + r - 60), (cx, cy + r + 60)], fill=c, width=3)
    box = 60
    draw.rectangle([cx - box, cy - box, cx + box, cy + box], outline=(255, 80, 60), width=3)
    for i in range(4):
        y = cy - r - 160 - i * 46
        w = random.randint(120, 320)
        draw.line([(cx - w // 2, y), (cx + w // 2, y)], fill=(COLORS["hud_dim"][0], COLORS["hud_dim"][1], COLORS["hud_dim"][2], 120), width=2)


def draw_scanlines(draw: ImageDraw.ImageDraw) -> None:
    for y in range(0, PANEL_Y, 6):
        draw.line([(0, y), (WIDTH, y)], fill=(0, 0, 0, 14))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    title = metadata["title"]
    author = metadata["author"]
    model = metadata.get("model", "")

    random.seed(42)
    img = Image.new("RGB", (WIDTH, HEIGHT), COLORS["sky_top"])
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    draw_sun(od)
    overlay = overlay.filter(ImageFilter.GaussianBlur(6))

    draw = ImageDraw.Draw(img, "RGBA")
    make_gradient(draw)
    img = Image.alpha_composite(img.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(img, "RGBA")
    draw_ground(draw)
    draw_drone(draw)
    draw_reticle(draw)
    draw_scanlines(draw)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(args.out, "PNG")
    print(f"Cover saved to {args.out}")


if __name__ == "__main__":
    main()
