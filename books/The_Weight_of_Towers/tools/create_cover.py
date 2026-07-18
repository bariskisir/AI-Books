#!/usr/bin/env python3
"""Cover: The Weight of Towers — Mediterranean coastal tower demolition, salt-cracked foundation, sunset silhouette."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# ── mediterranean sunset palette ─────────────────────────────────────────
SKY_TOP = (28, 18, 55)          # deep indigo zenith
SKY_HORIZON = (235, 175, 85)    # golden amber at horizon
SEA_TOP = (18, 55, 95)          # deep azure near horizon
SEA_BOTTOM = (12, 30, 55)       # darker blue at bottom
TOWER_LIGHT = (215, 190, 160)   # sunlit face of tower
TOWER_SHADOW = (140, 115, 90)   # shadow face
CRANE_DARK = (18, 16, 22)       # dark silhouette
SUN_COLOR = (255, 225, 150)     # warm sun
CRACK_COLOR = (195, 200, 205)   # salt-white damage
CLIFF_BASE = (110, 75, 50)      # cliff rock
VEGETATION = (65, 80, 45)       # coastal scrub

rng = random.Random()
rng.seed(20260718)


def make_cover(mp: Path, op: Path) -> None:
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    HORIZON_Y = 1550       # where sky meets sea
    TOWER_X = 500          # x centre of the tower
    TOWER_BASE_Y = 1500    # where tower meets the cliff
    TOWER_TOP_Y = 320      # top of tower
    TOWER_W = 180          # half-width of tower

    # ── 1. Sky gradient: deep indigo at top → amber at horizon ──────
    for y in range(HORIZON_Y):
        t = y / HORIZON_Y
        r = int(SKY_TOP[0] + (SKY_HORIZON[0] - SKY_TOP[0]) * t)
        g = int(SKY_TOP[1] + (SKY_HORIZON[1] - SKY_TOP[1]) * t)
        b = int(SKY_TOP[2] + (SKY_HORIZON[2] - SKY_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── 2. Sun glow near horizon ────────────────────────────────────
    sun_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sun_layer)
    # Large ambient glow
    sd.ellipse((550, HORIZON_Y - 200, 1050, HORIZON_Y + 150),
               fill=(255, 210, 140, 25))
    sd.ellipse((600, HORIZON_Y - 120, 1000, HORIZON_Y + 80),
               fill=(255, 220, 160, 40))
    sd.ellipse((680, HORIZON_Y - 60, 920, HORIZON_Y + 30),
               fill=(255, 230, 180, 60))
    sun_layer = sun_layer.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, sun_layer)
    draw = ImageDraw.Draw(img, "RGBA")
    # Bright sun disc
    draw.ellipse((760, HORIZON_Y - 40, 840, HORIZON_Y + 15),
                 fill=(*SUN_COLOR, 220))
    draw.ellipse((775, HORIZON_Y - 25, 825, HORIZON_Y + 5),
                 fill=(255, 240, 200, 180))

    # ── 3. Sea gradient: deep azure at horizon → darker below ──────
    for y in range(HORIZON_Y, H):
        t = (y - HORIZON_Y) / (H - HORIZON_Y)
        r = int(SEA_TOP[0] + (SEA_BOTTOM[0] - SEA_TOP[0]) * t)
        g = int(SEA_TOP[1] + (SEA_BOTTOM[1] - SEA_TOP[1]) * t)
        b = int(SEA_TOP[2] + (SEA_BOTTOM[2] - SEA_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── 4. Sea surface shimmer (sun reflection on water) ────────────
    shimmer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    smd = ImageDraw.Draw(shimmer)
    for i in range(24):
        y = HORIZON_Y + 20 + i * 20 + rng.randint(-5, 5)
        x_c = 800 + rng.randint(-80, 80)
        w = 60 + rng.randint(0, 100)
        smd.line((x_c - w // 2, y, x_c + w // 2, y),
                 fill=(255, 220, 150, rng.randint(6, 20)))
    shimmer = shimmer.filter(ImageFilter.GaussianBlur(4))
    img = Image.alpha_composite(img, shimmer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 5. Distant coastline silhouette ─────────────────────────────
    coast = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(coast)
    # Left hills
    left_hills = [(0, 1520)]
    for x in range(0, TOWER_X - 300, 40):
        h = 1480 - 60 * math.sin(x * 0.003) - 30 * math.sin(x * 0.008)
        left_hills.append((x, h))
    left_hills.append((TOWER_X - 300, 1540))
    cd.polygon(left_hills, fill=(40, 28, 35, 200))
    # Right hills
    right_hills = [(TOWER_X + TOWER_W + 250, 1520)]
    for x in range(TOWER_X + TOWER_W + 250, W + 10, 40):
        h = 1450 - 50 * math.sin(x * 0.003 + 1.5) - 40 * math.sin(x * 0.007)
        right_hills.append((x, h))
    right_hills.append((W, 1540))
    cd.polygon(right_hills, fill=(40, 28, 35, 200))
    img = Image.alpha_composite(img, coast)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 6. Cliff for tower base ─────────────────────────────────────
    cliff_pts = [(TOWER_X - 260, TOWER_BASE_Y + 40)]
    for x in range(TOWER_X - 260, TOWER_X + TOWER_W + 260, 15):
        y_off = 18 * math.sin(x * 0.04 + 0.5) + 12 * math.sin(x * 0.09)
        cliff_pts.append((x, TOWER_BASE_Y + int(y_off)))
    cliff_pts.append((TOWER_X + TOWER_W + 260, TOWER_BASE_Y + 60))
    cliff_pts.append((TOWER_X + TOWER_W + 260, TOWER_BASE_Y + 120))
    cliff_pts.append((TOWER_X - 260, TOWER_BASE_Y + 120))
    draw.polygon(cliff_pts, fill=(*CLIFF_BASE, 235))

    # Cliff texture - rough rock lines
    for _ in range(30):
        x = TOWER_X - 240 + rng.randint(0, TOWER_W * 2 + 480)
        y1 = TOWER_BASE_Y + rng.randint(10, 100)
        y2 = y1 + rng.randint(5, 25)
        draw.line((x, y1, x + rng.randint(-15, 15), y2),
                  fill=(90 + rng.randint(-20, 20), 60 + rng.randint(-15, 15),
                        40 + rng.randint(-10, 10), rng.randint(40, 100)),
                  width=1)

    # Vegetation on cliff
    for _ in range(40):
        vx = TOWER_X - 240 + rng.randint(0, TOWER_W * 2 + 480)
        vy = TOWER_BASE_Y - 20 + rng.randint(0, 50)
        vr = rng.randint(6, 18)
        draw.ellipse((vx - vr, vy - vr // 2, vx + vr, vy + vr // 2),
                     fill=(*VEGETATION, rng.randint(120, 200)))

    # ── 7. Torre del Mare tower ─────────────────────────────────────
    # Main tower body — two connected rectangular volumes with a setback
    # Lower section (wider)
    tw_low = TOWER_W + 25
    draw.rectangle((TOWER_X - tw_low, TOWER_BASE_Y - 380, TOWER_X + tw_low, TOWER_BASE_Y),
                   fill=(*TOWER_SHADOW, 240))
    # Upper section (narrower, setback)
    draw.rectangle((TOWER_X - TOWER_W, TOWER_BASE_Y - 850, TOWER_X + TOWER_W, TOWER_BASE_Y - 380),
                   fill=(*TOWER_SHADOW, 240))

    # Sunlit face (right side) for lower section
    draw.rectangle((TOWER_X, TOWER_BASE_Y - 380, TOWER_X + tw_low, TOWER_BASE_Y),
                   fill=(*TOWER_LIGHT, 230))
    # Sunlit face for upper section
    draw.rectangle((TOWER_X, TOWER_BASE_Y - 850, TOWER_X + TOWER_W, TOWER_BASE_Y - 380),
                   fill=(*TOWER_LIGHT, 230))

    # Tower crown / architectural cap
    crown_pts = [
        (TOWER_X - TOWER_W, TOWER_BASE_Y - 850),
        (TOWER_X - TOWER_W - 30, TOWER_BASE_Y - 870),
        (TOWER_X - TOWER_W - 30, TOWER_BASE_Y - 890),
        (TOWER_X - TOWER_W + 10, TOWER_BASE_Y - 920),
        (TOWER_X + TOWER_W - 10, TOWER_BASE_Y - 920),
        (TOWER_X + TOWER_W + 30, TOWER_BASE_Y - 890),
        (TOWER_X + TOWER_W + 30, TOWER_BASE_Y - 870),
        (TOWER_X + TOWER_W, TOWER_BASE_Y - 850),
    ]
    draw.polygon(crown_pts, fill=(*TOWER_LIGHT, 240))

    # Top antenna/spire
    draw.rectangle((TOWER_X - 3, TOWER_BASE_Y - 980, TOWER_X + 3, TOWER_BASE_Y - 920),
                   fill=(180, 170, 155, 230))

    # ── 8. Windows on tower (lit and unlit) ────────────────────────
    for floor in range(14):
        fy = TOWER_BASE_Y - 60 - floor * 58
        win_w = 14
        for col in range(6):
            wx = TOWER_X - TOWER_W + 25 + col * 55
            if wx < TOWER_X:  # left side - shadow face
                lit = rng.random() < 0.3
                if lit:
                    draw.rectangle((wx, fy, wx + win_w, fy + 32),
                                   fill=(240, 190, 100, rng.randint(120, 200)))
                    # window glow
                    draw.rectangle((wx - 4, fy - 2, wx + win_w + 4, fy + 34),
                                   fill=(250, 210, 140, 30))
            else:  # right side - lit face
                draw.rectangle((wx, fy, wx + win_w, fy + 32),
                               fill=(100, 95, 85, rng.randint(150, 220)))

    # ── 9. Saltwater crack damage creeping up from base ─────────────
    for _ in range(35):
        cx = TOWER_X + rng.randint(-tw_low, tw_low)
        cy = TOWER_BASE_Y - rng.randint(0, 500)
        segments = rng.randint(4, 14)
        pts = [(cx, cy)]
        for s in range(segments):
            cx += rng.randint(-12, 12)
            cy -= rng.randint(8, 25)
            pts.append((cx, cy))
        draw.line(pts, fill=(*CRACK_COLOR, rng.randint(60, 140)),
                  width=rng.randint(1, 3))

    # Crack branches (finer)
    for _ in range(25):
        cx = TOWER_X + rng.randint(-tw_low - 20, tw_low + 20)
        cy = TOWER_BASE_Y - rng.randint(0, 300)
        pts = [(cx, cy)]
        for s in range(rng.randint(3, 8)):
            cx += rng.randint(-8, 8)
            cy -= rng.randint(10, 20)
            pts.append((cx, cy))
        draw.line(pts, fill=(*CRACK_COLOR, rng.randint(30, 80)),
                  width=1)

    # ── 10. Demolition crane (right side) ───────────────────────────
    crane_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    crd = ImageDraw.Draw(crane_layer)
    # Main vertical mast
    crd.rectangle((1300, 850, 1320, TOWER_BASE_Y + 80),
                  fill=(*CRANE_DARK, 230))
    # Cross-bracing on mast
    for y in range(880, TOWER_BASE_Y, 60):
        crd.line((1300, y, 1320, y + 30), fill=(*CRANE_DARK, 180), width=2)
        crd.line((1320, y, 1300, y + 30), fill=(*CRANE_DARK, 180), width=2)
    # Jib arm extending left toward tower
    crd.polygon([
        (1300, 860), (TOWER_X + TOWER_W + 80, 840),
        (TOWER_X + TOWER_W + 80, 855), (1300, 880),
    ], fill=(*CRANE_DARK, 230))
    # Counter-jib (right side)
    crd.polygon([
        (1320, 860), (1530, 870), (1530, 885), (1320, 880),
    ], fill=(*CRANE_DARK, 230))
    # Cargo hook and cable
    crd.line((TOWER_X + TOWER_W - 20, 848, TOWER_X + TOWER_W - 20, 1000),
             fill=(60, 60, 65, 200), width=2)
    crd.ellipse((TOWER_X + TOWER_W - 30, 1000, TOWER_X + TOWER_W - 10, 1020),
                fill=(50, 50, 55, 220))
    # Crane cab at base of jib
    crd.rectangle((1280, 840, 1340, 900), fill=(*CRANE_DARK, 240))
    img = Image.alpha_composite(img, crane_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 11. Architectural blueprint overlay lines ───────────────────
    blue_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(blue_layer)
    # Horizontal section lines
    for y in range(TOWER_TOP_Y, TOWER_BASE_Y, 120):
        w = int(100 + 200 * (y - TOWER_TOP_Y) / (TOWER_BASE_Y - TOWER_TOP_Y))
        bd.line((TOWER_X - w // 2, y, TOWER_X + w // 2, y),
                fill=(150, 200, 230, 15), width=1)
    # Dimension arrows
    for y in [TOWER_BASE_Y - 200, TOWER_BASE_Y - 500, TOWER_BASE_Y - 800]:
        bd.line((TOWER_X + TOWER_W + 80, y, TOWER_X + TOWER_W + 150, y),
                fill=(150, 200, 230, 30), width=1)
        bd.line((TOWER_X + TOWER_W + 115, y - 10, TOWER_X + TOWER_W + 150, y),
                fill=(150, 200, 230, 30), width=1)
        bd.line((TOWER_X + TOWER_W + 115, y + 10, TOWER_X + TOWER_W + 150, y),
                fill=(150, 200, 230, 30), width=1)
    img = Image.alpha_composite(img, blue_layer)

    # ── 12. Atmospheric haze at horizon ─────────────────────────────
    haze = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(haze)
    hd.ellipse((-200, HORIZON_Y - 120, W + 200, HORIZON_Y + 60),
               fill=(200, 180, 160, 20))
    img = img.filter(ImageFilter.GaussianBlur(2))
    haze = haze.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img, haze)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Title panel via shared utility ──────────────────────────────
    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, title, author, model)
    img.convert("RGB").save(op, "PNG", optimize=True)


def main() -> None:
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
