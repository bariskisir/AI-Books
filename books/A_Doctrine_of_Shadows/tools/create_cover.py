#!/usr/bin/env python3
"""Cover: A Doctrine of Shadows — A CIA linguist decoding a dead diplomat's encrypted journal realizes the coup she helped orchestrate in West Africa was a decoy for a much larger operation aimed at the Hague."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

rng = random.Random()
rng.seed(924883015)

# ── 5x5 pixel bitmap font (compact binary encoding) ─────────────────
# Each character is 5 rows of 5 bits, packed MSB-first into a 25-bit int.
_BF = {
    'A': 0b0111010001111111000110001,
    'C': 0b0111010000100001000001110,
    'D': 0b1111010001100011000111110,
    'E': 0b1111110000111101000011111,
    'F': 0b1111110000111101000010000,
    'H': 0b1000110001111111000110001,
    'I': 0b1111100100001000010011111,
    'J': 0b0000100001000011000101110,
    'K': 0b1000110010111001001010001,
    'L': 0b1000010000100001000011111,
    'M': 0b1000111011101011000110001,
    'N': 0b1000111001101011001110001,
    'O': 0b0111010001100011000101110,
    'P': 0b1111010001111101000010000,
    'R': 0b1111010001111101001010001,
    'S': 0b0111110000011100000111110,
    'T': 0b1111100100001000010000100,
    'U': 0b1000110001100011000101110,
    'V': 0b1000110001010100010001000,
    'Y': 0b1000101010001000010000100,
    ' ': 0b0000000000000000000000000,
}
_BFW = 5  # font width in pixels


def _px(draw, x, y, text, fill, px=5):
    """Draw pixel text at (x,y) using the built-in bitmap font.
    px = size of each pixel block in output pixels.
    """
    for ch in text:
        if ch == ' ':
            x += px * 3
            continue
        pat = _BF.get(ch)
        if pat is None:
            x += px * 4
            continue
        for row in range(5):
            for col in range(5):
                if (pat >> (24 - row * 5 - col)) & 1:
                    sx = x + col * px
                    sy = y + row * px
                    draw.rectangle(
                        (sx, sy, sx + px - 1, sy + px - 1),
                        fill=fill
                    )
        x += (5 + 1) * px


def _draw_cipher(draw, x, y, size, color):
    """Draw a random geometric cipher glyph centered at (x,y)."""
    glyph_type = rng.randint(0, 5)
    col = color
    a = rng.randint(50, 130)
    if glyph_type == 0:
        # Triangle (pointing up or down)
        if rng.randint(0, 1):
            pts = [(x, y - size), (x - size, y + size), (x + size, y + size)]
        else:
            pts = [(x, y + size), (x - size, y - size), (x + size, y - size)]
        draw.polygon(pts, outline=(*col, a), width=2)
    elif glyph_type == 1:
        # Circle enclosing dot
        draw.ellipse((x - size, y - size, x + size, y + size), outline=(*col, a), width=2)
        draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(*col, min(a + 40, 200)))
    elif glyph_type == 2:
        # Diamond
        draw.polygon([
            (x, y - size), (x + size, y), (x, y + size), (x - size, y)
        ], outline=(*col, a), width=2)
        draw.line((x - size // 2, y, x + size // 2, y), fill=(*col, a // 2), width=1)
    elif glyph_type == 3:
        # Cross with terminal dots
        draw.line((x - size, y, x + size, y), fill=(*col, a), width=2)
        draw.line((x, y - size, x, y + size), fill=(*col, a), width=2)
        for dx, dy in [(size, 0), (-size, 0), (0, size), (0, -size)]:
            draw.ellipse(
                (x + dx - 3, y + dy - 3, x + dx + 3, y + dy + 3),
                fill=(*col, a),
            )
    elif glyph_type == 4:
        # Eye / oval
        draw.ellipse((x - size, y - size // 2, x + size, y + size // 2),
                     outline=(*col, a), width=2)
        draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(*col, a))
    elif glyph_type == 5:
        # Inscribed triangle in circle
        draw.ellipse((x - size, y - size, x + size, y + size), outline=(*col, a // 2), width=1)
        pts = []
        for i in range(3):
            ang = math.radians(i * 120 - 90)
            pts.append((x + int(math.cos(ang) * size * 0.8),
                         y + int(math.sin(ang) * size * 0.8)))
        draw.polygon(pts, outline=(*col, a), width=2)


# ── Main cover renderer ─────────────────────────────────────────────

def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    # ── 1. Dossier olive-green gradient ──────────────────────────────
    img = Image.new("RGBA", (W, H), (58, 52, 38, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        r = int(58 + (30 - 58) * t)
        g = int(52 + (26 - 52) * t)
        b = int(38 + (18 - 38) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── 2. Ruled document lines (faint horizontal texture) ──────────
    for y in range(80, 1765, 20):
        alpha = 18 - 8 * abs(y - 900) / 900
        draw.line((80, y, W - 80, y), fill=(65, 58, 42, max(8, int(alpha))), width=1)

    # ── 3. Large interrogation silhouette (left side) ───────────────
    # A shadowy profile head-and-shoulders looming over the composition
    silh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(silh)
    # Head profile polygon
    sd.polygon([
        (0, 280), (100, 260), (170, 270), (210, 295), (235, 325),  # top
        (248, 355), (254, 380), (253, 400),                           # forehead
        (260, 418), (256, 428),                                        # nose bridge
        (262, 440), (248, 450),                                        # nose / philtrum
        (254, 462), (244, 475), (238, 488),                           # lips / chin
        (230, 500), (218, 510), (202, 522),                           # jaw
        (190, 545), (170, 590), (150, 660),                           # neck
        (130, 780), (110, 920), (0, 1080),                            # torso
    ], fill=(15, 12, 8, 65))
    # Shoulder
    sd.polygon([
        (120, 700), (175, 740), (215, 790), (230, 840),
        (220, 900), (180, 930), (120, 910), (0, 870),
    ], fill=(15, 12, 8, 45))
    silh = silh.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img, silh)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 4. Interrogator light beam ──────────────────────────────────
    beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam)
    bd.polygon([
        (230, 440),
        (1600, 50),
        (1600, 1700),
    ], fill=(210, 185, 140, 8))
    beam = beam.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img, beam)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 5. West Africa silhouette map ───────────────────────────────
    # Stylized polygon from Mauritania / Senegal to Chad / Cameroon
    africa = [
        (290, 700), (330, 640), (390, 618), (460, 625), (525, 645),
        (585, 675), (635, 715), (675, 765), (695, 815), (705, 875),
        (685, 925), (655, 958), (615, 978), (565, 968), (525, 945),
        (495, 915), (465, 895), (435, 875), (405, 855), (375, 825),
        (345, 795), (315, 758),
    ]
    draw.polygon(africa, fill=(62, 55, 38, 160), outline=(88, 78, 54, 200), width=3)
    # Internal subtle highlight (river / border hint)
    river = [
        (460, 625), (480, 660), (495, 700), (505, 745), (510, 790),
        (500, 830), (480, 870), (455, 895),
    ]
    draw.line(river, fill=(80, 72, 50, 60), width=2)

    # ── 6. Route line: West Africa → The Hague (Bezier curve) ──────
    route_pts = []
    route_steps = 100
    for i in range(route_steps + 1):
        frac = i / route_steps
        # Control points: start (Mali), curve up-right, end (Hague)
        x = (1 - frac) ** 2 * 480 + 2 * (1 - frac) * frac * 750 + frac ** 2 * 1200
        y = (1 - frac) ** 2 * 730 + 2 * (1 - frac) * frac * 480 + frac ** 2 * 240
        route_pts.append((int(x), int(y)))

    # Faint solid trail
    for i in range(route_steps):
        a = max(8, int(60 * (1 - i / route_steps)))
        draw.line((route_pts[i], route_pts[i + 1]), fill=(190, 165, 90, a), width=2)

    # Dotted markers along the route
    for i in range(6, len(route_pts), max(1, route_steps // 14)):
        pt = route_pts[i]
        r2 = 4 if i % 2 == 0 else 2
        alpha = max(60, min(220, 100 + int(120 * (i / route_steps))))
        draw.ellipse(
            (pt[0] - r2, pt[1] - r2, pt[0] + r2, pt[1] + r2),
            fill=(200, 175, 100, alpha),
        )

    # ── 7. The Hague target marker ──────────────────────────────────
    hx, hy = 1200, 240
    # Outer ring
    draw.ellipse((hx - 18, hy - 18, hx + 18, hy + 18),
                 outline=(200, 175, 100, 200), width=3)
    # Crosshair
    draw.line((hx - 10, hy, hx + 10, hy), fill=(200, 175, 100, 200), width=2)
    draw.line((hx, hy - 10, hx, hy + 10), fill=(200, 175, 100, 200), width=2)
    # Center dot
    draw.ellipse((hx - 4, hy - 4, hx + 4, hy + 4), fill=(220, 195, 120, 230))
    # Label
    _px(draw, hx - 28, hy + 24, "HAGUE", (200, 175, 100, 180), 3)

    # ── 8. Cracked diplomatic seal ──────────────────────────────────
    sx, sy, sr = 1040, 1120, 145
    seal_color = (175, 148, 75)
    seal_dark = (60, 52, 28)

    # Outer ring thick
    draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr),
                 outline=(*seal_color, 170), width=6)
    # Outer ring thin
    draw.ellipse((sx - sr - 10, sy - sr - 10, sx + sr + 10, sy + sr + 10),
                 outline=(*seal_color, 80), width=2)
    # Inner ring
    draw.ellipse((sx - sr + 25, sy - sr + 25, sx + sr - 25, sy + sr - 25),
                 outline=(*seal_color, 110), width=2)
    # Center emblem — simple star
    star_r = sr - 55
    star_pts = []
    for i in range(10):
        angle = math.radians(i * 36 - 90)
        r2 = star_r if i % 2 == 0 else star_r // 2
        star_pts.append((sx + int(math.cos(angle) * r2),
                         sy + int(math.sin(angle) * r2)))
    draw.polygon(star_pts, outline=(*seal_color, 130), width=2)

    # Crack lines (jagged fractures radiating from center through the seal)
    for _ in range(rng.randint(3, 5)):
        angle = rng.uniform(0, math.tau)
        x1 = sx + int(math.cos(angle) * rng.randint(10, 40))
        y1 = sy + int(math.sin(angle) * rng.randint(10, 40))
        prev = (x1, y1)
        segs = rng.randint(3, 6)
        for _ in range(segs):
            ang2 = angle + rng.uniform(-0.4, 0.4)
            dist = rng.randint(20, 45)
            nx = prev[0] + int(math.cos(ang2) * dist)
            ny = prev[1] + int(math.sin(ang2) * dist)
            # Stop if outside the seal
            if ((nx - sx) ** 2 + (ny - sy) ** 2) ** 0.5 > sr + 15:
                draw.line((prev, (nx, ny)), fill=(*seal_dark, 120), width=2)
                break
            draw.line((prev, (nx, ny)), fill=(*seal_dark, 160), width=3)
            prev = (nx, ny)
        # Extra crack branching
        if rng.random() < 0.5:
            branch_ang = angle + rng.uniform(0.3, 0.8)
            bx = prev[0] + int(math.cos(branch_ang) * rng.randint(10, 25))
            by = prev[1] + int(math.sin(branch_ang) * rng.randint(10, 25))
            draw.line((prev, (bx, by)), fill=(*seal_dark, 100), width=1)

    # Dislodged seal fragments
    for _ in range(rng.randint(5, 10)):
        ang = rng.uniform(0, math.tau)
        dist = rng.randint(sr - 20, sr + 30)
        fx = sx + int(math.cos(ang) * dist)
        fy = sy + int(math.sin(ang) * dist)
        fsize = rng.randint(4, 14)
        draw.ellipse((fx - fsize, fy - fsize, fx + fsize, fy + fsize),
                     fill=(*seal_color, rng.randint(40, 110)))

    # ── 9. Redacted classified document strips ──────────────────────
    redacts = [
        (100, 1250, 480, 1280),
        (130, 1315, 560, 1345),
        (80, 1380, 600, 1410),
        (110, 1445, 420, 1475),
        (180, 1510, 610, 1540),
        (90, 1575, 500, 1605),
        (340, 1640, 650, 1670),
    ]
    red_color = (10, 8, 5)
    stamp = (190, 35, 35)
    for rx1, ry1, rx2, ry2 in redacts:
        draw.rectangle((rx1, ry1, rx2, ry2), fill=(*red_color, 235))
        draw.line((rx1, ry1, rx2, ry1), fill=(*stamp, 180), width=2)
        draw.line((rx1, ry1, rx1, ry2), fill=(*stamp, 100), width=1)

    # Stamped classification text (pixel font)
    _px(draw, 170, 1262, "TOP SECRET", (*stamp, 210), 4)
    _px(draw, 220, 1392, "CLASSIFIED", (*stamp, 210), 4)
    _px(draw, 200, 1522, "EYES ONLY", (*stamp, 190), 4)
    # Smaller stamped notations
    _px(draw, 130, 1448, "CASE FILE", (160, 140, 80, 160), 3)
    _px(draw, 370, 1643, "SEALED", (*stamp, 140), 3)

    # ── 10. Cipher glyphs (scattered geometric symbols) ─────────────
    glyph_data = [
        (160, 180, 28), (530, 130, 22), (820, 260, 18),
        (1250, 420, 24), (100, 520, 16), (1050, 580, 26),
        (720, 380, 18), (1400, 680, 22), (250, 880, 18),
        (450, 1050, 24), (800, 1200, 14), (1350, 900, 20),
        (530, 280, 16), (1170, 550, 20), (280, 680, 14),
    ]
    for gx, gy, gs in glyph_data:
        gc = (
            rng.randint(140, 200),
            rng.randint(120, 175),
            rng.randint(55, 95),
        )
        _draw_cipher(draw, gx, gy, gs, gc)

    # ── 11. Vignette (edge darkening) ───────────────────────────────
    vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    # Left / Right edges
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(70 * max(0, 1 - vt))
        if vv > 0:
            vd.line((0, vy, vv, vy), fill=(0, 0, 0, 55))
            vd.line((W - vv, vy, W, vy), fill=(0, 0, 0, 55))
    # Top / Bottom edges
    for vx in range(W):
        vt = 1 - abs(vx - W // 2) / (W // 2)
        vv = int(50 * max(0, 1 - vt))
        if vv > 0:
            vd.line((vx, 0, vx, vv), fill=(0, 0, 0, 40))
            vd.line((vx, H - vv, vx, H), fill=(0, 0, 0, 60))
    img = Image.alpha_composite(img, vig)

    # ── 12. Document header tag (top-left) ──────────────────────────
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle((30, 25, 230, 70), fill=(15, 13, 8, 180))
    draw.line((30, 25, 230, 25), fill=(*stamp, 160), width=2)
    _px(draw, 42, 36, "TOP SEC", (*stamp, 200), 3)

    # ── 13. Standard title panel ────────────────────────────────────
    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, title, author, model)
    img.convert("RGB").save(op, "PNG", optimize=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    mp = a.metadata
    op_ = a.out
    make_cover(
        ROOT / mp if not mp.is_absolute() else mp,
        ROOT / op_ if not op_.is_absolute() else op_,
    )


if __name__ == "__main__":
    main()
