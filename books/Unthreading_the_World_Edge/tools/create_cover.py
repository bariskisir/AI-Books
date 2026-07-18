#!/usr/bin/env python3
"""Cover: Unthreading the World-Edge — A blind weaver's apprentice who can feel the threads of fate journeys across a fractured kingdom to mend a severed destiny at the cosmic World-Edge."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# ── Fate-weaving palette: cosmic indigo, severed gold, blind-sight silver, frayed crimson ──
NIGHT_SKY = (8, 4, 28)          # deep cosmic void at top
DEPTH_ABYSS = (20, 12, 40)      # mid-sky
STONE_BASE = (35, 28, 45)       # fractured kingdom stone
THREAD_GOLD = (235, 195, 80)    # intact fate thread
THREAD_GOLD_DIM = (180, 145, 60)
THREAD_SEVERED = (220, 60, 50)  # severed thread — bleeding destiny
THREAD_BLOOD_DIM = (160, 40, 30)
BLIND_SIGHT = (190, 210, 240)   # Mara's tactile vision — silver-blue
BLIND_SIGHT_DIM = (120, 150, 190)
WORLD_EDGE_GLOW = (60, 200, 220) # the broken edge of reality
MIST_PALE = (140, 120, 180)     # fate mist
EMBER_DUST = (245, 220, 120)    # floating thread fragments

rng = random.Random()
rng.seed(761843209)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (*NIGHT_SKY, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 1. COSMIC VERTICAL GRADIENT: starless void → deep indigo → fractured stone ──
    for y in range(H):
        t = y / H
        if t < 0.35:
            lt = t / 0.35
            r = int(NIGHT_SKY[0] + (20 - NIGHT_SKY[0]) * lt)
            g = int(NIGHT_SKY[1] + (14 - NIGHT_SKY[1]) * lt)
            b = int(NIGHT_SKY[2] + (42 - NIGHT_SKY[2]) * lt)
        elif t < 0.65:
            lt = (t - 0.35) / 0.3
            r = int(20 + (DEPTH_ABYSS[0] - 20) * lt)
            g = int(14 + (DEPTH_ABYSS[1] - 14) * lt)
            b = int(42 + (DEPTH_ABYSS[2] - 42) * lt)
        else:
            lt = (t - 0.65) / 0.35
            r = int(DEPTH_ABYSS[0] + (STONE_BASE[0] - DEPTH_ABYSS[0]) * lt)
            g = int(DEPTH_ABYSS[1] + (STONE_BASE[1] - DEPTH_ABYSS[1]) * lt)
            b = int(DEPTH_ABYSS[2] + (STONE_BASE[2] - DEPTH_ABYSS[2]) * lt)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── 2. WORLD-EDGE: a jagged cosmic fissure tearing across the upper third ──
    edge_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ed = ImageDraw.Draw(edge_layer)

    # The Edge — a diagonal tear in reality from upper-left to mid-right
    tear_points = []
    for i in range(180):
        t = i / 179
        bx = int(-100 + t * 1900)
        # Fractured zigzag path — reality splintering
        zigzag = math.sin(t * 18) * 35 + math.sin(t * 43) * 12 + math.sin(t * 7) * 50
        by = int(160 + t * 900 + zigzag)
        tear_points.append((bx, by))

    # Glowing edge glow behind the tear
    for thickness in range(25, 5, -3):
        alpha = 15 - thickness // 3
        glow_pts = []
        for i, (bx, by) in enumerate(tear_points):
            t = i / 179
            offset = thickness * (1 + 0.5 * math.sin(t * 12))
            glow_pts.append((bx, by + offset))
        for i, (bx, by) in enumerate(tear_points):
            t = i / 179
            offset = thickness * (1 + 0.5 * math.sin(t * 12 + 2))
            glow_pts.insert(0, (bx, by - offset))
        ed.polygon(glow_pts, fill=(*WORLD_EDGE_GLOW, max(0, alpha)))

    # Bright inner tear
    for i in range(len(tear_points) - 1):
        x1, y1 = tear_points[i]
        x2, y2 = tear_points[i + 1]
        width = abs(int(3 + math.sin(i * 0.3) * 2))
        ed.line((x1, y1, x2, y2), fill=(*WORLD_EDGE_GLOW, 180), width=max(1, width))
        # inner bright core
        ed.line((x1, y1, x2, y2), fill=(255, 255, 255, 120), width=1)

    # Small fracture branches off the main tear
    for _ in range(30):
        idx = rng.randint(10, len(tear_points) - 10)
        fx, fy = tear_points[idx]
        angle = rng.uniform(-0.8, 0.8)
        length = rng.randint(15, 60)
        for step in range(length):
            sx = fx + int(math.cos(angle) * step + rng.randint(-2, 2))
            sy = fy + int(math.sin(angle) * step * 1.5 + rng.randint(-2, 2))
            alpha = max(10, 120 - step * 2)
            ed.ellipse((sx - 2, sy - 2, sx + 2, sy + 2), fill=(*WORLD_EDGE_GLOW, alpha))

    img = Image.alpha_composite(img, edge_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 3. FATE THREADS: a vast web of destiny strands radiating from above ──
    threads_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(threads_layer)

    # Thread origin point (above the frame — fate's loom in the cosmos)
    origin_x = W // 2 + rng.randint(-80, 80)
    origin_y = -50

    # Generate anchor points across the lower 2/3rds of the image
    anchors = []
    for _ in range(45):
        ax = rng.randint(50, W - 50)
        ay = rng.randint(700, 1900)
        anchors.append((ax, ay))

    # Draw intact fate threads from origin to anchors
    for ax, ay in anchors:
        # Thread path: origin → gentle catenary curve → anchor
        mid_x = (origin_x + ax) / 2 + rng.randint(-60, 60)
        mid_y = (origin_y + ay) / 2 + rng.randint(-40, 40)

        steps = 40
        for s in range(steps):
            t = s / steps
            # Quadratic bezier
            bx = (1 - t) ** 2 * origin_x + 2 * (1 - t) * t * mid_x + t ** 2 * ax
            by = (1 - t) ** 2 * origin_y + 2 * (1 - t) * t * mid_y + t ** 2 * ay

            alpha = rng.randint(40, 100)
            width = rng.randint(1, 3)
            color_variant = rng.randint(-15, 15)

            # Most threads are gold; some are silver-blue (Mara's special sight)
            if rng.random() < 0.15:
                col = (BLIND_SIGHT[0] + color_variant, BLIND_SIGHT[1] + color_variant, BLIND_SIGHT[2] + color_variant)
            else:
                col = (THREAD_GOLD[0] + color_variant, THREAD_GOLD[1] + color_variant, THREAD_GOLD[2] + color_variant)

            td.ellipse((bx - width, by - width, bx + width, by + width), fill=(*col, alpha))

    # ── 4. THE SEVERED THREAD: a broken golden strand, frayed ends, bleeding crimson ──
    # The thread Mara accidentally cut
    severed_start = (origin_x + 80, origin_y + 80)
    severed_end = (rng.randint(400, 600), rng.randint(900, 1100))

    # Frayed upper half
    for i in range(30):
        t = i / 29
        sx = severed_start[0] + t * (severed_end[0] - severed_start[0])
        sy = severed_start[1] + t * (severed_end[1] - severed_start[1])
        sx += rng.randint(-8, 8) + math.sin(t * 25) * 12
        sy += rng.randint(-5, 5) + math.cos(t * 20) * 8
        alpha = max(30, 200 - int(t * 160))
        width = max(1, 5 - int(t * 4))
        td.ellipse((sx - width, sy - width, sx + width, sy + width), fill=(*THREAD_GOLD_DIM, alpha))

    # Frayed end — the break point, with crimson bleed
    break_x, break_y = severed_end
    for _ in range(40):
        fx = break_x + rng.randint(-30, 30)
        fy = break_y + rng.randint(-20, 20) + rng.randint(0, 60)
        dist = math.hypot(fx - break_x, fy - break_y)
        alpha = max(20, 180 - int(dist * 3))
        sz = max(1, 4 - int(dist / 15))
        td.ellipse((fx - sz, fy - sz, fx + sz, fy + sz), fill=(*THREAD_SEVERED, alpha))

    # Bleeding crimson along the severed thread
    for _ in range(20):
        bx = break_x + rng.randint(-50, 50)
        by = break_y + rng.randint(-20, 80)
        alpha = rng.randint(30, 130)
        sz = rng.randint(2, 6)
        td.ellipse((bx - sz, by - sz, bx + sz, by + sz), fill=(*THREAD_BLOOD_DIM, alpha))

    # Loose thread ends — fine strands floating
    for _ in range(15):
        lx = break_x + rng.randint(-60, 60)
        ly = break_y + rng.randint(20, 120)
        for s in range(8):
            lx += rng.randint(-10, 10)
            ly += rng.randint(5, 15)
            alpha = max(10, 100 - s * 10)
            td.ellipse((lx - 1, ly - 1, lx + 1, ly + 1), fill=(*THREAD_GOLD, alpha))

    img = Image.alpha_composite(img, threads_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 5. MARA (blind protagonist) silhouette, reaching toward the severed thread ──
    figure_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(figure_layer)

    # Mara positioned below and to the right of the severed thread
    mara_x = severed_end[0] + 120
    mara_base = severed_end[1] + 150

    # Flowing weaver's robe — layered fabric
    robe_color = (30, 22, 45, 230)
    robe_pts = [
        (mara_x - 40, mara_base),
        (mara_x - 35, mara_base - 120),
        (mara_x - 25, mara_base - 170),
        (mara_x - 15, mara_base - 200),
        (mara_x + 10, mara_base - 210),
        (mara_x + 25, mara_base - 190),
        (mara_x + 30, mara_base - 140),
        (mara_x + 35, mara_base - 60),
        (mara_x + 38, mara_base),
    ]
    fd.polygon(robe_pts, fill=robe_color)

    # Head — tilted upward, sensing
    head_cx = mara_x + 5
    head_cy = mara_base - 240
    fd.ellipse((head_cx - 22, head_cy - 26, head_cx + 22, head_cy + 22), fill=(35, 28, 50, 230))

    # Hair — loose, flowing
    for strand in range(12):
        sx = head_cx + rng.randint(-18, 18)
        sy = head_cy + rng.randint(-10, 10)
        for s in range(10):
            sx += rng.randint(-5, 5)
            sy += rng.randint(3, 7)
            alpha = rng.randint(60, 160)
            fd.ellipse((sx - 1, sy - 1, sx + 1, sy + 1), fill=(20, 15, 35, alpha))

    # Reaching arm — left arm extended toward the severed thread
    hand_x = mara_x - 60
    hand_y = mara_base - 190
    # Sleeve
    fd.line((mara_x - 25, mara_base - 170, hand_x + 15, hand_y + 10),
            fill=(28, 20, 42, 220), width=14)
    fd.line((mara_x - 25, mara_base - 170, hand_x + 15, hand_y + 10),
            fill=(40, 32, 55, 120), width=8)
    # Arm / hand
    fd.line((hand_x + 15, hand_y + 10, hand_x, hand_y),
            fill=(50, 42, 65, 200), width=6)
    # Fingers splayed — sensing the threads
    for finger in range(5):
        ang = -1.0 + finger * 0.35
        fl = rng.randint(15, 30)
        fx = hand_x + int(math.cos(ang) * fl)
        fy = hand_y + int(math.sin(ang) * fl)
        fd.line((hand_x, hand_y, fx, fy), fill=(55, 45, 70, 180), width=2)

    # Right arm — holding a shuttle/weaving tool
    shuttle_x = mara_x + 50
    shuttle_y = mara_base - 150
    fd.line((mara_x + 25, mara_base - 190, shuttle_x, shuttle_y),
            fill=(28, 20, 42, 220), width=12)
    # Shuttle (small boat-shaped tool)
    fd.ellipse((shuttle_x - 10, shuttle_y - 5, shuttle_x + 10, shuttle_y + 5), fill=(160, 140, 100, 220))
    fd.ellipse((shuttle_x - 6, shuttle_y - 8, shuttle_x + 6, shuttle_y - 2), fill=(140, 120, 80, 200))
    # Thread wound on shuttle
    fd.ellipse((shuttle_x - 4, shuttle_y - 6, shuttle_x + 4, shuttle_y + 2), fill=(*THREAD_GOLD, 180))

    img = Image.alpha_composite(img, figure_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 6. BLIND-SIGHT WAVES: ethereal rings radiating from Mara's hand ──
    # She "sees" the threads through tactile magic
    sight_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sight_layer)

    for ring in range(8):
        radius = 30 + ring * 28
        alpha = max(6, 100 - ring * 10)
        width = max(1, 4 - ring // 2)
        # Partial arcs — like sonar pings
        start_deg = rng.randint(0, 360)
        span_deg = rng.randint(120, 240)
        col = (BLIND_SIGHT[0], BLIND_SIGHT[1], BLIND_SIGHT[2], alpha)
        sd.arc((hand_x - radius, hand_y - radius, hand_x + radius, hand_y + radius),
               start_deg, start_deg + span_deg, fill=col, width=width)

    # Extra sensing ripples toward the severed thread
    for ring in range(5):
        radius = 40 + ring * 35
        alpha = max(8, 70 - ring * 8)
        dx = severed_end[0] - hand_x
        dy = severed_end[1] - hand_y
        angle = math.degrees(math.atan2(dy, dx))
        sd.arc((hand_x - radius, hand_y - radius, hand_x + radius, hand_y + radius),
               int(angle - 40), int(angle + 40), fill=(*BLIND_SIGHT, alpha), width=max(1, 3 - ring // 2))

    img = Image.alpha_composite(img, sight_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 7. THE FRACTURED KINGDOM: distant landscape far below ──
    # Floating rock fragments and mountain silhouettes in the abyss
    land_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(land_layer)

    # Distant mountain range
    mountain_base = 1850
    mt_pts = [(0, H)]
    for x in range(0, W + 1, 8):
        base_h = mountain_base - 100
        noise = math.sin(x * 0.008 + 1.3) * 120 + math.sin(x * 0.003 + 0.7) * 60
        mt_pts.append((x, int(base_h + noise)))
    mt_pts.append((W, H))
    ld.polygon(mt_pts, fill=(25, 18, 35, 220))

    # Closer terrain ridge
    ridge_pts = [(0, H)]
    for x in range(0, W + 1, 6):
        base_h = 1850
        noise = math.sin(x * 0.012 + 2.1) * 60 + math.sin(x * 0.005 + 1.1) * 40
        ridge_pts.append((x, int(base_h + noise)))
    ridge_pts.append((W, H))
    ld.polygon(ridge_pts, fill=(30, 22, 42, 230))

    # Floating rock islands — broken chunks of the kingdom
    for _ in range(12):
        frx = rng.randint(100, W - 100)
        fry = rng.randint(1400, 1800)
        frw = rng.randint(60, 200)
        frh = rng.randint(30, 80)
        # Polygon for jagged floating rock
        rock_pts = [
            (frx - frw // 2 + rng.randint(0, 15), fry + rng.randint(-5, 5)),
            (frx - frw // 4 + rng.randint(-10, 0), fry - frh + rng.randint(-10, 0)),
            (frx + rng.randint(-10, 10), fry - frh - rng.randint(0, 20)),
            (frx + frw // 4 + rng.randint(0, 10), fry - frh + rng.randint(-5, 10)),
            (frx + frw // 2 + rng.randint(-15, 0), fry + rng.randint(-5, 5)),
        ]
        ld.polygon(rock_pts, fill=(45, 35, 55, 200))

        # Glowing thread fragment on rock
        if rng.random() < 0.5:
            gx = frx + rng.randint(-30, 30)
            gy = fry - frh // 2 + rng.randint(-10, 10)
            ld.ellipse((gx - 3, gy - 3, gx + 3, gy + 3), fill=(*THREAD_GOLD_DIM, rng.randint(60, 140)))

    # — Bottom abyss mist
    for _ in range(8):
        mx = rng.randint(-100, W + 100)
        my = rng.randint(1900, 2200)
        mw = rng.randint(200, 600)
        mh = rng.randint(60, 150)
        alpha = rng.randint(15, 40)
        ld.ellipse((mx - mw // 2, my - mh // 2, mx + mw // 2, my + mh // 2),
                   fill=(*MIST_PALE, alpha))

    img = Image.alpha_composite(img, land_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 8. SILVANUS (the hero) silhouette — distant, on a floating rock ──
    hero_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hero_layer)

    # Distant hero figure on a rock fragment
    hero_x = 280
    hero_y = 1680
    hd.ellipse((hero_x - 8, hero_y - 18, hero_x + 8, hero_y + 2), fill=(15, 10, 25, 200))  # head
    hd.line((hero_x, hero_y - 2, hero_x, hero_y + 30), fill=(15, 10, 25, 200), width=5)    # torso
    hd.line((hero_x, hero_y + 5, hero_x - 12, hero_y + 18), fill=(15, 10, 25, 180), width=3)  # sword arm
    # Sword (faint glint)
    hd.line((hero_x - 12, hero_y + 18, hero_x - 8, hero_y - 10), fill=(100, 100, 120, 120), width=2)
    hd.line((hero_x - 15, hero_y + 18, hero_x - 11, hero_y - 10), fill=(80, 80, 100, 90), width=1)
    # Faint golden thread fragment trailing from him
    for s in range(12):
        tx = hero_x - 15 - s * 3
        ty = hero_y + 20 + s * 4
        hd.ellipse((tx - 1, ty - 1, tx + 1, ty + 1), fill=(*THREAD_GOLD_DIM, max(10, 100 - s * 8)))

    img = Image.alpha_composite(img, hero_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 9. FATE EMBERS: glowing particles suspended throughout ──
    ember_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    emd = ImageDraw.Draw(ember_layer)

    for _ in range(200):
        ex = rng.randint(0, W)
        ey = rng.randint(100, 2000)
        sz = rng.uniform(1, 4)
        alpha = rng.randint(15, 80)
        col_choice = rng.random()
        if col_choice < 0.4:
            col = (THREAD_GOLD[0], THREAD_GOLD[1], THREAD_GOLD[2], alpha)
        elif col_choice < 0.7:
            col = (BLIND_SIGHT[0], BLIND_SIGHT[1], BLIND_SIGHT[2], alpha)
        elif col_choice < 0.85:
            col = (WORLD_EDGE_GLOW[0], WORLD_EDGE_GLOW[1], WORLD_EDGE_GLOW[2], alpha)
        else:
            col = (THREAD_SEVERED[0], THREAD_SEVERED[1], THREAD_SEVERED[2], alpha // 2)
        emd.ellipse((ex - sz, ey - sz, ex + sz, ey + sz), fill=col)

    # Small glittering thread fragments
    for _ in range(60):
        fx = rng.randint(0, W)
        fy = rng.randint(200, 1800)
        sz = rng.uniform(1, 2)
        alpha = rng.randint(30, 100)
        emd.ellipse((fx - sz, fy - sz, fx + sz, fy + sz), fill=(255, 240, 200, alpha))

    ember_layer = ember_layer.filter(ImageFilter.GaussianBlur(2))
    img = Image.alpha_composite(img, ember_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 10. AMBIENT GLOW LAYERS ──
    glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)

    # Glow from the World-Edge tear
    gd.ellipse((200, 100, 1400, 900), fill=(*WORLD_EDGE_GLOW, 4))

    # Glow from Mara's hand (blind-sight)
    gd.ellipse((hand_x - 150, hand_y - 150, hand_x + 150, hand_y + 150),
               fill=(*BLIND_SIGHT, 5))

    # Faint golden glow from the severed thread
    gd.ellipse((break_x - 100, break_y - 100, break_x + 100, break_y + 100),
               fill=(*THREAD_GOLD, 6))

    # Abyssal mist at bottom
    gd.ellipse((0, 1800, W, 2400), fill=(*MIST_PALE, 6))

    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(60))
    img = Image.alpha_composite(img, glow_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 11. SUBTLE VIGNETTE ──
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(35 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 80))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 80))

    # ── 12. TITLE PANEL via shared utility ──
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
