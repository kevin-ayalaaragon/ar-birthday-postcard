// CONFIG: set this to the pixel dimensions of target.jpg (the exact file you
// compiled into targets.mind). MindAR maps the target's WIDTH to 1 scene unit,
// so the video plane's height must be (targetImageHeight / targetImageWidth)
// or the overlay will look stretched/squashed relative to the printed card.
//
// Was left at the planned 1080x1920 after the airmail-art swap (commit
// 2570eb9) even though that art landed at 768x1376 (ratio 0.558 vs the
// planned 9:16's 0.5625) - a ~0.8% plane/photo mismatch the commit message
// flagged as "pending a test pass" and never resolved. Corrected to the
// actual file's pixel dimensions.
window.TARGET_IMAGE_WIDTH_PX = 768;   // target.jpg is 768x1376
window.TARGET_IMAGE_HEIGHT_PX = 1376;
