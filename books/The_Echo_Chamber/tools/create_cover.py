#!/usr/bin/env python3
"""Cover: The Echo Chamber — social media interface, fragmented face, neon colors."""

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

    # Gradient background — deep purple to black with neon pink accent
    for y in range(H):
        t = y / H
        if t < 0.6:
            r = int(40 + 30 * (t / 0.6))
            g = int(5 + 10 * (t / 0.6))
            b = int(60 + 20 * (t / 0.6))
        else:
            r = int(70 - 70 * ((t - 0.6) / 0.4))
            g = int(15 - 15 * ((t - 0.6) / 0.4))
            b = int(80 - 80 * ((t - 0.6) / 0.4))
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # --- Social Media Interface Elements ---
    # Simulated browser/search bar at top
    draw.rectangle((40, 30, W - 40, 90), fill=(15, 10, 20, 200))
    draw.rounded_rectangle((60, 42, W - 60, 78), radius=18, fill=(30, 20, 45, 220))
    sf = font("arial.ttf", 24)
    draw.text((80, 50), "https://vote.piperprime.ai/live", font=sf, fill=(180, 120, 200, 200))

    # Simulated notification bars
    for i, (y_pos, label, count) in enumerate(
        [
            (120, "piperprime", "LIVE"),
            (160, "piperprime.ai", "2.4M watching"),
        ]
    ):
        draw.rectangle((60, y_pos, W - 60, y_pos + 30), fill=(40, 25, 60, 180))
        nf = font("arialbd.ttf", 18)
        draw.text((75, y_pos + 4), label, font=nf, fill=(255, 100, 180, 240))
        draw.text((W - 160, y_pos + 4), count, font=font("arial.ttf", 16), fill=(255, 200, 100, 200))

    # --- Fragmented Face ---
    # Base oval for face silhouette
    face_cx, face_cy = W // 2, 700
    face_w, face_h = 280, 360
    # Create face layer
    face_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(face_layer)

    # Face outline
    fd.ellipse(
        (face_cx - face_w // 2, face_cy - face_h // 2, face_cx + face_w // 2, face_cy + face_h // 2),
        outline=(255, 100, 180, 120),
        width=3,
    )

    # Fragmented pixel blocks that make up the face
    block_size = 24
    for y_off in range(-face_h // 2 + 20, face_h // 2 - 20, block_size):
        for x_off in range(-face_w // 2 + 20, face_w // 2 - 20, block_size):
            px, py = face_cx + x_off, face_cy + y_off
            # Check if inside ellipse
            dx = (x_off / (face_w // 2)) ** 2
            dy = (y_off / (face_h // 2)) ** 2
            if dx + dy <= 1.0:
                # Random glitch offset or missing block
                rand = random.random()
                if rand < 0.3:
                    # Missing block - skip
                    continue
                elif rand < 0.45:
                    # Displaced block
                    shift_x = int(random.gauss(0, 30))
                    shift_y = int(random.gauss(0, 20))
                    block_color = (
                        random.randint(180, 255),
                        random.randint(80, 160),
                        random.randint(150, 220),
                        random.randint(100, 200),
                    )
                    fd.rectangle(
                        (px + shift_x, py + shift_y, px + block_size + shift_x, py + block_size + shift_y),
                        fill=block_color,
                    )
                else:
                    # Normal skin-tone block
                    brightness = random.randint(140, 200)
                    fd.rectangle(
                        (px, py, px + block_size, py + block_size),
                        fill=(brightness, brightness - 20, brightness - 10, 180),
                    )

    # Eye slits (dark bars)
    eye_size = 40
    fd.rectangle((face_cx - 60, face_cy - 50, face_cx - 10, face_cy - 30), fill=(5, 3, 10, 220))
    fd.rectangle((face_cx + 10, face_cy - 50, face_cx + 60, face_cy - 30), fill=(5, 3, 10, 220))

    # Mouth line
    fd.line(
        (face_cx - 50, face_cy + 100, face_cx + 50, face_cy + 100),
        fill=(5, 3, 10, 200),
        width=4,
    )

    # Apply glitch chromatic shift
    shift_amount = 8
    r_layer, g_layer, b_layer, a_layer = face_layer.split()
    r_shifted = Image.new("L", (W, H), 0)
    r_shifted.paste(r_layer, (shift_amount, 0))
    g_shifted = Image.new("L", (W, H), 0)
    g_shifted.paste(g_layer, (0, 0))
    b_shifted = Image.new("L", (W, H), 0)
    b_shifted.paste(b_layer, (-shift_amount, 0))
    glitch_face = Image.merge("RGBA", (r_shifted, g_shifted, b_shifted, a_layer))
    glitch_face = glitch_face.filter(ImageFilter.GaussianBlur(1))
    img = Image.alpha_composite(img, glitch_face)
    draw = ImageDraw.Draw(img, "RGBA")

    # --- Scan lines overlay ---
    for sy in range(0, int(H * 0.7), 4):
        draw.line((0, sy, W, sy), fill=(255, 255, 255, 8))

    # --- Horizontal glitch bars ---
    for _ in range(12):
        gy = random.randint(100, 1300)
        gh = random.randint(2, 6)
        draw.rectangle((0, gy, W, gy + gh), fill=(255, 100, 180, random.randint(20, 50)))

    # --- Floating UI elements ---
    # "VERIFIED" badges
    for bx, by in [(200, 850), (1200, 920), (350, 1050)]:
        draw.rounded_rectangle(
            (bx, by, bx + 90, by + 24),
            radius=12,
            fill=(255, 100, 180, 160),
        )
        draw.text((bx + 12, by + 2), "AI", font=font("arialbd.ttf", 14), fill=(0, 0, 0, 220))

    # Stats counters
    for sx, sy, label, val in [
        (150, 450, "Followers", "2.4M"),
        (W - 300, 450, "Likelihood", "99.7%"),
        (100, 600, "Trust Score", "∞"),
    ]:
        draw.text((sx, sy), label, font=font("arial.ttf", 16), fill=(180, 160, 200, 160))
        draw.text((sx, sy + 22), val, font=font("arialbd.ttf", 28), fill=(255, 100, 180, 220))

    # Data points / matrix rain effect in background
    for _ in range(40):
        mx = random.randint(0, W)
        my = random.randint(0, int(H * 0.7))
        mlen = random.randint(3, 12)
        for mi in range(mlen):
            draw.text(
                (mx, my + mi * 16),
                random.choice("010110101001"),
                font=font("arial.ttf", 12),
                fill=(100, 60, 180, random.randint(10, 40)),
            )

    # --- Title Panel ---
    # Light rectangle panel at bottom
    draw.rectangle((0, 1920, W, H), fill=(235, 228, 220, 240))
    # Decorative top line
    draw.line((120, 1930, W - 120, 1930), fill=(255, 100, 180, 180), width=3)
    # Bottom line
    draw.line((120, H - 100, W - 120, H - 100), fill=(200, 190, 180, 120), width=2)

    # Title
    tf = font("georgiab.ttf", 100)
    wrapped_title = wrap(draw, title, tf, 1300)
    y = centered(draw, 1990, wrapped_title, tf, (25, 15, 30), 8)

    # Author name
    y += 40
    af = font("arialbd.ttf", 40)
    centered(draw, y, [author], af, (80, 60, 100), 6)

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