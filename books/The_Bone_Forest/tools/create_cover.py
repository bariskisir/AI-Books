#!/usr/bin/env python3
"""Cover: The Bone Forest — looking up through a canopy of anatomical bone-trees in a Mongolian forest that remembers every death."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560
# Sickly bone-pale sky, shadowed earth — the forest's own color memory
PALETTE_SKY = (95, 110, 85)       # peak of canopy: pale cadaver green
PALETTE_DEPTH = (15, 12, 18)      # forest floor: near black with purple
BONE_HIGHLIGHT = (225, 215, 190)  # fresh bone
BONE_SHADOW = (140, 125, 105)     # aged bone
BLOOD_RED = (145, 35, 30)        # the forest's remembered deaths

rng = random.Random()
rng.seed(1984032715)


def bone_joint(draw, cx, cy, angle, scale, col, width=3):
    """Draw a single bone-segment (like a femur) radiating from (cx,cy)."""
    dx = math.cos(angle) * scale * 0.5
    dy = math.sin(angle) * scale * 0.5
    # Shaft
    draw.line((cx - dx, cy - dy, cx + dx, cy + dy), fill=col, width=width)
    # Knuckle ends (ellipses oriented along the angle)
    perp_angle = angle + math.pi / 2
    for side in (-1, 1):
        sx = cx + side * dx
        sy = cy + side * dy
        kw = scale * 0.12
        kh = scale * 0.08
        # rotated ellipse approximation with two circles and a rect
        draw.ellipse(
            (sx - kw, sy - kh, sx + kw, sy + kh),
            fill=(col[0] + 20, col[1] + 15, col[2] + 10, col[3] if len(col) > 3 else 255),
        )


def bone_branch(draw, x, y, angle, depth, trunk_width):
    """Recursively draw a bone-tree branch with anatomical joints."""
    if depth <= 0:
        return
    length = 40 + depth * rng.randint(30, 55)
    taper = max(2, trunk_width - depth * 1.2)
    end_x = x + math.cos(angle) * length
    end_y = y + math.sin(angle) * length

    # Bone color: yellower toward tips
    bone_t = depth / 6.0
    br = int(BONE_HIGHLIGHT[0] - bone_t * 60)
    bg = int(BONE_HIGHLIGHT[1] - bone_t * 40)
    bb = int(BONE_HIGHLIGHT[2] - bone_t * 30)
    bcol = (max(120, br), max(100, bg), max(80, bb), 240 - int(depth * 12))

    # Draw this segment as a bone (joint at start, shaft, joint at end)
    draw.line((x, y, end_x, end_y), fill=bcol, width=int(taper))
    # Joint at start
    jr = max(3, taper * 0.5)
    draw.ellipse(
        (x - jr, y - jr, x + jr, y + jr),
        fill=(bcol[0] + 15, bcol[1] + 10, bcol[2] + 5, bcol[3]),
    )

    # Branch split
    branches = 2 + (depth % 3)
    spread = 0.5 + (6 - depth) * 0.15
    for i in range(branches):
        off_angle = angle + math.radians(rng.uniform(-spread, spread))
        off_angle += (i - branches / 2) * math.radians(20 + rng.uniform(-5, 5))
        bone_branch(draw, end_x, end_y, off_angle, depth - 1, taper)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    # ── Background gradient: dark earth → sickly bone-sky → dark earth ──
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Radial gradient: brighter at center (canopy opening), dark at edges (forest floor shadows)
    cx, cy = W // 2, int(H * 0.22)
    for y in range(H):
        for x in range(0, W, 2):
            dx = (x - cx) / W
            dy = (y - cy) / H
            dist = math.sqrt(dx * dx + dy * dy * 2.5)
            t = min(1.0, dist * 1.3)
            r = int(PALETTE_DEPTH[0] + (PALETTE_SKY[0] - PALETTE_DEPTH[0]) * (1 - t))
            g = int(PALETTE_DEPTH[1] + (PALETTE_SKY[1] - PALETTE_DEPTH[1]) * (1 - t))
            b = int(PALETTE_DEPTH[2] + (PALETTE_SKY[2] - PALETTE_DEPTH[2]) * (1 - t))
            draw.point((x, y), fill=(r, g, b, 255))
            draw.point((x + 1, y), fill=(r, g, b, 255))

    # ── Bone-tree trunks from the edges, converging toward center ──
    num_trees = rng.randint(16, 22)
    trunk_bases = []
    for _ in range(num_trees):
        side = rng.randint(0, 3)
        if side == 0:       # top
            bx, by = rng.randint(0, W), rng.randint(-50, 50)
        elif side == 1:     # bottom
            bx, by = rng.randint(0, W), rng.randint(H - 50, H + 50)
        elif side == 2:     # left
            bx, by = rng.randint(-50, 50), rng.randint(0, H)
        else:               # right
            bx, by = rng.randint(W - 50, W + 50), rng.randint(0, H)
        trunk_bases.append((bx, by))

    for bx, by in trunk_bases:
        angle = math.atan2(cy - by, cx - bx)
        angle += math.radians(rng.uniform(-15, 15))
        trunk_w = rng.randint(14, 28)
        # Draw main trunk as a thick bone segment
        seg_len = rng.randint(120, 250)
        mx = bx + math.cos(angle) * seg_len
        my = by + math.sin(angle) * seg_len
        draw.line((bx, by, mx, my), fill=(*BONE_HIGHLIGHT, 180), width=trunk_w)
        # Trunk joints
        jr = trunk_w * 0.6
        draw.ellipse((bx - jr, by - jr, bx + jr, by + jr), fill=(*BONE_HIGHLIGHT, 180))
        # Branch from trunk
        bone_branch(draw, mx, my, angle + math.radians(rng.uniform(-25, 25)),
                    rng.randint(2, 5), trunk_w * 0.7)

    # ── Bone canopy interlock (skull-dome convergence) ──
    # Draw connecting arcs between branch tips to form a cranial vault
    cnv = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cnv)
    for _ in range(rng.randint(12, 20)):
        ax = rng.randint(cx - 250, cx + 250)
        ay = rng.randint(cy - 80, cy + 120)
        bx = rng.randint(cx - 250, cx + 250)
        by = rng.randint(cy - 80, cy + 120)
        # Suture-line arcs (like skull plates meeting)
        for t in range(0, 101, 5):
            f = t / 100.0
            px = ax + (bx - ax) * f + math.sin(f * math.pi) * rng.uniform(-60, 60)
            py = ay + (by - ay) * f + math.sin(f * math.pi) * rng.uniform(-40, 40)
            scol = (BONE_HIGHLIGHT[0] - rng.randint(0, 30),
                    BONE_HIGHLIGHT[1] - rng.randint(0, 20),
                    BONE_HIGHLIGHT[2] - rng.randint(0, 15),
                    rng.randint(100, 180))
            cd.ellipse((px - 3, py - 3, px + 3, py + 3), fill=scol)
    cnv = cnv.filter(ImageFilter.GaussianBlur(4))
    img = Image.alpha_composite(img, cnv)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Red death-memory particles drifting down ──
    particles = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(particles)
    for _ in range(rng.randint(80, 150)):
        px = rng.randint(50, W - 50)
        py = rng.randint(50, H - 200)
        pr = rng.uniform(2, 7)
        pa = rng.randint(60, 160)
        pr_col = (BLOOD_RED[0] + rng.randint(-15, 15),
                  BLOOD_RED[1] + rng.randint(-5, 10),
                  BLOOD_RED[2] + rng.randint(-5, 10), pa)
        pd.ellipse((int(px - pr), int(py - pr), int(px + pr), int(py + pr)), fill=pr_col)
        # Each particle has a faint trailing wisp
        if rng.random() < 0.4:
            pd.line((px, py, px + rng.randint(-5, 5), py + rng.randint(10, 25)),
                    fill=(pr_col[0], pr_col[1], pr_col[2], pa // 3), width=1)
    particles = particles.filter(ImageFilter.GaussianBlur(2))
    img = Image.alpha_composite(img, particles)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Human silhouette (expedition figure) at bottom-centre for scale ──
    fig_x, fig_y = W // 2 + rng.randint(-40, 40), H - 420
    fcol = (5, 3, 6, 220)
    # Head
    hr = 8
    draw.ellipse((fig_x - hr, fig_y - hr, fig_x + hr, fig_y + hr), fill=fcol)
    # Body (trapezoid)
    draw.polygon([
        (fig_x - 6, fig_y + hr),
        (fig_x + 6, fig_y + hr),
        (fig_x + 12, fig_y + 50),
        (fig_x - 12, fig_y + 50),
    ], fill=fcol)
    # Backpack
    draw.rectangle((fig_x + 6, fig_y + hr, fig_x + 18, fig_y + 35), fill=(*fcol[:-1], 180))
    # Arms holding something
    draw.line((fig_x - 10, fig_y + 12, fig_x - 22, fig_y + 30), fill=fcol, width=3)
    draw.line((fig_x + 10, fig_y + 12, fig_x + 22, fig_y + 30), fill=fcol, width=3)

    # ── Atmospheric bone-haze ──
    haze = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(haze)
    for _ in range(rng.randint(8, 15)):
        hx = rng.randint(100, W - 100)
        hy = rng.randint(100, H - 400)
        hr_adius = rng.randint(100, 300)
        hcol = (BONE_HIGHLIGHT[0], BONE_HIGHLIGHT[1], BONE_HIGHLIGHT[2], rng.randint(4, 12))
        hd.ellipse((hx - hr_adius, hy - hr_adius, hx + hr_adius, hy + hr_adius), fill=hcol)
    haze = haze.filter(ImageFilter.GaussianBlur(50))
    img = Image.alpha_composite(img, haze)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Floor-level bone-litter ──
    for _ in range(rng.randint(15, 30)):
        lx = rng.randint(0, W)
        ly = rng.randint(H - 300, H - 50)
        langle = rng.uniform(0, math.tau)
        ll = rng.randint(10, 30)
        lcol = (BONE_SHADOW[0] + rng.randint(-10, 20),
                BONE_SHADOW[1] + rng.randint(-10, 20),
                BONE_SHADOW[2] + rng.randint(-10, 20),
                rng.randint(100, 200))
        draw.line((lx, ly, lx + math.cos(langle) * ll, ly + math.sin(langle) * ll),
                  fill=lcol, width=rng.randint(2, 4))
        # tiny joint at one end
        draw.ellipse((lx - 2, ly - 2, lx + 2, ly + 2), fill=lcol)

    # ── Shadow vignette ──
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(35 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 80))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 80))

    # ── Title panel ──
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
