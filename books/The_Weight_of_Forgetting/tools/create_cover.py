#!/usr/bin/env python3
"""Cover: The Weight of Forgetting — Woman's silhouette against fractured fogged-over glass greenhouse, cold blue-gray palette."""

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
    _standard_cover_resolve_title,
    _standard_cover_resolve_author,
    _draw_standard_cover_title_panel,
)

ROOT = Path(__file__).resolve().parent.parent
W, H = 1600, 2560
FONT_DIR = Path("C:/Windows/Fonts")


def font(name: str, size: int):
    for candidate in (FONT_DIR / name, FONT_DIR / "arialbd.ttf", FONT_DIR / "arial.ttf"):
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def gradient(draw, top, bottom):
    for y in range(H):
        t = y / H
        fill = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3)) + (255,)
        draw.line((0, y, W, y), fill=fill)


def glow_layer(cx, cy, color):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer, "RGBA")
    for r in range(80, 760, 80):
        alpha = max(8, 80 - r // 12)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(*color, alpha), width=20)
    return layer.filter(ImageFilter.GaussianBlur(20))


def draw_weight_of_forgetting(draw):
    """Woman's silhouette against fractured fogged-over glass greenhouse, cold blue-gray palette."""
    random.seed("weight-forgetting")
    gradient(draw, (25, 18, 48), (68, 55, 90))
    draw.bitmap((0, 0), glow_layer(800, 600, (140, 100, 200)))
    for _ in range(25):
        cx = random.randint(200, 1400)
        cy = random.randint(300, 1500)
        pts = []
        for _ in range(6):
            pts.append((cx + random.randint(-80, 80), cy + random.randint(-80, 80)))
        alpha = random.randint(60, 140)
        draw.polygon(pts, fill=(180, 200, 230, alpha // 3), outline=(200, 210, 240, alpha // 2), width=2)
    greenhouse_left = 500
    greenhouse_right = 1100
    greenhouse_top = 300
    greenhouse_bot = 1400
    draw.rectangle((greenhouse_left, greenhouse_top, greenhouse_right, greenhouse_bot), fill=(30, 35, 55, 180))
    draw.rectangle((greenhouse_left, greenhouse_top, greenhouse_right, greenhouse_bot), outline=(50, 55, 80, 150), width=4)
    for x in range(greenhouse_left + 60, greenhouse_right, 80):
        draw.line((x, greenhouse_top, x, greenhouse_bot), fill=(50, 55, 80, 100), width=2)
    for y in range(greenhouse_top + 60, greenhouse_bot, 80):
        draw.line((greenhouse_left, y, greenhouse_right, y), fill=(50, 55, 80, 100), width=2)
    for _ in range(40):
        fx = random.randint(greenhouse_left + 20, greenhouse_right - 20)
        fy = random.randint(greenhouse_top + 20, greenhouse_bot - 20)
        fw = random.randint(20, 80)
        fh = random.randint(10, 40)
        draw.ellipse((fx, fy, fx + fw, fy + fh), fill=(220, 225, 240, random.randint(30, 80)))
    cx = W // 2
    sil_y = greenhouse_bot - 50
    draw.ellipse((cx - 12, sil_y - 180, cx + 12, sil_y - 150), fill=(15, 12, 25, 200))
    draw.polygon([(cx - 22, sil_y - 150), (cx + 22, sil_y - 150), (cx + 25, sil_y), (cx - 25, sil_y)], fill=(15, 12, 25, 200))
    draw.line((cx, sil_y, cx, sil_y + 40), fill=(15, 12, 25, 200), width=5)
    label = "COLD  BLUE  FOG"
    bb = draw.textbbox((0, 0), label, font=font("georgia.ttf", 34))
    draw.text(((W - bb[2]) // 2, 185), label, font=font("georgia.ttf", 34), fill=(180, 195, 220, 230))


def draw_indigo_wives(draw):
    """Indigo plantation — vats, Spanish moss, plantation house at dusk."""
    random.seed("indigo-wives")
    gradient(draw, (15, 15, 35), (40, 28, 65))
    draw.bitmap((0, 0), glow_layer(800, 700, (90, 50, 130)))
    # Indigo vats
    for x, y in [(150, 900), (500, 950), (850, 880), (1200, 920)]:
        draw.rectangle((x, y, x + 200, y + 150), fill=(12, 8, 35, 230), outline=(70, 40, 100, 200), width=4)
        draw.text((x + 30, y + 50), "INDIGO", font=font("arial.ttf", 30), fill=(80, 50, 120, 200))
    # Spanish moss trees
    random.seed("indigo-moss")
    for x, tx, ty in [(100, 150, 400), (380, 200, 350), (780, 120, 380), (1100, 180, 370), (1450, 140, 420)]:
        draw.line((x, ty + 300, x, ty), fill=(40, 25, 20, 230), width=18)
        for _ in range(40):
            mx = x + random.randint(-120, 120)
            my = ty + random.randint(50, 300)
            draw.line((mx, my, mx + random.randint(-15, 15), my + random.randint(15, 60)), fill=(120, 140, 120, random.randint(80, 160)), width=4)
    # Plantation house silhouette
    house = [(550, 750), (550, 450), (650, 380), (750, 450), (750, 750)]
    draw.polygon(house, fill=(15, 10, 15, 240), outline=(60, 50, 70, 180))
    for cx in (590, 710):
        draw.rectangle((cx, 500, cx + 40, 600), fill=(35, 30, 40, 200), outline=(60, 50, 70, 120), width=2)
    draw.rectangle((640, 620, 690, 720), fill=(30, 25, 35, 200))
    # Fireflies
    for _ in range(80):
        x, y = random.randint(50, 1550), random.randint(600, 1600)
        draw.ellipse((x, y, x + 5, y + 5), fill=(200, 220, 150, random.randint(60, 180)))
    label = "INDIGO  RESISTANCE  FREEDOM"
    bb = draw.textbbox((0, 0), label, font=font("georgia.ttf", 34))
    draw.text(((W - bb[2]) // 2, 185), label, font=font("georgia.ttf", 34), fill=(170, 150, 200, 230))


def draw_frozen_testimony(draw):
    """Frozen waterfront — ice, police tape, skeletal remains, street lamp."""
    random.seed("frozen-testimony")
    gradient(draw, (20, 28, 40), (55, 60, 70))
    draw.bitmap((0, 0), glow_layer(800, 650, (120, 150, 180)))
    # Frozen harbor
    for _ in range(30):
        x = random.randint(0, W)
        y = random.randint(1100, 1700)
        draw.ellipse((x - random.randint(20, 60), y - random.randint(10, 30), x + random.randint(20, 60), y + random.randint(5, 15)), fill=(200, 220, 240, random.randint(30, 80)))
    # Ice cracks
    for _ in range(15):
        x, y = random.randint(100, 1500), random.randint(1000, 1700)
        pts = [(x, y)]
        for _ in range(10):
            pts.append((pts[-1][0] + random.randint(-30, 30), pts[-1][1] + random.randint(10, 40)))
        draw.line(pts, fill=(180, 200, 230, random.randint(50, 120)), width=3)
    # Street lamp
    draw.line((310, 100, 310, 1600), fill=(60, 65, 72, 230), width=12)
    draw.ellipse((270, 70, 350, 180), fill=(220, 180, 80, 100), outline=(220, 180, 80, 200), width=6)
    # Light cone
    for y in range(200, 900, 10):
        t = (y - 200) / 700
        spread = 100 + t * 400
        alpha = max(10, int(80 * (1 - t)))
        draw.line((310 - spread // 2, y, 310 + spread // 2, y), fill=(200, 180, 100, alpha))
    # Skeletal outline
    draw.line((1200, 500, 1200, 650), fill=(220, 200, 180, 200), width=8)
    draw.line((1200, 500, 1160, 560), fill=(220, 200, 180, 180), width=6)
    draw.line((1200, 500, 1240, 560), fill=(220, 200, 180, 180), width=6)
    draw.ellipse((1170, 440, 1230, 500), fill=(160, 150, 140, 150), outline=(220, 200, 180, 200), width=5)
    # Police tape
    for x in range(400, 1300, 50):
        yy = 800 + math.sin(x / 30) * 30
        draw.rectangle((x, yy, x + 20, yy + 40), fill=(180, 40, 30, 200))
        draw.text((x + 2, yy + 5), "CAUTION", font=font("arial.ttf", 14), fill=(240, 200, 80, 220))
    label = "COLD CASE  WINTER  EVIDENCE"
    bb = draw.textbbox((0, 0), label, font=font("georgia.ttf", 34))
    draw.text(((W - bb[2]) // 2, 185), label, font=font("georgia.ttf", 34), fill=(190, 210, 230, 230))


def draw_concrete_chorus(draw):
    """London by night — Thames, magical runes, creature silhouettes."""
    random.seed("concrete-chorus")
    gradient(draw, (12, 15, 25), (30, 35, 50))
    draw.bitmap((0, 0), glow_layer(800, 700, (60, 180, 120)))
    # Thames skyline
    for x, w, h in [(50, 120, 550), (220, 90, 650), (380, 130, 500), (560, 100, 600), (720, 140, 480), (920, 110, 580), (1100, 130, 520), (1280, 100, 600), (1440, 120, 540)]:
        draw.rectangle((x, H - h, x + w, H), fill=(18, 22, 30, 220))
        for _ in range(8):
            wx = x + random.randint(5, w - 5)
            wy = H - h + random.randint(10, h - 20)
            draw.rectangle((wx, wy, wx + 8, wy + 12), fill=(40, 50, 65, 180))
    # London Eye reference
    draw.ellipse((680, 580, 920, 820), outline=(80, 180, 130, 150), width=6)
    for a in range(0, 360, 30):
        ex = 800 + math.cos(math.radians(a)) * 120
        ey = 700 + math.sin(math.radians(a)) * 120
        draw.ellipse((ex - 5, ey - 5, ex + 5, ey + 5), fill=(100, 200, 150, 180))
    draw.line((800, 820, 800, 1100), fill=(80, 180, 130, 120), width=5)
    # Magical runes
    runes = ["ᚠ", "ᚢ", "ᚦ", "ᚨ", "ᚱ", "ᚲ", "ᚷ", "ᚹ", "ᚺ", "ᚾ", "ᛁ", "ᛃ", "ᛇ", "ᛈ", "ᛉ", "ᛊ", "ᛏ", "ᛒ", "ᛖ", "ᛗ", "ᛚ", "ᛝ", "ᛟ", "ᛞ"]
    for i, (x, y, size) in enumerate([(120, 320, 40), (350, 250, 52), (580, 380, 36), (900, 280, 48), (1150, 340, 40), (1380, 260, 44), (250, 750, 34), (1050, 680, 38)]):
        r = runes[i % len(runes)]
        draw.text((x, y), r, font=font("arialbd.ttf", size), fill=(100, 220, 150, random.randint(100, 200)))
    # Creature silhouettes
    for x, y, w, h in [(100, 1300, 80, 120), (380, 1280, 60, 140), (720, 1340, 70, 100), (1050, 1300, 90, 130), (1350, 1320, 75, 115)]:
        draw.ellipse((x, y + h - 30, x + w, y + h), fill=(25, 30, 40, 240))
        draw.polygon([(x + w//2 - 15, y), (x + w//2, y - 30), (x + w//2 + 15, y)], fill=(25, 30, 40, 240))
    # Gorgon snake shadow
    for x, y in [(440, 1180), (520, 1130), (480, 1220)]:
        draw.line((x, y, x + random.randint(-10, 10), y + random.randint(-20, 40)), fill=(80, 160, 120, 120), width=6)
    label = "LONDON  MYTH  ACCORD"
    bb = draw.textbbox((0, 0), label, font=font("georgia.ttf", 34))
    draw.text(((W - bb[2]) // 2, 185), label, font=font("georgia.ttf", 34), fill=(140, 220, 170, 230))


def draw_wrecking_coast(draw):
    """Stormy Irish coast — cliffs, crashing waves, shipwreck, signal tower."""
    random.seed("wrecking-coast")
    gradient(draw, (15, 20, 28), (45, 50, 55))
    draw.bitmap((0, 0), glow_layer(800, 600, (100, 120, 140)))
    # Cliffs
    cliff = [(0, 1200)]
    for _ in range(20):
        x = _ * 85
        cliff.append((x, 1000 + random.randint(-80, 120)))
    cliff.append((W, 1350))
    cliff.append((W, H))
    cliff.append((0, H))
    draw.polygon(cliff, fill=(30, 35, 40, 250), outline=(55, 60, 68, 180))
    # Wave lines
    for y in range(1300, 1800, 15):
        t = (y - 1300) / 500
        alpha = int(max(20, 120 * (1 - t)))
        draw.line((0, y + math.sin(y / 30) * 20, W, y + math.sin((y + 300) / 25) * 25), fill=(70, 100, 130, alpha), width=8)
    # Breaking waves white foam
    for _ in range(40):
        x = random.randint(100, 1500)
        y = random.randint(1250, 1550)
        draw.ellipse((x - random.randint(10, 35), y - random.randint(5, 15), x + random.randint(10, 35), y + random.randint(3, 10)), fill=(200, 220, 240, random.randint(60, 140)))
    # Shipwreck mast
    draw.line((1200, 600, 1200, 1200), fill=(40, 35, 30, 230), width=14)
    draw.line((1180, 650, 1220, 650), fill=(40, 35, 30, 220), width=10)
    draw.line((1150, 750, 1250, 750), fill=(40, 35, 30, 220), width=8)
    # Broken hull
    draw.polygon([(1140, 1180), (1260, 1180), (1280, 1280), (1120, 1280)], fill=(35, 30, 25, 200), outline=(55, 50, 45, 160))
    # Signal tower ruin
    draw.rectangle((280, 580, 380, 1200), fill=(32, 38, 40, 230), outline=(55, 60, 65, 160), width=6)
    draw.rectangle((260, 550, 400, 620), fill=(32, 38, 40, 240), outline=(55, 60, 65, 160), width=5)
    draw.line((295, 670, 295, 1150), fill=(50, 55, 58, 140), width=4)
    draw.line((365, 670, 365, 1150), fill=(50, 55, 58, 140), width=4)
    # Lightning
    for x, segments in [(950, 5), (1100, 7), (450, 6)]:
        pts = [(x, 100)]
        for _ in range(segments):
            pts.append((pts[-1][0] + random.randint(-40, 40), pts[-1][1] + random.randint(40, 80)))
        draw.line(pts, fill=(200, 200, 220, random.randint(100, 200)), width=5)
    label = "STORM  SHIPWRECK  SURVIVAL"
    bb = draw.textbbox((0, 0), label, font=font("georgia.ttf", 34))
    draw.text(((W - bb[2]) // 2, 185), label, font=font("georgia.ttf", 34), fill=(180, 200, 220, 230))


SCENES = {
    "The Weight of Forgetting": draw_weight_of_forgetting,
    "The Indigo Wives": draw_indigo_wives,
    "The Frozen Testimony": draw_frozen_testimony,
    "The Concrete Chorus": draw_concrete_chorus,
    "The Wrecking Coast": draw_wrecking_coast,
}


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
    title = metadata.get("title", "")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")
    image = Image.new("RGBA", (W, H), (30, 32, 31, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    scene = SCENES.get(title, draw_weight_of_forgetting)
    scene(draw)
    _draw_standard_cover_title_panel(image, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    output_path.parent.mkdir(parents=True, exist_ok=True)
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
