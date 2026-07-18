#!/usr/bin/env python3
"""Cover: The Laughter of Iron Harvests — After the Battle of the Somme, a sapper unearths a gramophone buried in no-man's-land; the brass horn glows with the recorded voices of the dead, rising from shell-scarred mud under a storm-choked sky."""

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
    rng.seed(81726354)

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Deep earthen gradient: muddy brown (top) to near-black (bottom)
    for y in range(H):
        t = y / H
        r = int(55 + (20 - 55) * t)
        g = int(35 + (12 - 35) * t)
        b = int(18 + (6 - 18) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # Storm-laden sky overlay (top fifth)
    sky = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sky)
    for y in range(900):
        t = y / 900
        r = int(75 + (45 - 75) * t)
        g = int(65 + (35 - 65) * t)
        b = int(55 + (25 - 55) * t)
        sd.line((0, y, W, y), fill=(r, g, b, 180))
    img = Image.alpha_composite(img, sky)
    draw = ImageDraw.Draw(img, "RGBA")

    # Storm clouds — overlapping ellipses in the sky
    for _ in range(18):
        cx = rng.randint(-100, W + 100)
        cy = rng.randint(0, 650)
        rx = rng.randint(120, 350)
        ry = rng.randint(35, 90)
        alpha = rng.randint(25, 75)
        draw.ellipse(
            (cx - rx, cy - ry, cx + rx, cy + ry),
            fill=(50, 45, 40, alpha),
        )

    # Distant ridge / horizon line — jagged with shell damage
    pts = []
    for x in range(0, W + 5, 5):
        h_y = 880 + 28 * math.sin(x * 0.008) + 18 * math.sin(x * 0.023) + rng.randint(-6, 6)
        pts.append((x, h_y))
    draw.line(pts, fill=(30, 25, 18, 220), width=4)

    # Blasted tree stumps on the ridge
    for _ in range(6):
        tx = rng.randint(80, W - 80)
        th = int(880 + 28 * math.sin(tx * 0.008) + 18 * math.sin(tx * 0.023))
        draw.line((tx, th, tx, th + 50), fill=(22, 18, 14, 200), width=5)
        # Splintered branches
        for a in range(-50, 60, 35):
            rad = math.radians(a + rng.randint(-10, 10))
            bx = tx + int(35 * math.cos(rad))
            by = th + int(35 * math.sin(rad))
            draw.line((tx, th + 8, bx, by), fill=(22, 18, 14, 180), width=2)

    # MAIN SHELL CRATER — foreground center
    ccx, ccy = W // 2, 1650
    crx, cry = 420, 160
    # Outer crater rim
    draw.ellipse(
        (ccx - crx, ccy - cry, ccx + crx, ccy + cry),
        fill=(22, 18, 12, 240),
    )
    # Inner crater depression
    draw.ellipse(
        (ccx - crx + 40, ccy - cry + 25, ccx + crx - 40, ccy + cry - 15),
        fill=(38, 28, 20, 220),
    )
    # Rainwater pooled in the crater
    draw.ellipse(
        (ccx - 200, ccy - 35, ccx + 200, ccy + 50),
        fill=(60, 50, 38, 180),
    )
    # Muddy water highlights
    for _ in range(25):
        rx = rng.randint(-180, 180)
        ry = rng.randint(-25, 40)
        draw.ellipse(
            (ccx + rx - 5, ccy + ry - 2, ccx + rx + 5, ccy + ry + 2),
            fill=(90, 78, 58, rng.randint(25, 65)),
        )

    # Secondary craters scattered around foreground
    for _ in range(5):
        scx = rng.randint(80, W - 80)
        scy = rng.randint(1450, 1850)
        srr = rng.randint(40, 110)
        draw.ellipse(
            (scx - srr, scy - srr // 2, scx + srr, scy + srr // 2),
            fill=(rng.randint(18, 32), rng.randint(14, 26), rng.randint(10, 18), 220),
        )

    # Barbed wire tangles across the mid-ground
    wire_base_y = 1180
    for row in range(3):
        wy = wire_base_y + row * 25 + rng.randint(-5, 5)
        draw.line((0, wy, W, wy), fill=(65, 58, 50, 160), width=2)
        for px in range(40, W, rng.randint(80, 160)):
            # Post
            draw.line((px, wy - 35, px, wy + 12), fill=(50, 42, 35, 220), width=5)
            # Barb spirals
            for side in (-1, 1):
                ax = px + side * 18
                draw.line((px, wy - 12, ax, wy + 6), fill=(75, 68, 60, 180), width=1)
                draw.line((px, wy - 2, ax, wy - 8), fill=(75, 68, 60, 180), width=1)
                draw.line((px, wy + 4, ax, wy - 2), fill=(75, 68, 60, 180), width=1)

    # THE GRAMOPHONE — rising from the crater, the story's heartbeat
    gx, gy = ccx, ccy - 130

    # Wooden cabinet base
    draw.rectangle(
        (gx - 42, gy + 38, gx + 42, gy + 105),
        fill=(75, 55, 28, 240),
    )
    draw.rectangle(
        (gx - 44, gy + 36, gx + 44, gy + 107),
        fill=(55, 40, 20, 255),
        width=2,
    )

    # Turntable platter
    draw.ellipse(
        (gx - 38, gy + 22, gx + 38, gy + 50),
        fill=(48, 38, 22, 230),
    )
    draw.ellipse(
        (gx - 12, gy + 28, gx + 12, gy + 44),
        fill=(95, 80, 55, 220),
    )

    # Tonearm
    draw.line(
        (gx + 18, gy + 30, gx + 55, gy - 25),
        fill=(130, 118, 95, 230),
        width=5,
    )

    # Brass horn (the iconic flared Victrola horn)
    horn_pts = [
        (gx + 52, gy - 25),  # neck of horn
        (gx + 85, gy - 85),
        (gx + 135, gy - 145),
        (gx + 165, gy - 170),
        (gx + 180, gy - 158),
        (gx + 155, gy - 132),
        (gx + 105, gy - 75),
        (gx + 60, gy - 15),
    ]
    draw.polygon(horn_pts, fill=(185, 158, 85, 230))
    draw.polygon(horn_pts, outline=(145, 112, 52, 255), width=3)
    # Dark interior of the horn flare
    inner_horn = [
        (gx + 135, gy - 145),
        (gx + 165, gy - 170),
        (gx + 180, gy - 158),
        (gx + 155, gy - 132),
    ]
    draw.polygon(inner_horn, fill=(38, 28, 12, 200))

    # EERIE GLOW around the gramophone — the voices emerging
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    # Outer diffuse glow
    gd.ellipse(
        (gx - 220, gy - 280, gx + 340, gy + 160),
        fill=(170, 195, 225, 14),
    )
    gd.ellipse(
        (gx - 120, gy - 200, gx + 240, gy + 90),
        fill=(200, 225, 255, 18),
    )
    # Central hotspot at the horn mouth
    gd.ellipse(
        (gx + 120, gy - 190, gx + 200, gy - 120),
        fill=(220, 235, 255, 25),
    )
    glow = glow.filter(ImageFilter.GaussianBlur(35))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Sound-wave rings expanding from the horn mouth
    for r in range(1, 9):
        radius = r * 28 + 15
        alpha = max(3, 55 - r * 6)
        draw.ellipse(
            (gx + 155 - radius, gy - 160 - radius, gx + 155 + radius, gy - 160 + radius),
            outline=(155, 200, 235, alpha),
            width=2 if r % 2 == 1 else 1,
        )

    # Ethereal music particles / voice motes ascending from the horn
    for _ in range(40):
        wx = gx + 140 + rng.randint(-40, 100)
        wy = gy - 170 - rng.randint(0, 260)
        ws = rng.randint(2, 7)
        wa = rng.randint(25, 100)
        col = (
            rng.randint(170, 220),
            rng.randint(200, 240),
            rng.randint(220, 255),
            wa,
        )
        draw.ellipse((wx - ws, wy - ws, wx + ws, wy + ws), fill=col)
        # Short luminous trail
        for t in range(3):
            tx = wx + rng.randint(-12, 12)
            ty = wy - t * rng.randint(10, 22)
            draw.ellipse(
                (tx - 1, ty - 1, tx + 1, ty + 1),
                fill=(col[0], col[1], col[2], wa // 3),
            )

    # Ghostly soldier silhouettes emerging from the mist on either side
    for _ in range(6):
        sx = rng.randint(150, W - 150)
        sy = rng.randint(940, 1120)
        sa = rng.randint(15, 45)
        # Torso
        draw.ellipse((sx - 10, sy - 42, sx + 10, sy), fill=(55, 50, 45, sa))
        # Head with helmet
        draw.ellipse((sx - 8, sy - 62, sx + 8, sy - 42), fill=(55, 50, 45, sa))
        draw.arc((sx - 13, sy - 75, sx + 13, sy - 52), 180, 360, fill=(65, 60, 55, sa), width=3)
        # Rifle over shoulder
        draw.line(
            (sx + 8, sy - 22, sx + 45, sy - 8),
            fill=(45, 40, 35, sa),
            width=3,
        )

    # Half-buried unexploded shells in the mud (the "iron harvest")
    for _ in range(7):
        sx = rng.randint(40, W - 40)
        sy = rng.randint(1820, 2050)
        sa = rng.randint(-30, 30)
        sl = rng.randint(30, 55)
        ex = sx + int(sl * math.cos(math.radians(sa)))
        ey = sy + int(sl * math.sin(math.radians(sa)))
        draw.line(
            (sx, sy, ex, ey),
            fill=(85, 72, 48, rng.randint(140, 220)),
            width=7,
        )
        # Shell nose
        draw.ellipse(
            (ex - 4, ey - 4, ex + 4, ey + 4),
            fill=(105, 88, 55, rng.randint(140, 220)),
        )

    # Mud splatters and debris in extreme foreground
    for _ in range(50):
        mx = rng.randint(0, W)
        my = rng.randint(1950, H - 10)
        ms = rng.randint(3, 14)
        alpha = rng.randint(60, 140)
        mcol = (
            rng.randint(35, 60),
            rng.randint(22, 40),
            rng.randint(12, 24),
            alpha,
        )
        draw.ellipse((mx - ms, my - ms // 2, mx + ms, my + ms // 2), fill=mcol)

    # Faint fog layer near the horizon
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog)
    fd.ellipse((-200, 850, W + 200, 1400), fill=(160, 155, 145, 18))
    fd.ellipse((-200, 1000, W + 200, 1500), fill=(140, 135, 125, 12))
    fog = fog.filter(ImageFilter.GaussianBlur(50))
    img = Image.alpha_composite(img, fog)

    # Write output
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
