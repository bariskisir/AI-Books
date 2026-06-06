#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Winter Garden."""

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
    """Dove gray to winter blue gradient for the winter garden feel."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((180, 185, 190), (140, 155, 170), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((140, 155, 170), (100, 120, 140), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((100, 120, 140), (60, 75, 90), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_garden_wall(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a brick wall across the mid-section of the cover."""
    wall_y = int(height * 0.35)
    wall_h = 160

    # Wall body
    draw.rectangle([(0, wall_y), (width, wall_y + wall_h)], fill=(120, 90, 70))

    # Brick lines
    brick_h = 20
    brick_w = 60
    for row in range(wall_h // brick_h):
        y = wall_y + row * brick_h
        offset = (row % 2) * (brick_w // 2)
        for col in range(-1, (width // brick_w) + 2):
            x = col * brick_w + offset
            shade = 5 if random.random() < 0.3 else -5
            draw.rectangle(
                [(x, y), (x + brick_w - 2, y + brick_h - 2)],
                fill=(125 + shade, 95 + shade, 75 + shade),
                outline=(100, 75, 55),
            )

    # Wall cap
    draw.rectangle([(0, wall_y - 8), (width, wall_y)], fill=(100, 75, 55))
    draw.rectangle([(0, wall_y - 12), (width, wall_y - 8)], fill=(130, 100, 80))

    # Frost on wall top
    for x in range(0, width, 3):
        fh = random.randint(1, 4)
        draw.line([(x, wall_y - 12 - fh), (x, wall_y - 12)], fill=(220, 230, 240, 80))


def draw_gate(draw: ImageDraw, width: int, height: int) -> None:
    """Draw an iron gate in the centre of the wall."""
    gate_cx = width // 2
    wall_y = int(height * 0.35)
    gate_w = 160
    gate_h = 140

    # Gate opening (dark)
    draw.rectangle(
        [(gate_cx - gate_w // 2, wall_y - 8), (gate_cx + gate_w // 2, wall_y + gate_h)],
        fill=(30, 35, 40),
    )

    # Iron gate bars
    bar_color = (50, 55, 60)
    # Vertical bars
    for i in range(7):
        x = gate_cx - gate_w // 2 + 10 + i * 23
        draw.line([(x, wall_y - 8), (x, wall_y + gate_h)], fill=bar_color, width=3)

    # Horizontal bars
    for i in range(4):
        y = wall_y - 8 + i * 35
        draw.line(
            [(gate_cx - gate_w // 2 + 8, y), (gate_cx + gate_w // 2 - 8, y)],
            fill=bar_color,
            width=2,
        )

    # Gate arch
    draw.arc(
        [(gate_cx - gate_w // 2, wall_y - 80), (gate_cx + gate_w // 2, wall_y - 8)],
        0, 180, fill=bar_color, width=3,
    )


def draw_bare_trees(draw: ImageDraw, width: int, height: int) -> None:
    """Draw bare winter trees flanking the wall."""
    rng = random.Random(17)

    positions = [
        (80, int(height * 0.28)),
        (200, int(height * 0.25)),
        (width - 80, int(height * 0.27)),
        (width - 200, int(height * 0.23)),
        (140, int(height * 0.32)),
        (width - 140, int(height * 0.30)),
    ]

    for tx, ty in positions:
        trunk_h = rng.randint(180, 280)
        trunk_w = rng.randint(8, 14)

        # Trunk
        color = (45, 35, 30)
        draw.rectangle([tx - trunk_w // 2, ty - trunk_h, tx + trunk_w // 2, ty], fill=color)

        # Main branches
        for angle in range(-60, 70, 25):
            branch_len = rng.randint(40, 100)
            bx = tx + int(branch_len * math.sin(math.radians(angle)))
            by = ty - trunk_h + rng.randint(30, trunk_h - 40)
            draw.line([(tx, by), (bx, by - 30)], fill=color, width=rng.randint(2, 5))

            # Sub-branches
            sub_angle = angle + rng.randint(-20, 20)
            sub_len = rng.randint(15, 35)
            sx = bx + int(sub_len * math.sin(math.radians(sub_angle)))
            sy = by - 30 + rng.randint(-10, 10)
            draw.line([(bx, by - 30), (sx, sy)], fill=color, width=rng.randint(1, 2))

        # Fine twigs
        for _ in range(8):
            start_x = tx + rng.randint(-40, 40)
            start_y = ty - trunk_h + rng.randint(10, trunk_h - 20)
            end_x = start_x + rng.randint(-50, 50)
            end_y = start_y - rng.randint(20, 60)
            draw.line([(start_x, start_y), (end_x, end_y)], fill=(60, 50, 45), width=1)


def draw_holly_branches(draw: ImageDraw, width: int, height: int) -> None:
    """Draw holly branches with red berries at the edges."""
    rng = random.Random(42)

    # Left side holly
    for i in range(4):
        start_x = rng.randint(-30, 60)
        start_y = rng.randint(int(height * 0.2), int(height * 0.55))
        end_x = start_x + rng.randint(80, 150)
        end_y = start_y - rng.randint(10, 60)
        draw.line([(start_x, start_y), (end_x, end_y)], fill=(40, 60, 30), width=3)

        # Holly leaves (simple ovals)
        for lf in range(4):
            lx = start_x + (end_x - start_x) * (lf / 4) + rng.randint(-5, 5)
            ly = start_y + (end_y - start_y) * (lf / 4) + rng.randint(-5, 5)
            draw.ellipse([lx - 6, ly - 4, lx + 6, ly + 4], fill=(30, 70, 25))
            # Red berry
            draw.ellipse([lx + 8, ly - 3, lx + 14, ly + 3], fill=(180, 20, 20))

    # Right side holly
    for i in range(4):
        start_x = width - rng.randint(-30, 60)
        start_y = rng.randint(int(height * 0.2), int(height * 0.55))
        end_x = start_x - rng.randint(80, 150)
        end_y = start_y - rng.randint(10, 60)
        draw.line([(start_x, start_y), (end_x, end_y)], fill=(40, 60, 30), width=3)

        for lf in range(4):
            lx = start_x + (end_x - start_x) * (lf / 4) + rng.randint(-5, 5)
            ly = start_y + (end_y - start_y) * (lf / 4) + rng.randint(-5, 5)
            draw.ellipse([lx - 6, ly - 4, lx + 6, ly + 4], fill=(30, 70, 25))
            draw.ellipse([lx - 14, ly - 3, lx - 8, ly + 3], fill=(180, 20, 20))


def draw_frost_effects(draw: ImageDraw, width: int, height: int) -> None:
    """Add frost and snow particle effects."""
    rng = random.Random(31)

    # Frost crystals on ground
    ground_y = int(height * 0.35) + 160
    for _ in range(200):
        x = rng.randint(0, width)
        y = rng.randint(ground_y, int(height * 0.45))
        size = rng.randint(1, 3)
        draw.ellipse([x, y, x + size, y + size], fill=(220, 230, 240, rng.randint(60, 150)))

    # Falling snow particles
    for _ in range(80):
        x = rng.randint(0, width)
        y = rng.randint(0, int(height * 0.6))
        size = rng.randint(1, 4)
        alpha = rng.randint(100, 200)
        draw.ellipse([x, y, x + size, y + size], fill=(240, 245, 250, alpha))


def draw_path(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a garden path leading from the gate toward the viewer."""
    gate_cx = width // 2
    wall_y = int(height * 0.35) + 160

    # Path widening as it approaches viewer
    path_points = [
        (gate_cx - 25, wall_y),
        (gate_cx + 25, wall_y),
        (gate_cx + 120, HEIGHT),
        (gate_cx - 120, HEIGHT),
    ]
    draw.polygon(path_points, fill=(150, 140, 130))

    # Path stones
    rng = random.Random(53)
    for y in range(wall_y, HEIGHT, 30):
        x_range = 25 + (y - wall_y) * 95 / (HEIGHT - wall_y)
        cx = gate_cx
        for _ in range(3):
            sx = cx + rng.randint(-int(x_range), int(x_range))
            sy = y + rng.randint(-8, 8)
            draw.ellipse(
                [sx - rng.randint(8, 18), sy - 4, sx + rng.randint(8, 18), sy + 4],
                fill=(160, 150, 140),
            )

    # Frost on path edges
    for _ in range(60):
        ex = gate_cx + rng.randint(-160, 160)
        ey = rng.randint(wall_y, HEIGHT)
        draw.ellipse([ex, ey, ex + 3, ey + 3], fill=(200, 210, 220, rng.randint(40, 100)))


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark title panel at the bottom of the cover with WHITE text."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    draw.rectangle([(0, panel_top), (width, height)], fill=(25, 30, 40))

    # Subtle border at top of panel
    draw.line([(0, panel_top), (width, panel_top)], fill=(60, 70, 85), width=2)

    # Holly berry decorative line at panel top
    for x in range(60, width - 60, 40):
        draw.ellipse([x - 3, panel_top + 15, x + 3, panel_top + 21], fill=(160, 20, 20))

    # Title text — use arialbd.ttf, WHITE
    title = "The Winter\nGarden"
    title_font_size = 80
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    lines = title.split("\n")
    y_offset = panel_top + 55
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 0
        tx = (width - tw) // 2
        draw.text((tx, y_offset), line, fill=(255, 255, 255), font=title_font)
        y_offset += 100

    # Author name — smaller, WHITE
    author = "Barış Kısır"
    author_font_size = 38
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
    ay = panel_top + 260
    draw.text((ax, ay), author, fill=(220, 225, 230), font=author_font)

    # Small decorative line below author
    dec_line_y = ay + 45
    dec_line_w = 80
    draw.line(
        [(width // 2 - dec_line_w // 2, dec_line_y), (width // 2 + dec_line_w // 2, dec_line_y)],
        fill=(160, 20, 20),
        width=1,
    )


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Winter Garden")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Bare winter trees
    draw_bare_trees(draw, WIDTH, HEIGHT)

    # Step 3: Garden wall with gate
    draw_garden_wall(draw, WIDTH, HEIGHT)
    draw_gate(draw, WIDTH, HEIGHT)

    # Step 4: Holly branches with berries
    draw_holly_branches(draw, WIDTH, HEIGHT)

    # Step 5: Path leading from gate
    draw_path(draw, WIDTH, HEIGHT)

    # Step 6: Frost and snow effects
    draw_frost_effects(draw, WIDTH, HEIGHT)

    # Step 7: Title panel (dark with WHITE text)
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arial.ttf"),
        "small": str(FONTS_DIR / "arial.ttf"),
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