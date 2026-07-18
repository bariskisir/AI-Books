#!/usr/bin/env python3
"""Cover: The Cartographer's Last Meridian 3 — 1519 Magellan fleet at sea viewed through an astrolabe frame, star-map sky, storm-lit ships sailing toward the unknown strait, with a betrayal undertone bleeding crimson from below."""

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
rng.seed(547819203)

# Deep midnight ocean / betrayal palette
SKY_TOP = (4, 4, 35)
SKY_MID = (12, 16, 60)
SKY_BOT = (25, 30, 80)
STORM_GREEN = (40, 70, 65)
CRIMSON_UNDER = (90, 8, 5)
SEA_DARK = (8, 18, 28)
SEA_LIGHT = (28, 55, 65)
BRASS = (190, 160, 70)
BRASS_DARK = (130, 110, 50)
STAR_COLOR = (230, 230, 210)
SAIL_DARK = (35, 30, 25)
SAIL_LIGHT = (140, 130, 110)
LANTERN_WARM = (255, 200, 80)
WAVE_FOAM = (180, 200, 210)


def _draw_astrolabe_frame(draw: ImageDraw.ImageDraw) -> None:
    """Draw a large brass astrolabe/cross-staff silhouette framing the left/right edges.

    The instrument arcs inward at the top, suggesting the viewer is looking through
    a navigator's tool at the unfolding voyage.
    """
    # Left vertical arm of the astrolabe
    for x in range(0, 90):
        alpha = int(200 * (1 - x / 90))
        draw.line((x, 0, x, H), fill=(*BRASS_DARK, alpha // 2))
        if x < 30:
            a2 = int(200 * (1 - x / 30))
            draw.line((x, 0, x, H), fill=(*BRASS, a2 // 3))

    # Right vertical arm
    for x in range(W - 90, W):
        alpha = int(200 * (1 - (W - x) / 90))
        draw.line((x, 0, x, H), fill=(*BRASS_DARK, alpha // 2))
        if x > W - 30:
            a2 = int(200 * (1 - (W - x) / 30))
            draw.line((x, 0, x, H), fill=(*BRASS, a2 // 3))

    # Top arc (the graduated arc of an astrolabe)
    arc_center_x = W // 2
    arc_center_y = -200
    arc_radius = 1000
    for a_deg in range(0, 180, 2):
        rad = math.radians(a_deg)
        x0 = arc_center_x + math.cos(rad) * (arc_radius - 15)
        y0 = arc_center_y + math.sin(rad) * (arc_radius - 15)
        x1 = arc_center_x + math.cos(rad) * (arc_radius + 25)
        y1 = arc_center_y + math.sin(rad) * (arc_radius + 25)
        # Only draw the parts that are within the left and right arms
        if 0 <= x0 <= W:
            draw.line((x0, y0, x1, y1), fill=(*BRASS_DARK, 120), width=2)

    # Graduation tick marks on the arc
    for a_deg in range(0, 180, 5):
        rad = math.radians(a_deg)
        tick_inner = arc_radius - 10
        tick_outer = arc_radius + 10
        if a_deg % 20 == 0:
            tick_outer = arc_radius + 20
        tx = arc_center_x + math.cos(rad) * tick_inner
        ty = arc_center_y + math.sin(rad) * tick_inner
        tx2 = arc_center_x + math.cos(rad) * tick_outer
        ty2 = arc_center_y + math.sin(rad) * tick_outer
        if 0 <= tx <= W:
            draw.line((tx, ty, tx2, ty2), fill=(*BRASS, 100), width=2 if a_deg % 20 == 0 else 1)

    # Crossbar (horizontal sighting bar)
    for x in range(90, W - 90):
        bar_y = 80
        alpha = int(120 - 80 * abs(x - W / 2) / (W / 2))
        draw.line((x, bar_y - 4, x, bar_y + 4), fill=(*BRASS_DARK, max(10, alpha)))
        if abs(x - W / 2) < 200:
            draw.line((x, bar_y - 7, x, bar_y + 7), fill=(*BRASS, max(20, alpha)))

    # Pinhole sight at center of crossbar
    draw.ellipse((W // 2 - 12, 68, W // 2 + 12, 92), fill=(*BRASS, 180))
    draw.ellipse((W // 2 - 4, 76, W // 2 + 4, 84), fill=(4, 4, 35, 255))


def _draw_star_map(draw: ImageDraw.ImageDraw) -> None:
    """Draw a star-map sky with constellations, nebula glows, and a crescent moon."""
    const_stars = [
        # Constellation 1: A ship's outline (Carina-like)
        [(500, 150), (550, 120), (620, 130), (680, 170), (650, 200), (580, 210), (520, 190)],
        # Constellation 2: A compass (Circinus-like)
        [(900, 90), (950, 160), (1020, 140), (980, 100)],
        [(920, 180), (980, 190), (1020, 150)],
        # Constellation 3: A serpent/dragon (Hydra-like)
        [(200, 250), (260, 270), (330, 260), (400, 290), (470, 275), (540, 300),
         (610, 285), (680, 310), (750, 295), (820, 320), (890, 305)],
        # Constellation 4: Southern Cross
        [(1100, 250), (1140, 320), (1120, 360), (1080, 290)],
        [(1120, 250), (1120, 360)],
        [(1080, 290), (1140, 320)],
    ]

    # Draw constellation connection lines (faint)
    for stars in const_stars:
        for i in range(len(stars) - 1):
            draw.line(stars[i] + stars[i + 1], fill=(*STAR_COLOR, 20), width=1)

    # Draw individual stars from each constellation
    for stars in const_stars:
        for sx, sy in stars:
            sr = rng.uniform(1.5, 4.0)
            glow_r = int(sr * 4)
            # Star glow
            draw.ellipse((sx - glow_r, sy - glow_r, sx + glow_r, sy + glow_r),
                         fill=(*STAR_COLOR, 10))
            draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr),
                         fill=(*STAR_COLOR, rng.randint(150, 230)))

    # Random field stars
    for _ in range(300):
        sx = rng.randint(0, W)
        sy = rng.randint(0, 600)
        sr = rng.uniform(0.3, 2.0)
        sa = rng.randint(30, 200)
        draw.ellipse((int(sx - sr), int(sy - sr), int(sx + sr), int(sy + sr)),
                     fill=(*STAR_COLOR, sa))

    # Nebula glows
    nebula = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(nebula)
    nd.ellipse((100, 50, 500, 350), fill=(120, 100, 200, 8))
    nd.ellipse((900, 180, 1300, 450), fill=(200, 100, 150, 6))
    nd.ellipse((1100, 60, 1500, 280), fill=(100, 150, 220, 5))
    nebula = nebula.filter(ImageFilter.GaussianBlur(40))
    img_holder = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img_holder.alpha_composite(nebula)
    draw._image.alpha_composite(nebula)

    # Crescent moon
    moon_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(moon_layer)
    moon_cx, moon_cy = 1350, 180
    moon_rad = 55
    md.ellipse((moon_cx - moon_rad, moon_cy - moon_rad,
                moon_cx + moon_rad, moon_cy + moon_rad),
               fill=(210, 205, 190, 200))
    # Crescent cut-out (dark side)
    md.ellipse((moon_cx - moon_rad + 15, moon_cy - moon_rad - 10,
                moon_cx + moon_rad - 5, moon_cy + moon_rad + 10),
               fill=(*SKY_TOP, 255))
    moon_layer = moon_layer.filter(ImageFilter.GaussianBlur(1))
    draw._image.alpha_composite(moon_layer)


def _draw_fleet(draw: ImageDraw.ImageDraw) -> None:
    """Draw Magellan's fleet of sailing ships on the dark sea below."""
    ships = [
        (300, 1650, 1.0),
        (600, 1750, 0.85),
        (900, 1690, 0.9),
        (1250, 1780, 0.75),
        (1450, 1720, 0.7),
    ]

    for sx, sy, scale in ships:
        hull_w = int(100 * scale)
        hull_h = int(20 * scale)
        mast_h = int(120 * scale)

        # Hull
        hull_pts = [
            (sx - hull_w // 2, sy),
            (sx - hull_w // 2 + 5, sy + hull_h),
            (sx + hull_w // 2 - 10, sy + hull_h),
            (sx + hull_w // 2, sy - 5),
        ]
        draw.polygon(hull_pts, fill=(*SAIL_DARK, 220))
        # Hull highlight
        draw.line((sx - hull_w // 2 + 5, sy + hull_h - 3,
                   sx + hull_w // 2 - 10, sy + hull_h - 3),
                  fill=(50, 35, 25, 100))

        # Masts
        for m_off in [-40, 0, 40]:
            mx = sx + int(m_off * scale)
            draw.line((mx, sy, mx, sy - int(mast_h * (0.8 + 0.2 * (m_off == 0)))),
                      fill=(60, 55, 50, 200), width=max(1, int(3 * scale)))

        # Sails (billowing)
        for m_off, m_width, m_height, bulge in [
            (-40, 35, 50, 8),
            (0, 40, 60, 10),
            (40, 30, 45, 7),
        ]:
            mx = sx + int(m_off * scale)
            sail_top = sy - int(mast_h * 0.85 * scale)
            sail_bot = sy - int(mast_h * 0.3 * scale)
            sail_w = int(m_width * scale)
            sail_h = int(m_height * scale)
            bulge_amt = int(bulge * scale)

            # Sail as a filled curve
            sail_pts = [
                (mx - sail_w, sail_top + bulge_amt),
                (mx - 2, sail_top),
                (mx + sail_w, sail_top + bulge_amt),
                (mx + sail_w - 2, sail_bot - bulge_amt),
                (mx, sail_bot),
                (mx - sail_w + 2, sail_bot - bulge_amt),
            ]
            draw.polygon(sail_pts, fill=(*SAIL_LIGHT, 180))
            draw.polygon(sail_pts, fill=(*SAIL_LIGHT, 40), outline=(*SAIL_DARK, 100))

        # Lantern light on the stern
        lantern_r = int(6 * scale)
        draw.ellipse((sx + hull_w // 2 - lantern_r, sy - hull_h - lantern_r,
                      sx + hull_w // 2 + lantern_r, sy - hull_h + lantern_r),
                     fill=(*LANTERN_WARM, 220))

        # Lantern glow
        glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow_layer)
        glow_r = int(40 * scale)
        gd.ellipse((sx + hull_w // 2 - glow_r, sy - hull_h - glow_r,
                    sx + hull_w // 2 + glow_r, sy - hull_h + glow_r),
                   fill=(*LANTERN_WARM, 8))
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(15))
        draw._image.alpha_composite(glow_layer)

        # Small pennant at top of main mast
        penn_x = sx
        penn_top = sy - int(mast_h * scale)
        for py in range(0, 12):
            p_x = penn_x + int(8 * scale * (1 - py / 12))
            draw.line((p_x, penn_top + py, p_x + int(5 * scale), penn_top + py),
                      fill=(140, 25, 25, 180), width=1)


def _draw_sea(draw: ImageDraw.ImageDraw) -> None:
    """Draw the stormy sea with wave crests and foam."""
    # Base sea gradient
    sea_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sea_layer)
    for y in range(1550, H):
        t = (y - 1550) / (H - 1550)
        r = int(SEA_DARK[0] + (SEA_LIGHT[0] - SEA_DARK[0]) * t * 0.3)
        g = int(SEA_DARK[1] + (SEA_LIGHT[1] - SEA_DARK[1]) * t * 0.3)
        b = int(SEA_DARK[2] + (SEA_LIGHT[2] - SEA_DARK[2]) * t * 0.3)
        sd.line((0, y, W, y), fill=(r, g, b, 255))

    # Wave crests
    for wave_x in range(0, W, 4):
        for wi in range(3):
            wave_amp = 6 + wi * 4
            wave_freq = 0.015 + wi * 0.005
            wave_phase = rng.uniform(0, math.tau)
            wave_y = 1550 + wi * 40 + math.sin(wave_x * wave_freq + wave_phase) * wave_amp
            # Distorted wave crests for storm effect
            wave_y += math.sin(wave_x * 0.04 + wave_phase * 2) * 3
            if 1550 <= wave_y < H:
                alpha = max(10, 60 - wi * 15)
                sd.line((wave_x, wave_y, wave_x + 2, wave_y),
                        fill=(*WAVE_FOAM, alpha))

    sea_layer = sea_layer.filter(ImageFilter.GaussianBlur(1))
    draw._image.alpha_composite(sea_layer)

    # Foam near ship hulls
    for fx in range(0, W, rng.randint(8, 20)):
        fy = rng.randint(1560, 1800)
        fw = rng.randint(3, 8)
        draw.line((fx - fw, fy, fx + fw, fy), fill=(*WAVE_FOAM, rng.randint(15, 40)), width=1)


def _draw_storm_clouds(draw: ImageDraw.ImageDraw) -> None:
    """Draw storm clouds gathering above the sea, with a crimson undertone from below."""
    cloud_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cloud_layer)

    for _ in range(40):
        cx = rng.randint(0, W)
        cy = rng.randint(400, 1400)
        cw = rng.randint(80, 300)
        ch = rng.randint(30, 80)
        # Dark storm cloud
        cd.ellipse((cx - cw // 2, cy - ch // 2, cx + cw // 2, cy + ch // 2),
                   fill=(rng.randint(15, 30), rng.randint(15, 30), rng.randint(35, 50), rng.randint(40, 80)))
        # Cloud highlight (storm-top silver lining)
        cd.ellipse((cx - cw // 3, cy - ch // 3, cx + cw // 3, cy - ch // 6),
                   fill=(rng.randint(60, 100), rng.randint(60, 100), rng.randint(80, 120), rng.randint(20, 40)))

    # Crimson betrayal undertone creeping from the bottom horizon
    for y in range(1400, 1750):
        t = (y - 1400) / 350
        alpha = int(25 * t * (1 - t))
        cd.line((0, y, W, y), fill=(*CRIMSON_UNDER, alpha))

    cloud_layer = cloud_layer.filter(ImageFilter.GaussianBlur(12))
    draw._image.alpha_composite(cloud_layer)

    # Lightning strike suggestion (faint)
    if rng.random() < 0.5:
        lx = rng.randint(200, 1400)
        ly = rng.randint(400, 900)
        for branch in range(3):
            bx = lx + rng.randint(-30, 30)
            by = ly
            for _ in range(8):
                bx += rng.randint(-15, 15)
                by += rng.randint(30, 50)
                draw.line((bx - 2, by - 5, bx + 2, by + 5),
                          fill=(200, 210, 230, rng.randint(10, 30)), width=1)


def _draw_rocky_strait(draw: ImageDraw.ImageDraw) -> None:
    """Draw the rocky southern strait in the background, suggesting the passage ahead."""
    strait_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    std = ImageDraw.Draw(strait_layer)

    # Left land mass
    left_pts = [(0, 1450)]
    for lx in range(0, 500, 10):
        ly = 1280 + math.sin(lx * 0.02) * 60 + math.sin(lx * 0.07) * 20
        left_pts.append((lx, ly))
    left_pts.append((500, 1550))
    left_pts.append((0, 1550))
    std.polygon(left_pts, fill=(15, 15, 20, 200))
    # Left land highlight
    for lx in range(0, 400, 4):
        ly = 1290 + math.sin(lx * 0.02) * 55 + math.sin(lx * 0.07) * 18
        std.line((lx, ly, lx, ly + 3), fill=(25, 25, 35, 80), width=1)

    # Right land mass
    right_pts = [(W, 1450)]
    for rx in range(W, W - 500, -10):
        ry = 1250 + math.sin(rx * 0.025) * 70 + math.sin(rx * 0.06) * 15
        right_pts.append((rx, ry))
    right_pts.append((W - 500, 1550))
    right_pts.append((W, 1550))
    std.polygon(right_pts, fill=(15, 15, 20, 200))

    # Snow caps on the peaks
    for lx in range(100, 350, 15):
        ly = 1290 + math.sin(lx * 0.02) * 55
        if ly < 1380:
            std.ellipse((lx - 6, ly - 4, lx + 6, ly + 4), fill=(140, 150, 160, rng.randint(20, 40)))
    for rx in range(W - 350, W - 100, 15):
        ry = 1260 + math.sin(rx * 0.025) * 65
        if ry < 1360:
            std.ellipse((rx - 6, ry - 4, rx + 6, ry + 4), fill=(140, 150, 160, rng.randint(20, 40)))

    strait_layer = strait_layer.filter(ImageFilter.GaussianBlur(3))
    draw._image.alpha_composite(strait_layer)

    # Fog bank at the strait entrance
    fog_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog_layer)
    fd.ellipse((200, 1450, W - 200, 1650), fill=(100, 120, 130, 12))
    fog_layer = fog_layer.filter(ImageFilter.GaussianBlur(30))
    draw._image.alpha_composite(fog_layer)


def _draw_betrayal_motif(draw: ImageDraw.ImageDraw) -> None:
    """Add subtle crimson 'X' marks and blood-betrayal symbols to the edges."""
    # Blood-red 'X' marks suggesting crossed-out names / betrayal
    x_positions = [
        (120, 1200),
        (1480, 1350),
        (80, 900),
        (1520, 600),
    ]
    for xc, yc in x_positions:
        size = rng.randint(10, 18)
        alpha = rng.randint(40, 70)
        draw.line((xc - size, yc - size, xc + size, yc + size),
                  fill=(*CRIMSON_UNDER, alpha), width=2)
        draw.line((xc + size, yc - size, xc - size, yc + size),
                  fill=(*CRIMSON_UNDER, alpha), width=2)

    # Faint bloody drip at the bottom of the astrolabe frame
    for drip_x in [60, 130, 1470, 1540]:
        for dy in range(10):
            draw.line((drip_x + rng.randint(-3, 3), H - 800 - dy * 15,
                       drip_x + rng.randint(-3, 3), H - 800 - dy * 15 + 10),
                      fill=(*CRIMSON_UNDER, max(5, 30 - dy * 2)), width=rng.randint(1, 2))


def make_cover(mp: Path, op: Path) -> None:
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (*SKY_TOP, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Gradient sky background
    for y in range(H):
        t = y / H
        if t < 0.4:
            # Sky gradient: top to middle
            tt = t / 0.4
            r = int(SKY_TOP[0] + (SKY_MID[0] - SKY_TOP[0]) * tt)
            g = int(SKY_TOP[1] + (SKY_MID[1] - SKY_TOP[1]) * tt)
            b = int(SKY_TOP[2] + (SKY_MID[2] - SKY_TOP[2]) * tt)
        elif t < 0.65:
            # Middle to sea transition
            tt = (t - 0.4) / 0.25
            r = int(SKY_MID[0] + (SKY_BOT[0] - SKY_MID[0]) * tt)
            g = int(SKY_MID[1] + (SKY_BOT[1] - SKY_MID[1]) * tt)
            b = int(SKY_MID[2] + (SKY_BOT[2] - SKY_MID[2]) * tt)
        else:
            # Sea area, darken further
            tt = (t - 0.65) / 0.35
            r = int(SKY_BOT[0] * (1 - tt * 0.5))
            g = int(SKY_BOT[1] * (1 - tt * 0.4))
            b = int(SKY_BOT[2] * (1 - tt * 0.3))
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Draw all elements in order (back to front)
    _draw_star_map(draw)
    _draw_rocky_strait(draw)
    _draw_storm_clouds(draw)
    _draw_sea(draw)
    _draw_fleet(draw)
    _draw_astrolabe_frame(draw)
    _draw_betrayal_motif(draw)

    # Vignette effect
    vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette)
    for vy in range(H):
        vt = abs(vy - H // 2) / (H // 2)
        va = int(60 * vt * vt)
        if va > 0:
            vd.line((0, vy, 30, vy), fill=(0, 0, 0, va))
            vd.line((W - 30, vy, W, vy), fill=(0, 0, 0, va))
    vignette = vignette.filter(ImageFilter.GaussianBlur(4))
    img = Image.alpha_composite(img, vignette)
    draw = ImageDraw.Draw(img, "RGBA")

    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, title, author, model)
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
