import { expect, test } from '@playwright/test';
import { writeFile, mkdir } from 'node:fs/promises';

// Trace snapshots and repeated role-name scans over 300 rows distort frame timing.
test.use({ trace: 'off' });

test('300-model orbit benchmark', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  const start = Date.now();
  await page.goto('/?benchmark=300');
  const map = page.getByTestId('map');
  await expect(map).toHaveAttribute('data-models-loaded', '4', { timeout: 90_000 });
  const readyMs = Date.now() - start;
  await expect(map).toHaveAttribute('data-instance-count', '300');
  await page.getByRole('button', { name: 'Measure 8-second orbit' }).click();
  await page.waitForTimeout(8500); // Fixed 8s benchmark; do not poll the DOM during measurement.
  const coldOrbit = JSON.parse(await page.getByTestId('benchmark-result').innerText());
  await page.getByRole('button', { name: /Reset view/ }).click();
  // Warm the same camera path after shaders and visible tile resources have been used once.
  await page.waitForTimeout(2000);
  await page.getByRole('button', { name: 'Measure 8-second orbit' }).click();
  await page.waitForTimeout(8500);
  const result = JSON.parse(await page.getByTestId('benchmark-result').innerText());
  await page.getByText('Refine with filters', { exact: true }).click();
  await page.getByLabel('Max price ($)').fill('1');
  await expect(map).toHaveAttribute('data-rendered-instances', '0');
  await page.getByRole('button', { name: /Reset view/ }).click();
  await page.waitForTimeout(2000);
  await page.getByRole('button', { name: 'Measure 8-second orbit' }).click();
  await page.waitForTimeout(8500);
  const basemapOnly = JSON.parse(await page.getByTestId('benchmark-result').innerText());
  const resources = await page.evaluate(() => performance.getEntriesByType('resource')
    .filter(entry => entry.name.endsWith('.glb')).map(entry => {
      const resource = entry as PerformanceResourceTiming;
      return { url: new URL(resource.name).pathname, durationMs: +resource.duration.toFixed(1),
        transferredBytes: resource.transferSize, decodedBytes: resource.decodedBodySize };
    }));
  const report = { ...result, coldOrbit, basemapOnly, readyMs, modelPhaseMs: +(await map.getAttribute('data-model-load-ms'))!,
    browser: await page.evaluate(() => navigator.userAgent), resources };
  await mkdir('../docs/evidence', { recursive: true });
  await writeFile('../docs/evidence/m3-performance.json', JSON.stringify(report, null, 2));
  console.info(JSON.stringify(report));
  expect(resources).toHaveLength(4); // Four network assets, not 300 repeated model downloads.
  expect(result.deckFrames).toBeGreaterThan(0);
  expect(errors).toEqual([]);
});
