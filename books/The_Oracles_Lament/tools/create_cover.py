#!/usr/bin/env python3
"""Generate a 1600x2560 PNG book cover for The Oracle's Lament."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


WIDTH, HEIGHT = 1600, 2560
TITLE_PANEL_Y = 1920


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def draw_gradient(draw: ImageDraw, colors: list[tuple[int, int, int]]) -> None:
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        segments = len(colors) - 1
        seg = min(int(ratio * segments), segments - 1)
        local = (ratio * segments) - seg
        r = int(colors[seg][0] * (1 - local) + colors[seg + 1][0] * local)
        g = int(colors[seg][1] * (1 - local) + colors[seg + 1][1] * local)
        b = int(colors[seg][2] * (1 - local) + colors[seg + 1][2] * local)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def draw_wall_block(draw: ImageDraw, x: int, y: int, w: int, h: int, color: tuple[int, int, int]) -> None:
    """Draw a single stone block with slight border."""
    draw.rectangle([x, y, x + w, y + h], fill=color, outline=(0, 0, 0, 60))


def draw_troy_walls(draw: ImageDraw) -> None:
    """Draw Troy's walls with crenellations."""
    base_color = (140, 120, 95)
    highlight = (160, 140, 110)
    shadow = (100, 85, 65)

    # Main wall
    wall_left = 100
    wall_right = 1500
    wall_base = 900
    wall_top = 400

    # Draw wall body with block pattern
    block_w = 120
    block_h = 50
    for row_y in range(wall_top, wall_base, block_h):
        offset = (row_y // block_h) % 2 * 60
        for col_x in range(wall_left + offset, wall_right, block_w * 2):
            color = highlight if (row_y + col_x) % 400 < 200 else base_color
            draw_wall_block(draw, col_x, row_y, block_w, block_h, color)
            draw_wall_block(draw, col_x + block_w, row_y, block_w, block_h, shadow)

    # Crenellations (merlons and crenels)
    merlon_w = 60
    merlon_h = 60
    for mx in range(60, WIDTH - 60, merlon_w * 2):
        for my_offset in [0, merlon_w]:
            mx_pos = mx + my_offset
            if mx_pos < WIDTH - merlon_w:
                draw.rectangle(
                    [mx_pos, wall_top - merlon_h, mx_pos + merlon_w, wall_top],
                    fill=base_color,
                    outline=(0, 0, 0, 40),
                )

    # Gate arch
    gate_center = 800
    gate_width = 300
    gate_height = 350
    arch_top = wall_base - gate_height
    draw.rectangle(
        [gate_center - gate_width // 2, arch_top, gate_center + gate_width // 2, wall_base],
        fill=(30, 25, 20),
    )
    # Arch top
    draw.ellipse(
        [
            gate_center - gate_width // 2,
            arch_top - gate_width // 2,
            gate_center + gate_width // 2,
            arch_top + gate_width // 2,
        ],
        fill=(30, 25, 20),
    )

    # Gate doors
    door_color = (60, 50, 35)
    draw.rectangle(
        [gate_center - 130, arch_top + 20, gate_center - 5, wall_base],
        fill=door_color,
        outline=(40, 35, 25),
    )
    draw.rectangle(
        [gate_center + 5, arch_top + 20, gate_center + 130, wall_base],
        fill=door_color,
        outline=(40, 35, 25),
    )

    # Rivets on doors
    for ry in range(arch_top + 40, wall_base, 60):
        for rx in [-100, 100]:
            draw.ellipse(
                [gate_center + rx - 6, ry - 6, gate_center + rx + 6, ry + 6],
                fill=(100, 85, 55),
            )


def draw_cassandra(draw: ImageDraw) -> None:
    """Draw Cassandra silhouette on the walls."""
    cx, cy = 500, 500

    # Body
    draw.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], fill=(200, 180, 160))  # head

    # Laurel wreath
    wreath_color = (60, 120, 50)
    for angle in range(0, 360, 30):
        import math
        lx = cx + 18 * math.cos(math.radians(angle))
        ly = cy + 18 * math.sin(math.radians(angle))
        draw.ellipse([lx - 4, ly - 4, lx + 4, ly + 4], fill=wreath_color)

    # Dress/torso
    draw.polygon(
        [(cx - 20, cy + 18), (cx + 20, cy + 18), (cx + 25, cy + 90), (cx - 25, cy + 90)],
        fill=(200, 180, 160),
    )

    # Arms raised (prophetic gesture)
    draw.line([(cx - 20, cy + 30), (cx - 50, cy - 20)], fill=(200, 180, 160), width=6)
    draw.line([(cx + 20, cy + 30), (cx + 50, cy - 20)], fill=(200, 180, 160), width=6)


