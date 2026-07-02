#!/usr/bin/env python3
"""Cover: The Memory Palace — impossible architectural interior, indigo and gold."""

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

# Book-specific seed for reproducible art
random.seed(20260702)


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


def draw_galaxy_bg(draw):
    """Deep indigo-to-black space gradient."""
    for y in range(H):
        t = y / H
        r = int(8 + 12 * (1 - t))
        g = int(5 + 25 * (1 - t))
        b = int(35 + 65 * (1 - t))
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))


def draw_constellations(draw, img):
    """Constellations of golden light — memory motes scattered through the space."""
    stars = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stars)

    for _ in range(350):
        sx = random.randint(0, W)
        sy = random.randint(0, 1700)
        sr = random.uniform(1.0, 4.5)
        sa = random.randint(80, 220)
        # Golden glow
        sd.ellipse(
            (sx - sr, sy - sr, sx + sr, sy + sr),
            fill=(255, 220, 140, sa),
        )
        # Bright core
        if sr > 2.5:
            sd.ellipse(
                (sx - sr * 0.4, sy - sr * 0.4, sx + sr * 0.4, sy + sr * 0.4),
                fill=(255, 255, 230, min(255, sa + 30)),
            )

    # Connect some stars into constellation lines
    star_points = [(random.randint(0, W), random.randint(200, 1400)) for _ in range(30)]
    for i in range(len(star_points)):
        for j in range(i + 1, len(star_points)):
            dx = star_points[i][0] - star_points[j][0]
            dy = star_points[i][1] - star_points[j][1]
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 200 and dist > 50:
                sd.line(
                    (star_points[i][0], star_points[i][1], star_points[j][0], star_points[j][1]),
                    fill=(255, 210, 120, random.randint(20, 50)),
                    width=random.randint(1, 2),
                )

    stars = stars.filter(ImageFilter.GaussianBlur(2))
    return Image.alpha_composite(img, stars)


