#!/usr/bin/env python3
"""Cover: The Archivist's Dilemma — Cozy mystery / academic; a meticulous archivist discovers love letters hidden in a 1906 geography textbook that could prove a beloved philanthropist was a serial arsonist."""

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
rng.seed(579231648)

# ── Palette: warm amber lamp-light, deep mahogany, parchment, scorch, archive-green ──
LAMP_GLOW      = (240, 195, 120)   # warm incandescent
LAMP_HOT       = (255, 220, 140)   # centre of bulb
AMBER_DARK     = (160, 110, 40)    # shadow amber
PARCHMENT      = (235, 215, 175)   # aged paper
PARCHMENT_LIT  = (250, 238, 200)   # lit paper
PARCHMENT_SHAD = (170, 140, 100)   # shadow side of paper
MAHOGANY       = (45, 12, 8)       # dark wood bindings
MAHOGANY_LITE  = (70, 30, 18)      # lit wood
BOOK_GREEN     = (28, 55, 25)      # vintage cloth binding
BOOK_GREEN_LIT = (50, 85, 40)      # lit green cloth
SCORCH         = (180, 60, 20)     # burnt edge
SCORCH_DARK    = (90, 25, 8)       # deep char
INK_BLACK      = (15, 10, 8)       # ink
SHELF_DARK     = (20, 10, 6)       # shadow between shelves
BG_DARK        = (10, 6, 4)        # deepest background
DUST_GOLD      = (200, 175, 120)   # floating dust motes in light


def _draw_bookshelf(draw, x1, y1, x2, y2):
    """Draw a dark wooden bookshelf section filled with aged book spines at (x1,y1)-(x2,y2)."""
    # Shelf board
    draw.rectangle((x1, y1, x2, y2), fill=(18, 10, 6, 255), outline=(35, 18, 8, 180), width=1)
    # Shelf inner (where books sit)
    inner_t = y1 + 8
    inner_b = y2 - 6
    if inner_b - inner_t < 10:
        return
    # Fill with book spines
    bx = x1 + 6
    while bx < x2 - 6:
        bw = rng.randint(10, 28)
        if bx + bw > x2 - 6:
            bw = x2 - 6 - bx
        if bw < 6:
            break
        # Choose binding colour — varied vintage hues
        bcol = rng.choice([
            (40, 15, 12),        # dark red
            (15, 30, 18),        # dark green
            (22, 18, 35),        # navy
            (45, 30, 12),        # brown
            (50, 20, 15),        # maroon
            (20, 18, 12),        # dark tan
            (35, 25, 40),        # plum
            (12, 18, 25),        # slate
        ])
        draw.rectangle((bx, inner_t, bx + bw, inner_b), fill=bcol, outline=(10, 8, 6, 100), width=1)
        # Spine highlight line
        hl = rng.randint(2, 5)
        draw.line((bx + hl, inner_t + 8, bx + hl, inner_b - 8), fill=(min(255, bcol[0] + 25), min(255, bcol[1] + 20), min(255, bcol[2] + 15), 80), width=1)
        # Tiny gold lettering on some
        if rng.random() < 0.35 and bw > 14:
            gx = bx + bw // 2
            gy = (inner_t + inner_b) // 2
            gs = rng.randint(1, 2)
            draw.ellipse((gx - gs, gy - gs, gx + gs, gy + gs), fill=(180, 155, 80, rng.randint(60, 140)))
        bx += bw + rng.randint(1, 3)


