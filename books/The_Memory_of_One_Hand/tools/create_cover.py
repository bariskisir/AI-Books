#!/usr/bin/env python3
"""Cover: The Memory of One Hand — A disgraced neurosurgeon receiving anonymous memory fragments must reconstruct a serial killer's identity, only to find each fragment is a memory he erased from his own mind."""

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
rng.seed(891735204)

# ── Palette: deep clinical background, warm memory-gold, surgical glove, neural-cyan ──
BG_TOP = (8, 10, 20)
BG_BOT = (18, 28, 48)
MEMORY_COLORS = [
    (210, 170, 80),   # gold
    (190, 140, 65),   # amber
    (170, 105, 50),   # copper
    (200, 160, 95),   # pale gold
    (160, 90, 55),    # rust-gold
]
VOID_DARK = (3, 5, 12)
DIM_SLATE = (35, 50, 75)
NEURAL_CYAN = (60, 180, 210)


def _fragment_poly(cx, cy, w, h, verts_count):
    """Generate an irregular polygon resembling a shattered memory shard."""
    verts = []
    for i in range(verts_count):
        ang = i / verts_count * math.tau + rng.uniform(-0.18, 0.18)
        rad = rng.uniform(0.45, 1.0)
        vx = cx + math.cos(ang) * w * 0.5 * rad
        vy = cy + math.sin(ang) * h * 0.5 * rad
        verts.append((vx, vy))
    return verts


