#!/usr/bin/env python3
"""Cover: The Clockwork Rabbi — Clay Golem with brass clockwork gears in chest, Prague Gothic skyline, blood moon, earthen browns/brass/indigo."""

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

def wrap(draw, text, fnt, max_width):
    words, lines, cur = text.split(), [], []
    for w in words:
        p = " ".join([*cur, w])
        if draw.textbbox((0, 0), p, font=fnt)[2] <= max_width:
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

def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (18, 12, 28, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        if t < 0.5:
            r = int(18 + 20 * t * 2)
            g = int(12 + 15 * t * 2)
            b = int(28 + 10 * t * 2)
        else:
            r = int(38 + 30 * (t - 0.5) * 2)
            g = int(27 + 25 * (t - 0.5) * 2)
            b = int(38 - 10 * (t - 0.5) * 2)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    moon_cx, moon_cy = 1100, 180
    for r in range(200, 40, -10):
        alpha = max(5, 120 - r)
        draw.ellipse((moon_cx - r, moon_cy - r, moon_cx + r, moon_cy + r), fill=(160, 20, 25, alpha))
    draw.ellipse((moon_cx - 70, moon_cy - 70, moon_cx + 70, moon_cy + 70), fill=(200, 40, 45, 240))
    draw.ellipse((moon_cx - 55, moon_cy - 55, moon_cx + 55, moon_cy + 55), fill=(230, 60, 55, 230))

    spires = [
        (200, 600, 18, 380), (280, 580, 14, 320), (360, 560, 20, 400),
        (480, 550, 16, 360), (600, 540, 22, 440), (740, 570, 15, 340),
        (860, 530, 20, 420), (1000, 560, 14, 310), (1120, 540, 18, 380),
        (1240, 580, 16, 330), (1360, 560, 20, 400), (1480, 590, 14, 300),
    ]
    for sx, sy, sw, sh in spires:
        draw.polygon([(sx - sw, sy + sh), (sx, sy), (sx + sw, sy + sh)], fill=(10, 8, 20, 240))
        draw.rectangle((sx - sw // 2, sy + sh, sx + sw // 2, sy + sh + 200), fill=(12, 10, 22, 240))

    golem_cx, golem_cy = W // 2, 900
    draw.ellipse((golem_cx - 110, golem_cy - 220, golem_cx + 110, golem_cy + 60), fill=(95, 68, 48, 240))
    draw.ellipse((golem_cx - 120, golem_cy - 30, golem_cx + 120, golem_cy + 120), fill=(88, 62, 44, 240))
    draw.rectangle((golem_cx - 100, golem_cy + 100, golem_cx + 100, golem_cy + 350), fill=(82, 58, 40, 240))

    for _ in range(3):
        ax = golem_cx + random.choice([-95, 95])
        ay = golem_cy + random.randint(60, 200)
        draw.polygon([(ax, ay), (ax + random.choice([-60, 60]), ay + 100), (ax, ay + 120)], fill=(75, 52, 36, 240))

    cx, cy = golem_cx, golem_cy + 40
    for r in range(48, 16, -4):
        alpha = 120 - r
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(180, 140, 60, alpha))
    for i in range(14):
        ang = math.radians(i * 360 / 14)
        gx = cx + math.cos(ang) * 30
        gy = cy + math.sin(ang) * 30
        draw.ellipse((gx - 5, gy - 5, gx + 5, gy + 5), fill=(200, 160, 70, 180))
    draw.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=(240, 200, 80, 220))

    draw.ellipse((golem_cx - 35, golem_cy - 160, golem_cx - 10, golem_cy - 125), fill=(240, 210, 150, 200))
    draw.ellipse((golem_cx + 10, golem_cy - 160, golem_cx + 35, golem_cy - 125), fill=(240, 210, 150, 200))
    draw.ellipse((golem_cx - 18, golem_cy - 148, golem_cx - 12, golem_cy - 140), fill=(30, 25, 20, 240))
    draw.ellipse((golem_cx + 12, golem_cy - 148, golem_cx + 18, golem_cy - 140), fill=(30, 25, 20, 240))

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
