(function () {
  const startOverlay = document.getElementById('start-overlay');
  const startBtn = document.getElementById('start-btn');
  const errorOverlay = document.getElementById('error-overlay');
  const errorTitle = document.getElementById('error-title');
  const errorMessage = document.getElementById('error-message');
  const errorRetryBtn = document.getElementById('error-retry-btn');
  const sceneEl = document.getElementById('ar-scene');
  const videoEl = document.getElementById('ar-video');
  const videoPlane = document.getElementById('ar-video-plane');
  const anchor = document.getElementById('target-anchor');

  // MindAR's own "arError" event only ever carries {error: "VIDEO_FAIL"} for
  // every getUserMedia failure, whether it's a denied permission, no camera,
  // or the camera being busy in another app - it doesn't forward the actual
  // error. Wrap getUserMedia ourselves so we can see the real DOMException
  // and give a message people can actually act on.
  let lastCameraError = null;
  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    const originalGetUserMedia = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
    navigator.mediaDevices.getUserMedia = function (constraints) {
      return originalGetUserMedia(constraints).catch((err) => {
        lastCameraError = err;
        throw err;
      });
    };
  }

  const isIOS = /iPhone|iPad|iPod/.test(navigator.userAgent);

  function describeCameraError(err) {
    const name = err && err.name;
    if (name === 'NotAllowedError' || name === 'PermissionDeniedError') {
      return {
        title: 'Camera permission is blocked',
        message: isIOS
          ? 'Go to Settings → Safari → Camera, and allow access for this site (or Settings → Safari → Advanced → Website Data, remove this site, then reload).'
          : 'Tap the lock icon next to the address bar → Permissions → Camera, and switch it to Allow.',
      };
    }
    if (name === 'NotFoundError' || name === 'DevicesNotFoundError') {
      return { title: 'No camera found', message: 'This device doesn’t have a usable camera, or it isn’t accessible right now.' };
    }
    if (name === 'NotReadableError' || name === 'TrackStartError') {
      return { title: 'Camera is busy', message: 'Another app may be using the camera. Close other camera apps and try again.' };
    }
    return {
      title: 'Camera access is needed',
      message: 'Please allow camera permission for this site in your browser settings, then try again.',
    };
  }

  function showCameraError() {
    const { title, message } = describeCameraError(lastCameraError);
    errorTitle.textContent = title;
    errorMessage.textContent = message;
    errorOverlay.classList.add('visible');
  }

  // Purely decorative, purely DOM/CSS - runs on the 2D overlay layer above
  // the AR canvas, never touches WebGL/MindAR, and never blocks start().
  const CONFETTI_COLORS = ['#ff8a3d', '#ffcf4d', '#ff5f6d', '#6de3c0', '#8ab4ff'];
  const confettiContainer = document.getElementById('confetti-container');

  function launchConfetti() {
    const frag = document.createDocumentFragment();
    const pieceCount = 60;
    let maxLifetime = 0;

    for (let i = 0; i < pieceCount; i++) {
      const piece = document.createElement('div');
      piece.className = 'confetti-piece';
      const duration = 1.6 + Math.random() * 1.2;
      const delay = Math.random() * 0.35;
      piece.style.left = (Math.random() * 100) + 'vw';
      piece.style.background = CONFETTI_COLORS[i % CONFETTI_COLORS.length];
      piece.style.transform = `rotate(${Math.random() * 360}deg)`;
      piece.style.animationDuration = duration + 's';
      piece.style.animationDelay = delay + 's';
      maxLifetime = Math.max(maxLifetime, duration + delay);
      frag.appendChild(piece);
    }

    confettiContainer.appendChild(frag);
    // Cleanup once every piece has finished, so nothing lingers in the DOM.
    setTimeout(() => { confettiContainer.innerHTML = ''; }, maxLifetime * 1000 + 200);
  }

  // Size the video plane to match the target image's aspect ratio so the
  // overlay lines up exactly with the printed postcard, regardless of the
  // video file's own pixel dimensions.
  const targetW = window.TARGET_IMAGE_WIDTH_PX || 1;
  const targetH = window.TARGET_IMAGE_HEIGHT_PX || 1;
  videoPlane.setAttribute('width', 1);
  videoPlane.setAttribute('height', targetH / targetW);

  let started = false;
  let audioUnlocked = false;

  function unlockAudioThenStop() {
    if (audioUnlocked) return;
    videoEl.muted = false;
    const p = videoEl.play();
    if (p && p.catch) {
      p.then(() => {
        videoEl.pause();
        videoEl.currentTime = 0;
        audioUnlocked = true;
      }).catch(() => {
        // Fall back to muted playback if the browser still blocks sound.
        videoEl.muted = true;
        videoEl.play().then(() => {
          videoEl.pause();
          videoEl.currentTime = 0;
          audioUnlocked = true;
        }).catch(() => {});
      });
    } else {
      audioUnlocked = true;
    }
  }

  async function start() {
    if (started) return;
    started = true;

    // Must run inside the tap gesture so iOS Safari allows audio playback
    // for every later programmatic videoEl.play() call. Also re-runs safely
    // on a "Try Again" retry - unlockAudioThenStop() is a no-op once
    // audioUnlocked is already true.
    unlockAudioThenStop();

    startOverlay.classList.add('hidden');
    errorOverlay.classList.remove('visible');

    try {
      const arSystem = sceneEl.systems['mindar-image-system'];
      await arSystem.start();
    } catch (err) {
      // MindAR's VIDEO_FAIL path doesn't actually throw here (it emits
      // "arError" and returns normally - see the listener below), but keep
      // this as a fallback for any other startup exception.
      console.error('MindAR failed to start', err);
      started = false;
      showCameraError();
    }
  }

  startBtn.addEventListener('click', () => {
    launchConfetti();
    start();
  });

  errorRetryBtn.addEventListener('click', () => {
    started = false;
    start();
  });

  anchor.addEventListener('targetFound', () => {
    videoEl.currentTime = 0;
    videoEl.play().catch((err) => console.warn('play() blocked', err));
  });

  anchor.addEventListener('targetLost', () => {
    videoEl.pause();
  });

  sceneEl.addEventListener('arError', (e) => {
    console.error('AR error', e.detail, lastCameraError);
    started = false;
    showCameraError();
  });
})();
