#!/usr/bin/env python3
"""Cover: The Weavers of Oshun — A deaf teenage weaver in a floating Lagos market discovers her tapestries can physically re-weave time, but each use unravels a thread from her own lifespan."""

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
rng.seed(137925468)

# Africanfuturism palette — deep Lagos lagoon night, warm market amber, luminous time-magic teal/gold
SKY_TOP = (8, 6, 28)
SKY_BOT = (15, 12, 25)
HORIZON = (25, 20, 30)
WATER_COLOR = (5, 10, 18)
WOOD_DARK = (22, 16, 10)
WOOD_MID = (35, 26, 18)
LANTERN_WARM = (240, 170, 55)
MAGIC_TEAL = (80, 230, 220)
MAGIC_GOLD = (255, 200, 50)
THREAD_DIM = (180, 220, 210)
ORISHA_GLOW = (255, 190, 40)


def _sky_gradient(draw: ImageDraw.ImageDraw) -> None:
    """Deep indigo-violet night sky fading to warm dark at the horizon."""
    for y in range(1500):
        t = y / 1500
        if t < 0.6:
            lt = t / 0.6
            r = int(SKY_TOP[0] + (SKY_BOT[0] - SKY_TOP[0]) * lt)
            g = int(SKY_TOP[1] + (SKY_BOT[1] - SKY_TOP[1]) * lt)
            b = int(SKY_TOP[2] + (SKY_BOT[2] - SKY_TOP[2]) * lt)
        else:
            lt = (t - 0.6) / 0.4
            r = int(SKY_BOT[0] + (HORIZON[0] - SKY_BOT[0]) * lt)
            g = int(SKY_BOT[1] + (HORIZON[1] - SKY_BOT[1]) * lt)
            b = int(SKY_BOT[2] + (HORIZON[2] - SKY_BOT[2]) * lt)
        draw.line((0, y, W, y), fill=(r, g, b, 255))


def _stars(draw: ImageDraw.ImageDraw) -> None:
    """Tiny scattered stars in the upper night sky."""
    for _ in range(200):
        sx = rng.randint(0, W)
        sy = rng.randint(0, 500)
        sr = rng.uniform(0.5, 2.5)
        alpha = rng.randint(80, 220)
        bri = rng.randint(180, 255)
        draw.ellipse(
            (sx - sr, sy - sr, sx + sr, sy + sr),
            fill=(bri, bri, bri + 10, alpha),
        )


