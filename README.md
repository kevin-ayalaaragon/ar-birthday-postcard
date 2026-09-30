# AR Birthday Postcard

[![CI](https://github.com/kevin-ayalaaragon/ar-birthday-postcard/actions/workflows/ci.yml/badge.svg)](https://github.com/kevin-ayalaaragon/ar-birthday-postcard/actions/workflows/ci.yml)

Zero-install WebAR birthday card: scan a QR code on a printed postcard, the
phone's own browser opens, tracks the front photo, and plays a video overlay
locked onto it. No app install, no account, camera access is the only
permission asked for.

**Repo:** https://github.com/kevin-ayalaaragon/ar-birthday-postcard
**Live Pages URL:** https://kevin-ayalaaragon.github.io/ar-birthday-postcard/

This repo covers the technical/AR side only. Postcard print design (front
layout, back mailing lines, QR code placement, fonts, etc.) is being handled
separately, outside this repo.

```
/
├── index.html          # WebAR viewer shell (MindAR + A-Frame)
├── js/
│   ├── config.js        # target.jpg pixel dimensions (see "Asset pipeline")
│   └── app.js            # tap-to-start, camera-error recovery, AR event wiring
├── target.jpg           # cartoon artwork - the exact image compiled into targets.mind
├── targets.mind         # compiled MindAR tracking data, generated from target.jpg
├── video.mp4            # animation overlay (H.264 / AAC)
├── generate_qr.py       # print-safe QR generator with round-trip scan verification
├── tests/smoke.spec.js  # Playwright: CSP compliance, asset reachability, camera->AR startup
└── .github/workflows/ci.yml
```

## How it works

1. **Print-time**: `target.jpg` (the postcard's front photo) is compiled into
   `targets.mind` - a set of trackable feature points MindAR extracts at
   several image scales, offline, via its
   [web compiler](https://hiukim.github.io/mind-ar-js-doc/tools/compile/).
   MindAR's own detection/tracking algorithm is a custom, GPU-accelerated
   reimplementation of the [ARToolKit](https://github.com/artoolkitx/artoolkit5)
   approach, written as custom operations on top of TensorFlow.js's WebGL
   backend - it uses that library purely for GPU compute, not for a trained
   ML model (its own README is explicit about this).
2. **Scan-time**: the phone camera's live feed is matched against those
   feature points every frame. Once enough of them line up, MindAR solves a
   homography to recover the target's position/orientation and hands
   A-Frame a 6DoF pose each frame - the actual "AR" part: a virtual plane
   locked in 3D space that only appears to move because the camera does.
3. **Render**: A-Frame parents a video plane to that pose. The plane's
   aspect ratio is set at runtime (`js/app.js`) from `target.jpg`'s exact
   pixel dimensions, not the video file's own dimensions - otherwise the
   overlay drifts from the printed photo's edges by whatever the two
   aspect ratios differ by.
4. **Loss/recovery**: `targetFound`/`targetLost` events drive
   play/pause; there's no manual RAF loop or pose smoothing code here, that's
   internal to MindAR's tracker.

## Security & privacy

- **No data collection.** No analytics, no cookies, no backend - the entire
  app is static files served from GitHub Pages. Camera frames are processed
  client-side by MindAR/WebGL and never leave the device.
- **Subresource Integrity.** Both third-party scripts (A-Frame, MindAR) are
  loaded with SRI hashes pinned to the exact version in use, so a compromised
  or MITM'd CDN response gets rejected by the browser instead of executed.
- **Content-Security-Policy**, set via `<meta>` since GitHub Pages can't
  serve custom HTTP headers: restricts script execution to this origin plus
  the two pinned CDN origins, disallows `object-src`, and scopes
  `img-src`/`media-src`/`connect-src` to `self` + `blob:` (MindAR's tracker
  runs in a blob-sourced Web Worker). `unsafe-eval` is required in
  `script-src` because A-Frame's own attribute-schema parser uses
  `new Function()` internally - documented in `index.html`, not silently
  weakened. `frame-ancestors` can't be enforced from this host at all (not
  expressible via `<meta>`, and GitHub Pages won't set it as a header
  either) - a known, documented gap rather than an oversight.

## Asset pipeline

Target aspect ratio is **~9:16 portrait**. Current `target.jpg` is
**768×1376px** (ratio 0.558 - close to but not exactly 9:16/0.5625, from how
the artwork was exported). `js/config.js`'s `TARGET_IMAGE_WIDTH_PX`/
`HEIGHT_PX` **must match `target.jpg`'s exact pixel dimensions**, since the
video plane's aspect ratio is derived from them at runtime. (These were
briefly out of sync with the actual file after an art swap - see
[js/config.js](js/config.js) for the specifics of that fix.)

If any asset changes:
- **New `target.jpg`**: recompile `targets.mind` from it (MindAR's web
  compiler: https://hiukim.github.io/mind-ar-js-doc/tools/compile/), and
  update `TARGET_IMAGE_WIDTH_PX`/`HEIGHT_PX` in `js/config.js` to its exact
  pixel dimensions.
- **New `video.mp4`**: must be H.264 + AAC. It's stretched to match
  `target.jpg`'s aspect ratio at runtime, so it doesn't need to match exactly,
  but large differences will visibly distort it.
- **New CDN version of A-Frame or MindAR**: the SRI hash in `index.html`
  is pinned to that exact file's contents - bumping the version without
  recomputing the hash will make the browser refuse to run the script.

## CI

`.github/workflows/ci.yml` runs on every push:
- **HTML lint** (`html-validate`).
- **Browser smoke test** (`tests/smoke.spec.js`, Playwright + headless
  Chromium): loads the page and asserts zero console errors (catches CSP
  regressions), checks `js/config.js`/`js/app.js`/`targets.mind`/`video.mp4`
  all resolve, and - using Chromium's fake-camera-device flag - taps
  "Start", grants a synthetic camera stream, and asserts MindAR actually
  initializes without tripping the error-recovery overlay. It does not (and
  can't, without a printed target) assert that tracking locks on.

```bash
npm install
npx playwright install --with-deps chromium
npm run lint:html
npx playwright test
```

## Local testing

Camera access needs a secure context, but `localhost` counts as one:

```bash
npm install
npm run serve
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
