#!/usr/bin/env python3
"""Generate a 1600x2560 cover for The Watermelon Summer using PIL."""

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1600, 2560
ARIAL_BD = "C:/Windows/Fonts/arialbd.ttf"

GRADIENT_TOP = (34, 139, 34)      # forest green
GRADIENT_BOTTOM = (255, 215, 0)   # sun yellow
SUN_COLOR = (255, 200, 50)
DIRT_COLOR = (139, 90, 43)
STAND_COLOR = (101, 67, 33)       # brown for the stand
ROOF_COLOR = (178, 34, 34)        # firebrick for tin roof
MELON_GREEN = (21, 87, 36)
MELON_STRIPE = (10, 50, 20)
PANEL_COLOR = (20, 20, 20)        # dark panel for title


def make_gradient(draw: ImageDraw) -> None:
    """Draw a vertical gradient from GRADIENT_TOP to GRADIENT_BOTTOM."""
    for y in range(HEIGHT):
        r = int(GRADIENT_TOP[0] + (GRADIENT_BOTTOM[0] - GRADIENT_TOP[0]) * y / HEIGHT)
        g = int(GRADIENT_TOP[1] + (GRADIENT_BOTTOM[1] - GRADIENT_TOP[1]) * y / HEIGHT)
        b = int(GRADIENT_TOP[2] + (GRADIENT_BOTTOM[2] - GRADIENT_TOP[2]) * y / HEIGHT)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def draw_sun(draw: ImageDraw) -> None:
    """Draw a sun in the upper right."""
    cx, cy = 1300, 300
    for r in range(200, 0, -1):
        alpha = int(255 * (1 - r / 200))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*SUN_COLOR, alpha))


def draw_dirt_road(draw: ImageDraw) -> None:
    """Draw a winding dirt road at the bottom."""
    points = [(0, 2000), (400, 1900), (700, 1850), (900, 1800),
              (1100, 1750), (1300, 1700), (WIDTH, 1650)]
    widths = [200, 180, 160, 140, 120, 100, 80]
    for i in range(len(points) - 1):
        draw.line([points[i], points[i + 1]], fill=DIRT_COLOR, width=widths[i])


def draw_watermelon_stand(draw: ImageDraw) -> None:
    """Draw the watermelon stand in the middle distance."""
    # Platform
    draw.rectangle([550, 1400, 1050, 1500], fill=STAND_COLOR)
    # Posts
    draw.rectangle([560, 900, 590, 1400], fill=STAND_COLOR)
    draw.rectangle([1010, 900, 1040, 1400], fill=STAND_COLOR)
    # Roof
    draw.polygon([(530, 900), (800, 750), (1070, 900)], fill=ROOF_COLOR)
    # Sign board
    sign_y = 920
    draw.rectangle([620, sign_y, 980, sign_y + 80], fill=(255, 255, 240))
    try:
        font_sign = ImageFont.truetype(ARIAL_BD, 36)
        draw.text((800, sign_y + 40), "HARVELL'S MELONS", fill=(0, 0, 0),
                  font=font_sign, anchor="mm")
    except Exception:
        pass


def draw_watermelons(draw: ImageDraw) -> None:
    """Draw watermelon stacks near the stand."""
    positions = [
        (1100, 1480, 60),
        (1160, 1480, 55),
        (1220, 1480, 50),
        (1130, 1420, 55),
        (1190, 1420, 50),
        (1160, 1360, 50),
    ]
    for x, y, r in positions:
        draw.ellipse([x - r, y - r, x + r, y + r], fill=MELON_GREEN)
        # Stripes
        for offset in range(-r // 3, r // 3 + 1, 6):
            draw.arc([x - r, y - r, x + r, y + r],
                     -30 + offset * 2, 30 + offset * 2,
                     fill=MELON_STRIPE, width=2)
        # Highlight
        draw.ellipse([x - r // 4, y - r // 2, x, y - r // 4],
                     fill=(80, 200, 80), width=0)


def draw_title_panel(draw: ImageDraw) -> None:
    """Draw dark panel at bottom with title and author."""
    draw.rectangle([0, 1920, WIDTH, 2560], fill=PANEL_COLOR)

    # Decorative line at top of panel
    draw.line([(100, 1960), (WIDTH - 100, 1960)], fill=(255, 215, 0), width=3)

    try:
        font_title = ImageFont.truetype(ARIAL_BD, 80)
        font_author = ImageFont.truetype(ARIAL_BD, 40)

        # Title
        draw.text((WIDTH // 2, 2080), "THE WATERMELON", fill=(255, 255, 255),
                  font=font_title, anchor="mm")
        draw.text((WIDTH // 2, 2180), "SUMMER", fill=(255, 215, 0),
                  font=font_title, anchor="mm")

        # Decorative line
        draw.line([(400, 2260), (WIDTH - 400, 2260)], fill=(255, 215, 0), width=2)

        # Author
        draw.text((WIDTH // 2, 2360), "Barış Kısır", fill=(200, 200, 200),
                  font=font_author, anchor="mm")
    except Exception:
        # Fallback if font not found
        draw.text((WIDTH // 2, 2100), "THE WATERMELON SUMMER",
                  fill=(255, 255, 255), anchor="mm")
        draw.text((WIDTH // 2, 2300), "Barış Kısır",
                  fill=(200, 200, 200), anchor="mm")


def create_cover(output_path: Path) -> None:
    """Generate the 1600x2560 cover image."""
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # 1. Gradient background
    make_gradient(draw)

    # 2. Sun
    draw_sun(draw)

    # 3. Dirt road
    draw_dirt_road(draw)

    # 4. Watermelon stand
    draw_watermelon_stand(draw)

    # 5. Watermelons
    draw_watermelons(draw)

    # 6. Title panel at bottom
    draw_title_panel(draw)

    # Convert to RGB for saving as PNG
    img_rgb = img.convert("RGB")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img_rgb, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()))
    img_rgb.save(str(output_path), "PNG")
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
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--out", type=Path, default=Path(
        "The_Watermelon_Summer/covers/The_Watermelon_Summer.png"))
    args = parser.parse_args()

    output_path = args.out or Path(
        "The_Watermelon_Summer/covers/The_Watermelon_Summer.png")

    # If metadata is provided, derive output from it
    if args.metadata:
        meta = json.loads(args.metadata.read_text(encoding="utf-8"))
        cover_path = meta.get("cover_path")
        if cover_path:
            # Find the ROOT directory (parent of the tools directory)
            script_dir = Path(__file__).resolve().parent
            root_dir = script_dir.parent.parent
            output_path = root_dir / cover_path

    create_cover(output_path)


if __name__ == "__main__":
    main()