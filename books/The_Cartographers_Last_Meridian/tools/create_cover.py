#!/usr/bin/env python3
"""Cover: The Cartographer's Last Meridian — 1520s Seville: a blind cartographer who sailed with Magellan discovers the Crown omits a southern continent and must smuggle the true map past the Inquisition. Aged parchment, compass rose, hidden southern continent outline, meridian line, rhumb lines, and Inquisition shadow."""

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
rng.seed(142857)

# Parchment / aged-map palette
PARCHMENT_BASE = (200, 180, 140)      # warm aged vellum
PARCHMENT_DARK = (160, 130, 80)       # darker worn edge
INK_BROWN = (70, 50, 30)              # iron-gall ink
INK_FADED = (110, 85, 55)            # faded ink
SEPIA_LINE = (90, 65, 40)            # grid/rhumb lines
GOLD_ACCENT = (200, 165, 80)         # compass rose gold
SOUTHERN_GLOW = (180, 140, 60)       # hidden continent glow
BLOOD_RED = (140, 30, 20)             # Inquisition danger
CANDLE_WARM = (255, 220, 150)        # candlelight


def _make_compass_rose(cx, cy, size, draw):
    """Draw an intricate compass rose at (cx, cy) with given size."""
    # Outer ring
    draw.ellipse((cx - size, cy - size, cx + size, cy + size),
                 outline=(*INK_BROWN, 180), width=3)
    draw.ellipse((cx - size * 0.85, cy - size * 0.85, cx + size * 0.85, cy + size * 0.85),
                 outline=(*INK_FADED, 120), width=1)

    # Four cardinal points (darker, longer)
    cardinals = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    intercardinals = [(0.707, -0.707), (0.707, 0.707), (-0.707, 0.707), (-0.707, -0.707)]

    for dx, dy in cardinals:
        tip = (cx + dx * size * 1.2, cy + dy * size * 1.2)
        left = (cx + dx * size * 0.15 - dy * size * 0.25,
                cy + dy * size * 0.15 + dx * size * 0.25)
        right = (cx + dx * size * 0.15 + dy * size * 0.25,
                 cy + dy * size * 0.15 - dx * size * 0.25)
        draw.polygon([tip, left, right], fill=(*INK_BROWN, 200))
        # gold highlight on right half
        draw.polygon([tip, (right[0], right[1]),
                     ((left[0] + right[0]) / 2, (left[1] + right[1]) / 2)],
                     fill=(*GOLD_ACCENT, 160))

    for dx, dy in intercardinals:
        tip = (cx + dx * size * 0.9, cy + dy * size * 0.9)
        left = (cx + dx * size * 0.12 - dy * size * 0.18,
                cy + dy * size * 0.12 + dx * size * 0.18)
        right = (cx + dx * size * 0.12 + dy * size * 0.18,
                 cy + dy * size * 0.12 - dx * size * 0.18)
        draw.polygon([tip, left, right], fill=(*INK_FADED, 150))

    # Centre dot
    draw.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), fill=(*GOLD_ACCENT, 220))


