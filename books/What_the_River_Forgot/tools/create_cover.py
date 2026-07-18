#!/usr/bin/env python3
"""Cover: What the River Forgot — Coastal noir mystery: a retired marine biologist pulled back into her past when bodies of missing fishermen wash ashore along a remote Oregon coast, each one with gill slits carved into their necks."""

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
    rng.seed(974531)

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Noir sky gradient: cold steel blue top → charcoal → bruise dark bottom ──
    for y in range(H):
        t = y / H
        if t < 0.35:
            s = t / 0.35
            r = int(35 + 10 * s)
            g = int(48 + 8 * s)
            b = int(72 + 6 * s)
        elif t < 0.65:
            s = (t - 0.35) / 0.30
            r = int(45 + 15 * s)
            g = int(56 - 6 * s)
            b = int(78 - 18 * s)
        else:
            s = (t - 0.65) / 0.35
            r = int(60 - 35 * s)
            g = int(50 - 28 * s)
            b = int(60 - 35 * s)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── Noir vertical shadow bars (film noir high-contrast light/dark) ──
    noir_bars = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(noir_bars)
    for bar_x in range(0, W, rng.randint(140, 220)):
        bw = rng.randint(40, 100)
        ba = rng.randint(15, 40)
        nd.rectangle((bar_x, 0, bar_x + bw, H), fill=(0, 0, 0, ba))
    noir_bars = noir_bars.filter(ImageFilter.GaussianBlur(6))
    img = Image.alpha_composite(img, noir_bars)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Distant sea stacks (tall jagged rock formations off the Oregon coast) ──
    stacks_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stacks_img)

    # Sea stack data: (center_x, base_height, width, peak_offset_x)
    stack_data = [
        (180, 820, 70, 0), (280, 780, 55, -10), (420, 750, 65, 8),
        (580, 790, 50, -5), (780, 740, 80, 0), (920, 770, 60, 12),
        (1080, 760, 72, -8), (1240, 800, 55, 5), (1400, 770, 68, -6),
    ]
    for sx, base_h, sw, soff in stack_data:
        pts = []
        resolution = max(2, sw // 3)
        for wx in range(sx - sw, sx + sw + 1, resolution):
            frac = (wx - sx) / sw
            wy = base_h - abs(frac) * 120 + math.sin(frac * 4.5) * 18 + math.sin(frac * 9) * 6
            wy += math.sin(wx * 0.08) * 12
            if frac < -0.5:
                wy += 20 + math.sin(wx * 0.15) * 8
            pts.append((wx, wy))
        sd.polygon([(sx - sw, H)] + pts + [(sx + sw, H)], fill=(12, 10, 16, 230))
        # Jagged top highlight on some stacks
        if rng.random() < 0.5:
            hl_x = sx + soff
            hl_y = base_h - 120 + math.sin(soff * 0.1) * 12
            sd.ellipse((hl_x - 6, hl_y - 4, hl_x + 6, hl_y + 4), fill=(35, 40, 50, rng.randint(30, 70)))

    stacks_img = stacks_img.filter(ImageFilter.GaussianBlur(2))
    img = Image.alpha_composite(img, stacks_img)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Crashing ocean with churning foam patterns ──
    ocean_top = 980
    for y in range(ocean_top, 1780):
        t = (y - ocean_top) / 800
        r = int(10 + 8 * t + math.sin(y * 0.015) * 2)
        g = int(18 + 12 * t + math.sin(y * 0.02) * 3)
        b = int(32 + 18 * t + math.sin(y * 0.025) * 4)
        draw.line((0, y, W, y), fill=(r, g, b, 200))

    # ── White foam crash rings around sea stack bases ──
    for sx, base_h, sw, soff in stack_data:
        for _ in range(rng.randint(3, 6)):
            fx = sx + rng.randint(-sw, sw)
            f_base = base_h - 80 + rng.randint(0, 40)
            fw = rng.randint(30, 80)
            f_pts = []
            for fi in range(fw):
                f_pts.append((
                    fx + fi,
                    f_base + int(math.sin(fi * 0.25 + rng.random() * 2) * 6)
                ))
            fa = rng.randint(40, 100)
            draw.line(f_pts, fill=(200, 215, 225, fa), width=rng.randint(2, 5))

    # ── The River: a dark winding water channel through the scene with pale surface reflections ──
    river_pts = []
    for ri in range(0, W, 4):
        river_y = 1050 + math.sin(ri * 0.004) * 300 + math.sin(ri * 0.012) * 80 + math.sin(ri * 0.03) * 20
        river_pts.append((ri, river_y))
    draw.line(river_pts, fill=(5, 8, 14, 180), width=60)
    # River surface reflections (pale light streaks on the dark water)
    for reflection in range(rng.randint(8, 16)):
        rx = rng.randint(100, W - 100)
        ry = 1050 + math.sin(rx * 0.004) * 300 + math.sin(rx * 0.012) * 80 + math.sin(rx * 0.03) * 20
        rl = rng.randint(15, 40)
        ra = rng.randint(15, 40)
        draw.line((rx - rl // 2, ry - 2, rx + rl // 2, ry + 2), fill=(180, 195, 210, ra), width=rng.randint(1, 3))

    # ── Silhouette of Lena March on the shore, looking out at the sea ──
    fig_x = 1150
    fig_base_y = 1580
    # Body
    draw.polygon([
        (fig_x - 14, fig_base_y),
        (fig_x + 14, fig_base_y),
        (fig_x + 10, fig_base_y - 90),
        (fig_x - 10, fig_base_y - 90),
    ], fill=(5, 4, 7, 220))
    # Head
    draw.ellipse((fig_x - 8, fig_base_y - 110, fig_x + 8, fig_base_y - 94), fill=(5, 4, 7, 220))
    # Arms at sides
    draw.line((fig_x - 14, fig_base_y - 50, fig_x - 30, fig_base_y - 20), fill=(5, 4, 7, 200), width=3)
    draw.line((fig_x + 14, fig_base_y - 50, fig_x + 30, fig_base_y - 30), fill=(5, 4, 7, 200), width=3)
    # Coat/trench (noir detective aesthetic) — slight flare
    draw.polygon([
        (fig_x - 18, fig_base_y - 70),
        (fig_x - 14, fig_base_y),
        (fig_x + 14, fig_base_y),
        (fig_x + 18, fig_base_y - 70),
    ], fill=(5, 4, 7, 200))

    # ── Pine tree silhouettes framing the right edge ──
    for pi in range(rng.randint(6, 10)):
        px = W - rng.randint(10, 120)
        py = rng.randint(1150, 1800)
        ph = rng.randint(60, 200)
        trunk_w = max(3, ph // 20)
        # Trunk
        draw.rectangle((px - trunk_w // 2, py - ph // 3, px + trunk_w // 2, py), fill=(3, 2, 5, 230))
        # Foliage tiers (triangular pine shape)
        tiers = rng.randint(3, 5)
        for ti in range(tiers):
            tw = int(ph * 0.5 * (1 - ti / tiers))
            th = ph // tiers
            ty = py - ph + ti * th
            draw.polygon([
                (px - tw, ty + th),
                (px + tw, ty + th),
                (px, ty)
            ], fill=(4, 3, 6, 220))

    # ── The gill-slit motif carved into foreground rocks ──
    # These are curved triple-slash marks suggesting the serial killer's signature
    rock_base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rkd = ImageDraw.Draw(rock_base)
    # Foreground rock formations (left side)
    for rx_start, ry_start, rw, rh in [(0, 1750, 700, 300), (120, 1850, 500, 250), (900, 1800, 380, 200), (1300, 1900, 300, 180)]:
        pts = []
        for step_x in range(rx_start, rx_start + rw, 6):
            rel = (step_x - rx_start) / rw
            rel_y = ry_start + math.sin(rel * math.pi) * rh
            rel_y += math.sin(rel * 5) * 8 + math.sin(rel * 12) * 3
            pts.append((step_x, rel_y))
        rkd.polygon([(rx_start, H)] + pts + [(rx_start + rw, H)], fill=(rng.randint(8, 18), rng.randint(6, 14), rng.randint(10, 20), 240))

    # Carved gill-slit marks in the large foreground rock
    gill_groups = [
        # (center_x, center_y, scale)
        (180, 1920, 1.0),
        (280, 2000, 0.8),
        (430, 1900, 1.2),
        (1100, 1970, 0.9),
        (980, 1860, 0.7),
        (1400, 2030, 1.1),
    ]
    for gx, gy, gs in gill_groups:
        for gi in range(3):
            offset = (gi - 1) * int(20 * gs)
            pts = []
            for frac in range(0, 25):
                t = frac / 24
                cx = gx + offset + (t - 0.5) * int(70 * gs)
                cy = gy - math.sin(t * math.pi) * int(18 * gs) + math.sin(t * math.pi * 4) * int(3 * gs)
                pts.append((cx, cy))
            # Dark interior of the gash
            rkd.line(pts, fill=(3, 2, 4, 200), width=max(2, int(5 * gs)))
            # Pale highlight on the lower lip of the gash (catches the lighthouse beam)
            highlight_pts = []
            for frac in range(0, 25):
                t = frac / 24
                cx = gx + offset + (t - 0.5) * int(70 * gs)
                cy = gy - math.sin(t * math.pi) * int(18 * gs) + math.sin(t * math.pi * 4) * int(3 * gs) + int(3 * gs)
                highlight_pts.append((cx, cy))
            rkd.line(highlight_pts, fill=(rng.randint(60, 100), rng.randint(55, 90), rng.randint(50, 85), rng.randint(20, 50)), width=max(1, int(2 * gs)))

    img = Image.alpha_composite(img, rock_base)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Lighthouse in the distance on the tallest sea stack ──
    lighthouse_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lg_draw = ImageDraw.Draw(lighthouse_glow)
    lh_x, lh_y = 420, 630
    # Lighthouse tower (small, distant)
    tower_h = 55
    draw.rectangle((lh_x - 5, lh_y - tower_h, lh_x + 5, lh_y), fill=(15, 14, 18, 200))
    # Lantern room
    draw.rectangle((lh_x - 7, lh_y - tower_h - 8, lh_x + 7, lh_y - tower_h), fill=(18, 16, 22, 200))
    # Light glow in lantern
    draw.ellipse((lh_x - 4, lh_y - tower_h - 6, lh_x + 4, lh_y - tower_h - 2), fill=(230, 220, 170, 220))
    # Beam sweeping left across the scene
    for beam_angle in range(-30, 31, 1):
        rad = math.radians(beam_angle - 15)
        bx = lh_x + int(math.cos(rad) * 1200)
        by = lh_y - tower_h + int(math.sin(rad) * 350)
        lg_draw.line((lh_x, lh_y - tower_h, bx, by), fill=(235, 225, 180, max(0, int(22 - abs(beam_angle) * 0.4))), width=6)
    lighthouse_glow = lighthouse_glow.filter(ImageFilter.GaussianBlur(12))
    img = Image.alpha_composite(img, lighthouse_glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Distant town light glow (the small town of the story) ──
    town_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(town_glow)
    for _ in range(rng.randint(8, 15)):
        tx = rng.randint(900, 1500)
        ty = rng.randint(850, 950)
        tg_r = rng.randint(3, 8)
        tg_col = (rng.randint(200, 240), rng.randint(180, 210), rng.randint(140, 180))
        td.ellipse((tx - tg_r, ty - tg_r, tx + tg_r, ty + tg_r), fill=(*tg_col, rng.randint(100, 200)))
    town_glow = town_glow.filter(ImageFilter.GaussianBlur(4))
    img = Image.alpha_composite(img, town_glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Seagull silhouettes wheeling in the sky ──
    for _ in range(rng.randint(10, 18)):
        gx = rng.randint(100, W - 100)
        gy = rng.randint(80, 400)
        span = rng.randint(16, 35)
        ga = rng.randint(80, 180)
        # Two arcs forming a gull V-shape
        draw.arc((gx - span, gy - span // 3, gx, gy + span // 3), 0, 180,
                 fill=(rng.randint(25, 45), rng.randint(25, 45), rng.randint(30, 50), ga), width=2)
        draw.arc((gx, gy - span // 3, gx + span, gy + span // 3), 0, 180,
                 fill=(rng.randint(25, 45), rng.randint(25, 45), rng.randint(30, 50), ga), width=2)

    # ── Mist and fog layers ──
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog)
    for _ in range(rng.randint(6, 12)):
        fcx = rng.randint(0, W)
        fcy = rng.randint(600, 1600)
        fr = rng.randint(120, 350)
        fa = rng.randint(8, 25)
        fd.ellipse((fcx - fr, fcy - fr // 2, fcx + fr, fcy + fr // 2),
                    fill=(rng.randint(120, 160), rng.randint(130, 170), rng.randint(150, 190), fa))
    # Low-lying ground fog
    fd.ellipse((-300, 1700, W + 300, 2300), fill=(140, 155, 170, 25))
    fd.ellipse((-200, 1500, W + 200, 2100), fill=(130, 145, 160, 15))
    fog = fog.filter(ImageFilter.GaussianBlur(35))
    img = Image.alpha_composite(img, fog)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Light rain streaks ──
    rain_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rn_draw = ImageDraw.Draw(rain_layer)
    for _ in range(rng.randint(40, 70)):
        rx = rng.randint(0, W)
        ry = rng.randint(0, H)
        rl = rng.randint(25, 70)
        rn_draw.line((rx, ry, rx - 2, ry + rl), fill=(rng.randint(140, 190), rng.randint(150, 200), rng.randint(180, 220), rng.randint(6, 18)), width=1)
    img = Image.alpha_composite(img, rain_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Title panel ──
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
