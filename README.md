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

| File | Status |
|---|---|
| `target.jpg` | 768x1024 (3:4 portrait) cartoon, in place |
| `targets.mind` | compiled from this exact `target.jpg`, in place |
| `video.mp4` | ⚠️ currently 720x1280 (9:16) - doesn't match `target.jpg`'s 3:4 aspect ratio. Needs a re-export at 3:4 portrait (e.g. 768x1024 or 1080x1440) or the video will look stretched over the tracked image. |
| `index.html` | `TARGET_IMAGE_WIDTH_PX`/`HEIGHT_PX` already set to 768/1024 to match `target.jpg` |

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
