#!/usr/bin/env python3
"""Cover: The River Mother — Yara waist-deep in glowing river water under full moon, hands on pregnant belly, magical realism."""

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
    draw = ImageDraw.Draw(img)

    # Night sky: deep blue above, dark water below
    for y in range(H):
        t = y / H
        if y < 600:
            r, g, b = int(8 + 12 * t * 1.7), int(10 + 20 * t * 1.7), int(40 + 30 * t * 1.7)
        elif y < 1000:
            r, g, b = int(20 + 30 * (t - 0.35) * 3.3), int(30 + 20 * (t - 0.35) * 3.3), int(55 - 15 * (t - 0.35) * 3.3)
        else:
            r, g, b = int(50 - 30 * (t - 0.6) * 2.5), int(50 - 30 * (t - 0.6) * 2.5), int(40 - 25 * (t - 0.6) * 2.5)
        draw.line((0, y, W, y), fill=(max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), 255))

    # Full moon
    moon_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(moon_glow)
    md.ellipse((W // 2 - 200, 80, W // 2 + 200, 400), fill=(240, 230, 200, 60))
    moon_glow = moon_glow.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, moon_glow)
    draw = ImageDraw.Draw(img)
    draw.ellipse((W // 2 - 70, 120, W // 2 + 70, 260), fill=(245, 240, 220, 230))
    draw.ellipse((W // 2 - 65, 130, W // 2 + 65, 250), fill=(255, 250, 235, 255))

    # Moon reflection on water
    for r in range(60, 5, -5):
        draw.ellipse((W // 2 - r * 2, 950, W // 2 + r * 2, 950 + r), fill=(240, 230, 200, max(0, 30 - (60 - r) * 2)))

    # Glowing river water
    for y in range(1000, 1600, 3):
        wobble = int(5 * math.sin(y * 0.05) + 3 * math.sin(y * 0.08))
        for x in range(W // 2 - 200 + wobble, W // 2 + 200 + wobble, 4):
            alpha = int(30 * math.sin(x * 0.03 + y * 0.02) ** 2 + 20)
            draw.point((x, y), fill=(160, 200, 255, max(10, alpha)))

    # Yara waist-deep in glowing river
    yx, yy = W // 2, 1200
    # Body (waist up)
    draw.polygon([(yx - 30, yy), (yx + 30, yy), (yx + 35, yy - 140), (yx - 35, yy - 140)], fill=(60, 50, 45, 240))
    # Head
    draw.ellipse((yx - 18, yy - 190, yx + 18, yy - 155), fill=(70, 58, 50, 240))
    # Hair
    draw.arc((yx - 22, yy - 200, yx + 22, yy - 160), 180, 360, fill=(25, 20, 18, 240), width=6)
    # Arms curved down to belly
    draw.line((yx - 35, yy - 100, yx - 60, yy - 30), fill=(60, 50, 45, 240), width=8)
    draw.line((yx + 35, yy - 100, yx + 60, yy - 30), fill=(60, 50, 45, 240), width=8)
    # Hands on pregnant belly
    draw.ellipse((yx - 60, yy - 35, yx - 52, yy - 25), fill=(65, 55, 48, 240))
    draw.ellipse((yx + 52, yy - 35, yx + 60, yy - 25), fill=(65, 55, 48, 240))
    # Pregnant belly (rounded silhouette below waist, above water)
    draw.ellipse((yx - 25, yy - 30, yx + 25, yy + 30), fill=(60, 50, 45, 240))

    # Glowing water particles around Yara
    for _ in range(60):
        gx = yx + random.randint(-120, 120)
        gy = yy + random.randint(-20, 100)
        gr = random.randint(1, 4)
        draw.ellipse((gx - gr, gy - gr, gx + gr, gy + gr), fill=(160, 220, 255, random.randint(60, 180)))

    # Riverbank silhouettes
    draw.polygon([(0, 1500), (200, 1480), (400, 1490), (600, 1470), (800, 1480), (W, 1460), (W, 1800), (0, 1800)], fill=(15, 20, 25, 200))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(str(output_path), "PNG", optimize=True)



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