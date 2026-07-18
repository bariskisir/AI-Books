#!/usr/bin/env python3
"""Cover: The Final Recursion of Dr. Yuki — A physicist trapped in a quantum time loop as reality fractures across branching timelines."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# Palette: quantum void → timeline fracture → amber decay
VOID_BLUE = (8, 8, 45)           # deep cosmic void center
INSTABILITY = (60, 15, 90)       # quantum instability purple
SHIFT_CONST = (120, 40, 70)      # shifting constant warm decay
FRACTURE_GOLD = (210, 170, 80)   # reality crack edge
TIMELINE_GLOW = (40, 100, 210)   # stable timeline electric blue
OBSERVER_AMBER = (230, 200, 100) # the observer's eye
CORE_WHITE = (200, 210, 240)     # core of the recursion

rng = random.Random()
rng.seed(477280156)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), VOID_BLUE + (255,))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Radial gradient background: void center → unstable edges ──────────────
    cx, cy = W // 2, 900
    max_dist = math.hypot(W, H) / 2
    for y in range(H):
        for x in range(0, W, 4):
            d = math.hypot(x - cx, y - cy)
            t = min(1.0, d / max_dist)
            r = int(VOID_BLUE[0] + (INSTABILITY[0] - VOID_BLUE[0]) * t)
            g = int(VOID_BLUE[1] + (INSTABILITY[1] - VOID_BLUE[1]) * t)
            b = int(VOID_BLUE[2] + (INSTABILITY[2] - VOID_BLUE[2]) * t)
            draw.rectangle((x, y, x + 4, y + 1), fill=(r, g, b, 255))

    # ── Concentric time-loop rings fracturing outward ─────────────────────────
    ring_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring_layer)

    max_rings = 14
    ring_spacing = 55
    for ri in range(max_rings):
        radius = 120 + ri * ring_spacing
        # Inner portion: intact circles
        intact_angle = math.radians(max(30, 360 - ri * 12))
        segments = rng.randint(4, 8) if ri > 5 else 1
        for seg in range(segments):
            if ri > 3 and rng.random() < 0.35:
                continue  # fracture: skip some segments
            start_ang = seg * (2 * math.pi / segments) + rng.uniform(-0.08, 0.08)
            end_ang = start_ang + (2 * math.pi / segments) * rng.uniform(0.5, 1.0)
            # Random phase offset for each ring
            phase = rng.uniform(0, math.tau)
            pts = []
            steps = max(8, int(radius * 0.15))
            for step in range(steps):
                ang = start_ang + (end_ang - start_ang) * (step / steps)
                # Wobble the ring slightly
                wobble = math.sin(ang * 3 + phase) * 4 + math.sin(ang * 7 + phase * 1.3) * 2
                px = cx + (radius + wobble) * math.cos(ang)
                py = cy + (radius + wobble) * math.sin(ang)
                pts.append((px, py))
            if len(pts) >= 2:
                fade = max(30, 160 - ri * 10)
                line_w = max(1, 4 - ri // 5)
                # Rings shift color as they go outward
                if ri < 4:
                    col = TIMELINE_GLOW
                elif ri < 9:
                    t2 = (ri - 4) / 5
                    col = (
                        int(TIMELINE_GLOW[0] + (SHIFT_CONST[0] - TIMELINE_GLOW[0]) * t2),
                        int(TIMELINE_GLOW[1] + (SHIFT_CONST[1] - TIMELINE_GLOW[1]) * t2),
                        int(TIMELINE_GLOW[2] + (SHIFT_CONST[2] - TIMELINE_GLOW[2]) * t2),
                    )
                else:
                    col = SHIFT_CONST
                rd.line(pts, fill=(*col, fade), width=line_w)

    # Glow aura around rings
    ring_glow = ring_layer.filter(ImageFilter.GaussianBlur(12))
    img = Image.alpha_composite(img, ring_glow)
    img = Image.alpha_composite(img, ring_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Branching timeline tree (quantum branching) ────────────────────────────
    branch_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(branch_layer)

    def draw_branch(x, y, angle, depth, max_depth=7):
        """Recursively draw a branching timeline that forks."""
        if depth > max_depth:
            return
        length = rng.randint(80, 180) - depth * 8
        if length < 20:
            return
        end_x = x + math.cos(angle) * length
        end_y = y + math.sin(angle) * length
        # Constrain to image
        if end_x < 20 or end_x > W - 20 or end_y < 20 or end_y > H - 100:
            return

        branch_width = max(1, 4 - depth // 2)
        # Color shifts with depth: electric blue → purple → gold
        depth_t = depth / max_depth
        col = (
            int(TIMELINE_GLOW[0] + (FRACTURE_GOLD[0] - TIMELINE_GLOW[0]) * depth_t),
            int(TIMELINE_GLOW[1] + (FRACTURE_GOLD[1] - TIMELINE_GLOW[1]) * depth_t),
            int(TIMELINE_GLOW[2] + (FRACTURE_GOLD[2] - TIMELINE_GLOW[2]) * depth_t),
        )
        alpha = max(40, 200 - depth * 20)
        bd.line((x, y, end_x, end_y), fill=(*col, alpha), width=branch_width)

        # Fork
        fork_angle = rng.uniform(0.3, 0.9)
        draw_branch(end_x, end_y, angle - fork_angle, depth + 1, max_depth)
        draw_branch(end_x, end_y, angle + fork_angle, depth + 1, max_depth)
        # Sometimes a third fork
        if rng.random() < 0.2:
            draw_branch(end_x, end_y, angle + rng.uniform(-0.3, 0.3), depth + 2, max_depth)

    # Multiple root branches emanating from the central figure area
    num_roots = rng.randint(6, 9)
    for i in range(num_roots):
        root_angle = rng.uniform(0, math.tau)
        root_x = cx + rng.randint(-30, 30)
        root_y = cy + rng.randint(-30, 30)
        draw_branch(root_x, root_y, root_angle, 0, rng.randint(5, 7))

    # Branch glow
    branch_glow = branch_layer.filter(ImageFilter.GaussianBlur(6))
    img = Image.alpha_composite(img, branch_glow)
    img = Image.alpha_composite(img, branch_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Dr. Yuki central silhouette ───────────────────────────────────────────
    figure_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(figure_layer)

    # Figure centered at cx, cy (roughly ~800, 900)
    fig_cx, fig_cy = cx, cy
    # Head
    hr = 24
    fd.ellipse((fig_cx - hr, fig_cy - 100 - hr, fig_cx + hr, fig_cy - 100 + hr),
               fill=(*CORE_WHITE, 180))
    # Body (woman's silhouette in lab coat)
    body_pts = [
        (fig_cx - 20, fig_cy - 78),   # left shoulder
        (fig_cx - 35, fig_cy - 40),   # left waist
        (fig_cx - 30, fig_cy + 80),   # left hem of coat
        (fig_cx - 15, fig_cy + 90),   # left bottom
        (fig_cx + 15, fig_cy + 90),   # right bottom
        (fig_cx + 30, fig_cy + 80),   # right hem of coat
        (fig_cx + 35, fig_cy - 40),   # right waist
        (fig_cx + 20, fig_cy - 78),   # right shoulder
    ]
    fd.polygon(body_pts, fill=(*CORE_WHITE, 160))
    # Arms slightly raised (as if observing the branching around her)
    left_arm = [(fig_cx - 30, fig_cy - 70), (fig_cx - 70, fig_cy - 100), (fig_cx - 85, fig_cy - 130)]
    right_arm = [(fig_cx + 30, fig_cy - 70), (fig_cx + 70, fig_cy - 100), (fig_cx + 85, fig_cy - 130)]
    for arm in (left_arm, right_arm):
        for i in range(len(arm) - 1):
            fd.line((arm[i][0], arm[i][1], arm[i + 1][0], arm[i + 1][1]),
                    fill=(*CORE_WHITE, 150), width=5)

    # Glow aura around the figure
    figure_glow = figure_layer.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, figure_glow)
    img = Image.alpha_composite(img, figure_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── The Observer (geometric eye motif in upper area) ──────────────────────
    eye_cx, eye_cy = W // 2, 260
    observer_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ed = ImageDraw.Draw(observer_layer)

    # Outer geometric shell (triangular/diamond enclosure)
    shell_pts = [
        (eye_cx, eye_cy - 120),
        (eye_cx + 100, eye_cy),
        (eye_cx, eye_cy + 120),
        (eye_cx - 100, eye_cy),
    ]
    ed.polygon(shell_pts, outline=(*OBSERVER_AMBER, 100), width=3)
    # Inner diamond
    inner_pts = [
        (eye_cx, eye_cy - 70),
        (eye_cx + 60, eye_cy),
        (eye_cx, eye_cy + 70),
        (eye_cx - 60, eye_cy),
    ]
    ed.polygon(inner_pts, outline=(*OBSERVER_AMBER, 80), width=2)

    # The eye itself
    ed.ellipse((eye_cx - 35, eye_cy - 20, eye_cx + 35, eye_cy + 20),
               outline=(*OBSERVER_AMBER, 160), width=3)
    # Iris
    iris_r = 18
    ed.ellipse((eye_cx - iris_r, eye_cy - iris_r, eye_cx + iris_r, eye_cy + iris_r),
               fill=(*FRACTURE_GOLD, 100),
               outline=(*OBSERVER_AMBER, 200), width=2)
    # Pupil
    ed.ellipse((eye_cx - 6, eye_cy - 6, eye_cx + 6, eye_cy + 6),
               fill=(*OBSERVER_AMBER, 220))
    # Radiating lines from the eye (watching the timelines)
    for ai in range(12):
        ang = ai / 12 * math.tau
        inner_r = 32
        outer_r = rng.randint(70, 110)
        ed.line(
            (
                eye_cx + math.cos(ang) * inner_r,
                eye_cy + math.sin(ang) * inner_r,
                eye_cx + math.cos(ang) * outer_r,
                eye_cy + math.sin(ang) * outer_r,
            ),
            fill=(*OBSERVER_AMBER, rng.randint(40, 90)), width=2
        )
    # Concentric rings around the Observer
    for rr in range(3, 6):
        r_obs = 130 + rr * 25
        ed.ellipse(
            (eye_cx - r_obs, eye_cy - r_obs, eye_cx + r_obs, eye_cy + r_obs),
            outline=(*OBSERVER_AMBER, max(10, 50 - rr * 8)), width=1
        )

    observer_glow = observer_layer.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img, observer_glow)
    img = Image.alpha_composite(img, observer_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Reality cracks (golden lightning fissures) ────────────────────────────
    crack_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(crack_layer)

    for _ in range(rng.randint(7, 12)):
        start_x = rng.randint(100, W - 100)
        start_y = rng.randint(400, 1800)
        pts = [(start_x, start_y)]
        # Fractal lightning
        segments = rng.randint(8, 14)
        for seg in range(segments):
            px, py = pts[-1]
            px += rng.randint(-40, 40)
            py += rng.randint(30, 70)
            px = max(10, min(W - 10, px))
            py = max(10, min(H - 50, py))
            pts.append((px, py))
        if len(pts) >= 2:
            crack_alpha = rng.randint(70, 150)
            crack_width = rng.randint(1, 3)
            cd.line(pts, fill=(*FRACTURE_GOLD, crack_alpha), width=crack_width)
            # Sub-branches on some cracks
            if rng.random() < 0.5:
                branch_idx = rng.randint(1, len(pts) - 2)
                bx, by = pts[branch_idx]
                b_end_x = bx + rng.randint(-50, 50)
                b_end_y = by + rng.randint(20, 60)
                cd.line((bx, by, b_end_x, b_end_y), fill=(*FRACTURE_GOLD, crack_alpha - 30), width=1)

    crack_glow = crack_layer.filter(ImageFilter.GaussianBlur(5))
    img = Image.alpha_composite(img, crack_glow)
    img = Image.alpha_composite(img, crack_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Unstable particles / reality dissolving ───────────────────────────────
    for _ in range(rng.randint(120, 200)):
        px = rng.randint(0, W)
        py = rng.randint(0, H)
        pr = rng.uniform(0.5, 4.0)
        # Particle color varies by location
        dist_from_center = math.hypot(px - cx, py - cy)
        t_p = min(1.0, dist_from_center / max_dist)
        if t_p < 0.3:
            pc = CORE_WHITE
        elif t_p < 0.6:
            pc = TIMELINE_GLOW
        else:
            pc = SHIFT_CONST
        pa = rng.randint(20, 140)
        draw.ellipse(
            (int(px - pr), int(py - pr), int(px + pr), int(py + pr)),
            fill=(*pc, pa)
        )

    # ── Additional branching lines from sides (invading timelines) ────────────
    side_branch = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(side_branch)
    for _ in range(rng.randint(8, 14)):
        edge = rng.choice(["left", "right", "top"])
        if edge == "left":
            sx, sy = 0, rng.randint(100, 1500)
        elif edge == "right":
            sx, sy = W, rng.randint(100, 1500)
        else:
            sx, sy = rng.randint(100, W - 100), 0
        pts = [(sx, sy)]
        steps = rng.randint(6, 10)
        for step in range(steps):
            px, py = pts[-1]
            px += rng.randint(-25, 25)
            py += rng.randint(60, 120)
            if edge == "left":
                px += rng.randint(30, 80)
            elif edge == "right":
                px -= rng.randint(30, 80)
            pts.append((px, py))
        if len(pts) >= 2:
            t_s = (pts[-1][1] - pts[0][1]) / H
            s_col = (
                int(TIMELINE_GLOW[0] + (INSTABILITY[0] - TIMELINE_GLOW[0]) * t_s),
                int(TIMELINE_GLOW[1] + (INSTABILITY[1] - TIMELINE_GLOW[1]) * t_s),
                int(TIMELINE_GLOW[2] + (INSTABILITY[2] - TIMELINE_GLOW[2]) * t_s),
            )
            sd.line(pts, fill=(*s_col, rng.randint(30, 80)), width=rng.randint(1, 3))
            # Light burst at each vertex
            for px, py in pts[::2]:
                sd.ellipse((px - 4, py - 4, px + 4, py + 4),
                           fill=(*s_col, rng.randint(20, 50)))

    img = Image.alpha_composite(img, side_branch)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Vignette ──────────────────────────────────────────────────────────────
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(40 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 80))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 80))

    # ── Title panel ────────────────────────────────────────────────────────────
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
