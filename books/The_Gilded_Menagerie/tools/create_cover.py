#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Gilded Menagerie."""

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
FONTS_DIR = Path("C:/Windows/Fonts")

WIDTH, HEIGHT = 1600, 2560
TITLE_PANEL_TOP = 1920


def rel(path: str | Path) -> Path:
    p = Path(path)
    return ROOT / p if not p.is_absolute() else p


def lerp_color(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def draw_gradient(draw: ImageDraw, width: int, height: int) -> None:
    """Deep indigo twilight at the top warming to crimson and gaslight gold near the horizon."""
    for y in range(height):
        if y < height * 0.30:
            t = y / (height * 0.30)
            c = lerp_color((18, 14, 42), (44, 22, 70), t)
        elif y < height * 0.55:
            t = (y - height * 0.30) / (height * 0.25)
            c = lerp_color((44, 22, 70), (104, 36, 66), t)
        elif y < height * 0.72:
            t = (y - height * 0.55) / (height * 0.17)
            c = lerp_color((104, 36, 66), (168, 70, 52), t)
        else:
            t = (y - height * 0.72) / (height * 0.28)
            c = lerp_color((168, 70, 52), (96, 44, 30), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_dusk_glow(draw: ImageDraw, width: int, height: int) -> None:
    """A warm halo of gaslight glow rising behind the tent."""
    cx = width // 2
    cy = int(height * 0.62)
    for r in range(900, 0, -6):
        t = r / 900
        alpha = int(60 * (1 - t))
        if alpha <= 0:
            continue
        col = lerp_color((255, 196, 96), (180, 70, 50), t)
        draw.ellipse(
            [cx - r, cy - int(r * 0.7), cx + r, cy + int(r * 0.7)],
            fill=(col[0], col[1], col[2], alpha),
        )


def draw_field(draw: ImageDraw, width: int, height: int) -> None:
    """Trampled muddy fairground at the base, dark and wet."""
    import random

    rng = random.Random(13)
    base_y = height * 0.80
    ground = (38, 26, 24)
    for x in range(0, width + 1, 2):
        y = base_y + math.sin(x * 0.004) * 10 + rng.randint(-4, 4)
        draw.line([(x, int(y)), (x, height)], fill=ground)
    # Puddles catching the gold light
    for _ in range(14):
        px = rng.randint(80, width - 80)
        py = rng.randint(int(base_y) + 40, height - 60)
        pw = rng.randint(30, 110)
        ph = rng.randint(8, 22)
        draw.ellipse([px - pw, py - ph, px + pw, py + ph], fill=(150, 96, 54, 70))


def draw_big_top(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the striped big-top tent with center pole and pennant."""
    cx = width // 2
    base_y = int(height * 0.80)
    peak_y = int(height * 0.30)
    half_w = 520

    # Canvas stripes radiating from the peak
    stripe_count = 14
    left = cx - half_w
    for i in range(stripe_count):
        x0 = left + i * (2 * half_w / stripe_count)
        x1 = left + (i + 1) * (2 * half_w / stripe_count)
        col = (196, 54, 48) if i % 2 == 0 else (236, 224, 206)
        draw.polygon(
            [(cx, peak_y), (int(x0), base_y), (int(x1), base_y)],
            fill=col,
        )

    # Scalloped valance along the eaves
    scallops = 16
    for i in range(scallops):
        sx = left + i * (2 * half_w / scallops)
        col = (160, 40, 38) if i % 2 == 0 else (210, 196, 176)
        draw.pieslice(
            [int(sx), base_y - 26, int(sx + 2 * half_w / scallops), base_y + 26],
            0, 180, fill=col,
        )

    # Shadowed tent mouth (dark entrance)
    door_w = 120
    draw.polygon(
        [(cx, peak_y + 220), (cx - door_w, base_y), (cx + door_w, base_y)],
        fill=(28, 16, 24),
    )
    # Warm light spilling from the entrance
    draw.polygon(
        [(cx, peak_y + 380), (cx - door_w + 40, base_y), (cx + door_w - 40, base_y)],
        fill=(255, 198, 110, 120),
    )

    # Center pole and pennant flag at the peak
    draw.line([(cx, peak_y), (cx, peak_y - 90)], fill=(40, 28, 20), width=6)
    draw.polygon(
        [(cx, peak_y - 90), (cx + 70, peak_y - 70), (cx, peak_y - 50)],
        fill=(214, 176, 64),
    )


def draw_string_lights(draw: ImageDraw, width: int, height: int) -> None:
    """Strings of warm bulbs swagging across the fairground sky."""
    import random

    rng = random.Random(41)
    cx = width // 2
    anchors = [
        (120, height * 0.34, cx - 60, height * 0.40),
        (cx + 60, height * 0.40, width - 120, height * 0.34),
        (180, height * 0.50, width - 180, height * 0.52),
    ]
    for ax, ay, bx, by in anchors:
        sag = 90
        steps = 60
        for s in range(steps + 1):
            t = s / steps
            x = ax + (bx - ax) * t
            y = ay + (by - ay) * t + math.sin(t * math.pi) * sag
            if s % 4 == 0:
                r = 7
                # bulb glow
                draw.ellipse([x - r - 4, y - r - 4, x + r + 4, y + r + 4], fill=(255, 210, 120, 70))
                col = rng.choice([(255, 224, 150), (255, 196, 120), (255, 240, 200)])
                draw.ellipse([x - r, y - r, x + r, y + r], fill=col)


def draw_trapeze_silhouette(draw: ImageDraw, width: int, height: int) -> None:
    """A lone trapeze artist silhouetted high under the canvas glow."""
    cx = width // 2
    bar_y = int(height * 0.42)
    bar_x = cx + 150

    # Rigging lines down from the unseen peak
    draw.line([(bar_x - 60, bar_y - 150), (bar_x - 60, bar_y)], fill=(20, 14, 18), width=3)
    draw.line([(bar_x + 60, bar_y - 150), (bar_x + 60, bar_y)], fill=(20, 14, 18), width=3)
    # The bar
    draw.line([(bar_x - 60, bar_y), (bar_x + 60, bar_y)], fill=(16, 10, 14), width=5)

    # Figure hanging from the bar, arms up, legs arched
    fx, fy = bar_x, bar_y
    body = (14, 10, 16)
    # arms to bar
    draw.line([(fx - 18, fy + 4), (fx, fy + 40)], fill=body, width=7)
    draw.line([(fx + 18, fy + 4), (fx, fy + 40)], fill=body, width=7)
    # torso
    draw.line([(fx, fy + 40), (fx + 6, fy + 96)], fill=body, width=10)
    # head
    draw.ellipse([fx - 9, fy + 30, fx + 9, fy + 48], fill=body)
    # arched legs
    draw.line([(fx + 6, fy + 96), (fx + 44, fy + 120)], fill=body, width=8)
    draw.line([(fx + 44, fy + 120), (fx + 70, fy + 92)], fill=body, width=7)
    draw.line([(fx + 6, fy + 96), (fx + 30, fy + 134)], fill=body, width=8)
    draw.line([(fx + 30, fy + 134), (fx + 58, fy + 116)], fill=body, width=7)


def draw_birds(draw: ImageDraw, width: int, height: int) -> None:
    """A few distant birds against the twilight."""
    import random

    rng = random.Random(7)
    for _ in range(9):
        x = rng.randint(120, width - 120)
        y = rng.randint(int(height * 0.12), int(height * 0.26))
        s = rng.randint(8, 16)
        draw.line([(x - s, y), (x, y - s // 2)], fill=(30, 20, 30), width=2)
        draw.line([(x, y - s // 2), (x + s, y)], fill=(30, 20, 30), width=2)


def draw_dust(draw: ImageDraw, width: int, height: int) -> None:
    """Sparse motes of sawdust and light drifting in the glow."""
    import random

    rng = random.Random(29)
    for _ in range(160):
        x = rng.randint(10, width - 10)
        y = rng.randint(int(height * 0.30), height - 220)
        size = rng.randint(1, 3)
        alpha = rng.randint(40, 130)
        draw.ellipse(
            [x - size, y - size, x + size, y + size],
            fill=(255, 226, 170, alpha),
        )


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Gilded Menagerie")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Step 1: Twilight gradient sky
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Warm gaslight halo behind the tent
    draw_dusk_glow(draw, WIDTH, HEIGHT)

    # Step 3: Distant birds in the dusk
    draw_birds(draw, WIDTH, HEIGHT)

    # Step 4: Muddy fairground
    draw_field(draw, WIDTH, HEIGHT)

    # Step 5: The striped big-top tent
    draw_big_top(draw, WIDTH, HEIGHT)

    # Step 6: Lone trapeze silhouette under the canvas
    draw_trapeze_silhouette(draw, WIDTH, HEIGHT)

    # Step 7: Strings of warm bulbs
    draw_string_lights(draw, WIDTH, HEIGHT)

    # Step 8: Drifting sawdust motes
    draw_dust(draw, WIDTH, HEIGHT)

    # Soften slightly
    img = img.filter(ImageFilter.SMOOTH)

    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    metadata_path = rel(args.metadata)
    output_path = rel(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    create_cover(metadata_path, output_path)


if __name__ == "__main__":
    main()