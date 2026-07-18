#!/usr/bin/env python3
"""Cover: The Bone Harvester's Feast — A small-town mortician discovers the dead are regrowing their bones beneath the soil, and a secret farmers' guild harvests them for an autumnal feast that feeds something beneath the church."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# ── Folk Horror palette: autumnal decay, soil, bone, and corrupted ecclesiastical green ──
SKY_TOP = (60, 20, 8)           # deep blood-rust at zenith
SKY_BTM = (130, 55, 20)         # burnt orange near horizon
MOON = (220, 185, 140)          # jaundiced harvest moon
MOON_GLOW = (200, 160, 100)     # moon glow wash
SOIL_TOP = (35, 22, 10)         # dark topsoil
SOIL_BTM = (65, 40, 18)         # rich loam deeper down
BONE_LIGHT = (230, 218, 195)    # fresh bone
BONE_DIM = (185, 168, 140)      # aged bone
BONE_GLOW = (170, 200, 140)     # sickly greenish bone-magic
CHURCH_DARK = (12, 8, 6)        # silhouette of church
CHURCH_LIT = (60, 35, 15)       # dim warm church light
GRAVE_STONE = (55, 48, 38)      # weathered granite
FEAST_GLOW = (140, 180, 80)     # chartreuse ritual glow
UNDERGLOW = (80, 140, 60)       # deep underground ritual light

rng = random.Random()
rng.seed(819472635)


def gaussian(x, mu, sigma):
    return math.exp(-((x - mu) ** 2) / (2 * sigma * sigma))


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    base = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(base, "RGBA")

    # ════════════════════════════════════════════════════════════
    # SKY: blood-rust gradient fading to burnt orange at horizon
    # ════════════════════════════════════════════════════════════
    horizon_y = 800
    for y in range(horizon_y + 1):
        t = y / horizon_y
        r = int(SKY_TOP[0] + (SKY_BTM[0] - SKY_TOP[0]) * t)
        g = int(SKY_TOP[1] + (SKY_BTM[1] - SKY_TOP[1]) * t)
        b = int(SKY_TOP[2] + (SKY_BTM[2] - SKY_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── Harvest moon  ──
    moon_cx, moon_cy = 850, 320
    moon_r = 170
    moon_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(moon_layer)
    for gr in range(60, 0, -1):
        alpha = int(25 * (1 - gr / 60))
        md.ellipse((moon_cx - moon_r - gr, moon_cy - moon_r - gr,
                     moon_cx + moon_r + gr, moon_cy + moon_r + gr),
                   fill=MOON_GLOW + (alpha,))
    md.ellipse((moon_cx - moon_r, moon_cy - moon_r,
                moon_cx + moon_r, moon_cy + moon_r),
               fill=MOON + (230,))
    for _ in range(40):
        mx = rng.randint(-moon_r + 10, moon_r - 10)
        my = rng.randint(-moon_r + 10, moon_r - 10)
        md.ellipse((moon_cx + mx, moon_cy + my,
                    moon_cx + mx + 10, moon_cy + my + 10),
                   fill=(195, 165, 125, rng.randint(20, 50)))
    moon_layer = moon_layer.filter(ImageFilter.GaussianBlur(4))
    base = Image.alpha_composite(base, moon_layer)
    draw = ImageDraw.Draw(base, "RGBA")

    # ── Church silhouette  ──
    church = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(church)
    cd.rectangle((550, horizon_y - 480, 1050, horizon_y), fill=CHURCH_DARK + (240,))
    cd.polygon([(620, horizon_y - 480), (980, horizon_y - 480),
                (980, horizon_y - 620), (800, horizon_y - 750),
                (620, horizon_y - 620)], fill=CHURCH_DARK + (240,))
    cd.line((800, horizon_y - 750, 800, horizon_y - 790), fill=(20, 15, 10, 220), width=6)
    cd.line((785, horizon_y - 770, 815, horizon_y - 770), fill=(20, 15, 10, 220), width=5)
    for (wx, wy) in [(620, horizon_y - 300), (880, horizon_y - 300)]:
        cd.ellipse((wx, wy, wx + 100, wy + 120), fill=CHURCH_LIT + (180,))
        cd.ellipse((wx + 10, wy + 10, wx + 90, wy + 110), fill=(80, 50, 25, 120))
        cd.arc((wx, wy, wx + 100, wy + 120), 0, 180, fill=CHURCH_DARK + (200,), width=4)
    cd.ellipse((740, horizon_y - 460, 860, horizon_y - 340), fill=CHURCH_LIT + (150,))
    for ring in range(1, 4):
        ro = ring * 15
        cd.ellipse((740 + ro, horizon_y - 460 + ro, 860 - ro, horizon_y - 340 - ro),
                   outline=(40, 25, 12, 200), width=2)
    base = Image.alpha_composite(base, church)
    draw = ImageDraw.Draw(base, "RGBA")

    # ── Tombstones  ──
    for _ in range(30):
        gx = rng.randint(50, W - 50)
        tw, bw = rng.randint(8, 18), rng.randint(14, 28)
        gh = rng.randint(30, 80)
        tilt = rng.randint(-8, 8)
        sc = tuple(c + rng.randint(-10, 10) for c in GRAVE_STONE) + (200,)
        draw.polygon([(gx - bw // 2 + tilt, horizon_y),
                       (gx + bw // 2 + tilt, horizon_y),
                       (gx + tw // 2 + tilt, horizon_y - gh),
                       (gx - tw // 2 + tilt, horizon_y - gh)], fill=sc)

    # ── Bare trees  ──
    tree_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(tree_layer)
    for tree_x in [100, 200, 1350, 1480]:
        th = rng.randint(350, 500)
        td.line((tree_x, horizon_y, tree_x, horizon_y - th), fill=(8, 6, 4, 220), width=rng.randint(8, 14))
        ty = horizon_y - th + 80
        tx = tree_x
        dir = 1 if tree_x < W // 2 else -1
        while ty < horizon_y - 20:
            bl = rng.randint(40, 120)
            td.line((tx, ty, tx + dir * bl, ty - rng.randint(20, 60)),
                    fill=(8, 6, 4, 200), width=rng.randint(3, 6))
            if rng.random() < 0.5:
                td.line((tx + dir * bl // 2, ty - 10,
                         tx + dir * bl // 2 + dir * 30, ty - 40),
                        fill=(8, 6, 4, 180), width=2)
            ty += rng.randint(40, 80)
            tx += dir * 10
    base = Image.alpha_composite(base, tree_layer)

    # ════════════════════════════════════════════════════════════
    # SOIL BAND transitioning into cross-section underground
    # ════════════════════════════════════════════════════════════
    draw = ImageDraw.Draw(base, "RGBA")
    for y in range(horizon_y, H):
        t = (y - horizon_y) / (H - horizon_y)
        r = int(SOIL_TOP[0] + (SOIL_BTM[0] - SOIL_TOP[0]) * t)
        g = int(SOIL_TOP[1] + (SOIL_BTM[1] - SOIL_TOP[1]) * t)
        b = int(SOIL_TOP[2] + (SOIL_BTM[2] - SOIL_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ════════════════════════════════════════════════════════════
    # UNDERGROUND CROSS-SECTION: coffins, bone-roots, ritual
    # ════════════════════════════════════════════════════════════

    # ── Coffins cracked open, bones spilling  ──
    coffins = [(250, 1100, 430, 1320), (680, 1050, 900, 1300),
               (1150, 1150, 1320, 1380), (350, 1500, 500, 1700),
               (1050, 1480, 1200, 1680), (750, 1700, 910, 1920)]
    for cx1, cy1, cx2, cy2 in coffins:
        cl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cfd = ImageDraw.Draw(cl)
        ch = cy2 - cy1
        cfd.polygon([(cx1 + 10, cy1), (cx2 - 10, cy1),
                      (cx2, cy2 - 10), (cx1, cy2 - 10)],
                    fill=(40, 28, 15, 200), outline=(55, 40, 22, 220))
        cfd.line((cx1 + 5, cy1 + ch // 3, cx2 - 5, cy1 + ch // 3),
                 fill=(70, 50, 28, 180), width=3)
        for _ in range(rng.randint(4, 10)):
            bx = rng.randint(cx1 + 15, cx2 - 15)
            by = rng.randint(cy1 + ch // 3 + 5, cy2 - 10)
            bl = rng.randint(15, 40)
            ba = rng.random() * math.tau
            bc = BONE_LIGHT if rng.random() < 0.5 else BONE_DIM
            cfd.line((bx, by, bx + int(bl * math.cos(ba)), by + int(bl * math.sin(ba))),
                     fill=bc + (rng.randint(180, 230),), width=rng.randint(2, 5))
        base = Image.alpha_composite(base, cl)

    # ── Bone-thread roots growing through the soil toward the church  ──
    broot = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(broot)
    for _ in range(18):
        sx = rng.randint(100, 1500)
        sy = rng.randint(1100, 2300)
        pts = [(sx, sy)]
        for seg in range(rng.randint(5, 12)):
            lx, ly = pts[-1]
            nx = lx + (800 - lx) * 0.08 + rng.randint(-30, 30)
            ny = min(ly + 25 + rng.randint(-15, 15), H - 50)
            pts.append((int(nx), int(ny)))
        bc2 = rng.choice([BONE_DIM, BONE_GLOW, (200, 180, 150)])
        ba2 = rng.randint(80, 200)
        bw2 = rng.randint(2, 6)
        for i in range(len(pts) - 1):
            bd.line((pts[i], pts[i + 1]), fill=bc2 + (ba2,), width=bw2)
            if rng.random() < 0.25 and i < len(pts) - 2:
                be = (pts[i + 1][0] + rng.randint(-40, 40), pts[i + 1][1] + rng.randint(15, 35))
                bd.line((pts[i + 1], be), fill=bc2 + (ba2 - 30,), width=max(1, bw2 - 2))
        for pt in pts[::2]:
            bd.ellipse((pt[0] - 4, pt[1] - 4, pt[0] + 4, pt[1] + 4),
                       fill=(BONE_LIGHT[0], BONE_LIGHT[1], BONE_LIGHT[2], rng.randint(100, 180)))
    base = Image.alpha_composite(base, broot)

    # ── Cavern beneath the church  ──
    draw = ImageDraw.Draw(base, "RGBA")
    cavern_center_x, cavern_center_y = 800, 2200
    cad = ImageDraw.Draw(base)
    cad.ellipse((cavern_center_x - 300, cavern_center_y - 200,
                 cavern_center_x + 300, cavern_center_y + 200),
                fill=(15, 25, 8, 220))
    for gr in range(150, 0, -10):
        alpha = int(20 * (1 - gr / 150))
        cad.ellipse((cavern_center_x - gr, cavern_center_y - gr,
                     cavern_center_x + gr, cavern_center_y + gr),
                    fill=FEAST_GLOW + (alpha,))

    # ── Ritual figures in the cavern  ──
    def draw_fig(cx, cy, scale, alpha_val):
        sc = scale
        col2 = (5, 3, 2, alpha_val)
        cad.ellipse((cx - 8 * sc, cy - 22 * sc, cx + 8 * sc, cy - 6 * sc), fill=col2)
        cad.arc((cx - 18 * sc, cy - 5 * sc, cx + 12 * sc, cy + 25 * sc), 200, 340,
                fill=col2, width=max(2, int(4 * sc)))
        cad.polygon([(cx - 20 * sc, cy + 25 * sc), (cx + 15 * sc, cy + 25 * sc),
                      (cx + 25 * sc, cy + 55 * sc), (cx - 28 * sc, cy + 55 * sc)], fill=col2)
        cad.line((cx - 8 * sc, cy, cx - 28 * sc, cy - 25 * sc), fill=col2, width=max(2, int(3 * sc)))
        cad.line((cx + 8 * sc, cy, cx + 28 * sc, cy - 25 * sc), fill=col2, width=max(2, int(3 * sc)))

    draw_fig(cavern_center_x - 60, cavern_center_y + 20, 1.2, 180)
    draw_fig(cavern_center_x + 50, cavern_center_y + 15, 1.0, 160)
    draw_fig(cavern_center_x - 130, cavern_center_y + 40, 0.8, 130)
    draw_fig(cavern_center_x + 120, cavern_center_y + 35, 0.9, 140)

    # ── Central bone offering  ──
    for _ in range(15):
        bx = cavern_center_x + rng.randint(-30, 30)
        by = cavern_center_y + rng.randint(0, 25)
        bl = rng.randint(8, 20)
        ba2 = rng.random() * math.tau
        cad.line((bx, by, bx + int(bl * math.cos(ba2)), by + int(bl * math.sin(ba2))),
                 fill=BONE_LIGHT + (180,), width=rng.randint(2, 4))

    # ── Underground atmospheric glow  ──
    underglow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ugd = ImageDraw.Draw(underglow)
    for _ in range(12):
        gx = rng.randint(100, 1500)
        gy = rng.randint(1000, 2400)
        gr2 = rng.randint(80, 250)
        gc2 = rng.choice([UNDERGLOW, FEAST_GLOW, (60, 100, 40)])
        ugd.ellipse((gx - gr2, gy - gr2, gx + gr2, gy + gr2),
                    fill=gc2 + (rng.randint(4, 15),))
    underglow = underglow.filter(ImageFilter.GaussianBlur(25))
    base = Image.alpha_composite(base, underglow)

    # ── Floating motes (bone-magic)  ──
    draw = ImageDraw.Draw(base, "RGBA")
    for _ in range(100):
        mx = rng.randint(50, 1550)
        my = rng.randint(900, 2450)
        mr = rng.randint(1, 5)
        ma = rng.randint(20, 80)
        mc = rng.choice([BONE_GLOW, (200, 230, 180), (180, 210, 160)])
        draw.ellipse((mx - mr, my - mr, mx + mr, my + mr), fill=mc + (ma,))

    # ── Surface leaves  ──
    for _ in range(40):
        lx = rng.randint(0, W)
        ly = rng.randint(horizon_y - 20, horizon_y + 40)
        leaf_col = (rng.randint(130, 180), rng.randint(30, 60), rng.randint(10, 30))
        draw.ellipse((lx - 3, ly - 2, lx + 3, ly + 2), fill=leaf_col + (rng.randint(60, 140),))

    # ════════════════════════════════════════════════════════════
    # VIGNETTE
    # ════════════════════════════════════════════════════════════
    vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette)
    for vy in range(H):
        vh = 1 - gaussian(vy, H // 2, H * 0.45)
        dark = int(60 * vh)
        if dark > 0:
            vd.line((0, vy, min(dark, W), vy), fill=(0, 0, 0, 50))
            vd.line((max(W - dark, 0), vy, W, vy), fill=(0, 0, 0, 50))
    base = Image.alpha_composite(base, vignette)

    # ════════════════════════════════════════════════════════════
    # TITLE PANEL (shared utility)
    # ════════════════════════════════════════════════════════════
    _draw_standard_cover_title_panel(base, title, author, model)

    op.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(op, "PNG", optimize=True)


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
