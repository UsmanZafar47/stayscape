import { test, expect } from '@playwright/test';

// One end-to-end smoke test doubles as the requested screenshot capture.
test('offline AI query shares results, fits the map and returns to browse', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('.listing-row')).toHaveCount(300);
  const map = page.getByTestId('map');
  await expect(map).toHaveAttribute('data-models-loaded', '4', { timeout: 90000 });
  const responsePromise = page.waitForResponse(response => response.url().endsWith('/api/search') && response.request().method() === 'POST');
  await page.locator('.suggestion-chips button').first().click();
  const data = await (await responsePromise).json();
  expect(data.source).toBe('demo');
  await expect(page.locator('.search-answer')).toContainText('Offline demo');
  await expect(page.locator('.listing-row')).toHaveCount(data.items.length);
  await expect(map).toHaveAttribute('data-instance-count', String(data.items.length));
  const ids = await page.locator('.listing-row').evaluateAll(rows => rows.map(row => row.getAttribute('data-listing-id')));
  expect(ids).toEqual(data.items.map((item: { id: string }) => item.id));
  await expect.poll(async () => Number(await map.getAttribute('data-zoom'))).toBeGreaterThan(12.7);
  await page.waitForTimeout(2000); // Allow fitBounds and tile painting to finish before the screenshot.
  await page.screenshot({ path: '../docs/evidence/m4-ai-query.png' });
  await page.getByRole('button', { name: 'Clear search' }).click();
  await expect(page.locator('.listing-row')).toHaveCount(300);
  await page.getByLabel('Describe your city escape').fill('Quiet Manhattan apartment under $250 for 2 guests with wifi');
  await page.getByRole('button', { name: 'Find stays', exact: true }).click();
  await expect(page.locator('.search-answer')).toContainText('Keyword fallback');
  await expect(page.locator('.search-answer')).toContainText('Limited keyword interpretation');
  await page.getByText('Refine with filters', { exact: true }).click();
  await expect(page.getByLabel('Max price ($)')).toHaveValue('250');
  await page.getByLabel('Max price ($)').fill('1');
  await expect(page.getByText('No matches.', { exact: false })).toBeVisible();
  await expect(page.locator('.search-answer')).toHaveCount(0);
  await expect(map).toHaveAttribute('data-instance-count', '0');
});
