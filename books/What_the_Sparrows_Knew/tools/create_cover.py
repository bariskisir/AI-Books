#!/usr/bin/env python3
"""Cover: What the Sparrows Knew — Three generations of women in a Galician fishing village reckon with the disappearance of the family matriarch, whose presence still manifests as unexplained blooms of bioluminescence in the tide pools she tended."""

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

    rng = random.Random()
    rng.seed("what_the_sparrows_knew_2024")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Night sky gradient: deep navy to dark indigo ──────────────────────
    for y in range(H):
        t = y / H
        r = int(8 + 16 * t)
        g = int(8 + 12 * t)
        b = int(30 + 22 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── Stars ─────────────────────────────────────────────────────────────
    for _ in range(150):
        sx = rng.randint(0, W)
        sy = rng.randint(0, 850)
        sr = rng.uniform(0.5, 2.5)
        draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr),
                     fill=(rng.randint(200, 240), rng.randint(210, 245),
                           rng.randint(220, 255), rng.randint(80, 220)))

    # ── Subtle Milky Way wash ─────────────────────────────────────────────
    for _ in range(80):
        sx = rng.randint(0, W)
        sy = int(rng.gauss(300, 150))
        draw.ellipse((sx - 2, sy - 2, sx + 2, sy + 2),
                     fill=(170, 180, 210, rng.randint(15, 50)))

    # ── Waning moon over the sea ──────────────────────────────────────────
    moon_x, moon_y = 1100, 340
    for rad in range(90, 5, -6):
        a = max(0, 30 - rad // 3)
        draw.ellipse((moon_x - rad, moon_y - rad, moon_x + rad, moon_y + rad),
                     fill=(180, 190, 200, a))
    draw.ellipse((moon_x - 38, moon_y - 38, moon_x + 38, moon_y + 38),
                 fill=(215, 220, 225, 200))

    # ── Moon reflection on the sea ────────────────────────────────────────
    reflect = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(reflect)
    for i in range(18):
        ry = 1000 + i * 20 + rng.randint(-4, 4)
        rw = 140 - i * 5 + rng.randint(-12, 12)
        rx = moon_x - rw // 2 + rng.randint(-10, 10)
        ra = max(0, 50 - i * 2)
        if rw > 2 and ra > 0:
            rd.ellipse((rx, ry, rx + rw, ry + (i % 3 + 1) * 2),
                       fill=(200, 210, 220, ra))
    reflect = reflect.filter(ImageFilter.GaussianBlur(5))
    img = Image.alpha_composite(img, reflect)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Sea gradient (below horizon ~900) ─────────────────────────────────
    sea_y = 900
    sea_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sea_layer)
    for y in range(sea_y, H):
        t = (y - sea_y) / (H - sea_y)
        r = int(14 + 6 * (1 - t))
        g = int(16 + 8 * (1 - t))
        b = int(38 + 18 * (1 - t))
        sd.line((0, y, W, y), fill=(r, g, b, 200))
    img = Image.alpha_composite(img, sea_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Distant headland / cliff silhouette on the horizon ────────────────
    headland = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(headland)
    # Left headland
    left_pts = [(0, sea_y)]
    for cx in range(0, 500, 20):
        ch = sea_y - (100 + math.sin(cx * 0.012) * 40 +
                      math.sin(cx * 0.03) * 25 + rng.randint(-10, 10))
        left_pts.append((cx, ch))
    left_pts.append((500, sea_y))
    left_pts.append((0, sea_y))
    hd.polygon(left_pts, fill=(18, 16, 22, 230))

    # Right headland (lighthouse side)
    right_pts = [(1100, sea_y)]
    for cx in range(1100, W + 20, 20):
        ch = sea_y - (140 + math.sin(cx * 0.01) * 35 +
                      math.sin(cx * 0.025) * 20 + rng.randint(-12, 12))
        right_pts.append((cx, ch))
    right_pts.append((W, sea_y))
    right_pts.append((1100, sea_y))
    hd.polygon(right_pts, fill=(20, 18, 24, 230))
    img = Image.alpha_composite(img, headland)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Lighthouse ────────────────────────────────────────────────────────
    lh_x = W - 280
    lh_base_y = sea_y - 200

    # Tower body
    draw.polygon([
        (lh_x - 16, lh_base_y),
        (lh_x + 16, lh_base_y),
        (lh_x + 12, lh_base_y - 130),
        (lh_x - 12, lh_base_y - 130),
    ], fill=(40, 38, 42, 240))

    # Red stripes on lighthouse
    for stripe_y in range(lh_base_y - 110, lh_base_y, 20):
        t_top = 1 - (stripe_y - (lh_base_y - 130)) / 130
        half_w = 12 + (1 - t_top) * 4
        draw.rectangle((lh_x - half_w, stripe_y, lh_x + half_w, stripe_y + 8),
                       fill=(100, 30, 25, 180))

    # Lantern room
    draw.rectangle((lh_x - 14, lh_base_y - 148, lh_x + 14, lh_base_y - 130),
                   fill=(25, 25, 30, 240))

    # Lantern glass (glowing)
    draw.rectangle((lh_x - 10, lh_base_y - 145, lh_x + 10, lh_base_y - 133),
                   fill=(240, 220, 130, 200))

    # Roof
    draw.polygon([
        (lh_x - 16, lh_base_y - 148),
        (lh_x + 16, lh_base_y - 148),
        (lh_x, lh_base_y - 170),
    ], fill=(18, 18, 22, 240))

    # Antenna / finial
    draw.line((lh_x, lh_base_y - 170, lh_x, lh_base_y - 185),
              fill=(30, 30, 35, 200), width=2)

    # Light glow around lantern
    glow_halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ghd = ImageDraw.Draw(glow_halo)
    for rad in range(50, 5, -4):
        ghd.ellipse((lh_x - rad, lh_base_y - 140 - rad,
                     lh_x + rad, lh_base_y - 140 + rad),
                    fill=(240, 210, 100, max(0, 60 - rad)))
    glow_halo = glow_halo.filter(ImageFilter.GaussianBlur(10))
    img = Image.alpha_composite(img, glow_halo)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Lighthouse beam sweeping left ─────────────────────────────────────
    beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam)
    beam_center_x = lh_x
    beam_center_y = lh_base_y - 140
    for angle_deg in range(-30, 35, 2):
        angle_rad = math.radians(angle_deg - 8)
        length = 1000 + rng.randint(-100, 100)
        ex = beam_center_x + math.cos(angle_rad) * length
        ey = beam_center_y + math.sin(angle_rad) * length * 0.35
        bd.line((beam_center_x, beam_center_y, ex, ey),
                fill=(240, 210, 100, rng.randint(4, 10)),
                width=rng.randint(8, 18))
    # Bright core of beam
    for angle_deg in range(-12, 15, 1):
        angle_rad = math.radians(angle_deg - 8)
        length = 700 + rng.randint(-50, 50)
        ex = beam_center_x + math.cos(angle_rad) * length
        ey = beam_center_y + math.sin(angle_rad) * length * 0.35
        bd.line((beam_center_x, beam_center_y, ex, ey),
                fill=(255, 230, 140, rng.randint(6, 14)),
                width=6)
    beam = beam.filter(ImageFilter.GaussianBlur(12))
    img = Image.alpha_composite(img, beam)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Sparrows in flight around the lighthouse beam ─────────────────────
    sparrows = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    spd = ImageDraw.Draw(sparrows)
    for _ in range(rng.randint(12, 20)):
        bx = rng.randint(200, W - 50)
        by = rng.randint(200, 700)
        size = rng.uniform(4, 10)
        # Simple V-shape bird silhouette
        spd.line((bx - size, by, bx, by - size * 0.6),
                 fill=(15, 12, 18, rng.randint(160, 220)), width=2)
        spd.line((bx, by - size * 0.6, bx + size, by),
                 fill=(15, 12, 18, rng.randint(160, 220)), width=2)
    # A few closer, larger sparrows
    for _ in range(rng.randint(4, 6)):
        bx = rng.randint(100, W - 50)
        by = rng.randint(100, 400)
        size = rng.uniform(8, 16)
        spd.line((bx - size, by, bx, by - size * 0.7),
                 fill=(10, 8, 14, rng.randint(180, 240)), width=3)
        spd.line((bx, by - size * 0.7, bx + size, by),
                 fill=(10, 8, 14, rng.randint(180, 240)), width=3)
    img = Image.alpha_composite(img, sparrows)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Rocky shoreline in the foreground ─────────────────────────────────
    rocks = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rkd = ImageDraw.Draw(rocks)

    # Large cliff profile along the bottom
    cliff_pts = [(0, H)]
    for x in range(0, W + 10, 10):
        noise = math.sin(x * 0.005) * 60 + math.sin(x * 0.02) * 25
        cy = 1850 + noise + rng.randint(-20, 20)
        cliff_pts.append((x, cy))
    cliff_pts.append((W, H))
    cliff_pts.append((0, H))
    rkd.polygon(cliff_pts, fill=(28, 25, 32, 240))

    # Individual rock formations
    for _ in range(rng.randint(30, 50)):
        rx = rng.randint(-20, W + 20)
        ry = rng.randint(1500, 2350)
        rw = rng.randint(30, 120)
        rh = rng.randint(20, 90)
        rcol = (
            rng.randint(25, 50),
            rng.randint(22, 45),
            rng.randint(30, 55),
        )
        rkd.polygon([
            (rx - rw // 2, ry + rh),
            (rx - rw // 3, ry),
            (rx + rw // 3, ry - rh // 3),
            (rx + rw // 2 + rng.randint(5, 20), ry + rh),
        ], fill=(*rcol, 230))
        # Rock face highlight
        if rng.random() < 0.35:
            rkd.polygon([
                (rx - rw // 5, ry + rh // 2),
                (rx - rw // 7, ry + rh // 6),
                (rx + rw // 8, ry + rh // 3),
            ], fill=(*[min(255, c + 18) for c in rcol], 50))

    img = Image.alpha_composite(img, rocks)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Bioluminescent tide pools ─────────────────────────────────────────
    tide = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(tide)

    biolum_colors = [
        (50, 210, 180),   # teal
        (40, 190, 210),   # cyan
        (60, 230, 160),   # emerald
        (70, 200, 220),   # aqua
        (90, 240, 190),   # light emerald
        (50, 180, 200),   # deep aqua
    ]

    pool_centers = []
    for _ in range(rng.randint(8, 14)):
        px = rng.randint(80, W - 80)
        py = rng.randint(1700, 2100)
        pw = rng.randint(40, 160)
        ph = rng.randint(15, 50)
        pool_centers.append((px, py, pw, ph))

        # Dark pool basin
        td.ellipse((px - pw // 2, py - ph // 2, px + pw // 2, py + ph // 2),
                   fill=(15, 15, 22, 200))

        # Bioluminescent glow layers
        max_gr = max(pw, ph) // 2 - 4
        for gr in range(max_gr, 2, -3):
            intensity = 120 - gr * 3
            if intensity <= 0:
                continue
            pool_col = rng.choice(biolum_colors)
            td.ellipse(
                (px - gr, py - gr * ph // pw,
                 px + gr, py + gr * ph // pw),
                fill=(*pool_col, max(0, min(255, intensity))))

    # Soften the tide pool glows
    tide = tide.filter(ImageFilter.GaussianBlur(5))
    img = Image.alpha_composite(img, tide)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Bioluminescent sparkles (floating particles) ──────────────────────
    sparkle_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sld = ImageDraw.Draw(sparkle_layer)
    for _ in range(rng.randint(80, 130)):
        sx = rng.randint(50, W - 50)
        sy = rng.randint(1400, 2100)
        sr = rng.uniform(1, 4)
        sparkle_col = rng.choice(biolum_colors)
        sld.ellipse((sx - sr, sy - sr, sx + sr, sy + sr),
                    fill=(*sparkle_col, rng.randint(50, 180)))
    sparkle_layer = sparkle_layer.filter(ImageFilter.GaussianBlur(2))
    img = Image.alpha_composite(img, sparkle_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Three female silhouettes (Lidia, Sabela, Carme) on the rocks ──────
    figures = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(figures)

    # Position them at different heights on the rocky shore
    positions = [
        (W // 2 - 320, 1780, 210, True),   # Tall, standing straight
        (W // 2 - 80, 1830, 185, False),    # Medium, arms wrapped
        (W // 2 + 260, 1800, 195, True),    # Tallish, looking out
    ]

    for sx, sy, height, arms_out in positions:
        # Silhouette dress/coat shape
        fd.polygon([
            (sx - 14, sy),                   # left foot
            (sx - 11, sy - height * 0.55),   # hip
            (sx - 10, sy - height * 0.78),   # shoulder
            (sx - 4, sy - height),           # head top left
            (sx + 4, sy - height),           # head top right
            (sx + 10, sy - height * 0.78),   # shoulder
            (sx + 11, sy - height * 0.55),   # hip
            (sx + 14, sy),                   # right foot
        ], fill=(6, 4, 10, 220))

        # Head
        head_r = 9
        fd.ellipse((sx - head_r, sy - height - head_r,
                    sx + head_r, sy - height + head_r),
                   fill=(6, 4, 10, 220))

        # Hair suggestion
        fd.ellipse((sx - head_r - 2, sy - height - head_r - 3,
                    sx + head_r + 2, sy - height - head_r + 5),
                   fill=(4, 3, 8, 220))

        # Arms
        if arms_out:
            fd.line((sx - 10, sy - height * 0.75,
                     sx - 28, sy - height * 0.55),
                    fill=(6, 4, 10, 200), width=3)
            fd.line((sx + 10, sy - height * 0.75,
                     sx + 28, sy - height * 0.55),
                    fill=(6, 4, 10, 200), width=3)
        else:
            # Arms crossed/wrapped
            fd.line((sx - 10, sy - height * 0.75,
                     sx - 5, sy - height * 0.50),
                    fill=(6, 4, 10, 200), width=3)
            fd.line((sx + 10, sy - height * 0.75,
                     sx + 5, sy - height * 0.50),
                    fill=(6, 4, 10, 200), width=3)
            # Wrapped
            fd.ellipse((sx - 16, sy - height * 0.58,
                        sx + 16, sy - height * 0.40),
                       fill=(6, 4, 10, 200))

    # Subtle edge light on the figures from the bioluminescence below
    for sx, sy, height, _ in positions:
        fd.line((sx - 14, sy, sx - 10, sy - height * 0.3),
                fill=(60, 200, 180, 30), width=2)
        fd.line((sx + 14, sy, sx + 10, sy - height * 0.3),
                fill=(60, 200, 180, 30), width=2)

    img = Image.alpha_composite(img, figures)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Mist / fog rising from the tide pools ─────────────────────────────
    mist = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(mist)
    for _ in range(rng.randint(10, 16)):
        mx = rng.randint(50, W - 50)
        my = rng.randint(1400, 2100)
        mr = rng.randint(80, 280)
        mh = rng.randint(40, 150)
        md.ellipse((mx - mr, my - mh, mx + mr, my + mh),
                   fill=(
                       rng.randint(130, 180),
                       rng.randint(190, 220),
                       rng.randint(180, 210),
                       rng.randint(5, 14)
                   ))
    mist = mist.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img, mist)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Vignette (darken edges) ──────────────────────────────────────────
    vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(45 * max(0, 1 - vt))
        if vv > 0:
            vd.line((0, vy, vv, vy), fill=(0, 0, 0, 70))
            vd.line((W - vv, vy, W, vy), fill=(0, 0, 0, 70))
    # Top and bottom vignette
    for vx in range(W):
        vt = 1 - abs(vx - W // 2) / (W // 2)
        vv = int(60 * max(0, 1 - vt))
        if vv > 0:
            vd.line((vx, 0, vx, vv), fill=(0, 0, 0, 80))
            vd.line((vx, H - vv, vx, H), fill=(0, 0, 0, 80))
    img = Image.alpha_composite(img, vig)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Title panel and save ──────────────────────────────────────────────
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
