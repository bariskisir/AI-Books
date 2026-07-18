#!/usr/bin/env python3
"""Cover: The Oracle Never Blinks — split-timeline techno-thriller: CIA analyst Maya
Cross's kidnapped reality (cold left half) versus the parallel-timeline mirror-Maya's
warnings (amber right half), bisected by the Oracle's all-seeing data-stream eye,
with collapsing social-media sentiment graphs, redacted Treasury documents, and
the only alterable video file bridging two worlds."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560
DIV = 800  # timeline divider x-coordinate

rng = random.Random()
rng.seed(921836074)

# ── palette: cold-blue (timeline A) vs amber-rust (timeline B) ──────────
COLD_A = (8, 20, 42)
COLD_B = (4, 10, 22)
WARM_A = (48, 24, 8)
WARM_B = (28, 14, 4)
EYE_GREEN = (70, 225, 155)
WARN_AMBER = (245, 175, 35)
WARN_RED = (228, 38, 52)
DATA_CYAN = (55, 210, 245)
REDACT_BG = (8, 6, 10)
REDACT_BAR = (195, 30, 40)
COLD_TEXT = (80, 105, 140)
WARM_TEXT = (200, 145, 60)


def _dual_gradient(draw):
    """Parallel-timeline gradient: cold left, warm right."""
    for y in range(H):
        t = y / H
        # left half: cold steel-blue
        rl = int(COLD_A[0] + (COLD_B[0] - COLD_A[0]) * t)
        gl = int(COLD_A[1] + (COLD_B[1] - COLD_A[1]) * t)
        bl = int(COLD_A[2] + (COLD_B[2] - COLD_A[2]) * t)
        draw.line((0, y, DIV, y), fill=(rl, gl, bl, 255))
        # right half: warm amber-rust
        rr = int(WARM_A[0] + (WARM_B[0] - WARM_A[0]) * t)
        gr = int(WARM_A[1] + (WARM_B[1] - WARM_A[1]) * t)
        br = int(WARM_A[2] + (WARM_B[2] - WARM_A[2]) * t)
        draw.line((DIV, y, W, y), fill=(rr, gr, br, 255))


def _oracle_eye(draw, img):
    """The Oracle: a concentric data-ring eye at top centre, with oscilloscope
    scan-lines sweeping across a dark pupil — watching both timelines."""
    cx, cy = W // 2, 320

    # glow behind the eye
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((cx - 280, cy - 280, cx + 280, cy + 280), fill=(*EYE_GREEN, 6))
    gd.ellipse((cx - 160, cy - 160, cx + 160, cy + 160), fill=(*DATA_CYAN, 4))
    glow = glow.filter(ImageFilter.GaussianBlur(28))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # orbital data rings (outer to inner)
    for rad in range(280, 60, -24):
        a = max(4, 48 - (280 - rad) // 6)
        col = (
            rng.randint(EYE_GREEN[0] - 15, EYE_GREEN[0] + 15),
            rng.randint(EYE_GREEN[1] - 15, EYE_GREEN[1] + 15),
            rng.randint(EYE_GREEN[2] - 15, EYE_GREEN[2] + 15),
            a,
        )
        draw.ellipse((cx - rad, cy - rad, cx + rad, cy + rad),
                     outline=col, width=rng.randint(1, 2))

    # oscilloscope scan-lines
    for _ in range(80):
        ang = math.radians(rng.randint(0, 359))
        inner = 50 + rng.randint(0, 30)
        outer = 85 + rng.randint(0, 170)
        x1 = cx + math.cos(ang) * inner
        y1 = cy + math.sin(ang) * inner
        x2 = cx + math.cos(ang) * outer
        y2 = cy + math.sin(ang) * outer
        a = rng.randint(12, 55)
        col = rng.choice([EYE_GREEN, DATA_CYAN, WARN_AMBER])
        draw.line((x1, y1, x2, y2), fill=(*col, a), width=rng.randint(1, 2))

    # dark pupil
    draw.ellipse((cx - 48, cy - 48, cx + 48, cy + 48),
                 fill=(2, 4, 10, 230), outline=(*EYE_GREEN, 100), width=3)
    draw.ellipse((cx - 18, cy - 18, cx + 18, cy + 18),
                 fill=(1, 2, 5, 210))

    # glint
    draw.ellipse((cx + 8, cy - 10, cx + 16, cy - 2), fill=(*WARN_AMBER, 160))

    # horizontal data sweep through pupil
    for sy in range(cy - 38, cy + 39, 3):
        sa = max(4, 35 - abs(cy - sy) * 2)
        sw = int(130 * (1 - abs(cy - sy) / 38))
        draw.line((cx - sw, sy, cx + sw, sy),
                  fill=(*EYE_GREEN, int(sa)), width=1)

    return img


def _social_sentiment(draw):
    """Left half (Timeline A): social-media sentiment ticker tape, collapsing
    economic graph, and post fragments — Maya's predictive analytics domain."""
    # data ticker: rows of coloured blocks (sentiment pulse)
    for row in range(22):
        yb = 520 + row * 30
        for col_x in range(30, DIV - 20, 28):
            if rng.random() < 0.50:
                h = rng.randint(4, 7)
                w = rng.randint(8, 16)
                if rng.random() < 0.40:
                    col = (
                        80 + rng.randint(0, 60),
                        200 + rng.randint(0, 55),
                        120 + rng.randint(0, 40),
                        rng.randint(70, 150),
                    )
                else:
                    col = (
                        210 + rng.randint(0, 45),
                        50 + rng.randint(0, 40),
                        50 + rng.randint(0, 30),
                        rng.randint(80, 160),
                    )
                draw.rectangle((col_x, yb, col_x + w, yb + h), fill=col)

    # sentiment gauge: semicircular arc
    gx, gy = DIV // 2, 780
    for ang_deg in range(0, 181, 2):
        a = math.radians(ang_deg - 90)
        rad_outer = 70
        rad_inner = 55
        t = ang_deg / 180  # 0=left(green) to 1=right(red)
        col = (
            int(80 + (220 - 80) * t),
            int(220 + (50 - 220) * t),
            int(120 + (50 - 120) * t),
            120,
        )
        x1 = gx + math.cos(a) * rad_inner
        y1 = gy + math.sin(a) * rad_inner
        x2 = gx + math.cos(a) * rad_outer
        y2 = gy + math.sin(a) * rad_outer
        draw.line((x1, y1, x2, y2), fill=col, width=2)
    # needle pointing into red zone
    needle_ang = math.radians(110)
    draw.line((gx, gy, gx + math.cos(needle_ang) * 60,
               gy + math.sin(needle_ang) * 60),
              fill=(*WARN_RED, 180), width=2)
    draw.ellipse((gx - 6, gy - 6, gx + 6, gy + 6), fill=(*WARN_RED, 200))

    # economic collapse graph: steep plunge with oscillation
    gx0, gx1 = 50, DIV - 50
    gy0, gy1 = 980, 1180
    pts = []
    for gpx in range(gx0, gx1 + 1, 5):
        t = (gpx - gx0) / (gx1 - gx0)
        gpy = gy0 - (gy0 - gy1) * (t * 0.82 + math.sin(t * 9) * 0.10)
        gpy += rng.randint(-6, 6)
        pts.append((gpx, int(gpy)))
    draw.line(pts, fill=(*WARN_RED, 160), width=3)
    for i, (px_, py_) in enumerate(pts):
        if i % 12 == 0:
            draw.ellipse((px_ - 3, py_ - 3, px_ + 3, py_ + 3),
                         fill=(*WARN_RED, 200))

    # post fragments (social media feed)
    for _ in range(10):
        px = rng.randint(30, DIV - 100)
        py = rng.randint(540, 1550)
        pw = rng.randint(80, 180)
        ph = rng.randint(14, 22)
        draw.rectangle((px, py, px + pw, py + ph),
                       fill=(12, 16, 28, rng.randint(140, 200)),
                       outline=(*COLD_TEXT, 60), width=1)
        # avatar
        draw.ellipse((px + 4, py + 2, px + 14, py + ph - 2),
                     fill=(*DATA_CYAN, rng.randint(80, 150)))
        # username
        draw.rectangle((px + 18, py + 2, px + 18 + rng.randint(18, 45), py + 5),
                       fill=(*COLD_TEXT, rng.randint(60, 110)))
        # content
        draw.rectangle((px + 18, py + 9, px + pw - 6, py + 13),
                       fill=(*COLD_TEXT, rng.randint(40, 90)))
        # sentiment arrow
        if rng.random() < 0.55:
            draw.polygon([(px + pw - 10, py + 3), (px + pw - 3, py + 3),
                          (px + pw - 7, py + 0)], fill=(*WARN_RED, 110))
        else:
            draw.polygon([(px + pw - 10, py + 3), (px + pw - 3, py + 3),
                          (px + pw - 7, py + 6)], fill=(*EYE_GREEN, 110))

    # hashtag blocks drifting upward
    for _ in range(6):
        hx = rng.randint(30, DIV - 60)
        hy = rng.randint(300, 1400)
        for hi in range(rng.randint(3, 7)):
            draw.rectangle((hx + hi * 12, hy, hx + hi * 12 + 10, hy + 10),
                           fill=(*COLD_TEXT, rng.randint(30, 80)))


