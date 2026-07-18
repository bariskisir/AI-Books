#!/usr/bin/env python3
"""Cover: The Bone Accord — Grimdark Political Fantasy: three apprentices assemble a dead bone-oracle's fragmented prophecy from her skeleton as an invading army breaches the mountain city walls; each bone foretells a different future."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# ── Grimdark Siege Palette ─────────────────────────────────────────────────────
# charred crimson sky, iron-grey stone, bone marrow white, prophetic witch-light
SKY_TOP = (22, 8, 12)          # smoke-choked crimson-black sky
SKY_BOT = (55, 22, 28)         # blood reflection at horizon
STONE_DK = (30, 26, 30)        # dark mountain stone
STONE_MD = (50, 44, 48)        # midtone stone
STONE_LT = (72, 65, 66)        # light stone
BONE_PALE = (215, 205, 190)    # aged bone
BONE_DIM = (160, 148, 135)     # shadow bone
WITCH_GREEN = (130, 200, 120)  # skull prophecy — the true future
WITCH_GREEN_DIM = (70, 140, 60)
FALSE_GOLD = (210, 170, 80)    # arm bone prophecy — glorious victory
FALSE_GOLD_DIM = (150, 115, 45)
BETRAYAL_CRIMSON = (190, 40, 55)    # leg bone prophecy — betrayal
BETRAYAL_CRIMSON_DIM = (130, 20, 30)
LOST_BLUE = (80, 140, 210)     # rib prophecy — flight/escape
LOST_BLUE_DIM = (45, 90, 150)
FLAME_ORANGE = (220, 120, 40)  # siege fire
IRON_GREY = (60, 55, 58)       # weapons/armour
BLOOD_RED = (160, 25, 30)      # blood pooling
SMOKE = (45, 40, 42)           # smoke haze

rng = random.Random()
rng.seed(1123581321)


def _draw_siege_walls(draw: ImageDraw.ImageDraw) -> None:
    """Draw the mountain fortress walls on the horizon — layered stone with battlements."""
    wall_base_y = 1150
    # Far wall layer (distant, dark)
    for wx in range(0, W, 60):
        bh = rng.randint(180, 300)
        col = STONE_DK if (wx // 60) % 2 == 0 else (STONE_DK[0] - 5, STONE_DK[1] - 4, STONE_DK[2] - 5)
        safe = (max(0, c) for c in col)
        draw.rectangle((wx, wall_base_y - bh, wx + 58, wall_base_y), fill=(*safe, 200))
        # Merlon crenellations
        for m in range(wx, wx + 58, 14):
            mh = bh + rng.randint(18, 30)
            draw.rectangle((m, wall_base_y - mh, min(m + 8, wx + 58), wall_base_y - bh), fill=(col[0], col[1], col[2], 200))

    # Near wall layer (foreground fortress detail)
    near_wall_y = 1280
    draw.rectangle((0, near_wall_y, W, near_wall_y + 600), fill=(*STONE_MD, 230))
    # Stone block lines
    for row in range(20):
        ry = near_wall_y + row * 30
        offset = (row % 2) * 40
        for col in range(-1, W // 80 + 3):
            cx = col * 80 + offset
            draw.rectangle((cx, ry, cx + 76, ry + 28), fill=(*STONE_DK, 100), outline=(*STONE_LT, 30), width=1)

    # Battlements on near wall
    batt_y = near_wall_y
    for mx in range(0, W, 35):
        mh = rng.randint(35, 55)
        draw.rectangle((mx, batt_y - mh, mx + 22, batt_y), fill=(*STONE_MD, 230))


def _draw_siege_engines(draw: ImageDraw.ImageDraw) -> None:
    """Draw crude siege towers and ladders against the far wall."""
    for sx in [200, 500, 900, 1250]:
        sh = rng.randint(280, 380)
        col = (45 + rng.randint(0, 15), 35 + rng.randint(0, 10), 30 + rng.randint(0, 8))
        # Tower body (wooden framework)
        draw.rectangle((sx - 20, 800 - sh, sx + 20, 1000), fill=(*col, 200))
        # Cross braces
        draw.line((sx - 20, 800 - sh, sx + 20, 1000), fill=(*col, 120), width=2)
        draw.line((sx + 20, 800 - sh, sx - 20, 1000), fill=(*col, 120), width=2)
        # Flaming projectile arcs from siege engines
        if rng.random() < 0.7:
            fx, fy = sx, 1000
            for _ in range(rng.randint(1, 3)):
                tx = fx + rng.randint(-500, 500)
                ty = rng.randint(100, 800)
                # Parabolic arc
                pts = []
                for step in range(20):
                    t = step / 20
                    px = fx + (tx - fx) * t
                    py = fy + (ty - fy) * t - 4 * t * (1 - t) * fy * 0.3
                    pts.append((int(px), int(py)))
                draw.line(pts, fill=(*FLAME_ORANGE, rng.randint(30, 70)), width=rng.randint(2, 5))


def _draw_bone_oracle(draw: ImageDraw.ImageDraw) -> list[dict]:
    """Draw the oracle's skeleton laid out on a stone slab. Returns bone positions for prophecy rays."""
    slab_cx, slab_cy = W // 2, 1450
    slab_w, slab_h = 700, 340

    # Stone slab
    draw.rectangle(
        (slab_cx - slab_w // 2, slab_cy - slab_h // 2, slab_cx + slab_w // 2, slab_cy + slab_h // 2),
        fill=(*STONE_LT, 220), outline=(*STONE_DK, 180), width=3,
    )
    draw.rectangle(
        (slab_cx - slab_w // 2 - 8, slab_cy - slab_h // 2 - 8, slab_cx + slab_w // 2 + 8, slab_cy + slab_h // 2 + 8),
        fill=None, outline=(*STONE_DK, 120), width=2,
    )
    # Altar legs
    draw.rectangle((slab_cx - slab_w // 2 + 10, slab_cy + slab_h // 2, slab_cx - slab_w // 2 + 25, slab_cy + slab_h // 2 + 60), fill=(*STONE_DK, 200))
    draw.rectangle((slab_cx + slab_w // 2 - 25, slab_cy + slab_h // 2, slab_cx + slab_w // 2 - 10, slab_cy + slab_h // 2 + 60), fill=(*STONE_DK, 200))

    # Blood pooling on the slab
    draw.ellipse(
        (slab_cx - 200, slab_cy + 50, slab_cx + 50, slab_cy + 140),
        fill=(*BLOOD_RED, 60),
    )
    draw.ellipse(
        (slab_cx - 80, slab_cy + 80, slab_cx + 120, slab_cy + 150),
        fill=(*BLOOD_RED, 40),
    )

    bones = []

    # ── Skull (center-top of slab, projects WITCH_GREEN) ──
    skull_cx, skull_cy = slab_cx, slab_cy - 60
    skull_r = 48
    draw.ellipse(
        (skull_cx - skull_r, skull_cy - skull_r - 12, skull_cx + skull_r, skull_cy + skull_r * 0.6),
        fill=(*BONE_PALE, 230), outline=(*BONE_DIM, 180), width=2,
    )
    # Jaw
    draw.ellipse(
        (skull_cx - skull_r * 0.7, skull_cy + 5, skull_cx + skull_r * 0.7, skull_cy + skull_r * 0.5),
        fill=(*BONE_PALE, 200), outline=(*BONE_DIM, 140), width=1,
    )
    # Eye sockets
    for ex in (-18, 18):
        draw.ellipse(
            (skull_cx + ex - 10, skull_cy - 22, skull_cx + ex + 10, skull_cy - 2),
            fill=(15, 10, 10, 230),
        )
        # Witch-light glowing from eye sockets
        draw.ellipse(
            (skull_cx + ex - 7, skull_cy - 19, skull_cx + ex + 7, skull_cy - 5),
            fill=(*WITCH_GREEN, rng.randint(40, 100)),
        )
    # Nasal cavity
    draw.polygon(
        [(skull_cx, skull_cy - 12), (skull_cx - 6, skull_cy + 2), (skull_cx + 6, skull_cy + 2)],
        fill=(15, 10, 10, 230),
    )
    bones.append({"type": "skull", "cx": skull_cx, "cy": skull_cy, "color": WITCH_GREEN, "dim": WITCH_GREEN_DIM})

    # ── Left arm (FALSE_GOLD) ──
    arm_cx, arm_cy = slab_cx - 230, slab_cy - 20
    # Upper arm
    draw.line((slab_cx - 100, slab_cy - 20, arm_cx, arm_cy), fill=(*BONE_PALE, 220), width=12)
    # Elbow joint
    draw.ellipse((arm_cx - 8, arm_cy - 8, arm_cx + 8, arm_cy + 8), fill=(*BONE_PALE, 230))
    # Forearm + hand
    hand_cx, hand_cy = arm_cx - 100, arm_cy + 60
    draw.line((arm_cx, arm_cy, hand_cx, hand_cy), fill=(*BONE_PALE, 220), width=9)
    # Fingers as short lines
    for fi in range(4):
        fx = hand_cx + (fi - 1.5) * 10
        fy = hand_cy + 8
        draw.line((hand_cx, hand_cy, fx, fy), fill=(*BONE_DIM, 180), width=3)
    bones.append({"type": "arm", "cx": arm_cx, "cy": arm_cy, "color": FALSE_GOLD, "dim": FALSE_GOLD_DIM})

    # ── Right leg (BETRAYAL_CRIMSON) ──
    leg_cx, leg_cy = slab_cx + 160, slab_cy + 40
    draw.line((slab_cx + 70, slab_cy + 20, leg_cx, leg_cy), fill=(*BONE_PALE, 220), width=14)
    # Knee
    draw.ellipse((leg_cx - 9, leg_cy - 9, leg_cx + 9, leg_cy + 9), fill=(*BONE_PALE, 230))
    # Lower leg
    foot_cx, foot_cy = leg_cx + 30, leg_cy + 100
    draw.line((leg_cx, leg_cy, foot_cx, foot_cy), fill=(*BONE_PALE, 220), width=11)
    # Foot
    for fi in range(4):
        draw.line(
            (foot_cx, foot_cy, foot_cx + (fi - 1.5) * 8, foot_cy + 12),
            fill=(*BONE_DIM, 160), width=3,
        )
    bones.append({"type": "leg", "cx": leg_cx, "cy": leg_cy, "color": BETRAYAL_CRIMSON, "dim": BETRAYAL_CRIMSON_DIM})

    # ── Ribcage (LOST_BLUE) ──
    rib_cx, rib_cy = slab_cx + 50, slab_cy - 70
    for ri in range(6):
        ry = rib_cy + ri * 12
        rw = 55 - ri * 5
        draw.arc(
            (rib_cx - rw, ry, rib_cx + rw, ry + 25),
            180, 360, fill=(*BONE_PALE, rng.randint(160, 210)), width=3,
        )
    # Spine
    spine_pts = [(rib_cx, rib_cy - 12)]
    for vi in range(10):
        spine_pts.append((rib_cx + rng.randint(-3, 3), rib_cy - 12 + vi * 9))
    draw.line(spine_pts, fill=(*BONE_DIM, 200), width=4)
    bones.append({"type": "ribs", "cx": rib_cx, "cy": rib_cy, "color": LOST_BLUE, "dim": LOST_BLUE_DIM})

    return bones


def _draw_apprentice_silhouettes(draw: ImageDraw.ImageDraw) -> None:
    """Draw the three apprentice silhouettes gathered around the slab."""
    # Apprentice 1 — Varen Halfbone (left, reaching toward skull)
    _apprentice(draw, 380, 1380, scale=1.0, reach_dir=(1, -1))

    # Apprentice 2 — Morrow Kettle (right, inspecting the leg bone)
    _apprentice(draw, 1220, 1360, scale=1.1, reach_dir=(-1, 0))

    # Apprentice 3 — Aspect (center-right, behind the slab, tall and gaunt)
    _apprentice(draw, 1000, 1240, scale=1.3, reach_dir=(0, -1))


def _apprentice(draw, cx, cy, scale, reach_dir):
    """Draw a single apprentice figure silhouette with outstretched arm."""
    col = (8, 6, 10, 220)
    s = scale

    # Head
    draw.ellipse((cx - 14 * s, cy - 45 * s, cx + 14 * s, cy - 25 * s), fill=col)
    # Body (cloak/tunic)
    draw.polygon(
        [
            (cx - 20 * s, cy - 25 * s),
            (cx + 20 * s, cy - 25 * s),
            (cx + 25 * s, cy + 60 * s),
            (cx - 25 * s, cy + 60 * s),
        ],
        fill=col,
    )
    # Reaching arm
    ax = cx + reach_dir[0] * 40 * s
    ay = cy - 15 * s + reach_dir[1] * 30 * s
    draw.line(
        (cx + reach_dir[0] * 15 * s, cy - 10 * s, ax, ay),
        fill=col, width=int(7 * s),
    )
    # Hand
    draw.ellipse(
        (ax - 5 * s, ay - 5 * s, ax + 5 * s, ay + 5 * s),
        fill=col,
    )


def _draw_prophecy_rays(img: Image.Image, draw: ImageDraw.ImageDraw, bones: list[dict]) -> Image.Image:
    """Draw ghostly prophecy visions rising from each bone — fragments of the different futures."""
    for bone in bones:
        bx, by = bone["cx"], bone["cy"]
        col = bone["color"]
        dim = bone["dim"]

        # Outer glow around the bone
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        for gr in range(4, 0, -1):
            ga = 20 - gr * 4
            if ga < 0:
                continue
            grr = 60 + gr * 30
            gd.ellipse(
                (bx - grr, by - grr, bx + grr, by + grr),
                fill=(*col, ga),
            )
        glow = glow.filter(ImageFilter.GaussianBlur(15))
        img = Image.alpha_composite(img, glow)

    draw = ImageDraw.Draw(img, "RGBA")

    # ── Skull prophecy: ghostly true-future scene (a city falling) ──
    skull = bones[0]
    sx, sy = skull["cx"], skull["cy"]
    # Ghostly towers and battlements floating upward
    for vi in range(6):
        vy = sy - 120 - vi * 35
        for vx in range(sx - 80, sx + 90, 25):
            vh = rng.randint(15, 45)
            va = max(5, 35 - vi * 5)
            draw.rectangle(
                (vx - 6, vy - vh, vx + 6, vy),
                fill=(*WITCH_GREEN, va),
            )
    # Falling ghost towers (vision of collapse)
    for _ in range(5):
        tx = sx + rng.randint(-100, 100)
        ty = sy - rng.randint(80, 250)
        ang = rng.uniform(-0.3, 0.3)
        tw = rng.randint(10, 20)
        draw.rectangle(
            (tx - tw, ty - 40, tx + tw, ty),
            fill=(*WITCH_GREEN_DIM, rng.randint(10, 25)),
        )
    # Prophetic text runes in witch-light
    for ri in range(rng.randint(6, 12)):
        rx = sx + rng.randint(-70, 70)
        ry = sy - rng.randint(80, 200)
        # Rune strokes (abstract symbols)
        for _ in range(3):
            rsx = rx + rng.randint(-8, 8)
            rsy = ry + rng.randint(-8, 8)
            rex = rsx + rng.randint(-10, 10)
            rey = rsy + rng.randint(-5, 5)
            draw.line(
                (rsx, rsy, rex, rey),
                fill=(*WITCH_GREEN, rng.randint(20, 60)),
                width=rng.randint(1, 2),
            )

    # ── Arm prophecy (FALSE_GOLD): vision of glorious victory — crowns, banners ──
    arm = bones[1]
    ax, ay = arm["cx"], arm["cy"]
    # Ghostly crown
    crown_y = ay - 90
    for ci in range(3):
        cy2 = crown_y - 30 - ci * 12
        draw.polygon(
            [
                (ax - 30, cy2 + 15), (ax - 25, cy2),
                (ax - 10, cy2 + 12), (ax, cy2 - 5),
                (ax + 10, cy2 + 12), (ax + 25, cy2),
                (ax + 30, cy2 + 15),
            ],
            fill=None, outline=(*FALSE_GOLD, max(10, 50 - ci * 12)), width=2,
        )
    # Victory banners
    for bi in range(2):
        bx2 = ax + (bi * 2 - 1) * 40
        by2 = crown_y - 10
        draw.line((bx2, by2, bx2, by2 - 60), fill=(*FALSE_GOLD, 40), width=3)
        draw.polygon(
            [(bx2, by2 - 60), (bx2 + 20 * (bi * 2 - 1), by2 - 45), (bx2, by2 - 30)],
            fill=(*FALSE_GOLD, 25),
        )
    # Golden sparks (deceptive allure)
    for _ in range(20):
        gx = ax + rng.randint(-60, 60)
        gy = ay - rng.randint(30, 160)
        gr2 = rng.uniform(1, 4)
        draw.ellipse(
            (gx - gr2, gy - gr2, gx + gr2, gy + gr2),
            fill=(*FALSE_GOLD, rng.randint(15, 60)),
        )

    # ── Leg prophecy (BETRAYAL_CRIMSON): vision of betrayal — a knife in the back ──
    leg = bones[2]
    lx, ly = leg["cx"], leg["cy"]
    # Ghostly dagger blade
    dagger_x, dagger_y = lx - 15, ly - 80
    for di in range(5):
        da = max(10, 50 - di * 10)
        draw.polygon(
            [
                (dagger_x - 4, dagger_y - 40),
                (dagger_x + 4, dagger_y - 40),
                (dagger_x + 8, dagger_y + 10),
                (dagger_x - 8, dagger_y + 10),
            ],
            fill=(*BETRAYAL_CRIMSON, da),
        )
        dagger_y -= 12

    # Blood droplets from the dagger
    for _ in range(10):
        bx3 = dagger_x + rng.randint(-10, 10)
        by3 = dagger_y + rng.randint(20, 80)
        br = rng.uniform(2, 6)
        draw.ellipse(
            (bx3 - br, by3 - br, bx3 + br, by3 + br),
            fill=(*BETRAYAL_CRIMSON, rng.randint(20, 60)),
        )
    # Shattered chains (broken trust)
    for ci in range(3):
        cx2 = lx - 40 + ci * 30
        cy2 = ly - 50 - ci * 15
        draw.line(
            (cx2, cy2, cx2 + 15 + ci * 5, cy2 + 8),
            fill=(*BETRAYAL_CRIMSON_DIM, 40 - ci * 8), width=2,
        )

    # ── Rib prophecy (LOST_BLUE): vision of flight — birds, open sky ──
    rib = bones[3]
    rx, ry = rib["cx"], rib["cy"]
    # Swooping birds
    for bi in range(6):
        bx4 = rx + rng.randint(-80, 80)
        by4 = ry - rng.randint(40, 180)
        wingspan = rng.randint(15, 30)
        draw.arc(
            (bx4 - wingspan, by4 - 8, bx4, by4 + 8),
            180, 360, fill=(*LOST_BLUE, rng.randint(15, 45)), width=2,
        )
        draw.arc(
            (bx4, by4 - 8, bx4 + wingspan, by4 + 8),
            180, 360, fill=(*LOST_BLUE, rng.randint(15, 45)), width=2,
        )
    # Open door archway (the path of escape)
    for ai in range(3):
        aa = max(10, 35 - ai * 10)
        draw.arc(
            (rx - 50 - ai * 8, ry - 90 - ai * 6, rx + 50 + ai * 8, ry - 20 - ai * 6),
            0, 180, fill=(*LOST_BLUE, aa), width=3,
        )

    return img


def _draw_smoke_fire(draw: ImageDraw.ImageDraw) -> None:
    """Draw smoke plumes and fire flickers across the upper portion."""
    # Smoke billows
    for si in range(rng.randint(8, 14)):
        sx = rng.randint(0, W)
        sy = rng.randint(100, 700)
        sr = rng.randint(40, 150)
        sa = rng.randint(20, 50)
        draw.ellipse(
            (sx - sr, sy - sr, sx + sr, sy + sr),
            fill=(*SMOKE, sa),
        )

    # Flames at the wall line
    for fi in range(rng.randint(15, 25)):
        fx = rng.randint(0, W)
        fy = rng.randint(1050, 1200)
        fh = rng.randint(15, 50)
        fcol = rng.choice([
            (180, 60, 20, 120),
            (220, 120, 30, 100),
            (255, 180, 40, 80),
        ])
        draw.polygon(
            [(fx, fy), (fx - 6, fy - fh), (fx, fy - fh - 8), (fx + 6, fy - fh), (fx, fy)],
            fill=fcol,
        )


def _draw_fragmented_scatter(draw: ImageDraw.ImageDraw) -> None:
    """Draw scattered bone fragments and rune-stones around the slab area."""
    for _ in range(rng.randint(15, 30)):
        fx = rng.randint(200, 1400)
        fy = rng.randint(1400, 1800)
        fr = rng.randint(3, 10)
        fcol = (rng.randint(180, 210), rng.randint(160, 195), rng.randint(140, 175))
        # Irregular bone chip
        pts = []
        for pi in range(6):
            pa = pi * math.tau / 6
            pr = fr * (0.7 + rng.random() * 0.3)
            pts.append((int(fx + math.cos(pa) * pr), int(fy + math.sin(pa) * pr)))
        draw.polygon(pts, fill=(*fcol, rng.randint(120, 200)))

    # Rune-inscribed stones
    for _ in range(rng.randint(3, 7)):
        sx = rng.randint(250, 1350)
        sy = rng.randint(1500, 1850)
        sr = rng.randint(8, 15)
        draw.ellipse(
            (sx - sr, sy - sr * 0.7, sx + sr, sy + sr * 0.7),
            fill=(*STONE_MD, 180), outline=(*STONE_DK, 120), width=1,
        )
        # A carved rune on each stone
        for _ in range(3):
            rsx = sx + rng.randint(-6, 6)
            rsy = sy + rng.randint(-5, 5)
            draw.line(
                (rsx, rsy, rsx + rng.randint(-4, 4), rsy + rng.randint(-3, 3)),
                fill=(*STONE_LT, rng.randint(40, 80)), width=1,
            )


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (*SKY_TOP, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Grimdark sky gradient ──────────────────────────────────────────
    for y in range(H):
        t = y / H
        r = int(SKY_TOP[0] + (SKY_BOT[0] - SKY_TOP[0]) * min(t, 1.0))
        g = int(SKY_TOP[1] + (SKY_BOT[1] - SKY_TOP[1]) * min(t, 1.0))
        b = int(SKY_TOP[2] + (SKY_BOT[2] - SKY_TOP[2]) * min(t, 1.0))
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── Background layer: mountain silhouette ───────────────────────────
    mountain = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(mountain)
    mt_pts = [(0, H)]
    for mx2 in range(0, W + 10, 10):
        mt_h = 700 + 150 * math.sin(mx2 * 0.002 + 1.3) + 120 * math.sin(mx2 * 0.005) + rng.randint(-20, 20)
        mt_pts.append((mx2, mt_h))
    mt_pts.append((W, H))
    md.polygon(mt_pts, fill=(15, 10, 14, 200))
    img = Image.alpha_composite(img, mountain)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Siege walls and engines ────────────────────────────────────────
    _draw_siege_walls(draw)
    _draw_siege_engines(draw)

    # ── Smoke and fire ─────────────────────────────────────────────────
    _draw_smoke_fire(draw)

    # ── Bone oracle skeleton on slab ────────────────────────────────────
    bones = _draw_bone_oracle(draw)

    # ── Apprentice silhouettes ──────────────────────────────────────────
    _draw_apprentice_silhouettes(draw)

    # ── Prophecy visions rising from bones ──────────────────────────────
    img = _draw_prophecy_rays(img, draw, bones)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Scattered fragments ─────────────────────────────────────────────
    _draw_fragmented_scatter(draw)

    # ── Ambient motes (bone dust / prophecy sparks) ─────────────────────
    for _ in range(rng.randint(60, 100)):
        px = rng.randint(100, W - 100)
        py = rng.randint(400, 1700)
        pr = rng.uniform(1, 4)
        col = rng.choice([
            (*WITCH_GREEN, rng.randint(10, 40)),
            (*FALSE_GOLD, rng.randint(10, 40)),
            (*BETRAYAL_CRIMSON, rng.randint(10, 40)),
            (*LOST_BLUE, rng.randint(10, 40)),
            (*BONE_PALE, rng.randint(10, 30)),
        ])
        draw.ellipse((px - pr, py - pr, px + pr, py + pr), fill=col)

    # ── Vignette ───────────────────────────────────────────────────────
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(50 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 80))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 80))

    # ── Title panel & save ──────────────────────────────────────────────
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
