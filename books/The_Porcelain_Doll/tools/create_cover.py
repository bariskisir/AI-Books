#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Porcelain Doll."""

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
    """Vermillion-to-ivory gradient evoking Japanese literary aesthetics."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((100, 20, 20), (160, 60, 40), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((160, 60, 40), (200, 150, 110), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((200, 150, 110), (230, 210, 190), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_moon(draw: ImageDraw, width: int, height: int) -> None:
    """A pale full moon in the upper portion of the cover."""
    cx, cy = width // 2, int(height * 0.18)
    radius = 90

    # Outer glow
    for r in range(radius + 40, radius, -2):
        alpha = max(0, 40 - (r - radius) * 2)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 240, 220, alpha))

    # Moon body
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(245, 235, 215))

    # Subtle crater texture
    rng = random.Random(17)
    for _ in range(6):
        crx = cx + rng.randint(-50, 50)
        cry = cy + rng.randint(-50, 50)
        crr = rng.randint(8, 20)
        draw.ellipse([crx - crr, cry - crr, crx + crr, cry + crr], fill=(230, 220, 200, 80))
    for _ in range(4):
        crx = cx + rng.randint(-40, 40)
        cry = cy + rng.randint(-40, 40)
        crr = rng.randint(3, 8)
        draw.ellipse([crx - crr, cry - crr, crx + crr, cry + crr], fill=(220, 210, 190, 60))


def draw_porch_roof(draw: ImageDraw, width: int, height: int) -> None:
    """Japanese-style roof overhang (kirizuma-zukuri) for the doll shop."""
    roof_top = int(height * 0.38)
    roof_bottom = int(height * 0.42)
    overhang = 120

    # Roof body
    draw.polygon(
        [
            (0 - overhang, roof_top + 20),
            (width + overhang, roof_top + 20),
            (width + overhang + 60, roof_top),
            (width // 2, roof_top - 60),
            (0 - overhang - 60, roof_top),
        ],
        fill=(50, 30, 25),
    )

    # Roof edge detail
    draw.polygon(
        [
            (0 - overhang, roof_top + 20),
            (width + overhang, roof_top + 20),
            (width + overhang + 60, roof_top),
            (width // 2, roof_top - 60),
            (0 - overhang - 60, roof_top),
        ],
        outline=(70, 45, 35),
        width=2,
    )

    # Darker underside
    draw.rectangle(
        [0 - overhang, roof_top + 20, width + overhang, roof_bottom],
        fill=(35, 20, 15),
    )


def draw_shop_front(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the front of the doll shop with sliding doors and shelves."""
    shop_top = int(height * 0.42)
    shop_bottom = int(height * 0.72)
    shop_left = int(width * 0.1)
    shop_right = int(width * 0.9)

    # Shop wall (warm wood)
    draw.rectangle(
        [shop_left, shop_top, shop_right, shop_bottom],
        fill=(70, 50, 40),
    )

    # Pillars
    pillar_count = 3
    for i in range(pillar_count):
        px = shop_left + (shop_right - shop_left) * (i + 1) // (pillar_count + 1)
        draw.rectangle([px - 8, shop_top, px + 8, shop_bottom], fill=(55, 35, 25))

    # Shoji screens (sliding doors) between pillars
    for i in range(pillar_count + 1):
        sx = shop_left + (shop_right - shop_left) * i // (pillar_count + 1)
        ex = shop_left + (shop_right - shop_left) * (i + 1) // (pillar_count + 1)
        # Shoji frame
        draw.rectangle([sx + 10, shop_top + 10, ex - 10, shop_bottom - 10], fill=(180, 175, 160))
        # Shoji grid
        for gx in range(int(sx + 30), int(ex - 10), 40):
            draw.line([(gx, shop_top + 10), (gx, shop_bottom - 10)], fill=(160, 150, 135), width=2)
        for gy in range(int(shop_top + 40), int(shop_bottom - 10), 60):
            draw.line([(sx + 10, gy), (ex - 10, gy)], fill=(160, 150, 135), width=2)


