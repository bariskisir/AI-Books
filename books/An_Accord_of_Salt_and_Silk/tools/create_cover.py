#!/usr/bin/env python3
"""Cover: An Accord of Salt and Silk — A Persian merchant's daughter and a Han Chinese diplomat must pose as a married couple to smuggle silkworm eggs out of the Tang Empire."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

rng = random.Random()
rng.seed(6102024)

# Silk Road palette — warm terracotta, saffron gold, deep crimson, sand
SKY_TOP = (120, 30, 50)      # deep crimson at zenith
SKY_MID = (200, 90, 50)      # burnt orange
SKY_BOT = (230, 170, 90)     # golden sand at horizon
DUNE_COLORS = [
    (160, 100, 60),   # far — muted terracotta
    (140, 85, 50),    # mid-far
    (120, 70, 42),    # mid
    (95, 55, 35),     # mid-near
    (70, 40, 28),     # near — dark earth
]
GOLD = (220, 180, 80)
CRIMSON = (180, 40, 50)


def _draw_stars(draw: ImageDraw.ImageDraw) -> None:
    """Subtle stars in the upper third of the sky."""
    for _ in range(140):
        sx = rng.randint(0, W)
        sy = rng.randint(0, int(H * 0.32))
        sr = rng.uniform(0.4, 2.2)
        alpha = rng.randint(50, 200)
        brightness = rng.randint(200, 255)
        draw.ellipse(
            (sx - sr, sy - sr, sx + sr, sy + sr),
            fill=(brightness, brightness - 10, brightness - 40, alpha),
        )


def _draw_dune_silhouette(
    draw: ImageDraw.ImageDraw, color: tuple[int, int, int],
    y_base: int, amp: int, freq: float, phase: float, alpha: int,
) -> None:
    """Draw a single dune ridge with smooth sinusoidal curve filled to bottom."""
    points: list[tuple[int, int]] = []
    step = 6
    for x in range(0, W + step, step):
        y = y_base + int(amp * math.sin(freq * x + phase))
        points.append((x, y))
    points.extend([(W, H), (0, H)])
    draw.polygon(points, fill=(*color, alpha))


def _draw_moon(base_img: Image.Image) -> Image.Image:
    """Add a glowing crescent moon."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    mx, my = 1150, 160
    # Full disc
    d.ellipse((mx - 42, my - 42, mx + 42, my + 42), fill=(245, 225, 195, 210))
    # Carve crescent
    d.chord(
        (mx + 8, my - 38, mx + 52, my + 38), 0, 360,
        fill=(0, 0, 0, 0),
    )
    # Outer glow
    d.ellipse(
        (mx - 52, my - 52, mx + 52, my + 52),
        fill=(245, 225, 195, 18),
    )
    layer = layer.filter(ImageFilter.GaussianBlur(4))
    return Image.alpha_composite(base_img, layer)


