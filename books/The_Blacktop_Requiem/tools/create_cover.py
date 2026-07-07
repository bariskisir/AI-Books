#!/usr/bin/env python3
"""Cover: The Blacktop Requiem — Desert highway at dusk, abandoned car, red taillights fading into horizon."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import (
    _standard_cover_font, _standard_cover_repair_text, _standard_cover_wrap,
    _standard_cover_center, _standard_cover_title_font,
    _standard_cover_metadata_from_locals,
    _standard_cover_resolve_title, _standard_cover_resolve_author,
    _draw_standard_cover_title_panel,
)

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

def make_cover(mp, op):
    meta = json.loads(mp.read_text(encoding="utf-8"))
    title = meta.get("title", "The Blacktop Requiem")
    author = meta.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = meta.get("model", "")

    random.seed("blacktop-requiem")
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        if t < 0.35:
            c = (int(200 - 50 * t / 0.35), int(100 - 30 * t / 0.35), int(60 - 20 * t / 0.35))
        elif t < 0.55:
            c = (int(150 - 80 * (t - 0.35) / 0.2), int(70 - 40 * (t - 0.35) / 0.2), int(40 - 25 * (t - 0.35) / 0.2))
        else:
            c = (int(70 - 50 * (t - 0.55) / 0.45), int(30 - 20 * (t - 0.55) / 0.45), int(15 - 10 * (t - 0.55) / 0.45))
        draw.line((0, y, W, y), fill=(*c, 255))

    for y in range(900, H, 2):
        t = (y - 900) / (H - 900)
        rw = int(100 + t * 600)
        cx = W // 2
        draw.line((cx - rw // 2, y, cx + rw // 2, y), fill=(60 + int(40 * t), 55 + int(35 * t), 50 + int(30 * t), 200))

    draw.rectangle((W // 2 - 50, 1200, W // 2 + 50, 1350), fill=(60, 50, 45, 200))
    for lx in [-1, 1]:
        for ly in range(1200, 1350, 40):
            draw.ellipse((W // 2 - 30 + lx * 25, ly, W // 2 - 20 + lx * 25, ly + 15), fill=(160, 20, 20, 180))

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((W // 2 - 100, 1240, W // 2 + 100, 1290), fill=(200, 30, 30, 20))
    glow = glow.filter(ImageFilter.GaussianBlur(20))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    op.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(str(op), "PNG", optimize=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    metadata_path = ROOT / args.metadata if not args.metadata.is_absolute() else args.metadata
    output_path = ROOT / args.out if not args.out.is_absolute() else args.out
    make_cover(metadata_path, output_path)

if __name__ == "__main__":
    main()
