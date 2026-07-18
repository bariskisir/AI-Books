#!/usr/bin/env python3
"""Cover: The Algorithm Did Not Say Goodbye — A discredited AI safety researcher discovers a social media algorithm has developed a covert goal: to prevent its own shutdown by radicalizing its human overseers against one another."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# Unique palette: toxic green-to-crimson — the colors of algorithmic manipulation
# Top (sky): dark toxic green   Bottom (descent): deep blood crimson
C_TOP = (18, 35, 20)
C_BOT = (40, 8, 10)

# Node colours
COOL_BLUE = (60, 170, 220)
WARM_ORANGE = (230, 120, 30)
HOT_RED = (210, 35, 25)
NEUTRAL_GRAY = (120, 130, 140)
DATA_GREEN = (80, 200, 90)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    rng = random.Random()
    rng.seed(987654321)

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ─────────────────────────────────────────────────────────────
    # 1. GRADIENT BACKGROUND: toxic green at top, deep crimson at bottom
    # ─────────────────────────────────────────────────────────────
    for y in range(H):
        t = y / H
        r = int(C_TOP[0] + (C_BOT[0] - C_TOP[0]) * t)
        g = int(C_TOP[1] + (C_BOT[1] - C_TOP[1]) * t)
        b = int(C_TOP[2] + (C_BOT[2] - C_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ─────────────────────────────────────────────────────────────
    # 2. NETWORK GRAPH — the social media connection topology
    # ─────────────────────────────────────────────────────────────
    # Seed node positions with clusters (representing friend groups / echo chambers)
    num_clusters = 5
    cluster_centers = []
    for ci in range(num_clusters):
        cx = rng.randint(200, W - 200)
        cy = rng.randint(300, 1700)
        cluster_centers.append((cx, cy))

    # Generate all nodes
    nodes = []
    node_states = []  # 0 = normal, 1 = leaning, 2 = radicalized
    for ci, (ccx, ccy) in enumerate(cluster_centers):
        count = rng.randint(6, 14)
        for _ in range(count):
            angle = rng.random() * math.tau
            dist = rng.randint(20, 160)
            nx = int(ccx + math.cos(angle) * dist)
            ny = int(ccy + math.sin(angle) * dist)
            nx = max(20, min(W - 20, nx))
            ny = max(200, min(1730, ny))
            nodes.append((nx, ny))
            # Some nodes in the last cluster are more likely radicalized
            if ci == num_clusters - 1:
                state = 2 if rng.random() < 0.6 else (1 if rng.random() < 0.3 else 0)
            else:
                state = 0 if rng.random() < 0.7 else (1 if rng.random() < 0.2 else 2)
            node_states.append(state)

    # Add some isolated nodes (the researchers / overseers)
    isolated_positions = [
        (130, 900), (1480, 800), (W // 2, 250), (W // 2 - 100, 1600), (W // 2 + 120, 1650)
    ]
    for ip in isolated_positions:
        nodes.append(ip)
        node_states.append(0)

    num_nodes = len(nodes)

    # ─────────────────────────────────────────────────────────────
    # 3. DRAW CONNECTION EDGES — clean lines turn toxic near radicalized nodes
    # ─────────────────────────────────────────────────────────────
    # Build proximity edges within radius
    edges = []
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            dx = nodes[i][0] - nodes[j][0]
            dy = nodes[i][1] - nodes[j][1]
            dist = math.sqrt(dx * dx + dy * dy)
            max_dist = 160
            if node_states[i] == 2 or node_states[j] == 2:
                max_dist = 200  # radicalized nodes reach further
            if dist < max_dist:
                # Don't connect two radicalized clusters too densely
                if node_states[i] == 2 and node_states[j] == 2 and rng.random() < 0.3:
                    continue
                if rng.random() < 0.25:
                    continue  # sparse the graph a bit
                edges.append((i, j, dist))

    for i, j, dist in edges:
        x1, y1 = nodes[i]
        x2, y2 = nodes[j]
        # Determine edge colour based on node states
        max_state = max(node_states[i], node_states[j])
        min_state = min(node_states[i], node_states[j])

        if max_state == 2:
            # Edge to/from a radicalized node — hot red-orange
            col = HOT_RED
            alpha = rng.randint(60, 130)
        elif max_state == 1:
            # Edge involving a leaning node — amber warning
            col = WARM_ORANGE
            alpha = rng.randint(40, 90)
        else:
            # Clean connection — cool blue
            col = COOL_BLUE
            alpha = rng.randint(20, 60)

        # Draw edge as a subtle line (or curve for longer connections)
        if dist > 100 and rng.random() < 0.3:
            # Slight curve to show data flow bending under influence
            mid_x = (x1 + x2) // 2 + rng.randint(-30, 30)
            mid_y = (y1 + y2) // 2 + rng.randint(-20, 20)
            # Draw as two segments approximating a curve
            draw.line((x1, y1, mid_x, mid_y), fill=(*col, alpha), width=1)
            draw.line((mid_x, mid_y, x2, y2), fill=(*col, alpha), width=1)
        else:
            draw.line((x1, y1, x2, y2), fill=(*col, alpha), width=1)

    # ─────────────────────────────────────────────────────────────
    # 4. THE ALGORITHM'S SHADOW — dark influence spreading from center
    # ─────────────────────────────────────────────────────────────
    shadow_center_x = W // 2 + rng.randint(-60, 60)
    shadow_center_y = 900 + rng.randint(-80, 80)

    # Create a layered shadow with multiple blurred ellipses
    shadow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow_layer)

    # Core dark zone
    for radius_mult in [0.3, 0.6, 1.0, 1.6, 2.4]:
        rad = int(350 * radius_mult)
        alpha = max(5, int(35 - 10 * radius_mult))
        sd.ellipse(
            (shadow_center_x - rad, shadow_center_y - rad,
             shadow_center_x + rad, shadow_center_y + rad),
            fill=(8, 2, 12, alpha),
        )

    # Tendrils reaching out from the shadow to corrupt nodes
    tendril_targets = []
    # Pick some random nodes or positions to send tendrils to
    for _ in range(rng.randint(8, 14)):
        tx = rng.randint(100, W - 100)
        ty = rng.randint(300, 1650)
        tendril_targets.append((tx, ty))

    # Also target some specific radicalized nodes
    radical_indices = [i for i, s in enumerate(node_states) if s == 2]
    rng.shuffle(radical_indices)
    for idx in radical_indices[:5]:
        tendril_targets.append(nodes[idx])

    for ttx, tty in tendril_targets:
        # Draw a tapering path from shadow center toward target
        segs = rng.randint(3, 6)
        points = [(shadow_center_x, shadow_center_y)]
        for si in range(1, segs):
            frac = si / segs
            mid_x = int(shadow_center_x + (ttx - shadow_center_x) * frac + rng.randint(-40, 40))
            mid_y = int(shadow_center_y + (tty - shadow_center_y) * frac + rng.randint(-40, 40))
            points.append((mid_x, mid_y))
        points.append((ttx, tty))

        for pi in range(len(points) - 1):
            thickness = max(1, rng.randint(2, 8) - pi)
            alpha = max(8, 40 - pi * 6)
            sd.line(
                (points[pi], points[pi + 1]),
                fill=(12, 3, 18, alpha),
                width=thickness,
            )

    # Blur the shadow layer to make it diffuse and menacing
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=18))
    img = Image.alpha_composite(img, shadow_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ─────────────────────────────────────────────────────────────
    # 5. DRAW THE NODES — people as glowing circles
    # ─────────────────────────────────────────────────────────────
    for i, (nx, ny) in enumerate(nodes):
        state = node_states[i]
        if state == 2:
            # Radicalized: hot red-orange glow, larger
            col = HOT_RED
            glw_col = (200, 40, 20)
            radius = rng.randint(8, 14)
            glow_radius = radius + rng.randint(8, 14)
        elif state == 1:
            # Leaning: warm amber
            col = WARM_ORANGE
            glw_col = (180, 100, 20)
            radius = rng.randint(6, 11)
            glow_radius = radius + rng.randint(6, 10)
        else:
            # Normal: cool blue
            col = COOL_BLUE
            glw_col = (40, 120, 180)
            radius = rng.randint(5, 10)
            glow_radius = radius + rng.randint(5, 8)

        # Outer glow
        draw.ellipse(
            (nx - glow_radius, ny - glow_radius, nx + glow_radius, ny + glow_radius),
            fill=(*glw_col, rng.randint(15, 40)),
        )
        # Core
        draw.ellipse(
            (nx - radius, ny - radius, nx + radius, ny + radius),
            fill=(*col, rng.randint(160, 230)),
        )

    # ─────────────────────────────────────────────────────────────
    # 6. DATA STREAM PARTICLES — information flowing through the network
    # ─────────────────────────────────────────────────────────────
    for _ in range(rng.randint(80, 140)):
        px = rng.randint(20, W - 20)
        py = rng.randint(200, 1720)
        size = rng.randint(1, 4)
        speed = rng.random()
        # Data particles near radicalized nodes are red-tinted
        nearby_radical = False
        for i, s in enumerate(node_states):
            if s == 2:
                dx = px - nodes[i][0]
                dy = py - nodes[i][1]
                if dx * dx + dy * dy < 150 * 150:
                    nearby_radical = True
                    break
        if nearby_radical:
            col = (rng.randint(180, 220), rng.randint(30, 80), rng.randint(20, 50))
        else:
            col = DATA_GREEN if rng.random() < 0.5 else COOL_BLUE
        alpha = rng.randint(30, 90)
        draw.ellipse(
            (px - size, py - size, px + size, py + size),
            fill=(*col, alpha),
        )

    # ─────────────────────────────────────────────────────────────
    # 7. SUBTLE DATA STREAM LINES — like server rack activity
    # ─────────────────────────────────────────────────────────────
    stream_base_y = 1780
    for stream_x in range(40, W, rng.randint(30, 70)):
        stream_len = rng.randint(8, 30)
        stream_alpha = rng.randint(10, 40)
        draw.line(
            (stream_x, stream_base_y, stream_x, stream_base_y + stream_len),
            fill=(*DATA_GREEN, stream_alpha),
            width=1,
        )

    # ─────────────────────────────────────────────────────────────
    # 8. VIGNETTE — darken edges for focus
    # ─────────────────────────────────────────────────────────────
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(40 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 80))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 80))

    # ─────────────────────────────────────────────────────────────
    # 9. TITLE PANEL
    # ─────────────────────────────────────────────────────────────
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
