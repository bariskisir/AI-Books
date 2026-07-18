#!/usr/bin/env python3
"""Cover: The Taste of Salt on Another Planet — A marine biologist connects with a sentient plankton swarm through bioluminescent neural fields while a corporate terraforming threat encroaches."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    # ── base canvas ──────────────────────────────────────────────────────────
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── gradient: cosmic purple-black → deep ocean blue-black ────────────────
    for y in range(H):
        t = y / H
        if t < 0.35:
            lt = t / 0.35
            r = int(6 + (18 - 6) * lt)
            g = int(1 + (6 - 1) * lt)
            b = int(18 + (48 - 18) * lt)
        elif t < 0.70:
            lt = (t - 0.35) / 0.35
            r = int(18 + (12 - 18) * lt)
            g = int(6 + (22 - 6) * lt)
            b = int(48 + (60 - 48) * lt)
        else:
            lt = (t - 0.70) / 0.30
            r = int(12 + (3 - 12) * lt)
            g = int(22 + (35 - 22) * lt)
            b = int(60 + (50 - 60) * lt)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── deep background: faint water-surface caustics (looking up from below) ─
    rng = random.Random(313)
    caustic = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(caustic)
    for _ in range(40):
        cx = rng.randint(0, W)
        cy = rng.randint(0, 180)
        for angle_deg in range(0, 360, 12):
            rad = math.radians(angle_deg + rng.uniform(-6, 6))
            length = rng.randint(20, 90)
            ex = cx + math.cos(rad) * length
            ey = cy + math.sin(rad) * length * 0.25
            cd.line(
                (cx, cy, ex, ey),
                fill=(120, 210, 255, rng.randint(2, 7)),
                width=1,
            )
    img = Image.alpha_composite(img, caustic)

    # ── background plankton (scattered dim dots) ─────────────────────────────
    rng = random.Random(73)
    for _ in range(500):
        px = rng.randint(0, W)
        py = rng.randint(80, H - 500)
        pr = rng.uniform(0.8, 2.2)
        pb = rng.randint(100, 180)
        draw.ellipse(
            (px - pr, py - pr, px + pr, py + pr),
            fill=(pb, pb, 255, rng.randint(8, 30)),
        )

    # ── THE SWARM: bioluminescent constellation (neural figure) ──────────────
    rng = random.Random(137)
    swarm_cx, swarm_cy = W // 2, 700

    # Generate figure nodes — a reaching angelic/swarm-humanoid form
    nodes = []

    # Head
    hx, hy = swarm_cx + rng.randint(-10, 10), swarm_cy - 280
    nodes.append((hx, hy, 9))

    # Torso spine
    for i in range(1, 9):
        yoff = i * 32
        w = 12 + i * 2
        nodes.append((
            hx + rng.randint(-w, w),
            hy + yoff + rng.randint(-8, 8),
            7 - i * 0.35,
        ))

    # Left arm reaching outward & upward
    ax, ay = hx - 18, hy + 35
    for i in range(12):
        ax += rng.randint(-28, -12)
        ay += rng.randint(10, 28)
        nodes.append((ax, ay, max(2.5, 7 - i * 0.4)))

    # Right arm reaching outward & upward
    ax2, ay2 = hx + 18, hy + 35
    for i in range(10):
        ax2 += rng.randint(12, 28)
        ay2 += rng.randint(10, 25)
        nodes.append((ax2, ay2, max(2.5, 7 - i * 0.4)))

    # Wing-like trails (left)
    for i in range(18):
        wx = hx - 80 - i * rng.randint(18, 30)
        wy = hy - 30 + i * rng.randint(12, 22)
        nodes.append((wx, wy, rng.uniform(1.5, 4.5)))

    # Wing-like trails (right)
    for i in range(18):
        wx = hx + 80 + i * rng.randint(18, 30)
        wy = hy - 30 + i * rng.randint(12, 22)
        nodes.append((wx, wy, rng.uniform(1.5, 4.5)))

    # Surrounding scatter (the swarm's "halo" of plankton)
    for _ in range(160):
        angle = rng.uniform(0, math.tau)
        dist = rng.uniform(20, 280)
        sx = hx + math.cos(angle) * dist + rng.randint(-40, 40)
        sy = hy + math.sin(angle) * dist * 0.55 + rng.randint(-40, 40)
        if 0 <= sx < W and 80 <= sy < H - 500:
            nodes.append((sx, sy, rng.uniform(1.0, 3.5)))

    # ── neural connections between nearby swarm nodes ────────────────────────
    neural = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(neural)

    rng = random.Random(137)
    for i, (x1, y1, _) in enumerate(nodes):
        for j, (x2, y2, _) in enumerate(nodes):
            if j <= i:
                continue
            dx = x2 - x1
            dy = y2 - y1
            dist = math.sqrt(dx * dx + dy * dy)
            if 15 < dist < 90 and rng.random() < 0.35:
                alpha = max(8, int(90 - dist))
                nd.line(
                    (x1, y1, x2, y2),
                    fill=(120, 210, 255, alpha),
                    width=1,
                )
            if 30 < dist < 160 and rng.random() < 0.12:
                nd.line(
                    (x1, y1, x2, y2),
                    fill=(180, 240, 255, rng.randint(25, 55)),
                    width=rng.randint(2, 3),
                )

    neural = neural.filter(ImageFilter.GaussianBlur(1))
    img = Image.alpha_composite(img, neural)

    # ── render the swarm nodes (glowing bioluminescent plankton) ─────────────
    swarm_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(swarm_layer)

    for x, y, r in nodes:
        if r <= 0:
            continue
        # Outer glow
        glow_r = r * 5
        sd.ellipse(
            (x - glow_r, y - glow_r, x + glow_r, y + glow_r),
            fill=(80, 200, 255, int(20 + r * 5)),
        )
        # Mid glow
        sd.ellipse(
            (x - r * 2.5, y - r * 2.5, x + r * 2.5, y + r * 2.5),
            fill=(160, 230, 255, int(60 + r * 8)),
        )
        # Core
        sd.ellipse(
            (x - r, y - r, x + r, y + r),
            fill=(220, 245, 255, int(160 + r * 10)),
        )

    swarm_layer = swarm_layer.filter(ImageFilter.GaussianBlur(2))
    img = Image.alpha_composite(img, swarm_layer)

    # ── Dr. Orla Finn: silhouette reaching up from the depths ────────────────
    orla_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(orla_layer)

    ox, obase = W // 2, 1750

    # Dive-suit body
    od.polygon([
        (ox - 18, obase), (ox - 15, obase - 100),
        (ox - 22, obase - 130), (ox - 16, obase - 145),
        (ox - 10, obase - 155), (ox + 10, obase - 155),
        (ox + 16, obase - 145), (ox + 22, obase - 130),
        (ox + 15, obase - 100), (ox + 18, obase),
    ], fill=(12, 18, 30, 220))

    # Helmet
    od.ellipse(
        (ox - 15, obase - 195, ox + 15, obase - 155),
        fill=(12, 18, 30, 220),
    )
    # Helmet visor (reflection)
    od.ellipse(
        (ox - 10, obase - 190, ox + 10, obase - 162),
        fill=(30, 60, 100, 160),
    )
    od.ellipse(
        (ox - 5, obase - 185, ox + 5, obase - 168),
        fill=(80, 180, 220, 80),
    )

    # Left arm reaching toward the swarm
    od.polygon([
        (ox - 16, obase - 140), (ox - 40, obase - 210),
        (ox - 45, obase - 225), (ox - 35, obase - 230),
        (ox - 28, obase - 215), (ox - 12, obase - 148),
    ], fill=(12, 18, 30, 220))
    # Left glove
    od.ellipse(
        (ox - 47, obase - 235, ox - 33, obase - 220),
        fill=(12, 18, 30, 220),
    )

    # Right arm reaching toward the swarm
    od.polygon([
        (ox + 16, obase - 140), (ox + 40, obase - 210),
        (ox + 45, obase - 225), (ox + 35, obase - 230),
        (ox + 28, obase - 215), (ox + 12, obase - 148),
    ], fill=(12, 18, 30, 220))
    # Right glove
    od.ellipse(
        (ox + 33, obase - 235, ox + 47, obase - 220),
        fill=(12, 18, 30, 220),
    )

    # Dive-suit equipment lines (subtle detail)
    od.line(
        (ox - 8, obase - 100, ox - 8, obase - 20),
        fill=(40, 80, 120, 40), width=2,
    )
    od.line(
        (ox + 8, obase - 100, ox + 8, obase - 20),
        fill=(40, 80, 120, 40), width=2,
    )

    img = Image.alpha_composite(img, orla_layer)

    # ── emotional resonance: golden amber ripple waves from Orla's hands ─────
    wave = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wave)

    for hand_x, hand_y in [(ox - 39, obase - 227), (ox + 39, obase - 227)]:
        for radius in range(15, 260, 20):
            alpha = max(4, 55 - radius // 5)
            wd.ellipse(
                (hand_x - radius, hand_y - radius,
                 hand_x + radius, hand_y + radius),
                outline=(255, 200 + radius // 6, 90 + radius // 5, alpha),
                width=2 if radius < 100 else 1,
            )

    # Warm glow bloom at each hand
    for hx, hy in [(ox - 39, obase - 227), (ox + 39, obase - 227)]:
        wd.ellipse(
            (hx - 35, hy - 35, hx + 35, hy + 35),
            fill=(255, 210, 120, 30),
        )

    wave = wave.filter(ImageFilter.GaussianBlur(4))
    img = Image.alpha_composite(img, wave)

    # ── corporate terraforming threat: cold geometric overlay ────────────────
    threat = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(threat)

    # Vertical survey grid
    for gx in range(0, W, 70):
        alpha = 10 + int(12 * abs(math.sin(gx * 0.04)))
        td.line((gx, 0, gx, H - 500), fill=(150, 190, 220, alpha), width=1)

    # Horizontal survey grid
    for gy in range(0, H - 500, 55):
        alpha = 8 + int(10 * abs(math.sin(gy * 0.03)))
        td.line((0, gy, W, gy), fill=(150, 190, 220, alpha), width=1)

    # Diagonal terraforming scan lines
    for i in range(-6, 7):
        alpha = max(4, 25 - abs(i) * 3)
        xs = W // 2 + i * 55
        td.line(
            (xs, 0, xs + 420, 1300),
            fill=(180, 210, 240, alpha),
            width=1,
        )

    # Red hazard markers at grid intersections
    for gx in range(150, W, 180):
        for gy in range(80, 800, 140):
            alpha = 15 + int(12 * abs(math.sin(gx * gy * 0.0008)))
            td.polygon(
                [(gx, gy - 7), (gx - 5, gy + 5), (gx + 5, gy + 5)],
                fill=(255, 60, 50, alpha),
            )

    # Cold blue warning bars at top edge
    td.rectangle((0, 0, W, 6), fill=(120, 180, 220, 25))
    for bx in range(0, W, 40):
        td.rectangle((bx, 0, bx + 2, 12), fill=(180, 220, 255, rng.randint(10, 25)))

    img = Image.alpha_composite(img, threat)

    # ── central warm glow (the emotional heart of the connection) ─────────────
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)

    gd.ellipse(
        (W // 2 - 220, swarm_cy - 220, W // 2 + 220, swarm_cy + 220),
        fill=(255, 180, 80, 12),
    )
    gd.ellipse(
        (W // 2 - 120, swarm_cy - 120, W // 2 + 120, swarm_cy + 120),
        fill=(255, 200, 130, 18),
    )

    img = Image.alpha_composite(img, glow)

    # ── tiny bioluminescent sparks (floating plankton near the viewer) ───────
    rng = random.Random(199)
    for _ in range(150):
        sx = rng.randint(0, W)
        sy = rng.randint(H - 400, H - 100)
        sr = rng.uniform(0.5, 2.0)
        sb = rng.randint(80, 180)
        draw.ellipse(
            (sx - sr, sy - sr, sx + sr, sy + sr),
            fill=(sb, sb, 255, rng.randint(15, 40)),
        )

    # ── finalize ────────────────────────────────────────────────────────────
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
