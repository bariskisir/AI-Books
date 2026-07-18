#!/usr/bin/env python3
"""Cover: What the Tides Forgot — A marine biologist returns to the Oregon coast tide pools that hold organisms defying known taxonomy and seeming to remember her."""
from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# Unique palette: Oregon coast night, dark tide pools, bioluminescent creatures, memory glow
SKY_TOP = (10, 12, 28)          # deep indigo night
SKY_BOT = (22, 48, 52)          # dark teal horizon
CLIFF_DARK = (12, 14, 16)       # near-black basalt
CLIFF_MID = (20, 22, 26)        # mid-dark rock
CLIFF_LIGHT = (35, 38, 42)      # lighter rock edge
POOL_DARK = (8, 35, 30)         # tide pool dark water
POOL_MID = (14, 60, 55)         # tide pool mid water
BIO_CYAN = (50, 230, 210)       # bioluminescent cyan
BIO_EMERALD = (80, 255, 170)    # bioluminescent green
BIO_WHITE = (190, 245, 255)     # eerie white-blue glow
BIO_AMBER = (255, 200, 80)      # rare amber bioluminescence
MEMORY_SHINE = (160, 220, 230)  # the "remembering" shimmer
FOG_COLOR = (170, 185, 195)     # sea mist
WINDOW_WARM = (230, 190, 100)   # house window glow
MOON_PALE = (200, 210, 220)     # moon behind mist
SAND_DARK = (30, 28, 25)        # wet sand

rng = random.Random()
rng.seed(987210543)


