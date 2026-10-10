import { propertyTypes, type PropertyType } from './listings';
export type FilterDraft = { min: string; max: string; guests: string; bedrooms: string; type: string };
export type Filters = { price_min_minor?: number; price_max_minor?: number; guests?: number; bedrooms?: number; property_type?: PropertyType };
export const emptyFilters: FilterDraft = { min: '', max: '', guests: '', bedrooms: '', type: '' };
export function validateFilters(draft: FilterDraft): Filters {
  const result: Filters = {};
  for (const [key, value] of Object.entries(draft)) {
    if (!value) continue;
    if (key === 'type') {
      if (!propertyTypes.includes(value as PropertyType)) throw new Error('Choose a valid property type.');
      result.property_type = value as PropertyType;
    } else if (key === 'min' || key === 'max') {
      // Convert dollars once at the boundary; the API always receives integer cents.
      if (!/^\d+(\.\d{1,2})?$/.test(value) || Number(value) > 100000) throw new Error('Prices must be $0–$100,000 with at most two decimal places.');
      result[key === 'min' ? 'price_min_minor' : 'price_max_minor'] = Math.round(Number(value) * 100);
    } else {
      const number = Number(value);
      if (!/^\d+$/.test(value) || number < (key === 'guests' ? 1 : 0) || number > (key === 'guests' ? 10 : 5)) throw new Error('Choose a valid guest or bedroom count.');
      result[key as 'guests' | 'bedrooms'] = number;
    }
  }
  if ((result.price_min_minor ?? 0) > (result.price_max_minor ?? Infinity)) throw new Error('Minimum price cannot exceed maximum price.');
  return result;
}
export function retainedSelection(items: { id: string }[], selected: string | null) {
  return items.some(item => item.id === selected) ? selected : null;
}
