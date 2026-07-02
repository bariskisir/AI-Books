#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Paleolithic Contract.

Deep cave interior with stalactites, amber torchlight, ancient hand stencils
on limestone walls — warm ochres, charcoal black, deep green, flickering amber.
Human figures in silhouette near the cave mouth.
"""

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
    _standard_cover_resolve_title,
    _standard_cover_resolve_author,
    _draw_standard_cover_title_panel,
)


W = 1600
H = 2560


def _lerp(c1: tuple[int, ...], c2: tuple[int, ...], t: float) -> tuple[int, ...]:
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def _draw_gradient(draw: ImageDraw, y1: int, y2: int, c1: tuple, c2: tuple) -> None:
    for y in range(y1, min(y2, H)):
        t = (y - y1) / max(y2 - y1, 1)
        draw.line((0, y, W, y), fill=_lerp(c1, c2, t) + (255,), width=1)


def _draw_stalactites(draw: ImageDraw, rng) -> None:
    """Draw hanging stalactites from the cave ceiling."""
    stalactite_positions = []
    for i in range(40):
        x = rng.randint(20, W - 20)
        length = rng.randint(40, 250)
        width_base = rng.randint(12, 35)
        lean = rng.randint(-15, 15)
        stalactite_positions.append((x, length, width_base, lean))

    # Sort so wider ones are drawn first (farther back)
    stalactite_positions.sort(key=lambda s: -s[2])

    for x, length, w, lean in stalactite_positions:
        # Stalactite shape: wide at top, tapering to a point
        color_r = rng.randint(110, 170)
        color_g = rng.randint(95, 140)
        color_b = rng.randint(70, 100)

        # Main body
        points = [
            (x - w // 2, 0),
            (x + w // 2 + lean, 0),
            (x + lean + w // 8, length),
            (x + lean, length + 10),
        ]
        draw.polygon(points, fill=(color_r, color_g, color_b, 230))

        # Highlight edge (catch side light from torch)
        highlight_points = [
            (x - w // 4, 0),
            (x - w // 4 + 8, length - 20),
            (x + lean, length),
            (x + lean + 2, length + 8),
        ]
        draw.polygon(
            highlight_points,
            fill=(min(color_r + 40, 200), min(color_g + 30, 170), min(color_b + 20, 130), 60),
        )

        # Drip tip
        drip_len = rng.randint(8, 18)
        draw.line(
            (x + lean + 2, length, x + lean + 2, length + drip_len),
            fill=(160, 150, 130, 160),
            width=max(1, w // 6),
        )


def _draw_stalagmites(draw: ImageDraw, rng, floor_y: int) -> None:
    """Draw stalagmites rising from the cave floor."""
    for i in range(30):
        x = rng.randint(30, W - 30)
        height = rng.randint(15, 120)
        w = rng.randint(8, 30)

        r = rng.randint(100, 160)
        g = rng.randint(85, 130)
        b = rng.randint(65, 90)

        points = [
            (x - w // 2, floor_y),
            (x + w // 2, floor_y),
            (x + w // 4, floor_y - height),
            (x, floor_y - height - int(height * 0.3)),
        ]
        draw.polygon(points, fill=(r, g, b, 230))


def _draw_cave_walls(draw: ImageDraw, rng) -> None:
    """Draw rough cave wall shapes on left and right sides, retreating toward a mouth in the upper center."""
    left_wall_x = []
    # Left wall: irregular edge
    for y in range(0, 1000):
        noise = 40 * math.sin(y * 0.005) + 30 * math.sin(y * 0.013) + 20 * math.sin(y * 0.027)
        x = int(50 + noise + 30 * (1 - y / 1000))
        left_wall_x.append((x, y))

    # Right wall
    right_wall_x = []
    for y in range(0, 1000):
        noise = 40 * math.sin(y * 0.005 + 1.5) + 30 * math.sin(y * 0.013 + 2.1) + 20 * math.sin(y * 0.027 + 0.8)
        x = int(W - 50 - noise - 30 * (1 - y / 1000))
        right_wall_x.append((x, y))

    # Draw left wall fill
    left_poly = left_wall_x + [(0, 1000), (0, 0)]
    draw.polygon(left_poly, fill=(35, 28, 22, 255))

    # Draw right wall fill
    right_poly = right_wall_x + [(W, 1000), (W, 0)]
    draw.polygon(right_poly, fill=(30, 24, 19, 255))

    # Wall texture overlay — darker cracks
    for y in range(0, 1000, 4):
        lx = left_wall_x[min(y, len(left_wall_x) - 1)][0] if y < len(left_wall_x) else 50
        rx = right_wall_x[min(y, len(right_wall_x) - 1)][0] if y < len(right_wall_x) else W - 50

        # Crevice marks on walls
        if rng.random() < 0.1:
            side = rng.choice(["left", "right"])
            if side == "left":
                cx = lx + rng.randint(0, 30)
                cv = rng.randint(15, 25)
                draw.line((cx, y, cx + rng.randint(-5, 15), y + rng.randint(2, 12)), fill=(cv, cv, cv, 180), width=1)
            else:
                cx = rx - rng.randint(0, 30)
                cv = rng.randint(15, 25)
                draw.line((cx, y, cx + rng.randint(-15, 5), y + rng.randint(2, 12)), fill=(cv, cv, cv, 180), width=1)


def _draw_cave_floor(draw: ImageDraw, rng, floor_y: int) -> None:
    """Draw the cave floor with rock texture and debris."""
    # Base floor
    for y in range(floor_y, H):
        t = (y - floor_y) / (H - floor_y)
        r = int(40 + 20 * (1 - t))
        g = int(35 + 15 * (1 - t))
        b = int(28 + 10 * (1 - t))
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # Broken rock debris
    for _ in range(60):
        x = rng.randint(0, W)
        y = rng.randint(floor_y, H - 200)
        size = rng.randint(3, 20)
        shade = rng.randint(30, 65)
        draw.polygon(
            [
                (x, y),
                (x + size, y - size // 2),
                (x + size * 2, y),
                (x + size * 2, y + size // 2),
                (x + size, y + size),
            ],
            fill=(shade + 10, shade + 5, shade, 200),
        )


def _draw_hand_stencils(draw: ImageDraw, rng) -> None:
    """Draw ancient hand stencils on the cave walls — ochre spray patterns.

    Placed on upper wall areas where the cave interior is visible.
    """
    hand_groups = [
        # Group 1: left wall, upper
        [(190, 280, 0.8, 12), (170, 340, 0.7, 8), (210, 400, 0.9, 15)],
        # Group 2: left wall, mid
        [(220, 520, 1.0, 18), (240, 580, 0.85, 14), (200, 640, 0.75, 10), (210, 460, 0.6, 8)],
        # Group 3: right wall, upper
        [(1370, 310, 0.9, 14), (1400, 380, 0.8, 11), (1350, 440, 0.7, 9)],
        # Group 4: right wall, mid
        [(1420, 560, 1.1, 20), (1390, 620, 0.95, 16), (1430, 690, 0.8, 12), (1450, 510, 0.7, 10)],
    ]

    for group in hand_groups:
        for cx, cy, scale, alpha in group:
            ochre_r = rng.randint(140, 190)
            ochre_g = rng.randint(80, 120)
            ochre_b = rng.randint(40, 65)

            # Hand palm (oval)
            pw = int(40 * scale)
            ph = int(55 * scale)
            draw.ellipse(
                (cx - pw // 2, cy - ph // 2, cx + pw // 2, cy + ph // 2),
                fill=(ochre_r, ochre_g, ochre_b, alpha),
            )

            # Fingers
            finger_angles = [-0.4, -0.2, 0.0, 0.2, 0.4]
            for i, angle in enumerate(finger_angles):
                fx = cx + int(45 * scale * math.sin(angle))
                fy = cy - int(45 * scale * math.cos(angle))
                fl = int(30 * scale + rng.randint(-5, 5))
                fw = int(8 * scale)
                draw.ellipse(
                    (fx - fw, fy - fl, fx + fw, fy + 5),
                    fill=(ochre_r, ochre_g, ochre_b, max(5, alpha - 3)),
                )

            # Thumb
            tx = cx - int(30 * scale)
            ty = cy + int(10 * scale)
            draw.ellipse(
                (tx - int(10 * scale), ty - int(25 * scale), tx + int(10 * scale), ty + int(5 * scale)),
                fill=(ochre_r, ochre_g, ochre_b, max(5, alpha - 5)),
            )

            # Spray halo effect
            spray_alpha = max(3, alpha // 4)
            for _ in range(15):
                sx = cx + rng.randint(-int(50 * scale), int(50 * scale))
                sy = cy + rng.randint(-int(60 * scale), int(60 * scale))
                sr = rng.randint(1, 4)
                draw.ellipse(
                    (sx - sr, sy - sr, sx + sr, sy + sr),
                    fill=(ochre_r, ochre_g, ochre_b, spray_alpha),
                )


def _draw_torchlight(draw: ImageDraw, rng) -> Image.Image:
    """Draw torch/firelight glow as layered radial gradients on a separate layer.

    Returns an RGBA image with the glow to be composited.
    """
    glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow_layer)

    # Main torchlight sources in the lower half — warm amber glow
    sources = [
        (W // 2 - 180, 1100, 550, (240, 180, 80)),   # left torch
        (W // 2 + 200, 1150, 500, (230, 170, 70)),     # right torch
        (W // 2 - 40, 1250, 400, (200, 150, 60)),      # central ground fire
        (W // 2 + 60, 800, 350, (210, 160, 65)),       # upper torch on wall
    ]

    for sx, sy, radius, (cr, cg, cb) in sources:
        for i in range(radius, 0, -8):
            t = i / radius
            alpha = int(35 * (1 - t * t))
            if alpha < 1:
                continue
            r = int(cr * (1 - t * 0.4))
            g = int(cg * (1 - t * 0.4))
            b = int(cb * (1 - t * 0.5))
            gdraw.ellipse(
                (sx - i, sy - i, sx + i, sy + i),
                fill=(r, g, b, alpha),
            )

    # Blur to create soft light
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=40))
    return glow_layer


def _draw_torch_flames(draw: ImageDraw, rng) -> None:
    """Draw actual torch flames at specific positions."""
    flame_positions = [
        (W // 2 - 180, 1090, 0.9),
        (W // 2 + 200, 1140, 1.0),
        (W // 2 + 60, 790, 0.8),
    ]

    for fx, fy, scale in flame_positions:
        # Flame body
        flame_h = int(90 * scale)
        flame_w = int(30 * scale)
        colors = [
            (220, 180, 60, 200),   # outer yellow
            (240, 150, 40, 220),   # mid orange
            (250, 100, 30, 240),   # inner orange
            (200, 60, 20, 180),    # core
        ]

        for i, (cr, cg, cb, ca) in enumerate(colors):
            shrink = i * 8
            points = [
                (fx - flame_w + shrink, fy),
                (fx - flame_w // 2 + shrink, fy - flame_h + shrink * 2),
                (fx, fy - flame_h - int(20 * scale) + shrink * 3),
                (fx + flame_w // 2 - shrink, fy - flame_h + shrink * 2),
                (fx + flame_w - shrink, fy),
            ]
            draw.polygon(points, fill=(cr, cg, cb, ca))

        # Small flame flicker
        flicker_h = int(40 * scale)
        draw.polygon(
            [
                (fx - 8, fy - 10),
                (fx, fy - flicker_h - int(20 * rng.random() * scale)),
                (fx + 8, fy - 10),
            ],
            fill=(255, 200, 80, 150),
        )

        # Torch wood / handle
        draw.rectangle(
            (fx - 4, fy, fx + 4, fy + int(60 * scale)),
            fill=(45, 30, 15, 230),
        )


def _draw_human_silhouettes(draw: ImageDraw, rng, floor_y: int) -> None:
    """Draw human figures in silhouette near the cave mouth area (upper half of the image)."""
    # Figures standing near the cave mouth looking into the cave — upper portion
    figure_data = [
        # (x_base, y_base, scale, facing_left)
        (320, 980, 1.0, False),
        (380, 990, 0.85, False),
        (270, 1000, 0.7, True),
        (450, 1005, 0.6, False),
    ]

    for fx, fy, scale, facing_left in figure_data:
        sign = -1 if facing_left else 1

        # Head
        head_r = int(16 * scale)
        draw.ellipse(
            (fx - head_r, fy - head_r * 4, fx + head_r, fy - head_r * 2),
            fill=(10, 8, 8, 240),
        )

        # Body / torso
        body_w = int(22 * scale)
        body_h = int(55 * scale)
        draw.polygon(
            [
                (fx - body_w, fy - head_r * 2),
                (fx + body_w, fy - head_r * 2),
                (fx + body_w + int(5 * scale), fy - head_r * 2 + body_h),
                (fx - body_w + int(5 * scale), fy - head_r * 2 + body_h),
            ],
            fill=(10, 8, 8, 240),
        )

        # Arm reaching forward (pointing into cave)
        arm_len = int(35 * scale)
        draw.line(
            (
                fx + sign * body_w,
                fy - head_r + int(10 * scale),
                fx + sign * (body_w + arm_len),
                fy - head_r - int(10 * scale),
            ),
            fill=(10, 8, 8, 240),
            width=max(2, int(6 * scale)),
        )

        # Other arm (by side or holding torch)
        draw.line(
            (
                fx - sign * body_w,
                fy - int(5 * scale),
                fx - sign * (body_w + int(20 * scale)),
                fy + int(20 * scale),
            ),
            fill=(10, 8, 8, 240),
            width=max(2, int(6 * scale)),
        )

        # Legs
        for side in [-1, 1]:
            draw.line(
                (
                    fx + side * int(8 * scale),
                    fy - head_r * 2 + body_h,
                    fx + side * int(15 * scale),
                    fy - head_r * 2 + body_h + int(35 * scale),
                ),
                fill=(10, 8, 8, 240),
                width=max(2, int(7 * scale)),
            )


def _draw_cave_mouth_opening(draw: ImageDraw, rng) -> None:
    """Draw the cave mouth at the top of the image — a bright opening showing exterior light."""
    # Cave mouth: bright area at the top center
    mouth_cx = W // 2 + 30
    mouth_cy = 0
    mouth_rx = 320
    mouth_ry = 280

    # Exterior light gradient (outside world visible through cave mouth)
    sky_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(sky_layer)

    # Pale sky through opening
    sdraw.ellipse(
        (mouth_cx - mouth_rx, mouth_cy - mouth_ry, mouth_cx + mouth_rx, mouth_cy + mouth_ry),
        fill=(180, 200, 160, 255),
    )
    # Brighter center
    sdraw.ellipse(
        (mouth_cx - mouth_rx // 2, mouth_cy - 30, mouth_cx + mouth_rx // 2, mouth_cy + 60),
        fill=(210, 230, 200, 200),
    )
    sky_layer = sky_layer.filter(ImageFilter.GaussianBlur(30))

    # Composite
    return sky_layer, mouth_cx, mouth_cy, mouth_rx, mouth_ry


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
    title = metadata.get("title", "")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    import random
    seed = hash("The Paleolithic Contract cave cover v1")
    rng = random.Random(seed)

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # 1. Background gradient — deep cave darkness transitioning to warmer lower cave
    _draw_gradient(draw, 0, 600, (18, 16, 18), (30, 25, 22))
    _draw_gradient(draw, 600, 1200, (30, 25, 22), (55, 40, 32))
    _draw_gradient(draw, 1200, H, (55, 40, 32), (40, 32, 28))

    # 2. Cave mouth opening — exterior light
    sky_layer, mx, my, mrx, mry = _draw_cave_mouth_opening(draw, rng)
    img = Image.alpha_composite(img, sky_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # 3. Cave walls (drawn over sky to frame the opening)
    _draw_cave_walls(draw, rng)

    # 4. Stalactites from ceiling
    _draw_stalactites(draw, rng)

    # 5. Cave floor
    floor_y = 1300
    _draw_cave_floor(draw, rng, floor_y)

    # 6. Stalagmites on floor
    _draw_stalagmites(draw, rng, floor_y)

    # 7. Ancient hand stencils on walls
    _draw_hand_stencils(draw, rng)

    # 8. Human silhouettes near cave mouth
    _draw_human_silhouettes(draw, rng, floor_y)

    # 9. Torchlight glow layer (composite)
    glow = _draw_torchlight(draw, rng)
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # 10. Torch flames (drawn after glow so they're sharp)
    _draw_torch_flames(draw, rng)

    # 11. Subtle dust motes / cave particles in torchlight
    for _ in range(120):
        x = rng.randint(100, W - 100)
        y = rng.randint(700, 1400)
        pr = rng.randint(1, 3)
        pa = rng.randint(30, 90)
        draw.ellipse((x - pr, y - pr, x + pr, y + pr), fill=(200, 180, 120, pa))

    # 12. Title panel
    _draw_standard_cover_title_panel(
        img,
        _standard_cover_resolve_title(locals()),
        _standard_cover_resolve_author(locals()),
        model,
    )

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(output_path, "PNG", optimize=True)
    print(f"Cover saved to {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    mp = args.metadata if args.metadata.is_absolute() else Path(__file__).resolve().parents[3] / args.metadata
    op = args.out if args.out.is_absolute() else Path(__file__).resolve().parents[3] / args.out

    make_cover(mp, op)


if __name__ == "__main__":
    main()
