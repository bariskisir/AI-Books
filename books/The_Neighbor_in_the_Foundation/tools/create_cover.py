#!/usr/bin/env python3
"""Cover: The Neighbor in the Foundation — Lovecraftian body horror: a structural engineer discovers the city is built not on stone but on the carapace of a sleeping entity. The cover shows a gaping sinkhole fissure exposing layered chitinous plates and a vast unblinking eye in the depths."""

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
rng.seed(857346469)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (8, 3, 12, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 1. SKY GRADIENT — sickly Lovecraftian twilight ──
    for y in range(H):
        t = y / H
        sky_t = min(1, t * 0.6)
        r = 42 + int((6 - 42) * sky_t)
        g = 28 + int((2 - 28) * sky_t)
        b = 50 + int((10 - 50) * sky_t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── 2. FISSURE WALLS — organic wound in the earth ──
    cx = W // 2
    ftop = 280
    fbot = 1780

    lw_x = []
    rw_x = []
    for y in range(ftop, fbot):
        prog = (y - ftop) / (fbot - ftop)
        half = 30 + prog * 350
        wl = (22 * math.sin(y * 0.027 + 1.1) + 18 * math.sin(y * 0.061 + 3.7) +
              12 * math.sin(y * 0.013 + 0.8))
        wr = (22 * math.sin(y * 0.031 + 2.3) + 18 * math.sin(y * 0.057 + 0.2) +
              12 * math.sin(y * 0.019 + 2.1))
        lw_x.append(cx - half + wl)
        rw_x.append(cx + half + wr)

    # ── 3. CARAPACE TEXTURE — chitinous plates lining the fissure ──
    carapace_colors = [
        (30, 18, 8), (40, 22, 12), (20, 28, 16),
        (48, 32, 18), (12, 8, 5),
    ]
    for y_offset in range(0, fbot - ftop - 20, rng.randint(20, 40)):
        y1 = ftop + y_offset
        y2 = min(ftop + y_offset + rng.randint(20, 40), fbot - 1)
        idx1 = y_offset
        idx2 = min(y2 - ftop, len(lw_x) - 1)

        l1, l2 = lw_x[idx1], lw_x[idx2]
        r1, r2 = rw_x[idx1], rw_x[idx2]
        inset = rng.randint(5, 25)

        # Left wall plate
        col = rng.choice(carapace_colors)
        mx = (l1 + l2) * 0.5
        draw.polygon([
            (l1, y1), (mx - inset, y1 - rng.randint(0, 5)),
            (l2, y2), (mx - inset - rng.randint(0, 10), y2 + rng.randint(0, 3)),
        ], fill=(*col, 240))
        draw.line([(l1, y1), (mx - inset, y1 - rng.randint(0, 5)), (l2, y2)],
                  fill=(*[max(0, c - 18) for c in col], 200), width=2)

        # Right wall plate
        col = rng.choice(carapace_colors)
        mx = (r1 + r2) * 0.5
        draw.polygon([
            (r1, y1), (mx + inset, y1 - rng.randint(0, 5)),
            (r2, y2), (mx + inset + rng.randint(0, 10), y2 + rng.randint(0, 3)),
        ], fill=(*col, 240))
        draw.line([(r1, y1), (mx + inset, y1 - rng.randint(0, 5)), (r2, y2)],
                  fill=(*[max(0, c - 18) for c in col], 200), width=2)

    # ── 4. CITY BUILDINGS — silhouettes flanking the chasm ──
    def draw_buildings(side):
        if side < 0:
            x = 0
            while x < cx - 80 - rng.randint(0, 60):
                bw = rng.randint(30, 100)
                bh = rng.randint(100, 450)
                by = ftop + rng.randint(-10, 60)
                draw.rectangle((x, by - bh, x + bw, by + rng.randint(30, 120)),
                               fill=(5, 2, 8, 230))
                if rng.random() < 0.35:
                    for _ in range(rng.randint(2, 6)):
                        wx = x + rng.randint(4, max(4, bw - 8))
                        wy = by - bh + rng.randint(8, max(8, bh - 10))
                        draw.rectangle((wx, wy, wx + 4, wy + 4),
                                       fill=(255, 220, 150, rng.randint(20, 80)))
                x += bw + rng.randint(2, 20)
        else:
            x = W
            while x > cx + 80 + rng.randint(0, 60):
                bw = rng.randint(30, 100)
                bh = rng.randint(100, 450)
                by = ftop + rng.randint(-10, 60)
                draw.rectangle((x - bw, by - bh, x, by + rng.randint(30, 120)),
                               fill=(5, 2, 8, 230))
                if rng.random() < 0.35:
                    for _ in range(rng.randint(2, 6)):
                        wx = x - bw + rng.randint(4, max(4, bw - 8))
                        wy = by - bh + rng.randint(8, max(8, bh - 10))
                        draw.rectangle((wx, wy, wx + 4, wy + 4),
                                       fill=(255, 220, 150, rng.randint(20, 80)))
                x -= bw + rng.randint(2, 20)

    draw_buildings(-1)
    draw_buildings(1)

    # ── 5. THE ENTITY'S EYE — giant unblinking eye in the fissure ──
    eye_cx, eye_cy = cx, 1400

    # Fleshy outer socket
    draw.ellipse((eye_cx - 170, eye_cy - 110, eye_cx + 170, eye_cy + 110),
                 fill=(50, 12, 8, 240))
    draw.ellipse((eye_cx - 160, eye_cy - 100, eye_cx + 160, eye_cy + 100),
                 fill=(75, 20, 12, 240))

    # Sclera — sickly yellowed white
    draw.ellipse((eye_cx - 110, eye_cy - 70, eye_cx + 110, eye_cy + 70),
                 fill=(130, 115, 55, 240))
    draw.ellipse((eye_cx - 105, eye_cy - 65, eye_cx + 105, eye_cy + 65),
                 fill=(160, 140, 70, 240))

    # Iris — amber-red
    draw.ellipse((eye_cx - 60, eye_cy - 50, eye_cx + 60, eye_cy + 50),
                 fill=(155, 55, 25, 240))
    draw.ellipse((eye_cx - 55, eye_cy - 45, eye_cx + 55, eye_cy + 45),
                 fill=(175, 75, 35, 240))

    # Pupil — vertical slit
    draw.polygon([
        (eye_cx - 12, eye_cy - 45), (eye_cx + 12, eye_cy - 45),
        (eye_cx + 18, eye_cy - 8),  (eye_cx + 18, eye_cy + 8),
        (eye_cx + 12, eye_cy + 45), (eye_cx - 12, eye_cy + 45),
        (eye_cx - 18, eye_cy + 8),  (eye_cx - 18, eye_cy - 8),
    ], fill=(3, 2, 5, 250))

    # Veins and tendrils radiating from the eye into the carapace
    for i in range(28):
        angle = i * 0.224 + rng.uniform(-0.1, 0.1)
        length = rng.randint(50, 150)
        ex = eye_cx + math.cos(angle) * (165 + length * 0.3)
        ey = eye_cy + math.sin(angle) * (105 + length * 0.3)
        vein_col = (100 + rng.randint(0, 40), 12 + rng.randint(0, 15),
                    10 + rng.randint(0, 10), rng.randint(80, 170))
        draw.line((eye_cx + math.cos(angle) * 110, eye_cy + math.sin(angle) * 70,
                   ex, ey), fill=vein_col, width=rng.randint(1, 3))
        if rng.random() < 0.4:
            a2 = angle + rng.uniform(-0.6, 0.6)
            l2 = rng.randint(20, 60)
            draw.line((ex, ey, ex + math.cos(a2) * l2, ey + math.sin(a2) * l2),
                      fill=vein_col, width=1)

    # ── 6. BIOLUMINESCENT GLOW — sickly green-yellow radiance ──
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for rad in range(180, 20, -15):
        alpha = max(0, 40 - rad // 5)
        gd.ellipse((eye_cx - rad, eye_cy - rad, eye_cx + rad, eye_cy + rad),
                   fill=(90, 75, 30, alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(20))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 7. SURFACE CRACKS — branching from the fissure edges ──
    for _ in range(25):
        y = rng.randint(ftop + 80, fbot - 100)
        idx = min(y - ftop, len(lw_x) - 1)
        if rng.random() < 0.5:
            x0, dx = lw_x[idx], -rng.randint(20, 150)
        else:
            x0, dx = rw_x[idx], rng.randint(20, 150)
        dy = rng.randint(-30, 30)
        ccol = (25, 15, 8, rng.randint(120, 200))
        draw.line((x0, y, x0 + dx, y + dy), fill=ccol, width=rng.randint(1, 2))
        if rng.random() < 0.5:
            draw.line((x0 + dx // 2, y + dy // 2,
                       x0 + dx // 2 + rng.randint(-50, 50),
                       y + dy // 2 + rng.randint(-20, 20)),
                      fill=ccol, width=1)

    # ── 8. DUST / SPORES — floating particles in the fissure ──
    for _ in range(60):
        x = rng.uniform(cx - 350, cx + 350)
        y = rng.uniform(ftop + 100, fbot - 50)
        r = rng.uniform(1.0, 4.0)
        draw.ellipse((x - r, y - r, x + r, y + r),
                     fill=(160, 150, 110, rng.randint(15, 60)))

    # ── 9. VIGNETTE ──
    for y in range(200):
        a = int((1 - y / 200) * 60)
        draw.line((0, y, W, y), fill=(0, 0, 0, a))
    for y in range(H - 200, H):
        a = int(((y - (H - 200)) / 200) * 80)
        draw.line((0, y, W, y), fill=(0, 0, 0, a))

    # ── 10. TITLE PANEL ──
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
