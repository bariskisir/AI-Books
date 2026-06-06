#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Crimson Waste."""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


WIDTH = 1600
HEIGHT = 2560
TITLE_PANEL_Y = 1920


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype(path, size)
    except (IOError, OSError):
        return ImageFont.load_default()


def draw_gradient_bg(draw: ImageDraw.ImageDraw) -> None:
    """Draw a fiery desert gradient: deep crimson to tan to dark brown."""
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        if ratio < 0.5:
            # Upper half: dark crimson to fiery red
            r = int(180 + (ratio * 2) * 75)
            g = int(15 + (ratio * 2) * 25)
            b = int(15 + (ratio * 2) * 10)
        elif ratio < 0.75:
            # Upper-mid: fiery red to orange-tan
            r = int(255 - ((ratio - 0.5) * 4) * 30)
            g = int(40 + ((ratio - 0.5) * 4) * 80)
            b = int(20 + ((ratio - 0.5) * 4) * 15)
        else:
            # Lower: orange-tan to dark brown
            r = int(220 - ((ratio - 0.75) * 4) * 60)
            g = int(120 - ((ratio - 0.75) * 4) * 40)
            b = int(35 - ((ratio - 0.75) * 4) * 10)
        draw.line([(0, y), (WIDTH, y)], fill=(min(255, max(0, r)), min(255, max(0, g)), min(255, max(0, b))))


def draw_sun(draw: ImageDraw.ImageDraw) -> None:
    """Draw a red sun with corona effect."""
    cx, cy = 800, 300
    # Outer corona
    for r in range(300, 50, -10):
        alpha = max(5, 200 - r)
        draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            fill=(220, 60, 30, alpha)
        )
    # Sun disc
    draw.ellipse([cx - 80, cy - 80, cx + 80, cy + 80], fill=(255, 120, 50, 220))
    draw.ellipse([cx - 60, cy - 60, cx + 60, cy + 60], fill=(255, 180, 80, 240))
    draw.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=(255, 220, 150, 255))


def draw_dunes(draw: ImageDraw.ImageDraw) -> None:
    """Draw layered sand dune silhouettes."""
    layers = [
        (1400, (120, 35, 25, 200)),
        (1550, (140, 45, 30, 180)),
        (1700, (160, 55, 35, 160)),
        (1850, (100, 30, 20, 150)),
    ]
    for base_y, color in layers:
        points = [(0, base_y)]
        for x in range(0, WIDTH + 50, 50):
            offset_y = math.sin(x / 200 + base_y / 100) * 40 + math.sin(x / 80) * 15
            points.append((x, base_y + offset_y))
        points.append((WIDTH, HEIGHT))
        points.append((0, HEIGHT))
        draw.polygon(points, fill=color)


def draw_sword_silhouette(draw: ImageDraw.ImageDraw) -> None:
    """Draw a sword silhouette driven into the sand."""
    # Center the sword
    base_x, base_y = 800, 1400
    # Blade
    blade_points = [
        (base_x - 5, base_y - 300),
        (base_x - 3, base_y - 120),
        (base_x - 8, base_y - 100),
        (base_x - 8, base_y - 80),
        (base_x - 3, base_y - 60),
        (base_x - 3, base_y + 20),
        (base_x + 3, base_y + 20),
        (base_x + 3, base_y - 60),
        (base_x + 8, base_y - 80),
        (base_x + 8, base_y - 100),
        (base_x + 3, base_y - 120),
        (base_x + 5, base_y - 300),
    ]
    draw.polygon(blade_points, fill=(15, 10, 5, 230))

    # Crossguard
    draw.rectangle([base_x - 40, base_y - 105, base_x + 40, base_y - 80], fill=(15, 10, 5, 230))

    # Grip
    draw.rectangle([base_x - 4, base_y - 80, base_x + 4, base_y + 40], fill=(15, 10, 5, 230))

    # Pommel
    draw.ellipse([base_x - 8, base_y + 35, base_x + 8, base_y + 55], fill=(15, 10, 5, 230))

    # Glowing rune on blade (faint red)
    draw.text((base_x - 4, base_y - 220), "◆", fill=(200, 50, 30, 120), font=load_font("C:/Windows/Fonts/arial.ttf", 40))


