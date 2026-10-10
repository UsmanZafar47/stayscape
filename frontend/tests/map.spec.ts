import { expect, test } from '@playwright/test';

test('local GLBs, real tiles, model picking, selection, and reset', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => {
    if (message.type() === 'error' || message.type() === 'warning') console.info('Browser:', message.text());
  });
  await page.goto('/');
  await expect(page.locator('.listing-row')).toHaveCount(300);
  const map = page.getByTestId('map');
  await expect(page.getByRole('alert')).toHaveCount(0);
  await expect(map).toHaveAttribute('data-models-loaded', '4', { timeout: 90_000 });

  console.info('NYC tile building features:', await map.getAttribute('data-building-count'),
    'rendered building features:', await map.getAttribute('data-rendered-buildings'));
  await page.screenshot({ path: '../docs/evidence/m3-desktop.png' });
  const title = await page.locator('.listing-row strong').first().innerText();
  await page.locator('.listing-row').first().click();
  await expect(page.getByRole('region', { name: 'Selected listing' })).toContainText(title);
  await expect.poll(async () => Number(await map.getAttribute('data-zoom'))).toBeCloseTo(15.6, 1);
  // A style loading is insufficient: actual NYC building tile features must be present.
  await expect.poll(async () => Number(await map.getAttribute('data-building-count')),
    { timeout: 90_000 }).toBeGreaterThan(0);

  // Exercise real GPU picking, not a mocked callback: models, rings and tags share the listing ID.
  const box = (await map.boundingBox())!;
  let picked = false;
  let pickedPosition = { x: 0, y: 0 };
  let hoveredTitle = '';
  for (let y = box.height / 2 - 15; y >= box.height / 2 - 180 && !picked; y -= 15) {
    for (const x of [box.width / 2, box.width / 2 - 24, box.width / 2 + 24]) {
      await page.mouse.move(box.x + x, box.y + y);
      // GPU picking and React commit on later frames: don't read the previous pointer's tooltip.
      await page.evaluate(() => new Promise<void>(resolve =>
        requestAnimationFrame(() => requestAnimationFrame(() => resolve()))));
      hoveredTitle = await page.getByRole('tooltip').locator('strong').textContent({ timeout: 250 })
        .catch(() => '') || '';
      if (hoveredTitle && (await map.getAttribute('data-hover-layer'))?.startsWith('property-')) {
        picked = true; pickedPosition = { x: box.x + x, y: box.y + y }; break;
      }
    }
  }
  expect(picked, 'A GLB mesh itself must be pickable, not just its ring or price tag').toBe(true);
  await page.mouse.click(pickedPosition.x, pickedPosition.y);
  await expect(page.getByRole('region', { name: 'Selected listing' })).toContainText(hoveredTitle);
  await page.mouse.move(150, 100);
  await expect(page.getByRole('tooltip')).toHaveCount(0);
  await page.screenshot({ path: '../docs/evidence/m3-selected.png' });
  const center = await map.getAttribute('data-center');
  await page.getByText('Refine with filters', { exact: true }).click();
  await page.getByLabel('Max price ($)').fill('1');
  await expect(page.getByText('No matches.', { exact: false })).toBeVisible();
  await expect(page.getByRole('region', { name: 'Selected listing' })).toHaveCount(0);
  await expect(map).toHaveAttribute('data-instance-count', '0');
  const after = (await map.getAttribute('data-center'))!.split(',').map(Number);
  center!.split(',').map(Number).forEach((coordinate, i) => expect(after[i]).toBeCloseTo(coordinate, 8));
  await expect(map).toHaveAttribute('data-rendered-instances', '0');
  await expect(map).toHaveAttribute('data-zoom', '15.6');
  await page.getByRole('button', { name: 'Clear all filters' }).click();
  await expect(page.locator('.listing-row')).toHaveCount(300);
  await page.getByLabel('Property type').selectOption('loft');
  await expect.poll(() => page.locator('.listing-row').count()).toBeLessThan(300);
  const count = await page.locator('.listing-row').count();
  expect(count).toBeGreaterThan(0);
  await expect(map).toHaveAttribute('data-instance-count', String(count));
  expect(await page.locator('.listing-copy small').allTextContents()).toEqual(Array(count).fill(expect.stringContaining('loft')));
  await page.getByRole('button', { name: 'Clear filters', exact: true }).click();
  await expect(page.locator('.listing-row')).toHaveCount(300);
  await page.getByRole('button', { name: '3D buildings on' }).click();
  await expect(page.getByRole('button', { name: '3D buildings off' })).toHaveAttribute('aria-pressed', 'false');
  await page.getByRole('button', { name: '3D buildings off' }).click();
  await page.getByRole('button', { name: 'Reset view' }).click();
  await expect.poll(async () => Number(await map.getAttribute('data-zoom'))).toBeCloseTo(12.7, 1);
  await expect(page.getByRole('region', { name: 'Selected listing' })).toHaveCount(0);
  await expect(page.locator('.maplibregl-ctrl-attrib')).toContainText('OpenStreetMap');
  expect(errors).toEqual([]);
  await page.setViewportSize({ width: 390, height: 844 });
  await page.waitForTimeout(2000); // Let resized map tiles paint before capturing visual evidence.
  await page.screenshot({ path: '../docs/evidence/m3-mobile.png', fullPage: true });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
});

test('map service failure presents a retry instead of an endless loading state', async ({ page }) => {
  await page.route('https://tiles.openfreemap.org/**', route => route.abort());
  await page.goto('/');
  await expect(page.getByRole('alert')).toContainText('failed');
  await expect(page.getByRole('button', { name: 'Retry map' })).toBeVisible();
});
