#!/usr/bin/env python3
"""Cover: What the Gutter Remembers — Mumbai twilight through a rain-streaked library window, a glowing unsent letter tucked between archive shelves, paper fragments carrying half-faded words floating in the dusty air."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560
rng = random.Random("what-the-gutter-remembers-2026")


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Mumbai twilight sky gradient (dusty amber at horizon, violet above) ──
    for y in range(H):
        t = y / H
        if y < 800:
            tt = y / 800
            r = int(35 + 155 * tt)
            g = int(18 + 85 * tt)
            b = int(55 + 35 * tt)
        elif y < 1300:
            tt = (y - 800) / 500
            r = int(190 - 130 * tt)
            g = int(103 - 65 * tt)
            b = int(90 - 25 * tt)
        else:
            tt = (y - 1300) / (H - 1300)
            r = int(60 - 42 * tt)
            g = int(38 - 24 * tt)
            b = int(65 - 38 * tt)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # ── Smog-horizon haze ──────────────────────────────────────────────────
    haze = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(haze)
    hd.ellipse((-300, 650, W + 300, 1150), fill=(220, 155, 95, 40))
    hd.ellipse((200, 700, W - 200, 1100), fill=(195, 115, 75, 25))
    haze = haze.filter(ImageFilter.GaussianBlur(60))
    img = Image.alpha_composite(img, haze)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Mumbai chawl skyline silhouette ────────────────────────────────────
    skyline = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(skyline)

    buildings = []
    bx = 0
    while bx < W + 100:
        bw = rng.randint(50, 160)
        bh = rng.randint(200, 500)
        by = 1050 - bh
        sd.rectangle((bx, by, bx + bw, 1050), fill=(12, 8, 6, 230))
        # Water tank
        tw = bw * 0.4
        th = rng.randint(15, 35)
        tx = bx + (bw - tw) / 2
        sd.rectangle((tx, by - th, tx + tw, by), fill=(10, 6, 5, 240))
        sd.line((tx + 3, by, tx + 3, by + 8), fill=(8, 5, 4, 180), width=2)
        sd.line((tx + tw - 3, by, tx + tw - 3, by + 8), fill=(8, 5, 4, 180), width=2)
        for _ in range(rng.randint(1, 6)):
            wx = bx + rng.randint(8, bw - 8)
            wy = by + rng.randint(20, bh - 20)
            sd.rectangle((wx - 3, wy - 4, wx + 3, wy + 4), fill=(200, 160, 80, rng.randint(40, 120)))
        buildings.append((bx, bw, by, bh))
        bx += bw + rng.randint(-5, 15)

    # Antennae
    for bx2, bw2, by2, bh2 in buildings:
        if rng.random() < 0.4:
            ax = bx2 + rng.randint(10, bw2 - 10)
            ah = rng.randint(30, 80)
            sd.line((ax, by2, ax, by2 - ah), fill=(8, 5, 4, 180), width=1)
        if rng.random() < 0.3:
            ax1 = bx2 + rng.randint(5, bw2 - 5)
            ax2 = bx2 + rng.randint(5, bw2 - 5)
            sd.line((ax1, by2 - rng.randint(5, 15), ax2, by2 - rng.randint(5, 20)),
                    fill=(10, 7, 5, 120), width=1)

    # Distant high-rises
    for _ in range(5):
        dx = rng.randint(100, W - 100)
        dw = rng.randint(30, 60)
        dh = rng.randint(350, 600)
        dy = 1020 - dh
        sd.rectangle((dx, dy, dx + dw, 1020), fill=(25, 18, 14, 120))

    img = Image.alpha_composite(img, skyline)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Rain streaks on glass ──────────────────────────────────────────────
    rain = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rain)

    for _ in range(200):
        rx = rng.randint(0, W)
        ry = rng.randint(0, 1800)
        rlen = rng.randint(30, 120)
        ralpha = rng.randint(10, 45)
        slope = 0.3 + rng.random() * 0.35
        rd.line((rx, ry, rx + rlen * slope, ry + rlen),
                fill=(180, 192, 215, ralpha), width=rng.randint(1, 2))

    for _ in range(30):
        rx = rng.randint(0, W)
        ry = rng.randint(0, 1800)
        rlen = rng.randint(60, 200)
        ralpha = rng.randint(25, 70)
        slope = 0.25 + rng.random() * 0.3
        rd.line((rx, ry, rx + rlen * slope, ry + rlen),
                fill=(200, 210, 230, ralpha), width=rng.randint(2, 4))

    # Raindrops beaded on glass
    for _ in range(60):
        rx = rng.randint(0, W)
        ry = rng.randint(50, 1700)
        rs = rng.randint(3, 8)
        ralpha = rng.randint(30, 80)
        rd.ellipse((rx - rs, ry - rs // 2, rx + rs, ry + rs // 2),
                   fill=(190, 200, 220, ralpha))

    img = Image.alpha_composite(img, rain)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Library archive shelves receding into depth ────────────────────────
    shelves = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shd = ImageDraw.Draw(shelves)

    # Vertical posts between shelf sections
    for post_x in range(100, W - 50, rng.randint(120, 180)):
        shd.line((post_x, 800, post_x, 1800), fill=(30, 20, 15, 50), width=2)

    # Horizontal shelf planks
    for shelf_y in range(880, 1800, rng.randint(80, 120)):
        shd.line((0, shelf_y, W, shelf_y), fill=(50, 30, 18, 65), width=3)
        shd.line((0, shelf_y + 3, W, shelf_y + 3), fill=(15, 8, 5, 45), width=2)

    # Books
    for shelf_y in range(880, 1800, rng.randint(80, 120)):
        book_x = rng.randint(30, 80)
        while book_x < W - 60:
            bw = rng.randint(12, 28)
            bh = rng.randint(50, 75)
            by = shelf_y - bh + rng.randint(-5, 8)
            sr = rng.randint(40, 120)
            sg = rng.randint(25, 80)
            sb = rng.randint(20, 65)
            shd.rectangle((book_x, by, book_x + bw, by + bh),
                          fill=(sr, sg, sb, rng.randint(140, 200)))
            if rng.random() < 0.3:
                shd.line((book_x + 2, by + 12, book_x + bw - 2, by + 12),
                         fill=(180, 160, 100, rng.randint(20, 60)), width=1)
            if rng.random() < 0.15:
                lean = rng.randint(-3, 3)
                shd.rectangle((book_x + lean, by - 3, book_x + bw + lean, by + bh),
                              fill=(sr - 10, sg - 5, sb - 5, rng.randint(110, 170)))
            book_x += bw + rng.randint(3, 12)

    img = Image.alpha_composite(img, shelves)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Central glow — unsent letter tucked between books ──────────────────
    letter_cx, letter_cy = W // 2, 1320

    golden_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gg = ImageDraw.Draw(golden_glow)
    for rad in range(130, 10, -10):
        a = max(4, 55 - (130 - rad) // 2)
        gg.ellipse((letter_cx - rad, letter_cy - rad, letter_cx + rad, letter_cy + rad),
                   fill=(240, 200, 120, a))
    golden_glow = golden_glow.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, golden_glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Envelope
    letter_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(letter_layer)

    lw, lh = 160, 110
    lx, ly = letter_cx - lw // 2, letter_cy - lh // 2

    ld.rectangle((lx, ly, lx + lw, ly + lh), fill=(220, 195, 155, 230))
    ld.polygon([(lx, ly), (lx + lw // 2, ly + lh // 3), (lx + lw, ly)],
               fill=(200, 175, 135, 220))
    ld.rectangle((lx, ly, lx + lw, ly + lh), outline=(160, 130, 90, 180), width=2)

    for i in range(3):
        ly2 = ly + lh // 2 + 10 + i * 12
        lw2 = rng.randint(40, 80)
        ld.line((lx + lw - 30 - lw2, ly2, lx + lw - 30, ly2),
                fill=(100, 75, 45, rng.randint(40, 80)), width=1)

    stamp = 20
    ld.rectangle((lx + lw - stamp - 8, ly + 8, lx + lw - 8, ly + 8 + stamp),
                 fill=(180, 120, 80, 160))
    ld.rectangle((lx + lw - stamp - 8, ly + 8, lx + lw - 8, ly + 8 + stamp),
                 outline=(120, 80, 50, 180), width=1)
    ld.ellipse((lx + lw - stamp - 4, ly + 12, lx + lw - 12, ly + 12 + stamp - 8),
               fill=(200, 160, 100, 80))

    inner_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    igd = ImageDraw.Draw(inner_glow)
    igd.ellipse((letter_cx - 50, letter_cy - 30, letter_cx + 50, letter_cy + 30),
                fill=(255, 220, 150, 40))
    inner_glow = inner_glow.filter(ImageFilter.GaussianBlur(15))
    letter_layer = Image.alpha_composite(letter_layer, inner_glow)

    img = Image.alpha_composite(img, letter_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Floating paper fragments (unsent letters fluttering from the shelf) ─
    fragments = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fragments)

    # Small fragments
    for _ in range(30):
        fx = rng.randint(100, W - 100)
        fy = rng.randint(300, 1800)
        fw = rng.randint(20, 50)
        fh = rng.randint(15, 35)
        angle = rng.uniform(-0.4, 0.4)
        fac = rng.randint(60, 160)

        pts = [
            (fx, fy),
            (fx + fw, fy + fh * angle),
            (fx + fw - fh * 0.3, fy + fh + fh * angle),
            (fx - fh * 0.3, fy + fh),
        ]
        fd.polygon(pts, fill=(230, 210, 180, fac))
        fd.polygon(pts, outline=(180, 160, 130, fac), width=1)

        if rng.random() < 0.4:
            for _ in range(rng.randint(2, 5)):
                tx = fx + rng.randint(3, fw - 5)
                ty = fy + rng.randint(3, fh - 5)
                fd.line((tx, ty, tx + rng.randint(8, 18), ty),
                        fill=(120, 100, 70, rng.randint(20, 50)), width=1)

    # Larger full-page letters floating
    for _ in range(6):
        fx = rng.randint(150, W - 150)
        fy = rng.randint(400, 1600)
        fw = rng.randint(60, 90)
        fh = rng.randint(45, 65)
        fac = rng.randint(40, 100)

        pts = [
            (fx, fy),
            (fx + fw, fy + 4),
            (fx + fw - 8, fy + fh),
            (fx - 6, fy + fh - 2),
        ]
        fd.polygon(pts, fill=(235, 215, 185, fac))
        fd.polygon(pts, outline=(170, 150, 120, fac), width=1)
        for _ in range(rng.randint(3, 6)):
            lx2 = fx + rng.randint(5, fw - 15)
            ly2 = fy + rng.randint(8, fh - 8)
            lw3 = rng.randint(15, 35)
            fd.line((lx2, ly2, lx2 + lw3, ly2 + 2),
                    fill=(100, 80, 55, rng.randint(15, 40)), width=1)

    img = Image.alpha_composite(img, fragments)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Gutter/street at bottom with puddles and water reflections ────────
    gutter = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gutter)

    gd.rectangle((0, 1800, W, H), fill=(18, 14, 12, 200))

    gt_y = 1900
    for x in range(0, W, 2):
        wh = rng.randint(5, 20)
        wa = rng.randint(40, 100)
        gd.line((x, gt_y + wh, x, gt_y + wh + 15), fill=(100, 90, 120, wa))

    for _ in range(12):
        px = rng.randint(50, W - 50)
        pw = rng.randint(30, 120)
        ph = rng.randint(5, 15)
        pa = rng.randint(30, 80)
        gd.ellipse((px - pw // 2, 1920 - ph // 2, px + pw // 2, 1920 + ph // 2),
                   fill=(80, 70, 100, pa))

    for _ in range(15):
        rx = rng.randint(50, W - 50)
        ry = rng.randint(1920, 2200)
        rw2 = rng.randint(2, 6)
        rh2 = rng.randint(8, 25)
        rcol = rng.choice([(220, 120, 80), (200, 80, 60), (120, 180, 200), (240, 200, 100)])
        gd.ellipse((rx - rw2, ry, rx + rw2, ry + rh2), fill=(*rcol, rng.randint(40, 100)))

    img = Image.alpha_composite(img, gutter)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Dust motes in the archive air ──────────────────────────────────────
    for _ in range(120):
        dx = rng.randint(0, W)
        dy = rng.randint(300, 1850)
        dr = rng.randint(1, 4)
        da = rng.randint(20, 70)
        draw.ellipse((dx - dr, dy - dr, dx + dr, dy + dr),
                     fill=(240 - rng.randint(0, 30), 220 - rng.randint(0, 30), 180 - rng.randint(0, 30), da))

    # ── Warm spill glow from the letter onto surrounding scene ────────────
    warmth = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(warmth)
    wd.ellipse((letter_cx - 400, letter_cy - 300, letter_cx + 400, letter_cy + 300),
               fill=(240, 200, 120, 8))
    warmth = warmth.filter(ImageFilter.GaussianBlur(80))
    img = Image.alpha_composite(img, warmth)

    # ── Save ───────────────────────────────────────────────────────────────
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
