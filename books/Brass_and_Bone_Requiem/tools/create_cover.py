#!/usr/bin/env python3
"""Cover: Brass and Bone Requiem — In an alternate Victorian London where necromantic jazz raises the dead to dance for tourist coin, a bone-fiddle player discovers her music can resurrect not just bodies but the true memories the Empire has scrubbed from history."""

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
rng.seed(428571931)

# ── Gaslamp Fantasy palette: Victorian night, brass, bone, fog, memory-cyan ──
NIGHT_TOP = (12, 10, 18)        # charcoal sky
NIGHT_BTM = (50, 20, 25)        # deep burgundy at street level
BRASS = (190, 140, 60)          # gaslamp glow
BRASS_DIM = (140, 100, 40)      # distant gaslamp
BONE = (210, 195, 175)          # spectral figure / bone fiddle
BONE_DIM = (160, 145, 125)      # distant spirits
IVORY = (230, 225, 210)         # bright highlight
FOG = (80, 75, 80)              # London fog
MEMORY = (80, 200, 210)         # cyan memory magic
MEMORY_DIM = (40, 140, 160)     # dim memory
WINDOW_WARM = (220, 170, 80)    # lit window
CRIMSON = (140, 30, 40)         # blood/bone accent
STONE = (45, 40, 45)            # cobblestone
STONE_HI = (65, 58, 62)         # cobblestone highlight


