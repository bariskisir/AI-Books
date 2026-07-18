#!/usr/bin/env python3
"""Cover: Beneath the Root — Ecological Horror: A forestry crew on a remote sub-Arctic island discovers that the ancient trees share a single underground consciousness which has begun to remember and avenge human violence against the forest."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560
SEED = 739182465
rng = random.Random(SEED)


def make_cover(mp: Path, op: Path) -> None:
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (15, 18, 35, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Sub-Arctic twilight gradient ──────────────────────────────────────
    # Sky: dark blue-grey -> cold teal -> earth below the island surface
    SKY_TOP = (12, 15, 38)
    SKY_HORIZON = (28, 42, 60)
    EARTH_TOP = (35, 38, 33)
    EARTH_DEEP = (55, 48, 40)

    for y in range(H):
        if y < 1100:
            t = y / 1100
            r = int(SKY_TOP[0] + (SKY_HORIZON[0] - SKY_TOP[0]) * t)
            g = int(SKY_TOP[1] + (SKY_HORIZON[1] - SKY_TOP[1]) * t)
            b = int(SKY_TOP[2] + (SKY_HORIZON[2] - SKY_TOP[2]) * t)
        else:
            t = (y - 1100) / (1765 - 1100)
            r = int(SKY_HORIZON[0] + (EARTH_TOP[0] - SKY_HORIZON[0]) * t)
            g = int(SKY_HORIZON[1] + (EARTH_TOP[1] - SKY_HORIZON[1]) * t)
            b = int(SKY_HORIZON[2] + (EARTH_TOP[2] - SKY_HORIZON[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── Aurora Borealis (sub-Arctic setting) ──────────────────────────────
    aurora = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ad = ImageDraw.Draw(aurora)
    for band in range(4):
        band_x = rng.randint(100, 1400)
        band_w = rng.randint(250, 500)
        band_phase = rng.uniform(0, math.tau)
        hue = rng.choice([
            (50, 200, 110, 10),  # pale green
            (40, 150, 200, 8),   # pale cyan
            (80, 180, 70, 6),    # yellow-green
        ])
        for sy in range(0, 220, 2):
            intensity = 1.0 - abs(sy - 110) / 110
            if intensity < 0.1:
                continue
            for sx in range(band_x - band_w // 2, band_x + band_w // 2, 2):
                dist = abs(sx - band_x) / (band_w / 2)
                amp = intensity * (1.0 - dist)
                if amp < 0.05:
                    continue
                wave = math.sin(sx * 0.015 + sy * 0.04 + band_phase) * 0.5 + 0.5
                alpha_val = int(amp * wave * hue[3])
                if alpha_val < 1:
                    continue
                ad.point((sx, sy), fill=(hue[0], hue[1], hue[2], alpha_val))
    aurora = aurora.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img, aurora)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Distant sea ───────────────────────────────────────────────────────
    for y in range(260, 460):
        t = (y - 260) / 200
        r = int(20 + 12 * t)
        g = int(30 + 18 * t)
        b = int(50 + 22 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 180))

    # ── Island surface silhouette ──────────────────────────────────────────
    surface_pts = []
    for x in range(0, W + 5, 5):
        h = 480 + 180 * math.sin(x * 0.003) + 100 * math.sin(x * 0.008 + 1.7) \
            + 40 * math.sin(x * 0.015 + 3.2) + rng.randint(-15, 15)
        surface_pts.append((x, int(h)))
    surface_pts.append((W, H))
    surface_pts.append((0, H))
    draw.polygon(surface_pts, fill=(30, 38, 33, 255))

    # ── Sub-Arctic trees on the surface ────────────────────────────────────
    for _ in range(28):
        tx = rng.randint(30, W - 30)
        th = 480 + 180 * math.sin(tx * 0.003) + 100 * math.sin(tx * 0.008 + 1.7) \
             + 40 * math.sin(tx * 0.015 + 3.2)
        if th > 650:
            continue  # only on higher ground
        tree_h = rng.randint(100, 240)
        trunk_w = rng.randint(3, 8)
        # Wind-bent sparse trees
        lean = rng.uniform(-18, 18)
        trunk_col = (rng.randint(12, 22), rng.randint(18, 30), rng.randint(10, 18))
        draw.line((tx, th, tx + lean, th - tree_h), fill=(*trunk_col, 210), width=trunk_w)
        # Small sparse canopy clumps
        for c in range(rng.randint(2, 4)):
            cx = tx + lean + rng.randint(-18, 18)
            cy = th - tree_h + rng.randint(-10, 25)
            cr = rng.randint(10, 22)
            ccol = (rng.randint(18, 35), rng.randint(30, 50), rng.randint(18, 28))
            draw.ellipse((cx - cr, cy - cr, cx + cr, cy + cr), fill=(*ccol, 210))

    # ── Underground earth texturing ──────────────────────────────────────
    for y in range(950, 1765):
        t = (y - 950) / (1765 - 950)
        r = int(EARTH_TOP[0] + (EARTH_DEEP[0] - EARTH_TOP[0]) * t**0.7)
        g = int(EARTH_TOP[1] + (EARTH_DEEP[1] - EARTH_TOP[1]) * t**0.7)
        b = int(EARTH_TOP[2] + (EARTH_DEEP[2] - EARTH_TOP[2]) * t**0.7)
        # subtle horizontal banding for rock layers
        if int(y / 15) % 12 == 0:
            r = min(255, r + 5)
            g = min(255, g + 4)
            b = min(255, b + 3)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── Background ambient root glow ──────────────────────────────────────
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for _ in range(40):
        cx = rng.randint(100, 1500)
        cy = rng.randint(1080, 1700)
        cr = rng.randint(50, 180)
        gd.ellipse(
            (cx - cr, cy - cr, cx + cr, cy + cr),
            fill=(rng.randint(40, 100), rng.randint(100, 190), rng.randint(40, 100), rng.randint(6, 20)),
        )
    glow = glow.filter(ImageFilter.GaussianBlur(35))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── The Rootmind: hub-and-spoke underground network ────────────────────
    # Nodes (dense root plexus hubs)
    hubs = []
    for _ in range(10):
        hx = rng.randint(120, 1480)
        hy = rng.randint(1120, 1680)
        hr = rng.randint(25, 55)
        hubs.append((hx, hy, hr))
        # Dark organic hub
        draw.ellipse((hx - hr, hy - hr, hx + hr, hy + hr), fill=(35, 55, 32, 200))
        draw.ellipse((hx - hr * 3 // 4, hy - hr * 3 // 4, hx + hr * 3 // 4, hy + hr * 3 // 4), fill=(40, 72, 38, 180))
        # Inner glow — Rootmind consciousness
        draw.ellipse((hx - hr // 3, hy - hr // 3, hx + hr // 3, hy + hr // 3), fill=(70, 140, 65, 130))

    # Thick root bundles connecting hubs
    for i in range(len(hubs)):
        for j in range(i + 1, len(hubs)):
            if rng.random() < 0.55:
                hx1, hy1, _ = hubs[i]
                hx2, hy2, _ = hubs[j]
                dist = math.sqrt((hx2 - hx1) ** 2 + (hy2 - hy1) ** 2)
                if dist > 1000:
                    continue
                # Bezier-like curve
                cx = (hx1 + hx2) // 2 + rng.randint(-60, 60)
                cy = (hy1 + hy2) // 2 + rng.randint(-40, 40)
                root_w = rng.randint(8, 18)
                root_col = (rng.randint(30, 55), rng.randint(50, 85), rng.randint(28, 45))
                # Main cable
                draw.line([(hx1, hy1), (cx, cy), (hx2, hy2)], fill=(*root_col, 190), width=root_w)
                # Accompanying thin tendrils
                for _ in range(rng.randint(2, 4)):
                    ox = rng.randint(-10, 10)
                    oy = rng.randint(-10, 10)
                    draw.line(
                        [(hx1 + ox, hy1 + oy), (cx + ox * 2, cy + oy * 2), (hx2 + ox, hy2 + oy)],
                        fill=(*root_col, 90), width=rng.randint(2, 5),
                    )

    # ── Lateral root tendrils spreading through soil ───────────────────────
    for _ in range(55):
        sx = rng.randint(60, W - 60)
        sy = rng.randint(1050, 1740)
        pts = [(sx, sy)]
        segs = rng.randint(5, 12)
        for s in range(1, segs + 1):
            sx += rng.randint(-35, 35)
            sy += rng.randint(12, 35)
            pts.append((sx, sy))
        rcol = (rng.randint(40, 72), rng.randint(55, 95), rng.randint(32, 52))
        draw.line(pts, fill=(*rcol, rng.randint(80, 180)), width=rng.randint(2, 6))
        # Tiny root hairs (exploratory tendrils)
        if rng.random() < 0.35:
            tip = pts[-1]
            for _ in range(rng.randint(1, 3)):
                dx = tip[0] + rng.randint(-25, 25)
                dy = tip[1] + rng.randint(8, 25)
                draw.line([tip, (dx, dy)], fill=(*rcol, 70), width=rng.randint(1, 2))

    # ── Taproots descending from surface trees ─────────────────────────────
    for x in range(30, W - 30, 15):
        th = 480 + 180 * math.sin(x * 0.003) + 100 * math.sin(x * 0.008 + 1.7) \
             + 40 * math.sin(x * 0.015 + 3.2)
        if th > 650 and rng.random() < 0.3:
            continue
        if rng.random() < 0.25:
            root_len = rng.randint(200, 600)
            root_dx = rng.randint(-10, 10)
            draw.line(
                (x, th + 20, x + root_dx, th + 20 + root_len),
                fill=(rng.randint(30, 50), rng.randint(40, 65), rng.randint(25, 40), rng.randint(120, 190)),
                width=rng.randint(3, 7),
            )

    # ── Bioluminescent "memory" nodes ──────────────────────────────────────
    for _ in range(30):
        nx = rng.randint(150, 1450)
        ny = rng.randint(1100, 1700)
        nr = rng.randint(3, 10)
        intensity = rng.randint(100, 230)
        # Icy pale green bioluminescence
        draw.ellipse((nx - nr, ny - nr, nx + nr, ny + nr), fill=(120, 240, 120, intensity))
        if nr > 5:
            draw.ellipse((nx - nr * 2, ny - nr * 2, nx + nr * 2, ny + nr * 2), fill=(70, 180, 70, intensity // 4))

    # ── Body-horror elements: bones entwined in roots ──────────────────────
    for _ in range(5):
        bx = rng.randint(300, 1300)
        by = rng.randint(1150, 1580)
        angle = rng.uniform(0, math.tau)
        # Bone fragment
        bw, bh = rng.randint(30, 55), rng.randint(8, 14)
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        corners = [
            (-bw // 2, -bh // 2), (bw // 2, -bh // 2),
            (bw // 2, bh // 2), (-bw // 2, bh // 2),
        ]
        rotated = []
        for cx, cy in corners:
            rx = bx + cx * cos_a - cy * sin_a
            ry = by + cx * sin_a + cy * cos_a
            rotated.append((rx, ry))
        draw.polygon(rotated, fill=(150, 140, 125, 200))
        draw.polygon(rotated, fill=(120, 115, 100, 100), outline=(160, 150, 130, 80))

        # Roots wrapping around the bone
        for w in range(rng.randint(2, 4)):
            wrap_pts = []
            for t in range(0, 11):
                frac = t / 10
                wx = bx + math.sin(angle + frac * math.tau * 0.5) * bw * 0.6
                wy = by + math.cos(angle + frac * math.tau * 0.5) * bh * 0.6 \
                     + frac * rng.randint(-5, 5)
                wrap_pts.append((wx, wy))
            draw.line(wrap_pts, fill=(45, 55, 38, rng.randint(140, 210)), width=rng.randint(2, 4))

    # ── Vignette ──────────────────────────────────────────────────────────
    for vy in range(H):
        vt = 1.0 - abs(vy - H // 2) / (H // 2)
        vw = int(35 * max(0.0, 1.0 - vt))
        if vw > 0:
            draw.line((0, vy, vw, vy), fill=(0, 0, 0, 85))
            draw.line((W - vw, vy, W, vy), fill=(0, 0, 0, 85))

    # ── Title panel ───────────────────────────────────────────────────────
    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, title, author, model)
    img.convert("RGB").save(op, "PNG", optimize=True)


def main() -> None:
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
