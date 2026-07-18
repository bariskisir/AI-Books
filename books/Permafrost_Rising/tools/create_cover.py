#!/usr/bin/env python3
"""Cover: Permafrost Rising — A team in Siberia drills into ancient permafrost and awakens a 40,000-year-old bacterium that consumes plastic and excretes crude oil, triggering a global resource war the microbe was buried to prevent."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# Seed for reproducibility
rng = random.Random(20240718)


def make_cover(mp: Path, op: Path) -> None:
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")
    desc = m.get("short_description", "")

    # === COLOR PALETTE: Frozen tundra (ice blues / bone whites) vs. bacterial threat (amber / crude-oil iridescence / biohazard green) ===
    # Permafrost cold: deep ice blue -> frozen white
    # Bacterial contamination: crude-oil brown-amber -> sickly green glow
    SKY_TOP = (12, 30, 55)       # Deep arctic night sky
    SKY_MID = (45, 65, 90)       # Icy twilight
    SKY_BOT = (80, 90, 100)      # Frozen haze near horizon
    ICE_WHITE = (200, 210, 220)
    ICE_SHADOW = (140, 160, 180)
    PERMAFROST_BROWN = (75, 55, 40)
    OIL_SHINE_A = (180, 140, 60, 60)   # Amber oil sheen
    OIL_SHINE_B = (140, 180, 80, 40)   # Iridescent green oil
    BIO_GLOW = (160, 220, 60, 180)     # Bacterial bioluminescence
    BIO_CORE = (200, 240, 100, 255)    # Hot bacterial core
    BLOOD_ORANGE = (200, 80, 30, 180)  # Resource war / danger

    img = Image.new("RGBA", (W, H), SKY_TOP + (255,))
    draw = ImageDraw.Draw(img, "RGBA")

    # ====== 1. SKY GRADIENT ======
    # Three-zone arctic sky: dark -> icy blue -> frozen haze near horizon
    for y in range(H):
        t = y / H
        if t < 0.35:
            # Upper: deep night -> icy twilight
            lt = t / 0.35
            r = int(SKY_TOP[0] + (SKY_MID[0] - SKY_TOP[0]) * lt)
            g = int(SKY_TOP[1] + (SKY_MID[1] - SKY_TOP[1]) * lt)
            b = int(SKY_TOP[2] + (SKY_MID[2] - SKY_TOP[2]) * lt)
        elif t < 0.55:
            # Middle: icy twilight -> frozen haze
            lt = (t - 0.35) / 0.20
            r = int(SKY_MID[0] + (SKY_BOT[0] - SKY_MID[0]) * lt)
            g = int(SKY_MID[1] + (SKY_BOT[1] - SKY_MID[1]) * lt)
            b = int(SKY_MID[2] + (SKY_BOT[2] - SKY_MID[2]) * lt)
        else:
            # Lower: frozen haze -> permafrost brown (contaminated horizon)
            lt = (t - 0.55) / 0.45
            r = int(SKY_BOT[0] + (PERMAFROST_BROWN[0] - SKY_BOT[0]) * lt)
            g = int(SKY_BOT[1] + (PERMAFROST_BROWN[1] - SKY_BOT[1]) * lt)
            b = int(SKY_BOT[2] + (PERMAFROST_BROWN[2] - SKY_BOT[2]) * lt)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ====== 2. AURORA BOREALIS (cold, ethereal — the innocence of the permafrost before contamination) ======
    aurora = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ad = ImageDraw.Draw(aurora)
    for band in range(3):
        base_y = rng.randint(200, 600)
        amp = rng.randint(80, 180)
        freq = rng.uniform(0.006, 0.015)
        phase = rng.uniform(0, math.tau)
        pts = []
        for wx in range(0, W + 10, 10):
            wy = base_y + math.sin(wx * freq + phase) * amp * 0.5 + math.sin(wx * freq * 2.3 + phase * 0.7) * amp * 0.3
            pts.append((wx, wy))
        acol = rng.choice([
            (60, 180, 200, 12),   # Teal
            (40, 140, 200, 10),   # Blue
            (100, 200, 150, 8),   # Green
            (140, 80, 200, 8),    # Violet
        ])
        draw.line(pts, fill=acol, width=rng.randint(20, 50))
    # Soften the aurora
    aurora = aurora.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, aurora)
    draw = ImageDraw.Draw(img, "RGBA")

    # ====== 3. DRILLING RIG SILHOUETTE (left of center, rising from the ice) ======
    rig_x = 420
    rig_base = 2100
    rig_height = 900

    # Main derrick tower — an A-frame structure
    draw.polygon([
        (rig_x - 30, rig_base),
        (rig_x - 18, rig_base - rig_height),
        (rig_x + 18, rig_base - rig_height),
        (rig_x + 30, rig_base),
    ], fill=(15, 20, 28, 230))

    # Cross beams on derrick
    for y_cross in range(rig_base - rig_height + 60, rig_base - 60, 70):
        width_t = 1 - (rig_base - y_cross) / rig_height
        half_w = int(18 + 12 * width_t)
        draw.line((rig_x - half_w, y_cross, rig_x + half_w, y_cross), fill=(25, 32, 42, 200), width=3)

    # Drill pipe extending down from derrick into the ground
    draw.line((rig_x, rig_base - rig_height + 40, rig_x, 2400), fill=(60, 70, 85, 200), width=5)
    # Segmented pipe joints
    for py in range(rig_base - rig_height + 100, 2400, 50):
        draw.rectangle((rig_x - 8, py - 2, rig_x + 8, py + 2), fill=(80, 90, 105, 200))

    # Machinery cabin at base
    cabin_w, cabin_h = 80, 100
    draw.rectangle(
        (rig_x - cabin_w, rig_base - 20, rig_x + cabin_w, rig_base + cabin_h),
        fill=(18, 22, 30, 230)
    )
    # Cabin window with dim light
    draw.rectangle((rig_x - 20, rig_base + 10, rig_x + 20, rig_base + 40), fill=(200, 190, 140, 60))

    # Winch drum at top
    draw.ellipse((rig_x - 14, rig_base - rig_height - 10, rig_x + 14, rig_base - rig_height + 18), fill=(30, 38, 50, 230))

    # Guylines (cables from derrick to ground)
    for side in [-1, 1]:
        gx = rig_x + side * 120
        draw.line((gx, rig_base + 30, rig_x + side * 14, rig_base - rig_height + 40), fill=(40, 48, 60, 100), width=1)
        # Anchors
        draw.ellipse((gx - 6, rig_base + 20, gx + 6, rig_base + 40), fill=(30, 38, 50, 180))

    # ====== 4. SECOND DRILLING RIG (far background, smaller, right side) ======
    rig2_x = 1200
    rig2_base = 1850
    rig2_height = 500
    draw.polygon([
        (rig2_x - 16, rig2_base),
        (rig2_x - 10, rig2_base - rig2_height),
        (rig2_x + 10, rig2_base - rig2_height),
        (rig2_x + 16, rig2_base),
    ], fill=(20, 25, 35, 180))
    for yc in range(rig2_base - rig2_height + 40, rig2_base - 40, 50):
        hw = int(10 + 6 * (1 - (rig2_base - yc) / rig2_height))
        draw.line((rig2_x - hw, yc, rig2_x + hw, yc), fill=(30, 36, 48, 150), width=2)
    draw.line((rig2_x, rig2_base - rig2_height + 30, rig2_x, 2200), fill=(50, 60, 75, 150), width=3)

    # ====== 5. PERMAFROST LANDSCAPE (frozen tundra with ice wedges) ======
    # Tundra surface — rolling frozen plain
    tundra_top = 1750
    tundra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(tundra)

    # Snow-covered ground with gentle undulations
    for x in range(0, W + 10, 10):
        y_hill = tundra_top + int(math.sin(x * 0.003) * 30) + int(math.sin(x * 0.008) * 15)
        # Snow cap
        td.line((x - 5, y_hill - 8, x + 5, y_hill - 8), fill=(ICE_WHITE + (200,)), width=5)
        td.line((x - 5, y_hill - 4, x + 5, y_hill - 4), fill=(180, 195, 210, 180), width=5)
        td.line((x - 5, y_hill, x + 5, y_hill), fill=(PERMAFROST_BROWN + (220,)), width=6)

    # Permafrost cross-section (exposed face below tundra)
    for y in range(tundra_top + 10, H, 4):
        t = (y - tundra_top) / (H - tundra_top)
        # Layered permafrost soil: brown-gray grading to darker
        r_brown = int(PERMAFROST_BROWN[0] - 20 * t)
        g_brown = int(PERMAFROST_BROWN[1] - 15 * t)
        b_brown = int(PERMAFROST_BROWN[2] - 10 * t)
        layer_col = (max(20, r_brown), max(15, g_brown), max(10, b_brown), 230)
        draw.line((0, y, W, y), fill=layer_col)

    # Ice wedges (V-shaped intrusions into the permafrost)
    for wedge_x in range(80, W, rng.randint(120, 220)):
        wedge_depth = rng.randint(100, 350)
        wedge_top = tundra_top + rng.randint(0, 10)
        wedge_color = (rng.randint(150, 200), rng.randint(170, 215), rng.randint(200, 235), 180)
        draw.polygon([
            (wedge_x, wedge_top),
            (wedge_x - 25, wedge_top + wedge_depth),
            (wedge_x + 25, wedge_top + wedge_depth),
        ], fill=wedge_color)
        # Ice lense highlight
        draw.polygon([
            (wedge_x, wedge_top + 10),
            (wedge_x - 15, wedge_top + wedge_depth - 20),
            (wedge_x + 15, wedge_top + wedge_depth - 20),
        ], fill=(220, 235, 250, 80))

    # ====== 6. BACTERIAL CONTAMINATION (glowing colonies spreading from the drill site) ======
    # The core sample at the base of the main drill rig — a glowing fissure
    contamination = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(contamination)

    # Glowing crack radiating from drill point
    crack_base = (rig_x, rig_base + 100)
    for crack in range(8):
        angle = rng.uniform(0, math.tau)
        length = rng.randint(80, 350)
        segments = rng.randint(3, 7)
        px, py = crack_base
        for seg in range(segments):
            nx = px + int(math.cos(angle + rng.uniform(-0.4, 0.4)) * length / segments)
            ny = py + int(math.sin(angle + rng.uniform(-0.4, 0.4)) * length / segments)
            # Glow intensity fades with distance
            fade = 1 - seg / segments
            glow_alpha = int(180 * fade)
            cd.line((px, py, nx, ny), fill=(160, 220, 60, glow_alpha), width=rng.randint(2, 5))
            # Wider outer glow
            cd.line((px, py, nx, ny), fill=(120, 200, 40, glow_alpha // 3), width=rng.randint(6, 12))
            px, py = nx, ny

    # Bacterial colonies — clusters of glowing ellipses
    for colony in range(20):
        cx = rig_x + rng.randint(-120, 120)
        cy = rig_base + 80 + rng.randint(20, 300)
        colony_size = rng.randint(10, 45)
        # Outer glow
        alpha_outer = rng.randint(30, 80)
        cd.ellipse(
            (cx - colony_size, cy - colony_size * 0.6, cx + colony_size, cy + colony_size * 0.6),
            fill=(100, 200, 40, alpha_outer)
        )
        # Inner core
        alpha_inner = rng.randint(120, 220)
        cd.ellipse(
            (cx - colony_size * 0.5, cy - colony_size * 0.35, cx + colony_size * 0.5, cy + colony_size * 0.35),
            fill=BIO_GLOW[:3] + (alpha_inner,)
        )
        # Hot center
        if rng.random() < 0.5:
            cd.ellipse(
                (cx - colony_size * 0.2, cy - colony_size * 0.15, cx + colony_size * 0.2, cy + colony_size * 0.15),
                fill=BIO_CORE[:3] + (255,)
            )

    # Bacterial tendrils spreading through permafrost layers
    for tendril in range(12):
        tx = rig_x + rng.randint(-200, 200)
        ty = rig_base + 100 + rng.randint(50, 400)
        pts = [(tx, ty)]
        for _ in range(rng.randint(4, 10)):
            tx += rng.randint(-30, 30)
            ty += rng.randint(15, 40)
            pts.append((tx, ty))
        cd.line(pts, fill=(120, 200, 50, rng.randint(60, 140)), width=rng.randint(2, 4))

    # Blend contamination layer
    contamination = contamination.filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(img, contamination)
    draw = ImageDraw.Draw(img, "RGBA")

    # ====== 7. OIL SEEPAGE (iridescent crude oil seeping from the permafrost) ======
    oil = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(oil)

    for seep in range(15):
        sx = rig_x + rng.randint(-300, 400)
        sy = rig_base + 100 + rng.randint(100, 500)
        sr = rng.randint(15, 60)
        # Iridescent oil pool — layered ellipses with different hues
        for layer in range(4):
            shrink = 1 - layer * 0.2
            alpha_oil = rng.randint(20, 50)
            if layer % 3 == 0:
                col = (180, 140, 60, alpha_oil)    # Amber
            elif layer % 3 == 1:
                col = (140, 180, 80, alpha_oil)    # Green sheen
            else:
                col = (100, 120, 180, alpha_oil)   # Blue iridescence
            od.ellipse(
                (sx - sr * shrink, sy - sr * shrink * 0.5, sx + sr * shrink, sy + sr * shrink * 0.5),
                fill=col
            )

    # Merge oil layer
    img = Image.alpha_composite(img, oil)
    draw = ImageDraw.Draw(img, "RGBA")

    # ====== 8. SKY CONTAMINATION (amber/orange glow on the horizon — oil fires / resource war) ======
    war_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(war_glow)

    # Distant amber glow on the right horizon
    wd.ellipse(
        (1000, 1200, W + 200, 1600),
        fill=(200, 120, 40, 20)
    )
    wd.ellipse(
        (1100, 1250, W + 100, 1550),
        fill=(220, 150, 60, 15)
    )

    # Smoke plumes rising
    for plume in range(6):
        px = W - rng.randint(100, 400)
        py = rng.randint(800, 1400)
        pts = [(px, py)]
        for _ in range(rng.randint(5, 10)):
            px += rng.randint(-20, 20)
            py -= rng.randint(30, 60)
            pts.append((px, py))
        wd.line(pts, fill=(60, 40, 25, rng.randint(20, 50)), width=rng.randint(10, 25))

    # Merge war glow
    war_glow = war_glow.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, war_glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # ====== 9. ICE CRYSTAL DETAILS (foreground — shattered ice fragments) ======
    for _ in range(25):
        ix = rng.randint(0, W)
        iy = rng.randint(2200, 2500)
        isize = rng.randint(5, 20)
        # Ice shard (polygon)
        if rng.random() < 0.5:
            draw.polygon([
                (ix, iy),
                (ix + isize * 0.5, iy - isize * 0.8),
                (ix + isize, iy),
            ], fill=(180, 210, 230, rng.randint(100, 180)))
        else:
            draw.polygon([
                (ix + isize * 0.5, iy),
                (ix, iy - isize),
                (ix + isize, iy - isize),
            ], fill=(160, 200, 220, rng.randint(80, 160)))

    # ====== 10. FINE PARTICULATE (bacterial spores / ice crystals floating in air) ======
    for _ in range(120):
        px = rng.randint(0, W)
        py = rng.randint(0, H)
        pr = rng.uniform(1.0, 3.5)
        p_alpha = rng.randint(40, 120)
        # Mix between ice particles (white-blue) and bacterial spores (green)
        if rng.random() < 0.6:
            pcol = (200, 215, 230, p_alpha)  # Ice
        else:
            pcol = (150, 200, 70, p_alpha)   # Spore
        draw.ellipse((px - pr, py - pr, px + pr, py + pr), fill=pcol)

    # ====== 11. LIGHT SHAFTS (moonlight breaking through the contaminated sky) ======
    for _ in range(3):
        sx = rng.randint(100, W - 100)
        for a in range(-6, 7, 3):
            ang = math.radians(a + rng.uniform(-1, 1))
            ex = sx + int(math.sin(ang) * rng.randint(200, 500))
            ey = rng.randint(100, 400)
            draw.line((sx, 0, ex, ey), fill=(120, 160, 200, rng.randint(4, 12)), width=rng.randint(4, 14))

    # ====== 12. SAVE ======
    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, title, author, model)
    img.convert("RGB").save(op, "PNG", optimize=True)
    print(f"Cover saved to {op}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    mp = ROOT / a.metadata if not a.metadata.is_absolute() else a.metadata
    op = ROOT / a.out if not a.out.is_absolute() else a.out
    make_cover(mp, op)


if __name__ == "__main__":
    main()
