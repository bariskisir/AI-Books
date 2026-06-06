#!/usr/bin/env python3
"""Generate the cover image for The Star-Crossed Engine."""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


WIDTH = 1600
HEIGHT = 2560

FONT_DIR = Path("C:/Windows/Fonts")
TITLE_FONT = str(FONT_DIR / "georgiab.ttf")
AUTHOR_FONT = str(FONT_DIR / "arialbd.ttf")
SMALL_FONT = str(FONT_DIR / "arial.ttf")

random.seed(42)


def lerp_color(c1: tuple[int, ...], c2: tuple[int, ...], t: float) -> tuple[int, ...]:
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def draw_gradient(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a warm metallic gradient from dark bronze to copper to brass."""
    top = (25, 15, 10)        # near-black bronze
    mid = (120, 60, 25)       # copper
    bottom = (180, 130, 60)   # brass
    for y in range(height):
        if y < height * 0.5:
            t = y / (height * 0.5)
            c = lerp_color(top, mid, t)
        else:
            t = (y - height * 0.5) / (height * 0.5)
            c = lerp_color(mid, bottom, t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_gears(draw: ImageDraw, width: int, height: int) -> None:
    """Decorative gears in the upper background."""
    gear_specs = [
        (200, 300, 80, 30),
        (400, 500, 60, 22),
        (1100, 350, 100, 35),
        (1300, 600, 70, 25),
        (700, 200, 50, 18),
        (300, 700, 45, 16),
        (1200, 800, 55, 20),
    ]
    for cx, cy, radius, teeth_count in gear_specs:
        draw_gear(draw, cx, cy, radius, teeth_count)


def draw_gear(draw: ImageDraw, cx: int, cy: int, radius: int, teeth: int) -> None:
    """Draw a single gear with teeth."""
    inner_r = int(radius * 0.7)
    color = (140 + random.randint(-20, 20), 90 + random.randint(-20, 20), 30 + random.randint(-10, 10))
    outline = (100, 60, 20)

    # Draw teeth
    for i in range(teeth):
        angle = (2 * math.pi / teeth) * i
        next_angle = (2 * math.pi / teeth) * (i + 0.4)
        x1 = cx + int(radius * math.cos(angle))
        y1 = cy + int(radius * math.sin(angle))
        x2 = cx + int(radius * math.cos(next_angle))
        y2 = cy + int(radius * math.sin(next_angle))
        x1i = cx + int(inner_r * math.cos(angle))
        y1i = cy + int(inner_r * math.sin(angle))
        x2i = cx + int(inner_r * math.cos(next_angle))
        y2i = cy + int(inner_r * math.sin(next_angle))
        draw.polygon([(x1, y1), (x2, y2), (x2i, y2i), (x1i, y1i)], fill=color, outline=outline)

    # Draw main body
    draw.ellipse(
        [cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r],
        fill=color,
        outline=outline,
    )
    # Center hole
    hole_r = int(radius * 0.2)
    draw.ellipse(
        [cx - hole_r, cy - hole_r, cx + hole_r, cy + hole_r],
        fill=(25, 15, 10),
    )
    # Spokes
    for i in range(4):
        angle = (math.pi / 2) * i
        rx = int(inner_r * 0.7 * math.cos(angle))
        ry = int(inner_r * 0.7 * math.sin(angle))
        draw.line(
            [cx, cy, cx + rx, cy + ry],
            fill=outline, width=3,
        )


def draw_airship(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a dirigible/airship in the sky."""
    cx, cy = width // 2, height // 3

    # Envelope (gas bag)
    envelope_color = (160, 100, 40, 180)
    envelope = [
        (cx - 300, cy - 40),
        (cx - 250, cy - 120),
        (cx - 100, cy - 160),
        (cx + 100, cy - 160),
        (cx + 250, cy - 120),
        (cx + 300, cy - 40),
        (cx + 250, cy + 10),
        (cx + 100, cy + 30),
        (cx - 100, cy + 30),
        (cx - 250, cy + 10),
    ]
    draw.polygon(envelope, fill=(140, 85, 35), outline=(180, 130, 60))
    # Envelope highlight
    highlight = [
        (cx - 200, cy - 60),
        (cx - 150, cy - 100),
        (cx + 150, cy - 100),
        (cx + 200, cy - 60),
        (cx + 150, cy - 80),
        (cx - 150, cy - 80),
    ]
    draw.polygon(highlight, fill=(180, 130, 60), outline=None)

    # Gondola
    draw.rectangle(
        [cx - 120, cy + 30, cx + 120, cy + 70],
        fill=(100, 60, 25),
        outline=(180, 130, 60),
    )
    # Gondola windows
    for wx in [cx - 80, cx - 40, cx, cx + 40, cx + 80]:
        draw.ellipse([wx - 10, cy + 35, wx + 10, cy + 55], fill=(200, 180, 100))

    # Rigging lines
    for rlx, rly in [(cx - 250, cy - 20), (cx + 250, cy - 20)]:
        draw.line([(rlx, rly), (rlx, cy + 30)], fill=(100, 70, 30), width=2)
    draw.line([(cx - 120, cy + 30), (cx - 250, cy - 20)], fill=(100, 70, 30), width=2)
    draw.line([(cx + 120, cy + 30), (cx + 250, cy - 20)], fill=(100, 70, 30), width=2)

    # Fins
    fin_color = (120, 75, 30)
    draw.polygon(
        [(cx - 300, cy - 40), (cx - 350, cy - 80), (cx - 300, cy - 20)],
        fill=fin_color,
    )
    draw.polygon(
        [(cx + 300, cy - 40), (cx + 350, cy - 80), (cx + 300, cy - 20)],
        fill=fin_color,
    )


def draw_victorian_city(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a Victorian/steampunk city skyline at the lower portion of the image."""
    base_y = int(height * 0.62)
    buildings = [
        (50, base_y - 200, 110, base_y),
        (110, base_y - 320, 170, base_y),
        (170, base_y - 180, 230, base_y),
        (240, base_y - 280, 310, base_y),
        (310, base_y - 350, 370, base_y),
        (370, base_y - 220, 430, base_y),
        (440, base_y - 300, 500, base_y),
        (500, base_y - 160, 560, base_y),
        (570, base_y - 340, 640, base_y),
        (640, base_y - 250, 700, base_y),
        (700, base_y - 380, 770, base_y),
        (770, base_y - 200, 830, base_y),
        (840, base_y - 310, 900, base_y),
        (900, base_y - 260, 960, base_y),
        (960, base_y - 340, 1020, base_y),
        (1020, base_y - 190, 1080, base_y),
        (1090, base_y - 320, 1150, base_y),
        (1150, base_y - 250, 1210, base_y),
        (1210, base_y - 300, 1270, base_y),
        (1270, base_y - 200, 1330, base_y),
        (1340, base_y - 330, 1400, base_y),
        (1400, base_y - 240, 1460, base_y),
        (1460, base_y - 180, 1550, base_y),
    ]

    for x1, y1, x2, y2 in buildings:
        h = y2 - y1
        # Darken toward base
        brightness = max(40, 120 - h // 3)
        bricktone = (brightness, brightness - 20, brightness - 40)
        draw.rectangle([x1, y1, x2, y2], fill=bricktone, outline=(60, 40, 20))
        # Windows
        for wx in range(x1 + 8, x2 - 5, 18):
            for wy in range(y1 + 8, y2 - 5, 20):
                lit = random.random() > 0.4
                if lit:
                    winc = (220, 190, 100)
                else:
                    winc = (40, 35, 20)
                draw.rectangle([wx, wy, wx + 7, wy + 10], fill=winc)
        # Clock tower accents
        if (x2 - x1) > 60:
            draw.rectangle([x1 + (x2 - x1) // 2 - 5, y1 - 10, x1 + (x2 - x1) // 2 + 5, y1], fill=(80, 60, 30))
            draw.ellipse(
                [x1 + (x2 - x1) // 2 - 6, y1 - 6, x1 + (x2 - x1) // 2 + 6, y1 + 6],
                fill=(200, 180, 80),
            )

    # Steam plumes from chimneys
    for sx, sy in [(100, base_y - 320), (350, base_y - 350), (650, base_y - 380), (950, base_y - 340), (1250, base_y - 330)]:
        for r in range(10, 60, 10):
            alpha = max(20, 80 - r * 2)
            steam_color = (180, 160, 140, alpha)
            steam = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
            sdraw = ImageDraw.Draw(steam)
            sdraw.ellipse(
                [sx - r, sy - r - 40, sx + r, sy - r + 20],
                fill=steam_color,
            )
            draw.bitmap((0, 0), steam, fill=None)


def draw_title_panel(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the title panel at the bottom."""
    panel_top = int(height * 0.75)
    # Light rectangle panel
    draw.rectangle(
        [0, panel_top, width, height],
        fill=(230, 215, 185),
        outline=(180, 150, 100),
    )
    # Inner border
    draw.rectangle(
        [20, panel_top + 20, width - 20, height - 20],
        fill=None,
        outline=(160, 130, 80),
        width=2,
    )

    # Title text
    try:
        title_font = ImageFont.truetype(TITLE_FONT, 72)
    except (IOError, OSError):
        title_font = ImageFont.load_default()

    title = "The Star-Crossed"
    subtitle = "Engine"

    # Center title
    bbox1 = draw.textbbox((0, 0), title, font=title_font)
    tw1 = bbox1[2] - bbox1[0]
    tx = (width - tw1) // 2
    ty = panel_top + 80
    draw.text((tx, ty), title, fill=(40, 25, 10), font=title_font)

    bbox2 = draw.textbbox((0, 0), subtitle, font=title_font)
    tw2 = bbox2[2] - bbox2[0]
    tx = (width - tw2) // 2
    ty = ty + 90
    draw.text((tx, ty), subtitle, fill=(40, 25, 10), font=title_font)

    # Author name
    try:
        author_font = ImageFont.truetype(AUTHOR_FONT, 36)
    except (IOError, OSError):
        author_font = ImageFont.load_default()

    author_text = "Barış Kısır"
    bbox3 = draw.textbbox((0, 0), author_text, font=author_font)
    aw = bbox3[2] - bbox3[0]
    ax = (width - aw) // 2
    ay = ty + 110
    draw.text((ax, ay), author_text, fill=(100, 70, 30), font=author_font)

    # Genre line
    try:
        small_font = ImageFont.truetype(SMALL_FONT, 20)
    except (IOError, OSError):
        small_font = ImageFont.load_default()

    genre_text = "A Steampunk Novel"
    bbox4 = draw.textbbox((0, 0), genre_text, font=small_font)
    gw = bbox4[2] - bbox4[0]
    gx = (width - gw) // 2
    gy = ay + 55
    draw.text((gx, gy), genre_text, fill=(130, 100, 60), font=small_font)


def generate_cover(output_path: Path) -> None:
    """Generate the full cover image."""
    img = Image.new("RGBA", (WIDTH, HEIGHT), (25, 15, 10, 255))
    draw = ImageDraw.Draw(img)

    draw_gradient(draw, WIDTH, HEIGHT)
    draw_gears(draw, WIDTH, HEIGHT)
    draw_victorian_city(draw, WIDTH, HEIGHT)
    draw_airship(draw, WIDTH, HEIGHT)
    draw_title_panel(draw, WIDTH, HEIGHT)

    # Soft vignette
    vignette = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(vignette)
    for r in range(WIDTH // 2, 0, -1):
        alpha = int(80 * (1 - r / (WIDTH // 2)))
        vdraw.ellipse(
            [WIDTH // 2 - r, HEIGHT // 2 - r, WIDTH // 2 + r, HEIGHT // 2 + r],
            outline=(0, 0, 0, alpha),
        )
    img = Image.alpha_composite(img, vignette)

    # Convert to RGB for output
    rgb_img = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
    rgb_img.paste(img, mask=img.split()[3])
    _draw_standard_cover_title_panel(rgb_img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()))
    rgb_img.save(output_path, "PNG")
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
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    # Read metadata (for validation, but we use hardcoded design)
    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    print(f"Generating cover for: {metadata['title']}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    generate_cover(args.out)


if __name__ == "__main__":
    main()