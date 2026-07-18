#!/usr/bin/env python3
"""Cover: The Cartographer of Silent Oceans — Hard SF / Oceanic: a deaf oceanographer maps Europa's subsurface ocean via seismic harmonics, discovering the ice is a living intelligence."""

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
rng.seed(1686748950)


def _draw_starfield(draw, count: int, bbox):
    """Draw random stars in a bounding box (x1, y1, x2, y2)."""
    for _ in range(count):
        sx = rng.randint(bbox[0], bbox[2])
        sy = rng.randint(bbox[1], bbox[3])
        sr = rng.uniform(0.5, 2.5)
        alpha = rng.randint(80, 220)
        draw.ellipse(
            (sx - sr, sy - sr, sx + sr, sy + sr),
            fill=(220, 225, 240, alpha),
        )


def _draw_jupiter(cx, cy, radius):
    """Draw Jupiter as a banded gas giant with the Great Red Spot. Returns an RGBA Image."""
    jimg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    jdraw = ImageDraw.Draw(jimg, "RGBA")

    bands = [
        (0.00, 200, 180, 160),
        (0.08, 230, 190, 140),
        (0.18, 190, 160, 120),
        (0.28, 210, 180, 150),
        (0.35, 180, 140, 100),
        (0.42, 220, 195, 160),
        (0.50, 200, 170, 130),
        (0.60, 170, 130, 100),
        (0.68, 195, 165, 135),
        (0.78, 215, 185, 145),
        (0.85, 190, 155, 115),
        (0.92, 220, 200, 170),
        (1.00, 200, 180, 160),
    ]
    for i in range(len(bands) - 1):
        y0 = int(cy - radius + bands[i][0] * radius * 2)
        y1 = int(cy - radius + bands[i + 1][0] * radius * 2)
        r, g, b = bands[i][1], bands[i][2], bands[i][3]
        r2, g2, b2 = bands[i + 1][1], bands[i + 1][2], bands[i + 1][3]
        for y in range(y0, y1):
            t = (y - y0) / max(1, y1 - y0)
            cr = int(r + (r2 - r) * t)
            cg = int(g + (g2 - g) * t)
            cb = int(b + (b2 - b) * t)
            half_w = int(math.sqrt(max(0, radius * radius - (y - cy) * (y - cy))))
            x0 = cx - half_w
            x1 = cx + half_w
            jdraw.line((x0, y, x1, y), fill=(cr, cg, cb, 255))

    # Great Red Spot
    gsx = cx + int(radius * 0.55)
    gsy = cy + int(radius * 0.15)
    gsrx = int(radius * 0.18)
    gsry = int(radius * 0.10)
    jdraw.ellipse(
        (gsx - gsrx, gsy - gsry, gsx + gsrx, gsy + gsry),
        fill=(210, 140, 100, 220),
    )
    jdraw.ellipse(
        (gsx - gsrx + 5, gsy - gsry + 3, gsx + gsrx - 5, gsy + gsry - 3),
        fill=(190, 120, 80, 180),
    )

    # Glow
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse(
        (cx - radius - 20, cy - radius - 20, cx + radius + 20, cy + radius + 20),
        fill=(200, 180, 150, 15),
    )
    glow = glow.filter(ImageFilter.GaussianBlur(25))
    jimg = Image.alpha_composite(jimg, glow)
    return jimg


