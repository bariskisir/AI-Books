#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Glass Cockpit."""

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
    """Dusk storm sky: deep night-blue at the top easing to a cold amber horizon."""
    for y in range(height):
        if y < height * 0.30:
            t = y / (height * 0.30)
            c = lerp_color((6, 12, 26), (12, 22, 44), t)
        elif y < height * 0.55:
            t = (y - height * 0.30) / (height * 0.25)
            c = lerp_color((12, 22, 44), (24, 40, 66), t)
        elif y < height * 0.72:
            t = (y - height * 0.55) / (height * 0.17)
            c = lerp_color((24, 40, 66), (70, 64, 78), t)
        else:
            t = (y - height * 0.72) / (height * 0.28)
            c = lerp_color((70, 64, 78), (150, 96, 56), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_storm_clouds(draw: ImageDraw, width: int, height: int) -> None:
    """Soft banded storm clouds drifting across the upper sky."""
    import random

    rng = random.Random(41)
    overlay_colors = [
        (18, 26, 48, 70),
        (28, 36, 58, 55),
        (40, 30, 44, 45),
    ]
    for band in range(5):
        base_y = height * 0.12 + band * height * 0.07 + rng.randint(-12, 12)
        col = overlay_colors[band % len(overlay_colors)]
        for x in range(0, width, 2):
            wave = math.sin(x * 0.0016 + band * 1.1) * height * 0.03
            thickness = int(height * 0.035 + math.sin(x * 0.004 + band) * height * 0.012)
            y_c = int(base_y + wave)
            draw.line([(x, y_c - thickness), (x, y_c + thickness)], fill=col)


def draw_lightning(draw: ImageDraw, width: int, height: int) -> None:
    """A thin fork of lightning behind the wing, cool white-blue."""
    import random

    rng = random.Random(7)
    x = int(width * 0.30)
    y = int(height * 0.08)
    points = [(x, y)]
    while y < height * 0.55:
        x += rng.randint(-40, 30)
        y += rng.randint(40, 90)
        points.append((x, y))
    for glow in range(3, 0, -1):
        draw.line(points, fill=(150, 190, 235, 60), width=glow * 3)
    draw.line(points, fill=(225, 238, 255), width=2)


def draw_wing(draw: ImageDraw, width: int, height: int) -> None:
    """A swept airliner wing crossing the lower sky, seen from the cabin."""
    # Wing slab sweeping from lower-left up toward the right horizon.
    root = (-40, int(height * 0.72))
    root_aft = (-40, int(height * 0.80))
    tip = (int(width * 0.92), int(height * 0.50))
    tip_aft = (int(width * 0.86), int(height * 0.545))

    draw.polygon([root, tip, tip_aft, root_aft], fill=(22, 26, 34))
    # Upper edge catches the amber horizon light.
    draw.line([root, tip], fill=(120, 92, 64), width=5)
    # Underside shadow line.
    draw.line([root_aft, tip_aft], fill=(8, 10, 14), width=4)

    # Winglet turned up at the tip.
    draw.polygon(
        [tip, (int(width * 0.98), int(height * 0.40)), (int(width * 0.95), int(height * 0.405)),
         (int(width * 0.90), int(height * 0.505))],
        fill=(18, 22, 30),
    )
    draw.line([tip, (int(width * 0.98), int(height * 0.40))], fill=(110, 86, 60), width=4)

    # Navigation light at the tip: green starboard, with a small glow.
    gx, gy = int(width * 0.965), int(height * 0.405)
    for r in range(18, 4, -4):
        a = max(0, 90 - r * 3)
        draw.ellipse([gx - r, gy - r, gx + r, gy + r], outline=(60, 230, 140, a), width=2)
    draw.ellipse([gx - 6, gy - 6, gx + 6, gy + 6], fill=(120, 255, 170))

    # Faint anti-collision strobe mid-span.
    sx, sy = int(width * 0.55), int(height * 0.615)
    for r in range(14, 3, -3):
        a = max(0, 70 - r * 3)
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], outline=(255, 90, 70, a), width=2)
    draw.ellipse([sx - 4, sy - 4, sx + 4, sy + 4], fill=(255, 150, 130))


