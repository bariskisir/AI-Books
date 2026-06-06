#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Thirty-Seventh Floor."""

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


def wrap_title(draw, text, font, max_width):
    """Wrap title text to fit within max_width."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return "\n".join(lines)


def create_cover(metadata_path, output_path):
    # Load metadata
    with open(metadata_path, encoding="utf-8") as f:
        metadata = json.load(f)

    title = metadata["title"]
    author = metadata["author"]

    W, H = 1600, 2560

    # Create image
    img = Image.new("RGB", (W, H), "#0a0a1a")
    draw = ImageDraw.Draw(img)

    # --- Gradient background: dark blue at top, deep navy, dark near-black at bottom ---
    for y in range(H):
        r = int(8 + (y / H) * 4)
        g = int(8 + (y / H) * 6)
        b = int(26 + (y / H) * 8 - (y / H) * 20)
        b = max(b, 5)
        draw.rectangle([(0, y), (W, y)], fill=(r, g, b))

    # --- Stars ---
    import random
    random.seed(42)
    for _ in range(200):
        sx = random.randint(0, W)
        sy = random.randint(0, int(H * 0.45))
        brightness = random.randint(120, 255)
        size = random.choice([1, 2])
        draw.ellipse(
            [(sx - size, sy - size), (sx + size, sy + size)],
            fill=(brightness, brightness, max(brightness - 30, 0)),
        )

    # --- Moon ---
    moon_x, moon_y = 1200, 200
    draw.ellipse(
        [(moon_x - 60, moon_y - 60), (moon_x + 60, moon_y + 60)],
        fill=(220, 220, 200),
    )
    # Moon glow
    for r in range(80, 120, 10):
        alpha = max(0, 30 - r)
        draw.ellipse(
            [(moon_x - r, moon_y - r), (moon_x + r, moon_y + r)],
            fill=(60, 60, 80, alpha),
        )

    # --- Skyscraper ---
    # Main tower body
    tower_x, tower_w = 580, 320
    tower_h = int(H * 0.65)
    tower_y = int(H * 0.08)
    # Tower gradient
    for y in range(tower_y, tower_y + tower_h):
        progress = (y - tower_y) / tower_h
        r = int(20 + progress * 10)
        g = int(20 + progress * 10)
        b = int(30 + progress * 15)
        draw.rectangle(
            [(tower_x, y), (tower_x + tower_w, y + 1)],
            fill=(r, g, b),
        )

    # Tower outline
    draw.rectangle(
        [(tower_x, tower_y), (tower_x + tower_w, tower_y + tower_h)],
        outline=(70, 70, 90),
        width=2,
    )

    # Vertical window columns
    cols = 12
    col_w = tower_w // cols
    window_h = 18
    window_gap = 22
    floor_count = tower_h // window_gap

    for floor in range(floor_count):
        fy = tower_y + floor * window_gap + 8
        if fy > tower_y + tower_h - 10:
            break
        for col in range(cols):
            fx = tower_x + col * col_w + 4
            if fx + col_w // 3 > tower_x + tower_w - 4:
                break
            lit = random.random() > 0.55
            if lit:
                # Warm window glow
                r, g, b = random.choice([
                    (255, 220, 140),
                    (255, 200, 100),
                    (240, 180, 80),
                    (255, 230, 170),
                ])
                draw.rectangle(
                    [(fx, fy), (fx + col_w // 3, fy + window_h)],
                    fill=(r, g, b),
                )
                # Window glow spill
                for glow_r in [4, 8]:
                    alpha = 40 if glow_r == 4 else 15
                    draw.ellipse(
                        [(fx + 2 - glow_r, fy + 4 - glow_r),
                         (fx + 2 + glow_r, fy + 4 + glow_r)],
                        fill=(r, g, b, alpha),
                    )
            else:
                # Dark window with slight reflection
                draw.rectangle(
                    [(fx, fy), (fx + col_w // 3, fy + window_h)],
                    fill=(25, 28, 40),
                )

    # --- Dark band at 37th floor level ---
    band_y = tower_y + int(tower_h * 0.35)
    band_h = int(tower_h * 0.04)
    # Dark band across the tower
    for y in range(band_y, band_y + band_h):
        dark = int(3 + (y - band_y) / band_h * 4)
        draw.rectangle(
            [(tower_x, y), (tower_x + tower_w, y + 1)],
            fill=(dark, dark, dark + 2),
        )
    # Red accent line on the dark band
    draw.rectangle(
        [(tower_x, band_y), (tower_x + tower_w, band_y + 2)],
        fill=(180, 20, 20),
    )

    # --- Additional buildings silhouettes ---
    def draw_silhouette(x, w, h, y_base):
        for y in range(y_base, y_base + h):
            progress = (y - y_base) / h
            r = int(8 + progress * 4)
            g = int(10 + progress * 4)
            b = int(15 + progress * 6)
            draw.rectangle(
                [(x, y), (x + w, y + 1)],
                fill=(r, g, b),
            )
        draw.rectangle(
            [(x, y_base), (x + w, y_base + h)],
            outline=(30, 32, 45),
            width=1,
        )

    # Left buildings
    draw_silhouette(100, 120, tower_h - 80, tower_y + 80)
    draw_silhouette(250, 100, tower_h - 40, tower_y + 40)
    draw_silhouette(370, 80, tower_h - 120, tower_y + 120)
    # Right buildings
    draw_silhouette(950, 110, tower_h - 60, tower_y + 60)
    draw_silhouette(1090, 90, tower_h - 100, tower_y + 100)
    draw_silhouette(1250, 140, tower_h - 30, tower_y + 30)
    draw_silhouette(1420, 100, tower_h - 90, tower_y + 90)

    # Small windows on silhouettes
    for bx, bw, bh, by in [
        (100, 120, tower_h - 80, tower_y + 80),
        (250, 100, tower_h - 40, tower_y + 40),
        (950, 110, tower_h - 60, tower_y + 60),
        (1250, 140, tower_h - 30, tower_y + 30),
    ]:
        for yy in range(by + 10, by + bh - 10, 25):
            for xx in range(bx + 6, bx + bw - 6, bx + bw // 5):
                if random.random() > 0.6:
                    draw.rectangle(
                        [(xx, yy), (xx + 6, yy + 10)],
                        fill=(random.randint(200, 255), random.randint(180, 230), random.randint(100, 180)),
                    )

    # --- Light glow around the dark band ---
    for gr in range(10, 40, 5):
        alpha = max(0, 60 - gr * 2)
        glow_color = (180, 20, 20, alpha)
        draw.ellipse(
            [(tower_x - gr, band_y - gr),
             (tower_x + tower_w + gr, band_y + band_h + gr)],
            fill=glow_color,
        )

    # --- Title panel at bottom ---
    panel_y = 1920
    panel_h = 640
    # Gradient panel
    for y in range(panel_y, panel_y + panel_h):
        progress = (y - panel_y) / panel_h
        r = int(200 + progress * 30)
        g = int(195 + progress * 30)
        b = int(190 + progress * 30)
        draw.rectangle(
            [(0, y), (W, y + 1)],
            fill=(min(r, 255), min(g, 255), min(b, 255)),
        )
    # Panel top border
    draw.rectangle([(0, panel_y), (W, panel_y + 3)], fill=(180, 20, 20))

    # --- Load fonts ---
    try:
        title_font = ImageFont.truetype("C:/Windows/Fonts/georgiab.ttf", 80)
    except Exception:
        try:
            title_font = ImageFont.truetype("C:/Windows/Fonts/georgia.ttf", 80)
        except Exception:
            title_font = ImageFont.load_default()
    try:
        author_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 36)
    except Exception:
        try:
            author_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 36)
        except Exception:
            author_font = ImageFont.load_default()
    try:
        small_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 18)
    except Exception:
        small_font = ImageFont.load_default()

    # --- Title text ---
    max_text_width = W - 160
    wrapped = wrap_title(draw, title, title_font, max_text_width)
    lines = wrapped.split("\n")
    total_text_h = len(lines) * 100
    text_y_start = panel_y + (panel_h - total_text_h) // 2 - 20

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        tw = bbox[2] - bbox[0]
        tx = (W - tw) // 2
        draw.text((tx, text_y_start), line, fill=(25, 25, 35), font=title_font)
        text_y_start += 100

    # --- Author line ---
    author_y = panel_y + panel_h - 120
    bbox = draw.textbbox((0, 0), author, font=author_font)
    aw = bbox[2] - bbox[0]
    ax = (W - aw) // 2
    draw.text((ax, author_y), author, fill=(60, 60, 70), font=author_font)

    # --- Genre line ---
    genre = "A Conspiracy Thriller"
    bbox = draw.textbbox((0, 0), genre, font=small_font)
    gw = bbox[2] - bbox[0]
    gx = (W - gw) // 2
    draw.text((gx, author_y + 50), genre, fill=(120, 120, 130), font=small_font)

    # --- Save ---
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
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
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    create_cover(args.metadata, args.out)