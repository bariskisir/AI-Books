#!/usr/bin/env python3
"""Cover: These Days Like Glass — Three estranged siblings discover their mother spent forty years building a detailed miniature replica of their childhood home, each room frozen at a different decade, with a hidden figure who does not belong."""
from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# Deep indigo night → warm amber glow from the miniature
CR = (12, 8, 22)     # top: deepest night
CL = (55, 35, 18)     # bottom: warm amber-brown from the house glow

rng = random.Random()
rng.seed(294871563)

# Room color palettes for each decade visible in the miniature cross-section
DECADE_ROOMS = [
    # (label, wall_color, accent1, accent2, light_temp)
    ("1970s",  (180, 120, 60),  (200, 145, 50),  (160, 90, 35),  (255, 210, 120)),  # harvest gold/brown
    ("1980s",  (90, 150, 140),  (200, 80, 120),  (140, 180, 170), (180, 220, 255)),  # teal/magenta
    ("1990s",  (130, 90, 140),  (80, 150, 160),  (170, 120, 160), (200, 180, 255)),  # mauve/teal
    ("2000s",  (60, 100, 130),  (120, 160, 190), (80, 120, 150),  (200, 230, 255)),  # cool blue
]


def draw_room(draw, x, y, w, h, palette_idx, is_attic=False):
    """Draw a room cross-section with decade-specific colors and furnishings."""
    _label, wall_col, accent1, accent2, light_col = DECADE_ROOMS[palette_idx % len(DECADE_ROOMS)]

    # Wall
    draw.rectangle((x, y, x + w, y + h), fill=(*wall_col, 200))
    # Floor
    floor_col = (max(0, wall_col[0] - 30), max(0, wall_col[1] - 30), max(0, wall_col[2] - 30))
    draw.rectangle((x, y + h - 18, x + w, y + h), fill=(*floor_col, 220))

    if is_attic:
        # Triangular roof
        draw.polygon([(x - 30, y), (x + w // 2, y - 40), (x + w + 30, y)],
                     fill=(60, 40, 30, 220))
        draw.polygon([(x, y), (x + w // 2, y - 40), (x + w, y)],
                     fill=(80, 55, 40, 200))
        # Small dormer window
        dw_center = x + w // 2
        draw.rectangle((dw_center - 20, y - 55, dw_center + 20, y - 30), fill=(light_col[0], light_col[1], light_col[2], 60))
        draw.rectangle((dw_center - 20, y - 55, dw_center + 20, y - 30), outline=(accent1[0], accent1[1], accent1[2], 100), width=2)
    else:
        # Window
        win_x = x + w // 4
        win_col = (light_col[0] // 2, light_col[1] // 2, light_col[2] // 2)
        draw.rectangle((win_x, y + 15, win_x + 35, y + 60), fill=(*win_col, 100))
        draw.rectangle((win_x, y + 15, win_x + 35, y + 60), outline=(*accent1, 80), width=1)
        draw.line((win_x + 17, y + 15, win_x + 17, y + 60), fill=(*accent1, 60), width=1)
        draw.line((win_x, y + 37, win_x + 35, y + 37), fill=(*accent1, 60), width=1)

    # Warm light glow from within the room
    glow_rad = w * 0.5
    draw.ellipse((x + w // 2 - glow_rad, y + h // 2 - glow_rad,
                  x + w // 2 + glow_rad, y + h // 2 + glow_rad),
                 fill=(light_col[0], light_col[1], light_col[2], 18))


def draw_furniture(draw, x, y, w, h, palette_idx):
    """Draw era-appropriate miniature furniture silhouettes in a room."""
    _label, wall_col, accent1, accent2, light_col = DECADE_ROOMS[palette_idx % len(DECADE_ROOMS)]
    fcolor = (max(0, wall_col[0] - 20), max(0, wall_col[1] - 20), max(0, wall_col[2] - 20))

    # Bookshelf
    sx = x + 6
    draw.rectangle((sx, y + 22, sx + 14, y + h - 20), fill=(*fcolor, 180))
    for shelf_y in range(y + 28, y + h - 24, 12):
        draw.line((sx, shelf_y, sx + 14, shelf_y), fill=(*accent2, 80), width=1)
        if rng.random() < 0.6:
            bk_col = (rng.randint(80, 200), rng.randint(40, 150), rng.randint(80, 180))
            draw.rectangle((sx + 2, shelf_y + 2, sx + 12, shelf_y + 10), fill=(*bk_col, 160))

    # Small table/desk
    tx = x + w - 28
    draw.rectangle((tx, y + h - 30, tx + 20, y + h - 28), fill=(*fcolor, 180))
    draw.rectangle((tx + 2, y + h - 28, tx + 18, y + h - 18), fill=(*fcolor, 150))

    # Table lamp (tiny glow)
    lx = tx + 10
    draw.ellipse((lx - 2, y + h - 46, lx + 2, y + h - 34), fill=(light_col[0], light_col[1], light_col[2], 120))
    draw.ellipse((lx - 6, y + h - 50, lx + 6, y + h - 38), fill=(light_col[0], light_col[1], light_col[2], 35))


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (12, 8, 22, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Gradient background ──────────────────────────────────────────────
    for y in range(H):
        t = y / H
        r = int(CR[0] + (CL[0] - CR[0]) * t)
        g = int(CR[1] + (CL[1] - CR[1]) * t)
        b = int(CR[2] + (CL[2] - CR[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── Subtle vignette ──────────────────────────────────────────────────
    for vy in range(H):
        vt = 1 - abs(vy - H//2) / (H//2)
        vv = int(45 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 90))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 90))

    # ── Ambient glow behind the miniature house ──────────────────────────
    glow_bg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_bg)
    gd.ellipse((W // 2 - 400, 450, W // 2 + 400, 1400), fill=(180, 130, 60, 30))
    gd.ellipse((W // 2 - 250, 550, W // 2 + 250, 1200), fill=(220, 180, 80, 25))
    glow_bg = glow_bg.filter(ImageFilter.GaussianBlur(45))
    img = Image.alpha_composite(img, glow_bg)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── MINIATURE HOUSE — dollhouse cross-section ───────────────────────
    # The house is a 1.5-story cutaway showing 4 rooms from different decades.
    house_cx = W // 2
    house_top = 480
    room_w = 160
    room_h = 200
    gap = 6

    # Left wing: two rooms stacked (1970s bottom, 1980s top)
    left_x = house_cx - room_w - gap // 2
    draw_room(draw, left_x, house_top, room_w, room_h, 1)       # 1980s (top-left)
    draw_furniture(draw, left_x, house_top, room_w, room_h, 1)
    draw_room(draw, left_x, house_top + room_h + gap, room_w, room_h, 0)  # 1970s (bottom-left)
    draw_furniture(draw, left_x, house_top + room_h + gap, room_w, room_h, 0)

    # Right wing: two rooms stacked (2000s top, 1990s bottom)
    right_x = house_cx + gap // 2
    draw_room(draw, right_x, house_top, room_w, room_h, 3)      # 2000s (top-right)
    draw_furniture(draw, right_x, house_top, room_w, room_h, 3)
    draw_room(draw, right_x, house_top + room_h + gap, room_w, room_h, 2)  # 1990s (bottom-right)
    draw_furniture(draw, right_x, house_top + room_h + gap, room_w, room_h, 2)

    # Center stairwell / hallway connecting
    stair_x = house_cx - 22
    stair_w = 44
    draw.rectangle((stair_x, house_top, stair_x + stair_w, house_top + room_h * 2 + gap),
                   fill=(70, 55, 40, 200))
    # Stair steps
    for step in range(10):
        sy = house_top + room_h + gap + 5 + step * 18
        draw.line((stair_x + 4, sy, stair_x + stair_w - 4, sy), fill=(100, 75, 50, 150), width=2)

    # Attic — hidden figure resides here
    attic_x = house_cx - 40
    attic_w = 80
    attic_h = 100
    draw_room(draw, attic_x, house_top - attic_h, attic_w, attic_h, 2, is_attic=True)

    # ── HIDDEN FIGURE in the attic ──────────────────────────────────────
    # A small humanoid silhouette peering through the dormer
    hf_y = house_top - attic_h + 20
    hf_center = attic_x + attic_w // 2
    # Draw head
    draw.ellipse((hf_center - 7, hf_y + 5, hf_center + 7, hf_y + 20), fill=(20, 15, 25, 220))
    # Draw shoulders/torso
    draw.polygon([(hf_center - 14, hf_y + 22), (hf_center + 14, hf_y + 22),
                  (hf_center + 10, hf_y + 50), (hf_center - 10, hf_y + 50)],
                 fill=(20, 15, 25, 220))
    # Dim glow around the hidden figure — eerie, doesn't belong
    draw.ellipse((hf_center - 25, hf_y - 10, hf_center + 25, hf_y + 60),
                 fill=(180, 220, 255, 20))

    # ── GLASS SHARD FRAGMENTS (shattered time metaphor) ─────────────────
    # Translucent geometric shards around the edges of the house
    for _ in range(22):
        shard_cx = house_cx + rng.randint(-450, 450)
        shard_cy = house_top + rng.randint(-50, int(room_h * 2 + gap + 80))
        shard_sz = rng.randint(15, 55)
        shard_rot = rng.uniform(0, math.tau)
        shard_alpha = rng.randint(15, 50)
        shard_col = (rng.randint(160, 220), rng.randint(180, 230), rng.randint(200, 255))

        pts = []
        for side in range(3):
            angle = shard_rot + side * math.tau / 3 + rng.uniform(-0.15, 0.15)
            rad = shard_sz * (0.7 + rng.random() * 0.3)
            px = shard_cx + math.cos(angle) * rad
            py = shard_cy + math.sin(angle) * rad * 0.6
            pts.append((px, py))
        draw.polygon(pts, fill=(*shard_col, shard_alpha))

    # ── GLASS REFLECTION STREAKS ────────────────────────────────────────
    for _ in range(12):
        streak_x = rng.randint(50, W - 50)
        streak_y = rng.randint(300, 1600)
        streak_len = rng.randint(60, 200)
        streak_angle = rng.uniform(-0.3, 0.3)
        streak_col = (rng.randint(180, 230), rng.randint(190, 240), rng.randint(200, 255))
        draw.line((streak_x, streak_y,
                   streak_x + math.sin(streak_angle) * streak_len,
                   streak_y + math.cos(streak_angle) * streak_len * 0.3),
                  fill=(*streak_col, rng.randint(6, 20)), width=rng.randint(1, 3))

    # ── THREE SIBLING SILHOUETTES ───────────────────────────────────────
    # Miriam (left), Leo (center), Nora (right) — different heights/postures
    siblings = [
        # (cx_offset, height, body_width, opacity)
        (-240, 380, 90,  210),   # Miriam — tallest, straight posture
        (0,     320, 100, 200),   # Leo — mid, slightly broader
        (220,   340, 80,  210),   # Nora — mid, narrower
    ]
    base_y = 1680

    for idx, (sx_off, s_h, s_w, s_op) in enumerate(siblings):
        sx = house_cx + sx_off
        head_r = int(s_w * 0.20)
        head_y = base_y - s_h
        neck_len = int(s_w * 0.2)

        # Head
        draw.ellipse((sx - head_r, head_y, sx + head_r, head_y + head_r * 2),
                     fill=(8, 6, 14, s_op))
        if idx == 0:  # Miriam — facing forward, small bun
            draw.ellipse((sx - 6, head_y - 6, sx + 6, head_y + 2), fill=(6, 4, 10, s_op))
        elif idx == 2:  # Nora — head tilted slightly
            draw.ellipse((sx - 5, head_y + 2, sx + 7, head_y + head_r + 4),
                         fill=(8, 6, 14, s_op))

        # Shoulders + torso
        neck_top = head_y + head_r * 2
        draw.rectangle((sx - s_w // 4, neck_top, sx + s_w // 4, neck_top + neck_len),
                       fill=(6, 4, 12, s_op))

        shoulder_top = neck_top + neck_len
        # Body (coat/jacket shape)
        draw.polygon([
            (sx - s_w, shoulder_top + s_w // 3),
            (sx - s_w // 3, shoulder_top),
            (sx + s_w // 3, shoulder_top),
            (sx + s_w, shoulder_top + s_w // 3),
            (sx + s_w - s_w // 4, base_y - 15),
            (sx + s_w // 4, base_y),
            (sx - s_w // 4, base_y),
            (sx - s_w + s_w // 4, base_y - 15),
        ], fill=(6, 4, 12, s_op))

        # Edge light (warm amber glow from the miniature on their backs)
        edge_col = (200, 150, 80, 30)
        draw.line((sx - s_w, shoulder_top + s_w // 3, sx - s_w // 3, shoulder_top),
                  fill=edge_col, width=2)
        if idx == 1:  # Leo — subtle arm reaching forward
            draw.line((sx + s_w // 3, shoulder_top + 30, sx + s_w // 2 + 20, shoulder_top + 80),
                      fill=(6, 4, 12, s_op), width=6)

    # ── WARM LIGHT PARTICLES (memories floating upward from the house) ──
    for _ in range(rng.randint(40, 70)):
        px = rng.randint(house_cx - 350, house_cx + 350)
        py = rng.randint(300, house_top + room_h * 2 + gap)
        pr = rng.randint(2, 6)
        pa = rng.randint(25, 100)
        draw.ellipse((px - pr, py - pr, px + pr, py + pr),
                     fill=(255, 210, 130, pa))
        if rng.random() < 0.25:
            draw.ellipse((px - pr * 3, py - pr * 3, px + pr * 3, py + pr * 3),
                         fill=(255, 210, 130, pa // 4))

    # ── FRAGILE CRACK LINES (like cracked glass across the composition) ─
    for _ in range(8):
        start_x = rng.randint(50, W - 50)
        start_y = rng.randint(200, 1600)
        crack_pts = [(start_x, start_y)]
        cx, cy = start_x, start_y
        for seg in range(rng.randint(4, 10)):
            cx += rng.randint(-30, 30)
            cy += rng.randint(10, 50)
            crack_pts.append((cx, cy))
        draw.line(crack_pts, fill=(180, 190, 200, rng.randint(8, 25)), width=1)

    # ── Title panel ──────────────────────────────────────────────────────
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
