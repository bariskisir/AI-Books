#!/usr/bin/env python3
"""Cover: Letters from the Wrong Address — An archivist digitizing a dead poet's love letters falls for the cold estate executor who despises the poet, then discovers the passionate letters were actually written to her in a timeline that never happened."""

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

    rng = random.Random()
    rng.seed(918273645)

    # ── base image with deep-navy-to-warm-amber gradient ──────────────────
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        if t < 0.45:
            t2 = t / 0.45
            r = int(10 + 25 * t2)
            g = int(12 + 30 * t2)
            b = int(40 + 35 * t2)
        elif t < 0.7:
            t2 = (t - 0.45) / 0.25
            r = int(35 + 60 * t2)
            g = int(42 + 50 * t2)
            b = int(75 - 15 * t2)
        else:
            t2 = (t - 0.70) / 0.30
            r = int(95 + 90 * t2)
            g = int(92 + 60 * t2)
            b = int(60 - 20 * t2)
        draw.line((0, y, W, y), fill=(min(r, 255), min(g, 255), min(b, 255), 255))

    # ── temporary canvas for bird's-eye letters ──────────────────────────
    letter_canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    # Generate letter positions: (cx, cy, w, h, angle_rad, is_ghost)
    positions = []
    for i in range(18):
        cx = rng.randint(120, W - 120)
        cy = rng.randint(350, 2000)
        w = rng.randint(140, 230)
        h = rng.randint(190, 290)
        angle = rng.uniform(-0.45, 0.45)
        is_ghost = i >= 14  # last 4 are "wrong timeline" letters
        positions.append((cx, cy, w, h, angle, is_ghost))

    for cx, cy, lw, lh, angle, is_ghost in positions:
        cw, ch = lw + 60, lh + 60  # canvas size for each letter

        # ── shadow layer ─────────────────────────────────────────────
        shadow = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        sd.rectangle((34, 34, lw + 34, lh + 34), fill=(0, 0, 0, 80))
        shadow = shadow.filter(ImageFilter.GaussianBlur(6))

        # ── letter surface ──────────────────────────────────────────
        leaf = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        ld = ImageDraw.Draw(leaf)

        if is_ghost:
            # ghost letter — translucent, pale, slightly blue
            paper = (195, 200, 205, 70)
            ld.rectangle((30, 30, lw + 30, lh + 30), fill=paper,
                         outline=(170, 180, 190, 50), width=2)
            for _ in range(3):
                lx = rng.randint(50, lw - 30)
                ly = rng.randint(60, lh - 20)
                llen = rng.randint(40, lw - 60)
                ld.line([(lx, ly), (lx + llen, ly)], fill=(160, 170, 180, 35), width=2)
        else:
            # warm parchment letter
            paper = (235, 222, 195, rng.randint(200, 245)) if rng.random() < 0.7 \
                else (248, 235, 205, rng.randint(200, 245))
            ld.rectangle((30, 30, lw + 30, lh + 30), fill=paper,
                         outline=(175, 158, 128, rng.randint(120, 200)), width=2)
            # centerfold
            ld.line([(30, 30 + lh // 2), (lw + 30, 30 + lh // 2)],
                    fill=(200, 185, 155, 50), width=1)
            # handwriting lines
            for li in range(6):
                ly = 60 + li * 28
                llen = rng.randint(50, lw - 30)
                ld.line([(50, ly), (50 + llen, ly)],
                        fill=(115, 78, 55, rng.randint(60, 160)), width=2)
                # slight wavy overlay for handwriting feel
                ld.line([(50, ly), (50 + llen // 2, ly + 2), (50 + llen, ly)],
                        fill=(115, 78, 55, rng.randint(20, 50)), width=1)
            # address block at bottom
            for li in range(2):
                ly = 60 + 6 * 28 + 18 + li * 18
                llen = rng.randint(30, lw - 70)
                ld.line([(lw + 10 - llen, ly), (lw + 10, ly)],
                        fill=(90, 65, 45, 70), width=1)
            # postmark stamp
            pm_x = rng.randint(40, lw - 40)
            pm_y = rng.randint(60, 60 + 3 * 28)
            ld.ellipse((30 + pm_x, pm_y, 30 + pm_x + 20, pm_y + 16),
                       outline=(140, 100, 70, 50), width=1)
            ld.ellipse((30 + pm_x + 2, pm_y + 2, 30 + pm_x + 18, pm_y + 14),
                       fill=(140, 100, 70, 25))

        # ── rotate both shadow and letter ───────────────────────────
        angle_deg = angle * 180.0 / math.pi
        shadow = shadow.rotate(angle_deg, expand=False, fillcolor=(0, 0, 0, 0))
        leaf = leaf.rotate(angle_deg, expand=False, fillcolor=(0, 0, 0, 0))

        px = cx - cw // 2
        py = cy - ch // 2
        letter_canvas.paste(shadow, (px, py), shadow)
        letter_canvas.paste(leaf, (px, py), leaf)

    img = Image.alpha_composite(img, letter_canvas)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── rose-gold ink trails connecting letters ─────────────────────────
    for i in range(len(positions) - 2):
        cx1, cy1 = positions[i][0], positions[i][1]
        cx2, cy2 = positions[i + 1][0], positions[i + 1][1]
        steps = 40
        for s in range(steps):
            t = s / steps
            x = cx1 + (cx2 - cx1) * t
            y = cy1 + (cy2 - cy1) * t + 50 * math.sin(t * math.pi * 2.5)
            alpha = int(45 * (1.0 - abs(t - 0.5) * 2.0))
            col = (190, 105, 125, alpha)
            draw.ellipse((int(x) - 1, int(y) - 1, int(x) + 1, int(y) + 1), fill=col)

    # ── ink splatters ───────────────────────────────────────────────────
    for _ in range(55):
        sx = rng.randint(40, W - 40)
        sy = rng.randint(250, 1950)
        sr = rng.uniform(1.5, 9.0)
        sa = rng.randint(25, 100)
        draw.ellipse((int(sx - sr), int(sy - sr), int(sx + sr), int(sy + sr)),
                     fill=(75, 45, 55, sa))
        if sr > 5 and rng.random() < 0.4:
            # secondary splatter
            sr2 = sr * rng.uniform(0.3, 0.6)
            draw.ellipse((int(sx + sr - sr2), int(sy - sr2),
                          int(sx + sr + sr2), int(sy + sr2)),
                         fill=(75, 45, 55, sa // 2))

    # ── ghostly poet silhouette (very subtle) ──────────────────────────
    poet = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(poet)
    face_cx, face_cy = W // 2, 850
    pd.ellipse((face_cx - 65, face_cy - 80, face_cx + 65, face_cy + 50),
               fill=(210, 200, 185, 14))
    pd.ellipse((face_cx - 130, face_cy + 30, face_cx + 130, face_cy + 170),
               fill=(210, 200, 185, 10))
    # hair flowing to one side
    pd.ellipse((face_cx - 80, face_cy - 95, face_cx - 15, face_cy + 40),
               fill=(180, 170, 160, 18))
    # hand reaching down toward letters
    pd.ellipse((face_cx + 100, face_cy + 60, face_cx + 150, face_cy + 130),
               fill=(210, 200, 185, 8))
    poet = poet.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(img, poet)

    # ── warm desk-lamp glow ─────────────────────────────────────────────
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((200, 500, 1400, 1900), fill=(255, 210, 160, 18))
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    img = Image.alpha_composite(img, glow)

    # ── vignette ────────────────────────────────────────────────────────
    for vy in range(H):
        vt = 1.0 - abs(vy - H // 2) / (H // 2)
        vv = int(28 * max(0.0, 1.0 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 70))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 70))

    # Also top/bottom vignette
    for vx in range(W):
        dist_center = abs(vx - W // 2) / (W // 2)
        vt = int(25 * max(0.0, dist_center - 0.4) / 0.6)
        for y_off, y_val in [(0, 0), (1, H - 1)]:
            for i in range(vt):
                px2 = vx
                py2 = y_val + (i if y_off == 0 else -i)
                if 0 <= py2 < H:
                    draw.point((px2, py2), fill=(0, 0, 0, 60))

    # ── finalise ─────────────────────────────────────────────────────────
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
