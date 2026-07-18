#!/usr/bin/env python3
"""Cover: The Last Painted Lady of Harlan Street — Cozy mystery / art world: a forger dies surrounded by perfect Renaissance copies; his estranged daughter, a restorer with prosopagnosia, must tell real from fake. Composition: arched fresco niche with the Painted Lady (face deliberately blurred), easels bearing forged canvases on both sides, paint-splattered studio floor, art tools scattered in the foreground."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")
    rng = random.Random(573922)

    # ── Renaissance fresco palette ─────────────────────────────────────
    PLASTER = (195, 175, 150)
    TERRACOTTA = (155, 85, 55)
    OCHRE = (180, 145, 70)
    UMBER = (85, 55, 35)
    SIENNA = (140, 70, 40)
    FADED_GOLD = (195, 165, 95)
    FRESCO_SKY = (130, 155, 175)
    FRESCO_SKIN = (200, 165, 130)
    VERDIGRIS = (50, 90, 110)

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ═══════════════════════════════════════════════════════════════════
    # 1. AGED PLASTER WALL GRADIENT
    # ═══════════════════════════════════════════════════════════════════
    for y in range(H):
        t = y / H
        r = int(120 + (PLASTER[0] - 120) * min(1, t * 1.5))
        g = int(100 + (PLASTER[1] - 100) * min(1, t * 1.5))
        b = int(80 + (PLASTER[2] - 80) * min(1, t * 1.5))
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ═══════════════════════════════════════════════════════════════════
    # 2. STONE BLOCK LINES (studio wall texture)
    # ═══════════════════════════════════════════════════════════════════
    for sy in range(0, 1700, 85):
        alpha = rng.randint(6, 15)
        draw.line((0, sy, W, sy), fill=(90, 70, 50, alpha), width=1)
    for sx in range(0, W, rng.randint(130, 200)):
        for sy in range(0, 1700, 85):
            if rng.random() < 0.6:
                draw.line((sx, sy, sx, sy + 85), fill=(90, 70, 50, rng.randint(4, 12)), width=1)

    # ═══════════════════════════════════════════════════════════════════
    # 3. ARCHED FRESCO NICHE — the "Painted Lady" lives here
    # ═══════════════════════════════════════════════════════════════════
    niche_cx, niche_cy = W // 2, 650
    niche_rx, niche_ry = 350, 420

    # Arch background (dark recess)
    arch_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ad = ImageDraw.Draw(arch_layer)
    ad.polygon([
        (niche_cx - niche_rx, niche_cy - niche_ry + 60),
        (niche_cx - niche_rx, niche_cy + niche_ry),
        (niche_cx + niche_rx, niche_cy + niche_ry),
        (niche_cx + niche_rx, niche_cy - niche_ry + 60),
    ], fill=(90, 75, 55, 200))
    ad.ellipse((
        niche_cx - niche_rx, niche_cy - niche_ry,
        niche_cx + niche_rx, niche_cy + 60
    ), fill=(90, 75, 55, 200))
    arch_layer = arch_layer.filter(ImageFilter.SMOOTH_MORE)
    img = Image.alpha_composite(img, arch_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # Fresco inner surface (aged plaster within the arch)
    inner_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ind = ImageDraw.Draw(inner_layer)
    im = 18  # inner margin
    ind.polygon([
        (niche_cx - niche_rx + im, niche_cy - niche_ry + 60 + im),
        (niche_cx - niche_rx + im, niche_cy + niche_ry - im),
        (niche_cx + niche_rx - im, niche_cy + niche_ry - im),
        (niche_cx + niche_rx - im, niche_cy - niche_ry + 60 + im),
    ], fill=(175, 155, 130, 220))
    ind.ellipse((
        niche_cx - niche_rx + im,
        niche_cy - niche_ry + im,
        niche_cx + niche_rx - im,
        niche_cy + 60 - im
    ), fill=(175, 155, 130, 220))
    # Fresco sky area (upper portion of the niche)
    ind.ellipse((
        niche_cx - 200,
        niche_cy - 300,
        niche_cx + 200,
        niche_cy - 20
    ), fill=(120, 140, 160, 160))
    img = Image.alpha_composite(img, inner_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ═══════════════════════════════════════════════════════════════════
    # 4. CRACK LINES (age of the fresco)
    # ═══════════════════════════════════════════════════════════════════
    for _ in range(rng.randint(8, 15)):
        cx = rng.randint(niche_cx - 280, niche_cx + 280)
        cy = rng.randint(niche_cy - 300, niche_cy + 300)
        for _ in range(rng.randint(3, 7)):
            nx = cx + rng.randint(-15, 15)
            ny = cy + rng.randint(-10, 20)
            draw.line((cx, cy, nx, ny), fill=(65, 50, 35, rng.randint(40, 90)), width=rng.randint(1, 2))
            cx, cy = nx, ny

    # ═══════════════════════════════════════════════════════════════════
    # 5. THE PAINTED LADY — central Renaissance figure
    # ═══════════════════════════════════════════════════════════════════
    lady_cx, lady_cy = niche_cx, niche_cy + 30

    body_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(body_layer)

    # Dress / robe (Renaissance blue-green, fading with age)
    bd.polygon([
        (lady_cx - 70, lady_cy + 30),
        (lady_cx - 100, lady_cy + 250),
        (lady_cx + 100, lady_cy + 250),
        (lady_cx + 70, lady_cy + 30),
    ], fill=(*VERDIGRIS, 180))
    # Neck
    bd.ellipse((lady_cx - 18, lady_cy - 50, lady_cx + 18, lady_cy + 10),
               fill=(*FRESCO_SKIN, 180))
    # Head shape
    bd.ellipse((lady_cx - 40, lady_cy - 120, lady_cx + 40, lady_cy - 30),
               fill=(*FRESCO_SKIN, 180))
    # Hair (dark auburn)
    bd.ellipse((lady_cx - 45, lady_cy - 135, lady_cx + 45, lady_cy - 50),
               fill=(65, 40, 25, 180))
    bd.polygon([
        (lady_cx - 45, lady_cy - 60),
        (lady_cx - 40, lady_cy + 40),
        (lady_cx + 40, lady_cy + 40),
        (lady_cx + 45, lady_cy - 60),
    ], fill=(65, 40, 25, 180))

    # Arms (open, welcoming gesture)
    bd.polygon([
        (lady_cx - 70, lady_cy + 30),
        (lady_cx - 120, lady_cy + 100),
        (lady_cx - 110, lady_cy + 110),
        (lady_cx - 65, lady_cy + 60),
    ], fill=(*FRESCO_SKIN, 160))
    bd.polygon([
        (lady_cx + 70, lady_cy + 30),
        (lady_cx + 120, lady_cy + 100),
        (lady_cx + 110, lady_cy + 110),
        (lady_cx + 65, lady_cy + 60),
    ], fill=(*FRESCO_SKIN, 160))

    img = Image.alpha_composite(img, body_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ═══════════════════════════════════════════════════════════════════
    # 6. FACE BLURRING — prosopagnosia symbol
    # The face area is overpainted with blotches of plaster colour so the
    # features are unreadable, echoing Margot's face blindness.
    # ═══════════════════════════════════════════════════════════════════
    face_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(face_layer)
    for _ in range(rng.randint(15, 25)):
        bx = rng.randint(lady_cx - 30, lady_cx + 30)
        by = rng.randint(lady_cy - 100, lady_cy - 40)
        br = rng.randint(5, 18)
        fd.ellipse((bx - br, by - br, bx + br, by + br),
                    fill=(PLASTER[0] + rng.randint(-15, 15),
                          PLASTER[1] + rng.randint(-15, 15),
                          PLASTER[2] + rng.randint(-15, 15),
                          rng.randint(100, 200)))
    # Additional faint horizontal streaks across the face zone
    for _ in range(rng.randint(4, 8)):
        sy = rng.randint(lady_cy - 100, lady_cy - 40)
        for sx in range(lady_cx - 35, lady_cx + 35, 2):
            streak_col = (PLASTER[0] + rng.randint(-20, 20),
                          PLASTER[1] + rng.randint(-20, 20),
                          PLASTER[2] + rng.randint(-20, 20))
            fd.line((sx, sy + rng.randint(-2, 2), sx + 3, sy + rng.randint(-2, 2)),
                     fill=(*streak_col, rng.randint(80, 160)), width=1)
    face_layer = face_layer.filter(ImageFilter.GaussianBlur(4))
    img = Image.alpha_composite(img, face_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ═══════════════════════════════════════════════════════════════════
    # 7. GOLD HALO (Renaissance religious-art convention)
    # ═══════════════════════════════════════════════════════════════════
    halo_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo_layer)
    hd.ellipse((lady_cx - 100, lady_cy - 200, lady_cx + 100, lady_cy),
               fill=(*FADED_GOLD, 40))
    halo_layer = halo_layer.filter(ImageFilter.GaussianBlur(20))
    img = Image.alpha_composite(img, halo_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ═══════════════════════════════════════════════════════════════════
    # 8. EASELS WITH FORGED CANVASES — left and right of the niche
    # ═══════════════════════════════════════════════════════════════════
    def draw_easel_and_canvas(d, cx, cy, s):
        """Draw a wooden easel with a forged painting leaning on it."""
        # Easel legs
        d.line((cx - 50 * s, cy + 180 * s, cx, cy - 100 * s),
               fill=(60, 40, 25, 200), width=max(1, int(5 * s)))
        d.line((cx + 50 * s, cy + 180 * s, cx, cy - 100 * s),
               fill=(60, 40, 25, 200), width=max(1, int(5 * s)))
        d.line((cx, cy + 180 * s, cx, cy - 110 * s),
               fill=(60, 40, 25, 200), width=max(1, int(4 * s)))
        # Shelf
        d.line((cx - 45 * s, cy - 20 * s, cx + 45 * s, cy - 20 * s),
               fill=(70, 50, 30, 180), width=max(1, int(4 * s)))

        # Canvas dimensions
        cw, ch = int(80 * s), int(110 * s)
        canvas_x = cx - cw // 2
        canvas_y = cy - ch - int(20 * s)

        # Canvas shadow
        d.rectangle((canvas_x + int(3 * s), canvas_y + int(3 * s),
                      canvas_x + cw + int(3 * s), canvas_y + ch + int(3 * s)),
                     fill=(0, 0, 0, 60))
        # Canvas (primed linen colour)
        d.rectangle((canvas_x, canvas_y, canvas_x + cw, canvas_y + ch),
                     fill=(220, 205, 175, 220), outline=(100, 75, 45, 200), width=2)

        # Forgery painting on the canvas — abstract Renaissance copy
        pc = rng.choice([TERRACOTTA, OCHRE, SIENNA, UMBER, FADED_GOLD])
        # Background wash
        for _ in range(rng.randint(3, 6)):
            sx = rng.randint(canvas_x + 5, canvas_x + cw - 5)
            sy = rng.randint(canvas_y + 5, canvas_y + ch - 5)
            sw = rng.randint(10, 35)
            sh = rng.randint(10, 25)
            d.ellipse((sx, sy, sx + sw, sy + sh), fill=(*pc, rng.randint(100, 200)))
        # Figure hint on canvas
        fig_col = rng.choice([FRESCO_SKIN, FRESCO_SKY, FADED_GOLD])
        d.ellipse((canvas_x + cw // 3, canvas_y + ch // 4,
                    canvas_x + 2 * cw // 3, canvas_y + ch // 2),
                   fill=(*fig_col, rng.randint(80, 150)))

    # Left side: two easels at different depths
    draw_easel_and_canvas(draw, 260, 820, 0.9)
    draw_easel_and_canvas(draw, 480, 960, 0.65)

    # Right side: two easels at different depths
    draw_easel_and_canvas(draw, 1340, 820, 0.9)
    draw_easel_and_canvas(draw, 1120, 960, 0.65)

    # ═══════════════════════════════════════════════════════════════════
    # 9. PAINT-SPLATTERED FLOOR
    # ═══════════════════════════════════════════════════════════════════
    floor_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fld = ImageDraw.Draw(floor_layer)

    # Floor gradient (darkens toward the bottom)
    for fy in range(1550, H):
        t = (fy - 1550) / (H - 1550)
        alpha = int(60 * t)
        fld.line((0, fy, W, fy), fill=(50, 35, 20, alpha))

    # Paint splatters on the floor
    for _ in range(rng.randint(30, 50)):
        sx = rng.randint(50, W - 50)
        sy = rng.randint(1550, 1850)
        sr = rng.randint(3, 25)
        sc = rng.choice([TERRACOTTA, OCHRE, SIENNA, VERDIGRIS, FADED_GOLD])
        fld.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=(*sc, rng.randint(40, 120)))
        # Secondary drips
        for _ in range(rng.randint(0, 4)):
            dx = sx + rng.randint(-sr, sr)
            dy = sy + rng.randint(5, 25)
            fld.ellipse((dx - 3, dy - 3, dx + 3, dy + 3), fill=(*sc, rng.randint(30, 80)))

    floor_layer = floor_layer.filter(ImageFilter.SMOOTH)
    img = Image.alpha_composite(img, floor_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ═══════════════════════════════════════════════════════════════════
    # 10. ARTIST'S TOOLS in the foreground
    # ═══════════════════════════════════════════════════════════════════
    def draw_brush(d, bx, by, angle_deg, length):
        """Draw a loose paintbrush."""
        ang = math.radians(angle_deg)
        ex = bx + math.cos(ang) * length
        ey = by + math.sin(ang) * length
        d.line((bx, by, ex, ey), fill=(80, 60, 35, 180),
               width=max(1, int(4 * length / 60)))
        # Paint on brush tip
        tip_x = ex + math.cos(ang) * 8
        tip_y = ey + math.sin(ang) * 8
        tc = rng.choice([TERRACOTTA, OCHRE, SIENNA, VERDIGRIS])
        d.ellipse((tip_x - 4, tip_y - 4, tip_x + 4, tip_y + 4), fill=(*tc, 180))

    draw_brush(draw, 150, 1700, 45, 80)
    draw_brush(draw, 1450, 1750, 120, 70)
    draw_brush(draw, 200, 1300, 60, 55)
    draw_brush(draw, 1350, 1400, -30, 50)

    # Painter's palette (circular)
    draw.ellipse((1400, 1150, 1500, 1250), fill=(200, 180, 150, 180),
                  outline=(120, 90, 60, 200), width=2)
    draw.ellipse((1408, 1158, 1440, 1190), fill=(*TERRACOTTA, 180))
    draw.ellipse((1445, 1155, 1475, 1185), fill=(*OCHRE, 180))
    draw.ellipse((1425, 1195, 1455, 1225), fill=(*SIENNA, 180))

    # Small pigment jars / turpentine pot (glass)
    draw.rectangle((100, 1480, 130, 1530), fill=(150, 150, 140, 120),
                    outline=(180, 180, 170, 160), width=1)
    draw.ellipse((95, 1475, 135, 1490), fill=(180, 180, 170, 100),
                  outline=(200, 200, 190, 160), width=1)

    # ═══════════════════════════════════════════════════════════════════
    # 11. ATMOSPHERIC DUST MOTES (soft studio light)
    # ═══════════════════════════════════════════════════════════════════
    dust = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dust)
    for _ in range(rng.randint(40, 80)):
        dx = rng.randint(0, W)
        dy = rng.randint(0, 1700)
        dr = rng.randint(1, 4)
        db = rng.randint(200, 230)
        dd.ellipse((dx - dr, dy - dr, dx + dr, dy + dr),
                    fill=(db, db - 15, db - 30, rng.randint(10, 35)))
    dust = dust.filter(ImageFilter.GaussianBlur(2))
    img = Image.alpha_composite(img, dust)
    draw = ImageDraw.Draw(img, "RGBA")

    # ═══════════════════════════════════════════════════════════════════
    # 12. VIGNETTE
    # ═══════════════════════════════════════════════════════════════════
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(40 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 60))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 60))

    # ═══════════════════════════════════════════════════════════════════
    # SAVE
    # ═══════════════════════════════════════════════════════════════════
    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, title, author, model)
    img.convert("RGB").save(op, "PNG", optimize=True)


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
