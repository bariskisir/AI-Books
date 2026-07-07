#!/usr/bin/env python3
"""Cover: The Ghost Bridge — Mist-shrouded single-arch stone bridge over dark gorge, geometric carvings."""

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

    # Deep gorge gradient: dark stone gray at top, black at bottom
    for y in range(H):
        t = y / H
        r = int(30 + 20 * (1 - t))
        g = int(28 + 18 * (1 - t))
        b = int(35 + 20 * (1 - t))
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Gorge walls — jagged cliffs on both sides
    for side in [-1, 1]:
        cliff_pts = [(W // 2 + side * 200, 800)]
        for i in range(20):
            t = i / 20
            x = W // 2 + side * (200 - t * 180)
            y = 800 + t * 1400
            x += random.randint(-20, 20)
            cliff_pts.append((x, y))
        cliff_pts.append((W // 2 + side * 20, H))
        cliff_pts.append((W // 2 + side * 200, H))
        draw.polygon(cliff_pts, fill=(25, 24, 30, 200))

    # Distant mist layer behind bridge
    mist = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(mist)
    md.ellipse((200, 400, W - 200, 1000), fill=(200, 210, 220, 30))
    mist = mist.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img, mist)

    # Single-arch stone bridge
    bx, by = W // 2, 850
    arch_r = 380
    # Bridge arch
    draw.arc((bx - arch_r, by - arch_r, bx + arch_r, by + arch_r), 0, 180, fill=(80, 75, 70, 220), width=30)
    # Inner arch edge
    draw.arc((bx - arch_r + 25, by - arch_r + 25, bx + arch_r - 25, by + arch_r - 25), 0, 180, fill=(60, 55, 50, 200), width=8)
    # Keystone at top of arch
    draw.polygon([(bx - 20, by - arch_r + 5), (bx + 20, by - arch_r + 5), (bx + 15, by - arch_r + 35), (bx - 15, by - arch_r + 35)], fill=(100, 95, 88, 220))
    # Keystone glow
    for r in range(30, 5, -3):
        alpha = int(40 * (1 - r / 30))
        draw.ellipse((bx - r, by - arch_r - r, bx + r, by - arch_r + r), fill=(200, 180, 120, alpha))

    # Bridge deck
    draw.rectangle((bx - arch_r - 20, by - 15, bx + arch_r + 20, by + 10), fill=(70, 66, 60, 220))
    # Stone parapet
    draw.rectangle((bx - arch_r - 20, by - 30, bx + arch_r + 20, by - 15), fill=(75, 70, 65, 220))
    # Crenellations
    for cx in range(bx - arch_r - 10, bx + arch_r + 20, 50):
        draw.rectangle((cx, by - 45, cx + 20, by - 30), fill=(70, 65, 60, 220))

    # Geometric carvings on arch — circles and diamonds
    for angle in range(20, 170, 20):
        rad = math.radians(angle)
        cx = bx + int((arch_r - 60) * math.cos(rad))
        cy = by + int((arch_r - 60) * math.sin(rad))
        draw.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), outline=(100, 95, 88, 150), width=2)
        draw.polygon([(cx, cy - 10), (cx + 8, cy), (cx, cy + 10), (cx - 8, cy)], outline=(100, 95, 88, 120), width=1)

    # Mist wisps rising from gorge
    for wx in range(200, W - 200, 80):
        wy = by + arch_r + random.randint(0, 200)
        for w in range(6):
            alpha = max(0, 50 - w * 8)
            draw.ellipse((wx + random.randint(-30, 30), wy - w * 25, wx + random.randint(40, 80), wy - w * 25 + 40), fill=(200, 210, 220, alpha))

    # Ghostly white glow emanating from center of arch
    ghost = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(ghost)
    gd.ellipse((bx - 80, by - arch_r - 20, bx + 80, by - arch_r + 100), fill=(220, 230, 240, 30))
    ghost = ghost.filter(ImageFilter.GaussianBlur(20))
    img = Image.alpha_composite(img, ghost)

    # Subtle fog at bottom
    draw.rectangle((0, 1700, W, H), fill=(30, 28, 35, 180))

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