def draw_monstrous_shape(draw: ImageDraw.ImageDraw) -> None:
    """Draw a demon/shadow shape emerging from the sand."""
    cx, cy = 400, 1100

    # Body - amorphous shadow shape
    shadow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)

    # Main body mass
    body_points = []
    for angle in range(0, 360, 15):
        rad = math.radians(angle)
        r = 80 + math.sin(angle * 3) * 30 + math.cos(angle * 2) * 20
        px = cx + math.cos(rad) * r
        py = cy + math.sin(rad) * r * 0.8
        body_points.append((px, py))
    shadow_draw.polygon(body_points, fill=(40, 10, 15, 200))

    # Extended tendrils/claws
    tendrils = [
        (cx - 100, cy + 20, cx - 200, cy - 50),
        (cx + 80, cy - 40, cx + 180, cy - 120),
        (cx - 50, cy - 80, cx - 150, cy - 160),
        (cx + 60, cy + 50, cx + 160, cy + 30),
    ]
    for sx, sy, ex, ey in tendrils:
        shadow_draw.line([(sx, sy), (ex, ey)], fill=(50, 15, 20, 180), width=8)
        shadow_draw.ellipse([ex - 10, ey - 10, ex + 10, ey + 10], fill=(60, 20, 25, 200))

    # Eye glows
    eye_color = (200, 40, 30, 220)
    shadow_draw.ellipse([cx - 25, cy - 30, cx - 5, cy - 10], fill=eye_color)
    shadow_draw.ellipse([cx + 5, cy - 30, cx + 25, cy - 10], fill=eye_color)
    # Pupils
    shadow_draw.ellipse([cx - 18, cy - 22, cx - 12, cy - 16], fill=(255, 200, 100, 240))
    shadow_draw.ellipse([cx + 12, cy - 22, cx + 18, cy - 16], fill=(255, 200, 100, 240))

    # Mouth slit
    shadow_draw.arc(
        [cx - 30, cy, cx + 30, cy + 25],
        start=200, end=340,
        fill=(60, 15, 20, 220),
        width=4,
    )

    # Blend shadow layers
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=3))
    draw.bitmap((0, 0), shadow, fill=None)


def draw_crimson_sand_foreground(draw: ImageDraw.ImageDraw) -> None:
    """Draw red sand texture in the lower scene area."""
    random.seed(42)
    for _ in range(200):
        x = random.randint(0, WIDTH)
        y = random.randint(900, 1900)
        size = random.randint(2, 8)
        alpha = random.randint(30, 80)
        r = random.randint(90, 160) + random.randint(0, 40)
        g = random.randint(25, 50)
        b = random.randint(15, 30)
        draw.ellipse([x, y, x + size, y + size], fill=(r, g, b, alpha))


def draw_scattered_bones(draw: ImageDraw.ImageDraw) -> None:
    """Draw small bone fragments in the sand."""
    random.seed(123)
    for _ in range(15):
        x = random.randint(200, 1400)
        y = random.randint(1000, 1600)
        angle = random.randint(0, 360)
        length = random.randint(15, 40)
        ex = x + int(math.cos(math.radians(angle)) * length)
        ey = y + int(math.sin(math.radians(angle)) * length)
        draw.line([(x, y), (ex, ey)], fill=(200, 190, 170, 120), width=3)
        # Knob at end
        draw.ellipse([ex - 4, ey - 4, ex + 4, ey + 4], fill=(210, 200, 180, 150))


