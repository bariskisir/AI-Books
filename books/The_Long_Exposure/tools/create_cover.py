#!/usr/bin/env python3
"""Create a project-local raster cover for The Long Exposure — a night dome under star trails."""

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

    img = Image.new("RGBA", (W, H), (8, 10, 22, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Night-sky gradient — deep indigo at the zenith warming toward the horizon.
    for y in range(H):
        t = y / (H - 1)
        r = int(8 + 30 * t)
        g = int(10 + 26 * t)
        b = int(22 + 40 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # Faint scattered field stars.
    for _ in range(420):
        sx = rng.randrange(0, W)
        sy = rng.randrange(0, 1700)
        s = rng.choice([1, 1, 1, 2])
        b = rng.randrange(70, 150)
        draw.ellipse((sx, sy, sx + s, sy + s), fill=(b, b, min(255, b + 25), 200))

    # Star trails — concentric arcs about a celestial pole, the long-exposure motif.
    pole = (1180, 560)
    trails = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(trails)
    for _ in range(140):
        radius = rng.randrange(60, 1500)
        a0 = rng.uniform(0, math.tau)
        sweep = rng.uniform(0.18, 0.55)
        steps = max(8, int(radius * sweep / 6))
        bright = rng.randrange(40, 130)
        prev = None
        for i in range(steps + 1):
            a = a0 + sweep * (i / steps)
            px = pole[0] + radius * math.cos(a)
            py = pole[1] + radius * math.sin(a)
            if prev and 0 <= py < 1750:
                td.line((prev[0], prev[1], px, py), fill=(bright, bright, min(255, bright + 30), 90), width=1)
            prev = (px, py)
    trails = trails.filter(ImageFilter.GaussianBlur(0.6))
    img = Image.alpha_composite(img, trails)
    draw = ImageDraw.Draw(img, "RGBA")

    # The anomalous star — one bright point with a soft cross-flare, the heart of the book.
    gx, gy = 470, 430
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((gx - 70, gy - 70, gx + 70, gy + 70), fill=(180, 200, 255, 70))
    glow = glow.filter(ImageFilter.GaussianBlur(28))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")
    draw.line((gx - 90, gy, gx + 90, gy), fill=(220, 230, 255, 160), width=2)
    draw.line((gx, gy - 90, gx, gy + 90), fill=(220, 230, 255, 160), width=2)
    draw.ellipse((gx - 7, gy - 7, gx + 7, gy + 7), fill=(245, 248, 255, 255))

    # Mountain ridge in silhouette.
    ridge_y = 1640
    ridge = [(0, H)]
    x = 0
    y = ridge_y
    while x <= W:
        y += rng.randrange(-70, 70)
        y = max(1500, min(1760, y))
        ridge.append((x, y))
        x += rng.randrange(40, 120)
    ridge.append((W, H))
    draw.polygon(ridge, fill=(4, 5, 12, 255))

    # The dome — the observatory, hemispheric with its shutter slit open to the sky.
    dome_cx = 560
    dome_base = 1600
    dome_r = 150
    draw.rectangle((dome_cx - dome_r + 20, dome_base - 30, dome_cx + dome_r - 20, dome_base + 60),
                   fill=(14, 16, 26, 255))
    draw.pieslice((dome_cx - dome_r, dome_base - dome_r, dome_cx + dome_r, dome_base + dome_r),
                  180, 360, fill=(20, 22, 34, 255))
    draw.pieslice((dome_cx - dome_r, dome_base - dome_r, dome_cx + dome_r, dome_base + dome_r),
                  180, 360, outline=(60, 66, 86, 255), width=3)
    # Open shutter slit aimed at the guest star.
    draw.polygon([(dome_cx - 14, dome_base), (dome_cx + 14, dome_base),
                  (dome_cx + 26, dome_base - dome_r - 6), (dome_cx - 26, dome_base - dome_r - 6)],
                 fill=(6, 8, 16, 255))
    draw.line((dome_cx, dome_base - dome_r - 6, gx, gy), fill=(120, 140, 200, 40), width=2)

    # A lit window at the base — someone is still working.
    draw.rectangle((dome_cx + 60, dome_base + 18, dome_cx + 78, dome_base + 40),
                   fill=(230, 196, 120, 230))

    # Lower panel for type.
    draw.rectangle((0, 2010, W, H), fill=(6, 7, 14, 235))
    draw.line((250, 2046, W - 250, 2046), fill=(120, 130, 160, 70), width=1)

    title_font = font("georgiab.ttf", 110)
    author_font = font("arialbd.ttf", 42)
    subtitle_font = font("arial.ttf", 30)

    y = 2096
    y = centered(draw, y, ["VELA RIDGE OBSERVATORY"], subtitle_font, (150, 160, 190), 8)
    y += 54
    y = centered(draw, y, wrap(draw, title.upper(), title_font, 1200), title_font, (224, 228, 240), 18)
    y += 96
    centered(draw, y, [author], author_font, (170, 178, 200), 8)

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