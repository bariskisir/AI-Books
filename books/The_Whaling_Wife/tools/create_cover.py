#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Whaling Wife."""

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
    """Nantucket gray sky to dark navy sea gradient."""
    for y in range(height):
        if y < height * 0.45:
            t = y / (height * 0.45)
            c = lerp_color((140, 145, 150), (80, 85, 95), t)
        elif y < height * 0.55:
            c = (60, 65, 75)
        else:
            t = (y - height * 0.55) / (height * 0.45)
            c = lerp_color((60, 65, 75), (10, 15, 40), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_waves(draw: ImageDraw, width: int, height: int) -> None:
    """Draw stylized ocean waves in the lower portion."""
    wave_color = (200, 210, 220, 40)
    for row in range(12):
        y_base = int(height * 0.52) + row * 20
        for x in range(0, width, 8):
            offset = int(6 * (x / 80 + row * 1.5))
            y = y_base + offset
            if y < height:
                draw.point((x, y), fill=wave_color)


def draw_ship(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a whaling ship silhouette on the horizon."""
    cx = width // 2
    ship_y = int(height * 0.48)

    # Hull
    hull_points = [
        (cx - 160, ship_y),
        (cx - 140, ship_y + 50),
        (cx + 100, ship_y + 50),
        (cx + 120, ship_y),
    ]
    draw.polygon(hull_points, fill=(25, 28, 35))

    # Hull line detail
    draw.line(
        [(cx - 150, ship_y + 10), (cx + 110, ship_y + 10)],
        fill=(50, 55, 65),
        width=2,
    )

    # Masts
    masts = [cx - 70, cx, cx + 60]
    for mx in masts:
        draw.line(
            [(mx, ship_y - 180), (mx, ship_y - 10)],
            fill=(30, 33, 40),
            width=4,
        )

    # Cross spars
    spars = [
        (cx - 70, ship_y - 160, cx - 60, ship_y - 50),
        (cx, ship_y - 170, cx, ship_y - 50),
        (cx + 60, ship_y - 150, cx + 60, ship_y - 50),
    ]
    for mx, top, bot, _ in zip(
        [cx - 70, cx, cx + 60],
        [ship_y - 160, ship_y - 170, ship_y - 150],
        [ship_y - 50, ship_y - 50, ship_y - 50],
        spars,
    ):
        for y_level in range(top, bot, 30):
            spar_w = 60 + (y_level - top) * 2
            draw.line(
                [(mx - spar_w, y_level), (mx + spar_w, y_level)],
                fill=(35, 38, 45),
                width=2,
            )

    # Foreshortened sails (squares)
    draw.polygon(
        [(cx - 70 - 50, ship_y - 130), (cx - 70 + 50, ship_y - 130), (cx - 70 + 50, ship_y - 60), (cx - 70 - 50, ship_y - 60)],
        fill=(80, 85, 95, 180),
    )
    draw.polygon(
        [(cx - 50, ship_y - 140), (cx + 50, ship_y - 140), (cx + 50, ship_y - 60), (cx - 50, ship_y - 60)],
        fill=(90, 95, 105, 180),
    )
    draw.polygon(
        [(cx + 60 - 40, ship_y - 120), (cx + 60 + 40, ship_y - 120), (cx + 60 + 40, ship_y - 60), (cx + 60 - 40, ship_y - 60)],
        fill=(75, 80, 90, 180),
    )

    # Bowsprit
    draw.line(
        [(cx + 120, ship_y - 5), (cx + 190, ship_y - 40)],
        fill=(30, 33, 40),
        width=3,
    )

    # Flag
    draw.polygon(
        [(cx + 190, ship_y - 40), (cx + 190, ship_y - 25), (cx + 160, ship_y - 32)],
        fill=(60, 70, 90),
    )


def draw_harpoon(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a large harpoon diagonally crossing the composition."""
    start_x = int(width * 0.72)
    start_y = int(height * 0.18)
    end_x = int(width * 0.55)
    end_y = int(height * 0.38)

    # Shaft
    draw.line(
        [(start_x, start_y), (end_x, end_y)],
        fill=(160, 150, 130),
        width=5,
    )

    # Harpoon head (toggle iron)
    head_x = end_x
    head_y = end_y
    head_len = 18

    # Point
    draw.polygon(
        [(head_x, head_y), (head_x - head_len, head_y - head_len // 2), (head_x - head_len, head_y + head_len // 2)],
        fill=(180, 170, 150),
    )

    # Toggle barbs
    draw.line(
        [(head_x - 10, head_y - 10), (head_x - 18, head_y - 6)],
        fill=(180, 170, 150),
        width=3,
    )
    draw.line(
        [(head_x - 10, head_y + 10), (head_x - 18, head_y + 6)],
        fill=(180, 170, 150),
        width=3,
    )

    # Rope wrapped at base
    for i in range(3):
        rx = head_x - 20 - i * 4
        draw.ellipse(
            [rx - 4, head_y - 5, rx + 4, head_y + 5],
            fill=(140, 120, 90),
        )


def draw_moon(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a pale moon behind the ship."""
    mx = int(width * 0.35)
    my = int(height * 0.22)
    r = 50

    # Outer glow
    for i in range(6):
        glow_r = r + i * 12
        alpha = 15 - i * 2
        draw.ellipse(
            [mx - glow_r, my - glow_r, mx + glow_r, my + glow_r],
            fill=(200, 210, 230, alpha),
        )

    # Moon body
    draw.ellipse(
        [mx - r, my - r, mx + r, my + r],
        fill=(220, 225, 235, 180),
    )

    # Moon highlight
    draw.ellipse(
        [mx - r + 10, my - r + 10, mx + r - 15, my + r - 15],
        fill=(240, 242, 248, 100),
    )

    # Moon shadow (crescent effect)
    draw.ellipse(
        [mx - r + 20, my - r - 5, mx + r + 10, my + r + 5],
        fill=(140, 145, 150, 60),
    )


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom with white text."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    draw.rectangle([(0, panel_top), (width, height)], fill=(15, 18, 30))

    # Subtle top border line
    draw.line([(0, panel_top), (width, panel_top)], fill=(60, 70, 100), width=2)

    # Title text
    title = "The Whaling Wife"
    title_font_size = 80
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    try:
        bbox = draw.textbbox((0, 0), title, font=title_font)
        tw = bbox[2] - bbox[0]
    except Exception:
        tw = 0
    tx = (width - tw) // 2
    ty = panel_top + 100
    draw.text((tx, ty), title, fill=(255, 255, 255), font=title_font)

    # Divider line
    divider_y = ty + 85
    divider_w = 80
    draw.line(
        [(width // 2 - divider_w, divider_y), (width // 2 + divider_w, divider_y)],
        fill=(100, 120, 160),
        width=2,
    )

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
    ay = divider_y + 40
    draw.text((ax, ay), author, fill=(180, 190, 210), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Whaling Wife")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Waves
    draw_waves(draw, WIDTH, HEIGHT)

    # Step 3: Moon
    draw_moon(draw, WIDTH, HEIGHT)

    # Step 4: Whaling ship silhouette
    draw_ship(draw, WIDTH, HEIGHT)

    # Step 5: Harpoon
    draw_harpoon(draw, WIDTH, HEIGHT)

    # Step 6: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
        "small": str(FONTS_DIR / "arial.ttf"),
    }
    draw_title_panel(draw, WIDTH, HEIGHT, font_paths)

    # Soften the image slightly
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