#!/usr/bin/env python3
"""Cover: A Crown of Severed Waves — disgraced admiral Iskra Velen, whose bones are living coral, bargains with a dying sea god who is hatching a new ocean from her bloodline."""
from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# Unique three-zone palette: wine-crimson sky → murky purple → abyssal teal depths
CR = (18, 5, 22)    # top — deep wine purple
CM = (68, 15, 47)   # middle — murky crimson-purple
CL = (8, 71, 70)    # bottom — abyssal teal


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")
    rng = random.Random(hash(title + "severed-waves-crown-unique"))

    # ── Three-zone gradient background ──────────────────────────
    img = Image.new("RGBA", (W, H), (*CR, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(H):
        t = y / H
        if t < 0.35:
            u = t / 0.35
            r = int(CR[0] + (CM[0] - CR[0]) * u + 6 * math.sin(u * 4.7))
            g = int(CR[1] + (CM[1] - CR[1]) * u + 3 * math.sin(u * 3.1))
            b = int(CR[2] + (CM[2] - CR[2]) * u - 5 * math.sin(u * 2.3))
        elif t < 0.65:
            u = (t - 0.35) / 0.30
            r = int(CM[0] + (CL[0] - CM[0]) * u)
            g = int(CM[1] + (CL[1] - CM[1]) * u)
            b = int(CM[2] + (CL[2] - CM[2]) * u)
        else:
            u = (t - 0.65) / 0.35
            r = int(CL[0] * (1 - u))
            g = int(CL[1] + 32 * u)
            b = int(CL[2] + 12 * u)
        draw.line(
            (0, y, W, y),
            fill=(max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), 255),
        )

    # ── Crown of Waves (five-peaked crown arch at top) ──────────
    for ci in range(10):
        wave_alpha = 160 - ci * 15
        if wave_alpha < 5:
            continue
        wave_base = 15 + ci * 14
        pts = []
        for wx in range(0, W + 4, 4):
            cx = wx / W
            # Five peaks at 0.1, 0.3, 0.5, 0.7, 0.9
            d_peak = min(abs(cx - p) for p in [0.1, 0.3, 0.5, 0.7, 0.9])
            peak_height = max(0, 1 - d_peak * 9) ** 1.5
            # Gentle base arch
            arch = 1 - (2 * cx - 1) ** 2
            wy = wave_base - 55 * peak_height - 18 * arch + rng.randint(-3, 3)
            pts.append((wx, max(0, wy)))
        wcol = (
            rng.randint(170, 235),
            rng.randint(50, 110),
            rng.randint(70, 130),
            max(5, wave_alpha),
        )
        draw.line(pts, fill=wcol, width=rng.randint(2, 6))

    # ── The Dying Sea God (semi-transparent looming figure) ─────
    god_cx, god_cy = W // 2, int(H * 0.30)
    glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)

    # Torso — layered shrinking ellipses for organic taper
    for ti in range(6):
        tw = int(620 - ti * 55)
        th = int(460 + ti * 18)
        alpha = 28 - ti * 4
        if alpha < 3:
            break
        gd.ellipse(
            (god_cx - tw // 2, god_cy - 40 + ti * 18, god_cx + tw // 2, god_cy + th),
            fill=(50 + ti * 6, 110 - ti * 8, 140 - ti * 10, alpha),
        )

    # Shoulder mantle (wide arc)
    gd.arc(
        (god_cx - 420, god_cy + 70, god_cx + 420, god_cy + 260),
        0, 180, fill=(65, 130, 150, 25), width=22,
    )

    # Head (two offset ovals for organic feel)
    gd.ellipse(
        (god_cx - 260, god_cy - 210, god_cx + 260, god_cy + 40),
        fill=(75, 140, 160, 12),
    )
    gd.ellipse(
        (god_cx - 230, god_cy - 190, god_cx + 230, god_cy + 20),
        fill=(55, 120, 140, 18),
    )

    # Composite the god's soft glow body
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(32))
    img = Image.alpha_composite(img, glow_layer)

    # ── God's Eyes (hollow glowing pits) ─────────────────────────
    for eye_x in (-105, 105):
        for er in range(14, 0, -1):
            ea = 85 - er * 6
            if ea < 5:
                continue
            draw.ellipse(
                (god_cx + eye_x - er * 5, god_cy - 75 - er * 4,
                 god_cx + eye_x + er * 5, god_cy - 75 + er * 4),
                fill=(rng.randint(210, 255), rng.randint(80, 140), rng.randint(40, 80), ea),
            )

    # ── The Hatching New Ocean (glowing orb in god's chest) ──────
    orb_cx, orb_cy = god_cx, god_cy + 230
    orb_r = 100

    # Outer radiance rings
    for gri in range(6, 0, -1):
        gr = orb_r + gri * 28
        draw.ellipse(
            (orb_cx - gr, orb_cy - gr, orb_cx + gr, orb_cy + gr),
            fill=(70, 180, 215, max(0, 42 - gri * 7)),
        )

    # Core orb
    draw.ellipse(
        (orb_cx - orb_r, orb_cy - orb_r, orb_cx + orb_r, orb_cy + orb_r),
        fill=(90, 200, 230, 65),
    )

    # Concentric rings — the ocean "forming" inside
    for ri in range(7):
        cr = orb_r * (1.0 - ri * 0.11)
        draw.ellipse(
            (orb_cx - cr, orb_cy - cr, orb_cx + cr, orb_cy + cr),
            outline=(150, 230, 255, 85 - ri * 11),
            width=2,
        )

    # Embryonic sparks inside the orb (the new ocean's birth)
    for _ in range(rng.randint(14, 22)):
        sx = orb_cx + max(-orb_r + 10, min(orb_r - 10, int(rng.gauss(0, orb_r * 0.35))))
        sy = orb_cy + max(-orb_r + 10, min(orb_r - 10, int(rng.gauss(0, orb_r * 0.35))))
        sr = rng.uniform(2, 7)
        draw.ellipse(
            (sx - sr, sy - sr, sx + sr, sy + sr),
            fill=(rng.randint(200, 255), rng.randint(225, 255), rng.randint(235, 255), rng.randint(60, 170)),
        )

    # ── Admiral Iskra Velen (silhouette with coral bones) ────────
    iskra_cx, iskra_cy = W // 2, int(H * 0.65)
    body_top = iskra_cy - 220
    body_bot = body_top + 240

    # Head
    draw.ellipse(
        (iskra_cx - 28, body_top - 35, iskra_cx + 28, body_top + 20),
        fill=(5, 8, 22, 235),
    )
    # Neck
    draw.rectangle(
        (iskra_cx - 12, body_top + 15, iskra_cx + 12, body_top + 45),
        fill=(5, 8, 22, 235),
    )

    # Torso polygon (shoulder → waist → hip)
    torso = [
        (iskra_cx - 52, body_top + 40),
        (iskra_cx + 52, body_top + 40),
        (iskra_cx + 38, body_top + 120),
        (iskra_cx + 50, body_top + 220),
        (iskra_cx - 50, body_top + 220),
        (iskra_cx - 38, body_top + 120),
    ]
    draw.polygon(torso, fill=(5, 8, 22, 235))

    # Legs (simple split)
    draw.polygon(
        [(iskra_cx - 50, body_top + 220), (iskra_cx + 50, body_top + 220),
         (iskra_cx + 30, body_top + 280), (iskra_cx - 30, body_top + 280)],
        fill=(5, 8, 22, 235),
    )

    # Arms reaching upward toward the sea god
    for side, ox in [(-1, -57), (1, 57)]:
        ax = iskra_cx + ox
        ay = body_top + 55
        # Upper arm
        draw.line(
            (ax, ay, ax + side * 55, ay - 65),
            fill=(7, 10, 24, 230), width=16,
        )
        # Forearm
        draw.line(
            (ax + side * 55, ay - 65, ax + side * 95, ay - 155),
            fill=(7, 10, 24, 230), width=12,
        )
        # Hand
        draw.ellipse(
            (ax + side * 90 - 8, ay - 163, ax + side * 100 + 8, ay - 147),
            fill=(5, 8, 22, 235),
        )

    # ── Coral Bones glowing through Iskra's body ─────────────────
    # Ribcage (biopminescent arcs)
    for ri in range(7):
        ry = body_top + 58 + ri * 15
        iw = 22 - ri * 1
        ow = 30 + ri * 2
        alpha = 110 - ri * 13
        coral_col = (rng.randint(200, 255), rng.randint(65, 130), rng.randint(85, 150), max(25, alpha))
        # Left ribs
        draw.arc(
            (iskra_cx - ow, ry, iskra_cx - iw, ry + 20),
            0, 180, fill=coral_col, width=3,
        )
        # Right ribs
        draw.arc(
            (iskra_cx + iw, ry, iskra_cx + ow, ry + 20),
            0, 180, fill=coral_col, width=3,
        )

    # Spine (vertebrae beads)
    for vi in range(13):
        vy = body_top + 48 + vi * 13
        draw.ellipse(
            (iskra_cx - 3, vy - 3, iskra_cx + 3, vy + 3),
            fill=(225, 85, 115, 140),
        )

    # Coral sprays erupting from shoulders and upper back
    for _ in range(rng.randint(8, 14)):
        ox = iskra_cx + rng.randint(-48, 48)
        oy = body_top + rng.randint(35, 95)
        _draw_coral_spray(draw, ox, oy, rng.randint(35, 100), 0, rng)

    # ── Bloodline Threads (crimson energy from Iskra to god's orb)
    for ti in range(rng.randint(8, 14)):
        sx = iskra_cx + rng.randint(-25, 25)
        sy = body_top + rng.randint(100, 170)
        ex = orb_cx + rng.randint(-50, 50)
        ey = orb_cy + rng.randint(-40, 40)
        mx = (sx + ex) // 2 + rng.randint(-90, 90)
        my = (sy + ey) // 2 + rng.randint(-50, 50)
        bcol = (rng.randint(140, 210), rng.randint(10, 40), rng.randint(20, 55), rng.randint(40, 110))
        draw.line([(sx, sy), (mx, my), (ex, ey)], fill=bcol, width=rng.randint(1, 3))

    # Blood-drop motes floating through the threads
    for _ in range(rng.randint(25, 50)):
        bx = rng.randint(max(100, iskra_cx - 80), min(W - 100, orb_cx + 80))
        by_low = min(body_top + 60, orb_cy + 60)
        by_high = max(body_top + 60, orb_cy + 60)
        by = rng.randint(by_low, by_high)
        br = rng.uniform(1.0, 3.5)
        draw.ellipse(
            (bx - br, by - br, bx + br, by + br),
            fill=(rng.randint(170, 225), rng.randint(15, 50), rng.randint(25, 60), rng.randint(35, 140)),
        )

    # ── Drowned City Ruins at the depths ─────────────────────────
    for cx in range(30, W - 20, rng.randint(70, 140)):
        h = rng.randint(50, 170)
        col_base = rng.randint(6, 18)
        y0 = 1720 - h
        pw = rng.randint(12, 30)
        draw.rectangle(
            (cx - pw, y0, cx + pw, 1740),
            fill=(col_base, col_base + 3, col_base + 6, 170),
        )
        # Broken capital
        if rng.random() < 0.4:
            draw.polygon(
                [(cx - pw, y0), (cx - pw // 3, y0 - rng.randint(5, 14)),
                 (cx + pw // 3, y0 - rng.randint(5, 14)), (cx + pw, y0)],
                fill=(col_base + 10, col_base + 13, col_base + 16, 160),
            )

    # Rubble scatter
    for _ in range(rng.randint(12, 24)):
        rx, ry = rng.randint(10, W - 10), rng.randint(1670, 1740)
        rw, rh = rng.randint(4, 12), rng.randint(2, 6)
        draw.ellipse(
            (rx - rw, ry - rh, rx + rw, ry + rh),
            fill=(rng.randint(8, 22), rng.randint(10, 24), rng.randint(12, 26), rng.randint(100, 180)),
        )

    # ── Bioluminescent particles (denser near key figures) ──────
    for _ in range(rng.randint(140, 200)):
        px = rng.randint(100, W - 100)
        py = rng.randint(100, 1550)
        d_god = math.hypot(px - god_cx, py - god_cy)
        d_isk = math.hypot(px - iskra_cx, py - iskra_cy)
        if d_god > 500 and d_isk > 400 and rng.random() > 0.15:
            continue
        pr = rng.uniform(1.0, 4.5)
        draw.ellipse(
            (px - pr, py - pr, px + pr, py + pr),
            fill=(rng.randint(150, 255), rng.randint(180, 255), rng.randint(200, 255), rng.randint(10, 65)),
        )

    # ── Vignette ─────────────────────────────────────────────────
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(38 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 90))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 90))

    # ── Save ─────────────────────────────────────────────────────
    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, title, author, model)
    img.convert("RGB").save(op, "PNG", optimize=True)


def _draw_coral_spray(draw, x, y, length, depth, rng):
    """Recursive coral branching erupting from the admiral's body (her living coral bones)."""
    if depth > 4 or length < 6:
        return
    for _ in range(rng.randint(2, 3)):
        ang = rng.uniform(-1.5, 1.5)
        ex = int(x + math.sin(ang) * length * rng.uniform(0.5, 1.0))
        ey = int(y - length * rng.uniform(0.4, 0.9))
        w = max(2, 6 - depth)
        col = (
            rng.randint(190, 255),
            rng.randint(60, 130),
            rng.randint(80, 150),
            max(40, 130 - depth * 20),
        )
        draw.line((x, y, ex, ey), fill=col, width=w)
        if rng.random() < 0.55:
            _draw_coral_spray(draw, ex, ey, int(length * rng.uniform(0.3, 0.6)), depth + 1, rng)


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
