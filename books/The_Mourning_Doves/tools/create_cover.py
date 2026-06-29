#!/usr/bin/env python3
"""Cover: The Mourning Doves — Gothic romance, crumbling manor, fog, doves."""

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
    candidates = [FONT_DIR / name, FONT_DIR / "georgia.ttf", FONT_DIR / "arial.ttf"]
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


def centered(
    draw: ImageDraw, y: int, lines: list[str], font: ImageFont, fill, gap: int
) -> int:
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

    # Gradient background: deep violet to gray-black
    for y in range(H):
        t = y / H
        r = int(25 + 10 * t)
        g = int(12 + 8 * t)
        b = int(35 + 15 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # Moon glow
    moon = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(moon)
    md.ellipse((W - 400, 80, W - 120, 360), fill=(200, 195, 180, 120))
    moon = moon.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, moon)
    draw = ImageDraw.Draw(img)

    # Crumbling manor silhouette
    cx, cy = W // 2, 1100
    # Main body
    draw.polygon(
        [
            (cx - 450, cy + 200),
            (cx - 450, cy - 100),
            (cx - 250, cy - 100),
            (cx - 250, cy - 300),
            (cx + 250, cy - 300),
            (cx + 250, cy - 100),
            (cx + 450, cy - 100),
            (cx + 450, cy + 200),
        ],
        fill=(8, 5, 12, 230),
    )
    # Left tower
    draw.rectangle((cx - 400, cy - 450, cx - 250, cy - 300), fill=(8, 5, 12, 230))
    draw.polygon(
        [(cx - 430, cy - 450), (cx - 220, cy - 450), (cx - 325, cy - 520)],
        fill=(8, 5, 12, 230),
    )
    # Right tower
    draw.rectangle((cx + 250, cy - 480, cx + 400, cy - 300), fill=(8, 5, 12, 230))
    draw.polygon(
        [(cx + 220, cy - 480), (cx + 430, cy - 480), (cx + 325, cy - 560)],
        fill=(8, 5, 12, 230),
    )
    # Broken roof line
    draw.polygon(
        [(cx - 250, cy - 300), (cx - 150, cy - 260), (cx - 50, cy - 310),
         (cx + 50, cy - 270), (cx + 150, cy - 250), (cx + 250, cy - 300)],
        fill=(8, 5, 12, 230),
    )
    # Lit window
    draw.rectangle((cx - 30, cy - 180, cx + 30, cy - 120), fill=(160, 130, 70, 100))

    # Crumbling edges / debris
    for dx in [-460, -440, 440, 460]:
        draw.polygon(
            [(dx, cy + 200), (dx + 20, cy + 200), (dx + 10, cy + 240)],
            fill=(12, 8, 16, 200),
        )

    # Bare twisted trees
    for tx in [cx - 500, cx - 380, cx + 380, cx + 500]:
        for _ in range(6):
            sx = tx + random.randint(-20, 20)
            ex = sx + random.randint(-80, 80)
            ey = cy + 50 - random.randint(0, 100)
            draw.line(
                (sx, cy + 100, ex, ey),
                fill=(3, 2, 5, 200),
                width=random.randint(2, 4),
            )
            # Branches
            for _ in range(3):
                bx = ex + random.randint(-40, 40)
                by = ey - random.randint(20, 60)
                draw.line((ex, ey, bx, by), fill=(3, 2, 5, 180), width=2)

    # Mourning doves in sky
    for i in range(5):
        dx = 200 + i * 280 + random.randint(-30, 30)
        dy = 150 + i * 60 + random.randint(-20, 20)
        # Simple dove silhouette
        draw.ellipse((dx - 12, dy - 6, dx + 12, dy + 6), fill=(160, 155, 150, 100))
        draw.polygon(
            [(dx + 12, dy), (dx + 25, dy - 6), (dx + 20, dy + 2)],
            fill=(160, 155, 150, 100),
        )

    # Fog layers
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog)
    fd.ellipse((-300, 1400, W + 300, 1900), fill=(170, 165, 160, 25))
    fd.ellipse((-200, 1600, W + 200, 2100), fill=(180, 175, 170, 20))
    fog = fog.filter(ImageFilter.GaussianBlur(50))
    img = Image.alpha_composite(img, fog)
    draw = ImageDraw.Draw(img)

    # Bottom title panel
    draw.rectangle((0, 1920, W, H), fill=(10, 7, 14, 245))
    # Decorative lines
    draw.line((300, 1980, W - 300, 1980), fill=(140, 120, 90, 180), width=2)
    draw.line((300, H - 120, W - 300, H - 120), fill=(140, 120, 90, 80), width=1)

    # Title
    tf = font("georgiab.ttf", 100)
    af = font("arialbd.ttf", 40)
    sf = font("arial.ttf", 26)

    wrapped = wrap(draw, title.upper(), tf, 1200)
    y = centered(draw, 2010, wrapped, tf, (190, 175, 145), 8)

    # Author
    y = centered(draw, y + 50, [author], af, (170, 160, 140), 6)

    # Small genre text
    centered(draw, y + 60, ["GOTHIC ROMANCE"], sf, (120, 110, 95), 0)

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