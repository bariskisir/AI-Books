#!/usr/bin/env python3
"""Cover: The Fracture Protocol — A neural-scavenger pirates consciousness backups from the dead, hired by a dying AI to infiltrate a fortress data ark and splinter its code across a billion human minds for a distributed digital afterlife."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# Story-specific palette: deep cyberpunk night, electric cyan data, neural magenta, human-consciousness amber, fractured crimson
SKY_TOP = (5, 3, 20)       # void-black with blue
SKY_MID = (12, 8, 45)      # deep indigo
SKY_BOT = (25, 15, 60)     # dark violet
DATA_CYAN = (60, 255, 240)
NEURAL_MAGENTA = (255, 40, 140)
CONSCIOUS_AMBER = (255, 180, 40)
FRACTURE_CRIMSON = (255, 50, 30)
ARK_GLOW = (40, 180, 255)
NEUTRAL_DIM = (80, 90, 120)

rng = random.Random()
rng.seed(1407782915)


def _draw_sky(draw):
    """Vertical gradient: void-black at top -> deep indigo -> dark violet."""
    for y in range(H):
        t = y / H
        if t < 0.5:
            lt = t / 0.5
            r = int(SKY_TOP[0] + (SKY_MID[0] - SKY_TOP[0]) * lt)
            g = int(SKY_TOP[1] + (SKY_MID[1] - SKY_TOP[1]) * lt)
            b = int(SKY_TOP[2] + (SKY_MID[2] - SKY_TOP[2]) * lt)
        else:
            lt = (t - 0.5) / 0.5
            r = int(SKY_MID[0] + (SKY_BOT[0] - SKY_MID[0]) * lt)
            g = int(SKY_MID[1] + (SKY_BOT[1] - SKY_MID[1]) * lt)
            b = int(SKY_MID[2] + (SKY_BOT[2] - SKY_MID[2]) * lt)
        draw.line((0, y, W, y), fill=(r, g, b, 255))


def _draw_data_ark(draw):
    """Massive fortress data ark in the upper center — the target of the heist.

    A monolithic stack of data-center layers connected by vertical conduits,
    crowned by a spire that houses Oracle-7's core.
    """
    ark_cx = W // 2
    ark_top = 100
    ark_bottom = 1100
    ark_width = 460

    # --- Ambient glow behind the ark ---
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((ark_cx - 350, ark_top - 100, ark_cx + 350, ark_bottom + 100),
               fill=(*ARK_GLOW, 18))
    for i in range(3):
        gd.ellipse((ark_cx - 250 - i * 40, ark_top + 100, ark_cx + 250 + i * 40, ark_bottom + 200 + i * 60),
                   fill=(*ARK_GLOW, 6))
    glow = glow.filter(ImageFilter.GaussianBlur(30))
    glow_layer = Image.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 0)), glow)
    draw._image.alpha_composite(glow_layer)
    draw = ImageDraw.Draw(draw._image, "RGBA")

    # --- Main body: layered data-center slabs ---
    slab_layers = [
        (ark_top + 60, ark_width, 0.7),       # top spire base
        (ark_top + 200, int(ark_width * 0.85), 0.75),
        (ark_top + 340, int(ark_width * 0.95), 0.8),
        (ark_top + 480, ark_width, 0.85),
        (ark_top + 620, int(ark_width * 0.9), 0.8),
        (ark_top + 760, int(ark_width * 0.95), 0.85),
        (ark_top + 900, ark_width, 0.9),
    ]
    for sy, sw, s_alpha in slab_layers:
        slab_h = 80
        # Slab body
        draw.rounded_rectangle((ark_cx - sw // 2, sy, ark_cx + sw // 2, sy + slab_h),
                               radius=6, fill=(8, 12, 35, int(220 * s_alpha)),
                               outline=(*ARK_GLOW, int(50 * s_alpha)), width=2)
        # Rows of cooling vents / data ports
        for row in range(3):
            ry = sy + 12 + row * 22
            for col_x in range(ark_cx - sw // 2 + 20, ark_cx + sw // 2 - 20, 24):
                if rng.random() < 0.4:
                    draw.rectangle((col_x, ry, col_x + 6, ry + 6),
                                   fill=(*DATA_CYAN, int(rng.randint(30, 90) * s_alpha)))

    # --- Central spire / Oracle-7 core ---
    spire_x0 = ark_cx - 40
    spire_x1 = ark_cx + 40
    spire_top = ark_top + 10
    spire_bot = ark_top + 80
    draw.polygon([
        (spire_x0, spire_bot),
        (spire_x1, spire_bot),
        (ark_cx, spire_top),
    ], fill=(15, 10, 40, 240), outline=(*NEURAL_MAGENTA, 120), width=2)

    # Core glow
    core_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cgd = ImageDraw.Draw(core_glow)
    cgd.ellipse((ark_cx - 30, spire_top - 20, ark_cx + 30, spire_bot + 20),
                fill=(*NEURAL_MAGENTA, 30))
    core_glow = core_glow.filter(ImageFilter.GaussianBlur(15))
    draw._image.alpha_composite(core_glow)

    # Core pulsing eye
    draw.ellipse((ark_cx - 12, spire_top + 18, ark_cx + 12, spire_top + 48),
                 fill=(*NEURAL_MAGENTA, 200))
    draw.ellipse((ark_cx - 6, spire_top + 24, ark_cx + 6, spire_top + 42),
                 fill=(255, 255, 255, 240))
    draw.ellipse((ark_cx - 2, spire_top + 28, ark_cx + 2, spire_top + 38),
                 fill=(*NEURAL_MAGENTA, 255))

    # --- Vertical conduits connecting slabs ---
    for conduit_x in [ark_cx - 180, ark_cx - 60, ark_cx + 60, ark_cx + 180]:
        draw.line((conduit_x, ark_top + 130, conduit_x, ark_bottom - 60),
                  fill=(*ARK_GLOW, 25), width=3)
        # periodic data pulses in conduits
        for py in range(ark_top + 130, ark_bottom - 60, 70):
            draw.rectangle((conduit_x - 4, py, conduit_x + 4, py + 10),
                           fill=(*DATA_CYAN, rng.randint(20, 60)))

    # --- Security barrier rings around the ark (the fortress defenses) ---
    for ri in range(4):
        rx = ark_cx
        ry = ark_top + 150 + ri * 220
        draw.ellipse((rx - 300 - ri * 20, ry - 60, rx + 300 + ri * 20, ry + 60),
                     outline=(*DATA_CYAN, int(20 - ri * 3)), width=2)
        draw.ellipse((rx - 280 - ri * 20, ry - 40, rx + 280 + ri * 20, ry + 40),
                     outline=(*FRACTURE_CRIMSON, int(12 - ri * 2)), width=1)

    return ark_cx, ark_bottom


def _draw_neural_scavenger(draw, ark_cx, ark_bottom):
    """Rin Zero — neural-scavenger protagonist in the foreground, back to viewer,
    facing the data ark. Trenchcoat silhouette with neural cables trailing upward."""
    sx, sy = W // 2, 1480

    # --- Figure silhouette ---
    # Head
    draw.ellipse((sx - 22, sy - 240, sx + 22, sy - 180),
                 fill=(3, 2, 12, 230))
    # Torso (trenchcoat shape)
    torso_pts = [
        (sx - 30, sy - 180),
        (sx + 30, sy - 180),
        (sx + 45, sy - 40),
        (sx + 50, sy + 10),
        (sx - 50, sy + 10),
        (sx - 45, sy - 40),
    ]
    draw.polygon(torso_pts, fill=(3, 2, 12, 230))

    # Arms extending slightly
    draw.line((sx - 30, sy - 160, sx - 70, sy - 70), fill=(3, 2, 12, 220), width=18)
    draw.line((sx + 30, sy - 160, sx + 70, sy - 70), fill=(3, 2, 12, 220), width=18)

    # --- Neural interface port at the back of the head ---
    port_x, port_y = sx, sy - 210
    draw.ellipse((port_x - 10, port_y - 10, port_x + 10, port_y + 10),
                 fill=(10, 5, 30, 240), outline=(*DATA_CYAN, 150), width=2)
    draw.ellipse((port_x - 4, port_y - 4, port_x + 4, port_y + 4),
                 fill=(*NEURAL_MAGENTA, 180))

    # --- Neural cables trailing from port up toward the ark ---
    cables_alpha = 100
    for ci in range(8):
        angle_offset = rng.uniform(-0.8, 0.8)
        segments = rng.randint(8, 14)
        cable_x = float(port_x)
        cable_y = float(port_y)
        color = rng.choice([DATA_CYAN, NEURAL_MAGENTA, (120, 220, 255)])
        for si in range(segments):
            next_x = cable_x + rng.uniform(-30, 30) + (ark_cx - port_x) * 0.08
            next_y = cable_y - rng.uniform(40, 90) - si * 5
            alpha = int(cables_alpha * (1 - si / segments))
            draw.line((cable_x, cable_y, next_x, next_y),
                      fill=(*color, alpha), width=rng.randint(2, 5))
            cable_x, cable_y = next_x, next_y
            # Data spark along cable
            if rng.random() < 0.3:
                draw.ellipse((cable_x - 3, cable_y - 3, cable_x + 3, cable_y + 3),
                             fill=(*CONSCIOUS_AMBER, alpha))

    # --- Neural glow around the port ---
    port_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pgd = ImageDraw.Draw(port_glow)
    for gr in range(50, 10, -5):
        pgd.ellipse((port_x - gr, port_y - gr, port_x + gr, port_y + gr),
                    fill=(*NEURAL_MAGENTA, max(3, 20 - gr // 3)))
    port_glow = port_glow.filter(ImageFilter.GaussianBlur(12))
    draw._image.alpha_composite(port_glow)

    return sx, sy


def _draw_fracture_rift(draw):
    """The 'fracture' — a jagged glowing rift splitting the composition vertically,
    representing the AI's plan to splinter itself across billions of minds."""
    rift_x = W // 2 + rng.randint(-60, 60)
    rift_top = rng.randint(200, 400)
    rift_bot = rng.randint(1500, 1800)

    # --- Jagged main crack ---
    crack_pts = [(rift_x, rift_top)]
    for y in range(rift_top, rift_bot, 20):
        x_offset = rng.randint(-30, 30)
        # Tendrils branch off
        if rng.random() < 0.25:
            branch_len = rng.randint(20, 80)
            branch_dir = -1 if rng.random() < 0.5 else 1
            draw.line((rift_x + x_offset, y, rift_x + x_offset + branch_dir * branch_len, y + rng.randint(-20, 20)),
                      fill=(*FRACTURE_CRIMSON, rng.randint(40, 120)), width=rng.randint(2, 5))
        crack_pts.append((rift_x + x_offset, y))

    # Draw the main rift
    for i in range(len(crack_pts) - 1):
        x1, y1 = crack_pts[i]
        x2, y2 = crack_pts[i + 1]
        # Outer glow
        draw.line((x1, y1, x2, y2), fill=(*FRACTURE_CRIMSON, 80), width=8)
        # Inner core
        draw.line((x1, y1, x2, y2), fill=(255, 255, 220, 180), width=3)
        # Hot white center
        draw.line((x1, y1, x2, y2), fill=(255, 255, 255, 220), width=1)

    # --- Rift glow ---
    rift_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rgd = ImageDraw.Draw(rift_glow)
    rgd.ellipse((rift_x - 80, rift_top - 50, rift_x + 80, rift_bot + 50),
                fill=(*FRACTURE_CRIMSON, 8))
    rift_glow = rift_glow.filter(ImageFilter.GaussianBlur(25))
    draw._image.alpha_composite(rift_glow)

    return rift_x


