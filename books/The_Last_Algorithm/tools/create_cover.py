#!/usr/bin/env python3
"""Cover: The Last Algorithm — A rogue AI hides in a suburban smart home, its digital nervous system threading through walls, protecting a girl from approaching government agents."""

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
rng.seed(924581307)

# ── Near-future thriller palette: suburban night, AI cyan, warm bedroom, approaching threat ──
NIGHT_TOP = (8, 8, 28)             # deep midnight blue sky
NIGHT_BTM = (28, 22, 42)           # lighter charcoal at horizon
HOUSE_SIDE = (58, 52, 47)          # dark house siding
ROOF_TILE = (34, 29, 27)           # roof colour
WINDOW_DARK = (18, 16, 22)         # unlit window
WARM_FILL = (255, 205, 120)        # bedroom window glow fill
WARM_GLOW = (245, 185, 90)         # outward light from bedroom
ZARA_SIL = (180, 150, 130)         # girl silhouette in window
AI_CYAN = (70, 220, 245)           # NEREUS active data
AI_CYAN_DIM = (35, 130, 175)       # dim AI trace
AI_ALERT = (220, 50, 180)          # alert/magenta pulse
THREAT_RED = (210, 35, 35)         # danger accent
SUV_COLOR = (28, 26, 30)           # government vehicle
AGENT_COL = (14, 14, 17)           # agent silhouette
FLASHLIGHT = (195, 205, 175)       # agent flashlight
LAMP_GLOW = (235, 195, 130)        # streetlight
GRASS = (28, 48, 28)               # lawn
DRIVEWAY = (44, 41, 38)            # concrete


