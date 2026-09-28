// @ts-check
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  fullyParallel: true,
  reporter: process.env.CI ? [['github'], ['html', { open: 'never' }]] : 'list',
  webServer: {
    command: 'npx http-server . -p 8080 -c-1',
    port: 8080,
    reuseExistingServer: !process.env.CI,
  },
  use: {
    baseURL: 'http://localhost:8080',
    permissions: ['camera'],
    launchOptions: {
      args: [
        // Feed getUserMedia() a synthetic video stream instead of erroring
        // out or hanging on a permission prompt, so the tap-to-start ->
        // camera -> MindAR-init path can run for real in headless CI.
        '--use-fake-device-for-media-stream',
        '--use-fake-ui-for-media-stream',
        // Headless Chromium has no GPU by default; A-Frame/three.js need a
        // real WebGL context to initialize, so force software rendering.
        '--use-gl=angle',
        '--use-angle=swiftshader',
        '--enable-webgl',
        '--ignore-gpu-blocklist',
      ],
    },
  },
});