def _draw_caravan(base_img: Image.Image) -> Image.Image:
    """Tiny camel caravan winding across the mid-distance dunes."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    pts: list[tuple[int, int]] = []
    for x in range(150, 1451, 8):
        t = (x - 150) / 1300
        y = int(H * 0.55) + int(35 * math.sin(x * 0.007 + 0.5)) \
            + int(12 * math.sin(x * 0.019 + 1.2))
        pts.append((x, y))
    # Trail line
    d.line(pts, fill=(55, 32, 18, 130), width=2)
    # Tiny camel silhouettes (hump + body)
    for idx in (4, 9, 14, 18, 22):
        if idx < len(pts):
            cx, cy = pts[idx]
            d.ellipse((cx - 5, cy - 10, cx + 5, cy - 2), fill=(25, 16, 10, 200))
            d.rectangle((cx - 8, cy - 4, cx + 8, cy + 2), fill=(25, 16, 10, 200))
            # Neck / head
            d.ellipse((cx + 2, cy - 16, cx + 6, cy - 10), fill=(25, 16, 10, 200))
    return Image.alpha_composite(base_img, layer)


def _draw_figures(base_img: Image.Image) -> Image.Image:
    """Two silhouetted figures — Roxana (left) and Chen Weizhi (right) — on a dune crest."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # Dune crest they stand on
    crest_y = int(H * 0.49)
    crest_x = W // 2
    # a small prominence where they stand
    peak_dy = int(12 * math.sin(crest_x * 0.005 + 2.1))
    base_y = crest_y + peak_dy

    # Roxana — Persian woman, shorter, robe
    fx1, fy1 = crest_x - 30, base_y
    d.ellipse((fx1 - 7, fy1 - 22, fx1 + 7, fy1 - 10), fill=(14, 9, 7, 230))
    d.rectangle((fx1 - 5, fy1 - 10, fx1 + 5, fy1 + 8), fill=(14, 9, 7, 230))
    d.polygon([
        (fx1 - 11, fy1 + 8), (fx1 + 11, fy1 + 8),
        (fx1 + 7, fy1 + 22), (fx1 - 7, fy1 + 22),
    ], fill=(14, 9, 7, 210))
    # Headscarf hint
    d.arc((fx1 - 10, fy1 - 26, fx1 + 10, fy1 - 8), 190, 350,
          fill=(14, 9, 7, 130), width=2)

    # Chen Weizhi — Han Chinese diplomat, taller, scholar robe
    fx2, fy2 = crest_x + 32, base_y - 4
    d.ellipse((fx2 - 7, fy2 - 24, fx2 + 7, fy2 - 12), fill=(14, 9, 7, 230))
    d.rectangle((fx2 - 5, fy2 - 12, fx2 + 5, fy2 + 6), fill=(14, 9, 7, 230))
    d.polygon([
        (fx2 - 9, fy2 + 6), (fx2 + 9, fy2 + 6),
        (fx2 + 6, fy2 + 22), (fx2 - 6, fy2 + 22),
    ], fill=(14, 9, 7, 210))
    # Hat/scholar cap
    d.rectangle((fx2 - 9, fy2 - 28, fx2 + 9, fy2 - 24), fill=(14, 9, 7, 200))
    d.rectangle((fx2 - 12, fy2 - 30, fx2 + 12, fy2 - 28), fill=(14, 9, 7, 190))

    # Connection — a thin golden thread between their hands
    space_y = fy1 - 10
    d.line(
        (fx1 + 10, space_y, fx2 - 10, space_y),
        fill=(200, 160, 70, 50), width=2,
    )

    return Image.alpha_composite(base_img, layer)


