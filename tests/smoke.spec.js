const { test, expect } = require('@playwright/test');

test.describe('AR postcard smoke test', () => {
  test('loads with no console errors and CSP-clean script execution', async ({ page }) => {
    const errors = [];
    page.on('pageerror', (err) => errors.push(err.message));
    page.on('console', (msg) => {
      if (msg.type() === 'error') errors.push(msg.text());
    });

    await page.goto('/');
    await expect(page.locator('#start-btn')).toBeVisible();
    await page.waitForTimeout(500);

    expect(errors, `Console errors on load:\n${errors.join('\n')}`).toEqual([]);
  });

  test('critical assets are reachable', async ({ request, baseURL }) => {
    // targets.mind in particular is only fetched by MindAR after
    // arSystem.start() (autoStart: false), so hit these directly rather
    // than relying on what page.goto('/') happens to trigger.
    for (const path of ['/js/config.js', '/js/app.js', '/targets.mind', '/video.mp4']) {
      const res = await request.get(new URL(path, baseURL).toString());
      expect(res.status(), `${path} did not return a successful status`).toBeLessThan(400);
    }
  });

  test('tapping start grants the (fake) camera and starts AR without tripping the error overlay', async ({ page }) => {
    const errors = [];
    page.on('pageerror', (err) => errors.push(err.message));

    await page.goto('/');
    await page.click('#start-btn');

    // Give MindAR time to spin up its tracking worker, load targets.mind,
    // and call getUserMedia() against the fake camera device.
    await page.waitForTimeout(3000);

    await expect(page.locator('#error-overlay')).not.toHaveClass(/visible/);
    expect(errors, `Uncaught page errors after start:\n${errors.join('\n')}`).toEqual([]);
  });
});
