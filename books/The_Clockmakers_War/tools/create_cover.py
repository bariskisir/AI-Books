#!/usr/bin/env python3
"""Cover: The Clockmaker's War — militaristic fantasy, gears and clockwork soldiers."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import (
    _standard_cover_font,
    _standard_cover_repair_text,
    _standard_cover_wrap,
    _standard_cover_center,
    _standard_cover_title_font,
    _standard_cover_metadata_from_locals,
    _standard_cover_resolve_title,
    _standard_cover_resolve_author,
    _draw_standard_cover_title_panel,
)


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
    model = meta.get("model", "")

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

    # Subtle brass line accents
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
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(output_path, "PNG", optimize=True)



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