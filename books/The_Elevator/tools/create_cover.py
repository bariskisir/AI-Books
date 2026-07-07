#!/usr/bin/env python3
"""Cover: The Elevator — Dark elevator interior, glowing red 59:59 countdown, shadowed passenger silhouette, black/red/fluorescent white."""

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

    img = Image.new("RGBA", (W, H), (8, 8, 10, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        r = int(8 + (2 - 8) * t)
        g = int(8 + (2 - 8) * t)
        b = int(10 + (4 - 10) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    wl, wr, wt, wb = int(W * 0.12), int(W * 0.88), int(H * 0.10), int(H * 0.75)
    draw.rectangle((wl, wt, wr, wb), fill=(50, 48, 44), outline=(80, 76, 72), width=2)
    py = wt + 70
    for i in range(4):
        draw.line(((wl + 10, py), (wr - 10, py)), fill=(65, 62, 58), width=1)
        py += 70
    for x in range(wl + 50, wr, 110):
        draw.line(((x, wt), (x, wb)), fill=(60, 57, 53), width=1)

    draw.rectangle((wl, wb, wr, H), fill=(35, 32, 28), outline=(45, 42, 38), width=1)
    for ty in range(wb + 15, H, 25):
        draw.line(((wl, ty), (wr, ty)), fill=(40, 37, 32), width=1)

    dl, dr = int(W * 0.36), int(W * 0.64)
    draw.rectangle((dl, wt, dr, wb), fill=(42, 40, 36), outline=(85, 80, 75), width=3)
    draw.rectangle((dl + 5, wt + 5, (dl + dr) // 2 - 2, wb - 5), fill=(55, 52, 48), outline=(75, 70, 65), width=1)
    draw.rectangle(((dl + dr) // 2 + 2, wt + 5, dr - 5, wb - 5), fill=(55, 52, 48), outline=(75, 70, 65), width=1)
    draw.rectangle((dl + 12, wt + 25, dr - 12, wt + 110), fill=(20, 20, 28), outline=(85, 80, 75), width=2)

    panel_x = int(W * 0.74)
    panel_y = wb - 150
    draw.rectangle((panel_x, panel_y, panel_x + 60, panel_y + 130), fill=(35, 33, 30), outline=(85, 80, 75), width=2)
    draw.rectangle((panel_x + 6, panel_y + 8, panel_x + 54, panel_y + 48), fill=(8, 6, 6), outline=(50, 46, 42), width=1)

    countdown = "59:59"
    for gr in range(4, 0, -1):
        for dx in (-gr, gr):
            draw.text((panel_x + 18 + dx, panel_y + 16), countdown, font=font("arialbd.ttf", 26), fill=(60, 0, 0, 20 // gr))
        for dy in (-gr, gr):
            draw.text((panel_x + 18, panel_y + 16 + dy), countdown, font=font("arialbd.ttf", 26), fill=(60, 0, 0, 20 // gr))
    draw.text((panel_x + 18, panel_y + 16), countdown, font=font("arialbd.ttf", 26), fill=(255, 30, 30))

    sil = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sil)
    sx, sy = W // 2, wb - 50
    sd.ellipse((sx - 10, sy - 28, sx + 10, sy - 4), fill=(12, 10, 8, 230))
    sd.polygon([(sx - 14, sy - 4), (sx + 14, sy - 4), (sx + 16, sy + 40), (sx - 16, sy + 40)], fill=(14, 12, 10, 230))
    sd.line((sx - 10, sy, sx - 20, sy + 18), fill=(14, 12, 10, 230), width=5)
    sd.line((sx + 10, sy, sx + 20, sy + 18), fill=(14, 12, 10, 230), width=5)
    sd.line((sx - 8, sy + 40, sx - 12, sy + 60), fill=(14, 12, 10, 230), width=5)
    sd.line((sx + 8, sy + 40, sx + 12, sy + 60), fill=(14, 12, 10, 230), width=5)
    img = Image.alpha_composite(img, sil)

    for r in range(8, 0, -1):
        draw.ellipse((panel_x + 15 - r, panel_y + 12 - r, panel_x + 55 + r, panel_y + 45 + r), outline=(200, 80, 0, 15 // (r + 1)), width=1)

    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op, "PNG", optimize=True)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    metadata_path = ROOT / args.metadata if not args.metadata.is_absolute() else args.metadata
    output_path = ROOT / args.out if not args.out.is_absolute() else args.out
    make_cover(metadata_path, output_path)

if __name__ == "__main__":
    main()