def _parallel_warning(draw):
    """Right half (Timeline B): the video file the mirror-Maya alters,
    amber warning pulses, and timeline-bleed data streams."""
    # video file frame
    vx, vy = DIV + 80, 480
    vw, vh = 320, 210
    draw.rectangle((vx, vy, vx + vw, vy + vh),
                   fill=(4, 2, 6, 240), outline=(*WARN_AMBER, 130), width=3)

    # progress bar
    pb_y = vy + vh - 26
    draw.rectangle((vx + 8, pb_y, vx + vw - 8, pb_y + 10),
                   fill=(18, 16, 22, 200), outline=(*WARN_AMBER, 50), width=1)
    fill_w = int((vw - 16) * 0.67)
    draw.rectangle((vx + 8, pb_y, vx + 8 + fill_w, pb_y + 10),
                   fill=(*WARN_AMBER, 130))

    # play triangle
    pcx = vx + vw // 2
    pcy = vy + vh // 2 - 10
    draw.polygon([(pcx - 16, pcy - 20), (pcx - 16, pcy + 20), (pcx + 22, pcy)],
                 fill=(*DATA_CYAN, rng.randint(100, 170)))

    # timecode overlay
    tc_x, tc_y = vx + vw - 86, vy + 12
    draw.rectangle((tc_x, tc_y, tc_x + 76, tc_y + 16),
                   fill=(0, 0, 0, 180), outline=(*DATA_CYAN, 70), width=1)
    for tci in range(6):
        draw.rectangle((tc_x + 4 + tci * 12, tc_y + 4,
                        tc_x + 10 + tci * 12, tc_y + 12),
                       fill=(*DATA_CYAN, rng.randint(50, 130)))

    # warning pulse rings
    for pulse in range(8):
        off = pulse * 18 + int(math.sin(rng.random() * 6.28) * 10)
        a = max(4, 45 - pulse * 6)
        draw.ellipse((vx - off, vy - off, vx + vw + off, vy + vh + off),
                     outline=(*WARN_AMBER, a), width=1)

    # amber data-bleed streams (warnings crossing from mirror timeline)
    for _ in range(20):
        sx = DIV + rng.randint(10, 680)
        sy = rng.randint(300, 1600)
        length = rng.randint(40, 200)
        angle = rng.uniform(-0.7, 0.7) + math.pi * 0.80
        ex = sx + math.cos(angle) * length
        ey = sy + math.sin(angle) * length
        a = rng.randint(18, 80)
        draw.line((sx, sy, ex, ey), fill=(*WARN_AMBER, a), width=rng.randint(1, 3))

    # fragmentary data blocks on the right (the mirror's memory)
    for _ in range(15):
        bx = DIV + rng.randint(30, 700)
        by = rng.randint(400, 1600)
        bw = rng.randint(6, 20)
        bh = rng.randint(6, 20)
        col = rng.choice([
            (*WARN_AMBER, rng.randint(40, 100)),
            (*DATA_CYAN, rng.randint(30, 80)),
            (*EYE_GREEN, rng.randint(20, 60)),
        ])
        draw.rectangle((bx, by, bx + bw, by + bh), fill=col)

    # numbered countdown fragments (the 47-second consciousness motif adapted)
    for ci in range(5):
        cn = 47 - ci * 11
        cx2 = DIV + rng.randint(300, 600)
        cy2 = rng.randint(600, 1400)
        for di in range(3):
            d_off = di * 8
            draw.rectangle((cx2 + d_off, cy2, cx2 + d_off + 6, cy2 + 11),
                           fill=(*WARN_RED, rng.randint(30, 80)))


