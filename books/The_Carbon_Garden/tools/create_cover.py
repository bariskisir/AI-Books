#!/usr/bin/env python3
"""Cover: The Carbon Garden — terraced Portuguese hillside with glowing glass bioreactors."""

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

# Seed for reproducible artwork
random.seed(42)


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    for c in [FONT_DIR / name, FONT_DIR / "georgia.ttf", FONT_DIR / "arial.ttf"]:
        if c.exists():
            return ImageFont.truetype(str(c), size)
    return ImageFont.load_default()


def wrap(draw, text, fnt, mw):
    words, lines, cur = text.split(), [], []
    for w in words:
        p = " ".join([*cur, w])
        if draw.textbbox((0, 0), p, font=fnt)[2] <= mw:
            cur.append(w)
        else:
            lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def centered(draw, y, lines, fnt, fill, gap):
    for line in lines:
        bb = draw.textbbox((0, 0), line, font=fnt)
        draw.text(((W - (bb[2] - bb[0])) // 2, y), line, font=fnt, fill=fill)
        y += bb[3] - bb[1] + gap
    return y


def _draw_hillside(draw):
    """Draw terraced hillside with golden-brown earth tones."""
    # Distant hills
    for y in range(0, 600):
        t = y / 600
        r = int(80 + 20 * t)
        g = int(110 + 30 * t)
        b = int(60 + 15 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # Mid-ground hills with warmer greens
    for y in range(600, 1100):
        t = (y - 600) / 500
        r = int(100 - 10 * t)
        g = int(140 + 20 * t)
        b = int(75 - 15 * t)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Terraced slopes
    terrace_levels = [
        (1100, 1270, 100, 140, 70),   # warm med green
        (1270, 1430, 120, 150, 65),   # olive
        (1430, 1580, 140, 110, 55),   # terracotta-earth
        (1580, 1720, 145, 100, 50),   # more terracotta
    ]
    for y_start, y_end, r_base, g_base, b_base in terrace_levels:
        for y in range(y_start, y_end):
            t = (y - y_start) / (y_end - y_start)
            r = int(r_base + 20 * t)
            g = int(g_base - 15 * t)
            b = int(b_base - 5 * t)
            draw.line((0, y, W, y), fill=(max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), 255))

    # Terrace edge lines (retaining walls)
    for ty in [1100, 1270, 1430, 1580]:
        draw.line((0, ty, W, ty), fill=(80, 65, 45, 180), width=2)
        # Stone texture on walls
        for sx in range(0, W, 40):
            sv = 5 + random.randint(-3, 3)
            draw.rectangle((sx, ty - sv, sx + 30, ty), fill=(90, 75, 55, 100))


def _draw_sky(draw):
    """Clear sky with warm gold light near the horizon."""
    for y in range(0, 1100):
        t = y / 1100
        # Top: sky blue, Bottom: warm gold near horizon
        if t < 0.6:
            sub_t = t / 0.6
            r = int(80 + 60 * sub_t)
            g = int(130 + 50 * sub_t)
            b = int(190 - 20 * sub_t)
        else:
            sub_t = (t - 0.6) / 0.4
            r = int(140 + 80 * sub_t)
            g = int(180 + 50 * sub_t)
            b = int(170 - 100 * sub_t)
        draw.line((0, y, W, y), fill=(min(255, r), min(255, g), max(0, b), 255))
        # Horizon glow
    # Sun glow near horizon
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((W // 2 - 400, 700, W // 2 + 400, 1100), fill=(255, 200, 100, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(80))
    ImageDraw.Draw(glow)
    return glow


def _draw_sun(draw):
    """Golden sun low on the horizon."""
    sx, sy = W // 2, 920
    # Outer glow layers
    for radius, alpha in [(180, 30), (120, 50), (80, 80), (50, 120)]:
        draw.ellipse(
            (sx - radius, sy - radius, sx + radius, sy + radius),
            fill=(255, 200, 80, alpha),
        )
    # Core
    draw.ellipse((sx - 25, sy - 25, sx + 25, sy + 25), fill=(255, 220, 130, 200))


def _draw_village_rooftops(draw):
    """Layered terracotta rooftops on the middle terraces."""
    roof_clusters = [
        # (start_x, end_x, base_y, roof_count)
        (100, 450, 1160, 5),
        (500, 720, 1130, 4),
        (900, 1300, 1140, 7),
        (1100, 1500, 1170, 6),
    ]
    for start_x, end_x, base_y, count in roof_clusters:
        for _ in range(count):
            rx = start_x + random.randint(0, end_x - start_x - 60)
            rw = 40 + random.randint(10, 30)
            rh = 20 + random.randint(5, 15)
            ro = 5 + random.randint(-3, 5)

            # Roof triangle
            terracotta_shade = random.choice([
                (160, 75, 45), (175, 85, 50), (145, 65, 40),
                (185, 95, 55), (150, 80, 48),
            ])
            draw.polygon(
                [(rx, base_y + ro), (rx + rw // 2, base_y - rh + ro), (rx + rw, base_y + ro)],
                fill=terracotta_shade + (220,),
            )
            # House body below roof
            draw.rectangle(
                (rx, base_y + ro, rx + rw, base_y + ro + 25),
                fill=(200, 180, 150, 200),
            )
            # Window glow
            for _ in range(1, 3):
                wx = rx + 8 + random.randint(0, rw - 20)
                wy = base_y + ro + 6
                draw.rectangle((wx, wy, wx + 8, wy + 8), fill=(255, 230, 150, random.randint(80, 180)))


def _draw_mycelium_archways(draw):
    """White mycelium archways spanning across the terraces."""
    arch_positions = [
        (W // 2 - 200, 1150, 180),
        (W // 2 + 150, 1310, 140),
        (W // 2 - 300, 1450, 160),
        (W // 2 + 100, 1560, 130),
    ]
    for ax, ay, span in arch_positions:
        # Arch path
        segments = 30
        for i in range(segments):
            t = i / segments
            angle = math.pi * t
            px = ax + span * t
            py = ay - 80 * math.sin(angle)
            # Mycelium strands: thin white/grey lines
            strand_width = 2 + random.randint(1, 4)
            alpha = random.randint(80, 160)
            draw.ellipse(
                (px - strand_width, py - strand_width, px + strand_width, py + strand_width),
                fill=(220, 225, 230, alpha),
            )
        # Dense mycelium nodes at bases
        for side in [0, 1]:
            nx = ax + span * side
            ny = ay
            for _ in range(8):
                ox = random.randint(-10, 10)
                oy = random.randint(-8, 8)
                rn = random.randint(3, 8)
                draw.ellipse(
                    (nx + ox - rn, ny + oy - rn, nx + ox + rn, ny + oy + rn),
                    fill=(230, 235, 240, random.randint(60, 150)),
                )


def _draw_bioreactors(draw):
    """Glowing glass bioreactors in emerald and cyan spaced across terraces."""
    reactor_data = [
        # (terrace_y, count)
        (1200, 6),
        (1370, 8),
        (1510, 10),
        (1660, 12),
    ]
    for terrace_y, count in reactor_data:
        spacing = W // (count + 1)
        for i in range(count):
            cx = spacing * (i + 1) + random.randint(-20, 20)
            cy = terrace_y + random.randint(-15, 15)

            # Reactor body (rounded cylinder)
            rw, rh = 22 + random.randint(3, 10), 55 + random.randint(5, 20)

            # Glass body (translucent)
            color_choice = random.random()
            if color_choice < 0.5:
                # Emerald green
                r1, g1, b1 = 30, 180, 90
                r2, g2, b2 = 20, 220, 120
            elif color_choice < 0.85:
                # Cyan
                r1, g1, b1 = 20, 200, 200
                r2, g2, b2 = 10, 240, 240
            else:
                # Amber/gold
                r1, g1, b1 = 220, 180, 40
                r2, g2, b2 = 255, 210, 80

            glow_alpha = random.randint(60, 140)
            glass_alpha = random.randint(80, 160)
            core_alpha = random.randint(40, 100)

            # Outer glow
            draw.ellipse(
                (cx - rw - 8, cy - 8, cx + rw + 8, cy + rh + 8),
                fill=(r1, g1, b1, glow_alpha),
            )

            # Glass vessel
            draw.rounded_rectangle(
                (cx - rw, cy, cx + rw, cy + rh),
                radius=8,
                fill=(r1, g1, b1, glass_alpha),
                outline=(255, 255, 255, 60),
                width=1,
            )

            # Internal glow core
            draw.ellipse(
                (cx - rw // 2, cy + rh // 3, cx + rw // 2, cy + rh * 2 // 3),
                fill=(r2, g2, b2, core_alpha),
            )

            # Liquid level line
            level_y = cy + rh - random.randint(12, 20)
            draw.line(
                (cx - rw + 3, level_y, cx + rw - 3, level_y),
                fill=(r2, g2, b2, min(200, core_alpha + 40)),
                width=2,
            )

            # Connection tubes between reactors
            if i < count - 1 and random.random() < 0.4:
                nx = spacing * (i + 2) + random.randint(-20, 20)
                ncy = terrace_y + random.randint(-15, 15)
                draw.line(
                    (cx + rw, cy + rh // 2, nx - rw, ncy + rh // 2),
                    fill=(180, 200, 220, random.randint(30, 70)),
                    width=2,
                )


def _draw_solar_panels(draw):
    """Solar panels catching gold light on the terraces."""
    panel_groups = [
        (200, 1280, 3),
        (750, 1440, 4),
        (1050, 1290, 3),
        (300, 1600, 5),
        (1300, 1600, 4),
    ]
    for px, py, count in panel_groups:
        for i in range(count):
            px_off = px + i * 60 + random.randint(-5, 5)
            py_off = py + random.randint(-8, 8)
            pw, ph = 50, 22

            # Panel body: dark blue-black with gold reflection
            panel_angle = -0.15
            cos_a = math.cos(panel_angle)
            sin_a = math.sin(panel_angle)

            # Rectangle corners
            corners = [
                (px_off, py_off),
                (px_off + pw, py_off),
                (px_off + pw, py_off + ph),
                (px_off, py_off + ph),
            ]

            # Dark panel base
            draw.polygon(
                corners,
                fill=(30, 35, 55, 230),
            )

            # Gold reflection strip
            reflect_y = py_off + random.randint(3, ph - 6)
            draw.line(
                (px_off + 5, reflect_y, px_off + pw - 5, reflect_y),
                fill=(255, 200, 80, random.randint(60, 140)),
                width=3,
            )

            # Grid lines
            for gi in range(1, 4):
                gx = px_off + gi * (pw // 4)
                draw.line(
                    (gx, py_off + 2, gx, py_off + ph - 2),
                    fill=(60, 65, 85, 100),
                    width=1,
                )


def _draw_cork_oak_trees(draw):
    """Cork oak trees with textured bark and soft green canopy."""
    tree_positions = [
        (120, 1080, 60),
        (1550, 1060, 55),
        (80, 1300, 45),
        (1520, 1280, 50),
    ]
    for tx, ty, size in tree_positions:
        # Trunk
        for trunk_y in range(ty, ty + size + 20):
            trunk_width = max(3, 8 - (trunk_y - ty) // 15)
            draw.line(
                (tx - trunk_width, trunk_y, tx + trunk_width, trunk_y),
                fill=(70, 55, 35, 200),
                width=1,
            )
        # Canopy clusters
        canopy_color = random.choice([
            (60, 120, 60), (70, 130, 70), (55, 110, 55),
        ])
        for _ in range(20):
            ox = random.randint(-size // 2, size // 2)
            oy = random.randint(-size // 2, 0)
            cr = random.randint(15, 30)
            ca = random.randint(80, 160)
            draw.ellipse(
                (tx + ox - cr, ty - size + oy - cr, tx + ox + cr, ty - size + oy + cr),
                fill=canopy_color + (ca,),
            )


def _draw_calcite_stream(draw):
    """Small stream with calcite deposits weaving through the scene."""
    points = []
    for x in range(0, W, 10):
        y = 1450 + 30 * math.sin(x * 0.008) + 15 * math.sin(x * 0.02)
        points.append((x, y))

    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        # Water
        draw.line(
            (x1, y1, x2, y2),
            fill=(100, 180, 200, random.randint(40, 80)),
            width=4,
        )
        # Gold-light reflection
        if random.random() < 0.3:
            draw.line(
                (x1, y1 - 1, x2, y2 - 1),
                fill=(255, 200, 100, random.randint(20, 50)),
                width=2,
            )


def _draw_light_motes(draw):
    """Floating bioluminescent particles (algae spores) in the air."""
    for _ in range(90):
        mx = random.randint(0, W)
        my = random.randint(400, 1700)
        mr = random.randint(2, 5)
        color = random.choice([
            (0, 255, 150, random.randint(20, 70)),   # emerald
            (0, 220, 220, random.randint(15, 60)),   # cyan
            (255, 220, 100, random.randint(10, 40)), # gold
        ])
        draw.ellipse(
            (mx - mr, my - mr, mx + mr, my + mr),
            fill=color,
        )


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title, author = m["title"], m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # 1. Sky gradient
    _draw_sky(draw)

    # 2. Sun
    _draw_sun(draw)

    # 3. Distant and mid-ground hills
    _draw_hillside(draw)

    # 4. Cork oak trees
    _draw_cork_oak_trees(draw)

    # 5. Village rooftops
    _draw_village_rooftops(draw)

    # 6. Mycelium archways
    _draw_mycelium_archways(draw)

    # 7. Bioreactors
    _draw_bioreactors(draw)

    # 8. Solar panels
    _draw_solar_panels(draw)

    # 9. Calcite stream
    _draw_calcite_stream(draw)

    # 10. Light motes
    _draw_light_motes(draw)

    # 11. Subtle foreground foliage
    for fx in range(0, W, 15):
        fh = 5 + random.randint(0, 10)
        draw.line(
            (fx, H - fh, fx, H),
            fill=(60, 95, 50, random.randint(60, 120)),
            width=3,
        )

    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
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
