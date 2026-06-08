#!/usr/bin/env python3
"""Cover: The Marginalia — medieval manuscript, candlelight, parchment, hidden text."""

from __future__ import annotations
import argparse, json, math, random
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
    title, author = m["title"], m.get("author", "Barış Kísır")
    model = m.get("model", "")

    # Base: aged parchment gradient
    img = Image.new("RGBA", (W, H), (245, 240, 235, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Parchment aging gradient: top lighter, bottom darker and more brown
    for y in range(H):
        t = y / H
        r = int(245 - 35 * t)
        g = int(240 - 40 * t)
        b = int(235 - 45 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # Paper stains and aging spots
    random.seed(hash((title, author)))
    for _ in range(180):
        sx = int(random.random() * W)
        sy = int(random.random() * H)
        sr = int(30 + random.random() * 80)
        stain_alpha = int(5 + random.random() * 15)
        draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=(120, 90, 60, stain_alpha))

    # Burnt edge effect on left side
    for x in range(0, 80):
        t = x / 80
        alpha = int(30 * t)
        draw.line((x, 0, x, H), fill=(60, 40, 20, alpha))

    # Candlelight glow from upper left
    candle_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cg_draw = ImageDraw.Draw(candle_glow)
    candle_x, candle_y = 200, 300
    for r in range(400, 0, -10):
        alpha = int(8 * (1 - r / 400))
        cg_draw.ellipse(
            (candle_x - r, candle_y - r, candle_x + r, candle_y + r),
            fill=(255, 200, 100, alpha),
        )
    candle_glow = candle_glow.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, candle_glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Medieval border elements: interlocking geometric patterns in corners
    border_color = (139, 69, 19, 80)
    # Top left corner: interlocking circles
    for i in range(5):
        x_offset = 30 + i * 35
        draw.ellipse((x_offset - 15, 20 - 15, x_offset + 15, 20 + 15), outline=border_color, width=2)
        if i > 0:
            draw.line((x_offset - 35, 20, x_offset - 15, 20), fill=border_color, width=2)

    # Top right corner: interlocking circles
    for i in range(5):
        x_offset = W - 30 - i * 35
        draw.ellipse((x_offset - 15, 20 - 15, x_offset + 15, 20 + 15), outline=border_color, width=2)
        if i > 0:
            draw.line((x_offset + 35, 20, x_offset + 15, 20), fill=border_color, width=2)

    # Left side: vertical ornament line
    for i in range(0, H, 60):
        draw.rectangle((40, i, 45, i + 40), fill=border_color)
        draw.ellipse((35, i + 35, 50, i + 50), outline=border_color, width=2)

    # Right side: vertical ornament line
    for i in range(0, H, 60):
        draw.rectangle((W - 45, i, W - 40, i + 40), fill=border_color)
        draw.ellipse((W - 50, i + 35, W - 35, i + 50), outline=border_color, width=2)

    # Quill pen silhouette on right
    quill_x, quill_y = 1350, 1200
    # Feather
    feather_pts = [
        (quill_x - 80, quill_y - 100),
        (quill_x - 20, quill_y - 150),
        (quill_x + 20, quill_y - 100),
        (quill_x + 40, quill_y),
        (quill_x, quill_y + 50),
        (quill_x - 40, quill_y),
    ]
    draw.polygon(feather_pts, fill=(80, 60, 40, 120))
    # Barbs on feather
    for i in range(5):
        t = i / 5
        bx = quill_x - 80 + 160 * t
        by = quill_y - 100 - 50 * math.sin(t * math.pi)
        draw.line((bx, by, bx - 30, by - 20), fill=(100, 80, 60, 100), width=2)

    # Quill shaft
    draw.rectangle((quill_x - 8, quill_y + 50, quill_x + 8, quill_y + 400), fill=(50, 30, 10, 150))
    # Nib
    draw.polygon([(quill_x - 6, quill_y + 400), (quill_x + 6, quill_y + 400), (quill_x + 3, quill_y + 430)], fill=(40, 30, 20, 200))

    # Hidden text suggestion: faint watermark-like text scattered
    hint_font = font("georgia.ttf", 20)
    hint_words = ["sealed", "sleep", "rite", "crypt", "vigil"]
    for _ in range(8):
        word = random.choice(hint_words)
        hx = int(random.random() * (W - 200)) + 100
        hy = int(random.random() * (H - 800)) + 400
        draw.text((hx, hy), word, font=hint_font, fill=(100, 80, 60, 25))

    # Illuminated capital letter style: a large decorated "M" or "A"
    illu_x, illu_y = 150, 600
    illu_font = font("georgiab.ttf", 180)
    illu_text = "M"
    illu_bb = draw.textbbox((0, 0), illu_text, font=illu_font)
    # Gold background for illuminated letter
    gold_pad = 30
    draw.rectangle(
        (illu_x - gold_pad, illu_y - gold_pad, illu_x + (illu_bb[2] - illu_bb[0]) + gold_pad, illu_y + (illu_bb[3] - illu_bb[1]) + gold_pad),
        fill=(200, 150, 50, 100),
        outline=(180, 120, 30, 180),
        width=3
    )
    # Letter with decorative color
    draw.text((illu_x, illu_y), illu_text, font=illu_font, fill=(100, 40, 20, 220))

    # Decorative frame around letter
    frame_x = illu_x - gold_pad - 10
    frame_y = illu_y - gold_pad - 10
    frame_w = (illu_bb[2] - illu_bb[0]) + 2 * (gold_pad + 10)
    frame_h = (illu_bb[3] - illu_bb[1]) + 2 * (gold_pad + 10)
    draw.rectangle((frame_x, frame_y, frame_x + frame_w, frame_y + frame_h), outline=(140, 100, 30, 150), width=2)
    draw.rectangle((frame_x + 5, frame_y + 5, frame_x + frame_w - 5, frame_y + frame_h - 5), outline=(180, 140, 60, 120), width=1)

    # Title panel at bottom
    draw.rectangle((0, 1920, W, H), fill=(210, 195, 170, 245))
    # Decorative top border
    draw.line((150, 1960, W - 150, 1960), fill=(100, 40, 20, 200), width=4)
    # Decorative bottom border
    draw.line((150, H - 100, W - 150, H - 100), fill=(100, 40, 20, 180), width=3)

    # Title text
    tf = font("georgiab.ttf", 110)
    af = font("arialbd.ttf", 42)
    sf = font("arial.ttf", 28)

    y = 2010
    y = centered(draw, y, ["A MEDIEVAL MYSTERY"], sf, (80, 40, 20), 4)
    y += 30
    wrapped_title = wrap(draw, title.upper(), tf, 1200)
    y = centered(draw, y, wrapped_title, tf, (100, 50, 20), 10)
    y += 50
    centered(draw, y, [author], af, (120, 70, 30), 6)

    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
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
    return "Barış Kísır"


def _draw_standard_cover_title_panel(image, title: str = "", author: str = "", model: str = "") -> None:
    width = int(globals().get("W", globals().get("WIDTH", 1600)))
    height = int(globals().get("H", globals().get("HEIGHT", 2560)))
    panel_y = 1765
    title = _standard_cover_repair_text(str(title or "")).strip()
    author = _standard_cover_repair_text(str(author or "Barış Kísır")).strip()
    model = _standard_cover_repair_text(str(model or "")).strip()

    draw = ImageDraw.Draw(image, "RGBA")
    draw.rectangle((0, panel_y, width, height), fill=(210, 195, 170, 255))
    draw.line((180, panel_y + 17, width - 180, panel_y + 17), fill=(100, 40, 20, 150), width=3)

    title_font, title_lines, title_gap = _standard_cover_title_font(draw, title, 1260)
    author_font = _standard_cover_font("arialbd.ttf", 50)
    model_font = _standard_cover_font("arial.ttf", 24)
    title_height = sum(draw.textbbox((0, 0), line, font=title_font)[3] - draw.textbbox((0, 0), line, font=title_font)[1] for line in title_lines)
    title_height += max(0, len(title_lines) - 1) * title_gap
    author_bbox = draw.textbbox((0, 0), author, font=author_font)
    author_height = author_bbox[3] - author_bbox[1]
    block_height = title_height + 120 + author_height
    y = panel_y + 120 + max(0, (height - panel_y - 210 - block_height) // 2)
    y = _standard_cover_center(draw, y, title_lines, title_font, (80, 40, 20), title_gap, width)
    y += 120
    _standard_cover_center(draw, y, [author], author_font, (100, 50, 20), 12, width)
    if model:
        _standard_cover_center(draw, height - 80, [model], model_font, (100, 80, 60), 6, width)


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
