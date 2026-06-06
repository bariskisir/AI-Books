#!/usr/bin/env python3
"""Cover: The Mourning Doves — Gothic romance, crumbling manor, fog, doves."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[3]
FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    candidates = [FONT_DIR / name, FONT_DIR / "georgia.ttf", FONT_DIR / "arial.ttf"]
    for c in candidates:
        if c.exists():
            return ImageFont.truetype(str(c), size)
    return ImageFont.load_default()


def wrap(draw: ImageDraw, text: str, font: ImageFont, max_w: int) -> list[str]:
    words = text.split()
    lines, current = [], []
    for w in words:
        test = " ".join([*current, w])
        if draw.textbbox((0, 0), test, font=font)[2] <= max_w:
            current.append(w)
        else:
            if current:
                lines.append(" ".join(current))
            current = [w]
    if current:
        lines.append(" ".join(current))
    return lines


def centered(
    draw: ImageDraw, y: int, lines: list[str], font: ImageFont, fill, gap: int
) -> int:
    for line in lines:
        bb = draw.textbbox((0, 0), line, font=font)
        draw.text(((W - (bb[2] - bb[0])) // 2, y), line, font=font, fill=fill)
        y += bb[3] - bb[1] + gap
    return y


def make_cover(metadata_path: Path, output_path: Path) -> None:
    meta = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = meta["title"]
    author = meta.get("author", "Barış Kısır")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Gradient background: deep violet to gray-black
    for y in range(H):
        t = y / H
        r = int(25 + 10 * t)
        g = int(12 + 8 * t)
        b = int(35 + 15 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # Moon glow
    moon = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(moon)
    md.ellipse((W - 400, 80, W - 120, 360), fill=(200, 195, 180, 120))
    moon = moon.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, moon)
    draw = ImageDraw.Draw(img)

    # Crumbling manor silhouette
    cx, cy = W // 2, 1100
    # Main body
    draw.polygon(
        [
            (cx - 450, cy + 200),
            (cx - 450, cy - 100),
            (cx - 250, cy - 100),
            (cx - 250, cy - 300),
            (cx + 250, cy - 300),
            (cx + 250, cy - 100),
            (cx + 450, cy - 100),
            (cx + 450, cy + 200),
        ],
        fill=(8, 5, 12, 230),
    )
    # Left tower
    draw.rectangle((cx - 400, cy - 450, cx - 250, cy - 300), fill=(8, 5, 12, 230))
    draw.polygon(
        [(cx - 430, cy - 450), (cx - 220, cy - 450), (cx - 325, cy - 520)],
        fill=(8, 5, 12, 230),
    )
    # Right tower
    draw.rectangle((cx + 250, cy - 480, cx + 400, cy - 300), fill=(8, 5, 12, 230))
    draw.polygon(
        [(cx + 220, cy - 480), (cx + 430, cy - 480), (cx + 325, cy - 560)],
        fill=(8, 5, 12, 230),
    )
    # Broken roof line
    draw.polygon(
        [(cx - 250, cy - 300), (cx - 150, cy - 260), (cx - 50, cy - 310),
         (cx + 50, cy - 270), (cx + 150, cy - 250), (cx + 250, cy - 300)],
        fill=(8, 5, 12, 230),
    )
    # Lit window
    draw.rectangle((cx - 30, cy - 180, cx + 30, cy - 120), fill=(160, 130, 70, 100))

    # Crumbling edges / debris
    for dx in [-460, -440, 440, 460]:
        draw.polygon(
            [(dx, cy + 200), (dx + 20, cy + 200), (dx + 10, cy + 240)],
            fill=(12, 8, 16, 200),
        )

    # Bare twisted trees
    for tx in [cx - 500, cx - 380, cx + 380, cx + 500]:
        for _ in range(6):
            sx = tx + random.randint(-20, 20)
            ex = sx + random.randint(-80, 80)
            ey = cy + 50 - random.randint(0, 100)
            draw.line(
                (sx, cy + 100, ex, ey),
                fill=(3, 2, 5, 200),
                width=random.randint(2, 4),
            )
            # Branches
            for _ in range(3):
                bx = ex + random.randint(-40, 40)
                by = ey - random.randint(20, 60)
                draw.line((ex, ey, bx, by), fill=(3, 2, 5, 180), width=2)

    # Mourning doves in sky
    for i in range(5):
        dx = 200 + i * 280 + random.randint(-30, 30)
        dy = 150 + i * 60 + random.randint(-20, 20)
        # Simple dove silhouette
        draw.ellipse((dx - 12, dy - 6, dx + 12, dy + 6), fill=(160, 155, 150, 100))
        draw.polygon(
            [(dx + 12, dy), (dx + 25, dy - 6), (dx + 20, dy + 2)],
            fill=(160, 155, 150, 100),
        )

    # Fog layers
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog)
    fd.ellipse((-300, 1400, W + 300, 1900), fill=(170, 165, 160, 25))
    fd.ellipse((-200, 1600, W + 200, 2100), fill=(180, 175, 170, 20))
    fog = fog.filter(ImageFilter.GaussianBlur(50))
    img = Image.alpha_composite(img, fog)
    draw = ImageDraw.Draw(img)

    # Bottom title panel
    draw.rectangle((0, 1920, W, H), fill=(10, 7, 14, 245))
    # Decorative lines
    draw.line((300, 1980, W - 300, 1980), fill=(140, 120, 90, 180), width=2)
    draw.line((300, H - 120, W - 300, H - 120), fill=(140, 120, 90, 80), width=1)

    # Title
    tf = font("georgiab.ttf", 100)
    af = font("arialbd.ttf", 40)
    sf = font("arial.ttf", 26)

    wrapped = wrap(draw, title.upper(), tf, 1200)
    y = centered(draw, 2010, wrapped, tf, (190, 175, 145), 8)

    # Author
    y = centered(draw, y + 50, [author], af, (170, 160, 140), 6)

    # Small genre text
    centered(draw, y + 60, ["GOTHIC ROMANCE"], sf, (120, 110, 95), 0)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()))
    img.convert("RGB").save(str(output_path), "PNG", optimize=True)



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

    mp = ROOT / args.metadata if not args.metadata.is_absolute() else args.metadata
    op = ROOT / args.out if not args.out.is_absolute() else args.out
    make_cover(mp, op)


if __name__ == "__main__":
    main()