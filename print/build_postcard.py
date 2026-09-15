"""
Assemble a print-ready 4x6" AR birthday postcard (front + back) at 300 DPI.

Outputs (into ./output/):
  front.png            - print-ready front artwork (postcard face + polaroid frame)
  back.png             - print-ready back artwork (mailing lines + stamp + QR code)
  postcard_print.pdf   - both pages combined, sized correctly for a print shop
  target.jpg           - the EXACT image to feed into the MindAR image compiler
                         (cropped straight from the rendered front artwork, so the
                         AR tracker is trained on the very pixels that end up printed)

Dependencies:
    pip install pillow qrcode[pil]

Fonts:
  Drop free .ttf fonts into ./fonts/ and point the CONFIG block at them for a
  much nicer look than the built-in bitmap font. Good free picks (Google Fonts):
    - Handwritten caption : "Permanent Marker" or "Caveat"
    - Postcard title/body : "Special Elite" or "Courier Prime" (typewriter look)
  If a font file isn't found, the script falls back to PIL's default font and
  prints a warning instead of crashing.
"""

import os
import math
import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

# --------------------------------------------------------------------------
# CONFIG - edit these for your card
# --------------------------------------------------------------------------

COUSIN_NAME = "Mia"
COUSIN_AGE = 12
POSTCARD_SUBTITLE = "Ropes Course Adventure"

# The published GitHub Pages URL that the QR code will point to.
# (Set this AFTER you've deployed - see the README for the deploy steps.)
AR_EXPERIENCE_URL = "https://kevin-ayalaaragon.github.io/ar-birthday-postcard/"

# Source cartoon illustration (front artwork photo). This should already be
# roughly the right aspect ratio for the polaroid photo window below.
SOURCE_IMAGE_PATH = "../target-source.jpg"

OUTPUT_DIR = "output"

FONT_DIR = "fonts"
FONT_SCRIPT = os.path.join(FONT_DIR, "PermanentMarker-Regular.ttf")   # caption
FONT_TYPEWRITER = os.path.join(FONT_DIR, "SpecialElite-Regular.ttf")  # postcard text
FONT_BOLD = os.path.join(FONT_DIR, "Anton-Regular.ttf")               # POST CARD title

DPI = 300
CARD_W_IN, CARD_H_IN = 6, 4          # landscape 4x6 postcard
CARD_W_PX, CARD_H_PX = CARD_W_IN * DPI, CARD_H_IN * DPI

CREAM = (244, 236, 216)
INK = (40, 28, 20)
ADVENTURE_ORANGE = (255, 122, 45)
LINE_GRAY = (150, 140, 120)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def load_font(path, size):
    if os.path.isfile(path):
        return ImageFont.truetype(path, size)
    print(f"[warn] font not found: {path} -- falling back to default font. "
          f"See the module docstring for where to download it.")
    try:
        # Pillow >= 10.1 lets the built-in bitmap font scale to a size.
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def fit_cover(img, target_w, target_h):
    """Resize+crop `img` to exactly fill target_w x target_h (like CSS object-fit: cover)."""
    src_ratio = img.width / img.height
    dst_ratio = target_w / target_h
    if src_ratio > dst_ratio:
        new_h = target_h
        new_w = int(new_h * src_ratio)
    else:
        new_w = target_w
        new_h = int(new_w / src_ratio)
    resized = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def fit_contain(img, max_w, max_h):
    """
    Resize `img` to fit entirely within max_w x max_h, preserving aspect
    ratio and cropping nothing (like CSS object-fit: contain). We use this
    instead of fit_cover for the printed photo: the MindAR target image is
    compiled from the raw source art, so whatever gets printed must show
    that art unmodified (aside from a uniform scale) or the physically
    printed card will diverge from what was trained for tracking.
    """
    scale = min(max_w / img.width, max_h / img.height)
    new_w, new_h = int(img.width * scale), int(img.height * scale)
    return img.resize((new_w, new_h), Image.LANCZOS)


