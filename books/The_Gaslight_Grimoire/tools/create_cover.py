#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Gaslight Grimoire."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw) -> list[str]:
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = current + " " + word if current else word
        bbox = draw.textbbox((0, 0), test, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            current = test
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines



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

    with open(args.metadata, encoding="utf-8") as f:
        metadata = json.load(f)

    title = metadata.get("title", "The Gaslight Grimoire")
    author = metadata.get("author", "Barış Kısır")

    W, H = 1600, 2560
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Gradient background: dark to amber-tinged
    for y in range(H):
        ratio = y / H
        r = int(10 + ratio * 55)
        g = int(10 + ratio * 40)
        b = int(15 + ratio * 20)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

    # Fog layer
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fog_draw = ImageDraw.Draw(fog)
    fog_draw.ellipse([-200, 800, 600, 1800], fill=(60, 55, 40, 40))
    fog_draw.ellipse([400, 700, 1100, 1700], fill=(50, 48, 35, 35))
    fog_draw.ellipse([800, 900, 1600, 1900], fill=(65, 60, 45, 30))
    fog_draw.ellipse([300, 1400, 1300, 2400], fill=(45, 42, 30, 50))
    img = Image.alpha_composite(img, fog)

    # Victorian street silhouette (buildings on sides)
    buildings = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    b_draw = ImageDraw.Draw(buildings)
    # Left building cluster
    b_draw.polygon([(0, 600), (0, 1800), (120, 1800), (140, 1400), (160, 1800), (320, 1800), (300, 1200), (260, 900), (240, 700), (180, 600)], fill=(15, 12, 8, 220))
    # Right building cluster
    b_draw.polygon([(1280, 1800), (1500, 1800), (1480, 1300), (1460, 1100), (1400, 800), (1350, 750), (1300, 700), (1260, 650)], fill=(12, 10, 6, 220))
    b_draw.polygon([(1400, 1800), (1600, 1800), (1600, 900), (1550, 850), (1500, 800), (1450, 780)], fill=(18, 14, 8, 220))
    # Roof details
    b_draw.polygon([(180, 600), (240, 700), (200, 650), (150, 580)], fill=(8, 6, 3, 200))
    b_draw.polygon([(1300, 700), (1350, 750), (1320, 710), (1280, 680)], fill=(8, 6, 3, 200))
    # Windows (dim yellow rectangles)
    for wx, wy in [(80, 800), (80, 880), (80, 960), (100, 1050), (100, 1130), (240, 950), (240, 1030)]:
        b_draw.rectangle([wx, wy, wx + 25, wy + 35], fill=(40, 35, 10, 180))
    for wx, wy in [(1350, 900), (1350, 980), (1450, 1000), (1450, 1080), (1520, 950), (1520, 1030)]:
        b_draw.rectangle([wx, wy, wx + 20, wy + 30], fill=(40, 35, 10, 180))
    img = Image.alpha_composite(img, buildings)

    # Gaslamp post on the left
    lamp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    l_draw = ImageDraw.Draw(lamp)
    # Post
    l_draw.rectangle([440, 1100, 455, 1700], fill=(20, 18, 15, 240))
    # Crossbar
    l_draw.rectangle([410, 1100, 485, 1115], fill=(20, 18, 15, 240))
    # Lamp housing
    l_draw.polygon([(415, 1020), (420, 1100), (475, 1100), (480, 1020)], fill=(25, 22, 15, 240))
    # Glass glow
    glow_radius = 180
    for gr in range(glow_radius, 0, -8):
        alpha = max(0, 30 - (glow_radius - gr) // 6)
        l_draw.ellipse([448 - gr, 1000 - gr, 448 + gr, 1000 + gr], fill=(220, 180, 60, alpha))
    # Bright center
    l_draw.ellipse([435, 985, 462, 1015], fill=(255, 230, 150, 255))
    l_draw.ellipse([438, 990, 459, 1010], fill=(255, 255, 220, 200))
    img = Image.alpha_composite(img, lamp)

    # Magic sparkles/particles around the lamp
    particles = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    p_draw = ImageDraw.Draw(particles)
    sparkle_positions = [(420, 960), (470, 930), (490, 1000), (410, 1050), (440, 900), (510, 980), (400, 990)]
    for sx, sy in sparkle_positions:
        p_draw.ellipse([sx - 4, sy - 4, sx + 4, sy + 4], fill=(255, 220, 100, 200))
        p_draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 255, 200, 255))
    img = Image.alpha_composite(img, particles)

    # Cobblestone street at bottom
    street = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(street)
    s_draw.rectangle([0, 1750, W, 1920], fill=(25, 22, 18, 240))
    for cx in range(50, W, 80):
        cy = 1800
        s_draw.ellipse([cx - 20, cy - 10, cx + 20, cy + 10], fill=(35, 30, 25, 150))
        s_draw.ellipse([cx - 40, cy + 30, cx, cy + 50], fill=(30, 26, 22, 130))
        s_draw.ellipse([cx + 20, cy + 40, cx + 60, cy + 60], fill=(32, 28, 24, 130))
    img = Image.alpha_composite(img, street)

    # Title panel - lighter rectangle at bottom
    panel = Image.new("RGBA", (W, 640), (0, 0, 0, 0))
    p_draw = ImageDraw.Draw(panel)
    panel_bg = Image.new("RGBA", (W, 640), (30, 28, 25, 230))
    panel = Image.alpha_composite(panel, panel_bg)
    # Decorative border line
    p_draw.line([(100, 10), (W - 100, 10)], fill=(180, 150, 80, 200), width=3)
    p_draw.line([(100, 629), (W - 100, 629)], fill=(180, 150, 80, 200), width=3)
    img.paste(panel, (0, 1920))

    # Fonts
    try:
        title_font = ImageFont.truetype("C:/Windows/Fonts/georgiab.ttf", 72)
        author_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 42)
    except (IOError, OSError):
        title_font = ImageFont.load_default()
        author_font = ImageFont.load_default()

    # Title text - wrapped if needed
    title_lines = wrap_text(title, title_font, W - 200, draw)
    title_y = 1980
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        tw = bbox[2] - bbox[0]
        tx = (W - tw) // 2
        draw.text((tx, title_y), line, fill=(220, 210, 190, 255), font=title_font)
        title_y += 80

    # Author
    author_y = max(2220, title_y + 20)
    bbox_a = draw.textbbox((0, 0), author, font=author_font)
    aw = bbox_a[2] - bbox_a[0]
    draw.text(((W - aw) // 2, author_y), author, fill=(180, 170, 150, 255), font=author_font)

    # Apply subtle blur to the upper portion for atmosphere
    upper = img.crop((0, 0, W, 1800))
    upper = upper.filter(ImageFilter.GaussianBlur(radius=1))
    img.paste(upper, (0, 0))

    # Save
    args.out.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()))
    img.save(args.out, "PNG")
    print(f"Cover saved to {args.out}")


if __name__ == "__main__":
    main()