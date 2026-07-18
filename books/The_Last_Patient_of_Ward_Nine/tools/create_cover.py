#!/usr/bin/env python3
"""Cover: The Last Patient of Ward Nine — Medical horror: a night-shift nurse at a decommissioned psychiatric hospital discovers Ward Nine's last patient, locked in a padded cell since 1972, is still alive — because something inside feeds on anyone who tries to free him."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    rng = random.Random()
    rng.seed(747138292)

    # ── Perspective corridor parameters ──────────────────────────────────
    VX, VY = W // 2, int(H * 0.38)
    BW = int(W * 0.24)          # back-wall width
    BH = int(H * 0.15)          # back-wall height
    BL = VX - BW // 2            # back-wall left
    BR = VX + BW // 2            # back-wall right
    BT = VY - BH // 2            # back-wall top
    BB = VY + BH // 2            # back-wall bottom

    # ── 1. Base atmospheric gradient ─────────────────────────────────────
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(H):
        t = y / H
        # Deep green-black at top, sickly institutional at bottom
        draw.line(
            (0, y, W, y),
            fill=(
                int(8 + 22 * t),
                int(14 + 40 * t),
                int(10 + 18 * t),
                255,
            ),
        )

    # ── 2. One-point perspective corridor surfaces ───────────────────────
    # Ceiling
    draw.polygon(
        [(0, 0), (W, 0), (BR, BT), (BL, BT)],
        fill=(42, 52, 45, 255),
    )
    # Floor  — dirty institutional linoleum
    draw.polygon(
        [(0, H), (W, H), (BR, BB), (BL, BB)],
        fill=(52, 47, 38, 255),
    )
    # Left wall — faded hospital green
    draw.polygon(
        [(0, 0), (BL, BT), (BL, BB), (0, H)],
        fill=(50, 72, 56, 255),
    )
    # Right wall
    draw.polygon(
        [(W, 0), (BR, BT), (BR, BB), (W, H)],
        fill=(50, 72, 56, 255),
    )
    # Back wall (darker)
    draw.rectangle([(BL, BT), (BR, BB)], fill=(32, 45, 35, 255))

    # ── 3. Baseboards at wall-floor junction ─────────────────────────────
    for i in range(14):
        t = (i + 1) / 14
        y_pos = int(BB + (H - BB) * t)
        frac = (y_pos - BB) / (H - BB) if H > BB else 1
        lx = int(BL - BL * frac)
        rx = int(BR + (W - BR) * frac)
        draw.line((lx, y_pos, rx, y_pos), fill=(38, 48, 40, 160), width=4)

    # ── 4. Floor tile perspective grid ───────────────────────────────────
    # Horizontal lines (closer together at vanishing point = quadratic)
    for i in range(1, 24):
        t = i / 24
        y_pos = int(BB + (H - BB) * (t ** 2))
        frac = (y_pos - BB) / (H - BB) if H > BB else 1
        lx = int(BL - BL * frac)
        rx = int(BR + (W - BR) * frac)
        draw.line((lx, y_pos, rx, y_pos), fill=(62, 55, 48, 90), width=1)

    # Vertical lines radiating from vanishing-point area
    for i in range(-5, 6):
        if i == 0:
            continue
        near_x = VX + i * 120
        if near_x < 0 or near_x >= W:
            continue
        far_x = VX + i * (BW // 14)
        draw.line((near_x, H, far_x, max(BB, 1)), fill=(62, 55, 48, 70), width=1)

    # ── 5. Wall cracks and decay ─────────────────────────────────────────
    decay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(decay)
    for _ in range(10):
        sx = rng.randint(60, W - 60)
        sy = rng.randint(80, int(BB + (H - BB) * 0.5))
        sr = rng.randint(20, 65)
        dv = rng.randint(50, 95)
        dd.ellipse(
            (sx - sr, sy - sr, sx + sr, sy + sr),
            fill=(dv, dv - 20, dv - 30, rng.randint(12, 30)),
        )
    decay = decay.filter(ImageFilter.GaussianBlur(5))
    img = Image.alpha_composite(img, decay)
    draw = ImageDraw.Draw(img, "RGBA")

    # Fine crack lines on walls
    for _ in range(8):
        cx = rng.randint(50, W - 50)
        cy = rng.randint(80, 1300)
        pts = [(cx, cy)]
        segs = rng.randint(3, 7)
        for _ in range(segs):
            cx += rng.randint(-30, 30)
            cy += rng.randint(12, 35)
            pts.append((cx, cy))
        draw.line(
            pts,
            fill=(25, 35, 28, rng.randint(50, 100)),
            width=rng.randint(1, 3),
        )

    # ── 6. The Door to Ward Nine ─────────────────────────────────────────
    door_mx = 18
    door_my = 28
    dl = BL + door_mx
    dr = BR - door_mx
    dt = BT + door_my
    db = BB - door_my

    # Door frame
    draw.rectangle([(dl - 4, dt - 4), (dr + 4, db + 4)], fill=(50, 42, 32, 255))
    # Door surface — worn wood
    draw.rectangle([(dl, dt), (dr, db)], fill=(65, 55, 42, 255))
    # Upper decorative panel
    draw.rectangle(
        [(dl + 10, dt + 45), (dr - 10, dt + 190)],
        fill=None,
        outline=(55, 45, 35, 200),
        width=2,
    )
    # Lower decorative panel
    draw.rectangle(
        [(dl + 10, db - 120), (dr - 10, db - 15)],
        fill=None,
        outline=(55, 45, 35, 200),
        width=2,
    )

    # Door handle
    handle_y = dt + (db - dt) // 2 + 30
    handle_x = dr - 22
    draw.rectangle(
        [(handle_x - 4, handle_y - 8), (handle_x + 4, handle_y + 8)],
        fill=(160, 140, 100, 220),
    )
    draw.ellipse(
        [(handle_x - 6, handle_y - 6), (handle_x + 6, handle_y + 6)],
        fill=(180, 160, 120, 230),
    )

    # Ward Nine plaque (above door)
    plaque_w, plaque_h = 90, 22
    px = VX - plaque_w // 2
    py = BT + 6
    draw.rectangle([(px, py), (px + plaque_w, py + plaque_h)], fill=(55, 48, 38, 230))
    for li in range(3):
        ly = py + 5 + li * 5
        draw.line(
            [(px + 14, ly), (px + plaque_w - 14, ly)],
            fill=(70, 62, 50, 150),
            width=1,
        )

    # ── 7. Barred window in door ─────────────────────────────────────────
    win_w = (dr - dl) // 2 - 2
    win_h = int(win_w * 0.75)
    wx = (dl + dr - win_w) // 2
    wy = dt + 78

    # Window frame
    draw.rectangle(
        [(wx - 5, wy - 5), (wx + win_w + 5, wy + win_h + 5)],
        fill=(50, 42, 32, 255),
    )
    # Interior — absolute black
    draw.rectangle([(wx, wy), (wx + win_w, wy + win_h)], fill=(3, 3, 6, 255))

    # Three vertical bars
    bar_count = 3
    bspace = win_w // (bar_count + 1)
    for i in range(1, bar_count + 1):
        bx = wx + i * bspace
        draw.line(
            [(bx, wy), (bx, wy + win_h)],
            fill=(95, 88, 78, 235),
            width=5,
        )
    # Single horizontal bar through middle
    draw.line(
        [(wx, wy + win_h // 2), (wx + win_w, wy + win_h // 2)],
        fill=(95, 88, 78, 235),
        width=4,
    )

    # ── 8. The Patient's face behind bars ────────────────────────────────
    fc_x = wx + win_w // 2
    fc_y = wy + win_h // 2

    # Face base — gaunt, pallid
    draw.ellipse(
        [(fc_x - 27, fc_y - 30), (fc_x + 27, fc_y + 32)],
        fill=(175, 165, 152, 175),
    )

    # Hollow cheeks
    draw.ellipse(
        [(fc_x - 29, fc_y - 8), (fc_x - 10, fc_y + 14)],
        fill=(130, 120, 110, 85),
    )
    draw.ellipse(
        [(fc_x + 10, fc_y - 8), (fc_x + 29, fc_y + 14)],
        fill=(130, 120, 110, 85),
    )

    # Deep, dark eyes (hollow / soulless)
    draw.ellipse(
        [(fc_x - 17, fc_y - 15), (fc_x - 5, fc_y - 3)],
        fill=(12, 8, 10, 235),
    )
    draw.ellipse(
        [(fc_x + 5, fc_y - 15), (fc_x + 17, fc_y - 3)],
        fill=(12, 8, 10, 235),
    )

    # Dark circles under eyes (chronic sleep deprivation)
    draw.ellipse(
        [(fc_x - 19, fc_y - 8), (fc_x - 3, fc_y + 5)],
        fill=(85, 75, 80, 85),
    )
    draw.ellipse(
        [(fc_x + 3, fc_y - 8), (fc_x + 19, fc_y + 5)],
        fill=(85, 75, 80, 85),
    )

    # Subtle nose bridge
    draw.polygon(
        [
            (fc_x, fc_y - 4),
            (fc_x - 4, fc_y + 6),
            (fc_x + 4, fc_y + 6),
        ],
        fill=(155, 145, 135, 100),
    )

    # Mouth — half-open, unsettling
    draw.arc(
        [(fc_x - 11, fc_y + 8), (fc_x + 11, fc_y + 19)],
        0,
        180,
        fill=(65, 38, 38, 195),
        width=2,
    )

    # ── 9. Entity darkness seeping from under door ───────────────────────
    entity_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ed = ImageDraw.Draw(entity_layer)

    # Black pool spreading from under the door
    ed.ellipse(
        [(dl - 18, db - 2), (dr + 18, db + 60)],
        fill=(10, 3, 7, 220),
    )

    # Shadow tendrils crawling across the floor
    for _ in range(16):
        sx = dl + rng.random() * (dr - dl)
        ex = sx + (rng.random() - 0.5) * 400
        ey = db + 15 + rng.random() * 250
        pts = [(sx, db + 4)]
        cx, cy = sx, db + 4
        for _ in range(5):
            nx = cx + (ex - cx) * 0.30 + (rng.random() - 0.5) * 60
            ny = cy + (ey - cy) * 0.30 + (rng.random() - 0.5) * 20
            pts.append((nx, ny))
            cx, cy = nx, ny
        pts.append((ex, ey))
        if len(pts) >= 2:
            ed.line(
                pts,
                fill=(18, 7, 12, rng.randint(60, 170)),
                width=rng.randint(6, 20),
            )

    entity_layer = entity_layer.filter(ImageFilter.GaussianBlur(6))
    img = Image.alpha_composite(img, entity_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 10. Ceiling fluorescent light ────────────────────────────────────
    light_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(light_layer)

    # Light fixture
    fw = 100
    fx = VX - fw // 2
    ld.rectangle([(fx, 6), (fx + fw, 24)], fill=(200, 225, 195, 230))

    # Light cone (narrow)
    ld.polygon(
        [
            (fx + 10, 24),
            (fx + fw - 10, 24),
            (VX + fw * 3, BB + 250),
            (VX - fw * 3, BB + 250),
        ],
        fill=(190, 220, 190, 20),
    )
    # Light cone (wide, softer)
    ld.polygon(
        [
            (fx, 24),
            (fx + fw, 24),
            (VX + fw * 5, H),
            (VX - fw * 5, H),
        ],
        fill=(180, 210, 180, 8),
    )

    light_layer = light_layer.filter(ImageFilter.GaussianBlur(12))
    img = Image.alpha_composite(img, light_layer)

    # ── 11. Floor reflection of light ────────────────────────────────────
    floor_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fgd = ImageDraw.Draw(floor_glow)
    fgd.ellipse(
        [(VX - 140, BB + 15), (VX + 140, BB + 140)],
        fill=(160, 200, 160, 35),
    )
    floor_glow = floor_glow.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(img, floor_glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 12. Faint emergency red light (off-screen source) ────────────────
    red_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(red_glow)
    rd.ellipse(
        [(W - 80, 80), (W + 120, 500)],
        fill=(160, 20, 15, 14),
    )
    red_glow = red_glow.filter(ImageFilter.GaussianBlur(35))
    img = Image.alpha_composite(img, red_glow)

    # ── 13. Vignette — deep shadow at edges ──────────────────────────────
    vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette)

    # Left edge
    for x in range(130):
        a = int(130 * (1 - x / 130))
        vd.line([(x, 0), (x, H)], fill=(0, 0, 0, a))
    # Right edge
    for x in range(W - 130, W):
        a = int(130 * (1 - (W - 1 - x) / 130))
        vd.line([(x, 0), (x, H)], fill=(0, 0, 0, a))
    # Top edge
    for y in range(90):
        a = int(100 * (1 - y / 90))
        vd.line([(0, y), (W, y)], fill=(0, 0, 0, a))
    # Bottom (lighter — title panel covers this area)
    for y in range(H - 40, H):
        a = int(60 * (1 - (H - 1 - y) / 40))
        vd.line([(0, y), (W, y)], fill=(0, 0, 0, a))

    img = Image.alpha_composite(img, vignette)

    # ── 14. Standard cream title panel + save ───────────────────────────
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
