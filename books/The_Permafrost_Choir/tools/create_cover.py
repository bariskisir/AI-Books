#!/usr/bin/env python3
"""Cover: The Permafrost Choir — Arctic Gothic horror: a climate research team drilling Siberian permafrost unearths frozen vocal cords whose hum compels listeners to sing their darkest secret before falling catatonic."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# The Permafrost Choir palette: arctic night, frozen soil, sickly hum-green, desiccated tissue
SKY_TOP = (8, 10, 28)           # arctic midnight
SKY_MID = (18, 22, 48)          # deep polar twilight
SKY_BOT = (30, 45, 65)          # icy horizon glow
PERMAFROST_UPPER = (60, 50, 40) # frozen soil crust
PERMAFROST_DEEP = (25, 18, 12)  # dark permafrost below
ICE_BLUE = (160, 210, 230)      # ice highlight
ICE_BLUE_DIM = (80, 140, 180)   # shadow ice
EERIE_HUM = (180, 210, 100)     # the hum's sickly yellow-green glow
EERIE_HUM_DIM = (100, 140, 60)  # dimmer hum
VOCAL_CORD = (190, 160, 130)    # desiccated tissue
VOCAL_CORD_DIM = (120, 95, 70)  # shadow on frozen tissue
DRILL_RIG = (40, 45, 55)        # equipment silhouette
DRILL_LIGHT = (80, 180, 255)    # cold LED on equipment
SNOW = (220, 230, 235)          # snow surface

rng = random.Random()
rng.seed(892347169)


def gaussian(x, mu, sigma):
    return math.exp(-((x - mu) ** 2) / (2 * sigma * sigma))


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), SKY_TOP + (255,))
    draw = ImageDraw.Draw(img, "RGBA")

    # SKY GRADIENT: arctic night to icy horizon
    horizon_y = 900
    for y in range(horizon_y + 100):
        t = y / (horizon_y + 100)
        if t < 0.5:
            lt = t / 0.5
            r = int(SKY_TOP[0] + (SKY_MID[0] - SKY_TOP[0]) * lt)
            g = int(SKY_TOP[1] + (SKY_MID[1] - SKY_TOP[1]) * lt)
            b = int(SKY_TOP[2] + (SKY_MID[2] - SKY_TOP[2]) * lt)
        else:
            lt = (t - 0.5) / 0.5
            r = int(SKY_MID[0] + (SKY_BOT[0] - SKY_MID[0]) * lt)
            g = int(SKY_MID[1] + (SKY_BOT[1] - SKY_MID[1]) * lt)
            b = int(SKY_MID[2] + (SKY_BOT[2] - SKY_MID[2]) * lt)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # AURORA BOREALIS: faint green ribbons across the arctic sky
    aurora = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ad = ImageDraw.Draw(aurora)
    for ribbon in range(5):
        ry_base = rng.randint(80, 400)
        r_amp = rng.randint(10, 40)
        r_freq = rng.uniform(0.002, 0.006)
        r_phase = rng.uniform(0, math.tau)
        r_alpha = rng.randint(15, 35)
        r_color = (rng.randint(80, 180), rng.randint(180, 240), rng.randint(80, 160))
        pts = []
        for rx in range(0, W + 10, 10):
            ry = ry_base + math.sin(rx * r_freq + r_phase) * r_amp + math.sin(rx * r_freq * 1.7 + r_phase * 0.4) * r_amp * 0.4
            pts.append((rx, ry))
        ad.line(pts, fill=r_color + (r_alpha,), width=rng.randint(2, 8))
    aurora = aurora.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img, aurora)
    draw = ImageDraw.Draw(img, "RGBA")

    # STARS over the arctic
    stars = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    std = ImageDraw.Draw(stars)
    for _ in range(200):
        sx = rng.randint(0, W)
        sy = rng.randint(0, horizon_y - 50)
        sr = rng.uniform(0.5, 2.0)
        sa = rng.randint(100, 200)
        std.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=(220, 230, 240, sa))
    img = Image.alpha_composite(img, stars)
    draw = ImageDraw.Draw(img, "RGBA")

    # ICE PLAIN / TUNDRA SURFACE: snow-covered frozen ground
    td = ImageDraw.Draw(img)
    td.rectangle((0, horizon_y, W, H), fill=(50, 55, 60, 255))
    for y in range(horizon_y, horizon_y + 80):
        t = (y - horizon_y) / 80
        r = int(50 + (PERMAFROST_UPPER[0] - 50) * t)
        g = int(55 + (PERMAFROST_UPPER[1] - 55) * t)
        b = int(60 + (PERMAFROST_UPPER[2] - 60) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # Snow surface texture (gentle drifts)
    for _ in range(200):
        sx = rng.randint(0, W)
        sy = rng.randint(horizon_y, horizon_y + 60)
        sr = rng.randint(1, 4)
        snow_shade = 20 + rng.randint(0, 20)
        draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=(snow_shade, snow_shade + 5, snow_shade + 10, rng.randint(30, 80)))

    # PERMAFROST EXCAVATION PIT: a cross-section cutaway in the lower half
    pit_left = 350
    pit_right = W - 350
    pit_top = 1200
    pit_bottom = H

    # Stratified permafrost layers in the pit wall
    for y in range(pit_top, pit_bottom):
        t = (y - pit_top) / (pit_bottom - pit_top)
        wf = 1 - 0.3 * t
        left_edge = int(W // 2 - (W // 2 - pit_left) * wf)
        right_edge = int(W // 2 + (pit_right - W // 2) * wf)

        if t < 0.15:
            c = (65, 55, 40)       # active layer / frozen peat
        elif t < 0.35:
            c = (50, 45, 55)       # icy silt
        elif t < 0.55:
            c = (40, 55, 70)       # ice-rich permafrost
        elif t < 0.75:
            c = (35, 30, 25)       # ancient organic permafrost
        else:
            c = (20, 15, 10)       # deep nearly black permafrost

        draw.line((left_edge, y, right_edge, y), fill=c + (255,))

    # Ice lenses (horizontal ice veins) in the permafrost wall
    ice_lenses = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ild = ImageDraw.Draw(ice_lenses)
    for _ in range(30):
        li_y = rng.randint(pit_top + 30, pit_bottom - 50)
        t_layer = (li_y - pit_top) / (pit_bottom - pit_top)
        wf = 1 - 0.3 * t_layer
        left_edge = int(W // 2 - (W // 2 - pit_left) * wf)
        right_edge = int(W // 2 + (pit_right - W // 2) * wf)
        lx = left_edge + rng.randint(20, max(20, right_edge - left_edge - 60))
        lw = rng.randint(30, 120)
        ly_y = li_y + rng.randint(-3, 3)
        ild.rectangle((lx, ly_y - 2, lx + lw, ly_y + 2), fill=ICE_BLUE + (rng.randint(40, 100),))
    ice_lenses = ice_lenses.filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(img, ice_lenses)
    draw = ImageDraw.Draw(img, "RGBA")

    # FROZEN VOCAL CORDS entombed in the permafrost layers — the central horror
    cords = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cords)

    vocal_cord_groups = [
        (500, 1400, 200, 180, 3),
        (700, 1550, 180, 160, 4),
        (550, 1650, 150, 140, 2),
        (750, 1420, 160, 150, 3),
        (600, 1720, 200, 120, 3),
        (480, 1580, 120, 130, 2),
        (820, 1600, 100, 110, 2),
    ]

    for gx, gy, gw, gh, count in vocal_cord_groups:
        for _ in range(count):
            cx = gx + rng.randint(0, gw)
            cy = gy + rng.randint(0, gh)

            fold_width = rng.randint(20, 45)
            fold_height = rng.randint(6, 14)
            cord_color = VOCAL_CORD + (rng.randint(180, 230),)
            cord_color_dim = VOCAL_CORD_DIM + (rng.randint(120, 180),)

            # Left vocal fold
            l_pts = []
            for step in range(8):
                st = step / 7
                lx = cx - int(st * fold_width)
                ly = cy + int(math.sin(st * math.pi) * fold_height * 0.5) - fold_height // 2
                l_pts.append((lx, ly))
            cd.line(l_pts, fill=cord_color, width=rng.randint(3, 5))

            # Right vocal fold (mirror)
            r_pts = []
            for step in range(8):
                st = step / 7
                rx = cx + int(st * fold_width)
                ry = cy + int(math.sin(st * math.pi) * fold_height * 0.5) - fold_height // 2
                r_pts.append((rx, ry))
            cd.line(r_pts, fill=cord_color, width=rng.randint(3, 5))

            # Connecting tissue
            conn_y = cy + fold_height // 2 - 2
            cd.line((cx - fold_width, conn_y, cx + fold_width, conn_y), fill=cord_color_dim, width=rng.randint(2, 4))

            # Eerie hum-glow around each cord
            for gr in range(4):
                ga = int(8 * (1 - gr / 4))
                gr_rad = 30 + gr * 12
                cd.ellipse((cx - gr_rad, cy - gr_rad, cx + gr_rad, cy + gr_rad), fill=EERIE_HUM_DIM + (ga,))

    img = Image.alpha_composite(img, cords)
    draw = ImageDraw.Draw(img, "RGBA")

    # ICE CRYSTALS in the pit walls
    crystals = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    xd = ImageDraw.Draw(crystals)
    for _ in range(60):
        cx = rng.randint(pit_left + 10, pit_right - 10)
        cy = rng.randint(pit_top + 20, pit_bottom - 20)
        cs = rng.randint(3, 10)
        ca = rng.randint(40, 130)
        xd.polygon(
            [
                (cx, cy - cs),
                (cx + cs * 0.6, cy - cs * 0.4),
                (cx + cs * 0.6, cy + cs * 0.4),
                (cx, cy + cs),
                (cx - cs * 0.6, cy + cs * 0.4),
                (cx - cs * 0.6, cy - cs * 0.4),
            ],
            fill=ICE_BLUE + (ca,),
            outline=ICE_BLUE_DIM + (ca + 20,),
        )
    img = Image.alpha_composite(img, crystals)
    draw = ImageDraw.Draw(img, "RGBA")

    # DRILLING RIG on the surface above the pit
    rig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rig)

    rig_ground = horizon_y + 10
    tower_cx = W // 2 - 100

    # Main derrick tower
    rd.rectangle((tower_cx - 30, rig_ground - 350, tower_cx + 30, rig_ground), fill=DRILL_RIG + (230,))
    for brace in range(5):
        by = rig_ground - brace * 70
        rd.line((tower_cx - 30, by, tower_cx + 30, by - 25), fill=(60, 65, 75, 200), width=2)
        rd.line((tower_cx + 30, by, tower_cx - 30, by - 25), fill=(60, 65, 75, 200), width=2)
    rd.rectangle((tower_cx - 25, rig_ground - 370, tower_cx + 25, rig_ground - 345), fill=(50, 55, 65, 200))

    # Drill pipe
    rd.rectangle((tower_cx - 5, rig_ground, tower_cx + 5, rig_ground + 300), fill=(45, 50, 60, 200))
    bit_y = rig_ground + 300
    rd.polygon([(tower_cx - 10, bit_y), (tower_cx + 10, bit_y), (tower_cx + 5, bit_y + 25), (tower_cx - 5, bit_y + 25)], fill=(55, 60, 70, 220))
    for tooth in range(3):
        tx = tower_cx - 6 + tooth * 6
        rd.polygon([(tx, bit_y + 25), (tx + 3, bit_y + 25), (tx + 1, bit_y + 32)], fill=(70, 75, 85, 220))

    # Support legs
    rd.line((tower_cx - 110, rig_ground - 40, tower_cx - 30, rig_ground - 250), fill=DRILL_RIG + (200,), width=4)
    rd.line((tower_cx + 110, rig_ground - 40, tower_cx + 30, rig_ground - 250), fill=DRILL_RIG + (200,), width=4)

    # Equipment shed / generator
    rd.rectangle((tower_cx + 80, rig_ground - 60, tower_cx + 190, rig_ground), fill=(35, 40, 50, 230))
    rd.rectangle((tower_cx + 85, rig_ground - 55, tower_cx + 100, rig_ground - 45), fill=DRILL_LIGHT + (60,))
    img = Image.alpha_composite(img, rig)

    # CAMP OUTBUILDINGS
    camp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(camp)
    buildings = [
        (W // 2 + 250, rig_ground - 40, 80, 40),
        (W // 2 + 360, rig_ground - 30, 60, 30),
        (W // 2 - 350, rig_ground - 35, 70, 35),
        (W // 2 - 260, rig_ground - 25, 50, 25),
    ]
    for bx, by, bw, bh in buildings:
        cd.rectangle((bx, by - bh, bx + bw, by), fill=(30, 33, 40, 230))
        cd.polygon([(bx - 5, by - bh), (bx + bw // 2, by - bh - 12), (bx + bw + 5, by - bh)], fill=(35, 38, 45, 230))
    cd.line((W // 2 + 380, rig_ground - 30, W // 2 + 383, rig_ground - 70), fill=(50, 55, 65, 180), width=2)
    img = Image.alpha_composite(img, camp)
    draw = ImageDraw.Draw(img, "RGBA")

    # RESEARCHER IN TRANCE near the pit edge, compelled by the hum
    figs = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(figs)

    figure_x = W // 2 + 180
    figure_y = rig_ground - 5
    figure_h = 160

    fd.polygon(
        [(figure_x - 18, figure_y - figure_h + 30), (figure_x + 18, figure_y - figure_h + 30),
         (figure_x + 22, figure_y - 5), (figure_x - 22, figure_y - 5)],
        fill=(5, 5, 10, 220),
    )
    fd.ellipse((figure_x - 10, figure_y - figure_h + 5, figure_x + 10, figure_y - figure_h + 30), fill=(5, 5, 10, 220))
    fd.line((figure_x + 18, figure_y - figure_h + 45, figure_x + 40, figure_y - figure_h + 15), fill=(5, 5, 10, 200), width=5)
    fd.line((figure_x - 18, figure_y - figure_h + 45, figure_x - 35, figure_y - figure_h + 20), fill=(5, 5, 10, 200), width=5)

    # Sound-wave arcs from the figure's head (the compulsion)
    for ring in range(4):
        ring_r = 20 + ring * 18
        ring_alpha = max(10, 50 - ring * 12)
        fd.arc((figure_x - ring_r, figure_y - figure_h - ring_r, figure_x + ring_r, figure_y - figure_h + ring_r),
               start=0, end=180, fill=EERIE_HUM + (ring_alpha,), width=2)

    img = Image.alpha_composite(img, figs)
    draw = ImageDraw.Draw(img, "RGBA")

    # THE HUM: visible sound waves radiating from the exposed vocal cords upward
    hum = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hum)
    for wave_set in range(8):
        w_origin_x = W // 2 + rng.randint(-150, 150)
        w_origin_y = rng.randint(1400, 1750)
        w_phase = rng.uniform(0, math.tau)
        w_amp = rng.randint(30, 80)
        w_freq = rng.uniform(0.02, 0.05)
        w_alpha = rng.randint(20, 50)
        w_color = EERIE_HUM + (w_alpha,)
        pts = []
        for wx in range(0, W + 20, 20):
            wy = w_origin_y + math.sin((wx - w_origin_x) * w_freq + w_phase) * w_amp
            pts.append((wx, wy))
        hd.line(pts, fill=w_color, width=rng.randint(2, 6))
        pts2 = []
        for wx in range(0, W + 20, 10):
            wy = w_origin_y - 30 + math.sin((wx - w_origin_x) * w_freq * 2.3 + w_phase * 1.5) * w_amp * 0.4
            pts2.append((wx, wy))
        hd.line(pts2, fill=EERIE_HUM_DIM + (w_alpha - 10,), width=rng.randint(1, 3))
    # Standing wave / Chladni resonance pattern
    for _ in range(12):
        sx = rng.randint(200, 1400)
        sy = rng.randint(600, 1200)
        sr = rng.randint(40, 120)
        hd.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), outline=EERIE_HUM_DIM + (rng.randint(8, 20),), width=1)
    hum = hum.filter(ImageFilter.GaussianBlur(6))
    img = Image.alpha_composite(img, hum)
    draw = ImageDraw.Draw(img, "RGBA")

    # EERIE GLOW rising from the pit (the source of the hum)
    pit_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pgd = ImageDraw.Draw(pit_glow)
    for rad in range(5, 200, 15):
        ga = max(2, 20 - rad // 10)
        pgd.ellipse((W // 2 - rad, 1500 - rad, W // 2 + rad, 1500 + rad), fill=EERIE_HUM + (ga,))
    for rad in range(10, 120, 10):
        ga = max(3, 15 - rad // 8)
        pgd.ellipse((W // 2 - rad, 1500 - rad, W // 2 + rad, 1500 + rad), fill=ICE_BLUE_DIM + (ga,))
    pit_glow = pit_glow.filter(ImageFilter.GaussianBlur(25))
    img = Image.alpha_composite(img, pit_glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # ATMOSPHERIC FOG over the permafrost
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fgd = ImageDraw.Draw(fog)
    for _ in range(12):
        fx = rng.randint(-50, W + 50)
        fy = rng.randint(horizon_y, 1600)
        fw = rng.randint(200, 600)
        fh = rng.randint(40, 100)
        fgd.ellipse((fx - fw // 2, fy, fx + fw // 2, fy + fh), fill=(80, 90, 100, rng.randint(6, 18)))
    fog = fog.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img, fog)

    # FROST PARTICLES (tiny ice crystals suspended in the air)
    frost = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(frost)
    for _ in range(120):
        px = rng.randint(0, W)
        py = rng.randint(0, H)
        pr = rng.uniform(0.5, 2.5)
        fd.ellipse((px - pr, py - pr, px + pr, py + pr), fill=ICE_BLUE + (rng.randint(30, 90),))
    img = Image.alpha_composite(img, frost)

    # VIGNETTE
    vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette)
    for vy in range(H):
        vh = 1 - gaussian(vy, H // 2, H * 0.45)
        dark = int(60 * vh)
        if dark > 0:
            vd.line((0, vy, min(dark, W), vy), fill=(0, 0, 0, 60))
            vd.line((max(W - dark, 0), vy, W, vy), fill=(0, 0, 0, 60))
    img = Image.alpha_composite(img, vignette)

    # Title panel via shared utility
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
