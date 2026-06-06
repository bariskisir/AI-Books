#!/usr/bin/env python3
"""Create a project-local raster cover for Larklight — lighthouse on the Maine coast."""

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

    img = Image.new("RGB", (W, H), (15, 18, 22))
    draw = ImageDraw.Draw(img, "RGBA")

    # Night sky gradient.
    for y in range(H):
        t = y / (H - 1)
        draw.line((0, y, W, y), fill=(int(8 + 16 * t), int(10 + 20 * t), int(16 + 22 * t), 255))

    # Stars.
    for _ in range(180):
        x = rng.randrange(0, W)
        yy = rng.randrange(0, 1100)
        rad = rng.choice([1, 1, 2])
        alpha = rng.randrange(80, 210)
        draw.ellipse((x - rad, yy - rad, x + rad, yy + rad), fill=(240, 235, 220, alpha))

    # Moon and glow.
    moon_x = rng.randrange(1100, 1450)
    moon_y = rng.randrange(120, 280)
    moon_r = 70
    draw.ellipse((moon_x - moon_r, moon_y - moon_r, moon_x + moon_r, moon_y + moon_r),
                 fill=(230, 225, 205, 200))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((moon_x - 200, moon_y - 200, moon_x + 200, moon_y + 200),
               fill=(200, 195, 175, 12))
    glow = glow.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img.convert("RGBA"), glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Sea layer.
    sea_y = 1680
    for y in range(sea_y, H, 4):
        t = (y - sea_y) / (H - sea_y)
        r, g, b = int(12 + 8 * t), int(18 + 10 * t), int(30 + 14 * t)
        wave = rng.randrange(-3, 4)
        draw.line((0, y + wave, W, y), fill=(r, g, b, 220))
    for _ in range(35):
        x = rng.randrange(0, W)
        yy = sea_y + rng.randrange(0, H - sea_y - 40)
        draw.ellipse((x, yy, x + rng.randrange(30, 120), yy + 6),
                     fill=(220, 225, 230, rng.randrange(25, 70)))

    # Granite cliff silhouette.
    cliff = []
    for x in range(0, W + 20, 30):
        yy = 1500 + int(80 * rng.random()) + int(30 * (x / W))
        cliff.append((x, yy))
    draw.polygon(cliff + [(W, H), (0, H)], fill=(20, 22, 26, 235))

    # Lighthouse tower.
    lx = 760
    tower_w, tower_h = 88, 860
    t_top = 1650 - tower_h
    t_base = 1650
    for y in range(t_top, t_base, 4):
        t = (y - t_top) / tower_h
        w = int(tower_w * (1 - t * 0.12))
        shade = int(10 + 14 * t)
        draw.rectangle((lx - w // 2, y, lx + w // 2, y + 4),
                       fill=(shade + 20, shade + 22, shade + 26, 240))

    # Galleries.
    for yo in [80, 380, 680]:
        gy = t_top + yo
        draw.rectangle((lx - tower_w // 2 - 10, gy - 2, lx + tower_w // 2 + 10, gy + 6),
                       fill=(28, 32, 36, 240))

    # Lantern room.
    lan_w, lan_h = 76, 110
    lan_y = t_top - lan_h
    draw.rectangle((lx - lan_w // 2, lan_y, lx + lan_w // 2, t_top),
                   fill=(18, 20, 24, 245))
    for px in range(-2, 3):
        px_x = lx - 28 + px * 14
        draw.rectangle((px_x, lan_y + 8, px_x + 10, t_top - 10),
                       fill=(40, 46, 58, 160), outline=(50, 55, 65, 80))
    draw.polygon([(lx - 48, lan_y), (lx, lan_y - 38), (lx + 48, lan_y)],
                 fill=(12, 14, 16, 250))

    # Light beam.
    beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam)
    rad_a = math.radians(-18)
    bl = 900
    bd.polygon([
        (lx, lan_y + 30),
        (lx - bl, lan_y + 30 - int(bl * math.tan(rad_a))),
        (lx - bl + 150, lan_y + 30 - int(bl * math.tan(rad_a)) - 25),
    ], fill=(255, 245, 190, 20))
    bd.polygon([
        (lx, lan_y + 30),
        (lx + bl, lan_y + 30 - int(bl * math.tan(-rad_a))),
        (lx + bl - 150, lan_y + 30 - int(bl * math.tan(-rad_a)) + 25),
    ], fill=(255, 245, 190, 14))
    beam = beam.filter(ImageFilter.GaussianBlur(22))
    img = Image.alpha_composite(img, beam)

    # Foreground rocks.
    for _ in range(18):
        rx = rng.randrange(0, W)
        ry = rng.randrange(1800, 2200)
        rw, rh = rng.randrange(40, 160), rng.randrange(20, 60)
        draw.ellipse((rx, ry, rx + rw, ry + rh), fill=(18, 20, 22, 200))

    # Fog.
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog)
    for _ in range(50):
        fy = rng.randrange(900, 1800)
        fx = rng.randrange(-200, W + 200)
        fd.ellipse((fx, fy, fx + rng.randrange(300, 900), fy + rng.randrange(60, 160)),
                   fill=(190, 195, 200, rng.randrange(5, 15)))
    fog = fog.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, fog)

    draw = ImageDraw.Draw(img, "RGBA")
    # Title panel.
    draw.rectangle((0, 1940, W, H), fill=(5, 8, 10, 195))
    draw.line((200, 1965, W - 200, 1965), fill=(190, 195, 180, 120), width=2)

    title_font = font("georgiab.ttf", 118)
    author_font = font("arialbd.ttf", 46)
    subtitle_font = font("arial.ttf", 30)
    y = 2000
    y = centered(draw, y, ["LARKLIGHT POINT"], subtitle_font, (170, 178, 168), 8)
    y += 70
    y = centered(draw, y, wrap(draw, title.upper(), title_font, 1250), title_font, (240, 242, 228), 20)
    y += 100
    centered(draw, y, [author], author_font, (210, 216, 200), 10)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()))
    img.convert("RGB").save(output_path, "PNG", optimize=True)



