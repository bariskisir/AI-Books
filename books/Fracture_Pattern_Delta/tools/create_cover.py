#!/usr/bin/env python3
"""Cover: Fracture Pattern Delta — A bereaved father fakes remission from state-mandated grief therapy while building a resistance inside the camps that harvest emotional resonance for corporate profit."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# ── palette ──────────────────────────────────────────────────────────────────
# Cold institutional steel blues / gunmetal for the Mourning Authority compound,
# toxic amber/gold for the fracture, muted magenta for harvested grief.
SKY_TOP = (18, 22, 32)
SKY_BOT = (35, 42, 55)
FRACTURE_GLOW = (200, 170, 80)
FRACTURE_HOT = (230, 200, 100)
EXTRACT_COLOR = (180, 70, 120)
CONCRETE = (40, 44, 52)
CONCRETE_LIGHT = (58, 62, 72)
WARM_AMBER = (160, 120, 50)

rng = random.Random()
rng.seed(377648370)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), SKY_TOP + (255,))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 1. Sky gradient ──────────────────────────────────────────────────────
    for y in range(H):
        t = y / H
        r = int(SKY_TOP[0] + (SKY_BOT[0] - SKY_TOP[0]) * t)
        g = int(SKY_TOP[1] + (SKY_BOT[1] - SKY_TOP[1]) * t)
        b = int(SKY_TOP[2] + (SKY_BOT[2] - SKY_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── 2. The Fracture (delta-shaped crack glowing amber) ───────────────────
    # A branching crack that starts from center-top and spreads outward like a delta.
    fracture_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fracture_layer)

    crack_origin_x = W // 2 + rng.randint(-60, 60)
    crack_origin_y = rng.randint(60, 180)

    # Main trunk of the fracture
    segments = []
    cx, cy = crack_origin_x, crack_origin_y
    for _ in range(rng.randint(6, 10)):
        cx += rng.randint(-50, 50)
        cy += rng.randint(80, 160)
        segments.append((cx, cy))

    # Draw main crack thickly with glow
    for i in range(len(segments) - 1):
        x1, y1 = segments[i]
        x2, y2 = segments[i + 1]
        # Hot core
        fd.line((x1, y1, x2, y2), fill=FRACTURE_HOT + (200,), width=rng.randint(3, 6))
        # Outer glow layers
        fd.line((x1, y1, x2, y2), fill=FRACTURE_GLOW + (80,), width=rng.randint(10, 16))
        fd.line((x1, y1, x2, y2), fill=FRACTURE_GLOW + (40,), width=rng.randint(20, 30))

    # Branching sub-cracks
    for _ in range(rng.randint(12, 20)):
        start_idx = rng.randint(0, len(segments) - 2)
        sx, sy = segments[start_idx]
        bx, by = sx + rng.randint(-120, 120), sy + rng.randint(30, 200)
        fd.line((sx, sy, bx, by), fill=FRACTURE_GLOW + (rng.randint(60, 140),), width=rng.randint(2, 5))
        fd.line((sx, sy, bx, by), fill=FRACTURE_GLOW + (30,), width=rng.randint(6, 12))

    # Spiky shards radiating from crack nodes
    for _ in range(rng.randint(15, 25)):
        sx = rng.randint(100, W - 100)
        sy = rng.randint(200, 1400)
        angle = rng.uniform(0, math.tau)
        length = rng.randint(30, 90)
        ex = sx + math.cos(angle) * length
        ey = sy + math.sin(angle) * length
        fd.line((sx, sy, ex, ey), fill=FRACTURE_GLOW + (rng.randint(40, 100),), width=rng.randint(1, 3))

    fracture_layer = fracture_layer.filter(ImageFilter.GaussianBlur(4))
    img = Image.alpha_composite(img, fracture_layer)

    # Redraw core crack hot points (after blur) for intensity
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(rng.randint(8, 15)):
        px, py = rng.choice(segments)
        pr = rng.randint(4, 12)
        draw.ellipse((px - pr, py - pr, px + pr, py + pr), fill=FRACTURE_HOT + (rng.randint(100, 180),))

    # ── 3. Grief therapy camp / Mourning Authority compound ───────────────────
    camp_y = 1580  # base ground line

    # Perimeter wall
    wall_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wall_layer)
    wall_color = CONCRETE + (235,)
    wd.rectangle((0, camp_y - 180, W, camp_y + 30), fill=wall_color)
    # Top of wall with barbed wire
    wd.rectangle((0, camp_y - 190, W, camp_y - 180), fill=(30, 32, 38, 240))
    for bx in range(0, W, rng.randint(14, 22)):
        bw_y = camp_y - 190 + rng.randint(-6, 6)
        wd.line((bx, camp_y - 190, bx + 4, bw_y), fill=(60, 60, 68, 200), width=1)

    # Main building block — brutalist central structure
    build_cx = W // 2
    build_w = rng.randint(500, 700)
    build_h = rng.randint(400, 550)
    build_top = camp_y - build_h
    wd.rectangle((build_cx - build_w // 2, build_top, build_cx + build_w // 2, camp_y),
                 fill=CONCRETE + (240,))

    # Building facade details — rows of small windows (some lit cold, some dark)
    for row in range(4, 10):
        ry = build_top + 30 + row * 40
        if ry > camp_y - 30:
            break
        for col in range(3, 8):
            wx = (build_cx - build_w // 2 + 40) + col * 70
            if wx > build_cx + build_w // 2 - 40:
                break
            w_light = rng.random() < 0.35
            if w_light:
                wd.rectangle((wx, ry, wx + 14, ry + 18), fill=(100, 180, 200, rng.randint(80, 160)))
            else:
                wd.rectangle((wx, ry, wx + 14, ry + 18), fill=(18, 20, 28, 220))

    # Central entrance / intake arch
    arch_x = build_cx
    arch_w = 100
    arch_h = 140
    wd.rectangle((arch_x - arch_w // 2, camp_y - arch_h, arch_x + arch_w // 2, camp_y),
                 fill=(20, 22, 26, 240))
    wd.arc((arch_x - arch_w // 2, camp_y - arch_h, arch_x + arch_w // 2, camp_y),
            0, 180, fill=(40, 44, 52, 240), width=8)

    # Side wings (lower buildings on each side)
    for side, offset in [(-1, -build_w // 2 - 40), (1, build_w // 2 + 40)]:
        wing_w = rng.randint(160, 240)
        wing_h = rng.randint(180, 280)
        wing_x = build_cx + offset - wing_w // 2 if side == 1 else build_cx + offset
        wd.rectangle((wing_x, camp_y - wing_h, wing_x + wing_w, camp_y),
                     fill=CONCRETE_LIGHT + (230,))
        for row in range(2, 5):
            ry = camp_y - wing_h + 20 + row * 35
            if ry > camp_y - 20:
                break
            for col in range(2, 5):
                wx = wing_x + 15 + col * 35
                if wx > wing_x + wing_w - 15:
                    break
                w_light = rng.random() < 0.3
                if w_light:
                    wd.rectangle((wx, ry, wx + 8, ry + 10), fill=(100, 180, 200, rng.randint(60, 130)))
                else:
                    wd.rectangle((wx, ry, wx + 8, ry + 10), fill=(18, 20, 28, 220))

    # Guard towers
    for tx in [120, W - 150]:
        tower_w = 40
        tower_h = rng.randint(200, 280)
        wd.rectangle((tx - tower_w // 2, camp_y - tower_h, tx + tower_w // 2, camp_y),
                     fill=(30, 34, 42, 235))
        # Spotlight fixture
        spot_y = camp_y - tower_h + 20
        wd.rectangle((tx - 20, spot_y - 8, tx + 20, spot_y + 8),
                     fill=(50, 54, 62, 240))

    img = Image.alpha_composite(img, wall_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 4. Searchlight beams from towers ─────────────────────────────────────
    beam_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam_layer)
    for tx, angle_offset in [(120, -0.4), (W - 150, 0.4)]:
        ang = math.radians(90 + angle_offset * 45 + rng.uniform(-5, 5))
        beam_h = 700
        bx = tx
        by = camp_y - 200
        bd.polygon([
            (bx - 4, by),
            (bx + 4, by),
            (bx + math.sin(ang) * beam_h + 60, by - math.cos(ang) * beam_h),
            (bx + math.sin(ang) * beam_h - 60, by - math.cos(ang) * beam_h),
        ], fill=(200, 210, 220, rng.randint(20, 40)))
    beam_layer = beam_layer.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, beam_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 5. Small human figures (the processed) in rows ────────────────────────
    figures_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fgd = ImageDraw.Draw(figures_layer)
    # Queue / rows of people in the yard
    for row_idx in range(rng.randint(3, 5)):
        ry = camp_y + 10 + row_idx * 18
        if ry > camp_y + 80:
            break
        for col in range(rng.randint(8, 14)):
            fx = 200 + col * 90 + rng.randint(-10, 10)
            if fx > W - 200:
                break
            # Tiny human silhouette: head + body
            head_r = 5
            fgd.ellipse((fx - head_r, ry - head_r, fx + head_r, ry + head_r),
                        fill=(15, 17, 22, 200))
            fgd.rectangle((fx - 4, ry + head_r, fx + 4, ry + head_r + 12),
                          fill=(15, 17, 22, 200))
    img = Image.alpha_composite(img, figures_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 6. Emotional resonance extraction streams ────────────────────────────
    # Glowing tendrils rising from the figures up toward the fracture
    extract_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ed = ImageDraw.Draw(extract_layer)

    for _ in range(rng.randint(15, 25)):
        sx = rng.randint(200, 1400)
        sy = rng.randint(camp_y + 10, camp_y + 80)
        # Sinuous upward path
        pts = [(sx, sy)]
        cx, cy = sx, sy
        for _ in range(rng.randint(4, 8)):
            cx += rng.randint(-40, 40)
            cy -= rng.randint(40, 100)
            pts.append((cx, cy))
            if cy < 300:
                break
        # Draw as tapered glow
        for i in range(len(pts) - 1):
            alpha = rng.randint(40, 100)
            width = max(1, rng.randint(2, 5))
            # Core color shifts from amber to magenta as it rises
            t = i / max(1, len(pts))
            rc = int(EXTRACT_COLOR[0] + (FRACTURE_GLOW[0] - EXTRACT_COLOR[0]) * t)
            gc = int(EXTRACT_COLOR[1] + (FRACTURE_GLOW[1] - EXTRACT_COLOR[1]) * t)
            bc = int(EXTRACT_COLOR[2] + (FRACTURE_GLOW[2] - EXTRACT_COLOR[2]) * t)
            ed.line(pts[i:i+2], fill=(rc, gc, bc, alpha), width=width)
            ed.line(pts[i:i+2], fill=(rc, gc, bc, alpha // 3), width=width + 4)

    extract_layer = extract_layer.filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(img, extract_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 7. Floating amber motes / grief particles ────────────────────────────
    for _ in range(rng.randint(30, 50)):
        px = rng.randint(0, W)
        py = rng.randint(200, 1500)
        pr = rng.randint(2, 6)
        pa = rng.randint(40, 130)
        draw.ellipse((px - pr, py - pr, px + pr, py + pr),
                     fill=FRACTURE_GLOW + (pa,))

    # ── 8. Ground / foreground ───────────────────────────────────────────────
    ground = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(ground)
    gd.rectangle((0, camp_y + 80, W, H), fill=(25, 28, 35, 255))
    for gx in range(0, W, rng.randint(30, 60)):
        gh = rng.randint(-10, 15)
        gd.line((gx, camp_y + 80, gx + 20, camp_y + 80 + gh),
                fill=(30, 34, 42, rng.randint(40, 100)), width=2)
    img = Image.alpha_composite(img, ground)

    # ── 9. Token of resistance — faint delta symbol graffiti on wall ────────
    draw = ImageDraw.Draw(img, "RGBA")
    delta_pts = [
        (build_cx + 120, camp_y - 350),
        (build_cx + 120 + 40, camp_y - 300),
        (build_cx + 120 - 40, camp_y - 300),
    ]
    draw.polygon(delta_pts, outline=FRACTURE_GLOW + (60,), width=2)

    # ── Save ─────────────────────────────────────────────────────────────────
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
