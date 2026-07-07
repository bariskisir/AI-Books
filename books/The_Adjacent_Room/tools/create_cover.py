#!/usr/bin/env python3
"""Cover: The Adjacent Room — Resonance Array ring in a dark underground chamber with portal light."""

from __future__ import annotations
import argparse, json, math, random
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

ROOT = Path(__file__).resolve().parents[3]
FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560

random.seed(20260702)


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    for c in [FONT_DIR / name, FONT_DIR / "georgia.ttf", FONT_DIR / "arial.ttf"]:
        if c.exists():
            return ImageFont.truetype(str(c), size)
    return ImageFont.load_default()


def draw_concrete_bg(draw):
    """Dark concrete bunker gradient — grayish-brown, industrial."""
    for y in range(H):
        t = y / H
        r = int(48 + 20 * t)
        g = int(42 + 18 * t)
        b = int(38 + 15 * t)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))


def draw_resonance_ring(draw):
    """The central Array ring — a massive circle of cold metal, partially illuminated."""
    cx, cy = W // 2, 750
    outer_r = 420
    inner_r = 320

    # Outer glow (faint bleed from the ring)
    for glow_r in range(outer_r + 40, outer_r, -5):
        alpha = max(0, 12 - (outer_r + 40 - glow_r) // 4)
        draw.ellipse(
            (cx - glow_r, cy - glow_r, cx + glow_r, cy + glow_r),
            outline=(100, 120, 200, alpha),
            width=2,
        )

    # Main ring body
    draw.ellipse(
        (cx - outer_r, cy - outer_r, cx + outer_r, cy + outer_r),
        outline=(80, 85, 95, 220),
        width=12,
    )

    # Inner ring edge
    draw.ellipse(
        (cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r),
        outline=(120, 130, 150, 180),
        width=6,
    )

    # Magnet segments (small rectangles around the ring)
    for seg in range(24):
        angle = seg * (2 * math.pi / 24)
        seg_x = cx + (outer_r + inner_r) // 2 * math.cos(angle)
        seg_y = cy + (outer_r + inner_r) // 2 * math.sin(angle)
        seg_w, seg_h = 18, 24
        seg_alpha = 100 + random.randint(0, 60)
        draw.rectangle(
            (seg_x - seg_w // 2, seg_y - seg_h // 2, seg_x + seg_w // 2, seg_y + seg_h // 2),
            fill=(60, 70, 90, seg_alpha),
            outline=(100, 120, 160, seg_alpha + 20),
            width=1,
        )

    # Cryocooler vents (small glowing circles at cardinal points)
    for vent_angle in [0, math.pi / 2, math.pi, 3 * math.pi / 2]:
        vx = cx + outer_r * 0.85 * math.cos(vent_angle)
        vy = cy + outer_r * 0.85 * math.sin(vent_angle)
        draw.ellipse(
            (vx - 12, vy - 12, vx + 12, vy + 12),
            fill=(150, 180, 230, random.randint(30, 80)),
        )


def draw_portal_glow(draw, img):
    """Central portal glow — cold blue-white light emanating from the ring center."""
    cx, cy = W // 2, 750
    portal = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(portal)

    # Bright core
    for r in range(200, 0, -10):
        alpha = int(60 * (1 - r / 200))
        core_color = (180, 200, 255, max(0, alpha))
        pd.ellipse(
            (cx - r, cy - r, cx + r, cy + r),
            fill=core_color,
        )

    # Brighter inner zone
    for r in range(100, 0, -10):
        alpha = int(120 * (1 - r / 100))
        pd.ellipse(
            (cx - r, cy - r, cx + r, cy + r),
            fill=(220, 235, 255, max(0, alpha)),
        )

    # Central point
    pd.ellipse(
        (cx - 5, cy - 5, cx + 5, cy + 5),
        fill=(255, 255, 255, 200),
    )

    portal = portal.filter(ImageFilter.GaussianBlur(12))
    return Image.alpha_composite(img, portal)


def draw_light_beams(draw):
    """Beams of light radiating upward from the portal — like a searchlight from the ring."""
    cx, cy = W // 2, 750
    for beam in range(16):
        angle = beam * (2 * math.pi / 16) + random.uniform(-0.1, 0.1)
        beam_length = random.randint(200, 600)
        beam_alpha = random.randint(8, 25)
        bx = cx + beam_length * math.cos(angle)
        by = cy + beam_length * math.sin(angle)
        # Beam from portal center outward
        draw.line(
            (cx, cy, bx, by),
            fill=(180, 200, 255, beam_alpha),
            width=random.randint(3, 8),
        )
        # Secondary thinner beam
        draw.line(
            (cx + random.randint(-20, 20), cy + random.randint(-20, 20),
             bx + random.randint(-10, 10), by + random.randint(-10, 10)),
            fill=(200, 220, 255, beam_alpha // 2),
            width=random.randint(1, 3),
        )


def draw_cable_conduits(draw):
    """Cable conduits and industrial details on the floor — lab infrastructure."""
    # Floor line
    draw.line((0, 1200, W, 1200), fill=(60, 55, 50, 120), width=3)

    # Vertical cable runs from ceiling
    for cx in range(100, W, 200):
        cable_alpha = random.randint(30, 60)
        cable_wiggle = random.randint(-15, 15)
        draw.line(
            (cx, 0, cx + cable_wiggle, 400),
            fill=(50, 50, 55, cable_alpha),
            width=random.randint(2, 5),
        )
        draw.line(
            (cx + cable_wiggle, 400, cx + cable_wiggle // 2, 750),
            fill=(50, 50, 55, cable_alpha),
            width=random.randint(2, 4),
        )

    # Floor conduit box
    draw.rectangle(
        (400, 1180, 500, 1220),
        fill=(45, 42, 38, 150),
        outline=(70, 65, 60, 100),
        width=2,
    )
    draw.rectangle(
        (1100, 1180, 1200, 1220),
        fill=(45, 42, 38, 150),
        outline=(70, 65, 60, 100),
        width=2,
    )


def draw_observation_deck(draw):
    """Glass observation deck in the background — faint geometric lines."""
    # Deck railing (subtle, in background)
    deck_y = 250
    # Horizontal rail
    draw.line((0, deck_y, W, deck_y), fill=(100, 110, 130, 60), width=4)
    draw.line((0, deck_y + 20, W, deck_y + 20), fill=(100, 110, 130, 40), width=2)

    # Vertical supports
    for vx in range(100, W, 150):
        draw.line(
            (vx, deck_y, vx, deck_y + 20),
            fill=(100, 110, 130, 50),
            width=3,
        )

    # Glass panels (subtle blue rectangles)
    for gx in range(50, W - 50, 60):
        draw.rectangle(
            (gx, deck_y - 40, gx + 30, deck_y),
            fill=(120, 150, 200, 15),
            outline=(120, 150, 200, 25),
            width=1,
        )


def draw_ceiling_lights(draw):
    """Overhead industrial lights casting pools downward."""
    for lx in range(200, W, 300):
        # Light fixture
        draw.rectangle(
            (lx - 20, 10, lx + 20, 30),
            fill=(80, 80, 85, 100),
            outline=(50, 50, 55, 80),
            width=1,
        )
        # Light cone
        for step in range(20):
            cone_t = step / 20
            cone_width = int(15 + cone_t * 60)
            cone_alpha = max(0, int(25 * (1 - cone_t)))
            draw.line(
                (lx - cone_width, 30 + cone_t * 300, lx + cone_width, 30 + cone_t * 300),
                fill=(200, 200, 180, cone_alpha),
                width=1,
            )


def draw_monitor_stack(draw):
    """Stack of monitors/consoles in the foreground — lab equipment."""
    # Left console
    draw.rectangle((50, 950, 250, 1200), fill=(30, 28, 25, 180), outline=(50, 48, 45, 100), width=2)
    for mi in range(4):
        mx = 70 + mi * 45
        my = 970 + mi * 15
        draw.rectangle(
            (mx, my, mx + 35, my + 60),
            fill=(20, 30, 50, 200),
            outline=(80, 100, 140, 60),
            width=1,
        )
        # Screen glow
        draw.rectangle(
            (mx + 3, my + 3, mx + 32, my + 57),
            fill=(40, 80, 140, random.randint(30, 80)),
        )
        # Tiny waveforms on screens
        for wv in range(3):
            wv_y = my + 20 + wv * 12
            for wv_x in range(mx + 4, mx + 32, 3):
                wave_h = random.randint(-4, 4)
                draw.point(
                    (wv_x, wv_y + wave_h),
                    fill=(100, 200, 255, random.randint(40, 100)),
                )

    # Right console
    draw.rectangle((1350, 1000, 1550, 1200), fill=(30, 28, 25, 180), outline=(50, 48, 45, 100), width=2)
    for mi in range(3):
        mx = 1370 + mi * 55
        my = 1020
        draw.rectangle(
            (mx, my, mx + 45, my + 80),
            fill=(20, 30, 50, 200),
            outline=(80, 100, 140, 60),
            width=1,
        )
        draw.rectangle(
            (mx + 3, my + 3, mx + 42, my + 77),
            fill=(40, 80, 140, random.randint(30, 80)),
        )


def draw_dimensional_ripples(draw):
    """Subtle distortion ripples emanating from the ring — like heat haze."""
    cx, cy = W // 2, 750
    for r in range(3):
        ripple_r = 300 + r * 100 + random.randint(-10, 10)
        ripple_alpha = max(0, 12 - r * 4)
        draw.ellipse(
            (cx - ripple_r, cy - ripple_r, cx + ripple_r, cy + ripple_r),
            outline=(150, 180, 255, ripple_alpha),
            width=random.randint(2, 4),
        )


def draw_scattered_particles(draw):
    """Tiny floating particles in the beam path — quantum dust."""
    for _ in range(200):
        px = random.randint(100, W - 100)
        py = random.randint(200, 1100)
        pr = random.uniform(0.8, 2.5)
        pa = random.randint(10, 50)
        draw.ellipse(
            (px - pr, py - pr, px + pr, py + pr),
            fill=(200, 220, 255, pa),
        )


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title, author = m["title"], m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Step 1: Dark concrete bunker background
    draw_concrete_bg(draw)

    # Step 2: Ceiling lights
    draw_ceiling_lights(draw)

    # Step 3: Cable conduits
    draw_cable_conduits(draw)

    # Step 4: Observation deck
    draw_observation_deck(draw)

    # Step 5: Resonance Array ring
    draw_resonance_ring(draw)

    # Step 6: Portal glow at center
    img = draw_portal_glow(draw, img)
    draw = ImageDraw.Draw(img, "RGBA")

    # Step 7: Light beams from portal
    draw_light_beams(draw)

    # Step 8: Dimensional ripples
    draw_dimensional_ripples(draw)

    # Step 9: Monitor consoles
    draw_monitor_stack(draw)

    # Step 10: Floating particles
    draw_scattered_particles(draw)

    # Step 11: Standard title panel at bottom
    _draw_standard_cover_title_panel(
        img,
        _standard_cover_resolve_title(locals()),
        _standard_cover_resolve_author(locals()),
        model,
    )

    op.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(op, "PNG", optimize=True)


def main():
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
