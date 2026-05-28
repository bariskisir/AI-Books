#!/usr/bin/env python3
"""Create a project-local raster cover for The Bellweather Murders."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[2]
FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    for candidate in [FONT_DIR / name, FONT_DIR / "georgia.ttf", FONT_DIR / "arial.ttf"]:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def wrap(draw: ImageDraw.ImageDraw, text: str, selected_font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        proposed = " ".join([*current, word])
        if draw.textbbox((0, 0), proposed, font=selected_font)[2] <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def centered(draw: ImageDraw.ImageDraw, y: int, lines: list[str], selected_font: ImageFont.FreeTypeFont, fill: tuple[int, int, int], gap: int) -> int:
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=selected_font)
        x = (W - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), line, font=selected_font, fill=fill)
        y += bbox[3] - bbox[1] + gap
    return y


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata["title"]
    author = metadata.get("author", "Barış Kısır")
    rng = random.Random(title)

    img = Image.new("RGB", (W, H), (18, 22, 24))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / (H - 1)
        r = int(13 + 24 * t)
        g = int(19 + 28 * t)
        b = int(23 + 22 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    mist = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(mist, "RGBA")
    for _ in range(140):
        y = rng.randrange(260, 1680)
        alpha = rng.randrange(10, 30)
        x0 = rng.randrange(-500, 1200)
        x1 = x0 + rng.randrange(700, 1700)
        md.ellipse((x0, y, x1, y + rng.randrange(80, 190)), fill=(190, 204, 194, alpha))
    mist = mist.filter(ImageFilter.GaussianBlur(28))
    img = Image.alpha_composite(img.convert("RGBA"), mist)
    draw = ImageDraw.Draw(img, "RGBA")

    # Lake and town silhouette.
    draw.rectangle((0, 1330, W, 1650), fill=(28, 45, 50, 210))
    for y in range(1380, 1640, 34):
        draw.line((0, y, W, y + rng.randrange(-8, 9)), fill=(128, 154, 145, 34), width=3)
    draw.rectangle((0, 1120, W, 1340), fill=(12, 15, 17, 210))
    for x in range(70, W, 105):
        h = rng.randrange(80, 210)
        draw.rectangle((x, 1120 - h, x + rng.randrange(44, 88), 1340), fill=(15, 17, 18, 235))
        if rng.random() < 0.55:
            draw.rectangle((x + 12, 1160 - h // 2, x + 24, 1174 - h // 2), fill=(231, 196, 117, 105))

    # Church tower and bell glow.
    tx = 1050
    draw.rectangle((tx, 520, tx + 210, 1340), fill=(21, 22, 22, 245))
    draw.polygon([(tx - 25, 520), (tx + 105, 360), (tx + 235, 520)], fill=(14, 15, 16, 250))
    draw.rectangle((tx + 68, 690, tx + 142, 810), fill=(215, 178, 96, 95))
    draw.ellipse((tx + 58, 655, tx + 152, 805), outline=(221, 181, 91, 120), width=5)
    draw.line((tx + 105, 805, tx + 105, 1135), fill=(205, 192, 157, 120), width=5)
    draw.ellipse((tx + 85, 1130, tx + 125, 1170), fill=(205, 192, 157, 120))

    # Foreground road and clue-like blue thread.
    draw.polygon([(0, H), (650, 1620), (930, 1620), (W, H)], fill=(9, 11, 12, 230))
    path = [(260 + i * 18, 1900 + int(55 * rng.random()) + int(80 * (i / 60))) for i in range(61)]
    draw.line(path, fill=(76, 139, 176, 190), width=8)
    draw.line([(x, y + 10) for x, y in path], fill=(236, 238, 220, 120), width=2)

    # Title panel.
    draw.rectangle((0, 1745, W, H), fill=(5, 8, 10, 188))
    draw.line((190, 1768, W - 190, 1768), fill=(181, 196, 173, 130), width=3)
    title_font = font("georgiab.ttf", 126)
    author_font = font("arialbd.ttf", 52)
    subtitle_font = font("arial.ttf", 34)
    y = 1830
    y = centered(draw, y, ["A BELLWEATHER MYSTERY"], subtitle_font, (181, 196, 173), 16)
    y += 65
    y = centered(draw, y, wrap(draw, title.upper(), title_font, 1250), title_font, (242, 244, 229), 22)
    y += 120
    centered(draw, y, [author.upper()], author_font, (214, 220, 205), 12)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(output_path, "PNG", optimize=True)


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
