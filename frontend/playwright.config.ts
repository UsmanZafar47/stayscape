import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests', timeout: 180_000, workers: 1,
  // Software WebGL on CI can take longer than the nominal camera animation duration.
  expect: { timeout: 30_000 },
  use: {
    baseURL: 'http://127.0.0.1:4173', viewport: { width: 1280, height: 800 },
    // Edge is already installed on this Windows machine; no browser download is needed.
    channel: process.env.PLAYWRIGHT_CHANNEL || 'msedge',
    // Opt in to the machine's GPU for useful local performance measurements.
    // Default software rendering keeps functional tests reproducible on CI.
    launchOptions: { args: process.env.BENCHMARK_HARDWARE === '1'
      ? ['--enable-webgl'] : ['--enable-webgl', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] },
    trace: { mode: 'retain-on-failure', screenshots: false },
  },
  webServer: {
    command: 'npm run preview', url: 'http://127.0.0.1:4173',
    reuseExistingServer: !process.env.CI,
  },
});
