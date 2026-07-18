#!/usr/bin/env python3
"""Cover: The Signal Through Static — Radio astronomer Lena Voss at the remote Atacama observatory detects a structured pattern hidden in the cosmic microwave background — the oldest light in the universe carries a signal, repeating every 47 million years."""

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
rng.seed(47000000)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (5, 3, 20, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # 1. Cosmic gradient: deep space (top) to Atacama desert tones (below horizon)
    for y in range(H):
        t = y / H
        if t < 0.55:
            rt = t / 0.55
            r = int(5 + 8 * rt)
            g = int(3 + 6 * rt)
            b = int(25 + 25 * rt)
        elif t < 0.67:
            rt = (t - 0.55) / 0.12
            r = int(13 + 35 * rt)
            g = int(9 + 22 * rt)
            b = int(50 + 5 * rt)
        else:
            rt = (t - 0.67) / 0.33
            r = int(48 + 45 * rt)
            g = int(31 + 30 * rt)
            b = int(55 + 5 * rt)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # 2. Cosmic microwave background all-sky anisotropy (Planck-map style)
    cmb_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cmb_draw = ImageDraw.Draw(cmb_layer)
    for _ in range(80):
        cx = rng.randint(0, W)
        cy = rng.randint(0, int(H * 0.6))
        rad = rng.randint(60, 200)
        if rng.random() < 0.45:
            col = (200, 155, 80, rng.randint(4, 14))
        else:
            col = (70, 100, 200, rng.randint(4, 12))
        cmb_draw.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=col)
    for _ in range(120):
        cx = rng.randint(0, W)
        cy = rng.randint(0, int(H * 0.6))
        rad = rng.randint(20, 60)
        if rng.random() < 0.5:
            col = (220, 170, 90, rng.randint(3, 10))
        else:
            col = (60, 90, 200, rng.randint(3, 8))
        cmb_draw.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=col)
    cmb_layer = cmb_layer.filter(ImageFilter.GaussianBlur(25))
    img = Image.alpha_composite(img, cmb_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # 3. Static noise field — thousands of tiny particles representing raw static
    static_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    static_draw = ImageDraw.Draw(static_layer)
    for _ in range(3500):
        sx = rng.randint(0, W)
        sy = rng.randint(0, int(H * 0.72))
        sr = rng.uniform(0.5, 2.0)
        sa = rng.randint(15, 80)
        static_draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=(180, 190, 200, sa))
    img = Image.alpha_composite(img, static_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # 4. Atacama mountain ridge silhouettes
    mount_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    mount_draw = ImageDraw.Draw(mount_layer)
    base_y = 1620
    for mi in range(5):
        mx = rng.randint(100, W - 100)
        py = rng.randint(1460, 1560)
        pts = [(0, base_y + 20)]
        for sx in range(0, W + 1, max(1, W // rng.randint(10, 14))):
            dr = abs(sx - mx) / max(W, 1)
            ns = rng.randint(-20, 20)
            seg_y = py + dr * (base_y - py) + ns
            pts.append((sx, seg_y))
        pts.append((W, base_y + 20))
        mc = (max(3, 20 - mi * 3), max(3, 18 - mi * 3), max(3, 30 - mi * 3))
        mount_draw.polygon(pts, fill=(*mc, 230))
    img = Image.alpha_composite(img, mount_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # 5. ALMA-style radio telescope dish on the right side
    dish_cx, dish_cy = 1100, 1220
    dish_rx, dish_ry = 300, 170
    draw.ellipse(
        (dish_cx - dish_rx, dish_cy - dish_ry, dish_cx + dish_rx, dish_cy + dish_ry),
        fill=(12, 10, 15, 220),
        outline=(25, 22, 30, 200),
        width=3,
    )
    for ring_t in (0.7, 0.4):
        draw.ellipse(
            (dish_cx - dish_rx * ring_t, dish_cy - dish_ry * ring_t,
             dish_cx + dish_rx * ring_t, dish_cy + dish_ry * ring_t),
            outline=(35, 30, 40, 120),
            width=1,
        )
    for ang_deg in range(0, 360, 45):
        ang = math.radians(ang_deg)
        ex = dish_cx + math.cos(ang) * dish_rx
        ey = dish_cy + math.sin(ang) * dish_ry
        ix = dish_cx + math.cos(ang) * dish_rx * 0.15
        iy = dish_cy + math.sin(ang) * dish_ry * 0.15
        draw.line((ex, ey, ix, iy), fill=(35, 30, 40, 140), width=2)
    focal_x, focal_y = dish_cx, dish_cy - dish_ry - 70
    draw.rectangle(
        (focal_x - 12, focal_y - 18, focal_x + 12, focal_y + 12),
        fill=(20, 18, 25, 230),
    )
    for ang_deg in (210, 330):
        ang = math.radians(ang_deg)
        lx = dish_cx + math.cos(ang) * dish_rx * 0.7
        ly = dish_cy + math.sin(ang) * dish_ry * 0.7
        draw.line((focal_x, focal_y + 8, lx, ly), fill=(25, 22, 30, 180), width=3)
    tw = 25
    draw.rectangle(
        (dish_cx - tw, dish_cy + dish_ry, dish_cx + tw, dish_cy + dish_ry + 150),
        fill=(10, 8, 15, 220),
    )

    # 6. The Signal — structured waveform emerging from the receiver, arcing across the sky
    sig_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sig_draw = ImageDraw.Draw(sig_layer)
    sig_pts = []
    for ti in range(101):
        t = ti / 100
        bx = focal_x - t * 700 + math.sin(t * math.pi * 2.5) * 100
        by = focal_y - t * 1200 - math.sin(t * math.pi * 1.7) * 70
        sig_pts.append((bx, by))
    for w in range(8, 0, -1):
        sig_draw.line(sig_pts, fill=(80, 200, 255, 10 + (8 - w) * 6), width=w * 3)
    for ti in range(0, 101, 4):
        t = ti / 100
        bx = focal_x - t * 700 + math.sin(t * math.pi * 2.5) * 100
        by = focal_y - t * 1200 - math.sin(t * math.pi * 1.7) * 70
        ps = 5 + math.sin(t * math.pi * 8) * 3
        pa = int(180 * (1 - t * 0.6))
        sig_draw.ellipse((bx - ps, by - ps, bx + ps, by + ps), fill=(100, 220, 255, pa))
    for _ in range(100):
        t = rng.random()
        bx = focal_x - t * 700 + math.sin(t * math.pi * 2.5) * 100 + rng.uniform(-25, 25)
        by = focal_y - t * 1200 - math.sin(t * math.pi * 1.7) * 70 + rng.uniform(-20, 20)
        sr = rng.uniform(1.5, 4.5)
        sa = rng.randint(100, 200)
        sig_draw.ellipse((bx - sr, by - sr, bx + sr, by + sr), fill=(120, 230, 255, sa))
    sig_glow = sig_layer.filter(ImageFilter.GaussianBlur(12))
    img = Image.alpha_composite(img, sig_glow)
    img = Image.alpha_composite(img, sig_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # 7. Observatory domes on distant ridge with faint light pollution
    dome_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dome_draw = ImageDraw.Draw(dome_layer)
    dy = 1590
    for dx_pos in (200, 350, 500, 1300, 1400):
        dome_draw.ellipse((dx_pos - 18, dy - 12, dx_pos + 18, dy + 5), fill=(8, 6, 12, 200))
        dome_draw.rectangle((dx_pos - 12, dy + 5, dx_pos + 12, dy + 18), fill=(8, 6, 12, 200))
    dome_draw.ellipse((100, 1550, 600, 1630), fill=(180, 120, 60, 6))
    dome_draw.ellipse((1000, 1550, 1500, 1630), fill=(180, 120, 60, 4))
    dome_layer = dome_layer.filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(img, dome_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # 8. Spectrogram / radio frequency readout along the horizon
    spec_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    spec_draw = ImageDraw.Draw(spec_layer)
    spec_y = 1640
    for x in range(0, W, 2):
        val = math.sin(x * 0.025) * 4 + math.sin(x * 0.06) * 2.5 + rng.uniform(-1.2, 1.2)
        ly = spec_y + val
        spec_draw.line((x, ly, x + 1, ly + 1), fill=(80, 200, 255, 50), width=1)
    spike_x = 800
    for dx in range(-40, 41):
        sh = max(0, 25 - abs(dx) * 0.4)
        spec_draw.line(
            (spike_x + dx, spec_y - sh, spike_x + dx, spec_y + 1),
            fill=(100, 220, 255, int(60 + (1 - abs(dx) / 40) * 60)),
            width=2,
        )
    img = Image.alpha_composite(img, spec_layer)

    # 9. Save with standard bottom title panel
    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, title, author, model)
    img.convert("RGB").save(op, "PNG", optimize=True)
    print(f"Cover saved to {op}")


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
