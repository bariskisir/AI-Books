#!/usr/bin/env python3
"""Cover: The Osteomancer's Daughter — In an industrial city where a woman reads the dead in their bones, a grieving industrialist's drowned wife reveals a murder reaching into the city's founding. Bone-gothic with skeletal arch, industrial skyline, and bone-magic runes."""

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
rng.seed(941273156)

# ── The Osteomancer's Daughter palette ──────────────────────────────
# Bone-gothic industrial: weathered ivory, rust, coal-smoke, and cold spectral blue
SKY_TOP = (28, 24, 34)          # soot-stained midnight
SKY_MID = (45, 36, 30)          # smoky brown-grey
SKY_BOT = (55, 32, 28)          # rust-tinged brown near horizon
BONE_LIGHT = (225, 212, 188)    # polished bone highlight
BONE_MID = (195, 178, 152)      # weathered bone
BONE_DARK = (155, 138, 112)     # aged bone shadow
BONE_RUNES = (140, 200, 215)    # spectral blue-green bone-magic glow
BONE_RUNES_DIM = (80, 140, 160) # dim rune glow
RUST = (140, 60, 40)            # iron rust
SMOKE = (60, 52, 48)            # coal smoke / fog
EMBER = (200, 80, 40)           # forge glow
IVORY = (240, 232, 218)         # bright highlight
WINDOW_LIT = (200, 180, 100)    # lit window
COLD_WATER = (80, 120, 140)     # drowned wife's spectral hue