def gaussian(x, mu, sigma):
    return math.exp(-((x - mu) ** 2) / (2 * sigma * sigma))


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (*SKY_TOP, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Night sky gradient: deep indigo to teal horizon ──
    for y in range(H):
        t = y / H
        r = int(SKY_TOP[0] + (SKY_BOT[0] - SKY_TOP[0]) * t)
        g = int(SKY_TOP[1] + (SKY_BOT[1] - SKY_TOP[1]) * t)
        b = int(SKY_TOP[2] + (SKY_BOT[2] - SKY_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── Pale moon behind high mist ──
    moon = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(moon)
    md.ellipse((W - 420, 140, W - 180, 360), fill=(*MOON_PALE, 40))
    moon = moon.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(img, moon)

    # ── Distant headland silhouette (left) ──
    headland = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(headland)
    headland_pts = [(0, 900)]
    for hx in range(0, W, 8):
        t_frac = hx / W
        noise = math.sin(hx * 0.005) * 40 + math.sin(hx * 0.012) * 20 + math.sin(hx * 0.025) * 10
        headland_top = 600 + t_frac * 300 + noise
        if hx < 600:
            headland_top = 500 + math.sin(hx * 0.008) * 60 + noise * 0.5
        if hx > 1200:
            headland_top = 750 + (hx - 1200) * 0.3 + noise * 0.3
        headland_pts.append((hx, headland_top))
    headland_pts.append((W, 1800))
    headland_pts.append((0, 1800))
    hd.polygon(headland_pts, fill=(*CLIFF_MID, 220))
    img = Image.alpha_composite(img, headland)

    # ── Near cliff face (right, foreground) with tide pools at base ──
    cliff = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cliff)
    # Main cliff shape
    cliff_pts = [(600, 1200)]
    for cx in range(600, W + 8, 8):
        cf = (cx - 600) / (W - 600)
        c_noise = math.sin(cx * 0.007) * 80 + math.sin(cx * 0.018) * 40 + math.sin(cx * 0.035) * 20
        c_top = 1100 + cf * 300 + c_noise
        cliff_pts.append((cx, c_top))
    cliff_pts.append((W, 2000))
    cliff_pts.append((600, 2000))
    cd.polygon(cliff_pts, fill=(*CLIFF_DARK, 240))
    # Cliff texture - rock strata lines
    for cy in range(1100, 1800, 40):
        stratum_pts = []
        for cx in range(600, W, 6):
            cf = (cx - 600) / (W - 600)
            offset = math.sin(cx * 0.015 + cy * 0.02) * 15 + math.sin(cx * 0.04) * 5
            stratum_pts.append((cx, cy + offset))
        cd.line(stratum_pts, fill=(*CLIFF_LIGHT, 30), width=2)
    img = Image.alpha_composite(img, cliff)

    # ── The house on the cliff (left middle distance) ──
    house = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hld = ImageDraw.Draw(house)
    # House body (gabled roof shape)
    hx, hy = 250, 780
    house_w, house_h = 140, 100
    hld.rectangle((hx, hy, hx + house_w, hy + house_h), fill=(*CLIFF_MID, 230))
    # Roof
    hld.polygon([
        (hx - 12, hy),
        (hx + house_w // 2, hy - 50),
        (hx + house_w + 12, hy),
    ], fill=(*CLIFF_DARK, 240))
    # Lit window
    win_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wgd = ImageDraw.Draw(win_glow)
    wgd.rectangle((hx + 20, hy + 25, hx + 55, hy + 75), fill=(*WINDOW_WARM, 200))
    wgd.rectangle((hx + 75, hy + 25, hx + 110, hy + 75), fill=(*WINDOW_WARM, 180))
    # Window glow spill
    for gr in range(60, 200, 20):
        alpha_gr = max(5, 30 - gr // 8)
        wgd.ellipse((hx + 20 - gr, hy + 25 - gr, hx + 55 + gr, hy + 75 + gr), fill=(*WINDOW_WARM, alpha_gr))
    win_glow = win_glow.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img, win_glow)
    img = Image.alpha_composite(img, house)

    # ── Tide pools in the foreground ──
    pools = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pools)

    # Define pool shapes as polygons (organic, irregular)
    pool_defs = [
        # (center_x, center_y, radius_x, radius_y, rotation_offset)
        (300, 1700, 180, 80, 0),
        (550, 1850, 140, 70, 0.5),
        (800, 1750, 200, 90, 1.0),
        (1050, 1900, 160, 75, 1.5),
        (1300, 1800, 190, 85, 2.0),
        (200, 2000, 150, 65, 0.8),
        (700, 2000, 180, 80, 1.2),
        (1150, 2050, 170, 75, 0.3),
        (1450, 1950, 140, 60, 1.8),
    ]

    for pool_cx, pool_cy, rx, ry, rot in pool_defs:
        pool_pts = []
        n_segments = rng.randint(14, 22)
        for i in range(n_segments):
            angle = (math.tau * i / n_segments) + rot
            # Irregular radius
            noise_r = 0.75 + rng.random() * 0.5
            noise_r *= 1.0 + 0.15 * math.sin(angle * 3 + rot * 2)
            noise_r *= 1.0 + 0.1 * math.cos(angle * 5 - rot)
            px = pool_cx + math.cos(angle) * rx * noise_r
            py = pool_cy + math.sin(angle) * ry * noise_r * 0.6
            pool_pts.append((px, py))
        # Draw pool water
        pool_shade = (
            int(POOL_DARK[0] + rng.randint(0, 8)),
            int(POOL_DARK[1] + rng.randint(10, 30)),
            int(POOL_DARK[2] + rng.randint(0, 15)),
        )
        pd.polygon(pool_pts, fill=(*pool_shade, 230))
        # Pool edge highlight (rock rim)
        pd.polygon(pool_pts, outline=(*CLIFF_LIGHT, 120), width=3)

    # ── Wet sand / rock between pools ──
    for _ in range(100):
        sx = rng.randint(0, W)
        sy = rng.randint(1550, 2200)
        sr = rng.randint(10, 50)
        sand_shade = (
            int(SAND_DARK[0] + rng.randint(-5, 10)),
            int(SAND_DARK[1] + rng.randint(-5, 10)),
            int(SAND_DARK[2] + rng.randint(-5, 10)),
        )
        pd.ellipse((sx - sr, sy - sr // 2, sx + sr, sy + sr // 2), fill=(*sand_shade, 180))

    # ── Small rock scatter ──
    for _ in range(40):
        rx_day = rng.randint(50, W - 50)
        ry_day = rng.randint(1450, 2150)
        rr = rng.randint(8, 30)
        rock_shade = (
            rng.randint(15, 35),
            rng.randint(15, 35),
            rng.randint(18, 38),
        )
        pd.ellipse((rx_day - rr, ry_day - rr // 2, rx_day + rr, ry_day + rr // 2), fill=(*rock_shade, 220))

    img = Image.alpha_composite(img, pools)
    pd = ImageDraw.Draw(img, "RGBA")

    # ── Bioluminescent organisms in the tide pools ──
    # Each organism type: clustered dots, trailing filaments, or pulsing cores

    # Type 1: Clustered bioluminescent dots (like glowing anemones)
    cluster_centers = []
    for _ in range(35):
        cluster_cx = rng.randint(100, W - 100)
        cluster_cy = rng.randint(1650, 2150)
        cluster_centers.append((cluster_cx, cluster_cy))

    for cx, cy in cluster_centers:
        # Each cluster has 3-12 glowing dots
        num_dots = rng.randint(3, 12)
        bio_color = rng.choice([BIO_CYAN, BIO_EMERALD, BIO_WHITE, BIO_AMBER])
        for _ in range(num_dots):
            dx = cx + rng.gauss(0, 18)
            dy = cy + rng.gauss(0, 12)
            dot_r = rng.randint(2, 8)
            dot_alpha = rng.randint(100, 220)
            # Glow halo
            pd.ellipse(
                (dx - dot_r * 3, dy - dot_r * 3, dx + dot_r * 3, dy + dot_r * 3),
                fill=(*bio_color, dot_alpha // 6),
            )
            # Core
            pd.ellipse(
                (dx - dot_r, dy - dot_r, dx + dot_r, dy + dot_r),
                fill=(*bio_color, dot_alpha),
            )

    # Type 2: Trailing filaments (like bioluminescent tentacles or algal threads)
    for _ in range(18):
        fx = rng.randint(100, W - 100)
        fy = rng.randint(1650, 2150)
        f_len = rng.randint(30, 120)
        f_color = rng.choice([BIO_CYAN, BIO_EMERALD])
        f_pts = [(fx, fy)]
        for fi in range(f_len):
            f_pts.append((
                f_pts[-1][0] + rng.gauss(0, 5),
                f_pts[-1][1] + rng.gauss(2, 3),
            ))
        f_alpha = rng.randint(40, 120)
        pd.line(f_pts, fill=(*f_color, f_alpha), width=rng.randint(1, 3))

    # Type 3: "Remembering" shimmer — concentric rings emanating from some organisms
    for _ in range(8):
        rx_s = rng.randint(150, W - 150)
        ry_s = rng.randint(1680, 2100)
        for ri in range(3):
            ring_r = 20 + ri * 25 + rng.randint(0, 15)
            ring_alpha = max(5, 60 - ri * 18)
            pd.ellipse(
                (rx_s - ring_r, ry_s - ring_r, rx_s + ring_r, ry_s + ring_r),
                outline=(*MEMORY_SHINE, ring_alpha),
                width=2,
            )

    # Type 4: Floating bioluminescent motes rising from pools
    for _ in range(60):
        mx = rng.randint(50, W - 50)
        my = rng.randint(1200, 1700)
        mr = rng.randint(1, 4)
        m_alpha = rng.randint(15, 60)
        m_color = rng.choice([BIO_CYAN, BIO_WHITE])
        pd.ellipse(
            (mx - mr, my - mr, mx + mr, my + mr),
            fill=(*m_color, m_alpha),
        )

    # ── Fog/mist layers ──
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog)

    for _ in range(15):
        fog_y = rng.randint(300, 1800)
        fog_w = rng.randint(400, 1200)
        fog_x = rng.randint(-200, W - fog_w + 200)
        fog_alpha = rng.randint(5, 18)
        fd.ellipse(
            (fog_x - fog_w // 2, fog_y - 30, fog_x + fog_w // 2, fog_y + 30),
            fill=(*FOG_COLOR, fog_alpha),
        )

    # Mist bank at horizon
    fd.ellipse((-300, 900, W + 300, 1100), fill=(*FOG_COLOR, 12))
    fd.ellipse((-200, 1000, W + 200, 1250), fill=(*FOG_COLOR, 15))

    fog = fog.filter(ImageFilter.GaussianBlur(35))
    img = Image.alpha_composite(img, fog)

    # ── Subtle vignette ──
    vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette)
    for vy in range(H):
        vh = 1 - gaussian(vy, H // 2, H * 0.45)
        dark = int(50 * vh)
        if dark > 0:
            vd.line((0, vy, min(dark, W), vy), fill=(0, 0, 0, 70))
            vd.line((max(W - dark, 0), vy, W, vy), fill=(0, 0, 0, 70))
    vd.rectangle((0, 0, W, H), fill=(0, 0, 0, 25))
    img = Image.alpha_composite(img, vignette)

    # ── Final draw ──
    draw = ImageDraw.Draw(img, "RGBA")

    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, title, author, model)
    img.convert("RGB").save(op, "PNG", optimize=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    make_cover(
        ROOT / a.metadata if not a.metadata.is_absolute() else a.metadata,
        ROOT / a.out if not a.out.is_absolute() else a.out,
    )


if __name__ == "__main__":
    main()