def draw_greek_ships(draw: ImageDraw) -> None:
    """Draw Greek ships on the sea in background."""
    ship_color = (40, 35, 45)
    sail_color = (220, 210, 190)

    for sx, sy, scale in [(200, 150, 1.0), (600, 120, 1.3), (1100, 160, 0.9), (1400, 100, 1.1)]:
        sw = int(120 * scale)
        sh = int(35 * scale)
        # Hull
        draw.polygon(
            [(sx, sy), (sx + sw, sy), (sx + sw - 15, sy + sh), (sx + 15, sy + sh)],
            fill=ship_color,
        )
        # Mast
        draw.line([(sx + sw // 2, sy), (sx + sw // 2, sy - int(80 * scale))], fill=(60, 55, 50), width=4)
        # Sail
        draw.polygon(
            [
                (sx + sw // 2, sy - int(80 * scale)),
                (sx + sw // 2 + int(40 * scale), sy - int(20 * scale)),
                (sx + sw // 2, sy - int(5 * scale)),
            ],
            fill=sail_color,
            outline=(180, 170, 150),
        )
        # Oars
        for o in range(3):
            ox = sx + 20 + o * 30
            draw.line([(ox, sy + sh), (ox + 20, sy + sh + 20)], fill=(80, 70, 60), width=2)


def draw_red_sky(draw: ImageDraw) -> None:
    """Draw a stylized sun and sky glow."""
    # Red sun
    sun_center = (1300, 280)
    sun_radius = 80
    for r in range(sun_radius, 10, -2):
        alpha = int(255 * (1 - r / sun_radius))
        draw.ellipse(
            [sun_center[0] - r, sun_center[1] - r, sun_center[0] + r, sun_center[1] + r],
            fill=(220, 50 + alpha // 3, 20, alpha),
        )

    # Fire glow across the sky
    for y in range(0, 400, 4):
        alpha = max(0, int(60 * (1 - y / 400)))
        draw.line([(0, y), (WIDTH, y)], fill=(200, 40, 20, alpha))


def draw_title_panel(draw: ImageDraw) -> None:
    """Draw the bottom title panel with gradient and centered text."""
    # Light gradient panel from y=1920 to bottom
    panel_color_top = (245, 240, 230)
    panel_color_bot = (220, 210, 195)

    for y in range(TITLE_PANEL_Y, HEIGHT):
        ratio = (y - TITLE_PANEL_Y) / (HEIGHT - TITLE_PANEL_Y)
        r = int(panel_color_top[0] * (1 - ratio) + panel_color_bot[0] * ratio)
        g = int(panel_color_top[1] * (1 - ratio) + panel_color_bot[1] * ratio)
        b = int(panel_color_top[2] * (1 - ratio) + panel_color_bot[2] * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Decorative line at top of panel
    draw.line([(100, TITLE_PANEL_Y + 10), (WIDTH - 100, TITLE_PANEL_Y + 10)], fill=(180, 160, 130), width=2)

    # Title - try georgiab.ttf for bold serif, fall back
    title_text = "The Oracle's\nLament"
    font_size = 95
    try:
        title_font = ImageFont.truetype("C:/Windows/Fonts/georgiab.ttf", font_size)
    except (IOError, OSError):
        title_font = ImageFont.truetype("C:/Windows/Fonts/georgia.ttf", font_size)

    # Draw title centered - handle multiline
    lines = title_text.split("\n")
    total_height = 0
    line_heights = []
    for line in lines:
        bbox = title_font.getbbox(line)
        lh = bbox[3] - bbox[1]
        line_heights.append(lh)
        total_height += lh + 10

    title_y_start = TITLE_PANEL_Y + 350 - total_height // 2
    for i, line in enumerate(lines):
        bbox = title_font.getbbox(line)
        tw = bbox[2] - bbox[0]
        tx = (WIDTH - tw) // 2
        ty = title_y_start + sum(line_heights[:i]) + i * 10
        draw.text((tx, ty), line, fill=(40, 35, 30), font=title_font)

    # Author name
    author_text = "Barış Kısır"
    try:
        author_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 40)
    except (IOError, OSError):
        author_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 40)

    author_y = TITLE_PANEL_Y + 380 + total_height
    bbox = author_font.getbbox(author_text)
    aw = bbox[2] - bbox[0]
    ax = (WIDTH - aw) // 2
    draw.text((ax, author_y), author_text, fill=(80, 70, 60), font=author_font)

    # Genre line
    genre_text = "Mythological Fiction"
    try:
        small_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 24)
    except (IOError, OSError):
        small_font = ImageFont.load_default()

    bbox_s = small_font.getbbox(genre_text)
    gw = bbox_s[2] - bbox_s[0]
    gx = (WIDTH - gw) // 2
    gy = author_y + 50
    draw.text((gx, gy), genre_text, fill=(120, 110, 95), font=small_font)


def create_cover() -> Image.Image:
    """Create the full cover image."""
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # 1. Gradient background: dark red -> orange -> dark
    draw_gradient(draw, [(50, 15, 10), (120, 30, 20), (180, 60, 30), (100, 40, 25)])

    # 2. Red sky glow
    draw_red_sky(draw)

    # 3. Greek ships on the sea
    draw_greek_ships(draw)

    # 4. Troy walls
    draw_troy_walls(draw)

    # 5. Cassandra on the wall
    draw_cassandra(draw)

    # 6. Title panel at bottom
    draw_title_panel(draw)

    # Soft sharpen filter for print-like quality
    img = img.filter(ImageFilter.SMOOTH)

    return img



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

    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    output_path = args.out

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cover = create_cover()
    _draw_standard_cover_title_panel(cover, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()))
    cover.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")


if __name__ == "__main__":
    main()