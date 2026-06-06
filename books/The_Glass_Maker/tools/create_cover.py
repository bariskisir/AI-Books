#!/usr/bin/env python3
"""Cover: The Glass Maker — 17th-century Venice, amber and ruby glass."""

from __future__ import annotations
import argparse, json, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[3]; FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560

def font(n,s):
    for c in [FONT_DIR/n, FONT_DIR/"arial.ttf"]:
        if c.exists(): return ImageFont.truetype(str(c), s)
    return ImageFont.load_default()

def wrap(d,t,f,w):
    wo=t.split(); li=[]; cu=[]
    for wd in wo:
        p=" ".join([*cu,wd])
        if d.textbbox((0,0),p,font=f)[2]<=w: cu.append(wd)
        else: li.append(" ".join(cu)); cu=[wd]
    if cu: li.append(" ".join(cu))
    return li

def centered(d,y,li,f,fl,g):
    for l in li:
        bb=d.textbbox((0,0),l,font=f)
        d.text(((W-(bb[2]-bb[0]))//2,y),l,font=f,fill=fl)
        y+=bb[3]-bb[1]+g
    return y

def make_cover(mp,op):
    m=json.loads(mp.read_text(encoding="utf-8")); ti=m["title"]; au=m.get("author","Barış Kısır")
    img=Image.new("RGBA",(W,H),(50,30,25,255)); draw=ImageDraw.Draw(img,"RGBA")

    # Warm Venetian gradient — amber to deep crimson
    for y in range(H):
        t=y/H
        r=int(50+80*t)
        g=int(30+20*t)
        b=int(25-10*t)
        draw.line((0,y,W,y), fill=(min(r,255),min(g,255),max(b,0),255))

    # Canal at midground — dark water band
    for y in range(900, 1300):
        t=(y-900)/400
        draw.line((0,y,W,y), fill=(int(40-20*t),int(35-15*t),int(45-10*t),200))

    # Gondola silhouette
    gx, gy = 400, 1150
    draw.arc((gx,gy-120,gx+400,gy+40), 180, 360, fill=(15,15,20,200), width=6)
    draw.polygon([(gx+380,gy-38),(gx+420,gy-60),(gx+420,gy-20)], fill=(15,15,20,200))
    # Gondolier
    draw.ellipse((gx+200,gy-100,gx+240,gy-60), fill=(20,20,25,180))
    draw.polygon([(gx+200,gy-60),(gx+240,gy-60),(gx+220,gy-15)], fill=(15,15,20,180))

    # Building silhouettes on right
    for i in range(4):
        bx = 1100 + i*80
        bh = 700 + i*30
        draw.rectangle((bx,1300-bh,bx+70,1300), fill=(40,30,25,100))

    # Palace arches on left
    for i in range(3):
        ax=100+i*120; ay=950
        draw.arc((ax,ay,ax+100,ay+120), 180, 360, fill=(60,50,40,80), width=5)
        draw.rectangle((ax,ay+60,ax+100,ay+150), fill=(40,35,30,80))

    # Furnace glow — lower left
    fx, fy = 250, 1600
    # Glow circle
    for r in range(150,0,-1):
        a=min(60,int(40*(1-r/150)))
        draw.ellipse((fx-r,fy-r-100,fx+r,fy+r-100), fill=(200,int(100*(1-r/150)),int(20*(1-r/150)),a))
    # Furnace opening
    draw.rectangle((fx-60,fy-80,fx+60,fy+50), fill=(180,60,20,200))
    draw.rectangle((fx-50,fy-70,fx+50,fy+40), fill=(255,120,30,220))
    # Fire within
    draw.ellipse((fx-30,fy-40,fx+30,fy+10), fill=(255,180,50,200))

    # Ruby glass goblet silhouette above furnace
    gfx, gfy = fx, fy-300
    draw.polygon([(gfx-35,gfy),(gfx+35,gfy),(gfx+20,gfy-120),(gfx-20,gfy-120)], fill=(180,40,30,180))  # bowl
    draw.rectangle((gfx-5,gfy-180,gfx+5,gfy-120), fill=(180,40,30,180))  # stem
    draw.ellipse((gfx-25,gfy-200,gfx+25,gfy-180), fill=(180,40,30,180))  # base

    # Chandelier silhouette above
    cx, cy = 1200, 500
    draw.line((cx,cy-80,cx,cy), fill=(50,40,30,150), width=3)
    draw.arc((cx-80,cy,cx+80,cy+100), 180, 360, fill=(60,50,40,120), width=4)
    for a in range(0,360,45):
        rad=math.radians(a)
        lx=cx+int(80*math.cos(rad)); ly=cy+int(80*math.sin(rad))
        draw.line((lx,ly,lx+int(30*math.cos(rad)),ly+int(30*math.sin(rad))), fill=(60,50,40,80), width=2)

    # Title panel
    draw.rectangle((0,1920,W,H), fill=(15,12,10,240))
    draw.line((200,1960,W-200,1960), fill=(180,40,30,200), width=2)
    draw.line((200,H-120,W-200,H-120), fill=(180,40,30,100), width=1)

    # Ruby glow accent dots along bottom line
    for i in range(0,W,80):
        draw.ellipse((i-3,H-126,i+3,H-120), fill=(255,100,50,80))

    tf=font("arialbd.ttf", 100); af=font("arialbd.ttf", 40); sf=font("arial.ttf", 28)

    ypos=2000
    ypos=centered(draw,ypos,wrap(draw,ti.upper(),tf,1200),tf,(230,225,215),10); ypos+=60
    centered(draw,ypos,[au],af,(200,195,185),6)

    op.parent.mkdir(parents=True,exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()))
    img.convert("RGB").save(op,"PNG",optimize=True)


def _standard_cover_font(name: str, size: int):
    font_dir = globals().get("FONT_DIR", globals().get("FONTS_DIR", None))
    candidates = []
    if font_dir is not None:
        candidates.append(Path(font_dir) / name)
    candidates.extend([
        Path("C:/Windows/Fonts") / name,
        Path("C:/Windows/Fonts") / "arialbd.ttf",
        Path("C:/Windows/Fonts") / "arial.ttf",
    ])
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def _standard_cover_repair_text(text: str) -> str:
    try:
        return text.encode("latin1").decode("utf-8")
    except UnicodeError:
        return text


def _standard_cover_wrap(draw, text: str, selected_font, max_width: int) -> list[str]:
    words = text.split()
    lines = []
    current = []
    for word in words:
        proposed = " ".join([*current, word])
        if draw.textbbox((0, 0), proposed, font=selected_font)[2] <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def _standard_cover_center(draw, y: int, lines: list[str], selected_font, fill, line_gap: int, width: int) -> int:
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=selected_font)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), line, font=selected_font, fill=fill)
        y += bbox[3] - bbox[1] + line_gap
    return y


