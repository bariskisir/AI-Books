#!/usr/bin/env python3
"""Cover: The Indigo Pattern — Indigo silk gown on padded hanger, blue dust particles glowing under investigation light."""

from __future__ import annotations

import argparse
import json
import math
import random
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
W, H = 1600, 2560
PANEL_Y = 1765
FONT_DIR = Path("C:/Windows/Fonts")


def font(name: str, size: int):
    path = FONT_DIR / name
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def draw_couture_scene(draw: ImageDraw.ImageDraw) -> None:
    for y in range(PANEL_Y):
        t = y / PANEL_Y
        if t < 0.5:
            c = lerp((17, 22, 35), (34, 49, 76), t / 0.5)
        else:
            c = lerp((34, 49, 76), (14, 14, 20), (t - 0.5) / 0.5)
        draw.line((0, y, W, y), fill=(*c, 255))

    # Pattern paper worktable.
    draw.polygon([(170, 1450), (1430, 1450), (1320, 1638), (280, 1640)], fill=(214, 196, 156, 235), outline=(100, 78, 54, 160))
    for x in range(250, 1350, 95):
        draw.line((x, 1465, x - 70, 1632), fill=(124, 96, 60, 80), width=3)
    for y in range(1480, 1630, 36):
        draw.line((220, y, 1380, y + random.randint(-8, 8)), fill=(124, 96, 60, 70), width=2)

    # Indigo couture gown on a dress form.
    cx = W // 2
    draw.rectangle((cx - 40, 255, cx + 40, 475), fill=(76, 61, 52, 255))
    draw.ellipse((cx - 85, 215, cx + 85, 310), fill=(178, 164, 138, 255), outline=(90, 70, 54, 150))
    bodice = [(cx - 175, 470), (cx + 170, 470), (cx + 115, 895), (cx - 110, 895)]
    skirt = [(cx - 125, 875), (cx + 125, 875), (cx + 405, 1428), (cx - 410, 1428)]
    draw.polygon(skirt, fill=(12, 38, 91, 245), outline=(82, 110, 156, 180))
    draw.polygon(bodice, fill=(16, 48, 112, 252), outline=(118, 146, 190, 190))
    draw.arc((cx - 176, 415, cx + 180, 645), 20, 160, fill=(198, 214, 230, 210), width=6)
    draw.line((cx - 150, 480, cx + 95, 895), fill=(88, 124, 186, 180), width=9)
    for i in range(16):
        x = cx - 360 + i * 48
        draw.line((cx, 900, x, 1420), fill=(40, 70, 130, 100), width=4)

    # Pale glove, steamer head, and blue dust trail.
    draw.rounded_rectangle((250, 1135, 500, 1245), radius=24, fill=(230, 222, 205, 235), outline=(80, 70, 62, 160), width=3)
    for i in range(5):
        draw.rounded_rectangle((270 + i * 40, 1070 - i * 5, 307 + i * 40, 1150), radius=16, fill=(232, 225, 208, 230), outline=(86, 76, 66, 120), width=2)
    draw.ellipse((1148, 1168, 1305, 1328), fill=(66, 74, 82, 245), outline=(198, 184, 150, 170), width=5)
    draw.rectangle((1210, 1300, 1248, 1465), fill=(70, 78, 84, 235))
    for _ in range(180):
        x = random.randint(260, 1290)
        y = int(1120 + 250 * math.sin((x - 260) / 150) + random.randint(-38, 38))
        if 250 < y < 1480:
            s = random.randint(2, 6)
            draw.ellipse((x, y, x + s, y + s), fill=(42, 82, 184, random.randint(90, 210)))

    # Missing pattern book and labeled evidence tag.
    draw.rectangle((185, 520, 480, 760), fill=(88, 62, 44, 245), outline=(210, 174, 112, 170), width=5)
    draw.rectangle((220, 555, 455, 715), fill=(222, 204, 160, 235))
    draw.ellipse((390, 568, 445, 618), fill=(92, 54, 35, 130))
    draw.text((242, 610), "IDA SAYEGH", font=font("arialbd.ttf", 31), fill=(42, 36, 32, 230))
    draw.text((242, 653), "CRESCENT DRAFT", font=font("arial.ttf", 26), fill=(64, 50, 42, 225))

    # Thread arcs and cutting notches around the dress.
    for i in range(9):
        y = 615 + i * 72
        draw.arc((210, y, 1390, y + 280), 190, 350, fill=(118, 150, 222, 55), width=3)
    for x, y in [(570, 770), (1010, 760), (640, 1080), (960, 1110)]:
        draw.polygon([(x, y), (x + 28, y + 8), (x + 8, y + 35)], fill=(236, 226, 188, 230))

    # Soft steam cloud over neckline.
    cloud = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cloud, "RGBA")
    for _ in range(28):
        x = random.randint(cx - 260, cx + 260)
        y = random.randint(410, 690)
        cd.arc((x - 160, y - 45, x + 160, y + 85), 185, 355, fill=(220, 226, 218, random.randint(35, 82)), width=random.randint(5, 12))
    cloud = cloud.filter(ImageFilter.GaussianBlur(1.8))
    draw.bitmap((0, 0), cloud, fill=None)

    tagline = "TEXTILE FORENSICS  ARCHIVE  COUTURE"
    tag_font = font("georgia.ttf", 38)
    bb = draw.textbbox((0, 0), tagline, font=tag_font)
    draw.text(((W - (bb[2] - bb[0])) // 2, 285), tagline, font=tag_font, fill=(232, 220, 184, 230))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Indigo Pattern")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")
    rng = __import__("random").Random(17)

    image = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(image, "RGBA")

    # Dark investigative room gradient
    for y in range(H):
        t = y / H
        r = int(15 + 40 * t)
        g = int(20 + 45 * t)
        b = int(35 + 55 * t)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Amber spotlight from above
    spotlight = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(spotlight)
    sd.polygon([(W // 2 - 100, 0), (W // 2 + 100, 0), (W // 2 + 400, H), (W // 2 - 400, H)], fill=(255, 200, 100, 18))
    spotlight = spotlight.filter(ImageFilter.GaussianBlur(40))
    image = Image.alpha_composite(image, spotlight)
    draw = ImageDraw.Draw(image, "RGBA")

    # Indigo silk gown on padded hanger
    cx = W // 2
    # Padded hanger
    draw.ellipse((cx - 80, 250, cx + 80, 310), fill=(200, 190, 175))
    draw.ellipse((cx - 60, 260, cx + 60, 300), fill=(215, 205, 190))
    draw.rectangle((cx - 6, 285, cx + 6, 320), fill=(180, 170, 155))
    # Hook
    draw.line((cx, 250, cx, 220), fill=(150, 140, 130), width=4)
    draw.ellipse((cx - 6, 214, cx + 6, 226), fill=(150, 140, 130))

    # Gown body (indigo silk)
    # Bodice
    draw.polygon([(cx - 160, 320), (cx + 160, 320), (cx + 100, 750), (cx - 100, 750)], fill=(15, 40, 95, 245))
    draw.polygon([(cx - 160, 320), (cx + 160, 320), (cx + 100, 750), (cx - 100, 750)], outline=(40, 80, 150, 200), width=2)
    # Skirt - flowing indigo
    draw.polygon([(cx - 110, 730), (cx + 110, 730), (cx + 380, 1450), (cx - 380, 1450)], fill=(12, 35, 85, 245))
    draw.polygon([(cx - 110, 730), (cx + 110, 730), (cx + 380, 1450), (cx - 380, 1450)], outline=(35, 70, 140, 180), width=2)
    # Silk folds
    for i in range(10):
        fx = cx - 300 + i * 65
        draw.line((cx - 50 + i * 10, 500, fx, 1350), fill=(20, 50, 110, 80), width=3)
    # Neckline
    draw.arc((cx - 170, 300, cx + 170, 500), 20, 160, fill=(80, 120, 200, 200), width=5)
    # Shoulder straps
    draw.line((cx - 150, 320, cx - 100, 350), fill=(60, 100, 180, 200), width=6)
    draw.line((cx + 150, 320, cx + 100, 350), fill=(60, 100, 180, 200), width=6)

    # Glowing blue dust particles under investigation light
    for _ in range(200):
        dx = int(rng.random() * W)
        dy = int(rng.random() * H)
        ds = rng.randint(2, 6)
        da = rng.randint(60, 200)
        db = 100 + int(155 * rng.random())
        draw.ellipse((dx - ds, dy - ds, dx + ds, dy + ds), fill=(40, 80, db, da))
    # Extra bright particles around gown
    for _ in range(60):
        dx = cx + int(rng.gauss(0, 200))
        dy = 400 + int(rng.gauss(0, 300))
        ds = rng.randint(3, 8)
        draw.ellipse((dx - ds, dy - ds, dx + ds, dy + ds), fill=(60, 120, 255, rng.randint(100, 220)))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(
        image,
        _standard_cover_resolve_title(locals()),
        _standard_cover_resolve_author(locals()),
        model)
    image.convert("RGB").save(output_path, "PNG", optimize=True)



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