def _draw_silk_threads(base_img: Image.Image) -> Image.Image:
    """Flowing silk ribbons weaving across the upper sky — the silk accord."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # Elegant long sweeping arcs (silk ribbons)
    ribbon_specs = [
        # (cx, cy, rx, ry, start_deg, end_deg, color, alpha, width)
        (400, 500, 350, 200, 200, 350, GOLD, 55, 3),
        (400, 500, 350, 200, 210, 340, CRIMSON, 30, 2),
        (900, 300, 400, 250, 20, 160, GOLD, 45, 3),
        (900, 300, 400, 250, 30, 150, CRIMSON, 25, 2),
        (200, 700, 500, 300, 100, 280, GOLD, 35, 2),
        (200, 700, 500, 300, 110, 270, (200, 150, 100), 25, 2),
        (1300, 400, 300, 180, 150, 330, GOLD, 40, 2),
        (700, 800, 450, 200, 180, 360, CRIMSON, 30, 2),
    ]
    for (cx, cy, rx, ry, sa, ea, col, al, w) in ribbon_specs:
        d.arc(
            (cx - rx, cy - ry, cx + rx, cy + ry),
            sa, ea, fill=(*col, al), width=w,
        )

    # Thin golden threads criss-crossing (fate lines)
    for _ in range(14):
        x = rng.randint(50, W - 50)
        y = rng.randint(80, int(H * 0.4))
        pts: list[tuple[int, int]] = []
        for step in range(rng.randint(10, 22)):
            x += rng.randint(-25, 25)
            y += rng.randint(18, 40)
            pts.append((x, y))
        if len(pts) > 1:
            for i in range(len(pts) - 1):
                d.line(
                    (pts[i], pts[i + 1]),
                    fill=(*rng.choice([GOLD, CRIMSON, (200, 160, 100)]),
                          rng.randint(25, 70)),
                    width=rng.randint(1, 2),
                )

    layer = layer.filter(ImageFilter.GaussianBlur(2))
    return Image.alpha_composite(base_img, layer)


def _draw_cocoon_border(base_img: Image.Image) -> Image.Image:
    """Subtle silk cocoon / silkworm-egg border near the bottom."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    by = H - 220
    # Thread that weaves through the eggs
    for bx in range(60, W - 60, 3):
        by2 = by + int(4 * math.sin(bx * 0.04))
        d.point((bx, by2), fill=(200, 180, 150, 20))

    # Cocoon shapes
    for bx in range(80, W - 80, 45 + rng.randint(-10, 10)):
        br = rng.randint(5, 9)
        alpha = rng.randint(25, 60)
        d.ellipse(
            (bx - br, by - br // 2, bx + br, by + br // 2),
            fill=(210, 195, 165, alpha),
        )
        # Inner highlight
        if rng.random() < 0.4:
            d.ellipse(
                (bx - br // 2, by - br // 4, bx + br // 2, by + br // 4),
                fill=(230, 215, 190, alpha - 10),
            )
    return Image.alpha_composite(base_img, layer)


def _make_gradient_background() -> Image.Image:
    """Three-zone gradient: deep crimson sky -> burnt orange -> warm sand."""
    img = Image.new("RGBA", (W, H), (20, 10, 15, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(H):
        t = y / H
        if t < 0.38:
            lt = t / 0.38
            r = int(SKY_TOP[0] + (SKY_MID[0] - SKY_TOP[0]) * lt)
            g = int(SKY_TOP[1] + (SKY_MID[1] - SKY_TOP[1]) * lt)
            b = int(SKY_TOP[2] + (SKY_MID[2] - SKY_TOP[2]) * lt)
        elif t < 0.52:
            lt = (t - 0.38) / 0.14
            r = int(SKY_MID[0] + (SKY_BOT[0] - SKY_MID[0]) * lt)
            g = int(SKY_MID[1] + (SKY_BOT[1] - SKY_MID[1]) * lt)
            b = int(SKY_MID[2] + (SKY_BOT[2] - SKY_MID[2]) * lt)
        else:
            gt = min(1, (t - 0.52) / 0.48)
            r = int(SKY_BOT[0] - gt * 45)
            g = int(SKY_BOT[1] - gt * 55)
            b = int(SKY_BOT[2] - gt * 35)
        draw.line((0, y, W, y), fill=(r, g, b, 255))
    return img


def _draw_vignette(draw: ImageDraw.ImageDraw) -> None:
    """Darken edges for focus."""
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(45 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 55))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 55))


def make_cover(mp: Path, op: Path) -> None:
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    # 1. Gradient background
    img = _make_gradient_background()
    draw = ImageDraw.Draw(img, "RGBA")

    # 2. Stars
    _draw_stars(draw)

    # 3. Crescent moon
    img = _draw_moon(img)

    # 4. Dune silhouettes — five layers of sinusoidal ridges
    dune_specs = [
        (DUNE_COLORS[0], int(H * 0.50), 55, 0.0028, 0.0, 220),
        (DUNE_COLORS[1], int(H * 0.53), 75, 0.0033, 1.8, 210),
        (DUNE_COLORS[2], int(H * 0.58), 95, 0.0022, 3.2, 240),
        (DUNE_COLORS[3], int(H * 0.64), 115, 0.0038, 0.9, 235),
        (DUNE_COLORS[4], int(H * 0.74), 130, 0.0020, 4.5, 250),
    ]
    for color, yb, amp, freq, phase, alpha in dune_specs:
        _draw_dune_silhouette(draw, color, yb, amp, freq, phase, alpha)

    # 5. Caravan trail
    img = _draw_caravan(img)
    draw = ImageDraw.Draw(img, "RGBA")

    # 6. Two figures
    img = _draw_figures(img)
    draw = ImageDraw.Draw(img, "RGBA")

    # 7. Silk ribbons
    img = _draw_silk_threads(img)
    draw = ImageDraw.Draw(img, "RGBA")

    # 8. Cocoon border
    img = _draw_cocoon_border(img)
    draw = ImageDraw.Draw(img, "RGBA")

    # 9. Vignette
    _draw_vignette(draw)

    # 10. Title panel
    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, title, author, model)
    img.convert("RGB").save(op, "PNG", optimize=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    make_cover(
        ROOT / a.metadata if not a.metadata.is_absolute() else a.metadata,
        ROOT / a.out if not a.out.is_absolute() else a.out,
    )


if __name__ == "__main__":
    main()
