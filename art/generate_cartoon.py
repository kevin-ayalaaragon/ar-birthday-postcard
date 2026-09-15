"""
Generate a flat-cartoon illustration of two helmeted figures on a ropes
course, echoing the reference photo (two people, orange/red climbing
helmets, warm red rigging-course lighting, big smiles).

This is a hand-drawn-with-code placeholder/starter illustration, not an AI
photo-to-cartoon conversion (no image-generation model is available in this
environment). It's deliberately built with some background detail/texture
(rope lines, rigging dots, vignette) rather than flat single-color blocks,
since MindAR tracks better with visual detail. Swap it out for real AI-
generated or hand-drawn art later if you want higher fidelity - see
README.md section 0 for a ready-to-use prompt.

Usage:
    pip install pillow
    python generate_cartoon.py
Writes ../target-source.jpg
"""

import math
import os
from PIL import Image, ImageDraw, ImageFilter


# Match the postcard's actual photo-window aspect ratio (~2.02:1, from
# print/build_postcard.py's polaroid math) so build_postcard.py's cover-fit
# crop doesn't chop through the faces.
W, H = 1800, 890
BG_SCALE = H / 1200  # tuning below was dialed in at H=1200
OUT_PATH = os.path.join("..", "target-source.jpg")

# Palette - warm reds/magentas for the rigging-course lighting, orange/red
# helmets to match the reference photo.
BG_TOP = (58, 12, 28)
BG_BOTTOM = (176, 40, 46)
RIGGING = (90, 24, 34)
ROPE = (60, 16, 24)
SKIN_A = (230, 176, 140)
SKIN_B = (214, 156, 122)
HELMET_ORANGE = (255, 122, 40)
HELMET_RED = (226, 60, 50)
HELMET_SHADOW = (0, 0, 0)
HARNESS_YELLOW = (255, 205, 60)
HAIR_DARK = (48, 28, 24)
TEETH = (255, 250, 240)
BLUSH = (255, 140, 120)


def vertical_gradient(draw, box, top_color, bottom_color):
    x0, y0, x1, y1 = box
    height = y1 - y0
    for i in range(height):
        t = i / max(height - 1, 1)
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * t)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * t)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
        draw.line([(x0, y0 + i), (x1, y0 + i)], fill=(r, g, b))


def draw_background(img, draw):
    vertical_gradient(draw, (0, 0, W, H), BG_TOP, BG_BOTTOM)

    # rigging bars along the top, like ceiling truss/pulley hardware
    s = BG_SCALE
    for y in (40 * s, 70 * s):
        draw.line([(0, y), (W, y)], fill=RIGGING, width=6)
    for x in range(80, W, 160):
        draw.line([(x, 20 * s), (x, 110 * s)], fill=RIGGING, width=8)
        draw.ellipse([x - 10, 95 * s, x + 10, 115 * s], fill=RIGGING)

    # converging zipline/rope cables, like the photo's rigging lines
    vanish = (W * 0.55, -H * 0.4)
    for start_x in range(-200, W + 400, 140):
        draw.line([(start_x, H * 0.55), vanish], fill=ROPE, width=5)

    # soft vignette corners
    vignette = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(vignette)
    vd.ellipse([-W * 0.3, -H * 0.3, W * 1.3, H * 1.3], fill=255)
    vignette = vignette.filter(ImageFilter.GaussianBlur(180 * BG_SCALE))
    dark = Image.new("RGB", (W, H), (10, 0, 4))
    img.paste(dark, (0, 0), Image.eval(vignette, lambda v: 255 - v))


def draw_smile(draw, cx, cy, w, h, color=HAIR_DARK, teeth=True):
    box = [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]
    draw.arc(box, start=15, end=165, fill=color, width=max(4, int(h / 6)))
    if teeth:
        tw, th = w * 0.55, h * 0.35
        draw.ellipse([cx - tw / 2, cy - th * 0.1, cx + tw / 2, cy + th], fill=TEETH)
        draw.arc(box, start=15, end=165, fill=color, width=max(4, int(h / 6)))


def draw_helmet(draw, cx, cy, r, color, brim_color=None, logo=True):
    brim_color = brim_color or tuple(max(0, c - 40) for c in color)
    # dome
    draw.pieslice([cx - r, cy - r, cx + r, cy + r * 0.15], start=180, end=360, fill=color)
    draw.rectangle([cx - r, cy - r * 0.05, cx + r, cy + r * 0.15], fill=color)
    # brim (sits above the eyebrow line, well clear of the eyes)
    draw.ellipse([cx - r * 1.05, cy + r * 0.02, cx + r * 1.05, cy + r * 0.26], fill=brim_color)
    # vents / highlight
    draw.arc([cx - r * 0.8, cy - r * 0.95, cx + r * 0.8, cy], start=200, end=280,
              fill=(255, 255, 255), width=max(3, int(r * 0.05)))
    if logo:
        lw, lh = r * 0.5, r * 0.22
        draw.rounded_rectangle(
            [cx - lw / 2, cy - r * 0.6, cx + lw / 2, cy - r * 0.6 + lh],
            radius=lh * 0.2, fill=(30, 20, 16)
        )