def _finger_seg(dr, x1, y1, x2, y2, width):
    """Draw a finger segment as a tapered quadrilateral with outline."""
    ang = math.atan2(y2 - y1, x2 - x1)
    perp = ang + math.pi / 2
    hw = width / 2
    p1 = (x1 + math.cos(perp) * hw, y1 + math.sin(perp) * hw)
    p2 = (x2 + math.cos(perp) * hw, y2 + math.sin(perp) * hw)
    p3 = (x2 - math.cos(perp) * hw, y2 - math.sin(perp) * hw)
    p4 = (x1 - math.cos(perp) * hw, y1 - math.sin(perp) * hw)
    dr.polygon([p1, p2, p3, p4], fill=(16, 20, 35, 170),
               outline=(45, 60, 90, 90), width=1)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    # ── 1. Base with gradient: near-black top to deep clinical blue bottom ──
    img = Image.new("RGBA", (W, H), (*BG_TOP, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        r = int(BG_TOP[0] + (BG_BOT[0] - BG_TOP[0]) * t)
        g = int(BG_TOP[1] + (BG_BOT[1] - BG_TOP[1]) * t)
        b = int(BG_TOP[2] + (BG_BOT[2] - BG_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── 2. Vignette ──
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(60 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 120))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 120))

    # ── 3. Memory fragments clustered in a brain-shaped elliptical region ──
    brain_cx, brain_cy = W // 2, 750
    brain_w, brain_h = 750, 550

    fragments = []
    for _ in range(60):
        ang = rng.random() * math.tau
        radius = (rng.random() * 0.5 + rng.random() * 0.5) * 0.82
        fx = brain_cx + math.cos(ang) * brain_w * 0.45 * radius
        fy = brain_cy + math.sin(ang) * brain_h * 0.45 * radius

        fw = rng.randint(35, 100)
        fh = rng.randint(30, 85)

        type_roll = rng.random()
        if type_roll < 0.38:
            ftype = "intact"
            base_color = rng.choice(MEMORY_COLORS)
        elif type_roll < 0.68:
            ftype = "dim"
            base_color = DIM_SLATE
        else:
            ftype = "void"
            base_color = VOID_DARK

        verts = _fragment_poly(fx, fy, fw, fh, rng.randint(5, 7))
        fragments.append({
            "verts": verts, "color": base_color, "type": ftype,
            "cx": fx, "cy": fy, "fw": fw, "fh": fh,
        })

    # Draw voids and dim fragments first, then intact on top
    fragments.sort(key=lambda f: 0 if f["type"] == "intact" else 1)

    for frag in fragments:
        fc = frag["color"]
        if frag["type"] == "intact":
            alpha = rng.randint(180, 240)
            border_col = (
                min(255, fc[0] + 40),
                min(255, fc[1] + 35),
                min(255, fc[2] + 25),
                100,
            )
            # Warm glow behind intact fragments
            glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            gd = ImageDraw.Draw(glow)
            gr = max(frag["fw"], frag["fh"]) * 0.6
            gd.ellipse((frag["cx"] - gr, frag["cy"] - gr,
                        frag["cx"] + gr, frag["cy"] + gr),
                       fill=(*fc, 10))
            glow = glow.filter(ImageFilter.GaussianBlur(15))
            img = Image.alpha_composite(img, glow)
            draw = ImageDraw.Draw(img, "RGBA")
        elif frag["type"] == "dim":
            alpha = rng.randint(90, 160)
            border_col = (60, 80, 110, 50)
        else:
            alpha = 230
            border_col = (15, 18, 30, 70)

        draw.polygon(frag["verts"], fill=(*fc, alpha))
        if frag["type"] in ("intact", "void"):
            draw.polygon(frag["verts"], fill=None, outline=border_col, width=1)

    # ── 4. Neural connection threads (synaptic bridges between intact fragments) ──
    intact = [f for f in fragments if f["type"] == "intact"]
    for i, a in enumerate(intact):
        for b in intact[i + 1:]:
            dist = math.hypot(a["cx"] - b["cx"], a["cy"] - b["cy"])
            if 20 < dist < 160 and rng.random() < 0.35:
                alpha = rng.randint(12, 40)
                draw.line((a["cx"], a["cy"], b["cx"], b["cy"]),
                          fill=(*NEURAL_CYAN, alpha), width=rng.randint(1, 2))
                # Tiny node at midpoint (synaptic junction)
                mx, my = (a["cx"] + b["cx"]) / 2, (a["cy"] + b["cy"]) / 2
                draw.ellipse((mx - 2, my - 2, mx + 2, my + 2),
                             fill=(*NEURAL_CYAN, alpha + 10))

    # ── 5. Escaped memory fragments floating upward (lost memories) ──
    for _ in range(rng.randint(8, 15)):
        fx = rng.randint(200, W - 200)
        fy = rng.randint(60, 400)
        fw = rng.randint(15, 45)
        fh = rng.randint(12, 35)
        verts = _fragment_poly(fx, fy, fw, fh, 5)
        col = rng.choice(MEMORY_COLORS)
        alpha = rng.randint(60, 130)
        draw.polygon(verts, fill=(*col, alpha))
        draw.polygon(verts, fill=None, outline=(*col, alpha // 2), width=1)

    # ── 6. X-ray style surgical-glove hand silhouette (THE MEMORY OF ONE HAND) ──
    hand_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hand_layer)

    palm_cx = W - 350
    palm_cy = 1300

    # Arm/wrist emerging from bottom-right
    hd.polygon([
        (palm_cx - 45, palm_cy + 130),
        (palm_cx + 45, palm_cy + 110),
        (palm_cx + 30, palm_cy + 20),
        (palm_cx - 30, palm_cy + 30),
    ], fill=(16, 20, 35, 150), outline=(50, 65, 95, 90), width=1)

    # Palm
    hd.ellipse((palm_cx - 35, palm_cy - 30, palm_cx + 45, palm_cy + 40),
               fill=(16, 20, 35, 160), outline=(45, 60, 90, 100), width=1)

    # Fingers reaching toward the brain fragments (up and left)
    # Index finger
    _finger_seg(hd, palm_cx - 15, palm_cy - 25, palm_cx - 70, palm_cy - 160, 14)
    hd.ellipse((palm_cx - 77, palm_cy - 167, palm_cx - 63, palm_cy - 153),
               fill=(20, 25, 42, 180), outline=(50, 65, 95, 110), width=1)

    # Middle finger
    _finger_seg(hd, palm_cx + 10, palm_cy - 28, palm_cx - 40, palm_cy - 185, 15)
    hd.ellipse((palm_cx - 48, palm_cy - 193, palm_cx - 32, palm_cy - 177),
               fill=(20, 25, 42, 180), outline=(50, 65, 95, 110), width=1)

    # Ring finger
    _finger_seg(hd, palm_cx + 35, palm_cy - 22, palm_cx - 5, palm_cy - 170, 13)
    hd.ellipse((palm_cx - 12, palm_cy - 177, palm_cx + 2, palm_cy - 163),
               fill=(20, 25, 42, 180), outline=(50, 65, 95, 110), width=1)

    # Pinky
    _finger_seg(hd, palm_cx + 50, palm_cy - 10, palm_cx + 25, palm_cy - 135, 11)
    hd.ellipse((palm_cx + 18, palm_cy - 141, palm_cx + 32, palm_cy - 129),
               fill=(20, 25, 42, 180), outline=(50, 65, 95, 110), width=1)

    # Thumb
    _finger_seg(hd, palm_cx - 30, palm_cy + 10, palm_cx - 100, palm_cy - 40, 16)
    hd.ellipse((palm_cx - 107, palm_cy - 47, palm_cx - 93, palm_cy - 33),
               fill=(20, 25, 42, 180), outline=(50, 65, 95, 110), width=1)

    # Surgical glove cuff ring at wrist
    hd.ellipse((palm_cx - 32, palm_cy + 28, palm_cx + 28, palm_cy + 48),
               fill=None, outline=(55, 70, 100, 100), width=2)

    img = Image.alpha_composite(img, hand_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 7. Faint EEG-style background traces ──
    for wave_idx in range(4):
        y_base = 300 + wave_idx * 180 + rng.randint(0, 40)
        amp = 20 + wave_idx * 8
        pts = []
        for x in range(0, W + 1, 15):
            y = y_base + (math.sin(x * 0.018 + wave_idx * 1.7) * amp
                          + math.sin(x * 0.04 + wave_idx * 2.3) * amp * 0.4
                          + math.sin(x * 0.08 + wave_idx * 0.9) * amp * 0.2)
            pts.append((x, y))
        alpha = rng.randint(6, 16)
        for i in range(len(pts) - 1):
            draw.line((pts[i], pts[i + 1]), fill=(40, 140, 160, alpha), width=1)

    # ── 8. Fine atmospheric dust / neural particles ──
    dust = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(dust)
    for _ in range(100):
        dx = rng.randint(40, W - 40)
        dy = rng.randint(40, H - 200)
        dr = rng.randint(1, 3)
        db = rng.randint(180, 220)
        ds.ellipse((dx - dr, dy - dr, dx + dr, dy + dr),
                   fill=(db, db - 10, db - 30, rng.randint(8, 25)))
    dust = dust.filter(ImageFilter.GaussianBlur(1))
    img = Image.alpha_composite(img, dust)

    # ── 9. Separator line ──
    draw = ImageDraw.Draw(img, "RGBA")
    draw.line((180, H - 155, W - 180, H - 155), fill=(*NEURAL_CYAN, 80), width=1)

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
