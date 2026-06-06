#!/usr/bin/env python3
"""Cover: The Clockmaker's War — militaristic fantasy, gears and clockwork soldiers."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[3]
FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    for candidate in [FONT_DIR / name, FONT_DIR / "arialbd.ttf", FONT_DIR / "arial.ttf"]:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def wrap(draw: ImageDraw.Draw, text: str, fnt: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    words = text.split()
    lines = []
    cur = []
    for wd in words:
        test = " ".join([*cur, wd])
        if draw.textbbox((0, 0), test, font=fnt)[2] <= max_w:
            cur.append(wd)
        else:
            lines.append(" ".join(cur))
            cur = [wd]
    if cur:
        lines.append(" ".join(cur))
    return lines


def centered(draw: ImageDraw.Draw, y: int, lines: list[str], fnt: ImageFont.FreeTypeFont,
             fill: tuple, gap: int = 6) -> int:
    for line in lines:
        bb = draw.textbbox((0, 0), line, font=fnt)
        x = (W - (bb[2] - bb[0])) // 2
        draw.text((x, y), line, font=fnt, fill=fill)
        y += bb[3] - bb[1] + gap
    return y


def draw_gear(draw: ImageDraw.Draw, cx: int, cy: int, radius: int, teeth: int,
              color: tuple, angle_offset: float = 0) -> None:
    """Draw a gear with given number of teeth."""
    inner_r = int(radius * 0.65)
    tooth_h = int(radius * 0.25)
    tooth_w = int(radius * 0.18)

    pts = []
    for i in range(teeth * 2):
        a = angle_offset + math.pi * i / teeth
        is_tooth = (i % 2 == 0)
        r = radius + (tooth_h if is_tooth else 0)
        w = tooth_w if is_tooth else 0
        # taper the tooth base slightly
        if is_tooth:
            a1 = a - tooth_w / (radius * 2)
            a2 = a + tooth_w / (radius * 2)
            pts.append((cx + math.cos(a1) * (radius), cy + math.sin(a1) * (radius)))
            pts.append((cx + math.cos(a2) * (radius), cy + math.sin(a2) * (radius)))
            pts.append((cx + math.cos(a2) * (radius + tooth_h), cy + math.sin(a2) * (radius + tooth_h)))
            pts.append((cx + math.cos(a1) * (radius + tooth_h), cy + math.sin(a1) * (radius + tooth_h)))
        else:
            pts.append((cx + math.cos(a) * inner_r, cy + math.sin(a) * inner_r))
    if pts:
        draw.polygon(pts, fill=color)
    # center hole
    draw.ellipse((cx - inner_r // 2, cy - inner_r // 2, cx + inner_r // 2, cy + inner_r // 2),
                 fill=(5, 5, 10, 255))


def draw_clockwork_soldier(draw: ImageDraw.Draw, cx: int, base_y: int, scale: float) -> None:
    """Draw a silhouette of a clockwork soldier."""
    s = scale
    # Legs
    leg_w = int(20 * s)
    leg_h = int(180 * s)
    draw.rectangle((cx - leg_w - int(15 * s), base_y - leg_h, cx - int(15 * s), base_y),
                   fill=(15, 12, 10, 220))
    draw.rectangle((cx + int(15 * s), base_y - leg_h, cx + leg_w + int(15 * s), base_y),
                   fill=(15, 12, 10, 220))
    # Boots
    boot_w = int(35 * s)
    boot_h = int(25 * s)
    draw.rectangle((cx - leg_w - int(20 * s), base_y - boot_h, cx - int(10 * s), base_y),
                   fill=(8, 6, 5, 240))
    draw.rectangle((cx + int(10 * s), base_y - boot_h, cx + leg_w + int(20 * s), base_y),
                   fill=(8, 6, 5, 240))
    # Torso
    torso_w = int(80 * s)
    torso_h = int(130 * s)
    draw.rectangle((cx - torso_w // 2, base_y - leg_h - torso_h, cx + torso_w // 2, base_y - leg_h),
                   fill=(20, 18, 15, 230))
    # Chest gear (heart-key visible)
    gear_cy = base_y - leg_h - torso_h // 2
    draw_gear(draw, cx, gear_cy, int(18 * s), 8, (60, 55, 40, 200), math.pi / 8)
    draw.ellipse((cx - int(6 * s), gear_cy - int(6 * s), cx + int(6 * s), gear_cy + int(6 * s)),
                 fill=(80, 20, 15, 220))
    # Arms
    arm_w = int(15 * s)
    arm_h = int(110 * s)
    # Left arm (raised slightly, holding rifle suggestion)
    draw.rectangle((cx - torso_w // 2 - arm_w, base_y - leg_h - torso_h + int(20 * s),
                    cx - torso_w // 2, base_y - leg_h - torso_h + int(20 * s) + arm_h),
                   fill=(15, 12, 10, 220))
    # Rifle line
    draw.line((cx - torso_w // 2 - int(20 * s), base_y - leg_h - torso_h - int(10 * s),
               cx - torso_w // 2 - int(5 * s), base_y - leg_h - torso_h + arm_h + int(10 * s)),
              fill=(8, 6, 5, 230), width=int(6 * s))
    # Right arm
    draw.rectangle((cx + torso_w // 2, base_y - leg_h - torso_h + int(30 * s),
                    cx + torso_w // 2 + arm_w, base_y - leg_h - torso_h + int(30 * s) + arm_h),
                   fill=(15, 12, 10, 220))
    # Head
    head_r = int(30 * s)
    draw.ellipse((cx - head_r, base_y - leg_h - torso_h - head_r - int(10 * s),
                  cx + head_r, base_y - leg_h - torso_h - int(10 * s)),
                 fill=(25, 22, 20, 230))
    # Visor/eyes (glowing)
    draw.rectangle((cx - int(12 * s), base_y - leg_h - torso_h - head_r,
                    cx + int(12 * s), base_y - leg_h - torso_h - head_r + int(5 * s)),
                   fill=(180, 60, 30, 220))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    meta = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = meta["title"]
    author = meta.get("author", "Barış Kısır")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Gradient background: dark gunmetal to brass
    for y in range(H):
        t = y / H
        r = int(15 + 30 * t)
        g = int(15 + 25 * t)
        b = int(20 + 15 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # Battlefield smoke/cloud layers
    random.seed(42)
    for layer in range(3):
        alpha = 15 + layer * 10
        for _ in range(20):
            cx = int(W * random.uniform(-0.2, 1.2))
            cy = int(H * (0.3 + layer * 0.15 + random.uniform(-0.05, 0.05)))
            cr = int(100 + 200 * random.random())
            draw.ellipse((cx - cr, cy - cr // 2, cx + cr, cy + cr // 2),
                         fill=(40, 35, 30, alpha))

    # Background gears — large, faded
    for i in range(6):
        gx = int(W * (0.1 + 0.8 * random.random()))
        gy = int(H * (0.15 + 0.5 * random.random()))
        gr = int(40 + 100 * random.random())
        g_teeth = 8 + i * 2
        gc = (55 + i * 10, 50 + i * 8, 40 + i * 5, 60)
        draw_gear(draw, gx, gy, gr, g_teeth, gc, random.random() * math.pi)

    # Main clockwork soldier (left-center)
    draw_clockwork_soldier(draw, int(W * 0.35), int(H * 0.65), 1.1)

    # Second soldier (right, smaller, more faded)
    draw_clockwork_soldier(draw, int(W * 0.72), int(H * 0.58), 0.7)

    # Foreground gears — detailed
    draw_gear(draw, W // 2, int(H * 0.42), 45, 12, (80, 70, 50, 180), math.pi / 6)
    draw_gear(draw, int(W * 0.2), int(H * 0.55), 30, 10, (70, 60, 40, 160), math.pi / 4)
    draw_gear(draw, int(W * 0.85), int(H * 0.35), 35, 10, (75, 65, 45, 150), math.pi / 3)

    # Battlefield ground texture
    for x in range(0, W, 20):
        ground_y = int(H * 0.72 + 30 * math.sin(x * 0.01) + 20 * math.sin(x * 0.03))
        draw.line((x, ground_y, x + 20, ground_y + 10 * math.sin((x + 5) * 0.02)),
                  fill=(30, 25, 20, 180), width=3)

    # Sparks / fire in the background
    for _ in range(30):
        sx = int(W * random.uniform(0.1, 0.9))
        sy = int(H * random.uniform(0.15, 0.5))
        sr = int(2 + 5 * random.random())
        draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr),
                     fill=(200 + int(55 * random.random()), 80 + int(80 * random.random()),
                            20 + int(30 * random.random()), 150 + int(105 * random.random())))

    # Title panel at bottom
    draw.rectangle((0, 1920, W, H), fill=(8, 8, 12, 245))

    # Subtle brass line accents
    draw.line((80, 1970, W - 80, 1970), fill=(160, 140, 80, 180), width=2)
    draw.line((80, H - 120, W - 80, H - 120), fill=(160, 140, 80, 100), width=1)

    # Title — large, white, bold, using arialbd.ttf
    title_fnt = font("arialbd.ttf", 110)
    title_lines = wrap(draw, title.upper(), title_fnt, W - 160)

    # Author — smaller, white
    author_fnt = font("arial.ttf", 36)

    # Calculate positions
    panel_top = 1920
    panel_bot = H
    panel_mid = (panel_top + panel_bot) // 2

    # Title block height estimate
    title_h = sum(draw.textbbox((0, 0), l, font=title_fnt)[3] - draw.textbbox((0, 0), l, font=title_fnt)[1] + 10
                  for l in title_lines)
    author_h = draw.textbbox((0, 0), author, font=author_fnt)[3] - draw.textbbox((0, 0), author, font=author_fnt)[1]

    total_h = title_h + 30 + author_h
    start_y = panel_mid - total_h // 2

    # Draw title in white
    y = start_y
    for line in title_lines:
        bb = draw.textbbox((0, 0), line, font=title_fnt)
        lw = bb[2] - bb[0]
        draw.text(((W - lw) // 2, y), line, font=title_fnt, fill=(255, 255, 255, 255))
        y += bb[3] - bb[1] + 10

    # Divider line
    y += 10
    draw.line((W // 2 - 80, y, W // 2 + 80, y), fill=(160, 140, 80, 200), width=2)
    y += 20

    # Author in white
    bb = draw.textbbox((0, 0), author, font=author_fnt)
    aw = bb[2] - bb[0]
    draw.text(((W - aw) // 2, y), author, font=author_fnt, fill=(255, 255, 255, 220))

    # Subtle vignette overlay
    for y in range(H):
        edge = min(y, H - y, 100)
        if edge < 100:
            t = (100 - edge) / 100
            px = img.getpixel((W // 2, y))
            if len(px) == 4:
                nr = max(0, int(px[0] - 30 * t))
                ng = max(0, int(px[1] - 30 * t))
                nb = max(0, int(px[2] - 30 * t))
                draw.line((0, y, W, y), fill=(nr, ng, nb, 255))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()))
    img.convert("RGB").save(output_path, "PNG", optimize=True)



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
    meta_path = ROOT / args.metadata if not args.metadata.is_absolute() else args.metadata
    out_path = ROOT / args.out if not args.out.is_absolute() else args.out
    make_cover(meta_path, out_path)


if __name__ == "__main__":
    main()