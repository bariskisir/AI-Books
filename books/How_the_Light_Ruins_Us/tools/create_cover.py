#!/usr/bin/env python3
"""Cover: How the Light Ruins Us — lighthouse, ghost, shipwreck, and a photographer's aperture on Ireland's storm-western coast."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    # ── Base: deep charcoal night sky ───────────────────────────────────────
    img = Image.new("RGBA", (W, H), (22, 28, 40, 255))

    # ── Storm sky: steel-to-charcoal gradient ────────────────────────────────
    for y in range(H):
        t = y / H
        r = int(22 + (10 - 22) * t)
        g = int(28 + (12 - 28) * t)
        b = int(40 + (18 - 40) * t)
        draw = ImageDraw.Draw(img, "RGBA")
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── Storm clouds (blurred elliptical banks) ──────────────────────────────
    clouds = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(clouds)
    for _ in range(10):
        cx = random.randint(0, W)
        cy = random.randint(40, 850)
        cw = random.randint(300, 700)
        ch = random.randint(80, 200)
        cd.ellipse(
            (cx - cw // 2, cy - ch // 2, cx + cw // 2, cy + ch // 2),
            fill=(random.randint(15, 35), random.randint(18, 40), random.randint(25, 50), random.randint(120, 200)),
        )
    for _ in range(6):
        cx = random.randint(0, W)
        cy = random.randint(80, 800)
        cw = random.randint(200, 500)
        ch = random.randint(50, 120)
        cd.ellipse(
            (cx - cw // 2, cy - ch // 2, cx + cw // 2, cy + ch // 2),
            fill=(random.randint(60, 90), random.randint(65, 95), random.randint(80, 110), random.randint(40, 80)),
        )
    clouds = clouds.filter(ImageFilter.GaussianBlur(35))
    img = Image.alpha_composite(img, clouds)

    # ── Cliff face (jagged right-side palisade) ──────────────────────────────
    cliff = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cld = ImageDraw.Draw(cliff)
    cliff_pts = [(W, 680)]
    for x in range(W, 500, -random.randint(20, 40)):
        y_off = 680 + (W - x) * 1.3 + random.randint(-35, 35)
        cliff_pts.append((x, int(y_off)))
    cliff_pts.append((500, H))
    cliff_pts.append((W, H))
    cld.polygon(cliff_pts, fill=(random.randint(18, 30), random.randint(18, 28), random.randint(22, 35), 235))
    for _ in range(35):
        rx = random.randint(550, W)
        ry = random.randint(800, H - 200)
        rs = random.randint(10, 45)
        alpha = random.randint(30, 80)
        cld.rectangle((rx, ry, rx + rs, ry + rs // 2), fill=(random.randint(35, 50), random.randint(35, 48), random.randint(40, 55), alpha))
    img = Image.alpha_composite(img, cliff)

    # ── Lighthouse (tapered tower, red stripes, lantern) ─────────────────────
    lhx, lhy = W - 360, 650
    lh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lh)
    ld.polygon(
        [(lhx - 28, lhy), (lhx + 28, lhy), (lhx + 16, lhy - 250), (lhx - 16, lhy - 250)],
        fill=(60, 58, 55, 240),
    )
    # Red bands
    for y0, y1 in [(lhy - 60, lhy - 30), (lhy - 130, lhy - 100), (lhy - 200, lhy - 170)]:
        ld.polygon(
            [
                (lhx - 24 + (lhy - y0) * 0.04, y0),
                (lhx + 24 - (lhy - y0) * 0.04, y0),
                (lhx + 26 - (lhy - y1) * 0.04, y1),
                (lhx - 26 + (lhy - y1) * 0.04, y1),
            ],
            fill=(160, 40, 40, 220),
        )
    # Lantern room
    ld.rectangle((lhx - 20, lhy - 290, lhx + 20, lhy - 250), fill=(50, 48, 45, 240))
    ld.polygon(
        [(lhx - 18, lhy - 290), (lhx + 18, lhy - 290), (lhx + 22, lhy - 310), (lhx - 22, lhy - 310)],
        fill=(50, 48, 45, 240),
    )
    # Glowing glass
    ld.rectangle((lhx - 16, lhy - 285, lhx - 4, lhy - 258), fill=(255, 220, 150, 180))
    ld.rectangle((lhx + 4, lhy - 285, lhx + 16, lhy - 258), fill=(255, 220, 150, 180))
    # Dome roof
    ld.ellipse((lhx - 24, lhy - 340, lhx + 24, lhy - 308), fill=(55, 55, 50, 240))
    ld.ellipse((lhx - 6, lhy - 330, lhx + 6, lhy - 318), fill=(255, 235, 180, 200))
    # Gallery platform
    ld.rectangle((lhx - 30, lhy - 255, lhx + 30, lhy - 248), fill=(45, 45, 42, 240))
    img = Image.alpha_composite(img, lh)

    # ── Light beam (wide triangular sweep cutting the storm) ────────────────
    beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam)
    ox, oy = lhx, lhy - 290
    # Wide faint beam
    bd.polygon(
        [(ox, oy), (ox - 350, oy + 600), (ox + 1000, oy + 250)],
        fill=(255, 220, 140, 12),
    )
    # Narrower brighter core
    bd.polygon(
        [(ox, oy), (ox - 180, oy + 450), (ox + 700, oy + 150)],
        fill=(255, 235, 180, 22),
    )
    # Hot center
    bd.polygon(
        [(ox, oy), (ox - 80, oy + 300), (ox + 400, oy + 80)],
        fill=(255, 245, 210, 18),
    )
    # Floating motes in the beam
    for _ in range(8):
        fx = ox + random.randint(-80, 500)
        fy = oy + random.randint(40, 350)
        fr = random.randint(6, 30)
        bd.ellipse((fx - fr, fy - fr, fx + fr, fy + fr), fill=(255, 240, 200, random.randint(4, 12)))
    beam = beam.filter(ImageFilter.GaussianBlur(14))
    img = Image.alpha_composite(img, beam)

    # ── Ocean surface ────────────────────────────────────────────────────────
    ocean_top = 950
    sea = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sea)
    for y in range(ocean_top, H, 2):
        t = (y - ocean_top) / (H - ocean_top)
        r = int(10 + (8 - 10) * t)
        g = int(20 + (12 - 20) * t)
        b = int(38 + (20 - 38) * t)
        sd.line((0, y, W, y), fill=(r, g, b, min(200, int(120 + t * 80))))

    # Wave crests (whitecaps)
    for _ in range(50):
        wx = random.randint(0, W)
        wy = random.randint(ocean_top, H - 100)
        wlen = random.randint(15, 60)
        crest = [(wx + dx, wy + int(math.sin(dx * 0.5 + random.uniform(0, 1)) * 3)) for dx in range(wlen)]
        sd.line(
            crest,
            fill=(random.randint(180, 230), random.randint(190, 235), random.randint(200, 245), random.randint(40, 100)),
            width=random.randint(1, 3),
        )

    # Rolling swell lines
    for _ in range(6):
        wx = random.randint(50, W - 50)
        wy = random.randint(ocean_top, 1350)
        wa = random.randint(8, 14)
        swell = [(wx + dx, wy + int(wa * math.cos(dx * 0.045))) for dx in range(-70, 71)]
        sd.line(
            swell,
            fill=(random.randint(25, 40), random.randint(35, 55), random.randint(55, 75), random.randint(50, 90)),
            width=random.randint(3, 6),
        )

    # Foam where waves meet cliff
    for _ in range(12):
        fx = random.randint(520, W - 10)
        fy = random.randint(ocean_top, 1400)
        fe = random.randint(10, 35)
        sd.ellipse((fx - fe, fy - fe // 2, fx + fe, fy + fe // 2), fill=(190, 210, 230, random.randint(20, 50)))
    img = Image.alpha_composite(img, sea)

    # ── Shipwreck debris (broken timbers, rusted hoop) ──────────────────────
    wreck = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wreck)
    for _ in range(8):
        rx = random.randint(100, W - 100)
        ry = random.randint(1180, 1580)
        rw = random.randint(40, 130)
        rh = random.randint(8, 16)
        angle = random.uniform(-0.35, 0.35)
        pts = []
        for i in range(4):
            a = angle * (i if i < 2 else (3 - i))
            pts.append((
                rx + (rw // 2 if i in (1, 2) else -rw // 2) * math.cos(a),
                ry + (rh // 2 if i in (2, 3) else -rh // 2) * math.sin(a),
            ))
        wd.polygon(pts, fill=(random.randint(30, 50), random.randint(25, 45), random.randint(20, 35), random.randint(160, 220)))

    # Rusted hoop / barrel ring
    for _ in range(3):
        rx = random.randint(100, W - 100)
        ry = random.randint(1250, 1520)
        rr = random.randint(15, 35)
        wd.ellipse((rx - rr, ry - rr // 3, rx + rr, ry + rr // 3), outline=(random.randint(80, 100), random.randint(40, 60), random.randint(30, 45), 150), width=2)

    # Jagged vertical spars
    for _ in range(5):
        rx = random.randint(100, W - 100)
        ry = random.randint(1280, 1550)
        rh = random.randint(50, 120)
        wd.rectangle((rx - 3, ry - rh, rx + 3, ry), fill=(random.randint(35, 55), random.randint(30, 48), random.randint(25, 40), 200))
        if random.random() < 0.4:
            wd.line((rx, ry - rh, rx + random.randint(10, 30), ry - rh - random.randint(5, 15)), fill=(random.randint(35, 55), random.randint(30, 48), random.randint(25, 40), 180), width=2)
    img = Image.alpha_composite(img, wreck)

    # ── Ghostly figure of Padraig on the rocks ──────────────────────────────
    ghost = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(ghost)
    gx, gy = W // 2 - 100, 1380
    gd.ellipse((gx - 15, gy - 50, gx + 15, gy - 20), fill=(180, 200, 220, 55))
    gd.polygon(
        [(gx - 25, gy - 15), (gx + 25, gy - 15), (gx + 40, gy + 85), (gx - 40, gy + 85)],
        fill=(180, 200, 220, 30),
    )
    gd.ellipse((gx - 55, gy - 75, gx + 55, gy + 105), fill=(180, 200, 220, 6))
    ghost = ghost.filter(ImageFilter.GaussianBlur(6))
    img = Image.alpha_composite(img, ghost)

    # ── Photographic aperture ring (Lena's presence) ─────────────────────────
    aperture = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ad = ImageDraw.Draw(aperture)
    ap_cx, ap_cy = W // 4, 1280
    ap_r = 100
    blades = 6
    outer = [(ap_cx + ap_r * math.cos(i * math.tau / blades - math.pi / 2), ap_cy + ap_r * math.sin(i * math.tau / blades - math.pi / 2)) for i in range(blades)]
    ad.polygon(outer, outline=(200, 200, 180, 35), width=2)
    inner_r = 50
    inner = [(ap_cx + inner_r * math.cos(i * math.tau / blades - math.pi / 2 + math.pi / blades), ap_cy + inner_r * math.sin(i * math.tau / blades - math.pi / 2 + math.pi / blades)) for i in range(blades)]
    ad.polygon(inner, outline=(200, 200, 180, 25), width=1)
    # Light leak streaks
    for _ in range(4):
        lx = ap_cx + random.randint(-ap_r, ap_r)
        ly = ap_cy + random.randint(-ap_r, ap_r)
        ad.line(
            (lx, ly, lx + random.randint(8, 35), ly + random.randint(8, 35)),
            fill=(random.randint(200, 240), random.randint(160, 200), random.randint(120, 170), random.randint(8, 20)),
            width=1,
        )
    img = Image.alpha_composite(img, aperture)

    # ── Rain streaks ─────────────────────────────────────────────────────────
    rain = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rain)
    for _ in range(250):
        rx = random.randint(0, W)
        ry = random.randint(0, H - 200)
        rlen = random.randint(15, 45)
        alpha = random.randint(18, 55)
        rd.line((rx, ry, rx - 5, ry + rlen), fill=(180, 195, 210, alpha), width=1)
    img = Image.alpha_composite(img, rain)

    # ── Foreground rocks (shoreline) ─────────────────────────────────────────
    rocks = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rkd = ImageDraw.Draw(rocks)
    for _ in range(18):
        rx = random.randint(-50, W + 50)
        ry = random.randint(H - 320, H - 40)
        rw = random.randint(40, 170)
        rh = random.randint(20, 70)
        rkd.ellipse(
            (rx - rw // 2, ry - rh // 2, rx + rw // 2, ry + rh // 2),
            fill=(random.randint(15, 30), random.randint(14, 28), random.randint(18, 32), random.randint(180, 230)),
        )
    img = Image.alpha_composite(img, rocks)

    # ── Sea-mist / spray layer ──────────────────────────────────────────────
    mist = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(mist)
    for _ in range(10):
        mx = random.randint(0, W)
        my = random.randint(800, 1900)
        mr = random.randint(100, 350)
        md.ellipse(
            (mx - mr, my - mr // 2, mx + mr, my + mr // 2),
            fill=(140, 150, 165, random.randint(6, 18)),
        )
    mist = mist.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, mist)

    # ── Title panel ──────────────────────────────────────────────────────────
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
