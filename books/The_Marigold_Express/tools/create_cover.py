#!/usr/bin/env python3
"""Create a project-local raster cover for The Marigold Express — an Art Deco luxury train."""

from __future__ import annotations

import argparse
import json
import math
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


def centered(draw: ImageDraw.ImageDraw, y: int, lines: list[str], selected_font: ImageFont.FreeTypeFont, fill, gap: int) -> int:
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

    # Deep teal-to-plum night, an Art Deco evening palette.
    img = Image.new("RGBA", (W, H), (24, 28, 40, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(H):
        t = y / (H - 1)
        r = int(28 + 36 * t)
        g = int(30 + 18 * t)
        b = int(48 + 22 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    gold = (212, 168, 78)
    pale_gold = (236, 206, 130)
    deep_gold = (170, 128, 52)

    # Deco sunburst rays radiating from behind the title block.
    cx, cy = W // 2, 1180
    rays = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rays)
    for k in range(36):
        a = (math.tau / 36) * k
        x2 = cx + 2400 * math.cos(a)
        y2 = cy + 2400 * math.sin(a)
        if k % 2 == 0:
            rd.line((cx, cy, x2, y2), fill=(*deep_gold, 28), width=10)
    rays = rays.filter(ImageFilter.GaussianBlur(2))
    img = Image.alpha_composite(img, rays)
    draw = ImageDraw.Draw(img, "RGBA")

    # Concentric Deco arcs (a stylized sunrise the train runs toward).
    for i, rad in enumerate(range(220, 520, 60)):
        draw.arc((cx - rad, cy - rad, cx + rad, cy + rad), 200, 340,
                 fill=(*gold, 120 - i * 12), width=6)

    # --- The train, in three-quarter Deco silhouette along the lower third. ---
    base = 1560
    # Rails converging to a vanishing point.
    vp = (W // 2 + 120, base - 40)
    for off in (-1, 1):
        draw.line((cx + off * 700, H, vp[0] + off * 8, vp[1]), fill=(70, 64, 80, 200), width=6)
    for ty in range(base + 40, H, 70):
        f = (ty - vp[1]) / (H - vp[1])
        half = int(60 + 520 * f)
        draw.line((cx - half, ty, cx + half, ty), fill=(60, 54, 70, 120), width=4)

    # Locomotive body: a streamlined Deco engine, marigold and brass.
    loco_x = 360
    loco_y = base
    # Long body.
    draw.rounded_rectangle((loco_x, loco_y - 150, loco_x + 760, loco_y + 30), radius=40,
                           fill=(176, 132, 56, 255))
    # Streamlined nose.
    draw.pieslice((loco_x - 120, loco_y - 150, loco_x + 120, loco_y + 70), 90, 270,
                  fill=(176, 132, 56, 255))
    # Brass speed-stripes.
    for sy in (loco_y - 110, loco_y - 80, loco_y - 50):
        draw.line((loco_x - 40, sy, loco_x + 740, sy), fill=(*pale_gold, 230), width=6)
    # Cab roof.
    draw.rounded_rectangle((loco_x + 470, loco_y - 200, loco_x + 740, loco_y - 150), radius=20,
                           fill=(150, 110, 44, 255))
    # Cab window, warmly lit.
    draw.rounded_rectangle((loco_x + 560, loco_y - 192, loco_x + 690, loco_y - 152), radius=8,
                           fill=(250, 224, 150, 255))
    # Headlamp beam.
    beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam)
    bd.polygon([(loco_x - 110, loco_y - 70), (loco_x - 540, loco_y - 200),
                (loco_x - 540, loco_y + 120)], fill=(250, 230, 150, 40))
    beam = beam.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(img, beam)
    draw = ImageDraw.Draw(img, "RGBA")
    draw.ellipse((loco_x - 116, loco_y - 86, loco_x - 86, loco_y - 56), fill=(255, 244, 200, 255))
    # Driving wheels.
    for wx in (loco_x + 120, loco_x + 320, loco_x + 520):
        draw.ellipse((wx - 48, loco_y - 18, wx + 48, loco_y + 78), outline=(*pale_gold, 220), width=7)
        draw.ellipse((wx - 12, loco_y + 18, wx + 12, loco_y + 42), fill=(*pale_gold, 220))

    # One trailing carriage with a row of lit windows.
    car_x = loco_x + 770
    draw.rounded_rectangle((car_x, loco_y - 140, car_x + 520, loco_y + 30), radius=24,
                           fill=(150, 112, 46, 255))
    for i in range(6):
        wx = car_x + 36 + i * 80
        draw.rounded_rectangle((wx, loco_y - 110, wx + 50, loco_y - 50), radius=6,
                               fill=(250, 224, 150, 255))
    for wx in (car_x + 130, car_x + 390):
        draw.ellipse((wx - 40, loco_y - 18, wx + 40, loco_y + 70), outline=(*pale_gold, 200), width=6)

    # --- The Saffron Star: a faceted yellow diamond, glinting above the train. ---
    gx, gy = 1180, 760
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((gx - 120, gy - 120, gx + 120, gy + 120), fill=(255, 214, 90, 70))
    glow = glow.filter(ImageFilter.GaussianBlur(34))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")
    # Brilliant-cut gem: crown facets over a pointed pavilion.
    r = 70
    top = [(gx - r, gy - 20), (gx - r + 26, gy - 48), (gx + r - 26, gy - 48), (gx + r, gy - 20)]
    draw.polygon(top, fill=(255, 226, 120, 255))
    draw.polygon([(gx - r, gy - 20), (gx + r, gy - 20), (gx, gy + 90)], fill=(232, 188, 70, 255))
    draw.line((gx - r, gy - 20, gx + r, gy - 20), fill=(255, 244, 190, 255), width=3)
    draw.line((gx, gy - 48, gx, gy + 90), fill=(255, 244, 190, 220), width=2)
    draw.polygon([(gx - r, gy - 20), (gx - r + 26, gy - 48), (gx, gy - 20)], fill=(255, 240, 165, 255))
    # Sparkle flares.
    for (dx, dy, ln) in [(-1, 0, 150), (1, 0, 150), (0, -1, 120), (0, 1, 90)]:
        draw.line((gx, gy - 4, gx + dx * ln, gy - 4 + dy * ln), fill=(255, 240, 180, 130), width=2)

    # Deco corner ornaments (chevrons).
    for (ox, oy, d) in [(120, 150, 1), (W - 120, 150, -1)]:
        for j in range(3):
            draw.line((ox, oy + j * 26, ox + d * 60, oy + 40 + j * 26), fill=(*gold, 200), width=5)
            draw.line((ox + d * 60, oy + 40 + j * 26, ox + d * 120, oy + j * 26), fill=(*gold, 200), width=5)

    # --- Title plate. ---
    panel_top = 1980
    draw.rectangle((0, panel_top, W, H), fill=(18, 20, 30, 235))
    draw.line((220, panel_top + 36, W - 220, panel_top + 36), fill=(*gold, 200), width=3)
    draw.line((220, H - 150, W - 220, H - 150), fill=(*gold, 120), width=2)

    title_font = font("georgiab.ttf", 122)
    author_font = font("arialbd.ttf", 44)
    subtitle_font = font("arial.ttf", 32)

    y = panel_top + 70
    y = centered(draw, y, ["A CAPER ABOARD THE GRANDEST TRAIN ON THE CONTINENT"],
                 subtitle_font, (190, 168, 120), 8)
    y += 46
    y = centered(draw, y, wrap(draw, title.upper(), title_font, 1240), title_font, pale_gold, 14)
    y += 70
    centered(draw, y, [author], author_font, (208, 200, 180), 8)

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