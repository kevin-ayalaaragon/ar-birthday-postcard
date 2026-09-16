"""
Generate a print-safe QR code for the AR postcard, then round-trip decode
it to verify it actually scans back to the right URL before it goes
anywhere near a print shop.

Usage:
    pip install "qrcode[pil]" pyzbar
    python generate_qr.py
Writes qr-code.png (not used by index.html - this is a standalone asset
for whoever is doing the print/postcard design).
"""

import qrcode
from PIL import Image
from pyzbar.pyzbar import decode as decode_qr

URL = "https://kevin-ayalaaragon.github.io/ar-birthday-postcard/"
OUT_PATH = "qr-code.png"

# --- Best-practice settings for a printed, camera-scanned QR code ---
#
# - ERROR_CORRECT_H (~30% recovery): the postcard back may have other art,
#   a stamp/postmark graphic, folds, or print wear near the code. High
#   error correction survives partial damage/obstruction; L/M/Q don't.
# - border=4: the QR spec's minimum "quiet zone" is 4 modules of clear
#   space around the code. Less than this measurably hurts scan reliability
#   across real-world scanner/camera apps. Never crop this away.
# - box_size=20: each QR "module" (the smallest square unit) is rendered at
#   20x20px, so edges stay crisp at print resolution instead of needing to
#   be upscaled and blurred later.
# - Pure black-on-white: maximum contrast. Avoid tinting/coloring a QR code
#   for a print piece meant to be reliably scanned by an unknown range of
#   phones/lighting - contrast is what scanners actually key off.
qr = qrcode.QRCode(
    version=None,  # auto-select the smallest version that fits the data
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=20,
    border=4,
)
qr.add_data(URL)
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
img.save(OUT_PATH)  # PNG: lossless, no JPEG compression artifacts on the sharp edges
print(f"Wrote {OUT_PATH} ({img.width}x{img.height}px, QR version {qr.version})")

# --- Round-trip verification: decode it back and confirm it matches ---
results = decode_qr(Image.open(OUT_PATH))
decoded_text = results[0].data.decode("utf-8") if results else None

if decoded_text == URL:
    print(f"VERIFIED: decodes back to the exact correct URL:\n  {decoded_text}")
else:
    print(f"MISMATCH! decoded: {decoded_text!r}  expected: {URL!r}")
    raise SystemExit(1)
