#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Factory of Smiles."""

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
    """Clinical white to sickly yellow to sterile gray gradient."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((240, 240, 235), ((220, 210, 180)), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((220, 210, 180), ((190, 185, 170)), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((190, 185, 170), ((50, 45, 40)), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_conveyor_belt(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a conveyor belt running across the middle of the cover."""
    # Belt surface
    belt_y = int(height * 0.55)
    belt_h = 30
    draw.rectangle([(0, belt_y - belt_h // 2), (width, belt_y + belt_h // 2)], fill=(80, 75, 70))

    # Belt rollers
    for x in range(0, width, 120):
        draw.ellipse([(x - 8, belt_y - 12), (x + 8, belt_y + 12)], fill=(60, 60, 60))
        draw.ellipse([(x - 5, belt_y - 9), (x + 5, belt_y + 9)], fill=(100, 100, 100))

    # Belt highlight line
    draw.line([(0, belt_y), (width, belt_y)], fill=(130, 125, 120), width=1)


def draw_smile_cubes(draw: ImageDraw, width: int, height: int) -> None:
    """Draw smile-cubes on the conveyor belt."""
    belt_y = int(height * 0.55)
    cube_y = belt_y - 25
    cube_size = 30
    colors = [(255, 230, 100, 220), (255, 210, 80, 200), (240, 220, 120, 210), (250, 200, 60, 190)]

    for i, cx in enumerate(range(100, width - 50, 140)):
        color = colors[i % len(colors)]
        # Cube body
        draw.rectangle(
            [(cx - cube_size // 2, cube_y - cube_size // 2),
             (cx + cube_size // 2, cube_y + cube_size // 2)],
            fill=color,
        )
        # Glow effect
        draw.rectangle(
            [(cx - cube_size // 2 + 3, cube_y - cube_size // 2 + 3),
             (cx + cube_size // 2 - 3, cube_y + cube_size // 2 - 3)],
            fill=(255, 255, 200, 180),
        )
        # Smile face on each cube
        face_cx = cx
        face_cy = cube_y
        # Eyes
        draw.ellipse([(face_cx - 6, face_cy - 6), (face_cx - 3, face_cy - 3)], fill=(80, 60, 20, 200))
        draw.ellipse([(face_cx + 3, face_cy - 6), (face_cx + 6, face_cy - 3)], fill=(80, 60, 20, 200))
        # Smile
        draw.arc(
            [(face_cx - 7, face_cy - 3), (face_cx + 7, face_cy + 6)],
            start=0, end=180, fill=(80, 60, 20, 200), width=2,
        )


def draw_smile_masks(draw: ImageDraw, width: int, height: int) -> None:
    """Draw theatrical happy/sad masks as factory elements."""
    # Large happy mask on the left
    mx, my = int(width * 0.25), int(height * 0.35)
    mask_r = 80
    # Mask face
    draw.ellipse([(mx - mask_r, my - mask_r), (mx + mask_r, my + mask_r)], fill=(230, 215, 190, 200))
    draw.ellipse([(mx - mask_r, my - mask_r), (mx + mask_r, my + mask_r)], outline=(180, 165, 140), width=3)
    # Eye holes
    draw.ellipse([(mx - 30, my - 25), (mx - 10, my - 5)], fill=(50, 45, 40))
    draw.ellipse([(mx + 10, my - 25), (mx + 30, my - 5)], fill=(50, 45, 40))
    # Big painted smile
    draw.arc(
        [(mx - 35, my - 10), (mx + 35, my + 40)],
        start=10, end=170, fill=(180, 50, 50, 200), width=6,
    )

    # Large sad mask on the right
    mx2, my2 = int(width * 0.75), int(height * 0.35)
    draw.ellipse([(mx2 - mask_r, my2 - mask_r), (mx2 + mask_r, my2 + mask_r)], fill=(200, 190, 175, 200))
    draw.ellipse([(mx2 - mask_r, my2 - mask_r), (mx2 + mask_r, my2 + mask_r)], outline=(160, 150, 135), width=3)
    # Eye holes
    draw.ellipse([(mx2 - 30, my2 - 25), (mx2 - 10, my2 - 5)], fill=(50, 45, 40))
    draw.ellipse([(mx2 + 10, my2 - 25), (mx2 + 30, my2 - 5)], fill=(50, 45, 40))
    # Frown
    draw.arc(
        [(mx2 - 35, my2 + 10), (mx2 + 35, my2 + 40)],
        start=190, end=350, fill=(100, 80, 80, 200), width=6,
    )


def draw_pipes_and_hoppers(draw: ImageDraw, width: int, height: int) -> None:
    """Draw industrial pipes and hoppers at the top of the cover."""
    # Hoppers
    for hx in [int(width * 0.15), int(width * 0.5), int(width * 0.85)]:
        hy = 40
        # Hopper body (trapezoid)
        draw.polygon(
            [(hx - 50, hy), (hx + 50, hy), (hx + 30, hy + 120), (hx - 30, hy + 120)],
            fill=(160, 155, 145, 200),
        )
        draw.polygon(
            [(hx - 50, hy), (hx + 50, hy), (hx + 30, hy + 120), (hx - 30, hy + 120)],
            outline=(120, 115, 105), width=2,
        )

    # Pipes from hoppers
    pipe_color = (140, 135, 125, 200)
    for px in [int(width * 0.15), int(width * 0.5), int(width * 0.85)]:
        # Vertical pipe
        draw.rectangle([(px - 6, 160), (px + 6, int(height * 0.55))], fill=pipe_color)
        draw.rectangle([(px - 6, 160), (px + 6, int(height * 0.55))], outline=(100, 95, 85), width=1)


def draw_assembly_line_workers(draw: ImageDraw, width: int, height: int) -> None:
    """Draw stylized silhouette workers along the assembly line."""
    belt_y = int(height * 0.55)
    worker_colors = [(180, 175, 165, 180), (170, 165, 155, 180), (175, 170, 160, 180)]

    for i in range(6):
        wx = 60 + i * 280
        wy = belt_y - 80
        color = worker_colors[i % len(worker_colors)]

        # Body
        draw.rectangle([(wx - 18, wy - 10), (wx + 18, wy + 50)], fill=color)
        # Head
        draw.ellipse([(wx - 14, wy - 40), (wx + 14, wy - 14)], fill=color)
        # Smile on worker face (forced smile)
        draw.arc(
            [(wx - 8, wy - 30), (wx + 8, wy - 18)],
            start=0, end=180, fill=(100, 95, 85, 220), width=2,
        )
        # Arms reaching for belt
        draw.line([(wx + 18, wy + 10), (wx + 60, wy + 20)], fill=color, width=6)
        # Hair cap
        draw.rectangle([(wx - 16, wy - 42), (wx + 16, wy - 36)], fill=(200, 190, 170, 200))


def draw_background_eye(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a subtle all-seeing eye motif in the background."""
    cx, cy = width // 2, int(height * 0.25)
    # Outer ring
    draw.ellipse([(cx - 180, cy - 80), (cx + 180, cy + 80)], outline=(200, 190, 170, 60), width=3)
    # Inner circle
    draw.ellipse([(cx - 120, cy - 60), (cx + 120, cy + 60)], outline=(200, 190, 170, 40), width=2)
    # Pupil
    draw.ellipse([(cx - 30, cy - 20), (cx + 30, cy + 20)], fill=(200, 190, 170, 40))
    draw.ellipse([(cx - 10, cy - 8), (cx + 10, cy + 8)], fill=(200, 190, 170, 60))


def draw_title_panel(draw: ImageDraw, draw_img: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom of the cover."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark semi-transparent rectangle
    draw.rectangle([(0, panel_top), (width, height)], fill=(30, 25, 20, 220))

    # Subtle border at top
    draw.line([(0, panel_top), (width, panel_top)], fill=(255, 200, 50), width=3)

    # Title text
    title = "The Factory\nof Smiles"
    title_font_size = 80
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered, white text
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
    ay = y_offset + 45
    draw.text((ax, ay), author, fill=(255, 255, 200), font=author_font)

    # Tagline
    tagline = "A Dystopian Satire"
    tagline_font_size = 22
    try:
        tagline_font = ImageFont.truetype(str(font_paths["small"]), tagline_font_size)
    except Exception:
        tagline_font = ImageFont.load_default()

    try:
        tbbox = draw.textbbox((0, 0), tagline, font=tagline_font)
        tw2 = tbbox[2] - tbbox[0]
    except Exception:
        tw2 = 0
    tx2 = (width - tw2) // 2
    ty = ay + 50
    draw.text((tx2, ty), tagline, fill=(180, 180, 180), font=tagline_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Factory of Smiles")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Subtle all-seeing eye in background
    draw_background_eye(draw, WIDTH, HEIGHT)

    # Step 3: Pipes and hoppers at top
    draw_pipes_and_hoppers(draw, WIDTH, HEIGHT)

    # Step 4: Smile masks (theatrical)
    draw_smile_masks(draw, WIDTH, HEIGHT)

    # Step 5: Conveyor belt
    draw_conveyor_belt(draw, WIDTH, HEIGHT)

    # Step 6: Smile-cubes on belt
    draw_smile_cubes(draw, WIDTH, HEIGHT)

    # Step 7: Assembly line workers
    draw_assembly_line_workers(draw, WIDTH, HEIGHT)

    # Step 8: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
        "small": str(FONTS_DIR / "arial.ttf"),
    }
    draw_title_panel(draw, draw, WIDTH, HEIGHT, font_paths)

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