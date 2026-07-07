#!/usr/bin/env python3
"""Cover: The Long Count — Older boxer's scarred face in shadow, one eye swollen, empty ring under single lamp, ring white/shadow black/blood red."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

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
FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560

def font(name: str, size: int):
    for candidate in (FONT_DIR / name, FONT_DIR / "arialbd.ttf", FONT_DIR / "arial.ttf"):
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()

def wrap(d, t, f, w):
    words, lines, cur = t.split(), [], []
    for wd in words:
        p = " ".join([*cur, wd])
        if d.textbbox((0, 0), p, font=f)[2] <= w: cur.append(wd)
        else: lines.append(" ".join(cur)); cur = [wd]
    if cur: lines.append(" ".join(cur))
    return lines

def centered(d, y, lines, f, fl, g):
    for l in lines:
        bb = d.textbbox((0, 0), l, font=f)
        d.text(((W - (bb[2] - bb[0])) // 2, y), l, font=f, fill=fl)
        y += bb[3] - bb[1] + g
    return y

def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    ti = m["title"]
    au = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        r = int(15 + 20 * t)
        g = int(12 + 15 * t)
        b = int(10 + 12 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    lamp_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lamp_layer, "RGBA")
    for r in range(500, 0, -15):
        a = int(20 * (1 - r / 500))
        ld.ellipse([W // 2 - r, 0, W // 2 + r, r * 2], fill=(255, 220, 150, max(0, a)))
    lamp_layer = lamp_layer.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, lamp_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    draw.line([(W // 2 - 4, 0), (W // 2 - 4, 80)], fill=(40, 40, 45), width=8)
    draw.line([(W // 2 + 4, 0), (W // 2 + 4, 80)], fill=(40, 40, 45), width=8)
    draw.rectangle([W // 2 - 60, 60, W // 2 + 60, 90], fill=(50, 50, 55))
    draw.rectangle([W // 2 - 40, 65, W // 2 + 40, 85], fill=(255, 230, 180, 200))

    ring_top = int(H * 0.65)
    draw.polygon([
        (150, ring_top), (W - 150, ring_top),
        (W - 100, H - 200), (100, H - 200),
    ], fill=(40, 40, 42))
    draw.polygon([
        (200, ring_top), (W - 200, ring_top),
        (W - 120, H - 200), (120, H - 200),
    ], fill=(25, 25, 28))

    face_cx, face_cy = W // 2, int(H * 0.42)
    face_color = (60, 45, 40)
    draw.ellipse([face_cx - 55, face_cy - 65, face_cx + 55, face_cy + 55],
                  fill=face_color)

    jaw_pts = [
        (face_cx - 45, face_cy - 20), (face_cx - 50, face_cy + 30),
        (face_cx - 35, face_cy + 50), (face_cx + 35, face_cy + 50),
        (face_cx + 50, face_cy + 30), (face_cx + 45, face_cy - 20),
    ]
    draw.polygon(jaw_pts, fill=face_color)

    draw.ellipse([face_cx - 18, face_cy - 22, face_cx - 2, face_cy - 6],
                  fill=(30, 25, 22))
    draw.ellipse([face_cx + 2, face_cy - 22, face_cx + 18, face_cy - 6],
                  fill=(30, 25, 22))

    eye_right_cx, eye_right_cy = face_cx + 10, face_cy - 14
    draw.ellipse([eye_right_cx - 6, eye_right_cy - 4, eye_right_cx + 6, eye_right_cy + 4],
                  fill=(20, 18, 15))

    eye_left_cx, eye_left_cy = face_cx - 10, face_cy - 14
    draw.ellipse([eye_left_cx - 8, eye_left_cy - 5, eye_left_cx + 8, eye_left_cy + 5],
                  fill=(20, 18, 15))
    draw.ellipse([eye_left_cx - 10, eye_left_cy - 7, eye_left_cx + 10, eye_left_cy + 7],
                  fill=(120, 40, 30, 120))

    draw.line([(face_cx - 25, face_cy + 10), (face_cx + 25, face_cy + 8)],
               fill=(40, 30, 28), width=2)

    for scar in [
        (face_cx - 30, face_cy - 10, face_cx + 10, face_cy - 5),
        (face_cx - 10, face_cy + 15, face_cx + 20, face_cy + 5),
        (face_cx - 5, face_cy - 35, face_cx - 2, face_cy - 20),
    ]:
        draw.line([(scar[0], scar[1]), (scar[2], scar[3])],
                   fill=(80, 50, 40, 120), width=2)

    draw.polygon([
        (face_cx - 8, face_cy + 55), (face_cx + 8, face_cy + 55),
        (face_cx + 12, face_cy + 85), (face_cx - 12, face_cy + 85),
    ], fill=(50, 40, 38))
    draw.polygon([
        (face_cx - 8, face_cy + 55), (face_cx - 30, face_cy + 65),
        (face_cx - 25, face_cy + 75), (face_cx - 8, face_cy + 65),
    ], fill=(40, 35, 32))

    draw.rectangle((0, 1920, W, H), fill=(15, 10, 8, 235))
    draw.line((300, 1960, W - 300, 1960), fill=(180, 40, 30, 150), width=2)

    tf = font("arialbd.ttf", 85)
    af = font("arialbd.ttf", 36)
    title_lines = wrap(draw, ti.upper(), tf, 1300)
    y = centered(draw, 1980, title_lines, tf, (200, 200, 200), 10)
    y += 50
    bb = draw.textbbox((0, 0), au, font=af)
    draw.text(((W - (bb[2] - bb[0])) // 2, y), au, font=af, fill=(180, 170, 160))

    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op, "PNG", optimize=True)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    make_cover(
        ROOT / a.metadata if not a.metadata.is_absolute() else a.metadata,
        ROOT / a.out if not a.out.is_absolute() else a.out,
    )

if __name__ == "__main__":
    main()
