#!/usr/bin/env python3
"""Cover: The Rotation of Unsaid Things — In a Peruvian village where unspoken resentments physically accumulate as black sediment in the communal well, a mute woman must find words for what she knows."""

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
rng.seed(52830741)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (15, 10, 22, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 1. Night-sky gradient: deep indigo at zenith → warm earth at horizon ──
    for y in range(H):
        t = y / H
        if t < 0.5:
            lt = t / 0.5
            r = int(15 + (35 - 15) * lt)
            g = int(10 + (22 - 10) * lt)
            b = int(22 + (20 - 22) * lt)
        else:
            lt = (t - 0.5) / 0.5
            r = int(35 + (68 - 35) * lt)
            g = int(22 + (40 - 22) * lt)
            b = int(20 + (28 - 20) * lt)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── 2. Stars ──────────────────────────────────────────────────────────────
    for _ in range(200):
        sx = rng.randint(0, W)
        sy = rng.randint(0, int(H * 0.32))
        sr = rng.uniform(0.5, 2.8)
        alpha = rng.randint(50, 230)
        bri = rng.randint(210, 255)
        draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr),
                     fill=(bri, bri - 5, bri - 25, alpha))

    # ── 3. Andes mountain silhouettes (three overlapping layers) ──────────────
    for mi, (base_y, amp, col) in enumerate([
        (int(H * 0.30), 190, (20, 14, 27, 200)),
        (int(H * 0.34), 150, (30, 20, 25, 220)),
        (int(H * 0.38), 105, (42, 28, 22, 240)),
    ]):
        pts = [(0, base_y + amp + 80)]
        for x in range(0, W + 6, 6):
            n = (math.sin(x * 0.003 + mi * 2.3) * 0.5 +
                 math.sin(x * 0.008 + mi * 1.7) * 0.3 +
                 math.sin(x * 0.016 + mi * 0.9) * 0.2) * amp
            pts.append((x, base_y + amp * 0.3 - n))
        pts.extend([(W, H + 50), (0, H + 50)])
        draw.polygon(pts, fill=col)

    # ── 4. Snow-capped peak hints ─────────────────────────────────────────────
    for _ in range(4):
        px = rng.randint(250, 1350)
        py = int(H * 0.26) + rng.randint(0, 40)
        sw = rng.randint(12, 22)
        draw.polygon([
            (px - sw, py - 4), (px, py - sw * 1.2), (px + sw, py - 4),
        ], fill=(rng.randint(190, 225), rng.randint(180, 215),
                 rng.randint(170, 195), rng.randint(100, 170)))

    # ── 5. Terraced village on the mountainside ───────────────────────────────
    terrace_y = int(H * 0.40)
    for ti in range(4):
        ty = terrace_y + ti * 90
        for _ in range(rng.randint(5, 9)):
            bx = rng.randint(40, W - 40)
            bw = rng.randint(18, 44)
            bh = rng.randint(22, 48)
            # Adobe wall
            wr_ = rng.randint(72, 108)
            wg_ = rng.randint(52, 76)
            wb_ = rng.randint(32, 48)
            draw.rectangle((bx, ty - bh, bx + bw, ty), fill=(wr_, wg_, wb_, 235))
            # Thatched roof
            rt = ty - bh - rng.randint(8, 15)
            draw.polygon([(bx - 4, ty - bh), (bx + bw // 2, rt), (bx + bw + 4, ty - bh)],
                         fill=(rng.randint(52, 78), rng.randint(32, 52), rng.randint(18, 28), 245))
            # Warm window glow
            if rng.random() < 0.45:
                wx0 = bx + rng.randint(4, max(4, bw // 5))
                wx1 = bx + bw - rng.randint(4, max(4, bw // 5))
                wy0 = ty - bh + rng.randint(6, 14)
                wy1 = wy0 + rng.randint(8, 16)
                draw.rectangle((wx0, wy0, wx1, wy1),
                               fill=(rng.randint(200, 245), rng.randint(155, 205),
                                     rng.randint(55, 105), rng.randint(80, 180)))

    # ── 6. Stone well — focal point, slightly left of centre ─────────────────
    wx, wy = W // 2 - 80, int(H * 0.56)
    wr_well = 155

    # Shadow / ground base
    draw.ellipse((wx - wr_well - 40, wy - 22, wx + wr_well + 40, wy + 35),
                 fill=(28, 22, 18, 245))

    # Stone body — concentric layers for depth
    for li in range(6):
        frac = li / 5
        lr = wr_well - li * 7
        ly = wy - 22 + li * 8
        sr_ = int(80 - frac * 35)
        sg_ = int(72 - frac * 32)
        sb_ = int(60 - frac * 28)
        draw.ellipse((wx - lr, ly - lr, wx + lr, ly + lr), fill=(sr_, sg_, sb_, 235))

    # Individual rim stones
    for si in range(22):
        ang = si * math.tau / 22 + rng.uniform(-0.04, 0.04)
        sr = wr_well + 5
        sx_ = wx + math.cos(ang) * sr
        sy_ = wy - 22 + math.sin(ang) * sr
        sw_ = rng.randint(14, 26)
        sc = (rng.randint(68, 105), rng.randint(60, 90), rng.randint(50, 75))
        draw.ellipse((sx_ - sw_ // 2, sy_ - sw_ // 2, sx_ + sw_ // 2, sy_ + sw_ // 2),
                     fill=(*sc, 235))

    # Dark opening
    draw.ellipse((wx - wr_well + 30, wy - wr_well + 8, wx + wr_well - 30, wy + wr_well + 8),
                 fill=(8, 5, 8, 255))
    draw.ellipse((wx - wr_well + 60, wy - wr_well + 38, wx + wr_well - 60, wy + wr_well + 38),
                 fill=(3, 2, 5, 255))

    # ── 7. Black sediment rising in thick tendrils ────────────────────────────
    for ti in range(12):
        ang = rng.uniform(0, math.tau)
        start_r = rng.randint(15, wr_well - 25)
        sx_ = max(wx - wr_well + 32, min(wx + wr_well - 32, wx + math.cos(ang) * start_r))
        sy_ = max(wy - 12, min(wy + 12, wy + math.sin(ang) * (start_r * 0.3)))

        pts = [(sx_, sy_)]
        for step in range(1, 55):
            t = step * 7
            wave_x = math.sin(t * 0.007 + ti * 2.5) * t * 0.16
            wave_y = math.cos(t * 0.011 + ti * 1.8) * t * 0.05
            cx = sx_ + wave_x + rng.uniform(-2, 2)
            cy = sy_ - t + wave_y
            pts.append((cx, cy))
            if cy < H * 0.10:
                break

        for pi in range(len(pts) - 1):
            fade = 1 - pi / len(pts)
            alpha = int(180 * fade)
            w = max(1, int(12 * fade))
            pc = (int(10 + (1 - fade) * 10), int(8 + (1 - fade) * 6), int(5 + (1 - fade) * 4))
            draw.line((pts[pi], pts[pi + 1]), fill=(*pc, alpha), width=w)

    # ── 8. Floating sediment particles ────────────────────────────────────────
    for _ in range(rng.randint(120, 180)):
        px_ = wx + rng.randint(-wr_well - 60, wr_well + 60)
        py_ = wy - rng.randint(0, int(H * 0.45))
        pr_ = rng.uniform(1.5, 6.5)
        pa_ = rng.randint(25, 140)
        pd_ = rng.randint(8, 22)
        draw.ellipse((px_ - pr_, py_ - pr_, px_ + pr_, py_ + pr_),
                     fill=(pd_, pd_ - 3, pd_ - 6, pa_))

    # ── 9. Quilla Tupac silhouetted figure ────────────────────────────────────
    qx = wx + wr_well + 95
    qy = wy + 45

    # Head
    draw.ellipse((qx - 18, qy - 42, qx + 18, qy), fill=(14, 10, 18, 245))
    # Torso
    draw.polygon([(qx - 22, qy), (qx + 22, qy),
                  (qx + 18, qy + 88), (qx - 18, qy + 88)],
                 fill=(14, 10, 18, 245))
    # Pollera (traditional wide skirt)
    draw.polygon([(qx - 24, qy + 88), (qx + 24, qy + 88),
                  (qx + 55, qy + 240), (qx - 55, qy + 240)],
                 fill=(17, 12, 22, 245))
    # Arm reaching toward the well
    draw.line((qx - 20, qy + 22, qx - 100, qy + 16),
              fill=(14, 10, 18, 235), width=10)
    # Open hand
    draw.ellipse((qx - 107, qy + 8, qx - 93, qy + 24),
                 fill=(14, 10, 18, 235))

    # ── 10. Folk-magic chacana crosses on the ground ──────────────────────────
    for si in range(6):
        ang = si * math.tau / 6 + 0.3
        sx_ = wx + math.cos(ang) * (wr_well + 55)
        sy_ = wy + 18 + math.sin(ang) * 14
        cr = 11
        col = (rng.randint(140, 185), rng.randint(45, 80), rng.randint(25, 55))
        draw.ellipse((sx_ - cr, sy_ - cr, sx_ + cr, sy_ + cr),
                     outline=(*col, 160), width=2)
        draw.line((sx_ - cr - 5, sy_, sx_ + cr + 5, sy_),
                  fill=(*col, 140), width=2)
        draw.line((sx_, sy_ - cr - 5, sx_, sy_ + cr + 5),
                  fill=(*col, 140), width=2)
        for da in (0, math.pi / 2, math.pi, 3 * math.pi / 2):
            dx_ = sx_ + math.cos(da) * (cr + 8)
            dy_ = sy_ + math.sin(da) * (cr + 8)
            draw.ellipse((dx_ - 2.5, dy_ - 2.5, dx_ + 2.5, dy_ + 2.5),
                         fill=(*col, 190))

    # ── 11. Ambient glow pool around the well ────────────────────────────────
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((wx - wr_well - 90, wy - wr_well - 320, wx + wr_well + 90, wy + 90),
               fill=(rng.randint(18, 28), rng.randint(12, 20), rng.randint(32, 42), 14))
    glow = glow.filter(ImageFilter.GaussianBlur(45))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 12. Sediment drips from the well rim ─────────────────────────────────
    for di in range(rng.randint(8, 12)):
        ang = rng.uniform(-0.4, 0.4) + math.pi / 2
        dx_ = wx + math.cos(ang) * (wr_well - 12)
        dy_ = wy + math.sin(ang) * (wr_well - 12) + 8
        dl_ = rng.randint(12, 40)
        dw_ = rng.randint(2, 6)
        da_ = rng.randint(100, 180)
        draw.line((dx_, dy_, dx_, dy_ + dl_),
                  fill=(rng.randint(8, 16), rng.randint(6, 12), rng.randint(5, 10), da_),
                  width=dw_)
        draw.ellipse((dx_ - dw_, dy_ + dl_ - 2, dx_ + dw_, dy_ + dl_ + 4),
                     fill=(rng.randint(8, 16), rng.randint(6, 12), rng.randint(5, 10), da_ + 20))

    # ── Save ──────────────────────────────────────────────────────────────────
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
