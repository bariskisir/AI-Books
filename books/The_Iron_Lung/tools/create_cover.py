#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Iron Lung — a medical drama set in a 1950s polio ward."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
FONTS_DIR = Path("C:/Windows/Fonts")

WIDTH, HEIGHT = 1600, 2560
TITLE_PANEL_TOP = 1920


def rel(path: str | Path) -> Path:
    p = Path(path)
    return ROOT / p if not p.is_absolute() else p


def lerp_color(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def draw_gradient(draw: ImageDraw, width: int, height: int) -> None:
    """Sterile white-to-steel-blue gradient like a hospital ward."""
    for y in range(height):
        if y < height * 0.5:
            t = y / (height * 0.5)
            c = lerp_color((240, 245, 250), (200, 210, 220), t)
        else:
            t = (y - height * 0.5) / (height * 0.5)
            c = lerp_color((200, 210, 220), (60, 70, 85), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_iron_lung(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a large iron lung machine as the central image."""
    cx, cy = width // 2, int(height * 0.45)
    w, h = 400, 250

    # Main cylinder body
    draw.rounded_rectangle(
        [cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2],
        radius=30,
        fill=(180, 190, 200),
    )
    # Darker cylinder band
    draw.rounded_rectangle(
        [cx - w // 2 + 20, cy - h // 2 + 20, cx + w // 2 - 20, cy + h // 2 - 20],
        radius=25,
        fill=(160, 170, 180),
    )
    # Porthole window
    draw.ellipse(
        [cx - 60, cy - 60, cx + 60, cy + 60],
        fill=(200, 220, 240),
        outline=(120, 130, 140),
        width=4,
    )
    # Reflection in porthole
    draw.ellipse(
        [cx - 30, cy - 40, cx + 10, cy - 5],
        fill=(220, 235, 255, 120),
    )
    # Collar ring
    draw.rectangle(
        [cx - w // 2 - 10, cy - 30, cx - w // 2 + 15, cy + 30],
        fill=(140, 150, 160),
    )
    # Bellows housing
    draw.rectangle(
        [cx - w // 2 - 80, cy - 40, cx - w // 2 - 10, cy + 40],
        fill=(120, 130, 140),
    )
    # Pressure gauge
    draw.ellipse(
        [cx + w // 2 - 60, cy - 30, cx + w // 2 - 10, cy + 20],
        fill=(220, 225, 230),
        outline=(100, 110, 120),
        width=2,
    )
    # Gauge needle
    draw.line(
        [(cx + w // 2 - 35, cy - 5), (cx + w // 2 - 25, cy - 15)],
        fill=(60, 60, 70),
        width=3,
    )
    # Base/stand
    draw.rectangle(
        [cx - 30, cy + h // 2, cx + 30, cy + h // 2 + 60],
        fill=(100, 110, 120),
    )
    draw.rectangle(
        [cx - 60, cy + h // 2 + 60, cx + 60, cy + h // 2 + 70],
        fill=(80, 90, 100),
    )
    # Wheels
    for wx in [cx - 40, cx + 40]:
        draw.ellipse(
            [wx - 15, cy + h // 2 + 70, wx + 15, cy + h // 2 + 95],
            fill=(60, 65, 70),
        )


def draw_windows(draw: ImageDraw, width: int, height: int) -> None:
    """Draw tall hospital windows in the background."""
    for wx in [200, 500, 1100, 1400]:
        # Window frame
        draw.rectangle(
            [wx, int(height * 0.15), wx + 120, int(height * 0.55)],
            fill=(200, 215, 230),
            outline=(160, 170, 180),
            width=3,
        )
        # Window cross
        draw.line(
            [(wx + 60, int(height * 0.15)), (wx + 60, int(height * 0.55))],
            fill=(160, 170, 180),
            width=2,
        )
        draw.line(
            [(wx, int(height * 0.35)), (wx + 120, int(height * 0.35))],
            fill=(160, 170, 180),
            width=2,
        )
        # Glass reflection
        draw.rectangle(
            [wx + 5, int(height * 0.15) + 5, wx + 55, int(height * 0.34)],
            fill=(220, 235, 250, 80),
        )


def draw_hospital_lines(draw: ImageDraw, width: int, height: int) -> None:
    """Subtle horizontal lines evoking the sterile hospital environment."""
    # Floor line
    draw.line(
        [(0, int(height * 0.65)), (width, int(height * 0.65))],
        fill=(160, 170, 180),
        width=2,
    )
    # Baseboard
    draw.rectangle(
        [(0, int(height * 0.65)), (width, int(height * 0.67))],
        fill=(140, 150, 160),
    )


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark title panel at the bottom with white text for readability."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    draw.rectangle([(0, panel_top), (width, height)], fill=(25, 30, 40))

    # Subtle top border line
    draw.line([(0, panel_top), (width, panel_top)], fill=(80, 90, 110), width=2)

    # Title text
    title = "The Iron\nLung"
    title_font_size = 80
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    lines = title.split("\n")
    y_offset = panel_top + 80
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 0
        tx = (width - tw) // 2
        draw.text((tx, y_offset), line, fill=(255, 255, 255), font=title_font)
        y_offset += 95

    # Author name
    author = "Barış Kısır"
    author_font_size = 36
    try:
        author_font = ImageFont.truetype(str(font_paths["author"]), author_font_size)
    except Exception:
        author_font = ImageFont.load_default()

    try:
        abbox = draw.textbbox((0, 0), author, font=author_font)
        aw = abbox[2] - abbox[0]
    except Exception:
        aw = 0
    ax = (width - aw) // 2
    ay = y_offset + 50
    draw.text((ax, ay), author, fill=(200, 210, 220), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Iron Lung")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background (sterile hospital feel)
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Hospital windows
    draw_windows(draw, WIDTH, HEIGHT)

    # Step 3: Hospital floor lines
    draw_hospital_lines(draw, WIDTH, HEIGHT)

    # Step 4: Central iron lung machine
    draw_iron_lung(draw, WIDTH, HEIGHT)

    # Step 5: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
        "small": str(FONTS_DIR / "arial.ttf"),
    }
    draw_title_panel(draw, width=WIDTH, height=HEIGHT, font_paths=font_paths)

    # Soften
    img = img.filter(ImageFilter.SMOOTH)

    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()))
    img.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")



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

    metadata_path = rel(args.metadata)
    output_path = rel(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    create_cover(metadata_path, output_path)


if __name__ == "__main__":
    main()