#!/usr/bin/env python3
"""Cover: The Root Beneath the Porch — Botanical body horror: cross-section of a farmhouse built on a living root system that consumes whatever it's fed."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# ── Horizon: above is moonlit farmhouse, below is cross-section earth ──
HORIZON = 880

# Seeded for reproducibility
rng = random.Random()
rng.seed(918273645)

# ── Unique palette: midnight horror + cross-section earth ─────────────
# Night sky
NIGHT_TOP = (8, 4, 22)
NIGHT_BOT = (22, 14, 38)
MOON_COLOR = (235, 228, 212)
MOON_HALO  = (210, 205, 195)

# Soil layers (from topsoil down to deep earth)
SOIL_TOP  = (52, 34, 20)
SOIL_MID  = (36, 20, 12)
SOIL_DEEP = (18, 10, 6)

# The Root — sickly greens and bone pale
ROOT_DARK   = (40, 60, 22)
ROOT_MID    = (72, 100, 38)
ROOT_LIGHT  = (115, 150, 60)
ROOT_GLOW_GREEN = (130, 195, 65)
ROOT_GLOW_AMBER = (205, 185, 45)

ROOT_PALE = (155, 195, 120)

# Consumed matter
BLOOD  = (145, 22, 18)
BONE   = (200, 190, 170)

# House / warm elements
WINDOW_WARM  = (235, 205, 135)
HOUSE_DARK   = (5, 3, 7)


def _clamp(v: int) -> int:
    return max(0, min(255, v))


def _draw_soil_gradient(draw: ImageDraw.ImageDraw) -> None:
    """Topsoil → subsoil → deep earth gradient with grain texture."""
    for y in range(HORIZON, H):
        t = (y - HORIZON) / (H - HORIZON)
        if t < 0.4:
            frac = t / 0.4
            r = int(SOIL_TOP[0] + (SOIL_MID[0] - SOIL_TOP[0]) * frac)
            g = int(SOIL_TOP[1] + (SOIL_MID[1] - SOIL_TOP[1]) * frac)
            b = int(SOIL_TOP[2] + (SOIL_MID[2] - SOIL_TOP[2]) * frac)
        else:
            frac = (t - 0.4) / 0.6
            r = int(SOIL_MID[0] + (SOIL_DEEP[0] - SOIL_MID[0]) * frac)
            g = int(SOIL_MID[1] + (SOIL_DEEP[1] - SOIL_MID[1]) * frac)
            b = int(SOIL_MID[2] + (SOIL_DEEP[2] - SOIL_MID[2]) * frac)
        # Grain: small horizontal segments with noise
        for x in range(0, W, 6):
            vr = rng.randint(-6, 6)
            vg = rng.randint(-4, 4)
            vb = rng.randint(-3, 3)
            draw.line((x, y, x + 6, y),
                      fill=(_clamp(r + vr), _clamp(g + vg), _clamp(b + vb), 255))


def _draw_soil_pebbles(draw: ImageDraw.ImageDraw) -> None:
    """Small rocks embedded in the soil."""
    for _ in range(40):
        rx = rng.randint(20, W - 20)
        ry = rng.randint(HORIZON + 30, H - 60)
        rr = rng.randint(2, 7)
        rc = (rng.randint(55, 85), rng.randint(50, 75), rng.randint(40, 60))
        draw.ellipse((rx - rr, ry - rr, rx + rr, ry + rr), fill=(*rc, 200))


def _draw_burrows(draw: ImageDraw.ImageDraw) -> None:
    """Small worm tunnels / air pockets in the soil."""
    for _ in range(18):
        bx = rng.randint(20, W - 20)
        by = rng.randint(HORIZON + 40, H - 40)
        bl = rng.randint(8, 22)
        draw.ellipse((bx, by, bx + bl, by + rng.randint(1, 2)),
                     fill=(15, 10, 5, rng.randint(50, 100)))


def _draw_sky_gradient(draw: ImageDraw.ImageDraw) -> None:
    """Deep purple-black sky growing slightly lighter toward the horizon."""
    for y in range(HORIZON):
        t = y / HORIZON
        r = int(NIGHT_TOP[0] + (NIGHT_BOT[0] - NIGHT_TOP[0]) * t)
        g = int(NIGHT_TOP[1] + (NIGHT_BOT[1] - NIGHT_TOP[1]) * t)
        b = int(NIGHT_TOP[2] + (NIGHT_BOT[2] - NIGHT_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))


def _draw_stars(draw: ImageDraw.ImageDraw) -> None:
    """Tiny scattered stars in the night sky."""
    for _ in range(80):
        sx = rng.randint(0, W)
        sy = rng.randint(10, HORIZON - 30)
        sr = rng.uniform(0.5, 2.0)
        sa = rng.randint(80, 200)
        draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr),
                     fill=(220, 220, 235, sa))


def _draw_moon(img: Image.Image) -> Image.Image:
    """Large pale moon behind the farmhouse, with a soft halo."""
    cx, cy = W // 2 + 200, 320
    r = 155

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for mult, alpha in [(3.5, 12), (2.2, 25), (1.4, 45)]:
        gd.ellipse((cx - r * mult, cy - r * mult,
                    cx + r * mult, cy + r * mult),
                   fill=(*MOON_HALO, alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(35))
    img = Image.alpha_composite(img, glow)

    body = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(body)
    bd.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(*MOON_COLOR, 200))
    body = body.filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(img, body)
    return img


def _draw_farmhouse(draw: ImageDraw.ImageDraw) -> dict:
    """Draw the farmhouse silhouette and return anchor info for roots.

    Returns a dict with 'porch_x', 'porch_w', 'base_y' so the root
    system knows where to originate.
    """
    house_cx = W // 2 - 20
    base_y = HORIZON
    hw, hh = 340, 380
    hl = house_cx - hw // 2
    ht = base_y - hh

    # Main body
    draw.rectangle((hl, ht, hl + hw, base_y), fill=(*HOUSE_DARK, 240))

    # Gabled roof
    roof_peak = ht - 80
    draw.polygon([
        (hl - 20, ht),
        (hl + hw // 2, roof_peak),
        (hl + hw + 20, ht),
    ], fill=(*HOUSE_DARK, 240))

    # Chimney
    chim_x = hl + hw - 60
    chim_w, chim_h = 30, 90
    draw.rectangle((chim_x, roof_peak - chim_h, chim_x + chim_w, roof_peak),
                   fill=(*HOUSE_DARK, 240))

    # ── Porch (extending right) ──
    pw, ph = 200, 60
    px = hl + hw
    py = base_y - ph
    draw.rectangle((px, py, px + pw, base_y), fill=(*HOUSE_DARK, 240))

    # Slanted porch roof
    draw.polygon([
        (px - 10, py - 30),
        (px + pw + 20, py - 30),
        (px + pw, py),
        (px, py),
    ], fill=(*HOUSE_DARK, 240))

    # Porch pillars
    for pcol_x in (px + 20, px + pw - 20):
        draw.rectangle((pcol_x - 4, py, pcol_x + 4, base_y),
                       fill=(*HOUSE_DARK, 220))

    # Porch floorboards
    for fy in range(py + 8, base_y, 12):
        draw.line((px + 5, fy, px + pw - 5, fy),
                  fill=(15, 10, 18, 90), width=1)

    # ── The Root breaking through the porch floor ──
    root_x = px + pw // 2 + 15
    # Thick root erupting through floorboards
    for t in range(14, 8, -2):
        draw.line((root_x, base_y + 20, root_x + rng.randint(-3, 3), py - 10),
                  fill=(*ROOT_MID, 180 + t * 4), width=t)
    # Tendrils spreading across the porch
    for _ in range(6):
        tx = root_x + rng.randint(-15, 15)
        ty = py + rng.randint(10, 45)
        ex = tx + rng.randint(-35, 35)
        ey = ty + rng.randint(-12, 12)
        draw.line((root_x, ty, ex, ey),
                  fill=(*ROOT_LIGHT, rng.randint(130, 190)),
                  width=rng.randint(2, 4))

    # ── Lit window (Maya's room — warm glow) ──
    win_l = hl + 60
    win_t = ht + 140
    win_w, win_h = 65, 85
    draw.rectangle((win_l, win_t, win_l + win_w, win_t + win_h),
                   fill=(*WINDOW_WARM, 200))
    # Window cross bars
    draw.line((win_l + win_w // 2, win_t, win_l + win_w // 2, win_t + win_h),
              fill=(*HOUSE_DARK, 180), width=4)
    draw.line((win_l, win_t + win_h // 2, win_l + win_w, win_t + win_h // 2),
              fill=(*HOUSE_DARK, 180), width=4)
    # Window glow is handled at the scene level; skip here since
    # this function draws onto an existing draw context, not a layer.

    return {"porch_x": px, "porch_w": pw, "base_y": base_y, "house_cx": house_cx}


def _draw_dead_trees(draw: ImageDraw.ImageDraw, house_cx: int) -> None:
    """Bare skeletal trees on each side of the farmhouse."""
    hw = 340
    for side in (-1, 1):
        tx = house_cx + side * (hw // 2 + 80 + rng.randint(0, 80))
        ty = HORIZON
        th = rng.randint(200, 300)
        tw = rng.randint(4, 7)
        # Trunk
        draw.line((tx, ty, tx, ty - th), fill=(*HOUSE_DARK, 200), width=tw)
        # Branches
        for _ in range(rng.randint(5, 9)):
            by = ty - rng.randint(th // 3, th - 20)
            blen = rng.randint(40, 130)
            bdir = side * (1 if rng.random() < 0.7 else -1)
            draw.line((tx, by, tx + bdir * rng.randint(20, 50), by - blen),
                      fill=(*HOUSE_DARK, 180), width=rng.randint(1, 3))


def _draw_root_glow(img: Image.Image) -> Image.Image:
    """Bioluminescent pool of green/amber light deep under the porch."""
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    cx = W // 2 + 150  # under the porch
    cy = HORIZON + 80

    gd.ellipse((cx - 280, cy - 80, cx + 280, cy + 520),
               fill=(*ROOT_GLOW_GREEN, 22))
    gd.ellipse((cx - 160, cy, cx + 160, cy + 420),
               fill=(*ROOT_GLOW_GREEN, 14))
    for _ in range(6):
        px = cx + rng.randint(-120, 120)
        py = cy + rng.randint(30, 360)
        pr = rng.randint(50, 100)
        gd.ellipse((px - pr, py - pr, px + pr, py + pr),
                   fill=(*ROOT_GLOW_AMBER, 7))
    glow = glow.filter(ImageFilter.GaussianBlur(40))
    return Image.alpha_composite(img, glow)


def _draw_taproots(draw: ImageDraw.ImageDraw, cx: int, cy: int) -> list:
    """Draw main taproots descending from under the porch.

    Returns a list of point-tuples for each root (for secondary branching).
    """
    taproots = []
    for _ in range(5):
        tx = cx + rng.randint(-45, 45)
        ty = cy
        pts = [(tx, ty)]
        depth = rng.randint(7, 13)
        for d in range(depth):
            tx += rng.randint(-20, 20)
            ty += rng.randint(30, 55)
            tx = max(60, min(W - 60, tx))
            if ty > H - 150:
                break
            pts.append((int(tx), int(ty)))

        taproots.append(pts)

        # Draw with highlight edge for depth
        for i in range(len(pts) - 1):
            t = i / len(pts)
            thick = max(3, int(16 - i * 1.1))
            r = int(ROOT_MID[0] + (ROOT_DARK[0] - ROOT_MID[0]) * t)
            g = int(ROOT_MID[1] + (ROOT_DARK[1] - ROOT_MID[1]) * t)
            b = int(ROOT_MID[2] + (ROOT_DARK[2] - ROOT_MID[2]) * t)
            draw.line((pts[i], pts[i + 1]), fill=(r, g, b, 220), width=thick)

            # Edge highlight (light from the bioluminescence)
            x1, y1 = pts[i]
            x2, y2 = pts[i + 1]
            dx = x2 - x1
            dy = y2 - y1
            length = math.hypot(dx, dy)
            if length > 4:
                nx = -dy / length * 1.5
                ny = dx / length * 1.5
                draw.line((x1 + nx, y1 + ny, x2 + nx, y2 + ny),
                          fill=(*ROOT_LIGHT, 55), width=max(1, thick // 3))

    return taproots


def _draw_secondary_roots(draw: ImageDraw.ImageDraw, taproots: list) -> None:
    """Fine secondary roots branching off the main taproots."""
    for _ in range(30):
        if not taproots:
            break
        parent = rng.choice(taproots)
        idx = rng.randint(1, min(len(parent) - 1, 5))
        bx, by = parent[idx]
        direction = 1 if rng.random() < 0.5 else -1
        pts = [(bx, by)]
        segs = rng.randint(3, 7)
        for _ in range(segs):
            nx = pts[-1][0] + direction * rng.randint(20, 55)
            ny = pts[-1][1] + rng.randint(15, 40)
            if nx < 30 or nx > W - 30:
                direction *= -1
                nx = pts[-1][0] + direction * rng.randint(20, 55)
            if ny > H - 80:
                break
            pts.append((int(nx), int(ny)))
        for i in range(len(pts) - 1):
            thick = max(2, int(7 - i))
            fade = 180 - i * 15
            draw.line((pts[i], pts[i + 1]),
                      fill=(*ROOT_MID, max(40, fade)), width=thick)


def _draw_root_hairs(draw: ImageDraw.ImageDraw, cx: int, cy: int) -> None:
    """Delicate mycelium-like root hairs spreading through the soil."""
    for _ in range(60):
        fx = cx + rng.randint(-280, 280)
        fy = cy + rng.randint(30, 450)
        segs = rng.randint(2, 5)
        pts = [(fx, fy)]
        for _ in range(segs):
            fx += rng.randint(-25, 25)
            fy += rng.randint(15, 45)
            pts.append((int(fx), int(fy)))
        if pts[-1][1] < H - 50:
            draw.line(pts, fill=(*ROOT_PALE, rng.randint(15, 50)),
                      width=rng.randint(1, 2))


def _draw_nodules(img: Image.Image, cx: int, cy: int) -> Image.Image:
    """Bioluminescent root nodules — pulsating green and amber bulbs."""
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(18):
        nx = cx + rng.randint(-180, 180)
        ny = cy + rng.randint(40, 400)
        nr = rng.randint(5, 14)

        # Glow behind nodule
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(g)
        glow_color = rng.choice([ROOT_GLOW_GREEN, ROOT_GLOW_AMBER])
        gd.ellipse((nx - nr * 4, ny - nr * 4, nx + nr * 4, ny + nr * 4),
                   fill=(*glow_color, 14))
        g = g.filter(ImageFilter.GaussianBlur(10))
        img = Image.alpha_composite(img, g)

        draw = ImageDraw.Draw(img, "RGBA")
        # Nodule body
        draw.ellipse((nx - nr, ny - nr, nx + nr, ny + nr),
                     fill=(*glow_color, 210))
        draw.ellipse((nx - nr // 2, ny - nr // 2, nx + nr // 2, ny + nr // 2),
                     fill=(235, 245, 195, 180))
    return img


def _draw_body_horror(draw: ImageDraw.ImageDraw, cx: int, cy: int) -> None:
    """Skeletal remains consumed by roots — rib cages, bones, blood pools."""
    # ── Rib cage shapes wrapped in roots ──
    for _ in range(3):
        sx = cx + rng.randint(-110, 110)
        sy = cy + 120 + rng.randint(0, 160)
        scale = rng.uniform(0.6, 1.0)

        # Rib arcs
        for rib in range(4):
            ry = sy + rib * 22 * scale
            rw = 35 * scale + rng.randint(5, 15)
            draw.arc((sx - rw, ry - 8 * scale, sx + rw, ry + 8 * scale),
                     0, 180, fill=(*BONE, rng.randint(50, 100)),
                     width=max(1, int(2 * scale)))

        # Skull-like form
        sk_x = sx + rng.randint(-8, 8)
        sk_y = sy - 28 * scale
        draw.ellipse((sk_x - 16 * scale, sk_y - 18 * scale,
                      sk_x + 16 * scale, sk_y + 12 * scale),
                     fill=(*BONE, rng.randint(35, 70)))

        # Roots wrapping the bones
        for _ in range(4):
            rx = sx + rng.randint(-45, 45)
            ry = sy + rng.randint(-15, 90)
            draw.line((rx, ry, rx + rng.randint(-20, 20), ry + rng.randint(15, 35)),
                      fill=(*ROOT_DARK, rng.randint(140, 190)),
                      width=rng.randint(2, 4))

    # ── Blood pools / consumed organic residue ──
    for _ in range(10):
        bx = cx + rng.randint(-170, 170)
        by = cy + rng.randint(50, 390)
        br = rng.randint(10, 28)
        draw.ellipse((bx - br, by - br, bx + br, by + br),
                     fill=(*BLOOD, rng.randint(25, 60)))
        draw.ellipse((bx - br // 3, by - br // 3, bx + br // 3, by + br // 3),
                     fill=(*BLOOD, rng.randint(50, 90)))

    # ── Vein-like feeding tendrils (red) ──
    for _ in range(12):
        vx = cx + rng.randint(-160, 160)
        vy = cy + rng.randint(80, 350)
        pts = [(vx, vy)]
        for _ in range(rng.randint(3, 5)):
            vx += rng.randint(-12, 12)
            vy += rng.randint(10, 22)
            pts.append((vx, vy))
        for i in range(len(pts) - 1):
            draw.line((pts[i], pts[i + 1]),
                      fill=(*BLOOD, rng.randint(30, 70)),
                      width=rng.randint(1, 2))


def _draw_fog(img: Image.Image) -> Image.Image:
    """Low ground fog at the horizon line."""
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog)
    fd.ellipse((-300, HORIZON - 70, W + 300, HORIZON + 120),
               fill=(180, 175, 170, 22))
    fog = fog.filter(ImageFilter.GaussianBlur(45))
    return Image.alpha_composite(img, fog)


def _draw_vignette(draw: ImageDraw.ImageDraw) -> None:
    """Darken the edges of the frame for atmosphere."""
    # Sides
    for vy in range(H):
        vt = 1.0 - abs(vy - H // 2) / (H // 2)
        vw = int(45 * max(0.0, 1.0 - vt))
        if vw > 0:
            draw.line((0, vy, vw, vy), fill=(0, 0, 0, 70))
            draw.line((W - vw, vy, W, vy), fill=(0, 0, 0, 70))
    # Top edge
    for vy in range(80):
        alpha = int(90 * (1 - vy / 80))
        draw.line((0, vy, W, vy), fill=(0, 0, 0, alpha))
    # Bottom edge (subtle)
    for vy in range(H - 40, H):
        alpha = int(60 * (vy - (H - 40)) / 40)
        draw.line((0, vy, W, vy), fill=(0, 0, 0, alpha))


def make_cover(mp: Path, op: Path) -> None:
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    # ── Base canvas ──
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 1. Sky ──
    _draw_sky_gradient(draw)

    # ── 2. Stars ──
    _draw_stars(draw)

    # ── 3. Moon ──
    img = _draw_moon(img)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 4. Farmhouse and porch ──
    anchor = _draw_farmhouse(draw)

    # ── 5. Dead trees ──
    _draw_dead_trees(draw, anchor["house_cx"])

    # ── 6. Soil cross-section ──
    _draw_soil_gradient(draw)
    _draw_soil_pebbles(draw)
    _draw_burrows(draw)

    # ── 7. Root glow (underground) ──
    img = _draw_root_glow(img)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 8. Main taproots ──
    root_cx = anchor["porch_x"] + anchor["porch_w"] // 2
    root_cy = anchor["base_y"] + 80
    taproots = _draw_taproots(draw, root_cx, root_cy)

    # ── 9. Secondary branches ──
    _draw_secondary_roots(draw, taproots)

    # ── 10. Root hairs / mycelium ──
    _draw_root_hairs(draw, root_cx, root_cy)

    # ── 11. Bioluminescent nodules ──
    img = _draw_nodules(img, root_cx, root_cy)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 12. Body horror: consumed remains ──
    _draw_body_horror(draw, root_cx, root_cy)

    # ── 13. Fog at horizon ──
    img = _draw_fog(img)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 14. Grass tufts at ground line ──
    for _ in range(50):
        gx = rng.randint(10, W - 10)
        draw.line((gx, HORIZON, gx + rng.randint(-3, 3), HORIZON + rng.randint(3, 10)),
                  fill=(*SOIL_TOP, 180), width=1)

    # ── 15. Vignette ──
    _draw_vignette(draw)

    # ── 16. Title panel ──
    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, title, author, model)
    img.convert("RGB").save(op, "PNG", optimize=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()

    meta_path = ROOT / a.metadata if not a.metadata.is_absolute() else a.metadata
    out_path = ROOT / a.out if not a.out.is_absolute() else a.out
    make_cover(meta_path, out_path)


if __name__ == "__main__":
    main()
