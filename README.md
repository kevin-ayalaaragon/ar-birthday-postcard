# AR Birthday Postcard

Zero-install WebAR birthday card: scan a QR code on a printed postcard, the
phone's own browser opens, tracks the front photo, and plays a video overlay
locked onto it.

**Repo:** https://github.com/kevin-ayalaaragon/ar-birthday-postcard
**Live Pages URL:** https://kevin-ayalaaragon.github.io/ar-birthday-postcard/

This repo covers the technical/AR side only. Postcard print design (front
layout, back mailing lines, QR code placement, fonts, etc.) is being handled
separately, outside this repo.

```
/
├── index.html     # WebAR viewer (MindAR + A-Frame)
├── target.jpg     # cartoon artwork - the exact image compiled into targets.mind
├── targets.mind   # compiled MindAR tracking data, generated from target.jpg
└── video.mp4      # animation overlay (H.264 / AAC)
```

## Current asset status

Target aspect ratio is now **9:16 portrait (1080x1920)**, changed from an
earlier 3:4 version.

| File | Status |
|---|---|
| `target.jpg` | ⚠️ stale - still the old 768x1024 (3:4) cartoon. Needs replacing with the new 1080x1920 (or any exact-9:16) artwork. |
| `targets.mind` | ⚠️ stale - compiled from the old 3:4 `target.jpg`. Must be recompiled once the new `target.jpg` is in place. |
| `video.mp4` | ✅ already 720x1280, which is exactly 9:16 - **no re-export needed**, this file already matches the new target ratio. |
| `index.html` | ✅ `TARGET_IMAGE_WIDTH_PX`/`HEIGHT_PX` already updated to 1080/1920 |

Once the new `target.jpg` lands: replace the file, recompile `targets.mind`
from it, and if its exact pixel dimensions aren't precisely 1080x1920,
update `TARGET_IMAGE_WIDTH_PX`/`HEIGHT_PX` in `index.html` to match exactly.

## If any asset changes

- **New `target.jpg`**: recompile `targets.mind` from it (MindAR's web
  compiler: https://hiukim.github.io/mind-ar-js-doc/tools/compile/), and
  update `TARGET_IMAGE_WIDTH_PX`/`HEIGHT_PX` in `index.html` to its exact
  pixel dimensions.
- **New `video.mp4`**: must be H.264 + AAC, and match `target.jpg`'s aspect
  ratio exactly (otherwise the overlay stretches/squishes relative to the
  printed photo).

## Local testing

Camera access needs a secure context, but `localhost` counts as one:

```bash
python -m http.server 8080
```

Open `http://localhost:8080` in desktop Chrome, allow the camera, and point
it at `target.jpg` (on a second screen or printed) to test tracking and
video playback before testing on an actual phone / the printed card.

### What to check
- [ ] "Tap to Start" overlay appears, camera permission prompt shows once tapped
- [ ] Pointing the camera at the target image locks the video overlay within a second or two
- [ ] The video's edges line up with the photo's edges (no stretching/offset)
- [ ] Audio plays on first lock, on both iOS Safari and Android Chrome
- [ ] Moving the camera away and back re-triggers the video
- [ ] Test under the lighting the card will actually be viewed in

## Deploy

Already deployed via GitHub Pages (`master` branch, root). Any push to
`master` updates the live site automatically:

```bash
git add -A
git commit -m "..."
git push
```
