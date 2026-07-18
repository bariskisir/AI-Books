#!/usr/bin/env python3
"""Cover: The Pollination — Dystopian emotional harvest: a funeral home worker smuggles contraband feelings from the dying past a grief cartel."""

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
rng.seed(1978365902)

# Unique palette: cold industrial steel + toxic amber emotional essence
COLD_TOP = (8, 6, 14)
WARM_BOT = (38, 22, 10)
STEEL = (42, 46, 56)
PIPE = (26, 28, 35)
VIAL_AMBER = (255, 195, 40)
VIAL_GOLD = (220, 140, 30)
VIAL_BLUE = (130, 185, 255)
VIAL_RED = (225, 75, 55)
GLOW = (255, 190, 60)
DARK = (8, 6, 12)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (*COLD_TOP, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 1. Gradient: cold charcoal top -> toxic amber bottom ──
    for y in range(H):
        t = y / H
        r = int(COLD_TOP[0] + (WARM_BOT[0] - COLD_TOP[0]) * t)
        g = int(COLD_TOP[1] + (WARM_BOT[1] - COLD_TOP[1]) * t)
        b = int(COLD_TOP[2] + (WARM_BOT[2] - COLD_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── 2. Industrial architecture: massive steel columns framing the scene ──
    # Left column cluster
    for ox in range(0, 200, 8):
        taper = 1.0 - (ox / 200) ** 0.6
        col_s = int(STEEL[0] * taper), int(STEEL[1] * taper), int(STEEL[2] * taper)
        draw.rectangle((ox, 0, ox + 8, H), fill=(*col_s, 180 + int(60 * taper)))
    # Left girder rivets
    for y in range(0, H, 40):
        draw.ellipse((170, y - 4, 182, y + 4), fill=(*STEEL, 150))

    # Right column cluster
    for ox in range(W - 200, W, 8):
        taper = 1.0 - ((W - ox) / 200) ** 0.6
        col_s = int(STEEL[0] * taper), int(STEEL[1] * taper), int(STEEL[2] * taper)
        draw.rectangle((ox, 0, ox + 8, H), fill=(*col_s, 180 + int(60 * taper)))
    for y in range(0, H, 40):
        draw.ellipse((W - 182, y - 4, W - 170, y + 4), fill=(*STEEL, 150))

    # Horizontal steel beams crossing the top
    for by in (60, 130, 210, 310):
        beam_h = rng.randint(8, 14)
        draw.rectangle((200, by, W - 200, by + beam_h), fill=(*STEEL, 200))
        draw.rectangle((200, by + beam_h, W - 200, by + beam_h + 2), fill=(*STEEL, 120))

    # Angled pipe ducts in the upper-left and upper-right
    for side in (-1, 1):
        cx, cy = W // 2 + side * 300, rng.randint(350, 500)
        pts = [(cx, cy)]
        for _ in range(rng.randint(4, 7)):
            cx += side * rng.randint(30, 80)
            cy += rng.randint(20, 70)
            pts.append((cx, cy))
        draw.line(pts, fill=(*PIPE, rng.randint(150, 210)), width=rng.randint(5, 9))
        # Pipe joints
        for jx, jy in pts[1:-1]:
            draw.ellipse((jx - 8, jy - 8, jx + 8, jy + 8), fill=(*PIPE, 200))

    # ── 3. The HARVESTING TREE: a metal structure holding emotion vials ──
    tree_cx = W // 2

    # Back-glow dome behind the tree
    glow_bg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_bg)
    gd.ellipse((tree_cx - 400, 380, tree_cx + 400, 1500), fill=(*GLOW, 22))
    gd.ellipse((tree_cx - 250, 500, tree_cx + 250, 1350), fill=(*GLOW, 14))
    glow_bg = glow_bg.filter(ImageFilter.GaussianBlur(70))
    img = Image.alpha_composite(img, glow_bg)
    draw = ImageDraw.Draw(img, "RGBA")

    # Main trunk (pulsing metallic column)
    trunk_left = tree_cx - 18
    trunk_right = tree_cx + 18
    trunk_top = 400
    trunk_bot = 1150
    for x in range(trunk_left, trunk_right + 1):
        fade = 1.0 - abs(x - tree_cx) / 18
        alpha = int(180 + 60 * fade)
        draw.line((x, trunk_top, x, trunk_bot), fill=(32, 35, 44, alpha))

    # Horizontal bands wrapping the trunk
    for by in range(trunk_top + 40, trunk_bot, 60):
        band_w = 4 + rng.randint(0, 4)
        draw.rectangle((trunk_left - 4, by, trunk_right + 4, by + band_w), fill=(*STEEL, 180))

    # Metal branches (angular, mechanical)
    branches = []
    for _ in range(16):
        by = rng.randint(trunk_top + 60, trunk_bot - 60)
        bdir = 1 if rng.random() < 0.5 else -1
        pts = [(tree_cx, by)]
        segs = rng.randint(3, 6)
        for _ in range(segs):
            px, py = pts[-1]
            nx = px + bdir * rng.randint(20, 55)
            ny = py + rng.randint(-35, 35)
            pts.append((nx, ny))
        branches.append(pts)
        draw.line(pts, fill=(*STEEL, 170), width=rng.randint(3, 6))
        # Subtle highlight on branch top edge
        for i in range(len(pts) - 1):
            x1, y1 = pts[i]
            x2, y2 = pts[i + 1]
            draw.line((x1, y1 - 1, x2, y2 - 1), fill=(*STEEL, 70), width=1)
        # Nub at tip
        tx, ty = pts[-1]
        draw.ellipse((tx - 4, ty - 4, tx + 4, ty + 4), fill=(*STEEL, 190))

    # ── 4. EMOTION VIALS: glowing contraband hanging from branches ──
    for pts in branches:
        bx, by = pts[0]
        num_vials = rng.randint(2, 5)
        for _ in range(num_vials):
            vx = bx + rng.randint(-30, 30)
            vy = by + rng.randint(10, 50)
            vial_c = rng.choice([
                VIAL_AMBER, VIAL_GOLD, VIAL_BLUE, VIAL_RED,
                (VIAL_AMBER[0] - 30, VIAL_AMBER[1] + 20, VIAL_AMBER[2] + 40),
            ])
            vial_a = rng.randint(50, 120)
            vr = rng.randint(7, 16)
            # Thin connector line
            draw.line((bx, by, vx, vy), fill=(*STEEL, 80), width=1)
            # Radiant glow around vial
            draw.ellipse((vx - vr * 4, vy - vr * 4, vx + vr * 4, vy + vr * 4),
                        fill=(*vial_c, vial_a // 3))
            draw.ellipse((vx - vr * 2, vy - vr * 2, vx + vr * 2, vy + vr * 2),
                        fill=(*vial_c, vial_a // 2))
            # Vial shape
            vw, vh = vr, vr * 2 + 2
            draw.rectangle((vx - vw // 2, vy - vh // 2, vx + vw // 2, vy + vh // 2),
                          fill=(*vial_c, 180))
            draw.ellipse((vx - vw // 2, vy - vh // 2 - vw // 3,
                          vx + vw // 2, vy - vh // 2 + vw // 3),
                         fill=(*vial_c, 200))
            draw.ellipse((vx - vw // 2, vy + vh // 2 - vw // 3,
                          vx + vw // 2, vy + vh // 2 + vw // 3),
                         fill=(*vial_c, 140))
            # Core highlight
            draw.ellipse((vx - vr // 3, vy - vr // 3, vx + vr // 3, vy + vr // 3),
                        fill=(255, 250, 230, 120))

    # Extra stray vials floating disconnected (loose contraband)
    for _ in range(12):
        vx = tree_cx + rng.randint(-280, 280)
        vy = rng.randint(550, 1200)
        vial_c = rng.choice([VIAL_AMBER, VIAL_GOLD, VIAL_BLUE])
        vr = rng.randint(5, 10)
        draw.ellipse((vx - vr * 3, vy - vr * 3, vx + vr * 3, vy + vr * 3),
                    fill=(*vial_c, 20))
        draw.ellipse((vx - vr, vy - vr, vx + vr, vy + vr),
                    fill=(*vial_c, 150))

    # ── 5. ELARA TRENCH silhouette reaching for a contraband vial ──
    fig_x = tree_cx + 140
    fig_y = 1620
    # Body
    body = [
        (fig_x - 30, fig_y),
        (fig_x - 24, fig_y - 130),
        (fig_x - 20, fig_y - 210),
        (fig_x - 10, fig_y - 260),
        (fig_x - 8, fig_y - 300),
        (fig_x + 8, fig_y - 300),
        (fig_x + 10, fig_y - 260),
        (fig_x + 20, fig_y - 210),
        (fig_x + 24, fig_y - 130),
        (fig_x + 30, fig_y),
    ]
    draw.polygon(body, fill=(*DARK, 235))
    # Arm reaching upward and right toward a vial
    arm = [
        (fig_x + 20, fig_y - 200),
        (fig_x + 90, fig_y - 250),
        (fig_x + 150, fig_y - 280),
    ]
    draw.line(arm, fill=(*DARK, 235), width=10)
    # Hand
    draw.ellipse((fig_x + 145, fig_y - 290, fig_x + 160, fig_y - 275),
                fill=(*DARK, 235))
    # Coat tail
    draw.polygon([
        (fig_x - 24, fig_y - 100),
        (fig_x - 40, fig_y - 20),
        (fig_x - 35, fig_y),
        (fig_x - 20, fig_y - 10),
    ], fill=(*DARK, 210))

    # The contraband vial she reaches for (prominent glow)
    cb_x = fig_x + 175
    cb_y = fig_y - 280
    for gr in (40, 28, 18, 10):
        ga = 25 - gr // 2
        draw.ellipse((cb_x - gr, cb_y - gr, cb_x + gr, cb_y + gr),
                    fill=(*VIAL_AMBER, max(0, ga)))
    draw.ellipse((cb_x - 10, cb_y - 10, cb_x + 10, cb_y + 10),
                fill=(*VIAL_AMBER, 220))
    draw.ellipse((cb_x - 4, cb_y - 4, cb_x + 4, cb_y + 4),
                fill=(255, 245, 210, 240))

    # ── 6. EMMETT (the feeless boy) — smaller, separate silhouette ──
    boy_x = tree_cx - 200
    boy_y = fig_y + 10
    boy = [
        (boy_x - 12, boy_y),
        (boy_x - 10, boy_y - 110),
        (boy_x - 6, boy_y - 150),
        (boy_x, boy_y - 170),
        (boy_x + 6, boy_y - 150),
        (boy_x + 10, boy_y - 110),
        (boy_x + 12, boy_y),
    ]
    draw.polygon(boy, fill=(6, 4, 10, 210))
    # He stands apart, hands at sides — no reaching

    # ── 7. Conveyor belt / refinery mechanism below ──
    belt_y = fig_y + 35
    # Belt line
    draw.rectangle((0, belt_y, W, belt_y + 4), fill=(18, 16, 20, 200))
    draw.rectangle((0, belt_y + 12, W, belt_y + 16), fill=(18, 16, 20, 200))
    # Rollers
    for rx in range(0, W, 40):
        draw.ellipse((rx - 4, belt_y, rx + 4, belt_y + 16), fill=(*STEEL, 160))
    # Small dark forms on belt (harvested remains)
    for _ in range(30):
        bx = rng.randint(0, W)
        draw.ellipse((bx - 8, belt_y - 3, bx + 8, belt_y + 19),
                    fill=(10, 8, 12, rng.randint(160, 220)))
    # Lower industrial structure below belt
    draw.rectangle((0, belt_y + 20, W, H), fill=(6, 4, 8, 230))
    for lx in range(0, W, 100):
        draw.line((lx, belt_y + 20, lx + 50, H),
                 fill=(12, 10, 14, 80), width=2)

    # ── 8. WARDEN PAXTON's watchtower silhouette (distant background) ──
    tw_x = W - 280
    tw_y = 1250
    draw.rectangle((tw_x - 6, tw_y, tw_x + 6, tw_y + 280), fill=(12, 10, 14, 200))
    draw.rectangle((tw_x - 16, tw_y - 6, tw_x + 16, tw_y + 8), fill=(12, 10, 14, 200))
    draw.polygon([(tw_x - 24, tw_y - 6), (tw_x + 24, tw_y - 6), (tw_x, tw_y - 50)],
                fill=(12, 10, 14, 200))
    # Searchlight beam
    beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam)
    beam_angle = math.radians(15 + 10 * math.sin(1.7))
    beam_len = 900
    bd.polygon([
        (tw_x, tw_y),
        (tw_x - beam_len, tw_y + beam_len * 0.4),
        (tw_x + beam_len, tw_y + beam_len * 0.3),
    ], fill=(*VIAL_AMBER, 5))
    beam = beam.filter(ImageFilter.GaussianBlur(35))
    img = Image.alpha_composite(img, beam)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 9. Light rays emanating from the Harvesting Tree ──
    rays = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rays)
    for i in range(14):
        spread = math.radians(rng.uniform(-55, 55))
        rlen = rng.randint(500, 1000)
        ra = rng.randint(2, 7)
        lx = tree_cx + rng.randint(-60, 60)
        ly = 500 + rng.randint(-100, 200)
        rd.polygon([
            (lx, ly),
            (lx + rlen * math.sin(spread) - 15, ly + rlen * math.cos(spread)),
            (lx + rlen * math.sin(spread) + 15, ly + rlen * math.cos(spread)),
        ], fill=(*VIAL_AMBER, ra))
    rays = rays.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img, rays)

    # ── 10. Emotional motes / particles floating in the air ──
    for _ in range(200):
        px = rng.randint(80, W - 80)
        py = rng.randint(150, 1800)
        pr = rng.uniform(0.8, 3.5)
        pcol = rng.choice([
            (*VIAL_AMBER, rng.randint(30, 110)),
            (*VIAL_GOLD, rng.randint(25, 80)),
            (*VIAL_BLUE, rng.randint(15, 60)),
            (*VIAL_RED, rng.randint(15, 50)),
            (255, 255, 240, rng.randint(10, 40)),
        ])
        draw.ellipse((px - pr, py - pr, px + pr, py + pr), fill=pcol)

    # ── 11. Ash / particulate streaks ──
    for _ in range(40):
        ax = rng.randint(0, W)
        ay = rng.randint(100, 1800)
        alen = rng.randint(10, 60)
        aa = rng.randint(8, 30)
        draw.line((ax, ay, ax + alen, ay + 3), fill=(60, 55, 50, aa), width=1)

    # ── 12. Vignette ──
    for vy in range(H):
        vt = 1.0 - abs(vy - H // 2) / (H // 2)
        vw = int(50 * max(0.0, 1.0 - vt))
        if vw > 0:
            draw.line((0, vy, vw, vy), fill=(0, 0, 0, 120))
            draw.line((W - vw, vy, W, vy), fill=(0, 0, 0, 120))

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
