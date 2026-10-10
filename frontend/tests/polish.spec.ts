import { test, expect } from '@playwright/test';

test('polished desktop and phone preserve selection, motion preference and attribution', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('.listing-row')).toHaveCount(300);
  await expect(page.getByTestId('map')).toHaveAttribute('data-models-loaded', '4', { timeout: 90000 });
  await page.locator('.suggestion-chips button').first().click();
  await expect(page.locator('.search-answer')).toContainText('Offline demo');
  await page.locator('.listing-row').first().click();
  await expect(page.getByRole('region', { name: 'Selected listing' })).toBeVisible();
  // Wait for city geometry, not only model downloads, before portfolio captures.
  await expect.poll(async () => Number(await page.getByTestId('map').getAttribute('data-rendered-buildings')),
    { timeout: 90000 }).toBeGreaterThan(0);
  await page.waitForTimeout(2500);
  await page.screenshot({ path: '../docs/evidence/m5-desktop.png' });
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.setViewportSize({ width: 390, height: 844 });
  const credits = page.locator('.maplibregl-ctrl-attrib');
  await expect(credits).toBeVisible();
  const creditBox = await credits.boundingBox();
  const detailsBox = await page.locator('.details-panel').boundingBox();
  expect(creditBox!.y + creditBox!.height).toBeLessThanOrEqual(detailsBox!.y);
  await page.getByRole('button', { name: 'Close selected listing' }).click();
  await page.getByRole('button', { name: 'Collapse explorer' }).click();
  await expect(page.locator('#explorer-controls')).toBeHidden();
  await page.getByRole('button', { name: /Explore .* stays/ }).click();
  await expect(page.getByLabel('Describe your city escape')).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.screenshot({ path: '../docs/evidence/m5-phone.png' });
});