def _standard_cover_title_font(draw, title: str, max_width: int):
    for size in (116, 104, 96, 88, 80, 72):
        selected = _standard_cover_font("arialbd.ttf", size)
        lines = _standard_cover_wrap(draw, title.upper(), selected, max_width)
        heights = [draw.textbbox((0, 0), line, font=selected)[3] - draw.textbbox((0, 0), line, font=selected)[1] for line in lines]
        total = sum(heights) + max(0, len(lines) - 1) * 18
        if len(lines) <= 4 and total <= 430:
            return selected, lines, 18
    selected = _standard_cover_font("arialbd.ttf", 68)
    return selected, _standard_cover_wrap(draw, title.upper(), selected, max_width), 16


def _standard_cover_metadata_from_locals(local_vars):
    for key in ("metadata", "meta", "data", "m", "book", "book_data"):
        value = local_vars.get(key)
        if isinstance(value, dict):
            return value

    candidates = []
    args = local_vars.get("args")
    if args is not None:
        candidates.append(getattr(args, "metadata", None))
    for key in ("metadata_path", "meta_path", "mp"):
        candidates.append(local_vars.get(key))

    for metadata_path in candidates:
        if not metadata_path:
            continue
        try:
            json_mod = __import__("json")
            path_cls = __import__("pathlib").Path
            return json_mod.loads(path_cls(metadata_path).read_text(encoding="utf-8"))
        except Exception:
            continue
    return {}


def _standard_cover_resolve_title(local_vars):
    for key in ("title", "ti", "book_title", "TITLE"):
        value = local_vars.get(key)
        if value:
            return value

    metadata = _standard_cover_metadata_from_locals(local_vars)
    for key in ("title", "book_title", "name"):
        value = metadata.get(key)
        if value:
            return value

    args = local_vars.get("args")
    candidates = []
    if args is not None:
        candidates.append(getattr(args, "out", None))
    for key in ("output_path", "out_path", "op", "out"):
        candidates.append(local_vars.get(key))

    for output_path in candidates:
        if not output_path:
            continue
        try:
            path_cls = __import__("pathlib").Path
            stem = path_cls(output_path).stem.replace("_", " ").strip()
            if stem:
                return stem
        except Exception:
            continue
    return ""


def _standard_cover_resolve_author(local_vars):
    for key in ("author", "au", "AUTHOR"):
        value = local_vars.get(key)
        if value:
            return value

    metadata = _standard_cover_metadata_from_locals(local_vars)
    value = metadata.get("author")
    if value:
        return value
    return "Barış Kısır"

def _draw_standard_cover_title_panel(image, title: str = "", author: str = "") -> None:
    width = int(globals().get("W", globals().get("WIDTH", 1600)))
    height = int(globals().get("H", globals().get("HEIGHT", 2560)))
    panel_y = 1765
    title = _standard_cover_repair_text(str(title or "")).strip()
    author = _standard_cover_repair_text(str(author or "Barış Kısır")).strip()

    draw = ImageDraw.Draw(image, "RGBA")
    draw.rectangle((0, panel_y, width, height), fill=(3, 5, 8, 255))
    draw.line((180, panel_y + 17, width - 180, panel_y + 17), fill=(160, 225, 209, 105), width=3)

    title_font, title_lines, title_gap = _standard_cover_title_font(draw, title, 1260)
    author_font = _standard_cover_font("arialbd.ttf", 50)
    title_height = sum(draw.textbbox((0, 0), line, font=title_font)[3] - draw.textbbox((0, 0), line, font=title_font)[1] for line in title_lines)
    title_height += max(0, len(title_lines) - 1) * title_gap
    author_bbox = draw.textbbox((0, 0), author, font=author_font)
    author_height = author_bbox[3] - author_bbox[1]
    block_height = title_height + 120 + author_height
    y = panel_y + 120 + max(0, (height - panel_y - 210 - block_height) // 2)
    y = _standard_cover_center(draw, y, title_lines, title_font, (244, 249, 238), title_gap, width)
    y += 120
    _standard_cover_center(draw, y, [author], author_font, (210, 229, 221), 12, width)
def main():
    p=argparse.ArgumentParser(); p.add_argument("--metadata",type=Path,required=True); p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    make_cover(ROOT/a.metadata if not a.metadata.is_absolute() else a.metadata, ROOT/a.out if not a.out.is_absolute() else a.out)

if __name__=="__main__": main()