#!/usr/bin/env python3
"""Cover: A Map of Every Mourning — coastal Andalusian town where grief manifests as visible weather above each resident."""

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
rng.seed(2048197365)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (160, 180, 210, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Mediterranean sky gradient (warm horizon, deep blue upper) ──
    for y in range(H):
        t = y / H
        r = int(160 + (220 - 160) * max(0, 1 - t * 1.5))
        g = int(180 + (190 - 180) * max(0, 1 - t * 1.5))
        b = int(210 + (170 - 210) * max(0, 1 - t * 1.5))
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── Distant sea ──
    sea_y = 450
    for y in range(sea_y, sea_y + 80):
        t = (y - sea_y) / 80
        sb = int(140 + (100 - 140) * t)
        draw.line((0, y, W, y), fill=(80, 140, sb, 255))

    # ── Hillside with whitewashed Andalusian buildings ──
    # Build a silhouette layer for the town
    town = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(town)

    # Hillside contour
    hill_base = 1750
    hill_pts = []
    for x in range(0, W + 2, 4):
        h = math.sin(x * 0.003 + 0.5) * 60 + math.sin(x * 0.007) * 30 + math.sin(x * 0.015) * 15
        hill_pts.append((x, hill_base + int(h)))
    td.polygon([(0, H), *hill_pts, (W, H)], fill=(170, 140, 90, 255))

    # White buildings clustered on the hillside
    building_data = []
    clusters = [
        (250, 1350, 12), (500, 1300, 10), (700, 1280, 8),
        (900, 1320, 9), (1100, 1340, 11), (1300, 1370, 7),
        (400, 1420, 6), (800, 1400, 7), (1050, 1430, 5),
    ]
    for cx, cy, count in clusters:
        for _ in range(count):
            bw = rng.randint(40, 80)
            bh = rng.randint(60, 130)
            bx = cx + rng.randint(-60, 60)
            by = cy + rng.randint(-40, 40)
            # Clip to hillside
            hill_h = math.sin((bx) * 0.003 + 0.5) * 60 + math.sin((bx) * 0.007) * 30 + math.sin((bx) * 0.015) * 15
            hill_top = hill_base + int(hill_h)
            if by + bh > hill_top:
                bh = hill_top - by
            if bh < 20:
                continue
            # White wall with slight warm shading
            shade = rng.randint(-15, 15)
            wall = (230 + shade, 215 + shade, 185 + shade)
            td.rectangle((bx, by, bx + bw, by + bh), fill=(*wall, 240))
            # Terracotta roof
            roof_h = rng.randint(12, 22)
            td.polygon([(bx - 4, by), (bx + bw // 2, by - roof_h), (bx + bw + 4, by)],
                        fill=(160 + rng.randint(-20, 20), 80 + rng.randint(-10, 10), 50 + rng.randint(-10, 10), 240))
            # Windows
            for _ in range(rng.randint(1, 3)):
                wx = bx + rng.randint(6, bw - 14)
                wy = by + rng.randint(10, bh - 20)
                ws = rng.randint(6, 12)
                td.rectangle((wx, wy, wx + ws, wy + ws), fill=(50, 40, 35, rng.randint(120, 200)))
            building_data.append((bx, by, bx + bw, by + bh))

    # Church tower (campanile) — landmark
    tower_x = 600
    tower_y = 1190
    td.rectangle((tower_x - 25, tower_y, tower_x + 25, tower_y + 160), fill=(240, 225, 195, 240))
    td.polygon([(tower_x - 30, tower_y), (tower_x + 30, tower_y), (tower_x, tower_y - 35)],
                fill=(170, 85, 55, 240))
    # Church bell window
    td.rectangle((tower_x - 12, tower_y + 20, tower_x + 12, tower_y + 45), fill=(40, 35, 30, 180))
    td.rectangle((tower_x - 12, tower_y + 55, tower_x + 12, tower_y + 80), fill=(40, 35, 30, 150))

    img = Image.alpha_composite(img, town)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── LUCIA'S DROUGHT (left side) — cracked earth, heat haze, oppressive sun ──
    # Cracked earth patches on the ground
    for _ in range(rng.randint(40, 70)):
        cx = rng.randint(50, 550)
        cy = rng.randint(1550, 1800)
        # Crack lines
        for _ in range(rng.randint(3, 6)):
            ox = cx + rng.randint(-30, 30)
            oy = cy + rng.randint(-30, 30)
            ex = ox + rng.randint(-20, 20)
            ey = oy + rng.randint(-10, 10)
            draw.line((ox, oy, ex, ey), fill=(130, 90, 50, rng.randint(60, 120)), width=rng.randint(1, 2))

    # Heat haze shimmer lines
    haze_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(haze_layer)
    for _ in range(rng.randint(8, 14)):
        hx = rng.randint(100, 500)
        hy = rng.randint(800, 1400)
        hw = rng.randint(80, 200)
        for li in range(rng.randint(3, 5)):
            hd.line((hx - hw // 2 + li * (hw // 5), hy + li * 4,
                      hx + hw // 2 - li * (hw // 5), hy + li * 4),
                     fill=(200, 180, 140, rng.randint(8, 20)), width=rng.randint(1, 2))
    haze_layer = haze_layer.filter(ImageFilter.GaussianBlur(6))
    img = Image.alpha_composite(img, haze_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # Harsh sun (Lucia's drought) — upper left
    sun_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sun_layer)
    for radius in range(60, 0, -3):
        alpha = int(200 * (1 - radius / 60))
        sd.ellipse((200 - radius, 120 - radius, 200 + radius, 120 + radius),
                    fill=(255, 220, 140, alpha))
    sun_layer = sun_layer.filter(ImageFilter.GaussianBlur(12))
    img = Image.alpha_composite(img, sun_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── SANTIAGO'S HURRICANE (right side) — swirling spiral of dark clouds ──
    storm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    std = ImageDraw.Draw(storm)

    storm_cx, storm_cy = 1200, 600
    # Spiral arms
    for arm in range(6):
        angle_offset = arm * math.tau / 6
        for r in range(20, 260, 8):
            angle = angle_offset + r * 0.04
            sx = storm_cx + math.cos(angle) * r
            sy = storm_cy + math.sin(angle) * r * 0.6  # flatten vertically
            sw = rng.randint(6, 18)
            alpha = int(max(0, min(120, 140 - r * 0.3)))
            gray = rng.randint(30, 80)
            std.ellipse((sx - sw, sy - sw * 0.6, sx + sw, sy + sw * 0.6),
                         fill=(gray, gray - 10, gray - 5, alpha))

    # Dark core
    std.ellipse((storm_cx - 80, storm_cy - 60, storm_cx + 80, storm_cy + 60),
                 fill=(20, 18, 22, 140))
    # Eye
    std.ellipse((storm_cx - 25, storm_cy - 20, storm_cx + 25, storm_cy + 20),
                 fill=(160, 170, 180, 100))

    storm = storm.filter(ImageFilter.GaussianBlur(6))
    img = Image.alpha_composite(img, storm)
    draw = ImageDraw.Draw(img, "RGBA")

    # Lightning bolt from the hurricane
    lx = 1150
    ly = 480
    for _ in range(rng.randint(1, 3)):
        pts = [(lx + rng.randint(-20, 20), ly)]
        for seg in range(1, rng.randint(4, 7)):
            pts.append((lx + rng.randint(-40, 40), ly + seg * rng.randint(30, 60)))
        draw.line(pts, fill=(200, 210, 255, rng.randint(80, 150)), width=rng.randint(2, 4))

    # ── ABUELA PAZ'S MIST (center) — soft fog of patient grief ──
    mist = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(mist)
    for _ in range(rng.randint(6, 10)):
        mx = rng.randint(550, 850)
        my = rng.randint(900, 1200)
        mr = rng.randint(80, 180)
        mg = 180 + rng.randint(-20, 20)
        md.ellipse((mx - mr, my - mr * 0.4, mx + mr, my + mr * 0.4),
                    fill=(mg, mg - 10, mg - 20, rng.randint(12, 30)))
    mist = mist.filter(ImageFilter.GaussianBlur(20))
    img = Image.alpha_composite(img, mist)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── RAFAEL'S MEMORY RAIN (deceased husband) — ghostly rain over the town ──
    rain_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rain_layer)
    for _ in range(rng.randint(80, 130)):
        rx = rng.randint(350, 850)
        ry = rng.randint(200, 1600)
        rl = rng.randint(15, 40)
        rd.line((rx, ry, rx - 2, ry + rl),
                 fill=(180, 200, 220, rng.randint(5, 18)), width=rng.randint(1, 2))
    rain_layer = rain_layer.filter(ImageFilter.GaussianBlur(2))
    img = Image.alpha_composite(img, rain_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Weather map lines — represent the "map" of every mourning ──
    # Isobar-like contour lines showing different weather zones
    for ci in range(rng.randint(4, 7)):
        isobar_color = (rng.randint(60, 100), rng.randint(60, 100), rng.randint(80, 130))
        pts = []
        for x in range(-50, W + 50, 10):
            y = 900 + math.sin(x * 0.004 + ci * 2.1) * 80 + math.sin(x * 0.009 + ci * 1.3) * 40 + math.sin(x * 0.02 + ci * 0.7) * 20
            pts.append((x, y))
        draw.line(pts, fill=(*isobar_color, rng.randint(15, 35)), width=rng.randint(1, 2))

    # ── Foreground: dry cracked ground blending into healthy earth ──
    # Transition from drought (left) to fertile (right)
    ground = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(ground)
    # Left side: cracked dry
    for x in range(0, 500, rng.randint(8, 16)):
        gy = H - rng.randint(0, 200)
        gd.line((x, gy, x + rng.randint(4, 12), gy + rng.randint(2, 8)),
                 fill=(160, 120, 70, rng.randint(40, 80)), width=1)
    # Right side: hints of green returning
    for _ in range(rng.randint(15, 30)):
        gx = rng.randint(1100, 1550)
        gy = H - rng.randint(50, 250)
        gd.ellipse((gx - rng.randint(3, 8), gy - rng.randint(3, 8),
                     gx + rng.randint(3, 8), gy + rng.randint(3, 8)),
                    fill=(60 + rng.randint(-10, 10), 110 + rng.randint(-10, 10), 50 + rng.randint(-10, 10), rng.randint(60, 120)))
    img = Image.alpha_composite(img, ground)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Subtle gold light bridge between the drought and the hurricane ──
    # The "connection" Lucia seeks
    bridge = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bridge)
    for t_val in range(0, 100, 2):
        tt = t_val / 100
        bx = int(300 + tt * 900)
        by = int(400 + math.sin(tt * math.pi) * 200)
        br = rng.randint(4, 8)
        bd.ellipse((bx - br, by - br, bx + br, by + br),
                    fill=(220, 200, 120, rng.randint(8, 18)))
    bridge = bridge.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img, bridge)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Scattered wildflowers on the healthy side ──
    for _ in range(rng.randint(20, 40)):
        fx = rng.randint(1000, 1550)
        fy = rng.randint(1500, 1900)
        fc = rng.choice([(200, 80, 60), (220, 180, 80), (180, 60, 120), (240, 200, 180)])
        draw.ellipse((fx - 3, fy - 3, fx + 3, fy + 3), fill=(*fc, rng.randint(60, 140)))

    # ── Final atmosphere: vignette framing ──
    vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette)
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(35 * max(0, 1 - vt))
        if vv > 0:
            vd.line((0, vy, vv, vy), fill=(0, 0, 0, 100))
            vd.line((W - vv, vy, W, vy), fill=(0, 0, 0, 100))
    img = Image.alpha_composite(img, vignette)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Title panel ──
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
