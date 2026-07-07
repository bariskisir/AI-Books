#!/usr/bin/env python3
"""Cover: The Endgame Paradox — Chessboard mid-game, pawn advancing under dramatic lighting, bold serif title, black/ivory/dramatic amber."""

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

    img = Image.new("RGBA", (W, H), (20, 18, 15, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        r = int(20 + (180 - 20) * t)
        g = int(18 + (160 - 18) * t)
        b = int(15 + (130 - 15) * t)
        if t > 0.6:
            fade = (t - 0.6) / 0.4
            r = int(180 - 80 * fade)
            g = int(160 - 70 * fade)
            b = int(130 - 60 * fade)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    board_top, board_left = 400, 200
    sq = 100
    for row in range(8):
        for col in range(8):
            x = board_left + col * sq
            y = board_top + row * sq
            colr = (200, 185, 160) if (row + col) % 2 == 0 else (50, 45, 38)
            draw.rectangle((x, y, x + sq, y + sq), fill=colr)

    for pcol, ptype, px, py in [
        ("b", "rook", 2, 0), ("w", "knight", 4, 1), ("b", "bishop", 5, 0),
        ("w", "pawn", 3, 3), ("b", "pawn", 4, 3), ("b", "king", 4, 0),
        ("w", "queen", 3, 1), ("w", "pawn", 1, 3), ("b", "knight", 6, 1),
    ]:
        cx = board_left + px * sq + sq // 2
        cy = board_top + py * sq + sq // 2
        colr = (220, 210, 190) if pcol == "w" else (30, 28, 24)
        r = 28
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=colr)
        draw.ellipse((cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4), fill=(colr[0] + 20 if pcol == "w" else colr[0] - 5, colr[1] + 18 if pcol == "w" else colr[1] - 4, colr[2] + 15 if pcol == "w" else colr[2] - 3))

    light = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(light)
    ld.polygon([(380, 0), (480, 0), (600, 1200), (300, 1200)], fill=(255, 200, 100, 25))
    light = light.filter(ImageFilter.GaussianBlur(12))
    img = Image.alpha_composite(img, light)

    pawn_cx = board_left + 3 * sq + sq // 2
    pawn_cy = board_top + 3 * sq + sq // 2
    pshadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    psd = ImageDraw.Draw(pshadow)
    psd.ellipse((pawn_cx - 8, pawn_cy - 30, pawn_cx + 8, pawn_cy + 10), fill=(255, 200, 80, 180))
    for r in range(15, 0, -1):
        psd.ellipse((pawn_cx - r - 4, pawn_cy - r - 30, pawn_cx + r + 4, pawn_cy + r + 10), fill=(255, 200, 80, 5))
    img = Image.alpha_composite(img, pshadow)

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
