#!/usr/bin/env python3
"""Create a project-local raster cover for The Bellweather Murders."""

from __future__ import annotations

import argparse
import json
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

    img = Image.new("RGB", (W, H), (18, 22, 24))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / (H - 1)
        r = int(13 + 24 * t)
        g = int(19 + 28 * t)
        b = int(23 + 22 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    mist = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(mist, "RGBA")
    for _ in range(140):
        y = rng.randrange(260, 1680)
        alpha = rng.randrange(10, 30)
        x0 = rng.randrange(-500, 1200)
        x1 = x0 + rng.randrange(700, 1700)
        md.ellipse((x0, y, x1, y + rng.randrange(80, 190)), fill=(190, 204, 194, alpha))
    mist = mist.filter(ImageFilter.GaussianBlur(28))
    img = Image.alpha_composite(img.convert("RGBA"), mist)
    draw = ImageDraw.Draw(img, "RGBA")

    # Lake and town silhouette.
    draw.rectangle((0, 1330, W, 1650), fill=(28, 45, 50, 210))
    for y in range(1380, 1640, 34):
        draw.line((0, y, W, y + rng.randrange(-8, 9)), fill=(128, 154, 145, 34), width=3)
    draw.rectangle((0, 1120, W, 1340), fill=(12, 15, 17, 210))
    for x in range(70, W, 105):
        h = rng.randrange(80, 210)
        draw.rectangle((x, 1120 - h, x + rng.randrange(44, 88), 1340), fill=(15, 17, 18, 235))
        if rng.random() < 0.55:
            draw.rectangle((x + 12, 1160 - h // 2, x + 24, 1174 - h // 2), fill=(231, 196, 117, 105))

    # Church tower and bell glow.
    tx = 1050
    draw.rectangle((tx, 520, tx + 210, 1340), fill=(21, 22, 22, 245))
    draw.polygon([(tx - 25, 520), (tx + 105, 360), (tx + 235, 520)], fill=(14, 15, 16, 250))
    draw.rectangle((tx + 68, 690, tx + 142, 810), fill=(215, 178, 96, 95))
    draw.ellipse((tx + 58, 655, tx + 152, 805), outline=(221, 181, 91, 120), width=5)
    draw.line((tx + 105, 805, tx + 105, 1135), fill=(205, 192, 157, 120), width=5)
    draw.ellipse((tx + 85, 1130, tx + 125, 1170), fill=(205, 192, 157, 120))

    # Foreground road and clue-like blue thread.
    draw.polygon([(0, H), (650, 1620), (930, 1620), (W, H)], fill=(9, 11, 12, 230))
    path = [(260 + i * 18, 1900 + int(55 * rng.random()) + int(80 * (i / 60))) for i in range(61)]
    draw.line(path, fill=(76, 139, 176, 190), width=8)
    draw.line([(x, y + 10) for x, y in path], fill=(236, 238, 220, 120), width=2)

    # Title panel.
    draw.rectangle((0, 1745, W, H), fill=(5, 8, 10, 188))
    draw.line((190, 1768, W - 190, 1768), fill=(181, 196, 173, 130), width=3)
    title_font = font("georgiab.ttf", 126)
    author_font = font("arialbd.ttf", 52)
    subtitle_font = font("arial.ttf", 34)
    y = 1830
    y = centered(draw, y, ["A BELLWEATHER MYSTERY"], subtitle_font, (181, 196, 173), 16)
    y += 65
    y = centered(draw, y, wrap(draw, title.upper(), title_font, 1250), title_font, (242, 244, 229), 22)
    y += 120
    centered(draw, y, [author], author_font, (214, 220, 205), 12)

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