def _orisha_presence(img: Image.Image) -> Image.Image:
    """The Orisha's Voice — a luminous abstract golden face in the upper sky, formed from woven light."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # Diffuse aura glow
    d.ellipse((W // 2 - 280, 60, W // 2 + 280, 420), fill=(255, 190, 40, 5))
    d.ellipse((W // 2 - 200, 90, W // 2 + 200, 390), fill=(255, 200, 60, 8))

    # Face-like arrangement of concentric arcs suggesting an Orisha mask
    # Crown / headdress arcs
    for i in range(5):
        spread = 60 + i * 25
        d.arc(
            (W // 2 - spread, 80 - i * 6, W // 2 + spread, 200),
            180, 360, fill=(255, 200, 60, 20 - i * 2), width=3,
        )

    # Eyes as woven golden circles
    for ex, ey in [(W // 2 - 80, 210), (W // 2 + 80, 210)]:
        d.ellipse((ex - 30, ey - 20, ex + 30, ey + 20), fill=(255, 200, 60, 4))
        d.ellipse((ex - 20, ey - 12, ex + 20, ey + 12), fill=(255, 220, 100, 8))
        d.ellipse((ex - 6, ey - 6, ex + 6, ey + 6), fill=(255, 230, 150, 20))

    # Weft-thread lines across the face area (like a veil of woven light)
    for ty in range(140, 320, 10):
        wav = int(6 * math.sin(ty * 0.05 + 1.3))
        d.line(
            (W // 2 - 140 + wav, ty, W // 2 + 140 + wav, ty),
            fill=(255, 200, 60, rng.randint(4, 12)), width=1,
        )

    # Nose / vertical thread line
    d.line((W // 2, 175, W // 2, 260), fill=(255, 210, 70, 12), width=2)

    # Mouth as an arc
    d.arc(
        (W // 2 - 50, 255, W // 2 + 50, 285),
        0, 180, fill=(255, 200, 60, 15), width=2,
    )

    layer = layer.filter(ImageFilter.GaussianBlur(8))
    return Image.alpha_composite(img, layer)


def _floating_market(draw: ImageDraw.ImageDraw) -> list[tuple[int, int]]:
    """Draw wooden market stalls on stilts framing the left and right edges. Returns lantern positions."""
    stall_y = 780
    stalls = [
        (60, 200, 540), (280, 160, 440),           # left side
        (W - 260, 200, 520), (W - 480, 160, 460),  # right side
    ]

    lanterns = []

    for sx, sw, sh in stalls:
        # Main stall body
        draw.rectangle((sx, stall_y, sx + sw, stall_y + sh), fill=(*WOOD_DARK, 220))

        # Roof with slight overhang
        draw.rectangle((sx - 12, stall_y - 8, sx + sw + 12, stall_y), fill=(*WOOD_MID, 230))

        # Vertical stilts descending into water
        n_stilts = max(2, sw // 50)
        for si in range(n_stilts):
            st_x = sx + 15 + (sw - 30) * si // (n_stilts - 1) if n_stilts > 1 else sx + sw // 2
            draw.rectangle((st_x - 3, stall_y + sh - 40, st_x + 3, stall_y + sh + 320),
                           fill=(*WOOD_DARK, 200))

        # Horizontal shelves
        for shelf_y in (stall_y + sh // 3, stall_y + 2 * sh // 3):
            draw.line((sx + 5, shelf_y, sx + sw - 5, shelf_y), fill=(45, 32, 20, 120), width=2)

        # Lantern positions (2 per stall)
        for la_x in (sx + sw // 4, sx + 3 * sw // 4):
            ly = stall_y + 20
            lanterns.append((la_x, ly))

    return lanterns


def _lanterns(draw: ImageDraw.ImageDraw, positions: list[tuple[int, int]]) -> None:
    """Draw warm glowing lanterns hanging from the market stalls."""
    for lx, ly in positions:
        # Glow halos
        for gr in (35, 25, 15, 8):
            ga = max(4, 28 - gr)
            draw.ellipse((lx - gr, ly - gr, lx + gr, ly + gr), fill=(*LANTERN_WARM, ga))
        # Lantern body (rounded rectangle)
        draw.ellipse((lx - 7, ly - 9, lx + 7, ly + 9), fill=(*LANTERN_WARM, 220))
        draw.ellipse((lx - 4, ly - 6, lx + 4, ly + 6), fill=(255, 210, 100, 200))
        # Hanging string
        draw.line((lx, ly - 14, lx + (1 if ly % 2 == 0 else -1) * 2, ly - 11),
                  fill=(60, 50, 40, 80), width=1)


def _loom_and_tapestry(draw: ImageDraw.ImageDraw) -> tuple[int, int]:
    """Draw the central wooden loom with a glowing half-woven tapestry. Returns (cx, cy) of loom center."""
    cx, cy = W // 2, 1040
    frame = (40, 30, 20)

    # Loom frame posts
    draw.rectangle((cx - 125, cy - 210, cx - 110, cy + 210), fill=(*frame, 230))
    draw.rectangle((cx + 110, cy - 210, cx + 125, cy + 210), fill=(*frame, 230))
    # Top and bottom beams
    draw.rectangle((cx - 130, cy - 215, cx + 130, cy - 200), fill=(*frame, 230))
    draw.rectangle((cx - 130, cy + 200, cx + 130, cy + 215), fill=(*frame, 230))
    # Cross-brace
    draw.rectangle((cx - 112, cy - 3, cx + 112, cy + 3), fill=(*frame, 150))

    # Warp threads (vertical — the un-woven strings)
    for wx in range(cx - 108, cx + 109, 10):
        draw.line((wx, cy - 205, wx, cy + 205), fill=(*THREAD_DIM, rng.randint(80, 140)), width=1)

    # Weft tapestry — woven portion with alternating colors
    pattern = [MAGIC_TEAL, MAGIC_GOLD, (200, 150, 220), (100, 200, 180), (255, 180, 100)]
    weave_top = cy - 170
    weave_bot = cy + 150
    for wy in range(weave_top, weave_bot, 5):
        wav = int(7 * math.sin(wy * 0.07 + 0.5))
        col = rng.choice(pattern)
        alpha = rng.randint(120, 200)
        draw.line(
            (cx - 108 + wav, wy, cx + 108 + wav, wy),
            fill=(*col, alpha), width=2,
        )
        # Occasional bright accent thread
        if rng.random() < 0.12:
            draw.line(
                (cx - 105 + wav, wy, cx + 105 + wav, wy),
                fill=(255, 255, 255, 180), width=1,
            )

    # Tapestry edge — slightly irregular outline
    for ey in (weave_top, weave_bot):
        e_wav = int(5 * math.sin(ey * 0.1))
        draw.line(
            (cx - 110 + e_wav, ey, cx + 110 + e_wav, ey),
            fill=(*frame, 180), width=2,
        )

    return cx, cy


def _tapestry_glow(img: Image.Image, cx: int, cy: int) -> Image.Image:
    """Glow effect emanating from the woven tapestry."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse((cx - 130, cy - 190, cx + 130, cy + 190), fill=(80, 220, 210, 5))
    d.ellipse((cx - 100, cy - 160, cx + 100, cy + 160), fill=(255, 200, 50, 4))
    layer = layer.filter(ImageFilter.GaussianBlur(15))
    return Image.alpha_composite(img, layer)


