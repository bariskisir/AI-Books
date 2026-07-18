#!/usr/bin/env python3
"""Cover: The Ledger of Seven Crossings — A retired archivist inherits a 19th-century lending library ledger with seven borrower names crossed out in blood; tracing each name reveals an unsolved murder tied to a secret society, and the seventh name belongs to the archivist herself, dated 1872."""

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
rng.seed(18721872)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    # ── Base: dark brown wooden desk surface ────────────────────────
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        r = int(28 + 35 * t)
        g = int(18 + 22 * t)
        b = int(10 + 12 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── Candle glow from bottom-right corner ────────────────────────
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for radius in range(200, 800, 60):
        cx, cy = W - 180, H - 500
        gd.ellipse((cx - radius, cy - radius, cx + radius, cy + radius),
                   fill=(255, 200, 120, max(0, 14 - radius // 60)))
    glow = glow.filter(ImageFilter.GaussianBlur(50))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Open ledger pages ──────────────────────────────────────────
    page_w, page_h = 560, 800
    spine_x = W // 2
    page_y = 380
    left_x = spine_x - page_w - 6
    right_x = spine_x + 6

    # Shadow under ledger
    shdw = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shdw)
    sd.rectangle((left_x - 30, page_y - 15, right_x + page_w + 30, page_y + page_h + 25),
                 fill=(0, 0, 0, 140))
    shdw = shdw.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(img, shdw)
    draw = ImageDraw.Draw(img, "RGBA")

    # Aged page cream
    page_base = (225, 212, 185)

    # Left page
    draw.rectangle((left_x, page_y, left_x + page_w, page_y + page_h), fill=page_base)
    # Right page
    draw.rectangle((right_x, page_y, right_x + page_w, page_y + page_h), fill=page_base)

    # Spine binding
    draw.rectangle((left_x + page_w - 4, page_y + 30, right_x + 4, page_y + page_h - 30),
                   fill=(75, 55, 35))
    draw.rectangle((spine_x - 9, page_y + 20, spine_x + 9, page_y + page_h - 20),
                   fill=(50, 35, 20))

    # Page-edge shadows near spine
    for i in range(25):
        a = 35 - i
        if a > 0:
            draw.line((left_x + page_w - i, page_y + 40, left_x + page_w - i, page_y + page_h - 40),
                      fill=(130, 110, 80, a))
            draw.line((right_x + i, page_y + 40, right_x + i, page_y + page_h - 40),
                      fill=(130, 110, 80, a))

    # ── Faint body text on left page (illegible filler lines) ─────
    for _ in range(60):
        tx = left_x + 35 + rng.randint(0, 40)
        ty = page_y + 60 + rng.randint(0, page_h - 120)
        line_w = rng.randint(60, 150)
        ink = (55 + rng.randint(-5, 10), 50 + rng.randint(-5, 10), 45 + rng.randint(-5, 10), rng.randint(30, 70))
        for sx in range(0, line_w, rng.randint(8, 16)):
            up = rng.randint(-2, 2)
            draw.line((tx + sx, ty + up, tx + sx + rng.randint(4, 10), ty + up + rng.randint(-1, 2)),
                      fill=ink, width=1)

    # ── Column header on right page ────────────────────────────────
    col_x = right_x + 45
    header_ink = (40, 35, 30, 180)
    draw.text((col_x, page_y + 55), "LEDGER OF SEVEN CROSSINGS", fill=header_ink)
    draw.text((col_x, page_y + 78), "Lending Library — Borough of Whitmore", fill=(50, 45, 40, 120))
    draw.line((col_x, page_y + 95, col_x + 400, page_y + 95), fill=(60, 50, 40, 80), width=1)

    # ── Seven borrower entries ─────────────────────────────────────
    name_start_y = page_y + 115
    name_data = [
        ("Amos Blackwood", "Mar 3, 1872", True),
        ("Eleanor Crane",   "Apr 11, 1872", True),
        ("Thomas Webb",     "May 19, 1872", True),
        ("Lydia Parrish",   "Jun 7, 1872",  True),
        ("Jonah Hale",      "Jul 22, 1872", True),
        ("Constance Whitlock", "Aug 4, 1872", True),
        ("Frances Tewksbury", "Sep 15, 1872", False),
    ]

    for i, (n, d, crossed) in enumerate(name_data):
        ny = name_start_y + i * 88
        ink = (50, 45, 40, 200)

        # Print name
        name_x = col_x
        draw.text((name_x, ny), n, fill=ink)

        # Print date
        draw.text((col_x + 280, ny + 2), d, fill=(55, 50, 45, 140))

        if crossed:
            # Jagged blood-red crossing
            bx_start = col_x - 8
            bx_end = col_x + 180
            by = ny + 14
            pts = [(bx_start, by + rng.randint(-4, 4))]
            for px in range(bx_start + 8, bx_end, 10):
                pts.append((px, by + rng.randint(-7, 7)))
            pts.append((bx_end, by + rng.randint(-4, 4)))

            # Multiple overlapping strokes for dried-blood look
            for w in range(2, 6):
                bc = (110 + rng.randint(0, 15), 12 + rng.randint(0, 8), 12 + rng.randint(0, 8), 130 + rng.randint(0, 30))
                shifted = [(p[0], p[1] + rng.randint(-2, 2)) for p in pts]
                draw.line(shifted, fill=bc, width=w)

            # Blood splatter dots
            for _ in range(rng.randint(4, 10)):
                sx = col_x + rng.randint(0, 180)
                sy = ny + rng.randint(-15, 20)
                sr = rng.randint(1, 4)
                draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr),
                             fill=(120 + rng.randint(0, 15), 10 + rng.randint(0, 8), 10 + rng.randint(0, 8), 110 + rng.randint(0, 30)))
        else:
            # The seventh name is uncrossed — subtle red underline
            draw.line((col_x, ny + 22, col_x + 175, ny + 22), fill=(90, 15, 15, 80), width=1)
            draw.text((col_x + 185, ny - 2), "*", fill=(90, 15, 15, 120))

    # ── Circular library stamp ─────────────────────────────────────
    stamp_cx = right_x + page_w - 140
    stamp_cy = page_y + page_h - 110
    sc = (130, 115, 95, 55)
    draw.ellipse((stamp_cx - 55, stamp_cy - 55, stamp_cx + 55, stamp_cy + 55), outline=sc, width=3)
    draw.ellipse((stamp_cx - 45, stamp_cy - 45, stamp_cx + 45, stamp_cy + 45), outline=sc, width=1)
    draw.text((stamp_cx - 25, stamp_cy - 10), "WHITMORE", fill=sc)
    draw.text((stamp_cx - 20, stamp_cy + 6), "ARCHIVE", fill=sc)

    # ── Secret society watermark (faint embossed seal) ─────────────
    wm_cx = left_x + 200
    wm_cy = page_y + page_h - 120
    wc = (100, 85, 65, 25)
    # Outer ring
    draw.ellipse((wm_cx - 40, wm_cy - 40, wm_cx + 40, wm_cy + 40), outline=wc, width=2)
    # Seven-pointed star
    for p in range(7):
        a1 = math.tau * p / 7 - math.pi / 2
        a2 = math.tau * (p + 1) / 7 - math.pi / 2
        draw.line((wm_cx + 28 * math.cos(a1), wm_cy + 28 * math.sin(a1),
                   wm_cx + 28 * math.cos(a2), wm_cy + 28 * math.sin(a2)), fill=wc, width=1)
    # Inner key-like symbol
    draw.line((wm_cx, wm_cy - 15, wm_cx, wm_cy + 15), fill=wc, width=1)
    draw.ellipse((wm_cx - 6, wm_cy - 8, wm_cx + 6, wm_cy + 2), outline=wc, width=1)

    # ── Age spots on both pages ────────────────────────────────────
    for page_origin_x in (left_x, right_x):
        for _ in range(rng.randint(25, 50)):
            sx = page_origin_x + rng.randint(20, page_w - 20)
            sy = page_y + rng.randint(20, page_h - 20)
            sr = rng.randint(2, 7)
            sa = rng.randint(8, 35)
            draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=(170, 155, 125, sa))

    # ── Subtle vignette ────────────────────────────────────────────
    vg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vg)
    for vy in range(H):
        vt = 1 - abs(vy - H//2) / (H//2)
        vv = int(50 * max(0, 1 - vt))
        if vv > 0:
            vd.line((0, vy, vv, vy), fill=(0, 0, 0, 70))
            vd.line((W - vv, vy, W, vy), fill=(0, 0, 0, 70))
    vg = vg.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img, vg)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Save ───────────────────────────────────────────────────────
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
