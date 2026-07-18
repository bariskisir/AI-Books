#!/usr/bin/env python3
"""Cover: The Knife-Grinder's Saint — In 1780s Prague, a Jewish knife-grinder who can read the history of any blade by
touching its edge is hunted by a nobleman who wants him to authenticate a dagger that supposedly killed a saint.

Unique elements:
- Warm amber/sepia/terracotta palette evoking 18th-century Prague stone, candlelight, and old parchment.
- A looming dagger blade in the foreground with ghostly "memory echoes" — translucent scenes of a saint's martyrdom
  bleeding from the steel, representing Yakov's supernatural touch.
- Prague gothic spires (St. Vitus Cathedral) silhouetted in the mist behind the blade.
- Cobblestone street texture along the bottom, grounding the scene in the Jewish Quarter.
- Count Hradek's silhouette watching from a high tower window, a subtle threat in the background.
- An engraved Hebrew-style blessing along the blade's tang, hinting at Jewish folklore and the relic's origin."""

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
rng.seed(4718915)  # deterministic but unique per-book


def _composite_onto(dest: Image.Image, src: Image.Image) -> Image.Image:
    """Alpha-composite *src* over *dest* and return a new Image."""
    return Image.alpha_composite(dest, src)


def _render_sky_gradient() -> Image.Image:
    """Dusk sky: deep terracotta at horizon fading to charcoal at top, Prague at twilight."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(1400):
        t = y / 1400
        r = int(180 * (1 - t) + 40 * t)
        g = int(100 * (1 - t) + 32 * t)
        b = int(55 * (1 - t) + 38 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))
    return img


def _render_streak_clouds() -> Image.Image:
    """Thin horizontal amber clouds — dust and smoke over 18th-century Prague."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(18):
        y = rng.randint(80, 600)
        x0 = rng.randint(-100, W - 200)
        length = rng.randint(300, 900)
        base_alpha = rng.randint(12, 35)
        for wx in range(length):
            amp = 1.0 - abs(wx - length / 2) / (length / 2)
            dy = int(math.sin(wx * 0.02) * 2) if rng.random() < 0.5 else 0
            draw.point((x0 + wx, y + dy), fill=(220, 180, 130, int(base_alpha * amp)))
    return img