def _damilola_silhouette(draw: ImageDraw.ImageDraw, cx: int, cy: int) -> None:
    """Silhouette of Damilola seated at the loom, hands working the threads."""
    fig_x = cx - 145
    fig_y = cy + 15

    # Head
    draw.ellipse((fig_x - 9, fig_y - 58, fig_x + 9, fig_y - 40), fill=(4, 3, 7, 210))
    # Hair / wrapped head tie hint
    draw.arc((fig_x - 12, fig_y - 62, fig_x + 12, fig_y - 44), 190, 350,
             fill=(4, 3, 7, 200), width=3)

    # Body — seated posture leaning slightly forward toward loom
    draw.polygon([
        (fig_x - 15, fig_y - 40), (fig_x + 15, fig_y - 40),
        (fig_x + 16, fig_y + 18), (fig_x - 16, fig_y + 18),
    ], fill=(4, 3, 7, 200))

    # Arms extended to work the loom
    draw.line((fig_x - 14, fig_y - 28, cx - 105, cy - 40),
              fill=(4, 3, 7, 180), width=4)
    draw.line((fig_x + 14, fig_y - 28, cx - 105, cy + 30),
              fill=(4, 3, 7, 180), width=4)

    # Small detail — hand position
    draw.ellipse((cx - 108, cy - 43, cx - 102, cy - 37), fill=(4, 3, 7, 200))
    draw.ellipse((cx - 108, cy + 27, cx - 102, cy + 33), fill=(4, 3, 7, 200))