def _draw_aged_page_corner(draw, cx, cy, w, h, angle_deg):
    """Draw a rectangular aged page rotated by angle degrees, with a possible scorched corner."""
    ang = math.radians(angle_deg)
    cos_a = math.cos(ang)
    sin_a = math.sin(ang)
    # Four corners of the rectangle (centered at 0,0)
    corners = [(-w // 2, -h // 2), (w // 2, -h // 2), (w // 2, h // 2), (-w // 2, h // 2)]
    pts = []
    for (px, py) in corners:
        rx = cx + px * cos_a - py * sin_a
        ry = cy + px * sin_a + py * cos_a
        pts.append((rx, ry))
    # Fill with parchment
    draw.polygon(pts, fill=PARCHMENT, outline=(160, 130, 80, 180), width=1)
    return pts


def _draw_text_lines(draw, pts, n_lines, x_off, y_off, line_len):
    """Draw tiny horizontal ink lines inside a rotated page to represent handwriting."""
    # Get bounding box of the page
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    min_y, max_y = min(ys), max(ys)
    min_x, max_x = min(xs), max(xs)
    # Infer rotation from first two points
    dx = pts[1][0] - pts[0][0]
    dy = pts[1][1] - pts[0][1]
    ang = math.atan2(dy, dx) if dx != 0 else 0
    cos_a = math.cos(ang)
    sin_a = math.sin(ang)

    step = (max_y - min_y) / (n_lines + 1)
    for i in range(n_lines):
        ly = min_y + step * (i + 1) + rng.randint(-3, 3)
        lx1 = min_x + x_off + rng.randint(0, 5)
        llen = rng.randint(int(line_len * 0.4), line_len)
        # Rotate the line endpoints (they're already in the rotated frame, just draw horizontally in page-space)
        lx2 = min(lx1 + llen, max_x - 4)
        # Slight waviness for handwriting feel
        segments = max(3, llen // 12)
        prev = (lx1, ly)
        for s in range(1, segments + 1):
            t = s / segments
            wx = lx1 + (lx2 - lx1) * t
            wy = ly + rng.randint(-2, 2)
            # Apply inverse rotation to get to world space — wait, pts are already world space.
            # Actually, the page is rotated already. Just draw horizontal lines but with small offsets.
            alpha = rng.randint(60, 120)
            draw.line((prev[0], prev[1], wx, wy), fill=(*INK_BLACK, alpha), width=1)
            prev = (wx, wy)


def _draw_scorch_mark(draw, cx, cy, size):
    """Draw a scorched/charred area at a corner of a page."""
    # Outer glow
    for rad in range(size, 0, -3):
        alpha = max(8, 80 - rad * 2)
        r = SCORCH[0] - (size - rad) * 2
        g = SCORCH[1] - (size - rad)
        b = SCORCH[2] - (size - rad) // 2
        draw.ellipse((cx - rad, cy - rad, cx + rad, cy + rad),
                     fill=(max(0, r), max(0, g), max(0, b), alpha))
    # Dark core
    draw.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=(*SCORCH_DARK, 200))


def _draw_letter(draw, img, cx, cy, w, h, angle_deg, has_scorch=False):
    """Draw a single love letter page, possibly with scorched corner, and handwriting lines."""
    pts = _draw_aged_page_corner(draw, cx, cy, w, h, angle_deg)

    # Envelope fold lines (classic three-panel letter)
    fold_alpha = 100
    ang = math.radians(angle_deg)
    cos_a = math.cos(ang)
    sin_a = math.sin(ang)
    # Draw horizontal fold lines in the page's local space
    for frac in [0.33, 0.66]:
        ly = cy + (frac - 0.5) * h
        lx1 = cx - (w // 2) * cos_a - 0 * sin_a
        lx2 = cx + (w // 2) * cos_a - 0 * sin_a
        # Actually, draw in the rotated direction: both ends offset perpendicular to the length axis
        # The page width extends along the rotated x-axis (angle_deg)
        half_w_vec_x = (w // 2) * cos_a
        half_w_vec_y = (w // 2) * sin_a
        # and height extends perpendicular
        half_h_vec_x = (h // 2) * (-sin_a)
        half_h_vec_y = (h // 2) * cos_a

        # Point at fraction of height along perpendicular
        perp_frac = (frac - 0.5)
        px = cy + perp_frac * half_h_vec_y * 2
        py = cx + perp_frac * half_h_vec_x * 2  # Wait, this is wrong. Let me rethink.

        # Actually for rotated rectangle, local y is along the height direction
        # The center is (cx, cy). The top edge is at -h/2 along the perpendicular direction.
        # perpendicular direction: (-sin_a, cos_a)
        perp_x = -sin_a
        perp_y = cos_a
        # Width direction: (cos_a, sin_a)
        wid_x = cos_a
        wid_y = sin_a

        frac_offset = (frac - 0.5) * h
        p_cx = cx + frac_offset * perp_x
        p_cy = cy + frac_offset * perp_y
        # Line goes from left edge to right edge along width direction
        l1 = (p_cx - (w // 2) * wid_x, p_cy - (w // 2) * wid_y)
        l2 = (p_cx + (w // 2) * wid_x, p_cy + (w // 2) * wid_y)
        draw.line((l1[0], l1[1], l2[0], l2[1]), fill=(120, 100, 60, fold_alpha), width=1)

    # Handwriting lines
    ang_local = math.degrees(math.atan2(-sin_a, cos_a))  # rotation in degrees
    _draw_text_lines(draw, pts, rng.randint(6, 10), int(w * 0.15), 0, int(w * 0.65))

    # Scorch at a corner if requested
    if has_scorch:
        # Pick a corner (top-right in page-local space)
        scorch_corner_x = cx + (w // 2 - 10) * wid_x + (-h // 2 + 10) * perp_x
        scorch_corner_y = cy + (w // 2 - 10) * wid_y + (-h // 2 + 10) * perp_y
        _draw_scorch_mark(draw, scorch_corner_x, scorch_corner_y, rng.randint(18, 30))

    # Subtle page shadow
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.polygon(pts, fill=(0, 0, 0, 20))
    shadow = shadow.filter(ImageFilter.GaussianBlur(6))
    img = Image.alpha_composite(img, shadow)
    draw = ImageDraw.Draw(img, "RGBA")
    return draw, img


def _draw_ink_swirl(draw, x, y, scale):
    """Draw a stylized ink-swirl / scent-tendril rising from the page."""
    pts = []
    for t in range(0, 360, 5):
        ang = math.radians(t)
        r = scale * (8 + 4 * math.sin(ang * 1.7 + 0.3 * t))
        px = x + r * math.cos(ang)
        py = y + r * math.sin(ang) - t * 0.5 * scale / 10
        pts.append((px, py))
    if len(pts) > 2:
        for i in range(len(pts) - 1):
            alpha = max(5, 40 - i)
            draw.line((pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1]),
                      fill=(190, 170, 120, alpha), width=1)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    # ── 1. Deep background: shadowy archive ──
    img = Image.new("RGBA", (W, H), BG_DARK)
    draw = ImageDraw.Draw(img, "RGBA")

    # Gradient: pitch black at top → very dark brown → slightly warmer at bottom
    for y in range(H):
        t = y / H
        r = int(8 + 18 * t * (1 - t * 0.3))
        g = int(5 + 8 * t * (1 - t * 0.3))
        b = int(3 + 6 * t * (1 - t * 0.3))
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # ── 2. Bookshelves flanking the scene ──
    # Left shelves
    for sy in range(0, 1900, 120):
        _draw_bookshelf(draw, 0, sy, 280, sy + 110)
    # Right shelves
    for sy in range(0, 1900, 120):
        _draw_bookshelf(draw, W - 280, sy, W, sy + 110)
    # Middle-back shelf (shorter, between the two main ones)
    for sy in range(0, 1400, 120):
        _draw_bookshelf(draw, 580, sy, 1020, sy + 110)

    # ── 3. Desk / reading table ──
    desk_t = 1380
    desk_b = 1760
    # Desk top surface
    draw.rectangle((80, desk_t, W - 80, desk_b), fill=(35, 18, 8, 255), outline=(55, 28, 12, 200), width=2)
    # Desk front edge
    draw.rectangle((60, desk_b, W - 60, desk_b + 60), fill=(22, 12, 5, 255),
                   outline=(40, 20, 8, 180), width=1)
    # Wood grain on desk
    for _ in range(40):
        gx = rng.randint(120, W - 120)
        gy = rng.randint(desk_t + 6, desk_b - 6)
        glen = rng.randint(20, 100)
        gcol = (rng.randint(40, 60), rng.randint(18, 30), rng.randint(6, 14))
        draw.line((gx, gy, gx + glen, gy + rng.randint(-3, 3)),
                  fill=(*gcol, rng.randint(15, 40)), width=1)

    # ── 4. Lamp light pool ──
    # Warm conical light from upper-left
    light_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(light_layer)

    # Main cone of light
    cone_pts = [(100, 200), (W + 100, 500), (W + 500, desk_b + 100), (-300, desk_b + 100)]
    ld.polygon(cone_pts, fill=(LAMP_GLOW[0], LAMP_GLOW[1], LAMP_GLOW[2], 18))

    # Smaller bright spot on desk
    ld.ellipse((100, desk_t - 40, W - 100, desk_b + 40), fill=(LAMP_HOT[0], LAMP_HOT[1], LAMP_HOT[2], 12))
    light_layer = light_layer.filter(ImageFilter.GaussianBlur(35))
    img = Image.alpha_composite(img, light_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 5. Open 1906 geography textbook ──
    # Left page
    book_cx, book_cy = W // 2 + 30, desk_t - 120
    book_w, book_h = 420, 340

    # Left page (slightly angled toward viewer)
    left_pts = []
    left_ang = -8
    ang_l = math.radians(left_ang)
    cos_l = math.cos(ang_l)
    sin_l = math.sin(ang_l)
    l_cx = book_cx - 190
    for (px, py) in [(-book_w // 2, -book_h // 2), (book_w // 2, -book_h // 2),
                      (book_w // 2, book_h // 2), (-book_w // 2, book_h // 2)]:
        rx = l_cx + px * cos_l - py * sin_l
        ry = book_cy + px * sin_l + py * cos_l
        left_pts.append((rx, ry))
    draw.polygon(left_pts, fill=PARCHMENT_SHAD, outline=(100, 80, 40, 200), width=1)

    # Right page (more angled, catching the light)
    right_pts = []
    right_ang = 14
    ang_r = math.radians(right_ang)
    cos_r = math.cos(ang_r)
    sin_r = math.sin(ang_r)
    r_cx = book_cx + 190
    for (px, py) in [(-book_w // 2, -book_h // 2), (book_w // 2, -book_h // 2),
                      (book_w // 2, book_h // 2), (-book_w // 2, book_h // 2)]:
        rx = r_cx + px * cos_r - py * sin_r
        ry = book_cy + px * sin_r + py * cos_r
        right_pts.append((rx, ry))
    draw.polygon(right_pts, fill=PARCHMENT_LIT, outline=(140, 110, 60, 200), width=1)

    # Book spine / center crease
    draw.line((book_cx - 10, book_cy - book_h // 2 + 5, book_cx - 5, book_cy + book_h // 2 - 5),
              fill=(60, 35, 10, 200), width=3)

    # Textbook text on right page
    for i in range(18):
        ly = book_cy - book_h // 2 + 15 + i * 17 + rng.randint(-2, 2)
        lx = r_cx - 150 + rng.randint(0, 8)
        llen = rng.randint(100, 240)
        alpha = rng.randint(40, 90)
        draw.line((lx, ly, lx + llen, ly + rng.randint(-1, 1)),
                  fill=(30, 28, 20, alpha), width=1)

    # A few visible lines on left page (darker)
    for i in range(14):
        ly = book_cy - book_h // 2 + 20 + i * 18
        lx = l_cx - 140 + rng.randint(0, 5)
        llen = rng.randint(80, 200)
        draw.line((lx, ly, lx + llen, ly), fill=(50, 40, 25, rng.randint(40, 80)), width=1)

    # ── 6. Love letters spilling out from between the pages ──
    # Letter 1: falling toward left, slightly scorched
    draw, img = _draw_letter(draw, img, book_cx - 140, book_cy + 100, 260, 170, -22, has_scorch=True)
    # Letter 2: falling toward right, catching the light
    draw, img = _draw_letter(draw, img, book_cx + 190, book_cy + 60, 240, 155, 18)
    # Letter 3: sticking out the top, folded
    draw, img = _draw_letter(draw, img, book_cx + 40, book_cy - 220, 200, 130, 35)
    # Letter 4: half-hidden, bottom right, heavily scorched
    draw, img = _draw_letter(draw, img, book_cx + 280, book_cy + 200, 220, 145, 42, has_scorch=True)
    # Letter 5: peeking out left side
    draw, img = _draw_letter(draw, img, book_cx - 240, book_cy - 80, 180, 120, -30)

    # ── 7. Scorch marks on the textbook page edges ──
    # The right page has a burned edge
    for _ in range(3):
        sx = r_cx + book_w // 2 - 10 + rng.randint(-15, 5)
        sy = book_cy + rng.randint(-book_h // 2 + 20, book_h // 2 - 20)
        _draw_scorch_mark(draw, sx, sy, rng.randint(12, 22))

    # ── 8. Ink-scent swirls rising from the pages ──
    # Hugh Pargetter can smell ink — visualize this as faint golden/amber tendrils
    swirl_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sw = ImageDraw.Draw(swirl_layer)
    for _ in range(5):
        sx = book_cx + rng.randint(-200, 200)
        sy = book_cy - rng.randint(50, 200)
        _draw_ink_swirl(sw, sx, sy, rng.randint(8, 16))
    swirl_layer = swirl_layer.filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(img, swirl_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 9. Vintage desk lamp (visible at left edge) ──
    # Lamp base
    lamp_x = 140
    lamp_y = desk_t - 20
    draw.ellipse((lamp_x - 30, lamp_y - 8, lamp_x + 30, lamp_y + 8), fill=(55, 40, 20, 255))
    draw.ellipse((lamp_x - 25, lamp_y - 4, lamp_x + 25, lamp_y + 4), fill=(80, 55, 25, 180))
    # Lamp stem
    draw.line((lamp_x, lamp_y, lamp_x, lamp_y - 200), fill=(50, 35, 18, 220), width=6)
    # Shade
    shade_top = lamp_y - 240
    draw.polygon([
        (lamp_x - 60, shade_top),
        (lamp_x + 60, shade_top),
        (lamp_x + 40, lamp_y - 200),
        (lamp_x - 40, lamp_y - 200),
    ], fill=(45, 50, 35, 230), outline=(60, 65, 50, 200), width=2)
    # Inner glow of shade
    draw.ellipse((lamp_x - 20, lamp_y - 200, lamp_x + 20, lamp_y - 186),
                 fill=(*LAMP_GLOW, 180))

    # ── 10. Warm glow on the desk surface from the lamp (additional) ──
    desk_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dg = ImageDraw.Draw(desk_glow)
    dg.ellipse((lamp_x - 250, desk_t, lamp_x + 500, desk_b), fill=(*LAMP_GLOW, 14))
    desk_glow = desk_glow.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, desk_glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 11. Floating dust motes in the light beam ──
    dust_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    du = ImageDraw.Draw(dust_layer)
    for _ in range(150):
        dx = rng.randint(100, W - 100)
        dy = rng.randint(100, desk_t + 50)
        dr = rng.uniform(0.5, 3.0)
        da = rng.randint(20, 80)
        du.ellipse((dx - dr, dy - dr, dx + dr, dy + dr), fill=(*DUST_GOLD, da))
    dust_layer = dust_layer.filter(ImageFilter.GaussianBlur(1.5))
    img = Image.alpha_composite(img, dust_layer)

    # ── 12. Vignette ──
    draw = ImageDraw.Draw(img, "RGBA")
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(50 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 120))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 120))

    # ── 13. Bottom edge: faint ember glow (arson motif) ──
    ember = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    eb = ImageDraw.Draw(ember)
    eb.ellipse((book_cx - 300, desk_b - 20, book_cx + 300, desk_b + 80), fill=(200, 70, 20, 6))
    ember = ember.filter(ImageFilter.GaussianBlur(25))
    img = Image.alpha_composite(img, ember)

    # ── 14. Save ──
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
