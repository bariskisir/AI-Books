#!/usr/bin/env python3
"""Cover: The Vellum Engine — Brass gear train on aged vellum, sepia patent-drafting lines, letterpress title."""

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


def draw_juniper(draw):
    random.seed("juniper-docket")
    gradient(draw, (20, 45, 42), (78, 69, 45))
    draw.bitmap((0, 0), glow_layer(820, 650, (154, 198, 143)))
    draw.rectangle((0, 1180, W, 1765), fill=(45, 67, 54, 245))
    for i in range(15):
        x = 80 + i * 105
        h = random.randint(360, 700)
        trunk = (x + random.randint(-20, 20), 1180 - h // 3, x + 24, 1510)
        draw.line(trunk, fill=(61, 46, 32, 230), width=random.randint(12, 24))
        for r in range(150, 30, -30):
            color = (52, 108, 86, 170 + r // 3)
            draw.ellipse((x - r, 1020 - h // 4 - r // 3, x + r, 1020 - h // 4 + r), fill=color)
        for _ in range(12):
            bx = x + random.randint(-105, 105)
            by = 990 - h // 4 + random.randint(-75, 95)
            draw.ellipse((bx, by, bx + 12, by + 12), fill=(88, 126, 142, 225))
    draw.rounded_rectangle((310, 285, 1290, 920), radius=18, fill=(232, 224, 194, 238), outline=(55, 76, 58, 160), width=4)
    draw.text((380, 345), "CHANCERY DOCKET 4182", font=font("georgiab.ttf", 52), fill=(48, 55, 44, 240))
    for y in range(445, 760, 62):
        draw.line((390, y, 1200, y), fill=(104, 115, 85, 140), width=3)
    draw.rectangle((590, 650, 1010, 715), outline=(127, 42, 35, 220), width=5)
    draw.text((620, 662), "FORGED RELEASE", font=font("arialbd.ttf", 34), fill=(126, 45, 38, 235))
    draw.line((230, 1360, 1370, 1205), fill=(204, 144, 72, 215), width=8)
    for x in (360, 720, 1080):
        draw.ellipse((x - 30, 1285, x + 30, 1345), fill=(34, 31, 26, 255), outline=(210, 170, 95, 190), width=5)
    for _ in range(90):
        x, y = random.randint(100, 1500), random.randint(300, 1600)
        draw.ellipse((x, y, x + 5, y + 5), fill=(210, 191, 112, random.randint(50, 135)))
    label = "JUNIPER POLLEN  SURVEY STONE  COURT RECORD"
    bb = draw.textbbox((0, 0), label, font=font("georgia.ttf", 34))
    draw.text(((W - bb[2]) // 2, 185), label, font=font("georgia.ttf", 34), fill=(225, 220, 176, 230))


def draw_ferrite(draw):
    random.seed("ferrite-ledger")
    gradient(draw, (24, 31, 37), (62, 57, 50))
    draw.bitmap((0, 0), glow_layer(820, 760, (118, 160, 185)))
    for y in (1050, 1220, 1390):
        draw.line((90, y, 1510, y - 90), fill=(72, 86, 91, 245), width=38)
        draw.line((90, y + 45, 1510, y - 45), fill=(28, 35, 39, 255), width=10)
    for x in range(180, 1450, 190):
        draw.polygon([(x, 760), (x + 65, 760), (x + 145, 1550), (x + 60, 1550)], fill=(38, 49, 54, 250), outline=(112, 130, 132, 140))
    draw.rounded_rectangle((250, 270, 1350, 850), radius=20, fill=(223, 218, 196, 238), outline=(71, 88, 94, 170), width=5)
    draw.text((335, 335), "FERRITE REPAIR LEDGER", font=font("georgiab.ttf", 56), fill=(42, 48, 52, 240))
    for i, txt in enumerate(["Lot F-19", "Pier Four", "Reserve Weatherization", "Installed: FALSE"]):
        y = 455 + i * 76
        draw.text((360, y), txt, font=font("courbd.ttf", 38), fill=(45, 50, 48, 230))
        draw.line((350, y + 52, 1230, y + 52), fill=(105, 112, 102, 115), width=3)
    for x, y in [(420, 930), (770, 875), (1120, 945), (615, 1125), (990, 1165)]:
        draw.ellipse((x - 70, y - 70, x + 70, y + 70), fill=(32, 35, 37, 255), outline=(180, 190, 184, 170), width=8)
        draw.line((x - 50, y, x + 50, y), fill=(126, 139, 139, 180), width=8)
    draw.arc((300, 1560, 1300, 1980), 205, 335, fill=(192, 104, 61, 230), width=14)
    draw.text((525, 1620), "MAGNETIC TEST", font=font("arialbd.ttf", 48), fill=(226, 196, 151, 230))
    label = "RAIL BRIDGE  PHANTOM STEEL  PUBLIC LEDGER"
    bb = draw.textbbox((0, 0), label, font=font("georgia.ttf", 34))
    draw.text(((W - bb[2]) // 2, 185), label, font=font("georgia.ttf", 34), fill=(220, 229, 224, 230))


def draw_vellum(draw):
    random.seed("vellum-engine")
    gradient(draw, (42, 34, 28), (78, 58, 36))
    draw.bitmap((0, 0), glow_layer(780, 690, (215, 170, 90)))
    draw.rounded_rectangle((245, 240, 1355, 1260), radius=28, fill=(224, 203, 164, 242), outline=(92, 61, 32, 180), width=5)
    draw.text((350, 315), "VELLUM ENGINE PATENT", font=font("georgiab.ttf", 54), fill=(59, 43, 28, 240))
    for cx, cy, r, teeth in [(555, 720, 175, 18), (850, 740, 230, 24), (1030, 505, 115, 14)]:
        for i in range(teeth):
            a = 2 * math.pi * i / teeth
            x = cx + math.cos(a) * (r + 22)
            y = cy + math.sin(a) * (r + 22)
            draw.rectangle((x - 10, y - 10, x + 10, y + 10), fill=(80, 59, 35, 180))
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(76, 55, 34, 235), width=12)
        draw.ellipse((cx - 34, cy - 34, cx + 34, cy + 34), fill=(72, 50, 31, 200))
    draw.line((455, 1070, 1180, 1070), fill=(120, 70, 36, 210), width=8)
    draw.text((515, 1115), "IMPOSSIBLE GEAR TRAIN", font=font("arialbd.ttf", 38), fill=(126, 43, 35, 235))
    for _ in range(120):
        x, y = random.randint(300, 1280), random.randint(380, 1170)
        draw.point((x, y), fill=(93, 62, 35, random.randint(45, 140)))
    draw.rounded_rectangle((330, 1360, 1270, 1640), radius=18, fill=(38, 31, 25, 235), outline=(205, 151, 78, 135), width=4)
    for x in range(410, 1210, 100):
        draw.line((x, 1395, x + 60, 1605), fill=(188, 133, 69, 150), width=4)
    label = "VELLUM DRAWING  CAM WEAR  WORKERS' TRUST"
    bb = draw.textbbox((0, 0), label, font=font("georgia.ttf", 34))
    draw.text(((W - bb[2]) // 2, 185), label, font=font("georgia.ttf", 34), fill=(231, 205, 151, 230))


def draw_oxblood(draw):
    random.seed("oxblood-cantata")
    gradient(draw, (37, 25, 32), (76, 48, 44))
    draw.bitmap((0, 0), glow_layer(815, 660, (154, 52, 60)))
    draw.rounded_rectangle((270, 250, 1330, 1250), radius=22, fill=(232, 219, 188, 242), outline=(112, 54, 53, 175), width=5)
    draw.text((385, 330), "CANTATA IN OXBLOOD", font=font("georgiab.ttf", 56), fill=(100, 28, 34, 245))
    for y in range(485, 1010, 135):
        for offset in range(0, 48, 12):
            draw.line((360, y + offset, 1240, y + offset), fill=(58, 53, 48, 185), width=3)
        for i in range(18):
            x = 390 + i * 47
            yy = y + random.choice([0, 12, 24, 36])
            draw.ellipse((x, yy - 16, x + 24, yy + 8), fill=(42, 37, 34, 220))
            draw.line((x + 22, yy - 45, x + 22, yy), fill=(42, 37, 34, 220), width=4)
    draw.text((430, 1075), "PUBLIC GIFT", font=font("arialbd.ttf", 42), fill=(50, 45, 39, 210))
    draw.rectangle((760, 1060, 1130, 1130), outline=(132, 35, 40, 230), width=5)
    draw.text((790, 1075), "FALSE CLAIM", font=font("arialbd.ttf", 34), fill=(132, 35, 40, 235))
    for x in range(240, 1380, 160):
        draw.rectangle((x, 1395, x + 90, 1650), fill=(46, 37, 41, 240), outline=(174, 92, 83, 140), width=4)
        draw.line((x + 18, 1430, x + 72, 1430), fill=(220, 196, 164, 160), width=3)
    label = "CHOIR LIBRARY  RED PIGMENT  PUBLIC SCORE"
    bb = draw.textbbox((0, 0), label, font=font("georgia.ttf", 34))
    draw.text(((W - bb[2]) // 2, 185), label, font=font("georgia.ttf", 34), fill=(235, 208, 186, 232))


def draw_basalt(draw):
    random.seed("basalt-testament")
    gradient(draw, (20, 31, 37), (70, 55, 45))
    draw.bitmap((0, 0), glow_layer(820, 585, (191, 92, 54)))
    draw.polygon([(0, 1120), (260, 850), (520, 1180), (870, 760), (1240, 1160), (1600, 900), (1600, 1765), (0, 1765)], fill=(31, 36, 38, 255))
    for x in range(80, 1530, 120):
        top = random.randint(850, 1280)
        draw.polygon([(x, top), (x + 85, top + random.randint(-40, 45)), (x + 105, 1765), (x - 25, 1765)], fill=(43, 45, 44, 245), outline=(98, 82, 66, 130))
    draw.rounded_rectangle((315, 285, 1285, 855), radius=20, fill=(225, 214, 186, 240), outline=(89, 62, 48, 170), width=5)
    draw.text((405, 355), "TESTAMENT OF EAMON ORIN", font=font("georgiab.ttf", 50), fill=(49, 43, 36, 238))
    for y in range(460, 685, 56):
        draw.line((410, y, 1175, y), fill=(100, 87, 70, 125), width=3)
    draw.polygon([(690, 700), (760, 650), (850, 675), (900, 760), (830, 830), (725, 810)], fill=(20, 22, 23, 255), outline=(185, 103, 69, 190))
    draw.text((520, 900), "WRONG LAVA FLOW", font=font("arialbd.ttf", 50), fill=(232, 165, 113, 235))
    draw.line((230, 1515, 1380, 1460), fill=(228, 217, 178, 210), width=12)
    for x in (360, 590, 840, 1090, 1310):
        draw.ellipse((x - 25, 1425, x + 25, 1475), fill=(218, 205, 164, 230))
    label = "BASALT SAMPLE  TIDE LEDGER  COMMON SHORE"
    bb = draw.textbbox((0, 0), label, font=font("georgia.ttf", 34))
    draw.text(((W - bb[2]) // 2, 185), label, font=font("georgia.ttf", 34), fill=(235, 200, 162, 230))


SCENES = {
    "The Juniper Docket": draw_juniper,
    "The Ferrite Ledger": draw_ferrite,
    "The Vellum Engine": draw_vellum,
    "The Oxblood Cantata": draw_oxblood,
    "The Basalt Testament": draw_basalt,
}


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "")
    author = metadata.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = metadata.get("model", "")
    image = Image.new("RGBA", (W, H), (30, 32, 31, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    scene = SCENES.get(title, draw_juniper)
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
