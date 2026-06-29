#!/usr/bin/env python3
"""
Cover art for The Tessera Bureau.

Scene: a city fractured into adjacent parallel panes. A cool institutional
dusk over a tessellated grid; a skyline printed twice and slightly offset,
cyan and magenta, like a misregistered print — the two worlds drifting toward
each other. At the center a single warm doorway of light, a seam standing open,
and one small figure on the threshold deciding whether to step through.
"""

from __future__ import annotations

import argparse
import json
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


WIDTH = 1600
HEIGHT = 2560
ART_HEIGHT = 1765


def draw_background(draw: ImageDraw.ImageDraw) -> None:
    """Cool grey-blue institutional dusk."""
    for y in range(ART_HEIGHT):
        t = y / ART_HEIGHT
        r = int(34 + (78 - 34) * t)
        g = int(40 + (92 - 40) * t)
        b = int(58 + (110 - 58) * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def draw_tessellation(image: Image.Image) -> None:
    """A faint diamond-tile grid laid over the whole field — the city tessellated."""
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    step = 96
    col = (150, 170, 200, 26)
    for gy in range(-step, ART_HEIGHT + step, step):
        for gx in range(-step, WIDTH + step, step):
            od.line([(gx, gy + step // 2), (gx + step // 2, gy)], fill=col, width=2)
            od.line([(gx + step // 2, gy), (gx + step, gy + step // 2)], fill=col, width=2)
            od.line([(gx + step, gy + step // 2), (gx + step // 2, gy + step)], fill=col, width=2)
            od.line([(gx + step // 2, gy + step), (gx, gy + step // 2)], fill=col, width=2)
    image.paste(Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB"), (0, 0))


def _skyline(draw: ImageDraw.ImageDraw, base_y: int, color, dx: int) -> None:
    """A row of towers in a single flat color, offset by dx."""
    import random
    rng = random.Random(7)
    x = -40 + dx
    while x < WIDTH + 40:
        w = rng.choice([70, 90, 110, 140, 60])
        h = rng.choice([360, 520, 680, 440, 600, 300])
        top = base_y - h
        draw.rectangle([(x, top), (x + w, base_y)], fill=color)
        # a few lit windows as the same flat color, lighter
        x += w + rng.choice([10, 18, 26])


def draw_offset_skylines(image: Image.Image) -> None:
    """Two skylines, cyan and magenta, slightly offset — misregistered panes."""
    base_y = 1180
    cyan = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    mag = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    _skyline(ImageDraw.Draw(cyan), base_y, (70, 200, 210, 120), dx=-16)
    _skyline(ImageDraw.Draw(mag), base_y, (210, 70, 150, 110), dx=16)
    merged = Image.alpha_composite(image.convert("RGBA"), cyan)
    merged = Image.alpha_composite(merged, mag)
    image.paste(merged.convert("RGB"), (0, 0))


def draw_seam(image: Image.Image) -> None:
    """A vertical doorway of warm light at the center — the open seam."""
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    cx = WIDTH // 2
    door_w, door_h = 150, 470
    top = 740
    # halo
    for r in range(220, 0, -6):
        a = int(70 * (1 - r / 220))
        gd.ellipse([(cx - door_w // 2 - r, top - r), (cx + door_w // 2 + r, top + door_h + r)],
                   fill=(255, 226, 150, max(0, a // 5)))
    # the bright slit
    for i in range(door_w // 2, 0, -1):
        t = i / (door_w / 2)
        a = int(255 * (1 - t) ** 1.5)
        gd.rectangle([(cx - i, top), (cx + i, top + door_h)], fill=(255, 235, 180, a))
    gd.rectangle([(cx - 10, top), (cx + 10, top + door_h)], fill=(255, 248, 224, 255))
    glow = glow.filter(ImageFilter.GaussianBlur(3))
    image.paste(Image.alpha_composite(image.convert("RGBA"), glow).convert("RGB"), (0, 0))


def draw_figure(draw: ImageDraw.ImageDraw) -> None:
    """A small lone figure on the threshold, silhouetted against the seam."""
    cx = WIDTH // 2
    base = 1210
    col = (16, 18, 26)
    # legs
    draw.line([(cx - 16, base), (cx - 8, base - 70)], fill=col, width=15)
    draw.line([(cx + 16, base), (cx + 8, base - 70)], fill=col, width=15)
    # torso
    draw.line([(cx, base - 64), (cx, base - 150)], fill=col, width=30)
    # head
    draw.ellipse([(cx - 20, base - 196), (cx + 20, base - 150)], fill=col)
    # long shadow toward viewer
    draw.polygon([(cx - 22, base), (cx + 22, base), (cx + 70, base + 130), (cx - 70, base + 130)],
                 fill=(20, 24, 34))


def create_cover(metadata_path: str, out_path: str) -> None:
    metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    title = metadata.get("title", "The Tessera Bureau")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    image = Image.new("RGB", (WIDTH, HEIGHT), (40, 48, 66))
    # overlays are full-height so alpha_composite matches the base image size
    draw = ImageDraw.Draw(image)

    draw_background(draw)
    draw_tessellation(image)
    draw_offset_skylines(image)
    draw_seam(image)
    draw_figure(ImageDraw.Draw(image))

    _draw_standard_cover_title_panel(image, title=title, author=author, model=model)

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    image.save(out_path, "PNG")
    print(f"Cover saved: {out_path}")


# ---------------------------------------------------------------------------
# Standard cover helpers
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    create_cover(args.metadata, args.out)

if __name__ == "__main__":
    main()
