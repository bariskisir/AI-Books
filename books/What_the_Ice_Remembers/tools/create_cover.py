#!/usr/bin/env python3
"""Cover: What the Ice Remembers — A xenolinguist drilling into a frozen ocean on a moon of Saturn finds preserved in the ice not microorganisms but a complete alien conversation frozen mid-dialogue a million years ago, and thawing the last sentence unleashes an ancient signal straight back to the extinct civilization's homeworld."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

random.seed(5522113377)

# Cold alien palette for ice moon + frozen dialogue
SPACE_TOP = (5, 5, 22)
SPACE_BOT = (10, 18, 38)
ICE_SURF_COLOR = (165, 190, 205)
STRATA_COLORS = [
    (140, 172, 198),
    (105, 148, 182),
    (78, 122, 165),
    (58, 98, 148),
    (45, 78, 130),
    (35, 62, 115),
    (28, 50, 100),
    (22, 42, 88),
    (18, 35, 76),
    (14, 28, 65),
    (12, 24, 58),
    (10, 20, 50),
    (8, 16, 45),
    (6, 12, 38),
    (5, 10, 32),
]
SIGNAL_BRIGHT = (140, 235, 255)
SIGNAL_CORE = (220, 248, 255)
GLYPH_A = (255, 205, 65)
GLYPH_B = (255, 170, 40)
AURORA_COLORS = [(70, 240, 170), (150, 75, 240), (90, 180, 250)]


def _glyph(draw, cx, cy, sz, variant, fill):
    """Draw one of 6 alien character shapes around (cx, cy)."""
    h = sz // 2
    if variant == 0:  # diamond
        draw.polygon([(cx, cy - h), (cx + h, cy), (cx, cy + h), (cx - h, cy)], outline=fill, width=2)
    elif variant == 1:  # nested rings
        for r in (h, h * 2 // 3, h // 3):
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=fill, width=1 if r < h else 2)
    elif variant == 2:  # inverted Y
        draw.line((cx, cy - h, cx, cy + h), fill=fill, width=2)
        draw.line((cx, cy, cx + h, cy + h // 2), fill=fill, width=2)
        draw.line((cx, cy, cx - h, cy + h // 2), fill=fill, width=2)
    elif variant == 3:  # wave
        pts = []
        for i in range(-h, h + 1, 2):
            a = i * 0.35
            pts.append((cx + i, cy + int(math.sin(a) * h // 2)))
        draw.line(pts, fill=fill, width=2)
    elif variant == 4:  # arrow chevrons
        for dy in (-h // 2, 0, h // 2):
            draw.line((cx - h, cy + dy, cx, cy + dy + h // 3), fill=fill, width=2)
            draw.line((cx, cy + dy + h // 3, cx + h, cy + dy), fill=fill, width=2)
    elif variant == 5:  # circle with cross
        draw.ellipse((cx - h, cy - h, cx + h, cy + h), outline=fill, width=2)
        draw.line((cx - h, cy, cx + h, cy), fill=fill, width=1)
        draw.line((cx, cy - h, cx, cy + h), fill=fill, width=1)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 1. Space gradient ───────────────────────────────────────────────────
    for y in range(H):
        t = y / H
        r = int(SPACE_TOP[0] + (SPACE_BOT[0] - SPACE_TOP[0]) * t)
        g = int(SPACE_TOP[1] + (SPACE_BOT[1] - SPACE_TOP[1]) * t)
        b = int(SPACE_TOP[2] + (SPACE_BOT[2] - SPACE_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── 2. Stars ────────────────────────────────────────────────────────────
    for _ in range(120):
        sx = random.randint(0, W - 1)
        sy = random.randint(0, H // 2 - 1)
        sr = random.uniform(0.5, 2.0)
        sa = random.randint(80, 220)
        draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=(255, 255, 255, sa))

    # ── 3. Saturn in the sky ────────────────────────────────────────────────
    scx, scy = 260, 180
    # atmosphere glow
    for rad in (55, 80, 110):
        draw.ellipse((scx - rad, scy - rad, scx + rad, scy + rad), fill=(180, 165, 130, 6))
    # planet body
    draw.ellipse((scx - 42, scy - 36, scx + 42, scy + 36), fill=(192, 175, 138, 210))
    for i in range(5):
        by = scy - 24 + i * 12
        o = int(15 * math.sin(i * 1.7))
        draw.line((scx - 38 + o, by, scx + 38 + o, by), fill=(172, 158, 122, 90), width=3)
    # rings (front arc)
    for rw in (50, 62, 76):
        for ang in range(5, 176, 2):
            a = math.radians(ang)
            rx = (rw + random.uniform(-1, 1)) * math.cos(a)
            ry = (rw * 0.32 + random.uniform(-1, 1)) * math.sin(a)
            ca = random.randint(35, 75)
            draw.ellipse((scx + rx - 2, scy + ry - 2, scx + rx + 2, scy + ry + 2),
                         fill=(205, 182, 140, ca))

    # ── 4. Aurora bands ─────────────────────────────────────────────────────
    aur = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ad = ImageDraw.Draw(aur)
    for _ in range(8):
        ax = random.randint(150, 1450)
        aw = random.randint(80, 350)
        ah = random.randint(60, 220)
        ac = random.choice(AURORA_COLORS)
        ad.ellipse((ax - aw, 30 - ah // 2, ax + aw, 30 + ah // 2),
                   fill=(ac[0], ac[1], ac[2], random.randint(6, 18)))
    for _ in range(5):
        ax = random.randint(200, 1400)
        aw = random.randint(60, 180)
        ah = random.randint(100, 280)
        ac = AURORA_COLORS[0]
        ad.ellipse((ax - aw, 80 - ah // 2, ax + aw, 80 + ah // 2),
                   fill=(ac[0], ac[1], ac[2], random.randint(4, 12)))
    aur = aur.filter(ImageFilter.GaussianBlur(28))
    img = Image.alpha_composite(img, aur)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 5. Icy surface ──────────────────────────────────────────────────────
    surface_y = 580
    ice = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    idr = ImageDraw.Draw(ice)
    surf_pts = []
    for x in range(0, W + 1, 3):
        n = sum(random.uniform(-25, 25) for _ in range(5)) / 5
        y = surface_y + n
        surf_pts.append((x, y))
    surf_pts.append((W, H))
    surf_pts.append((0, H))
    idr.polygon(surf_pts, fill=(*ICE_SURF_COLOR, 185))

    # surface details — lighter cracks
    for i in range(0, min(W, len(surf_pts) - 2), 2):
        if surf_pts[i][1] < surf_pts[min(i + 2, len(surf_pts) - 2)][1]:
            idr.line((surf_pts[i][0], surf_pts[i][1], surf_pts[i + 2][0], surf_pts[i + 2][1]),
                     fill=(195, 212, 222, 80), width=2)
    ice = ice.filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(img, ice)
    draw = ImageDraw.Draw(img, "RGBA")

    # surface cracks
    for _ in range(20):
        cx = random.randint(0, W)
        cy = surface_y + random.randint(0, 30)
        pts = [(cx, cy)]
        for _ in range(random.randint(4, 10)):
            cx += random.randint(-12, 12)
            cy += random.randint(3, 18)
            pts.append((cx, cy))
        draw.line(pts, fill=(210, 225, 235, random.randint(25, 70)), width=1)

    # ── 6. Drilling rig / lander ────────────────────────────────────────────
    rig_x = W // 2 - 40
    rig_base = surface_y + 2
    # body
    draw.polygon([(rig_x - 35, rig_base - 55), (rig_x + 35, rig_base - 55),
                  (rig_x + 25, rig_base), (rig_x - 25, rig_base)],
                 fill=(55, 65, 75, 230))
    # landing legs
    for lx in (rig_x - 25, rig_x + 25):
        draw.line((lx, rig_base - 5, lx + (-12 if lx < rig_x else 12), rig_base + 12),
                  fill=(90, 95, 105, 200), width=3)
    # tower
    draw.rectangle((rig_x - 6, rig_base - 115, rig_x + 6, rig_base - 55),
                   fill=(72, 78, 88, 230))
    for by in (rig_base - 105, rig_base - 88, rig_base - 72):
        draw.line((rig_x - 6, by, rig_x + 6, by), fill=(115, 120, 130, 180), width=2)
    # derrick top
    draw.polygon([(rig_x - 12, rig_base - 125), (rig_x + 12, rig_base - 125),
                  (rig_x, rig_base - 142)], fill=(62, 68, 78, 230))
    # warm work light
    for rad in (4, 10, 18):
        draw.ellipse((rig_x - rad, rig_base - 130 - rad, rig_x + rad, rig_base - 130 + rad),
                     fill=(255, 200, 70, 12 - rad // 2))

    # ── 7. Scientist silhouette ─────────────────────────────────────────────
    sx = rig_x + 65
    sy = surface_y + 2
    draw.line((sx, sy - 22, sx, sy), fill=(18, 22, 35, 220), width=2)
    draw.ellipse((sx - 3, sy - 27, sx + 3, sy - 22), fill=(18, 22, 35, 220))

    # ── 8. Borehole cross-section ───────────────────────────────────────────
    bx = W // 2
    by_top = surface_y + 15
    by_bot = 1720
    bw = 45  # half-width

    # dark shaft
    draw.rectangle((bx - bw, by_top, bx + bw, by_bot), fill=(6, 10, 24, 240))

    # ice strata on borehole walls
    n_strata = len(STRATA_COLORS)
    strata_h = (by_bot - by_top) // n_strata
    for i, sc in enumerate(STRATA_COLORS):
        sy0 = by_top + i * strata_h
        sy1 = sy0 + strata_h if i < n_strata - 1 else by_bot
        # left wall band
        draw.rectangle((bx - bw - 28, sy0, bx - bw, sy1), fill=(sc[0], sc[1], sc[2], 155))
        # right wall band
        draw.rectangle((bx + bw, sy0, bx + bw + 28, sy1), fill=(sc[0], sc[1], sc[2], 155))
        # horizontal strata lines
        for ly in range(sy0, sy1, random.randint(6, 14)):
            if ly >= by_bot:
                break
            lc = (min(255, sc[0] + 25), min(255, sc[1] + 25), min(255, sc[2] + 25))
            draw.line((bx - bw - 28, ly, bx - bw, ly), fill=(*lc, 70), width=1)
            draw.line((bx + bw, ly, bx + bw + 28, ly), fill=(*lc, 70), width=1)

    # ── 9. Frozen alien conversation (glyphs) ────────────────────────────────
    gy = by_top + 100
    while gy < by_bot - 80:
        # speaker A (left wall)
        if random.random() < 0.65:
            gs = random.randint(12, 26)
            gx = bx - bw - 14
            gv = random.randint(0, 5)
            _glyph(draw, gx, gy, gs, gv, (GLYPH_A[0], GLYPH_A[1], GLYPH_A[2], random.randint(110, 195)))
        # speaker B (right wall)
        if random.random() < 0.65:
            gs = random.randint(10, 22)
            gx = bx + bw + 14
            gv = (random.randint(0, 5) + 3) % 6
            _glyph(draw, gx, gy + random.randint(-12, 12), gs, gv,
                   (GLYPH_B[0], GLYPH_B[1], GLYPH_B[2], random.randint(90, 170)))
        gy += random.randint(22, 45)

    # ── 10. Dense glyph clusters (the "conversation nodes") ─────────────────
    for _ in range(4):
        cl_y = by_top + random.randint(180, by_bot - by_top - 180)
        side = random.choice([-1, 1])
        cl_x = bx + side * (bw + 14)
        for _ in range(random.randint(4, 7)):
            gs = random.randint(6, 14)
            gx = cl_x + random.randint(-8, 8)
            gy = cl_y + random.randint(-12, 12)
            gv = random.randint(0, 5)
            _glyph(draw, gx, gy, gs, gv, (GLYPH_A[0], GLYPH_A[1], GLYPH_A[2], random.randint(100, 170)))

    # ── 11. "Last sentence" thawing glow at borehole bottom ─────────────────
    glow_y = by_bot - 20
    for rad in (75, 50, 30, 15):
        al = max(3, 28 - rad)
        draw.ellipse((bx - rad, glow_y - rad, bx + rad, glow_y + rad),
                     fill=(255, 185, 50, al))
    for i in range(4):
        r = 18 + i * 10
        draw.ellipse((bx - r, glow_y - r, bx + r, glow_y + r),
                     outline=(255, 210, 80, 70 - i * 15), width=2)

    # ── 12. Signal beam (vertical, expanding upward) ────────────────────────
    sig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sig)

    # wide glow cone
    sd.polygon([(bx - 15, glow_y), (bx + 15, glow_y),
                (bx + bw + 50, by_top - 80), (bx - bw - 50, by_top - 80)],
               fill=(SIGNAL_BRIGHT[0], SIGNAL_BRIGHT[1], SIGNAL_BRIGHT[2], 6))
    # tight beam
    sd.polygon([(bx - 2, glow_y), (bx + 2, glow_y),
                (bx + bw - 5, by_top), (bx - bw + 5, by_top)],
               fill=(SIGNAL_CORE[0], SIGNAL_CORE[1], SIGNAL_CORE[2], 35))
    sig = sig.filter(ImageFilter.GaussianBlur(6))
    img = Image.alpha_composite(img, sig)
    draw = ImageDraw.Draw(img, "RGBA")

    # sharp beam core
    for y in range(by_top, glow_y, 3):
        t = (y - by_top) / (glow_y - by_top)
        w = int(2 + t * bw * 0.4)
        al = int(50 + 45 * t)
        draw.line((bx - w, y, bx + w, y), fill=(*SIGNAL_CORE, al))

    # signal escaping into space above the ice
    for y in range(30, by_top, 3):
        t = 1 - (y - 30) / (by_top - 30)
        w = int(2 + t * 20)
        al = int(12 * t)
        draw.line((bx - w, y, bx + w, y), fill=(*SIGNAL_BRIGHT, al))

    # particles riding the beam
    for _ in range(40):
        t = random.random()
        py = by_top + t * (glow_y - by_top)
        tw = (py - by_top) / (glow_y - by_top)
        beam_w = 2 + tw * bw * 0.4
        px = bx + random.uniform(-beam_w, beam_w)
        ps = random.randint(1, 3)
        draw.ellipse((px - ps, py - ps, px + ps, py + ps),
                     fill=(SIGNAL_CORE[0], SIGNAL_CORE[1], SIGNAL_CORE[2], random.randint(80, 210)))

    # ── 13. Borehole rim ─────────────────────────────────────────────────────
    draw.ellipse((bx - bw, by_top - 3, bx + bw, by_top + 5), fill=(4, 6, 18, 230))
    draw.arc((bx - bw - 4, by_top - 2, bx + bw + 4, by_top + 4), 0, 180,
             fill=(30, 38, 55, 100), width=2)

    # surface glow around borehole
    for rad in range(8, 55, 10):
        al = max(2, 14 - rad // 5)
        draw.ellipse((bx - rad, by_top - rad, bx + rad, by_top + rad),
                     fill=(*SIGNAL_BRIGHT, al))

    # ── 14. Vignette ────────────────────────────────────────────────────────
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(45 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 85))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 85))

    # ── 15. Title panel ─────────────────────────────────────────────────────
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