def draw_title_panel(draw: ImageDraw.ImageDraw, title: str, author: str) -> None:
    """Draw the bottom title panel area."""
    # Light rectangle panel
    draw.rectangle([0, TITLE_PANEL_Y, WIDTH, HEIGHT], fill=(220, 218, 210))
    # Subtle border line at top
    draw.rectangle([0, TITLE_PANEL_Y, WIDTH, TITLE_PANEL_Y + 3], fill=(180, 175, 165))

    title_font = load_font("C:/Windows/Fonts/georgiab.ttf", 68)
    author_font = load_font("C:/Windows/Fonts/arialbd.ttf", 32)
    small_font = load_font("C:/Windows/Fonts/arial.ttf", 20)

    # Title - wrap if too wide
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_w = title_bbox[2] - title_bbox[0]
    if title_w > WIDTH - 100:
        # Split into two lines
        words = title.split()
        mid = len(words) // 2
        line1 = " ".join(words[:mid])
        line2 = " ".join(words[mid:])

        line1_font = load_font("C:/Windows/Fonts/georgiab.ttf", 56)
        line2_font = load_font("C:/Windows/Fonts/georgiab.ttf", 56)

        bbox1 = draw.textbbox((0, 0), line1, font=line1_font)
        line1_w = bbox1[2] - bbox1[0]
        draw.text(((WIDTH - line1_w) // 2, TITLE_PANEL_Y + 40), line1, fill=(40, 35, 30), font=line1_font)

        bbox2 = draw.textbbox((0, 0), line2, font=line2_font)
        line2_w = bbox2[2] - bbox2[0]
        draw.text(((WIDTH - line2_w) // 2, TITLE_PANEL_Y + 110), line2, fill=(40, 35, 30), font=line2_font)

        author_y = TITLE_PANEL_Y + 200
    else:
        draw.text(((WIDTH - title_w) // 2, TITLE_PANEL_Y + 60), title, fill=(40, 35, 30), font=title_font)
        author_y = TITLE_PANEL_Y + 200

    # Author
    author_bbox = draw.textbbox((0, 0), author, font=author_font)
    author_w = author_bbox[2] - author_bbox[0]
    draw.text(((WIDTH - author_w) // 2, author_y), author, fill=(100, 95, 85), font=author_font)

    # Genre label at very bottom
    genre_text = "Sword and Sorcery"
    genre_bbox = draw.textbbox((0, 0), genre_text, font=small_font)
    genre_w = genre_bbox[2] - genre_bbox[0]
    draw.text(((WIDTH - genre_w) // 2, TITLE_PANEL_Y + 500), genre_text, fill=(150, 145, 135), font=small_font)



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

    with open(args.metadata, encoding="utf-8") as f:
        meta = json.load(f)

    title = meta.get("title", "The Crimson Waste")
    author = meta.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, "RGBA")

    # Background gradient
    draw_gradient_bg(draw)

    # Sun and sky effects
    draw_sun(draw)

    # Dune layers
    draw_dunes(draw)

    # Monstrous shadow emerging from sand
    draw_monstrous_shape(draw)

    # Sword silhouette
    draw_sword_silhouette(draw)

    # Sand texture details
    draw_crimson_sand_foreground(draw)

    # Scattered bones
    draw_scattered_bones(draw)

    # Overall atmospheric blur on scene elements
    scene_layer = img.filter(ImageFilter.GaussianBlur(radius=1))

    # Re-draw key elements sharp on top
    draw = ImageDraw.Draw(scene_layer, "RGBA")
    draw_sword_silhouette(draw)
    draw_monstrous_shape(draw)
    draw_sun(draw)
    draw_crimson_sand_foreground(draw)
    draw_scattered_bones(draw)

    # Title panel - drawn sharp on blurred scene
    draw_title_panel(draw, title, author)

    # Convert to RGB and save
    rgb_img = scene_layer.convert("RGB")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(rgb_img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()))
    rgb_img.save(args.out, "PNG")
    print(f"Cover saved to {args.out}")


if __name__ == "__main__":
    main()