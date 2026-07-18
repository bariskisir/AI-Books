#!/usr/bin/env python3
"""Cover: Code of Salt and Honey — Cozy culinary mystery: a locked tasting room, honeycomb geometry, amber light, and cryptic recipe fragments."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# ── warm honey / amber / dark-wood palette ──────────────────────────────
AMBER_DARK = (60, 30, 15)       # wood / shadow
AMBER_MID = (140, 80, 30)      # mid amber
GOLDEN_HONEY = (220, 175, 60)  # honey glow
WARM_CREAM = (245, 225, 180)   # light / recipe paper
DEEP_BROWN = (40, 20, 8)       # bg base


def _hexagon_ring(xc: float, yc: float, radius: float) -> list[tuple[float, float]]:
    """Return 6 vertices of a regular hexagon centered at (xc, yc)."""
    return [
        (xc + radius * math.cos(math.radians(60 * i - 30)),
         yc + radius * math.sin(math.radians(60 * i - 30)))
        for i in range(6)
    ]


def make_cover(mp: Path, op: Path) -> None:
    meta = json.loads(mp.read_text(encoding="utf-8"))
    title = meta.get("title", "Code of Salt and Honey")
    author = meta.get("author", "Barış Kısır")
    model = meta.get("model", "")

    rng = random.Random()
    rng.seed(0xCAFE + 42)  # stable seed for reproducibility

    img = Image.new("RGBA", (W, H), DEEP_BROWN + (255,))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 1. Deep amber gradient background ────────────────────────────────
    # Top is very dark brown, descending into warm amber, then golden near the middle
    for y in range(H):
        t = y / H
        if t < 0.5:
            # dark brown -> warm amber
            p = t / 0.5
            r = int(AMBER_DARK[0] + (AMBER_MID[0] - AMBER_DARK[0]) * p)
            g = int(AMBER_DARK[1] + (AMBER_MID[1] - AMBER_DARK[1]) * p)
            b = int(AMBER_DARK[2] + (AMBER_MID[2] - AMBER_DARK[2]) * p)
        else:
            # warm amber -> golden honey glow near mid-section
            p = (t - 0.5) / 0.5
            r = int(AMBER_MID[0] + (GOLDEN_HONEY[0] - AMBER_MID[0]) * min(p, 0.6))
            g = int(AMBER_MID[1] + (GOLDEN_HONEY[1] - AMBER_MID[1]) * min(p, 0.6))
            b = int(AMBER_MID[2] + (GOLDEN_HONEY[2] - AMBER_MID[2]) * min(p, 0.6))
            if t > 0.7:
                # fade back toward darker toward bottom (for panel area)
                q = (t - 0.7) / 0.3
                r = int(r + (AMBER_MID[0] - r) * q)
                g = int(g + (AMBER_MID[1] - g) * q)
                b = int(b + (AMBER_MID[2] - b) * q)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── 2. Warm backlight glow behind the central composition ────────────
    glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)
    glow_cx, glow_cy = W // 2, 1100
    gd.ellipse((glow_cx - 500, glow_cy - 400, glow_cx + 500, glow_cy + 400),
               fill=(240, 190, 80, 40))
    gd.ellipse((glow_cx - 300, glow_cy - 250, glow_cx + 300, glow_cy + 250),
               fill=(255, 210, 100, 30))
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(60))
    img = Image.alpha_composite(img, glow_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 3. Honeycomb hex grid (subtle, fading toward edges) ──────────────
    hex_radius = 50
    hex_gap_x = hex_radius * 1.73  # sqrt(3) * r
    hex_gap_y = hex_radius * 1.5
    for row in range(-1, int(H / hex_gap_y) + 2):
        for col in range(-1, int(W / hex_gap_x) + 2):
            ox = col * hex_gap_x
            oy = row * hex_gap_y
            if row % 2 == 1:
                ox += hex_gap_x / 2
            cx, cy = ox, oy
            # Fade hexagons toward top (dark) and bottom (panel), strongest in the middle
            y_norm = (cy - 200) / 1400
            if y_norm < 0 or y_norm > 1:
                continue
            fade = 1.0 - abs(y_norm - 0.5) * 1.2
            fade = max(0, min(0.5, fade))
            if rng.random() > fade * 3:
                continue
            verts = _hexagon_ring(cx, cy, hex_radius)
            alpha = int(12 + fade * 25)
            hex_col = (
                int(180 + fade * 60),
                int(140 + fade * 40),
                int(60 + fade * 30),
                alpha,
            )
            draw.polygon(verts, fill=None, outline=hex_col, width=1)

    # ── 4. Tasting room door — tall, arched wooden door, slightly ajar ──
    door_x = W // 2
    door_w = 300
    door_top = 300
    door_bot = 1680

    # Door frame (dark wood)
    draw.rectangle((door_x - door_w // 2 - 18, door_top - 20,
                    door_x + door_w // 2 + 18, door_bot),
                   fill=(45, 22, 8, 230))
    # Arch top
    draw.ellipse((door_x - door_w // 2 - 18, door_top - door_w // 2 - 30,
                  door_x + door_w // 2 + 18, door_top + door_w // 2),
                 fill=(45, 22, 8, 230))

    # Door panels (slightly lighter wood)
    draw.rectangle((door_x - door_w // 2 - 4, door_top + 10,
                    door_x + door_w // 2 + 4, door_bot),
                   fill=(70, 38, 16, 240))
    draw.ellipse((door_x - door_w // 2 - 4, door_top - door_w // 2 - 10,
                  door_x + door_w // 2 + 4, door_top + door_w // 2 + 10),
                 fill=(70, 38, 16, 240))

    # Door is slightly ajar — warm light spills through the crack
    for crack_x in range(-6, 7, 2):
        light_col = (245, 210, 120, 30 + abs(crack_x) * 5)
        draw.line((door_x + crack_x, door_top + 40, door_x + crack_x, door_bot - 20),
                  fill=light_col, width=2)

    # Diagonal light beam from crack
    beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam)
    for _ in range(30):
        ang = rng.uniform(-0.35, 0.35)
        length = rng.randint(400, 800)
        bx = door_x
        by = rng.randint(door_top + 50, door_top + 300)
        ex = bx + int(math.sin(ang) * length)
        ey = by + length
        alpha = rng.randint(4, 12)
        bd.line((bx, by, ex, ey), fill=(255, 215, 120, alpha), width=rng.randint(8, 25))
    beam = beam.filter(ImageFilter.GaussianBlur(12))
    img = Image.alpha_composite(img, beam)
    draw = ImageDraw.Draw(img, "RGBA")

    # Door details: vertical planks
    for plank in range(-3, 4):
        px = door_x + plank * 38
        draw.line((px, door_top + 15, px, door_bot),
                  fill=(55, 28, 10, 180), width=2)

    # Door handle / ornate lock
    lock_x = door_x + 100
    lock_y = door_top + 400
    # Lock plate
    draw.ellipse((lock_x - 22, lock_y - 28, lock_x + 28, lock_y + 28),
                 fill=(180, 150, 80, 220), outline=(120, 90, 40, 200), width=3)
    # Keyhole
    draw.ellipse((lock_x + 1, lock_y - 6, lock_x + 9, lock_y + 6),
                 fill=(20, 15, 8, 240))
    draw.rectangle((lock_x + 3, lock_y + 2, lock_x + 7, lock_y + 18),
                   fill=(20, 15, 8, 240))
    # Keyhole glow
    draw.ellipse((lock_x - 6, lock_y - 10, lock_x + 16, lock_y + 22),
                 fill=(255, 200, 80, 18))

    # ── 5. Honey jar silhouette on a shelf ──────────────────────────────
    jar_x = door_x + door_w // 2 + 140
    jar_y = 1480
    jar_w, jar_h = 90, 120

    # Jar body
    draw.rectangle((jar_x - jar_w // 2, jar_y - jar_h // 2 + 15,
                    jar_x + jar_w // 2, jar_y + jar_h // 2),
                   fill=(80, 45, 18, 220))
    draw.ellipse((jar_x - jar_w // 2, jar_y - jar_h // 2 - 5,
                  jar_x + jar_w // 2, jar_y - jar_h // 2 + 25),
                 fill=(80, 45, 18, 220))

    # Jar neck
    draw.rectangle((jar_x - 20, jar_y - jar_h // 2 - 25,
                    jar_x + 20, jar_y - jar_h // 2),
                   fill=(60, 32, 12, 220))
    # Jar lid
    draw.rectangle((jar_x - 28, jar_y - jar_h // 2 - 32,
                    jar_x + 28, jar_y - jar_h // 2 - 22),
                   fill=(180, 140, 60, 230))

    # Golden glow emanating from the jar
    jar_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    jd = ImageDraw.Draw(jar_glow)
    jd.ellipse((jar_x - 100, jar_y - 100, jar_x + 100, jar_y + 100),
               fill=(240, 200, 80, 20))
    jd.ellipse((jar_x - 60, jar_y - 60, jar_x + 60, jar_y + 60),
               fill=(255, 220, 100, 15))
    jar_glow = jar_glow.filter(ImageFilter.GaussianBlur(20))
    img = Image.alpha_composite(img, jar_glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Label on jar
    draw.rectangle((jar_x - 35, jar_y - 25, jar_x + 35, jar_y + 15),
                   fill=(220, 200, 160, 200), outline=(160, 130, 80, 180), width=1)

    # ── 6. Cryptic recipe fragments (torn paper) floating in foreground ──
    recipe_colors = [(235, 215, 175), (240, 220, 180), (225, 205, 165),
                     (245, 230, 190), (230, 210, 170)]
    recipe_phrases = [
        "3 parts salt, 1 part...",
        "steep 40 min @ 95F",
        "hive #7: wildflower?",
        "tbsp of amber — no",
        "turn left at the oak",
        "the key is in the comb",
        "honey + tears = ?",
        "distill twice over",
    ]

    recipe_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(recipe_layer)

    for _ in range(7):
        # Random torn-paper rectangle
        px = rng.randint(100, W - 200)
        py = rng.randint(400, 1500)
        pw = rng.randint(80, 150)
        ph = rng.randint(30, 55)
        angle = rng.uniform(-0.25, 0.25)
        paper_color = rng.choice(recipe_colors)
        alpha_paper = rng.randint(150, 220)

        # Draw ragged rectangle (torn edges via jitter)
        corners = [
            (px + rng.randint(-4, 4), py + rng.randint(-4, 4)),
            (px + pw + rng.randint(-4, 4), py + rng.randint(-4, 4)),
            (px + pw + rng.randint(-4, 4), py + ph + rng.randint(-4, 4)),
            (px + rng.randint(-4, 4), py + ph + rng.randint(-4, 4)),
        ]
        # Rotate corners
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        cx_ = px + pw // 2
        cy_ = py + ph // 2
        rotated = []
        for (rx, ry) in corners:
            dx = rx - cx_
            dy = ry - cy_
            rotated.append((cx_ + dx * cos_a - dy * sin_a,
                            cy_ + dx * sin_a + dy * cos_a))
        rd.polygon(rotated, fill=(*paper_color, alpha_paper))
        rd.polygon(rotated, fill=(*paper_color, alpha_paper), outline=(160, 130, 90, 180), width=1)

        # Handwriting scribble
        phrase = rng.choice(recipe_phrases)
        fx, fy = rotated[0]
        for ch_i, ch in enumerate(phrase):
            ch_x = fx + ch_i * 10 + rng.randint(-2, 2)
            ch_y = fy + rng.randint(6, 18)
            ch_color = (50 + rng.randint(0, 30), 40 + rng.randint(0, 20), 30 + rng.randint(0, 15))
            draw.text((ch_x, ch_y), ch, fill=(*ch_color, 180))
        # Draw via draw directly on img for text clarity
        for ch_i, ch in enumerate(phrase):
            ch_x = rotated[0][0] + ch_i * 10 + rng.randint(-2, 2)
            ch_y = rotated[0][1] + rng.randint(6, 18)
            ch_color = (50 + rng.randint(0, 30), 40 + rng.randint(0, 20), 30 + rng.randint(0, 15))
            draw.text((ch_x, ch_y), ch, fill=(*ch_color, 180))

    img = Image.alpha_composite(img, recipe_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 7. Fine golden dust motes in the light beam ──────────────────────
    for _ in range(80):
        dx = rng.randint(door_x - 250, door_x + 250)
        dy = rng.randint(350, 1600)
        ds = rng.randint(1, 4)
        da = rng.randint(30, 90)
        draw.ellipse((dx - ds, dy - ds, dx + ds, dy + ds),
                     fill=(245, 215, 130, da))

    # ── 8. Hanging honey drip from top of door frame ────────────────────
    for drip in range(rng.randint(8, 14)):
        dx = door_x - door_w // 2 + rng.randint(10, door_w - 10)
        dy_start = door_top - 20 + rng.randint(0, 40)
        dy_end = dy_start + rng.randint(30, 100)
        drip_w = rng.randint(2, 5)
        drip_alpha = rng.randint(80, 160)
        draw.line((dx, dy_start, dx, dy_end),
                  fill=(180 + rng.randint(0, 40), 140 + rng.randint(0, 30), 40 + rng.randint(0, 20), drip_alpha),
                  width=drip_w)
        # Drip droplet at tip
        draw.ellipse((dx - drip_w, dy_end - 2, dx + drip_w, dy_end + 4),
                     fill=(200, 160, 60, drip_alpha))

    # ── 9. Shelf below the jar ───────────────────────────────────────────
    draw.rectangle((door_x - door_w // 2 - 40, jar_y + jar_h // 2 + 5,
                    door_x + door_w // 2 + 200, jar_y + jar_h // 2 + 12),
                   fill=(55, 28, 10, 200))

    # ── 10. Save ─────────────────────────────────────────────────────────
    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, title, author, model)
    img.convert("RGB").save(op, "PNG", optimize=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    meta_path = ROOT / a.metadata if not a.metadata.is_absolute() else a.metadata
    out_path = ROOT / a.out if not a.out.is_absolute() else a.out
    make_cover(meta_path, out_path)


if __name__ == "__main__":
    main()