def _draw_coastline(segments, cx, cy, scale, draw):
    """Draw a stylised coastline silhouette suggesting a continent."""
    for seg in segments:
        pts = [(cx + int(p[0] * scale), cy + int(p[1] * scale)) for p in seg]
        if len(pts) > 2:
            draw.polygon(pts, fill=(*SOUTHERN_GLOW, 25))
            draw.line(pts + [pts[0]], fill=(*INK_FADED, 100), width=2)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    # --- Base parchment canvas ---
    img = Image.new("RGBA", (W, H), PARCHMENT_BASE + (255,))
    draw = ImageDraw.Draw(img, "RGBA")

    # --- Gradient: creamily lit from top, darkening toward bottom (Inquisition shadow) ---
    for y in range(H):
        t = y / H
        r = int(PARCHMENT_BASE[0] + (PARCHMENT_DARK[0] - PARCHMENT_BASE[0]) * t * 0.7 + (BLOOD_RED[0] - PARCHMENT_BASE[0]) * max(0, t - 0.5) * 0.3)
        g = int(PARCHMENT_BASE[1] + (PARCHMENT_DARK[1] - PARCHMENT_BASE[1]) * t * 0.7 - max(0, t - 0.5) * 20)
        b = int(PARCHMENT_BASE[2] + (PARCHMENT_DARK[2] - PARCHMENT_BASE[2]) * t * 0.7 - max(0, t - 0.7) * 30)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # --- Aged parchment texture (speckle) ---
    for _ in range(3000):
        sx = rng.randint(0, W)
        sy = rng.randint(0, 1700)
        sr = rng.uniform(0.5, 2.5)
        sa = rng.randint(5, 25)
        draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=(140, 110, 60, sa))

    # --- Latitude / Longitude grid (curved, as on a globe projection) ---
    grid_alpha = 60
    # Longitude lines: radiating slightly from a vanishing point
    vp_x, vp_y = W // 2, 200
    for lon in range(-6, 7):
        spread = lon * 0.08
        pts = []
        for yp in range(200, 1800, 10):
            offset = spread * (yp - vp_y) * 1.5
            xp = vp_x + offset
            pts.append((xp, yp))
        draw.line(pts, fill=(*SEPIA_LINE, grid_alpha), width=1)

    # Latitude lines: horizontal arcs
    for lat_i in range(5, 25):
        y_base = 200 + lat_i * 65
        if y_base > 1750:
            break
        pts = []
        curve_amp = 30 * math.sin((y_base - 200) / 1550 * math.pi)
        for xp in range(0, W + 10, 10):
            x_ratio = xp / W
            yp = y_base + curve_amp * math.sin(x_ratio * math.pi) * (x_ratio * (1 - x_ratio) * 4)
            pts.append((xp, yp))
        draw.line(pts, fill=(*SEPIA_LINE, grid_alpha // 2), width=1)

    # --- Rhumb lines (navigation lines radiating from compass points) ---
    rhumb_origins = [
        (200, 300), (1400, 300), (100, 700), (1500, 700),
        (W // 2, 400), (300, 1200), (1300, 1200)
    ]
    for ox, oy in rhumb_origins:
        for angle_deg in range(0, 360, rng.choice([15, 22, 30, 45])):
            rad = math.radians(angle_deg + rng.uniform(-3, 3))
            ex = ox + math.cos(rad) * 1800
            ey = oy + math.sin(rad) * 1800
            draw.line((ox, oy, ex, ey), fill=(*SEPIA_LINE, rng.randint(8, 20)), width=1)

    # --- Compass Rose ---
    _make_compass_rose(W // 2, 450, 130, draw)

    # --- The Prominent Meridian Line (the "last meridian") ---
    meridian_x = W // 2 + 30
    # Glow layer behind meridian
    meridian_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    mglow_draw = ImageDraw.Draw(meridian_glow)
    for g_radius in range(100, 10, -5):
        alpha = max(0, 20 - g_radius // 5)
        mglow_draw.ellipse((meridian_x - g_radius, 0, meridian_x + g_radius, 1800),
                           fill=(*GOLD_ACCENT, alpha // 3))
    meridian_glow = meridian_glow.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, meridian_glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # The meridian line itself
    draw.line((meridian_x, 0, meridian_x, 1750), fill=(*GOLD_ACCENT, 200), width=4)
    draw.line((meridian_x, 0, meridian_x, 1750), fill=(255, 230, 170, 100), width=8)
    # Meridian tick marks
    for y_tick in range(100, 1750, 40):
        tick_w = 15 if y_tick % 200 < 20 else 8
        draw.line((meridian_x - tick_w, y_tick, meridian_x + tick_w, y_tick),
                  fill=(*INK_BROWN, 160), width=1)

    # --- Hidden Southern Continent ---
    cont_segments = [
        # Main body of the hidden continent
        [(x, y) for x, y in [
            (-500, 200), (-400, 150), (-250, 100), (-80, 120), (0, 80),
            (100, 60), (200, 90), (300, 70), (400, 100), (450, 130),
            (500, 180), (520, 250), (500, 320), (450, 380), (400, 400),
            (300, 420), (200, 400), (100, 430), (0, 410), (-100, 420),
            (-200, 400), (-300, 380), (-400, 340), (-480, 300), (-500, 250),
        ]],
        # An island chain
        [(x, y) for x, y in [
            (-200, -50), (-150, -80), (-80, -60), (-50, -30), (-80, 0),
            (-150, 20), (-200, 0),
        ]],
        # Another island
        [(x, y) for x, y in [
            (350, -20), (400, -40), (450, -10), (440, 30), (380, 40),
            (340, 20),
        ]],
    ]
    _draw_coastline(cont_segments, meridian_x, 1100, 1.2, draw)

    # Continent label placeholder (faint inscription)
    cont_bbox = draw.textbbox((0, 0), "TERRA AUSTRALIS", font=None)
    label_x = meridian_x - (cont_bbox[2] - cont_bbox[0]) // 2
    draw.text((label_x, 1380), "TERRA AUSTRALIS", fill=(*INK_FADED, 60))
    draw.text((label_x, 1390), "~ incognita ~", fill=(*INK_FADED, 40))

    # --- Coastline details / sea monsters (decorative) ---
    for _ in range(8):
        mx = rng.randint(100, W - 100)
        my = rng.randint(700, 1500)
        mr = rng.randint(15, 40)
        # Sea-creature suggestion: wavy lines
        for wave_angle in range(0, 360, 30):
            rad = math.radians(wave_angle)
            x1 = mx + math.cos(rad) * mr
            y1 = my + math.sin(rad) * mr
            x2 = mx + math.cos(rad) * (mr + 10)
            y2 = my + math.sin(rad) * (mr + 10)
            draw.line((x1, y1, x2, y2), fill=(*INK_FADED, 40), width=1)

    # --- Ocean wave marks (small chevrons suggesting water) ---
    for _ in range(200):
        wx = rng.randint(0, W)
        wy = rng.randint(800, 1650)
        wsize = rng.randint(3, 8)
        draw.arc((wx - wsize, wy - wsize // 2, wx + wsize, wy + wsize // 2),
                 0, 180, fill=(*INK_FADED, rng.randint(15, 40)), width=1)

    # --- Candlelight glow at top ---
    candle_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(candle_glow)
    # Warm glow from an unseen candle above
    cd.ellipse((W // 2 - 300, -200, W // 2 + 300, 400), fill=(*CANDLE_WARM, 15))
    cd.ellipse((W // 2 - 150, -100, W // 2 + 150, 250), fill=(*CANDLE_WARM, 10))
    candle_glow = candle_glow.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, candle_glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # --- Inquisition shadow darkening from bottom edges ---
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    # Left edge darkness
    for x in range(0, 200):
        alpha = int(180 * (1 - x / 200))
        sd.line((x, 0, x, H), fill=(*BLOOD_RED, alpha // 3))
    # Right edge darkness
    for x in range(W - 200, W):
        alpha = int(180 * (1 - (W - x) / 200))
        sd.line((x, 0, x, H), fill=(*BLOOD_RED, alpha // 3))
    # Bottom shadow (inquisition creeping up)
    for y in range(1700, H):
        t = (y - 1700) / (H - 1700)
        alpha = int(120 * t)
        sd.line((0, y, W, y), fill=(20, 5, 5, alpha))
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img, shadow)
    draw = ImageDraw.Draw(img, "RGBA")

    # --- Archive shelf lines (suggesting the royal archive) ---
    for shelf_y in [520, 540, 560, 580, 600, 1480, 1500, 1520]:
        draw.line((0, shelf_y, W, shelf_y), fill=(*INK_BROWN, 30), width=1)

    # --- Parchment burn marks near edges ---
    burn = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(burn)
    for _ in range(5):
        bx = rng.randint(0, W)
        by = rng.randint(0, 1700)
        br = rng.randint(30, 100)
        bd.ellipse((bx - br, by - br, bx + br, by + br), fill=(100, 60, 30, rng.randint(3, 10)))
    burn = burn.filter(ImageFilter.GaussianBlur(12))
    img = Image.alpha_composite(img, burn)
    draw = ImageDraw.Draw(img, "RGBA")

    # --- Seal / stamp (royal seal suggestion) ---
    seal_cx, seal_cy = W - 180, 1050
    draw.ellipse((seal_cx - 40, seal_cy - 40, seal_cx + 40, seal_cy + 40),
                 outline=(*BLOOD_RED, 100), width=3)
    draw.ellipse((seal_cx - 25, seal_cy - 25, seal_cx + 25, seal_cy + 25),
                 outline=(*BLOOD_RED, 70), width=2)
    # Cross inside seal
    draw.line((seal_cx - 15, seal_cy, seal_cx + 15, seal_cy), fill=(*BLOOD_RED, 90), width=2)
    draw.line((seal_cx, seal_cy - 15, seal_cx, seal_cy + 15), fill=(*BLOOD_RED, 90), width=2)

    # --- Subtle fold lines (aged map) ---
    draw.line((400, 0, 450, H), fill=(120, 95, 60, 20), width=2)
    draw.line((1200, 0, 1150, H), fill=(120, 95, 60, 15), width=2)

    # --- Light dust motes in candle beam ---
    for _ in range(60):
        dx = rng.gauss(W // 2, 250)
        dy = rng.uniform(20, 600)
        dr = rng.uniform(1, 3)
        draw.ellipse((dx - dr, dy - dr, dx + dr, dy + dr), fill=(*CANDLE_WARM, rng.randint(20, 60)))

    # --- Blindness motif: two faint eye-like circles, sightless ---
    eye_y = 280
    for eye_x in [meridian_x - 120, meridian_x + 120]:
        draw.ellipse((eye_x - 18, eye_y - 18, eye_x + 18, eye_y + 18),
                     outline=(*INK_FADED, 60), width=2)
        draw.line((eye_x - 12, eye_y, eye_x + 12, eye_y), fill=(*INK_FADED, 40), width=2)

    # --- Main title panel ---
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
