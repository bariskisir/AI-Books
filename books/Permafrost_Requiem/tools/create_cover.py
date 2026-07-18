#!/usr/bin/env python3
"""Cover: Permafrost Requiem — a thawologist in Siberia uncovers a frozen viral archive in the permafrost, betrayal under arctic aurora."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import (
    _standard_cover_font,
    _standard_cover_repair_text,
    _standard_cover_wrap,
    _standard_cover_center,
    _standard_cover_title_font,
    _standard_cover_metadata_from_locals,
    _standard_cover_resolve_title,
    _standard_cover_resolve_author,
    _draw_standard_cover_title_panel,
)

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# Unique palette: frozen permafrost blue-greys + viral bioluminescence + frost + warning amber
DEEP_FROST_SKY = (5, 12, 35)
ICE_STRATUM = (180, 215, 235)
VIRAL_GREEN = (50, 235, 110)
VIRAL_PURPLE = (160, 45, 210)
VIRAL_CYAN = (30, 220, 200)
AURORA_GREEN = (40, 210, 160)
AURORA_PURPLE = (130, 50, 210)
WARNING_AMBER = (210, 90, 20)
BETRAYAL_RED = (150, 20, 25)
SILHOUETTE = (6, 8, 16)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")
    rng = random.Random("permafrost-requiem-core")

    img = Image.new("RGBA", (W, H), DEEP_FROST_SKY + (255,))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 1. Deep arctic night sky gradient ─────────────────────────────────
    for y in range(H):
        t = y / H
        r = int(5 + 18 * max(0, 1 - t * 1.8))
        g = int(12 + 28 * max(0, 1 - t * 1.8))
        b = int(35 + 20 * max(0, 1 - t * 1.8))
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── 2. Aurora borealis bands ───────────────────────────────────────────
    aurora = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ad = ImageDraw.Draw(aurora)
    for band in range(6):
        base_y = 80 + band * 110 + rng.randint(-25, 25)
        for x in range(0, W, 3):
            wave = math.sin(x * 0.0035 + band * 1.7) * 45 + math.sin(x * 0.011 + band * 2.3) * 12
            wave2 = math.cos(x * 0.005 + band * 0.9) * 20
            col = AURORA_GREEN if band % 2 == 0 else AURORA_PURPLE
            ad.line((x, base_y + wave + wave2, x + 3, base_y + wave + wave2 + 6),
                    fill=(col[0], col[1], col[2], rng.randint(7, 22)))
    aurora = aurora.filter(ImageFilter.GaussianBlur(radius=18))
    img = Image.alpha_composite(img, aurora)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 3. Stars ──────────────────────────────────────────────────────────
    for _ in range(160):
        sx = rng.randint(0, W)
        sy = rng.randint(0, 750)
        sr = rng.choice([1, 1, 2])
        sa = rng.randint(60, 200)
        draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=(220, 225, 235, sa))

    # ── 4. Distant mountain range (Siberian taiga/tundra edge) ────────────
    mtn_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(mtn_layer)
    for mtn_idx in range(3):
        base_h = 750 + mtn_idx * 35
        col_val = 18 - mtn_idx * 4
        pts = [(0, base_h + 120)]
        for mx in range(0, W + 10, 10):
            mtn_h = 160 + math.sin(mx * 0.0028 + mtn_idx * 2.1) * 90
            mtn_h += math.sin(mx * 0.007 + mtn_idx * 3.7) * 25
            mtn_h += math.sin(mx * 0.015 + mtn_idx * 5.3) * 10
            pts.append((mx, 500 + mtn_h + mtn_idx * 50))
        pts.append((W, base_h + 120))
        pts.append((0, base_h + 120))
        md.polygon(pts, fill=(max(6, col_val - 4), max(8, col_val - 2), max(12, col_val + 4), 210))
    # Snow caps
    for cap in range(8):
        cx = rng.randint(100, W - 100)
        cy = rng.randint(580, 780)
        cw, ch = rng.randint(30, 60), rng.randint(8, 18)
        md.ellipse((cx - cw, cy - ch, cx + cw, cy + ch), fill=(200, 210, 220, rng.randint(40, 80)))
    img = Image.alpha_composite(img, mtn_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 5. Permafrost tundra / ice sheet (entire lower zone) ──────────────
    tundra_start = 1100
    for y in range(tundra_start, 1900, 2):
        t = (y - tundra_start) / 800
        r = int(20 + 25 * t + math.sin(y * 0.008) * 4)
        g = int(30 + 30 * t + math.cos(y * 0.011) * 4)
        b = int(50 + 20 * t + math.sin(y * 0.006) * 4)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── 6. Permafrost ice strata — layered horizontal bands ────────────────
    for si in range(12):
        sy = 1170 + si * 55 + rng.randint(-8, 8)
        for x in range(0, W, 2):
            ice_var = math.sin(x * 0.025 + si * 1.3) * 6
            a = rng.randint(15, 40)
            draw.line((x, sy + ice_var, x + 2, sy + ice_var + 1),
                      fill=(rng.randint(150, 210), rng.randint(200, 240), rng.randint(225, 250), a))

    # ── 7. The viral archive — glowing core embedded in the ice ────────────
    acx, acy = W // 2, 1400

    # Outer viral glow (green)
    vglow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vglow)
    for rad in range(140, 10, -10):
        a = max(0, 45 - rad // 3)
        vd.ellipse((acx - rad, acy - rad, acx + rad, acy + rad),
                   fill=(VIRAL_GREEN[0], VIRAL_GREEN[1], VIRAL_GREEN[2], a))
    vglow = vglow.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img, vglow)

    # Secondary purple-pink glow
    vglow2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd2 = ImageDraw.Draw(vglow2)
    for rad in range(90, 10, -10):
        a = max(0, 30 - rad // 4)
        vd2.ellipse((acx - rad + 25, acy - rad - 15, acx + rad + 25, acy + rad - 15),
                    fill=(VIRAL_PURPLE[0], VIRAL_PURPLE[1], VIRAL_PURPLE[2], a))
    vglow2 = vglow2.filter(ImageFilter.GaussianBlur(28))
    img = Image.alpha_composite(img, vglow2)

    # Central cyan glow (inner core)
    vglow3 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd3 = ImageDraw.Draw(vglow3)
    vd3.ellipse((acx - 30, acy - 30, acx + 30, acy + 30),
                fill=(VIRAL_CYAN[0], VIRAL_CYAN[1], VIRAL_CYAN[2], 60))
    vglow3 = vglow3.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, vglow3)

    draw = ImageDraw.Draw(img, "RGBA")

    # ── 8. Permafrost core sample (drawn as an extracted ice core cylinder) ─
    core_w, core_h = 28, 90
    core_x, core_y = acx, acy - core_h - 30
    # Core tube (extracted ice sample)
    draw.rectangle((core_x - core_w, core_y, core_x + core_w, core_y + core_h),
                   fill=(200, 220, 230, 220))
    # Ice strata visible inside the core
    for layer in range(6):
        ly = core_y + 5 + layer * 13
        draw.line((core_x - core_w + 2, ly, core_x + core_w - 2, ly),
                  fill=(rng.randint(140, 180), rng.randint(190, 230), rng.randint(210, 245), 180), width=2)
    # Trapped virus particle visible inside the core
    draw.ellipse((core_x - 6, core_y + 35, core_x + 6, core_y + 47),
                 fill=(VIRAL_GREEN[0], VIRAL_GREEN[1], VIRAL_GREEN[2], 200))
    draw.ellipse((core_x - 3, core_y + 38, core_x + 3, core_y + 44),
                 fill=(180, 255, 210, 230))

    # ── 9. Viral particles (icosahedral / hexagonal) scattered around ──────
    for _ in range(20):
        px = acx + rng.randint(-220, 220)
        py = acy + rng.randint(-200, 200)
        ps = rng.randint(4, 16)
        pc = rng.choice([VIRAL_GREEN, VIRAL_PURPLE, VIRAL_CYAN, (80, 255, 140)])
        pa = rng.randint(70, 190)

        # Hexagonal shape
        hex_pts = []
        for hi in range(6):
            ang = hi * math.pi / 3 + rng.uniform(-0.08, 0.08)
            hex_pts.append((px + ps * math.cos(ang), py + ps * math.sin(ang)))
        draw.polygon(hex_pts, fill=(*pc, pa), outline=(*pc, min(255, pa + 30)))

        # Bright inner core
        draw.ellipse((px - ps // 3, py - ps // 3, px + ps // 3, py + ps // 3),
                     fill=(*pc, min(255, pa + 50)))

        # Spikes (glycoprotein spikes like a real virus)
        if ps > 8:
            for _ in range(rng.randint(3, 5)):
                sa = rng.uniform(0, math.tau)
                sp_x = px + (ps + 4) * math.cos(sa)
                sp_y = py + (ps + 4) * math.sin(sa)
                draw.line((px, py, sp_x, sp_y), fill=(*pc, pa // 2), width=1)

    # ── 10. Radiating ice fractures (the thaw breaking the permafrost) ────
    for fi in range(14):
        fx = acx + rng.randint(-30, 30)
        fy = acy + rng.randint(-30, 30)
        ang = rng.uniform(0, math.tau)
        pts = [(fx, fy)]
        cx, cy = fx, fy
        for step in range(rng.randint(6, 18)):
            cx += math.cos(ang + rng.uniform(-0.35, 0.35)) * rng.randint(12, 35)
            cy += math.sin(ang + rng.uniform(-0.35, 0.35)) * rng.randint(12, 35)
            pts.append((cx, cy))
        fc = (rng.randint(50, 110), rng.randint(120, 200), rng.randint(190, 245))
        draw.line(pts, fill=(*fc, rng.randint(25, 70)), width=rng.randint(1, 3))

    # ── 11. Human silhouettes — the betrayal scene ─────────────────────────
    # Dr. Yelena Volkov (turning away, gripping the extracted sample)
    yx, yy = acx + 150, 1580
    draw.ellipse((yx - 16, yy - 55, yx + 16, yy - 15), fill=SILHOUETTE + (230,))
    draw.ellipse((yx - 11, yy - 76, yx + 11, yy - 54), fill=SILHOUETTE + (230,))
    # Arm clutching sample to chest
    draw.line((yx - 14, yy - 32, yx - 42, yy - 38), fill=SILHOUETTE + (230,), width=4)
    draw.line((yx - 42, yy - 38, yx - 48, yy - 28), fill=SILHOUETTE + (230,), width=3)

    # Amir Hassan (reaching out, betrayed — left side)
    ax, ay = acx - 120, 1570
    draw.ellipse((ax - 14, ay - 52, ax + 14, ay - 12), fill=SILHOUETTE + (230,))
    draw.ellipse((ax - 10, ay - 72, ax + 10, ay - 52), fill=SILHOUETTE + (230,))
    # Arm reaching out toward the archive
    draw.line((ax + 12, ay - 30, ax + 50, ay - 42), fill=SILHOUETTE + (230,), width=4)
    draw.line((ax + 50, ay - 42, ax + 55, ay - 52), fill=SILHOUETTE + (230,), width=3)
    # Other arm hanging
    draw.line((ax - 12, ay - 28, ax - 30, ay - 10), fill=SILHOUETTE + (200,), width=3)

    # ── 12. Amber warning dots (military / Colonel Dementiev presence) ──────
    for _ in range(10):
        wx = rng.randint(120, W - 120)
        wy = rng.randint(1300, 1750)
        wr = rng.randint(2, 5)
        draw.ellipse((wx - wr, wy - wr, wx + wr, wy + wr),
                     fill=(WARNING_AMBER[0], WARNING_AMBER[1], WARNING_AMBER[2], rng.randint(40, 100)))

    # Faint amber searchlight beam from distance
    for _ in range(3):
        lx = rng.randint(200, W - 200)
        ly = rng.randint(1100, 1300)
        for a_offset in range(-3, 4):
            ang = math.radians(a_offset + rng.randint(-2, 2))
            draw.line((lx, ly, lx + int(math.sin(ang) * 300), ly + 400),
                      fill=(WARNING_AMBER[0], WARNING_AMBER[1], WARNING_AMBER[2], rng.randint(2, 8)),
                      width=rng.randint(2, 6))

    # ── 13. Frost crystals on the tundra ──────────────────────────────────
    for _ in range(25):
        fx = rng.randint(50, W - 50)
        fy = rng.randint(1700, 1880)
        fw = rng.randint(8, 25)
        draw.ellipse((fx, fy, fx + fw, fy + 3),
                     fill=(ICE_STRATUM[0], ICE_STRATUM[1], ICE_STRATUM[2], rng.randint(15, 40)))

    # Delicate frost dendrites (branching crystals)
    for _ in range(12):
        dx = rng.randint(100, W - 100)
        dy = rng.randint(1650, 1850)
        dc = (rng.randint(190, 220), rng.randint(220, 245), rng.randint(235, 255))
        da = rng.randint(20, 50)
        branches = rng.randint(3, 6)
        for bi in range(branches):
            bang = bi * math.pi / 3 + rng.uniform(-0.2, 0.2)
            blen = rng.randint(6, 14)
            draw.line((dx, dy, dx + blen * math.cos(bang), dy + blen * math.sin(bang)),
                      fill=(*dc, da), width=1)

    # ── 14. Tiny bioluminescent particles in the air (aerosolized virus) ──
    for _ in range(50):
        px = rng.randint(0, W)
        py = rng.randint(1000, 1700)
        pr = rng.uniform(0.5, 2.5)
        pa = rng.randint(30, 90)
        pc = rng.choice([VIRAL_GREEN, VIRAL_PURPLE, VIRAL_CYAN])
        draw.ellipse((px - pr, py - pr, px + pr, py + pr), fill=(*pc, pa))

    # ── 15. Save ────────────────────────────────────────────────────────────
    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()),
                                     _standard_cover_resolve_author(locals()), model)
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