def _magic_threads(img: Image.Image, cx: int, cy: int) -> Image.Image:
    """Luminous threads lifting from the tapestry, spiraling upward — time being rewoven."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # Main thread bundles spiraling upward
    for ti in range(30):
        start_y = cy + rng.randint(-100, 100)
        start_x = cx + rng.randint(-90, 90)
        pts = [(start_x, start_y)]
        px, py = start_x, start_y
        curve_bias = rng.uniform(-0.8, 0.8)
        for step in range(14):
            px += rng.randint(-12, 18) + curve_bias * 12
            py -= rng.randint(20, 55)
            # Slight spiral oscillation
            px += int(6 * math.sin(step * 0.8 + ti))
            pts.append((px, py))
        col = rng.choice([MAGIC_TEAL, MAGIC_GOLD, (200, 180, 255)])
        d.line(pts, fill=(*col, rng.randint(35, 90)), width=rng.randint(2, 5))

    # Loose thread ends — fragments unraveling
    for fi in range(12):
        fx = cx + rng.randint(-80, 80)
        fy = cy + rng.randint(-120, 120)
        pts = [(fx, fy)]
        for step in range(6):
            fx += rng.randint(-20, 20)
            fy += rng.randint(-30, -10)
            pts.append((fx, fy))
        d.line(pts, fill=(*MAGIC_TEAL, rng.randint(20, 50)), width=1)

    # Luminous particles / sparkles along the thread paths
    for pi in range(200):
        px = cx + rng.randint(-250, 250)
        py = 250 + rng.randint(0, 700)
        pr = rng.uniform(1, 4.5)
        pc = rng.choice([MAGIC_TEAL, MAGIC_GOLD, (255, 255, 255)])
        d.ellipse((px - pr, py - pr, px + pr, py + pr),
                  fill=(*pc, rng.randint(30, 150)))

    # Larger timeline orbs — critical moments being rewoven
    for oi in range(25):
        ox = cx + rng.randint(-180, 180)
        oy = 350 + rng.randint(0, 550)
        orad = rng.randint(5, 14)
        oc = rng.choice([MAGIC_TEAL, MAGIC_GOLD])
        d.ellipse((ox - orad, oy - orad, ox + orad, oy + orad),
                  fill=(*oc, rng.randint(15, 50)))
        # Inner bright core
        if orad > 7:
            d.ellipse((ox - orad // 2, oy - orad // 2, ox + orad // 2, oy + orad // 2),
                      fill=(*oc, 60))

    layer = layer.filter(ImageFilter.GaussianBlur(2))
    return Image.alpha_composite(img, layer)


def _water_and_reflections(draw: ImageDraw.ImageDraw, lantern_positions: list[tuple[int, int]]) -> None:
    """Dark lagoon surface with warm reflected lantern lights and stilts descending into water."""
    water_y = 1470
    # Water fill
    draw.rectangle((0, water_y, W, H), fill=(*WATER_COLOR, 235))

    # Water horizon line
    for wl_x in range(0, W, 2):
        wav_h = int(1.5 * math.sin(wl_x * 0.05))
        draw.point((wl_x, water_y + wav_h), fill=(25, 30, 50, 200))

    # Reflected lantern light in the water — warm golden streaks
    for lx, ly in lantern_positions:
        for ri in range(10):
            ry = water_y + 8 + ri * 14 + rng.randint(-3, 3)
            r_alpha = max(8, 60 - ri * 6)
            r_width = max(2, 22 - ri * 2)
            offset = rng.randint(-4, 4)
            draw.line(
                (lx - r_width + offset, ry, lx + r_width + offset, ry),
                fill=(*LANTERN_WARM, r_alpha), width=2,
            )

    # Broader ambient reflection
    for ai in range(15):
        ax = rng.randint(0, W)
        ay = water_y + 10 + rng.randint(0, 160)
        alen = rng.randint(30, 120)
        draw.line(
            (ax, ay, ax + alen, ay),
            fill=(*LANTERN_WARM, rng.randint(3, 10)), width=2,
        )

    # Stilt reflections continuing into water
    for sx in [80, 200, 300, W - 240, W - 400, W - 80]:
        draw.rectangle((sx - 2, water_y, sx + 2, water_y + 140),
                       fill=(8, 6, 5, 120))

    # Water ripples
    for wi in range(50):
        wx = rng.randint(0, W)
        wy = water_y + 10 + rng.randint(0, 220)
        ww = rng.randint(15, 60)
        draw.line((wx, wy, wx + ww, wy),
                  fill=(40, 50, 65, rng.randint(15, 50)), width=1)


def _vignette(draw: ImageDraw.ImageDraw) -> None:
    """Darken the edges to draw focus to the center."""
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(40 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 55))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 55))


def make_cover(mp: Path, op: Path) -> None:
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    # 1. Base image with sky gradient
    img = Image.new("RGBA", (W, H), (8, 6, 28, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    _sky_gradient(draw)

    # 2. Stars
    _stars(draw)

    # 3. Orisha's Voice — ethereal golden presence
    img = _orisha_presence(img)
    draw = ImageDraw.Draw(img, "RGBA")

    # 4. Floating market stalls
    lantern_positions = _floating_market(draw)

    # 5. Warm lanterns
    _lanterns(draw, lantern_positions)

    # 6. Central loom
    cx, cy = _loom_and_tapestry(draw)

    # 7. Glow from the woven tapestry
    img = _tapestry_glow(img, cx, cy)
    draw = ImageDraw.Draw(img, "RGBA")

    # 8. Damilola silhouette
    _damilola_silhouette(draw, cx, cy)

    # 9. Magic threads lifting upward
    img = _magic_threads(img, cx, cy)
    draw = ImageDraw.Draw(img, "RGBA")

    # 10. Water surface with reflections
    _water_and_reflections(draw, lantern_positions)

    # 11. Vignette
    _vignette(draw)

    # 12. Title panel and save
    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, title, author, model)
    img.convert("RGB").save(op, "PNG", optimize=True)


def main() -> None:
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