def draw_instruments(draw: ImageDraw, width: int, height: int) -> None:
    """Glowing cockpit instruments along the bottom: an attitude indicator and dials."""
    base_y = int(height * 0.84)

    # Dark instrument coaming spanning the width.
    draw.rectangle([(0, base_y - 30), (width, int(height * 0.95))], fill=(10, 14, 20))
    for i in range(3):
        draw.line([(0, base_y - 30 + i), (width, base_y - 30 + i)],
                  fill=(40, 120, 90, 90 - i * 20), width=1)

    # Central primary flight display (attitude indicator).
    cx, cy = width // 2, base_y + 110
    pfd_r = 120
    draw.rectangle([cx - pfd_r - 18, cy - pfd_r - 18, cx + pfd_r + 18, cy + pfd_r + 18],
                   fill=(6, 9, 14), outline=(30, 90, 70), width=2)
    # Sky (blue) over ground (amber-brown), banked slightly.
    draw.pieslice([cx - pfd_r, cy - pfd_r, cx + pfd_r, cy + pfd_r], 200, 20, fill=(28, 110, 170))
    draw.pieslice([cx - pfd_r, cy - pfd_r, cx + pfd_r, cy + pfd_r], 20, 200, fill=(120, 80, 40))
    # Horizon line.
    draw.line([cx - pfd_r, cy + 12, cx + pfd_r, cy - 12], fill=(230, 235, 240), width=3)
    # Aircraft reference symbol (instrument green).
    draw.line([cx - 55, cy, cx - 18, cy], fill=(120, 255, 150), width=4)
    draw.line([cx + 18, cy, cx + 55, cy], fill=(120, 255, 150), width=4)
    draw.rectangle([cx - 4, cy - 4, cx + 4, cy + 4], fill=(120, 255, 150))

    # Flanking round dials.
    for dx in (-1, 1):
        ox = cx + dx * (pfd_r + 230)
        dr = 80
        draw.ellipse([ox - dr - 12, cy - dr - 12, ox + dr + 12, cy + dr + 12],
                     fill=(6, 9, 14), outline=(30, 90, 70), width=2)
        draw.ellipse([ox - dr, cy - dr, ox + dr, cy + dr], outline=(50, 140, 110), width=2)
        # Tick marks.
        for tick in range(12):
            ang = tick * math.pi / 6
            x1 = ox + int(math.cos(ang) * (dr - 12))
            y1 = cy + int(math.sin(ang) * (dr - 12))
            x2 = ox + int(math.cos(ang) * dr)
            y2 = cy + int(math.sin(ang) * dr)
            draw.line([x1, y1, x2, y2], fill=(110, 200, 170), width=2)
        # Needle (amber warning tone on one, green on the other).
        needle = (255, 176, 60) if dx < 0 else (120, 255, 150)
        na = -2.1 if dx < 0 else 0.9
        draw.line([ox, cy, ox + int(math.cos(na) * (dr - 18)), cy + int(math.sin(na) * (dr - 18))],
                  fill=needle, width=4)
        draw.ellipse([ox - 6, cy - 6, ox + 6, cy + 6], fill=needle)


def draw_runway_lights(draw: ImageDraw, width: int, height: int) -> None:
    """Twin rows of runway lights converging toward a vanishing point on the horizon."""
    vx, vy = int(width * 0.42), int(height * 0.66)
    left_base = int(width * 0.06)
    right_base = int(width * 0.94)
    base_y = int(height * 0.80)

    for i in range(9):
        t = i / 9.0
        lx = int(left_base + (vx - left_base) * t)
        rx = int(right_base + (vx - right_base) * t)
        ly = int(base_y + (vy - base_y) * t)
        size = max(1, int(8 * (1 - t)))
        # Edge lights warm amber, brighter and larger near the viewer.
        for side_x in (lx, rx):
            for g in range(size + 4, 0, -2):
                a = max(0, 60 - g * 6)
                draw.ellipse([side_x - g, ly - g, side_x + g, ly + g],
                             outline=(255, 190, 90, a), width=1)
            draw.ellipse([side_x - size, ly - size, side_x + size, ly + size],
                         fill=(255, 210, 120))
    # A few green threshold lights at the far end.
    for k in range(-2, 3):
        tx = vx + k * 14
        draw.ellipse([tx - 3, vy - 3, tx + 3, vy + 3], fill=(120, 255, 160))


def draw_rain(draw: ImageDraw, width: int, height: int) -> None:
    """Streaks of rain slanting across the sky."""
    import random

    rng = random.Random(23)
    for _ in range(220):
        x = rng.randint(0, width)
        y = rng.randint(0, int(height * 0.78))
        length = rng.randint(14, 34)
        slant = rng.randint(4, 10)
        alpha = rng.randint(40, 120)
        draw.line([(x, y), (x - slant, y + length)], fill=(180, 200, 225, alpha), width=1)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Glass Cockpit")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Step 1: Dusk storm gradient
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Banded storm clouds
    draw_storm_clouds(draw, WIDTH, HEIGHT)

    # Step 3: Lightning fork
    draw_lightning(draw, WIDTH, HEIGHT)

    # Step 4: Rain
    draw_rain(draw, WIDTH, HEIGHT)

    # Step 5: Runway lights converging on the horizon
    draw_runway_lights(draw, WIDTH, HEIGHT)

    # Step 6: The airliner wing
    draw_wing(draw, WIDTH, HEIGHT)

    # Step 7: Glowing cockpit instruments
    draw_instruments(draw, WIDTH, HEIGHT)

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
