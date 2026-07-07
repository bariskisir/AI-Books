#!/usr/bin/env python3
"""Cover: The Jade Dragon — Ruined temple courtyard at dusk, broken jade bell, mist in valley, figure in meditation pose."""

from __future__ import annotations
import argparse, json, math
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


WIDTH, HEIGHT = 1600, 2560


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()

    meta = json.loads(args.metadata.read_text(encoding="utf-8-sig"))
    title = meta.get("title", "The Jade Dragon")
    author = meta.get("author", "Barış Kısır")
    model = meta.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    rng = __import__("random").Random(11)

    # Dusk gradient: temple gray to mist white
    for y in range(HEIGHT):
        t = y / HEIGHT
        if t < 0.5:
            r = int(60 + 40 * (t / 0.5))
            g = int(65 + 35 * (t / 0.5))
            b = int(70 + 30 * (t / 0.5))
        else:
            r = int(100 + 80 * ((t - 0.5) / 0.5))
            g = int(100 + 85 * ((t - 0.5) / 0.5))
            b = int(100 + 90 * ((t - 0.5) / 0.5))
        draw.line([(0, y), (WIDTH, y)], fill=(max(0, r), max(0, g), max(0, b), 255))

    # Ruined temple courtyard walls
    # Left wall
    draw.polygon([(0, 600), (250, 550), (250, 900), (0, 950)], fill=(80, 75, 68))
    draw.polygon([(0, 600), (250, 550), (200, 530), (0, 580)], fill=(70, 65, 58))
    # Right wall
    draw.polygon([(WIDTH, 580), (1350, 530), (1350, 880), (WIDTH, 930)], fill=(75, 70, 63))
    draw.polygon([(WIDTH, 580), (1350, 530), (1400, 510), (WIDTH, 560)], fill=(65, 60, 53))

    # Crumbling stone columns
    for cx in [350, 500, 1100, 1250]:
        draw.rectangle((cx - 15, 500, cx + 15, 850), fill=(90, 85, 78))
        draw.rectangle((cx - 12, 500, cx + 12, 520), fill=(80, 75, 68))
        # Cracks
        if rng.random() > 0.5:
            draw.line((cx, 600, cx + 8, 650), fill=(60, 55, 48), width=2)

    # Broken jade bell on ground
    bx, by = WIDTH // 2, 780
    # Bell body (cracked)
    draw.polygon([(bx - 40, by), (bx - 30, by - 60), (bx + 30, by - 60), (bx + 40, by)], fill=(60, 120, 80))
    draw.polygon([(bx - 30, by - 60), (bx - 20, by - 80), (bx + 20, by - 80), (bx + 30, by - 60)], fill=(55, 110, 75))
    # Crack
    draw.line([(bx - 5, by - 75), (bx + 3, by - 40), (bx - 2, by - 10), (bx + 5, by)], fill=(40, 80, 55), width=2)
    # Broken piece
    draw.polygon([(bx + 30, by - 30), (bx + 50, by - 45), (bx + 40, by - 20)], fill=(50, 100, 65))
    # Jade shimmer
    draw.ellipse([bx - 15, by - 50, bx - 5, by - 35], fill=(80, 160, 110, 100))

    # Figure in meditation pose (foreground, shadows)
    fig_x = WIDTH // 2 + 30
    fig_y = 900
    # Body
    draw.ellipse((fig_x - 20, fig_y - 50, fig_x + 20, fig_y + 20), fill=(25, 20, 18, 200))
    draw.ellipse((fig_x - 12, fig_y - 65, fig_x + 12, fig_y - 48), fill=(25, 20, 18, 200))
    # Legs (crossed)
    draw.ellipse((fig_x - 30, fig_y + 15, fig_x, fig_y + 40), fill=(25, 20, 18, 180))
    draw.ellipse((fig_x, fig_y + 15, fig_x + 30, fig_y + 40), fill=(25, 20, 18, 180))
    # Arms (hands on knees)
    draw.line((fig_x - 18, fig_y - 30, fig_x - 25, fig_y + 10), fill=(25, 20, 18, 180), width=5)
    draw.line((fig_x + 18, fig_y - 30, fig_x + 25, fig_y + 10), fill=(25, 20, 18, 180), width=5)

    # Mist in valley (background)
    mist = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    md = ImageDraw.Draw(mist)
    for _ in range(30):
        mx = int(rng.random() * WIDTH)
        my = int(400 + 400 * rng.random())
        mw = int(200 + 500 * rng.random())
        mh = int(30 + 60 * rng.random())
        md.ellipse((mx - mw // 2, my - mh // 2, mx + mw // 2, my + mh // 2), fill=(180, 185, 190, 12))
    mist = mist.filter(ImageFilter.GaussianBlur(35))
    img = Image.alpha_composite(img, mist)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.save(args.out, "PNG")


if __name__ == "__main__":
    main()
