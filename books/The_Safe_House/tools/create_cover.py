#!/usr/bin/env python3
"""Cover: The Safe House — mountain cabin in snow, romantic suspense."""

from __future__ import annotations
import argparse, json
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

    # Night sky gradient: dark blue to deep indigo
    for y in range(H):
        t = y / H
        r = int(10 + 5 * t)
        g = int(10 + 8 * t)
        b = int(50 + 30 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # Moon
    moon_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    moon_draw = ImageDraw.Draw(moon_layer)
    moon_draw.ellipse((1100, 120, 1340, 360), fill=(220, 220, 230, 200))
    moon_layer = moon_layer.filter(ImageFilter.GaussianBlur(12))
    img = Image.alpha_composite(img, moon_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # Mountains in background (distant)
    mt_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    mt_draw = ImageDraw.Draw(mt_layer)
    mt1 = [(0, 900), (200, 500), (400, 700), (600, 480), (800, 650), (1000, 520), (1200, 680), (1400, 490), (1600, 600), (1600, 1100), (0, 1100)]
    mt_draw.polygon(mt1, fill=(30, 40, 60, 200))
    mt2 = [(0, 1000), (150, 600), (350, 800), (550, 620), (750, 780), (950, 560), (1100, 720), (1300, 580), (1500, 700), (1600, 550), (1600, 1100), (0, 1100)]
    mt_draw.polygon(mt2, fill=(20, 30, 50, 200))
    img = Image.alpha_composite(img, mt_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # Snow-covered pines
    trees = [
        (200, 800, 60, 160),
        (380, 780, 50, 140),
        (550, 820, 55, 150),
        (780, 790, 45, 130),
        (950, 810, 65, 170),
        (1150, 785, 50, 145),
        (1320, 805, 60, 155),
        (1480, 790, 45, 130),
    ]
    pine_colors = [(10, 40, 20, 220), (8, 35, 18, 220), (12, 45, 22, 220)]
    snow_cap = (220, 230, 240, 200)
    for i, (cx, cy, w, h) in enumerate(trees):
        pts = [(cx, cy - h), (cx - w // 2, cy + h // 3), (cx + w // 2, cy + h // 3)]
        draw.polygon(pts, fill=pine_colors[i % 3])
        # Snow cap
        cap_pts = [(cx, cy - h), (cx - w // 4, cy - h + h // 4), (cx, cy - h + h // 6), (cx + w // 4, cy - h + h // 4)]
        draw.polygon(cap_pts, fill=snow_cap)

    # The cabin
    cabin_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cabin_draw = ImageDraw.Draw(cabin_layer)
    # Cabin body
    cabin_draw.rectangle((680, 980, 920, 1200), fill=(60, 40, 30, 230))
    # Roof (snow-covered)
    roof_pts = [(650, 980), (800, 880), (950, 980)]
    cabin_draw.polygon(roof_pts, fill=(80, 55, 40, 230))
    # Snow on roof
    snow_roof = [(655, 975), (800, 885), (945, 975)]
    cabin_draw.polygon(snow_roof, fill=(200, 210, 220, 180))
    # Door
    cabin_draw.rectangle((770, 1120, 830, 1200), fill=(40, 30, 20, 230))
    # Window with warm light
    cabin_draw.rectangle((700, 1030, 750, 1080), fill=(255, 200, 100, 220))
    # Window glow
    cabin_draw.rectangle((695, 1025, 755, 1085), fill=(255, 200, 100, 60))
    # Chimney
    cabin_draw.rectangle((870, 900, 900, 970), fill=(50, 40, 35, 230))
    # Smoke
    cabin_draw.ellipse((865, 860, 905, 900), fill=(150, 150, 160, 80))
    cabin_draw.ellipse((860, 830, 910, 875), fill=(140, 140, 150, 50))
    img = Image.alpha_composite(img, cabin_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # Warm window glow effect
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((660, 980, 790, 1130), fill=(255, 200, 100, 25))
    glow = glow.filter(ImageFilter.GaussianBlur(20))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Foreground snow
    snow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    snow_draw = ImageDraw.Draw(snow_layer)
    snow_draw.rectangle((0, 1300, W, 1500), fill=(40, 45, 55, 230))
    snow_draw.rectangle((0, 1480, W, 1700), fill=(35, 40, 50, 230))
    # Snow highlights
    for x in range(0, W, 40):
        sy = 1300 + (x % 37)
        snow_draw.line((x, sy, x + 20, sy + 8), fill=(60, 65, 75, 100), width=2)
    img = Image.alpha_composite(img, snow_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # Falling snow particles
    import random
    random.seed(42)
    for _ in range(200):
        sx = random.randint(0, W)
        sy = random.randint(0, H)
        sr = random.randint(1, 3)
        sa = random.randint(40, 120)
        draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=(200, 210, 230, sa))

    # Title panel at bottom
    draw.rectangle((0, 1920, W, 2560), fill=(230, 230, 235, 240))
    draw.rectangle((0, 1920, W, 1922), fill=(200, 200, 210, 255))

    # Fonts
    title_font = get_font("georgiab.ttf", 90)
    author_font = get_font("arialbd.ttf", 42)
    tagline_font = get_font("arial.ttf", 28)

    # Title
    title_lines = wrap_text(draw, title.upper(), title_font, 1400)
    center_text(draw, 2000, title_lines, title_font, (30, 30, 50), 8)

    # Decorative line
    draw.line((600, 2170, 1000, 2170), fill=(100, 100, 140, 180), width=2)

    # Tagline
    tagline = "ROMANTIC SUSPENSE"
    center_text(draw, 2200, [tagline], tagline_font, (80, 80, 110), 0)

    # Author
    center_text(draw, 2320, [author], author_font, (40, 40, 60), 0)

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