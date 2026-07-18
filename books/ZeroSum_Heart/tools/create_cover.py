#!/usr/bin/env python3
"""Cover: ZeroSum Heart — Two figures face across a cosmic balance scale beneath celestial rings, a luminous heart at the fulcrum."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel


ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560
CX, CY = W // 2, 1300          # center of the composition


def make_cover(mp: Path, op: Path) -> None:
    meta = json.loads(mp.read_text(encoding="utf-8"))
    title = meta.get("title", "ZeroSum Heart")
    author = meta.get("author", "Barış Kısır")
    model = meta.get("model", "")

    rng = random.Random("zerosum-heart-v2")
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── split-field background: warm left, cool right ─────────────────────
    for y in range(H):
        t = y / H
        for x in range(W):
            rel_x = x / W
            if rel_x < 0.5:
                # warm side: deep amber to dark crimson
                r = int(110 - 60 * t)
                g = int(60 - 40 * t)
                b = int(30 - 20 * t)
            else:
                # cool side: deep indigo to near-black
                r = int(15 - 10 * t)
                g = int(25 - 15 * t)
                b = int(60 - 35 * t)
            draw.point((x, y), fill=(max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), 255))

    # ── soft transition glow along the centre seam ────────────────────────
    seam_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(seam_glow)
    sd.ellipse((CX - 300, 800, CX + 300, 1800), fill=(220, 180, 100, 30))
    seam_glow = seam_glow.filter(ImageFilter.GaussianBlur(50))
    img = Image.alpha_composite(img, seam_glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── celestial astrolabe rings ─────────────────────────────────────────
    for ring_radius in range(350, 551, 50):
        alpha = int(60 - 40 * (ring_radius - 350) / 200)
        col = (200, 170, 120, max(10, alpha)) if ring_radius % 100 == 0 else (120, 140, 200, max(8, alpha // 2))
        draw.ellipse((CX - ring_radius, CY - ring_radius,
                       CX + ring_radius, CY + ring_radius),
                      outline=col, width=2)

    # ── astrolabe cross-hairs ─────────────────────────────────────────────
    for angle_deg in range(0, 360, 30):
        rad = math.radians(angle_deg)
        r1, r2 = 370, 520
        x1 = CX + r1 * math.cos(rad)
        y1 = CY + r1 * math.sin(rad)
        x2 = CX + r2 * math.cos(rad)
        y2 = CY + r2 * math.sin(rad)
        col = (180, 160, 100, 50) if angle_deg % 60 == 0 else (100, 120, 180, 30)
        draw.line((x1, y1, x2, y2), fill=col, width=2)

    # ── astrolabe degree ticks ────────────────────────────────────────────
    for deg in range(0, 360, 5):
        rad = math.radians(deg)
        is_major = deg % 30 == 0
        r_in = 345 if is_major else 355
        r_out = 360 if is_major else 358
        x1 = CX + r_in * math.cos(rad)
        y1 = CY + r_in * math.sin(rad)
        x2 = CX + r_out * math.cos(rad)
        y2 = CY + r_out * math.sin(rad)
        col = (200, 180, 130, 80) if is_major else (150, 160, 210, 40)
        draw.line((x1, y1, x2, y2), fill=col, width=3 if is_major else 1)

    # ── balance scale ─────────────────────────────────────────────────────
    # beam
    beam_col = (180, 160, 110, 200)
    draw.line((CX - 250, CY - 50, CX + 250, CY - 50), fill=beam_col, width=5)
    # centre post
    draw.line((CX, CY - 50, CX, CY + 30), fill=beam_col, width=5)
    # base of post
    draw.ellipse((CX - 20, CY + 20, CX + 20, CY + 50), fill=beam_col)
    # chains
    chain_col = (160, 150, 100, 180)
    for side, sign in ((-1, -1), (1, 1)):
        draw.line((CX + sign * 250, CY - 50, CX + sign * 250 + sign * 20, CY + 20), fill=chain_col, width=2)
        draw.line((CX + sign * 250, CY - 50, CX + sign * 250 - sign * 20, CY + 20), fill=chain_col, width=2)
        # left pan (warm side) - holds the glowing heart
        pan_cx = CX - 260
        pan_cy = CY + 80
        draw.ellipse((pan_cx - 65, pan_cy - 20, pan_cx + 65, pan_cy + 20), fill=(100, 70, 40, 180), outline=(180, 150, 80, 200), width=2)
        # right pan (cool side) - holds a shadow/shape
        pan_cx = CX + 260
        pan_cy = CY + 80
        draw.ellipse((pan_cx - 65, pan_cy - 20, pan_cx + 65, pan_cy + 20), fill=(30, 35, 50, 180), outline=(80, 90, 140, 200), width=2)

    # ── glowing heart on the left pan ─────────────────────────────────────
    heart_base_x, heart_base_y = CX - 260, CY + 60
    heart_parts = []
    for a in [a for a in range(0, 360, 3)]:
        rad = math.radians(a)
        # parametric heart curve
        t = rad
        sx = 16 * (math.sin(t) ** 3)
        sy = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
        hx = heart_base_x + sx * 3.5
        hy = heart_base_y - sy * 3.5
        heart_parts.append((hx, hy))

    # draw heart glow first, then the heart
    heart_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hgd = ImageDraw.Draw(heart_glow)
    hgd.ellipse((heart_base_x - 80, heart_base_y - 100, heart_base_x + 80, heart_base_y + 60), fill=(220, 150, 50, 35))
    heart_glow = heart_glow.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, heart_glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # draw the heart
    for i in range(len(heart_parts) - 1):
        draw.line((heart_parts[i][0], heart_parts[i][1],
                    heart_parts[i+1][0], heart_parts[i+1][1]),
                   fill=(240, 180, 60, 220), width=4)
        draw.line((heart_parts[i][0], heart_parts[i][1],
                    heart_parts[i+1][0], heart_parts[i+1][1]),
                   fill=(255, 220, 120, 80), width=8)

    # inner heart glow fill
    for py in range(int(heart_base_y - 90), int(heart_base_y + 50)):
        for px in range(int(heart_base_x - 50), int(heart_base_x + 50)):
            dist = math.sqrt((px - heart_base_x)**2 + (py - heart_base_y)**2)
            if dist < 35:
                alpha = int(max(0, 40 - dist))
                if alpha > 0:
                    draw.point((px, py), fill=(255, 200, 80, alpha))

    # ── shadow mass on the right pan ──────────────────────────────────────
    shadow_base_x, shadow_base_y = CX + 260, CY + 80
    for py in range(int(shadow_base_y - 30), int(shadow_base_y + 15)):
        for px in range(int(shadow_base_x - 45), int(shadow_base_x + 45)):
            dist = math.sqrt((px - shadow_base_x)**2 + (py - shadow_base_y)**2)
            if dist < 40:
                alpha = int(max(0, 120 * (1 - dist / 40)))
                if alpha > 0:
                    draw.point((px, py), fill=(80, 60, 120, alpha))

    # ── left figure (warm side) ───────────────────────────────────────────
    # a merchant/rogue silhouette
    lx = CX - 420
    fig_base_y = CY + 160

    # body
    body_col = (180, 140, 80, 210)
    # torso
    draw.polygon([(lx - 25, fig_base_y - 120), (lx + 25, fig_base_y - 120),
                   (lx + 35, fig_base_y), (lx - 35, fig_base_y)],
                  fill=body_col)
    # head
    draw.ellipse((lx - 18, fig_base_y - 165, lx + 18, fig_base_y - 130), fill=body_col)
    # hat / wide brim
    draw.ellipse((lx - 30, fig_base_y - 160, lx + 30, fig_base_y - 140), fill=body_col)
    draw.ellipse((lx - 12, fig_base_y - 175, lx + 12, fig_base_y - 158), fill=body_col)
    # arm reaching toward heart (right arm)
    draw.line((lx + 25, fig_base_y - 100, lx + 100, fig_base_y - 50, lx + 140, fig_base_y - 30),
              fill=body_col, width=8)

    # ── right figure (cool side) ──────────────────────────────────────────
    # a regal/scholar silhouette
    rx = CX + 420
    # torso with robes
    body_col2 = (60, 70, 120, 210)
    # robe
    draw.polygon([(rx - 30, fig_base_y - 130), (rx + 30, fig_base_y - 130),
                   (rx + 45, fig_base_y), (rx - 45, fig_base_y)],
                  fill=body_col2)
    # robe detail - collar
    draw.polygon([(rx - 20, fig_base_y - 130), (rx + 20, fig_base_y - 130),
                   (rx, fig_base_y - 90)],
                  fill=(70, 80, 140, 200))
    # head
    draw.ellipse((rx - 20, fig_base_y - 175, rx + 20, fig_base_y - 135), fill=body_col2)
    # crown / circlet
    draw.polygon([(rx - 24, fig_base_y - 170), (rx - 18, fig_base_y - 190),
                   (rx - 10, fig_base_y - 178), (rx, fig_base_y - 195),
                   (rx + 10, fig_base_y - 178), (rx + 18, fig_base_y - 190),
                   (rx + 24, fig_base_y - 170)],
                  fill=(100, 110, 180, 200))
    # arm reaching toward heart (left arm)
    draw.line((rx - 25, fig_base_y - 110, rx - 100, fig_base_y - 60, rx - 140, fig_base_y - 30),
              fill=body_col2, width=8)

    # ── floating embers / star particles ──────────────────────────────────
    for _ in range(200):
        px = rng.randint(50, W - 50)
        py = rng.randint(200, 2000)
        size = rng.uniform(1.5, 4.5)
        side_col = rng.choice(["warm", "cool"])
        if side_col == "warm":
            col = (240 - rng.randint(0, 60), 200 - rng.randint(0, 60), 80 + rng.randint(0, 40))
        else:
            col = (100 + rng.randint(0, 40), 150 + rng.randint(0, 50), 220 + rng.randint(0, 35))
        alpha = rng.randint(40, 150)
        draw.ellipse((int(px - size), int(py - size), int(px + size), int(py + size)),
                      fill=(*col, alpha))

    # ── floating geometric symbols (orbiting the astrolabe) ──────────────
    for i, deg in enumerate(range(0, 360, 45)):
        rad = math.radians(deg)
        orbit_r = 440
        ox = CX + orbit_r * math.cos(rad)
        oy = CY + orbit_r * math.sin(rad)
        # small diamond or circle
        if i % 2 == 0:
            col = (220, 190, 110, 100)
            draw.polygon([(ox, oy - 8), (ox + 6, oy), (ox, oy + 8), (ox - 6, oy)],
                          fill=col)
        else:
            col = (130, 170, 220, 100)
            draw.ellipse((ox - 6, oy - 6, ox + 6, oy + 6), fill=col)

    # ── ornate arch framing the composition ──────────────────────────────
    arch_col = (130, 110, 80, 120)
    draw.arc((50, 250, W - 50, CY * 2 + 100), 180, 0, fill=arch_col, width=4)
    # pillars
    draw.line((100, CY + 200, 100, H - 100), fill=arch_col, width=6)
    draw.line((W - 100, CY + 200, W - 100, H - 100), fill=arch_col, width=6)
    # pillar capitals
    draw.ellipse((85, CY + 180, 115, CY + 210), fill=arch_col)
    draw.ellipse((W - 115, CY + 180, W - 85, CY + 210), fill=arch_col)

    # ── title panel via shared utility ────────────────────────────────────
    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, title, author, model)
    img.convert("RGB").save(op, "PNG", optimize=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    mp = ROOT / a.metadata if not a.metadata.is_absolute() else a.metadata
    op = ROOT / a.out if not a.out.is_absolute() else a.out
    make_cover(mp, op)


if __name__ == "__main__":
    main()
