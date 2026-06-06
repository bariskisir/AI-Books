#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Thief of Small Things."""

from __future__ import annotations

import argparse
import json
import math
import random
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
    """Warm ochre to deep teal gradient for the quirky/folkloric feel."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((180, 140, 80), (210, 170, 100), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((210, 170, 100), (100, 140, 140), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((100, 140, 140), (30, 60, 70), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_village_market(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a stylized village market scene with stalls and awnings."""
    rng = random.Random(42)

    # Market stalls in the background
    stall_colors = [(160, 130, 100), (140, 110, 80), (170, 140, 110)]
    for i in range(5):
        sx = 100 + i * 300
        sy = int(height * 0.45)
        sw, sh = 180, 160

        # Stall body
        color = stall_colors[i % len(stall_colors)]
        draw.rectangle([sx, sy, sx + sw, sy + sh], fill=color)

        # Awning
        awning_color = [(160, 80, 60), (60, 100, 110), (140, 120, 70)][i % 3]
        draw.polygon(
            [(sx - 10, sy), (sx + sw + 10, sy), (sx + sw + 20, sy - 30), (sx - 20, sy - 30)], fill=awning_color
        )

        # Items on stall
        for j in range(3):
            ix = sx + 30 + j * 50
            iy = sy + 20
            # Small objects: jars, books, fruits
            if rng.random() < 0.5:
                draw.ellipse([ix, iy, ix + 25, iy + 30], fill=(200, 180, 120))
            else:
                draw.rectangle([ix, iy, ix + 20, iy + 28], fill=(120, 80, 60))


def draw_small_objects(draw: ImageDraw, width: int, height: int) -> None:
    """Draw scattered small objects in the foreground — keys, coins, a feather, a jar."""
    rng = random.Random(7)

    objects = [
        # Keys
        lambda: draw.ellipse([200, 1350, 220, 1370], fill=(180, 160, 100)),
        lambda: draw.line([210, 1350, 210, 1320], fill=(180, 160, 100), width=3),
        lambda: draw.ellipse([210, 1315, 220, 1325], fill=(180, 160, 100)),
        # Coin
        lambda: draw.ellipse([750, 1400, 780, 1430], fill=(200, 180, 80)),
        lambda: draw.ellipse([752, 1402, 778, 1428], fill=(160, 140, 60)),
        # Feather
        lambda: draw.line([1300, 1380, 1350, 1320], fill=(180, 170, 150), width=2),
        lambda: draw.ellipse([1330, 1330, 1360, 1360], fill=(190, 180, 160)),
        # Small jar
        lambda: draw.rectangle([500, 1280, 540, 1340], fill=(150, 180, 180, 180)),
        lambda: draw.ellipse([495, 1275, 545, 1295], fill=(160, 190, 190, 200)),
        # Scattered buttons
        lambda: draw.ellipse([1000, 1420, 1020, 1440], fill=(140, 100, 80)),
        lambda: draw.ellipse([1025, 1430, 1040, 1445], fill=(120, 80, 60)),
        # A playing card
        lambda: draw.rectangle([300, 1420, 350, 1480], fill=(220, 210, 190)),
        lambda: draw.rectangle([303, 1423, 347, 1477], outline=(100, 80, 60), width=1),
        # Spool of thread
        lambda: draw.rectangle([1150, 1340, 1175, 1370], fill=(80, 120, 130)),
        lambda: draw.rectangle([1145, 1345, 1180, 1365], fill=(100, 140, 150)),
    ]

    for obj in objects:
        obj()


