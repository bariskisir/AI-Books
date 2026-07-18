#!/usr/bin/env python3
"""Cover: The Broker of Last Looks — surveillance-monitor wall composition, cold clinical blue-gray palette with red danger alerts, multi-screen tableau centered on a hostage livestream."""
from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# Surveillance clinical palette: cold tech tones with neon hazard accents
BG_TOP = (18, 22, 30)
BG_BOT = (8, 10, 14)
ALERT_RED = (220, 30, 40)
COLD_CYAN = (100, 200, 230)
MONO_GREEN = (80, 180, 70)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (*BG_TOP, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Deep control-room gradient background
    for y in range(H):
        t = y / H
        r = int(BG_TOP[0] + (BG_BOT[0] - BG_TOP[0]) * t)
        g = int(BG_TOP[1] + (BG_BOT[1] - BG_TOP[1]) * t)
        b = int(BG_TOP[2] + (BG_BOT[2] - BG_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # CRT scanline texture over the upper surveillance area
    for y in range(0, 1700, 4):
        draw.line((0, y, W, y), fill=(255, 255, 255, 2))

    # ─── 3x2 surveillance monitor grid ───
    cols, rows = 3, 2
    sw, sh = 380, 260
    gap = 20
    grid_w = cols * sw + (cols - 1) * gap
    grid_h = rows * sh + (rows - 1) * gap
    gx0 = (W - grid_w) // 2
    gy0 = 170
    screens = []
    for r_idx in range(rows):
        for c_idx in range(cols):
            sx = gx0 + c_idx * (sw + gap)
            sy = gy0 + r_idx * (sh + gap)
            screens.append((sx, sy, sw, sh))

    # Draw monitor bezels
    for (sx, sy, sw, sh) in screens:
        draw.rectangle((sx, sy, sx + sw, sy + sh), fill=(25, 28, 35, 255), outline=(55, 60, 70, 200), width=2)
        im = 12
        draw.rectangle((sx + im, sy + im, sx + sw - im, sy + sh - im), fill=(8, 10, 16, 255))

    # ─── SCREEN 0 — Night-vision city skyline ───
    sx, sy, sw, sh = screens[0]
    ix, iy, iw, ih = sx + 12, sy + 12, sw - 24, sh - 24
    nd = ImageDraw.Draw(img, "RGBA")
    for bx in range(ix, ix + iw, 36):
        bh = random.randint(50, ih - 20)
        nd.rectangle((bx, iy + ih - bh, bx + 28, iy + ih), fill=(40, 80, 35, 140), outline=(60, 140, 50, 90), width=1)
        for wy in range(iy + ih - bh + 4, iy + ih - 4, 10):
            for wx in range(bx + 3, bx + 25, 8):
                if random.random() < 0.4:
                    nd.rectangle((wx, wy, wx + 4, wy + 4), fill=(80, 200, 60, random.randint(50, 140)))
    nd.text((ix + 4, iy + 4), "CAM-07  NV", fill=(80, 200, 70, 180))
    nd.text((ix + 4, iy + ih - 14), "UTC %s" % "%04d" % random.randint(0, 2359), fill=(80, 200, 70, 120))

    # ─── SCREEN 1 — Facial-recognition targeting crosshair ───
    sx, sy, sw, sh = screens[1]
    ix, iy, iw, ih = sx + 12, sy + 12, sw - 24, sh - 24
    nd = ImageDraw.Draw(img, "RGBA")
    cx, cy = ix + iw // 2, iy + ih // 2
    nd.line((cx - 40, cy, cx - 10, cy), fill=(*ALERT_RED, 140), width=2)
    nd.line((cx + 10, cy, cx + 40, cy), fill=(*ALERT_RED, 140), width=2)
    nd.line((cx, cy - 40, cx, cy - 10), fill=(*ALERT_RED, 140), width=2)
    nd.line((cx, cy + 10, cx, cy + 40), fill=(*ALERT_RED, 140), width=2)
    nd.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), outline=(*ALERT_RED, 100), width=1)
    nd.ellipse((cx - 22, cy - 30, cx + 22, cy + 30), outline=(100, 200, 220, 80), width=1)
    nd.line((cx - 26, cy + 40, cx + 26, cy + 40), fill=(100, 200, 220, 60), width=1)
    nd.text((ix + 4, iy + 4), "FACE ID: MATCH", fill=(100, 200, 220, 160))
    nd.text((ix + 4, iy + ih - 14), "TARGET: CROSS", fill=(100, 200, 220, 120))

    # ─── SCREEN 2 — Hexadecimal data stream ───
    sx, sy, sw, sh = screens[2]
    ix, iy, iw, ih = sx + 12, sy + 12, sw - 24, sh - 24
    nd = ImageDraw.Draw(img, "RGBA")
    hex_chars = "0123456789ABCDEF"
    for ri in range(14):
        ty = iy + 8 + ri * 17
        line = "".join(random.choice(hex_chars) for _ in range(random.randint(16, 42)))
        nd.text((ix + 4, ty), line, fill=(100, 200, 220, random.randint(40, 130)))

    # ─── SCREEN 3 — The hostage livestream (core plot element) ───
    sx, sy, sw, sh = screens[3]
    ix, iy, iw, ih = sx + 12, sy + 12, sw - 24, sh - 24
    # Red-tinted scene
    for ly in range(iy, iy + ih):
        lt = (ly - iy) / ih
        lr = int(35 + 40 * lt)
        lg = int(6 + 4 * lt)
        lb = int(8 + 4 * lt)
        draw.line((ix, ly, ix + iw, ly), fill=(lr, lg, lb, 190))
    nd = ImageDraw.Draw(img, "RGBA")
    # Hostage kneeling
    hx, hy = ix + iw // 2 - 25, iy + ih // 2 + 20
    nd.ellipse((hx - 16, hy - 12, hx + 16, hy + 28), fill=(12, 8, 10, 210))
    nd.ellipse((hx - 8, hy - 26, hx + 8, hy - 8), fill=(12, 8, 10, 210))
    # Hostage-taker standing
    tx = hx + 52
    nd.ellipse((tx - 14, hy - 35, tx + 14, hy + 12), fill=(6, 6, 8, 220))
    nd.ellipse((tx - 7, hy - 50, tx + 7, hy - 32), fill=(6, 6, 8, 220))
    nd.line((tx - 14, hy - 18, tx - 42, hy - 48), fill=(6, 6, 8, 210), width=3)
    nd.line((tx + 14, hy - 18, tx + 38, hy - 48), fill=(6, 6, 8, 210), width=3)
    # LIVESTREAM banner
    nd.rectangle((ix, iy, ix + iw, iy + 28), fill=(180, 18, 22, 210))
    nd.ellipse((ix + 8, iy + 8, ix + 18, iy + 18), fill=(255, 50, 50, 240))
    nd.text((ix + 24, iy + 6), "LIVE  HOSTAGE SITUATION", fill=(255, 255, 255, 220))
    nd.text((ix + iw - 80, iy + 6), "%02d:%02d" % (random.randint(1, 59), random.randint(0, 59)), fill=(255, 255, 255, 200))
    nd.text((ix + 8, iy + ih - 28), "STATUS: CONFIRMED DECEASED", fill=(255, 200, 50, 160))

    # ─── SCREEN 4 — Death-verification case file ───
    sx, sy, sw, sh = screens[4]
    ix, iy, iw, ih = sx + 12, sy + 12, sw - 24, sh - 24
    nd = ImageDraw.Draw(img, "RGBA")
    nd.text((ix + 8, iy + 8), "CASE: DEATH VERIFICATION #447", fill=(200, 200, 200, 160))
    nd.text((ix + 8, iy + 26), "SUBJ: DECEASED (CONFIRMED)", fill=(200, 200, 200, 120))
    nd.text((ix + 8, iy + 44), "REAPPEARED: HOSTAGE TAKER", fill=(200, 200, 200, 120))
    nd.line((ix + 8, iy + 62, ix + iw - 8, iy + 62), fill=(180, 180, 180, 60), width=1)
    # Photo placeholder
    phx, phy = ix + iw - 76, iy + 36
    nd.rectangle((phx, phy, phx + 58, phy + 64), outline=(180, 180, 180, 100), width=1)
    nd.ellipse((phx + 14, phy + 8, phx + 44, phy + 38), outline=(180, 180, 180, 80), width=1)
    nd.line((phx + 8, phy + 50, phx + 50, phy + 50), fill=(180, 180, 180, 60), width=1)
    for dri in range(4):
        filler = "".join(random.choice("abcdefghijklmnopqrstuvwxyz    ") for _ in range(random.randint(10, 28)))
        nd.text((ix + 8, iy + 76 + dri * 17), "— " + filler, fill=(140, 140, 140, 80))

    # ─── SCREEN 5 — Signal lost / static ───
    sx, sy, sw, sh = screens[5]
    ix, iy, iw, ih = sx + 12, sy + 12, sw - 24, sh - 24
    nd = ImageDraw.Draw(img, "RGBA")
    nd.rectangle((ix, iy, ix + iw, iy + ih), fill=(28, 30, 36, 255))
    for _ in range(120):
        x0 = ix + random.randint(0, iw - 1)
        y0 = iy + random.randint(0, ih - 1)
        x1 = x0 + random.randint(1, 5)
        y1 = y0 + random.randint(1, 2)
        nd.rectangle((x0, y0, x1, y1), fill=(120, 120, 130, random.randint(15, 55)))
    nd.text((ix + 40, iy + ih // 2 - 10), "SIGNAL LOST", fill=(180, 45, 45, 160))

    # ─── Ambient monitor glow ───
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for (sx, sy, sw, sh) in screens:
        gd.ellipse((sx - 40, sy - 40, sx + sw + 40, sy + sh + 40), fill=(40, 80, 140, 8))
    glow = glow.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # ─── Dangling cables beneath the monitors ───
    for _ in range(14):
        wx = random.randint(80, W - 80)
        wy = gy0 + rows * (sh + gap) - gap + random.randint(0, 40)
        pts = [(wx, wy)]
        for _ in range(random.randint(4, 9)):
            wx += random.randint(-18, 18)
            wy += random.randint(8, 22)
            pts.append((wx, wy))
        draw.line(pts, fill=(38, 40, 48, random.randint(60, 130)), width=random.randint(2, 3))

    # ─── Subtle tech border line above monitors ───
    draw.line((220, 150, W - 220, 150), fill=(60, 140, 200, 50), width=1)

    # ─── Dark gradient fade into title panel ───
    for y in range(1600, 1765):
        t = (y - 1600) / 165
        alpha = int(70 * t)
        draw.line((0, y, W, y), fill=(4, 6, 12, alpha))

    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op, "PNG", optimize=True)


def _standard_cover_resolve_title(local_vars):
    for key in ("title", "ti"):
        v = local_vars.get(key)
        if v:
            return str(v)
    return ""


def _standard_cover_resolve_author(local_vars):
    for key in ("author", "au"):
        v = local_vars.get(key)
        if v:
            return str(v)
    return "Barış Kısır"


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
