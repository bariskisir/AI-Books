#!/usr/bin/env python3
"""Cover: The Safe House — snowy Montana cabin at twilight, warm-lit window, dark pines, jagged mountain under indigo sky."""

from __future__ import annotations
import argparse, json, random
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


def get_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    p = FONT_DIR / name
    if p.exists():
        return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def wrap_text(draw, text: str, font, max_width: int) -> list[str]:
    words = text.split()
    lines = []
    current = []
    for w in words:
        test = " ".join([*current, w])
        bb = draw.textbbox((0, 0), test, font=font)
        if bb[2] <= max_width:
            current.append(w)
        else:
            lines.append(" ".join(current))
            current = [w]
    if current:
        lines.append(" ".join(current))
    return lines


def center_text(draw, y: int, lines: list[str], font, fill, gap: int) -> int:
    for line in lines:
        bb = draw.textbbox((0, 0), line, font=font)
        x = (W - (bb[2] - bb[0])) // 2
        draw.text((x, y), line, font=font, fill=fill)
        y += bb[3] - bb[1] + gap
    return y


def make_cover(metadata_path: Path, output_path: Path) -> None:
    meta = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = meta["title"]
    author = meta.get("author", "Barış Kısır")
    model = meta.get("model", "")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Indigo night sky
    for y in range(H):
        t = y / H
        r = int(8 + 4 * t)
        g = int(8 + 6 * t)
        b = int(45 + 28 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # Jagged mountain silhouette
    mt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(mt)
    pts1 = [(0, 950), (150, 520), (350, 680), (550, 480), (750, 620), (1000, 500), (1200, 650), (1400, 470), (W, 580), (W, 1100), (0, 1100)]
    md.polygon(pts1, fill=(28, 36, 55, 200))
    pts2 = [(0, 1050), (180, 620), (400, 800), (600, 600), (800, 750), (1050, 580), (1250, 700), (1450, 550), (W, 600), (W, 1100), (0, 1100)]
    md.polygon(pts2, fill=(18, 28, 48, 200))
    img = Image.alpha_composite(img, mt)
    draw = ImageDraw.Draw(img, "RGBA")

    # Dark pines
    for cx, h in [(180, 140), (340, 120), (520, 150), (720, 130), (900, 160), (1080, 125), (1260, 145), (1420, 120), (1520, 110)]:
        draw.polygon([(cx, 800 - h), (cx - h // 3, 820), (cx + h // 3, 820)], fill=(8, 35, 18, 220))
        draw.polygon([(cx, 800 - h), (cx - h // 5, 800 - h + h // 4), (cx, 800 - h + h // 6), (cx + h // 5, 800 - h + h // 4)], fill=(215, 225, 235, 180))

    # Montana cabin
    draw.rectangle((660, 980, 940, 1220), fill=(58, 38, 28, 235))
    draw.polygon([(630, 980), (800, 860), (970, 980)], fill=(78, 52, 38, 235))
    draw.polygon([(635, 975), (800, 865), (965, 975)], fill=(200, 210, 220, 180))
    # Warm-lit window
    draw.rectangle((690, 1030, 760, 1090), fill=(255, 210, 100, 230))
    draw.rectangle((685, 1025, 765, 1095), fill=(255, 210, 100, 50))
    # Door
    draw.rectangle((810, 1140, 870, 1220), fill=(38, 28, 18, 235))
    # Chimney
    draw.rectangle((900, 900, 925, 970), fill=(48, 38, 32, 235))

    # Window glow
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((650, 980, 800, 1140), fill=(255, 210, 100, 30))
    glow = glow.filter(ImageFilter.GaussianBlur(22))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Snowy ground
    draw.rectangle((0, 1300, W, 1700), fill=(38, 42, 52, 230))

    # Snow on ground
    for x in range(0, W, 20):
        sy = 1300 + (x % 30)
        draw.line((x, sy, x + 15, sy + 6), fill=(55, 60, 70, 80), width=2)

    # Falling snow
    random.seed(42)
    for _ in range(200):
        sx = random.randint(0, W)
        sy = random.randint(0, H)
        sr = random.randint(1, 3)
        draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=(200, 210, 230, random.randint(40, 110)))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(output_path, "PNG", optimize=True)



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    make_cover(
        ROOT / args.metadata if not args.metadata.is_absolute() else args.metadata,
        ROOT / args.out if not args.out.is_absolute() else args.out,
    )


if __name__ == "__main__":
    main()