def draw_hands_reaching(draw: ImageDraw, width: int, height: int) -> None:
    """Draw stylized reaching hands emerging from the sides toward the center."""
    rng = random.Random(13)

    # Left hand reaching right
    hand_y = int(height * 0.55)
    # Arm
    draw.line([(0, hand_y + 20), (250, hand_y)], fill=(200, 170, 140), width=18)
    # Fingers
    for i in range(4):
        fx = 230 + i * 15
        fy = hand_y - 5 + i * 5
        draw.line([(fx, fy), (fx + 40, fy - 10 + i * 3)], fill=(200, 170, 140), width=6)
    # Thumb
    draw.line([(230, hand_y + 15), (260, hand_y + 25)], fill=(200, 170, 140), width=7)

    # Right hand reaching left
    hand_y2 = int(height * 0.65)
    draw.line([(width, hand_y2 - 10), (width - 250, hand_y2 + 5)], fill=(190, 160, 130), width=18)
    for i in range(4):
        fx = width - 230 - i * 15
        fy = hand_y2 - 10 + i * 5
        draw.line([(fx, fy), (fx - 40, fy - 10 + i * 3)], fill=(190, 160, 130), width=6)
    draw.line([(width - 230, hand_y2 + 10), (width - 260, hand_y2 + 20)], fill=(190, 160, 130), width=7)


def draw_glowing_motes(draw: ImageDraw, width: int, height: int) -> None:
    """Draw small glowing motes of light — stolen intangibles floating upward."""
    rng = random.Random(99)

    for _ in range(60):
        x = rng.randint(100, width - 100)
        y = rng.randint(200, int(height * 0.8))
        size = rng.randint(2, 6)

        # Color: warm gold or cool teal
        if rng.random() < 0.6:
            color = (255, 220, 120, 160)
            glow = (255, 200, 80, 40)
        else:
            color = (120, 200, 220, 160)
            glow = (80, 160, 180, 40)

        # Outer glow
        draw.ellipse([x - size * 3, y - size * 3, x + size * 3, y + size * 3], fill=glow)
        # Core
        draw.ellipse([x - size, y - size, x + size, y + size], fill=color)


def draw_cobblestones(draw: ImageDraw, width: int, height: int) -> None:
    """Draw subtle cobblestone texture at the bottom of the scene."""
    rng = random.Random(24)
    base_y = int(height * 0.78)

    for row in range(4):
        offset = (row % 2) * 40
        for col in range(20):
            cx = col * 90 + offset
            cy = base_y + row * 35
            shade = rng.randint(60, 90)
            draw.ellipse([cx - 35, cy - 12, cx + 35, cy + 12], fill=(shade, shade + 5, shade + 10))


def draw_title_panel(draw: ImageDraw, draw_img: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom with white text."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark semi-transparent
    draw.rectangle([(0, panel_top), (width, height)], fill=(20, 25, 30, 220))

    # Subtle top border line
    draw.line([(0, panel_top), (width, panel_top)], fill=(180, 160, 100), width=2)

    # Decorative line
    draw.line([(int(width * 0.3), panel_top + 5), (int(width * 0.7), panel_top + 5)], fill=(180, 160, 100, 120), width=1)

    # Title text - use arialbd.ttf
    title = "The Thief of\nSmall Things"
    title_font_size = 76
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered
    lines = title.split("\n")
    y_offset = panel_top + 100
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
    author_font_size = 34
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
    ay = y_offset + 30
    draw.text((ax, ay), author, fill=(200, 200, 200), font=author_font)

    # Small decorative element below author
    draw.line(
        [(int(width * 0.4), ay + 45), (int(width * 0.6), ay + 45)],
        fill=(180, 160, 100, 100),
        width=1,
    )


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Thief of Small Things")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Village market
    draw_village_market(draw, WIDTH, HEIGHT)

    # Step 3: Cobblestones
    draw_cobblestones(draw, WIDTH, HEIGHT)

    # Step 4: Small objects scattered
    draw_small_objects(draw, WIDTH, HEIGHT)

    # Step 5: Hands reaching
    draw_hands_reaching(draw, WIDTH, HEIGHT)

    # Step 6: Glowing motes (stolen intangibles)
    draw_glowing_motes(draw, WIDTH, HEIGHT)

    # Step 7: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arial.ttf"),
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