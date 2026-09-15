# AR Birthday Postcard

Zero-install WebAR birthday card: scan a QR code on a printed postcard, the
phone's own browser opens, tracks the front photo, and plays a video overlay
locked onto it.

```
/
├── index.html          # WebAR viewer (MindAR + A-Frame)
├── target-source.jpg   # your cartoon illustration (source art, see below)
├── video.mp4           # animation overlay (H.264 / AAC)
├── targets.mind         # compiled tracking file (generated, see step 3)
└── print/
    ├── build_postcard.py
    ├── fonts/           # drop free .ttf files here (optional but recommended)
    └── output/          # front.png, back.png, postcard_print.pdf, target.jpg
```

---

## 0. About the cartoon illustration

I can't turn your ropes-course photo into a cartoon directly — I don't have
an image-generation tool in this session. Two practical paths:

**A — AI-generate it (recommended for the real card).** Use any AI image
tool you have access to (ChatGPT/DALL·E, Midjourney, Ideogram, Claude.ai's
own image generation in a browser, etc.) and feed it your photo with a
prompt like:

> Turn this photo into a flat-color cartoon illustration in a vintage
> adventure-travel-poster style. Two people wearing orange Petzl climbing
> helmets and safety harnesses, big warm smiles, on an indoor ropes/zipline
> course with visible rigging, pulleys, and carabiners in the background.
> Bold outlines, warm retro palette (amber, coral, deep teal), soft
> directional lighting, slightly stylized proportions like a Pixar/travel-
> postcard poster. Square-ish composition, clean readable shapes, no text.

Keep the final export at a decent resolution (1800×1200 px or larger) so it
holds up at 300 DPI print.

**B — Use the placeholder pipeline now.** `build_postcard.py` runs fine
without real art (it drops in a solid-color block) so you can wire up and
test the entire AR pipeline — QR code, tracking, video overlay, print
layout — today, then swap in the real illustration as the very last step.
Whichever path you pick, drop the final artwork at `target-source.jpg` in
the project root before the final print run.

One tracking note: MindAR needs visual *detail* to lock onto — sharp edges,
varied color, texture (the polaroid frame, caption text, and illustration
line-work all help). A very flat, low-detail cartoon with huge single-color
areas will track worse than one with some linework/texture in it. If you
render option A, ask for "clean bold outlines and some background detail"
rather than fully flat vector shapes.

---

## 1. Assets checklist

| File | Requirement |
|---|---|
| `target-source.jpg` | The cartoon illustration, roughly landscape, reasonably detailed (see above) |
| `video.mp4` | H.264 video + AAC audio, **same aspect ratio as the printed front artwork**, ideally 10–20s, looping-friendly (starts/ends on a similar pose) |

Match the video's aspect ratio to the *printed* postcard photo area (the
polaroid photo window, not the raw source photo) — `build_postcard.py`
prints the exact final pixel dimensions each run so you can conform your
video export to them.

---

## 2. Build the postcard artwork

```bash
pip install pillow "qrcode[pil]"
```

Edit the `CONFIG` block at the top of [`print/build_postcard.py`](print/build_postcard.py):
cousin's name/age, the subtitle, and — once you know it (step 4) —
`AR_EXPERIENCE_URL`, the GitHub Pages link the QR code will point to.

Optionally drop free fonts into `print/fonts/` (Google Fonts: "Permanent
Marker" for the handwritten caption, "Special Elite" or "Courier Prime" for
the typewriter-style postcard text, "Anton" for the "POST CARD" title). The
script falls back to a plain system font and prints a warning if a font
file is missing — it still runs fine either way.

```bash
cd print
python build_postcard.py
```

This writes into `print/output/`:
- `front.png`, `back.png` — 300 DPI, ready to send to a print shop
- `postcard_print.pdf` — both sides as a single print-ready PDF
- `target.jpg` — **cropped straight from the rendered front artwork**, not
  the raw source photo. This matters: MindAR needs to train on the exact
  pixels that will physically exist on the printed card, frame and all, not
  a differently-cropped original. Copy this file to the project root.

