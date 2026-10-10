export const propertyTypes = ['apartment', 'townhouse', 'house', 'loft'] as const;
export type PropertyType = typeof propertyTypes[number];
export type Listing = {
  id: string; title: string; neighborhood: string;
  position: [longitude: number, latitude: number];
  priceMinor: number; currency: 'USD'; rating: number; guests: number;
  bedrooms: number; propertyType: PropertyType; description: string;
  amenities: string[]; pictures: string[];
};
export const stressMode = typeof window !== 'undefined' && new URLSearchParams(window.location.search).get('benchmark') === '300';
const formatter = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
export const price = (listing: Listing) => formatter.format(listing.priceMinor / 100);
export function ratingColor(rating: number): [number, number, number, number] {
  return rating >= 4.8 ? [111, 225, 185, 255] : rating >= 4.5 ? [133, 182, 239, 255] : [238, 186, 111, 255];
}
