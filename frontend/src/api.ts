import { propertyTypes, type Listing } from './listings';
import type { Filters } from './filters';
// Vite substitutes this public origin at build time; blank retains the local proxy.
const API_ORIGIN = (import.meta.env?.VITE_API_URL ?? '').replace(/\/$/, '');
export const apiUrl = (path: string) => `${API_ORIGIN}${path}`;
// Transport names stay at this boundary; render code uses one normalized Listing type.
type ApiListing = {
  id: string; title: string; neighborhood: string; longitude: number; latitude: number;
  price_minor: number; currency: string; rating: number; max_guests: number;
  bedrooms: number; property_type: Listing['propertyType']; description: string;
  amenities: string[]; pictures: string[];
};
function listing(value: unknown): Listing {
  const d = value as ApiListing;
  if (!d || !['id', 'title', 'neighborhood', 'description'].every(key => typeof d[key as keyof ApiListing] === 'string') ||
    ![d.longitude, d.latitude, d.rating, d.price_minor, d.max_guests, d.bedrooms].every(Number.isFinite) ||
    d.currency !== 'USD' || !propertyTypes.includes(d.property_type) ||
    !Array.isArray(d.amenities) || !d.amenities.every(v => typeof v === 'string') ||
    !Array.isArray(d.pictures) || !d.pictures.length || !d.pictures.every(v => /^\/static\/placeholders\/[a-z-]+\.svg$/.test(v))) {
    throw new Error('The listings response is incompatible. Check the backend dataset and retry.');
  }
  return { id: d.id, title: d.title, neighborhood: d.neighborhood, position: [d.longitude, d.latitude],
    priceMinor: d.price_minor, currency: 'USD', rating: d.rating, guests: d.max_guests, bedrooms: d.bedrooms,
    propertyType: d.property_type, description: d.description, amenities: d.amenities, pictures: d.pictures.map(apiUrl) };
}

export type SearchIntent = Filters & { region?: string | null; amenities: string[]; vibes: string[] };
export type SearchResult = { query: string; intent: SearchIntent; items: Listing[]; explanation: string;
  bounds: [[number, number], [number, number]] | null; source: 'demo' | 'rules' | 'provider'; eligible_total: number; cached: boolean };
export async function searchListings(query: string, demo: boolean, signal: AbortSignal): Promise<SearchResult> {
  const response = await fetch(apiUrl('/api/search'), { method: 'POST', signal,
    headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ query, demo }) });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.error?.message || `Search failed (HTTP ${response.status}). Retry.`);
  }
  const result = await response.json();
  if (!Array.isArray(result.items) || typeof result.explanation !== 'string' || !result.intent ||
      !Array.isArray(result.intent.amenities) || !Array.isArray(result.intent.vibes) ||
      !['demo', 'rules', 'provider'].includes(result.source) || !Number.isInteger(result.eligible_total) ||
      (result.bounds !== null && (!Array.isArray(result.bounds) || result.bounds.length !== 2 ||
        !result.bounds.every((pair: unknown) => Array.isArray(pair) && pair.length === 2 && pair.every(Number.isFinite))))) {
    throw new Error('Search returned an invalid response. Retry.');
  }
  return { ...result, items: result.items.map(listing) };
}
export async function getSearchExamples(signal: AbortSignal): Promise<{ queries: string[]; demo_mode: boolean }> {
  const response = await fetch(apiUrl('/api/search/examples'), { signal });
  if (!response.ok) throw new Error('Could not load suggestions.');
  const result = await response.json();
  if (!Array.isArray(result.queries) || !result.queries.every((q: unknown) => typeof q === 'string')) throw new Error('Invalid suggestions.');
  return result;
}
export async function getListings(filters: Filters, signal: AbortSignal, fetcher: typeof fetch = fetch): Promise<Listing[]> {
  const items: Listing[] = [];
  let total = Infinity;
  // Commit all pages atomically, never a partial map/list. One signal cancels every page.
  while (items.length < total) {
    const params = new URLSearchParams({ limit: '100', offset: String(items.length) });
    Object.entries(filters).forEach(([key, value]) => { if (value !== undefined) params.set(key, String(value)); });
    const response = await fetcher(apiUrl(`/api/listings?${params}`), { signal });
    if (!response.ok) throw new Error(`Could not load listings (HTTP ${response.status}). Check the backend and retry.`);
    const page = await response.json();
    if (!Array.isArray(page.items) || !Number.isInteger(page.total) || page.total < 0 || page.offset !== items.length ||
      page.limit !== 100 || page.items.length > 100 || (total !== Infinity && total !== page.total)) throw new Error('Invalid or changing listing pages. Please retry.');
    total = page.total;
    if (!page.items.length && items.length < total) throw new Error('The listing page was incomplete. Please retry.');
    items.push(...page.items.map(listing));
    if (items.length > total || new Set(items.map(d => d.id)).size !== items.length) throw new Error('Duplicate or inconsistent listings. Please retry.');
  }
  return items;
}
