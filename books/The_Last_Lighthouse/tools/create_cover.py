#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Last Lighthouse."""

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
    """Steel gray to storm dark gradient for dystopian coastal feel."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((180, 185, 190), (120, 125, 130), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((120, 125, 130), (60, 65, 70), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((60, 65, 70), (15, 18, 22), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_sea(draw: ImageDraw, width: int, height: int) -> None:
    """Draw rough sea with whitecaps at the base of the lighthouse."""
    sea_top = int(height * 0.65)
    rng = random.Random(13)

    for y in range(sea_top, height):
        t = (y - sea_top) / (height - sea_top)
        if t < 0.3:
            c = lerp_color((40, 45, 55), (25, 30, 40), t / 0.3)
        else:
            c = lerp_color((25, 30, 40), (10, 12, 18), (t - 0.3) / 0.7)
        draw.line([(0, y), (width, y)], fill=c)

    # Whitecaps
    for _ in range(60):
        wx = rng.randint(0, width)
        wy = sea_top + rng.randint(0, int(height * 0.25))
        wlen = rng.randint(10, 40)
        wh = rng.randint(1, 3)
        draw.line([(wx, wy), (wx + wlen, wy)], fill=(220, 225, 230, 120), width=wh)

    # Foam line at shore
    shore_y = int(height * 0.62)
    for i in range(width):
        offset = int(math.sin(i * 0.05) * 3 + math.sin(i * 0.02) * 5)
        draw.line(
            [(i, shore_y + offset), (i, shore_y + offset + rng.randint(2, 5))],
            fill=(240, 245, 250, 100),
        )


def draw_lighthouse(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the lighthouse standing against the storm."""
    base_x = width // 2
    base_y = int(height * 0.68)
    tower_w = 60
    tower_h = int(height * 0.55)
    top_y = base_y - tower_h

    # Main tower body (slightly tapered)
    for y in range(top_y, base_y):
        t = (y - top_y) / tower_h
        tw = int(tower_w * (1 - t * 0.3))
        x1 = base_x - tw // 2
        x2 = base_x + tw // 2
        # Shadow side
        shade = int(40 * t)
        color = (180 - shade, 185 - shade, 190 - shade)
        draw.line([(x1, y), (x2, y)], fill=color)

    # Red stripes on lighthouse
    stripe_y = base_y - int(tower_h * 0.25)
    stripe_h = int(tower_h * 0.06)
    for s in range(3):
        sy = stripe_y - s * int(tower_h * 0.18)
        t = (sy - top_y) / tower_h
        tw = int(tower_w * (1 - t * 0.3))
        x1 = base_x - tw // 2
        x2 = base_x + tw // 2
        for y in range(sy, sy + stripe_h):
            draw.line([(x1, y), (x2, y)], fill=(160, 40, 40))

    # Lantern room
    lantern_top = top_y - int(height * 0.03)
    lantern_bottom = top_y
    lantern_w = int(tower_w * 0.8)
    for y in range(lantern_top, lantern_bottom):
        x1 = base_x - lantern_w // 2
        x2 = base_x + lantern_w // 2
        draw.line([(x1, y), (x2, y)], fill=(40, 42, 45))

    # Lantern glass (glowing)
    glass_top = lantern_top + int(height * 0.01)
    glass_bottom = lantern_bottom - int(height * 0.005)
    glass_w = int(lantern_w * 0.6)
    for y in range(glass_top, glass_bottom):
        x1 = base_x - glass_w // 2
        x2 = base_x + glass_w // 2
        glow = random.randint(200, 255)
        draw.line([(x1, y), (x2, y)], fill=(glow, glow - 40, 50, 200))

    # Light beam (triangle extending right)
    beam_center = (glass_top + glass_bottom) // 2
    beam_points = [
        (base_x + glass_w // 2, beam_center - 5),
        (base_x + glass_w // 2, beam_center + 5),
        (width + 100, beam_center - int(height * 0.3)),
        (width + 100, beam_center + int(height * 0.3)),
    ]
    draw.polygon(beam_points, fill=(255, 220, 100, 30))

    # Second beam to left
    beam_points2 = [
        (base_x - glass_w // 2, beam_center - 5),
        (base_x - glass_w // 2, beam_center + 5),
        (-100, beam_center - int(height * 0.2)),
        (-100, beam_center + int(height * 0.2)),
    ]
    draw.polygon(beam_points2, fill=(255, 220, 100, 20))

    # Lighthouse base/platform
    for y in range(base_y, base_y + int(height * 0.02)):
        x1 = base_x - int(tower_w * 0.6)
        x2 = base_x + int(tower_w * 0.6)
        draw.line([(x1, y), (x2, y)], fill=(50, 52, 55))


def draw_storm_clouds(draw: ImageDraw, width: int, height: int) -> None:
    """Draw storm clouds gathering above the lighthouse."""
    rng = random.Random(17)
    for _ in range(40):
        cx = rng.randint(0, width)
        cy = rng.randint(0, int(height * 0.25))
        rx = rng.randint(100, 300)
        ry = rng.randint(30, 80)
        shade = rng.randint(30, 80)
        draw.ellipse(
            [cx - rx, cy - ry, cx + rx, cy + ry],
            fill=(shade, shade + 5, shade + 10, 150),
        )

    # Lightning bolt
    lx = rng.randint(width // 3, width * 2 // 3)
    ly = rng.randint(0, int(height * 0.15))
    points = [(lx, ly)]
    for i in range(6):
        lx += rng.randint(-30, 30)
        ly += rng.randint(30, 80)
        points.append((lx, ly))
    draw.line(points, fill=(255, 255, 200), width=3)
    # Glow around lightning
    draw.line(points, fill=(255, 255, 200, 60), width=8)


def draw_rising_water(draw: ImageDraw, width: int, height: int) -> None:
    """Draw submerged structures — rooftops, poles — emerging from the water."""
    rng = random.Random(23)

    # Submerged rooftops
    for _ in range(5):
        rx = rng.randint(100, width - 100)
        ry = int(height * 0.62) + rng.randint(-20, 30)
        rw = rng.randint(40, 80)
        draw.polygon(
            [(rx - rw // 2, ry), (rx, ry - 20), (rx + rw // 2, ry)],
            fill=(50, 45, 40, 120),
        )
        draw.rectangle([rx - rw // 4, ry, rx + rw // 4, ry + 10], fill=(50, 45, 40, 120))

    # Sunken telephone poles
    for _ in range(3):
        px = rng.randint(80, width - 80)
        py = int(height * 0.65) + rng.randint(-10, 20)
        draw.line(
            [(px, py), (px, py - rng.randint(30, 60))],
            fill=(40, 35, 30),
            width=4,
        )

    # Cross arm on pole
    for _ in range(2):
        px = rng.randint(80, width - 80)
        py = int(height * 0.62) + rng.randint(-10, 10)
        if rng.random() < 0.5:
            draw.line(
                [(px - 15, py), (px + 15, py)],
                fill=(40, 35, 30),
                width=3,
            )


def draw_lone_figure(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a small lone figure on the rocks at the base of the lighthouse."""
    fig_x = width // 2 - 100
    fig_y = int(height * 0.65)

    # Body
    draw.ellipse([fig_x - 8, fig_y - 20, fig_x + 8, fig_y + 10], fill=(15, 15, 18))
    # Head
    draw.ellipse([fig_x - 5, fig_y - 28, fig_x + 5, fig_y - 18], fill=(25, 25, 30))
    # Coat
    draw.polygon(
        [(fig_x - 8, fig_y - 5), (fig_x - 12, fig_y + 15), (fig_x + 12, fig_y + 15), (fig_x + 8, fig_y - 5)],
        fill=(20, 20, 25),
    )


def draw_rocks(draw: ImageDraw, width: int, height: int) -> None:
    """Draw rocky shoreline at the base of the lighthouse."""
    rng = random.Random(31)
    shore_y = int(height * 0.62)
    for _ in range(30):
        rx = rng.randint(100, width - 100)
        ry = shore_y + rng.randint(-5, 20)
        rw = rng.randint(15, 50)
        rh = rng.randint(10, 25)
        shade = rng.randint(40, 80)
        draw.ellipse([rx - rw // 2, ry, rx + rw // 2, ry + rh], fill=(shade, shade + 2, shade + 5))


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom of the cover with white text."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark semi-transparent
    for y in range(panel_top, height):
        t = (y - panel_top) / (height - panel_top)
        shade = int(15 + t * 10)
        draw.line([(0, y), (width, y)], fill=(shade, shade + 1, shade + 3, 240))

    # Top border line
    for i in range(3):
        draw.line([(0, panel_top + i), (width, panel_top + i)], fill=(100, 110, 120, 200), width=1)

    # Title text
    title = "The Last\nLighthouse"
    title_font_size = 80
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered in white
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

    # Subtitle text
    subtitle = "A Dystopian Survival Novel"
    subtitle_font_size = 26
    try:
        subtitle_font = ImageFont.truetype(str(font_paths["small"]), subtitle_font_size)
    except Exception:
        subtitle_font = ImageFont.load_default()

    try:
        sbbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        sw = sbbox[2] - sbbox[0]
    except Exception:
        sw = 0
    sx = (width - sw) // 2
    draw.text((sx, y_offset + 10), subtitle, fill=(180, 185, 190), font=subtitle_font)

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
    ay = y_offset + 70
    draw.text((ax, ay), author, fill=(200, 205, 210), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Last Lighthouse")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Storm clouds
    draw_storm_clouds(draw, WIDTH, HEIGHT)

    # Step 3: Sea and rising water
    draw_sea(draw, WIDTH, HEIGHT)

    # Step 4: Submerged structures
    draw_rising_water(draw, WIDTH, HEIGHT)

    # Step 5: Rocky shore
    draw_rocks(draw, WIDTH, HEIGHT)

    # Step 6: Lighthouse
    draw_lighthouse(draw, WIDTH, HEIGHT)

    # Step 7: Lone figure
    draw_lone_figure(draw, WIDTH, HEIGHT)

    # Step 8: Title panel
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