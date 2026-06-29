#!/usr/bin/env python3
"""Create a project-local raster cover for a Meridian Cycle book."""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560


PALE = (50, 48, 42)
MUTED = (88, 76, 58)


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        FONT_DIR / name,
        FONT_DIR / "arial.ttf",
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def repair_mojibake(text: str) -> str:
    try:
        return text.encode("latin1").decode("utf-8")
    except UnicodeError:
        return text


def lerp(a: int, b: int, t: float) -> int:
    return int(a * (1 - t) + b * t)


def mix(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(lerp(c1[i], c2[i], t) for i in range(3))


def wrap_text(draw: ImageDraw.ImageDraw, text: str, selected_font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
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


def centered_text(
    draw: ImageDraw.ImageDraw,
    y: int,
    lines: list[str],
    selected_font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
    line_gap: int,
    width: int,
) -> int:
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=selected_font)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), line, font=selected_font, fill=fill)
        y += bbox[3] - bbox[1] + line_gap
    return y


def background(top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    img = Image.new("RGB", (W, H), top)
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / (H - 1)
        draw.line((0, y, W, y), fill=mix(top, bottom, t))
    vignette = Image.new("L", (W, H), 0)
    vdraw = ImageDraw.Draw(vignette)
    vdraw.ellipse((-330, -120, W + 330, H + 220), fill=215)
    vignette = vignette.filter(ImageFilter.GaussianBlur(160))
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 145))
    img = Image.composite(img.convert("RGBA"), shade, vignette).convert("RGBA")
    return img


def add_noise_and_stars(img: Image.Image, rng: random.Random, count: int = 320, color=(218, 241, 230)) -> None:
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(count):
        x = rng.randrange(60, W - 60)
        y = rng.randrange(70, H - 470)
        r = rng.choice([1, 1, 1, 2, 2, 3])
        alpha = rng.randrange(55, 155)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(*color, alpha))


def add_glow(img: Image.Image, bbox: tuple[int, int, int, int], color: tuple[int, int, int], blur: int = 50, alpha: int = 95) -> Image.Image:
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow, "RGBA")
    gd.ellipse(bbox, fill=(*color, alpha))
    return Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(blur)))


def draw_gate_scene(img: Image.Image, rng: random.Random) -> None:
    draw = ImageDraw.Draw(img, "RGBA")
    add_noise_and_stars(img, rng, 520, (216, 238, 231))
    center = (W // 2, 1040)
    for radius, color, line_width in [
        (520, (114, 231, 199, 150), 12),
        (430, (210, 247, 232, 122), 7),
        (338, (59, 173, 184, 125), 4),
    ]:
        draw.ellipse((center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius), outline=color, width=line_width)
    for i in range(18):
        angle = i * math.tau / 18 + 0.09
        draw.line(
            (
                center[0] + math.cos(angle) * 350,
                center[1] + math.sin(angle) * 350,
                center[0] + math.cos(angle) * 560,
                center[1] + math.sin(angle) * 560,
            ),
            fill=(105, 220, 203, 95),
            width=5,
        )
    path = [(220 + t * 1160, 1605 - math.sin(t * math.pi) * 690 - t * 260) for t in [i / 179 for i in range(180)]]
    for width_px, alpha in [(30, 32), (18, 55), (7, 205)]:
        draw.line(path, fill=(237, 250, 215, alpha), width=width_px, joint="curve")


def draw_reef_scene(img: Image.Image, rng: random.Random) -> None:
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(180, 1260, 86):
        draw.arc((-220, y, W + 220, y + 440), 190, 350, fill=(119, 212, 220, 40), width=3)
    for base_x in range(130, W, 170):
        base_y = rng.randrange(1180, 1570)
        height = rng.randrange(260, 520)
        branch_color = rng.choice([(165, 238, 232, 150), (126, 214, 199, 135), (221, 244, 236, 125)])
        draw.line((base_x, base_y, base_x + rng.randrange(-70, 70), base_y - height), fill=branch_color, width=rng.randrange(8, 14))
        for _ in range(5):
            yy = base_y - rng.randrange(70, height)
            x2 = base_x + rng.randrange(-120, 120)
            draw.line((base_x, yy, x2, yy - rng.randrange(45, 120)), fill=branch_color, width=rng.randrange(4, 8))
            draw.ellipse((x2 - 14, yy - 132, x2 + 14, yy - 104), fill=(232, 255, 248, 85), outline=(255, 255, 255, 90))
    draw.ellipse((475, 520, 1125, 1170), outline=(207, 245, 242, 135), width=7)
    draw.arc((530, 580, 1070, 1120), 20, 340, fill=(164, 229, 226, 90), width=6)
    for _ in range(42):
        x = rng.randrange(360, 1240)
        y = rng.randrange(620, 1120)
        draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(247, 255, 247, 150))


