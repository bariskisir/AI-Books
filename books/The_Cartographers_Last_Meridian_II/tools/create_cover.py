#!/usr/bin/env python3
"""Cover: The Cartographer's Last Meridian II — a disgraced Portuguese cartographer in 1519 maps the unknown southern continent as mutiny brews and his eyesight fails."""

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
rng.seed(11589304422)

# ── Warm aged-parchment palettes vs deep ocean indigos ──────────────────
PARCHMENT = (212, 190, 148)       # base parchment
PARCHMENT_LT = (232, 214, 172)    # lighter highlight
PARCHMENT_DK = (142, 118, 80)     # shadow
INK_BROWN = (72, 52, 28)
INK_FADED = (112, 88, 56)
OCEAN_DARK = (18, 26, 48)
OCEAN_MID = (30, 44, 72)
SEPIA_RED = (148, 42, 36)         # mutiny / blood accents
GOLD_OCHRE = (186, 150, 72)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    # ── 1. PARCHMENT-TO-OCEAN VERTICAL GRADIENT ──────────────────────
    img = Image.new("RGBA", (W, H), (212, 190, 148, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        if t < 0.55:
            tt = t / 0.55
            r = int(212 + (30 - 212) * tt)
            g = int(190 + (20 - 190) * tt)
            b = int(148 + (18 - 148) * tt)
        else:
            tt = (t - 0.55) / 0.45
            r = int(30 + (18 - 30) * tt)
            g = int(20 + (26 - 20) * tt)
            b = int(18 + (48 - 18) * tt)
        draw.line((0, y, W, y), fill=(max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), 255))

    # ── 2. AGED PARCHMENT TEXTURE (subtle noise overlay) ──────────────
    texture = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(texture)
    for _ in range(6000):
        px = rng.randint(0, W - 1)
        py = rng.randint(0, int(H * 0.55))
        va = rng.randint(2, 15)
        td.point((px, py), fill=(180, 160, 120, va))
    for _ in range(2000):
        px = rng.randint(0, W - 1)
        py = rng.randint(int(H * 0.55), H - 1)
        va = rng.randint(2, 10)
        td.point((px, py), fill=(10, 15, 30, va))
    texture = texture.filter(ImageFilter.GaussianBlur(1.5))
    img = Image.alpha_composite(img, texture)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 3. AGE STAINS / WATER RINGS ───────────────────────────────────
    stains = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stains)
    for _ in range(rng.randint(6, 10)):
        sx = rng.randint(200, 1400)
        sy = rng.randint(100, 1300)
        sr = rng.randint(80, 250)
        sa = rng.randint(6, 18)
        sd.ellipse((sx - sr, sy - sr, sx + sr, sy + sr),
                   fill=(180, 155, 100, sa))
    for _ in range(rng.randint(4, 7)):
        sx = rng.randint(100, 1500)
        sy = rng.randint(50, 1200)
        sr = rng.randint(30, 100)
        sa = rng.randint(3, 10)
        sd.ellipse((sx - sr, sy - sr, sx + sr, sy + sr),
                   fill=(218, 200, 165, sa))
    stains = stains.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, stains)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 4. RHUMB LINES (navigational web radiating from compass) ─────
    cx, cy = 780, 640  # compass center
    for angle_deg in range(0, 360, 15):
        ang = math.radians(angle_deg)
        dist = 1300
        if angle_deg % 45 == 0:
            a = rng.randint(25, 40)
            w = 2
        elif angle_deg % 90 == 0:
            a = rng.randint(35, 55)
            w = 3
        else:
            a = rng.randint(8, 18)
            w = 1
        ex = cx + int(math.cos(ang) * dist)
        ey = cy + int(math.sin(ang) * dist)
        ey = min(ey, int(H * 0.52))
        draw.line((cx, cy, ex, ey), fill=(*INK_FADED, a), width=w)

    # ── 5. COMPASS ROSE ───────────────────────────────────────────────
    draw.ellipse((cx - 120, cy - 120, cx + 120, cy + 120),
                 outline=(*INK_BROWN, 200), width=4)
    draw.ellipse((cx - 115, cy - 115, cx + 115, cy + 115),
                 outline=(*GOLD_OCHRE, 80), width=1)
    draw.ellipse((cx - 60, cy - 60, cx + 60, cy + 60),
                 outline=(*INK_BROWN, 120), width=2)

    cardinals = [(0, -1, "N"), (0, 1, "S"), (1, 0, "E"), (-1, 0, "W")]
    intercardinals = [(1, -1), (1, 1), (-1, 1), (-1, -1)]
    for dx, dy, label in cardinals:
        col = SEPIA_RED if label == "S" else (60, 52, 38)
        diamond = [
            (cx, cy),
            (cx + dx * 140 + dy * 12, cy + dy * 140 + dx * 12),
            (cx + dx * 150, cy + dy * 150),
            (cx + dx * 140 - dy * 12, cy + dy * 140 - dx * 12),
        ]
        draw.polygon(diamond, fill=(*col, 200))
        draw.polygon(diamond, outline=(*INK_BROWN, 220), width=2)

    for dx, dy in intercardinals:
        diamond = [
            (cx + dx * 70, cy + dy * 70),
            (cx + dx * 90 + dy * 6, cy + dy * 90 + dx * 6),
            (cx + dx * 95, cy + dy * 95),
            (cx + dx * 90 - dy * 6, cy + dy * 90 - dx * 6),
        ]
        draw.polygon(diamond, fill=(*INK_FADED, 150))
        draw.polygon(diamond, outline=(*INK_BROWN, 140), width=1)

    draw.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), fill=(*INK_BROWN, 230))

    # ── 6. TERRA AUSTRALIS INCOGNITA (coastline contour) ──────────────
    coast_base_y = 380
    coast_pts = []
    for wx in range(-100, W + 101, 4):
        noise = sum(rng.uniform(-1, 1) for _ in range(3)) * 12
        wave = math.sin(wx * 0.012) * 25 + math.sin(wx * 0.025 + 1.3) * 12 + math.sin(wx * 0.005 + 3.7) * 18
        c_y = coast_base_y + int(wave + noise)
        coast_pts.append((wx, c_y))

    cont_poly = coast_pts + [(-100, 0), (W + 100, 0)]
    draw.polygon(cont_poly, fill=(145, 118, 65, 60))
    draw.polygon(cont_poly, outline=(*INK_FADED, 120), width=2)

    for offset_ratio in [0.15, 0.25, 0.35, 0.45]:
        offset = offset_ratio * 35
        contour = [(wx, max(0, cy3 - offset + math.sin(wx * 0.008 + offset_ratio * 10) * 8))
                   for wx, cy3 in coast_pts if cy3 - offset > 0]
        if len(contour) > 5:
            draw.line(contour, fill=(*INK_FADED, 40), width=1)

    # ── 7. "TERRA AVSTRALIS INCOGNITA" label (stylized map text) ─────
    label_text = "TERRA AVSTRALIS INCOGNITA"
    label_x, label_y = 520, 175
    spacing = 14
    for ch_idx, ch in enumerate(label_text):
        if ch == ' ':
            continue
        lx = label_x + ch_idx * spacing
        ly = label_y + math.sin(ch_idx * 0.7) * 3
        glyph_type = rng.randint(0, 2)
        col = (rng.randint(100, 120), rng.randint(74, 92), rng.randint(48, 60), 80)
        if glyph_type == 0:
            draw.line((lx, ly, lx, ly + 18), fill=col, width=1)
            draw.line((lx, ly, lx + 8, ly), fill=col, width=1)
        elif glyph_type == 1:
            draw.line((lx, ly + 18, lx + 6, ly), fill=col, width=1)
        else:
            draw.arc((lx - 3, ly, lx + 3, ly + 18), 0, 180, fill=col, width=1)

    # ── 8. PORTUGUESE CARAVEL SILHOUETTE ──────────────────────────────
    ship_x = 960
    ship_y = 820
    sc = 1.6

    hull_pts = [
        (ship_x - int(120 * sc), ship_y),
        (ship_x - int(90 * sc), ship_y + int(12 * sc)),
        (ship_x + int(60 * sc), ship_y + int(14 * sc)),
        (ship_x + int(110 * sc), ship_y + int(4 * sc)),
        (ship_x + int(120 * sc), ship_y - int(4 * sc)),
        (ship_x + int(110 * sc), ship_y - int(12 * sc)),
        (ship_x + int(60 * sc), ship_y - int(16 * sc)),
        (ship_x - int(90 * sc), ship_y - int(14 * sc)),
    ]
    draw.polygon(hull_pts, fill=(30, 22, 14, 240))
    draw.polygon(hull_pts, outline=(*INK_BROWN, 200), width=2)
    draw.line((ship_x + int(110 * sc), ship_y - int(6 * sc),
               ship_x + int(170 * sc), ship_y - int(20 * sc)),
              fill=(35, 28, 18, 220), width=3)

    masts = [
        (ship_x - int(50 * sc), int(130 * sc)),
        (ship_x + int(15 * sc), int(160 * sc)),
        (ship_x + int(70 * sc), int(110 * sc)),
    ]
    for mx, mh in masts:
        draw.line((mx, ship_y - int(14 * sc), mx, ship_y - int(14 * sc) - mh),
                  fill=(35, 28, 18, 220), width=4)
        cn_y = ship_y - int(14 * sc) - mh + 20
        draw.rectangle((mx - 8, cn_y - 6, mx + 8, cn_y + 6), fill=(30, 22, 14, 220))

    # Main lateen sail
    main_top = (ship_x + 15, ship_y - 14 * sc - 160)
    main_bot = (ship_x + 15, ship_y - 14 * sc - 30)
    sail_left = (ship_x - int(55 * sc), ship_y - 14 * sc - 50)
    draw.polygon([main_top, main_bot, sail_left], fill=(195, 175, 140, 120))
    draw.polygon([main_top, main_bot, sail_left], outline=(*INK_FADED, 100), width=1)
    belly_pts = []
    for frac in range(11):
        t2 = frac / 10
        bx = main_top[0] + (sail_left[0] - main_top[0]) * t2
        by = main_top[1] + (sail_left[1] - main_top[1]) * t2 + math.sin(t2 * math.pi) * 18
        belly_pts.append((int(bx), int(by)))
    draw.line(belly_pts, fill=(*INK_BROWN, 100), width=2)

    # Foremast lateen
    fore_top = (ship_x - 50, ship_y - 14 * sc - 130)
    fore_bot = (ship_x - 50, ship_y - 14 * sc - 25)
    fore_left = (ship_x - int(95 * sc), ship_y - 14 * sc - 40)
    draw.polygon([fore_top, fore_bot, fore_left], fill=(190, 168, 132, 110))
    draw.polygon([fore_top, fore_bot, fore_left], outline=(*INK_FADED, 90), width=1)

    # Mizzen lateen
    miz_top = (ship_x + 70, ship_y - 14 * sc - 110)
    miz_bot = (ship_x + 70, ship_y - 14 * sc - 20)
    miz_right = (ship_x + int(115 * sc), ship_y - 14 * sc - 35)
    draw.polygon([miz_top, miz_bot, miz_right], fill=(185, 162, 125, 100))
    draw.polygon([miz_top, miz_bot, miz_right], outline=(*INK_FADED, 80), width=1)

    # Portuguese flag
    flag_pts = [
        (main_top[0] + 5, main_top[1]),
        (main_top[0] + 25, main_top[1] + 6),
        (main_top[0] + 25, main_top[1] + 22),
        (main_top[0] + 5, main_top[1] + 16),
    ]
    draw.polygon(flag_pts, fill=(160, 42, 36, 200))
    draw.ellipse((main_top[0] + 8, main_top[1] + 4, main_top[0] + 18, main_top[1] + 14),
                 fill=(200, 175, 80, 180))

    # ── 9. THE LAST MERIDIAN ──────────────────────────────────────────
    # Vertical longitude lines
    for lon_x in range(60, 1560, rng.randint(80, 140)):
        alpha = rng.randint(10, 30)
        draw.line((lon_x, 20, lon_x, int(H * 0.5)),
                  fill=(*INK_FADED, alpha), width=1)
        for tick_y in range(50, int(H * 0.5), 60):
            draw.line((lon_x - 3, tick_y, lon_x + 3, tick_y),
                      fill=(*INK_FADED, alpha // 2), width=1)

    for lat_y in range(60, int(H * 0.5), rng.randint(60, 100)):
        alpha = rng.randint(8, 25)
        draw.line((20, lat_y, W - 20, lat_y),
                  fill=(*INK_FADED, alpha), width=1)

    # The Last Meridian — prominent gold line with tremor
    last_meridian_x = 1220
    draw.line((last_meridian_x, 30, last_meridian_x, int(H * 0.52)),
              fill=(*GOLD_OCHRE, 140), width=3)
    tremor_band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td2 = ImageDraw.Draw(tremor_band)
    for tremor_y in range(0, int(H * 0.52), 2):
        offset_x = int(math.sin(tremor_y * 0.05 + rng.random() * 2) * 3)
        td2.point((last_meridian_x + offset_x, tremor_y),
                  fill=(*GOLD_OCHRE, 180))
    tremor_band = tremor_band.filter(ImageFilter.GaussianBlur(1))
    img = Image.alpha_composite(img, tremor_band)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 10. CARTOGRAPHER'S HANDS AND QUILL ────────────────────────────
    hands = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hands)
    hd.polygon([
        (1160, 1280), (1170, 1240), (1185, 1200), (1195, 1180),
        (1210, 1170), (1225, 1175), (1230, 1190), (1225, 1220),
        (1215, 1260), (1205, 1300), (1195, 1320),
    ], fill=(142, 118, 80, 30))
    hd.polygon([
        (1190, 1300), (1205, 1260), (1220, 1220), (1235, 1195),
        (1250, 1190), (1255, 1210), (1245, 1240), (1230, 1280),
        (1210, 1320),
    ], fill=(142, 118, 80, 25))
    hd.line((1220, 1170, 1280, 1080), fill=(*INK_BROWN, 60), width=3)
    hd.line((1280, 1080, 1300, 1060), fill=(*INK_FADED, 40), width=1)
    hands = hands.filter(ImageFilter.GaussianBlur(6))
    img = Image.alpha_composite(img, hands)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 11. DIVIDER / COMPASS TOOL ────────────────────────────────────
    tool_x, tool_y = 310, 860
    draw.line((tool_x - 30, tool_y + 20, tool_x - 50, tool_y + 60),
              fill=(140, 130, 115, 150), width=3)
    draw.line((tool_x + 30, tool_y + 20, tool_x + 50, tool_y + 60),
              fill=(140, 130, 115, 150), width=3)
    draw.ellipse((tool_x - 10, tool_y - 5, tool_x + 10, tool_y + 15),
                 fill=(160, 148, 130, 160))
    draw.ellipse((tool_x - 4, tool_y + 1, tool_x + 4, tool_y + 9),
                 fill=(55, 48, 38, 180))

    # ── 12. MUTINY BLOOD STAINS ───────────────────────────────────────
    blood = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(blood)
    for _ in range(rng.randint(4, 7)):
        bx = rng.randint(100, 1500)
        by = rng.randint(300, 1000)
        br = rng.randint(8, 40)
        ba = rng.randint(10, 35)
        bd.ellipse((bx - br, by - br, bx + br, by + br), fill=(*SEPIA_RED, ba))
    for _ in range(rng.randint(3, 5)):
        bx2 = rng.randint(200, 1400)
        by2 = rng.randint(400, 900)
        bd.line((bx2, by2, bx2 + rng.randint(20, 60), by2 + rng.randint(20, 40)),
                fill=(*SEPIA_RED, rng.randint(15, 40)), width=rng.randint(2, 4))
    blood = blood.filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(img, blood)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 13. SEA MONSTER CARTOUCHE ─────────────────────────────────────
    monster_x, monster_y = 250, 280
    for ci in range(4):
        cx3 = monster_x + ci * 22
        cy3 = monster_y + ci * 14 + int(math.sin(ci * 0.8) * 8)
        draw.ellipse((cx3 - 10, cy3 - 6, cx3 + 10, cy3 + 6),
                     fill=(*INK_FADED, 60))
    draw.ellipse((monster_x - 18, monster_y - 18, monster_x + 8, monster_y + 10),
                 fill=(*INK_FADED, 70))
    draw.ellipse((monster_x - 12, monster_y - 12, monster_x - 6, monster_y - 6),
                 fill=(*INK_BROWN, 100))
    draw.line((monster_x - 20, monster_y + 2, monster_x - 40, monster_y - 10),
              fill=(*SEPIA_RED, 50), width=2)
    draw.line((monster_x - 20, monster_y + 2, monster_x - 38, monster_y + 8),
              fill=(*SEPIA_RED, 50), width=2)
    tail_pts = [(monster_x + 88, monster_y + 56),
                (monster_x + 110, monster_y + 48),
                (monster_x + 118, monster_y + 36)]
    draw.line(tail_pts, fill=(*INK_FADED, 50), width=2)

    # ── 14. DECORATIVE MAP BORDER ─────────────────────────────────────
    border_inset = 18
    draw.rectangle((border_inset, border_inset, W - border_inset, int(H * 0.52)),
                   outline=(*INK_FADED, 100), width=2)
    draw.rectangle((border_inset + 6, border_inset + 6, W - border_inset - 6, int(H * 0.52) - 6),
                   outline=(*INK_FADED, 50), width=1)
    for corner_x, corner_y, flip_x, flip_y in [
        (border_inset + 8, border_inset + 8, 1, 1),
        (W - border_inset - 8, border_inset + 8, -1, 1),
        (border_inset + 8, int(H * 0.52) - 8, 1, -1),
        (W - border_inset - 8, int(H * 0.52) - 8, -1, -1),
    ]:
        draw.arc((corner_x - 12, corner_y - 12, corner_x + 12, corner_y + 12),
                 0, 90, fill=(*INK_FADED, 100), width=2)

    # ── 15. OCEAN DEPTH WAVE LINES ────────────────────────────────────
    wave_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wave_layer)
    for wi in range(6):
        base_y = int(H * 0.55) + wi * 85
        if base_y > H:
            break
        amp = 10 + wi * 3
        freq = 0.008 + wi * 0.001
        pts = []
        for wx in range(-20, W + 21, 8):
            wy = base_y + math.sin(wx * freq + wi * 1.2) * amp + math.sin(wx * freq * 2.3 + 2.1) * amp * 0.3
            pts.append((wx, wy))
        alpha = max(5, 25 - wi * 3)
        wcol = (50, 70, 110) if wi % 2 == 0 else (40, 55, 90)
        wd.line(pts, fill=(*wcol, alpha), width=max(1, 4 - wi // 2))
    wave_layer = wave_layer.filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(img, wave_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 16. BLURED INK SPLATTERS (failing eyesight) ──────────────────
    for _ in range(rng.randint(8, 15)):
        ix = rng.randint(200, 1400)
        iy = rng.randint(200, 1100)
        ir = rng.randint(4, 16)
        ia = rng.randint(10, 40)
        draw.ellipse((ix - ir, iy - ir, ix + ir, iy + ir), fill=(*INK_BROWN, ia))
        if rng.random() < 0.3:
            for _ in range(rng.randint(3, 6)):
                spx = ix + rng.randint(-30, 30)
                spy = iy + rng.randint(-30, 30)
                spr = rng.randint(1, 4)
                draw.ellipse((spx - spr, spy - spr, spx + spr, spy + spr),
                             fill=(*INK_BROWN, ia // 2))

    # ── 17. VIGNETTE ──────────────────────────────────────────────────
    vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(60 * max(0, 1 - vt))
        if vv > 0:
            vd.line((0, vy, vv, vy), fill=(0, 0, 0, 40))
            vd.line((W - vv, vy, W, vy), fill=(0, 0, 0, 40))
    for vx in range(W):
        vt = 1 - abs(vx - W // 2) / (W // 2)
        vv = int(40 * max(0, 1 - vt))
        if vv > 0:
            vd.line((vx, 0, vx, vv), fill=(0, 0, 0, 30))
            vd.line((vx, H - vv, vx, H), fill=(0, 0, 0, 50))
    img = Image.alpha_composite(img, vig)

    # ── 18. STANDARD TITLE PANEL ──────────────────────────────────────
    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, title, author, model)
    img.convert("RGB").save(op, "PNG", optimize=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    mp = a.metadata
    op_ = a.out
    make_cover(
        ROOT / mp if not mp.is_absolute() else mp,
        ROOT / op_ if not op_.is_absolute() else op_,
    )


if __name__ == "__main__":
    main()
