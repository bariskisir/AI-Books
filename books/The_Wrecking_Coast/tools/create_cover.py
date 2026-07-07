#!/usr/bin/env python3
"""Cover: The Wrecking Coast — Wreck survivors around driftwood fire in sea cave, storm at cliff entrance, distant signal tower silhouetted."""

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
    """Fragmented memory — mirror shards, floating clocks, fog."""
    random.seed("weight-forgetting")
    gradient(draw, (25, 18, 48), (68, 55, 90))
    draw.bitmap((0, 0), glow_layer(800, 600, (140, 100, 200)))
    # Fragmented mirror pieces
    for _ in range(30):
        cx = random.randint(100, 1500)
        cy = random.randint(200, 1600)
        pts = []
        for _ in range(5):
            pts.append((cx + random.randint(-60, 60), cy + random.randint(-60, 60)))
        alpha = random.randint(100, 200)
        draw.polygon(pts, fill=(180, 200, 230, alpha // 2), outline=(200, 210, 240, alpha), width=3)
    # Floating clocks
    for cx, cy, r in [(300, 400, 90), (1200, 350, 70), (700, 850, 110), (1350, 900, 60), (200, 1000, 80)]:
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(220, 225, 240, 160), width=6)
        draw.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=(220, 225, 240, 200))
        for a in [0, 50, 110, 200, 300]:
            ex = cx + math.cos(math.radians(a)) * r * 0.7
            ey = cy + math.sin(math.radians(a)) * r * 0.7
            draw.line((cx, cy, ex, ey), fill=(220, 225, 240, 120), width=4)
    # Fog bands
    for y in range(300, 1500, 120):
        alpha = random.randint(30, 70)
        draw.line((0, y, W, y + random.randint(-20, 20)), fill=(180, 170, 200, alpha), width=random.randint(40, 80))
    # Doorway silhouette
    draw.rectangle((680, 400, 920, 1500), fill=(20, 15, 35, 200))
    draw.rectangle((700, 420, 900, 1480), fill=(35, 28, 55, 150))
    label = "FORGOTTEN  FRAGMENT  DISAPPEARED"
    bb = draw.textbbox((0, 0), label, font=font("georgia.ttf", 34))
    draw.text(((W - bb[2]) // 2, 185), label, font=font("georgia.ttf", 34), fill=(200, 195, 220, 230))


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
    """Wreck survivors around driftwood fire in sea cave, storm at cliff entrance, distant signal tower silhouetted."""
    random.seed("wrecking-coast")
    gradient(draw, (15, 20, 28), (45, 50, 55))
    draw.bitmap((0, 0), glow_layer(800, 600, (100, 120, 140)))
    cave_left = 0
    cave_right = 1100
    cave_top = 500
    cave_bot = 1700
    draw.polygon([(cave_left, cave_top), (cave_right, cave_top + 200), (cave_right, cave_bot), (cave_left, cave_bot)], fill=(25, 28, 35, 240))
    cave_arch_pts = [(cave_left, cave_top), (300, 400), (600, 350), (900, 400), (cave_right, cave_top + 200)]
    draw.polygon(cave_arch_pts, fill=(30, 33, 40, 250), outline=(50, 55, 62, 180))
    cliff_right_x = W
    cliff_pts = [(cave_right, cave_top + 200), (1200, 600), (1400, 550), (cliff_right_x, 650), (cliff_right_x, cave_bot), (cave_right, cave_bot)]
    draw.polygon(cliff_pts, fill=(28, 32, 38, 240), outline=(50, 55, 62, 150))
    storm_sky = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(storm_sky)
    for _ in range(20):
        sx = random.randint(cave_right, W)
        sy = random.randint(300, 800)
        sw = random.randint(100, 300)
        sh = random.randint(30, 80)
        sd.ellipse((sx, sy, sx + sw, sy + sh), fill=(80, 90, 110, random.randint(20, 50)))
    storm_sky = storm_sky.filter(ImageFilter.GaussianBlur(20))
    draw.bitmap((0, 0), storm_sky)
    for y in range(cave_top + 100, cave_bot, 10):
        alpha = int(20 * (1 - (y - cave_top - 100) / (cave_bot - cave_top - 100)))
        if alpha > 2:
            draw.line((cave_left + 20, y, cave_right - 20, y), fill=(200, 180, 100, alpha), width=1)
    fire_cx, fire_cy = 400, 1250
    for i in range(30, 0, -1):
        fr = i * 3
        alpha = max(5, 80 - i * 2)
        draw.ellipse((fire_cx - fr, fire_cy - fr, fire_cx + fr, fire_cy + fr), fill=(255, 180 + i * 2, 50, alpha))
    draw.ellipse((fire_cx - 15, fire_cy - 15, fire_cx + 15, fire_cy + 15), fill=(255, 200, 80, 200))
    for _ in range(8):
        fx = fire_cx + random.randint(-40, 40)
        fy = fire_cy - random.randint(20, 60)
        fw = random.randint(3, 6)
        draw.line((fx, fy + 20, fx + random.randint(-5, 5), fy - 10), fill=(255, 200, 80, random.randint(60, 150)), width=fw)
    driftwood_pts = [(250, 1280), (350, 1270), (450, 1290), (550, 1270)]
    for i in range(len(driftwood_pts) - 1):
        draw.line((driftwood_pts[i][0], driftwood_pts[i][1], driftwood_pts[i + 1][0], driftwood_pts[i + 1][1]), fill=(40, 30, 20, 200), width=6)
    for _ in range(5):
        dx = fire_cx + random.randint(-120, 120)
        dy = 1270 + random.randint(-10, 20)
        draw.line((dx, dy, dx + random.randint(20, 60), dy), fill=(35, 25, 15), width=random.randint(4, 8))
    survivors = [(320, 1180, 1.0), (480, 1190, 0.85), (550, 1200, 0.9), (280, 1210, 0.75)]
    for sx, sy, sc in survivors:
        sh = int(100 * sc)
        draw.ellipse((sx - 8 * sc, sy - sh, sx + 8 * sc, sy - sh + 16 * sc), fill=(15, 12, 18, 200))
        draw.polygon([(sx - 15 * sc, sy - sh + 16 * sc), (sx + 15 * sc, sy - sh + 16 * sc), (sx + 18 * sc, sy), (sx - 18 * sc, sy)], fill=(15, 12, 18, 200))
    signal_tower_x = 1350
    signal_tower_bot = 1000
    draw.rectangle((signal_tower_x - 15, signal_tower_bot - 300, signal_tower_x + 15, signal_tower_bot), fill=(32, 38, 40, 230))
    draw.rectangle((signal_tower_x - 25, signal_tower_bot - 320, signal_tower_x + 25, signal_tower_bot - 300), fill=(32, 38, 40, 240))
    draw.line((signal_tower_x, signal_tower_bot - 400, signal_tower_x, signal_tower_bot - 320), fill=(32, 38, 40, 200), width=4)
    for _ in range(3):
        lx = signal_tower_x + random.randint(-20, 20)
        ly = signal_tower_bot - 350 + random.randint(-30, 30)
        draw.ellipse((lx - 4, ly - 4, lx + 4, ly + 4), fill=(200, 180, 100, random.randint(80, 180)))
    for x, segments in [(950, 5), (1100, 7)]:
        pts = [(x, 100)]
        for _ in range(segments):
            pts.append((pts[-1][0] + random.randint(-30, 30), pts[-1][1] + random.randint(30, 60)))
        draw.line(pts, fill=(200, 200, 220, random.randint(80, 150)), width=3)
    label = "STORM  SURVIVAL  SIGNAL"
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