def gaussian(x, mu, sigma):
    return math.exp(-((x - mu) ** 2) / (2 * sigma * sigma))


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), SKY_TOP + (255,))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Gradient sky: soot-black at top, rust-brown at horizon ──
    for y in range(H):
        t = y / H
        if t < 0.5:
            t2 = t / 0.5
            r = int(SKY_TOP[0] + (SKY_MID[0] - SKY_TOP[0]) * t2)
            g = int(SKY_TOP[1] + (SKY_MID[1] - SKY_TOP[1]) * t2)
            b = int(SKY_TOP[2] + (SKY_MID[2] - SKY_TOP[2]) * t2)
        else:
            t2 = (t - 0.5) / 0.5
            r = int(SKY_MID[0] + (SKY_BOT[0] - SKY_MID[0]) * t2)
            g = int(SKY_MID[1] + (SKY_BOT[1] - SKY_MID[1]) * t2)
            b = int(SKY_MID[2] + (SKY_BOT[2] - SKY_MID[2]) * t2)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── INDUSTRIAL SKYLINE: factory chimneys, foundries, tenements ──
    skyline = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(skyline)
    horizon = 1750

    # Factory buildings (rear layer, darker)
    factories = [
        (0, horizon - 320, 200, horizon),
        (180, horizon - 260, 380, horizon),
        (350, horizon - 380, 580, horizon),
        (550, horizon - 220, 700, horizon),
        (680, horizon - 350, 890, horizon),
        (870, horizon - 280, 1050, horizon),
        (1030, horizon - 400, 1240, horizon),
        (1220, horizon - 250, 1420, horizon),
        (1400, horizon - 340, 1600, horizon),
    ]
    for fx1, fy1, fx2, fy2 in factories:
        sd.rectangle((fx1, fy1, fx2, fy2), fill=(22, 18, 20, 230))
        # Factory roof (flat with parapet)
        sd.rectangle((fx1 - 5, fy1 - 5, fx2 + 5, fy1), fill=(18, 14, 16, 230))

    # Smokestacks rising from factories
    stacks = [
        (60, horizon - 320, 12, 320),
        (260, horizon - 260, 10, 200),
        (440, horizon - 380, 14, 380),
        (750, horizon - 350, 10, 280),
        (1130, horizon - 400, 12, 340),
        (1500, horizon - 340, 10, 260),
    ]
    for sx, sy, sw, sh in stacks:
        sd.rectangle((sx - sw, sy - sh, sx + sw, sy), fill=(16, 12, 14, 230))
        # Chimney top rim
        sd.rectangle((sx - sw - 4, sy - sh - 6, sx + sw + 4, sy - sh), fill=(20, 16, 18, 230))

    # Smoke plumes from chimneys
    stack_smoke_centers = [(60, 1550), (260, 1700), (440, 1520), (750, 1600), (1130, 1550), (1500, 1630)]
    for sm_x, sm_y in stack_smoke_centers:
        for ring in range(8):
            ring_r = 20 + ring * 18
            ring_alpha = max(4, 28 - ring * 3)
            ring_off_x = rng.randint(-10, 10) + ring * 4
            ring_off_y = -ring * 12 + rng.randint(-5, 5)
            sd.ellipse(
                (sm_x - ring_r + ring_off_x, sm_y - ring_r + ring_off_y,
                 sm_x + ring_r + ring_off_x, sm_y + ring_r + ring_off_y),
                fill=SMOKE + (ring_alpha,),
            )
    img = Image.alpha_composite(img, skyline)

    # ── Foreground cobblestone street ──
    street = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    std = ImageDraw.Draw(street)
    street_y = 1850
    for row in range(10):
        row_y = street_y + row * 40
        offset = (row % 2) * 45
        for col in range(-1, 24):
            cx = col * 75 + offset
            cy = row_y + rng.randint(-4, 4)
            stone_shade = 50 + rng.randint(0, 20)
            std.ellipse(
                (cx - 28, cy - 12, cx + 28, cy + 14),
                fill=(stone_shade, stone_shade - 4, stone_shade - 6, 200),
            )
    img = Image.alpha_composite(img, street)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Gas lamps along street ──
    def draw_lamp(lx, ly, height, glow_radius):
        lamp_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lamp_layer)
        # Post
        ld.line((lx, ly, lx, ly + height), fill=(30, 26, 24, 200), width=5)
        # Lantern
        ld.rectangle((lx - 12, ly - 25, lx + 12, ly), fill=(35, 30, 25, 220))
        ld.polygon([(lx - 16, ly - 25), (lx + 16, ly - 25), (lx, ly - 35)], fill=(35, 30, 25, 220))
        # Glow
        for g in range(6):
            a = int(14 * (1 - g / 6))
            rr = glow_radius - g * 15
            ld.ellipse((lx - rr, ly - 25 - rr // 2, lx + rr, ly + rr // 2), fill=(220, 180, 80, a))
        return lamp_layer

    for lamp_x, lamp_y, lamp_h, lamp_g in [
        (120, 1000, 680, 150),
        (380, 1050, 650, 130),
        (1220, 1040, 660, 130),
        (1480, 1000, 680, 150),
    ]:
        lamp = draw_lamp(lamp_x, lamp_y, lamp_h, lamp_g)
        img = Image.alpha_composite(img, lamp)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── THE BONE ARCH: a massive skeletal archway (rib cage / whalebone structure) dominating the composition ──
    bone_arch = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bone_arch)

    arch_cx, arch_cy = W // 2, 850
    arch_span = 700
    arch_height = 600

    # Left main rib column (femur-like)
    rib_segments_left = [
        (arch_cx - 350, arch_cy + 200, arch_cx - 220, arch_cy - 350),
        (arch_cx - 380, arch_cy + 180, arch_cx - 260, arch_cy - 380),
    ]
    for x1, y1, x2, y2 in rib_segments_left:
        bd.line((x1, y1, x2, y2), fill=BONE_MID + (220,), width=18)
        # Bone joint knobs
        bd.ellipse((x1 - 12, y1 - 12, x1 + 12, y1 + 12), fill=BONE_LIGHT + (220,))
        bd.ellipse((x2 - 10, y2 - 10, x2 + 10, y2 + 10), fill=BONE_LIGHT + (220,))

    # Right main rib column
    rib_segments_right = [
        (arch_cx + 220, arch_cy + 200, arch_cx + 350, arch_cy - 350),
        (arch_cx + 260, arch_cy + 180, arch_cx + 380, arch_cy - 380),
    ]
    for x1, y1, x2, y2 in rib_segments_right:
        bd.line((x1, y1, x2, y2), fill=BONE_MID + (220,), width=18)
        bd.ellipse((x1 - 12, y1 - 12, x1 + 12, y1 + 12), fill=BONE_LIGHT + (220,))
        bd.ellipse((x2 - 10, y2 - 10, x2 + 10, y2 + 10), fill=BONE_LIGHT + (220,))

    # Curved arch ribs (like whale ribs crossing overhead)
    for i in range(6):
        t = i / 5  # 0 to 1
        x_offset = int((t - 0.5) * arch_span)
        y_peak = int(arch_cy - 350 - (1 - abs(t - 0.5) * 2) * arch_height * 0.6)
        # Left-side curved rib
        if t < 0.6:
            left_x = arch_cx - int(arch_span * 0.4) + x_offset
            left_y_top = arch_cy - 350 - int((1 - abs(t - 0.5) * 2) * arch_height * 0.5)
            pts_left = []
            for seg in range(10):
                seg_t = seg / 9
                px = left_x - int(seg_t * 200)
                py = left_y_top + int(seg_t * 400)
                pts_left.append((px, py))
            # Draw thicker ribs at bottom, thinner at top
            rib_w = max(4, 16 - int(t * 12))
            for s in range(len(pts_left) - 1):
                bd.line((pts_left[s], pts_left[s + 1]), fill=BONE_DARK + (180 - int(t * 40),), width=rib_w)

    for i in range(6):
        t = i / 5
        x_offset = int((t - 0.5) * arch_span)
        if t > 0.4:
            right_x = arch_cx + int(arch_span * 0.4) - (1 - t) * int(arch_span * 0.4)
            right_y_top = arch_cy - 350 - int((1 - abs(t - 0.5) * 2) * arch_height * 0.5)
            pts_right = []
            for seg in range(10):
                seg_t = seg / 9
                px = right_x + int(seg_t * 200)
                py = right_y_top + int(seg_t * 400)
                pts_right.append((px, py))
            rib_w = max(4, 16 - int(t * 12))
            for s in range(len(pts_right) - 1):
                bd.line((pts_right[s], pts_right[s + 1]), fill=BONE_DARK + (180 - int(t * 40),), width=rib_w)

    # Skull/top structure: a pelvic bone shape at the apex of the arch
    apex_y = arch_cy - 380
    bd.ellipse(
        (arch_cx - 80, apex_y - 40, arch_cx + 80, apex_y + 40),
        fill=BONE_MID + (200,),
    )
    bd.ellipse(
        (arch_cx - 60, apex_y - 25, arch_cx - 10, apex_y + 15),
        fill=(10, 8, 12, 200),
    )
    bd.ellipse(
        (arch_cx + 10, apex_y - 25, arch_cx + 60, apex_y + 15),
        fill=(10, 8, 12, 200),
    )

    # Bone-magic runes glowing on the arch ribs
    rune_positions = [
        (arch_cx - 280, arch_cy - 200),
        (arch_cx - 300, arch_cy - 50),
        (arch_cx - 250, arch_cy + 100),
        (arch_cx + 250, arch_cy - 200),
        (arch_cx + 280, arch_cy - 50),
        (arch_cx + 240, arch_cy + 100),
        (arch_cx - 180, arch_cy - 280),
        (arch_cx + 180, arch_cy - 280),
    ]

    for rx, ry in rune_positions:
        # Glow under the rune
        for g in range(5):
            ga = int(20 * (1 - g / 5))
            gr = 30 + g * 10
            bd.ellipse((rx - gr, ry - gr, rx + gr, ry + gr), fill=BONE_RUNES + (ga,))
        # Draw rune shape (angular bone-script glyphs)
        rune_type = rng.randint(0, 3)
        rune_col = BONE_RUNES + (180,)
        if rune_type == 0:
            # Angular zigzag
            bd.line((rx - 10, ry - 12, rx + 10, ry - 12), fill=rune_col, width=3)
            bd.line((rx + 10, ry - 12, rx - 5, ry), fill=rune_col, width=3)
            bd.line((rx - 5, ry, rx + 8, ry + 12), fill=rune_col, width=3)
        elif rune_type == 1:
            # Cross-hatch diamond
            bd.line((rx - 12, ry, rx + 12, ry), fill=rune_col, width=3)
            bd.line((rx, ry - 12, rx, ry + 12), fill=rune_col, width=3)
            bd.line((rx - 8, ry - 8, rx + 8, ry + 8), fill=rune_col, width=2)
            bd.line((rx + 8, ry - 8, rx - 8, ry + 8), fill=rune_col, width=2)
        elif rune_type == 2:
            # Spiral glyph
            for ring in range(4):
                rr = 5 + ring * 3
                bd.ellipse((rx - rr, ry - rr, rx + rr, ry + rr), outline=rune_col, width=2)
        else:
            # Vertical rune-stick with crossbar
            bd.line((rx, ry - 14, rx, ry + 14), fill=rune_col, width=4)
            bd.line((rx - 8, ry - 5, rx + 8, ry - 5), fill=rune_col, width=3)
            bd.line((rx - 8, ry + 5, rx + 8, ry + 5), fill=rune_col, width=3)

        # Faint rune trail connecting to adjacent rune
        if rng.random() < 0.6:
            trail_end_x = rx + rng.randint(-60, 60)
            trail_end_y = ry + rng.randint(-60, 60)
            for con in range(3):
                ta = int(10 * (1 - con / 3))
                bd.line(
                    (rx + con * (trail_end_x - rx) // 3,
                     ry + con * (trail_end_y - ry) // 3,
                     rx + (con + 1) * (trail_end_x - rx) // 3,
                     ry + (con + 1) * (trail_end_y - ry) // 3),
                    fill=BONE_RUNES_DIM + (ta,),
                    width=1,
                )

    img = Image.alpha_composite(img, bone_arch)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── FIGURE: Maren Chalk (silhouette) standing before the arch, reading bones ──
    figures = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(figures)

    # Maren (left foreground, facing right toward the arch)
    f_cx, f_cy = arch_cx - 300, 1800
    # Head
    fd.ellipse((f_cx - 14, f_cy - 60, f_cx + 14, f_cy - 32), fill=(8, 6, 10, 230))
    # Body (cloak)
    fd.polygon(
        [
            (f_cx - 25, f_cy - 30),
            (f_cx + 20, f_cy - 28),
            (f_cx + 30, f_cy + 80),
            (f_cx - 35, f_cy + 80),
        ],
        fill=(8, 6, 10, 230),
    )
    # Arm holding a bone
    fd.line((f_cx + 18, f_cy - 15, f_cx + 55, f_cy - 50), fill=(10, 8, 12, 230), width=6)
    # The bone she holds
    fd.line((f_cx + 55, f_cy - 50, f_cx + 75, f_cy - 70), fill=BONE_DARK + (220,), width=5)
    fd.ellipse((f_cx + 50, f_cy - 55, f_cx + 60, f_cy - 45), fill=BONE_LIGHT + (220,))

    # Glow on the bone Maren holds
    for g in range(4):
        ga = int(25 * (1 - g / 4))
        gr = 25 + g * 10
        fd.ellipse(
            (f_cx + 45 - gr, f_cy - 75 - gr, f_cx + 85 + gr, f_cy - 35 + gr),
            fill=BONE_RUNES + (ga,),
        )

    # Spectral figure of Elara Humber (drowned wife) within the arch
    elara_cx, elara_cy = arch_cx + 80, 1700
    # Translucent ghostly figure
    for alpha in [15, 25, 35]:
        ed_col = COLD_WATER + (alpha,)
        ed_scale = 1.2
        fd.ellipse(
            (elara_cx - 18 * ed_scale, elara_cy - 65 * ed_scale,
             elara_cx + 18 * ed_scale, elara_cy - 35 * ed_scale),
            fill=ed_col,
        )
        fd.polygon(
            [
                (elara_cx - 30 * ed_scale, elara_cy - 33 * ed_scale),
                (elara_cx + 25 * ed_scale, elara_cy - 30 * ed_scale),
                (elara_cx + 35 * ed_scale, elara_cy + 70 * ed_scale),
                (elara_cx - 40 * ed_scale, elara_cy + 70 * ed_scale),
            ],
            fill=ed_col,
        )
        # Water drips from her
        for drip in range(3):
            dx = elara_cx + rng.randint(-15, 15)
            dy = elara_cy + rng.randint(-10, 30)
            fd.ellipse((dx - 3, dy - 3, dx + 3, dy + 3), fill=COLD_WATER + (alpha + 10,))

    elara_cx2, elara_cy2 = arch_cx - 80, 1750
    for alpha in [10, 20]:
        ed_col = COLD_WATER + (alpha,)
        fd.ellipse(
            (elara_cx2 - 15, elara_cy2 - 55, elara_cx2 + 15, elara_cy2 - 30), fill=ed_col
        )
        fd.polygon(
            [
                (elara_cx2 - 25, elara_cy2 - 28),
                (elara_cx2 + 20, elara_cy2 - 25),
                (elara_cx2 + 28, elara_cy2 + 60),
                (elara_cx2 - 30, elara_cy2 + 60),
            ],
            fill=ed_col,
        )

    img = Image.alpha_composite(img, figures)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Bone-magic ambient glow from within the arch ──
    magic_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    mgd = ImageDraw.Draw(magic_glow)
    for _ in range(6):
        gx = arch_cx + rng.randint(-250, 250)
        gy = arch_cy + rng.randint(-200, 200)
        gr = rng.randint(40, 120)
        ga = rng.randint(8, 20)
        mgd.ellipse((gx - gr, gy - gr, gx + gr, gy + gr), fill=BONE_RUNES + (ga,))
    magic_glow = magic_glow.filter(ImageFilter.GaussianBlur(20))
    img = Image.alpha_composite(img, magic_glow)

    # ── Fog layers ──
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fgd = ImageDraw.Draw(fog)
    for _ in range(8):
        fx = rng.randint(-100, W + 100)
        fy = rng.randint(800, 1800)
        fw = rng.randint(300, 700)
        fh = rng.randint(60, 150)
        fa = rng.randint(8, 22)
        fgd.ellipse((fx - fw // 2, fy, fx + fw // 2, fy + fh), fill=SMOKE + (fa,))
    fog = fog.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, fog)

    # ── Soot / particulate in the air ──
    particles = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(particles)
    for _ in range(120):
        px = rng.randint(0, W)
        py = rng.randint(0, 1700)
        pr = rng.randint(1, 3)
        pa = rng.randint(10, 40)
        pd.ellipse((px - pr, py - pr, px + pr, py + pr), fill=SMOKE + (pa,))
    img = Image.alpha_composite(img, particles)

    # ── Subtle vignette ──
    vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette)
    for vy in range(H):
        vh = 1 - gaussian(vy, H // 2, H * 0.5)
        dark = int(50 * vh)
        if dark > 0:
            vd.line((0, vy, min(dark, W), vy), fill=(0, 0, 0, 50))
            vd.line((max(W - dark, 0), vy, W, vy), fill=(0, 0, 0, 50))
    img = Image.alpha_composite(img, vignette)

    # ── Title panel via shared utility ──
    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, title, author, model)
    img.convert("RGB").save(op, "PNG", optimize=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    make_cover(
        ROOT / a.metadata if not a.metadata.is_absolute() else a.metadata,
        ROOT / a.out if not a.out.is_absolute() else a.out,
    )


if __name__ == "__main__":
    main()