def draw_glowing_doorways(draw):
    """Glowing doorways floating in midair — arched portals of golden light."""
    portals = [
        (200, 600, 260, 1000),     # Far left
        (1200, 450, 260, 1000),    # Far right
        (700, 300, 200, 800),      # Center high
        (100, 1100, 180, 700),     # Lower left
        (1300, 1000, 180, 700),    # Lower right
        (500, 900, 160, 600),      # Mid left
        (1000, 750, 160, 600),     # Mid right
    ]

    for px, py, pw, ph in portals:
        # Outer glow
        for glow_r in range(20, 0, -3):
            alpha = int(15 * (1 - glow_r / 20))
            draw.arc(
                (px - glow_r, py - glow_r, px + pw + glow_r, py + ph + glow_r),
                180, 360,
                fill=(255, 200, 100, max(0, alpha)),
                width=2,
            )
            draw.arc(
                (px - glow_r, py - glow_r, px + pw + glow_r, py + ph + glow_r),
                0, 180,
                fill=(255, 200, 100, max(0, alpha)),
                width=2,
            )

        # Arch shape
        draw.arc(
            (px, py, px + pw, py + ph),
            180, 360,
            fill=(255, 215, 130, 200),
            width=6,
        )

        # Doorway interior fill (translucent golden light)
        door_poly = []
        for a_deg in range(180, 360):
            a_rad = math.radians(a_deg)
            door_poly.append((px + pw // 2 + (pw // 2) * math.cos(a_rad), py + ph // 2 + (ph // 2) * math.sin(a_rad)))
        door_poly.append((px + pw, py + ph))
        door_poly.append((px, py + ph))
        draw.polygon(door_poly, fill=(255, 210, 120, 25))

        # Inner light beam streaming from door
        beam_cx = px + pw // 2
        beam_y = py + ph
        for b_line in range(5):
            bx_offset = random.randint(-pw // 3, pw // 3)
            b_alpha = random.randint(10, 30)
            draw.line(
                (beam_cx + bx_offset, beam_y, beam_cx + bx_offset + random.randint(-30, 30), beam_y + random.randint(100, 250)),
                fill=(255, 220, 150, b_alpha),
                width=random.randint(2, 6),
            )


def draw_spiral_staircases(draw):
    """Floating spiral staircases — impossible architectural elements."""
    stairsets = [
        {"cx": 400, "cy": 800, "r": 120, "height": 600, "rot": 0.0},
        {"cx": 1200, "cy": 600, "r": 100, "height": 500, "rot": 30.0},
        {"cx": 800, "cy": 1100, "r": 140, "height": 700, "rot": 15.0},
        {"cx": 100, "cy": 500, "r": 80, "height": 400, "rot": -10.0},
        {"cx": 1500, "cy": 900, "r": 90, "height": 450, "rot": 20.0},
    ]

    for stair in stairsets:
        cx, cy, r, sh, rot = stair["cx"], stair["cy"], stair["r"], stair["height"], stair["rot"]
        rot_rad = math.radians(rot)
        steps = 20
        for i in range(steps):
            t = i / steps
            angle = t * 2 * math.pi * 2.5 + rot_rad
            sx = cx + r * math.cos(angle) * (1 - t * 0.3)
            sy = cy + t * sh
            sz = r * (1 - t * 0.3) * 0.3  # step width scales with perspective

            # Step tread
            alpha = int(60 + 120 * (1 - t))
            step_color = (180, 160, 120, alpha)
            draw.ellipse(
                (sx - sz, sy - 4, sx + sz, sy + 4),
                fill=step_color,
                outline=(200, 180, 140, alpha + 20),
            )

            # Riser line (thin vertical connector between steps)
            if i > 0:
                prev_t = (i - 1) / steps
                prev_angle = prev_t * 2 * math.pi * 2.5 + rot_rad
                p_sx = cx + r * math.cos(prev_angle) * (1 - prev_t * 0.3)
                p_sy = cy + prev_t * sh
                draw.line(
                    (p_sx, p_sy, sx, sy),
                    fill=(160, 140, 100, alpha // 2),
                    width=2,
                )

        # Central glowing core of staircase
        core_y_top = cy
        core_y_bot = cy + sh
        for y_line in range(core_y_top, core_y_bot, 4):
            t_core = (y_line - core_y_top) / sh
            core_width = int(6 * (1 - t_core * 0.5))
            core_alpha = int(40 * (1 - t_core * 0.3))
            draw.line(
                (cx - core_width, y_line, cx + core_width, y_line),
                fill=(255, 220, 150, max(0, core_alpha)),
                width=1,
            )


def draw_translucent_bridges(draw):
    """Translucent bridges connecting rooms and platforms in midair."""
    bridges = [
        (200, 800, 700, 600),
        (500, 1100, 1200, 900),
        (400, 600, 100, 500),
        (800, 500, 1300, 700),
        (300, 950, 800, 1100),
        (1200, 650, 1500, 800),
        (700, 900, 1000, 750),
    ]

    for x1, y1, x2, y2 in bridges:
        # Bridge path with slight sag
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2 + 30  # Sag in middle
        segments = 20

        for s in range(segments):
            s1 = s / segments
            s2 = (s + 1) / segments
            # Quadratic bezier
            bx1 = (1 - s1) ** 2 * x1 + 2 * (1 - s1) * s1 * mid_x + s1 ** 2 * x2
            by1 = (1 - s1) ** 2 * y1 + 2 * (1 - s1) * s1 * mid_y + s1 ** 2 * y2
            bx2 = (1 - s2) ** 2 * x1 + 2 * (1 - s2) * s2 * mid_x + s2 ** 2 * x2
            by2 = (1 - s2) ** 2 * y1 + 2 * (1 - s2) * s2 * mid_y + s2 ** 2 * y2

            alpha = int(25 + 15 * math.sin(s * 1.5))
            width = int(3 + 2 * math.sin(s * 1.2))

            # Main bridge line (translucent)
            draw.line(
                (bx1, by1, bx2, by2),
                fill=(180, 200, 220, max(0, alpha)),
                width=width,
            )

            # Glowing edge
            draw.line(
                (bx1 - 1, by1 - 1, bx2 - 1, by2 - 1),
                fill=(220, 230, 255, max(0, alpha // 2)),
                width=1,
            )

        # Small glowing dots along bridge (memory particles crossing)
        for _ in range(12):
            st = random.random()
            bp_x = (1 - st) ** 2 * x1 + 2 * (1 - st) * st * mid_x + st ** 2 * x2
            bp_y = (1 - st) ** 2 * y1 + 2 * (1 - st) * st * mid_y + st ** 2 * y2
            rad = random.uniform(1.5, 3.5)
            draw.ellipse(
                (bp_x - rad, bp_y - rad, bp_x + rad, bp_y + rad),
                fill=(255, 230, 180, random.randint(60, 150)),
            )


def draw_architectural_frames(draw):
    """Partial architectural frames — column arches, floating pillars suggesting infinite space."""
    # Large central arch frame
    arch_cx = W // 2
    arch_y = 300
    arch_w = 900
    arch_h = 600

    # Outer ghost arch
    for offset in [0, -300, 300, -600, 600]:
        fade = max(0, 20 - abs(offset) // 10)
        ax = arch_cx + offset - arch_w // 2
        draw.arc(
            (ax, arch_y, ax + arch_w, arch_y + arch_h),
            180, 360,
            fill=(100, 120, 180, fade),
            width=3,
        )

    # Main arch
    draw.arc(
        (arch_cx - arch_w // 2, arch_y, arch_cx + arch_w // 2, arch_y + arch_h),
        180, 360,
        fill=(160, 180, 220, 120),
        width=5,
    )

    # Pillars (ghost columns)
    pillar_positions = [
        (50, 200, 1700),
        (100, 150, 1400),
        (200, 250, 1600),
        (1400, 200, 1700),
        (1500, 150, 1400),
        (1300, 250, 1600),
    ]
    for px, py, ph in pillar_positions:
        p_alpha = random.randint(30, 70)
        # Column shaft
        draw.rectangle(
            (px - 10, py, px + 10, py + ph),
            fill=(120, 140, 200, p_alpha),
        )
        # Capital (top)
        draw.rectangle(
            (px - 20, py - 5, px + 20, py + 10),
            fill=(150, 170, 220, p_alpha + 10),
        )
        # Base
        draw.rectangle(
            (px - 20, py + ph - 10, px + 20, py + ph + 5),
            fill=(150, 170, 220, p_alpha + 10),
        )


def draw_nebula_glow(draw, img):
    """Diffuse nebula-like glow in the indigo space."""
    nebula = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(nebula)

    # Several large soft glows
    centers = [
        (800, 400, 300),   # Center high
        (300, 700, 250),   # Left mid
        (1300, 500, 200),  # Right high
        (600, 1200, 350),  # Lower center-left
        (1100, 1000, 250), # Lower center-right
    ]

    for gx, gy, gr in centers:
        for layer in range(3):
            lr = gr - layer * 30
            alpha = 20 - layer * 5
            if alpha <= 0:
                continue
            colors = [
                (80, 60, 140, alpha),
                (60, 40, 120, alpha),
                (100, 70, 160, alpha),
                (50, 80, 130, alpha),
                (120, 80, 100, alpha),
            ]
            col = random.choice(colors)
            nd.ellipse(
                (gx - lr, gy - lr, gx + lr, gy + lr),
                fill=col,
            )

    nebula = nebula.filter(ImageFilter.GaussianBlur(50))
    return Image.alpha_composite(img, nebula)


def draw_glowing_rooms(draw):
    """Floating room structures — cubes and rectilinear spaces suspended in the void."""
    rooms = [
        (600, 500, 180, 160),
        (1000, 400, 150, 140),
        (300, 1200, 140, 120),
        (1200, 1100, 160, 130),
        (750, 800, 200, 170),
        (200, 900, 120, 110),
        (1350, 700, 130, 120),
    ]

    for rx, ry, rw, rh in rooms:
        # Room walls (translucent)
        alpha = random.randint(25, 45)
        draw.rectangle(
            (rx, ry, rx + rw, ry + rh),
            fill=(100, 120, 180, alpha),
            outline=(160, 180, 220, alpha + 30),
            width=2,
        )

        # Window openings
        win_count = random.randint(1, 3)
        for _ in range(win_count):
            wx = rx + random.randint(int(rw * 0.1), int(rw * 0.8))
            wy = ry + random.randint(int(rh * 0.15), int(rh * 0.75))
            ww = random.randint(15, 35)
            wh = random.randint(25, 45)
            win_alpha = random.randint(60, 130)
            draw.rectangle(
                (wx, wy, wx + ww, wy + wh),
                fill=(255, 220, 140, win_alpha),
            )
            # Warm glow spill from window
            draw.rectangle(
                (wx - 5, wy - 5, wx + ww + 5, wy + wh + 5),
                fill=(255, 210, 120, 15),
            )

        # Room floor glow
        draw.line(
            (rx, ry + rh, rx + rw, ry + rh),
            fill=(255, 220, 150, 60),
            width=3,
        )


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title, author = m["title"], m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Step 1: Deep space gradient
    draw_galaxy_bg(draw)

    # Step 2: Nebula glow layers
    img = draw_nebula_glow(draw, img)
    draw = ImageDraw.Draw(img, "RGBA")

    # Step 3: Architectural frames (ghost pillars and arches)
    draw_architectural_frames(draw)

    # Step 4: Floating spiral staircases
    draw_spiral_staircases(draw)

    # Step 5: Glowing doorways in midair
    draw_glowing_doorways(draw)

    # Step 6: Translucent bridges
    draw_translucent_bridges(draw)

    # Step 7: Floating rooms
    draw_glowing_rooms(draw)

    # Step 8: Memory constellations
    img = draw_constellations(draw, img)

    # Step 9: Additional ambient golden particles
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(120):
        px = random.randint(0, W)
        py = random.randint(0, 1750)
        pr = random.uniform(0.8, 2.5)
        pa = random.randint(20, 80)
        draw.ellipse(
            (px - pr, py - pr, px + pr, py + pr),
            fill=(255, 230, 170, pa),
        )

    # Step 10: Standard title panel at bottom
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