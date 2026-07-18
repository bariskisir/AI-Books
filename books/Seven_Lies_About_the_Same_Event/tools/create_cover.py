#!/usr/bin/env python3
"""Cover: Seven Lies About the Same Event — A tech billionaire is found dead in a hermetically sealed data-center vault; seven employees each confess to the murder, and the detective must map their contradictory stories against a single server log that cannot be forged."""
from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# Palette: cold data-center steel blues with amber/crimson alert accents
# Derived from the locked-room tech-mystery setting: sterile vault, server LEDs, evidence markers
CR = (10, 14, 28)       # ceiling: deep vault shadow
CL = (28, 36, 55)       # floor: slightly lighter industrial steel

rng = random.Random()
rng.seed(2098317544)

USE_PALETTE = [
    (15, 20, 42),       # vault shadow
    (35, 45, 70),       # steel rack
    (180, 60, 50),      # crimson alert
    (220, 180, 60),     # amber status LED / evidence
    (60, 180, 220),     # cool data glow
]


def draw_rack(d, x, y, w, h):
    """Draw a server rack with equipment bays and status LEDs."""
    if w < 6 or h < 20:
        return
    d.rectangle((x, y, x + w, y + h), fill=(20, 26, 45, 230), outline=(40, 50, 75, 100))
    n_slots = max(2, h // 38)
    slot_h = (h - 12) // n_slots
    for i in range(n_slots):
        sy = y + 6 + i * slot_h
        sh = slot_h - 6
        if sh < 3 or w < 10:
            continue
        x1_outer = x + 3
        x2_outer = x + w - 3
        if x2_outer <= x1_outer:
            continue
        d.rectangle((x1_outer, sy, x2_outer, sy + sh), fill=(12, 16, 32, 200))
        x1_inner = x + 6
        x2_inner = x + w - 6
        if x2_inner > x1_inner:
            d.rectangle((x1_inner, sy + 2, x2_inner, sy + sh - 2), fill=(18, 22, 40, 180))
        # Status LEDs (only if slot is wide enough)
        if w >= 24:
            for lx, lc in [(x + 8, (60, 200, 60)), (x + w - 16, (220, 180, 40)), (x + w - 8, (200, 50, 40))]:
                if rng.random() < 0.7:
                    d.ellipse((lx, sy + 4, lx + 4, sy + 8), fill=(*lc, 180))
        # Data activity flicker
        if w >= 22 and rng.random() < 0.5:
            ax = x + rng.randint(10, max(10, w - 25))
            ay = sy + sh // 2
            aw = rng.randint(12, max(12, w - 20))
            if ax + aw <= W:
                d.line((ax, ay, ax + aw, ay), fill=(40, 120, 200, rng.randint(50, 100)), width=1)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (10, 14, 28, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ---- Gradient background: cold steel vault ----
    for y in range(H):
        t = y / H
        r = int(CR[0] + (CL[0] - CR[0]) * t)
        g = int(CR[1] + (CL[1] - CR[1]) * t)
        b = int(CR[2] + (CL[2] - CR[2]) * t)
        mf = max(0, 1 - abs(t - 0.4) * 2)
        b = min(255, b + int(18 * mf))
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ---- Vignette: darken edges ----
    for vy in range(H):
        vt = 1 - abs(vy - H//2) / (H//2)
        vv = int(40 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 90))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 90))

    # ---- Perspective floor grid (data-center tile pattern) ----
    vx, vy = W // 2, 280  # vanishing point near vault door
    for row in range(1, 30):
        t = row / 30
        y_row = int(vy + t * (H - vy))
        wr = t
        x1 = int(vx - 900 * wr)
        x2 = int(vx + 900 * wr)
        a = int(18 * (1 - t))
        if a > 0:
            draw.line((x1, y_row, x2, y_row), fill=(50, 80, 130, a), width=1)
    for col in range(-14, 15):
        if col == 0:
            continue
        x1 = vx + int(col * 20 * 0.3)
        y1 = vy + 10
        x2 = vx + int(col * 20 * (H / max(1, vy)))
        a = max(2, 14 - abs(col))
        draw.line((x1, y1, x2, H), fill=(50, 80, 130, a), width=1)

    # ---- Server racks: two rows creating forced-perspective corridor ----
    for side in (-1, 1):
        for depth in range(8):
            z = depth / 8
            scale = 0.08 + z * 0.92
            r_y = int(vy + z * 1500)
            r_w = int(140 * scale)
            r_h = int(900 * scale)
            r_x = vx + int(side * (40 + z * 550)) - r_w // 2
            if r_x + r_w < 0 or r_x > W or r_y < 50:
                continue
            draw_rack(draw, r_x, r_y, r_w, r_h)

    # ---- Vault door at the vanishing point ----
    vw, vh = 180, 320
    v_door_x = vx - vw // 2
    v_door_y = vy - 20
    draw.rectangle(
        (v_door_x, v_door_y, v_door_x + vw, v_door_y + vh),
        fill=(35, 42, 65, 220), outline=(70, 90, 140, 180), width=4,
    )
    # Circular handle / locking mechanism
    draw.ellipse(
        (vx - 20, v_door_y + vh // 2 - 20, vx + 20, v_door_y + vh // 2 + 20),
        fill=(55, 65, 95, 200), outline=(90, 120, 170, 180), width=3,
    )
    draw.ellipse(
        (vx - 6, v_door_y + vh // 2 - 6, vx + 6, v_door_y + vh // 2 + 6),
        fill=(120, 90, 50, 200),
    )
    # Hinges
    for hy_off in (40, vh - 40):
        for hx_sign in (-1, 1):
            hx = v_door_x + (vw if hx_sign == 1 else 0) + hx_sign * 8
            draw.ellipse(
                (hx - 6, v_door_y + hy_off - 6, hx + 6, v_door_y + hy_off + 6),
                fill=(40, 48, 75, 200),
            )

    # ---- Seven confessor silhouettes (the seven employees who each confess) ----
    silhouettes = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(silhouettes)

    # (x_rel, y_rel, size_scale, pose_id)
    # poses: a=standing, b=arms-raised, c=kneeling, d=head-down, e=pointing
    confessors = [
        (-0.30, 0.42, 1.0, "a"),    # standing
        (0.35, 0.38, 0.9, "b"),     # arms raised
        (-0.55, 0.37, 0.85, "c"),   # kneeling
        (0.60, 0.40, 0.95, "d"),    # head down
        (-0.15, 0.48, 1.1, "e"),    # pointing toward vault
        (0.20, 0.50, 1.05, "a"),    # standing
        (-0.45, 0.52, 1.15, "b"),   # arms raised
    ]

    for x_rel, y_rel, size_sc, pose in confessors:
        cx = int(vx + x_rel * W * 0.38)
        cy = int(600 + y_rel * 900)
        sh = int(140 * size_sc)
        sw = int(sh * 0.32)
        col = (4, 6, 16, 210)

        # Torso
        sd.ellipse((cx - sw, cy - sh, cx + sw, cy - sh // 3), fill=col)
        # Head
        hr = int(sw * 0.7)
        sd.ellipse((cx - hr, cy - sh - hr, cx + hr, cy - sh + hr), fill=col)

        if pose == "a":  # standing, arms at sides
            sd.line((cx - sw // 2, cy - sh // 3, cx - sw // 2 + 4, cy + 5), fill=col, width=sw)
            sd.line((cx + sw // 2, cy - sh // 3, cx + sw // 2 - 4, cy + 5), fill=col, width=sw)
        elif pose == "b":  # arms raised (dramatic confession)
            sd.line((cx - sw, cy - sh // 2, cx - sw * 2, cy - sh - sw), fill=(4, 6, 16, 200), width=sw // 2)
            sd.line((cx + sw, cy - sh // 2, cx + sw * 2, cy - sh - sw), fill=(4, 6, 16, 200), width=sw // 2)
            sd.line((cx - sw // 2, cy - sh // 3, cx - sw // 2 + 4, cy + 5), fill=col, width=sw)
            sd.line((cx + sw // 2, cy - sh // 3, cx + sw // 2 - 4, cy + 5), fill=col, width=sw)
        elif pose == "c":  # kneeling
            sd.line((cx - sw // 2, cy - sh // 3, cx - sw // 2 - 6, cy - sh // 4), fill=col, width=sw)
            sd.line((cx + sw // 2, cy - sh // 3, cx + sw // 2 + 6, cy - sh // 4), fill=col, width=sw)
        elif pose == "d":  # head down (ashamed / guilty posture)
            sd.line((cx - sw // 2, cy - sh // 3, cx - sw // 2 + 4, cy + 5), fill=col, width=sw)
            sd.line((cx + sw // 2, cy - sh // 3, cx + sw // 2 - 4, cy + 5), fill=col, width=sw)
            sd.line((cx - sw, cy - sh // 3 + 10, cx - sw - 10, cy - sh // 3 + 30), fill=(4, 6, 16, 200), width=sw // 2)
            sd.line((cx + sw, cy - sh // 3 + 10, cx + sw + 10, cy - sh // 3 + 30), fill=(4, 6, 16, 200), width=sw // 2)
        elif pose == "e":  # pointing (accusation / testimony)
            sd.line((cx - sw // 2, cy - sh // 3, cx - sw // 2 + 4, cy + 5), fill=col, width=sw)
            sd.line((cx + sw // 2, cy - sh // 3, cx + sw // 2 - 4, cy + 5), fill=col, width=sw)
            p_dir = -1 if cx > vx else 1
            sd.line((cx + p_dir * sw, cy - sh // 2, cx + p_dir * sw * 2, cy - sh * 0.8), fill=(4, 6, 16, 200), width=sw // 2)

    silhouettes = silhouettes.filter(ImageFilter.GaussianBlur(radius=2))
    img = Image.alpha_composite(img, silhouettes)
    draw = ImageDraw.Draw(img, "RGBA")

    # ---- Server log lines: horizontal glowing bars suggesting contradictory log entries ----
    log_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(log_layer)

    for _ in range(25):
        lx = rng.randint(50, 1550)
        ly = rng.randint(300, 1700)
        lw = rng.randint(60, 350)
        lh = rng.randint(4, 7)
        alpha = rng.randint(35, 80)
        ld.rectangle((lx, ly, lx + lw, ly + lh), fill=(80, 170, 220, alpha))
        if rng.random() < 0.5:
            ld.rectangle((lx + 3, ly + 1, lx + lw - 3, ly + lh - 1), fill=(160, 220, 255, rng.randint(40, 80)))

    # Outer glow on the log lines
    log_glow = log_layer.filter(ImageFilter.GaussianBlur(radius=5))
    img = Image.alpha_composite(img, log_glow)
    img = Image.alpha_composite(img, log_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ---- Crime scene evidence markers ----
    crime_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cs = ImageDraw.Draw(crime_layer)

    bcx, bcy = vx + 20, 1350  # body position on the floor
    # Chalk-like body outline
    cs.ellipse((bcx - 60, bcy - 90, bcx + 60, bcy + 20), outline=(180, 180, 200, 100), width=3)
    cs.ellipse((bcx - 60, bcy - 90, bcx + 60, bcy + 20), outline=(180, 180, 200, 40), width=6)
    # Evidence number markers (yellow crosshairs)
    for mx, my in [
        (bcx - 80, bcy - 100),
        (bcx + 70, bcy - 70),
        (bcx - 50, bcy + 30),
        (bcx + 40, bcy + 40),
    ]:
        cs.ellipse((mx - 5, my - 5, mx + 5, my + 5), fill=(200, 180, 40, 130))
        cs.line((mx - 10, my, mx + 10, my), fill=(200, 180, 40, 100), width=1)
        cs.line((mx, my - 10, mx, my + 10), fill=(200, 180, 40, 100), width=1)

    img = Image.alpha_composite(img, crime_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ---- Harsh overhead vault light cone ----
    light_cone = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lc = ImageDraw.Draw(light_cone)
    for _ in range(200):
        sx = vx + rng.randint(-50, 50)
        sy = rng.randint(50, 150)
        ex = vx + rng.randint(-350, 350)
        ey = rng.randint(900, 1500)
        lc.line((sx, sy, ex, ey), fill=(160, 190, 220, rng.randint(2, 8)), width=1)
    light_cone = light_cone.filter(ImageFilter.GaussianBlur(radius=10))
    img = Image.alpha_composite(img, light_cone)
    draw = ImageDraw.Draw(img, "RGBA")

    # ---- Crime scene tape (undulating amber band as visual barrier) ----
    for x in range(0, W, 4):
        yp = 1050 + int(math.sin(x * 0.025) * 20)
        draw.line((x, yp, x + 4, yp), fill=(200, 170, 40, rng.randint(20, 50)), width=2)

    # ---- Cyan ambient light pools near the server racks ----
    ambient = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ad = ImageDraw.Draw(ambient)
    for _ in range(10):
        gx = rng.randint(100, 1500)
        gy = rng.randint(400, 1200)
        gr = rng.randint(50, 140)
        ad.ellipse((gx - gr, gy - gr, gx + gr, gy + gr), fill=(30, 100, 200, rng.randint(5, 15)))
    ambient = ambient.filter(ImageFilter.GaussianBlur(radius=25))
    img = Image.alpha_composite(img, ambient)
    draw = ImageDraw.Draw(img, "RGBA")

    # ---- Floating digital particles (data evidence motes) ----
    for _ in range(100):
        px = rng.randint(0, W)
        py = rng.randint(200, 1700)
        pr = rng.uniform(0.5, 2.0)
        draw.ellipse(
            (int(px - pr), int(py - pr), int(px + pr), int(py + pr)),
            fill=(80, 200, 255, rng.randint(15, 60)),
        )

    # ---- Save ----
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
