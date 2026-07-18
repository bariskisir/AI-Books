#!/usr/bin/env python3
"""Cover: The Last Man Who Knew How to Dream — Weird Fiction/Metaphysical Horror: the last surviving dreamer in a sleepless surveillance state has nightmares that literally manifest into reality."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560
SEED = 709182345
rng = random.Random(SEED)

# ── Unique palette: clinical sterile world vs. nightmare manifest ────────────
# Sterile zone (bottom): cold clinic whites, pale blues, surgical greys
STERILE_WHITE = (210, 215, 225)
STERILE_BLUE = (160, 175, 195)
STERILE_GREY = (120, 130, 145)

# Nightmare zone (top): deep violets, toxic greens, bruise purples, rot oranges
NM_DEEP = (12, 4, 28)        # deepest nightmare void
NM_PURPLE = (65, 20, 70)     # bruise purple
NM_GREEN = (25, 55, 30)      # sickly dark green
NM_MAGENTA = (140, 25, 80)   # nightmare bloom
NM_ORANGE = (180, 60, 20)    # rot orange
NM_CYAN = (40, 180, 190)     # unnatural dream-cyan (manifestation glow)

# Surveillance-state accents
WAKE_AMBER = (240, 190, 50)  # searchlight / agency amber
WAKE_RED = (200, 25, 35)     # alarm red

# ── helpers ──────────────────────────────────────────────────────────────────

def _col_lerp(a: tuple[int, ...], b: tuple[int, ...], t: float) -> tuple[int, ...]:
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(len(a)))


def _noise(x: float, y: float, seed: int = 0) -> float:
    """Simple value noise for organic textures."""
    n = int(x * 73.7 + y * 137.9 + seed)
    n = (n << 13) ^ n
    return (1.0 - ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7FFFFFFF) / 1073741824.0) * 0.5 + 0.5


def make_cover(mp: Path, op: Path) -> None:
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (*STERILE_WHITE, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ═══════════════════════════════════════════════════════════════════════
    # 1. Vertical gradient: sterile white/grey bottom → nightmare top
    # ═══════════════════════════════════════════════════════════════════════
    DREAM_LINE = 1150   # y where nightmare starts bleeding through
    STERILE_BOT = 1765  # panel top

    for y in range(H):
        if y < 200:
            # Top: pure nightmare void
            t = y / 200
            col = _col_lerp(NM_DEEP, NM_PURPLE, t)
        elif y < DREAM_LINE:
            # Dream zone: turbulent nightmare colors
            t = (y - 200) / (DREAM_LINE - 200)
            n = _noise(t * 4.0, 0.5, 1234)
            base = _col_lerp(NM_PURPLE, NM_GREEN, t * 0.7 + n * 0.3)
            r = base[0] + int(30 * math.sin(t * 5.3 + n * 6.2))
            g = base[1] + int(20 * math.sin(t * 7.1 + n * 4.8))
            b = base[2] + int(40 * math.sin(t * 3.7 + n * 9.1))
            col = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
        elif y < STERILE_BOT:
            # Transition: nightmare bleeding into sterile world
            t = (y - DREAM_LINE) / (STERILE_BOT - DREAM_LINE)
            # Cracks of nightmare color piercing the sterile surface
            night_col = _col_lerp(NM_GREEN, STERILE_GREY, t * 0.8)
            day_col = _col_lerp(STERILE_GREY, STERILE_WHITE, t)
            mix = max(0, 1 - t * 1.8)
            col = tuple(int(day_col[i] * (1 - mix * 0.5) + night_col[i] * mix * 0.5) for i in range(3))
        else:
            # Bottom: sterile clinical white-grey
            t = (y - STERILE_BOT) / (H - STERILE_BOT)
            col = _col_lerp(STERILE_GREY, STERILE_BLUE, t)

        draw.line((0, y, W, y), fill=(*col, 255))

    # ═══════════════════════════════════════════════════════════════════════
    # 2. Sterile city skyline (soulless geometric blocks at the bottom)
    # ═══════════════════════════════════════════════════════════════════════
    SKYLINE_Y = 1550
    buildings: list[dict] = []
    bx = 0
    while bx < W:
        bw = rng.randint(35, 120)
        bh = rng.randint(80, 450)
        # Buildings get taller toward center
        center_factor = 1 - abs(bx + bw / 2 - W // 2) / (W // 2)
        bh = int(bh * (0.7 + 0.6 * center_factor))
        bcol = (rng.randint(100, 180), rng.randint(105, 185), rng.randint(120, 200))
        buildings.append({"x": bx, "w": bw, "h": bh, "col": bcol})
        bx += bw + rng.randint(2, 8)

    # Draw buildings (layer: back)
    for b in buildings:
        draw.rectangle(
            (b["x"], SKYLINE_Y - b["h"], b["x"] + b["w"], SKYLINE_Y),
            fill=(*b["col"], 220), outline=(80, 85, 100, 40),
        )
        # Sterile windows — harsh clinical light, no warmth
        for wy in range(SKYLINE_Y - b["h"] + 8, SKYLINE_Y - 8, rng.randint(22, 38)):
            for wx in range(b["x"] + 5, b["x"] + b["w"] - 5, rng.randint(18, 32)):
                if rng.random() < 0.6:
                    wbright = rng.randint(180, 255)
                    wcol = (wbright, wbright, min(255, wbright + 20))
                    draw.rectangle((wx, wy, wx + 5, wy + 5), fill=(*wcol, rng.randint(150, 220)))

    # ═══════════════════════════════════════════════════════════════════════
    # 3. Surveillance searchlights (The Wake agency)
    # ═══════════════════════════════════════════════════════════════════════
    searchlights = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(searchlights)
    for sl in range(6):
        sx = rng.randint(50, W - 50)
        sy = SKYLINE_Y
        angle = math.radians(rng.randint(-65, -25) if sl % 2 == 0 else rng.randint(-155, -115))
        length = rng.randint(600, 1000)
        ex = sx + math.cos(angle) * length
        ey = sy + math.sin(angle) * length
        # Amber searchlight beam — wide at base, narrow at tip
        beam_width_start = rng.randint(60, 120)
        beam_width_end = rng.randint(8, 20)
        steps = 40
        for si in range(steps):
            t = si / steps
            x1 = sx + math.cos(angle) * length * t - math.sin(angle) * (beam_width_start + (beam_width_end - beam_width_start) * t) / 2
            y1 = sy + math.sin(angle) * length * t + math.cos(angle) * (beam_width_start + (beam_width_end - beam_width_start) * t) / 2
            x2 = sx + math.cos(angle) * length * t + math.sin(angle) * (beam_width_start + (beam_width_end - beam_width_start) * t) / 2
            y2 = sy + math.sin(angle) * length * t - math.cos(angle) * (beam_width_start + (beam_width_end - beam_width_start) * t) / 2
            nx1 = sx + math.cos(angle) * length * (t + 1 / steps) - math.sin(angle) * (beam_width_start + (beam_width_end - beam_width_start) * (t + 1 / steps)) / 2
            ny1 = sy + math.sin(angle) * length * (t + 1 / steps) + math.cos(angle) * (beam_width_start + (beam_width_end - beam_width_start) * (t + 1 / steps)) / 2
            nx2 = sx + math.cos(angle) * length * (t + 1 / steps) + math.sin(angle) * (beam_width_start + (beam_width_end - beam_width_start) * (t + 1 / steps)) / 2
            ny2 = sy + math.sin(angle) * length * (t + 1 / steps) - math.cos(angle) * (beam_width_start + (beam_width_end - beam_width_start) * (t + 1 / steps)) / 2
            alpha = int(max(2, 25 * (1 - t) * (1 - t)))
            sd.polygon([(x1, y1), (x2, y2), (nx2, ny2), (nx1, ny1)], fill=(*WAKE_AMBER, alpha))
    searchlights = searchlights.filter(ImageFilter.GaussianBlur(6))
    img = Image.alpha_composite(img, searchlights)
    draw = ImageDraw.Draw(img, "RGBA")

    # Bright searchlight source points
    for sl in range(6):
        sx = rng.randint(50, W - 50)
        draw.ellipse((sx - 12, SKYLINE_Y - 6, sx + 12, SKYLINE_Y + 6), fill=(*WAKE_AMBER, 200))

    # ═══════════════════════════════════════════════════════════════════════
    # 4. The dreaming figure — Solomon Grey (central silhouette on rooftop)
    # ═══════════════════════════════════════════════════════════════════════
    FIGURE_X = W // 2
    FIGURE_Y = 1350  # standing on a rooftop

    # The figure (silhouette: head, torso, arms outstretched)
    # Head
    draw.ellipse((FIGURE_X - 28, FIGURE_Y - 120, FIGURE_X + 28, FIGURE_Y - 65), fill=(8, 4, 22, 230))
    # Body
    draw.polygon([
        (FIGURE_X - 20, FIGURE_Y - 65),
        (FIGURE_X + 20, FIGURE_Y - 65),
        (FIGURE_X + 25, FIGURE_Y),
        (FIGURE_X - 25, FIGURE_Y),
    ], fill=(8, 4, 22, 230))
    # Arms outstretched (cruciform, reaching upward)
    draw.line((FIGURE_X - 18, FIGURE_Y - 50, FIGURE_X - 170, FIGURE_Y - 130), fill=(8, 4, 22, 200), width=8)
    draw.line((FIGURE_X + 18, FIGURE_Y - 50, FIGURE_X + 170, FIGURE_Y - 130), fill=(8, 4, 22, 200), width=8)
    # Hands (open, fingers splayed)
    for arm_sign in [-1, 1]:
        hx = FIGURE_X + arm_sign * 170
        hy = FIGURE_Y - 130
        for fi in range(4):
            angle_f = math.radians(-30 + fi * 20 if arm_sign == -1 else 210 - fi * 20)
            draw.line(
                (hx, hy, hx + math.cos(angle_f) * 25, hy + math.sin(angle_f) * 15),
                fill=(8, 4, 22, 200), width=3,
            )

    # ═══════════════════════════════════════════════════════════════════════
    # 5. Dream-aura crackling from the figure's head (manifestation field)
    # ═══════════════════════════════════════════════════════════════════════
    aura = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ad = ImageDraw.Draw(aura)

    # Bright core around the head
    ad.ellipse(
        (FIGURE_X - 180, FIGURE_Y - 320, FIGURE_X + 180, FIGURE_Y - 20),
        fill=(*NM_CYAN, 25),
    )
    ad.ellipse(
        (FIGURE_X - 100, FIGURE_Y - 260, FIGURE_X + 100, FIGURE_Y - 60),
        fill=(*NM_CYAN, 40),
    )
    ad.ellipse(
        (FIGURE_X - 45, FIGURE_Y - 160, FIGURE_X + 45, FIGURE_Y - 75),
        fill=(200, 240, 255, 60),
    )

    # Lightning-like dream-energy tendrils radiating from the head
    for tendril in range(40):
        start_angle = rng.uniform(0, math.tau)
        length = rng.randint(60, 350)
        segments = rng.randint(4, 12)
        cx, cy = FIGURE_X + rng.randint(-30, 30), FIGURE_Y - 95
        points = [(cx, cy)]
        angle = start_angle
        for seg in range(segments):
            seg_len = length / segments * (0.6 + rng.random() * 0.8)
            angle += rng.uniform(-0.6, 0.6)
            nx = cx + math.cos(angle) * seg_len
            ny = cy + math.sin(angle) * seg_len * 0.7  # bias upward
            cx, cy = nx, ny
            points.append((cx, cy))

        alpha = rng.randint(60, 200)
        width = rng.randint(2, 5)
        col = rng.choice([
            (*NM_CYAN, alpha),
            (*NM_MAGENTA, alpha),
            (200, 255, 255, alpha),
            (*NM_ORANGE, alpha),
        ])
        for pi in range(len(points) - 1):
            ad.line((points[pi], points[pi + 1]), fill=col, width=width)

        # Small glow dot at the tip
        tip = points[-1]
        ad.ellipse(
            (tip[0] - 4, tip[1] - 4, tip[0] + 4, tip[1] + 4),
            fill=(255, 255, 255, min(255, alpha + 40)),
        )

    aura = aura.filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(img, aura)
    draw = ImageDraw.Draw(img, "RGBA")

    # ═══════════════════════════════════════════════════════════════════════
    # 6. Manifesting nightmares — organic horrors emerging from the dream field
    # ═══════════════════════════════════════════════════════════════════════
    nightmares = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(nightmares)

    # Twisted amalgamations — flesh, eyes, teeth, impossible geometry
    for _ in range(14):
        # Each nightmare clusters near a tendril endpoint
        nx = rng.randint(200, 1400)
        ny = rng.randint(80, 700)
        size = rng.randint(40, 130)

        # Base organic mass
        mass_col = rng.choice([
            (35, 8, 50),    # dark purple flesh
            (60, 15, 40),   # bruised magenta
            (25, 40, 25),   # sickly green
            (80, 30, 15),   # rust brown
        ])

        # Bulbous organic shape (multi-ellipse cluster)
        for _ in range(rng.randint(3, 7)):
            ox = nx + rng.randint(-size // 2, size // 2)
            oy = ny + rng.randint(-size // 2, size // 2)
            orad = rng.randint(size // 3, size // 2)
            nd.ellipse(
                (ox - orad, oy - orad, ox + orad, oy + orad),
                fill=(*mass_col, rng.randint(140, 200)),
            )

        # Eyes within the nightmare mass (watching)
        for _ in range(rng.randint(1, 4)):
            ex = nx + rng.randint(-size // 2, size // 2)
            ey = ny + rng.randint(-size // 2, size // 2)
            # Sclera (yellow-white)
            nd.ellipse((ex - 12, ey - 10, ex + 12, ey + 10), fill=(220, 200, 120, 200))
            # Iris (amber/red)
            nd.ellipse((ex - 6, ey - 6, ex + 6, ey + 6), fill=(*rng.choice([WAKE_AMBER, WAKE_RED, (180, 220, 100)]), 230))
            # Pupil (dilated — fear)
            nd.ellipse((ex - 3, ey - 3, ex + 3, ey + 3), fill=(5, 3, 8, 240))

        # Teeth / mandibles
        for _ in range(rng.randint(2, 5)):
            tx = nx + rng.randint(-size // 2, size // 2)
            ty = ny + rng.randint(-size // 2, size // 2)
            angle_t = rng.uniform(0, math.tau)
            tlen = rng.randint(15, 35)
            nd.line(
                (tx, ty, tx + math.cos(angle_t) * tlen, ty + math.sin(angle_t) * tlen),
                fill=(220, 210, 190, rng.randint(120, 180)), width=rng.randint(5, 9),
            )
            # Sharp tip
            nd.line(
                (tx + math.cos(angle_t) * tlen, ty + math.sin(angle_t) * tlen,
                 tx + math.cos(angle_t) * tlen + math.cos(angle_t + 0.3) * 5,
                 ty + math.sin(angle_t) * tlen + math.sin(angle_t + 0.3) * 5),
                fill=(240, 230, 210, rng.randint(100, 160)), width=3,
            )

    # Add a few larger, more defined nightmare forms
    # The Architect's influence: geometric impossibilities within the organic
    for _ in range(5):
        gx = rng.randint(150, 1450)
        gy = rng.randint(60, 500)
        gsize = rng.randint(60, 150)
        # Impossible staircase/spiral geometry
        for ring_i in range(8):
            ring_r = gsize * (1 - ring_i / 10)
            ring_alpha = max(5, 80 - ring_i * 8)
            ring_col = (100, 30, 80, ring_alpha) if rng.random() < 0.5 else (30, 80, 70, ring_alpha)
            nd.polygon(
                [(gx + math.cos(math.radians(a * 45 + ring_i * 13)) * ring_r,
                  gy + math.sin(math.radians(a * 45 + ring_i * 13)) * ring_r * 0.6)
                 for a in range(8)],
                fill=ring_col, outline=(*NM_CYAN, max(1, ring_alpha - 20)), width=1,
            )

    nightmares = nightmares.filter(ImageFilter.GaussianBlur(2))
    img = Image.alpha_composite(img, nightmares)
    draw = ImageDraw.Draw(img, "RGBA")

    # ═══════════════════════════════════════════════════════════════════════
    # 7. Reality cracks — tears where nightmare leaks into the sterile world
    # ═══════════════════════════════════════════════════════════════════════
    for _ in range(30):
        cx = rng.randint(100, 1500)
        cy = rng.randint(DREAM_LINE - 100, STERILE_BOT - 50)
        crack_len = rng.randint(20, 120)
        angle_c = rng.uniform(0, math.tau)
        # zigzag crack
        pts = [(cx, cy)]
        for seg in range(rng.randint(3, 6)):
            last = pts[-1]
            new_x = last[0] + math.cos(angle_c + rng.uniform(-0.8, 0.8)) * rng.randint(10, 30)
            new_y = last[1] + math.sin(angle_c + rng.uniform(-0.8, 0.8)) * rng.randint(10, 30)
            pts.append((new_x, new_y))

        # Glowing crack line
        for pi in range(len(pts) - 1):
            crack_alpha = rng.randint(60, 180)
            draw.line((pts[pi], pts[pi + 1]), fill=(*NM_CYAN, crack_alpha), width=rng.randint(2, 5))
            # Inner bright core
            draw.line((pts[pi], pts[pi + 1]), fill=(200, 255, 255, min(200, crack_alpha + 40)), width=1)

        # Small particle spray from crack
        for _ in range(rng.randint(3, 8)):
            px = pts[-1][0] + rng.randint(-15, 15)
            py = pts[-1][1] + rng.randint(-15, 15)
            pr = rng.randint(1, 4)
            draw.ellipse((px - pr, py - pr, px + pr, py + pr), fill=(*NM_CYAN, rng.randint(80, 180)))

    # ═══════════════════════════════════════════════════════════════════════
    # 8. Surveillance eye motifs — the Wake watches from above
    # ═══════════════════════════════════════════════════════════════════════
    # Drone-like eyes scattered in the upper nightmare zone
    for _ in range(8):
        dx = rng.randint(100, 1500)
        dy = rng.randint(50, 400)
        dr = rng.randint(8, 18)
        # Mechanical iris ring
        draw.ellipse((dx - dr, dy - dr, dx + dr, dy + dr), outline=(*WAKE_AMBER, rng.randint(60, 130)), width=2)
        draw.ellipse((dx - dr - 3, dy - dr - 3, dx + dr + 3, dy + dr + 3), outline=(*WAKE_AMBER, rng.randint(20, 50)), width=1)
        # Amber iris
        draw.ellipse((dx - dr // 2, dy - dr // 2, dx + dr // 2, dy + dr // 2), fill=(*WAKE_AMBER, rng.randint(100, 180)))
        # Black pupil
        draw.ellipse((dx - 2, dy - 2, dx + 2, dy + 2), fill=(5, 3, 8, 220))
        # Glint
        draw.ellipse((dx - 1, dy - dr // 2 + 2, dx + 1, dy - dr // 2 + 5), fill=(255, 255, 250, rng.randint(100, 180)))

    # ═══════════════════════════════════════════════════════════════════════
    # 9. Floating dream particles — scattered throughout
    # ═══════════════════════════════════════════════════════════════════════
    for _ in range(200):
        px = rng.randint(0, W)
        py = rng.randint(20, 1500)
        pr = rng.randint(1, 4)
        pcol = rng.choice([
            (*NM_CYAN, rng.randint(30, 120)),
            (*NM_MAGENTA, rng.randint(20, 80)),
            (200, 220, 255, rng.randint(20, 90)),
            (*NM_ORANGE, rng.randint(15, 60)),
        ])
        draw.ellipse((px - pr, py - pr, px + pr, py + pr), fill=pcol)

    # ═══════════════════════════════════════════════════════════════════════
    # 10. Vignette — darkens edges
    # ═══════════════════════════════════════════════════════════════════════
    vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette)
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(60 * max(0, 1 - vt))
        if vv > 0:
            vd.line((0, vy, vv, vy), fill=(0, 0, 0, 80))
            vd.line((W - vv, vy, W, vy), fill=(0, 0, 0, 80))
    for vx in range(W):
        vt = 1 - abs(vx - W // 2) / (W // 2)
        vv_top = int(100 * max(0, 1 - vt))
        if vv_top > 0:
            vd.line((vx, 0, vx, vv_top), fill=(0, 0, 0, min(200, vv_top * 2)))
    img = Image.alpha_composite(img, vignette)
    draw = ImageDraw.Draw(img, "RGBA")

    # ═══════════════════════════════════════════════════════════════════════
    # 11. Title/author panel (via shared utility, at the bottom)
    # ═══════════════════════════════════════════════════════════════════════
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