def draw_red_algorithm_scene(img: Image.Image, rng: random.Random) -> None:
    draw = ImageDraw.Draw(img, "RGBA")
    for x in range(-120, W + 120, 120):
        draw.line((x, 1350, W // 2 + (x - W // 2) * 0.22, 740), fill=(237, 71, 59, 55), width=3)
    for y in range(760, 1380, 95):
        draw.line((170, y, W - 170, y), fill=(237, 71, 59, 45), width=2)
    for i in range(12):
        cx = 190 + i * 108
        cy = 1090 + int(math.sin(i * 0.8) * 70)
        draw.ellipse((cx - 20, cy - 20, cx + 20, cy + 20), fill=(255, 78, 63, 150))
        if i:
            draw.line((cx - 108, 1090 + int(math.sin((i - 1) * 0.8) * 70), cx, cy), fill=(255, 87, 72, 105), width=6)
    for x in range(260, 1380, 210):
        draw.rectangle((x - 56, 1160, x + 56, 1470), fill=(36, 23, 29, 210), outline=(216, 69, 58, 95), width=3)
        draw.arc((x - 86, 1110, x + 86, 1210), 180, 360, fill=(240, 98, 73, 100), width=5)
    for x in [560, 710, 850, 1010]:
        draw.ellipse((x - 22, 1410, x + 22, 1454), fill=(14, 17, 24, 240))
        draw.rounded_rectangle((x - 16, 1450, x + 16, 1545), radius=12, fill=(14, 17, 24, 240))


def draw_orchard_scene(img: Image.Image, rng: random.Random) -> None:
    draw = ImageDraw.Draw(img, "RGBA")
    horizon = 830
    draw.rectangle((0, horizon, W, 1700), fill=(24, 65, 48, 190))
    vanishing = (W // 2, horizon)
    for row in range(9):
        offset = (row - 4) * 190
        draw.line((vanishing[0], vanishing[1], W // 2 + offset * 3, 1660), fill=(162, 212, 125, 90), width=9)
        for step in range(8):
            t = step / 7
            x = lerp(vanishing[0], W // 2 + offset * 3, t)
            y = lerp(vanishing[1], 1660, t)
            scale = 0.32 + t * 1.2
            trunk = int(18 * scale)
            canopy = int(75 * scale)
            draw.rectangle((x - trunk // 2, y - 20 * scale, x + trunk // 2, y + 105 * scale), fill=(76, 52, 39, 185))
            draw.ellipse((x - canopy, y - canopy, x + canopy, y + canopy), fill=(65, 132, 83, 170))
            if (row + step) % 3 == 0:
                draw.ellipse((x - 9, y - 38, x + 9, y - 20), fill=(225, 177, 82, 180))
    draw.rounded_rectangle((585, 655, 1015, 850), radius=18, fill=(196, 205, 175, 195), outline=(235, 241, 220, 110), width=5)
    draw.rectangle((640, 720, 960, 850), fill=(38, 72, 58, 220))
    draw.line((160, 1280, 1460, 940), fill=(117, 198, 213, 115), width=18)


def draw_warship_scene(img: Image.Image, rng: random.Random) -> None:
    draw = ImageDraw.Draw(img, "RGBA")
    add_noise_and_stars(img, rng, 420, (224, 224, 218))
    for _ in range(24):
        x = rng.randrange(80, W - 80)
        y = rng.randrange(360, 1370)
        r = rng.randrange(18, 58)
        draw.polygon(
            [(x + math.cos(a) * r * rng.uniform(0.65, 1.25), y + math.sin(a) * r * rng.uniform(0.65, 1.25)) for a in [i * math.tau / 7 for i in range(7)]],
            fill=(119, 112, 103, 135),
            outline=(202, 194, 178, 70),
        )
    hull = [(260, 990), (580, 850), (1250, 900), (1420, 990), (1235, 1100), (575, 1130)]
    draw.polygon(hull, fill=(142, 165, 170, 230), outline=(232, 242, 237, 110))
    draw.polygon([(420, 970), (720, 900), (1180, 930), (1260, 990), (1090, 1035), (690, 1030)], fill=(38, 54, 65, 220))
    draw.line((390, 1085, 1235, 970), fill=(125, 225, 211, 120), width=6)
    for x in range(520, 1140, 105):
        draw.ellipse((x - 18, 958, x + 18, 994), fill=(171, 239, 230, 150))
    draw.line((260, 1190, 1420, 1225), fill=(250, 250, 230, 55), width=13)


def draw_lumen_scene(img: Image.Image, rng: random.Random) -> None:
    draw = ImageDraw.Draw(img, "RGBA")
    add_noise_and_stars(img, rng, 520, (214, 230, 249))
    for alpha, width in [(42, 210), (65, 122), (135, 42)]:
        draw.line((800, 250, 800, 1510), fill=(114, 177, 255, alpha), width=width)
    for r, alpha in [(330, 75), (230, 110), (105, 210)]:
        draw.ellipse((800 - r, 855 - r, 800 + r, 855 + r), outline=(168, 209, 255, alpha), width=9)
    for i in range(54):
        angle = i * math.tau / 54
        if i % 7 in (0, 1):
            continue
        x = 800 + math.cos(angle) * 500
        y = 855 + math.sin(angle) * 260
        draw.ellipse((x - 6, y - 6, x + 6, y + 6), fill=(238, 252, 255, 130))
    draw.arc((435, 1220, 1165, 1650), 194, 346, fill=(213, 229, 232, 150), width=18)
    draw.line((800, 1435, 800, 1600), fill=(213, 229, 232, 140), width=18)
    draw.arc((620, 1275, 980, 1545), 205, 335, fill=(236, 245, 239, 180), width=11)


def draw_mirror_scene(img: Image.Image, rng: random.Random) -> None:
    draw = ImageDraw.Draw(img, "RGBA")
    for i in range(6):
        x1 = 185 + i * 220
        color = rng.choice([(72, 226, 221), (228, 92, 190), (245, 193, 80)])
        draw.rounded_rectangle((x1, 530, x1 + 150, 1340), radius=24, outline=(*color, 155), width=10, fill=(14, 21, 31, 130))
        draw.line((x1 + 20, 590, x1 + 130, 1280), fill=(*color, 45), width=5)
        draw.ellipse((x1 + 56, 830, x1 + 94, 882), fill=(231, 245, 239, 80))
        draw.rounded_rectangle((x1 + 63, 880, x1 + 87, 1050), radius=10, fill=(231, 245, 239, 58))
    for y in range(1280, 1680, 85):
        draw.line((180, y, 1420, y), fill=(80, 223, 211, 34), width=3)
    draw.line((800, 485, 800, 1640), fill=(255, 255, 255, 40), width=3)


def draw_salt_parliament_scene(img: Image.Image, rng: random.Random) -> None:
    draw = ImageDraw.Draw(img, "RGBA")
    for r, alpha in [(610, 35), (470, 48), (330, 72), (190, 95)]:
        draw.ellipse((800 - r, 1070 - r * 0.46, 800 + r, 1070 + r * 0.46), outline=(229, 245, 232, alpha), width=8)
    for i in range(36):
        angle = i * math.tau / 36
        x = 800 + math.cos(angle) * (270 + (i % 3) * 120)
        y = 1070 + math.sin(angle) * (125 + (i % 3) * 55)
        if i % 4 == 0:
            draw.polygon([(x, y - 45), (x + 32, y + 30), (x - 35, y + 22)], fill=(239, 255, 247, 125))
        else:
            draw.ellipse((x - 30, y - 22, x + 30, y + 22), fill=(125, 219, 202, 125))
    for base_x in range(170, 1470, 190):
        draw.line((base_x, 1430, base_x + rng.randrange(-80, 80), 920), fill=(178, 238, 226, 105), width=7)
    draw.polygon([(800, 835), (892, 1045), (800, 1265), (708, 1045)], outline=(255, 255, 255, 120), fill=(208, 247, 236, 40))


def draw_ashes_scene(img: Image.Image, rng: random.Random) -> None:
    draw = ImageDraw.Draw(img, "RGBA")
    add_noise_and_stars(img, rng, 350, (225, 218, 205))
    for r in [360, 520, 690]:
        draw.arc((800 - r, 830 - r * 0.42, 800 + r, 830 + r * 0.42), 8, 352, fill=(209, 168, 116, 52), width=5)
    for i in range(9):
        x = 320 + i * 120
        y = 810 + int(math.sin(i) * 38)
        draw.rectangle((x - 34, y - 24, x + 34, y + 24), fill=(151, 122, 93, 145), outline=(238, 213, 172, 80))
    draw.rounded_rectangle((310, 1190, 1290, 1500), radius=18, fill=(42, 36, 33, 230), outline=(222, 198, 160, 95), width=5)
    draw.polygon([(470, 1155), (1130, 1155), (1020, 1025), (580, 1025)], fill=(74, 62, 54, 210), outline=(225, 197, 156, 90))
    draw.rectangle((610, 1055, 990, 1280), fill=(238, 229, 199, 220))
    for y in range(1090, 1248, 34):
        draw.line((650, y, 950, y), fill=(83, 61, 52, 145), width=4)
    draw.ellipse((760, 960, 840, 1040), fill=(247, 226, 155, 130))
    for _ in range(80):
        x = rng.randrange(170, 1450)
        y = rng.randrange(410, 1580)
        draw.line((x, y, x + rng.randrange(-20, 20), y + rng.randrange(16, 55)), fill=(222, 177, 112, rng.randrange(25, 80)), width=2)


def draw_moon_fire_scene(img: Image.Image, rng: random.Random) -> None:
    draw = ImageDraw.Draw(img, "RGBA")
    add_noise_and_stars(img, rng, 620, (229, 229, 218))
    img.alpha_composite(add_glow(Image.new("RGBA", (W, H), (0, 0, 0, 0)), (330, 360, 1270, 1300), (231, 228, 197), 70, 105))
    draw = ImageDraw.Draw(img, "RGBA")
    draw.ellipse((445, 475, 1155, 1185), fill=(211, 212, 189, 225), outline=(255, 250, 220, 130), width=5)
    draw.ellipse((595, 430, 1245, 1125), fill=(9, 15, 27, 225))
    ship = [(585, 995), (800, 875), (1015, 995), (1015, 1110), (800, 1195), (585, 1110)]
    draw.polygon(ship, fill=(119, 140, 145, 220), outline=(232, 239, 222, 110))
    for x in [690, 760, 830, 900]:
        draw.rectangle((x - 20, 1012, x + 20, 1080), fill=(245, 237, 184, 120))
    for i in range(10):
        t = i / 9
        path = [(250 + step * 22, 1530 - math.sin((step / 60 + t) * math.pi) * (150 + i * 8) - i * 25) for step in range(61)]
        draw.line(path, fill=(245, 107, 57, 40 + i * 10), width=4 + i // 3)
    for angle in [0.2, 0.9, 1.45, 2.35, 2.9]:
        draw.line((800, 1120, 800 + math.cos(angle) * 620, 1120 + math.sin(angle) * 360), fill=(119, 226, 209, 88), width=5)


SCENES = {
    0: ((9, 18, 33), (14, 56, 58), draw_gate_scene),
    1: ((5, 20, 34), (9, 83, 91), draw_reef_scene),
    2: ((30, 13, 18), (92, 35, 29), draw_red_algorithm_scene),
    3: ((18, 39, 45), (45, 88, 49), draw_orchard_scene),
    4: ((12, 15, 24), (64, 58, 51), draw_warship_scene),
    5: ((8, 14, 34), (31, 38, 80), draw_lumen_scene),
    6: ((13, 16, 29), (42, 23, 54), draw_mirror_scene),
    7: ((8, 38, 47), (42, 86, 79), draw_salt_parliament_scene),
    8: ((22, 19, 22), (83, 63, 50), draw_ashes_scene),
    9: ((6, 12, 26), (50, 37, 47), draw_moon_fire_scene),
}


def draw_title_block(img: Image.Image, title: str, author: str, book_number: str, model: str = "") -> None:
    draw = ImageDraw.Draw(img, "RGBA")
    title_font = font("arialbd.ttf", 116)
    if len(title) > 28:
        title_font = font("arialbd.ttf", 104)
    author_font = font("arialbd.ttf", 50)
    small_font = font("arial.ttf", 38)
    title_lines = wrap_text(draw, title.upper(), title_font, 1260)

    draw.rectangle((0, 1765, W, H), fill=(235, 229, 214, 255))
    draw.line((180, 1782, W - 180, 1782), fill=(94, 82, 66, 170), width=3)
    y = 1840
    y = centered_text(draw, y, ["THE MERIDIAN CYCLE", book_number], small_font, MUTED, 18, W)
    y += 70
    y = centered_text(draw, y, title_lines, title_font, PALE, 18, W)
    y += 120
    centered_text(draw, y, [author], author_font, (88, 76, 58), 12, W)
    if model:
        mf = font("arial.ttf", 24)
        centered_text(draw, H - 80, [model], mf, (112, 102, 84), 6, W)


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = repair_mojibake(metadata["title"])
    author = repair_mojibake(metadata.get("author", "Barış Kısır"))
    number = int(metadata.get("number", 0))
    book_number = f"BOOK {number}"

    top, bottom, scene = SCENES.get(number, SCENES[0])
    rng = random.Random(f"{number}:{title}")
    img = background(top, bottom)
    scene(img, rng)
    img = add_glow(img, (360, 465, 1240, 1365), mix(top, bottom, 0.45), 95, 40)
    model = metadata.get("model", "")
    draw_title_block(img, title, author, book_number, model)

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