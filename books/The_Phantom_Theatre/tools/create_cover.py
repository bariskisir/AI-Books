#!/usr/bin/env python3
"""Cover: The Phantom Theatre — Alpine sanatorium at dusk, grey silhouette in theatre stage wings, lone woman in red coat on stage."""

from __future__ import annotations

import argparse
import json
import sys
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import (
    _standard_cover_font,
    _standard_cover_repair_text,
    _standard_cover_center,
    _standard_cover_title_font,
    _standard_cover_resolve_title,
    _standard_cover_resolve_author,
    _draw_standard_cover_title_panel,
    W, H, PANEL_Y,
)

from PIL import Image, ImageDraw, ImageFilter


def make_cover(metadata_path: Path, out_path: Path) -> None:
    with open(metadata_path, encoding="utf-8") as f:
        meta = json.load(f)

    title = _standard_cover_resolve_title(meta)
    author = _standard_cover_resolve_author(meta)
    model = meta.get("model", "")

    img = Image.new("RGBA", (W, H), (20, 18, 30, 255))
    draw = ImageDraw.Draw(img)

    # Alpine sky gradient
    for y in range(800):
        t = y / 800
        if t < 0.5:
            c = (int(15 + 15 * t * 2), int(14 + 12 * t * 2), int(30 + 20 * t * 2))
        else:
            c = (int(30 + 30 * (t - 0.5) * 2), int(26 + 20 * (t - 0.5) * 2), int(50 + 10 * (t - 0.5) * 2))
        draw.line((0, y, W, y), fill=(*c, 255))

    # Alpine sanatorium building
    # Main building
    draw.rectangle((400, 600, 1200, 1100), fill=(60, 56, 52, 230))
    draw.polygon([(380, 600), (800, 520), (1220, 600)], fill=(50, 46, 42, 230))
    # Windows
    for wx in [450, 580, 710, 840, 970, 1100]:
        draw.rectangle((wx, 650, wx + 50, 720), fill=(220, 200, 160, 150))
    # Dark wings
    draw.rectangle((200, 650, 400, 1000), fill=(45, 42, 38, 220))
    draw.rectangle((1200, 650, 1400, 1000), fill=(45, 42, 38, 220))

    # Stage wings silhouette (left side)
    draw.polygon([(0, 500), (250, 500), (300, 700), (280, 900), (0, 1000)], fill=(70, 68, 75, 200))

    # Grey silhouette in wings
    sx, sy = 200, 650
    draw.ellipse((sx - 15, sy - 35, sx + 15, sy - 5), fill=(70, 68, 72, 220))
    draw.polygon([(sx - 20, sy - 5), (sx + 20, sy - 5), (sx + 28, sy + 80), (sx - 28, sy + 80)], fill=(70, 68, 72, 220))

    # Lone woman on stage in red coat
    wx2, wy2 = 800, 780
    # Red coat body
    draw.polygon([(wx2 - 22, wy2 + 70), (wx2 - 28, wy2 + 180), (wx2 + 28, wy2 + 180), (wx2 + 22, wy2 + 70)], fill=(180, 30, 35, 230))
    draw.polygon([(wx2 - 22, wy2 + 70), (wx2, wy2 + 10), (wx2 + 22, wy2 + 70)], fill=(180, 30, 35, 230))
    # Head
    draw.ellipse((wx2 - 12, wy2 - 12, wx2 + 12, wy2 + 12), fill=(40, 38, 36, 230))
    # Red coat outline
    draw.line((wx2 - 28, wy2 + 70, wx2 - 28, wy2 + 180), fill=(140, 20, 25, 255), width=3)
    draw.line((wx2 + 28, wy2 + 70, wx2 + 28, wy2 + 180), fill=(140, 20, 25, 255), width=3)

    # Stage floor
    draw.rectangle((100, 1050, 1500, 1065), fill=(50, 46, 44, 200))
    draw.line((100, 1065, 1500, 1065), fill=(30, 28, 26, 255), width=2)

    # Spotlight on stage
    spot = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(spot)
    sd.polygon([(wx2, 400), (wx2 - 60, 1050), (wx2 + 60, 1050)], fill=(255, 230, 200, 15))
    sd.ellipse((wx2 - 40, 1050, wx2 + 40, 1080), fill=(255, 230, 200, 25))
    spot = spot.filter(ImageFilter.GaussianBlur(10))
    img = Image.alpha_composite(img, spot)

    _draw_standard_cover_title_panel(img, title, author, model)
    img.save(out_path)
    print(f"Cover saved to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    make_cover(args.metadata, args.out)
