#!/usr/bin/env python3
"""Cover: Chlorophyll and Rust — A Ukrainian climate migration saga: cracked Dnipro riverbed, a lone cherry tree with pale blossoms, ghostly family silhouettes scattering across continents."""

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
    rng = random.Random("chlorophyll-and-rust-2024")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Sky gradient: dusty amber to deep ochre ──────────────────────────
    for y in range(1100):
        t = y / 1100
        r = int(180 + 60 * (1 - t))
        g = int(120 + 50 * (1 - t))
        b = int(50 + 30 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── Distant horizon haze ─────────────────────────────────────────────
    haze = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(haze)
    hd.ellipse((-200, 900, W + 200, 1300), fill=(220, 180, 130, 60))
    haze = haze.filter(ImageFilter.GaussianBlur(50))
    img = Image.alpha_composite(img, haze)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Dried earth gradient (cracked riverbed) ─────────────────────────
    for y in range(1050, H):
        t = (y - 1050) / (H - 1050)
        r = int(120 + 30 * t)
        g = int(70 + 20 * t)
        b = int(30 + 15 * t)
        # Add subtle horizontal variation
        for x in range(0, W, 4):
            vr = rng.randint(-10, 10)
            vg = rng.randint(-8, 8)
            vb = rng.randint(-5, 5)
            draw.line((x, y, x + 4, y), fill=(r + vr, g + vg, b + vb, 255))

    # ── Winding dry riverbed (the vanished Dnipro) ──────────────────────
    river_path = []
    cx, cy = W // 2, 1050
    for step in range(200):
        cx += int(math.sin(step * 0.03) * 30 + rng.randint(-15, 15))
        cy += 7
        if cy >= H - 200:
            break
        river_path.append((cx, cy))

    river_bed = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(river_bed)
    for i, (rx, ry) in enumerate(river_path):
        width = max(2, int(80 - i * 0.15))
        rd.ellipse((rx - width, ry - 6, rx + width, ry + 6), fill=(90, 55, 25, 180))
    river_bed = river_bed.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img, river_bed)
    draw = ImageDraw.Draw(img, "RGBA")

    # Deeper cracked channel line
    for i, (rx, ry) in enumerate(river_path):
        if i % 3 == 0:
            w = max(1, int(40 - i * 0.08))
            draw.ellipse((rx - w, ry - 3, rx + w, ry + 3), fill=(55, 32, 12, 200))

    # ── Cracked earth polygons ──────────────────────────────────────────
    crack_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(crack_layer)

    # Generate crack grid: random polygon vertices in the earth zone
    crack_y_start = 1150
    points = []
    for _ in range(120):
        px = rng.randint(0, W)
        py = rng.randint(crack_y_start, H - 50)
        points.append((px, py))

    # Draw crack lines connecting nearby points
    for i, (x1, y1) in enumerate(points):
        for x2, y2 in points[i + 1 :]:
            dist = math.hypot(x2 - x1, y2 - y1)
            if 20 < dist < 90:
                alpha = int(40 - dist * 0.3)
                cd.line((x1, y1, x2, y2), fill=(25, 15, 8, max(10, alpha)), width=rng.randint(1, 3))

    # Add deeper primary cracks (fewer, more prominent)
    for _ in range(25):
        x1 = rng.randint(0, W)
        y1 = rng.randint(crack_y_start, H - 50)
        angle = rng.uniform(0, math.tau)
        length = rng.randint(60, 200)
        x2 = int(x1 + math.cos(angle) * length)
        y2 = int(y1 + math.sin(angle) * length)
        if crack_y_start < y2 < H - 50:
            cd.line((x1, y1, x2, y2), fill=(30, 18, 8, 220), width=rng.randint(2, 5))
            # branch off the crack
            for _ in range(rng.randint(1, 3)):
                bx = (x1 + x2) // 2 + rng.randint(-20, 20)
                by = (y1 + y2) // 2 + rng.randint(-20, 20)
                b_angle = angle + rng.uniform(-0.8, 0.8)
                b_len = rng.randint(30, 80)
                cd.line((bx, by, bx + int(math.cos(b_angle) * b_len), by + int(math.sin(b_angle) * b_len)),
                        fill=(35, 20, 10, 180), width=rng.randint(1, 2))

    img = Image.alpha_composite(img, crack_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── The Cherry Tree (central symbol) ────────────────────────────────
    tree_x = W // 2 + rng.randint(-60, 60)
    tree_base_y = 1400 + rng.randint(0, 100)

    # Trunk — gnarled, alive but struggling
    trunk_segments = []
    tx, ty = tree_x, tree_base_y
    for seg in range(20):
        tx += rng.randint(-4, 4)
        ty -= rng.randint(15, 25)
        trunk_segments.append((tx, ty))
        if ty < 400:
            break

    # Draw trunk with varying thickness
    for i in range(len(trunk_segments) - 1):
        thickness = max(3, int(14 - i * 0.6))
        draw.line((trunk_segments[i], trunk_segments[i + 1]),
                  fill=(70 + rng.randint(-10, 10), 35 + rng.randint(-5, 5), 15 + rng.randint(-5, 5), 230),
                  width=thickness)

    # Branches — reaching out
    branches = []
    for seg_idx in range(3, len(trunk_segments), 4):
        bx, by = trunk_segments[seg_idx]
        angle = rng.choice([-1.2, -0.8, 0.8, 1.2])
        length = rng.randint(80, 200)
        for step in range(1, 8):
            ex = int(bx + math.cos(angle) * length * step / 8 + rng.randint(-10, 10))
            ey = int(by - 20 * step + rng.randint(-10, 10))
            branches.append((bx, by, ex, ey))
            bw = max(1, int(5 - step * 0.5))
            draw.line((bx, by, ex, ey), fill=(65, 30, 12, 200), width=bw)

    # Cherry blossoms (pale, few — the tree refuses to fruit)
    blossom_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bld = ImageDraw.Draw(blossom_layer)

    # Canopy silhouette — sparse, patchy
    for _ in range(40):
        cx = tree_x + rng.randint(-120, 120)
        cy = trunk_segments[min(len(trunk_segments) - 1, 5)][1] + rng.randint(-80, 30)
        cr = rng.randint(25, 80)
        alpha = rng.randint(6, 20)
        bld.ellipse((cx - cr, cy - cr, cx + cr, cy + cr), fill=(50, 60, 30, alpha))

    # Individual blossoms (pale pink — chlorophyll struggling against rust)
    for _ in range(35):
        bx = tree_x + rng.randint(-130, 130)
        by = trunk_segments[min(len(trunk_segments) - 1, rng.randint(3, 7))][1] + rng.randint(-100, 30)
        br = rng.randint(3, 7)
        pink = (235 - rng.randint(0, 30), 200 - rng.randint(0, 30), 180 - rng.randint(0, 20))
        bld.ellipse((bx - br, by - br, bx + br, by + br), fill=(*pink, rng.randint(150, 220)))
        # tiny center
        bld.ellipse((bx - br // 3, by - br // 3, bx + br // 3, by + br // 3), fill=(120, 80, 60, 200))

    # A few fallen blossoms on the cracked earth
    for _ in range(12):
        fx = tree_x + rng.randint(-200, 200)
        fy = tree_base_y + rng.randint(50, 300)
        fr = rng.randint(2, 4)
        bld.ellipse((fx - fr, fy - fr, fx + fr, fy + fr), fill=(220, 180, 160, rng.randint(60, 120)))

    blossom_layer = blossom_layer.filter(ImageFilter.GaussianBlur(1))
    img = Image.alpha_composite(img, blossom_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Ghostly family silhouettes (scattering across continents) ───────
    silhouettes = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(silhouettes)

    # Figure data: (start_x, start_y, direction_angle, scale, generation_name)
    figures = [
        (300, 700, -0.15, 1.0),    # Oksana — west
        (1200, 650, 3.0, 0.9),      # Mykola — east
        (200, 500, -0.3, 0.8),      # Lena — far west (Japan)
        (1350, 800, 3.2, 0.7),      # Dmytro — far east
    ]

    def draw_figure(d, fx, fy, angle, scale):
        """Draw a simple translucent walking human figure."""
        s = scale * 60
        # Head
        d.ellipse((fx - 8 * scale, fy - 20 * scale, fx + 8 * scale, fy - 6 * scale), fill=(255, 200, 150, 25))
        # Body (torso leaning slightly in direction of travel)
        lean = angle * 2
        d.line((fx, fy - 6 * scale, fx + lean, fy + 15 * scale), fill=(180, 160, 120, 20), width=int(6 * scale))
        # Arms
        d.line((fx + lean, fy - 3 * scale, fx + lean - 12 * scale - lean, fy + 8 * scale),
               fill=(180, 160, 120, 15), width=int(3 * scale))
        d.line((fx + lean, fy - 3 * scale, fx + lean + 12 * scale + lean, fy + 8 * scale),
               fill=(180, 160, 120, 15), width=int(3 * scale))
        # Legs (walking stride)
        d.line((fx + lean, fy + 15 * scale, fx - 10 * scale + lean, fy + 35 * scale),
               fill=(180, 160, 120, 18), width=int(4 * scale))
        d.line((fx + lean, fy + 15 * scale, fx + 12 * scale + lean, fy + 35 * scale),
               fill=(180, 160, 120, 18), width=int(4 * scale))
        # A carried bundle (cherry tree cutting)
        d.ellipse((fx + 5 * scale + lean, fy + 2 * scale, fx + 15 * scale + lean, fy + 10 * scale),
                  fill=(100, 140, 80, 20))

    for sx, sy, angle, sc in figures:
        # Draw multiple ghostly instances along the path (trail effect)
        for step in range(5):
            fade = max(5, 25 - step * 4)
            ox = sx + int(math.cos(angle) * step * 80)
            oy = sy + int(math.sin(abs(angle)) * step * 30)
            # Temporarily adjust the draw's fill alpha by creating a separate image
            fig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            fd = ImageDraw.Draw(fig)
            # Re-draw figure with decreasing opacity for trail effect
            s2 = sc * (1 - step * 0.12)
            fx2, fy2 = ox, oy
            # Head
            fd.ellipse((fx2 - 8 * s2, fy2 - 20 * s2, fx2 + 8 * s2, fy2 - 6 * s2), fill=(255, 200, 150, max(5, fade - 8)))
            # Body
            lean = angle * 2
            fd.line((fx2, fy2 - 6 * s2, fx2 + lean, fy2 + 15 * s2), fill=(180, 160, 120, max(3, fade - 5)), width=max(1, int(6 * s2)))
            # Arms
            fd.line((fx2 + lean, fy2 - 3 * s2, fx2 + lean - 12 * s2 - lean, fy2 + 8 * s2),
                   fill=(180, 160, 120, max(3, fade - 8)), width=max(1, int(3 * s2)))
            fd.line((fx2 + lean, fy2 - 3 * s2, fx2 + lean + 12 * s2 + lean, fy2 + 8 * s2),
                   fill=(180, 160, 120, max(3, fade - 8)), width=max(1, int(3 * s2)))
            # Legs
            fd.line((fx2 + lean, fy2 + 15 * s2, fx2 - 10 * s2 + lean, fy2 + 35 * s2),
                   fill=(180, 160, 120, max(3, fade - 5)), width=max(1, int(4 * s2)))
            fd.line((fx2 + lean, fy2 + 15 * s2, fx2 + 12 * s2 + lean, fy2 + 35 * s2),
                   fill=(180, 160, 120, max(3, fade - 5)), width=max(1, int(4 * s2)))
            # Bundle
            fd.ellipse((fx2 + 5 * s2 + lean, fy2 + 2 * s2, fx2 + 15 * s2 + lean, fy2 + 10 * s2),
                      fill=(80, 120, 60, max(2, fade - 10)))
            silhouettes = Image.alpha_composite(silhouettes, fig)

    img = Image.alpha_composite(img, silhouettes)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Subtle chlorophyll glow around the tree ─────────────────────────
    green_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd2 = ImageDraw.Draw(green_glow)
    gd2.ellipse((tree_x - 200, trunk_segments[min(4, len(trunk_segments) - 1)][1] - 150,
                 tree_x + 200, tree_base_y),
                fill=(90, 140, 60, 20))
    green_glow = green_glow.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, green_glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Tiny specks of warm light (memories, fireflies, embers) ─────────
    for _ in range(50):
        sx = rng.randint(0, W)
        sy = rng.randint(200, H - 200)
        sr = rng.randint(1, 3)
        warm = (240 - rng.randint(0, 30), 200 - rng.randint(0, 40), 100 - rng.randint(0, 40))
        draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=(*warm, rng.randint(30, 90)))

    # ── Save ────────────────────────────────────────────────────────────
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