def draw_doll_shelf(draw: ImageDraw, width: int, height: int) -> None:
    """A shelf of porcelain doll faces visible through the shop window."""
    shelf_top = int(height * 0.48)
    shelf_left = int(width * 0.25)
    shelf_right = int(width * 0.75)

    # Shelf board
    draw.rectangle([shelf_left, shelf_top, shelf_right, shelf_top + 6], fill=(80, 60, 45))
    draw.rectangle([shelf_left, shelf_top + 55, shelf_right, shelf_top + 61], fill=(80, 60, 45))

    # Doll faces on upper shelf
    rng = random.Random(42)
    for i in range(5):
        dx = shelf_left + 60 + i * 130 + rng.randint(-15, 15)
        dy = shelf_top - 50 + rng.randint(-10, 10)
        face_r = 20 + rng.randint(5, 10)

        # Porcelain face shape (ellipse)
        draw.ellipse([dx - face_r, dy - face_r - 5, dx + face_r, dy + face_r + 5], fill=(235, 225, 210))

        # Hair
        draw.arc([dx - face_r - 2, dy - face_r - 20, dx + face_r + 2, dy + face_r], 180, 360, fill=(30, 20, 15), width=6)

        # Eyes (closed or open slits)
        eye_size = 3
        draw.ellipse([dx - 8, dy - 3, dx - 8 + eye_size, dy - 3 + eye_size], fill=(40, 30, 25))
        draw.ellipse([dx + 5, dy - 3, dx + 5 + eye_size, dy - 3 + eye_size], fill=(40, 30, 25))

        # Small mouth
        draw.arc([dx - 5, dy + 8, dx + 5, dy + 15], 0, 180, fill=(120, 60, 50), width=2)

    # Smaller dolls on lower shelf
    for i in range(4):
        dx = shelf_left + 80 + i * 150 + rng.randint(-10, 10)
        dy = shelf_top + 80 + rng.randint(-5, 5)
        face_r = 14 + rng.randint(2, 5)

        draw.ellipse([dx - face_r, dy - face_r - 3, dx + face_r, dy + face_r + 3], fill=(225, 215, 200))
        draw.arc([dx - face_r - 2, dy - face_r - 12, dx + face_r + 2, dy + face_r], 180, 360, fill=(40, 25, 20), width=4)
        draw.ellipse([dx - 5, dy - 2, dx - 5 + 2, dy - 2 + 2], fill=(40, 30, 25))
        draw.ellipse([dx + 3, dy - 2, dx + 3 + 2, dy - 2 + 2], fill=(40, 30, 25))
        draw.arc([dx - 3, dy + 5, dx + 3, dy + 10], 0, 180, fill=(120, 60, 50), width=1)


