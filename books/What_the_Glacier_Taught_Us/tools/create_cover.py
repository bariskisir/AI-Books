#!/usr/bin/env python3
"""Cover: What the Glacier Taught Us — Three generations of women reunite at a melting Alaskan glacier cabin when the matriarch reveals a diary written in a language no one can read, sparking a reckoning with their erased Indigenous heritage."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# ── Unique palette: glacial twilight, deep crevasses, warm cabin amber, Indigenous ochre/red, thaw-water teal ──
DEEP_TWILIGHT   = (6, 14, 42)
HORIZON_BLUE    = (40, 72, 130)
ICE_BRIGHT      = (225, 242, 255)
ICE_MID         = (160, 205, 235)
ICE_SHADOW      = (80, 140, 190)
CREVASSE_BLUE   = (15, 45, 95)
CREVASSE_DARK   = (8, 22, 55)
CABIN_AMBER     = (255, 195, 70)
CABIN_WARM      = (255, 160, 50)
DIARY_GOLD      = (215, 190, 85)
DIARY_GLOW      = (240, 220, 140)
INDIGENOUS_RED  = (160, 50, 35)
INDIGENOUS_WARM = (190, 90, 50)
SILHOUETTE      = (8, 10, 16)
THAW_CYAN       = (55, 140, 185)
SNOW_WHITE      = (240, 248, 255)


def build_sky(draw: ImageDraw.ImageDraw) -> None:
    """Arctic twilight gradient: deep indigo at zenith to pale blue at the horizon."""
    for y in range(700):
        t = y / 700
        r = int(DEEP_TWILIGHT[0] + (HORIZON_BLUE[0] - DEEP_TWILIGHT[0]) * t)
        g = int(DEEP_TWILIGHT[1] + (HORIZON_BLUE[1] - DEEP_TWILIGHT[1]) * t)
        b = int(DEEP_TWILIGHT[2] + (HORIZON_BLUE[2] - DEEP_TWILIGHT[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))


def build_distant_mountains(img: Image.Image, rng: random.Random) -> Image.Image:
    """Faint jagged peaks on the horizon behind the glacier."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for mi in range(3):
        pts = [(0, 640 + mi * 25)]
        for mx in range(0, W + 10, 10):
            mh = 140 + math.sin(mx * 0.0032 + mi * 2.3) * 90
            mh += math.sin(mx * 0.009 + mi * 3.7) * 20
            pts.append((mx, 360 + mh + mi * 40))
        pts.append((W, 640 + mi * 25))
        cv = 35 - mi * 10
        ld.polygon(pts, fill=(max(4, cv - 6), max(8, cv - 2), max(20, cv + 12), 160))
    for _ in range(10):
        sx = rng.randint(80, W - 80)
        sy = rng.randint(380, 500)
        sw = rng.randint(18, 45)
        sh = rng.randint(5, 12)
        ld.ellipse((sx - sw, sy - sh, sx + sw, sy + sh), fill=(210, 225, 240, rng.randint(30, 60)))
    return Image.alpha_composite(img, layer)


