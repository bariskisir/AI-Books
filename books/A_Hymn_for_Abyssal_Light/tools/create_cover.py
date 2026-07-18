#!/usr/bin/env python3
"""Cover: A Hymn for Abyssal Light — a deep-sea research team discovers an alien intelligence in the Mariana Trench that communicates through bioluminescent patterns."""

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
rng.seed(9147723561)

GLYPH_COLORS = [
    (0, 180, 255, 140),
    (100, 60, 255, 120),
    (0, 255, 140, 130),
    (255, 200, 60, 110),
]


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (5, 8, 30, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Gradient background: abyssal gradient (very dark at top, slightly brighter at bottom)
    for y in range(H):
        t = y / H
        r = int(5 + 25 * t)
        g = int(8 + 30 * t)
        b = int(30 + 55 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # Vignette
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(40 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 100))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 100))

    # === ALIEN STRUCTURE ON THE SEAFLOOR ===
    struct_cx = W // 2
    seafloor_y = 1920

    # Undulating seafloor base
    floor_pts = []
    for px in range(-50, W + 51, 10):
        py = seafloor_y + math.sin(px * 0.02) * 14 + math.sin(px * 0.05) * 5
        floor_pts.append((px, py))
    floor_pts.append((W + 50, H))
    floor_pts.append((-50, H))
    draw.polygon(floor_pts, fill=(8, 12, 28, 240))

    # Central alien spire (main temple/array structure)
    spire_w = 180
    spire_h = 380
    draw.polygon([
        (struct_cx - spire_w, seafloor_y),
        (struct_cx - spire_w + 30, seafloor_y - spire_h),
        (struct_cx + spire_w - 30, seafloor_y - spire_h),
        (struct_cx + spire_w, seafloor_y)
    ], fill=(12, 18, 38, 235))

    # Secondary spires
    for offset, sw, sh in [(-280, 70, 220), (280, 70, 220), (-400, 40, 120), (400, 40, 120)]:
        draw.polygon([
            (struct_cx + offset - sw, seafloor_y),
            (struct_cx + offset - sw // 2, seafloor_y - sh),
            (struct_cx + offset + sw // 2, seafloor_y - sh),
            (struct_cx + offset + sw, seafloor_y)
        ], fill=(10, 15, 32, 230))

    # Glowing "eye" at the center of the structure
    eye_y = seafloor_y - 280
    # Outer glow
    glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)
    gd.ellipse((struct_cx - 60, eye_y - 30, struct_cx + 60, eye_y + 30),
               fill=(0, 180, 255, 40))
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(25))
    img = Image.alpha_composite(img, glow_layer)
    draw = ImageDraw.Draw(img, "RGBA")
    # Bright core
    draw.ellipse((struct_cx - 18, eye_y - 12, struct_cx + 18, eye_y + 12),
                 fill=(180, 255, 255, 220))
    # Pupil detail
    draw.ellipse((struct_cx - 8, eye_y - 6, struct_cx + 8, eye_y + 6),
                 fill=(255, 255, 255, 180))

    # Glowing alien glyphs embedded in the spires
    glyph_positions = [
        (struct_cx - 100, seafloor_y - 270),
        (struct_cx + 100, seafloor_y - 270),
        (struct_cx - 220, seafloor_y - 150),
        (struct_cx + 220, seafloor_y - 150),
        (struct_cx, seafloor_y - 350),
        (struct_cx - 370, seafloor_y - 80),
        (struct_cx + 370, seafloor_y - 80),
    ]
    for gx, gy in glyph_positions:
        gcol = rng.choice(GLYPH_COLORS)
        gs = 12 + rng.randint(0, 10)
        shape = rng.choice(['triangle', 'diamond', 'chevron', 'cross'])
        if shape == 'triangle':
            draw.polygon([
                (gx, gy - gs),
                (gx - int(gs * 0.8), gy + int(gs * 0.6)),
                (gx + int(gs * 0.8), gy + int(gs * 0.6))
            ], fill=gcol)
        elif shape == 'diamond':
            draw.polygon([
                (gx, gy - gs),
                (gx - int(gs * 0.7), gy),
                (gx, gy + gs),
                (gx + int(gs * 0.7), gy)
            ], fill=gcol)
        elif shape == 'chevron':
            draw.polygon([
                (gx - gs, gy - int(gs * 0.5)),
                (gx, gy),
                (gx - gs, gy + int(gs * 0.5))
            ], fill=gcol)
            draw.polygon([
                (gx, gy - int(gs * 0.5)),
                (gx + gs, gy),
                (gx, gy + int(gs * 0.5))
            ], fill=gcol)
        else:  # cross
            draw.rectangle((gx - int(gs * 0.2), gy - gs, gx + int(gs * 0.2), gy + gs), fill=gcol)
            draw.rectangle((gx - gs, gy - int(gs * 0.2), gx + gs, gy + int(gs * 0.2)), fill=gcol)

    # Bioluminescent threads rising from the structure
    for _ in range(12):
        tx = struct_cx + rng.randint(-380, 380)
        ty = seafloor_y - rng.randint(50, 350)
        pts = [(tx, ty)]
        segs = rng.randint(4, 8)
        for _ in range(segs):
            nx = pts[-1][0] + rng.randint(-50, 50)
            ny = pts[-1][1] - rng.randint(20, 50)
            pts.append((nx, ny))
        tcol = rng.choice([(0, 200, 255, 35), (100, 100, 255, 30), (0, 255, 150, 25)])
        draw.line(pts, fill=tcol, width=rng.randint(2, 4))

    # === SUBMERSIBLE ===
    sub_x = struct_cx - 350
    sub_y = seafloor_y - 520
    # Hull
    draw.ellipse((sub_x - 35, sub_y - 14, sub_x + 35, sub_y + 14), fill=(55, 60, 70, 235))
    # Cockpit canopy
    draw.ellipse((sub_x + 8, sub_y - 10, sub_x + 32, sub_y + 10), fill=(80, 150, 230, 200))
    draw.ellipse((sub_x + 12, sub_y - 7, sub_x + 28, sub_y + 7), fill=(120, 200, 255, 180))
    # Thruster glow
    draw.ellipse((sub_x - 37, sub_y - 6, sub_x - 28, sub_y + 6), fill=(80, 120, 255, 100))
    # Antenna with red warning light
    draw.line((sub_x + 20, sub_y - 14, sub_x + 20, sub_y - 28), fill=(140, 150, 160, 180), width=2)
    draw.ellipse((sub_x + 17, sub_y - 32, sub_x + 23, sub_y - 26), fill=(255, 50, 50, 200))

    # Searchlight beams from sub
    for sl_angle, sl_offset in [(0.35, -4), (0.55, 4)]:
        beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        bd = ImageDraw.Draw(beam)
        beam_len = 450
        spread = 0.35
        sx = sub_x - 22
        sy = sub_y + sl_offset
        x1 = sx + int(math.cos(sl_angle - spread) * beam_len)
        y1 = sy + int(math.sin(sl_angle - spread) * beam_len)
        x2 = sx + int(math.cos(sl_angle + spread) * beam_len)
        y2 = sy + int(math.sin(sl_angle + spread) * beam_len)
        bd.polygon([(sx, sy), (x1, y1), (x2, y2)], fill=(200, 230, 255, 12))
        beam = beam.filter(ImageFilter.GaussianBlur(12))
        img = Image.alpha_composite(img, beam)
        draw = ImageDraw.Draw(img, "RGBA")

    # === FLOATING ALIEN GLYPHS IN WATER COLUMN ===
    for _ in range(rng.randint(10, 18)):
        gx = rng.randint(100, W - 100)
        gy = rng.randint(350, 1500)
        gcol = rng.choice([(0, 180, 255, 50), (100, 80, 255, 40), (0, 240, 150, 45), (255, 180, 50, 35)])
        gs = 6 + rng.randint(0, 8)
        draw.polygon([
            (gx, gy - gs),
            (gx - int(gs * 0.6), gy),
            (gx, gy + gs),
            (gx + int(gs * 0.6), gy)
        ], fill=gcol)

    # === BIOLUMINESCENT PLANKTON ===
    for _ in range(rng.randint(250, 400)):
        px = rng.randint(0, W)
        py = rng.randint(150, 2000)
        pr = rng.uniform(1.0, 3.5)
        pa = rng.randint(20, 90)
        pcol = rng.choice([(0, 200, 255), (120, 100, 255), (0, 255, 160), (255, 200, 80)])
        draw.ellipse((int(px - pr), int(py - pr), int(px + pr), int(py + pr)), fill=(*pcol, pa))

    # === FAINT SURFACE LIGHT RAYS ===
    for _ in range(rng.randint(3, 5)):
        sx = rng.randint(100, 1500)
        ray_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        rd = ImageDraw.Draw(ray_layer)
        rw = rng.randint(30, 100)
        ra = rng.uniform(-0.12, 0.12)
        rd.polygon([
            (sx - rw // 2, 0), (sx + rw // 2, 0),
            (sx + rw // 2 + int(math.sin(ra) * 600), 600),
            (sx - rw // 2 + int(math.sin(ra) * 600), 600)
        ], fill=(40, 100, 180, rng.randint(3, 8)))
        ray_layer = ray_layer.filter(ImageFilter.GaussianBlur(20))
        img = Image.alpha_composite(img, ray_layer)
        draw = ImageDraw.Draw(img, "RGBA")

    # === DEEP HAZE ===
    haze = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(haze)
    for _ in range(rng.randint(3, 6)):
        hx = rng.randint(100, W - 100)
        hy = rng.randint(1400, 2100)
        hr = rng.randint(150, 350)
        hcol = rng.choice([(0, 80, 180, 8), (40, 30, 120, 6), (0, 120, 80, 5)])
        hd.ellipse((hx - hr, hy - hr, hx + hr, hy + hr), fill=hcol)
    haze = haze.filter(ImageFilter.GaussianBlur(50))
    img = Image.alpha_composite(img, haze)

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
