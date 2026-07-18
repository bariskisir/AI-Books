#!/usr/bin/env python3
"""Cover: The Cartographer of Last Things — a cartographer discovers a vault immune to entropy in a decaying world."""

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
rng.seed(1743290881)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    # Base — deep charcoal with rust undertone
    img = Image.new("RGBA", (W, H), (20, 15, 18, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 1. Rust-to-charcoal gradient ─────────────────────────────────────────
    for y in range(H):
        t = y / H
        r = int(20 + 65 * t)
        g = int(15 + 28 * t)
        b = int(18 + 8 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── 2. Vignette ──────────────────────────────────────────────────────────
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(45 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 100))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 100))

    # ── 3. Ghost cartographic grid (faint cyan overlay — vanished cities) ──
    for gx in range(0, W, 60):
        draw.line((gx, 0, gx, 1700), fill=(100, 180, 210, 12), width=1)
    for gy in range(0, 1700, 60):
        draw.line((0, gy, W, gy), fill=(100, 180, 210, 12), width=1)

    # ── 4. Topographic contour arcs (cartographer's map language) ────────────
    cx_center, cy_center = W // 2, 1720
    for radius in range(200, 1300, 50):
        draw.arc(
            (cx_center - radius, cy_center - radius,
             cx_center + radius, cy_center + radius),
            -115, -65,
            fill=(100, 180, 210, rng.randint(6, 14)),
            width=1,
        )

    # ── 5. Compass rose (cartographer symbol) ────────────────────────────────
    cx, cy = W // 2, 380
    for ang_deg in range(0, 360, 45):
        ang = math.radians(ang_deg)
        inner = 45 if ang_deg % 90 == 0 else 30
        arm_len = 110
        draw.line(
            (cx + math.cos(ang) * inner, cy + math.sin(ang) * inner,
             cx + math.cos(ang) * arm_len, cy + math.sin(ang) * arm_len),
            fill=(180, 210, 230, 18), width=2,
        )

    # ── 6. Partially decayed building fragments (left & right) ──────────────
    for side in (-1, 1):
        base_x = W // 2 + side * 280
        for _ in range(rng.randint(5, 8)):
            bx = base_x + side * rng.randint(0, 120)
            bw = rng.randint(45, 120)
            bh = rng.randint(150, 400)
            by = 1550 - bh
            shade = rng.randint(18, 32)
            # Jagged crumbling top edge
            pts = [(bx, by + bh)]
            decay_peak = by + rng.randint(-40, 10)
            for px in range(bx, bx + bw + 1, 8):
                jitter = rng.randint(-25, 5) if px < bx + bw // 2 else rng.randint(-5, 25)
                pts.append((px, decay_peak + jitter))
            pts.append((bx + bw, by + bh))
            draw.polygon(pts, fill=(shade, shade - 3, shade - 5, 220))
            # Decay holes / collapsed windows
            for _ in range(rng.randint(2, 4)):
                hx = bx + rng.randint(10, bw - 10)
                hy = by + rng.randint(15, bh - 15)
                hs = rng.randint(5, 15)
                draw.ellipse(
                    (hx - hs, hy - hs, hx + hs, hy + hs),
                    fill=(shade + 6, shade + 2, shade - 1, 160),
                )

    # ── 7. Vault warm golden glow (multi-layer radial) ───────────────────────
    vx, vy = W // 2, 1450
    for gl in range(6, 0, -1):
        grad_r = 160 + gl * 45
        grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(grad)
        gd.ellipse(
            (vx - grad_r, vy - grad_r, vx + grad_r, vy + grad_r),
            fill=(210, 170, 80, 5 + gl * 4),
        )
        grad = grad.filter(ImageFilter.GaussianBlur(20 + gl * 6))
        img = Image.alpha_composite(img, grad)

    draw = ImageDraw.Draw(img, "RGBA")

    # ── 8. Vault door (the undecayed object) ─────────────────────────────────
    vr = 155
    # Outer rim
    draw.ellipse(
        (vx - vr, vy - vr, vx + vr, vy + vr),
        outline=(180, 150, 75, 240), width=8,
    )
    # Inner ring
    draw.ellipse(
        (vx - vr + 14, vy - vr + 14, vx + vr - 14, vy + vr - 14),
        outline=(215, 180, 90, 200), width=4,
    )
    # Bright core pools
    draw.ellipse(
        (vx - vr // 2, vy - vr // 2, vx + vr // 2, vy + vr // 2),
        fill=(255, 215, 115, 55),
    )
    draw.ellipse(
        (vx - vr // 3, vy - vr // 3, vx + vr // 3, vy + vr // 3),
        fill=(255, 235, 155, 40),
    )
    # Rivet details around the door ring
    for ang_deg in range(0, 360, 30):
        ang = math.radians(ang_deg)
        rx = vx + math.cos(ang) * (vr - 16)
        ry = vy + math.sin(ang) * (vr - 16)
        draw.ellipse((rx - 4, ry - 4, rx + 4, ry + 4), fill=(235, 195, 105, 230))

    # ── 9. Light beams radiating from vault ──────────────────────────────────
    for _ in range(8):
        ang = math.radians(rng.randint(-40, 40))
        blen = rng.randint(300, 600)
        ex = vx + math.sin(ang) * blen
        ey = vy - math.cos(ang) * blen * 0.5 - 150
        draw.line(
            (vx + math.sin(ang) * 15, vy - math.cos(ang) * 15, ex, ey),
            fill=(255, 200, 100, rng.randint(5, 15)),
            width=rng.randint(8, 22),
        )

    # ── 10. Decay particles floating upward (entropy visualization) ──────────
    for _ in range(250):
        px = rng.randint(0, W)
        py = rng.randint(200, 1750)
        sz = rng.uniform(1.0, 3.5)
        dist = math.hypot(px - vx, py - vy) / 1400
        warmth = max(0, 1 - dist)
        pr = int(70 + 185 * warmth)
        pg = int(30 + 170 * warmth)
        pb = int(15 + 50 * warmth)
        draw.ellipse(
            (int(px - sz), int(py - sz), int(px + sz), int(py + sz)),
            fill=(pr, pg, pb, rng.randint(25, 120)),
        )

    # ── 11. Ground cracks spreading from vault (entropy fracturing) ─────────
    for _ in range(18):
        sx = vx + rng.randint(-200, 200)
        sy = vy + rng.randint(50, 220)
        pts = [(sx, sy)]
        for _ in range(rng.randint(3, 6)):
            sx += rng.randint(-30, 30)
            sy += rng.randint(10, 30)
            pts.append((sx, sy))
        draw.line(pts, fill=(rng.randint(30, 50), rng.randint(15, 30), rng.randint(10, 20), rng.randint(60, 140)),
                  width=rng.randint(2, 5))

    # ── 12. Ground debris layer ──────────────────────────────────────────────
    for _ in range(100):
        dx = rng.randint(0, W)
        dy = rng.randint(1520, 1750)
        ds = rng.randint(2, 8)
        draw.ellipse(
            (dx - ds, dy - ds, dx + ds, dy + ds),
            fill=(rng.randint(45, 85), rng.randint(20, 45), rng.randint(12, 25), 130),
        )

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