def build_glacier_face(img: Image.Image, rng: random.Random) -> Image.Image:
    """Massive diagonal ice wall — the glacier dominates the middle of the cover.

    The face runs from upper-left (tall) down to lower-right, creating a dramatic
    diagonal composition. Deep crevasses, ice strata, and trapped air bubbles
    are rendered in layered blues.
    """
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(layer)

    # Primary ice face polygon — a towering diagonal wall
    wall_top_left = 420
    wall_top_right = 1000
    wall_base_right = 1780
    wall_base_left = 1300
    face_pts = [
        (0, wall_top_left),
        (W, wall_top_right),
        (W, wall_base_right),
        (0, wall_base_left),
    ]
    gd.polygon(face_pts, fill=(*ICE_MID, 255))

    # Ice face — vertical shading: darker at top, lighter at base
    for y in range(wall_top_left, wall_base_right + 1):
        # interpolate left/right top and bottom
        t = (y - wall_top_left) / (wall_base_right - wall_top_left)
        left_x = 0 + t * 0  # left x stays at 0
        right_x = W + t * 0  # right x stays at W

        # gradient from ice shade at top to bright at bottom
        r = int(ICE_SHADOW[0] + (ICE_BRIGHT[0] - ICE_SHADOW[0]) * t)
        g = int(ICE_SHADOW[1] + (ICE_BRIGHT[1] - ICE_SHADOW[1]) * t)
        b = int(ICE_SHADOW[2] + (ICE_BRIGHT[2] - ICE_SHADOW[2]) * t)
        # add subtle horizontal variation for ice texture
        for x in range(0, W, 4):
            vr = rng.randint(-8, 8)
            vg = rng.randint(-6, 6)
            vb = rng.randint(-4, 4)
            gd.line((x, y, x + 4, y), fill=(r + vr, g + vg, b + vb, 200))

    # ── Ice strata layers (horizontal compression bands) ──
    for si in range(18):
        t_base = 0.05 + si * 0.05
        sy = int(wall_top_left + t_base * (wall_base_right - wall_top_left))
        sy += rng.randint(-6, 6)
        if sy < wall_top_left or sy > wall_base_right:
            continue
        # wavy strata line
        for x in range(0, W, 3):
            wave = math.sin(x * 0.02 + si * 1.1) * 4
            a = rng.randint(20, 50)
            gd.line((x, sy + wave, x + 3, sy + wave + 1),
                    fill=(rng.randint(190, 220), rng.randint(220, 245), rng.randint(235, 255), a))

    # ── Deep crevasses (dark blue cracks in the ice) ──
    for ci in range(8):
        cx = rng.randint(100, W - 100)
        cy = rng.randint(wall_top_left + 50, wall_base_right - 100)
        crack_len = rng.randint(40, 160)
        crack_angle = math.radians(rng.randint(-30, 30)) - 0.5  # mostly downward
        cpts = [(cx, cy)]
        ccx, ccy = cx, cy
        for _ in range(rng.randint(4, 10)):
            ccx += math.cos(crack_angle + rng.uniform(-0.3, 0.3)) * rng.randint(15, 40)
            ccy += math.sin(crack_angle + rng.uniform(-0.3, 0.3)) * rng.randint(15, 40) + 20
            cpts.append((ccx, ccy))
        gd.line(cpts, fill=(*CREVASSE_BLUE, rng.randint(180, 240)), width=rng.randint(2, 5))
        # darker inner shadow on one side
        if len(cpts) > 2:
            inner = [(x + 2, y + 2) for x, y in cpts]
            gd.line(inner, fill=(*CREVASSE_DARK, rng.randint(100, 160)), width=1)

    # ── Trapped air bubbles (tiny round highlights in the ice) ──
    for _ in range(60):
        bx = rng.randint(50, W - 50)
        by = rng.randint(wall_top_left + 20, wall_base_right - 20)
        br = rng.choice([1, 1, 2, 2, 3])
        ba = rng.randint(40, 130)
        gd.ellipse((bx - br, by - br, bx + br, by + br), fill=(*SNOW_WHITE, ba))

    # ── Icicles at the top edge of the ice face ──
    for i in range(25):
        ix = rng.randint(20, W - 20)
        # y at top of ice face at this x position
        top_y_pct = ix / W
        top_y = wall_top_left + (wall_top_right - wall_top_left) * top_y_pct
        ic_len = rng.randint(15, 50)
        ic_width = rng.randint(2, 5)
        gd.polygon([
            (ix - ic_width, top_y),
            (ix + ic_width, top_y),
            (ix + 1, top_y + ic_len)
        ], fill=(*ICE_BRIGHT, rng.randint(150, 220)))

    return Image.alpha_composite(img, layer)