The script also prints the exact pixel dimensions of `target.jpg`, e.g.:

```
window.TARGET_IMAGE_WIDTH_PX = 1800;
window.TARGET_IMAGE_HEIGHT_PX = 1200;
```

Copy those two numbers into the `<script>` config block near the top of
`index.html` — that's what keeps the video overlay's aspect ratio locked to
the real printed image instead of stretching.

---

## 3. Compile `targets.mind`

MindAR needs a compiled feature file, not the raw JPG. Use the official
browser-based compiler:

**https://hiukim.github.io/mind-ar-js-doc/tools/compile/**

1. Upload `target.jpg` (the one from `print/output/`, copied to the project root).
2. Wait for it to extract features — the tool shows which regions have
   strong trackable detail (a heatmap-style preview). If large areas show
   weak features, that's the flat-color warning from step 0 — add more
   detail/contrast to the artwork and re-export.
3. Download the resulting `targets.mind` and place it next to `index.html`.

---

## 4. Local testing

Camera access requires a secure context, but `localhost` counts as one, so
plain local testing works without HTTPS:

```bash
cd /path/to/ar-birthday-postcard
python -m http.server 8080
```

Open `http://localhost:8080` in desktop Chrome, allow the camera, and hold
up `target.jpg` on a second screen or your phone to test tracking and video
playback. This confirms wiring before you involve a real phone camera.

To test on your **actual phone** before deploying, either:
- Deploy to GitHub Pages first (step 5) and iterate from there — simplest, and
- Or tunnel your local server over HTTPS (e.g. with a tool like ngrok) if you want a faster local iteration loop on-device.

### What to check
- [ ] "Tap to Start" overlay appears, camera permission prompt shows once you tap
- [ ] After tapping, pointing the camera at a printed (or on-screen) copy of
      `target.jpg` locks the video on top of it within a second or two
- [ ] The video overlay's edges line up with the photo's edges (no
      stretching/offset) — if not, double check `TARGET_IMAGE_WIDTH_PX` /
      `HEIGHT_PX` match `target.jpg` exactly
- [ ] Audio plays on the first lock (iOS Safari and Android Chrome both) —
      this is what the tap-to-start audio unlock in `index.html` is for
- [ ] Moving the camera away and back re-triggers the video (pause on
      `targetLost`, resume on `targetFound`)
- [ ] Test under the lighting you'll actually gift it in — dim/uneven light
      hurts feature tracking more than most other variables

---

## 5. Deploy to GitHub Pages

```bash
cd /path/to/ar-birthday-postcard
git init
git add index.html targets.mind video.mp4 target.jpg
git commit -m "AR birthday postcard"
gh repo create ar-birthday-postcard --public --source=. --push
```

Then in the repo's GitHub Settings → Pages, set the source to the `main`
branch, root folder. GitHub gives you a URL like:

```
https://YOUR-GITHUB-USERNAME.github.io/ar-birthday-postcard/
```

GitHub Pages serves everything over HTTPS automatically, satisfying the
secure-context requirement for camera access on a real phone.

Put that exact URL into `AR_EXPERIENCE_URL` in `build_postcard.py`, then
re-run the script so the printed QR code points at the live page:

```bash
cd print
python build_postcard.py
```

---

## 6. Final print run

1. Re-run `build_postcard.py` once `target-source.jpg` is the real
   cartoon illustration and `AR_EXPERIENCE_URL` is the live Pages link.
2. Re-compile `targets.mind` from the new `print/output/target.jpg` (step 3)
   — the tracking image must match whatever actually gets printed.
3. Send `print/output/postcard_print.pdf` to a print shop as a standard
   4×6" postcard, matte or semi-gloss finish (avoid high-gloss — glare on
   glossy stock can hurt phone-camera tracking).
4. Do one more end-to-end test scanning the **actual printed card** before
   gifting it — printed color/contrast always shifts slightly from the
   on-screen render, and that's what the phone will actually see.