def _draw_europa_ice_surface(draw, y_base):
    """Draw Europa's cracked icy surface as a jagged horizontal band."""
    pts = []
    for x in range(0, W + 20, 10):
        offset = 0
        # Large ridges
        offset += math.sin(x * 0.003) * 30
        offset += math.sin(x * 0.007 + 1.2) * 15
        offset += math.sin(x * 0.015 + 2.8) * 8
        # Random jaggedness
        offset += rng.randint(-5, 5)
        pts.append((x, y_base + int(offset)))

    # Ice crust body (thick layer below surface)
    ice_body = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    id_ = ImageDraw.Draw(ice_body)
    ice_poly = pts + [(W, y_base + 120), (0, y_base + 120)]
    id_.polygon(ice_poly, fill=(180, 210, 235, 180))

    # Ice surface line (bright edge)
    draw.line(pts, fill=(230, 240, 255, 220), width=4)

    # Ice cracks (deeper fissures)
    for _ in range(rng.randint(8, 14)):
        cx = rng.randint(50, W - 50)
        cy = y_base + rng.randint(10, 100)
        length = rng.randint(30, 120)
        angle = rng.uniform(-0.5, 0.5) + math.pi / 2
        end_x = cx + int(math.cos(angle) * length)
        end_y = cy + int(math.sin(angle) * length)
        crack_alpha = rng.randint(80, 180)
        draw.line(
            (cx, cy, end_x, end_y),
            fill=(120, 160, 200, crack_alpha),
            width=rng.randint(1, 3),
        )
        # Branching
        if rng.random() < 0.4:
            branch_angle = angle + rng.uniform(0.5, 1.2)
            bx = end_x + int(math.cos(branch_angle) * length * 0.4)
            by = end_y + int(math.sin(branch_angle) * length * 0.4)
            draw.line(
                (end_x, end_y, bx, by),
                fill=(130, 170, 210, crack_alpha - 40),
                width=1,
            )

    # Bioluminescent glow in deep cracks (Elder Crest's presence)
    for _ in range(rng.randint(4, 8)):
        gx = rng.randint(50, W - 50)
        gy = y_base + rng.randint(20, 90)
        gr = rng.randint(15, 40)
        gcol = rng.choice([
            (100, 220, 200),   # cyan
            (80, 200, 230),    # light blue
            (140, 230, 180),   # mint
            (60, 180, 210),    # teal
        ])
        id_.ellipse(
            (gx - gr, gy - gr, gx + gr, gy + gr),
            fill=(*gcol, rng.randint(15, 40)),
        )

    img_ice = Image.alpha_composite(
        Image.new("RGBA", (W, H), (0, 0, 0, 0)),
        ice_body,
    )
    return img_ice


