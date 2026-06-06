#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Understudy."""

from __future__ import annotations

import argparse
import json
import math
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
    """Deep crimson to dark charcoal gradient for theatrical atmosphere."""
    for y in range(height):
        if y < height * 0.6:
            t = y / (height * 0.6)
            c = lerp_color((80, 10, 10), ((140, 20, 20)), t)
        else:
            t = (y - height * 0.6) / (height * 0.4)
            c = lerp_color((140, 20, 20), ((10, 5, 5)), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_curtains(draw: ImageDraw, width: int, height: int) -> None:
    """Draw velvet curtains framing the stage."""
    colors = [(180, 30, 30), (150, 20, 20), (120, 15, 15)]
    # Left curtain
    for i in range(6):
        x_offset = i * 35
        top_width = 80 - i * 8
        points = [
            (x_offset, 0),
            (x_offset + top_width, 0),
            (x_offset + 110, int(height * 0.85)),
            (x_offset + 50, int(height * 0.85)),
        ]
        draw.polygon(points, fill=colors[i % len(colors)])
        # Drape folds
        for fy in range(0, int(height * 0.8), 60):
            wave = int(15 * math.sin(fy / 40))
            draw.line(
                [(x_offset + 30 + wave, fy), (x_offset + 60, fy + 30)],
                fill=(100, 10, 10), width=3
            )

    # Right curtain
    for i in range(6):
        x_offset = width - (i + 1) * 35
        top_width = 80 - i * 8
        points = [
            (width - x_offset + (i * 35) - top_width, 0),
            (width - x_offset + (i * 35), 0),
            (width - x_offset + (i * 35) - 50, int(height * 0.85)),
            (width - x_offset + (i * 35) - 110, int(height * 0.85)),
        ]
        # Mirror the left curtain
        points2 = [
            (x_offset, 0),
            (x_offset + top_width, 0),
            (x_offset + 110, int(height * 0.85)),
            (x_offset + 50, int(height * 0.85)),
        ]
        draw.polygon(points2, fill=colors[i % len(colors)])
        for fy in range(0, int(height * 0.8), 60):
            wave = int(15 * math.sin(fy / 40))
            draw.line(
                [(x_offset + 30 - wave, fy), (x_offset + 60, fy + 30)],
                fill=(100, 10, 10), width=3
            )

    # Top valance
    draw.rectangle([(0, 0), (width, 60)], fill=(160, 25, 25))
    draw.rectangle([(0, 60), (width, 65)], fill=(200, 180, 140))


def draw_stage(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the stage floor at the bottom."""
    stage_y = int(height * 0.75)
    draw.rectangle([(0, stage_y), (width, height)], fill=(60, 40, 25))
    # Stage edge
    draw.line([(0, stage_y), (width, stage_y)], fill=(200, 180, 140), width=4)
    # Floorboards
    for x in range(0, width, 40):
        draw.line([(x, stage_y), (x, height)], fill=(50, 35, 20), width=1)


def draw_spotlight(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a cone of light from above, striking the stage."""
    cx = width // 2
    light_origin_y = 0
    spot_width_top = 400
    spot_width_bottom = 800
    stage_y = int(height * 0.75)

    # Light cone - subtle yellow/white
    points = [
        (cx - spot_width_top // 2, light_origin_y),
        (cx + spot_width_top // 2, light_origin_y),
        (cx + spot_width_bottom // 2, stage_y),
        (cx - spot_width_bottom // 2, stage_y),
    ]
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.polygon(points, fill=(255, 240, 200, 30))
    draw.bitmap((0, 0), overlay, fill=None)

    # More intense inner cone
    points2 = [
        (cx - spot_width_top // 4, light_origin_y),
        (cx + spot_width_top // 4, light_origin_y),
        (cx + spot_width_bottom // 3, stage_y),
        (cx - spot_width_bottom // 3, stage_y),
    ]
    overlay2 = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    overlay2_draw = ImageDraw.Draw(overlay2)
    overlay2_draw.polygon(points2, fill=(255, 240, 200, 40))
    draw.bitmap((0, 0), overlay2, fill=None)


def draw_mask(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a single theatrical comedy/tragedy mask on the stage."""
    cx = width // 2
    my = int(height * 0.55)

    # Mask face shape
    mask_color = (220, 210, 190)
    # Face oval
    draw.ellipse([cx - 70, my - 80, cx + 70, my + 80], fill=mask_color, outline=(180, 170, 150), width=3)
    # Eye holes (tragedy - downturned)
    draw.ellipse([cx - 40, my - 30, cx - 15, my - 10], fill=(20, 15, 15))
    draw.ellipse([cx + 15, my - 30, cx + 40, my - 10], fill=(20, 15, 15))
    # Mouth (tragedy frown)
    draw.arc([cx - 25, my + 25, cx + 25, my + 55], 0, 180, fill=(20, 15, 15), width=4)
    # Eyebrows (downturned)
    draw.line([cx - 45, my - 42, cx - 15, my - 38], fill=(20, 15, 15), width=3)
    draw.line([cx + 15, my - 38, cx + 45, my - 42], fill=(20, 15, 15), width=3)
    # Nose
    draw.ellipse([cx - 5, my - 5, cx + 5, my + 10], fill=(180, 170, 150))
    # Highlight on mask
    draw.ellipse([cx - 50, my - 60, cx - 20, my - 40], fill=(240, 235, 220, 80))
    draw.ellipse([cx + 20, my - 60, cx + 50, my - 40], fill=(240, 235, 220, 80))

    # Ribbon below mask
    draw.rectangle([cx - 10, my + 82, cx + 10, my + 120], fill=(180, 30, 30))
    draw.ellipse([cx - 10, my + 115, cx + 10, my + 130], fill=(180, 30, 30))


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    draw.rectangle([(0, panel_top), (width, height)], fill=(15, 10, 10, 230))

    # Gold border at top of panel
    draw.line([(60, panel_top), (width - 60, panel_top)], fill=(210, 175, 60), width=3)

    # Title text
    title = "The Understudy"
    title_font_size = 80
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered
    try:
        bbox = draw.textbbox((0, 0), title, font=title_font)
        tw = bbox[2] - bbox[0]
    except Exception:
        tw = 0
    tx = (width - tw) // 2
    ty = panel_top + 80
    draw.text((tx, ty), title, fill=(255, 255, 255), font=title_font)

    # Gold line under title
    draw.line([(int(width * 0.35), ty + 100), (int(width * 0.65), ty + 100)], fill=(210, 175, 60), width=2)

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
    ay = ty + 130
    draw.text((ax, ay), author, fill=(210, 175, 60), font=author_font)

    # Small decorative elements at panel corners
    corner_size = 20
    draw.line([(30, panel_top + 10), (30, panel_top + corner_size)], fill=(210, 175, 60), width=2)
    draw.line([(30, panel_top + 10), (30 + corner_size, panel_top + 10)], fill=(210, 175, 60), width=2)
    draw.line([(width - 30, panel_top + 10), (width - 30, panel_top + corner_size)], fill=(210, 175, 60), width=2)
    draw.line([(width - 30, panel_top + 10), (width - 30 - corner_size, panel_top + 10)], fill=(210, 175, 60), width=2)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Understudy")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Stage floor
    draw_stage(draw, WIDTH, HEIGHT)

    # Step 3: Curtains
    draw_curtains(draw, WIDTH, HEIGHT)

    # Step 4: Spotlight
    draw_spotlight(draw, WIDTH, HEIGHT)

    # Step 5: Mask
    draw_mask(draw, WIDTH, HEIGHT)

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