def draw_garden(draw: ImageDraw, width: int, height: int) -> None:
    """Kyoto garden elements: stone lantern, moss, maple leaves below the shop."""
    garden_top = int(height * 0.72)
    garden_bottom = TITLE_PANEL_TOP

    # Ground / moss
    draw.rectangle([0, garden_top, width, garden_bottom], fill=(100, 120, 70))

    # Stone lantern (toro)
    lx, ly = int(width * 0.25), garden_top + 30
    # Base
    draw.polygon([(lx - 25, ly + 50), (lx + 25, ly + 50), (lx + 20, ly + 40), (lx - 20, ly + 40)], fill=(120, 115, 105))
    # Post
    draw.rectangle([lx - 8, ly + 10, lx + 8, ly + 40], fill=(130, 125, 115))
    # Fire box
    draw.rectangle([lx - 18, ly - 10, lx + 18, ly + 10], fill=(140, 135, 125))
    # Lantern opening (glow)
    draw.rectangle([lx - 10, ly - 5, lx + 10, ly + 5], fill=(255, 200, 100, 180))
    # Roof
    draw.polygon([(lx - 25, ly - 10), (lx + 25, ly - 10), (lx + 15, ly - 22), (lx - 15, ly - 22)], fill=(110, 105, 95))
    # Top finial
    draw.ellipse([lx - 4, ly - 28, lx + 4, ly - 22], fill=(100, 95, 85))

    # Moss patches
    rng = random.Random(33)
    for _ in range(30):
        mx = rng.randint(50, width - 50)
        my = rng.randint(garden_top + 10, garden_bottom - 10)
        mr = rng.randint(10, 30)
        draw.ellipse([mx - mr, my - mr // 2, mx + mr, my + mr // 2], fill=(80, 110, 60, 120))

    # Small maple leaves scattered
    rng = random.Random(101)
    for _ in range(25):
        lx2 = rng.randint(50, width - 50)
        ly2 = rng.randint(garden_top + 20, garden_bottom - 10)
        size = rng.randint(8, 18)
        # Simple leaf shape (star-like polygon)
        draw.polygon(
            [
                (lx2, ly2 - size),
                (lx2 + size // 3, ly2 - size // 3),
                (lx2 + size, ly2 - size // 3),
                (lx2 + size // 2, ly2),
                (lx2 + size * 2 // 3, ly2 + size // 2),
                (lx2, ly2 + size // 4),
                (lx2 - size * 2 // 3, ly2 + size // 2),
                (lx2 - size // 2, ly2),
                (lx2 - size, ly2 - size // 3),
                (lx2 - size // 3, ly2 - size // 3),
            ],
            fill=(180, 60, 30, 150),
        )

    # Small stones on path
    for _ in range(12):
        sx = rng.randint(100, width - 100)
        sy = garden_bottom - rng.randint(20, 50)
        sr = rng.randint(4, 10)
        draw.ellipse([sx - sr, sy - sr // 2, sx + sr, sy + sr // 2], fill=(130, 125, 110))


def draw_cherry_branches(draw: ImageDraw, width: int, height: int) -> None:
    """Cherry blossom branches framing the top and sides."""
    rng = random.Random(55)

    # Top branches
    for b in range(3):
        start_x = (b + 1) * width // 4
        start_y = 0
        points = [(start_x, start_y)]
        segments = 8
        cx, cy = start_x, start_y
        for s in range(segments):
            cx += rng.randint(-20, 30)
            cy += rng.randint(30, 60)
            points.append((cx, cy))
        draw.line(points, fill=(60, 30, 20), width=rng.randint(4, 8))

        # Blossoms along branch
        for px, py in points[2::2]:
            for _ in range(rng.randint(1, 2)):
                bx = px + rng.randint(-10, 10)
                by = py + rng.randint(-5, 10)
                br = rng.randint(5, 10)
                # Pink blossom
                draw.ellipse([bx - br, by - br, bx + br, by + br], fill=(230, 180, 180, 180))
                draw.ellipse([bx - br // 2, by - br // 2, bx + br // 2, by + br // 2], fill=(240, 200, 200, 200))
                # Center
                draw.ellipse([bx - 2, by - 2, bx + 2, by + 2], fill=(200, 100, 100))

    # Side branches
    for side, sx in [(0, 0), (1, width)]:
        points = [(sx, int(height * 0.3))]
        cx, cy = sx, int(height * 0.3)
        for s in range(5):
            cx += (1 if side == 1 else -1) * rng.randint(30, 60)
            cy += rng.randint(40, 80)
            points.append((cx, cy))
        draw.line(points, fill=(50, 25, 15), width=rng.randint(3, 6))
        for px, py in points[1::2]:
            for _ in range(rng.randint(1, 2)):
                bx = px + rng.randint(-8, 8)
                by = py + rng.randint(-5, 10)
                br = rng.randint(4, 8)
                draw.ellipse([bx - br, by - br, bx + br, by + br], fill=(220, 170, 170, 160))
                draw.ellipse([bx - 2, by - 2, bx + 2, by + 2], fill=(200, 90, 90))


def draw_lantern_glow(draw: ImageDraw, width: int, height: int) -> None:
    """Warm glowing lantern light spilling from the shop interior."""
    glow_center_y = int(height * 0.57)
    for radius in range(200, 40, -10):
        alpha = max(0, 25 - (200 - radius) // 8)
        draw.ellipse(
            [width // 2 - radius, glow_center_y - radius, width // 2 + radius, glow_center_y + radius],
            fill=(255, 200, 100, alpha),
        )


def draw_title_panel(draw: ImageDraw, width: int, height: int) -> None:
    """Dark title panel at the bottom with WHITE text for readability."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark semi-transparent
    draw.rectangle([(0, panel_top), (width, height)], fill=(25, 15, 10, 220))

    # Subtle vermillion accent line at top of panel
    draw.line([(0, panel_top), (width, panel_top)], fill=(160, 60, 40), width=3)

    # Decorative geometric line below accent
    for x in range(100, width - 100, 140):
        draw.rectangle([x, panel_top + 10, x + 80, panel_top + 12], fill=(100, 40, 30))

    # Title text - use arialbd.ttf
    font_path = str(FONTS_DIR / "arialbd.ttf")

    title_line1 = "The Porcelain"
    title_line2 = "Doll"
    title_font_size = 80

    try:
        title_font = ImageFont.truetype(font_path, title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw "The Porcelain"
    try:
        bbox1 = draw.textbbox((0, 0), title_line1, font=title_font)
        tw1 = bbox1[2] - bbox1[0]
    except Exception:
        tw1 = 0
    tx1 = (width - tw1) // 2
    draw.text((tx1, panel_top + 40), title_line1, fill=(255, 255, 255), font=title_font)

    # Draw "Doll" - slightly larger
    try:
        bbox2 = draw.textbbox((0, 0), title_line2, font=title_font)
        tw2 = bbox2[2] - bbox2[0]
    except Exception:
        tw2 = 0
    tx2 = (width - tw2) // 2
    draw.text((tx2, panel_top + 130), title_line2, fill=(255, 255, 255), font=title_font)

    # Author name
    author = "Barış Kısır"
    author_font_size = 36
    try:
        author_font = ImageFont.truetype(font_path, author_font_size)
    except Exception:
        author_font = ImageFont.load_default()

    try:
        abbox = draw.textbbox((0, 0), author, font=author_font)
        aw = abbox[2] - abbox[0]
    except Exception:
        aw = 0
    ax = (width - aw) // 2

    # Thin decorative line above author
    draw.line([(width // 2 - 60, panel_top + 200), (width // 2 + 60, panel_top + 200)], fill=(160, 60, 40), width=1)
    draw.text((ax, panel_top + 215), author, fill=(255, 255, 255), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Porcelain Doll")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Moon
    draw_moon(draw, WIDTH, HEIGHT)

    # Step 3: Cherry blossom branches
    draw_cherry_branches(draw, WIDTH, HEIGHT)

    # Step 4: Porch roof
    draw_porch_roof(draw, WIDTH, HEIGHT)

    # Step 5: Shop front
    draw_shop_front(draw, WIDTH, HEIGHT)

    # Step 6: Warm lantern glow
    draw_lantern_glow(draw, WIDTH, HEIGHT)

    # Step 7: Doll faces on shelf
    draw_doll_shelf(draw, WIDTH, HEIGHT)

    # Step 8: Garden
    draw_garden(draw, WIDTH, HEIGHT)

    # Step 9: Title panel (dark, white text)
    draw_title_panel(draw, WIDTH, HEIGHT)

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