#!/usr/bin/env python3
"""Cover: Songs My Mother Sold — A jukebox repairman in coastal Kerala realizes every broken jukebox he fixes plays songs not from its records but from the suppressed memories of whoever is near it."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# ── Kerala sunset palette ──────────────────────────────────────────────────
# Deep night sky at top → warm magenta/orange sunset → golden horizon
# → coconut palm greens → ocean teal → dark coastal waters
SKY_TOP = (25, 15, 55)       # deep indigo night
SKY_MID = (130, 40, 70)      # magenta-purple sunset
SKY_HORIZON = (220, 150, 50) # gold at horizon
SEA_TOP = (30, 70, 90)       # teal ocean
SEA_BOTTOM = (10, 25, 45)    # dark deep water

VOICE_GLOW = (255, 220, 120)
MEMORY_WHITE = (230, 235, 240)
PALM_GREEN = (35, 70, 35)
JUKEBOX_WOOD = (65, 30, 15)
NOTE_GOLD = (255, 200, 80)

rng = random.Random()
rng.seed(1820794957)


def draw_gradient_background(draw):
    """Kerala sunset sky blending into ocean."""
    # Sky gradient: night → magenta → gold
    for y in range(0, 1300):
        t = y / 1300
        if t < 0.5:
            t2 = t * 2.0
            r = int(SKY_TOP[0] + (SKY_MID[0] - SKY_TOP[0]) * t2)
            g = int(SKY_TOP[1] + (SKY_MID[1] - SKY_TOP[1]) * t2)
            b = int(SKY_TOP[2] + (SKY_MID[2] - SKY_TOP[2]) * t2)
        else:
            t2 = (t - 0.5) * 2.0
            r = int(SKY_MID[0] + (SKY_HORIZON[0] - SKY_MID[0]) * t2)
            g = int(SKY_MID[1] + (SKY_HORIZON[1] - SKY_MID[1]) * t2)
            b = int(SKY_MID[2] + (SKY_HORIZON[2] - SKY_MID[2]) * t2)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # Ocean gradient
    for y in range(1300, H):
        t = (y - 1300) / (H - 1300)
        r = int(SEA_TOP[0] + (SEA_BOTTOM[0] - SEA_TOP[0]) * t)
        g = int(SEA_TOP[1] + (SEA_BOTTOM[1] - SEA_TOP[1]) * t)
        b = int(SEA_TOP[2] + (SEA_BOTTOM[2] - SEA_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))


def draw_sun(draw):
    """Setting sun at the horizon casting a warm reflection across the water."""
    cx, cy = W // 2, 1280
    # Glow layers
    for r, a in [(180, 40), (120, 60), (70, 80), (40, 100)]:
        draw.ellipse((cx - r, cy - r, cx + r, cy + r),
                     fill=(255, 200, 80, a // 4))
    # Core sun
    sun_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sun_layer)
    sd.ellipse((cx - 55, cy - 55, cx + 55, cy + 55), fill=(255, 195, 70, 200))
    sd.ellipse((cx - 35, cy - 35, cx + 35, cy + 35), fill=(255, 220, 120, 230))
    sd.ellipse((cx - 18, cy - 18, cx + 18, cy + 18), fill=(255, 240, 200, 255))
    sun_layer = sun_layer.filter(ImageFilter.GaussianBlur(4))
    draw._image.paste(sun_layer, (0, 0), sun_layer)

    # Sun reflection on water
    for i in range(16):
        ox = cx + rng.randint(-60, 60)
        oy = 1290 + i * rng.randint(8, 20)
        ow = rng.randint(8, 40)
        oh = rng.randint(3, 8)
        alpha = int(160 * max(0, 1 - i / 16))
        draw.ellipse((ox - ow // 2, oy, ox + ow // 2, oy + oh),
                     fill=(255, 210, 90, alpha // 2))


def draw_palm_silhouettes(draw):
    """Coconut palm silhouettes framing the edges against the sunset."""
    for side in (-1, 1):
        base_x = W // 2 + side * (500 + rng.randint(0, 120))
        trunk_h = rng.randint(300, 500)
        # Curved trunk
        pts = []
        for i in range(trunk_h):
            t = i / trunk_h
            sway = side * int(40 * math.sin(t * math.pi * 0.6))
            px = base_x + sway
            py = 1280 - i
            pts.append((px, py))
        if len(pts) > 1:
            # Trunk shadow
            draw.line(pts, fill=(*PALM_GREEN, 180), width=rng.randint(5, 10))
            # Fronds
            frond_count = rng.randint(4, 7)
            for fi in range(frond_count):
                angle = math.radians(-30 + fi * 15 + rng.randint(-10, 10))
                frond_len = rng.randint(80, 160)
                fx, fy = pts[-1]
                fex = fx + side * int(math.cos(angle) * frond_len)
                fey = fy - int(math.sin(angle) * frond_len * 0.4)
                # Drooping frond
                fpts = [(fx, fy)]
                for step in range(1, 12):
                    st = step / 11
                    mx = fx + (fex - fx) * st
                    my = fy + (fey - fy) * st + int(15 * math.sin(st * math.pi))
                    fpts.append((int(mx), int(my)))
                draw.line(fpts, fill=(*PALM_GREEN, 200), width=rng.randint(3, 6))


def draw_jukebox(draw):
    """Vintage jukebox silhouette as the central focal point."""
    bx, by = W // 2, 1400  # base center, bottom of jukebox
    jukebox_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    jd = ImageDraw.Draw(jukebox_layer)

    base_w, base_h = 120, 30
    body_w, body_h = 160, 300
    top_w, top_h = 140, 60
    arch_h = 90

    jb_x = bx - body_w // 2
    jb_y = by - base_h - body_h - arch_h

    # Arch top (the iconic Wurlitzer bubble tube arch)
    jd.arc((jb_x - 10, jb_y - arch_h, jb_x + body_w + 10, jb_y + top_h),
           -180, 0, fill=(*JUKEBOX_WOOD, 220), width=8)

    # Body
    jd.rectangle((jb_x, jb_y + top_h, jb_x + body_w, jb_y + top_h + body_h),
                 fill=(*JUKEBOX_WOOD, 230))
    # Inner arch (glass front)
    jd.arc((jb_x + 15, jb_y - arch_h + 20, jb_x + body_w - 15, jb_y + top_h),
           -180, 0, fill=(*MEMORY_WHITE, 60), width=4)
    # Glass glow
    jd.rectangle((jb_x + 20, jb_y + 20, jb_x + body_w - 20, jb_y + top_h + body_h - 20),
                 fill=(*MEMORY_WHITE, 25))
    # Record inside glow
    jd.ellipse((bx - 30, jb_y + 60, bx + 30, jb_y + 120),
               fill=(*NOTE_GOLD, 40))

    # Chrome trim strips
    for trim_x in (jb_x, jb_x + body_w):
        jd.rectangle((trim_x, jb_y + top_h, trim_x + 4, jb_y + top_h + body_h),
                     fill=(160, 120, 60, 200))
    # Base
    jd.rectangle((bx - base_w // 2, by - base_h, bx + base_w // 2, by),
                 fill=(45, 20, 8, 230))
    # Chrome feet
    for fx in (bx - base_w // 2 + 10, bx + base_w // 2 - 10):
        jd.ellipse((fx - 8, by - 8, fx + 8, by + 4), fill=(120, 100, 80, 220))

    # Inner glow (jukebox lit up)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((bx - 100, by - 350, bx + 100, by - 100),
               fill=(*NOTE_GOLD, 12))
    glow = glow.filter(ImageFilter.GaussianBlur(30))
    jukebox_layer = Image.alpha_composite(jukebox_layer, glow)

    draw._image.paste(jukebox_layer, (0, 0), jukebox_layer)


def draw_memory_music_notes(draw):
    """Musical notes rising from the jukebox, transforming into translucent human memories."""
    note_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(note_layer)

    # Musical notes floating up
    note_positions = []
    for _ in range(rng.randint(18, 28)):
        angle = math.radians(rng.uniform(-35, 35))
        dist = rng.randint(80, 550)
        nx = W // 2 + int(math.sin(angle) * dist)
        ny = 1400 - 300 - rng.randint(0, 450)
        note_positions.append((nx, ny))

    for nx, ny in note_positions:
        size = rng.randint(10, 25)
        alpha = rng.randint(60, 180)
        # Note head (filled ellipse)
        nd.ellipse((nx - size, ny - size // 2, nx, ny + size // 2),
                   fill=(*NOTE_GOLD, alpha))
        # Note stem
        stem_h = size * 2
        nd.line((nx, ny - size // 2, nx, ny - size // 2 - stem_h),
                fill=(*NOTE_GOLD, alpha), width=max(2, size // 5))
        # Flag for some notes
        if rng.random() < 0.4:
            nd.arc((nx, ny - size // 2 - stem_h, nx + size, ny - size // 2 - stem_h + size),
                   180, 0, fill=(*NOTE_GOLD, alpha), width=2)

        # Glow around each note
        nd.ellipse((nx - size * 2, ny - size * 2, nx + size * 2, ny + size * 2),
                   fill=(*NOTE_GOLD, alpha // 8))

    # Memory wisps — translucent human silhouettes emerging from the jukebox music
    for mi in range(5):
        base_angle = rng.uniform(-40, 40)
        base_dist = rng.uniform(60, 400)
        mx = W // 2 + int(math.sin(math.radians(base_angle)) * base_dist)
        my = 1400 - 320 - rng.randint(0, 300)  # above jukebox
        wisp_height = rng.randint(100, 180)
        wisp_alpha = rng.randint(20, 60)

        # Head
        head_r = rng.randint(10, 16)
        nd.ellipse((mx - head_r, my - wisp_height,
                    mx + head_r, my - wisp_height + head_r * 2),
                   fill=(*MEMORY_WHITE, wisp_alpha))
        # Body (trapezoid-ish)
        body_w = rng.randint(12, 20)
        nd.polygon([
            (mx - body_w, my - wisp_height + head_r * 2),
            (mx + body_w, my - wisp_height + head_r * 2),
            (mx + body_w + 4, my),
            (mx - body_w - 4, my),
        ], fill=(*MEMORY_WHITE, wisp_alpha // 2))

        # Drifting wisp trail below each figure (they're dissolving into memory)
        for ti in range(8):
            tt = ti / 8
            tx = mx + int(8 * math.sin(tt * math.pi * 2 + mi))
            ty = my + int(tt * 200)
            tr = int(6 * (1 - tt))
            if tr > 1:
                nd.ellipse((tx - tr, ty - tr, tx + tr, ty + tr),
                           fill=(*MEMORY_WHITE, int(wisp_alpha * (0.3 - tt * 0.25))))

    # Connect some notes to memory wisps with thin glowing lines
    for _ in range(6):
        if len(note_positions) < 2:
            break
        n1 = note_positions[rng.randint(0, len(note_positions) - 1)]
        n2 = note_positions[rng.randint(0, len(note_positions) - 1)]
        nd.line((n1[0], n1[1], n2[0], n2[1]),
                fill=(*NOTE_GOLD, rng.randint(8, 20)), width=1)

    draw._image.paste(note_layer, (0, 0), note_layer)


def draw_coastal_elements(draw):
    """Backwater reflections, distant houseboats, and shoreline vegetation."""
    # Distant houseboat silhouettes on the water
    boat_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(boat_layer)

    for _ in range(rng.randint(3, 5)):
        bx = rng.randint(100, W - 100)
        by = 1320 + rng.randint(0, 80)
        b_len = rng.randint(40, 70)
        b_h = rng.randint(10, 16)
        # Hull
        bd.ellipse((bx - b_len // 2, by, bx + b_len // 2, by + b_h),
                   fill=(*PALM_GREEN, rng.randint(60, 120)))
        # Cabin
        cab_w = rng.randint(15, 25)
        bd.rectangle((bx - cab_w // 2, by - b_h, bx + cab_w // 2, by),
                     fill=(*PALM_GREEN, rng.randint(80, 130)))
        # Reflection
        reflect_y = by + b_h + rng.randint(2, 8)
        bd.ellipse((bx - b_len // 2, reflect_y, bx + b_len // 2, reflect_y + b_h),
                   fill=(*PALM_GREEN, rng.randint(20, 40)))

    # Water ripples
    for _ in range(rng.randint(30, 50)):
        rx = rng.randint(0, W)
        ry = rng.randint(1310, 1720)
        rw = rng.randint(20, 80)
        col = (rng.randint(60, 130), rng.randint(80, 160), rng.randint(100, 200))
        bd.arc((rx - rw, ry - 3, rx + rw, ry + 3),
               0, 180, fill=(*col, rng.randint(15, 40)), width=1)

    # Firefly sparkles (magical realism touches)
    for _ in range(rng.randint(50, 80)):
        sx = rng.randint(0, W)
        sy = rng.randint(300, 1700)
        sr = rng.randint(1, 4)
        alpha = rng.randint(40, 150)
        bd.ellipse((sx - sr, sy - sr, sx + sr, sy + sr),
                   fill=(*NOTE_GOLD, alpha))

    draw._image.paste(boat_layer, (0, 0), boat_layer)


def draw_vignette(draw):
    """Subtle dark vignette around the edges to focus attention."""
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(50 * max(0, 0.7 - vt * 0.5))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 90))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 90))


def draw_woman_in_song_7(draw):
    """Ethereal silhouette of 'The Woman in Song 7' — a faint ghostly female figure
    emerging from the jukebox glow, her form made of translucent memory particles."""
    wx = W // 2 - rng.randint(80, 160)
    wy = 1300 - 350  # floating above and to the left

    woman_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(woman_layer)

    figure_alpha = rng.randint(40, 70)

    # Head
    hr = 14
    wd.ellipse((wx - hr, wy - 180, wx + hr, wy - 180 + hr * 2),
               fill=(*MEMORY_WHITE, figure_alpha))

    # Hair flowing (Kerala woman with long hair)
    for si in range(-1, 2, 2):
        hx = wx + si * hr
        for hi in range(5):
            tt = hi / 5
            by = wy - 175 + tt * 80 + 5 * math.sin(tt * math.pi)
            bx = hx + si * int(10 + tt * 30 + 8 * math.sin(tt * math.pi * 1.5))
            wd.line((hx, wy - 175 + hi * 15, bx, by),
                    fill=(*MEMORY_WHITE, figure_alpha // 2), width=2)

    # Sari-clad body
    body_pts = [
        (wx - 18, wy - 150),  # shoulders
        (wx - 12, wy - 170),  # neck
        (wx + 12, wy - 170),  # neck
        (wx + 18, wy - 150),  # shoulders
        (wx + 25, wy - 80),   # right hip
        (wx + 20, wy - 40),   # right foot area
        (wx - 20, wy - 40),   # left foot area
        (wx - 25, wy - 80),   # left hip
    ]
    wd.polygon(body_pts, fill=(*MEMORY_WHITE, figure_alpha // 2))

    # Sari drape (one side lower, flowing)
    sari_pts = [
        (wx - 18, wy - 150),
        (wx - 30, wy - 100),
        (wx - 35, wy - 50),
        (wx - 28, wy - 40),
        (wx - 20, wy - 40),
        (wx - 25, wy - 80),
    ]
    wd.polygon(sari_pts, fill=(*VOICE_GLOW, figure_alpha // 3))

    # Particles dissolving from the woman (she's a memory, not solid)
    for _ in range(rng.randint(15, 25)):
        px = wx + rng.randint(-60, 60)
        py = wy - 180 + rng.randint(0, 150)
        pr = rng.randint(1, 4)
        wd.ellipse((px - pr, py - pr, px + pr, py + pr),
                   fill=(*MEMORY_WHITE, rng.randint(20, 60)))

    draw._image.paste(woman_layer, (0, 0), woman_layer)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (25, 15, 55, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Layer 1: Sky and ocean gradient
    draw_gradient_background(draw)

    # Layer 2: Setting sun with water reflection
    draw_sun(draw)

    # Layer 3: Coconut palm silhouettes
    draw_palm_silhouettes(draw)

    # Layer 4: Central jukebox
    draw_jukebox(draw)

    # Layer 5: Musical notes transforming into memory wisps
    draw_memory_music_notes(draw)

    # Layer 6: The Woman in Song 7 (ghostly figure)
    draw_woman_in_song_7(draw)

    # Layer 7: Coastal elements (houseboats, ripples, fireflies)
    draw_coastal_elements(draw)

    # Layer 8: Vignette
    draw_vignette(draw)

    # Final: cream title panel
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
