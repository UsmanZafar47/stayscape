import { expect, test } from '@playwright/test';

test.beforeEach(async ({ page }) => {
  // Component tests isolate the API/UI from external tiles; map.spec exercises real WebGL.
  await page.route('https://tiles.openfreemap.org/**', route => route.abort());
});

// Component flows run in a real browser while API failures/timing stay deterministic.
test('loading, failure, retry, debounced validation and local image details', async ({ page }) => {
  let fail = true;
  const requests: string[] = [];
  await page.route('**/api/listings?**', async route => {
    requests.push(route.request().url());
    if (fail) await route.fulfill({ status: 503, json: { error: { message: 'Unavailable' } } });
    else await route.continue();
  });
  await page.goto('/');
  await expect(page.getByText('Loading stays…', { exact: false })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Retry listings' })).toBeVisible();
  fail = false;
  await page.getByRole('button', { name: 'Retry listings' }).click();
  await expect(page.locator('.listing-row')).toHaveCount(300);
  await page.locator('.listing-row').first().click();
  const details = page.getByRole('region', { name: 'Selected listing' });
  await expect(details.locator('.description')).not.toBeEmpty();
  await expect(details.locator('.amenities li').first()).toBeVisible();
  await expect(details.locator('img')).toHaveAttribute('src', /^\/static\/placeholders\//);
  await expect.poll(() => details.locator('img').evaluate((img: HTMLImageElement) => img.naturalWidth)).toBeGreaterThan(0);
  await page.getByText('Map legend & controls').click();
  const legend = (await page.locator('.sidebar-legend').boundingBox())!;
  const map = (await page.getByTestId('map').boundingBox())!;
  expect(legend.x + legend.width).toBeLessThanOrEqual(map.x);
  await page.getByText('Refine with filters', { exact: true }).click();
  await page.getByLabel('Min price ($)').fill('500');
  await page.getByLabel('Max price ($)').fill('100');
  await expect(page.getByRole('alert').filter({ hasText: 'Minimum price' })).toBeVisible();
  const before = requests.length;
  await page.waitForTimeout(400); // Assert no invalid request crosses the debounce boundary.
  expect(requests.length).toBe(before);
  await page.getByRole('button', { name: 'Clear filters', exact: true }).click();
  await expect(page.locator('.listing-list')).toHaveAttribute('aria-busy', 'false');
  const start = requests.length;
  await page.getByLabel('Max price ($)').fill('1');
  await page.getByLabel('Max price ($)').fill('10');
  await page.getByLabel('Max price ($)').fill('100');
  await expect(page.locator('.listing-list')).toHaveAttribute('aria-busy', 'false');
  expect(requests.slice(start).every(url => url.includes('price_max_minor=10000'))).toBe(true);
  expect(requests.length).toBeGreaterThan(start);
});

test('a late obsolete response cannot overwrite newer results; a later page failure keeps the whole old snapshot', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('.listing-row')).toHaveCount(300);
  let release: () => void = () => {};
  const delayed = new Promise<void>(resolve => { release = resolve; });
  await page.route('**/api/listings?**', async route => {
    const url = new URL(route.request().url());
    if (url.searchParams.get('price_max_minor') === '100') {
      await delayed;
      await route.fulfill({ json: { items: [], total: 0, offset: 0, limit: 100 } }).catch(() => {});
    } else if (url.searchParams.get('offset') === '100') await route.fulfill({ status: 503, body: 'offline' });
    else await route.continue();
  });
  await page.getByText('Refine with filters', { exact: true }).click();
  await page.getByLabel('Max price ($)').fill('1');
  await page.waitForRequest(request => request.url().includes('price_max_minor=100'));
  await page.getByRole('button', { name: 'Clear filters', exact: true }).click();
  await expect(page.getByRole('button', { name: 'Retry listings' })).toBeVisible();
  release();
  await page.waitForTimeout(100);
  await expect(page.locator('.listing-row')).toHaveCount(300);
  await expect(page.getByTestId('map')).toHaveAttribute('data-instance-count', '300');
  await page.unroute('**/api/listings?**');
  await page.getByRole('button', { name: 'Retry listings' }).click();
  await expect(page.locator('.listing-list')).toHaveAttribute('aria-busy', 'false');
});

test('local illustration failures are recoverable without changing the selected stay', async ({ page }) => {
  await page.route('**/static/placeholders/**', route => route.fulfill({ status: 503, body: 'offline' }));
  await page.goto('/');
  await expect(page.locator('.listing-row')).toHaveCount(300);
  const title = await page.locator('.listing-row strong').first().innerText();
  await page.locator('.listing-row').first().click();
  await expect(page.getByRole('button', { name: 'Retry image' })).toBeVisible();
  await page.unroute('**/static/placeholders/**');
  await page.getByRole('button', { name: 'Retry image' }).click();
  const details = page.getByRole('region', { name: 'Selected listing' });
  await expect(details).toContainText(title);
  await expect.poll(() => details.locator('img').evaluate((img: HTMLImageElement) => img.naturalWidth)).toBeGreaterThan(0);
  await page.getByRole('button', { name: 'Close selected listing' }).click();
  await expect(details).toHaveCount(0);
});

