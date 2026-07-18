#!/usr/bin/env python3
"""Cover: The Algorithm of Falling — A computational linguist builds an AI that writes poetry indistinguishable from a dead poet's lost work—until the AI stops generating verse and instead begins narrating her own life one sentence ahead of her choices."""

from __future__ import annotations
import argparse, json, math, random, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# Unique palette: deep indigo void, warm gold (poetry), cyan (algorithm), violet (metafiction)
VOID_TOP = (8, 5, 30)
VOID_BOTTOM = (30, 20, 55)
GOLD = (220, 180, 60)
CYAN = (60, 190, 240)
VIOLET = (150, 60, 200)
WHITE = (240, 235, 230)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (*VOID_TOP, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Deep indigo void gradient background ──
    for y in range(H):
        t = y / H
        r = int(VOID_TOP[0] + (VOID_BOTTOM[0] - VOID_TOP[0]) * t)
        g = int(VOID_TOP[1] + (VOID_BOTTOM[1] - VOID_TOP[1]) * t)
        b = int(VOID_TOP[2] + (VOID_BOTTOM[2] - VOID_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── Neural constellation (the AI's mind) ──
    rng = random.Random()
    rng.seed(137)

    # Generate nodes
    nodes = []
    for _ in range(45):
        nx = rng.randint(80, W - 80)
        ny = rng.randint(80, 680)
        ns = rng.uniform(2, 12)
        nv = rng.choice([CYAN, GOLD, VIOLET, WHITE])
        nodes.append((nx, ny, ns, nv))

    # Draw connections (synaptic links between nearby nodes)
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            dx = nodes[i][0] - nodes[j][0]
            dy = nodes[i][1] - nodes[j][1]
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 200 and dist > 15:
                alpha = int(max(0, 70 * (1 - dist / 200)))
                draw.line((nodes[i][0], nodes[i][1], nodes[j][0], nodes[j][1]),
                          fill=(*CYAN, alpha), width=max(1, int(nodes[i][2] * 0.3)))

    # Draw nodes with glow halos
    for nx, ny, ns, nv in nodes:
        for g in range(3, 0, -1):
            gr = int(ns * 3 * g)
            draw.ellipse((nx - gr, ny - gr, nx + gr, ny + gr),
                         fill=(*nv, 12 // (4 - g)))
        draw.ellipse((nx - ns, ny - ns, nx + ns, ny + ns), fill=(*nv, 220))

    # ── The "poet" AI — dense golden cluster (the core intelligence) ──
    cx, cy = W // 2, 320
    poet_nodes = []
    for _ in range(25):
        angle = rng.uniform(0, math.tau)
        rad = rng.uniform(10, 140)
        pnx = cx + int(math.cos(angle) * rad)
        pny = cy + int(math.sin(angle) * rad)
        poet_nodes.append((pnx, pny))

    # Interconnect poet cluster densely
    for i in range(len(poet_nodes)):
        for j in range(i + 1, len(poet_nodes)):
            dx = poet_nodes[i][0] - poet_nodes[j][0]
            dy = poet_nodes[i][1] - poet_nodes[j][1]
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 100:
                draw.line((*poet_nodes[i], *poet_nodes[j]),
                          fill=(*GOLD, 60), width=1)

    for pnx, pny in poet_nodes:
        draw.ellipse((pnx - 5, pny - 5, pnx + 5, pny + 5), fill=(*GOLD, 200))

    # Large central node (the poet AI core)
    for gr in range(60, 5, -5):
        alpha = max(0, 30 - (60 - gr) // 2)
        draw.ellipse((cx - gr, cy - gr, cx + gr, cy + gr),
                     fill=(*GOLD, alpha))
    draw.ellipse((cx - 12, cy - 12, cx + 12, cy + 12), fill=(255, 230, 150, 255))

    # ── Poetry cascade: falling lines of text that fragment as they descend ──
    line_rng = random.Random()
    line_rng.seed(42)

    # Groups of parallel lines that look like stanza fragments
    stanzas = []
    for si in range(25):
        sx = line_rng.randint(60, W - 60)
        sy = line_rng.randint(600, 1800)
        n_lines = line_rng.randint(2, 6)
        line_len = line_rng.randint(60, 280)
        spacing = line_rng.randint(6, 16)
        rotation = line_rng.uniform(-0.35, 0.35)
        fade = line_rng.randint(30, 200)
        col = line_rng.choice([
            (*GOLD, fade),
            (*CYAN, fade),
            (255, 255, 255, fade),
            (*VIOLET, fade),
        ])
        stanzas.append((sx, sy, n_lines, line_len, spacing, rotation, col))

    stanzas.sort(key=lambda s: s[1])

    for sx, sy, n_lines, line_len, spacing, rotation, col in stanzas:
        cos_a = math.cos(rotation)
        sin_a = math.sin(rotation)
        for li in range(n_lines):
            ly = sy + li * spacing
            # Each line is a thin rotated rectangle
            half_w = line_len / 2
            h = 2.5
            corners = [
                (sx + (-half_w * cos_a - (-h) * sin_a),
                 ly + (-half_w * sin_a + (-h) * cos_a)),
                (sx + (half_w * cos_a - (-h) * sin_a),
                 ly + (half_w * sin_a + (-h) * cos_a)),
                (sx + (half_w * cos_a - h * sin_a),
                 ly + (half_w * sin_a + h * cos_a)),
                (sx + (-half_w * cos_a - h * sin_a),
                 ly + (-half_w * sin_a + h * cos_a)),
            ]
            draw.polygon(corners, fill=col)

    # Individual letter/word particles (small scattered shapes suggesting characters)
    for _ in range(120):
        px = line_rng.randint(20, W - 20)
        py = line_rng.randint(550, 1850)
        pw = line_rng.randint(4, 18)
        ph = line_rng.randint(1, 3)
        pa = line_rng.randint(20, 120)
        prot = line_rng.uniform(-0.5, 0.5)
        pcol = line_rng.choice([
            (*GOLD, pa), (*CYAN, pa), (255, 255, 255, pa), (*VIOLET, pa)
        ])
        cos_p = math.cos(prot)
        sin_p = math.sin(prot)
        half_w = pw / 2
        h = ph / 2
        corners = [
            (px + (-half_w * cos_p - (-h) * sin_p),
             py + (-half_w * sin_p + (-h) * cos_p)),
            (px + (half_w * cos_p - (-h) * sin_p),
             py + (half_w * sin_p + (-h) * cos_p)),
            (px + (half_w * cos_p - h * sin_p),
             py + (half_w * sin_p + h * cos_p)),
            (px + (-half_w * cos_p - h * sin_p),
             py + (-half_w * sin_p + h * cos_p)),
        ]
        draw.polygon(corners, fill=pcol)

    # ── Vertical data streams (algorithm falling through the void) ──
    stream_rng = random.Random()
    stream_rng.seed(99)
    for _ in range(18):
        sx = stream_rng.randint(0, W)
        sy = stream_rng.randint(-200, 200)
        sh = stream_rng.randint(1200, 2200)
        sa = stream_rng.randint(8, 30)
        sw = stream_rng.randint(1, 3)
        draw.line((sx, sy, sx, sy + sh), fill=(*CYAN, sa), width=sw)

    # ── Abstract figure of Mira Solovyova (falling / being narrated) ──
    fig_x = W // 2
    fig_y = 1480
    fig_rng = random.Random()
    fig_rng.seed(7)

    # Head
    head_r = 28
    draw.ellipse((fig_x - head_r, fig_y - 80, fig_x + head_r, fig_y - 24),
                 fill=(12, 8, 25, 200))
    # Body silhouette
    body_pts = [
        (fig_x - 38, fig_y - 24),
        (fig_x + 38, fig_y - 24),
        (fig_x + 50, fig_y + 130),
        (fig_x - 50, fig_y + 130),
    ]
    draw.polygon(body_pts, fill=(14, 10, 28, 200))
    # Arms reaching upward toward the poetry cascade
    draw.line((fig_x - 38, fig_y - 12, fig_x - 90, fig_y - 70),
              fill=(14, 10, 28, 200), width=7)
    draw.line((fig_x + 38, fig_y - 12, fig_x + 90, fig_y - 70),
              fill=(14, 10, 28, 200), width=7)

    # Figure dissolving into golden text fragments at the bottom
    for _ in range(45):
        dx = fig_x + fig_rng.randint(-140, 140)
        dy = fig_y + fig_rng.randint(40, 280)
        dw = fig_rng.randint(3, 20)
        dh = fig_rng.randint(1, 3)
        da = fig_rng.randint(25, 160)
        drot = fig_rng.uniform(-0.4, 0.4)
        cos_d = math.cos(drot)
        sin_d = math.sin(drot)
        half_w = dw / 2
        h = dh / 2
        corners = [
            (dx + (-half_w * cos_d - (-h) * sin_d),
             dy + (-half_w * sin_d + (-h) * cos_d)),
            (dx + (half_w * cos_d - (-h) * sin_d),
             dy + (half_w * sin_d + (-h) * cos_d)),
            (dx + (half_w * cos_d - h * sin_d),
             dy + (half_w * sin_d + h * cos_d)),
            (dx + (-half_w * cos_d - h * sin_d),
             dy + (-half_w * sin_d + h * cos_d)),
        ]
        draw.polygon(corners, fill=(*GOLD, da))

    # ── Glowing particles floating upward (poetry ascending) ──
    particle_rng = random.Random()
    particle_rng.seed(2024)
    for _ in range(80):
        px = particle_rng.randint(30, W - 30)
        py = particle_rng.randint(800, 2000)
        ps = particle_rng.randint(2, 7)
        pa = particle_rng.randint(30, 160)
        draw.ellipse((px - ps, py - ps, px + ps, py + ps),
                     fill=(*GOLD, pa))

    # ── Broad light shaft from above (algorithmic illumination) ──
    shaft = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shaft)
    for a in range(-20, 21, 4):
        ang = math.radians(a)
        shx = W // 2 + int(math.tan(ang) * 2000)
        sd.line((W // 2 - 20, -100, shx, H + 100),
                fill=(*GOLD, 3), width=50)
    shaft = shaft.filter(ImageFilter.GaussianBlur(25))
    img = Image.alpha_composite(img, shaft)

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