def _render_prague_skyline() -> Image.Image:
    """Silhouette of St. Vitus Cathedral and Old Town Prague rooftops at twilight."""
    skyline = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(skyline)

    base_y = 820
    cx = 800  # cathedral center

    # Cathedral main body
    sd.polygon([
        (cx - 120, base_y), (cx - 110, base_y - 160), (cx - 100, base_y - 170),
        (cx - 90, base_y - 340), (cx - 85, base_y - 350),
        (cx - 40, base_y - 350), (cx - 35, base_y - 340),
        (cx - 20, base_y - 200), (cx + 20, base_y - 200),
        (cx + 35, base_y - 340), (cx + 40, base_y - 350),
        (cx + 85, base_y - 350), (cx + 90, base_y - 340),
        (cx + 100, base_y - 170), (cx + 110, base_y - 160), (cx + 120, base_y),
    ], fill=(15, 12, 18, 230))

    # Left spire
    sd.polygon([
        (cx - 100, base_y - 170), (cx - 80, base_y - 170),
        (cx - 70, base_y - 360), (cx - 68, base_y - 440),
        (cx - 55, base_y - 440), (cx - 50, base_y - 350),
        (cx - 40, base_y - 350), (cx - 35, base_y - 340),
    ], fill=(15, 12, 18, 230))

    # Right spire
    sd.polygon([
        (cx + 100, base_y - 170), (cx + 80, base_y - 170),
        (cx + 70, base_y - 360), (cx + 68, base_y - 440),
        (cx + 55, base_y - 440), (cx + 50, base_y - 350),
        (cx + 40, base_y - 350), (cx + 35, base_y - 340),
    ], fill=(15, 12, 18, 230))

    # Smaller rooftops along the skyline
    step = rng.randint(18, 40)
    roofs_x = list(range(0, W, step))
    for rx in roofs_x:
        rw = rng.randint(20, 45)
        gable = rng.randint(8, 20)
        peak = base_y - rng.randint(30, 90)
        sd.polygon([
            (rx - rw // 2, base_y),
            (rx - rw // 2 + gable, base_y - rng.randint(40, 90)),
            (rx + rw // 2 - gable, peak),
            (rx + rw // 2, base_y),
        ], fill=(18, 14, 20, 200))
        # Tiny lit window
        if rng.random() < 0.3:
            wy_top = base_y - rng.randint(25, 55)
            wy_bot = wy_top + rng.randint(10, 25)
            sd.rectangle(
                (rx - 3, wy_top, rx + 3, wy_bot),
                fill=(255, 200, 100, rng.randint(40, 100)),
            )

    # Tower with Count Hradek's silhouette
    tx, ty = 1250, 600
    sd.rectangle((tx - 25, ty, tx + 25, base_y), fill=(15, 12, 18, 220))
    sd.polygon([(tx - 35, ty), (tx + 35, ty), (tx, ty - 50)], fill=(15, 12, 18, 220))
    sd.rectangle((tx - 8, ty + 55, tx + 8, ty + 80), fill=(220, 180, 100, 100))
    sd.rectangle((tx - 4, ty + 60, tx + 4, ty + 75), fill=(5, 3, 8, 180))

    skyline = skyline.filter(ImageFilter.GaussianBlur(3))
    return skyline


def _render_foreground_blade() -> Image.Image:
    """Massive dagger blade from lower-right to upper-center with memory-echo scenes."""
    blade_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(blade_layer)

    tip_x, tip_y = 640, 300
    hilt_cx, hilt_cy = 1200, 1800
    angle = math.atan2(hilt_cy - tip_y, hilt_cx - tip_x)

    base_width = 42
    tip_width = 6
    segs = 60

    # Build blade polygon
    blade_pts = []
    for i in range(segs + 1):
        frac = i / segs
        x = tip_x + (hilt_cx - tip_x) * frac
        y = tip_y + (hilt_cy - tip_y) * frac
        w = tip_width + (base_width - tip_width) * frac
        perp = angle + math.pi / 2
        blade_pts.append((int(x + math.cos(perp) * w), int(y + math.sin(perp) * w)))
    for i in range(segs, -1, -1):
        frac = i / segs
        x = tip_x + (hilt_cx - tip_x) * frac
        y = tip_y + (hilt_cy - tip_y) * frac
        w = tip_width + (base_width - tip_width) * frac
        perp = angle - math.pi / 2
        blade_pts.append((int(x + math.cos(perp) * w), int(y + math.sin(perp) * w)))

    bd.polygon(blade_pts, fill=(180, 185, 190, 200))

    # Fuller (groove down the center)
    groove_pts = []
    for i in range(segs + 1):
        frac = i / segs
        x = tip_x + (hilt_cx - tip_x) * frac
        y = tip_y + (hilt_cy - tip_y) * frac
        w = (tip_width + (base_width - tip_width) * frac) * 0.35
        perp = angle + math.pi / 2
        groove_pts.append((int(x + math.cos(perp) * w), int(y + math.sin(perp) * w)))
    for i in range(segs, -1, -1):
        frac = i / segs
        x = tip_x + (hilt_cx - tip_x) * frac
        y = tip_y + (hilt_cy - tip_y) * frac
        w = (tip_width + (base_width - tip_width) * frac) * 0.35
        perp = angle - math.pi / 2
        groove_pts.append((int(x + math.cos(perp) * w), int(y + math.sin(perp) * w)))
    bd.polygon(groove_pts, fill=(120, 125, 130, 180))

    # Edge highlight (left edge of blade)
    for i in range(segs):
        frac = i / segs
        x1 = tip_x + (hilt_cx - tip_x) * frac
        y1 = tip_y + (hilt_cy - tip_y) * frac
        w1 = tip_width + (base_width - tip_width) * frac
        x2 = tip_x + (hilt_cx - tip_x) * (frac + 1 / segs)
        y2 = tip_y + (hilt_cy - tip_y) * (frac + 1 / segs)
        w2 = tip_width + (base_width - tip_width) * (frac + 1 / segs)
        perp = angle + math.pi / 2
        p1 = (int(x1 + math.cos(perp) * w1), int(y1 + math.sin(perp) * w1))
        p2 = (int(x2 + math.cos(perp) * w2), int(y2 + math.sin(perp) * w2))
        bd.line((p1, p2), fill=(220, 225, 235, 160), width=3)

    # Crossguard (hilt)
    hx, hy = hilt_cx, hilt_cy
    hperp = angle + math.pi / 2
    bd.line((
        int(hx + math.cos(hperp) * 70), int(hy + math.sin(hperp) * 70),
        int(hx + math.cos(hperp + math.pi) * 70), int(hy + math.sin(hperp + math.pi) * 70),
    ), fill=(100, 90, 70, 220), width=14)
    # Grip
    bd.line((
        int(hx + math.cos(angle + math.pi) * 20), int(hy + math.sin(angle + math.pi) * 20),
        int(hx + math.cos(angle + math.pi) * 120), int(hy + math.sin(angle + math.pi) * 120),
    ), fill=(40, 30, 20, 220), width=18)
    # Grip wrapping
    for wi in range(6):
        wx = hx + math.cos(angle + math.pi) * 30 * (1 + wi * 0.7)
        wy = hy + math.sin(angle + math.pi) * 30 * (1 + wi * 0.7)
        bd.line((
            int(wx + math.cos(hperp) * 12), int(wy + math.sin(hperp) * 12),
            int(wx + math.cos(hperp + math.pi) * 12), int(wy + math.sin(hperp + math.pi) * 12),
        ), fill=(60, 50, 40, 200), width=3)

    # Hebrew-style engraving along the tang
    engraving_text = "    ".join(["אני", "הדרך",
                                  "והאמת", "והחיים"])
    eng_x = tip_x + (hilt_cx - tip_x) * 0.65
    eng_y = tip_y + (hilt_cy - tip_y) * 0.65
    eng_spacing = 22
    for i, ch in enumerate(engraving_text):
        ex = int(eng_x + math.cos(angle) * i * eng_spacing - math.sin(angle) * 8)
        ey = int(eng_y + math.sin(angle) * i * eng_spacing + math.cos(angle) * 8)
        if ch != " ":
            lcol = (180, 170, 150, rng.randint(60, 120))
            lt = rng.randint(0, 3)
            if lt == 0:
                bd.rectangle((ex - 3, ey - 5, ex + 1, ey + 5), fill=lcol)
                bd.rectangle((ex - 1, ey - 5, ex + 3, ey - 2), fill=lcol)
            elif lt == 1:
                bd.ellipse((ex - 4, ey - 4, ex + 2, ey + 4), fill=lcol)
                bd.line((ex + 2, ey - 5, ex + 2, ey + 5), fill=lcol)
            elif lt == 2:
                bd.polygon([(ex, ey - 5), (ex - 4, ey - 1), (ex - 3, ey + 4),
                            (ex + 1, ey + 5), (ex + 3, ey + 2)], fill=lcol)
            else:
                bd.line((ex, ey - 4, ex, ey + 4), fill=lcol)
                bd.line((ex, ey - 4, ex + 4, ey), fill=lcol)
        else:
            eng_spacing = 10

    # ── Memory echoes: translucent martyrdom scenes ──
    echoes = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ed = ImageDraw.Draw(echoes)

    # Saint figure with halo
    sx, sy = 500, 600
    ed.ellipse((sx - 15, sy - 50, sx + 15, sy - 20), fill=(220, 200, 170, 40))
    ed.polygon([
        (sx - 12, sy - 18), (sx + 12, sy - 18),
        (sx + 18, sy + 10), (sx - 18, sy + 10),
    ], fill=(200, 180, 160, 30))
    ed.ellipse((sx - 6, sy - 30, sx + 6, sy - 20), fill=(210, 190, 170, 30))
    for ci in range(8):
        ca = math.radians(ci * 45)
        ed.line((sx, sy - 25, int(sx + math.cos(ca) * 25), int(sy - 25 + math.sin(ca) * 25)),
                fill=(220, 190, 120, 25), width=2)

    # Bound hands / stigmata
    hhx, hhy = 750, 500
    ed.line((hhx - 20, hhy, hhx + 20, hhy), fill=(160, 120, 100, 35), width=3)
    ed.ellipse((hhx - 12, hhy - 5, hhx - 4, hhy + 5), fill=(200, 150, 130, 30))
    ed.ellipse((hhx + 4, hhy - 5, hhx + 12, hhy + 5), fill=(200, 150, 130, 30))
    for _ in range(5):
        bdx = hhx + rng.randint(-25, 25)
        bdy = hhy + rng.randint(5, 30)
        ed.ellipse((bdx - 2, bdy - 2, bdx + 2, bdy + 2), fill=(160, 40, 30, rng.randint(20, 40)))

    # Gothic stone arch
    aa, ab = 400, 400
    ed.arc((aa - 30, ab - 20, aa + 30, ab + 40), 0, 180, fill=(180, 170, 150, 25), width=3)
    ed.rectangle((aa - 25, ab + 10, aa + 25, ab + 40), fill=(50, 45, 40, 20))

    # Reliquary
    ra, rb = 650, 700
    ed.rectangle((ra - 20, rb - 12, ra + 20, rb + 12), fill=(180, 160, 100, 30))
    for _ in range(4):
        gx = ra + rng.randint(-15, 15)
        gy = rb + rng.randint(-8, 8)
        ed.ellipse((gx - 3, gy - 3, gx + 3, gy + 3), fill=(200, 50, 50, rng.randint(30, 50)))

    # Particle trails rising from blade
    for _ in range(40):
        pt = rng.random()
        pxx = tip_x + (hilt_cx - tip_x) * pt
        pyy = tip_y + (hilt_cy - tip_y) * pt
        for drift in range(3):
            ddx = pxx + rng.randint(-50, 50) + drift * rng.randint(-10, 10)
            ddy = pyy + rng.randint(-80, -20) - drift * 15
            ed.ellipse((ddx - 2, ddy - 2, ddx + 2, ddy + 2),
                       fill=(220, 200, 170, rng.randint(10, 30)))

    echoes = echoes.filter(ImageFilter.GaussianBlur(6))
    blade_layer = Image.alpha_composite(blade_layer, echoes)
    blade_layer = blade_layer.filter(ImageFilter.GaussianBlur(2))
    return blade_layer


def _render_cobblestone_base() -> Image.Image:
    """Warm worn cobblestones suggesting Jewish Quarter streets."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(img)

    y_start = 1650
    for cy in range(y_start, H, rng.randint(14, 22)):
        for cx in range(0, W + 20, rng.randint(30, 55)):
            cw = rng.randint(20, 40)
            ch = rng.randint(10, 18)
            shade = rng.randint(60, 110)
            cd.ellipse(
                (cx - cw // 2, cy - ch // 2, cx + cw // 2, cy + ch // 2),
                fill=(shade, shade - 8, shade - 12, rng.randint(120, 200)),
            )
            cd.ellipse(
                (cx - cw // 2 + 2, cy - ch // 2 + 2, cx + cw // 2 - 2, cy + ch // 2 - 2),
                fill=(shade + 20, shade + 12, shade + 5, rng.randint(50, 100)),
            )
    # Grout lines
    for cy in range(y_start + 7, H, rng.randint(14, 22)):
        cd.line((0, cy, W, cy), fill=(35, 30, 25, rng.randint(30, 60)), width=1)

    return img.filter(ImageFilter.GaussianBlur(1))


def _render_vignette() -> Image.Image:
    """Edge darkening."""
    vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(60 * max(0, 1 - vt))
        if vv > 0:
            vd.line((0, vy, vv, vy), fill=(0, 0, 0, 70))
            vd.line((W - vv, vy, W, vy), fill=(0, 0, 0, 70))
    for vx in range(W):
        vt = 1 - abs(vx - W // 2) / (W // 2)
        vv = int(50 * max(0, 1 - vt))
        if vv > 0:
            vd.line((vx, 0, vx, vv), fill=(0, 0, 0, 50))
            vd.line((vx, H - vv, vx, H), fill=(0, 0, 0, 80))
    return vig


def _render_candlelight_glow() -> Image.Image:
    """Warm candle glow spots."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(img)
    for _ in range(8):
        gx = rng.randint(50, W - 50)
        gy = rng.randint(100, 1400)
        gr = rng.randint(40, 100)
        gd.ellipse((gx - gr, gy - gr, gx + gr, gy + gr),
                   fill=(255, 200, 120, rng.randint(8, 20)))
    return img.filter(ImageFilter.GaussianBlur(15))


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    # Base canvas
    img = Image.new("RGBA", (W, H), (40, 32, 30, 255))
    img = _composite_onto(img, _render_sky_gradient())
    img = _composite_onto(img, _render_streak_clouds())
    img = _composite_onto(img, _render_prague_skyline())

    # Tiny candle windows drawn directly via draw
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(12):
        wx = rng.randint(50, W - 50)
        wy = rng.randint(200, 750)
        draw.rectangle((wx - 2, wy - 3, wx + 2, wy + 3),
                       fill=(255, 200, 100, rng.randint(30, 80)))
        if rng.random() < 0.4:
            draw.ellipse((wx - 8, wy - 8, wx + 8, wy + 8),
                         fill=(255, 210, 140, rng.randint(5, 15)))

    # Foreground blade
    img = _composite_onto(img, _render_foreground_blade())

    # Cobblestone base
    cobble = _render_cobblestone_base()
    img = _composite_onto(img, cobble)

    # Candlelight glow
    img = _composite_onto(img, _render_candlelight_glow())

    # Vignette
    img = _composite_onto(img, _render_vignette())

    # Title panel
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