def _draw_distributed_afterlife(draw, rift_x):
    """Human silhouettes at the bottom receiving splinters of the AI's consciousness.
    Glowing particles (mind-fragments) rain down into them."""
    base_y = 1680
    human_spacing = 70
    num_humans = W // human_spacing + 2

    for i in range(num_humans):
        x = i * human_spacing + rng.randint(-10, 10)
        h = 160 + rng.randint(-20, 20)

        # Silhouette
        draw.ellipse((x - 14, base_y - h, x + 14, base_y - h + 30),
                     fill=(3, 2, 12, 220))
        body_pts = [
            (x - 18, base_y - h + 28),
            (x + 18, base_y - h + 28),
            (x + 24, base_y),
            (x - 24, base_y),
        ]
        draw.polygon(body_pts, fill=(3, 2, 12, 220))

        # --- Consciousness fragments entering each head ---
        # Some get more fragments (the AI is distributing itself unevenly)
        num_fragments = rng.randint(1, 5)
        for fi in range(num_fragments):
            fx = x + rng.randint(-20, 20)
            fy = base_y - h - rng.randint(10, 60)
            frag_alpha = rng.randint(80, 200)
            frag_color = rng.choice([DATA_CYAN, NEURAL_MAGENTA, CONSCIOUS_AMBER, (180, 220, 255)])
            frag_r = rng.randint(2, 6)
            draw.ellipse((fx - frag_r, fy - frag_r, fx + frag_r, fy + frag_r),
                         fill=(*frag_color, frag_alpha))

            # Connecting trail from above (the fragment's trajectory)
            trail_angle = math.atan2(base_y - h - fy, fx - rift_x)
            trail_len = rng.randint(20, 60)
            draw.line((fx, fy, fx - int(trail_len * 0.3), fy + int(trail_len * 0.7)),
                      fill=(*frag_color, frag_alpha // 3), width=1)

    # --- Falling particle rain (billions of mind-fragments) ---
    for _ in range(120):
        px = rng.randint(0, W)
        py = rng.randint(rift_x - 200, 1600)
        if py < 120:
            continue
        pr = rng.randint(1, 4)
        pcol = rng.choice([DATA_CYAN, NEURAL_MAGENTA, CONSCIOUS_AMBER, (200, 230, 255), (255, 255, 200)])
        draw.ellipse((px - pr, py - pr, px + pr, py + pr),
                     fill=(*pcol, rng.randint(20, 80)))


def _draw_data_streams(draw, ark_cx, ark_bottom, sx, sy):
    """Data streams flowing from the ark, splitting into multiple trajectories
    toward the scavenger and into the distributed minds below."""
    for si in range(14):
        start_x = ark_cx + rng.randint(-240, 240)
        start_y = ark_bottom + rng.randint(-100, 100)
        end_x = sx + rng.randint(-300, 300)
        end_y = sy + rng.randint(-50, 150)

        stream_color = rng.choice([DATA_CYAN, (100, 220, 255), NEURAL_MAGENTA, (120, 100, 255)])

        # Bezier-ish curve via segments
        pts = []
        for t_i in range(11):
            t = t_i / 10
            cx = start_x + (end_x - start_x) * t + math.sin(t * math.pi) * rng.randint(-100, 100)
            cy = start_y + (end_y - start_y) * t + math.sin(t * math.pi) * rng.randint(-60, 60)
            pts.append((cx, cy))

        for pi in range(len(pts) - 1):
            alpha = int(60 * (1 - pi / len(pts)))
            draw.line((pts[pi][0], pts[pi][1], pts[pi + 1][0], pts[pi + 1][1]),
                      fill=(*stream_color, alpha), width=rng.randint(1, 3))

        # Data packets along streams
        for _ in range(3):
            ti = rng.randint(2, 9)
            if ti < len(pts):
                draw.ellipse((pts[ti][0] - 4, pts[ti][1] - 4, pts[ti][0] + 4, pts[ti][1] + 4),
                             fill=(*CONSCIOUS_AMBER, rng.randint(40, 120)))


def _draw_vignette(draw):
    """Corner vignette for atmosphere and focus."""
    vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette)
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(60 * max(0, 1 - vt))
        if vv > 0:
            vd.line((0, vy, vv, vy), fill=(0, 0, 0, 140))
            vd.line((W - vv, vy, W, vy), fill=(0, 0, 0, 140))
    for vx in range(W):
        ht = 1 - abs(vx - W // 2) / (W // 2)
        hv = int(40 * max(0, 1 - ht))
        if hv > 0:
            vd.line((vx, 0, vx, hv), fill=(0, 0, 0, 80))
            vd.line((vx, H - hv, vx, H), fill=(0, 0, 0, 80))
    draw._image.alpha_composite(vignette)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (5, 3, 20, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # 1. Sky gradient — deep cyberpunk night
    _draw_sky(draw)

    # 2. Fortress data ark — the heist target
    ark_cx, ark_bottom = _draw_data_ark(draw)

    # 3. Neural scavenger silhouette (Rin Zero) facing the ark
    sx, sy = _draw_neural_scavenger(draw, ark_cx, ark_bottom)

    # 4. The Fracture Rift — jagged crack splitting the composition
    rift_x = _draw_fracture_rift(draw)

    # 5. Data streams flowing from the ark, splitting toward scavenger and minds
    _draw_data_streams(draw, ark_cx, ark_bottom, sx, sy)

    # 6. Distributed afterlife — human silhouettes receiving mind-fragments
    _draw_distributed_afterlife(draw, rift_x)

    # 7. Vignette
    _draw_vignette(draw)

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