def build_meltwater_stream(img: Image.Image, rng: random.Random) -> Image.Image:
    """A braided meltwater stream flowing from under the glacier across the foreground."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(layer)

    # Braided stream channels
    for channel in range(6):
        cx, cy = 200 + rng.randint(-50, 150), 1700 + rng.randint(-50, 50)
        pts = [(cx, cy)]
        for step in range(25):
            cx += math.sin(step * 0.4 + channel * 1.2) * 20 + rng.randint(-8, 8)
            cy += 15 + rng.randint(-3, 6)
            if cy >= H - 50:
                break
            pts.append((cx, cy))
        # Stream channel body
        for i, (px, py) in enumerate(pts[:-1]):
            nx, ny = pts[i + 1]
            w = max(2, int(14 - i * 0.3))
            sd.line((px, py, nx, ny), fill=(*THAW_CYAN, rng.randint(100, 180)), width=w)

    # Light reflection on water
    for _ in range(15):
        rx = rng.randint(100, 600)
        ry = rng.randint(1750, H - 60)
        rr = rng.randint(2, 5)
        sd.ellipse((rx - rr, ry - rr, rx + rr, ry + rr), fill=(180, 220, 240, rng.randint(40, 90)))

    return Image.alpha_composite(img, layer)


def build_cabin(img: Image.Image, rng: random.Random) -> Image.Image:
    """A small log cabin nestled at the glacier's base, radiating warm amber light.

    The cabin sits in the lower-left area. Snow on the roof, warm windows,
    a chimney with smoke. Three generations of women are silhouetted in the doorway.
    """
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(layer)

    cx, cy = 240, 1750  # cabin center

    # ── Snow mound at cabin base ──
    cd.ellipse((cx - 160, cy - 20, cx + 160, cy + 40), fill=(220, 230, 240, 200))

    # ── Cabin walls (log texture) ──
    cabin_w, cabin_h = 140, 100
    left, right = cx - cabin_w, cx + cabin_w
    top, bottom = cy - cabin_h, cy

    # Main wall
    cd.rectangle((left, top, right, bottom), fill=(45, 30, 18, 230))
    # Log lines
    for log_y in range(top + 12, bottom, 14):
        cd.line((left + 4, log_y, right - 4, log_y), fill=(55, 38, 22, 180), width=2)
        cd.line((left + 4, log_y + 1, right - 4, log_y + 1), fill=(35, 22, 12, 120), width=1)

    # ── Roof (snow-laden) ──
    roof_pts = [
        (left - 20, top),
        (cx, top - 55),
        (right + 20, top),
        (right + 10, top + 5),
        (left - 10, top + 5),
    ]
    cd.polygon(roof_pts, fill=(55, 38, 20, 230))

    # Snow on roof
    cd.polygon([
        (left - 15, top),
        (cx, top - 50),
        (right + 15, top),
        (right + 25, top + 8),
        (left - 25, top + 8),
    ], fill=(SNOW_WHITE[0], SNOW_WHITE[1], SNOW_WHITE[2], 210))

    # Snow hanging off eaves
    cd.ellipse((left - 25, top - 5, left + 5, top + 12), fill=(*SNOW_WHITE, 200))
    cd.ellipse((right - 5, top - 5, right + 25, top + 12), fill=(*SNOW_WHITE, 200))

    # ── Warm window glow ──
    # Left window
    cd.rectangle((left + 15, top + 20, left + 50, top + 65), fill=(*CABIN_AMBER, 220))
    cd.rectangle((left + 15, top + 20, left + 50, top + 65), fill=(*CABIN_WARM, 120))
    # Window crossbars
    cd.line((left + 32, top + 20, left + 32, top + 65), fill=(35, 22, 12, 200), width=2)
    cd.line((left + 15, top + 42, left + 50, top + 42), fill=(35, 22, 12, 200), width=2)

    # Right window
    cd.rectangle((right - 50, top + 20, right - 15, top + 65), fill=(*CABIN_AMBER, 220))
    cd.rectangle((right - 50, top + 20, right - 15, top + 65), fill=(*CABIN_WARM, 120))
    cd.line((right - 32, top + 20, right - 32, top + 65), fill=(35, 22, 12, 200), width=2)
    cd.line((right - 50, top + 42, right - 15, top + 42), fill=(35, 22, 12, 200), width=2)

    # ── Warm light spilling onto snow ──
    spill = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    spd = ImageDraw.Draw(spill)
    spd.ellipse((cx - 180, cy - 30, cx + 180, cy + 80), fill=(*CABIN_AMBER, 20))
    spill = spill.filter(ImageFilter.GaussianBlur(15))
    layer = Image.alpha_composite(layer, spill)
    cd = ImageDraw.Draw(layer)

    # ── Chimney and smoke ──
    cd.rectangle((cx + 40, top - 70, cx + 55, top - 30), fill=(40, 28, 16, 220))
    # Smoke wisps
    for si in range(6):
        sx = cx + 48 + rng.randint(-8, 8)
        sy = top - 80 - si * 18
        sr = 8 + si * 4
        sa = max(3, 25 - si * 4)
        cd.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=(120, 115, 110, sa))

    # ── Three female silhouettes in the doorway (the three generations) ──
    door_left = cx - 18
    door_right = cx + 18
    door_top = top + 5
    door_bottom = cy

    # Doorway dark interior
    cd.rectangle((door_left, door_top, door_right, door_bottom), fill=(5, 3, 2, 230))

    # Figure positions (oldest to youngest, left to right)
    fig_data = [
        (door_left + 6, door_bottom, 0.70, 0),   # Ruth (matriarch) — center, tallest
        (door_left - 12, door_bottom, 0.60, -4),  # Lena (middle) — slightly left, shorter
        (door_right + 10, door_bottom, 0.50, -6), # Sophie (youngest) — slightly right, shortest
    ]

    for fx, fy, scale, x_off in fig_data:
        # Head
        head_r = int(10 * scale)
        head_y = fy - int(45 * scale)
        cd.ellipse((fx - head_r + x_off, head_y - head_r, fx + head_r + x_off, head_y + head_r),
                   fill=(*SILHOUETTE, 230))
        # Body
        cd.polygon([
            (fx - int(12 * scale) + x_off, head_y + head_r),
            (fx + int(12 * scale) + x_off, head_y + head_r),
            (fx + int(6 * scale) + x_off, fy),
            (fx - int(6 * scale) + x_off, fy),
        ], fill=(*SILHOUETTE, 230))

    # Edge glow on silhouettes from the warm light behind them (rim light)
    rim = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rim)
    rd.ellipse((cx - 80, cy - 130, cx + 80, cy + 20), fill=(*CABIN_AMBER, 6))
    rim = rim.filter(ImageFilter.GaussianBlur(8))
    layer = Image.alpha_composite(layer, rim)

    return Image.alpha_composite(img, layer)


def build_diary_and_script(img: Image.Image, rng: random.Random) -> Image.Image:
    """The diary — a weathered leather-bound book — floats in the lower-right foreground,
    glowing with indecipherable script. Ghostly Indigenous formline patterns emanate from it,
    weaving upward through the ice in translucent ochre and red.

    This is the emotional heart of the cover: the lost language seeking to be remembered.
    """
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(layer)

    # ── Diary position (lower right) ──
    dx, dy = 1200, 1900
    diary_w, diary_h = 120, 160
    diary_angle = -0.15  # slight tilt

    # Outer golden glow
    for rad in range(100, 10, -8):
        a = max(0, 50 - rad // 2)
        dd.ellipse((dx - rad, dy - rad, dx + rad, dy + rad),
                   fill=(*DIARY_GOLD, a))
    glow = layer.filter(ImageFilter.GaussianBlur(20))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(layer)
    # Redraw diary on top of glow

    # Diary cover (leather)
    dd.rectangle((dx - diary_w, dy - diary_h, dx + diary_w, dy + diary_h),
                 fill=(50, 30, 12, 240))

    # Spine
    dd.rectangle((dx - diary_w - 8, dy - diary_h, dx - diary_w, dy + diary_h),
                 fill=(35, 20, 8, 240))

    # Pages (golden edge)
    dd.rectangle((dx - diary_w + 8, dy - diary_h + 6, dx + diary_w - 8, dy + diary_h - 6),
                 fill=(*DIARY_GOLD, 200))

    # Pages visible on the side (book slightly open)
    for page in range(8):
        py = dy - diary_h + 12 + page * 18
        pa = rng.randint(60, 120)
        dd.line((dx + diary_w - 10, py, dx + diary_w - 6, py + 4),
                fill=(*DIARY_GLOW, pa), width=2)

    # ── Indecipherable script on the open pages ──
    script_chars = [
        "ᐃ", "ᐅ", "ᐊ", "ᑉ", "ᑕ", "ᑯ", "ᒥ", "ᓄ", "ᓯ", "ᔭ",
        "ᙱ", "ᖏ", "ᖑ", "ᖕ", "ᖠ", "ᙳ", "ᖂ", "ᖄ", "ᕿ", "ᑐ",
    ]
    # Lines of "text" on the diary pages
    for line in range(6):
        line_y = dy - diary_h + 25 + line * 20
        line_x = dx - diary_w + 18
        for _ in range(rng.randint(5, 9)):
            ch = rng.choice(script_chars)
            dd.text((line_x, line_y), ch, fill=(*DIARY_GLOW, rng.randint(180, 240)),
                    font=None)  # will use default — we'll draw manually
            line_x += 16

    # ── Indigenous formline patterns emanating from the diary ──
    # These are geometric shapes inspired by Northwest Coast/Inuit formline art:
    # ovoids, U-forms, S-curves — rendered in translucent INDIGENOUS_RED

    formline_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(formline_layer)

    # Primary ovoid forms (the classic formline basic shape)
    for ovoid in range(14):
        # Position: emanating from diary upward and outward
        angle = math.radians(-60 + rng.uniform(-10, 10) - ovoid * 6)
        dist = 80 + ovoid * 45 + rng.randint(-20, 30)
        ox = dx + math.cos(angle) * dist + rng.randint(-30, 30)
        oy = dy + math.sin(angle) * dist + rng.randint(-30, 30)

        if oy < 200 or oy > 2100 or ox < -100 or ox > W + 100:
            continue

        ovoid_w = rng.randint(18, 55)
        ovoid_h = rng.randint(12, 35)
        alpha = max(10, 80 - ovoid * 5)

        # Ovoid: rounded rectangle with indented top/bottom (classic formline)
        col = rng.choice([INDIGENOUS_RED, INDIGENOUS_WARM])
        fd.ellipse((ox - ovoid_w, oy - ovoid_h, ox + ovoid_w, oy + ovoid_h),
                   fill=(*col, alpha))

        # Inner shape (negative space)
        inner_w = int(ovoid_w * 0.5)
        inner_h = int(ovoid_h * 0.5)
        fd.ellipse((ox - inner_w, oy - inner_h, ox + inner_w, oy + inner_h),
                   fill=(*col, max(3, alpha - 20)))

    # U-forms and S-curves — flowing lines that connect the ovoids
    for li in range(20):
        angle = math.radians(-70 + li * 5 + rng.uniform(-8, 8))
        dist = 70 + li * 40 + rng.randint(-10, 20)
        sx = dx + math.cos(angle) * dist
        sy = dy + math.sin(angle) * dist
        if sy < 150 or sy > 2100:
            continue

        # Draw a flowing U-shape or S-curve
        u_width = rng.randint(20, 50)
        u_height = rng.randint(15, 40)
        col = rng.choice([INDIGENOUS_RED, INDIGENOUS_WARM])
        alpha = max(5, 60 - li * 3)

        # U-form: two parallel lines curving at the bottom
        cx = sx
        cy = sy + u_height // 2
        fd.arc((cx - u_width, cy - u_height, cx, cy),
               180, 360, fill=(*col, alpha), width=2)
        fd.arc((cx, cy - u_height, cx + u_width, cy),
               180, 360, fill=(*col, alpha), width=2)

    # S-curves — flowing double lines
    for si in range(12):
        angle = math.radians(-65 + si * 7 + rng.uniform(-5, 5))
        dist = 100 + si * 35 + rng.randint(-15, 15)
        sx = dx + math.cos(angle) * dist
        sy = dy + math.sin(angle) * dist
        if sy < 200 or sy > 2000:
            continue

        col = rng.choice([INDIGENOUS_RED, INDIGENOUS_WARM])
        alpha = max(5, 50 - si * 3)
        pts = []
        cx, cy = sx, sy
        for st in range(12):
            cx += math.sin(st * 0.7) * 8
            cy -= 6 + math.cos(st * 0.5) * 3
            pts.append((cx, cy))
        fd.line(pts, fill=(*col, alpha), width=2)

    # Ghostly faces/masks emerging from the text (ancestral spirits)
    for fi in range(5):
        angle = math.radians(-55 + fi * 8 + rng.uniform(-5, 5))
        dist = 150 + fi * 30 + rng.randint(-10, 20)
        fx = dx + math.cos(angle) * dist
        fy = dy + math.sin(angle) * dist - 50
        if fy < 300 or fy > 1900:
            continue

        # Simple mask-like oval — suggesting an ancestral face
        fw, fh = rng.randint(20, 35), rng.randint(25, 40)
        alpha = max(5, 40 - fi * 7)
        fd.ellipse((fx - fw, fy - fh, fx + fw, fy + fh),
                   fill=(*INDIGENOUS_RED, alpha))
        # Eyes
        eye_off = fw // 3
        fd.ellipse((fx - eye_off - 3, fy - 5, fx - eye_off + 3, fy + 3),
                   fill=(*INDIGENOUS_RED, alpha + 10))
        fd.ellipse((fx + eye_off - 3, fy - 5, fx + eye_off + 3, fy + 3),
                   fill=(*INDIGENOUS_RED, alpha + 10))

    # Soft blur to blend the formline elements
    formline_layer = formline_layer.filter(ImageFilter.GaussianBlur(2))
    layer = Image.alpha_composite(layer, formline_layer)

    # ── Secondary golden glow burst from within the diary ──
    burst = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(burst)
    for bi in range(8):
        ba = math.radians(bi * 45 + rng.randint(-5, 5))
        bl = rng.randint(60, 150)
        bd.line((dx, dy, dx + math.cos(ba) * bl, dy + math.sin(ba) * bl),
                fill=(*DIARY_GLOW, rng.randint(5, 15)), width=rng.randint(2, 5))
    burst = burst.filter(ImageFilter.GaussianBlur(6))
    layer = Image.alpha_composite(layer, burst)

    return Image.alpha_composite(img, layer)


def add_stars_and_atmosphere(img: Image.Image, rng: random.Random) -> Image.Image:
    """Tiny stars in the upper sky and subtle ice-fog at the base of the glacier."""
    draw = ImageDraw.Draw(img, "RGBA")

    # Stars (only in the upper region, above the glacier)
    for _ in range(80):
        sx = rng.randint(0, W)
        sy = rng.randint(10, 380)
        sr = rng.choice([1, 1, 2])
        sa = rng.randint(60, 180)
        draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=(220, 225, 240, sa))

    # Ice fog / mist at the glacier base
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog)
    fd.ellipse((-200, 1700, W + 200, 2100), fill=(*ICE_BRIGHT, 15))
    fd.ellipse((-100, 1500, W // 2, 1950), fill=(*ICE_BRIGHT, 10))
    fog = fog.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img, fog)

    # Add scattered light motes (snow/ice crystals catching the cabin + diary light)
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(45):
        mx = rng.randint(50, W - 50)
        my = rng.randint(200, H - 200)
        mr = rng.uniform(1, 3)
        ma = rng.randint(20, 70)
        mc = rng.choice([(220, 230, 240), (255, 220, 180), (210, 200, 160)])
        draw.ellipse((mx - mr, my - mr, mx + mr, my + mr), fill=(*mc, ma))

    return img


def make_cover(mp: Path, op: Path) -> None:
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")
    rng = random.Random("glacier-taught-us-diary-2025")

    # Base canvas
    img = Image.new("RGBA", (W, H), DEEP_TWILIGHT + (255,))
    draw = ImageDraw.Draw(img, "RGBA")

    # Layer 1: Sky
    build_sky(draw)

    # Layer 2: Distant mountains
    img = build_distant_mountains(img, rng)

    # Layer 3: The glacier — massive diagonal ice face
    img = build_glacier_face(img, rng)

    # Layer 4: Meltwater stream
    img = build_meltwater_stream(img, rng)

    # Layer 5: The cabin and three generations
    img = build_cabin(img, rng)

    # Layer 6: The diary with Indigenous formline patterns
    img = build_diary_and_script(img, rng)

    # Layer 7: Atmosphere (stars, ice fog, light motes)
    img = add_stars_and_atmosphere(img, rng)

    # Save with standard title panel
    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, title, author, model)
    img.convert("RGB").save(op, "PNG", optimize=True)
    print(f"Cover saved to {op}")


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
