#!/usr/bin/env python3
"""Cover: The Bone Mendicant — A pathologist in a rainswept coastal town finds tiny inscribed bones inside her patients' joints, each message foretelling the next death."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# Unique palette: dissected cadaver greens, bone-ivory, rust-rust brown, bruise-purple
CR = (12, 18, 14)   # top — midnight cadaver-green
CL = (55, 38, 28)   # bottom — wet earth / dried blood

BONE_PALE = (215, 205, 185)
BONE_GLOW = (200, 185, 155)
RUST = (120, 55, 35)
BRUISE = (90, 50, 80)
ICHOR = (130, 160, 120)

# Rune-like inscribed markings for the prophetic bones
RUNES = [
    [(0, 0), (6, -10), (12, 0), (6, -10), (6, 0)],           # angular glyph A
    [(0, -8), (8, -8), (8, 2), (0, 2), (0, -8), (8, 2)],      # rectangular glyph B
    [(0, 0), (6, -10), (0, -10), (6, -8), (0, -6)],           # zigzag glyph C
    [(0, -10), (0, 0), (8, -5), (0, -5), (8, 0)],             # fork glyph D
    [(0, -10), (6, -10), (3, -5), (0, 0), (6, 0)],           # arrow glyph E
    [(4, -10), (0, -3), (8, -3), (4, -10), (4, 0)],          # diamond-thread glyph F
    [(0, -10), (8, -10), (0, 0), (8, 0), (4, -5)],           # cross-hatch glyph G
]


def _draw_rune(draw, cx, cy, scale, col, rng):
    """Draw a tiny inscribed bone-rune at (cx, cy)."""
    glyph = rng.choice(RUNES)
    pts = [(cx + int(x * scale), cy + int(y * scale)) for (x, y) in glyph]
    draw.line(pts, fill=col, width=max(1, int(scale * 0.8)))
    # Small dot at start (the "bone knot")
    draw.ellipse((cx - scale, cy - scale, cx + scale, cy + scale), fill=col)


def _draw_inscribed_bone(draw, cx, cy, size, rng):
    """Draw a tiny bone fragment with inscribed runes."""
    angle = rng.uniform(0, math.tau)
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    # Bone shaft
    pts = []
    segments = rng.randint(3, 5)
    for i in range(segments + 1):
        t = i / segments
        ox = int(math.sin(t * math.pi * 2) * size * 0.18)
        bx = int(cx + t * size * 0.7 * cos_a - ox * sin_a)
        by = int(cy + t * size * 0.7 * sin_a + ox * cos_a)
        pts.append((bx, by))
    col = (rng.randint(180, 215), rng.randint(165, 200), rng.randint(140, 180), rng.randint(80, 200))
    draw.line(pts, fill=col, width=max(2, size // 8))
    # Knobby ends
    for end_x, end_y in [pts[0], pts[-1]]:
        draw.ellipse(
            (end_x - size * 0.12, end_y - size * 0.12,
             end_x + size * 0.12, end_y + size * 0.12),
            fill=col,
        )
    # Inscribed rune on the bone
    rx = int(cx + math.cos(angle + 0.5) * size * 0.15)
    ry = int(cy + math.sin(angle + 0.5) * size * 0.15)
    _draw_rune(draw, rx, ry, max(2, size // 12),
               (rng.randint(220, 255), rng.randint(190, 220), rng.randint(130, 170), rng.randint(150, 230)),
               rng)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")
    rng = random.Random(hash(title + "mendicant-bone-cadaver-iris-2025"))

    # ── 1. Gradient background (cadaver-green to mud-brown) ─────────
    img = Image.new("RGBA", (W, H), (*CR, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(H):
        t = y / H
        r = int(CR[0] + (CL[0] - CR[0]) * t + 4 * math.sin(t * 2.3))
        g = int(CR[1] + (CL[1] - CR[1]) * t + 3 * math.sin(t * 1.7 + 0.5))
        b = int(CR[2] + (CL[2] - CR[2]) * t + 2 * math.sin(t * 3.1))
        draw.line((0, y, W, y), fill=(max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), 255))

    # ── 2. X-ray ribcage — the central anatomical focal point ──────
    rib_cx, rib_cy = W // 2, H // 2 - 180

    # Deep glow behind the ribs
    glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)
    gd.ellipse(
        (rib_cx - 300, rib_cy - 200, rib_cx + 300, rib_cy + 380),
        fill=(ICHOR[0], ICHOR[1], ICHOR[2], 18),
    )
    gd.ellipse(
        (rib_cx - 180, rib_cy - 120, rib_cx + 180, rib_cy + 280),
        fill=(BRUISE[0], BRUISE[1], BRUISE[2], 25),
    )
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img, glow_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # Spine (vertebral column)
    for vi in range(16):
        vy = rib_cy - 100 + vi * 28
        vw = 14 - vi * 0.4
        vh = 12 + vi * 0.3
        v_alpha = 180 - vi * 8
        # Vertebra body
        draw.ellipse(
            (rib_cx - vw, vy - vh, rib_cx + vw, vy + vh),
            fill=(BONE_PALE[0] - vi * 3, BONE_PALE[1] - vi * 4, BONE_PALE[2] - vi * 5, max(40, v_alpha)),
        )
        # Spinous process (small rear projection)
        draw.line(
            (rib_cx, vy - vh, rib_cx, vy - vh - 8),
            fill=(*BONE_PALE, max(30, v_alpha - 20)), width=2,
        )

    # Clavicles (collarbones)
    draw.line((rib_cx - 160, rib_cy - 95, rib_cx + 160, rib_cy - 95),
              fill=(*BONE_PALE, 180), width=8)
    # Left clavicle arc
    draw.arc((rib_cx - 200, rib_cy - 120, rib_cx - 140, rib_cy - 70),
             180, 360, fill=(*BONE_PALE, 140), width=6)
    # Right clavicle arc
    draw.arc((rib_cx + 140, rib_cy - 120, rib_cx + 200, rib_cy - 70),
             0, 180, fill=(*BONE_PALE, 140), width=6)

    # Ribs (seven pairs, arcs sweeping outward)
    for ri in range(7):
        ry = rib_cy - 70 + ri * 32
        iw = 25 + ri * 4    # inner width of rib arc
        ow = 80 + ri * 18   # outer width
        rh = 80 - ri * 6
        alpha = 160 - ri * 18
        rib_col = (
            min(215, BONE_PALE[0] - ri * 5),
            min(205, BONE_PALE[1] - ri * 6),
            min(185, BONE_PALE[2] - ri * 7),
            max(30, alpha),
        )
        # Left rib arc
        draw.arc(
            (rib_cx - ow, ry, rib_cx - iw, ry + rh),
            0, 180,
            fill=rib_col, width=max(3, 7 - ri),
        )
        draw.arc(
            (rib_cx - ow + 10, ry + 6, rib_cx - iw - 8, ry + rh - 5),
            0, 180,
            fill=(20, 25, 22, max(20, 70 - ri * 8)), width=max(2, 5 - ri),
        )
        # Right rib arc
        draw.arc(
            (rib_cx + iw, ry, rib_cx + ow, ry + rh),
            0, 180,
            fill=rib_col, width=max(3, 7 - ri),
        )
        draw.arc(
            (rib_cx + iw + 8, ry + 6, rib_cx + ow - 10, ry + rh - 5),
            0, 180,
            fill=(20, 25, 22, max(20, 70 - ri * 8)), width=max(2, 5 - ri),
        )

    # Sternum (breastbone)
    draw.polygon(
        [(rib_cx - 12, rib_cy - 80), (rib_cx + 12, rib_cy - 80),
         (rib_cx + 16, rib_cy + 90), (rib_cx - 16, rib_cy + 90)],
        fill=(195, 180, 155, 160),
    )

    # ── 3. Pelvis (lower, faded, emerging from shadow) ────────────
    pelvis_y = rib_cy + 230
    draw.arc(
        (rib_cx - 140, pelvis_y - 40, rib_cx + 140, pelvis_y + 80),
        0, 180, fill=(*BONE_PALE, 90), width=12,
    )
    draw.arc(
        (rib_cx - 70, pelvis_y - 10, rib_cx + 70, pelvis_y + 60),
        0, 180, fill=(*BONE_PALE, 60), width=6,
    )
    # Iliac crests
    draw.arc((rib_cx - 180, pelvis_y - 10, rib_cx - 130, pelvis_y + 50),
             90, 270,
             fill=(*BONE_PALE, 70), width=5)
    draw.arc((rib_cx + 130, pelvis_y - 10, rib_cx + 180, pelvis_y + 50),
             270, 450,
             fill=(*BONE_PALE, 70), width=5)

    # ── 4. Dissection / autopsy table line ─────────────────────────
    table_y = rib_cy + 320
    draw.line((80, table_y, W - 80, table_y), fill=(60, 45, 35, 200), width=4)
    draw.line((100, table_y + 8, W - 100, table_y + 8), fill=(40, 30, 20, 120), width=2)
    # Metal table legs
    for leg_x in (200, W - 200):
        draw.line((leg_x, table_y, leg_x - 20, table_y + 160), fill=(50, 45, 40, 180), width=5)
        draw.line((leg_x + 40, table_y, leg_x + 60, table_y + 160), fill=(50, 45, 40, 180), width=5)

    # ── 5. Inscribed bones (floating / emerging from the ribcage) ──
    for _ in range(rng.randint(18, 30)):
        angle_offset = rng.uniform(0, math.tau)
        dist = rng.uniform(40, 320)
        bx = int(rib_cx + math.cos(angle_offset) * dist)
        by = int(rib_cy + math.sin(angle_offset) * dist * 0.7)
        # Bones cluster near the ribs, scatter outward
        b_size = rng.randint(12, 32)
        _draw_inscribed_bone(draw, bx, by, b_size, rng)

    # ── 6. Runed bone fragments scattered across the cover ─────────
    for _ in range(rng.randint(12, 20)):
        fx = rng.randint(100, W - 100)
        fy = rng.randint(80, table_y - 50)
        # Avoid overlapping the central ribcage too much
        dx, dy = fx - rib_cx, fy - rib_cy
        if math.hypot(dx / 1.5, dy) < 180:
            continue
        f_size = rng.randint(6, 18)
        _draw_inscribed_bone(draw, fx, fy, f_size, rng)

    # ── 7. Anatomical reference / measurement lines ────────────────
    # Fine diagrammatic lines (like a medical textbook)
    for _ in range(rng.randint(6, 10)):
        lx = rng.randint(40, 120)
        ly = rng.randint(200, table_y - 50)
        angle_m = rng.uniform(-0.3, 0.3)
        line_len = rng.randint(60, 200)
        end_x = lx + int(math.cos(angle_m) * line_len)
        end_y = ly + int(math.sin(angle_m) * line_len)
        draw.line((lx, ly, end_x, end_y), fill=(160, 140, 120, rng.randint(25, 60)), width=1)
        # Tic marks
        draw.line((end_x - 4, end_y - 4, end_x + 4, end_y + 4), fill=(160, 140, 120, 40), width=1)
        # Label dot
        draw.ellipse((lx - 2, ly - 2, lx + 2, ly + 2), fill=(170, 150, 130, max(40, rng.randint(30, 70))))

    # ── 8. Rain — heavy, slanting, coastal ─────────────────────────
    rain_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rain_layer)
    for _ in range(rng.randint(200, 350)):
        rx = rng.randint(0, W + 200) - 100
        ry = rng.randint(0, H)
        r_len = rng.randint(15, 50)
        r_off = rng.uniform(2.0, 5.0)
        r_width = rng.uniform(0.5, 1.5)
        rd.line(
            (rx, ry, rx + r_off, ry + r_len),
            fill=(160, 175, 185, rng.randint(8, 30)),
            width=round(r_width),
        )
    rain_layer = rain_layer.filter(ImageFilter.GaussianBlur(1.0))
    img = Image.alpha_composite(img, rain_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 9. Coastal fog drifting in from the edges ──────────────────
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog)
    for _ in range(rng.randint(6, 12)):
        f_cx = rng.choice([rng.randint(-200, 100), rng.randint(W - 100, W + 200)])
        f_cy = rng.randint(200, table_y)
        f_r = rng.randint(200, 450)
        f_alpha = rng.randint(6, 18)
        fd.ellipse(
            (f_cx - f_r, f_cy - f_r, f_cx + f_r, f_cy + f_r),
            fill=(140, 155, 160, f_alpha),
        )
    # Fog bank across the bottom
    fd.ellipse((-300, table_y - 80, W + 300, H + 100), fill=(130, 145, 140, 30))
    fog = fog.filter(ImageFilter.GaussianBlur(50))
    img = Image.alpha_composite(img, fog)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 10. Fine red/copper threads (like nerve or blood traces) ───
    for _ in range(rng.randint(8, 14)):
        sx = rng.randint(0, W)
        sy = rng.randint(0, table_y)
        pts = [(sx, sy)]
        cx, cy = sx, sy
        for _ in range(rng.randint(4, 10)):
            cx += rng.randint(-40, 40)
            cy += rng.randint(15, 45)
            pts.append((cx, cy))
        draw.line(
            pts,
            fill=(rng.randint(100, 160), rng.randint(20, 50), rng.randint(20, 50), rng.randint(20, 60)),
            width=rng.randint(1, 2),
        )

    # ── 11. Vignette ───────────────────────────────────────────────
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(45 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 100))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 100))

    # ── 12. Title panel ────────────────────────────────────────────
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
