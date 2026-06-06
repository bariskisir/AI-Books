#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Iron Whale."""

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
    """Ocean column: faint teal light near the surface fading down into abyssal black."""
    for y in range(height):
        if y < height * 0.18:
            t = y / (height * 0.18)
            c = lerp_color((18, 58, 70), (12, 44, 58), t)
        elif y < height * 0.45:
            t = (y - height * 0.18) / (height * 0.27)
            c = lerp_color((12, 44, 58), (8, 28, 42), t)
        elif y < height * 0.72:
            t = (y - height * 0.45) / (height * 0.27)
            c = lerp_color((8, 28, 42), (5, 16, 26), t)
        else:
            t = (y - height * 0.72) / (height * 0.28)
            c = lerp_color((5, 16, 26), (2, 6, 12), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_surface_light(draw: ImageDraw, width: int, height: int) -> None:
    """Faint shafts of light filtering down from the unseen surface above."""
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    rng = __import__("random").Random(7)
    for _ in range(9):
        x_top = rng.randint(-200, width)
        spread = rng.randint(60, 160)
        depth = rng.randint(int(height * 0.30), int(height * 0.55))
        for i in range(spread):
            xa = x_top + i
            xb = x_top + i + int(depth * 0.25)
            alpha = max(0, 22 - abs(i - spread // 2) // 4)
            if alpha > 0:
                od.line([(xa, 0), (xb, depth)], fill=(90, 170, 180, alpha), width=1)
    draw._image.paste(Image.alpha_composite(draw._image.convert("RGBA"), overlay), (0, 0))


def draw_particles(draw: ImageDraw, width: int, height: int) -> None:
    """Marine snow and suspended grit drifting in the water column."""
    rng = __import__("random").Random(23)
    for _ in range(420):
        x = rng.randint(0, width)
        y = rng.randint(0, int(height * 0.88))
        depth_t = y / height
        size = rng.choice([1, 1, 1, 2])
        alpha = int(rng.randint(20, 80) * (1.0 - depth_t * 0.6))
        if alpha > 4:
            draw.ellipse([x - size, y - size, x + size, y + size], fill=(150, 185, 195, alpha))


def draw_submarine(draw: ImageDraw, width: int, height: int) -> None:
    """A dark steel hull descending bow-down into the abyss, sail and planes in silhouette."""
    cx = width * 0.50
    cy = height * 0.46
    length = width * 0.95
    half_h = height * 0.075

    hull_dark = (16, 26, 34)
    hull_mid = (24, 38, 48)
    hull_light = (40, 60, 70)

    # Hull body: a long tapered cylinder, tilted slightly bow-down to the right.
    angle = math.radians(11)
    ca, sa = math.cos(angle), math.sin(angle)

    def pt(u: float, v: float) -> tuple[float, float]:
        # u along hull (-1 bow .. +1 stern), v across (-1 top .. +1 bottom)
        x = u * (length / 2)
        y = v * half_h
        return (cx + x * ca - y * sa, cy + x * sa + y * ca)

    # Build the hull outline from bow (right) to stern (left).
    top_pts = []
    bot_pts = []
    steps = 60
    for i in range(steps + 1):
        u = -1.0 + 2.0 * i / steps
        # taper toward both ends
        taper = (1.0 - u * u) ** 0.5
        # sharper, longer bow on the right
        if u < 0:
            taper *= 1.0
        top_pts.append(pt(u, -taper))
        bot_pts.append(pt(u, taper))

    hull_poly = top_pts + list(reversed(bot_pts))
    draw.polygon(hull_poly, fill=hull_dark)

    # Upper highlight band along the curved back of the hull.
    hi = []
    for i in range(steps + 1):
        u = -1.0 + 2.0 * i / steps
        taper = (1.0 - u * u) ** 0.5
        hi.append(pt(u, -taper * 0.92))
    lo = []
    for i in range(steps + 1):
        u = 1.0 - 2.0 * i / steps
        taper = (1.0 - u * u) ** 0.5
        lo.append(pt(u, -taper * 0.55))
    draw.polygon(hi + lo, fill=hull_mid)

    # Thin crest highlight catching the last surface light.
    crest = []
    for i in range(steps + 1):
        u = -1.0 + 2.0 * i / steps
        taper = (1.0 - u * u) ** 0.5
        crest.append(pt(u, -taper * 0.97))
    if len(crest) > 1:
        draw.line(crest, fill=hull_light, width=2)

    # Conning tower (sail) rising from the upper hull.
    s_u = -0.06
    sail_base_l = pt(s_u - 0.16, -0.95)
    sail_base_r = pt(s_u + 0.16, -0.95)
    sail_top_l = pt(s_u - 0.11, -2.6)
    sail_top_r = pt(s_u + 0.11, -2.6)
    draw.polygon([sail_base_l, sail_top_l, sail_top_r, sail_base_r], fill=hull_mid)
    draw.line([sail_top_l, sail_base_l], fill=hull_light, width=2)
    # Periscope / mast.
    mast_b = pt(s_u, -2.6)
    mast_t = pt(s_u, -3.5)
    draw.line([mast_b, mast_t], fill=(50, 70, 78), width=4)

    # Bow plane (fairwater plane) jutting from the sail.
    bp_a = pt(s_u + 0.10, -1.9)
    bp_b = pt(s_u + 0.55, -1.75)
    bp_c = pt(s_u + 0.55, -1.55)
    bp_d = pt(s_u + 0.10, -1.5)
    draw.polygon([bp_a, bp_b, bp_c, bp_d], fill=hull_dark)

    # Stern planes / rudder at the left tail.
    st_top = pt(0.95, -1.7)
    st_root = pt(0.78, -0.5)
    st_bot = pt(0.95, 1.7)
    draw.polygon([st_root, st_top, pt(1.02, -1.2)], fill=hull_dark)
    draw.polygon([st_root, st_bot, pt(1.02, 1.2)], fill=hull_dark)

    # A line of faint rivets running the length of the hull.
    for i in range(2, steps - 1, 2):
        u = -1.0 + 2.0 * i / steps
        taper = (1.0 - u * u) ** 0.5
        rx, ry = pt(u, -taper * 0.35)
        draw.ellipse([rx - 1, ry - 1, rx + 1, ry + 1], fill=(60, 82, 90))

    # A single faint porthole glow on the sail — small sliver of warm interior light.
    px, py = pt(s_u - 0.02, -2.0)
    draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(70, 90, 95))


def draw_emergency_light(draw: ImageDraw, width: int, height: int) -> None:
    """A sliver of red emergency light bleeding from a hatch on the hull."""
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    gx = int(width * 0.42)
    gy = int(height * 0.455)
    # Soft red glow.
    for r in range(120, 6, -10):
        alpha = max(0, 40 - r // 4)
        od.ellipse([gx - r, gy - int(r * 0.6), gx + r, gy + int(r * 0.6)],
                   fill=(140, 30, 25, alpha))
    # Hot red core.
    od.ellipse([gx - 10, gy - 6, gx + 10, gy + 6], fill=(220, 60, 45, 180))
    od.ellipse([gx - 4, gy - 3, gx + 4, gy + 3], fill=(255, 120, 100, 220))
    draw._image.paste(Image.alpha_composite(draw._image.convert("RGBA"), overlay), (0, 0))


def draw_sonar_arcs(draw: ImageDraw, width: int, height: int) -> None:
    """Faint concentric sonar/ping arcs radiating through the dark water."""
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    ox, oy = int(width * 0.16), int(height * 0.20)
    for r in range(120, 900, 120):
        alpha = max(0, 34 - r // 40)
        if alpha > 0:
            od.arc([ox - r, oy - r, ox + r, oy + r], start=20, end=120,
                   fill=(70, 200, 190, alpha), width=2)
    draw._image.paste(Image.alpha_composite(draw._image.convert("RGBA"), overlay), (0, 0))


def draw_depth_haze(draw: ImageDraw, width: int, height: int) -> None:
    """Darken the lower abyss so the hull seems to descend out of light into black."""
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for y in range(int(height * 0.55), height):
        t = (y - height * 0.55) / (height * 0.45)
        alpha = int(min(150, t * 150))
        od.line([(0, y), (width, y)], fill=(1, 4, 9, alpha))
    draw._image.paste(Image.alpha_composite(draw._image.convert("RGBA"), overlay), (0, 0))


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark steel title panel at the bottom with a red emergency hairline."""
    panel_top = TITLE_PANEL_TOP

    draw.rectangle([(0, panel_top), (width, height)], fill=(6, 12, 18, 220))

    # Panel top border — a thin red emergency line over teal.
    for i in range(3):
        draw.line(
            [(0, panel_top - i), (width, panel_top - i)],
            fill=(160, 40, 35, 90 - i * 20),
            width=1,
        )

    title = "The Iron\nWhale"
    title_font_size = 80
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
        draw.text((tx + 2, y_offset + 2), line, fill=(2, 6, 10), font=title_font)
        draw.text((tx, y_offset), line, fill=(210, 222, 226), font=title_font)
        y_offset += 95

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
    ay = y_offset + 40
    draw.text((ax + 1, ay + 1), author, fill=(2, 6, 10), font=author_font)
    draw.text((ax, ay), author, fill=(150, 195, 200), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Iron Whale")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Ocean column gradient
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Light shafts from the surface
    draw_surface_light(draw, WIDTH, HEIGHT)

    # Step 3: Faint sonar arcs
    draw_sonar_arcs(draw, WIDTH, HEIGHT)

    # Step 4: Suspended particles / marine snow
    draw_particles(draw, WIDTH, HEIGHT)

    # Step 5: The submarine hull descending
    draw_submarine(draw, WIDTH, HEIGHT)

    # Step 6: Sliver of red emergency light
    draw_emergency_light(draw, WIDTH, HEIGHT)

    # Step 7: Depth haze into the abyss
    draw_depth_haze(draw, WIDTH, HEIGHT)

    # Step 8: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
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