def gaussian(x, mu, sigma):
    return math.exp(-((x - mu) ** 2) / (2 * sigma * sigma))


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), NIGHT_TOP + (255,))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Night gradient: charcoal sky fading to burgundy street-level glow ──
    for y in range(H):
        t = y / H
        r = int(NIGHT_TOP[0] + (NIGHT_BTM[0] - NIGHT_TOP[0]) * t)
        g = int(NIGHT_TOP[1] + (NIGHT_BTM[1] - NIGHT_TOP[1]) * t)
        b = int(NIGHT_TOP[2] + (NIGHT_BTM[2] - NIGHT_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── Cobblestone street at bottom third ──
    street_y_start = 1800
    street_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(street_layer)
    for row in range(8):
        row_y = street_y_start + row * 45
        offset = (row % 2) * 40
        for col in range(-1, 22):
            cx = col * 80 + offset
            cy = row_y + rng.randint(-5, 5)
            stone_color = STONE if (col + row) % 2 == 0 else STONE_HI
            sd.ellipse((cx - 30, cy - 15, cx + 30, cy + 18), fill=stone_color + (180,))
    img = Image.alpha_composite(img, street_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Victorian building silhouettes in background mist ──
    buildings = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(buildings)
    building_profiles = [
        (0, 800, 160, 1300),
        (140, 850, 280, 1300),
        (260, 780, 420, 1300),
        (400, 880, 540, 1300),
        (520, 750, 680, 1300),
        (660, 820, 800, 1300),
        (780, 790, 940, 1300),
        (920, 860, 1060, 1300),
        (1040, 770, 1200, 1300),
        (1180, 840, 1320, 1300),
        (1300, 790, 1460, 1300),
        (1440, 850, 1600, 1300),
    ]
    for bx1, by1, bx2, by2 in building_profiles:
        # Building body
        bd.rectangle((bx1, by1, bx2, by2), fill=(20, 18, 25, 220))
        # Roof peak (townhouse style)
        peak = by1 - rng.randint(30, 70)
        bd.polygon([(bx1 - 10, by1), (bx1 + (bx2 - bx1) // 2, peak), (bx2 + 10, by1)], fill=(18, 16, 22, 220))
        # Windows
        for wy in range(by1 + 40, by2 - 60, 60):
            for wx in range(bx1 + 15, bx2 - 10, 35):
                if rng.random() > 0.3:
                    lit = rng.randint(0, 2)
                    if lit == 0:
                        wcol = WINDOW_WARM + (40,)
                    elif lit == 1:
                        wcol = (200, 170, 100, 20)
                    else:
                        continue
                    bd.rectangle((wx, wy, wx + 20, wy + 30), fill=wcol)
    img = Image.alpha_composite(img, buildings)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Gas lamps ──
    lamps = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lamps)

    def draw_lamp(lx, ly, height, brightness, warmth):
        """Draw a Victorian gas lamp post and its glow."""
        # Post
        ld.line((lx, ly, lx, ly + height), fill=(25, 22, 20, 200), width=6)
        # Lamp head (Victorian lantern)
        lh = 40
        lw = 25
        ld.rectangle((lx - lw, ly - lh, lx + lw, ly), fill=(30, 28, 25, 220))
        ld.polygon([(lx - lw - 5, ly - lh), (lx + lw + 5, ly - lh), (lx, ly - lh - 18)], fill=(30, 28, 25, 220))
        # Glow
        glow_rad = brightness
        for g in range(5):
            a = int(12 * (1 - g / 5) * warmth)
            r2 = glow_rad - g * 12
            ld.ellipse((lx - r2, ly - lh - r2 // 2, lx + r2, ly + r2 // 2), fill=BRASS + (a,))

    draw_lamp(100, 820, 420, 200, 1.0)
    draw_lamp(280, 880, 380, 160, 0.7)
    draw_lamp(480, 850, 400, 140, 0.5)
    draw_lamp(1500, 810, 430, 200, 1.0)
    draw_lamp(1320, 870, 390, 160, 0.7)
    draw_lamp(1120, 840, 410, 140, 0.5)
    draw_lamp(800, 950, 340, 100, 0.4)

    img = Image.alpha_composite(img, lamps)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Fog layer ──
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog)
    for fy in range(1000, 2000, 60):
        fw = rng.randint(300, 900)
        fx = rng.randint(-200, W - fw + 200)
        fa = rng.randint(15, 35)
        fd.ellipse((fx - fw // 2, fy, fx + fw // 2, fy + 120), fill=FOG + (fa,))
    fog = fog.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, fog)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Spectral dancing figures (raised dead) in the fog ──
    spectres = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    spd = ImageDraw.Draw(spectres)

    def draw_spectre(cx, cy, scale, opacity, is_dancer=True):
        """Draw a translucent spectral figure."""
        s = scale
        col = BONE + (opacity,)
        # Head
        spd.ellipse((cx - 10 * s, cy - 35 * s, cx + 10 * s, cy - 15 * s), fill=col)
        # Body
        if is_dancer and rng.random() > 0.5:
            spd.line((cx, cy - 15 * s, cx - 15 * s, cy - 35 * s), fill=col, width=max(2, int(3 * s)))
            spd.line((cx, cy - 15 * s, cx + 12 * s, cy - 20 * s), fill=col, width=max(2, int(3 * s)))
            spd.line((cx, cy - 10 * s, cx - 10 * s, cy + 20 * s), fill=col, width=max(2, int(3 * s)))
            spd.line((cx, cy - 10 * s, cx + 10 * s, cy + 25 * s), fill=col, width=max(2, int(3 * s)))
        else:
            spd.line((cx, cy - 15 * s, cx, cy + 20 * s), fill=col, width=max(2, int(3 * s)))
            spd.line((cx, cy + 5 * s, cx - 10 * s, cy + 15 * s), fill=col, width=max(2, int(3 * s)))
            spd.line((cx, cy + 5 * s, cx + 10 * s, cy + 15 * s), fill=col, width=max(2, int(3 * s)))
            spd.line((cx, cy - 15 * s, cx - 12 * s, cy - 28 * s), fill=col, width=max(2, int(3 * s)))
            spd.line((cx, cy - 15 * s, cx + 12 * s, cy - 28 * s), fill=col, width=max(2, int(3 * s)))

    for _ in range(14):
        sx = rng.randint(300, 1300)
        sy = rng.randint(1100, 1650)
        sc = 0.6 + rng.random() * 0.8
        opa = rng.randint(25, 65)
        draw_spectre(sx, sy, sc, opa, is_dancer=True)

    for _ in range(4):
        sx = rng.randint(200, 1400)
        sy = rng.randint(1400, 1750)
        sc = 1.0 + rng.random() * 0.6
        opa = rng.randint(40, 75)
        draw_spectre(sx, sy, sc, opa, is_dancer=rng.random() > 0.3)

    img = Image.alpha_composite(img, spectres)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Bone fiddle in foreground (silhouette) ──
    fiddle = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fid = ImageDraw.Draw(fiddle)

    fx, fy = 550, 1980
    fiddle_col = BONE_DIM + (200,)

    # Fiddle body (figure-8 shape)
    fid.ellipse((fx - 45, fy - 70, fx + 25, fy + 20), fill=fiddle_col)
    fid.ellipse((fx - 10, fy - 30, fx + 60, fy + 60), fill=fiddle_col)
    fid.ellipse((fx + 5, fy - 5, fx + 30, fy + 25), fill=(0, 0, 0, 180))
    fid.ellipse((fx - 20, fy - 20, fx + 5, fy + 10), fill=(0, 0, 0, 180))

    # Neck and scroll
    fid.line((fx + 5, fy - 65, fx + 15, fy - 200), fill=fiddle_col, width=8)
    fid.ellipse((fx + 5, fy - 215, fx + 25, fy - 195), fill=fiddle_col)

    # Strings
    for s_off in (-3, 0, 3):
        fid.line((fx + 10 + s_off, fy - 195, fx + 12 + s_off, fy - 50), fill=BONE + (160,), width=1)

    img = Image.alpha_composite(img, fiddle)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Memory magic: cyan motes swirling upward from the fiddle ──
    memory_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(memory_layer)

    for spiral in range(3):
        center_x = fx + 30 + spiral * 40
        center_y = fy - 250 - spiral * 60
        for t in range(60):
            angle = t * 0.4 + spiral * 2.0
            radius = 20 + t * 1.2
            mx = center_x + int(radius * math.cos(angle))
            my = center_y + int(radius * math.sin(angle) * 0.5 - t * 5)
            if my < 50 or my > 1800:
                continue
            alpha = max(10, 90 - t)
            size = max(2, 6 - t // 15)
            motes_col = MEMORY if t % 3 != 0 else (200, 230, 240)
            md.ellipse((mx - size, my - size, mx + size, my + size), fill=motes_col + (alpha,))
            if t > 0:
                prev_angle = (t - 1) * 0.4 + spiral * 2.0
                prev_radius = 20 + (t - 1) * 1.2
                px = center_x + int(prev_radius * math.cos(prev_angle))
                py = center_y + int(prev_radius * math.sin(prev_angle) * 0.5 - (t - 1) * 5)
                md.line((mx, my, px, py), fill=MEMORY_DIM + (alpha // 2,), width=1)

    for _ in range(80):
        mx = rng.randint(100, 1500)
        my = rng.randint(300, 1800)
        mr = rng.randint(2, 6)
        ma = rng.randint(15, 60)
        md.ellipse((mx - mr, my - mr, mx + mr, my + mr), fill=MEMORY + (ma,))

    for _ in range(30):
        mx = rng.randint(300, 1300)
        my = rng.randint(400, 1700)
        mr = rng.randint(2, 5)
        ma = rng.randint(10, 40)
        md.ellipse((mx - mr, my - mr, mx + mr, my + mr), fill=BRASS + (ma,))

    img = Image.alpha_composite(img, memory_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Subtle vignette ──
    vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette)
    for vy in range(H):
        vh = 1 - gaussian(vy, H // 2, H * 0.5)
        dark = int(60 * vh)
        if dark > 0:
            vd.line((0, vy, min(dark, W), vy), fill=(0, 0, 0, 60))
            vd.line((max(W - dark, 0), vy, W, vy), fill=(0, 0, 0, 60))
    img = Image.alpha_composite(img, vignette)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Title panel via shared utility ──
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
