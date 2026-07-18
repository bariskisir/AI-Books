#!/usr/bin/env python3
"""Cover: What Burns the Wisteria — Magical Realism Family Drama: the Tanaka family's wisteria vine blooms in colors visible only to family members, each hue foretelling a death; the teenage granddaughter sees a color meaning the vine itself will die by winter, along with the family's oldest secret."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# ── Twilight Japanese garden palette ──────────────────────────────────────
SKY_TOP = (18, 10, 38)         # deep indigo night sky
SKY_MID = (48, 25, 65)         # twilight purple
SKY_BOTTOM = (70, 55, 80)      # hazy dusk horizon
GROUND_COLOR = (30, 38, 35)    # dark earth / moss
STONE_GRAY = (75, 78, 80)
LANTERN_WARM = (210, 140, 60)
VINE_WOOD = (55, 30, 20)       # wisteria trunk/stem
FOLIAGE_DARK = (18, 35, 22)

# Prophetic bloom colors (each foretells a different death)
PROPHECY_COLORS = [
    (200, 40, 50, 220),        # RED    — violent death
    (220, 180, 60, 220),       # GOLD   — peaceful passing
    (70, 130, 220, 200),       # BLUE   — death by water
    (180, 80, 180, 200),       # VIOLET — lingering illness
    (160, 200, 80, 200),       # GREEN  — death in nature
    (240, 200, 120, 210),      # AMBER  — sudden accident
]

# The deadly color — what Emi sees: the vine's own death color
DEATH_OF_VINE = (210, 205, 195, 230)  # pale spectral white

rng = random.Random()
rng.seed(1804552093)


def _twilight_gradient(draw: ImageDraw) -> None:
    """Three-band vertical gradient: indigo night → twilight purple → hazy dusk."""
    for y in range(H):
        t = y / H
        if t < 0.55:
            lt = t / 0.55
            r = int(SKY_TOP[0] + (SKY_MID[0] - SKY_TOP[0]) * lt)
            g = int(SKY_TOP[1] + (SKY_MID[1] - SKY_TOP[1]) * lt)
            b = int(SKY_TOP[2] + (SKY_MID[2] - SKY_TOP[2]) * lt)
        else:
            lt = (t - 0.55) / 0.45
            r = int(SKY_MID[0] + (SKY_BOTTOM[0] - SKY_MID[0]) * lt)
            g = int(SKY_MID[1] + (SKY_BOTTOM[1] - SKY_MID[1]) * lt)
            b = int(SKY_MID[2] + (SKY_BOTTOM[2] - SKY_MID[2]) * lt)
        draw.line((0, y, W, y), fill=(r, g, b, 255))


def _draw_ground_and_path(draw: ImageDraw) -> None:
    """Dark mossy ground with a winding stone path receding into the distance."""
    # Ground plane (lower 30%)
    ground_top = int(H * 0.72)
    for y in range(ground_top, H):
        t = (y - ground_top) / (H - ground_top)
        darken = 1.0 - t * 0.3
        r = int(GROUND_COLOR[0] * darken)
        g = int(GROUND_COLOR[1] * darken)
        b = int(GROUND_COLOR[2] * darken)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # Winding stone path — perspective: wider at bottom, narrower at horizon
    for step in range(18):
        st = step / 18
        path_y = ground_top + 30 + st * (H - ground_top - 60)
        path_width = int(80 + st * 300)
        path_alpha = int(100 + st * 80)
        cx = W // 2 + int(math.sin(st * 3.5 + 0.7) * 180)
        # Stone slab (rough ellipse)
        slab_w = path_width + rng.randint(-20, 20)
        slab_h = 12 + int(st * 18)
        draw.ellipse(
            (cx - slab_w // 2, path_y - slab_h,
             cx + slab_w // 2, path_y + slab_h),
            fill=(*STONE_GRAY, path_alpha),
        )
        # Moss edge on stones
        if rng.random() < 0.6:
            draw.ellipse(
                (cx - slab_w // 2 + rng.randint(2, 10), path_y - slab_h + 2,
                 cx + slab_w // 2 - rng.randint(2, 10), path_y + slab_h - 2),
                fill=(*FOLIAGE_DARK, 60 + path_alpha // 2),
            )


def _draw_wisteria_arbor(draw: ImageDraw) -> None:
    """The massive wisteria arbor — two upright posts + cross beam + hanging vines."""
    # Left post
    lx = int(W * 0.22)
    post_top = int(H * 0.02)
    post_bot = int(H * 0.68)
    draw.rectangle((lx - 8, post_top, lx + 8, post_bot), fill=(*VINE_WOOD, 235))
    # Right post
    rx = int(W * 0.78)
    draw.rectangle((rx - 8, post_top, rx + 8, post_bot), fill=(*VINE_WOOD, 235))
    # Cross beam (top)
    beam_y = post_top + 20
    draw.rectangle((lx - 12, beam_y - 12, rx + 12, beam_y + 12), fill=(*VINE_WOOD, 235))
    # Secondary cross beams
    for bx in range(lx, rx, 120):
        draw.rectangle((bx - 4, beam_y - 8, bx + 4, beam_y + 60), fill=(*VINE_WOOD, 200))

    # Twisted vine trunks winding up the posts
    for side_x in (lx, rx):
        for s in range(6):
            sy = post_bot - s * 60
            sway = int(math.sin(s * 1.2) * 12)
            draw.ellipse(
                (side_x + sway - 6, sy - 26,
                 side_x + sway + 6, sy + 26),
                fill=(*VINE_WOOD, 180 + s * 8),
            )

    # Thick canopy vines stretching horizontally between posts
    for v in range(12):
        vy = beam_y + rng.randint(0, 80)
        vine_pts = []
        for x in range(lx + 20, rx - 15, 15):
            t = (x - lx) / (rx - lx)
            sway_y = math.sin(t * 8 + v * 1.7) * 18 + math.sin(t * 16 + v * 0.7) * 6
            vine_pts.append((x, vy + sway_y))
        if len(vine_pts) > 1:
            draw.line(vine_pts, fill=(*VINE_WOOD, 80 + v * 8), width=rng.randint(2, 5))

    # Canopy foliage mass (dark green backdrop above the flowers)
    foliage = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(foliage)
    for _ in range(80):
        fx = rng.randint(lx - 60, rx + 60)
        fy = rng.randint(beam_y - 20, beam_y + 180)
        fr = rng.randint(30, 120)
        alpha = rng.randint(20, 70)
        fd.ellipse((fx - fr, fy - fr, fx + fr, fy + fr),
                    fill=(*FOLIAGE_DARK, alpha))
    foliage = foliage.filter(ImageFilter.GaussianBlur(15))
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img = Image.alpha_composite(img, foliage)
    return img


def _draw_hanging_blooms(draw: ImageDraw) -> None:
    """Draw hanging wisteria racemes (flower clusters) in multiple prophetic colors.

    Each raceme hangs down from the canopy, cascading in the signature wisteria shape:
    a thick stem with dense pea-like florets along it.
    """
    lx = int(W * 0.22)
    rx = int(W * 0.78)
    canopy_top = int(H * 0.02)
    canopy_bottom = canopy_top + 200

    # Normal prophetic blooms
    for _ in range(45):
        # Position along the canopy
        bx = rng.randint(lx - 30, rx + 30)
        by = rng.randint(canopy_top, canopy_bottom)

        # Raceme length and direction (hanging down)
        rl = rng.randint(50, 140)
        rw = rng.randint(10, 22)

        # Pick a prophecy color
        col = rng.choice(PROPHECY_COLORS)
        base_alpha = col[3] if len(col) > 3 else 200

        # Stem
        draw.line((bx, by, bx + rng.randint(-8, 8), by + rl),
                  fill=(60, 45, 35, base_alpha // 2), width=2)

        # Florets along the stem — dense overlapping circles
        for fi in range(0, rl, 6):
            f_offset = fi / rl
            f_width = int(rw * (1 - f_offset * 0.5))
            f_x = bx + int(math.sin(fi * 0.7) * f_width * 0.3)
            f_y = by + fi
            f_r = rng.randint(3, max(4, f_width // 3))
            alpha = int(base_alpha * (1 - f_offset * 0.3))
            draw.ellipse(
                (f_x - f_r, f_y - f_r, f_x + f_r, f_y + f_r),
                fill=(col[0], col[1], col[2], alpha),
            )
            # Highlight on floret
            highlight_alpha = min(255, alpha + 40)
            draw.ellipse(
                (f_x - f_r // 3, f_y - f_r // 3, f_x + f_r // 3, f_y + f_r // 3),
                fill=(min(255, col[0] + 60), min(255, col[1] + 60),
                      min(255, col[2] + 60), highlight_alpha // 2),
            )

    # The single DEATH OF VINE raceme — palest white, prominently placed, center-left
    dx, dy = lx + (rx - lx) // 3, canopy_top + 30
    drl = 160  # Extra long
    dw = 26
    draw.line((dx, dy, dx - 5, dy + drl), fill=(80, 75, 70, 180), width=3)
    for fi in range(0, drl, 5):
        f_offset = fi / drl
        f_width = int(dw * (1 - f_offset * 0.6))
        f_x = dx + int(math.sin(fi * 0.5 + 0.3) * f_width * 0.25)
        f_y = dy + fi
        f_r = rng.randint(4, max(5, f_width // 3))
        alpha = int(DEATH_OF_VINE[3] * (1 - f_offset * 0.25))
        draw.ellipse(
            (f_x - f_r, f_y - f_r, f_x + f_r, f_y + f_r),
            fill=(DEATH_OF_VINE[0], DEATH_OF_VINE[1], DEATH_OF_VINE[2], alpha),
        )
        # Cold spectral glow
        draw.ellipse(
            (f_x - f_r - 3, f_y - f_r - 3, f_x + f_r + 3, f_y + f_r + 3),
            fill=(DEATH_OF_VINE[0], DEATH_OF_VINE[1], DEATH_OF_VINE[2], alpha // 4),
        )


def _draw_figures(draw: ImageDraw) -> None:
    """Four small family figures walking under the wisteria arbor toward the light.

    Emi (teenage granddaughter) is slightly ahead, looking up at the white bloom.
    """
    ground_level = int(H * 0.70)
    # Family positions on the path, walking left to right toward the arbor
    figures = [
        # (x, height, color_shift, name_hint)
        (W // 2 - 220, ground_level, "Yuki",   (60, 55, 75)),   # grandmother
        (W // 2 - 100, ground_level, "Kenji",  (55, 60, 70)),   # father
        (W // 2 + 20,  ground_level, "Hanako", (65, 55, 72)),   # mother
        (W // 2 + 160, ground_level, "Emi",    (45, 50, 68)),   # daughter (ahead)
    ]

    for idx, (fx, fy, name, kimono_col) in enumerate(figures):
        fh = 48 + idx * 4  # slight perspective — closer figures taller
        fw = 18 + idx * 2
        dim_alpha = 180 - idx * 10

        # Kimono body (simplified silhouette triangle)
        draw.polygon(
            [
                (fx - fw // 2, fy),
                (fx + fw // 2, fy),
                (fx, fy - fh),
            ],
            fill=(*kimono_col, dim_alpha),
        )
        # Head
        head_r = max(4, fw // 3)
        draw.ellipse(
            (fx - head_r, fy - fh - head_r * 2,
             fx + head_r, fy - fh),
            fill=(*[min(255, c + 40) for c in kimono_col], dim_alpha),
        )

        if name == "Emi":
            # Emi is looking up at the white bloom — add a faint arm pointing up
            arm_end_x = fx + 14
            arm_end_y = fy - fh + 8
            draw.line(
                (fx + 4, fy - fh + 4, arm_end_x, arm_end_y),
                fill=(*[min(255, c + 30) for c in kimono_col], dim_alpha),
                width=2,
            )
            # Faint glow above her hand connecting to the white bloom
            glow_up = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            gd = ImageDraw.Draw(glow_up)
            gd.ellipse((arm_end_x - 15, arm_end_y - 40, arm_end_x + 15, arm_end_y - 10),
                        fill=(*DEATH_OF_VINE[:3], 18))
            glow_up = glow_up.filter(ImageFilter.GaussianBlur(10))


def _draw_petal_fall(draw: ImageDraw) -> None:
    """Scattered falling petals drifting down from the canopy."""
    for _ in range(60):
        px = rng.randint(50, W - 50)
        py = rng.randint(200, 1900)
        pr = rng.randint(2, 5)
        col = rng.choice(PROPHECY_COLORS)
        alpha = rng.randint(30, 90)
        draw.ellipse(
            (px - pr, py - pr, px + pr, py + pr),
            fill=(col[0], col[1], col[2], alpha),
        )
        # Slight stretch for falling petal effect
        draw.ellipse(
            (px - pr - 1, py - pr + 1, px + pr + 1, py + pr - 1),
            fill=(col[0], col[1], col[2], alpha // 2),
        )


def _draw_stone_lantern(draw: ImageDraw) -> Image.Image:
    """Japanese stone lantern (toro) on the left side, lit from within."""
    bx, by = 140, int(H * 0.64)

    # Base
    draw.rectangle((bx - 18, by - 5, bx + 18, by + 8), fill=(100, 96, 90, 220))
    # Post
    draw.rectangle((bx - 6, by - 55, bx + 6, by - 5), fill=(110, 105, 98, 220))
    # Fire box
    draw.rectangle((bx - 16, by - 80, bx + 16, by - 55), fill=(95, 90, 85, 220))
    # Fire box opening
    draw.rectangle((bx - 8, by - 74, bx + 8, by - 61), fill=(*LANTERN_WARM, 200))
    # Roof (curved top)
    draw.polygon([
        (bx - 24, by - 80),
        (bx + 24, by - 80),
        (bx + 20, by - 92),
        (bx - 20, by - 92),
    ], fill=(100, 95, 88, 220))
    # Finial
    draw.ellipse((bx - 4, by - 100, bx + 4, by - 92), fill=(90, 85, 78, 220))

    # Warm glow from lantern
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((bx - 80, by - 120, bx + 80, by - 20), fill=(*LANTERN_WARM, 14))
    glow = glow.filter(ImageFilter.GaussianBlur(18))
    return glow


def _draw_ambient_glows(draw: ImageDraw) -> None:
    """Atmospheric glows: moon glow, floral bioluminescence, and general mist."""
    glows = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glows)

    # Moon/light source in upper right
    gd.ellipse((1300, 40, 1500, 240), fill=(200, 190, 220, 20))
    gd.ellipse((1280, 20, 1520, 260), fill=(180, 170, 200, 10))

    # General atmospheric haze
    for _ in range(10):
        hx = rng.randint(0, W)
        hy = rng.randint(200, 1400)
        hr = rng.randint(100, 300)
        ha = rng.randint(4, 12)
        gd.ellipse((hx - hr, hy - hr, hx + hr, hy + hr),
                    fill=(140, 120, 180, ha))

    # Bioluminescent floral glow pockets under the arbor
    for _ in range(12):
        gx = rng.randint(200, 1400)
        gy = rng.randint(200, 600)
        gr = rng.randint(40, 100)
        col = rng.choice(PROPHECY_COLORS)
        gd.ellipse((gx - gr, gy - gr, gx + gr, gy + gr),
                    fill=(col[0], col[1], col[2], 8))

    # Death-of-vine cold glow (center-left, larger)
    gd.ellipse((400, 200, 700, 450), fill=(*DEATH_OF_VINE[:3], 10))

    glows = glows.filter(ImageFilter.GaussianBlur(30))
    return glows


def make_cover(mp: Path, op: Path) -> None:
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    # ── Base image ──
    img = Image.new("RGBA", (W, H), (*SKY_TOP, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Background ──
    _twilight_gradient(draw)

    # ── Ground and stone path ──
    _draw_ground_and_path(draw)

    # ── Stone lantern (left side, mid-ground) ──
    lantern_glow = _draw_stone_lantern(draw)

    # ── Wisteria arbor structure and foliage ──
    canopy_layer = _draw_wisteria_arbor(draw)

    # ── Hanging prophetic blooms ──
    # Draw on a separate layer so we can blur the glow
    bloom_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bloom_draw = ImageDraw.Draw(bloom_layer, "RGBA")
    _draw_hanging_blooms(bloom_draw)

    # ── Petal fall ──
    _draw_petal_fall(draw)

    # ── Family figures ──
    _draw_figures(draw)

    # ── Ambient atmospheric glows ──
    glows = _draw_ambient_glows(draw)
    img = Image.alpha_composite(img, glows)

    # ── Composite blooms and canopy ──
    img = Image.alpha_composite(img, canopy_layer)
    img = Image.alpha_composite(img, bloom_layer)

    # Soften the bloom layer glow
    bloom_glow = bloom_layer.filter(ImageFilter.GaussianBlur(20))
    img = Image.alpha_composite(img, bloom_glow)

    # Composite lantern glow
    img = Image.alpha_composite(img, lantern_glow)

    # ── Title panel ──
    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, title, author, model)
    img.convert("RGB").save(op, "PNG", optimize=True)
    print(f"Cover saved to {op}")


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
