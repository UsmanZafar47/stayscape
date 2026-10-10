import { test, expect } from '@playwright/test';
test.use({ trace: 'off' });

// Real browser captures for the repository walkthrough; attribution remains in every map frame.
test('capture the complete local portfolio walkthrough', async ({ page }) => {
  test.setTimeout(240000);
  // Captures need settled frames; motion itself is covered by the interaction tests.
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto('/');
  const map = page.getByTestId('map');
  await expect(page.locator('.listing-row')).toHaveCount(300);
  await expect(map).toHaveAttribute('data-models-loaded', '4', { timeout: 90000 });
  await page.waitForTimeout(3000);
  await page.screenshot({ path: '../docs/screenshots/01-overview.png' });

  await page.locator('.listing-row').first().click();
  await expect.poll(async () => Number(await map.getAttribute('data-rendered-buildings')), { timeout: 90000 }).toBeGreaterThan(0);
  await expect.poll(async () => Number(await map.getAttribute('data-zoom'))).toBeCloseTo(15.6, 1);
  await page.waitForTimeout(1500);
  await page.screenshot({ path: '../docs/screenshots/02-details.png' });
  await page.getByRole('button', { name: 'Close selected listing' }).click();

  await page.getByText('Refine with filters', { exact: true }).click();
  await page.getByLabel('Max price ($)').fill('180');
  // This label includes option text in Playwright; use the first filter-grid dropdown.
  await page.locator('.filter-grid select').first().selectOption('2');
  await page.getByLabel('Property type').selectOption('apartment');
  await expect.poll(() => page.locator('.listing-row').count()).toBeLessThan(300);
  await page.getByRole('button', { name: 'Reset view' }).click();
  await expect.poll(async () => Number(await map.getAttribute('data-zoom'))).toBeCloseTo(12.7, 1);
  await page.waitForTimeout(1500);
  await page.screenshot({ path: '../docs/screenshots/03-filters.png' });

  await page.getByRole('button', { name: 'Clear filters', exact: true }).click();
  await expect(page.locator('.listing-row')).toHaveCount(300);
  await page.getByText('Refine with filters', { exact: true }).click();
  await page.locator('.suggestion-chips button').first().click();
  await expect(page.locator('.search-answer')).toContainText('Offline demo');
  await expect(page.locator('.listing-row')).toHaveCount(12);
  await page.waitForTimeout(3000);
  await page.screenshot({ path: '../docs/screenshots/04-demo-search.png' });

  await page.getByText('Refine with filters', { exact: true }).click();
  await page.getByLabel('Max price ($)').fill('1');
  await expect(page.getByText('No matches.', { exact: false })).toBeVisible();
  await expect(map).toHaveAttribute('data-rendered-instances', '0');
  await page.screenshot({ path: '../docs/screenshots/05-no-matches.png' });
  await page.getByRole('button', { name: 'Clear all filters' }).click();
  await expect(page.locator('.listing-row')).toHaveCount(300);
  await page.getByText('Refine with filters', { exact: true }).click();
  await page.locator('.suggestion-chips button').first().click();
  await expect(page.locator('.search-answer')).toContainText('Offline demo');
  await page.setViewportSize({ width: 390, height: 844 });
  await page.waitForTimeout(2500);
  await page.screenshot({ path: '../docs/screenshots/06-phone-explorer.png' });
  await page.getByRole('button', { name: 'Collapse explorer' }).click();
  await page.waitForTimeout(1500);
  await page.screenshot({ path: '../docs/screenshots/07-phone-map.png' });
  await expect(page.locator('.maplibregl-ctrl-attrib')).toBeVisible();
});