def draw_curved_text(base_img, text, center, radius, font, fill, start_deg, end_deg):
    """Draw `text` along an arc from start_deg to end_deg (0deg = up, clockwise)."""
    n = len(text)
    if n == 0:
        return
    span = end_deg - start_deg
    step = span / max(n - 1, 1)
    for i, ch in enumerate(text):
        angle_deg = start_deg + step * i
        angle_rad = math.radians(angle_deg)
        x = center[0] + radius * math.sin(angle_rad)
        y = center[1] - radius * math.cos(angle_rad)

        glyph = Image.new("RGBA", (font.size * 2, font.size * 2), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glyph)
        gd.text((font.size, font.size), ch, font=font, fill=fill, anchor="mm")
        glyph = glyph.rotate(-angle_deg, resample=Image.BICUBIC, center=(font.size, font.size))

        base_img.alpha_composite(
            glyph, (int(x - font.size), int(y - font.size))
        )


def draw_perforated_stamp(draw, box, fill=(255, 250, 240), notch_r=6, notch_gap=18):
    """Draw a rectangle with a scalloped/perforated stamp edge."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=fill, outline=INK, width=2)
    for x in range(x0, x1 + 1, notch_gap):
        draw.ellipse([x - notch_r, y0 - notch_r, x + notch_r, y0 + notch_r], fill=CREAM)
        draw.ellipse([x - notch_r, y1 - notch_r, x + notch_r, y1 + notch_r], fill=CREAM)
    for y in range(y0, y1 + 1, notch_gap):
        draw.ellipse([x0 - notch_r, y - notch_r, x0 + notch_r, y + notch_r], fill=CREAM)
        draw.ellipse([x1 - notch_r, y - notch_r, x1 + notch_r, y + notch_r], fill=CREAM)


# --------------------------------------------------------------------------
# Front
# --------------------------------------------------------------------------

def build_front():
    canvas = Image.new("RGB", (CARD_W_PX, CARD_H_PX), CREAM)
    draw = ImageDraw.Draw(canvas)

    margin = int(0.28 * DPI)
    polaroid_w = CARD_W_PX - 2 * margin
    polaroid_h = CARD_H_PX - 2 * margin
    px0, py0 = margin, margin
    px1, py1 = px0 + polaroid_w, py0 + polaroid_h

    # drop shadow
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    offset = int(0.05 * DPI)
    sd.rectangle([px0 + offset, py0 + offset, px1 + offset, py1 + offset], fill=(0, 0, 0, 90))
    shadow = shadow.filter(ImageFilter.GaussianBlur(offset))
    canvas.paste(Image.alpha_composite(Image.new("RGBA", canvas.size, (0, 0, 0, 0)), shadow), (0, 0), shadow)

    # white polaroid body
    draw.rectangle([px0, py0, px1, py1], fill=(255, 255, 255))

    # photo window (leave extra white space at the bottom for the caption,
    # like a real polaroid)
    photo_pad = int(0.12 * DPI)
    caption_h = int(0.75 * DPI)
    photo_box = (px0 + photo_pad, py0 + photo_pad, px1 - photo_pad, py1 - caption_h)
    pw = photo_box[2] - photo_box[0]
    ph = photo_box[3] - photo_box[1]

    if os.path.isfile(SOURCE_IMAGE_PATH):
        art = Image.open(SOURCE_IMAGE_PATH).convert("RGB")
        art = ImageOps.exif_transpose(art)
        # contain-fit, not cover-crop: the MindAR target is compiled from this
        # exact source image, so the print must show it whole (just scaled),
        # never cropped, or the tracked pixels stop matching the printed ones.
        art = fit_contain(art, pw, ph)
    else:
        print(f"[warn] source image not found: {SOURCE_IMAGE_PATH} -- using a placeholder block.")
        art = Image.new("RGB", (pw, ph), (255, 200, 150))

    # center the (possibly letterboxed) art inside the photo window
    art_x = photo_box[0] + (pw - art.width) // 2
    art_y = photo_box[1] + (ph - art.height) // 2
    canvas.paste(art, (art_x, art_y))
    draw.rectangle([art_x, art_y, art_x + art.width, art_y + art.height], outline=INK, width=3)

    # caption
    script_font = load_font(FONT_SCRIPT, int(0.42 * DPI))
    sub_font = load_font(FONT_TYPEWRITER, int(0.16 * DPI))
    caption_cx = (px0 + px1) // 2
    caption_cy = py1 - caption_h // 2 - int(0.05 * DPI)
    draw.text((caption_cx, caption_cy), f"Happy {COUSIN_AGE}th Birthday, {COUSIN_NAME}!",
              font=script_font, fill=ADVENTURE_ORANGE, anchor="mm")
    draw.text((caption_cx, caption_cy + int(0.32 * DPI)), POSTCARD_SUBTITLE.upper(),
              font=sub_font, fill=INK, anchor="mm")

    return canvas


# --------------------------------------------------------------------------
# Back
# --------------------------------------------------------------------------

def build_back():
    canvas = Image.new("RGB", (CARD_W_PX, CARD_H_PX), (255, 255, 250)).convert("RGBA")
    draw = ImageDraw.Draw(canvas)
    margin = int(0.3 * DPI)

    title_font = load_font(FONT_BOLD, int(0.34 * DPI))
    body_font = load_font(FONT_TYPEWRITER, int(0.15 * DPI))
    small_font = load_font(FONT_TYPEWRITER, int(0.12 * DPI))

    # "POST CARD" header
    draw.text((margin, margin - int(0.05 * DPI)), "POST CARD", font=title_font, fill=INK)

    # center divider
    mid_x = CARD_W_PX // 2 + int(0.2 * DPI)
    draw.line([(mid_x, margin + int(0.55 * DPI)), (mid_x, CARD_H_PX - margin)],
              fill=LINE_GRAY, width=2)

    # message lines (left side)
    line_y_start = margin + int(0.75 * DPI)
    line_gap = int(0.32 * DPI)
    for i in range(4):
        y = line_y_start + i * line_gap
        draw.line([(margin, y), (mid_x - int(0.25 * DPI), y)], fill=LINE_GRAY, width=2)

    # address lines (right side, below the stamp/instructions block)
    addr_y_start = CARD_H_PX - margin - int(0.9 * DPI)
    for i in range(3):
        y = addr_y_start + i * line_gap
        draw.line([(mid_x + int(0.2 * DPI), y), (CARD_W_PX - margin, y)], fill=LINE_GRAY, width=2)
    draw.text((mid_x + int(0.2 * DPI), addr_y_start - int(0.28 * DPI)), "To:",
              font=body_font, fill=INK)

    # --- stamp (top right) ---
    stamp_w, stamp_h = int(1.0 * DPI), int(1.2 * DPI)
    stamp_box = (CARD_W_PX - margin - stamp_w, margin, CARD_W_PX - margin, margin + stamp_h)
    draw_perforated_stamp(draw, stamp_box)
    icon_font = load_font(FONT_BOLD, int(0.5 * DPI))
    stamp_cx = (stamp_box[0] + stamp_box[2]) // 2
    stamp_cy = (stamp_box[1] + stamp_box[3]) // 2
    draw.text((stamp_cx, stamp_cy), "AR", font=icon_font, fill=ADVENTURE_ORANGE, anchor="mm")

    # --- circular cancellation postmark, overlapping the stamp ---
    postmark_r = int(0.5 * DPI)
    postmark_cx = stamp_box[0] - int(0.32 * DPI)
    postmark_cy = stamp_box[3] - int(0.05 * DPI)
    draw.ellipse(
        [postmark_cx - postmark_r, postmark_cy - postmark_r,
         postmark_cx + postmark_r, postmark_cy + postmark_r],
        outline=ADVENTURE_ORANGE, width=6
    )
    draw.ellipse(
        [postmark_cx - postmark_r + 14, postmark_cy - postmark_r + 14,
         postmark_cx + postmark_r - 14, postmark_cy + postmark_r - 14],
        outline=ADVENTURE_ORANGE, width=3
    )
    for angle in range(0, 360, 20):
        rad = math.radians(angle)
        x0 = postmark_cx + (postmark_r - 20) * math.cos(rad)
        y0 = postmark_cy + (postmark_r - 20) * math.sin(rad)
        x1 = postmark_cx + (postmark_r - 40) * math.cos(rad)
        y1 = postmark_cy + (postmark_r - 40) * math.sin(rad)
        draw.line([(x0, y0), (x1, y1)], fill=ADVENTURE_ORANGE, width=2)

    arc_font = load_font(FONT_TYPEWRITER, int(0.11 * DPI))
    draw_curved_text(canvas, "SCAN TO ANIMATE", (postmark_cx, postmark_cy), postmark_r - 55,
                      arc_font, ADVENTURE_ORANGE + (255,), start_deg=-95, end_deg=95)

    # --- QR code + instructions (bottom left, in the message column) ---
    qr_size = int(0.95 * DPI)
    qr_img = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=2
    )
    qr_img.add_data(AR_EXPERIENCE_URL)
    qr_img.make(fit=True)
    qr_pil = qr_img.make_image(fill_color=INK, back_color="white").convert("RGB")
    qr_pil = qr_pil.resize((qr_size, qr_size), Image.NEAREST)

    qr_x = margin
    qr_y = CARD_H_PX - margin - qr_size
    canvas.paste(qr_pil, (qr_x, qr_y))
    draw.rectangle([qr_x, qr_y, qr_x + qr_size, qr_y + qr_size], outline=INK, width=2)

    instr_x = qr_x + qr_size + int(0.2 * DPI)
    instr_y = qr_y
    instructions = [
        "Scan with your phone",
        "camera to bring this",
        "picture to life!",
    ]
    for i, line in enumerate(instructions):
        draw.text((instr_x, instr_y + i * int(0.22 * DPI)), line, font=small_font, fill=INK)

    return canvas.convert("RGB")


# --------------------------------------------------------------------------
# AR target image - an exact copy of the raw source art
# --------------------------------------------------------------------------

def build_target_image():
    """
    Return the source art untouched (aside from an EXIF-orientation fix).
    If you've already compiled targets.mind from target-source.jpg directly
    (e.g. via MindAR's web compiler), the printed target image must stay
    byte-for-byte the same content - a crop, letterbox, or even a re-encode
    can shift or soften the very features MindAR trained on. The front
    artwork uses fit_contain (see build_front) for exactly this reason: the
    art appears on the printed card unmodified, just uniformly scaled.
    """
    art = Image.open(SOURCE_IMAGE_PATH).convert("RGB")
    return ImageOps.exif_transpose(art)


# --------------------------------------------------------------------------

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    front = build_front()
    back = build_back()

    front_path = os.path.join(OUTPUT_DIR, "front.png")
    back_path = os.path.join(OUTPUT_DIR, "back.png")
    pdf_path = os.path.join(OUTPUT_DIR, "postcard_print.pdf")
    target_path = os.path.join(OUTPUT_DIR, "target.jpg")

    front.save(front_path, dpi=(DPI, DPI))
    back.save(back_path, dpi=(DPI, DPI))
    front.save(pdf_path, save_all=True, append_images=[back], resolution=float(DPI))

    print("\nDone:")
    print(f"  {front_path}")
    print(f"  {back_path}")
    print(f"  {pdf_path}")

    if os.path.isfile(SOURCE_IMAGE_PATH):
        target = build_target_image()
        target.save(target_path, quality=95)
        print(f"  {target_path}")
        print(f"\nTarget image is {target.width}x{target.height}px.")
        print("Set these in index.html to match exactly:")
        print(f"  window.TARGET_IMAGE_WIDTH_PX = {target.width};")
        print(f"  window.TARGET_IMAGE_HEIGHT_PX = {target.height};")
        print("\nIf targets.mind was already compiled from target-source.jpg directly,")
        print("you're done - no need to recompile. Otherwise, run target.jpg through the")
        print("MindAR image compiler to produce targets.mind (see README.md).")
    else:
        print(f"\n[warn] {SOURCE_IMAGE_PATH} not found -- skipped target.jpg.")


if __name__ == "__main__":
    main()
