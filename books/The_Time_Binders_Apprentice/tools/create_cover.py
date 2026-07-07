#!/usr/bin/env python3
"""Cover: Edwardian boy in workshop before giant glowing brass clockwork machine, pocket watch in hand, London fog beyond window, workshop amber/brass-gold/fog gray."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[3]
FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560


def font(name: str, size: int):
    for c in [FONT_DIR / name, FONT_DIR / "georgia.ttf", FONT_DIR / "arial.ttf"]:
        if c.exists():
            try:
                from PIL import ImageFont
                return ImageFont.truetype(str(c), size)
            except Exception:
                pass
    from PIL import ImageFont

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


def lerp_color(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def wrap(draw, text, fnt, mw):
    words, lines, cur = text.split(), [], []
    for w in words:
        p = " ".join([*cur, w])
        bb = draw.textbbox((0, 0), p, font=fnt)
        if bb[2] <= mw:
            cur.append(w)
        else:
            lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def centered(draw, y, lines, fnt, fill, gap):
    for line in lines:
        bb = draw.textbbox((0, 0), line, font=fnt)
        draw.text(((W - (bb[2] - bb[0])) // 2, y), line, font=fnt, fill=fill)
        y += bb[3] - bb[1] + gap
    return y


def draw_gear(draw, cx, cy, inner_r, outer_r, teeth, angle_offset=0, fill=None, outline=None):
    """Draw a gear shape."""
    points = []
    for i in range(teeth * 2):
        a = angle_offset + (math.pi * i) / teeth
        r = outer_r if i % 2 == 0 else inner_r
        x = cx + r * math.cos(a)
        y = cy + r * math.sin(a)
        points.append((x, y))
    if fill:
        draw.polygon(points, fill=fill, outline=outline)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title, author = m["title"], m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Warm workshop gradient: amber-gold walls to dark wooden floor
    for y in range(H):
        t = y / H
        if t < 0.4:
            c = lerp_color((60, 40, 20), (100, 65, 30), t / 0.4)
        elif t < 0.7:
            c = lerp_color((100, 65, 30), (50, 30, 15), (t - 0.4) / 0.3)
        else:
            c = lerp_color((50, 30, 15), (20, 12, 8), (t - 0.7) / 0.3)
        draw.line((0, y, W, y), fill=c)

    # London fog seen through workshop window (back wall)
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog)
    for _ in range(40):
        fx = random.randint(100, W - 100)
        fy = random.randint(100, 600)
        fr = random.randint(60, 200)
        fd.ellipse([fx - fr, fy - fr, fx + fr, fy + fr],
                   fill=(160, 150, 140, random.randint(8, 25)))
    fog = fog.filter(ImageFilter.GaussianBlur(20))
    img = Image.alpha_composite(img, fog)
    draw = ImageDraw.Draw(img, "RGBA")

    # Distant city silhouette through fog
    for bx, bw, bh in [(100, 60, 300), (200, 40, 250), (350, 80, 350), (500, 50, 280),
                        (700, 70, 320), (850, 45, 260), (1000, 90, 380), (1200, 55, 300),
                        (1350, 65, 330), (1500, 50, 280)]:
        draw.rectangle([bx, 600 - bh, bx + bw, 600], fill=(40, 35, 30, 100))
        # small lit windows
        for wy in range(620 - bh, 590, 30):
            for wx in range(bx + 8, bx + bw - 8, 20):
                if random.random() > 0.5:
                    draw.rectangle([wx, wy, wx + 6, wy + 8], fill=(200, 180, 100, 60))

    # Giant brass clockwork machine (center)
    mach_cx, mach_cy = W // 2, 700
    # Outer glow
    for r in range(350, 0, -15):
        a = max(3, 80 - (350 - r) // 6)
        draw.ellipse([mach_cx - r, mach_cy - r, mach_cx + r, mach_cy + r],
                     fill=(200, 150, 50, max(0, a // 3)))
    # Main gear mechanism
    for i in range(8):
        angle = i * 45
        rad = math.radians(angle)
        gx = mach_cx + int(200 * math.cos(rad))
        gy = mach_cy + int(200 * math.sin(rad) * 0.4)
        draw_gear(draw, gx, gy, 20, 40, 8, angle_offset=rad,
                  fill=(180, 140, 60, 180), outline=(220, 180, 80, 200))
    # Central drive gear
    draw_gear(draw, mach_cx, mach_cy, 60, 100, 16, angle_offset=0,
              fill=(200, 160, 70, 200), outline=(230, 190, 90, 220))
    draw_gear(draw, mach_cx, mach_cy, 20, 50, 10, angle_offset=0.5,
              fill=(220, 180, 80, 220), outline=(240, 200, 100, 240))
    # Glowing core
    for r in range(40, 0, -3):
        a = max(5, 150 - (40 - r) * 6)
        draw.ellipse([mach_cx - r, mach_cy - r, mach_cx + r, mach_cy + r],
                     fill=(255, 220, 100, a))

    # Brass pipes and rods connecting gears
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        px = mach_cx + int(250 * math.cos(rad))
        py = mach_cy + int(250 * math.sin(rad) * 0.4)
        draw.line([(mach_cx, mach_cy), (px, py)], fill=(160, 120, 50, 150), width=5)

    # Workshop floor (wooden planks)
    for y in range(1300, 1800, 12):
        shade = int(35 + 20 * math.sin(y * 0.05))
        draw.line([(0, y), (W, y)], fill=(shade, shade - 5, shade - 10))
    # Floorboard gaps
    for x in range(0, W, 80):
        draw.line([(x, 1300), (x, 1800)], fill=(15, 10, 8, 80), width=2)

    # Edwardian boy (foreground, facing the machine)
    boy_cx, boy_base = W // 2 - 180, 1320
    # Shadow
    draw.ellipse([boy_cx - 25, boy_base - 5, boy_cx + 25, boy_base + 5], fill=(10, 8, 5, 100))
    # Legs
    draw.line([(boy_cx - 8, boy_base), (boy_cx - 10, boy_base - 80)], fill=(50, 40, 30), width=12)
    draw.line([(boy_cx + 8, boy_base), (boy_cx + 10, boy_base - 80)], fill=(50, 40, 30), width=12)
    # Torso (Edwardian jacket)
    draw.rectangle([boy_cx - 20, boy_base - 160, boy_cx + 20, boy_base - 80], fill=(60, 45, 35))
    # Jacket buttons
    for by in range(boy_base - 150, boy_base - 90, 15):
        draw.ellipse([boy_cx - 3, by, boy_cx + 3, by + 6], fill=(180, 160, 100))
    # Head
    draw.ellipse([boy_cx - 16, boy_base - 208, boy_cx + 16, boy_base - 165], fill=(200, 180, 160))
    # Hair (Edwardian side-part)
    draw.ellipse([boy_cx - 18, boy_base - 212, boy_cx + 18, boy_base - 190], fill=(40, 30, 20))
    # Flat cap
    draw.arc([boy_cx - 20, boy_base - 225, boy_cx + 20, boy_base - 195], 180, 0, fill=(50, 40, 30), width=6)
    draw.rectangle([boy_cx - 20, boy_base - 210, boy_cx + 20, boy_base - 205], fill=(50, 40, 30))
    # Arm reaching forward holding pocket watch
    draw.line([(boy_cx + 18, boy_base - 130), (boy_cx + 70, boy_base - 150)], fill=(60, 45, 35), width=8)
    # Pocket watch in hand
    watch_cx, watch_cy = boy_cx + 75, boy_base - 155
    draw.ellipse([watch_cx - 12, watch_cy - 12, watch_cx + 12, watch_cy + 12], fill=(200, 180, 120))
    draw.ellipse([watch_cx - 9, watch_cy - 9, watch_cx + 9, watch_cy + 9], fill=(220, 200, 140))
    # Watch face
    draw.ellipse([watch_cx - 6, watch_cy - 6, watch_cx + 6, watch_cy + 6], fill=(240, 230, 200))
    # Watch chain
    draw.line([(watch_cx, watch_cy + 12), (boy_cx + 5, boy_base - 100)], fill=(200, 180, 120), width=3)
    draw.line([(boy_cx + 5, boy_base - 100), (boy_cx, boy_base - 80)], fill=(200, 180, 120), width=3)
    # Watch glow
    for r in range(20, 0, -3):
        a = max(3, 40 - (20 - r) * 3)
        draw.ellipse([watch_cx - r, watch_cy - r, watch_cx + r, watch_cy + r],
                     fill=(255, 230, 150, a))

    # Light rays from machine toward boy
    for angle in range(-20, 20, 3):
        rad = math.radians(angle)
        for d in range(0, 300, 15):
            lx = mach_cx - int(d * math.sin(rad) * 0.5)
            ly = mach_cy + int(d * math.cos(rad) * 0.5)
            if ly > H or lx < 0:
                break
            a = max(2, 40 - d // 10)
            draw.point((lx, ly), fill=(255, 200, 80, a))

    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
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