def _standard_cover_font(name: str, size: int):
    font_dir = globals().get("FONT_DIR", globals().get("FONTS_DIR", None))
    candidates = []
    if font_dir is not None:
        candidates.append(Path(font_dir) / name)
    candidates.extend([
        Path("C:/Windows/Fonts") / name,
        Path("C:/Windows/Fonts") / "arialbd.ttf",
        Path("C:/Windows/Fonts") / "arial.ttf",
    ])
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def _standard_cover_repair_text(text: str) -> str:
    try:
        return text.encode("latin1").decode("utf-8")
    except UnicodeError:
        return text


def _standard_cover_wrap(draw, text: str, selected_font, max_width: int) -> list[str]:
    words = text.split()
    lines = []
    current = []
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


def _standard_cover_center(draw, y: int, lines: list[str], selected_font, fill, line_gap: int, width: int) -> int:
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=selected_font)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), line, font=selected_font, fill=fill)
        y += bbox[3] - bbox[1] + line_gap
    return y


def _standard_cover_title_font(draw, title: str, max_width: int):
    for size in (116, 104, 96, 88, 80, 72):
        selected = _standard_cover_font("arialbd.ttf", size)
        lines = _standard_cover_wrap(draw, title.upper(), selected, max_width)
        heights = [draw.textbbox((0, 0), line, font=selected)[3] - draw.textbbox((0, 0), line, font=selected)[1] for line in lines]
        total = sum(heights) + max(0, len(lines) - 1) * 18
        if len(lines) <= 4 and total <= 430:
            return selected, lines, 18
    selected = _standard_cover_font("arialbd.ttf", 68)
    return selected, _standard_cover_wrap(draw, title.upper(), selected, max_width), 16


def _standard_cover_metadata_from_locals(local_vars):
    for key in ("metadata", "meta", "data", "m", "book", "book_data"):
        value = local_vars.get(key)
        if isinstance(value, dict):
            return value

    candidates = []
    args = local_vars.get("args")
    if args is not None:
        candidates.append(getattr(args, "metadata", None))
    for key in ("metadata_path", "meta_path", "mp"):
        candidates.append(local_vars.get(key))

    for metadata_path in candidates:
        if not metadata_path:
            continue
        try:
            json_mod = __import__("json")
            path_cls = __import__("pathlib").Path
            return json_mod.loads(path_cls(metadata_path).read_text(encoding="utf-8"))
        except Exception:
            continue
    return {}


def _standard_cover_resolve_title(local_vars):
    for key in ("title", "ti", "book_title", "TITLE"):
        value = local_vars.get(key)
        if value:
            return value

    metadata = _standard_cover_metadata_from_locals(local_vars)
    for key in ("title", "book_title", "name"):
        value = metadata.get(key)
        if value:
            return value

    args = local_vars.get("args")
    candidates = []
    if args is not None:
        candidates.append(getattr(args, "out", None))
    for key in ("output_path", "out_path", "op", "out"):
        candidates.append(local_vars.get(key))

    for output_path in candidates:
        if not output_path:
            continue
        try:
            path_cls = __import__("pathlib").Path
            stem = path_cls(output_path).stem.replace("_", " ").strip()
            if stem:
                return stem
        except Exception:
            continue
    return ""


def _standard_cover_resolve_author(local_vars):
    for key in ("author", "au", "AUTHOR"):
        value = local_vars.get(key)
        if value:
            return value

    metadata = _standard_cover_metadata_from_locals(local_vars)
    value = metadata.get("author")
    if value:
        return value
    return "Barış Kısır"

def _draw_standard_cover_title_panel(image, title: str = "", author: str = "") -> None:
    width = int(globals().get("W", globals().get("WIDTH", 1600)))
    height = int(globals().get("H", globals().get("HEIGHT", 2560)))
    panel_y = 1765
    title = _standard_cover_repair_text(str(title or "")).strip()
    author = _standard_cover_repair_text(str(author or "Barış Kısır")).strip()

    draw = ImageDraw.Draw(image, "RGBA")
    draw.rectangle((0, panel_y, width, height), fill=(3, 5, 8, 255))
    draw.line((180, panel_y + 17, width - 180, panel_y + 17), fill=(160, 225, 209, 105), width=3)

    title_font, title_lines, title_gap = _standard_cover_title_font(draw, title, 1260)
    author_font = _standard_cover_font("arialbd.ttf", 50)
    title_height = sum(draw.textbbox((0, 0), line, font=title_font)[3] - draw.textbbox((0, 0), line, font=title_font)[1] for line in title_lines)
    title_height += max(0, len(title_lines) - 1) * title_gap
    author_bbox = draw.textbbox((0, 0), author, font=author_font)
    author_height = author_bbox[3] - author_bbox[1]
    block_height = title_height + 120 + author_height
    y = panel_y + 120 + max(0, (height - panel_y - 210 - block_height) // 2)
    y = _standard_cover_center(draw, y, title_lines, title_font, (244, 249, 238), title_gap, width)
    y += 120
    _standard_cover_center(draw, y, [author], author_font, (210, 229, 221), 12, width)
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