#!/usr/bin/env python3
"""Custom PIL cover generator."""
from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

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

def _scene(image, scene: str, title: str) -> None:
    random.seed(title)
    draw = ImageDraw.Draw(image, "RGBA")
    def gradient(a, b):
        for y in range(H):
            t = y / H
            draw.line((0, y, W, y), fill=tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3)) + (255,))
    if scene == "apothecary":
        gradient((16, 26, 29), (61, 83, 66))
        draw.ellipse((1030, 170, 1400, 540), fill=(232, 226, 186, 185))
        for x in range(120, W, 210):
            draw.rectangle((x, 260, x + 90, 1350), fill=(30, 42, 38, 210), outline=(160, 185, 150, 80), width=3)
            for y in range(330, 1260, 150):
                draw.line((x, y, x + 90, y), fill=(185, 205, 164, 70), width=2)
                draw.ellipse((x + 25, y - 56, x + 65, y - 16), fill=(226, 236, 202, 95))
        for i in range(22):
            bx = 230 + i * 52
            by = 1160 + int(80 * math.sin(i))
            draw.line((bx, by, bx + 35, by - 250), fill=(86, 128, 92, 180), width=5)
            draw.ellipse((bx + 8, by - 280, bx + 74, by - 214), fill=(225, 232, 196, 150))
        draw.rectangle((190, 1320, 1410, 1530), fill=(19, 24, 24, 180), outline=(209, 194, 142, 110), width=4)
    elif scene == "sundial":
        gradient((38, 32, 25), (132, 95, 45))
        cx, cy = W // 2, 900
        for r in range(620, 80, -42):
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(222, 184, 104, 30 + r // 18), width=5)
        for a in range(0, 360, 15):
            rad = math.radians(a)
            draw.line((cx + math.cos(rad) * 150, cy + math.sin(rad) * 150, cx + math.cos(rad) * 590, cy + math.sin(rad) * 590), fill=(238, 204, 129, 80), width=3)
        draw.polygon([(cx, cy - 360), (cx + 78, cy + 70), (cx - 40, cy + 35)], fill=(38, 29, 20, 230), outline=(240, 198, 112, 160))
        draw.line((cx, cy, cx + 470, cy + 65), fill=(5, 5, 5, 185), width=22)
        for i in range(12):
            x = 210 + (i % 4) * 310
            y = 260 + (i // 4) * 145
            draw.arc((x, y, x + 170, y + 170), 0, 300, fill=(230, 190, 95, 120), width=7)
    else:
        gradient((21, 27, 31), (116, 48, 35))
        draw.polygon([(150, 1360), (550, 520), (850, 1040), (1110, 450), (1460, 1360)], fill=(46, 39, 36, 245), outline=(204, 92, 45, 160))
        for r in range(520, 40, -30):
            draw.ellipse((800-r, 780-r, 800+r, 780+r), fill=(233, 95, 41, max(0, 90 - r // 7)))
        for i in range(18):
            x = random.randint(150, 1450)
            y = random.randint(220, 1350)
            draw.line((x, y, x + random.randint(-80, 80), y + random.randint(120, 260)), fill=(218, 82, 39, 90), width=random.randint(2, 5))
        draw.rectangle((245, 1340, 1355, 1530), fill=(230, 210, 160, 170), outline=(63, 44, 34, 190), width=5)

def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")
    image = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    _scene(image, metadata.get("cover_scene", ""), title)
    _draw_standard_cover_title_panel(image, _standard_cover_resolve_title(locals()), author, model)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(output_path, "PNG", optimize=True)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    make_cover(ROOT / args.metadata if not args.metadata.is_absolute() else args.metadata, ROOT / args.out if not args.out.is_absolute() else args.out)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    make_cover(args.metadata, args.out)

if __name__ == "__main__":
    main()
