#!/usr/bin/env python3
"""Cover: The Bone Button Archive — Forensic archivist Elena Voss's examination reveals a Victorian button is carved from a child's patella; dark Victorian body-horror with bone, crimson, and amber tones."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

RNG = random.Random()
RNG.seed(801423567)

# Victorian body-horror palette: deep maroon, aged bone, sickly amber gaslight, blood crimson
BG_TOP = (60, 18, 22)
BG_BOT = (12, 4, 6)
BONE = (215, 195, 165)
AMBER = (200, 160, 75)
CRIMSON = (140, 18, 28)
GOLD_TRIM = (170, 140, 60)


def _draw_small_button(draw, cx, cy, radius):
    """Draw a small Victorian bone button with four holes."""
    if radius < 4:
        return
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius),
                 fill=(*BONE, 200), outline=(160, 142, 110, 180), width=1)
    hr = max(1, radius // 4)
    for ox, oy in [(-radius * 0.25, -radius * 0.25), (radius * 0.25, -radius * 0.25),
                    (-radius * 0.25, radius * 0.25), (radius * 0.25, radius * 0.25)]:
        hx, hy = int(cx + ox), int(cy + oy)
        draw.ellipse((hx - hr, hy - hr, hx + hr, hy + hr), fill=(30, 15, 18, 200))


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), BG_TOP + (255,))
    draw = ImageDraw.Draw(img, "RGBA")

    # Deep maroon-to-black vertical gradient
    for y in range(H):
        t = y / H
        r = int(BG_TOP[0] + (BG_BOT[0] - BG_TOP[0]) * t)
        g = int(BG_TOP[1] + (BG_BOT[1] - BG_TOP[1]) * t)
        b = int(BG_TOP[2] + (BG_BOT[2] - BG_BOT[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # Victorian wainscoting panel lines (subtle architectural framing)
    for x in range(100, W - 50, 160):
        draw.line((x, 380, x, 1600), fill=(30, 12, 14, 40), width=2)
    for y_line in range(380, 1700, 300):
        draw.line((100, y_line, W - 50, y_line), fill=(30, 12, 14, 40), width=1)

    # The Collector's shadow — a tall, looming figure in the background
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.polygon([
        (180, 380), (260, 300), (340, 320),
        (380, 430), (420, 680), (480, 1280),
        (400, 1400), (300, 1400), (200, 1280),
        (220, 680), (180, 430),
    ], fill=(8, 2, 4, 100))
    shadow = shadow.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, shadow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Archive shelf (dark stained wood)
    shelf_y = 1480
    draw.rectangle((60, shelf_y, W - 60, shelf_y + 12), fill=(28, 12, 14, 230))
    draw.rectangle((60, shelf_y + 12, W - 60, shelf_y + 18), fill=(8, 4, 5, 200))

    # Specimen jars with small buttons on the shelf
    for sx in range(120, W - 80, 100):
        if RNG.random() < 0.78:
            jar_w, jar_h = 40, 60
            jx = sx - jar_w // 2
            jy = shelf_y - jar_h - 5
            draw.rectangle((jx, jy, jx + jar_w, shelf_y - 5),
                           fill=(50, 35, 25, 180), outline=(35, 25, 20, 200), width=1)
            draw.rectangle((jx + 2, jy + 2, jx + jar_w // 3, shelf_y - 7),
                           fill=(*AMBER, 12))
            br = RNG.randint(6, 12)
            _draw_small_button(draw, sx, jy + jar_h // 2 + 5, br)

    # Catalog card on the shelf
    card_x, card_y = 180, shelf_y + 30
    draw.rectangle((card_x, card_y, card_x + 220, card_y + 55),
                   fill=(60, 45, 35, 200), outline=(40, 30, 25, 255), width=1)
    draw.rectangle((card_x + 6, card_y + 6, card_x + 214, card_y + 49),
                   fill=(100, 85, 70, 180))
    for i, tw in enumerate([90, 65, 120, 45]):
        lx = card_x + 12
        ly = card_y + 8 + i * 11
        draw.line((lx, ly, lx + tw, ly), fill=(50, 40, 35, 200), width=2)

    # Scattered loose buttons on the shelf
    for _ in range(5):
        sx = RNG.randint(550, W - 130)
        sy = RNG.randint(shelf_y + 25, shelf_y + 90)
        sr = RNG.randint(8, 14)
        _draw_small_button(draw, sx, sy, sr)

    # ── Central focal point: the examined button ──────────────────────────
    cx, cy = W // 2, 800
    btn_r = 175

    # Warm examination glow around the button (like a magnifying glass focus)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((cx - btn_r - 50, cy - btn_r - 50, cx + btn_r + 50, cy + btn_r + 50),
               fill=(*AMBER, 15))
    glow = glow.filter(ImageFilter.GaussianBlur(25))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Magnifying glass brass frame
    mg_r = btn_r + 30
    draw.ellipse((cx - mg_r, cy - mg_r, cx + mg_r, cy + mg_r),
                 outline=(*GOLD_TRIM, 200), width=6)
    draw.ellipse((cx - mg_r - 3, cy - mg_r - 3, cx + mg_r + 3, cy + mg_r + 3),
                 outline=(*GOLD_TRIM, 80), width=2)
    # Handle angling down-right
    handle_angle = math.pi * 0.72
    hx1 = cx + math.cos(handle_angle) * mg_r
    hy1 = cy + math.sin(handle_angle) * mg_r
    hx2 = cx + math.cos(handle_angle) * (mg_r + 220)
    hy2 = cy + math.sin(handle_angle) * (mg_r + 220)
    draw.line((hx1, hy1, hx2, hy2), fill=(*GOLD_TRIM, 200), width=8)
    draw.line((hx1, hy1, hx2, hy2), fill=(*GOLD_TRIM, 120), width=4)

    # Glass lens highlight
    draw.ellipse((cx - mg_r + 12, cy - mg_r + 12, cx - mg_r // 3, cy - mg_r // 3),
                 fill=(*AMBER, 22))

    # THE BUTTON — aged bone, semi-translucent
    draw.ellipse((cx - btn_r, cy - btn_r, cx + btn_r, cy + btn_r),
                 fill=(*BONE, 230), outline=(160, 142, 110, 255), width=3)

    # Patella (kneecap) bone ghost visible INSIDE the button
    pat_r = int(btn_r * 0.55)
    pat_points = []
    for i in range(24):
        angle = i * math.tau / 24
        vary = 1.0 + 0.15 * math.sin(angle * 3 + 0.5) + 0.1 * math.cos(angle * 2)
        pr = pat_r * vary
        px = cx + math.cos(angle) * pr
        py = cy + math.sin(angle) * pr * 0.88
        pat_points.append((int(px), int(py)))
    draw.polygon(pat_points, fill=(190, 170, 140, 80), outline=(170, 150, 120, 60))

    # Trabecular bone structure lines inside the patella
    for _ in range(18):
        angle = RNG.random() * math.tau
        dist = RNG.random() * pat_r * 0.5
        sx = int(cx + math.cos(angle) * dist)
        sy = int(cy + math.sin(angle) * dist * 0.88)
        ex = int(sx + math.cos(angle + (RNG.random() - 0.5) * 0.8) * pat_r * 0.25)
        ey = int(sy + math.sin(angle + (RNG.random() - 0.5) * 0.8) * pat_r * 0.25)
        draw.line((sx, sy, ex, ey), fill=(150, 130, 100, 40), width=2)

    # Decorative rim carving on the button edge
    for i in range(36):
        angle = i * math.tau / 36
        r1, r2 = btn_r - 5, btn_r
        x1 = int(cx + math.cos(angle) * r1)
        y1 = int(cy + math.sin(angle) * r1)
        x2 = int(cx + math.cos(angle) * r2)
        y2 = int(cy + math.sin(angle) * r2)
        draw.line((x1, y1, x2, y2), fill=(180, 162, 132, 80), width=1)

    # Four button holes
    hole_r = 14
    offsets = [
        (-btn_r * 0.3, -btn_r * 0.3),
        (btn_r * 0.3, -btn_r * 0.3),
        (-btn_r * 0.3, btn_r * 0.3),
        (btn_r * 0.3, btn_r * 0.3),
    ]
    for ox, oy in offsets:
        hx, hy = int(cx + ox), int(cy + oy)
        draw.ellipse((hx - hole_r, hy - hole_r, hx + hole_r, hy + hole_r),
                     fill=(30, 15, 18, 255))
        draw.ellipse((hx - hole_r // 2, hy - hole_r // 2,
                      hx + hole_r // 2, hy + hole_r // 2),
                     fill=(10, 5, 6, 255))

    # Blood-red silk threads dangling from each hole
    for ox, oy in offsets:
        tx, ty = int(cx + ox), int(cy + oy)
        pts = [(tx, ty)]
        segs = RNG.randint(5, 9)
        for _ in range(segs):
            nx = pts[-1][0] + RNG.randint(-6, 6)
            ny = pts[-1][1] + RNG.randint(12, 25)
            pts.append((nx, ny))
        draw.line(pts, fill=(*CRIMSON, RNG.randint(140, 210)), width=RNG.randint(2, 4))

    # Gas lamp illumination from upper-left
    gas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd2 = ImageDraw.Draw(gas)
    gd2.ellipse((50, 30, 350, 330), fill=(*AMBER, 35))
    gd2.ellipse((100, 60, 300, 270), fill=(*AMBER, 20))
    gd2.ellipse((140, 90, 260, 220), fill=(255, 225, 160, 10))
    gas = gas.filter(ImageFilter.GaussianBlur(50))
    img = Image.alpha_composite(img, gas)
    draw = ImageDraw.Draw(img, "RGBA")

    # Vignette — darken edges
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(100 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 50))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 50))

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