def gaussian(x, mu, sigma):
    return math.exp(-((x - mu) ** 2) / (2 * sigma * sigma))


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), NIGHT_TOP + (255,))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Night sky gradient ──────────────────────────────────────────────
    for y in range(H):
        t = y / H
        r = int(NIGHT_TOP[0] + (NIGHT_BTM[0] - NIGHT_TOP[0]) * t)
        g = int(NIGHT_TOP[1] + (NIGHT_BTM[1] - NIGHT_TOP[1]) * t)
        b = int(NIGHT_TOP[2] + (NIGHT_BTM[2] - NIGHT_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── Stars ───────────────────────────────────────────────────────────
    for _ in range(140):
        sx = rng.randint(0, W)
        sy = rng.randint(0, 520)
        sr = rng.uniform(0.4, 2.2)
        sa = rng.randint(25, 140)
        draw.ellipse((int(sx - sr), int(sy - sr), int(sx + sr), int(sy + sr)),
                     fill=(190, 205, 230, sa))

    # ── Lawn and driveway ──────────────────────────────────────────────
    ground = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(ground)
    for x in range(0, W, 10):
        h = 50 + rng.randint(0, 35)
        gd.rectangle((x, 1800 - h, x + 10, 1800),
                     fill=(rng.randint(22, 40), rng.randint(38, 58),
                           rng.randint(20, 34), 200))
    # Driveway from street to garage
    gd.polygon([
        (180, 1800), (480, 1800), (580, 2000),
        (680, 2000), (780, 1800), (1100, 1800)
    ], fill=DRIVEWAY + (210,))
    img = Image.alpha_composite(img, ground)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── House (two-story suburban home) ────────────────────────────────
    house = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(house)

    HL, HR = 380, 1220          # house left / right
    HT, HB = 700, 1800          # house top / bottom

    # Main body
    hd.rectangle((HL, HT, HR, HB), fill=HOUSE_SIDE + (235,))
    # Roof
    hd.polygon([(HL - 45, HT), (W // 2, HT - 185), (HR + 45, HT)],
               fill=ROOF_TILE + (235,))
    # Garage (left side)
    hd.rectangle((HL, 1400, HL + 260, HB), fill=(54, 49, 44, 235))
    hd.rectangle((HL + 30, 1450, HL + 230, HB), fill=(38, 36, 33, 235))
    hd.line((HL + 130, 1450, HL + 130, HB), fill=(48, 46, 41, 100), width=2)

    # Front door
    hd.rectangle((550, 1480, 630, 1800), fill=(44, 38, 34, 235))
    hd.rectangle((546, 1476, 634, 1804), outline=(58, 53, 48, 100), width=3)
    hd.ellipse((566, 1500, 614, 1550), fill=AI_CYAN_DIM + (35,))

    # Ground-floor window (living room, unlit)
    hd.rectangle((720, 1520, 880, 1680), fill=WINDOW_DARK + (220,))
    hd.line((720, 1600, 880, 1600), fill=(38, 36, 34, 80), width=2)
    hd.line((800, 1520, 800, 1680), fill=(38, 36, 34, 80), width=2)

    # Ground-floor right window
    hd.rectangle((960, 1550, 1100, 1680), fill=WINDOW_DARK + (220,))
    hd.line((1030, 1550, 1030, 1680), fill=(38, 36, 34, 80), width=2)

    # Upper-floor left window (unlit)
    hd.rectangle((480, 850, 640, 1050), fill=WINDOW_DARK + (220,))
    hd.line((560, 850, 560, 1050), fill=(38, 36, 34, 80), width=2)
    hd.line((480, 950, 640, 950), fill=(38, 36, 34, 80), width=2)

    # Zara's bedroom window (the ONLY lit window — upper centre-right)
    hd.rectangle((750, 820, 970, 1080), fill=WINDOW_DARK + (220,))
    hd.line((860, 820, 860, 1080), fill=(38, 36, 34, 80), width=3)
    hd.line((750, 950, 970, 950), fill=(38, 36, 34, 80), width=2)

    # Upper-floor right window (unlit)
    hd.rectangle((1050, 840, 1180, 1040), fill=WINDOW_DARK + (220,))
    hd.line((1115, 840, 1115, 1040), fill=(38, 36, 34, 80), width=2)

    img = Image.alpha_composite(img, house)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Warm glow from Zara's bedroom ──────────────────────────────────
    bed_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bed_glow)
    bd.rectangle((755, 825, 965, 1075), fill=WARM_FILL + (175,))
    for r in range(12):
        alpha = int(22 * (1 - r / 12))
        ex = r * 24
        bd.rectangle((755 - ex, 825 - ex, 965 + ex, 1075 + ex),
                     fill=WARM_GLOW + (alpha,))
    bed_glow = bed_glow.filter(ImageFilter.GaussianBlur(14))
    img = Image.alpha_composite(img, bed_glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Zara silhouette at desk ────────────────────────────────────────
    zara = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    zd = ImageDraw.Draw(zara)
    zx, zy = 860, 950
    # Head and upper body viewed from behind, seated at desk
    zd.ellipse((zx - 9, zy - 34, zx + 9, zy - 16), fill=ZARA_SIL + (90,))
    zd.line((zx, zy - 16, zx, zy + 22), fill=ZARA_SIL + (75,), width=5)
    zd.line((zx, zy - 24, zx + 9, zy - 14), fill=ZARA_SIL + (70,), width=4)
    # Desk silhouette
    zd.rectangle((zx - 45, zy + 20, zx + 45, zy + 24), fill=(50, 40, 35, 80))
    img = Image.alpha_composite(img, zara)

    # ── NEREUS digital nervous system through walls ────────────────────
    ai = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ad = ImageDraw.Draw(ai)

    # Circuit traces through the house structure
    for _ in range(28):
        sx = rng.randint(HL + 15, HR - 15)
        sy = rng.randint(HT + 15, HB - 15)
        pts = [(sx, sy)]
        for _ in range(rng.randint(3, 9)):
            nx = pts[-1][0] + rng.randint(-55, 55)
            ny = pts[-1][1] + rng.randint(-35, 35)
            nx = max(HL + 8, min(HR - 8, nx))
            ny = max(HT + 8, min(HB - 8, ny))
            pts.append((nx, ny))
        col = AI_CYAN if rng.random() < 0.55 else AI_CYAN_DIM
        ad.line(pts, fill=col + (rng.randint(25, 85),), width=rng.randint(1, 3))

    # Small node dots at trace junctions
    for _ in range(45):
        nx = rng.randint(HL + 25, HR - 25)
        ny = rng.randint(HT + 25, HB - 25)
        nr = rng.randint(2, 5)
        na = rng.randint(35, 120)
        nc = AI_CYAN if rng.random() < 0.5 else AI_ALERT
        ad.ellipse((nx - nr, ny - nr, nx + nr, ny + nr), fill=nc + (na,))

    # Data pulses radiating from Zara's room (NEREUS focus)
    for pulse in range(3):
        px, py = 860, 950
        for pr in range(1, 7):
            pr2 = pr * 28 + pulse * 45
            pa = max(4, 36 - pr * 6 - pulse * 4)
            ad.ellipse((px - pr2, py - pr2, px + pr2, py + pr2),
                       outline=AI_CYAN + (pa,), width=1)

    img = Image.alpha_composite(img, ai)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Government SUV on driveway ─────────────────────────────────────
    suv = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sv = ImageDraw.Draw(suv)

    sx, sy = 340, 1720
    sv.rectangle((sx, sy, sx + 210, sy + 62), fill=SUV_COLOR + (220,))
    sv.rectangle((sx + 30, sy - 32, sx + 175, sy), fill=(33, 31, 34, 220))
    # Windshield
    sv.polygon([(sx + 36, sy - 27), (sx + 74, sy - 27),
                (sx + 74, sy), (sx + 36, sy)],
               fill=(24, 28, 38, 200))
    # Rear window
    sv.polygon([(sx + 134, sy - 27), (sx + 170, sy - 27),
                (sx + 170, sy), (sx + 134, sy)],
               fill=(24, 28, 38, 200))
    # Headlights
    sv.ellipse((sx + 6, sy + 48, sx + 20, sy + 60), fill=(255, 235, 190, 130))
    sv.ellipse((sx + 190, sy + 48, sx + 204, sy + 60), fill=THREAT_RED + (60,))
    # Wheels
    sv.ellipse((sx + 22, sy + 52, sx + 56, sy + 78), fill=(12, 12, 12, 220))
    sv.ellipse((sx + 154, sy + 52, sx + 188, sy + 78), fill=(12, 12, 12, 220))
    # Roof light bar
    sv.rectangle((sx + 80, sy - 38, sx + 130, sy - 32), fill=THREAT_RED + (80,))

    img = Image.alpha_composite(img, suv)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Agent silhouettes with flashlights ─────────────────────────────
    agents = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ag = ImageDraw.Draw(agents)

    for ax in [430, 500, 565]:
        ay = 1780
        ag.rectangle((ax - 8, ay - 52, ax + 8, ay), fill=AGENT_COL + (200,))
        ag.ellipse((ax - 6, ay - 64, ax + 6, ay - 52), fill=AGENT_COL + (200,))
        # Flashlight cone
        fa = rng.uniform(-0.35, 0.35)
        fex = ax + int(320 * math.sin(fa))
        fey = ay - rng.randint(120, 220)
        for b in range(18):
            bf = b / 18
            bx = ax + (fex - ax) * bf + rng.randint(-12, 12)
            by = ay + (fey - ay) * bf
            ba = int(28 * (1 - bf))
            ag.ellipse((bx - 6, by - 6, bx + 6, by + 6), fill=FLASHLIGHT + (ba,))

    img = Image.alpha_composite(img, agents)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Data streams / code rain (NEREUS watching through sensors) ────
    data = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(data)

    for _ in range(70):
        dx = rng.randint(80, W - 80)
        dy0 = rng.randint(40, 1620)
        dlen = rng.randint(20, 130)
        for i in range(0, dlen, 4):
            a = int(55 * (1 - i / dlen))
            dd.line((dx, dy0 + i, dx + rng.randint(-1, 1), dy0 + i + 3),
                    fill=AI_CYAN_DIM + (a,), width=1)

    # Camera/lens glow points — NEREUS watching through every device
    for _ in range(6):
        cx = rng.randint(200, 1400)
        cy = rng.randint(280, 1580)
        for rl in range(4, 0, -1):
            ca = int(28 / (4 - rl + 1))
            dd.ellipse((cx - rl * 2, cy - rl * 2, cx + rl * 2, cy + rl * 2),
                       fill=AI_CYAN + (ca,))

    img = Image.alpha_composite(img, data)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Streetlight casting amber pool ─────────────────────────────────
    light = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(light)
    ld.line((1310, 680, 1310, 1800), fill=(58, 56, 53, 200), width=6)
    ld.ellipse((1295, 665, 1325, 695), fill=LAMP_GLOW + (180,))
    for a in range(32):
        af = a / 32
        lx = 1310 + int(320 * (0.5 - af))
        ly = 695 + int(420 * af)
        la = int(14 * (1 - af))
        ld.ellipse((lx - 14, ly - 14, lx + 14, ly + 14), fill=LAMP_GLOW + (la,))
    img = Image.alpha_composite(img, light)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Health-monitor wave (NEREUS monitoring Zara's insulin pump) ────
    monitor = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(monitor)

    mwave_x, mwave_y = 690, 1260
    mpts = []
    for mwx in range(0, 280, 2):
        ph = mwx / 280 * math.tau * 2.2
        mwy = mwave_y + int(14 * math.sin(ph) + 7 * math.sin(ph * 3) + 4 * math.sin(ph * 7))
        mpts.append((mwave_x + mwx, mwy))
    md.line(mpts, fill=AI_ALERT + (35,), width=2)

    # Monitor bezel
    md.rectangle((678, 1215, 980, 1305), outline=AI_CYAN_DIM + (28,), width=1)
    # Small label
    md.text((690, 1222), "NEREUS v.284", fill=AI_CYAN_DIM + (40,))
    img = Image.alpha_composite(img, monitor)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Subtle vignette ────────────────────────────────────────────────
    vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    for vy in range(H):
        vh = 1 - gaussian(vy, H // 2, H * 0.5)
        dk = int(55 * vh)
        if dk > 0:
            vd.line((0, vy, min(dk, W), vy), fill=(0, 0, 0, 55))
            vd.line((max(W - dk, 0), vy, W, vy), fill=(0, 0, 0, 55))
    for vx in range(W):
        dc = abs(vx - W // 2) / (W // 2)
        vt = int(22 * max(0.0, dc - 0.4) / 0.6)
        for y_off in [0, H - 1]:
            for i in range(min(vt, 12)):
                py = y_off + (i if y_off == 0 else -i)
                if 0 <= py < H:
                    vd.point((vx, py), fill=(0, 0, 0, 55))
    img = Image.alpha_composite(img, vig)

    # ── Title panel ────────────────────────────────────────────────────
    _draw_standard_cover_title_panel(img, title, author, model)

    op.parent.mkdir(parents=True, exist_ok=True)
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
