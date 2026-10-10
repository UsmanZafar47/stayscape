import { ScenegraphLayer } from '@deck.gl/mesh-layers';
import { ScatterplotLayer, TextLayer } from '@deck.gl/layers';
import type { PickingInfo } from '@deck.gl/core';
import { price, ratingColor } from './listings';
import type { Listing } from './listings';
import models from './model-manifest.json';

// Stable per-instance colors retain four shared GPU scenes and the original textures.
const tints: [number, number, number][] = [[255, 245, 224], [217, 241, 255], [225, 255, 227]];
function tint(id: string) {
  let hash = 0;
  for (const char of id) hash = (hash * 31 + char.charCodeAt(0)) >>> 0;
  return tints[hash % tints.length];
}
export const MIN_MODEL_PIXELS = 38;
// Stable group arrays let deck.gl retain four shared scenes and instance buffers between updates.
const groupCache = new WeakMap<Listing[], { model: typeof models[number]; data: Listing[] }[]>();
const byType = Object.fromEntries(models.map(model => [model.type, model]));
type Options = {
  searchActive?: boolean;
  listings: Listing[];
  entering: Set<string>; exiting: Set<string>; progress: number;
  selectedId?: string;
  hoveredId?: string;
  zoom: number;
  latitude: number;
  reducedMotion: boolean;
  labelIds: Set<string>;
  onHover: (info: PickingInfo<Listing>) => void;
  onClick: (info: PickingInfo<Listing>) => void;
  onModelDraw: (type: string) => void;
};

export function listingLayers(options: Options) {
  const mapListings = options.listings;
  let groups = groupCache.get(mapListings);
  if (!groups) {
    groups = models.map(model => ({ model, data: mapListings.filter(d => d.propertyType === model.type) }));
    groupCache.set(mapListings, groups);
  }
  const visibility = (d: Listing) => options.exiting.has(d.id) ? 1 - options.progress : options.entering.has(d.id) ? options.progress : 1;
  const { selectedId, hoveredId, zoom, latitude } = options;
  // A city overview needs smaller symbols: the old 38px floor buried dense neighborhoods.
  // Restore the original visual size as the user approaches individual stays.
  const minPixels = Math.min(MIN_MODEL_PIXELS, Math.max(16, 16 + (zoom - 12.7) * 12));
  const active = (d: Listing) => d.id === selectedId || d.id === hoveredId;
  // Match ScenegraphLayer's meter-to-pixel clamp for the ground rings and tag altitude.
  // At close zoom the actual model width wins; at city zoom the symbol is exaggerated.
  const metersPerPixel = 40075016.686 * Math.cos(latitude * Math.PI / 180) / (512 * 2 ** zoom);
  const width = (d: Listing) => Math.max(byType[d.propertyType].widthMeters, minPixels * metersPerPixel);
  const lift = (d: Listing) => active(d) ? 5 : 0;
  const triggers = [zoom, latitude, selectedId, hoveredId];
  const events = { onHover: options.onHover, onClick: options.onClick };
  return [
    // Three translucent concentric strokes approximate a soft glow without a bloom framebuffer.
    ...[0, 1, 2].map(index => new ScatterplotLayer<Listing>({
      id: `rating-halo-${index}`, data: mapListings, getPosition: d => d.position,
      radiusUnits: 'meters', getRadius: d => width(d) * (0.73 + index * 0.08) * visibility(d),
      filled: index === 0, stroked: true, billboard: false,
      getFillColor: d => [...ratingColor(d.rating).slice(0, 3), active(d) ? 45 : 20] as [number, number, number, number],
      getLineColor: d => options.searchActive && index === 0 ? [185, 243, 215, 255] : [...ratingColor(d.rating).slice(0, 3), [220, 65, 22][index]] as [number, number, number, number],
      lineWidthUnits: 'pixels', getLineWidth: d => index === 0 ? (active(d) || options.searchActive ? 3 : 1.6) : 5,
      // The center also picks: a building is still selectable through a gap in its mesh.
      pickable: index === 0, ...events,
      parameters: { depthWriteEnabled: false },
      updateTriggers: { getRadius: [...triggers, options.progress], getFillColor: triggers, getLineWidth: [...triggers, options.searchActive], getLineColor: [options.searchActive] },
    })),
    ...groups.map(({ model, data }) => new ScenegraphLayer<Listing>({
      id: `property-${model.type}`, data, scenegraph: model.url,
      sizeScale: model.widthMeters, sizeMinPixels: minPixels,
      // Export already centers the footprint and rotates Y-up to Z-up; no runtime axis guesswork.
      getPosition: d => [d.position[0], d.position[1], lift(d)],
      // Short-lived exit ghosts are presentation only; picking rejects them in MapScene.
      getScale: d => { const scale = (active(d) ? 1.12 : 1) * visibility(d); return [scale, scale, scale]; },
      getOrientation: [0, 28, 0], getColor: d => [...tint(d.id), Math.round(255 * visibility(d))],
      // Kenney's palette already separates roof/facade details. Flat textured lighting
      // keeps that crisp toy-city look and avoids PBR shading cost on integrated GPUs.
      _lighting: 'flat', pickable: true, ...events,
      // Matrix/scale accessors don't transition in 9.4; GPU position transitions provide the lift.
      transitions: { getPosition: options.reducedMotion ? 0 : 260 },
      updateTriggers: { getPosition: [selectedId, hoveredId], getScale: [selectedId, hoveredId, options.progress], getColor: [options.progress] },
      onFirstDraw: () => options.onModelDraw(model.type),
    })),
    new ScatterplotLayer<Listing>({
      id: 'active-outline', data: mapListings.filter(active), getPosition: d => d.position,
      getRadius: d => width(d) * 0.72, filled: false, stroked: true,
      getLineColor: [242, 255, 247, 245], lineWidthUnits: 'pixels', getLineWidth: 1.5,
      parameters: { depthCompare: 'always', depthWriteEnabled: false },
      updateTriggers: { getRadius: triggers },
    }),
    new TextLayer<Listing>({
      id: 'price-tags',
      // Simple screen-grid decluttering is cheaper than a collision framebuffer for 300 labels.
      // Models and rating rings remain pickable even when a crowded price tag is suppressed.
      data: mapListings.filter(d => !options.exiting.has(d.id) && (options.labelIds.has(d.id) || active(d))),
      // Ground anchors + fixed pixel offset make collision rectangles match rendered labels.
      getPosition: d => d.position,
      getText: price, getSize: 12, sizeUnits: 'pixels', billboard: true,
      fontFamily: 'Arial, sans-serif', fontWeight: 700, characterSet: '$0123456789,',
      getPixelOffset: [0, -48], getTextAnchor: 'middle', getAlignmentBaseline: 'bottom',
      getColor: d => active(d) ? [17, 35, 29, 255] : [245, 249, 247, 255],
      background: true, getBackgroundColor: d => active(d) ? [185, 243, 215, 255] : [24, 37, 46, 240],
      backgroundPadding: [8, 5], getBorderColor: [137, 177, 159, 170], getBorderWidth: 1,
      // Billboard UI tags should remain readable even when behind another model.
      parameters: { depthCompare: 'always', depthWriteEnabled: false },
      pickable: true, ...events,
      updateTriggers: { getPosition: triggers, getColor: triggers, getBackgroundColor: triggers },
    }),
  ];
}

