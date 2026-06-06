#!/usr/bin/env python3
"""Generate a 1600x2560 cover image for The Night Market."""

import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


def wrap_text(draw, text, font, max_width):
    """Wrap text to fit within max_width."""
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test = current_line + " " + word if current_line else word
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line = test
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines


def create_cover(metadata_path, output_path):
    with open(metadata_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    title = meta["title"]
    author = meta["author"]

    W, H = 1600, 2560

    img = Image.new("RGB", (W, H), (20, 10, 30))
    draw = ImageDraw.Draw(img)

    # Gradient background: deep purple to midnight blue to dark teal
    for y in range(H):
        r = int(20 + (y / H) * 15)
        g = int(5 + (y / H) * 20)
        b = int(40 + (y / H) * 30)
        for x in range(W):
            noise = random.randint(-3, 3)
            draw.point((x, y), fill=(r + noise, g + noise, b + noise))

    # Draw starry sky in upper portion
    random.seed(42)
    star_colors = [(255, 255, 200), (255, 200, 150), (200, 200, 255)]
    for _ in range(300):
        x = random.randint(0, W)
        y = random.randint(0, int(H * 0.5))
        size = random.choice([1, 1, 2, 2, 3])
        color = random.choice(star_colors)
        draw.ellipse([x, y, x + size, y + size], fill=color)
        if size > 1:
            draw.ellipse([x - 1, y - 1, x + size + 1, y + size + 1],
                         fill=(color[0], color[1], color[2], 60))

    # Draw moon
    moon_center = (W // 2, 180)
    moon_radius = 100
    draw.ellipse([
        moon_center[0] - moon_radius, moon_center[1] - moon_radius,
        moon_center[0] + moon_radius, moon_center[1] + moon_radius
    ], fill=(255, 240, 200))
    # Moon glow
    for r in range(moon_radius + 10, moon_radius + 50, 5):
        alpha = max(0, 60 - r)
        draw.ellipse([
            moon_center[0] - r, moon_center[1] - r,
            moon_center[0] + r, moon_center[1] + r
        ], fill=(255, 240, 200, alpha // 10))

    # Draw stall structures
    random.seed(123)
    stall_colors = [(80, 40, 30), (60, 50, 40), (70, 35, 25), (90, 55, 35)]
    for i in range(6):
        sx = 100 + i * 250 + random.randint(-30, 30)
        sy = int(H * 0.35)
        sw = 180 + random.randint(-20, 30)
        sh = 250 + random.randint(-30, 30)

        # Stall post
        post_color = random.choice(stall_colors)
        draw.rectangle([sx, sy, sx + 12, sy + sh], fill=post_color)
        draw.rectangle([sx + sw - 12, sy, sx + sw, sy + sh], fill=post_color)

        # Stall roof
        roof_color = (139, 69, 19)
        draw.polygon([
            (sx - 20, sy),
            (sx + sw + 20, sy),
            (sx + sw + 10, sy - 30),
            (sx - 10, sy - 30)
        ], fill=roof_color)

        # Stall counter
        counter_color = (101, 67, 33)
        draw.rectangle([sx + 12, sy + sh - 40, sx + sw - 12, sy + sh],
                       fill=counter_color)

        # Canopy
        canopy_color = (180, 50, 50) if i % 2 == 0 else (50, 80, 150)
        draw.rectangle([sx, sy + 20, sx + sw, sy + 50], fill=canopy_color)

    # Draw lanterns hanging from strings
    random.seed(456)
    lantern_colors = [(255, 200, 50), (255, 150, 50), (255, 100, 50),
                      (150, 200, 255), (200, 100, 200)]
    for x in range(100, W - 100, 40):
        lantern_y = int(H * 0.32) + random.randint(-10, 10)
        lantern_color = random.choice(lantern_colors)
        # String
        draw.line([x, int(H * 0.28), x, lantern_y], fill=(100, 80, 60), width=1)
        # Lantern body
        lw = 16
        lh = 24
        draw.ellipse([x - lw // 2, lantern_y - 5, x + lw // 2, lantern_y + lh - 5],
                     fill=lantern_color)
        # Glow
        glow_r = 30
        for g in range(glow_r, 0, -5):
            a = int(40 * (1 - g / glow_r))
            draw.ellipse([
                x - g, lantern_y - g,
                x + g, lantern_y + g
            ], fill=(lantern_color[0], lantern_color[1], lantern_color[2], a // 4))

    # Draw mysterious wares on counters
    random.seed(789)
    for i in range(8):
        wx = 140 + i * 200 + random.randint(-20, 20)
        wy = int(H * 0.62) + random.randint(-10, 10)
        # Jars
        jar_color = (100, 200, 255)
        draw.rectangle([wx - 10, wy - 30, wx + 10, wy], fill=(200, 220, 255, 100))
        draw.rectangle([wx - 10, wy - 30, wx + 10, wy], outline=jar_color, width=2)
        # Inner glow
        glow_h = random.randint(5, 20)
        glow_color = random.choice([(255, 200, 100), (200, 255, 200), (255, 150, 150)])
        draw.ellipse([wx - 5, wy - 10 - glow_h, wx + 5, wy - 10], fill=glow_color)

    # Ground/earth boundary
    ground_y = int(H * 0.7)
    for x in range(W):
        noise = random.randint(-3, 3)
        draw.point((x, ground_y + noise), fill=(40, 30, 20))

    # Title panel at bottom
    panel_y1 = int(H * 0.78)
    panel_y2 = H
    for y in range(panel_y1, panel_y2):
        alpha = (y - panel_y1) / (panel_y2 - panel_y1)
        r = int(15 * (1 - alpha) + 10 * alpha)
        g = int(10 * (1 - alpha) + 5 * alpha)
        b = int(25 * (1 - alpha) + 15 * alpha)
        for x in range(W):
            n = random.randint(-2, 2)
            draw.point((x, y), fill=(r + n, g + n, b + n))

    # Border line above panel
    draw.line([(30, panel_y1-3), (W-30, panel_y1-3)], fill=(180, 160, 100), width=2)

    # Load fonts
    font_dirs = [
        "C:/Windows/Fonts",
        "/System/Library/Fonts",
        "/usr/share/fonts/truetype",
    ]

    title_font = None
    author_font = None
    small_font = None

    for fd in font_dirs:
        p = Path(fd)
        if title_font is None:
            tf = p / "georgiab.ttf"
            if tf.exists():
                title_font = ImageFont.truetype(str(tf), 72)
            else:
                tf2 = p / "Georgia Bold.ttf"
                if tf2.exists():
                    title_font = ImageFont.truetype(str(tf2), 72)
        if author_font is None:
            af = p / "arialbd.ttf"
            if af.exists():
                author_font = ImageFont.truetype(str(af), 36)
            else:
                af2 = p / "Arial Bold.ttf"
                if af2.exists():
                    author_font = ImageFont.truetype(str(af2), 36)
        if small_font is None:
            sf = p / "arial.ttf"
            if sf.exists():
                small_font = ImageFont.truetype(str(sf), 20)
            else:
                sf2 = p / "Arial.ttf"
                if sf2.exists():
                    small_font = ImageFont.truetype(str(sf2), 20)

    if title_font is None:
        title_font = ImageFont.load_default()
    if author_font is None:
        author_font = ImageFont.load_default()
    if small_font is None:
        small_font = ImageFont.load_default()

    # Draw title text, wrapped
    max_text_width = W - 100
    title_lines = wrap_text(draw, title, title_font, max_text_width)
    title_y = panel_y1 + 80
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        tw = bbox[2] - bbox[0]
        tx = (W - tw) // 2
        # Title shadow
        draw.text((tx + 2, title_y + 2), line, fill=(0, 0, 0), font=title_font)
        draw.text((tx, title_y), line, fill=(255, 220, 150), font=title_font)
        title_y += bbox[3] - bbox[1] + 10

    # Draw author name
    author_y = panel_y2 - 120
    abox = draw.textbbox((0, 0), author, font=author_font)
    aw = abox[2] - abox[0]
    ax = (W - aw) // 2
    draw.text((ax + 2, author_y + 2), author, fill=(0, 0, 0), font=author_font)
    draw.text((ax, author_y), author, fill=(200, 200, 200), font=author_font)

    # Decorative line above author
    line_y = author_y - 20
    draw.line([(W//2 - 100, line_y), (W//2 + 100, line_y)], fill=(180, 160, 100), width=1)

    output_path.parent.mkdir(parents=True, exist_ok=True)
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
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    create_cover(args.metadata, args.out)


if __name__ == "__main__":
    main()