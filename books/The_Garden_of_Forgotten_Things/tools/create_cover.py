#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Garden of Forgotten Things."""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import (
    _standard_cover_font,
    _standard_cover_repair_text,
    _standard_cover_wrap,
    _standard_cover_center,
    _standard_cover_title_font,
    _standard_cover_metadata_from_locals,
    _standard_cover_resolve_title,
    _standard_cover_resolve_author,
    _draw_standard_cover_title_panel,
)



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
    """Soft green to dusty rose to deep green gradient for magical realism feel."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((20, 50, 30), (80, 60, 50), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((80, 60, 50), (120, 70, 60), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((120, 70, 60), (15, 40, 25), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_stone_wall(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the walled garden's stone wall across the midground."""
    wall_y = int(height * 0.52)
    wall_h = int(height * 0.18)

    # Wall base
    draw.rectangle([(0, wall_y), (width, wall_y + wall_h)], fill=(60, 55, 50))

    # Individual stones
    rng = random.Random(13)
    stone_w = 80
    stone_h = 35
    gap = 4
    for row in range(4):
        offset = (stone_w // 2) if row % 2 == 1 else 0
        y_pos = wall_y + 5 + row * (stone_h + gap)
        for col in range(width // stone_w + 2):
            x_pos = col * (stone_w + gap) + offset - stone_w // 2
            if x_pos < -stone_w:
                continue
            if x_pos > width + stone_w:
                break
            shade = rng.randint(50, 75)
            draw.rectangle(
                [x_pos, y_pos, x_pos + stone_w - gap, min(y_pos + stone_h, wall_y + wall_h - 5)],
                fill=(shade, shade - 5, shade - 10),
            )
            # Moss on some stones
            if rng.random() < 0.3:
                moss_x = x_pos + rng.randint(2, stone_w - 10)
                moss_y = y_pos + rng.randint(2, stone_h - 8)
                draw.ellipse(
                    [moss_x, moss_y, moss_x + rng.randint(8, 20), moss_y + rng.randint(4, 10)],
                    fill=(40, 80, 45, 150),
                )

    # Top edge of wall
    draw.line([(0, wall_y), (width, wall_y)], fill=(50, 45, 40), width=3)


def draw_gate(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the wooden garden gate in the centre of the wall."""
    wall_y = int(height * 0.52)
    wall_h = int(height * 0.18)

    cx = width // 2
    gate_w = 160
    gate_h = int(wall_h * 0.85)
    gate_y = wall_y + wall_h - gate_h

    # Gate frame
    draw.rectangle(
        [cx - gate_w // 2, gate_y, cx + gate_w // 2, wall_y + wall_h],
        fill=(40, 30, 20),
    )
    # Gate door
    draw.rectangle(
        [cx - gate_w // 2 + 8, gate_y + 5, cx - 4, wall_y + wall_h - 5],
        fill=(55, 42, 28),
    )
    draw.rectangle(
        [cx + 4, gate_y + 5, cx + gate_w // 2 - 8, wall_y + wall_h - 5],
        fill=(55, 42, 28),
    )
    # Cross planks
    for door_x in [cx - gate_w // 2 + 8, cx + 4]:
        for py in range(gate_y + 30, wall_y + wall_h, 40):
            draw.line(
                [(door_x, py), (door_x + gate_w // 2 - 12, py)],
                fill=(45, 33, 20),
                width=2,
            )
    # Handle
    draw.ellipse([cx + gate_w // 2 - 20, wall_y + wall_h - 40, cx + gate_w // 2 - 10, wall_y + wall_h - 30], fill=(80, 70, 55))


def draw_climbing_roses(draw: ImageDraw, width: int, height: int) -> None:
    """Draw climbing roses on the stone wall."""
    rng = random.Random(7)
    wall_y = int(height * 0.52)
    wall_h = int(height * 0.18)

    # Rose vines along top of wall
    for vine in range(12):
        vx = rng.randint(50, width - 50)
        vy = wall_y + rng.randint(-20, 5)
        # Vine stem
        stem_points = []
        for s in range(5):
            stem_points.append((vx + rng.randint(-15, 15), vy - s * rng.randint(20, 35)))
        draw.line(stem_points, fill=(30, 60, 25), width=3)

        # Leaves
        for lf in range(3):
            lx = stem_points[lf * 2][0] + rng.randint(-10, 10)
            ly = stem_points[lf * 2][1] + rng.randint(-5, 5)
            draw.ellipse([lx - 8, ly - 4, lx + 8, ly + 4], fill=(35, 75, 30))

        # Roses
        num_roses = rng.randint(1, 3)
        for _ in range(num_roses):
            rx = vx + rng.randint(-20, 20)
            ry = vy - rng.randint(5, 80)
            rose_size = rng.randint(10, 20)
            # Outer petals (dusty rose)
            draw.ellipse([rx - rose_size, ry - rose_size, rx + rose_size, ry + rose_size], fill=(140, 70, 60))
            # Inner petals
            inner = int(rose_size * 0.65)
            draw.ellipse([rx - inner, ry - inner, rx + inner, ry + inner], fill=(160, 90, 75))
            # Centre
            centre = int(rose_size * 0.35)
            draw.ellipse([rx - centre, ry - centre, rx + centre, ry + centre], fill=(180, 110, 85))


def draw_sundial(draw: ImageDraw, width: int, height: int, img: Image.Image) -> None:
    """Draw a stone sundial at the center foreground area."""
    sx = width // 2
    sy = int(height * 0.72)

    # Base pedestal
    base_w = 50
    base_h = 60
    draw.polygon(
        [(sx - base_w, sy), (sx - base_w + 10, sy - base_h), (sx + base_w - 10, sy - base_h), (sx + base_w, sy)],
        fill=(100, 95, 85),
    )

    # Pedestal highlight
    draw.polygon(
        [(sx - base_w, sy), (sx - base_w + 10, sy - base_h), (sx - base_w + 5, sy - base_h), (sx - base_w + 5, sy)],
        fill=(120, 112, 100),
    )

    # Sundial disc
    disc_r = 45
    draw.ellipse(
        [sx - disc_r, sy - base_h - disc_r, sx + disc_r, sy - base_h + 5],
        fill=(130, 122, 110),
    )
    # Disc face
    draw.ellipse(
        [sx - disc_r + 5, sy - base_h - disc_r + 5, sx + disc_r - 5, sy - base_h + 1],
        fill=(160, 150, 135),
    )

    # Gnomon (shadow pointer)
    draw.polygon(
        [(sx - 3, sy - base_h + 5), (sx + 3, sy - base_h + 5), (sx, sy - base_h - disc_r + 10)],
        fill=(50, 45, 40),
    )

    # Worn text marks around disc edge
    rng = random.Random(31)
    for angle_deg in range(0, 360, 30):
        rad = math.radians(angle_deg)
        mx = sx + int((disc_r - 10) * math.cos(rad))
        my = sy - base_h + int((disc_r - 10) * math.sin(rad))
        dot_size = rng.randint(2, 5)
        draw.ellipse([mx - dot_size, my - dot_size, mx + dot_size, my + dot_size], fill=(100, 92, 82))


def draw_memory_plants(draw: ImageDraw, width: int, height: int) -> None:
    """Draw foreground plants and flowers emerging from the soil."""
    rng = random.Random(23)
    ground_y = int(height * 0.85)

    # Ground line
    draw.line([(0, ground_y), (width, ground_y)], fill=(25, 50, 30), width=2)

    # Plants across the bottom foreground
    for plant in range(20):
        px = rng.randint(30, width - 30)
        py = ground_y + rng.randint(-10, 5)
        plant_h = rng.randint(40, 120)
        plant_type = rng.randint(0, 2)

        # Stem
        draw.line([(px, py), (px, py - plant_h)], fill=(35, 65, 30), width=3)

        if plant_type == 0:
            # Peonies - white blooms
            bloom_r = rng.randint(12, 20)
            draw.ellipse(
                [px - bloom_r, py - plant_h - bloom_r, px + bloom_r, py - plant_h + bloom_r],
                fill=(220, 210, 200),
            )
            draw.ellipse(
                [px - bloom_r + 4, py - plant_h - bloom_r + 4, px + bloom_r - 4, py - plant_h + bloom_r - 4],
                fill=(240, 230, 220),
            )
        elif plant_type == 1:
            # Rosemary - small blue flowers
            for fl in range(5):
                fx = px + rng.randint(-8, 8)
                fy = py - plant_h + rng.randint(0, 15)
                draw.ellipse([fx - 3, fy - 3, fx + 3, fy + 3], fill=(100, 130, 160))
            # Leaves
            for lf in range(4):
                lx = px - 5 + rng.randint(0, 10)
                ly = py - rng.randint(15, plant_h - 5)
                draw.line([(lx, ly), (lx + 6, ly - 2)], fill=(50, 80, 45), width=2)
        else:
            # Lavender - purple spikes
            spike_h = rng.randint(15, 30)
            for sp in range(6):
                sy = py - plant_h + sp * (spike_h // 6)
                draw.ellipse([px - 3, sy - spike_h // 12, px + 3, sy + spike_h // 12], fill=(110, 80, 120))

    # Some creeping ivy at the base
    for ivy in range(8):
        ix = rng.randint(0, width)
        iy = ground_y + rng.randint(1, 20)
        for seg in range(6):
            y0 = iy + rng.randint(-3, 3)
            y1 = iy + rng.randint(2, 8)
            if y0 > y1:
                y0, y1 = y1, y0
            draw.ellipse(
                [ix + seg * 8, y0, ix + seg * 8 + 10, y1],
                fill=(30, 70, 35),
            )


def draw_light_particles(draw: ImageDraw, width: int, height: int) -> None:
    """Draw small golden light particles floating in the air for magical atmosphere."""
    rng = random.Random(17)
    for _ in range(80):
        lx = rng.randint(50, width - 50)
        ly = rng.randint(int(height * 0.3), int(height * 0.8))
        size = rng.randint(2, 6)
        alpha = rng.randint(60, 160)
        draw.ellipse(
            [lx - size, ly - size, lx + size, ly + size],
            fill=(220, 200, 150, alpha),
        )
        # Inner glow
        if size > 3:
            draw.ellipse(
                [lx - size // 2, ly - size // 2, lx + size // 2, ly + size // 2],
                fill=(255, 240, 200, alpha + 40),
            )


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark title panel at the bottom with white text for readability."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background - nearly black with slight green tint
    draw.rectangle([(0, panel_top), (width, height)], fill=(15, 25, 18, 230))
    draw.rectangle([(0, panel_top), (width, panel_top + 3)], fill=(40, 70, 45))

    # Subtle top border line
    draw.line([(0, panel_top), (width, panel_top)], fill=(60, 100, 65), width=2)

    # Title text
    title = "The Garden of\nForgotten Things"
    title_font_size = 78
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    lines = title.split("\n")
    y_offset = panel_top + 70
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 0
        tx = (width - tw) // 2
        # White text
        draw.text((tx, y_offset), line, fill=(255, 255, 255), font=title_font)
        y_offset += 100

    # Decorative line separator
    line_y = y_offset - 5
    draw.line(
        [(width // 2 - 120, line_y), (width // 2 + 120, line_y)],
        fill=(80, 130, 90),
        width=1,
    )

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
    ay = y_offset + 30
    draw.text((ax, ay), author, fill=(180, 200, 185), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background (green to dusty rose)
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Stone wall (wall of the walled garden)
    draw_stone_wall(draw, WIDTH, HEIGHT)

    # Step 3: Wooden gate
    draw_gate(draw, WIDTH, HEIGHT)

    # Step 4: Climbing roses over the wall
    draw_climbing_roses(draw, WIDTH, HEIGHT)

    # Step 5: Sundial at center
    draw_sundial(draw, WIDTH, HEIGHT, img)

    # Step 6: Memory plants in foreground
    draw_memory_plants(draw, WIDTH, HEIGHT)

    # Step 7: Light particles for magical atmosphere
    draw_light_particles(draw, WIDTH, HEIGHT)

    # Step 8: Title panel at bottom
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arial.ttf"),
    }
    draw_title_panel(draw, WIDTH, HEIGHT, font_paths)

    # Soften slightly
    img = img.filter(ImageFilter.SMOOTH)

    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), metadata.get("model", ""))
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