def _draw_research_vessel(draw, cx, cy):
    """Draw the NEMO research submarine in cross-section."""
    # Hull (rounded capsule shape)
    hull_w = 220
    hull_h = 50

    hull = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hull)

    mid_x = cx
    mid_y = cy

    # Main body
    hd.rounded_rectangle(
        (mid_x - hull_w // 2, mid_y - hull_h // 2,
         mid_x + hull_w // 2, mid_y + hull_h // 2),
        radius=25,
        fill=(55, 65, 75, 230),
        outline=(100, 130, 160, 200),
        width=2,
    )

    # Cockpit window (viewport)
    hd.ellipse(
        (mid_x + hull_w // 2 - 40, mid_y - 20,
         mid_x + hull_w // 2 + 10, mid_y + 20),
        fill=(80, 180, 220, 200),
        outline=(140, 200, 240, 220),
        width=2,
    )

    # Interior lights from cockpit
    for _ in range(3):
        lx = mid_x + hull_w // 2 - 25 + rng.randint(-5, 5)
        ly = mid_y + rng.randint(-8, 8)
        hd.ellipse(
            (lx - 3, ly - 3, lx + 3, ly + 3),
            fill=(180, 230, 255, 220),
        )

    # Engine glow at rear
    hd.ellipse(
        (mid_x - hull_w // 2 - 15, mid_y - 12,
         mid_x - hull_w // 2 + 5, mid_y + 12),
        fill=(30, 100, 180, 150),
    )
    hd.ellipse(
        (mid_x - hull_w // 2 - 10, mid_y - 8,
         mid_x - hull_w // 2, mid_y + 8),
        fill=(60, 150, 220, 200),
    )

    # Antenna / sensor array on top
    hd.line(
        (mid_x - 20, mid_y - hull_h // 2,
         mid_x - 20, mid_y - hull_h // 2 - 25),
        fill=(100, 130, 160, 200),
        width=2,
    )
    for i in range(3):
        hd.ellipse(
            (mid_x - 20 - 4, mid_y - hull_h // 2 - 25 + i * 6 - 3,
             mid_x - 20 + 4, mid_y - hull_h // 2 - 25 + i * 6 + 3),
            fill=(200, 60, 60, 180),
        )

    # Label "NEMO" on hull
    for i, ch in enumerate("NEMO"):
        hd.text(
            (mid_x - 15 + i * 14, mid_y - 8),
            ch,
            fill=(140, 190, 220, 180),
        )

    # Side thrusters
    for sign in (-1, 1):
        hd.ellipse(
            (mid_x - hull_w // 2 + 40, mid_y + hull_h // 2 - 5,
             mid_x - hull_w // 2 + 55, mid_y + hull_h // 2 + 8),
            fill=(70, 80, 90, 200),
        )

    # Sonar pulse ring from the vessel
    for ring_r in range(40, 200, 40):
        alpha = max(10, 60 - ring_r // 4)
        hd.ellipse(
            (mid_x - ring_r, mid_y - ring_r,
             mid_x + ring_r, mid_y + ring_r),
            outline=(100, 220, 255, alpha),
            width=2,
        )

    img_hull = Image.alpha_composite(
        Image.new("RGBA", (W, H), (0, 0, 0, 0)),
        hull,
    )
    return img_hull


def _draw_seismic_harmonics(draw, cx, cy):
    """Draw concentric seismic harmonic wave rings originating from the vessel."""
    waves = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(waves)

    base_angles = [
        rng.uniform(0, math.tau) for _ in range(rng.randint(4, 7))
    ]

    for radius in range(60, 800, rng.randint(15, 30)):
        t = radius / 800  # 0 to ~1
        alpha = int(80 * (1 - t) + 5)
        width = max(1, int(4 * (1 - t) + 1))

        # Not all rings are complete — gaps create pattern interference
        if rng.random() < 0.15:
            continue

        # Perturb the circle with sine to create harmonic patterns
        pts = []
        steps = 72
        for i in range(steps + 1):
            ang = math.radians(i * 360 / steps)
            # Seismic harmonic perturbation based on multiple frequencies
            perturb = 0
            for ba in base_angles:
                perturb += math.sin(ang * 2.5 + ba) * radius * 0.04
            perturb += math.sin(ang * 5.0) * radius * 0.02
            perturb += math.cos(ang * 7.3 + 1.2) * radius * 0.015
            rr = radius + int(perturb)
            px = cx + int(math.cos(ang) * rr)
            py = cy + int(math.sin(ang) * rr)
            pts.append((px, py))

        # Color shifts from golden to cyan as it radiates
        t2 = t
        rcol = int(200 - 120 * t2)
        gcol = int(180 + 50 * t2)
        bcol = int(80 + 150 * t2)

        wd.line(pts, fill=(rcol, gcol, bcol, alpha), width=width)

    # Add some data visualization elements — spectral lines
    for _ in range(rng.randint(8, 16)):
        ang = rng.uniform(0, math.tau)
        dist = rng.randint(100, 750)
        x1 = cx + int(math.cos(ang) * dist)
        y1 = cy + int(math.sin(ang) * dist)
        x2 = cx + int(math.cos(ang) * (dist + rng.randint(30, 80)))
        y2 = cy + int(math.sin(ang) * (dist + rng.randint(30, 80)))
        wd.line(
            (x1, y1, x2, y2),
            fill=(rng.randint(180, 255), rng.randint(180, 220), 100, rng.randint(40, 90)),
            width=rng.randint(1, 3),
        )

    img_waves = Image.alpha_composite(
        Image.new("RGBA", (W, H), (0, 0, 0, 0)),
        waves,
    )
    return img_waves


def _draw_subsurface_ocean(draw, y_top, y_bot):
    """Draw the subsurface ocean with depth gradient, particles, and bioluminescence."""
    ocean = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ocean)

    # Depth gradient
    for y in range(y_top, y_bot):
        t = (y - y_top) / max(1, y_bot - y_top)
        r = int(15 - 8 * t)
        g = int(50 + 30 * t)
        b = int(100 + 60 * t)
        od.line((0, y, W, y), fill=(r, g, b, 200))

    # Thermal vent particles rising from bottom
    for _ in range(rng.randint(30, 50)):
        vx = rng.randint(100, W - 100)
        vy = rng.randint(y_bot - 200, y_bot)
        for j in range(rng.randint(3, 6)):
            dy = vy - j * rng.randint(8, 20)
            dx = vx + rng.randint(-8, 8)
            size = 3 - j * 0.5
            if size < 1:
                break
            alpha = rng.randint(40, 100) - j * 10
            od.ellipse(
                (dx - size, dy - size, dx + size, dy + size),
                fill=(rng.randint(150, 220), rng.randint(200, 255), 180, max(10, alpha)),
            )

    # Bioluminescent organisms / Elder Crest traces
    for _ in range(rng.randint(15, 25)):
        bx = rng.randint(50, W - 50)
        by = rng.randint(y_top + 50, y_bot - 50)
        br = rng.randint(8, 30)
        bcol = rng.choice([
            (80, 220, 200),
            (60, 180, 230),
            (120, 230, 180),
            (200, 180, 255),
            (180, 230, 120),
        ])
        balpha = rng.randint(20, 60)
        od.ellipse(
            (bx - br, by - br, bx + br, by + br),
            fill=(*bcol, balpha),
        )
        # Inner glow
        od.ellipse(
            (bx - br // 3, by - br // 3, bx + br // 3, by + br // 3),
            fill=(*bcol, balpha + 40),
        )

        # Connecting filaments (mycelium-like patterns of the living ice)
        if rng.random() < 0.3:
            tx = rng.randint(50, W - 50)
            ty = rng.randint(y_top + 50, y_bot - 50)
            od.line(
                (bx, by, tx, ty),
                fill=(*bcol, rng.randint(10, 25)),
                width=rng.randint(1, 2),
            )

    # Ice crystal shards falling / floating
    for _ in range(rng.randint(20, 35)):
        ix = rng.randint(50, W - 50)
        iy = rng.randint(y_top + 20, y_bot - 20)
        isize = rng.randint(2, 6)
        iangle = rng.uniform(0, math.tau)
        alpha = rng.randint(30, 80)
        pts = []
        for k in range(6):
            a = iangle + k * math.pi / 3
            pts.extend([
                (ix + int(math.cos(a) * isize),
                 iy + int(math.sin(a) * isize)),
                (ix + int(math.cos(a + math.pi / 6) * isize * 0.3),
                 iy + int(math.sin(a + math.pi / 6) * isize * 0.3)),
            ])
        if len(pts) >= 6:
            od.polygon(pts, outline=(180, 220, 255, alpha), width=1)

    img_ocean = Image.alpha_composite(
        Image.new("RGBA", (W, H), (0, 0, 0, 0)),
        ocean,
    )
    return img_ocean


def _draw_ice_cavern_bioluminescence(draw, y_base):
    """Draw intricate ice formations and bioluminescent patterns from Elder Crest."""
    cavern = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cavern)

    # Ice stalactites hanging from the ice crust
    for _ in range(rng.randint(15, 25)):
        sx = rng.randint(50, W - 50)
        length = rng.randint(40, 180)
        width = rng.randint(8, 25)
        pts = [
            (sx - width // 2, y_base),
            (sx + width // 2, y_base),
            (sx + width // 4, y_base + length),
            (sx - width // 4, y_base + length),
        ]
        cd.polygon(pts, fill=(150, 190, 220, rng.randint(60, 120)))

    # Elder Crest communication patterns — glyph-like symbols in the ice
    glyph_positions = []
    for _ in range(rng.randint(6, 10)):
        gx = rng.randint(100, W - 100)
        gy = y_base + rng.randint(20, 150)
        glyph_positions.append((gx, gy))

        # Glow aura
        cd.ellipse(
            (gx - 50, gy - 50, gx + 50, gy + 50),
            fill=(rng.randint(60, 100), rng.randint(180, 240), rng.randint(180, 230), rng.randint(10, 25)),
        )

        # Inner symbol — concentric rings (the "patterns she maps")
        for ring_r in (20, 13, 6, 2):
            alpha = rng.randint(40, 120)
            cd.ellipse(
                (gx - ring_r, gy - ring_r, gx + ring_r, gy + ring_r),
                outline=(80, 220, 210, alpha),
                width=2 if ring_r > 6 else 1,
            )

        # Radial pattern lines
        for rad_angle in range(0, 360, 45):
            ra = math.radians(rad_angle)
            rx = gx + int(math.cos(ra) * 25)
            ry = gy + int(math.sin(ra) * 25)
            cd.line(
                (gx, gy, rx, ry),
                fill=(100, 230, 220, rng.randint(30, 60)),
                width=1,
            )

    # Connecting lines between glyphs (the communication network)
    for i in range(len(glyph_positions) - 1):
        g1 = glyph_positions[i]
        g2 = glyph_positions[i + 1]
        if rng.random() < 0.6:
            cd.line(
                (g1[0], g1[1], g2[0], g2[1]),
                fill=(120, 220, 210, rng.randint(15, 35)),
                width=rng.randint(1, 2),
            )

    img_cavern = Image.alpha_composite(
        Image.new("RGBA", (W, H), (0, 0, 0, 0)),
        cavern,
    )
    return img_cavern


def _draw_vertical_sonar_lines(draw):
    """Draw sonar/data-display vertical lines as an overlay element."""
    sonar = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sonar)

    # Vertical scan lines (like a CRT sonar display)
    for x in range(rng.randint(6, 10)):
        sx = rng.randint(50, W - 50)
        for y in range(0, H, 3):
            if rng.random() < 0.1:
                continue
            alpha = rng.randint(5, 15)
            sd.line(
                (sx, y, sx + rng.randint(-1, 1), y),
                fill=(rng.randint(100, 200), rng.randint(200, 255), rng.randint(150, 220), alpha),
                width=1,
            )

    # Horizontal sampling lines (like a seismograph readout)
    for _ in range(rng.randint(3, 5)):
        sy = rng.randint(200, 1500)
        pts = []
        for x in range(0, W + 10, 10):
            y = sy + math.sin(x * 0.02 + rng.uniform(0, math.tau)) * rng.randint(8, 25)
            y += math.sin(x * 0.05 + rng.uniform(0, math.tau)) * rng.randint(3, 10)
            pts.append((x, y))
        sd.line(
            pts,
            fill=(rng.randint(150, 220), rng.randint(200, 255), rng.randint(100, 180), rng.randint(20, 45)),
            width=1,
        )

    img_sonar = Image.alpha_composite(
        Image.new("RGBA", (W, H), (0, 0, 0, 0)),
        sonar,
    )
    return img_sonar


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    # ── 1. Deep space gradient background ──────────────────────────────
    img = Image.new("RGBA", (W, H), (5, 5, 15, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Vertical gradient: deep space black -> Europa horizon blue
    for y in range(H):
        t = y / H
        if y < 700:
            # Deep space
            r = int(5 + 2 * (y / 700))
            g = int(5 + 3 * (y / 700))
            b = int(15 + 8 * (y / 700))
        elif y < 1150:
            # Europa ice horizon zone
            t2 = (y - 700) / 450
            r = int(7 + 30 * t2)
            g = int(8 + 50 * t2)
            b = int(23 + 80 * t2)
        else:
            # Deep ocean below
            t3 = (y - 1150) / (H - 1150)
            r = int(37 - 22 * t3)
            g = int(58 - 8 * t3)
            b = int(103 + 30 * t3)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── 2. Starfield ──────────────────────────────────────────────────
    # Dense in space, sparse across ice
    _draw_starfield(draw, 180, (0, 0, W, 680))
    _draw_starfield(draw, 30, (0, 680, W, 1080))

    # ── 3. Jupiter in the sky ─────────────────────────────────────────
    img_jupiter = _draw_jupiter(1100, 240, 180)
    img = Image.alpha_composite(img, img_jupiter)

    # ── 4. Europa ice surface (horizon band) ──────────────────────────
    ice_y = 1050
    img_ice = _draw_europa_ice_surface(draw, ice_y)
    img = Image.alpha_composite(img, img_ice)

    # ── 5. Subsurface ocean ───────────────────────────────────────────
    ocean_y_top = ice_y + 120
    ocean_y_bot = H
    img_ocean = _draw_subsurface_ocean(draw, ocean_y_top, ocean_y_bot)
    img = Image.alpha_composite(img, img_ocean)

    # ── 6. NEMO research vessel ───────────────────────────────────────
    vessel_cx = W // 2
    vessel_cy = 1600
    img_vessel = _draw_research_vessel(draw, vessel_cx, vessel_cy)
    img = Image.alpha_composite(img, img_vessel)

    # ── 7. Seismic harmonic wave patterns ─────────────────────────────
    img_harmonics = _draw_seismic_harmonics(draw, vessel_cx, vessel_cy)
    img = Image.alpha_composite(img, img_harmonics)

    # ── 8. Ice caverns and Elder Crest communication glyphs ───────────
    img_cavern = _draw_ice_cavern_bioluminescence(draw, ice_y)
    img = Image.alpha_composite(img, img_cavern)

    # ── 9. Sonar / data visualization overlay ─────────────────────────
    img_sonar = _draw_vertical_sonar_lines(draw)
    img = Image.alpha_composite(img, img_sonar)

    # ── 10. Vignette (edge darkening) ─────────────────────────────────
    vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)

    for y in range(H):
        vt = 1 - abs(y - H // 2) / (H // 2)
        vv = int(60 * max(0, 1 - vt))
        if vv > 0:
            vd.line((0, y, vv, y), fill=(0, 0, 0, 50))
            vd.line((W - vv, y, W, y), fill=(0, 0, 0, 50))

    for x in range(W):
        vt = 1 - abs(x - W // 2) / (W // 2)
        vv = int(40 * max(0, 1 - vt))
        if vv > 0:
            vd.line((x, 0, x, vv), fill=(0, 0, 0, 35))
            vd.line((x, H - vv, x, H), fill=(0, 0, 0, 50))

    img = Image.alpha_composite(img, vig)

    # ── 11. Title panel ───────────────────────────────────────────────
    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, title, author, model)
    img.convert("RGB").save(op, "PNG", optimize=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    mp = a.metadata
    op_ = a.out
    make_cover(
        ROOT / mp if not mp.is_absolute() else mp,
        ROOT / op_ if not op_.is_absolute() else op_,
    )


if __name__ == "__main__":
    main()
