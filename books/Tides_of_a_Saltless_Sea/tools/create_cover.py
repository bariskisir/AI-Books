#!/usr/bin/env python3
"""Cover: Tides of a Saltless Sea — Two estranged oceanographers share a Dead Sea research station; salt terraces, a lone pier, and the chemistry that pulls them back together."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# Warm mineral earth meets cool saline water
# Sky: amber-ochre sunset fading to violet-slate
# Water: deep teal-slate with saline reflections
# Salt: ivory, cream, pale gold


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")
    rng = random.Random("tides-saltless-sea-2024")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Sky gradient: deep violet-slate at top → amber-ochre at horizon ──
    horizon = 1050
    for y in range(horizon + 50):
        t = y / (horizon + 50)
        r = int(180 + 70 * math.sin(t * math.pi * 0.4))
        g = int(90 + 80 * (1 - t))
        b = int(60 + 90 * (1 - t))
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── Desert mountain silhouettes (distant) ─────────────────────────────
    mt_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(mt_layer)
    for peak in range(5):
        px = peak * 400 + rng.randint(-100, 100)
        py = 500 + rng.randint(-80, 80)
        pts = [(0, horizon)]
        for sx in range(0, W + 20, 20):
            dist = abs(sx - px) / W
            noise = math.sin(sx * 0.008 + peak) * 40 + rng.randint(-20, 20)
            sy = py + dist * dist * (horizon - py) + noise
            pts.append((sx, int(sy)))
        pts.append((W, horizon))
        mt_shade = 40 + peak * 8
        md.polygon(pts, fill=(mt_shade, mt_shade - 5, mt_shade - 10, 200))

    # Distant layer (lighter, hazier)
    for peak in range(3):
        px = peak * 600 + rng.randint(-80, 80)
        py = 600 + rng.randint(-40, 40)
        pts = [(0, horizon)]
        for sx in range(0, W + 20, 20):
            dist = abs(sx - px) / W
            noise = math.sin(sx * 0.006 + peak * 2) * 30
            sy = py + dist * dist * (horizon - py) + noise
            pts.append((sx, int(sy)))
        pts.append((W, horizon))
        md.polygon(pts, fill=(80, 65, 50, 120))

    img = Image.alpha_composite(img, mt_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Salt terrace formations (white mineral deposits along shore) ─────
    salt_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sld = ImageDraw.Draw(salt_layer)

    shore_y = horizon + rng.randint(20, 40)
    for terrace in range(12):
        tx = terrace * 150 + rng.randint(-40, 40)
        tw = rng.randint(120, 250)
        th = rng.randint(15, 40)
        ty = shore_y + terrace * 8 + rng.randint(-5, 5)
        # Irregular salt polygon
        pts = [(tx - tw // 2, ty),
               (tx - tw // 4, ty - th // 2),
               (tx, ty - th),
               (tx + tw // 4, ty - th // 2),
               (tx + tw // 2, ty)]
        for p in range(len(pts)):
            pts[p] = (pts[p][0] + rng.randint(-8, 8), pts[p][1] + rng.randint(-4, 4))
        salt_light = rng.randint(180, 230)
        sld.polygon(pts, fill=(salt_light, salt_light - 10, salt_light - 20, rng.randint(120, 200)))

    # Salt crust along entire shoreline (mosaic effect)
    for x in range(0, W, 6):
        cy = shore_y + int(math.sin(x * 0.03) * 12 + math.sin(x * 0.07) * 5) + rng.randint(-3, 3)
        cv = rng.randint(160, 220)
        sld.line((x, cy, x + 4, cy + rng.randint(-2, 2)),
                  fill=(cv, cv - 8, cv - 15, rng.randint(60, 150)), width=rng.randint(2, 5))

    # Individual salt crystal clusters (foreground)
    for _ in range(40):
        cx = rng.randint(0, W)
        cy = shore_y + rng.randint(20, 160)
        size = rng.randint(4, 15)
        angle = rng.uniform(0, math.tau)
        crystal_color = (220 + rng.randint(-20, 20), 215 + rng.randint(-20, 20), 200 + rng.randint(-20, 20))
        # Draw hexagon-ish crystal
        hex_pts = []
        for h in range(6):
            ha = angle + h * math.pi / 3
            hx = cx + math.cos(ha) * size
            hy = cy + math.sin(ha) * size * 0.7
            hex_pts.append((hx, hy))
        sld.polygon(hex_pts, fill=(*crystal_color, rng.randint(80, 160)))
        # Inner facet highlight
        inner = []
        for h in range(6):
            ha = angle + h * math.pi / 3
            hx = cx + math.cos(ha) * size * 0.4
            hy = cy + math.sin(ha) * size * 0.4
            inner.append((hx, hy))
        sld.polygon(inner, fill=(240, 238, 230, rng.randint(60, 100)))

    img = Image.alpha_composite(img, salt_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Dead Sea water ────────────────────────────────────────────────────
    water_y = horizon + 30
    for y in range(water_y, H):
        t = (y - water_y) / (H - water_y)
        r = int(40 + 15 * t)
        g = int(80 + 20 * t)
        b = int(100 + 30 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # Water ripple reflections (salt sheen)
    ripple_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rl = ImageDraw.Draw(ripple_layer)
    for ripple in range(25):
        rx = rng.randint(0, W)
        ry = water_y + rng.randint(0, 600)
        rw = rng.randint(40, 200)
        ra = rng.randint(10, 40)
        rl.ellipse((rx - rw, ry - 3, rx + rw, ry + 3),
                    fill=(200, 195, 180, ra))
    ripple_layer = ripple_layer.filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(img, ripple_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Research station (silhouette on shore, lit windows) ───────────────
    station_x = W // 2 + rng.randint(-20, 20)
    station_y = shore_y - 5

    # Main building
    station_w = 260
    station_h = 100
    draw.rectangle((station_x - station_w // 2, station_y - station_h,
                    station_x + station_w // 2, station_y),
                   fill=(25, 30, 35, 220))
    # Roof
    draw.rectangle((station_x - station_w // 2 - 10, station_y - station_h - 8,
                    station_x + station_w // 2 + 10, station_y - station_h),
                   fill=(30, 35, 40, 230))

    # Solar panels on roof
    for sp in range(3):
        spx = station_x - 80 + sp * 60
        draw.rectangle((spx, station_y - station_h - 15, spx + 40, station_y - station_h - 5),
                       fill=(60, 70, 90, 200))
        draw.line((spx + 20, station_y - station_h - 15, spx + 20, station_y - station_h - 5),
                  fill=(80, 90, 110, 150), width=1)

    # Antenna / instruments
    draw.line((station_x + 80, station_y - station_h, station_x + 80, station_y - station_h - 50),
              fill=(40, 45, 50, 200), width=3)
    # Anemometer
    draw.ellipse((station_x + 75, station_y - station_h - 60, station_x + 85, station_y - station_h - 50),
                 fill=(60, 65, 70, 200))
    draw.line((station_x + 80, station_y - station_h - 60, station_x + 90, station_y - station_h - 70),
              fill=(50, 55, 60, 180), width=2)
    draw.line((station_x + 80, station_y - station_h - 60, station_x + 70, station_y - station_h - 70),
              fill=(50, 55, 60, 180), width=2)

    # Lit windows (warm light — the people inside)
    for wx in range(3):
        for wy in range(2):
            win_x = station_x - 80 + wx * 60
            win_y = station_y - station_h + 20 + wy * 35
            win_w = 20
            win_h = 18
            glow_strength = rng.randint(40, 70)
            draw.rectangle((win_x, win_y, win_x + win_w, win_y + win_h),
                           fill=(255, 220, 140, glow_strength))
            # Inner glow
            draw.rectangle((win_x + 3, win_y + 3, win_x + win_w - 3, win_y + win_h - 3),
                           fill=(255, 235, 180, glow_strength + 30))

    # Warm window glow on ground
    glow_pool = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gpd = ImageDraw.Draw(glow_pool)
    gpd.ellipse((station_x - 100, station_y - 40, station_x + 100, station_y + 20),
                fill=(200, 180, 120, 30))
    img = Image.alpha_composite(img, glow_pool)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Scientific equipment near station ─────────────────────────────────
    # Buoy / sensor array on the water
    buoy_x = station_x + 350
    buoy_y = water_y + 80
    draw.ellipse((buoy_x - 12, buoy_y - 12, buoy_x + 12, buoy_y + 12),
                 fill=(60, 65, 70, 200))
    draw.ellipse((buoy_x - 6, buoy_y - 6, buoy_x + 6, buoy_y + 6),
                 fill=(200, 100, 50, 180))  # red sensor light
    draw.rectangle((buoy_x - 2, buoy_y - 25, buoy_x + 2, buoy_y - 12),
                   fill=(50, 55, 60, 200))
    # Sensor tether line
    draw.line((buoy_x, buoy_y + 12, buoy_x, buoy_y + 120),
              fill=(100, 110, 120, 80), width=1)
    # Floating sensor string
    for fs in range(4):
        fbx = buoy_x - 30 + fs * 20
        fby = buoy_y + 60 + fs * 15
        draw.ellipse((fbx - 4, fby - 4, fbx + 4, fby + 4),
                     fill=(50, 120, 140, 150))

    # ── The dock/pier ─────────────────────────────────────────────────────
    pier_x1 = station_x + 100
    pier_x2 = pier_x1 + 350
    pier_y = station_y + 10

    # Dock planks
    for plank in range(18):
        px = pier_x1 + plank * 20
        draw.rectangle((px, pier_y, px + 18, pier_y + 60),
                       fill=(60 + rng.randint(-5, 5), 55 + rng.randint(-5, 5), 50 + rng.randint(-5, 5), 220))
    # Dock posts
    for post in [pier_x1, pier_x1 + 80, pier_x1 + 170, pier_x1 + 260, pier_x2]:
        draw.rectangle((post - 3, pier_y - 15, post + 3, pier_y + 70),
                       fill=(40, 38, 35, 220))

    # Dock reflection in water
    dock_reflect = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    drd = ImageDraw.Draw(dock_reflect)
    for plank in range(18):
        px = pier_x1 + plank * 20
        drd.rectangle((px, pier_y + 62, px + 18, pier_y + 62 + (18 - plank) * 3),
                      fill=(30, 40, 55, 25))
    img = Image.alpha_composite(img, dock_reflect)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Two figures on the dock (Dr. Amira Hassan & Leo Castellano) ──────
    fig1_x = pier_x1 + 40   # Amira (left end)
    fig2_x = pier_x2 - 40   # Leo (right end)
    fig_y = pier_y - 30
    fig_scale = 1.0

    def draw_figure(d, fx, fy, scale, gender="f"):
        """Draw a stylized silhouette figure."""
        s = scale * 50
        # Head
        d.ellipse((fx - 7 * s / 50, fy - 22 * s / 50,
                   fx + 7 * s / 50, fy - 8 * s / 50),
                  fill=(15, 18, 22, 200))
        # Body
        d.line((fx, fy - 8 * s / 50, fx, fy + 12 * s / 50),
               fill=(15, 18, 22, 200), width=int(8 * scale))
        # Arms
        if gender == "f":
            # Arms crossed or holding a notebook
            d.line((fx, fy - 2 * s / 50, fx - 10 * s / 50, fy + 4 * s / 50),
                   fill=(15, 18, 22, 180), width=int(4 * scale))
            d.line((fx, fy - 2 * s / 50, fx + 10 * s / 50, fy + 4 * s / 50),
                   fill=(15, 18, 22, 180), width=int(4 * scale))
            # Hair (longer)
            d.ellipse((fx - 9 * s / 50, fy - 26 * s / 50,
                       fx + 9 * s / 50, fy - 16 * s / 50),
                      fill=(10, 12, 16, 200))
            # Skirt/pants hint
            d.line((fx - 4 * s / 50, fy + 12 * s / 50, fx - 6 * s / 50, fy + 22 * s / 50),
                   fill=(15, 18, 22, 180), width=int(4 * scale))
            d.line((fx + 4 * s / 50, fy + 12 * s / 50, fx + 6 * s / 50, fy + 22 * s / 50),
                   fill=(15, 18, 22, 180), width=int(4 * scale))
        else:
            # Arms at sides or in pockets
            d.line((fx, fy - 2 * s / 50, fx - 12 * s / 50, fy + 8 * s / 50),
                   fill=(15, 18, 22, 180), width=int(4 * scale))
            d.line((fx, fy - 2 * s / 50, fx + 12 * s / 50, fy + 8 * s / 50),
                   fill=(15, 18, 22, 180), width=int(4 * scale))
            # Broader shoulders
            d.line((fx - 6 * s / 50, fy - 6 * s / 50, fx + 6 * s / 50, fy - 6 * s / 50),
                   fill=(15, 18, 22, 200), width=int(5 * scale))
            # Legs
            d.line((fx - 3 * s / 50, fy + 12 * s / 50, fx - 5 * s / 50, fy + 25 * s / 50),
                   fill=(15, 18, 22, 180), width=int(4 * scale))
            d.line((fx + 3 * s / 50, fy + 12 * s / 50, fx + 5 * s / 50, fy + 25 * s / 50),
                   fill=(15, 18, 22, 180), width=int(4 * scale))

    draw_figure(draw, fig1_x, fig_y, fig_scale, "f")
    draw_figure(draw, fig2_x, fig_y, fig_scale, "m")

    # ── Chemistry particles between the two figures ───────────────────────
    # Glowing particles — the "chemistry" that pulls them together
    chem_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    chd = ImageDraw.Draw(chem_layer)

    # Particle stream connecting them
    for _ in range(80):
        t = rng.random()
        px = fig1_x + (fig2_x - fig1_x) * t + rng.randint(-30, 30)
        py = fig_y - 20 + math.sin(t * math.pi * 6) * 40 + rng.randint(-15, 15)
        pr = rng.randint(2, 6)
        # Warm golden particles (chemistry spark)
        p_alpha = int(80 * math.sin(t * math.pi) + rng.randint(0, 40))
        chd.ellipse((px - pr, py - pr, px + pr, py + pr),
                     fill=(255, 200 + rng.randint(-30, 30), 100 + rng.randint(-40, 40), max(10, min(200, p_alpha))))

    # Larger spark clusters
    for _ in range(15):
        cx = fig1_x + (fig2_x - fig1_x) * rng.random()
        cy = fig_y - 20 + rng.randint(-50, 50)
        cr = rng.randint(8, 20)
        chd.ellipse((cx - cr, cy - cr, cx + cr, cy + cr),
                     fill=(255, 200, 120, rng.randint(10, 30)))

    chem_layer = chem_layer.filter(ImageFilter.GaussianBlur(4))
    img = Image.alpha_composite(img, chem_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Sunset glow over the horizon ──────────────────────────────────────
    sun_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sgd = ImageDraw.Draw(sun_glow)
    # Sun glow behind mountains
    sgd.ellipse((W // 2 - 300, horizon - 200, W // 2 + 300, horizon + 100),
                fill=(255, 200, 100, 40))
    sgd.ellipse((W // 2 - 150, horizon - 120, W // 2 + 150, horizon + 50),
                fill=(255, 180, 80, 60))
    sun_glow = sun_glow.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, sun_glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Subtle sun disc (low on horizon, behind mountains)
    sun_disc = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sdd = ImageDraw.Draw(sun_disc)
    sdd.ellipse((W // 2 - 60, horizon - 80, W // 2 + 60, horizon + 20),
                fill=(255, 200, 120, 90))
    sun_disc = sun_disc.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, sun_disc)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Minutiae: seagull silhouettes (distant, migrating) ────────────────
    for _ in range(6):
        gx = rng.randint(100, W - 100)
        gy = rng.randint(100, horizon - 100)
        # Simple seagull "V" shape
        wing_span = rng.randint(30, 60)
        draw.arc((gx - wing_span // 2, gy - 6, gx, gy + 4), 0, 180,
                 fill=(30 + rng.randint(-10, 10), 30 + rng.randint(-10, 10), 35 + rng.randint(-10, 10), rng.randint(60, 120)),
                 width=2)
        draw.arc((gx, gy - 6, gx + wing_span // 2, gy + 4), 0, 180,
                 fill=(30 + rng.randint(-10, 10), 30 + rng.randint(-10, 10), 35 + rng.randint(-10, 10), rng.randint(60, 120)),
                 width=2)

    # ── Foreground salt details (macro crystals, bottom edge) ─────────────
    fore_salt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fsd = ImageDraw.Draw(fore_salt)
    for _ in range(20):
        fx = rng.randint(0, W)
        fy = H - rng.randint(50, 200)
        fsize = rng.randint(15, 40)
        fangle = rng.uniform(0, math.tau)
        fcol = (200 + rng.randint(-20, 20), 195 + rng.randint(-20, 20), 185 + rng.randint(-20, 20))
        # Crystal shape
        pts = []
        for h in range(6):
            ha = fangle + h * math.pi / 3
            hx = fx + math.cos(ha) * fsize
            hy = fy + math.sin(ha) * fsize * 0.6
            pts.append((hx, hy))
        fsd.polygon(pts, fill=(*fcol, rng.randint(60, 130)))
    img = Image.alpha_composite(img, fore_salt)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Vignette (subtle darkening at edges) ──────────────────────────────
    vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(50 * max(0, 1 - vt))
        if vv > 0:
            vd.line((0, vy, vv, vy), fill=(0, 0, 0, 80))
            vd.line((W - vv, vy, W, vy), fill=(0, 0, 0, 80))
    img = Image.alpha_composite(img, vig)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Save ──────────────────────────────────────────────────────────────
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
