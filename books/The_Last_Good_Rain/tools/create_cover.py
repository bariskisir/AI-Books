#!/usr/bin/env python3
"""Cover: The Last Good Rain — When a drought grips their Kenyan village for the seventh year, a grandmother begins weaving clouds from river reeds, and her grandchildren must protect her magic from a preacher who calls it witchcraft."""

from __future__ import annotations
import argparse, json, math, random, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

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
    rng.seed(19631212)  # Kenya Independence Day

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ------------------------------------------------------------------
    # 1. SKY GRADIENT — deep burnt orange at zenith through gold to pale
    #    sand at the horizon, then darkening to rich earth tones below.
    # ------------------------------------------------------------------
    for y in range(H):
        t = y / H
        if y < 1100:
            tr = y / 1100
            r = int(175 + (235 - 175) * tr)
            g = int(65 + (180 - 65) * tr)
            b = int(25 + (95 - 25) * tr)
        elif y < 1350:
            tr = (y - 1100) / 250
            r = int(235 + (195 - 235) * tr)
            g = int(180 + (145 - 180) * tr)
            b = int(95 + (100 - 95) * tr)
        else:
            tr = (y - 1350) / (H - 1350)
            r = int(195 + (75 - 195) * tr)
            g = int(145 + (45 - 145) * tr)
            b = int(100 + (25 - 100) * tr)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ------------------------------------------------------------------
    # 2. SUN — blistering white disc at center-top, layered glow.
    # ------------------------------------------------------------------
    sun_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sun_draw = ImageDraw.Draw(sun_layer)
    sx, sy = W // 2, 200
    sun_draw.ellipse((sx - 50, sy - 50, sx + 50, sy + 50), fill=(255, 252, 235, 255))
    sun_draw.ellipse((sx - 90, sy - 90, sx + 90, sy + 90), fill=(255, 240, 190, 90))
    sun_draw.ellipse((sx - 150, sy - 150, sx + 150, sy + 150), fill=(255, 215, 150, 35))
    sun_draw.ellipse((sx - 250, sy - 250, sx + 250, sy + 250), fill=(255, 190, 110, 12))
    sun_layer = sun_layer.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, sun_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ------------------------------------------------------------------
    # 3. WOVEN CLOUDS — clouds rendered as interwoven reed strands,
    #    alternating horizontal weft and vertical warp lines so the
    #    cloud bodies look like giant woven baskets in the sky.
    # ------------------------------------------------------------------
    cloud_positions = [
        (400, 360, 320, 170),
        (1250, 300, 270, 150),
        (780, 520, 380, 210),
        (250, 620, 220, 140),
        (1380, 560, 240, 130),
        (880, 200, 200, 110),
    ]
    weft_colors = [
        (248, 242, 228, 170), (238, 228, 205, 150),
        (252, 248, 238, 130), (232, 218, 195, 180),
    ]
    warp_colors = [
        (242, 232, 212, 150), (228, 218, 198, 170),
        (248, 238, 218, 130), (222, 208, 185, 190),
    ]

    for cx, cy, cw, ch in cloud_positions:
        # Soft base glow behind each cloud cluster
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.ellipse(
            (cx - cw // 2, cy - ch // 2, cx + cw // 2, cy + ch // 2),
            fill=(245, 235, 215, 50),
        )
        glow = glow.filter(ImageFilter.GaussianBlur(18))
        img = Image.alpha_composite(img, glow)
        draw = ImageDraw.Draw(img, "RGBA")

        # Horizontal weft strands
        step = max(4, ch // 30)
        for s in range(ch // step):
            sy_line = cy - ch // 2 + s * step + rng.randint(0, 3)
            sy_line = max(sy_line, cy - ch // 2 + 2)
            sy_line = min(sy_line, cy + ch // 2 - 2)
            sx0 = max(cx - cw // 2 + rng.randint(-8, 8), 0)
            sx1 = min(cx + cw // 2 + rng.randint(-8, 8), W)
            pts = []
            for x in range(sx0, sx1, 3):
                wave = math.sin(x * 0.035 + s * 0.6 + cx * 0.01) * 3
                pts.append((x, sy_line + wave))
            if len(pts) > 1:
                draw.line(pts, fill=rng.choice(weft_colors), width=rng.randint(1, 2))

        # Vertical warp strands
        step2 = max(5, cw // 30)
        for s in range(cw // step2):
            sx_line = cx - cw // 2 + s * step2 + rng.randint(0, 5)
            sx_line = max(sx_line, cx - cw // 2 + 2)
            sx_line = min(sx_line, cx + cw // 2 - 2)
            sy0 = max(cy - ch // 2 + rng.randint(-4, 4), 0)
            sy1 = min(cy + ch // 2 + rng.randint(-4, 4), H)
            pts = []
            for yc in range(sy0, sy1, 3):
                wave = math.sin(yc * 0.04 + s * 0.45 + cy) * 3
                pts.append((sx_line + wave, yc))
            if len(pts) > 1:
                draw.line(pts, fill=rng.choice(warp_colors), width=rng.randint(1, 2))

    # ------------------------------------------------------------------
    # 4. DISTANT HILLS — undulating hills on the horizon.
    # ------------------------------------------------------------------
    for i in range(8):
        hx = i * 250 + rng.randint(-40, 40)
        hh = rng.randint(60, 180)
        hw = rng.randint(200, 350)
        hill_tone = (
            100 + rng.randint(-20, 20),
            70 + rng.randint(-15, 15),
            45 + rng.randint(-10, 10),
            160,
        )
        draw.ellipse(
            (hx - hw // 2, 1050 - hh // 2, hx + hw // 2, 1050 + hh // 2),
            fill=hill_tone,
        )

    # ------------------------------------------------------------------
    # 5. ACACIA TREE SILHOUETTES — flat-topped umbrella canopies.
    # ------------------------------------------------------------------
    for tx, ty, th in [
        (180, 1030, 100), (450, 1050, 80), (1050, 1040, 110),
        (1350, 1060, 70), (750, 1060, 60),
    ]:
        trunk = (45, 28, 12, 230)
        # Trunk
        draw.line((tx, ty, tx, ty + th), fill=trunk, width=rng.randint(3, 5))
        # Flat-top canopy
        tw = rng.randint(70, 120)
        tch = rng.randint(12, 25)
        draw.ellipse(
            (tx - tw // 2, ty - tch, tx + tw // 2, ty + tch // 2),
            fill=trunk,
        )
        draw.ellipse(
            (tx - tw // 2 + 8, ty - tch - 4, tx + tw // 2 - 8, ty + tch // 2),
            fill=trunk,
        )

    # ------------------------------------------------------------------
    # 6. DRY RIVERBED — a winding pale scar through the landscape.
    # ------------------------------------------------------------------
    river_pts = []
    for rx in range(0, W + 50, 50):
        ry = 1150 + math.sin(rx * 0.005) * 30 + math.sin(rx * 0.012) * 15
        river_pts.append((rx, ry))
    draw.line(river_pts, fill=(160, 140, 100, 200), width=rng.randint(30, 50))
    for dx in (-30, 30):
        bank_pts = [
            (p[0] + dx + rng.randint(-5, 5), p[1] + rng.randint(-5, 5))
            for p in river_pts
        ]
        draw.line(bank_pts, fill=(120, 95, 65, 180), width=3)

    # ------------------------------------------------------------------
    # 7. CRACKED EARTH — branching fissures radiating from seed points.
    # ------------------------------------------------------------------
    for _ in range(80):
        cx = rng.randint(0, W)
        cy = rng.randint(1250, 2100)
        for _c in range(rng.randint(2, 4)):
            angle = rng.uniform(0, math.tau)
            length = rng.randint(15, 70)
            pts = [(cx, cy)]
            a = angle
            px, py = cx, cy
            for _s in range(length // 4):
                px += math.cos(a) * 4 + rng.randint(-2, 2)
                py += math.sin(a) * 4 + rng.randint(-2, 2)
                pts.append((px, py))
                a += rng.uniform(-0.3, 0.3)
            draw.line(pts, fill=(45, 25, 10, 180), width=rng.randint(1, 2))

    # Larger polygonal crack plates
    for _ in range(15):
        pcx = rng.randint(200, W - 200)
        pcy = rng.randint(1400, 2000)
        sz = rng.randint(40, 100)
        sides = rng.randint(4, 7)
        poly = []
        for i in range(sides):
            a = i / sides * math.tau + rng.uniform(-0.25, 0.25)
            r = sz * rng.uniform(0.6, 1.4)
            poly.append((pcx + math.cos(a) * r, pcy + math.sin(a) * r))
        draw.polygon(poly, outline=(40, 22, 10, 160), width=1)

    # ------------------------------------------------------------------
    # 8. RIVER REEDS — tall thin grasses with seed heads.
    # ------------------------------------------------------------------
    def draw_reed(d, x, y, height, shade_shift=0):
        base_r, base_g, base_b = 180 + shade_shift, 145 + shade_shift, 50 + shade_shift
        # Curved stalk
        stalk_pts = [(x, y)]
        for i in range(1, height, 5):
            offset = math.sin(i * 0.08) * 3
            stalk_pts.append((x + offset, y - i))
        d.line(stalk_pts, fill=(base_r, base_g, base_b, 220), width=2)
        # Leaf blades
        for lf in range(3, 7):
            ly = y - height * (lf / 8)
            lw = rng.randint(10, 22)
            la = math.radians(rng.randint(-45, 45))
            ex = x + math.sin(la) * lw
            ey = ly - math.cos(la) * lw * 0.4
            d.line((x, ly, ex, ey), fill=(base_r + 15, base_g - 5, base_b - 10, 200), width=1)
        # Seed head
        d.ellipse(
            (x - 3, y - height - 6, x + 3, y - height),
            fill=(base_r - 10, base_g - 5, base_b + 20, 200),
        )

    for _ in range(50):
        draw_reed(
            draw,
            rng.randint(50, W - 50),
            rng.randint(1350, 1850),
            rng.randint(80, 220),
            rng.randint(-10, 20),
        )

    # ------------------------------------------------------------------
    # 9. NYOKABI (GRANDMOTHER) SILHOUETTE — standing at the riverbank,
    #    shawl-wrapped, arms raised skyward, weaving.
    # ------------------------------------------------------------------
    fx, fy = 600, 1620  # figure anchor

    # Body / robe
    body_poly = [
        (fx - 28, fy + 10),
        (fx - 22, fy - 25),
        (fx - 12, fy - 50),
        (fx - 5, fy - 60),
        (fx + 5, fy - 60),
        (fx + 12, fy - 50),
        (fx + 22, fy - 25),
        (fx + 28, fy + 10),
    ]
    draw.polygon(body_poly, fill=(28, 16, 8, 240))

    # Head
    draw.ellipse((fx - 8, fy - 78, fx + 8, fy - 60), fill=(28, 16, 8, 240))

    # Arms raised
    draw.line((fx - 18, fy - 48, fx - 35, fy - 120), fill=(28, 16, 8, 240), width=5)
    draw.line((fx + 18, fy - 48, fx + 35, fy - 120), fill=(28, 16, 8, 240), width=5)

    # Shawl streaming sideways
    for sw in range(3):
        swx = fx - 28 - sw * 12
        swy = fy - 20 + sw * 8
        sw_len = rng.randint(30, 50)
        draw.line((swx, swy, swx - sw_len, swy + 10), fill=(28, 16, 8, 200), width=3)

    # ------------------------------------------------------------------
    # 10. WEAVING STRANDS — reed-threads arcing from Nyokabi's raised
    #     hands up into the woven clouds above.
    # ------------------------------------------------------------------
    for cloud_target in [(400, 360), (780, 520)]:
        for strand in range(5):
            sx0 = fx + rng.randint(-10, 10)
            sy0 = fy - 115 + rng.randint(-15, 15)
            ttx = cloud_target[0] + rng.randint(-60, 60)
            tty = cloud_target[1] + rng.randint(-40, 40)
            # Control point — arcs upward
            mxx = (sx0 + ttx) / 2 + rng.randint(-40, 40)
            myy = min(sy0, tty) - rng.randint(30, 80)
            pts = []
            for t in range(21):
                f = t / 20
                bx = (1 - f) ** 2 * sx0 + 2 * (1 - f) * f * mxx + f**2 * ttx
                by = (1 - f) ** 2 * sy0 + 2 * (1 - f) * f * myy + f**2 * tty
                pts.append((bx, by))
            draw.line(
                pts, fill=(230, 215, 185, rng.randint(80, 150)),
                width=rng.randint(1, 2),
            )

    # ------------------------------------------------------------------
    # 11. ATMOSPHERIC DUST — fine suspended particles in the hot air.
    # ------------------------------------------------------------------
    dust = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dust_draw = ImageDraw.Draw(dust)
    for _ in range(250):
        dx = rng.randint(0, W)
        dy = rng.randint(300, 2200)
        dr = rng.randint(1, 3)
        dust_draw.ellipse(
            (dx - dr, dy - dr, dx + dr, dy + dr),
            fill=(210, 185, 140, rng.randint(10, 50)),
        )
    dust = dust.filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(img, dust)
    draw = ImageDraw.Draw(img, "RGBA")

    # ------------------------------------------------------------------
    # 12. TITLE PANEL AND OUTPUT
    # ------------------------------------------------------------------
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