def draw_figure(img, draw, cx, base_y, scale, skin, helmet_color, hair_wisps=False, chin_strap=True):
    head_r = 95 * scale
    neck_w = 40 * scale
    shoulder_w = 300 * scale
    shoulder_h = 220 * scale
    shoulder_top = base_y - shoulder_h
    head_cy = shoulder_top - head_r * 0.75

    # shoulders / torso (rounded)
    draw.rounded_rectangle(
        [cx - shoulder_w / 2, shoulder_top, cx + shoulder_w / 2, base_y + 40 * scale],
        radius=shoulder_w * 0.28, fill=(40, 34, 46)
    )
    # harness straps (diagonal), matching the ropes-course gear in the photo
    strap_w = 22 * scale
    draw.line([(cx - shoulder_w * 0.28, base_y - shoulder_h * 0.9),
               (cx + shoulder_w * 0.05, base_y + 20 * scale)], fill=HARNESS_YELLOW, width=int(strap_w))
    draw.line([(cx + shoulder_w * 0.28, base_y - shoulder_h * 0.9),
               (cx - shoulder_w * 0.05, base_y + 20 * scale)], fill=HARNESS_YELLOW, width=int(strap_w))
    buckle_r = 20 * scale
    draw.ellipse([cx - buckle_r, base_y - shoulder_h * 0.35 - buckle_r,
                  cx + buckle_r, base_y - shoulder_h * 0.35 + buckle_r], fill=(60, 50, 40))

    # neck
    draw.rectangle([cx - neck_w / 2, head_cy + head_r * 0.6, cx + neck_w / 2, shoulder_top + 10 * scale],
                    fill=skin)

    # face
    draw.ellipse([cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r], fill=skin)

    if hair_wisps:
        for ang in range(-70, 71, 20):
            rad = math.radians(ang)
            x0 = cx + head_r * 0.95 * math.sin(rad)
            y0 = head_cy - head_r * 0.6 - head_r * 0.3 * math.cos(rad)
            x1 = cx + head_r * 1.35 * math.sin(rad)
            y1 = y0 - head_r * 0.55
            draw.line([(x0, y0), (x1, y1)], fill=HAIR_DARK, width=int(14 * scale))

    # blush
    br = head_r * 0.18
    draw.ellipse([cx - head_r * 0.62 - br, head_cy + head_r * 0.15 - br,
                  cx - head_r * 0.62 + br, head_cy + head_r * 0.15 + br], fill=BLUSH)
    draw.ellipse([cx + head_r * 0.62 - br, head_cy + head_r * 0.15 - br,
                  cx + head_r * 0.62 + br, head_cy + head_r * 0.15 + br], fill=BLUSH)

    # eyes (happy closed-arc eyes, since everyone's mid-laugh)
    eye_w, eye_h = head_r * 0.36, head_r * 0.3
    for sign in (-1, 1):
        ex = cx + sign * head_r * 0.42
        ey = head_cy - head_r * 0.08
        draw.arc([ex - eye_w / 2, ey - eye_h / 2, ex + eye_w / 2, ey + eye_h / 2],
                  start=200, end=340, fill=HAIR_DARK, width=int(9 * scale))

    # smile
    draw_smile(draw, cx, head_cy + head_r * 0.42, head_r * 0.9, head_r * 0.7)

    # helmet on top of head
    draw_helmet(draw, cx, head_cy - head_r * 0.95, head_r * 1.1, helmet_color)

    if chin_strap:
        draw.line([(cx - head_r * 0.55, head_cy + head_r * 0.15),
                   (cx, head_cy + head_r * 0.65)], fill=(30, 20, 16), width=int(8 * scale))
        draw.line([(cx + head_r * 0.55, head_cy + head_r * 0.15),
                   (cx, head_cy + head_r * 0.65)], fill=(30, 20, 16), width=int(8 * scale))


def main():
    img = Image.new("RGB", (W, H), BG_TOP)
    draw = ImageDraw.Draw(img)

    draw_background(img, draw)

    # smaller figure (front-left, red helmet) drawn first so the larger
    # figure overlaps in front of it, matching the photo's framing
    draw_figure(img, draw, cx=W * 0.30, base_y=H * 0.95, scale=1.5,
                skin=SKIN_B, helmet_color=HELMET_RED, hair_wisps=True)

    # larger figure (front-right, orange helmet)
    draw_figure(img, draw, cx=W * 0.70, base_y=H * 1.05, scale=2.0,
                skin=SKIN_A, helmet_color=HELMET_ORANGE, hair_wisps=False)

    img = img.filter(ImageFilter.SMOOTH_MORE)
    img.save(OUT_PATH, quality=92)
    print(f"Wrote {os.path.abspath(OUT_PATH)} ({img.width}x{img.height})")


if __name__ == "__main__":
    main()
