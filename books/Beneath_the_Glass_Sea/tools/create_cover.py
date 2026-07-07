#!/usr/bin/env python3
"""Cover: Beneath the Glass Sea — underwater colony bio-dome, bioluminescent jellyfish, glass architecture, deep teal/cyan."""

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

    img = Image.new("RGBA", (W, H), (8, 60, 72, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        r = int(12 + (6 - 12) * t)
        g = int(80 + (40 - 80) * t)
        b = int(95 + (55 - 95) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for _ in range(8):
        cx = random.randint(200, 1400)
        cy = random.randint(200, 1500)
        rad = random.randint(60, 180)
        gd.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=(100, 220, 230, 12))
    glow = glow.filter(ImageFilter.GaussianBlur(25))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    dome_cx, dome_cy = W // 2, 600
    draw.arc((dome_cx - 520, dome_cy - 100, dome_cx + 520, dome_cy + 500), 0, 180, fill=(140, 230, 235, 80), width=8)
    for x in range(dome_cx - 480, dome_cx + 481, 80):
        draw.arc((x, dome_cy - 80, x + 80, dome_cy + 460), 0, 180, fill=(160, 235, 240, 50), width=4)
    for wx in range(dome_cx - 400, dome_cx + 401, 60):
        draw.line((wx, dome_cy - 60, wx, dome_cy + 420), fill=(180, 240, 245, 40), width=2)

    for _ in range(18):
        jx = random.randint(100, 1500)
        jy = random.randint(300, 1600)
        jr = random.randint(12, 35)
        alpha = random.randint(100, 200)
        rcol = random.choice([(200, 230, 255), (180, 255, 220), (160, 200, 255), (220, 180, 255)])
        draw.ellipse((jx - jr, jy - jr, jx + jr, jy + jr), fill=(*rcol, alpha // 2))
        draw.ellipse((jx - jr // 2, jy - jr // 2, jx + jr // 2, jy + jr // 2), fill=(*rcol, alpha))
        for _ in range(6):
            ang = random.random() * math.tau
            tx = jx + math.cos(ang) * jr * 1.8
            ty = jy + math.sin(ang) * jr * 1.8
            draw.line((jx, jy, tx, ty), fill=(*rcol, alpha // 2), width=2)

    seafloor = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(seafloor)
    for x in range(0, W, 40):
        h = 60 + random.randint(0, 80)
        sd.ellipse((x - 60, 1700 - h // 2, x + 60, 1765), fill=(20, 70, 60, 220))
    img = Image.alpha_composite(img, seafloor)
    draw = ImageDraw.Draw(img, "RGBA")

    for _ in range(60):
        x = random.randint(0, W)
        y = random.randint(100, 1700)
        r = random.randint(2, 5)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(120, 230, 240, random.randint(30, 90)))

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
