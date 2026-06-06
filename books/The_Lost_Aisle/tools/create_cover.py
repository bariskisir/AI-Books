#!/usr/bin/env python3
"""Cover: The Lost Aisle — an academic mystery with hidden library stacks."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[3]
FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        FONT_DIR / name,
        FONT_DIR / "georgiab.ttf",
        FONT_DIR / "georgia.ttf",
        FONT_DIR / "arialbd.ttf",
        FONT_DIR / "arial.ttf",
    ]
    for c in candidates:
        if c.exists():
            return ImageFont.truetype(str(c), size)
    return ImageFont.load_default()


def wrap(draw, text, fnt, mw):
    words = text.split()
    lines = []
    cur = []
    for w in words:
        p = " ".join([*cur, w])
        if draw.textbbox((0, 0), p, font=fnt)[2] <= mw:
            cur.append(w)
        else:
            lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def centered(draw, y, lines, fnt, fill, gap):
    for line in lines:
        bb = draw.textbbox((0, 0), line, font=fnt)
        draw.text(((W - (bb[2] - bb[0])) // 2, y), line, font=fnt, fill=fill)
        y += bb[3] - bb[1] + gap
    return y


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Deep mahogany-to-dark gradient — library atmosphere
    for y in range(H):
        t = y / H
        # Dark mahogany at top, deepening to near-black at bottom
        r = int(80 - 40 * t)
        g = int(30 - 15 * t)
        b = int(15 - 8 * t)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Candlelight glow — warm amber from upper center
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for i in range(5):
        cx = W // 2 + random.randint(-100, 100)
        cy = 400 + random.randint(-80, 80)
        radius = 300 + i * 60
        alpha = 40 - i * 6
        gd.ellipse(
            (cx - radius, cy - radius, cx + radius, cy + radius),
            fill=(240, 200, 120, max(0, alpha)),
        )
    glow = glow.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Bookshelf stacks — tall rectangles with spine lines
    shelf_y_base = 250
    shelf_colors = [
        (140, 60, 30, 200),
        (120, 50, 25, 200),
        (100, 80, 40, 200),
        (150, 70, 35, 200),
        (110, 55, 28, 200),
        (90, 70, 30, 200),
    ]
    # Left side shelves
    for col in range(5):
        sx = 100 + col * 160
        shelf_h = 1300 + random.randint(-200, 100)
        color = shelf_colors[col % len(shelf_colors)]
        draw.rectangle((sx, shelf_y_base, sx + 100, shelf_y_base + shelf_h), fill=color)
        # Spine lines on books
        for bk in range(8):
            by = shelf_y_base + bk * (shelf_h // 8)
            draw.rectangle(
                (sx + 8, by + 4, sx + 92, by + (shelf_h // 8) - 4),
                fill=(
                    max(0, color[0] - 30 + bk * 5),
                    max(0, color[1] - 10 + bk * 3),
                    max(0, color[2] - 5 + bk * 2),
                    color[3],
                ),
            )
        # Book edges (horizontal lines)
        for bk in range(9):
            by = shelf_y_base + bk * (shelf_h // 8)
            draw.line(
                (sx + 8, by, sx + 92, by),
                fill=(200, 160, 80, 60),
                width=1,
            )

    # Right side shelves
    for col in range(5):
        sx = W - 200 - col * 160
        shelf_h = 1200 + random.randint(-150, 150)
        color = shelf_colors[(col + 2) % len(shelf_colors)]
        draw.rectangle((sx, shelf_y_base + 50, sx + 100, shelf_y_base + 50 + shelf_h), fill=color)
        for bk in range(7):
            by = shelf_y_base + 50 + bk * (shelf_h // 7)
            draw.rectangle(
                (sx + 8, by + 4, sx + 92, by + (shelf_h // 7) - 4),
                fill=(
                    max(0, color[0] - 20 + bk * 4),
                    max(0, color[1] - 8 + bk * 2),
                    max(0, color[2] - 3 + bk * 1),
                    color[3],
                ),
            )
        for bk in range(8):
            by = shelf_y_base + 50 + bk * (shelf_h // 7)
            draw.line(
                (sx + 8, by, sx + 92, by),
                fill=(200, 160, 80, 50),
                width=1,
            )

    # Hidden door between shelves — center, slightly ajar, glowing edge
    door_x, door_y = W // 2 - 80, 500
    door_w, door_h = 160, 900
    # Door frame
    draw.rectangle(
        (door_x - 8, door_y - 8, door_x + door_w + 8, door_y + door_h + 8),
        fill=(60, 40, 20, 220),
    )
    # Door itself — dark wood
    draw.rectangle((door_x, door_y, door_x + door_w, door_y + door_h), fill=(45, 30, 15, 240))
    # Door panels
    draw.rectangle(
        (door_x + 15, door_y + 30, door_x + door_w - 15, door_y + door_h // 2 - 20),
        fill=(55, 38, 20, 230),
    )
    draw.rectangle(
        (door_x + 15, door_y + door_h // 2 + 20, door_x + door_w - 15, door_y + door_h - 30),
        fill=(55, 38, 20, 230),
    )
    # Crack of light from slightly open door
    draw.rectangle(
        (door_x + door_w - 4, door_y + 60, door_x + door_w + 6, door_y + door_h - 60),
        fill=(200, 170, 100, 180),
    )
    # Light spill on floor
    spill = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(spill)
    sd.polygon(
        [
            (door_x + door_w - 4, door_y + door_h),
            (door_x + door_w + 260, door_y + door_h + 150),
            (door_x + door_w + 200, door_y + door_h + 200),
            (door_x + door_w - 4, door_y + door_h + 80),
        ],
        fill=(200, 170, 100, 40),
    )
    spill = spill.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, spill)
    draw = ImageDraw.Draw(img, "RGBA")

    # Gold decorative lines on sides
    for side_x in [60, W - 60]:
        draw.line((side_x, 120, side_x, H - 200), fill=(200, 160, 80, 120), width=2)

    # Subtle arch at top
    for i in range(0, W, 4):
        arch_y = 80 + int(40 * math.sin(math.pi * i / W))
        draw.point((i, arch_y), fill=(200, 160, 80, 100))

    # Light rectangle title panel at bottom
    draw.rectangle((0, 1920, W, H), fill=(30, 25, 20, 230))
    # Gold accent lines
    draw.line((200, 1960, W - 200, 1960), fill=(200, 160, 80, 200), width=3)
    draw.line((200, H - 160, W - 200, H - 160), fill=(200, 160, 80, 150), width=2)

    # Subtitle: small text
    sf = font("arial.ttf", 28)
    centered(draw, 1980, ["AN ACADEMIC MYSTERY"], sf, (180, 150, 100), 6)

    # Title
    tf = font("georgiab.ttf", 100)
    title_lines = wrap(draw, title.upper(), tf, 1200)
    y = centered(draw, 2070, title_lines, tf, (220, 185, 130), 10)

    # Author
    y += 50
    af = font("arialbd.ttf", 42)
    centered(draw, y, [author], af, (200, 190, 170), 6)

    # Faint gold sparkles/fireflies
    for _ in range(30):
        sx = int(random.random() * W)
        sy = int(200 + 1600 * random.random())
        sr = int(1 + 3 * random.random())
        sa = int(40 + 60 * random.random())
        draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=(240, 210, 120, sa))

    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()))
    img.convert("RGB").save(op, "PNG", optimize=True)



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
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    make_cover(
        ROOT / a.metadata if not a.metadata.is_absolute() else a.metadata,
        ROOT / a.out if not a.out.is_absolute() else a.out,
    )


if __name__ == "__main__":
    main()