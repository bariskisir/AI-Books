#!/usr/bin/env python3
"""Cover: The Hollow Men — foggy Appalachian forest with shadowy figures."""

from __future__ import annotations
import argparse, json, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[3]
FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    for c in [FONT_DIR / name, FONT_DIR / "georgia.ttf", FONT_DIR / "arial.ttf"]:
        if c.exists():
            return ImageFont.truetype(str(c), size)
    return ImageFont.load_default()


def wrap(draw, text, fnt, mw):
    words, lines, cur = text.split(), [], []
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
    title, author = m["title"], m.get("author", "Barış Kısır")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Muted green-gray gradient: dark top to lighter foggy bottom
    for y in range(H):
        t = y / H
        r = int(60 - 20 * t)
        g = int(70 - 15 * t)
        b = int(55 - 10 * t)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Fog layer — lighter mist rising from bottom
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fdraw = ImageDraw.Draw(fog)
    for y in range(H // 2, H):
        t = (y - H // 2) / (H // 2)
        alpha = int(80 * t)
        gray = 140 + int(60 * t)
        fdraw.line((0, y, W, y), fill=(gray, gray, gray, min(alpha, 120)))
    fog = fog.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img, fog)
    draw = ImageDraw.Draw(img, "RGBA")

    # Bare tree trunks on left and right
    tree_color = (25, 20, 18, 200)
    for side, base_x in [("L", 80), ("L", 200), ("L", 350), ("R", 1250), ("R", 1400), ("R", 1520)]:
        trunk_w = 18 + int(math.sin(base_x) * 8)
        trunk_h = 800 + int(math.cos(base_x) * 200)
        top_y = 400 + int(math.sin(base_x * 2) * 100)
        draw.rectangle((base_x, top_y, base_x + trunk_w, top_y + trunk_h), fill=tree_color)
        # Branches
        for b_off in [150, 350, 550]:
            bx = base_x + trunk_w // 2
            by = top_y + b_off
            b_len = 60 + int(math.sin(b_off) * 30)
            draw.line((bx, by, bx - b_len, by - 40), fill=tree_color, width=6)
            draw.line((bx, by, bx + b_len, by - 30), fill=tree_color, width=5)

    # Shadowy figure at center-left
    fig_color = (10, 8, 8, 200)
    fx, fy = 600, 1100
    # Body
    draw.ellipse((fx - 50, fy - 180, fx + 50, fy), fill=fig_color)
    # Head
    draw.ellipse((fx - 25, fy - 230, fx + 25, fy - 180), fill=fig_color)
    # Arms
    draw.line((fx - 50, fy - 140, fx - 100, fy - 80), fill=fig_color, width=14)
    draw.line((fx + 50, fy - 140, fx + 100, fy - 100), fill=fig_color, width=14)

    # Second shadowy figure at right, smaller
    fx2, fy2 = 1200, 1300
    draw.ellipse((fx2 - 35, fy2 - 120, fx2 + 35, fy2), fill=fig_color)
    draw.ellipse((fx2 - 18, fy2 - 155, fx2 + 18, fy2 - 120), fill=fig_color)
    draw.line((fx2 - 35, fy2 - 90, fx2 - 70, fy2 - 50), fill=fig_color, width=10)
    draw.line((fx2 + 35, fy2 - 90, fx2 + 70, fy2 - 60), fill=fig_color, width=10)

    # Empty house silhouette left background
    house_color = (20, 18, 15, 160)
    hx, hy = 250, 950
    draw.polygon([(hx, hy), (hx + 120, hy), (hx + 120, hy + 180), (hx, hy + 180)], fill=house_color)
    draw.polygon([(hx - 10, hy), (hx + 130, hy), (hx + 60, hy - 80)], fill=house_color)
    # Dark window
    draw.rectangle((hx + 30, hy + 30, hx + 60, hy + 70), fill=(5, 5, 5, 180))
    draw.rectangle((hx + 75, hy + 30, hx + 105, hy + 70), fill=(5, 5, 5, 180))
    draw.rectangle((hx + 30, hy + 100, hx + 60, hy + 140), fill=(5, 5, 5, 180))
    draw.rectangle((hx + 75, hy + 100, hx + 105, hy + 140), fill=(5, 5, 5, 180))

    # Faint mist streaks
    for _ in range(25):
        mx = int(W * __import__("random").random())
        my = int(800 + 1200 * __import__("random").random())
        mw2 = int(80 + 160 * __import__("random").random())
        mh2 = int(8 + 16 * __import__("random").random())
        a = int(15 + 25 * __import__("random").random())
        draw.ellipse((mx - mw2 // 2, my - mh2 // 2, mx + mw2 // 2, my + mh2 // 2),
                     fill=(180, 190, 180, a))

    # Title panel
    draw.rectangle((0, 1920, W, H), fill=(8, 12, 10, 235))
    draw.rectangle((0, 1920, W, 1930), fill=(60, 80, 65, 200))
    draw.line((200, 1960, W - 200, 1960), fill=(140, 160, 140, 150), width=2)

    # Title
    tf = font("georgiab.ttf", 100)
    af = font("arialbd.ttf", 40)
    sf = font("arial.ttf", 28)

    y = 2010
    y = centered(draw, y, wrap(draw, title.upper(), tf, 1300), tf, (200, 215, 200), 12)
    y += 50
    centered(draw, y, [author], af, (170, 185, 170), 8)

    # Decorative line below author
    draw.line((600, y + 60, W - 600, y + 60), fill=(100, 120, 100, 120), width=1)

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