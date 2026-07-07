#!/usr/bin/env python3
"""Cover: The Last Tide — Small research vessel crossing blazing sunset line, tiger swimming through oil-slick water, sunset blaze/ocean blue/tiger orange."""

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


def font(name: str, size: int):
    candidates = [
        FONT_DIR / name,
        FONT_DIR / "arialbd.ttf",
        FONT_DIR / "arial.ttf",
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def draw_mangrove_labyrinth(draw: ImageDraw.ImageDraw) -> None:
    """Draw a mangrove labyrinth at sunset — stilt houses, amber water, rowboat, fireflies."""
    random.seed("the-last-tide-cover-2026")

    # ── Sky gradient: deep violet (top) → orange (horizon) ──────────────────
    for y in range(900):
        t = y / 900.0
        r = int(38 * (1 - t) + 230 * t)
        g = int(18 * (1 - t) + 130 * t)
        b = int(60 * (1 - t) + 40 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── Sun disk on the horizon ──────────────────────────────────────────────
    sun_cx, sun_cy = 720, 840
    for rad, alpha in [(220, 25), (170, 40), (120, 60), (72, 80), (40, 175)]:
        draw.ellipse(
            (sun_cx - rad, sun_cy - rad, sun_cx + rad, sun_cy + rad),
            fill=(254, 210, 90, alpha),
        )
    draw.ellipse(
        (sun_cx - 22, sun_cy - 22, sun_cx + 22, sun_cy + 22),
        fill=(255, 232, 140, 240),
    )

    # ── Water: deep warm amber grading to dark teal ──────────────────────────
    for y in range(870, 1765):
        t = (y - 870) / 895.0
        r = int(175 * (1 - t * 0.55) + 28 * t)
        g = int(92 * (1 - t * 0.5) + 40 * t)
        b = int(40 * (1 - t * 0.3) + 52 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── Sun reflection on water ──────────────────────────────────────────────
    reflect = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(reflect, "RGBA")
    for i in range(30):
        offset_y = 878 + i * random.randint(14, 38)
        seg_w = max(20, 180 - i * 3)
        seg_x = sun_cx - seg_w // 2 + random.randint(-25, 25)
        alpha = max(18, 110 - i * 3)
        rd.rectangle(
            (seg_x, offset_y, seg_x + seg_w, offset_y + 5),
            fill=(255, 200, 80, alpha),
        )
    reflect = reflect.filter(ImageFilter.GaussianBlur(4))
    draw.bitmap((0, 0), reflect, fill=None)

    # ── Mangrove roots (dense, twisted, rising from the water) ──────────────
    root_colors = [
        (55, 42, 28, 235),
        (45, 35, 22, 240),
        (38, 30, 20, 230),
        (70, 54, 34, 220),
        (48, 37, 24, 245),
        (35, 28, 18, 235),
    ]

    # Stilt-like prop roots — the signature of Sundarbans mangroves
    root_base_y = random.randint(900, 960)
    for root_x in range(20, W, random.randint(38, 75)):
        root_color = random.choice(root_colors)
        trunk_h = random.randint(220, 520)
        trunk_w = random.randint(14, 30)
        draw.rectangle(
            (root_x, root_base_y - trunk_h, root_x + trunk_w, root_base_y),
            fill=root_color,
        )
        # Branched prop roots arching outward
        for _ in range(random.randint(3, 7)):
            bx = root_x + random.randint(-8, trunk_w + 8)
            bend = random.choice([-1, 1])
            draw.line(
                (
                    bx, root_base_y - random.randint(20, trunk_h - 40),
                    bx + bend * random.randint(30, 130),
                    root_base_y - random.randint(60, trunk_h - 80),
                ),
                fill=root_color,
                width=random.randint(3, 10),
            )
            # Secondary branching
            bx2 = bx + bend * random.randint(30, 130)
            by2 = root_base_y - random.randint(60, trunk_h - 80)
            for _ in range(2):
                b2_bend = random.choice([-1, 1])
                draw.line(
                    (
                        bx2, by2,
                        bx2 + b2_bend * random.randint(15, 55),
                        by2 - random.randint(10, 40),
                    ),
                    fill=root_color,
                    width=random.randint(2, 5),
                )

        # Dense canopy (green-black foliage), a bit higher
        canopy_y = root_base_y - trunk_h - random.randint(5, 25)
        canopy_w = random.randint(60, 140)
        canopy_h = random.randint(35, 75)
        foliage_color = (
            random.randint(18, 38),
            random.randint(38, 65),
            random.randint(16, 30),
            235,
        )
        draw.ellipse(
            (root_x - canopy_w // 2, canopy_y - canopy_h,
             root_x + trunk_w + canopy_w // 2, canopy_y),
            fill=foliage_color,
        )
        # Lighter highlight on some foliage
        if random.random() < 0.3:
            hl_color = (
                random.randint(50, 90),
                random.randint(90, 130),
                random.randint(30, 55),
                100,
            )
            draw.ellipse(
                (root_x - canopy_w // 3, canopy_y - canopy_h // 2,
                 root_x + trunk_w + canopy_w // 3, canopy_y - 4),
                fill=hl_color,
            )

    # ── Wooden stilt houses half-submerged ───────────────────────────────────
    house_data = [
        (180, 1050, "left"),
        (480, 1070, "left"),
        (1020, 1040, "right"),
        (1280, 1065, "right"),
    ]
    for hx, hy, side in house_data:
        # Stilts
        for sx_offset in (10, 50, 90):
            draw.line(
                (hx + sx_offset, hy + 75, hx + sx_offset + 3, hy + 85 + random.randint(25, 55)),
                fill=(58, 44, 32, 235),
                width=5,
            )
            draw.line(
                (hx + sx_offset + 3, hy + 85 + random.randint(25, 55),
                 hx + sx_offset - (10 if side == "left" else -10),
                 hy + 85 + random.randint(25, 55)),
                fill=(58, 44, 32, 235),
                width=3,
            )

        # House body (partially submerged)
        sub_h = random.randint(20, 50)
        draw.rectangle(
            (hx, hy + sub_h, hx + 100, hy + 75),
            fill=(78, 60, 38, 240),
            outline=(58, 44, 30, 220),
            width=3,
        )
        # Roof (palm thatch)
        draw.polygon(
            [
                (hx - 10, hy + sub_h),
                (hx + 50, hy - 18),
                (hx + 110, hy + sub_h),
            ],
            fill=(82, 56, 28, 245),
            outline=(55, 38, 18, 210),
        )
        # Window
        draw.rectangle(
            (hx + 30, hy + sub_h + 18, hx + 70, hy + sub_h + 48),
            fill=(25, 18, 12, 230),
        )
        # Window glow
        draw.rectangle(
            (hx + 33, hy + sub_h + 21, hx + 67, hy + sub_h + 45),
            fill=(240, 180, 55, 60),
        )
        # Door
        draw.rectangle(
            (hx + 20, hy + sub_h + 28, hx + 30, hy + 75),
            fill=(45, 34, 22, 230),
        )

    # ── Small rowboat between twisted roots ──────────────────────────────────
    boat_x = 740
    boat_y = 980
    draw.ellipse(
        (boat_x, boat_y, boat_x + 120, boat_y + 28),
        fill=(65, 48, 30, 235),
        outline=(48, 34, 20, 220),
        width=3,
    )
    # Boat interior
    draw.ellipse(
        (boat_x + 6, boat_y + 4, boat_x + 114, boat_y + 24),
        fill=(72, 54, 34, 240),
    )
    # Gunwale line
    draw.line(
        (boat_x + 8, boat_y + 6, boat_x + 112, boat_y + 6),
        fill=(42, 31, 18, 200),
        width=2,
    )
    # Bow detail
    draw.polygon(
        [
            (boat_x, boat_y + 2),
            (boat_x - 8, boat_y - 2),
            (boat_x - 4, boat_y + 14),
            (boat_x, boat_y + 10),
        ],
        fill=(55, 40, 24, 235),
    )
    # Oar
    draw.line(
        (boat_x + 40, boat_y - 20, boat_x + 85, boat_y + 32),
        fill=(88, 65, 38, 230),
        width=4,
    )
    # Oar blade
    draw.ellipse(
        (boat_x + 78, boat_y + 28, boat_x + 98, boat_y + 42),
        fill=(72, 52, 30, 230),
    )

    # ── Water ripple rings around roots and boat ─────────────────────────────
    for cx, cy, rmax in [
        (boat_x + 60, boat_y + 28, 55),
        (180, 1100, 35),
        (480, 1120, 28),
        (1020, 1090, 32),
        (1280, 1115, 30),
    ]:
        for r in range(1, 4):
            rad = r * (rmax // 3)
            draw.ellipse(
                (cx - rad, cy - rad // 2, cx + rad, cy + rad // 2),
                outline=(200, 155, 70, max(10, 50 - r * 14)),
                width=1,
            )

    # ── Half-submerged debris and fallen trees ───────────────────────────────
    for _ in range(8):
        dx = random.randint(50, 1550)
        dy = random.randint(1020, 1400)
        debris_color = (random.randint(40, 65), random.randint(30, 50), random.randint(18, 32), 200)
        draw.line(
            (dx, dy, dx + random.randint(40, 120), dy + random.randint(-15, 15)),
            fill=debris_color,
            width=random.randint(4, 8),
        )

    # ── Fireflies (glowing gold dots scattered through the scene) ────────────
    firefly_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(firefly_layer, "RGBA")
    for _ in range(200):
        fx = random.randint(50, 1550)
        fy = random.randint(350, 1400)
        glow_radius = random.randint(8, 22)
        core_radius = random.randint(2, 5)
        glow_alpha = random.randint(50, 140)
        core_alpha = random.randint(180, 255)
        # Outer glow
        fd.ellipse(
            (fx - glow_radius, fy - glow_radius,
             fx + glow_radius, fy + glow_radius),
            fill=(255, 220, 80, glow_alpha),
        )
        # Core
        fd.ellipse(
            (fx - core_radius, fy - core_radius,
             fx + core_radius, fy + core_radius),
            fill=(255, 245, 140, core_alpha),
        )
    firefly_layer = firefly_layer.filter(ImageFilter.GaussianBlur(3))
    draw.bitmap((0, 0), firefly_layer, fill=None)

    # ── Additional bright firefly specks (unblurred, distinct points) ────────
    for _ in range(55):
        fx = random.randint(60, 1540)
        fy = random.randint(380, 1350)
        fs = random.randint(2, 4)
        draw.ellipse(
            (fx - fs, fy - fs, fx + fs, fy + fs),
            fill=(255, 248, 170, random.randint(180, 255)),
        )

    # ── Wading bird silhouette ───────────────────────────────────────────────
    bird_x = 250
    bird_y = 1050
    draw.polygon(
        [
            (bird_x, bird_y),
            (bird_x + 35, bird_y - 8),
            (bird_x + 70, bird_y - 12),
            (bird_x + 105, bird_y - 6),
            (bird_x + 130, bird_y + 4),
        ],
        fill=(22, 20, 18, 200),
    )
    # Legs
    draw.line((bird_x + 55, bird_y, bird_x + 50, bird_y + 35), fill=(22, 20, 18, 195), width=2)
    draw.line((bird_x + 100, bird_y + 2, bird_x + 105, bird_y + 35), fill=(22, 20, 18, 195), width=2)

    # ── Tagline ──────────────────────────────────────────────────────────────
    tagline = "BAY OF BENGAL  RISING TIDES  VANISHING ISLANDS"
    tag_font = font("georgia.ttf", 34)
    bb = draw.textbbox((0, 0), tagline, font=tag_font)
    draw.text(
        ((W - (bb[2] - bb[0])) // 2, 310),
        tagline,
        font=tag_font,
        fill=(255, 210, 120, 200),
    )


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Last Tide")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")
    image = Image.new("RGBA", (W, H), (25, 12, 30, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw_mangrove_labyrinth(draw)

    # Research vessel crossing the sunset line
    rv_x, rv_y = 980, 830
    draw.polygon([
        (rv_x - 50, rv_y + 12), (rv_x + 55, rv_y + 12),
        (rv_x + 40, rv_y - 8), (rv_x - 35, rv_y - 8),
    ], fill=(120, 130, 140, 220))
    draw.polygon([
        (rv_x - 30, rv_y - 8), (rv_x - 20, rv_y - 35),
        (rv_x + 30, rv_y - 35), (rv_x + 38, rv_y - 8),
    ], fill=(150, 160, 170, 200))
    # Cabin window
    draw.rectangle([rv_x - 15, rv_y - 30, rv_x + 10, rv_y - 15],
                    fill=(255, 220, 120, 200))
    # Mast/antenna
    draw.line([(rv_x, rv_y - 35), (rv_x, rv_y - 55)], fill=(140, 150, 160), width=2)

    # Tiger swimming through mangroves
    tig_x, tig_y = 420, 940
    # Body
    draw.ellipse([tig_x - 35, tig_y - 12, tig_x + 35, tig_y + 12],
                  fill=(200, 120, 40, 220))
    # Head
    draw.ellipse([tig_x + 30, tig_y - 18, tig_x + 50, tig_y + 8],
                  fill=(210, 130, 45, 220))
    # Ear
    draw.ellipse([tig_x + 38, tig_y - 22, tig_x + 46, tig_y - 16],
                  fill=(180, 100, 30, 220))
    # Eye
    draw.ellipse([tig_x + 40, tig_y - 12, tig_x + 44, tig_y - 8],
                  fill=(30, 25, 20, 220))
    # Snout
    draw.ellipse([tig_x + 46, tig_y - 10, tig_x + 50, tig_y - 4],
                  fill=(220, 160, 60, 220))
    # Stripes
    for sx in range(tig_x - 20, tig_x + 25, 8):
        draw.line([(sx, tig_y - 10), (sx + 3, tig_y + 8)],
                   fill=(140, 70, 20, 150), width=2)
    # Tail
    draw.arc([tig_x - 60, tig_y - 25, tig_x - 30, tig_y + 15],
              200, 340, fill=(200, 120, 40, 200), width=4)
    # Water ripples around tiger
    for r in range(2, 6):
        rad = r * 10
        draw.ellipse([tig_x - rad, tig_y + 10 - rad // 2,
                       tig_x + rad, tig_y + 10 + rad // 2],
                      outline=(200, 155, 70, max(10, 40 - r * 8)), width=1)

    _draw_standard_cover_title_panel(
        image,
        _standard_cover_resolve_title(locals()),
        _standard_cover_resolve_author(locals()),
        model)
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
