#!/usr/bin/env python3
"""Cover: The Children of the Flood — generation ship interior with starfield."""

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
    title, author = m["title"], m.get("author", "Barış Kısır")
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Deep space gradient: dark blue-gray to black
    for y in range(H):
        t = y / H
        r = int(20 - 15 * t)
        g = int(25 - 20 * t)
        b = int(45 - 30 * t)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Starfield layer
    random.seed(42)
    star_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(star_layer)
    # Tiny stars
    for _ in range(400):
        sx = int(random.random() * W)
        sy = int(random.random() * H * 0.85)
        sr = 1 + int(2 * random.random())
        brightness = int(150 + 105 * random.random())
        sd.ellipse((sx - sr, sy - sr, sx + sr, sy + sr),
                    fill=(brightness, brightness, int(brightness * 0.95), 200 + int(55 * random.random())))
    # Brighter stars
    for _ in range(80):
        sx = int(random.random() * W)
        sy = int(random.random() * H * 0.85)
        sr = 2 + int(3 * random.random())
        sd.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=(220, 230, 255, 220))
    # Glow around bright stars
    glow_layer = star_layer.filter(ImageFilter.GaussianBlur(6))
    star_layer = Image.alpha_composite(glow_layer, star_layer)
    img = Image.alpha_composite(img, star_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # Generation ship window frame (large curved viewport)
    # Outer frame - dark metal
    frame_color = (35, 40, 48, 255)
    inner_color = (55, 62, 72, 255)
    highlight = (80, 88, 98, 180)

    # Main viewport arch
    vp_left = 100
    vp_right = W - 100
    vp_top = 200
    vp_bottom = 1700

    # Window frame - thick border with rivets
    draw.rectangle((vp_left - 40, vp_top - 40, vp_right + 40, vp_bottom + 40), fill=frame_color)
    draw.rectangle((vp_left - 20, vp_top - 20, vp_right + 20, vp_bottom + 20), fill=inner_color)
    # Window opening (semi-transparent dark to show stars through)
    draw.rectangle((vp_left, vp_top, vp_right, vp_bottom), fill=(15, 18, 28, 180))

    # Ship interior structure - bulkhead panels flanking the window
    # Left bulkhead
    draw.rectangle((0, 0, vp_left - 25, H), fill=(42, 48, 55, 255))
    # Right bulkhead
    draw.rectangle((vp_right + 25, 0, W, H), fill=(42, 48, 55, 255))

    # Bulkhead panel lines
    for bx in [vp_left - 35, vp_right + 25]:
        draw.line((bx, 0, bx, H), fill=(60, 68, 78, 200), width=2)

    # Rivets along frame
    for ry in range(vp_top, vp_bottom + 1, 80):
        for rx in [vp_left - 30, vp_left - 10, vp_right + 10, vp_right + 30]:
            draw.ellipse((rx - 4, ry - 4, rx + 4, ry + 4), fill=(70, 78, 88, 220))
            draw.ellipse((rx - 2, ry - 2, rx + 2, ry + 2), fill=(100, 110, 120, 200))

    # Horizontal support beam across the window
    beam_y = vp_top + 600
    draw.rectangle((vp_left, beam_y - 15, vp_right, beam_y + 15), fill=(50, 56, 65, 220))
    # Beam rivets
    for bx in range(vp_left + 50, vp_right, 100):
        draw.ellipse((bx - 5, beam_y - 5, bx + 5, beam_y + 5), fill=(75, 82, 92, 200))

    # Console / control panel at bottom of viewport
    panel_y = vp_bottom - 120
    draw.rectangle((vp_left + 20, panel_y, vp_right - 20, vp_bottom), fill=(30, 35, 42, 240))
    # Screen glow on console
    for sx in range(vp_left + 50, vp_right - 50, 90):
        draw.rectangle((sx, panel_y + 15, sx + 60, panel_y + 50), fill=(25, 80, 120, 200))
        draw.rectangle((sx + 2, panel_y + 17, sx + 58, panel_y + 48), fill=(40, 120, 180, 180))

    # Console indicator lights
    for lx in range(vp_left + 40, vp_right - 30, 40):
        draw.ellipse((lx, panel_y + 65, lx + 8, panel_y + 73), fill=(180, 60, 60, 200))
        draw.ellipse((lx + 12, panel_y + 65, lx + 20, panel_y + 73), fill=(60, 180, 60, 200))
        draw.ellipse((lx + 24, panel_y + 65, lx + 32, panel_y + 73), fill=(60, 120, 200, 200))

    # Cross-bracing cables on left and right bulkheads
    for offset in range(100, H - 100, 200):
        draw.line((0, offset, vp_left - 25, offset + 30), fill=(55, 62, 72, 100), width=2)
        draw.line((vp_right + 25, offset, W, offset + 30), fill=(55, 62, 72, 100), width=2)

    # Floor grating at the bottom
    for fy in range(1800, H, 12):
        draw.line((0, fy, W, fy), fill=(45, 50, 58, 60))
    for fx in range(0, W, 25):
        draw.line((fx, 1800, fx, H), fill=(45, 50, 58, 40))

    # Nebula glow through window
    nebula = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(nebula)
    nd.ellipse((W // 2 - 400, 400, W // 2 + 400, 800), fill=(30, 60, 120, 30))
    nd.ellipse((W // 2 - 300, 500, W // 2 + 300, 700), fill=(40, 80, 160, 20))
    nebula = nebula.filter(ImageFilter.GaussianBlur(60))
    img = Image.alpha_composite(img, nebula)
    draw = ImageDraw.Draw(img, "RGBA")

    # Title panel at bottom
    draw.rectangle((0, 1920, W, H), fill=(18, 20, 28, 245))
    # Thin accent lines
    draw.line((200, 1940, W - 200, 1940), fill=(100, 160, 220, 180), width=2)
    draw.line((200, H - 140, W - 200, H - 140), fill=(100, 160, 220, 120), width=2)

    # Small tagline
    tf = font("georgiab.ttf", 100)
    af = font("arialbd.ttf", 44)
    sf = font("arial.ttf", 28)

    centered(draw, 1970, ["A GENERATION SHIP NOVEL"], sf, (130, 170, 210), 4)
    y = 2040
    wrapped_title = wrap(draw, title.upper(), tf, 1200)
    centered(draw, y, wrapped_title, tf, (200, 210, 230), 10)
    y += len(wrapped_title) * 110 + 60
    centered(draw, y, [author], af, (170, 180, 200), 6)

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