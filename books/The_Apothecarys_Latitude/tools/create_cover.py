#!/usr/bin/env python3
"""Cover: The Apothecary's Latitude — 1764 naval surgeon strands ship on unmapped Pacific island seeking a scurvy cure; tropical flora, sunset sea, ship silhouette."""

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
rng.seed(184729651)

# ── Tropical Island palette: sunset golds, deep foliage greens, teal sea ──
SKY_TOP = (180, 140, 70)
SKY_MID = (220, 180, 110)
SKY_BOT = (250, 215, 165)
SEA_DEEP = (20, 105, 130)
SEA_MID = (40, 155, 175)
SEA_SHALLOW = (70, 195, 200)
SAND = (205, 180, 135)
FOL_DARK = (18, 42, 12)
FOL_MID = (40, 78, 30)
FOL_LIGHT = (65, 115, 42)
PALM_TRUNK = (65, 45, 28)
SHIP_HULL = (20, 22, 28)
FLOWER_RED = (215, 70, 50)
FLOWER_ORANGE = (240, 150, 40)
PLANT_DRAW = (85, 55, 40)
SUN_COL = (255, 200, 100)


def gauss(x, mu, sigma):
    return math.exp(-((x - mu) ** 2) / (2 * sigma * sigma))


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), SKY_TOP + (255,))
    draw = ImageDraw.Draw(img, "RGBA")

    # ──────────────────────────────────────────────
    # 1. SKY GRADIENT — warm sunset
    # ──────────────────────────────────────────────
    for y in range(520):
        t = y / 520
        if t < 0.5:
            t2 = t * 2
            r = int(SKY_TOP[0] + (SKY_MID[0] - SKY_TOP[0]) * t2)
            g = int(SKY_TOP[1] + (SKY_MID[1] - SKY_TOP[1]) * t2)
            b = int(SKY_TOP[2] + (SKY_MID[2] - SKY_TOP[2]) * t2)
        else:
            t2 = (t - 0.5) * 2
            r = int(SKY_MID[0] + (SKY_BOT[0] - SKY_MID[0]) * t2)
            g = int(SKY_MID[1] + (SKY_BOT[1] - SKY_MID[1]) * t2)
            b = int(SKY_MID[2] + (SKY_BOT[2] - SKY_MID[2]) * t2)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ──────────────────────────────────────────────
    # 2. SUN — large warm glow with corona rings
    # ──────────────────────────────────────────────
    sun_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sun_layer)
    for ring in range(80, 0, -2):
        a = int(18 * (1 - ring / 80))
        sd.ellipse(
            (W // 2 - ring * 3, 370 - ring * 2, W // 2 + ring * 3, 370 + ring * 2),
            fill=(255, 220, 140, a),
        )
    sun_layer = sun_layer.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(img, sun_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    sun_core = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    scd = ImageDraw.Draw(sun_core)
    scd.ellipse((W // 2 - 55, 345, W // 2 + 55, 395), fill=(255, 210, 110, 220))
    sun_core = sun_core.filter(ImageFilter.GaussianBlur(12))
    img = Image.alpha_composite(img, sun_core)
    draw = ImageDraw.Draw(img, "RGBA")

    # Sun reflection path on water
    refl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(refl)
    for ri in range(40):
        rx = W // 2 + int(ri * 4 * math.sin(ri * 0.3))
        rw = max(2, 40 - ri)
        ra = max(5, 80 - ri * 2)
        rd.ellipse((rx - rw, 520 + ri * 18, rx + rw, 520 + ri * 18 + 6), fill=(255, 200, 100, ra))
    img = Image.alpha_composite(img, refl)
    draw = ImageDraw.Draw(img, "RGBA")

    # ──────────────────────────────────────────────
    # 3. DISTANT VOLCANIC ISLAND silhouette
    # ──────────────────────────────────────────────
    island = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    id_ = ImageDraw.Draw(island)
    id_.polygon([
        (200, 510), (350, 360), (480, 290), (550, 270),
        (620, 280), (720, 310), (850, 340), (1120, 510),
    ], fill=(35, 45, 50, 220))
    id_.polygon([
        (480, 290), (550, 270), (620, 280), (580, 305),
    ], fill=(55, 68, 72, 120))
    img = Image.alpha_composite(img, island)
    draw = ImageDraw.Draw(img, "RGBA")

    # ──────────────────────────────────────────────
    # 4. OCEAN — deep to shallow gradient
    # ──────────────────────────────────────────────
    for y in range(510, 1400):
        t = (y - 510) / 890
        r = int(SEA_DEEP[0] + (SEA_SHALLOW[0] - SEA_DEEP[0]) * t)
        g = int(SEA_DEEP[1] + (SEA_SHALLOW[1] - SEA_DEEP[1]) * t)
        b = int(SEA_DEEP[2] + (SEA_SHALLOW[2] - SEA_DEEP[2]) * t)
        shimmer = 0
        if rng.random() < 0.008:
            shimmer = 20
        draw.line((0, y, W, y), fill=(min(r + shimmer, 255), min(g + shimmer, 255), min(b + shimmer, 255), 255))

    # ──────────────────────────────────────────────
    # 5. OCEAN WAVES
    # ──────────────────────────────────────────────
    for wi in range(10):
        amp = rng.randint(6, 20)
        freq = rng.uniform(0.003, 0.012)
        phase = rng.uniform(0, math.tau)
        y_base = rng.randint(520, 1100)
        pts = []
        for wx in range(0, W + 5, 6):
            wy = y_base + math.sin(wx * freq + phase) * amp + math.sin(wx * freq * 2.3 + phase * 0.6) * amp * 0.25
            pts.append((wx, wy))
        wcol = (
            rng.randint(90, 170),
            rng.randint(190, 240),
            rng.randint(220, 255),
        )
        draw.line(pts, fill=(*wcol, rng.randint(30, 70)), width=rng.randint(2, 4))

    # ──────────────────────────────────────────────
    # 6. SAILING SHIP (brigantine silhouette)
    # ──────────────────────────────────────────────
    ship = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shd = ImageDraw.Draw(ship)
    sx, sy = 1050, 465
    # Hull
    shd.polygon([
        (sx - 110, sy + 15), (sx + 90, sy + 15),
        (sx + 65, sy + 38), (sx - 85, sy + 38),
    ], fill=SHIP_HULL + (220,))
    shd.polygon([
        (sx - 105, sy + 15), (sx + 85, sy + 15),
        (sx + 75, sy + 22), (sx - 95, sy + 22),
    ], fill=(40, 35, 30, 200))
    # Bowsprit
    shd.line((sx + 90, sy + 10, sx + 130, sy - 10), fill=SHIP_HULL + (200,), width=3)
    # Masts
    shd.line((sx - 45, sy + 15, sx - 45, sy - 110), fill=SHIP_HULL + (220,), width=4)
    shd.line((sx + 25, sy + 15, sx + 25, sy - 90), fill=SHIP_HULL + (220,), width=3)
    shd.line((sx + 65, sy + 15, sx + 65, sy - 60), fill=SHIP_HULL + (220,), width=2)
    # Sails (square rig)
    # Mainmast sails
    shd.polygon([
        (sx - 48, sy - 25), (sx + 0, sy - 95),
        (sx + 0, sy - 20),
    ], fill=SHIP_HULL + (180,))
    shd.polygon([
        (sx - 46, sy + 0), (sx + 2, sy - 18),
        (sx + 2, sy + 10),
    ], fill=SHIP_HULL + (160,))
    # Foremast sails
    shd.polygon([
        (sx + 22, sy - 20), (sx + 50, sy - 78),
        (sx + 50, sy - 10),
    ], fill=SHIP_HULL + (180,))
    shd.polygon([
        (sx + 23, sy + 2), (sx + 48, sy - 8),
        (sx + 48, sy + 12),
    ], fill=SHIP_HULL + (160,))
    # Mizzen
    shd.polygon([
        (sx + 62, sy - 10), (sx + 85, sy - 50),
        (sx + 85, sy - 2),
    ], fill=SHIP_HULL + (170,))
    # Pennant
    shd.line((sx + 25, sy - 90, sx + 50, sy - 105), fill=(170, 45, 40, 200), width=3)
    shd.line((sx + 50, sy - 105, sx + 45, sy - 98), fill=(170, 45, 40, 150), width=2)
    img = Image.alpha_composite(img, ship)
    draw = ImageDraw.Draw(img, "RGBA")

    # ──────────────────────────────────────────────
    # 7. BEACH
    # ──────────────────────────────────────────────
    for y in range(1200, 1600):
        t = (y - 1200) / 400
        # Dune undulation
        dune = math.sin(y * 0.02) * 0.1 + 0.9
        r = int(SEA_SHALLOW[0] * (1 - t) + SAND[0] * t * dune)
        g = int(SEA_SHALLOW[1] * (1 - t) + SAND[1] * t * dune)
        b = int(SEA_SHALLOW[2] * (1 - t) + SAND[2] * t * dune)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ──────────────────────────────────────────────
    # 8. FOREGROUND: DENSE TROPICAL FOLIAGE (frame)
    # ──────────────────────────────────────────────
    foliage = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(foliage)
    leaf_cols = [FOL_DARK, FOL_MID, FOL_LIGHT, (32, 60, 24), (50, 90, 35)]

    # --- Left-side large leaves (monstera / palm) ---
    for li in range(14):
        lx = rng.randint(-60, 150)
        ly = rng.randint(150, 2200)
        lw = rng.randint(140, 350)
        lh = rng.randint(100, 220)
        lcol = rng.choice(leaf_cols)
        alpha = rng.randint(210, 250)
        # Main leaf body
        fd.ellipse((lx - lw // 2, ly - lh // 2, lx + lw // 2, ly + lh // 2), fill=lcol + (alpha,))
        # Central vein
        fd.line(
            (lx, ly - lh // 2 + 12, lx + rng.randint(-15, 15), ly + lh // 2 - 12),
            fill=(10, 30, 8, alpha // 2), width=3,
        )
        # Side veins
        for vi in range(5):
            vy = ly - lh // 2 + 18 + vi * (lh // 6)
            fd.line(
                (lx, vy, lx + rng.randint(-50, -20), vy + rng.randint(-8, 8)),
                fill=(10, 30, 8, alpha // 3), width=1,
            )

    # --- Right-side large leaves ---
    for li in range(14):
        lx = rng.randint(W - 170, W + 60)
        ly = rng.randint(150, 2200)
        lw = rng.randint(140, 350)
        lh = rng.randint(100, 220)
        lcol = rng.choice(leaf_cols)
        alpha = rng.randint(210, 250)
        fd.ellipse((lx - lw // 2, ly - lh // 2, lx + lw // 2, ly + lh // 2), fill=lcol + (alpha,))
        fd.line(
            (lx, ly - lh // 2 + 12, lx + rng.randint(-15, 15), ly + lh // 2 - 12),
            fill=(10, 30, 8, alpha // 2), width=3,
        )

    # --- Palm trunks visible through foliage gaps ---
    for ti in range(3):
        tx = 180 + ti * 300
        ty = 1400
        tcol = PALM_TRUNK + (150,)
        # Curved trunk
        pts = []
        for ti2 in range(40):
            t = ti2 / 40
            pts.append((tx + int(20 * math.sin(t * math.pi)), ty - int(t * 800)))
        fd.line(pts, fill=tcol, width=10)
        # Frond tuft at top
        for fr in range(7):
            ang = fr * math.tau / 7
            fr_len = rng.randint(80, 150)
            fdx = tx + int(fr_len * math.cos(ang))
            fdy = ty - 800 + int(fr_len * math.sin(ang) * 0.4)
            fd.line((tx, ty - 800, fdx, fdy), fill=(30, 65, 20, 180), width=4)

    # --- Hanging vines from top ---
    for vi in range(20):
        vx = rng.randint(0, W)
        vy = rng.randint(-30, 100)
        vlen = rng.randint(80, 400)
        vcol = (rng.randint(20, 45), rng.randint(40, 75), rng.randint(15, 30))
        fd.line(
            (vx, vy, vx + rng.randint(-40, 40), vy + vlen),
            fill=vcol + (210,), width=rng.randint(2, 5),
        )
        for li in range(rng.randint(4, 10)):
            ly2 = vy + vlen * li // 8
            lx_off = rng.randint(-14, 14)
            fd.ellipse(
                (vx + lx_off - 10, ly2 - 5, vx + lx_off + 10, ly2 + 5),
                fill=(rng.randint(25, 55), rng.randint(50, 85), rng.randint(18, 35), 200),
            )

    # --- Dense ground undergrowth ---
    for bi in range(30):
        bx = rng.randint(0, W)
        by = rng.randint(1800, 2250)
        bw = rng.randint(60, 250)
        bh = rng.randint(40, 140)
        bcol = (rng.randint(12, 35), rng.randint(30, 65), rng.randint(8, 25))
        fd.ellipse((bx - bw // 2, by - bh // 2, bx + bw // 2, by + bh // 2), fill=bcol + (rng.randint(190, 250),))

    # --- Tropical flowers (hibiscus / bird of paradise accents) ---
    for fi in range(8):
        side = "left" if rng.random() < 0.5 else "right"
        fx = rng.randint(20, 180) if side == "left" else rng.randint(W - 200, W - 20)
        fy = rng.randint(400, 1800)
        fcol = FLOWER_RED if rng.random() < 0.6 else FLOWER_ORANGE
        # Petals
        for petal in range(5):
            angle = petal * math.tau / 5 + rng.uniform(-0.2, 0.2)
            px = fx + int(22 * math.cos(angle))
            py = fy + int(18 * math.sin(angle))
            fd.ellipse((px - 13, py - 9, px + 13, py + 9), fill=fcol + (230,))
        # Stamen
        fd.line((fx, fy, fx + 6, fy - 20), fill=(255, 220, 80, 220), width=2)
        fd.ellipse((fx + 3, fy - 23, fx + 9, fy - 17), fill=(255, 220, 80, 240))

    img = Image.alpha_composite(img, foliage)
    draw = ImageDraw.Draw(img, "RGBA")

    # ──────────────────────────────────────────────
    # 9. BOTANICAL SPECIMEN (scurvy-cure plant drawing)
    # ──────────────────────────────────────────────
    botany = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(botany)
    bp_x, bp_y = 230, 120
    plant_c = PLANT_DRAW + (70,)
    # Stem
    bd.line((bp_x, bp_y, bp_x, bp_y + 180), fill=plant_c, width=3)
    # Leaves
    for li in range(5):
        ly = bp_y + 25 + li * 32
        l_dir = 1 if li % 2 == 0 else -1
        bd.line((bp_x, ly, bp_x + l_dir * 40, ly - 8), fill=plant_c, width=2)
        bd.line((bp_x + l_dir * 40, ly - 8, bp_x + l_dir * 55, ly - 3), fill=plant_c, width=2)
        bd.line((bp_x + l_dir * 40, ly - 8, bp_x + l_dir * 38, ly - 18), fill=plant_c, width=2)
    # Flower head
    bd.ellipse((bp_x - 7, bp_y - 12, bp_x + 7, bp_y + 4), fill=PLANT_DRAW + (90,))
    for ci in range(4):
        ca = ci * math.tau / 4
        cx = bp_x + int(14 * math.cos(ca))
        cy = bp_y - 4 + int(14 * math.sin(ca))
        bd.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=(120, 160, 90, 70))
    # Roots
    for ri in range(3):
        rx = bp_x + rng.randint(-12, 12)
        ry = bp_y + 180
        bd.line((rx, ry, rx + rng.randint(-35, 35), ry + 25), fill=plant_c, width=2)
    # Label line (like a scientific illustration)
    bd.line((bp_x + 60, bp_y - 5, bp_x + 90, bp_y - 5), fill=PLANT_DRAW + (50,), width=1)
    # Small text-like marks (just dashes suggesting a label)
    for t in range(3):
        bd.line((bp_x + 90, bp_y - 8 + t * 8, bp_x + 130, bp_y - 8 + t * 8), fill=PLANT_DRAW + (40,), width=1)
    img = Image.alpha_composite(img, botany)
    draw = ImageDraw.Draw(img, "RGBA")

    # ──────────────────────────────────────────────
    # 10. HUMAN FIGURE on beach (Miri or Surgeon)
    # ──────────────────────────────────────────────
    fig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fgd = ImageDraw.Draw(fig)
    fig_x, fig_y = 720, 1320
    fcol = (25, 18, 14, 190)
    # Legs
    fgd.line((fig_x - 3, fig_y - 20, fig_x - 8, fig_y + 10), fill=fcol, width=4)
    fgd.line((fig_x + 3, fig_y - 20, fig_x + 8, fig_y + 10), fill=fcol, width=4)
    # Torso
    fgd.line((fig_x, fig_y - 60, fig_x, fig_y - 20), fill=fcol, width=5)
    # Head
    fgd.ellipse((fig_x - 7, fig_y - 72, fig_x + 7, fig_y - 58), fill=fcol)
    # Arms
    fgd.line((fig_x, fig_y - 52, fig_x - 15, fig_y - 35), fill=fcol, width=3)
    fgd.line((fig_x, fig_y - 52, fig_x + 25, fig_y - 45), fill=fcol, width=3)  # pointing
    img = Image.alpha_composite(img, fig)
    draw = ImageDraw.Draw(img, "RGBA")

    # ──────────────────────────────────────────────
    # 11. SUBTLE COMPASS ROSE watermark (faded)
    # ──────────────────────────────────────────────
    compass = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd_ = ImageDraw.Draw(compass)
    cx_, cy_ = 1380, 220
    comp_c = (130, 110, 70, 25)
    # Outer ring
    cd_.ellipse((cx_ - 40, cy_ - 40, cx_ + 40, cy_ + 40), outline=comp_c, width=1)
    cd_.ellipse((cx_ - 35, cy_ - 35, cx_ + 35, cy_ + 35), outline=comp_c, width=1)
    # Points
    for ci in range(8):
        ang = ci * math.tau / 8
        in_r = 10
        out_r = 42 if ci % 2 == 0 else 32
        cd_.line((
            cx_ + int(in_r * math.cos(ang)),
            cy_ + int(in_r * math.sin(ang)),
            cx_ + int(out_r * math.cos(ang)),
            cy_ + int(out_r * math.sin(ang)),
        ), fill=comp_c, width=2 if ci % 2 == 0 else 1)
    img = Image.alpha_composite(img, compass)
    draw = ImageDraw.Draw(img, "RGBA")

    # ──────────────────────────────────────────────
    # 12. SUBTLE VIGNETTE
    # ──────────────────────────────────────────────
    vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette)
    for vy in range(H):
        vh = 1 - gauss(vy, H // 2, H * 0.5)
        dark = int(60 * vh)
        if dark > 0:
            vd.line((0, vy, min(dark, W), vy), fill=(0, 0, 0, 35))
            vd.line((max(W - dark, 0), vy, W, vy), fill=(0, 0, 0, 35))
    img = Image.alpha_composite(img, vignette)
    draw = ImageDraw.Draw(img, "RGBA")

    # ──────────────────────────────────────────────
    # 13. TITLE PANEL
    # ──────────────────────────────────────────────
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
