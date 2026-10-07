#!/usr/bin/env python3
"""Cover: The Persuasion Engine — Human head silhouette filled with concentric signal ripples dissolving into thousands of tiny particles, cold indigo and pale cyan palette."""

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
    "bg_top": (8, 10, 40),
    "bg_mid": (16, 18, 66),
    "bg_bot": (4, 4, 22),
    "accent_indigo": (60, 60, 160),
    "accent_cyan": (140, 220, 255),
    "accent_dim": (30, 34, 80),
    "panel_bg": (240, 240, 248),
    "title_text": (10, 12, 44),
    "author_text": (70, 72, 110),
}


def make_gradient(draw: ImageDraw.ImageDraw) -> None:
    for y in range(PANEL_Y):
        t = y / PANEL_Y
        if t < 0.5:
            t2 = t * 2
            r = int(COLORS["bg_top"][0] + (COLORS["bg_mid"][0] - COLORS["bg_top"][0]) * t2)
            g = int(COLORS["bg_top"][1] + (COLORS["bg_mid"][1] - COLORS["bg_top"][1]) * t2)
            b = int(COLORS["bg_top"][2] + (COLORS["bg_mid"][2] - COLORS["bg_top"][2]) * t2)
        else:
            t2 = (t - 0.5) * 2
            r = int(COLORS["bg_mid"][0] + (COLORS["bg_bot"][0] - COLORS["bg_mid"][0]) * t2)
            g = int(COLORS["bg_mid"][1] + (COLORS["bg_bot"][1] - COLORS["bg_mid"][1]) * t2)
            b = int(COLORS["bg_mid"][2] + (COLORS["bg_bot"][2] - COLORS["bg_mid"][2]) * t2)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def draw_ripples(draw: ImageDraw.ImageDraw, center: tuple[int, int], count: int = 26) -> None:
    cx, cy = center
    for i in range(count):
        radius = 30 + i * 34
        alpha = max(6, 60 - i * 2)
        draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            outline=(COLORS["accent_cyan"][0], COLORS["accent_cyan"][1], COLORS["accent_cyan"][2], alpha),
            width=max(1, 3 - i // 8),
        )


def draw_particle_field(draw: ImageDraw.ImageDraw, center: tuple[int, int]) -> None:
    cx, cy = center
    for _ in range(2500):
        angle = random.uniform(0, math.tau)
        dist = random.expovariate(0.004)
        x = int(cx + math.cos(angle) * dist)
        y = int(cy + math.sin(angle) * dist * 0.8)
        if 0 <= x < WIDTH and 0 <= y < PANEL_Y:
            tint = random.choice([COLORS["accent_cyan"], COLORS["accent_indigo"], (220, 240, 255)])
            alpha = random.randint(20, 120)
            draw.point((x, y), fill=(tint[0], tint[1], tint[2], alpha))


def draw_head_silhouette(draw: ImageDraw.ImageDraw, center: tuple[int, int]) -> None:
    cx, cy = center
    head = [
        (cx - 230, cy + 60),
        (cx - 240, cy - 180),
        (cx - 160, cy - 330),
        (cx - 30, cy - 400),
        (cx + 120, cy - 380),
        (cx + 210, cy - 260),
        (cx + 240, cy - 80),
        (cx + 200, cy + 90),
        (cx + 120, cy + 220),
        (cx + 40, cy + 300),
        (cx - 30, cy + 300),
        (cx - 160, cy + 240),
        (cx - 230, cy + 140),
    ]
    draw.polygon(head, fill=(14, 16, 52), outline=(120, 200, 255, 160))
    for _ in range(1400):
        x = random.randint(cx - 240, cx + 240)
        y = random.randint(cy - 400, cy + 320)
        if 0 <= x < WIDTH and 0 <= y < PANEL_Y:
            draw.point((x, y), fill=(140, 220, 255, random.randint(15, 80)))


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

    center = (WIDTH // 2, PANEL_Y // 2 - 80)
    draw_head_silhouette(draw, center)
    draw_ripples(draw, center)
    draw_particle_field(draw, center)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.save(args.out, "PNG")
    print(f"Cover saved to {args.out}")


if __name__ == "__main__":
    main()
