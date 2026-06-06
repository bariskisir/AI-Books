#!/usr/bin/env python3
"""Create a project-local raster cover for The Lantern Index."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560


def rel(path: Path) -> Path:
    return ROOT / path if not path.is_absolute() else path


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


def centered(
    draw: ImageDraw.ImageDraw,
    y: int,
    lines: list[str],
    selected_font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
    gap: int,
) -> int:
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=selected_font)
        x = (W - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), line, font=selected_font, fill=fill)
        y += bbox[3] - bbox[1] + gap
    return y


def draw_gradient(draw: ImageDraw.ImageDraw) -> None:
    top = (12, 23, 34)
    middle = (24, 59, 78)
    horizon = (48, 84, 92)
    lower = (6, 12, 20)
    for y in range(H):
        if y < 900:
            t = y / 900
            c = tuple(int(a + (b - a) * t) for a, b in zip(top, middle))
        elif y < 1650:
            t = (y - 900) / 750
            c = tuple(int(a + (b - a) * t) for a, b in zip(middle, horizon))
        else:
            t = (y - 1650) / (H - 1650)
            c = tuple(int(a + (b - a) * t) for a, b in zip(horizon, lower))
        draw.line((0, y, W, y), fill=c + (255,))


def draw_rain(draw: ImageDraw.ImageDraw) -> None:
    for x in range(0, W, 32):
        for y in range(0, 1700, 70):
            draw.line((x, y, x + 10, y + 38), fill=(220, 240, 255, 18), width=2)


def draw_harbor(draw: ImageDraw.ImageDraw) -> Image.Image:
    draw.rectangle((0, 1180, W, 1540), fill=(12, 19, 28, 220))
    draw.polygon([(0, 1440), (180, 1360), (360, 1390), (520, 1320), (760, 1360), (980, 1290), (1210, 1340), (1450, 1305), (W, 1360), (W, 1540), (0, 1540)], fill=(7, 12, 18, 240))
    for x in range(30, W, 120):
        deck = 40 + (x // 120) % 3 * 12
        draw.rectangle((x, 1260 - deck, x + 54, 1360 - deck), fill=(16, 23, 31, 255))
        if x % 240 == 0:
            draw.rectangle((x + 14, 1280 - deck, x + 38, 1308 - deck), fill=(210, 180, 112, 120))

    water = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(water, "RGBA")
    for y in range(1180, 1580, 26):
        wobble = int(10 * math.sin(y / 42))
        wd.line((0, y, W, y + wobble), fill=(120, 185, 205, 32), width=3)
        wd.line((0, y + 6, W, y + 6 + wobble), fill=(40, 90, 110, 28), width=2)
    water = water.filter(ImageFilter.GaussianBlur(0.6))
    return water


def draw_lights(draw: ImageDraw.ImageDraw) -> None:
    lantern_positions = [(210, 1040), (360, 980), (520, 1015), (690, 940), (860, 980), (1020, 920), (1210, 960), (1370, 905)]
    for x, y in lantern_positions:
        draw.ellipse((x - 20, y - 20, x + 20, y + 20), fill=(255, 224, 140, 140))
        draw.ellipse((x - 46, y - 46, x + 46, y + 46), fill=(255, 224, 140, 30))
        draw.line((x, y + 20, x, y + 120), fill=(250, 225, 150, 50), width=2)


def draw_lighthouse(img: Image.Image, draw: ImageDraw.ImageDraw) -> None:
    base_x = 1250
    base_y = 1380
    tower = [(base_x - 65, base_y), (base_x + 65, base_y), (base_x + 48, 980), (base_x - 48, 980)]
    draw.polygon(tower, fill=(28, 35, 42, 255))
    draw.rectangle((base_x - 78, 950, base_x + 78, 988), fill=(46, 54, 61, 255))
    draw.rectangle((base_x - 52, 910, base_x + 52, 950), fill=(64, 74, 82, 255))
    draw.ellipse((base_x - 32, 886, base_x + 32, 932), fill=(196, 204, 210, 255))
    beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam, "RGBA")
    bd.polygon([(base_x, 909), (base_x + 420, 770), (W, 820), (W, 1110), (base_x + 350, 1110)], fill=(255, 240, 180, 30))
    bd.polygon([(base_x, 909), (base_x - 440, 790), (0, 840), (0, 1090), (base_x - 360, 1100)], fill=(255, 240, 180, 18))
    beam = beam.filter(ImageFilter.GaussianBlur(18))
    img.alpha_composite(beam)


def draw_index_cards(img: Image.Image, draw: ImageDraw.ImageDraw) -> None:
    cards = [
        (190, 1640, -18),
        (360, 1550, 11),
        (530, 1685, -9),
        (720, 1600, 15),
        (890, 1710, -7),
        (1080, 1560, 9),
        (1270, 1675, -12),
    ]
    for x, y, tilt in cards:
        rect = Image.new("RGBA", (220, 120), (0, 0, 0, 0))
        rd = ImageDraw.Draw(rect, "RGBA")
        rd.rounded_rectangle((0, 0, 220, 120), radius=8, fill=(238, 232, 220, 230))
        rd.line((14, 22, 205, 22), fill=(140, 135, 128, 90), width=2)
        rd.line((14, 46, 178, 46), fill=(140, 135, 128, 70), width=2)
        rd.line((14, 70, 196, 70), fill=(140, 135, 128, 70), width=2)
        rd.line((14, 94, 160, 94), fill=(140, 135, 128, 70), width=2)
        rect = rect.rotate(tilt, expand=1, resample=Image.Resampling.BICUBIC)
        glow = rect.filter(ImageFilter.GaussianBlur(8))
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        layer.alpha_composite(glow, (x - rect.size[0] // 2, y - rect.size[1] // 2))
        layer.alpha_composite(rect, (x - rect.size[0] // 2, y - rect.size[1] // 2))
        img.alpha_composite(layer)


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Lantern Index")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    draw_gradient(draw)
    water = draw_harbor(draw)
    img = Image.alpha_composite(img, water)
    draw = ImageDraw.Draw(img, "RGBA")
    draw_rain(draw)
    draw_lanterns = draw_lights
    draw_lanterns(draw)
    draw_lighthouse(img, draw)
    draw_index_cards(img, draw)

    for x in range(80, W, 240):
        draw.line((x, 1510, x + 60, 1590), fill=(25, 45, 56, 60), width=3)

    title_plate = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(title_plate, "RGBA")
    pd.rounded_rectangle((70, 2050, W - 70, 2375), radius=14, fill=(8, 13, 18, 150), outline=(180, 200, 198, 90), width=2)
    title_plate = title_plate.filter(ImageFilter.GaussianBlur(0.5))
    img = Image.alpha_composite(img, title_plate)
    draw = ImageDraw.Draw(img, "RGBA")

    title_font = font("georgiab.ttf", 112)
    author_font = font("arialbd.ttf", 50)
    subtitle_font = font("arial.ttf", 32)
    y = 190
    y = centered(draw, y, ["A HARBOR OF"], subtitle_font, (175, 208, 214), 10)
    y = centered(draw, y, ["ERASED RECORDS"], subtitle_font, (175, 208, 214), 18)
    y += 12
    y = centered(draw, y, wrap(draw, title.upper(), title_font, 1210), title_font, (245, 243, 235), 18)
    y += 22
    centered(draw, y, [author], author_font, (210, 220, 219), 10)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
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


def _standard_cover_resolve_model(local_vars):
    for key in ("model", "mo", "MODEL"):
        value = local_vars.get(key)
        if value:
            return value
    metadata = _standard_cover_metadata_from_locals(local_vars)
    value = metadata.get("model")
    if value:
        return value
    return ""


def _draw_standard_cover_title_panel(image, title: str = "", author: str = "", model: str = "") -> None:
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
    if not model:
        model = _standard_cover_resolve_model(locals())
    if model:
        mf = _standard_cover_font("arial.ttf", 36)
        _standard_cover_center(draw, height - 110, [model], mf, (140, 140, 160), 12, width)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    metadata_path = rel(args.metadata)
    output_path = rel(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    make_cover(metadata_path, output_path)


if __name__ == "__main__":
    main()
