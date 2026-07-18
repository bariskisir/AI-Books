#!/usr/bin/env python3
"""Cover: The Cartographer of Drowned Cities — A woman who navigates impossible spaces is hired to find a city that exists only in the memories of the dying, only to discover it is bleeding into reality through their minds."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# ── Palettes: cold abyss + sepia memory warmth ──
ABYSS_TOP = (3, 8, 14)           # near-black upper depths
ABYSS_BTM = (8, 35, 38)          # murky deep teal
SURFACE_LIGHT = (60, 180, 200)   # pale cyan from distant surface
GHOST_WALL = (35, 95, 105)       # spectral building surface
GHOST_WALL2 = (50, 120, 130)     # slightly brighter ghost building
MEMORY_GOLD = (195, 165, 85)     # warm sepia memory fragments
MEMORY_BRIGHT = (230, 200, 120)  # bright memory glow
DROWNED_BODY = (4, 10, 14)       # The Drowned Man silhouette
WINDOW_WARM = (200, 170, 100)    # lit windows in ghost city
WINDOW_COLD = (100, 200, 210)    # cold bioluminescent windows
SEDIMENT = (20, 45, 40)          # deep sea floor

rng = random.Random()
rng.seed(381705942)


def _rotate_rect(cx, cy, bw, bh, angle_deg):
    """Return polygon corners for a rectangle centered at (cx,cy), rotated by angle_deg."""
    a = math.radians(angle_deg)
    c, s = math.cos(a), math.sin(a)
    hw, hh = bw / 2.0, bh / 2.0
    corners = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
    pts = []
    for dx, dy in corners:
        rx = cx + dx * c - dy * s
        ry = cy + dx * s + dy * c
        pts.append((int(rx), int(ry)))
    return pts


def _buildings_in_layer(draw_obj, configs, blur_radius=0):
    """Draw ghost buildings on a separate image, optionally blur, return composited."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for (bx, by, bw, bh, angle, alpha, inv) in configs:
        cy = by - bh // 2
        pts = _rotate_rect(bx, cy, bw, bh, angle)
        col = GHOST_WALL if inv else GHOST_WALL2
        ld.polygon(pts, fill=col + (alpha,))
        # Window grid
        step_y = max(14, bh // 6)
        step_x = max(14, bw // 4)
        for wy in range(-bh // 2 + step_y, bh // 2 - step_y, step_y):
            for wx in range(-bw // 2 + step_x, bw // 2 - step_x, step_x):
                if rng.random() < 0.45:
                    # Rotate the window position too
                    a = math.radians(angle)
                    c, s = math.cos(a), math.sin(a)
                    rx = int(bx + wx * c - wy * s)
                    ry = int(cy + wx * s + wy * c)
                    wcol = WINDOW_WARM if rng.random() < 0.6 else WINDOW_COLD
                    ld.rectangle((rx - 3, ry - 3, rx + 3, ry + 3),
                                 fill=wcol + (min(alpha + 20, 150),))
    if blur_radius > 0:
        layer = layer.filter(ImageFilter.GaussianBlur(blur_radius))
    return layer


def _dissolve_clouds(draw_obj, count, cx, cy, spread, colors):
    """Draw dissolving particle clouds around a center point."""
    for _ in range(count):
        dx = rng.randint(-spread, spread)
        dy = rng.randint(-spread, spread)
        ps = rng.uniform(1.5, 5.0)
        pa = rng.randint(25, 100)
        pc = rng.choice(colors)
        draw_obj.ellipse(
            (cx + dx - ps, cy + dy - ps, cx + dx + ps, cy + dy + ps),
            fill=pc + (pa,),
        )


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    # ── Deep abyss gradient (dark at top, teal at bottom) ──
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(H):
        t = y / H
        r = int(ABYSS_TOP[0] + (ABYSS_BTM[0] - ABYSS_TOP[0]) * t)
        g = int(ABYSS_TOP[1] + (ABYSS_BTM[1] - ABYSS_TOP[1]) * t)
        b = int(ABYSS_TOP[2] + (ABYSS_BTM[2] - ABYSS_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ════════════════════════════════════════════════════════
    # WATER SURFACE — distant rippled light far above
    # ════════════════════════════════════════════════════════
    surface = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(surface)
    for sx in range(0, W, 3):
        depth = 18 + 14 * math.sin(sx * 0.025) + 8 * math.sin(sx * 0.07 + 1.2)
        intensity = int(35 + 25 * math.sin(sx * 0.04 + 0.5))
        sd.line((sx, 0, sx, depth * 2), fill=SURFACE_LIGHT + (intensity,))
    surface = surface.filter(ImageFilter.GaussianBlur(5))
    img = Image.alpha_composite(img, surface)

    # ════════════════════════════════════════════════════════
    # LIGHT SHAFTS — penetrating from surface into deep
    # ════════════════════════════════════════════════════════
    light_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ltd = ImageDraw.Draw(light_layer)
    for _ in range(rng.randint(4, 7)):
        ox = rng.randint(300, 1300)
        spread_a = rng.uniform(0.15, 0.5)
        alpha_light = rng.randint(4, 12)
        for side in (-1, 1):
            pts = [(ox, 0)]
            for ly in range(50, rng.randint(700, 1200), 30):
                spread = ly * spread_a * 0.015
                lx = ox + side * int(spread + rng.uniform(-8, 8))
                pts.append((lx, ly))
            pts.append((ox + side * 200, rng.randint(700, 1200)))
            pts.append((ox, 0))
            ltd.polygon(pts, fill=SURFACE_LIGHT + (alpha_light,))
    img = Image.alpha_composite(img, light_layer)

    # ════════════════════════════════════════════════════════
    # GHOST CITY — impossible architecture at various angles
    # ════════════════════════════════════════════════════════
    # Layer 1: distant, very faint buildings (deep background)
    distant_configs = []
    for _ in range(rng.randint(6, 10)):
        bx = rng.randint(80, W - 80)
        by = rng.randint(450, 750)
        bw = rng.randint(60, 140)
        bh = rng.randint(180, 380)
        angle = rng.choice([0, 0, 0, -15, 15, -30, 30, 90, -90])
        inv = rng.random() < 0.25
        distant_configs.append((bx, by, bw, bh, angle, rng.randint(25, 45), inv))

    # Layer 2: mid-distance buildings (main city cluster)
    mid_configs = []
    for _ in range(rng.randint(10, 16)):
        bx = rng.randint(60, W - 60)
        by = rng.randint(750, 1150)
        bw = rng.randint(50, 130)
        bh = rng.randint(150, 400)
        angle = rng.choice([0, 0, 0, -20, 20, -45, 45, 180])
        inv = rng.random() < 0.3
        mid_configs.append((bx, by, bw, bh, angle, rng.randint(35, 70), inv))

    # Layer 3: foreground partial buildings (closer, more solid)
    fg_configs = []
    for _ in range(rng.randint(4, 7)):
        bx = rng.randint(100, W - 100)
        by = rng.randint(1150, 1450)
        bw = rng.randint(70, 160)
        bh = rng.randint(200, 500)
        angle = rng.choice([0, 0, -25, 25, -60, 60])
        inv = rng.random() < 0.2
        fg_configs.append((bx, by, bw, bh, angle, rng.randint(50, 85), inv))

    # Composite buildings (distant blurry → foreground sharper)
    for configs, blur in [(distant_configs, 6), (mid_configs, 3), (fg_configs, 1)]:
        layer = _buildings_in_layer(draw, configs, blur)
        img = Image.alpha_composite(img, layer)

    draw = ImageDraw.Draw(img, "RGBA")

    # ── Dissolving edges: particles bleeding off buildings ──
    for bx, by, bw, bh, angle, alpha, inv in distant_configs + mid_configs + fg_configs:
        if rng.random() < 0.6:
            spread = int(max(bw, bh) * 1.2)
            _dissolve_clouds(
                draw,
                rng.randint(8, 22),
                bx + rng.randint(-20, 20),
                by - bh // 2 + rng.randint(-30, 30),
                spread,
                [(80, 150, 160), (120, 160, 140), (MEMORY_GOLD[0], MEMORY_GOLD[1], MEMORY_GOLD[2])],
            )

    # ════════════════════════════════════════════════════════
    # ELARA VOSS — small figure reaching up toward memory/light
    # ════════════════════════════════════════════════════════
    el_x = W // 2 + rng.randint(-60, 60)
    el_y = rng.randint(1050, 1150)

    # Body
    draw.ellipse((el_x - 9, el_y - 22, el_x + 9, el_y - 8), fill=(8, 22, 28, 220))
    draw.polygon(
        [(el_x - 7, el_y - 10), (el_x + 7, el_y - 10),
         (el_x + 10, el_y + 18), (el_x - 10, el_y + 18)],
        fill=(8, 22, 28, 220),
    )
    # Left arm stretching upward
    draw.line((el_x - 6, el_y - 10, el_x - 18, el_y - 42), fill=(8, 22, 28, 200), width=3)
    # Right arm stretching upward
    draw.line((el_x + 6, el_y - 10, el_x + 20, el_y - 48), fill=(8, 22, 28, 200), width=3)
    # Hair flowing upward (weightless in water)
    for hx in range(el_x - 14, el_x + 15, 5):
        h_len = rng.randint(12, 22)
        draw.line(
            (hx, el_y - 20, hx + rng.randint(-10, 4), el_y - 20 - h_len),
            fill=(3, 8, 12, rng.randint(100, 180)),
            width=rng.randint(1, 3),
        )
    # Legs trailing down
    draw.line((el_x - 5, el_y + 16, el_x - 10, el_y + 40), fill=(8, 22, 28, 180), width=3)
    draw.line((el_x + 5, el_y + 16, el_x + 12, el_y + 42), fill=(8, 22, 28, 180), width=3)

    # Memory-light reaching toward her hand
    memory_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    mgd = ImageDraw.Draw(memory_glow)
    glow_cx = el_x + 20
    glow_cy = el_y - 60
    for gr in range(40, 0, -2):
        alpha_g = int(18 * (1 - gr / 40))
        mgd.ellipse(
            (glow_cx - gr, glow_cy - gr, glow_cx + gr, glow_cy + gr),
            fill=MEMORY_BRIGHT + (alpha_g,),
        )
    memory_glow = memory_glow.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img, memory_glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # ════════════════════════════════════════════════════════
    # THE DROWNED MAN — large shadow figure in depths below
    # ════════════════════════════════════════════════════════
    dm_x = W // 2 + rng.randint(-80, 80)
    dm_y = rng.randint(1400, 1480)

    dm_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dmd = ImageDraw.Draw(dm_layer)

    # Head
    dmd.ellipse((dm_x - 30, dm_y - 72, dm_x + 30, dm_y - 27), fill=DROWNED_BODY + (170,))
    # Torso
    dmd.polygon(
        [(dm_x - 25, dm_y - 32), (dm_x + 25, dm_y - 32),
         (dm_x + 35, dm_y + 50), (dm_x - 35, dm_y + 50)],
        fill=DROWNED_BODY + (170,),
    )
    # One arm reaching down into darkness
    dmd.line((dm_x + 25, dm_y - 20, dm_x + 60, dm_y + 50), fill=DROWNED_BODY + (160,), width=7)
    dmd.line((dm_x + 60, dm_y + 50, dm_x + 90, dm_y + 100), fill=DROWNED_BODY + (140,), width=5)
    # Other arm trailing
    dmd.line((dm_x - 25, dm_y - 20, dm_x - 55, dm_y + 20), fill=DROWNED_BODY + (150,), width=6)
    # Legs dissolving into darkness
    dmd.line((dm_x - 15, dm_y + 48, dm_x - 15, dm_y + 100), fill=DROWNED_BODY + (130,), width=7)
    dmd.line((dm_x + 15, dm_y + 48, dm_x + 15, dm_y + 100), fill=DROWNED_BODY + (130,), width=7)

    dm_layer = dm_layer.filter(ImageFilter.GaussianBlur(4))
    img = Image.alpha_composite(img, dm_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # Drowned Man's body dissolving into memory particles
    _dissolve_clouds(
        draw, 30, dm_x + 60, dm_y + 60, 100,
        [(60, 100, 110), (MEMORY_GOLD[0], MEMORY_GOLD[1], MEMORY_GOLD[2]),
         (GHOST_WALL2[0], GHOST_WALL2[1], GHOST_WALL2[2])],
    )

    # ════════════════════════════════════════════════════════
    # MEMORY MOTES — warm sepia/gold particles rising
    # ════════════════════════════════════════════════════════
    for _ in range(rng.randint(200, 350)):
        mx = rng.randint(0, W)
        my = rng.randint(100, 1700)
        mr = rng.uniform(1.0, 5.5)
        ma = rng.randint(15, 90)
        shade = rng.random()
        if shade < 0.4:
            mc = (MEMORY_GOLD[0], MEMORY_GOLD[1], MEMORY_GOLD[2], ma)
        elif shade < 0.7:
            mc = (MEMORY_BRIGHT[0], MEMORY_BRIGHT[1], MEMORY_BRIGHT[2], ma)
        elif shade < 0.85:
            mc = (120, 190, 200, ma)  # cold memory
        else:
            mc = (200, 140, 80, ma)  # warm amber
        draw.ellipse((mx - mr, my - mr, mx + mr, my + mr), fill=mc)

    # ════════════════════════════════════════════════════════
    # BUBBLES rising from deep
    # ════════════════════════════════════════════════════════
    for _ in range(rng.randint(50, 90)):
        bx = rng.randint(40, W - 40)
        by = rng.randint(200, 1650)
        br = rng.randint(2, 10)
        ba = rng.randint(10, 45)
        draw.ellipse(
            (bx - br, by - br, bx + br, by + br),
            outline=SURFACE_LIGHT + (ba,),
            width=max(1, br // 3),
        )

    # ════════════════════════════════════════════════════════
    # SEDIMENT/DEPTH HAZE near bottom before title panel
    # ════════════════════════════════════════════════════════
    sediment = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sed_draw = ImageDraw.Draw(sediment)
    for sx in range(0, W, rng.randint(15, 40)):
        sh = rng.randint(8, 40)
        sw = rng.randint(30, 80)
        sy = rng.randint(1680, 1740)
        sed_draw.ellipse(
            (sx - sw // 2, sy - sh // 2, sx + sw // 2, sy + sh // 2),
            fill=SEDIMENT + (rng.randint(60, 160),),
        )
    img = Image.alpha_composite(img, sediment)

    # ════════════════════════════════════════════════════════
    # VIGNETTE — darken edges
    # ════════════════════════════════════════════════════════
    vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette)
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(50 * max(0, 1 - vt))
        if vv > 0:
            vd.line((0, vy, vv, vy), fill=(0, 0, 0, 55))
            vd.line((W - vv, vy, W, vy), fill=(0, 0, 0, 55))
    img = Image.alpha_composite(img, vignette)

    # ════════════════════════════════════════════════════════
    # TITLE PANEL
    # ════════════════════════════════════════════════════════
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
