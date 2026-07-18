#!/usr/bin/env python3
"""Cover: SpindleHearts — Master Spinner Elara Threadwell discovers a queen's
heart hidden in the threads of memory, woven into the royal tapestry."""

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
rng.seed(918273645)

def hsla_to_rgba(h, s, l, a=255):
    """Convert HSL to RGBA (all 0-1 range except alpha 0-255)."""
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h * 6) % 2 - 1))
    m = l - c / 2
    if h < 1/6: r1, g1, b1 = c, x, 0
    elif h < 2/6: r1, g1, b1 = x, c, 0
    elif h < 3/6: r1, g1, b1 = 0, c, x
    elif h < 4/6: r1, g1, b1 = 0, x, c
    elif h < 5/6: r1, g1, b1 = x, 0, c
    else: r1, g1, b1 = c, 0, x
    return (int((r1 + m) * 255), int((g1 + m) * 255), int((b1 + m) * 255), a)

def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    # ── Background: deep royal purple-to-crimson gradient ──
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        # top: dark purple (0.75, 0.6, 0.15) -> mid: crimson (0.95, 0.7, 0.2) -> bottom: near-black (0.8, 0.5, 0.05)
        h = 0.78 - 0.12 * t
        s = 0.55 + 0.25 * t
        l = 0.15 + 0.08 * math.sin(t * math.pi)
        r, g, b, _ = hsla_to_rgba(h, s, l)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── Subtle radial glow from center-top (magical thread-light) ──
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((W//2 - 600, -100, W//2 + 600, 1100), fill=(200, 180, 230, 18))
    gd.ellipse((W//2 - 350, 50, W//2 + 350, 800), fill=(210, 190, 240, 12))
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Ornate loom frame ──
    loom_cx = W // 2
    loom_top = 180
    loom_bot = 1550
    loom_w = 700

    # Frame pillars
    pillar_color = (60, 40, 55, 220)
    for side_x in (loom_cx - loom_w // 2, loom_cx + loom_w // 2):
        # Main pillar
        draw.rectangle((side_x - 18, loom_top, side_x + 18, loom_bot), fill=pillar_color)
        # Ornamental grooves
        for gy in range(loom_top + 40, loom_bot, 60):
            draw.rectangle((side_x - 22, gy, side_x + 22, gy + 6), fill=(80, 55, 70, 200))
            draw.rectangle((side_x - 22, gy + 28, side_x + 22, gy + 34), fill=(80, 55, 70, 200))
        # Capital-top ornament
        draw.polygon([
            (side_x - 30, loom_top), (side_x + 30, loom_top),
            (side_x + 40, loom_top - 30), (side_x - 40, loom_top - 30)
        ], fill=(80, 55, 70, 230))
        draw.ellipse((side_x - 12, loom_top - 50, side_x + 12, loom_top - 26), fill=(160, 130, 100, 180))

    # Crossbeam top
    draw.rectangle((loom_cx - loom_w // 2 - 10, loom_top - 55, loom_cx + loom_w // 2 + 10, loom_top - 10), fill=pillar_color)
    draw.rectangle((loom_cx - loom_w // 2 - 6, loom_top - 65, loom_cx + loom_w // 2 + 6, loom_top - 55), fill=(80, 55, 70, 220))
    # Crossbeam bottom (seat)
    draw.rectangle((loom_cx - loom_w // 2 - 15, loom_bot - 20, loom_cx + loom_w // 2 + 15, loom_bot + 10), fill=pillar_color)
    draw.rectangle((loom_cx - loom_w // 2 - 8, loom_bot + 10, loom_cx + loom_w // 2 + 8, loom_bot + 40), fill=(80, 55, 70, 220))

    # ── Warp threads (vertical strings of the loom) ──
    for i in range(-loom_w // 2 + 10, loom_w // 2, 8):
        wx = loom_cx + i
        # Silver-white warp threads with slight variation
        brightness = 180 + rng.randint(-20, 20)
        warp_alpha = 80 + rng.randint(-15, 15)
        draw.line((wx, loom_top - 40, wx, loom_bot + 20),
                  fill=(brightness, brightness, brightness + 10, warp_alpha), width=1)

    # ── Weft threads (horizontal) with glowing silver and gold ──
    for i in range(0, 35):
        wy = loom_top + 30 + i * 40 + rng.randint(-5, 5)
        # Some threads are silver, some copper, some gold
        t_type = i % 7
        if t_type == 0:
            # Gold thread (truth)
            tc = (220, 180, 80, 100 + rng.randint(-20, 20))
            tw = 3
        elif t_type == 3:
            # Copper thread (sorrow)
            tc = (180, 120, 60, 90 + rng.randint(-20, 20))
            tw = 2
        else:
            # Silver thread (joy)
            br = 200 + rng.randint(-20, 20)
            tc = (br, br, br + 20, 80 + rng.randint(-20, 20))
            tw = 1
        # Wavy weft line
        pts = []
        for wx in range(loom_cx - loom_w // 2 + 5, loom_cx + loom_w // 2, 4):
            offset = 4 * math.sin(wx * 0.08 + i * 1.2)
            pts.append((wx, wy + offset))
        if len(pts) > 1:
            draw.line(pts, fill=tc, width=tw)

    # ── The woven tapestry section (central panel within the loom) ──
    # A beautiful surface scene: a queen's coronation (outer joyful imagery)
    tap_x0 = loom_cx - loom_w // 2 + 40
    tap_x1 = loom_cx + loom_w // 2 - 40
    tap_y0 = loom_top + 60
    tap_y1 = loom_bot - 50

    # Queen figure in tapestry (silhouette)
    qx = loom_cx
    qy = tap_y0 + 350
    # Crown/head
    draw.ellipse((qx - 30, qy - 50, qx + 30, qy + 10), fill=(200, 180, 150, 100))
    # Crown points
    for cp in range(-25, 30, 10):
        draw.polygon([(qx + cp - 5, qy - 50), (qx + cp + 5, qy - 50), (qx + cp, qy - 70)],
                     fill=(200, 180, 100, 120))
    # Body/robe
    draw.polygon([(qx - 50, qy + 10), (qx + 50, qy + 10), (qx + 80, qy + 250), (qx - 80, qy + 250)],
                 fill=(160, 100, 120, 80))
    # Robe folds
    for fx in range(-60, 70, 20):
        draw.line((qx + fx, qy + 50, qx + fx + 30, qy + 250), fill=(120, 70, 90, 60), width=2)

    # ── Dark hidden image beneath the surface (the secret) ──
    # A hooded figure with a heart - barely visible through the weave
    hidden = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hidden)

    # Hooded figure shape (the Weaver's Ghost)
    hx, hy = loom_cx + 80, tap_y0 + 750
    hd.polygon([
        (hx - 80, hy + 200), (hx - 60, hy - 20), (hx - 40, hy - 60),
        (hx - 20, hy - 80), (hx + 20, hy - 80), (hx + 40, hy - 60),
        (hx + 60, hy - 20), (hx + 80, hy + 200)
    ], fill=(30, 20, 40, 50))
    # Hollow face (dark void)
    hd.ellipse((hx - 20, hy - 50, hx + 20, hy), fill=(10, 5, 15, 60))
    # Hands holding a glowing heart
    hd.ellipse((hx - 35, hy + 60, hx + 35, hy + 110), fill=(180, 40, 50, 45))
    # Glowing heart
    hd.ellipse((hx - 18, hy + 68, hx + 18, hy + 100), fill=(220, 80, 60, 55))
    hd.ellipse((hx - 10, hy + 74, hx + 10, hy + 94), fill=(240, 160, 80, 60))

    hidden = hidden.filter(ImageFilter.GaussianBlur(12))
    img = Image.alpha_composite(img, hidden)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Cross-hatch weave texture over the tapestry area ──
    for wx in range(tap_x0, tap_x1, 6):
        draw.line((wx, tap_y0, wx, tap_y1), fill=(80, 60, 70, 10), width=1)
    for wy in range(tap_y0, tap_y1, 6):
        draw.line((tap_x0, wy, tap_x1, wy), fill=(80, 60, 70, 10), width=1)

    # ── Radiant silver threads escaping the loom ──
    for _ in range(30):
        start_x = loom_cx + rng.randint(-loom_w // 2, loom_w // 2)
        start_y = loom_top + rng.randint(100, loom_bot - loom_top - 100)
        end_x = rng.randint(100, W - 100)
        end_y = rng.randint(50, 1200)
        # Bezier-style curve points
        ctrl1_x = start_x + (end_x - start_x) * 0.3 + rng.randint(-100, 100)
        ctrl1_y = start_y + (end_y - start_y) * 0.2 + rng.randint(-150, -50)
        ctrl2_x = start_x + (end_x - start_x) * 0.7 + rng.randint(-100, 100)
        ctrl2_y = start_y + (end_y - start_y) * 0.6 + rng.randint(-100, 50)

        pts = []
        for t_int in range(21):
            t = t_int / 20
            # Cubic Bezier
            bx = (1-t)**3 * start_x + 3*(1-t)**2 * t * ctrl1_x + 3*(1-t) * t**2 * ctrl2_x + t**3 * end_x
            by = (1-t)**3 * start_y + 3*(1-t)**2 * t * ctrl1_y + 3*(1-t) * t**2 * ctrl2_y + t**3 * end_y
            pts.append((int(bx), int(by)))

        silver_br = 180 + rng.randint(-30, 30)
        alpha = 30 + rng.randint(-10, 25)
        draw.line(pts, fill=(silver_br, silver_br, silver_br + 20, alpha), width=rng.randint(1, 3))

    # ── Floating thread-sparks (luminous particles) ──
    for _ in range(120):
        sx = rng.randint(50, W - 50)
        sy = rng.randint(30, 1500)
        sr = rng.uniform(1.5, 4.5)
        # Some gold, some silver, some copper
        stype = rng.random()
        if stype < 0.2:
            sc = (220, 180, 80, rng.randint(40, 120))  # gold
        elif stype < 0.35:
            sc = (180, 120, 60, rng.randint(40, 100))  # copper
        else:
            br2 = 200 + rng.randint(-20, 30)
            sc = (br2, br2, br2 + 20, rng.randint(40, 140))  # silver
        draw.ellipse((int(sx - sr), int(sy - sr), int(sx + sr), int(sy + sr)), fill=sc)

    # ── Elara silhouette (foreground, facing the loom) ──
    ex, ey = loom_cx - 250, 1400
    # Body
    draw.line((ex, ey, ex, ey + 280), fill=(10, 8, 15, 220), width=14)
    # Head
    draw.ellipse((ex - 18, ey - 55, ex + 18, ey - 15), fill=(10, 8, 15, 220))
    # Hair (long, flowing back)
    draw.arc((ex - 40, ey - 60, ex + 10, ey + 20), 180, 360, fill=(10, 8, 15, 200), width=8)
    # Arm reaching toward the loom
    draw.line((ex, ey + 30, ex + 100, ey - 40), fill=(10, 8, 15, 220), width=8)
    # Hand open
    draw.ellipse((ex + 90, ey - 52, ex + 115, ey - 28), fill=(10, 8, 15, 200))
    # A single silver thread connects from her hand to the loom
    thread_pts = []
    for ti in range(31):
        tt = ti / 30
        tx2 = (ex + 100) * (1 - tt) + (loom_cx - 100) * tt
        ty2 = (ey - 40) * (1 - tt) + (loom_top + 300) * tt
        # slight arc
        ty2 -= 80 * math.sin(tt * math.pi)
        thread_pts.append((int(tx2), int(ty2)))
    draw.line(thread_pts, fill=(190, 190, 210, 100), width=2)

    # ── Faint memory-thread patterns in the background ──
    for _ in range(8):
        bx = rng.randint(50, W - 50)
        by = rng.randint(40, 1400)
        bpts = []
        for bi in range(40):
            bx2 = bx + bi * 20 + rng.randint(-30, 30)
            by2 = by + 30 * math.sin(bi * 0.5) + rng.randint(-10, 10)
            bpts.append((bx2, by2))
        draw.line(bpts, fill=(100, 80, 110, 15), width=1)

    # ── Bottom part: a woven fabric edge before the title panel ──
    for fring_x in range(100, W - 100, 12):
        fring_len = 10 + rng.randint(-3, 8)
        draw.line((fring_x, 1760, fring_x + rng.randint(-3, 3), 1760 + fring_len),
                  fill=(180, 160, 140, 60), width=2)

    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()),
                                     _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op, "PNG", optimize=True)


# ── Standard helpers (from cover_utils patterns, kept local to avoid import
#     of private helpers that would add more than the allowed imports) ──

def _standard_cover_resolve_title(local_vars):
    for key in ("title", "ti", "book_title", "TITLE"):
        value = local_vars.get(key)
        if value:
            return str(value)
    return "SpindleHearts"

def _standard_cover_resolve_author(local_vars):
    for key in ("author", "au", "AUTHOR"):
        value = local_vars.get(key)
        if value:
            return str(value)
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
