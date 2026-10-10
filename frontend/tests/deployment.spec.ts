import { test, expect } from '@playwright/test';

test('first slow backend request explains waking and offers retry', async ({ page }) => {
  await page.route('https://tiles.openfreemap.org/**', route => route.abort());
  let count = 0;
  await page.route('**/api/listings?**', async route => {
    count++;
    if (count === 1) {
      await new Promise(resolve => setTimeout(resolve, 5500));
      await route.fulfill({ status: 503, json: {} }).catch(() => {});
    } else {
      await route.fulfill({ json: { items: [], total: 0, offset: 0, limit: 100 } });
    }
  });
  await page.goto('/');
  await expect(page.getByText('Backend is waking up or unreachable.', { exact: false })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Retry connection' })).toBeVisible();
  await page.getByRole('button', { name: 'Retry connection' }).click();
  await expect(page.getByText('No matches.', { exact: false })).toBeVisible();
  await expect(page.getByText('Backend is waking up or unreachable.', { exact: false })).toHaveCount(0);
});

// Built separately with VITE_API_URL; verifies both API calls and image URLs in the shipped bundle.
test('configured deployment origin serves listings and placeholder images', async ({ page }) => {
  test.skip(process.env.DEPLOY_API_TEST !== '1', 'Requires the production-origin test build');
  const { readFileSync } = await import('node:fs');
  const record = JSON.parse(readFileSync('../backend/data/listings.json', 'utf8')).listings[0];
  const origin = 'https://stayscape-api.example';
  await page.route('https://tiles.openfreemap.org/**', route => route.abort());
  await page.route(`${origin}/api/search/examples`, route => route.fulfill({ json: { queries: [], demo_mode: true } }));
  await page.route(`${origin}/api/listings?**`, route => route.fulfill({ json: { items: [record], total: 1, offset: 0, limit: 100 } }));
  await page.route(`${origin}/static/placeholders/**`, route => route.fulfill({ path: `../backend/static/placeholders/${record.property_type}.svg` }));
  await page.goto('/');
  await expect(page.locator('.listing-row')).toHaveCount(1);
  await page.locator('.listing-row').click();
  const image = page.locator('.detail-image');
  await expect(image).toHaveAttribute('src', `${origin}${record.pictures[0]}?retry=0`);
  await expect.poll(() => image.evaluate((img: HTMLImageElement) => img.naturalWidth)).toBeGreaterThan(0);
});
