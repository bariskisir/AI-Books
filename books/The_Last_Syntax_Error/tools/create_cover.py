#!/usr/bin/env python3
"""Cover: The Last Syntax Error — A washed-up code detective in a megacity where law is written in executable clauses discovers a hidden subroutine that, if executed, will retroactively render every human who ever had a criminal record legally non-existent, erasing millions from history. Central Codex monolith of executable law cracks open at a fatal syntax error; ghostly erasure silhouettes dissolve on either side as a lone detective faces the code."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# ── Corrupted-Legality Palette ──────────────────────────────────────────
# Deep void indigo to lawless crimson, code-stream cyan, fatal-error amber,
# erasure ghost-white, syntax-comment green, data-string gold, glitch magenta
VOID_TOP = (8, 3, 18)
VOID_BOT = (55, 10, 30)
C_CODE = (70, 215, 235)       # cyan — code keywords
C_NORMAL = (50, 160, 180)     # teal — normal code
C_STRING = (255, 180, 50)     # amber — string literals / data
C_COMMENT = (80, 200, 100)    # green — comments
C_FATAL = (255, 130, 20)      # bright amber — fatal error
C_CORRUPT = (230, 35, 55)     # red — data corruption
C_GLITCH = (240, 35, 195)     # magenta — glitch artifact
C_GHOST = (180, 195, 215)     # ghost white — erasure
C_WARN = (220, 50, 60)        # warning red

rng = random.Random()
rng.seed(1984462735)


# ── Helper: code-row generation ─────────────────────────────────────────

def _generate_code_rows(
    width: int, height: int, row_start: int, row_end: int,
) -> list[list[dict]]:
    """Generate a 2D grid of code token blocks representing the Codex.

    Each token dict: {x, y, w, h, color, alpha}
    The middle third is the "fatal subroutine zone" — tokens become
    corrupted, overlaid with error highlights, and a prominent
    "SYNTAX_ERROR" marker splits the monolith vertically.
    """
    rows: list[list[dict]] = []
    line_height = 18
    gutter = 14
    fatal_center_x = width // 2
    fatal_zone_left = fatal_center_x - 180
    fatal_zone_right = fatal_center_x + 180

    for row_i, y in enumerate(range(row_start, row_end, line_height)):
        row_tokens: list[dict] = []
        x = gutter
        in_fatal_zone = (fatal_zone_left < x + 40 < fatal_zone_right) or \
                        abs(row_i - 18) < 10  # middle rows get corruption

        # Every row is a mix of keyword/string/comment tokens
        while x < width - gutter:
            # Token type and size
            is_fatal_region = (fatal_zone_left < x < fatal_zone_right) and \
                              (12 <= row_i <= 30)
            is_deep_fatal = is_fatal_region and (18 <= row_i <= 24)

            if is_deep_fatal and rng.random() < 0.35:
                # Corrupted token — broken half-width glitch fragment
                tw = rng.randint(6, 18)
                th = line_height - 4
                color = C_CORRUPT if rng.random() < 0.6 else C_GLITCH
                alpha = rng.randint(160, 220)
                # Draw a broken token with a zigzag top
                row_tokens.append({
                    "x": x, "y": y + 2, "w": tw, "h": th,
                    "color": color, "alpha": alpha, "type": "corrupt",
                })
                # Maybe a tiny error highlight dot
                if rng.random() < 0.4:
                    row_tokens.append({
                        "x": x + rng.randint(2, tw - 3),
                        "y": y + rng.randint(2, 6),
                        "w": 3, "h": 3,
                        "color": C_WARN, "alpha": 200, "type": "dot",
                    })
                x += tw + rng.randint(2, 5)
                continue

            if is_fatal_region and rng.random() < 0.2:
                # Error underline — a bright line under the token
                tw = rng.randint(12, 30)
                row_tokens.append({
                    "x": x, "y": y + line_height - 3,
                    "w": tw, "h": 2,
                    "color": C_FATAL, "alpha": rng.randint(180, 255),
                    "type": "error",
                })
                x += tw + rng.randint(2, 4)
                continue

            # Normal code tokens
            t = rng.random()
            if t < 0.30:
                # Keyword (cyan)
                tw = rng.randint(16, 48)
                tc = C_CODE
                ta = rng.randint(140, 210)
            elif t < 0.55:
                # Identifier / normal (teal)
                tw = rng.randint(12, 34)
                tc = C_NORMAL
                ta = rng.randint(110, 170)
            elif t < 0.75:
                # String literal (amber)
                tw = rng.randint(22, 60)
                tc = C_STRING
                ta = rng.randint(130, 200)
            else:
                # Comment (green)
                tw = rng.randint(18, 54)
                tc = C_COMMENT
                ta = rng.randint(100, 170)

            # Slight corruption in fatal zone: colours shift to warm
            if is_fatal_region:
                if rng.random() < 0.3:
                    tc = C_CORRUPT if rng.random() < 0.5 else C_FATAL
                    ta = min(255, ta + 40)
                elif rng.random() < 0.2:
                    tc = C_GLITCH
                    ta = min(255, ta + 30)

            th = line_height - 6
            row_tokens.append({
                "x": x, "y": y + 3, "w": tw, "h": th,
                "color": tc, "alpha": ta, "type": "normal",
            })
            x += tw + rng.randint(2, 6)

        rows.append(row_tokens)
    return rows


def _draw_code_lines(draw, rows: list[list[dict]]):
    """Draw all code token blocks onto the image."""
    for row in rows:
        for tok in row:
            x, y, w, h = tok["x"], tok["y"], tok["w"], tok["h"]
            col = tok["color"]
            alpha = tok["alpha"]
            ttype = tok.get("type", "normal")

            if ttype == "corrupt":
                # Jagged broken block
                draw.polygon([
                    (x, y + h), (x, y), (x + w, y + h // 2),
                    (x + w, y + h),
                ], fill=(*col, alpha))
            elif ttype == "error":
                draw.line((x, y, x + w, y), fill=(*col, alpha), width=2)
            elif ttype == "dot":
                draw.ellipse((x, y, x + w, y + h), fill=(*col, alpha))
            else:
                draw.rectangle((x, y, x + w, y + h), fill=(*col, alpha))


# ── Ghost silhouette (erasure victim) ───────────────────────────────────

def _draw_erasure_silhouette(
    draw, cx: int, cy: int, scale: float, mirrored: bool,
):
    """Draw a dissolving human silhouette — a person being erased from
    existence by the Codex's hidden subroutine. Made of scattered
    horizontal line fragments that fade toward the outer edge."""
    dir_sign = -1 if mirrored else 1
    # Body shape — column of horizontal dashes at varying widths
    segments = [
        # (y_offset, width, density)
        (-140, 40, 0.9),   # top of head
        (-110, 60, 0.85),  # head
        (-80, 52, 0.8),
        (-55, 70, 0.85),   # shoulders
        (-35, 56, 0.8),
        (0, 50, 0.75),     # torso
        (30, 46, 0.7),
        (60, 40, 0.65),
        (85, 30, 0.55),    # hips
        (100, 18, 0.4),
        (110, 14, 0.3),
        (118, 8, 0.2),     # legs dissolve
        (125, 4, 0.1),
    ]

    for y_off, width, density in segments:
        sy = cy + int(y_off * scale)
        half_w = int(width * scale * dir_sign)
        # Draw as fragmented horizontal dashes
        for dx in range(0, abs(half_w), 3):
            if rng.random() > density:
                continue  # skip — erasure fragmentation
            dash_len = rng.randint(2, 6)
            x_pos = cx + (dx if half_w > 0 else -dx)
            if x_pos < 0 or x_pos >= W:
                continue
            # Fade alpha based on distance from centre and vertical position
            dist_factor = max(0.0, 1.0 - (abs(dx) / max(abs(half_w), 1)))
            vert_fade = max(0.0, 1.0 - (y_off + 140) / 280)
            alpha = int(min(180, 220 * dist_factor * vert_fade * density))
            if alpha < 8:
                continue
            # Ghost colour shifts slightly with position
            gc = (
                rng.randint(150, 200),
                rng.randint(170, 215),
                rng.randint(190, 230),
            )
            draw.line((
                x_pos, sy, x_pos + dash_len, sy,
            ), fill=(*gc, alpha), width=rng.randint(1, 2))


# ── Main cover composition ──────────────────────────────────────────────

def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), VOID_TOP + (255,))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 1. Gradient: deep void top -> lawless crimson bottom ────────────
    for y in range(H):
        t = y / H
        r = int(VOID_TOP[0] + (VOID_BOT[0] - VOID_TOP[0]) * t)
        g = int(VOID_TOP[1] + (VOID_BOT[1] - VOID_TOP[1]) * t)
        b = int(VOID_TOP[2] + (VOID_BOT[2] - VOID_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── 2. Vignette ────────────────────────────────────────────────────
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(40 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 90))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 90))

    # ── 3. The Codex Monolith — a towering column of executable legal
    #      code dominating the centre of the composition ────────────────
    monolith_margin = 250  # horizontal margins for the code block
    code_left = monolith_margin
    code_right = W - monolith_margin
    code_top = 180
    code_bot = 1720
    code_width = code_right - code_left

    # Generate and draw the code rows
    rows = _generate_code_rows(code_width, H, code_top, code_bot)
    # Shift each token's x by code_left
    shifted_rows = []
    for row in rows:
        shifted = []
        for tok in row:
            t = dict(tok)
            t["x"] += code_left
            shifted.append(t)
        shifted_rows.append(shifted)
    _draw_code_lines(draw, shifted_rows)

    # ── 4. The syntax-error fissure: a jagged vertical crack through the
    #      centre of the Codex where the fatal subroutine is exposed ────
    crack_cx = W // 2
    crack_top = 160
    crack_bot = code_bot

    # Glowing amber warning band surrounding the crack
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for band_r in range(12, 48, 4):
        alpha_band = max(1, 16 - band_r // 4)
        gd.rectangle((
            crack_cx - band_r, crack_top - 20,
            crack_cx + band_r, crack_bot + 20,
        ), fill=(*C_FATAL, alpha_band))
    glow = glow.filter(ImageFilter.GaussianBlur(14))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Jagged crack line
    prev_y = crack_top
    prev_x = crack_cx + rng.randint(-3, 3)
    for cr_y in range(crack_top + 8, crack_bot, 12):
        cr_x = crack_cx + rng.randint(-8, 8)
        draw.line((prev_x, prev_y, cr_x, cr_y),
                  fill=(*C_FATAL, rng.randint(160, 230)), width=rng.randint(2, 4))
        # Small forked sparks
        if rng.random() < 0.3:
            f_x = cr_x + rng.randint(-15, 15)
            f_y = cr_y + rng.randint(-4, 4)
            draw.line((cr_x, cr_y, f_x, f_y),
                      fill=(*C_CORRUPT, rng.randint(100, 180)), width=1)
        prev_x, prev_y = cr_x, cr_y

    # "SYNTAX ERROR" marker — rendered as a bold bright panel across the crack
    # (Implemented as geometric blocks suggesting the text)
    marker_y = code_top + 320
    marker_w = 280
    marker_h = 36
    marker_x = crack_cx - marker_w // 2
    # Background panel
    draw.rectangle((
        marker_x - 8, marker_y - 8,
        marker_x + marker_w + 8, marker_y + marker_h + 8,
    ), fill=(160, 30, 15, 220))
    # Outer border glow
    draw.rectangle((
        marker_x - 10, marker_y - 10,
        marker_x + marker_w + 10, marker_y + marker_h + 10,
    ), outline=(*C_FATAL, 140), width=2)
    # Character blocks simulating "SYNTAX ERROR"
    label = "SYNTAX_ERROR"
    char_w = marker_w // len(label)
    for ci, ch in enumerate(label):
        cx2 = marker_x + ci * char_w + char_w // 2
        cy2 = marker_y + marker_h // 2
        char_h = marker_h - 10
        # Bright amber with slight random pixel noise
        draw.rectangle((
            marker_x + ci * char_w + 2, marker_y + 4,
            marker_x + (ci + 1) * char_w - 2, marker_y + marker_h - 4,
        ), fill=(*C_FATAL, 200))
        # Small glitch offset on some characters
        if rng.random() < 0.3:
            offset = rng.randint(-3, 3)
            draw.rectangle((
                marker_x + ci * char_w + 2 + offset, marker_y + 4,
                marker_x + (ci + 1) * char_w - 2 + offset,
                marker_y + marker_h - 4,
            ), fill=(*C_GLITCH, 100))

    # Fatal subroutine zone bracket — a right-side pulsing bracket
    bracket_x = code_right + 8
    bracket_top = code_top + 270
    bracket_bot = code_top + 410
    draw.line((bracket_x, bracket_top, bracket_x, bracket_bot),
              fill=(*C_FATAL, 160), width=3)
    draw.line((bracket_x, bracket_top, bracket_x + 18, bracket_top),
              fill=(*C_FATAL, 160), width=2)
    draw.line((bracket_x, bracket_bot, bracket_x + 18, bracket_bot),
              fill=(*C_FATAL, 160), width=2)
    # Small label blocks
    label_y = bracket_bot + 6
    for li in range(40):
        draw.rectangle((
            bracket_x, label_y + li * 1,
            bracket_x + rng.randint(1, 4), label_y + li * 1 + 1,
        ), fill=(*C_COMMENT, rng.randint(100, 180)))

    # ── 5. Erasure silhouettes — two ghostly figures dissolving on
    #      either side of the Codex, representing retroactively-deleted
    #      citizens ─────────────────────────────────────────────────────
    # Left silhouette — Cade Morrow facing the code
    _draw_erasure_silhouette(
        draw, code_left - 60, 950, 1.8, mirrored=False,
    )
    # Right silhouette — a second figure, more dissolved (earlier erasure)
    _draw_erasure_silhouette(
        draw, code_right + 60, 1000, 1.6, mirrored=True,
    )
    # A smaller third silhouette behind the left one, barely visible
    _draw_erasure_silhouette(
        draw, code_left - 120, 750, 1.0, mirrored=False,
    )

    # ── 6. Floating data particles — fragments of deleted records
    #      drifting upward like ash from the Codex ──────────────────────
    for _ in range(120):
        px = rng.randint(40, W - 40)
        py = rng.randint(code_top, 1600)
        style = rng.random()
        alpha = rng.randint(30, 150)
        size = rng.randint(2, 6)
        if style < 0.4:
            # Cyan data dot
            col = (rng.randint(60, 100), rng.randint(190, 235),
                   rng.randint(220, 255), alpha)
            draw.ellipse((px - size, py - size, px + size, py + size), fill=col)
        elif style < 0.7:
            # Red warning diamond
            col = (rng.randint(200, 255), rng.randint(30, 70),
                   rng.randint(40, 90), alpha)
            draw.polygon([
                (px, py - size), (px + size, py),
                (px, py + size), (px - size, py),
            ], fill=col)
        else:
            # Ghost-white hex fragment
            col = (rng.randint(160, 200), rng.randint(180, 220),
                   rng.randint(200, 240), alpha)
            pts = []
            for hi in range(6):
                ha = math.radians(hi * 60 + 30)
                pts.append((px + math.cos(ha) * size,
                           py + math.sin(ha) * size))
            draw.polygon(pts, fill=col)

    # ── 7. Horizontal scan lines across the code — CRT monitor effect ──
    for y in range(code_top, code_bot, 4):
        draw.line((code_left, y, code_right, y), fill=(0, 0, 0, 6))

    # ── 8. The crack's residual glow at the bottom: execution countdown ─
    countdown_y = 1630
    countdown_x = crack_cx - 180
    countdown_w = 360
    # Progress bar frame
    draw.rectangle((
        countdown_x, countdown_y,
        countdown_x + countdown_w, countdown_y + 14,
    ), outline=(*C_FATAL, 100), width=1)
    # Fill at 87% (subroutine nearly executed)
    fill_w = int(countdown_w * 0.87)
    draw.rectangle((
        countdown_x, countdown_y,
        countdown_x + fill_w, countdown_y + 14,
    ), fill=(*C_FATAL, 180))
    # Ticks on the bar
    for ti in range(11):
        tx = countdown_x + int(countdown_w * ti / 10)
        draw.line((tx, countdown_y - 3, tx, countdown_y),
                  fill=(*C_GHOST, 80), width=1)

    # ── 9. Vignette pass 2 (subtle inner shadow reinforcement) ─────────
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(25 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 50))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 50))

    # ── Save ────────────────────────────────────────────────────────────
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
