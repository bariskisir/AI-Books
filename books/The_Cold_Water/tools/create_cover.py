#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Cold Water — Florida hurricane debut novel."""

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


def draw_hurricane_sky(draw: ImageDraw, width: int, height: int) -> None:
    """Storm gray to bruised purple gradient for the hurricane sky."""
    for y in range(height):
        if y < height * 0.3:
            t = y / (height * 0.3)
            c = lerp_color((80, 85, 90), (55, 60, 70), t)
        elif y < height * 0.6:
            t = (y - height * 0.3) / (height * 0.3)
            c = lerp_color((55, 60, 70), (40, 45, 55), t)
        else:
            t = (y - height * 0.6) / (height * 0.4)
            c = lerp_color((40, 45, 55), (20, 22, 30), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_storm_clouds(draw: ImageDraw, width: int, height: int) -> None:
    """Draw layered storm clouds across the sky."""
    rng = random.Random(1)
    cloud_positions = [
        (width * 0.1, height * 0.08, 1.2),
        (width * 0.35, height * 0.05, 1.5),
        (width * 0.6, height * 0.12, 1.3),
        (width * 0.8, height * 0.06, 1.1),
        (width * 0.2, height * 0.2, 0.9),
        (width * 0.5, height * 0.18, 1.0),
        (width * 0.75, height * 0.22, 0.8),
        (width * -0.1, height * 0.15, 1.4),
    ]
    for cx, cy, scale in cloud_positions:
        w = int(400 * scale)
        h = int(120 * scale)
        # Cloud body
        for i in range(5):
            ox = rng.randint(-30, 30)
            oy = rng.randint(-20, 20)
            rw = int(w * (0.6 + rng.random() * 0.4))
            rh = int(h * (0.6 + rng.random() * 0.4))
            draw.ellipse(
                [int(cx + ox - rw // 2), int(cy + oy - rh // 2), int(cx + ox + rw // 2), int(cy + oy + rh // 2)],
                fill=(45, 50, 60, 180),
            )
        # Darker bottom
        draw.ellipse(
            [int(cx - w // 2), int(cy + h // 4), int(cx + w // 2), int(cy + h // 2 + 20)],
            fill=(30, 35, 45, 200),
        )


def draw_palmetto(draw: ImageDraw, x: int, y: int, scale: float, rng: random.Random) -> None:
    """Draw a single palmetto plant."""
    # Fronds radiating from center
    frond_count = rng.randint(6, 10)
    for i in range(frond_count):
        angle = (i / frond_count) * 360 + rng.randint(-15, 15)
        radians = math.radians(angle)
        length = int(rng.randint(60, 120) * scale)
        end_x = x + int(math.cos(radians) * length)
        end_y = y + int(math.sin(radians) * (length * 0.6))
        # Draw frond as connected line segments
        segments = 8
        points = []
        for s in range(segments + 1):
            t = s / segments
            px = x + (end_x - x) * t + rng.randint(-8, 8)
            py = y + (end_y - y) * t + rng.randint(-4, 4)
            points.append((px, py))
        draw.line(points, fill=(25, 55, 30), width=rng.randint(2, 4))
        # Leaf tips
        draw.ellipse(
            [end_x - 3, end_y - 3, end_x + 3, end_y + 3],
            fill=(35, 70, 40),
        )


def draw_trailer(draw: ImageDraw, x: int, y: int, scale: float) -> None:
    """Draw a small double-wide trailer."""
    w, h = int(280 * scale), int(140 * scale)
    # Main body
    draw.rectangle([x - w // 2, y - h // 2, x + w // 2, y + h // 2], fill=(160, 150, 130))
    # Roof line
    draw.line([(x - w // 2 - 10, y - h // 2), (x + w // 2 + 10, y - h // 2)], fill=(100, 95, 80), width=4)
    # Windows
    for wx in range(-60, 80, 50):
        draw.rectangle(
            [x + wx, y - h // 2 + 20, x + wx + 30, y - h // 2 + 55],
            fill=(30, 35, 50),
        )
    # Door
    draw.rectangle([x + 20, y - h // 2 + 20, x + 55, y + h // 2], fill=(100, 55, 35))
    # Steps
    draw.rectangle([x + 15, y + h // 2, x + 60, y + h // 2 + 15], fill=(120, 115, 100))
    # Skirting
    draw.rectangle([x - w // 2, y + h // 2, x + w // 2, y + h // 2 + 12], fill=(90, 85, 75))
    # Air conditioner in window
    draw.rectangle(
        [x - w // 2 + 10, y - h // 2 + 25, x - w // 2 + 45, y - h // 2 + 55],
        fill=(100, 100, 100),
    )


def draw_trailer_park(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a small cluster of trailers and palmettos for the landscape."""
    rng = random.Random(3)
    # Ground line
    ground_y = int(height * 0.72)
    draw.rectangle([(0, ground_y), (width, height)], fill=(55, 65, 35))

    # Trailer 1 (center, main)
    draw_trailer(draw, width // 2, ground_y - 80, 1.0)
    # Trailer 2 (left, smaller)
    draw_trailer(draw, width // 2 - 350, ground_y - 65, 0.7)
    # Trailer 3 (right, smaller)
    draw_trailer(draw, width // 2 + 320, ground_y - 60, 0.6)

    # Palmettos
    for _ in range(15):
        px = rng.randint(50, width - 50)
        py = ground_y + rng.randint(10, 60)
        sc = 0.5 + rng.random() * 0.8
        draw_palmetto(draw, px, py, sc, rng)

    # Broken tree / debris in foreground
    for _ in range(6):
        dx = rng.randint(100, width - 100)
        dy = ground_y + rng.randint(30, 100)
        # Fallen branch
        draw.line(
            [(dx, dy), (dx + rng.randint(30, 80), dy + rng.randint(10, 30))],
            fill=(40, 35, 25),
            width=rng.randint(3, 6),
        )

    # Additional ground texture
    for _ in range(20):
        gx = rng.randint(0, width)
        gy = ground_y + rng.randint(0, 200)
        draw.rectangle([gx, gy, gx + 2, gy + 2], fill=(60, 75, 40))


def draw_rain(draw: ImageDraw, width: int, height: int) -> None:
    """Draw diagonal rain streaks across the image."""
    rng = random.Random(5)
    for _ in range(200):
        x = rng.randint(0, width)
        y = rng.randint(0, int(height * 0.75))
        length = rng.randint(15, 40)
        draw.line(
            [(x, y), (x + 8, y + length)],
            fill=(180, 190, 200, 60),
            width=1,
        )


def draw_citrus_glow(draw: ImageDraw, width: int, height: int) -> None:
    """Subtle citrus color glow in the lower sky — a hint of Florida."""
    for y in range(int(height * 0.4), int(height * 0.6)):
        t = (y - height * 0.4) / (height * 0.2)
        alpha = int(20 * (1 - abs(t - 0.5) * 2))
        if alpha > 0:
            t_adj = (y - height * 0.4) / (height * 0.2)
            c = lerp_color((220, 160, 50), (240, 180, 60), t_adj)
            draw.line([(0, y), (width, y)], fill=(c[0], c[1], c[2], alpha))


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom with WHITE text."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    draw.rectangle([(0, panel_top), (width, height)], fill=(18, 20, 25, 230))

    # Subtle line at top of panel
    draw.line([(0, panel_top), (width, panel_top)], fill=(80, 85, 95), width=2)

    # Title text - use arialbd.ttf
    title = "The Cold Water"
    title_font_size = 80
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        try:
            title_font = ImageFont.truetype(str(font_paths["fallback"]), title_font_size)
        except Exception:
            title_font = ImageFont.load_default()

    # Draw title centered in white
    try:
        bbox = draw.textbbox((0, 0), title, font=title_font)
        tw = bbox[2] - bbox[0]
    except Exception:
        tw = 0
    tx = (width - tw) // 2
    ty = panel_top + 80
    draw.text((tx, ty), title, fill=(255, 255, 255), font=title_font)

    # Author name below title
    author = "Barış Kısır"
    author_font_size = 36
    try:
        author_font = ImageFont.truetype(str(font_paths["author"]), author_font_size)
    except Exception:
        try:
            author_font = ImageFont.truetype(str(font_paths["fallback"]), author_font_size)
        except Exception:
            author_font = ImageFont.load_default()

    try:
        abbox = draw.textbbox((0, 0), author, font=author_font)
        aw = abbox[2] - abbox[0]
    except Exception:
        aw = 0
    ax = (width - aw) // 2
    ay = ty + 110
    draw.text((ax, ay), author, fill=(200, 200, 200), font=author_font)

    # Genre line at bottom
    genre = "A DEBUT NOVEL"
    genre_font_size = 20
    try:
        genre_font = ImageFont.truetype(str(font_paths["small"]), genre_font_size)
    except Exception:
        genre_font = ImageFont.load_default()

    try:
        gbbox = draw.textbbox((0, 0), genre, font=genre_font)
        gw = gbbox[2] - gbbox[0]
    except Exception:
        gw = 0
    gx = (width - gw) // 2
    gy = ay + 60
    draw.text((gx, gy), genre, fill=(150, 155, 160), font=genre_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Cold Water")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Hurricane sky gradient
    draw_hurricane_sky(draw, WIDTH, HEIGHT)

    # Step 2: Storm clouds
    draw_storm_clouds(draw, WIDTH, HEIGHT)

    # Step 3: Citrus glow in lower sky
    draw_citrus_glow(draw, WIDTH, HEIGHT)

    # Step 4: Trailer park landscape
    draw_trailer_park(draw, WIDTH, HEIGHT)

    # Step 5: Rain streaks
    draw_rain(draw, WIDTH, HEIGHT)

    # Step 6: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
        "small": str(FONTS_DIR / "arial.ttf"),
        "fallback": str(FONTS_DIR / "arial.ttf"),
    }
    draw_title_panel(draw, WIDTH, HEIGHT, font_paths)

    # Soften slightly
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