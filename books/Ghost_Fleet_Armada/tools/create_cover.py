#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for Ghost Fleet Armada."""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


FONT_DIR = Path("C:/Windows/Fonts")
WIDTH, HEIGHT = 1600, 2560
PANEL_Y = 1920

COLORS = {
    "bg_top": (10, 5, 30),
    "bg_mid": (15, 10, 50),
    "bg_bot": (5, 0, 20),
    "nebula_core": (80, 50, 180),
    "nebula_edge": (40, 20, 100),
    "nebula_glow": (30, 10, 60),
    "star_bright": (220, 220, 255),
    "star_dim": (150, 150, 200),
    "ship_hull": (20, 25, 40),
    "ship_glow": (60, 100, 200),
    "panel_bg": (240, 240, 248),
    "title_text": (10, 5, 30),
    "author_text": (60, 60, 80),
}


def make_gradient(draw: ImageDraw.ImageDraw) -> None:
    for y in range(HEIGHT):
        if y < HEIGHT // 2:
            t = y / (HEIGHT // 2)
            r = int(COLORS["bg_top"][0] + (COLORS["bg_mid"][0] - COLORS["bg_top"][0]) * t)
            g = int(COLORS["bg_top"][1] + (COLORS["bg_mid"][1] - COLORS["bg_top"][1]) * t)
            b = int(COLORS["bg_top"][2] + (COLORS["bg_mid"][2] - COLORS["bg_top"][2]) * t)
        else:
            t = (y - HEIGHT // 2) / (HEIGHT // 2)
            r = int(COLORS["bg_mid"][0] + (COLORS["bg_bot"][0] - COLORS["bg_mid"][0]) * t)
            g = int(COLORS["bg_mid"][1] + (COLORS["bg_bot"][1] - COLORS["bg_mid"][1]) * t)
            b = int(COLORS["bg_mid"][2] + (COLORS["bg_bot"][2] - COLORS["bg_mid"][2]) * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def draw_nebula(draw: ImageDraw.ImageDraw, img: Image.Image) -> None:
    nebula_img = Image.new("RGBA", (WIDTH, PANEL_Y), (0, 0, 0, 0))
    ndraw = ImageDraw.Draw(nebula_img)

    for _ in range(12):
        cx = random.randint(200, WIDTH - 200)
        cy = random.randint(100, PANEL_Y - 200)
        rx = random.randint(150, 400)
        ry = random.randint(100, 250)
        alpha = random.randint(15, 40)
        color = random.choice([
            COLORS["nebula_core"],
            COLORS["nebula_edge"],
            COLORS["nebula_glow"],
        ])
        ndraw.ellipse(
            [cx - rx, cy - ry, cx + rx, cy + ry],
            fill=(color[0], color[1], color[2], alpha),
        )

    nebula_img = nebula_img.filter(ImageFilter.GaussianBlur(radius=60))
    img.paste(nebula_img, (0, 0), nebula_img)


def draw_stars(draw: ImageDraw.ImageDraw) -> None:
    for _ in range(800):
        x = random.randint(0, WIDTH - 1)
        y = random.randint(0, PANEL_Y - 1)
        r = random.choice([1, 1, 1, 2, 2, 3])
        brightness = random.randint(100, 255)
        color = (brightness, brightness, min(255, brightness + 20))
        draw.ellipse([x - r, y - r, x + r, y + r], fill=color)

    for _ in range(8):
        x = random.randint(0, WIDTH - 1)
        y = random.randint(0, PANEL_Y - 1)
        r = random.randint(3, 6)
        for ring in range(r, 0, -1):
            alpha = max(0, 100 - ring * 15)
            draw.ellipse(
                [x - ring * 4, y - ring * 4, x + ring * 4, y + ring * 4],
                outline=(COLORS["star_bright"][0], COLORS["star_bright"][1], COLORS["star_bright"][2], alpha),
            )


def draw_ship(draw: ImageDraw.ImageDraw, x: int, y: int, scale: float, angle: float = 0) -> None:
    length = int(200 * scale)
    width = int(60 * scale)
    half_w = width // 2

    cos_a = math.cos(angle)
    sin_a = math.sin(angle)

    cx, cy = x, y
    nose = (cx + int(length * 0.4 * cos_a), cy + int(length * 0.4 * sin_a))
    tail = (cx - int(length * 0.4 * cos_a), cy - int(length * 0.4 * sin_a))
    wing_l = (cx - int(20 * scale * cos_a) - int(half_w * sin_a), cy - int(20 * scale * sin_a) + int(half_w * cos_a))
    wing_r = (cx - int(20 * scale * cos_a) + int(half_w * sin_a), cy - int(20 * scale * sin_a) - int(half_w * cos_a))
    tail_l = (cx - int(40 * scale * cos_a) - int(half_w * 0.6 * sin_a), cy - int(40 * scale * sin_a) + int(half_w * 0.6 * cos_a))
    tail_r = (cx - int(40 * scale * cos_a) + int(half_w * 0.6 * sin_a), cy - int(40 * scale * sin_a) - int(half_w * 0.6 * cos_a))

    hull_color = COLORS["ship_hull"]
    draw.polygon([nose, wing_l, tail_l, tail, tail_r, wing_r], fill=hull_color, outline=(40, 50, 80))

    glow_color = COLORS["ship_glow"]
    engine_l = (tail_l[0] - int(10 * scale * cos_a), tail_l[1] - int(10 * scale * sin_a))
    engine_r = (tail_r[0] - int(10 * scale * cos_a), tail_r[1] - int(10 * scale * sin_a))
    draw.ellipse(
        [engine_l[0] - 4, engine_l[1] - 4, engine_l[0] + 4, engine_l[1] + 4],
        fill=glow_color,
    )
    draw.ellipse(
        [engine_r[0] - 4, engine_r[1] - 4, engine_r[0] + 4, engine_r[1] + 4],
        fill=glow_color,
    )


def draw_ships(draw: ImageDraw.ImageDraw) -> None:
    # Main large derelict ship - center-left
    draw_ship(draw, 500, 600, 3.5, angle=-0.15)

    # Second large ship - right side, angled away
    draw_ship(draw, 1100, 450, 2.8, angle=0.25)

    # Smaller ships in background
    draw_ship(draw, 300, 300, 1.2, angle=0.5)
    draw_ship(draw, 750, 250, 0.8, angle=-0.3)
    draw_ship(draw, 1300, 700, 1.5, angle=-0.4)
    draw_ship(draw, 200, 850, 1.0, angle=0.6)
    draw_ship(draw, 1400, 300, 0.6, angle=0.1)
    draw_ship(draw, 850, 900, 1.8, angle=0.35)


def draw_title_panel(draw: ImageDraw.ImageDraw, title: str, author: str) -> None:
    draw.rectangle([0, PANEL_Y, WIDTH, HEIGHT], fill=COLORS["panel_bg"])

    separator_y = PANEL_Y + 10
    draw.rectangle([100, separator_y, WIDTH - 100, separator_y + 2], fill=(180, 180, 200))

    georgia_bold_path = FONT_DIR / "georgiab.ttf"
    arial_bold_path = FONT_DIR / "arialbd.ttf"
    arial_path = FONT_DIR / "arial.ttf"

    try:
        title_font_size = 80
        title_font = ImageFont.truetype(str(georgia_bold_path), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    try:
        author_font = ImageFont.truetype(str(arial_bold_path), 36)
    except Exception:
        author_font = ImageFont.load_default()

    words = title.split()
    line1_words = []
    line2_words = []
    mid = len(words) // 2
    if len(words) <= 3:
        line1_words = words
    else:
        line1_words = words[:mid]
        line2_words = words[mid:]

    line1 = " ".join(line1_words)
    line2 = " ".join(line2_words)

    center_x = WIDTH // 2

    try:
        bbox1 = draw.textbbox((0, 0), line1, font=title_font)
        w1 = bbox1[2] - bbox1[0]
        h1 = bbox1[3] - bbox1[1]
    except Exception:
        w1, h1 = title_font.getsize(line1)

    line1_y = PANEL_Y + 60

    if line2:
        try:
            bbox2 = draw.textbbox((0, 0), line2, font=title_font)
            w2 = bbox2[2] - bbox2[0]
            h2 = bbox2[3] - bbox2[1]
        except Exception:
            w2, h2 = title_font.getsize(line2)

        total_h = h1 + 10 + h2
        start_y = PANEL_Y + (HEIGHT - PANEL_Y - total_h) // 2 - 30
        line1_y = start_y
        line2_y = start_y + h1 + 10

        draw.text((center_x - w2 // 2, line2_y), line2, fill=COLORS["title_text"], font=title_font)

    draw.text((center_x - w1 // 2, line1_y), line1, fill=COLORS["title_text"], font=title_font)

    author_y = HEIGHT - 80
    try:
        abbox = draw.textbbox((0, 0), author, font=author_font)
        aw = abbox[2] - abbox[0]
    except Exception:
        aw, _ = author_font.getsize(author)
    draw.text((center_x - aw // 2, author_y), author, fill=COLORS["author_text"], font=author_font)

    tagline = "A Space Opera"
    try:
        small_font = ImageFont.truetype(str(arial_path), 18)
        sbbox = draw.textbbox((0, 0), tagline, font=small_font)
        sw = sbbox[2] - sbbox[0]
    except Exception:
        small_font = ImageFont.load_default()
        sw, _ = small_font.getsize(tagline)
    draw.text((center_x - sw // 2, HEIGHT - 120), tagline, fill=(140, 140, 160), font=small_font)



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

    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    title = metadata["title"]
    author = metadata["author"]

    img = Image.new("RGB", (WIDTH, HEIGHT), COLORS["bg_top"])
    draw = ImageDraw.Draw(img, "RGBA")

    make_gradient(draw)
    draw_nebula(draw, img)
    draw_stars(draw)
    draw_ships(draw)

    draw_rgb = ImageDraw.Draw(img)
    draw_title_panel(draw_rgb, title, author)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()))
    img.save(args.out, "PNG")
    print(f"Cover saved to {args.out}")


if __name__ == "__main__":
    main()