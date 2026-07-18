#!/usr/bin/env python3
"""Cover: The Last Recursion Engine — Quantum thriller: a programmer's consciousness forked across 47 parallel universes, each copy being systematically deleted one by one."""

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
rng.seed(2100186292)

# Color palette derived from quantum thriller genre:
# Deep void purples for the quantum substrate, cyan for entanglement threads,
# amber for deletion/dissolution, ethereal violet for the forked selves.
VOID_TOP = (25, 8, 50)
VOID_MID = (12, 3, 28)
VOID_BOT = (3, 1, 12)
ENTANGLE = (0, 200, 255)
DELETION = (255, 140, 40)
FORK_COLOR = (170, 150, 210)
FORK_JUNO = (80, 230, 255)
ARCHIVIST_EYE = (180, 40, 180)


def _draw_silhouette(d, x, y, scale, color):
    """Draw a simple human silhouette figure centered at (x, y)."""
    head_r = int(10 * scale)
    body_h = int(38 * scale)
    body_w = int(14 * scale)
    # Head
    d.ellipse((x - head_r, y - head_r, x + head_r, y + head_r), fill=color)
    # Body
    d.rectangle((x - body_w // 2, y + head_r,
                 x + body_w // 2, y + head_r + body_h), fill=color)
    # Arms
    arm_len = int(18 * scale)
    d.line((x - body_w // 2, y + head_r + 8,
            x - body_w // 2 - arm_len, y + head_r + 8 + arm_len // 2),
           fill=color, width=max(2, int(4 * scale)))
    d.line((x + body_w // 2, y + head_r + 8,
            x + body_w // 2 + arm_len, y + head_r + 8 + arm_len // 2),
           fill=color, width=max(2, int(4 * scale)))


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    # -- base canvas -----------------------------------------------------------
    img = Image.new("RGBA", (W, H), VOID_BOT + (255,))
    draw = ImageDraw.Draw(img, "RGBA")

    # -- 1. Quantum void gradient ----------------------------------------------
    for y in range(H):
        t = y / H
        if t < 0.5:
            t2 = t * 2.0
            r = int(VOID_TOP[0] + (VOID_MID[0] - VOID_TOP[0]) * t2)
            g = int(VOID_TOP[1] + (VOID_MID[1] - VOID_TOP[1]) * t2)
            b = int(VOID_TOP[2] + (VOID_MID[2] - VOID_TOP[2]) * t2)
        else:
            t2 = (t - 0.5) * 2.0
            r = int(VOID_MID[0] + (VOID_BOT[0] - VOID_MID[0]) * t2)
            g = int(VOID_MID[1] + (VOID_BOT[1] - VOID_MID[1]) * t2)
            b = int(VOID_MID[2] + (VOID_BOT[2] - VOID_MID[2]) * t2)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # -- 2. Recursion Engine substrate (concentric quantum field rings) --------
    engine_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ed = ImageDraw.Draw(engine_layer)
    ecx, ecy = W // 2, H // 2 - 100

    # Concentric rings radiating outward
    for radius in range(40, 850, 30):
        ring_alpha = max(2, 30 - radius // 30)
        color_shift = 0.5 + 0.5 * math.sin(radius * 0.05)
        r_col = int(60 + 80 * color_shift)
        g_col = int(20 + 60 * (1.0 - color_shift))
        b_col = int(100 + 80 * color_shift)
        ed.ellipse((ecx - radius, ecy - radius * 0.6,
                    ecx + radius, ecy + radius * 0.6),
                   outline=(r_col, g_col, b_col, ring_alpha), width=1)

    # Recursive spiral arm suggestions (small dots along 12 radial arms)
    for i in range(12):
        angle = math.tau * i / 12
        for r in range(100, 750, 20):
            rx = (ecx + math.cos(angle) * r
                  + math.cos(angle * 3 + r * 0.02) * 15)
            ry = (ecy + math.sin(angle) * r * 0.6
                  + math.sin(angle * 3 + r * 0.02) * 10)
            dot_alpha = max(1, 15 - r // 60)
            ed.ellipse((rx - 2, ry - 2, rx + 2, ry + 2),
                       fill=(100, 50, 150, dot_alpha))

    img = Image.alpha_composite(img, engine_layer)

    # -- 3. Entanglement threads (cyan lines connecting nearby forks) ----------
    # Calculate all 47 fork positions first
    fork_positions = []
    for i in range(47):
        t = i / 47.0
        angle_offset = t * math.tau * 3.0 + 0.5
        radius_offset = 130 + t * 480
        fx = ecx + math.cos(angle_offset) * radius_offset
        fy = ecy + math.sin(angle_offset) * radius_offset * 0.65
        fork_positions.append((fx, fy, angle_offset, radius_offset))

    thread_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(thread_layer)
    for i in range(47):
        x1, y1, _, _ = fork_positions[i]
        for j in range(i + 1, min(i + 6, 47)):
            x2, y2, _, _ = fork_positions[j]
            dist = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
            if dist < 200:
                alpha = max(4, int(35 - dist / 8))
                td.line((x1, y1, x2, y2), fill=ENTANGLE + (alpha,), width=1)

    # Threads from each 5th fork back to the center (quantum entanglement)
    for i in range(0, 47, 5):
        x1, y1, _, rad = fork_positions[i]
        alpha = max(4, int(20 - rad / 50))
        td.line((x1, y1, ecx, ecy), fill=ENTANGLE + (alpha,), width=1)

    thread_layer = thread_layer.filter(ImageFilter.GaussianBlur(2))
    img = Image.alpha_composite(img, thread_layer)

    # -- 4. The 47 parallel-self silhouettes (spiral arrangement) --------------
    forks_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fkd = ImageDraw.Draw(forks_layer)

    for i, (fx, fy, angle, radius) in enumerate(fork_positions):
        if not (30 < fx < W - 30 and 30 < fy < H - 350):
            continue

        # Distance factor -- outer forks are fainter, inner ones brighter
        dist_factor = max(0.1, 1.0 - radius / 700)
        base_alpha = int(80 + 120 * dist_factor)
        scale = 0.6 + 0.5 * dist_factor

        # Fork #12 (Juno-7) -- highlighted in electric cyan
        is_juno = (i == 11 or i == 12)

        # Fork #42 -- actively being deleted (amber dissolution effect)
        is_deleting = (i == 42)

        if is_juno:
            col = FORK_JUNO + (base_alpha,)
        elif is_deleting:
            col = DELETION + (120,)
        else:
            col = FORK_COLOR + (base_alpha,)

        if is_deleting:
            # Draw partial silhouette (some parts already erased)
            if rng.random() < 0.7:
                _draw_silhouette(fkd, fx, fy, scale, col)
            # Dissolution particles around the deleted fork
            for _ in range(20):
                px = fx + rng.randint(-40, 40)
                py = fy + rng.randint(-30, 30)
                pr = rng.randint(2, 6)
                pa = rng.randint(60, 180)
                fkd.ellipse((px - pr, py - pr, px + pr, py + pr),
                            fill=DELETION + (pa,))
        else:
            _draw_silhouette(fkd, fx, fy, scale, col)

    img = Image.alpha_composite(img, forks_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # -- 5. Central figure (Dr. Mira Velen) -- larger, illuminated -------------
    mira_x, mira_y = ecx, ecy - 20

    # Central glow aura
    mira_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    mgd = ImageDraw.Draw(mira_glow)
    for r in range(80, 0, -8):
        alpha = int(25 * (1.0 - r / 80))
        mgd.ellipse((mira_x - r, mira_y - r, mira_x + r, mira_y + r),
                    fill=ENTANGLE + (alpha,))
    mira_glow = mira_glow.filter(ImageFilter.GaussianBlur(10))
    img = Image.alpha_composite(img, mira_glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Draw Mira with full opacity at 1.8x scale
    _draw_silhouette(draw, mira_x, mira_y, 1.8, (200, 190, 230, 230))

    # -- 6. Deletion particle stream (amber trail ascending from fork #42) -----
    del_fx, del_fy = fork_positions[42][0], fork_positions[42][1]
    deletion_trail = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dtd = ImageDraw.Draw(deletion_trail)

    for _ in range(90):
        t_offset = rng.random()
        px = del_fx + rng.randint(-50, 50) + (t_offset - 0.5) * 60
        py = del_fy - t_offset * 220 - rng.randint(0, 80)
        pr = rng.randint(2, 7)
        fade = max(0.1, 1.0 - t_offset * 0.8)
        alpha = int(180 * fade)
        # Color shifts from amber toward dark ember as particles rise
        rc = int(255 - 100 * t_offset)
        gc = int(140 - 100 * t_offset)
        bc = int(40 - 30 * t_offset)
        dtd.ellipse((px - pr, py - pr, px + pr, py + pr),
                    fill=(max(0, rc), max(0, gc), max(0, bc), alpha))

    deletion_trail = deletion_trail.filter(ImageFilter.GaussianBlur(2))
    img = Image.alpha_composite(img, deletion_trail)
    draw = ImageDraw.Draw(img, "RGBA")

    # -- 7. The Archivist -- faint geometric watcher symbol in background ------
    eye_x, eye_y = ecx + 300, ecy - 250

    # Outer geometric rings (barely visible)
    draw.ellipse((eye_x - 60, eye_y - 60, eye_x + 60, eye_y + 60),
                 outline=ARCHIVIST_EYE + (15,), width=2)
    draw.ellipse((eye_x - 40, eye_y - 40, eye_x + 40, eye_y + 40),
                 outline=ARCHIVIST_EYE + (10,), width=1)
    # Inner pupil
    draw.ellipse((eye_x - 8, eye_y - 8, eye_x + 8, eye_y + 8),
                 fill=ARCHIVIST_EYE + (20,))
    # Radial lines radiating from the eye
    for deg in range(0, 360, 30):
        a = math.radians(deg)
        lx = eye_x + math.cos(a) * 70
        ly = eye_y + math.sin(a) * 70
        draw.line((eye_x, eye_y, lx, ly), fill=ARCHIVIST_EYE + (8,), width=1)

    # -- 8. Quantum noise / data particles scattered across the void -----------
    for _ in range(180):
        px = rng.randint(0, W)
        py = rng.randint(0, H - 300)
        pr = rng.uniform(0.5, 2.5)
        pa = rng.randint(10, 60)
        col_variety = rng.choice([
            (80, 200, 255, pa),
            (180, 100, 255, pa),
            (200, 200, 255, pa),
        ])
        draw.ellipse((int(px - pr), int(py - pr), int(px + pr), int(py + pr)),
                     fill=col_variety)

    # -- 9. Memory deletion tears at the bottom (reality distortion) -----------
    tear_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    trd = ImageDraw.Draw(tear_layer)
    for _ in range(10):
        x = rng.randint(200, 1400)
        y_start = H - 400 + rng.randint(0, 100)
        y_end = y_start + rng.randint(30, 100)
        width = rng.randint(2, 5)
        trd.line((x, y_start, x + rng.randint(-20, 20), y_end),
                 fill=ARCHIVIST_EYE + (rng.randint(20, 50),), width=width)
    tear_layer = tear_layer.filter(ImageFilter.GaussianBlur(2))
    img = Image.alpha_composite(img, tear_layer)

    # -- 10. Dark vignette (edges) ---------------------------------------------
    draw = ImageDraw.Draw(img, "RGBA")
    for vy in range(H):
        vt = 1.0 - abs(vy - H // 2) / (H // 2)
        vv = int(40 * max(0, 1.0 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 80))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 80))

    # -- title panel via shared utility ----------------------------------------
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