def _redacted_fragments(draw):
    """Redacted Treasury documents and keyword fragments scattered across
    both halves — the conspiracy the Treasury faction is burying."""
    for _ in range(7):
        x = rng.randint(30, W - 220)
        y = rng.randint(900, 1650)
        w = rng.randint(140, 260)
        h = rng.randint(50, 100)
        draw.rectangle((x, y, x + w, y + h),
                       fill=(12, 10, 8, rng.randint(150, 210)),
                       outline=(50, 42, 34, 80), width=1)
        # redaction bars
        for _ in range(rng.randint(2, 3)):
            by = y + 8 + rng.randint(0, max(1, h - 20))
            bw = rng.randint(w // 3, w - 16)
            bx = x + rng.randint(6, w - bw - 6)
            draw.rectangle((bx, by, bx + bw, by + 9),
                           fill=(*REDACT_BAR, rng.randint(100, 170)))
        # unredacted text lines
        for _ in range(rng.randint(2, 4)):
            ly = y + 10 + rng.randint(0, max(1, h - 20))
            lw = rng.randint(18, w - 40)
            draw.rectangle((x + 10, ly, x + 10 + lw, ly + 3),
                           fill=(*COLD_TEXT, rng.randint(30, 70)))

    # floating keyword fragments
    kw_data = [
        (DIV - 130, 420, 6),
        (DIV + 140, 380, 5),
        (50, 1690, 7),
        (W - 150, 1720, 6),
        (DIV - 210, 1660, 8),
    ]
    for kx, ky, kc in kw_data:
        for ki in range(kc):
            col = rng.choice([COLD_TEXT, WARM_TEXT])
            draw.rectangle((kx + ki * 16, ky, kx + ki * 16 + 12, ky + 14),
                           fill=(*col, rng.randint(40, 80)))


def _divider_bleed(draw):
    """Vertical timeline divider with data-bleed sparks crossing between worlds."""
    draw.line((DIV, 0, DIV, H), fill=(*DATA_CYAN, 20), width=2)
    for _ in range(35):
        dy = rng.randint(100, 1800)
        side = -1 if rng.random() < 0.5 else 1
        sl = rng.randint(2, 8)
        sx = DIV + side * rng.randint(2, 8)
        ex = sx + side * sl
        a = rng.randint(25, 90)
        col = rng.choice([DATA_CYAN, WARN_AMBER, EYE_GREEN])
        draw.line((sx, dy, ex, dy), fill=(*col, a), width=rng.randint(1, 2))


def _surveillance_crosshairs(draw):
    """Faint intelligence-agency crosshairs and scan-line overlay."""
    # three crosshairs
    ch_pos = [
        (70, 180, WARN_RED, 35),
        (W - 70, 180, WARN_AMBER, 35),
        (DIV, 90, DATA_CYAN, 30),
    ]
    for chx, chy, col, a in ch_pos:
        arm = 22
        draw.line((chx - arm, chy, chx + arm, chy), fill=(*col, a), width=1)
        draw.line((chx, chy - arm, chx, chy + arm), fill=(*col, a), width=1)
        draw.ellipse((chx - 16, chy - 16, chx + 16, chy + 16),
                     outline=(*col, a - 10), width=1)

    # surveillance scan lines
    for sy in range(0, 1700, 4):
        if rng.random() < 0.12:
            draw.line((0, sy, W, sy), fill=(*DATA_CYAN, rng.randint(2, 6)), width=1)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (6, 10, 18, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    _dual_gradient(draw)                    # 1. split-timeline background
    img = _oracle_eye(draw, img)            # 2. central Oracle eye (returns modified img)
    draw = ImageDraw.Draw(img, "RGBA")       # refresh draw after alpha_composite
    _surveillance_crosshairs(draw)          # 3. CIA surveillance overlays
    _divider_bleed(draw)                    # 4. timeline divider with crossover
    _social_sentiment(draw)                 # 5. left half: social + economic data
    _parallel_warning(draw)                 # 6. right half: video warning + amber streams
    _redacted_fragments(draw)               # 7. redacted documents + keywords

    # vignette
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(40 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 80))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 80))

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
