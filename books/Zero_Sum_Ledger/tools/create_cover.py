#!/usr/bin/env python3
"""Cover: Zero Sum Ledger — A forensic accountant tracking a trillion-dollar conspiracy realizes the numbers only add up if one of her murdered colleagues is still logging into the system every Tuesday at 3 AM."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# ── Palette: deep financial greens, corporate blacks, blood-red audit flags ──
# Inspired by ledgers, balance sheets, forensic accounting — the colour of money and corruption.
BG_TOP = (8, 12, 8)        # deep fiscal green-black
BG_BOT = (22, 32, 22)       # dark money-green
LEDGER_GREEN = (80, 130, 80)   # classic ledger color
INK_BLACK = (25, 30, 25)
RED_INK = (200, 45, 45)        # flagged transactions
AMBER_AUDIT = (210, 180, 60)   # warning highlights
GHOST_TEAL = (100, 200, 190)   # dead man's data signature
CORP_GRAY = (140, 145, 140)    # shell-company neutral
PAPER = (195, 190, 175)        # aged document


def _gradient(draw):
    """Deep fiscal green gradient — from ledger-black at top to muted money-green at bottom."""
    for y in range(H):
        t = y / H
        r = int(BG_TOP[0] + (BG_BOT[0] - BG_TOP[0]) * t)
        g = int(BG_TOP[1] + (BG_BOT[1] - BG_TOP[1]) * t)
        b = int(BG_TOP[2] + (BG_BOT[2] - BG_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))


def _ledger_sheet(draw, rng):
    """Overlay a translucent ledger-page texture with ruled lines and faint column borders."""
    # Ruled horizontal lines — like a financial ledger
    for y in range(100, 1765, 18):
        a = 18 - 10 * abs(y - 900) / 900
        draw.line((80, y, W - 80, y), fill=(*LEDGER_GREEN, max(6, int(a))), width=1)

    # Column dividers — the anatomy of a financial statement
    for col_x in [280, 480, 680, 880, 1080, 1280]:
        a = rng.randint(15, 30)
        draw.line((col_x, 80, col_x, 1740), fill=(*CORP_GRAY, a), width=1)

    # Faint header row — like "ASSETS / LIABILITIES / EQUITY"
    draw.line((70, 118, W - 70, 118), fill=(*LEDGER_GREEN, 25), width=2)
    draw.line((70, 136, W - 70, 136), fill=(*LEDGER_GREEN, 18), width=1)

    # Aged paper stain — subtle discolouration patches
    stain = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stain)
    for _ in range(6):
        sx = rng.randint(100, 1500)
        sy = rng.randint(200, 1600)
        sr = rng.randint(80, 250)
        sd.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=(*PAPER, rng.randint(4, 10)))
    stain = stain.filter(ImageFilter.GaussianBlur(30))
    draw._image.paste(stain, (0, 0), stain)


def _cascading_numbers(draw, rng):
    """Columns of faint numerical digits cascading down the ledger — the trillion-dollar trail.

    Each column is a stream of digits representing shell-company transactions.
    Some rows are "flagged" in red — anomalies Zara has identified.
    """
    for col in range(40):
        col_x = 100 + col * 36
        num_len = rng.randint(8, 18)
        y_start = 160 + rng.randint(0, 40) * 18
        for row in range(num_len):
            y = y_start + row * 18
            if y > 1720:
                break
            # Generate a short number fragment
            digits = "".join(str(rng.randint(0, 9)) for _ in range(rng.randint(4, 10)))
            # Most numbers are faint ledger ink
            a = rng.randint(14, 35)
            col = (55 + rng.randint(0, 20), 90 + rng.randint(0, 30), 55 + rng.randint(0, 20))
            draw.text((col_x, y), digits, fill=(*col, a))
            # Occasionally a red-flagged number — audit finding
            if rng.random() < 0.04:
                flag_x = col_x - 8
                draw.rectangle((flag_x, y - 1, flag_x + 5, y + 10), fill=(*RED_INK, 120))
                # Red underline
                draw.line((col_x, y + 11, col_x + 70, y + 11), fill=(*RED_INK, 100), width=1)


def _shell_company_web(draw, rng):
    """Interconnected node diagram of shell corporations — the hidden ownership structure.

    Each node is a numbered entity (offshore corp). Lines show opaque ownership
    chains. Some nodes glow ghostly teal — the dead man's shell companies.
    """
    nodes = []
    # Generate 25 shell-company nodes scattered across the upper-mid area
    for _ in range(25):
        nx = rng.randint(100, 1500)
        ny = rng.randint(150, 1200)
        radius = rng.randint(16, 35)
        # Is this node part of the dead man's network?
        is_ghost = rng.random() < 0.25
        nodes.append((nx, ny, radius, is_ghost))

    # Draw connections between related shell companies
    # Dense connections form a web of ownership
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            dx = nodes[i][0] - nodes[j][0]
            dy = nodes[i][1] - nodes[j][1]
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 300 and rng.random() < 0.35:
                a = int(30 * (1 - dist / 300))
                # Ghost connections — links involving the dead man's shell companies
                if nodes[i][3] or nodes[j][3]:
                    col = (*GHOST_TEAL, a)
                else:
                    col = (*CORP_GRAY, a)
                draw.line((nodes[i][0], nodes[i][1], nodes[j][0], nodes[j][1]), fill=col, width=rng.randint(1, 2))

    # Draw the nodes themselves
    for nx, ny, radius, is_ghost in nodes:
        if is_ghost:
            # Ghostly teal node — the dead man's company
            draw.ellipse((nx - radius, ny - radius, nx + radius, ny + radius),
                         fill=(*GHOST_TEAL, 50), outline=(*GHOST_TEAL, 120), width=2)
            # Inner glow
            draw.ellipse((nx - radius // 2, ny - radius // 2, nx + radius // 2, ny + radius // 2),
                         fill=(*GHOST_TEAL, 80))
        else:
            # Normal shell company — dark grey
            draw.ellipse((nx - radius, ny - radius, nx + radius, ny + radius),
                         fill=(*INK_BLACK, 150), outline=(*CORP_GRAY, 80), width=1)

        # Label each node with a shell-company number
        label = f"#{rng.randint(1000, 9999)}"
        draw.text((nx - 10, ny - 4), label, fill=(*CORP_GRAY, 100))


def _dead_man_logging(draw, rng):
    """Ghostly translucent figure of 'The Ledgerkeeper' — the murdered colleague who still logs in.

    A spectral human silhouette emerges from the numbers, partially formed from
    cascading digits and data streams. The figure is rendered as a translucent
    overlay with teal-green data trails flowing through it.
    """
    figure = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(figure)

    # Spectral figure — seated at a desk / terminal posture
    cx, cy = W // 2 + 80, 850

    # Head
    fd.ellipse((cx - 55, cy - 100, cx + 55, cy + 10), fill=(*GHOST_TEAL, 25))
    fd.ellipse((cx - 45, cy - 90, cx + 45, cy + 2), fill=(*GHOST_TEAL, 30))

    # Torso — leaning forward at a desk
    torso_pts = [
        (cx - 70, cy + 10),   # left shoulder
        (cx - 40, cy + 320),  # left hip
        (cx + 40, cy + 320),  # right hip
        (cx + 70, cy + 10),   # right shoulder
    ]
    fd.polygon(torso_pts, fill=(*GHOST_TEAL, 20))

    # Arms reaching toward a keyboard
    # Left arm
    fd.line((cx - 65, cy + 40, cx - 120, cy + 200, cx - 100, cy + 260),
            fill=(*GHOST_TEAL, 30), width=8)
    # Right arm
    fd.line((cx + 65, cy + 40, cx + 110, cy + 180, cx + 90, cy + 250),
            fill=(*GHOST_TEAL, 30), width=8)

    # Data-stream tendrils flowing FROM the figure into the ledger below
    for _ in range(20):
        sx = cx + rng.randint(-40, 40)
        sy = cy + rng.randint(80, 200)
        pts = []
        for step in range(30):
            t = step / 30
            ex = sx + t * rng.randint(-200, 200)
            ey = sy + t * (rng.randint(300, 700))
            ex += math.sin(t * 8 + rng.random() * 5) * 20
            pts.append((int(ex), int(ey)))
        a = rng.randint(8, 20)
        draw.line(pts, fill=(*GHOST_TEAL, a), width=rng.randint(1, 2))

    # The figure's face — faint hollow eyes and mouth
    fd.ellipse((cx - 18, cy - 65, cx - 5, cy - 50), fill=(*GHOST_TEAL, 45))
    fd.ellipse((cx + 5, cy - 65, cx + 18, cy - 50), fill=(*GHOST_TEAL, 45))
    fd.arc((cx - 15, cy - 30, cx + 15, cy + 2), 0, 180, fill=(*GHOST_TEAL, 35), width=2)

    # Blur the entire figure for a ghostly, out-of-phase appearance
    figure = figure.filter(ImageFilter.GaussianBlur(8))
    draw._image.paste(figure, (0, 0), figure)


def _tuesday_3am_clock(draw):
    """A clock face frozen at 3 AM — the weekly login time of the dead man.

    Integrated into the ledger as a forensic finding — embedded in the data.
    """
    cx, cy = 260, 420
    r = 85

    # Clock face — like a watermark on the ledger
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(*GHOST_TEAL, 40), width=2)
    draw.ellipse((cx - r + 8, cy - r + 8, cx + r - 8, cy + r - 8), outline=(*GHOST_TEAL, 20), width=1)

    # Hour markers (12 positions)
    for i in range(12):
        ang = math.radians(i * 30 - 90)
        inner = r - 10
        outer = r - 3
        x1 = cx + math.cos(ang) * inner
        y1 = cy + math.sin(ang) * inner
        x2 = cx + math.cos(ang) * outer
        y2 = cy + math.sin(ang) * outer
        draw.line((x1, y1, x2, y2), fill=(*GHOST_TEAL, 60), width=2)

    # Hour hand pointing at 3 (90 degrees)
    hour_angle = math.radians(90 - 90)  # 3 AM = 90 degrees from 12
    he_x = cx + math.cos(hour_angle) * (r - 35)
    he_y = cy + math.sin(hour_angle) * (r - 35)
    draw.line((cx, cy, he_x, he_y), fill=(*GHOST_TEAL, 90), width=4)

    # Minute hand at 12 (pointing up, straight)
    draw.line((cx, cy, cx, cy - r + 20), fill=(*GHOST_TEAL, 60), width=2)

    # Center dot
    draw.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=(*GHOST_TEAL, 100))

    # Label: "03:00 TUE" below clock
    draw.text((cx - 32, cy + r + 8), "03:00 TUE", fill=(*GHOST_TEAL, 60))


def _audit_trail_highlights(draw, rng):
    """Red-flagged audit findings scattered through the ledger — evidence markers.

    Each is a red bracket or circle around a suspicious transaction,
    with a small marker number. Zara's forensic annotations.
    """
    for _ in range(12):
        x = rng.randint(100, 1500)
        y = rng.randint(180, 1650)
        w = rng.randint(40, 120)
        h = rng.randint(14, 22)

        # Red bracket around suspicious entry
        a = rng.randint(80, 150)
        # Left bracket
        draw.line((x, y, x, y + h), fill=(*RED_INK, a), width=2)
        draw.line((x, y, x + 4, y), fill=(*RED_INK, a), width=1)
        draw.line((x, y + h, x + 4, y + h), fill=(*RED_INK, a), width=1)
        # Right bracket
        draw.line((x + w, y, x + w, y + h), fill=(*RED_INK, a), width=2)
        draw.line((x + w, y, x + w - 4, y), fill=(*RED_INK, a), width=1)
        draw.line((x + w, y + h, x + w - 4, y + h), fill=(*RED_INK, a), width=1)

        # Marker number
        marker = f"[{rng.randint(1, 99)}]"
        draw.text((x + w + 6, y - 1), marker, fill=(*RED_INK, a))

        # Connect some flags with dotted lines — showing the money trail
        if rng.random() < 0.3 and _ > 0:
            # Draw a dotted line to another flagged entry
            prev_x = max(100, x - rng.randint(150, 400))
            prev_y = y + rng.randint(-60, 60)
            for step in range(0, x - prev_x, 6):
                if step % 12 == 0:
                    px = prev_x + step
                    draw.line((px, prev_y, px + 3, prev_y), fill=(*RED_INK, 40), width=1)


def _money_trail_glow(draw, rng):
    """Subtle amber-glowing pathways — the trillion-dollar money trail winding through the data.

    Glowing sine-wave paths that snake through the shell-company web and ledger numbers,
    representing the hidden flow of illicit funds.
    """
    trails = [
        (100, 600, 1500, 1100, 0.015, 40),
        (200, 900, 1400, 500, 0.02, 30),
        (300, 300, 1300, 1400, 0.012, 35),
    ]

    for x1, y1, x2, y2, freq, amp in trails:
        pts = []
        steps = 120
        for i in range(steps + 1):
            t = i / steps
            x = x1 + (x2 - x1) * t
            y = y1 + (y2 - y1) * t + math.sin(t * math.tau * 3) * amp * 0.5 + math.sin(t * math.tau * 7) * amp * 0.25
            pts.append((int(x), int(y)))

        # Glowing amber trail
        for i in range(len(pts) - 1):
            a = int(50 * (1 - i / len(pts)))
            draw.line((pts[i], pts[i + 1]), fill=(*AMBER_AUDIT, max(5, a)), width=rng.randint(1, 3))


def _data_motes(draw, rng):
    """Tiny floating data fragments — digits and symbols drifting through the scene.

    Like the ambient particles of a financial database — encrypted transactions
    floating in the darkness around the ledger.
    """
    for _ in range(100):
        x = rng.randint(0, W)
        y = rng.randint(60, 1765)
        r = rng.randint(1, 3)
        t = rng.random()
        if t < 0.5:
            col = (*LEDGER_GREEN, rng.randint(20, 60))
        elif t < 0.75:
            col = (*AMBER_AUDIT, rng.randint(15, 45))
        else:
            col = (*RED_INK, rng.randint(10, 35))
        draw.ellipse((x - r, y - r, x + r, y + r), fill=col)

    # Occasional larger dollar-amount fragments floating
    for _ in range(8):
        x = rng.randint(100, 1500)
        y = rng.randint(200, 1500)
        amount = f"${rng.randint(1, 999):,}M"
        draw.text((x, y), amount, fill=(*AMBER_AUDIT, rng.randint(15, 40)))


def _vignette(draw):
    """Darken edges to focus attention on the ledger center."""
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(60 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 50))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 50))
    for vx in range(W):
        vt = 1 - abs(vx - W // 2) / (W // 2)
        vv = int(40 * max(0, 1 - vt))
        if vv > 0:
            draw.line((vx, 0, vx, vv), fill=(0, 0, 0, 35))
            draw.line((vx, H - vv, vx, H), fill=(0, 0, 0, 50))


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    rng = random.Random()
    rng.seed(386208441)

    img = Image.new("RGBA", (W, H), BG_TOP)
    draw = ImageDraw.Draw(img, "RGBA")

    # 1. Deep fiscal-green gradient background
    _gradient(draw)

    # 2. Ledger sheet with ruled lines and column borders
    _ledger_sheet(draw, rng)

    # 3. Cascading columns of faint transaction numbers
    _cascading_numbers(draw, rng)

    # 4. Interactive shell-company ownership web
    _shell_company_web(draw, rng)

    # 5. Ghostly figure of the dead man logging in (The Ledgerkeeper)
    _dead_man_logging(draw, rng)

    # 6. Clock frozen at Tuesday 3 AM
    _tuesday_3am_clock(draw)

    # 7. Red audit-trail highlights / forensic evidence markers
    _audit_trail_highlights(draw, rng)

    # 8. Glowing amber money trail through the shell web
    _money_trail_glow(draw, rng)

    # 9. Floating data motes and dollar fragments
    _data_motes(draw, rng)

    # 10. Vignette edge darkening
    _vignette(draw)

    # 11. Standard title panel
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
