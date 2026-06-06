#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Saffron Kitchen."""

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
    """Warm kitchen light: deep red-brown at top, saffron gold through the middle, copper below."""
    for y in range(height):
        if y < height * 0.30:
            t = y / (height * 0.30)
            c = lerp_color((38, 14, 10), (90, 38, 16), t)
        elif y < height * 0.55:
            t = (y - height * 0.30) / (height * 0.25)
            c = lerp_color((90, 38, 16), (168, 92, 26), t)
        elif y < height * 0.78:
            t = (y - height * 0.55) / (height * 0.23)
            c = lerp_color((168, 92, 26), (120, 60, 22), t)
        else:
            t = (y - height * 0.78) / (height * 0.22)
            c = lerp_color((120, 60, 22), (52, 24, 12), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_warm_glow(draw: ImageDraw, width: int, height: int) -> None:
    """A soft saffron glow, as if from an overhead kitchen lamp, centered on the still-life."""
    cx, cy = width // 2, int(height * 0.42)
    for r in range(640, 40, -14):
        t = r / 640
        alpha = int(34 * (1 - t))
        if alpha <= 0:
            continue
        col = lerp_color((255, 196, 70), (255, 150, 40), t)
        draw.ellipse(
            [cx - r, cy - int(r * 0.85), cx + r, cy + int(r * 0.85)],
            fill=(col[0], col[1], col[2], alpha),
        )


def draw_counter(draw: ImageDraw, width: int, height: int) -> None:
    """A dark wooden prep counter the still-life sits upon."""
    counter_top = int(height * 0.62)
    # Counter surface
    for y in range(counter_top, int(height * 0.80)):
        t = (y - counter_top) / (height * 0.80 - counter_top)
        c = lerp_color((70, 36, 18), (40, 20, 10), t)
        draw.line([(0, y), (width, y)], fill=c)
    # Wood grain lines
    rng_seed = 7
    for i in range(14):
        gy = counter_top + 18 + i * 26
        shade = 28 + (i % 3) * 10
        draw.line(
            [(0, gy + (i % 2) * 4), (width, gy - (i % 2) * 4)],
            fill=(40 + shade, 22 + shade // 2, 12),
            width=2,
        )
    # Front edge highlight
    draw.line([(0, counter_top), (width, counter_top)], fill=(150, 96, 48), width=4)


def draw_copper_pot(draw: ImageDraw, width: int, height: int) -> None:
    """A copper stockpot, the heart of the still-life, with rising steam."""
    cx = int(width * 0.50)
    base_y = int(height * 0.62)
    pot_w = 360
    pot_h = 300
    left = cx - pot_w // 2
    right = cx + pot_w // 2
    top = base_y - pot_h

    # Body of the pot (copper)
    for y in range(top, base_y):
        t = (y - top) / pot_h
        c = lerp_color((196, 110, 48), (120, 58, 24), t)
        draw.line([(left, y), (right, y)], fill=c)

    # Vertical copper sheen bands
    for bx in range(left + 30, right - 20, 60):
        draw.line([(bx, top + 20), (bx, base_y - 10)], fill=(235, 160, 90), width=6)
        draw.line([(bx + 18, top + 30), (bx + 18, base_y - 20)], fill=(150, 78, 36), width=4)

    # Rim
    draw.rectangle([left - 16, top - 22, right + 16, top + 6], fill=(210, 132, 64))
    draw.rectangle([left - 16, top - 22, right + 16, top - 12], fill=(245, 178, 104))

    # Dark interior at the rim
    draw.ellipse([left - 6, top - 14, right + 6, top + 30], fill=(48, 24, 12))
    # Golden broth surface inside
    draw.ellipse([left + 14, top - 4, right - 14, top + 24], fill=(232, 168, 52))
    draw.ellipse([left + 60, top + 2, right - 90, top + 16], fill=(255, 206, 96))

    # Handles
    draw.arc([left - 70, top + 60, left + 10, top + 150], 70, 290, fill=(220, 140, 70), width=14)
    draw.arc([right - 10, top + 60, right + 70, top + 150], 250, 110, fill=(220, 140, 70), width=14)

    # Steam rising
    rng = __import__("random").Random(21)
    for s in range(3):
        sx = cx - 70 + s * 70
        sy = top - 20
        pts = []
        for i in range(26):
            yy = sy - i * 16
            xx = sx + math.sin(i * 0.5 + s) * (18 + i) + rng.randint(-4, 4)
            pts.append((xx, yy))
        for i in range(len(pts) - 1):
            alpha = max(0, 70 - i * 3)
            if alpha <= 0:
                continue
            draw.line([pts[i], pts[i + 1]], fill=(255, 244, 220, alpha), width=8)


def draw_spice_bowls(draw: ImageDraw, width: int, height: int) -> None:
    """Small ceramic bowls of saffron and spices on the counter."""
    base_y = int(height * 0.62)

    # Bowl of saffron threads (left, deep red)
    bx, by = int(width * 0.24), base_y - 26
    draw.ellipse([bx - 90, by - 30, bx + 90, by + 50], fill=(60, 34, 22))
    draw.ellipse([bx - 78, by - 24, bx + 78, by + 34], fill=(36, 18, 12))
    # saffron threads heaped
    rng = __import__("random").Random(33)
    for _ in range(140):
        ang = rng.uniform(0, math.pi)
        rr = rng.uniform(0, 66)
        tx = bx + math.cos(ang) * rr
        ty = by + 4 - math.sin(ang) * (rr * 0.34)
        length = rng.randint(5, 12)
        a2 = rng.uniform(0, math.pi)
        col = rng.choice([(196, 36, 18), (220, 70, 24), (160, 24, 14), (235, 96, 30)])
        draw.line(
            [(tx, ty), (tx + math.cos(a2) * length, ty + math.sin(a2) * length * 0.5)],
            fill=col,
            width=2,
        )

    # Bowl of ground spice (right, ochre)
    gx, gy = int(width * 0.76), base_y - 22
    draw.ellipse([gx - 76, gy - 26, gx + 76, gy + 44], fill=(58, 32, 20))
    draw.ellipse([gx - 64, gy - 20, gx + 64, gy + 30], fill=(150, 86, 28))
    draw.ellipse([gx - 50, gy - 14, gx + 50, gy + 18], fill=(196, 124, 40))
    draw.ellipse([gx - 28, gy - 8, gx + 14, gy + 6], fill=(224, 156, 60))


def draw_chefs_knife(draw: ImageDraw, width: int, height: int) -> None:
    """A chef's knife laid across the counter at an angle, blade catching the light."""
    base_y = int(height * 0.62)
    # Knife laid diagonally in the foreground
    x0, y0 = int(width * 0.30), base_y + 96   # tip
    x1, y1 = int(width * 0.62), base_y + 40    # heel of blade
    # Blade (steel)
    blade = [
        (x0, y0),
        (x1, y1 - 36),
        (x1, y1 - 6),
        (x0 + 8, y0 + 16),
    ]
    draw.polygon(blade, fill=(176, 182, 190))
    # Blade sheen
    draw.line([(x0, y0 + 2), (x1, y1 - 30)], fill=(228, 232, 238), width=4)
    draw.line([(x0 + 6, y0 + 12), (x1, y1 - 10)], fill=(120, 126, 134), width=3)
    # Handle (dark wood)
    hx0, hy0 = x1, y1 - 22
    hx1, hy1 = x1 + 150, y1 + 2
    draw.line([(hx0, hy0), (hx1, hy1)], fill=(46, 26, 16), width=30)
    draw.line([(hx0, hy0 - 2), (hx1, hy1 - 2)], fill=(78, 46, 26), width=8)
    # Rivets
    for i in range(3):
        rx = hx0 + 36 + i * 38
        ry = hy0 + int((hy1 - hy0) * ((36 + i * 38) / 150))
        draw.ellipse([rx - 5, ry - 5, rx + 5, ry + 5], fill=(150, 120, 80))


def draw_scattered_threads(draw: ImageDraw, width: int, height: int) -> None:
    """A few stray saffron threads scattered across the counter for life."""
    base_y = int(height * 0.62)
    rng = __import__("random").Random(51)
    for _ in range(60):
        tx = rng.randint(40, width - 40)
        ty = rng.randint(base_y + 10, int(height * 0.78))
        length = rng.randint(8, 18)
        ang = rng.uniform(0, math.pi)
        col = rng.choice([(190, 40, 18), (216, 70, 26), (150, 28, 16)])
        draw.line(
            [(tx, ty), (tx + math.cos(ang) * length, ty + math.sin(ang) * length)],
            fill=col,
            width=2,
        )


def draw_embers(draw: ImageDraw, width: int, height: int) -> None:
    """Tiny warm motes drifting in the lamp light above the pot."""
    rng = __import__("random").Random(63)
    for _ in range(160):
        x = rng.randint(10, width - 10)
        y = rng.randint(10, int(height * 0.60))
        size = rng.randint(1, 3)
        alpha = rng.randint(50, 150)
        col = rng.choice([(255, 210, 120), (255, 170, 70), (255, 230, 160)])
        draw.ellipse(
            [x - size, y - size, x + size, y + size],
            fill=(col[0], col[1], col[2], alpha),
        )


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Saffron Kitchen")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Step 1: Warm gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Soft saffron lamp glow
    draw_warm_glow(draw, WIDTH, HEIGHT)

    # Step 3: Drifting warm motes
    draw_embers(draw, WIDTH, HEIGHT)

    # Step 4: The prep counter
    draw_counter(draw, WIDTH, HEIGHT)

    # Step 5: Spice bowls behind the pot
    draw_spice_bowls(draw, WIDTH, HEIGHT)

    # Step 6: The copper stockpot with steam
    draw_copper_pot(draw, WIDTH, HEIGHT)

    # Step 7: The chef's knife in the foreground
    draw_chefs_knife(draw, WIDTH, HEIGHT)

    # Step 8: Scattered saffron threads
    draw_scattered_threads(draw, WIDTH, HEIGHT)

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
