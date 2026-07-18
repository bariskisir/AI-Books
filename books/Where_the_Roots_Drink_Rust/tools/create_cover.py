#!/usr/bin/env python3
"""Cover: Where the Roots Drink Rust — Looking down into a Louisiana bayou sinkhole where roots grow through abandoned machinery, pulsing with amber voice-memories of parish disasters since 1823."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# Seeded RNG for reproducibility
rng = random.Random(18230817)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    # ── COLOR PALETTE: Bayou sinkhole — murky swamp greens, rusted iron, copper voice-glow ──
    # Eco-Weird / Southern Gothic: decay, humidity, submerged machinery, organic rot
    SWAMP_SURFACE = (18, 40, 30)        # Murky bayou water surface
    SWAMP_DEPTH = (5, 12, 8)            # Impenetrable darkness below
    CYPRESS_GREEN = (30, 55, 35)        # Cypress tree / moss tones
    RUST_ORANGE = (160, 80, 30)         # Oxidized machinery
    RUST_DARK = (80, 40, 20)            # Deep rust shadow
    COPPER_GLOW = (220, 150, 60)        # Voice-memory pulse
    COPPER_DIM = (160, 100, 40)         # Faint voice residue
    MOSS_PALE = (140, 160, 120)         # Spanish moss / pale vegetation
    MACHINE_GREY = (60, 55, 50)         # Abandoned metal
    VOICE_WHITE = (240, 220, 190)       # Bright voice pulse

    img = Image.new("RGBA", (W, H), (5, 12, 8, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ═══════════════════════════════════════════════════════════════════════
    # 1. SINKHOLE RADIAL GRADIENT — dark edges, deep center
    # ═══════════════════════════════════════════════════════════════════════
    # The sinkhole is centered, with the bayou at the edges and the abyss in the middle
    sinkhole_cx, sinkhole_cy = W // 2, H // 2 - 200
    sinkhole_radius = 700

    for y in range(H):
        for x in range(0, W, 2):
            dx = (x - sinkhole_cx) / sinkhole_radius
            dy = (y - sinkhole_cy) / sinkhole_radius
            dist = math.sqrt(dx * dx + dy * dy)
            t = min(1.0, dist)

            if dist < 0.6:
                # Deep sinkhole center — near black with faint green undertone
                r = int(3 + 8 * (dist / 0.6))
                g = int(8 + 18 * (dist / 0.6))
                b = int(5 + 10 * (dist / 0.6))
            elif dist < 1.0:
                # Sinkhole walls — murky swamp water
                lt = (dist - 0.6) / 0.4
                r = int(8 + (SWAMP_SURFACE[0] - 8) * lt)
                g = int(18 + (SWAMP_SURFACE[1] - 18) * lt)
                b = int(10 + (SWAMP_SURFACE[2] - 10) * lt)
            else:
                # Bayou surface — dark green-brown with some variation
                r = int(SWAMP_SURFACE[0] + 10 * math.sin(x * 0.01))
                g = int(SWAMP_SURFACE[1] + 8 * math.sin(x * 0.007 + y * 0.005))
                b = int(SWAMP_SURFACE[2] + 5 * math.sin(x * 0.009))
            draw.point((x, y), fill=(r, g, b, 255))
            draw.point((x + 1, y), fill=(r, g, b, 255))

    # ═══════════════════════════════════════════════════════════════════════
    # 2. BAYOU EDGE — Cypress knees, Spanish moss, swamp vegetation
    # ═══════════════════════════════════════════════════════════════════════
    vegetation = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vegetation)

    # Cypress knees rising from the swamp edge (left and right borders)
    for side_x in (0, W):
        for knee in range(rng.randint(4, 7)):
            kx = side_x + rng.randint(-20, 20) if side_x == 0 else side_x - rng.randint(-20, 20)
            ky = rng.randint(200, 1800)
            k_height = rng.randint(80, 250)
            k_width = rng.randint(12, 30)
            # Knee shape: tapered cone
            vd.polygon([
                (kx - k_width, ky + k_height),
                (kx, ky),
                (kx + k_width, ky + k_height),
            ], fill=(25 + rng.randint(-5, 5), 45 + rng.randint(-8, 8), 28 + rng.randint(-5, 5), 220))
            # Knee highlight
            vd.polygon([
                (kx - k_width // 3, ky + k_height),
                (kx, ky + k_height // 4),
                (kx + k_width // 3, ky + k_height),
            ], fill=(40 + rng.randint(-5, 5), 65 + rng.randint(-8, 8), 40 + rng.randint(-5, 5), 180))

    # Spanish moss hanging from top edge
    for _ in range(rng.randint(30, 50)):
        mx = rng.randint(0, W)
        my = rng.randint(-20, 80)
        moss_len = rng.randint(40, 200)
        moss_pts = [(mx, my)]
        for _ in range(rng.randint(4, 10)):
            mx += rng.randint(-8, 8)
            my += rng.randint(15, 30)
            moss_pts.append((mx, my))
        moss_col = (MOSS_PALE[0] + rng.randint(-20, 10),
                    MOSS_PALE[1] + rng.randint(-20, 10),
                    MOSS_PALE[2] + rng.randint(-20, 10),
                    rng.randint(100, 200))
        vd.line(moss_pts, fill=moss_col, width=rng.randint(2, 5))

    # ═══════════════════════════════════════════════════════════════════════
    # 2. SUBMERGED MACHINERY — rusted engines, gears, pipes in the sinkhole walls
    # ═══════════════════════════════════════════════════════════════════════
    machinery = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(machinery)

    # Large rusted gear / wheel on the left wall
    gear_cx, gear_cy = sinkhole_cx - 350, sinkhole_cy + 200
    gear_r = 180
    for tooth in range(16):
        angle = tooth * math.tau / 16
        next_angle = (tooth + 1) * math.tau / 16
        # Gear tooth
        inner_r = gear_r - 30
        outer_r = gear_r + 20
        pts = [
            (gear_cx + math.cos(angle) * inner_r, gear_cy + math.sin(angle) * inner_r),
            (gear_cx + math.cos(angle) * outer_r, gear_cy + math.sin(angle) * outer_r),
            (gear_cx + math.cos(next_angle) * outer_r, gear_cy + math.sin(next_angle) * outer_r),
            (gear_cx + math.cos(next_angle) * inner_r, gear_cy + math.sin(next_angle) * inner_r),
        ]
        vd.polygon(pts, fill=(RUST_ORANGE[0] + rng.randint(-15, 15),
                               RUST_ORANGE[1] + rng.randint(-10, 10),
                               RUST_ORANGE[2] + rng.randint(-10, 10), 200))
    # Gear inner ring
    vd.ellipse((gear_cx - 120, gear_cy - 120, gear_cx + 120, gear_cy + 120),
               fill=(RUST_DARK[0], RUST_DARK[1], RUST_DARK[2], 200))
    vd.ellipse((gear_cx - 60, gear_cy - 60, gear_cx + 60, gear_cy + 60),
               fill=(RUST_ORANGE[0], RUST_ORANGE[1], RUST_ORANGE[2], 180))
    # Gear hub
    vd.ellipse((gear_cx - 20, gear_cy - 20, gear_cx + 20, gear_cy + 20),
               fill=(MACHINE_GREY[0], MACHINE_GREY[1], MACHINE_GREY[2], 220))

    # Rusted pipe segments embedded in the sinkhole wall (right side)
    for pipe in range(rng.randint(5, 8)):
        px = sinkhole_cx + rng.randint(200, 500)
        py = sinkhole_cy + rng.randint(-300, 600)
        p_angle = rng.uniform(-0.6, 0.6)
        p_len = rng.randint(80, 250)
        p_w = rng.randint(8, 20)
        ex = px + int(math.cos(p_angle) * p_len)
        ey = py + int(math.sin(p_angle) * p_len)
        pipe_col = (MACHINE_GREY[0] + rng.randint(-10, 20),
                    MACHINE_GREY[1] + rng.randint(-10, 15),
                    MACHINE_GREY[2] + rng.randint(-10, 10),
                    rng.randint(180, 230))
        vd.line((px, py, ex, ey), fill=pipe_col, width=p_w)
        # Pipe flange (joint ring)
        flange_x = (px + ex) // 2
        flange_y = (py + ey) // 2
        vd.ellipse((flange_x - p_w - 4, flange_y - p_w - 4,
                    flange_x + p_w + 4, flange_y + p_w + 4),
                   fill=(RUST_DARK[0], RUST_DARK[1], RUST_DARK[2], 200))
        # Rust drip
        drip_x = (px + ex) // 2 + rng.randint(-10, 10)
        drip_y = (py + ey) // 2 + rng.randint(10, 30)
        vd.line((drip_x, drip_y, drip_x + rng.randint(-3, 3), drip_y + rng.randint(20, 50)),
                fill=(RUST_ORANGE[0], RUST_ORANGE[1], RUST_ORANGE[2], rng.randint(60, 120)),
                width=rng.randint(2, 4))

    # Rusted engine block / machinery silhouette embedded in lower-left wall
    engine_x = sinkhole_cx - 450
    engine_y = sinkhole_cy + 400
    # Block shape
    vd.rectangle((engine_x - 100, engine_y - 60, engine_x + 80, engine_y + 80),
                 fill=(MACHINE_GREY[0], MACHINE_GREY[1], MACHINE_GREY[2], 200))
    vd.rectangle((engine_x - 90, engine_y - 50, engine_x + 70, engine_y + 70),
                 fill=(RUST_DARK[0], RUST_DARK[1], RUST_DARK[2], 200))
    # Cylinder bores (engine block)
    for bore in range(4):
        bx = engine_x - 60 + bore * 35
        vd.ellipse((bx - 10, engine_y - 30, bx + 10, engine_y - 10),
                   fill=(RUST_ORANGE[0], RUST_ORANGE[1], RUST_ORANGE[2], 200))
        vd.ellipse((bx - 6, engine_y - 26, bx + 6, engine_y - 14),
                   fill=(15, 12, 8, 220))

    # Rusted pipe network weaving through the sinkhole walls
    for pipe in range(rng.randint(10, 16)):
        px = sinkhole_cx + rng.randint(-500, 500)
        py = sinkhole_cy + rng.randint(-400, 600)
        pts = [(px, py)]
        segs = rng.randint(3, 6)
        for _ in range(segs):
            px += rng.randint(-80, 80)
            py += rng.randint(40, 100)
            pts.append((px, py))
        p_w = rng.randint(4, 12)
        p_alpha = rng.randint(120, 200)
        p_col = (MACHINE_GREY[0] + rng.randint(-10, 20),
                 MACHINE_GREY[1] + rng.randint(-10, 15),
                 MACHINE_GREY[2] + rng.randint(-10, 10),
                 p_alpha)
        vd.line(pts, fill=p_col, width=p_w)
        # Rust patches on pipes
        for pi in range(0, len(pts) - 1, 2):
            rx, ry = pts[pi]
            vd.ellipse((rx - 6, ry - 4, rx + 6, ry + 4),
                       fill=(RUST_ORANGE[0], RUST_ORANGE[1], RUST_ORANGE[2], rng.randint(60, 120)))

    # ═══════════════════════════════════════════════════════════════════════
    # 2b. Additional machinery — a submerged tractor/engine block lower right
    # ═══════════════════════════════════════════════════════════════════════
    tractor_x = sinkhole_cx + 300
    tractor_y = sinkhole_cy + 500
    # Blocky silhouette
    vd.rectangle((tractor_x - 80, tractor_y - 50, tractor_x + 60, tractor_y + 70),
                 fill=(MACHINE_GREY[0], MACHINE_GREY[1], MACHINE_GREY[2], 200))
    vd.rectangle((tractor_x - 70, tractor_y - 40, tractor_x + 50, tractor_y + 60),
                 fill=(RUST_DARK[0], RUST_DARK[1], RUST_DARK[2], 200))
    # Exhaust pipe
    vd.line((tractor_x + 30, tractor_y - 50, tractor_x + 40, tractor_y - 120),
            fill=(MACHINE_GREY[0], MACHINE_GREY[1], MACHINE_GREY[2], 200), width=6)
    vd.line((tractor_x + 30, tractor_y - 50, tractor_x + 40, tractor_y - 120),
            fill=(RUST_ORANGE[0], RUST_ORANGE[1], RUST_ORANGE[2], 120), width=8)
    # Wheel rim
    vd.ellipse((tractor_x - 40, tractor_y + 30, tractor_x - 10, tractor_y + 70),
               fill=(MACHINE_GREY[0], MACHINE_GREY[1], MACHINE_GREY[2], 200))
    vd.ellipse((tractor_x - 35, tractor_y + 35, tractor_x - 15, tractor_y + 65),
               fill=(RUST_DARK[0], RUST_DARK[1], RUST_DARK[2], 200))

    # ═══════════════════════════════════════════════════════════════════════
    # 3. THE ROOT SYSTEM — growing through and around the machinery
    # ═══════════════════════════════════════════════════════════════════════
    roots = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(roots)

    # Root anchor points — the roots emerge from the sinkhole walls and converge
    # toward the center, wrapping around machinery
    root_anchors = []
    for _ in range(rng.randint(20, 30)):
        angle = rng.uniform(0, math.tau)
        dist_from_center = rng.uniform(0.3, 0.95)
        rx = sinkhole_cx + int(math.cos(angle) * sinkhole_radius * dist_from_center)
        ry = sinkhole_cy + int(math.sin(angle) * sinkhole_radius * dist_from_center * 0.8)
        root_anchors.append((rx, ry))

    # Draw thick roots growing from walls toward center, wrapping machinery
    for anchor_idx, (ax, ay) in enumerate(root_anchors):
        # Each root is a thick, gnarled line from the wall toward the center
        target_x = sinkhole_cx + rng.randint(-200, 200)
        target_y = sinkhole_cy + rng.randint(-100, 500)
        segs = rng.randint(4, 10)
        pts = [(ax, ay)]
        cx, cy = ax, ay
        for seg in range(segs):
            t = (seg + 1) / segs
            # Curve toward target with some randomness
            nx = cx + (target_x - cx) * 0.25 + rng.randint(-40, 40)
            ny = cy + (target_y - cy) * 0.25 + rng.randint(-20, 30)
            pts.append((nx, ny))
            cx, cy = nx, ny
        # Draw root with varying thickness (tapering)
        for i in range(len(pts) - 1):
            thickness = max(2, int(14 - i * 1.2))
            root_col = (30 + rng.randint(-5, 10),
                        50 + rng.randint(-8, 8),
                        25 + rng.randint(-5, 5),
                        rng.randint(180, 230))
            vd.line((pts[i], pts[i + 1]), fill=root_col, width=thickness)
            # Root tendrils branching off
            if rng.random() < 0.3:
                tx, ty = pts[i]
                t_angle = rng.uniform(-1.2, 1.2)
                t_len = rng.randint(20, 60)
                vd.line((tx, ty, tx + int(math.cos(t_angle) * t_len),
                         ty + int(math.sin(t_angle) * t_len)),
                        fill=(40, 65, 35, rng.randint(100, 180)), width=rng.randint(2, 4))

    # Rusted gear / wheel on the right wall
    gear2_x = sinkhole_cx + 400
    gear2_y = sinkhole_cy + 100
    for tooth in range(12):
        angle = tooth * math.tau / 12
        next_angle = (tooth + 1) * math.tau / 12
        inner_r2 = 80
        outer_r2 = 100
        vd.polygon([
            (gear2_x + math.cos(angle) * inner_r2, gear2_y + math.sin(angle) * inner_r2),
            (gear2_x + math.cos(angle) * outer_r2, gear2_y + math.sin(angle) * outer_r2),
            (gear2_x + math.cos(next_angle) * outer_r2, gear2_y + math.sin(next_angle) * outer_r2),
            (gear2_x + math.cos(next_angle) * inner_r2, gear2_y + math.sin(next_angle) * inner_r2),
        ], fill=(RUST_DARK[0] + rng.randint(-10, 10),
                 RUST_DARK[1] + rng.randint(-5, 5),
                 RUST_DARK[2] + rng.randint(-5, 5), 200))
    vd.ellipse((gear2_x - 40, gear2_y - 40, gear2_x + 40, gear2_y + 40),
               fill=(RUST_ORANGE[0], RUST_ORANGE[1], RUST_ORANGE[2], 180))

    # Broken pipe spewing rust-water on the right
    pipe_x = sinkhole_cx + 500
    pipe_y = sinkhole_cy - 100
    vd.line((pipe_x, pipe_y, pipe_x, pipe_y + 300),
            fill=(MACHINE_GREY[0], MACHINE_GREY[1], MACHINE_GREY[2], 200), width=14)
    vd.line((pipe_x, pipe_y, pipe_x, pipe_y + 300),
            fill=(RUST_ORANGE[0], RUST_ORANGE[1], RUST_ORANGE[2], 100), width=18)
    # Broken end
    vd.ellipse((pipe_x - 10, pipe_y + 290, pipe_x + 10, pipe_y + 310),
               fill=(RUST_ORANGE[0], RUST_ORANGE[1], RUST_ORANGE[2], 200))

    # ═══════════════════════════════════════════════════════════════════════
    # 3. THE ROOT SYSTEM — growing through machinery, pulsing with voices
    # ═══════════════════════════════════════════════════════════════════════
    # Roots emerge from all directions, converging toward center, wrapping machinery

    # Generate root paths: each root is a thick organic line with branches
    root_paths = []
    for _ in range(rng.randint(18, 26)):
        # Start from a random point on the sinkhole perimeter
        start_angle = rng.uniform(0, math.tau)
        start_dist = rng.uniform(0.5, 1.0)
        sx = sinkhole_cx + int(math.cos(start_angle) * sinkhole_radius * start_dist)
        sy = sinkhole_cy + int(math.sin(start_angle) * sinkhole_radius * start_dist * 0.8)
        # Target: somewhere in the sinkhole interior, often near machinery
        tx = sinkhole_cx + rng.randint(-300, 300)
        ty = sinkhole_cy + rng.randint(-200, 500)
        # Build path
        pts = [(sx, sy)]
        cx, cy = sx, sy
        segs = rng.randint(5, 12)
        for seg in range(segs):
            t = (seg + 1) / segs
            # Curve toward target with organic wobble
            nx = cx + (tx - cx) * 0.2 + rng.randint(-30, 30)
            ny = cy + (ty - cy) * 0.2 + rng.randint(-15, 25)
            pts.append((nx, ny))
            cx, cy = nx, ny
        root_paths.append(pts)

    # Draw all roots with thickness and organic color
    for pts in root_paths:
        for i in range(len(pts) - 1):
            thickness = max(2, int(12 - i * 0.5))
            t = i / len(pts)
            # Roots are darker near the wall, slightly lighter toward center
            r_col = (25 + int(15 * t), 45 + int(20 * t), 22 + int(10 * t), rng.randint(180, 230))
            rd.line((pts[i], pts[i + 1]), fill=r_col, width=thickness)
            # Small root hairs branching off
            if rng.random() < 0.25:
                hx, hy = pts[i]
                h_angle = rng.uniform(-1.5, 1.5)
                h_len = rng.randint(15, 45)
                rd.line((hx, hy, hx + int(math.cos(h_angle) * h_len),
                         hy + int(math.sin(h_angle) * h_len)),
                        fill=(35, 55, 30, rng.randint(80, 150)), width=rng.randint(1, 3))

    # ═══════════════════════════════════════════════════════════════════════
    # 4. VOICE PULSES — Amber/copper glow nodes along the roots
    # ═══════════════════════════════════════════════════════════════════════
    voices = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vod = ImageDraw.Draw(voices)

    # Place voice-nodes along the root paths — these are the "recorded human voices"
    voice_nodes = []
    for pts in root_paths:
        # Pick 1-3 points along each root to be voice nodes
        for _ in range(rng.randint(1, 3)):
            idx = rng.randint(1, len(pts) - 2)
            vx, vy = pts[idx]
            voice_nodes.append((vx, vy))

    # Draw voice glow nodes
    for vx, vy in voice_nodes:
        # Outer glow (large, diffuse)
        glow_r = rng.randint(30, 80)
        glow_alpha = rng.randint(20, 50)
        vod.ellipse((vx - glow_r, vy - glow_r, vx + glow_r, vy + glow_r),
                    fill=(COPPER_GLOW[0], COPPER_GLOW[1], COPPER_GLOW[2], glow_alpha))
        # Inner glow
        inner_r = rng.randint(8, 20)
        vod.ellipse((vx - inner_r, vy - inner_r, vx + inner_r, vy + inner_r),
                    fill=(COPPER_GLOW[0] + 20, COPPER_GLOW[1] + 10, COPPER_GLOW[2] - 10, rng.randint(120, 200)))
        # Bright core
        vod.ellipse((vx - 4, vy - 4, vx + 4, vy + 4),
                    fill=(VOICE_WHITE[0], VOICE_WHITE[1], VOICE_WHITE[2], rng.randint(180, 240)))

    # ═══════════════════════════════════════════════════════════════════════
    # 4. VOICE WISPS — Faint spectral trails rising from the nodes
    # ═══════════════════════════════════════════════════════════════════════
    for vx, vy in voice_nodes:
        for _ in range(rng.randint(2, 5)):
            wx = vx + rng.randint(-15, 15)
            wy = vy + rng.randint(-10, 10)
            wpts = [(wx, wy)]
            for _ in range(rng.randint(3, 6)):
                wx += rng.randint(-12, 12)
                wy -= rng.randint(20, 50)
                wpts.append((wx, wy))
            w_alpha = rng.randint(30, 80)
            vod.line(wpts, fill=(COPPER_GLOW[0], COPPER_GLOW[1], COPPER_GLOW[2], w_alpha),
                     width=rng.randint(1, 3))

    # Blend roots and machinery layers
    roots = roots.filter(ImageFilter.GaussianBlur(1))
    img = Image.alpha_composite(img, roots)
    img = Image.alpha_composite(img, machinery)
    draw = ImageDraw.Draw(img, "RGBA")

    # ═══════════════════════════════════════════════════════════════════════
    # 4. VOICE GLOW — Ambient light pulsing from the roots
    # ═══════════════════════════════════════════════════════════════════════
    voice_ambient = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vad = ImageDraw.Draw(voice_ambient)

    for vx, vy in voice_nodes:
        for _ in range(rng.randint(1, 3)):
            gx = vx + rng.randint(-40, 40)
            gy = vy + rng.randint(-30, 30)
            gr = rng.randint(60, 150)
            ga = rng.randint(4, 12)
            vad.ellipse((gx - gr, gy - gr, gx + gr, gy + gr),
                        fill=(COPPER_GLOW[0], COPPER_GLOW[1], COPPER_GLOW[2], ga))

    # Large ambient glow from the deep center
    vad.ellipse((sinkhole_cx - 300, sinkhole_cy - 200, sinkhole_cx + 300, sinkhole_cy + 400),
                fill=(COPPER_GLOW[0], COPPER_GLOW[1], COPPER_GLOW[2], 6))

    voice_ambient = voice_ambient.filter(ImageFilter.GaussianBlur(20))
    img = Image.alpha_composite(img, voice_ambient)
    draw = ImageDraw.Draw(img, "RGBA")

    # ═══════════════════════════════════════════════════════════════════════
    # 5. BLEND ROOTS AND ADD DETAIL
    # ═══════════════════════════════════════════════════════════════════════
    roots = roots.filter(ImageFilter.GaussianBlur(1))
    img = Image.alpha_composite(img, roots)
    draw = ImageDraw.Draw(img, "RGBA")

    # ═══════════════════════════════════════════════════════════════════════
    # 6. VOICE WISPS — Spectral trails rising from the sinkhole
    # ═══════════════════════════════════════════════════════════════════════
    wisps = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wisps)

    for _ in range(rng.randint(20, 35)):
        wx = sinkhole_cx + rng.randint(-300, 300)
        wy = sinkhole_cy + rng.randint(-100, 400)
        wpts = [(wx, wy)]
        for _ in range(rng.randint(4, 8)):
            wx += rng.randint(-15, 15)
            wy -= rng.randint(20, 50)
            wpts.append((wx, wy))
        w_alpha = rng.randint(20, 60)
        wd.line(wpts, fill=(COPPER_GLOW[0], COPPER_GLOW[1], COPPER_GLOW[2], w_alpha),
                width=rng.randint(1, 3))

    wisps = wisps.filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(img, wisps)
    draw = ImageDraw.Draw(img, "RGBA")

    # ═══════════════════════════════════════════════════════════════════════
    # 7. SPANISH MOSS — Hanging from the top frame
    # ═══════════════════════════════════════════════════════════════════════
    moss = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    msd = ImageDraw.Draw(moss)

    for _ in range(rng.randint(20, 35)):
        mx = rng.randint(0, W)
        my = rng.randint(-10, 30)
        m_len = rng.randint(60, 250)
        m_pts = [(mx, my)]
        for _ in range(rng.randint(5, 12)):
            mx += rng.randint(-6, 6)
            my += rng.randint(15, 25)
            if my > m_len:
                break
            m_pts.append((mx, my))
        m_col = (MOSS_PALE[0] + rng.randint(-20, 10),
                 MOSS_PALE[1] + rng.randint(-20, 10),
                 MOSS_PALE[2] + rng.randint(-20, 10),
                 rng.randint(80, 180))
        msd = ImageDraw.Draw(moss)
        msd.line(m_pts, fill=m_col, width=rng.randint(2, 5))

    # ═══════════════════════════════════════════════════════════════════════
    # 8. WATER RIPPLE / REFLECTION on the sinkhole surface
    # ═══════════════════════════════════════════════════════════════════════
    water = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wad = ImageDraw.Draw(water)

    for _ in range(rng.randint(40, 60)):
        wx = sinkhole_cx + rng.randint(-500, 500)
        wy = sinkhole_cy + rng.randint(-300, 500)
        wr = rng.randint(5, 20)
        wa = rng.randint(8, 30)
        wad.ellipse((wx - wr, wy - wr, wx + wr, wy + wr),
                    fill=(COPPER_GLOW[0], COPPER_GLOW[1], COPPER_GLOW[2], wa))

    water = water.filter(ImageFilter.GaussianBlur(2))
    img = Image.alpha_composite(img, water)
    draw = ImageDraw.Draw(img, "RGBA")

    # ═══════════════════════════════════════════════════════════════════════
    # 8. HUMAN SILHOUETTE — Dr. Selene Broussard at the sinkhole edge
    # ═══════════════════════════════════════════════════════════════════════
    # Small figure at the top, looking down into the hole
    fig_x = sinkhole_cx + rng.randint(-80, 80)
    fig_y = 120
    fig_scale = 0.7
    fcol = (8, 10, 8, 220)

    # Head
    hr = int(8 * fig_scale)
    draw.ellipse((fig_x - hr, fig_y - hr, fig_x + hr, fig_y + hr), fill=fcol)
    # Body (leaning forward, looking down)
    draw.polygon([
        (fig_x - 5, fig_y + hr),
        (fig_x + 5, fig_y + hr),
        (fig_x + 8, fig_y + int(35 * fig_scale)),
        (fig_x - 8, fig_y + int(35 * fig_scale)),
    ], fill=fcol)
    # Arms (one pointing down into the sinkhole)
    draw.line((fig_x - 5, fig_y + int(10 * fig_scale),
               fig_x - int(20 * fig_scale), fig_y + int(25 * fig_scale)),
              fill=fcol, width=int(3 * fig_scale))
    draw.line((fig_x + 5, fig_y + int(10 * fig_scale),
               fig_x + int(15 * fig_scale), fig_y + int(30 * fig_scale)),
              fill=fcol, width=int(3 * fig_scale))
    # Backpack / field gear
    draw.rectangle((fig_x + 5, fig_y + hr, fig_x + int(14 * fig_scale), fig_y + int(28 * fig_scale)),
                   fill=(fcol[0], fcol[1], fcol[2], 180))
    # Headlamp (small light pointing down)
    draw.ellipse((fig_x - 3, fig_y - 2, fig_x + 3, fig_y + 4),
                 fill=(COPPER_GLOW[0], COPPER_GLOW[1], COPPER_GLOW[2], 200))
    # Headlamp beam (cone of light pointing down into the sinkhole)
    beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam)
    bd.polygon([
        (fig_x, fig_y + 4),
        (fig_x - 80, fig_y + 400),
        (fig_x + 80, fig_y + 400),
    ], fill=(COPPER_GLOW[0], COPPER_GLOW[1], COPPER_GLOW[2], 6))
    beam = beam.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img, beam)
    draw = ImageDraw.Draw(img, "RGBA")

    # ═══════════════════════════════════════════════════════════════════════
    # 9. DISASTER ECHOES — Faint text-like marks / symbols in the glow
    # ═══════════════════════════════════════════════════════════════════════
    # These represent the "recorded human voices from every disaster"
    echoes = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ed = ImageDraw.Draw(echoes)

    for _ in range(rng.randint(15, 25)):
        ex = sinkhole_cx + rng.randint(-250, 250)
        ey = sinkhole_cy + rng.randint(-100, 500)
        # Draw a tiny abstract "voice mark" — a short wavy line with a dot
        e_angle = rng.uniform(-0.5, 0.5)
        e_len = rng.randint(8, 20)
        e_alpha = rng.randint(30, 80)
        ed.line((ex, ey, ex + int(math.cos(e_angle) * e_len),
                 ey + int(math.sin(e_angle) * e_len)),
                fill=(COPPER_GLOW[0], COPPER_GLOW[1], COPPER_GLOW[2], e_alpha),
                width=rng.randint(1, 2))
        ed.ellipse((ex + int(math.cos(e_angle) * e_len) - 2,
                    ey + int(math.sin(e_angle) * e_len) - 2,
                    ex + int(math.cos(e_angle) * e_len) + 2,
                    ey + int(math.sin(e_angle) * e_len) + 2),
                   fill=(VOICE_WHITE[0], VOICE_WHITE[1], VOICE_WHITE[2], e_alpha))

    echoes = echoes.filter(ImageFilter.GaussianBlur(1))
    img = Image.alpha_composite(img, echoes)
    draw = ImageDraw.Draw(img, "RGBA")

    # ═══════════════════════════════════════════════════════════════════════
    # 10. VIGNETTE — Darken edges to focus on the sinkhole center
    # ═══════════════════════════════════════════════════════════════════════
    for y in range(H):
        for x in range(0, W, 2):
            dx = (x - sinkhole_cx) / sinkhole_radius
            dy = (y - sinkhole_cy) / sinkhole_radius
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0.7:
                fade = min(1.0, (dist - 0.7) / 0.5)
                dark = int(60 * fade)
                draw.point((x, y), fill=(0, 0, 0, dark))
                draw.point((x + 1, y), fill=(0, 0, 0, dark))

    # ═══════════════════════════════════════════════════════════════════════
    # 11. FIREFLY PARTICLES — Tiny specks of light in the bayou air
    # ═══════════════════════════════════════════════════════════════════════
    for _ in range(rng.randint(50, 80)):
        fx = rng.randint(0, W)
        fy = rng.randint(0, H - 400)
        fr = rng.uniform(1, 3)
        fa = rng.randint(30, 100)
        fcol = (COPPER_GLOW[0] + rng.randint(-20, 20),
                COPPER_GLOW[1] + rng.randint(-20, 20),
                COPPER_GLOW[2] + rng.randint(-20, 20),
                fa)
        draw.ellipse((fx - fr, fy - fr, fx + fr, fy + fr), fill=fcol)

    # ═══════════════════════════════════════════════════════════════════════
    # 12. SAVE
    # ═══════════════════════════════════════════════════════════════════════
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
