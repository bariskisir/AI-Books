#!/usr/bin/env python3
"""Cover: Debt Flesh — Biocapitalist dystopia: organ leasing, surgical repossession, collection drones,
neural backups. A skeletal X-ray aesthetic with glowing debt-encoded bones, circling drones, and
corrupted neural signals from beyond the grave."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

RNG = random.Random()
RNG.seed(684217590)

# Cold clinical backdrop — like an unlit MRI suite
BG_TOP = (18, 22, 38)
BG_BOT = (42, 52, 72)


def _gradient(img, draw):
    """Dark clinical blue-gray vertical gradient."""
    for y in range(H):
        t = y / H
        r = int(BG_TOP[0] + (BG_BOT[0] - BG_TOP[0]) * t)
        g = int(BG_TOP[1] + (BG_BOT[1] - BG_TOP[1]) * t)
        b = int(BG_TOP[2] + (BG_BOT[2] - BG_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))


def _vignette(image):
    """Darken edges — tunnel vision, clinical isolation."""
    v = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(v)
    cx, cy = W // 2, H // 2
    for r in range(0, max(W, H) // 2, 20):
        alpha = max(0, int(120 * (1 - r / (max(W, H) / 2))))
        vd.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(0, 0, 0, alpha), width=10)
    v = v.filter(ImageFilter.GaussianBlur(40))
    return Image.alpha_composite(image, v)


def _scan_lines(draw, opacity=10):
    """Faint horizontal medical monitor scan lines."""
    for y in range(0, H, 4):
        draw.line((0, y, W, y), fill=(180, 220, 255, opacity))


def _ribcage(draw):
    """Construct a skeletal ribcage from arcs — some ribs glowing with debt."""
    cx, top = W // 2, 480
    spine_pts = []

    # Spine (central vertical — vertebrae)
    for v in range(0, 36):
        vy = top + v * 18
        vw = 10 + 4 * math.sin(v * 0.4)
        debt = 0.4 < v / 36 < 0.75  # middle section = 43 months area
        col = (220, 50, 40, 180) if debt else (140, 180, 210, 120)
        draw.ellipse((cx - vw, vy - 5, cx + vw, vy + 5), fill=col)
        spine_pts.append((cx, vy))

    # Left ribs — arcs from spine outward
    for i in range(13):
        base_y = top + 45 + i * 18 + 5 * math.sin(i * 0.7)
        span = 70 + i * 15
        if i > 7:
            span = int(span * (1 - (i - 7) * 0.12))
        curve = 30 + i * 2
        debt_flag = 5 <= i <= 9  # ribs glowing with hidden debt arrears

        rib_color = (200, 70, 50, 220) if debt_flag else (130, 170, 200, 120)
        rib_glow = (240, 120, 60, 60) if debt_flag else None

        # Left rib
        if rib_glow:
            draw.arc((cx - span - 20, base_y - curve - 10, cx - 10, base_y + curve + 10),
                     200, 280, fill=rib_glow, width=12)
        draw.arc((cx - span, base_y - curve, cx - 10, base_y + curve),
                 200, 280, fill=rib_color, width=5)

        # Right rib
        if rib_glow:
            draw.arc((cx + 10, base_y - curve - 10, cx + span + 20, base_y + curve + 10),
                     -80, 0, fill=rib_glow, width=12)
        draw.arc((cx + 10, base_y - curve, cx + span, base_y + curve),
                 -80, 0, fill=rib_color, width=5)

    # Pelvis — bone cradle
    draw.arc((cx - 160, top + 330, cx - 10, top + 430), 180, 270, fill=(130, 175, 205, 140), width=8)
    draw.arc((cx + 10, top + 330, cx + 160, top + 430), 270, 360, fill=(130, 175, 205, 140), width=8)
    draw.arc((cx - 160, top + 380, cx + 160, top + 440), 0, 180, fill=(110, 160, 190, 100), width=6)

    return cx, top


def _skull_echo(draw):
    """Faint skull silhouette — the neural echo of the mother broadcasting."""
    cx, cy = W // 2, 300
    # Skull outline
    draw.ellipse((cx - 70, cy - 80, cx + 70, cy + 40), outline=(100, 160, 200, 60), width=3)
    # Eye sockets — hollow, dark
    draw.ellipse((cx - 40, cy - 50, cx - 10, cy - 25), fill=(10, 15, 30, 200))
    draw.ellipse((cx + 10, cy - 50, cx + 40, cy - 25), fill=(10, 15, 30, 200))
    # Mouth cavity
    draw.ellipse((cx - 25, cy - 5, cx + 25, cy + 15), fill=(10, 15, 30, 200))
    # Neural crackle — data leaking from the skull
    for _ in range(12):
        sx = cx + RNG.randint(-60, 60)
        sy = cy + RNG.randint(-70, 40)
        for seg in range(3):
            ex = sx + RNG.randint(-40, 40)
            ey = sy + RNG.randint(-20, 40)
            draw.line((sx, sy, ex, ey), fill=(60, 200, 255, RNG.randint(20, 60)), width=RNG.randint(1, 3))
            sx, sy = ex, ey
    # Radiating data pulses
    for ring_r in range(80, 220, 30):
        pulse_alpha = max(5, 40 - ring_r // 6)
        draw.ellipse((cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r),
                     outline=(60, 190, 255, pulse_alpha), width=1)


def _collection_drones(draw):
    """Insectoid collection drones circling like vultures around the skeleton."""
    for _ in range(9):
        ang = RNG.random() * math.tau
        rad = RNG.randint(200, 550)
        dx = W // 2 + int(math.cos(ang) * rad)
        dy = 500 + int(math.sin(ang) * rad * 0.4)
        scale = RNG.randint(8, 16)

        # Angular drone body
        body_col = (60, 80, 100, 200)
        # Fuselage
        draw.polygon([
            (dx - scale * 2, dy),
            (dx, dy - scale * 3),
            (dx + scale * 2, dy),
            (dx, dy + scale * 2),
        ], fill=body_col)
        # Wings
        draw.polygon([
            (dx - scale, dy - scale),
            (dx - scale * 4, dy - scale * 4),
            (dx - scale * 2, dy - scale),
        ], fill=(40, 60, 80, 150))
        draw.polygon([
            (dx + scale, dy - scale),
            (dx + scale * 4, dy - scale * 4),
            (dx + scale * 2, dy - scale),
        ], fill=(40, 60, 80, 150))
        # Red sensor eye
        draw.ellipse((dx - 3, dy - 6, dx + 3, dy), fill=(255, 40, 30, 220))
        # Tracking beam (faint line toward skeleton)
        beam_target_y = dy + RNG.randint(20, 100)
        draw.line((dx, dy + 2, W // 2 + RNG.randint(-30, 30), beam_target_y),
                  fill=(255, 60, 50, RNG.randint(8, 25)), width=1)


def _neural_data_streams(draw):
    """Neural backup data broadcasting — wavy digital signals rising from the body."""
    for stream in range(7):
        base_x = 200 + stream * 200
        base_y_start = 700 + RNG.randint(-100, 100)
        pts = []
        for py in range(base_y_start, 300, -6):
            px = base_x + int(25 * math.sin(py * 0.03 + stream * 1.2) +
                              12 * math.sin(py * 0.07 + stream * 0.8))
            pts.append((px, py))
        if len(pts) > 1:
            alpha = RNG.randint(12, 35)
            col = (80, 200, 255, alpha)
            for i in range(len(pts) - 1):
                draw.line((*pts[i], *pts[i + 1]), fill=col, width=RNG.randint(1, 2))


def _repossession_hand(draw):
    """A shadowy hand reaching up from below — surgical repossession."""
    hx = W // 2 + RNG.randint(-80, 80)
    hy = H - 500
    # Forearm
    draw.polygon([
        (hx - 35, hy + 200),
        (hx + 35, hy + 200),
        (hx + 25, hy),
        (hx - 25, hy),
    ], fill=(25, 35, 55, 180))
    # Fingers reaching up
    for fi in range(5):
        fx = hx - 30 + fi * 15
        f_length = 40 + fi * 8 + RNG.randint(0, 20)
        draw.line((fx, hy, fx + RNG.randint(-8, 8), hy - f_length),
                  fill=(35, 50, 75, 200), width=5)
    # Metallic surgical clamp at fingertips
    draw.ellipse((hx - 12, hy - 60, hx + 12, hy - 40), fill=(140, 160, 180, 150))


def _glowing_debt_inscriptions(draw):
    """Faint glowing text/data fragments representing 43 months of arrears encoded in bone."""
    cx = W // 2
    for i in range(14):
        x = cx + RNG.randint(-200, 200)
        y = 520 + RNG.randint(0, 350)
        fragment = RNG.choice(["43m", "ARR", "DEBT", "DEFAULT", "REPO", "LEASE", "TERM",
                               "INTEREST", "FORECLOSE", "BALANCE", "COLLAT", "LIEN", "OWE"])
        alpha = RNG.randint(15, 50)
        draw.text((x, y), fragment, fill=(255, 80, 60, alpha))
    # Barcode-like debt strips on the bones
    for strip in range(8):
        sx = cx + RNG.randint(-160, 160)
        sy = 550 + RNG.randint(0, 280)
        for bar in range(6):
            bw = RNG.choice([2, 4, 6])
            bh = RNG.randint(8, 20)
            draw.rectangle((sx + bar * 8, sy, sx + bar * 8 + bw, sy + bh),
                           fill=(200, 60, 50, RNG.randint(40, 90)))


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (*BG_TOP, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Layer 1: Clinical gradient backdrop
    _gradient(img, draw)

    # Layer 2: Faint scan-line overlay (medical monitor aesthetic)
    _scan_lines(draw, opacity=8)

    # Layer 3: Neural data streams (mother's broadcast) — behind the body
    _neural_data_streams(draw)

    # Layer 4: Skeletal ribcage with glowing debt — the central figure
    _ribcage(draw)

    # Layer 5: Skull neural echo
    _skull_echo(draw)

    # Layer 6: Debt inscriptions glowing in the bones
    _glowing_debt_inscriptions(draw)

    # Layer 7: Collection drones circling
    _collection_drones(draw)

    # Layer 8: Repossession hand from below
    _repossession_hand(draw)

    # Layer 9: Vignette
    img = _vignette(img)
    draw = ImageDraw.Draw(img, "RGBA")

    # Layer 10: Very faint fog/atmosphere layer
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog)
    for _ in range(3):
        fx = RNG.randint(100, W - 100)
        fy = RNG.randint(100, 1500)
        fr = RNG.randint(200, 500)
        fd.ellipse((fx - fr, fy - fr, fx + fr, fy + fr),
                   fill=(100, 160, 200, RNG.randint(3, 8)))
    fog = fog.filter(ImageFilter.GaussianBlur(60))
    img = Image.alpha_composite(img, fog)

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
