#!/usr/bin/env python3
"""Cover: The Fifth Season — Literary Romance on a Greek island."""

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

    # Gradient sky: Aegean blue at top, warm terracotta near horizon
    for y in range(H):
        t = y / H
        if y < 1200:
            # Sky: deep blue to pale azure
            r = int(30 + 60 * (y / 1200))
            g = int(80 + 100 * (y / 1200))
            b = int(180 - 30 * (y / 1200))
        else:
            # Horizon to sea: warm peach to deep teal
            t2 = (y - 1200) / 1360
            r = int(90 - 50 * t2)
            g = int(180 - 120 * t2)
            b = int(150 - 40 * t2)
        draw.line((0, y, W, y), fill=(max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), 255))

    # Sun glow near horizon
    sun = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sun)
    sd.ellipse((W // 2 - 250, 1050, W // 2 + 250, 1450), fill=(240, 180, 100, 40))
    sd.ellipse((W // 2 - 150, 1100, W // 2 + 150, 1400), fill=(255, 200, 120, 50))
    sun = sun.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, sun)
    draw = ImageDraw.Draw(img)

    # Sea with wave lines
    for w in range(8):
        wy = 1400 + w * 25
        wax = math.sin(w * 0.7) * 60
        for x in range(0, W, 8):
            px = x + int(math.sin(x * 0.02 + w * 1.2) * 15)
            if 0 <= px < W:
                draw.point((px, wy), fill=(200, 220, 240, 60 + w * 5))

    # Distant island silhouette
    draw.polygon(
        [(100, 1350), (200, 1200), (350, 1150), (500, 1180), (650, 1120),
         (800, 1150), (950, 1100), (1100, 1130), (1250, 1080), (1400, 1110),
         (1500, 1140), (1550, 1350)],
        fill=(60, 80, 95, 180),
    )

    # Whitewashed buildings on the island
    # Church with blue dome
    bx, by = 700, 1080
    draw.rectangle((bx - 40, by - 80, bx + 40, by), fill=(230, 235, 240, 220))
    draw.ellipse((bx - 30, by - 110, bx + 30, by - 70), fill=(30, 100, 160, 200))
    draw.polygon(
        [(bx - 5, by - 110), (bx + 5, by - 110), (bx, by - 130)],
        fill=(220, 225, 230, 200),
    )

    # Buildings cluster left
    for i, (bdx, bdy, bw, bh) in enumerate([
        (560, 1090, 60, 50), (580, 1060, 50, 80), (530, 1080, 45, 60),
        (780, 1080, 55, 55), (810, 1050, 60, 85), (840, 1070, 40, 65),
    ]):
        draw.rectangle((bdx, bdy - bh, bdx + bw, bdy), fill=(210 + i * 3, 215 + i * 3, 220 + i * 3, 200))
        # Blue window
        draw.rectangle((bdx + 10, bdy - bh + 15, bdx + bw - 10, bdy - bh + 30), fill=(40, 120, 180, 150))

    # Second church or bell tower
    draw.rectangle((500, 1060, 520, 1120), fill=(225, 230, 235, 190))
    draw.polygon([(495, 1060), (525, 1060), (510, 1040)], fill=(220, 225, 230, 190))

    # Steps / stairs on hillside
    for s in range(6):
        sx = 640 + s * 25
        sy = 1130 - s * 8
        draw.line((sx, sy, sx + 60, sy), fill=(180, 190, 200, 120), width=2)

    # Terracotta roof tiles
    for rx, rw in [(540, 80), (600, 70), (720, 90), (790, 80), (840, 60)]:
        draw.polygon(
            [(rx, 1120), (rx + rw, 1120), (rx + rw // 2, 1105)],
            fill=(180, 100, 60, 150),
        )

    # Rocky cliff edge
    draw.polygon(
        [(0, 1350), (50, 1300), (120, 1320), (200, 1270), (300, 1300),
         (400, 1280), (W, 1350), (W, H), (0, H)],
        fill=(180, 165, 140, 200),
    )
    draw.polygon(
        [(0, 1380), (80, 1320), (180, 1340), (280, 1300), (400, 1330), (W, 1380), (W, H), (0, H)],
        fill=(200, 185, 160, 180),
    )

    # Olive tree silhouette on cliff
    draw.line((320, 1330, 340, 1280), fill=(100, 80, 50, 180), width=4)
    draw.ellipse((310, 1240, 370, 1290), fill=(80, 100, 60, 120))

    # Small boat in distance
    draw.ellipse((250, 1380, 280, 1395), fill=(140, 80, 60, 150))
    draw.line((260, 1370, 260, 1390), fill=(60, 60, 60, 120), width=1)

    # Soft mist layer over the island
    mist = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(mist)
    md.ellipse((100, 1100, W - 100, 1450), fill=(210, 210, 220, 15))
    mist = mist.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, mist)
    draw = ImageDraw.Draw(img)

    # Bottom title panel
    draw.rectangle((0, 1960, W, H), fill=(20, 25, 40, 245))
    # Decorative lines
    draw.line((200, 2000, W - 200, 2000), fill=(180, 200, 220, 150), width=2)
    draw.line((200, H - 100, W - 200, H - 100), fill=(180, 200, 220, 80), width=1)

    # Title in white using arialbd.ttf
    tf = font("arialbd.ttf", 100)
    af = font("arialbd.ttf", 38)
    sf = font("arial.ttf", 28)

    wrapped = wrap(draw, title.upper(), tf, 1300)
    y = centered(draw, 2040, wrapped, tf, (255, 255, 255), 10)

    # Author in white
    y = centered(draw, y + 50, [author], af, (220, 225, 235), 6)

    # Genre line in white
    centered(draw, y + 55, ["LITERARY ROMANCE"], sf, (180, 210, 240), 0)

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