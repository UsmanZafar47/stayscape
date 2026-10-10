import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';
import { getListings } from '../src/api';
import { emptyFilters, retainedSelection, validateFilters } from '../src/filters';
import { declutter } from '../src/declutter';
import { propertyTypes } from '../src/listings';
const models: { type: string }[] = JSON.parse(readFileSync('src/model-manifest.json', 'utf8'));
const records = JSON.parse(readFileSync('../backend/data/listings.json', 'utf8')).listings;

test('client paginates all records, normalizes fields, forwards filters and cancellation', async () => {
  const calls: string[] = [];
  const controller = new AbortController();
  const fake: typeof fetch = async (input, init) => {
    expect(init?.signal).toBe(controller.signal);
    calls.push(String(input));
    const offset = Number(new URL(String(input), 'http://local').searchParams.get('offset'));
    return Response.json({ items: records.slice(offset, offset + 100), total: 300, offset, limit: 100 });
  };
  const items = await getListings({ bedrooms: 0, price_max_minor: 25000 }, controller.signal, fake);
  expect(items).toHaveLength(300);
  expect(items[0].position).toEqual([records[0].longitude, records[0].latitude]);
  expect(calls).toHaveLength(3);
  expect(calls[2]).toContain('offset=200');
  expect(calls.every(call => call.includes('bedrooms=0') && call.includes('price_max_minor=25000'))).toBe(true);
});

test('client rejects HTTP, malformed, incomplete and duplicate pages; accepts empty results', async () => {
  const signal = new AbortController().signal;
  await expect(getListings({}, signal, async () => new Response('', { status: 503 }))).rejects.toThrow('503');
  await expect(getListings({}, signal, async () => Response.json({}))).rejects.toThrow('Invalid');
  await expect(getListings({}, signal, async () => Response.json({ items: [], total: 1, offset: 0, limit: 100 }))).rejects.toThrow('incomplete');
  await expect(getListings({}, signal, async () => Response.json({ items: [records[0], records[0]], total: 2, offset: 0, limit: 100 }))).rejects.toThrow('Duplicate');
  await expect(getListings({}, signal, async () => Response.json({ items: [{ ...records[0], property_type: 'castle' }], total: 1, offset: 0, limit: 100 }))).rejects.toThrow('incompatible');
  expect(await getListings({}, signal, async () => Response.json({ items: [], total: 0, offset: 0, limit: 100 }))).toEqual([]);
});

test('filter validation preserves zero and cents, enforces bounds and retained selection', () => {
  expect([...propertyTypes].sort()).toEqual(models.map(model => model.type).sort());
  expect(validateFilters({ ...emptyFilters, min: '0', max: '250.35', bedrooms: '0', type: 'loft', guests: '2' }))
    .toEqual({ price_min_minor: 0, price_max_minor: 25035, bedrooms: 0, property_type: 'loft', guests: 2 });
  for (const patch of [{ min: '500', max: '200' }, { min: '-1' }, { max: '1.001' }, { guests: '11' }, { bedrooms: '6' }, { type: 'castle' }]) {
    expect(() => validateFilters({ ...emptyFilters, ...patch })).toThrow();
  }
  expect(retainedSelection([{ id: 'a' }], 'a')).toBe('a');
  expect(retainedSelection([], 'a')).toBeNull();
});

test('declutter reserves priority labels and thins low zoom with rectangle collisions', () => {
  const tags = [0, 1, 2, 3].map(i => ({ id: String(i), x: 100 + i * 90, y: 100, width: 60, priority: i === 0 }));
  expect(declutter(tags, 12, 1000, 800).size).toBeLessThan(declutter(tags, 16, 1000, 800).size);
  const crowded = [{ ...tags[0], priority: false }, { ...tags[0], id: 'selected', priority: true }, { ...tags[0], id: 'hovered', priority: true }];
  expect([...declutter(crowded, 12, 1000, 800)]).toEqual(['selected', 'hovered']);
});
