#!/usr/bin/env python3
"""Cover: The Fourth Wall — Programmatic, metafictional design with bold sans-serif title."""

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


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    candidates = [FONT_DIR / name, FONT_DIR / "arialbd.ttf", FONT_DIR / "arial.ttf"]
    for c in candidates:
        if c.exists():
            return ImageFont.truetype(str(c), size)
    return ImageFont.load_default()


def wrap(draw: ImageDraw, text: str, font: ImageFont, max_w: int) -> list[str]:
    words = text.split()
    lines, current = [], []
    for w in words:
        test = " ".join([*current, w])
        if draw.textbbox((0, 0), test, font=font)[2] <= max_w:
            current.append(w)
        else:
            if current:
                lines.append(" ".join(current))
            current = [w]
    if current:
        lines.append(" ".join(current))
    return lines


def centered(draw: ImageDraw, y: int, lines: list[str], font: ImageFont, fill, gap: int) -> int:
    for line in lines:
        bb = draw.textbbox((0, 0), line, font=font)
        draw.text(((W - (bb[2] - bb[0])) // 2, y), line, font=font, fill=fill)
        y += bb[3] - bb[1] + gap
    return y


def make_cover(metadata_path: Path, output_path: Path) -> None:
    meta = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = meta["title"]
    author = meta.get("author", "Barış Kısır")
    model = meta.get("model", "")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Clean white/gray background with subtle grid — metafictional design
    for y in range(H):
        t = y / H
        r = int(200 + 55 * t)
        g = int(200 + 50 * t)
        b = int(210 + 45 * t)
        draw.line((0, y, W, y), fill=(min(255, r), min(255, g), min(255, b), 255))

    # Grid lines — theatrical stage grid
    for x in range(0, W, 80):
        draw.line((x, 0, x, H), fill=(180, 180, 190, 80), width=1)
    for y in range(0, H, 80):
        draw.line((0, y, W, y), fill=(180, 180, 190, 80), width=1)

    # Proscenium arch outline
    arch_color = (60, 60, 70, 200)
    draw.arc((100, 100, W - 100, 800), 0, 180, fill=arch_color, width=8)
    draw.line((100, 450, 100, H), fill=arch_color, width=8)
    draw.line((W - 100, 450, W - 100, H), fill=arch_color, width=8)
    draw.line((80, 450, W - 80, 450), fill=arch_color, width=6)

    # Curtain lines suggesting velvet drapes
    for cx in [120, 160, W - 160, W - 120]:
        for cy in range(450, 1800, 20):
            swing = int(15 * math.sin(cy * 0.05))
            draw.line((cx + swing, cy, cx + swing + 30, cy + 10), fill=(120, 40, 40, 120), width=2)

    # Bold sans-serif title in the center — THE FOURTH WALL
    tf_big = font("arialbd.ttf", 160)
    subtitle_text = "THE FOURTH WALL"
    bb = draw.textbbox((0, 0), subtitle_text, font=tf_big)
    tw = bb[2] - bb[0]
    draw.text(((W - tw) // 2, 600), subtitle_text, font=tf_big, fill=(30, 30, 40, 255))

    # Subtitle line — metafictional tag
    sf = font("arial.ttf", 36)
    sub_line = "A PLAY WITHIN A PLAY WITHIN A PLAY"
    bbs = draw.textbbox((0, 0), sub_line, font=sf)
    sw = bbs[2] - bbs[0]
    draw.text(((W - sw) // 2, 820), sub_line, font=sf, fill=(100, 100, 120, 180))

    # Decorative typographic elements — asterisks, dashes, rules
    for i in range(3):
        dx = 400 + i * 400
        draw.text((dx, 950), "*", font=font("arialbd.ttf", 60), fill=(80, 80, 100, 150))

    # Horizontal rule
    draw.line((300, 1050, W - 300, 1050), fill=(60, 60, 80, 150), width=3)

    # Stage directions — small text
    mono = font("arial.ttf", 24)
    directions = [
        "(The stage is bare. A single chair stands in the pool of light.)",
        "(The actor turns to the audience and speaks.)",
    ]
    for i, line in enumerate(directions):
        bb = draw.textbbox((0, 0), line, font=mono)
        lw = bb[2] - bb[0]
        draw.text(((W - lw) // 2, 1100 + i * 40), line, font=mono, fill=(120, 120, 130, 160))

    # Faint figure silhouette center stage
    fig_color = (40, 40, 50, 80)
    fig_cx = W // 2
    fig_by = 1500
    draw.ellipse((fig_cx - 30, fig_by - 200, fig_cx + 30, fig_by - 140), fill=fig_color)
    draw.polygon([(fig_cx - 25, fig_by - 140), (fig_cx + 25, fig_by - 140), (fig_cx + 30, fig_by - 30), (fig_cx - 30, fig_by - 30)], fill=fig_color)
    draw.rectangle((fig_cx - 35, fig_by - 30, fig_cx + 35, fig_by), fill=fig_color)

    # Spotlight from above
    spotlight = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(spotlight)
    sd.polygon([(fig_cx - 80, 450), (fig_cx + 80, 450), (fig_cx + 120, 1600), (fig_cx - 120, 1600)], fill=(255, 255, 240, 20))
    spotlight = spotlight.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, spotlight)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(output_path, "PNG", optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    mp = ROOT / args.metadata if not args.metadata.is_absolute() else args.metadata
    op = ROOT / args.out if not args.out.is_absolute() else args.out
    make_cover(mp, op)


if __name__ == "__main__":
    main()
