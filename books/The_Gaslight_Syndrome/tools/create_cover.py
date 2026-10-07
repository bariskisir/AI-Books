#!/usr/bin/env python3
"""Cover: The Gaslight Syndrome — fractured mirror, dim violet-grey palette, doubled silhouette."""

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
    "bg_top": (18, 14, 26),
    "bg_mid": (38, 32, 52),
    "bg_bot": (10, 8, 16),
    "violet_dim": (72, 58, 96),
    "violet_edge": (110, 92, 140),
    "grey_shard": (90, 88, 104),
    "shatter_line": (150, 138, 170),
    "panel_bg": (240, 238, 246),
    "title_text": (22, 16, 34),
    "author_text": (70, 64, 88),
}


def draw_silhouette(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float, color, dy: int = 0) -> None:
    head_r = int(120 * scale)
    head_cx, head_cy = cx, cy - int(160 * scale) + dy
    draw.ellipse([head_cx - head_r, head_cy - head_r, head_cx + head_r, head_cy + head_r], fill=color)
    neck_w = int(60 * scale)
    body_top = head_cy + head_r - int(20 * scale)
    body_bot = cy + int(380 * scale) + dy
    points = [
        (cx - neck_w, body_top),
        (cx + neck_w, body_top),
        (cx + int(150 * scale), body_bot),
        (cx - int(150 * scale), body_bot),
    ]
    draw.polygon(points, fill=color)
    draw.polygon(
        [(cx - int(150 * scale), body_bot), (cx + int(150 * scale), body_bot), (cx + int(220 * scale), body_bot + int(140 * scale)), (cx - int(220 * scale), body_bot + int(140 * scale))],
        fill=color,
    )
    mole_x = cx + int(28 * scale)
    draw.ellipse([mole_x - 8, head_cy - 8, mole_x + 8, head_cy + 8], fill=(6, 4, 10))


def draw_shards(draw: ImageDraw.ImageDraw) -> None:
    for _ in range(26):
        x = random.randint(60, WIDTH - 60)
        y = random.randint(80, PANEL_Y - 160)
        size = random.randint(20, 90)
        angle = random.uniform(0, 2 * math.pi)
        pts = []
        for i in range(3):
            a = angle + i * 2 * math.pi / 3 + random.uniform(-0.3, 0.3)
            pts.append((x + math.cos(a) * size * random.uniform(0.4, 1.0), y + math.sin(a) * size * random.uniform(0.4, 1.0)))
        draw.polygon(pts, outline=COLORS["shatter_line"], fill=(30, 26, 44))
    for _ in range(50):
        x = random.randint(0, WIDTH)
        y = random.randint(0, PANEL_Y)
        angle = random.uniform(0, math.pi)
        length = random.randint(30, 220)
        draw.line([(x, y), (x + math.cos(angle) * length, y + math.sin(angle) * length)], fill=(*COLORS["shatter_line"], 60), width=1)


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
    draw_shards(draw)

    draw_silhouette(draw, WIDTH // 2 - 40, 1100, 1.0, (6, 4, 10))
    draw_silhouette(draw, WIDTH // 2 + 40, 1120, 1.0, (40, 32, 58, 200), dy=18)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.save(args.out, "PNG")
    print(f"Cover saved to {args.out}")


if __name__ == "__main__":
    main()
