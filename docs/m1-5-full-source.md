# M1.5 full changed source

This snapshot accompanies the working files. GLB/PNG binaries, original license files and package-lock.json are stored separately in the repository. M2 is not included.

## frontend/package.json

```

{
  "name": "stayscape-map-spike",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "engines": {
    "node": "^20.19.0 || >=22.12.0"
  },
  "scripts": {
    "dev": "vite --host 127.0.0.1",
    "build": "tsc --noEmit && vite build",
    "preview": "vite preview --host 127.0.0.1",
    "test:browser": "playwright test"
  },
  "dependencies": {
    "@deck.gl/core": "9.4.0",
    "@deck.gl/layers": "9.4.0",
    "@deck.gl/maplibre": "9.4.0",
    "@deck.gl/mesh-layers": "9.4.0",
    "@luma.gl/core": "9.4.0",
    "@luma.gl/gltf": "9.4.0",
    "maplibre-gl": "6.11.2",
    "react": "19.3.0",
    "react-dom": "19.3.0"
  },
  "devDependencies": {
    "@gltf-transform/core": "4.5.1",
    "@gltf-transform/extensions": "4.5.1",
    "@gltf-transform/functions": "4.5.1",
    "@playwright/test": "1.63.0",
    "@types/node": "26.6.3",
    "@types/react": "19.3.0",
    "@types/react-dom": "19.3.0",
    "@vitejs/plugin-react": "6.1.1",
    "typescript": "7.0.2",
    "vite": "8.3.1"
  }
}


```

## frontend/tsconfig.json

```

{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "resolveJsonModule": true,
    "jsx": "react-jsx",
    "strict": true,
    "skipLibCheck": true,
    "noEmit": true,
    "esModuleInterop": true,
    "verbatimModuleSyntax": true,
    "types": ["vite/client", "node"]
  },
  "include": ["src", "vite.config.ts", "playwright.config.ts", "tests"]
}


```

## frontend/playwright.config.ts

```

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


```

## frontend/src/listings.ts

```

export type Listing = {
  id: string;
  title: string;
  neighborhood: string;
  position: [longitude: number, latitude: number];
  priceMinor: number;
  currency: 'USD';
  rating: number;
  guests: number;
  propertyType: 'apartment' | 'townhouse' | 'house' | 'loft';
};

// Hand-authored demo fixtures, not real rentals or scraped addresses.
// A compact Manhattan collection makes the illustrated models easy to compare.
const rows: [string, string, number, number, number, number, number][] = [
  ['Canal Street loft', 'Tribeca', -74.0058, 40.7220, 24500, 4.9, 4],
  ['Quiet courtyard studio', 'SoHo', -74.0015, 40.7248, 16500, 4.7, 2],
  ['Spring Street hideaway', 'SoHo', -74.0031, 40.7266, 21000, 4.8, 2],
  ['A little room in Nolita', 'Nolita', -73.9957, 40.7234, 13500, 4.4, 2],
  ['Bowery light-filled loft', 'Lower East Side', -73.9926, 40.7220, 22500, 4.9, 4],
  ['Orchard Street apartment', 'Lower East Side', -73.9895, 40.7195, 18000, 4.6, 3],
  ['City-view corner suite', 'Civic Center', -74.0034, 40.7135, 32000, 4.9, 4],
  ['Tribeca family retreat', 'Tribeca', -74.0093, 40.7188, 28500, 4.8, 6],
  ['Hudson-side townhouse', 'Tribeca', -74.0101, 40.7251, 39000, 5.0, 6],
  ['Chinatown morning light', 'Chinatown', -73.9983, 40.7163, 12500, 4.3, 2],
  ['Seaport brick studio', 'Seaport', -74.0016, 40.7083, 19500, 4.7, 2],
  ['Wall Street weekend', 'Financial District', -74.0091, 40.7069, 26000, 4.8, 4],
  ['Broadway city nest', 'Financial District', -74.0120, 40.7107, 15500, 4.5, 2],
  ['Greenwich reading nook', 'Greenwich Village', -74.0022, 40.7310, 20500, 4.9, 2],
  ['Bleecker Street home', 'Greenwich Village', -74.0064, 40.7320, 27500, 4.8, 4],
  ['East Village artist loft', 'East Village', -73.9868, 40.7265, 21500, 4.6, 3],
  ['Second Avenue studio', 'East Village', -73.9879, 40.7301, 14500, 4.4, 2],
  ['Ludlow two-bedroom', 'Lower East Side', -73.9881, 40.7165, 23500, 4.7, 4],
  ['West Village pied-à-terre', 'West Village', -74.0093, 40.7355, 29500, 4.9, 2],
  ['NoHo sunny escape', 'NoHo', -73.9938, 40.7284, 18500, 4.5, 2],
];

export const listings: Listing[] = rows.map(
  ([title, neighborhood, longitude, latitude, priceMinor, rating, guests], index) => ({
    id: `sample-${index + 1}`, title, neighborhood, position: [longitude, latitude],
    priceMinor, currency: 'USD', rating, guests,
    propertyType: (['loft', 'house', 'townhouse', 'apartment'] as const)[index % 4],
  }),
);

// Render-only stress fixture, deliberately separate from M2's future validated geography/data.
// A deterministic grid stresses 300 instances without cloning meshes or claiming real locations.
export const stressMode = new URLSearchParams(window.location.search).get('benchmark') === '300';
export const mapListings: Listing[] = stressMode ? Array.from({ length: 300 }, (_, index) => ({
  ...listings[index % listings.length], id: `stress-${index}`,
  title: `Render test ${index + 1}`,
  position: [-74.019 + (index % 20) * 0.0018, 40.708 + Math.floor(index / 20) * 0.0018],
})) : listings;

export const currencyCode = (import.meta.env.VITE_CURRENCY_CODE || 'USD').toUpperCase();
// Refuse relabeling: changing USD to EUR without converting/reseeding is incorrect money handling.
export const currencyError = currencyCode !== 'USD'
  ? 'M1 fixtures are USD cents. Set VITE_CURRENCY_CODE=USD; configurable datasets arrive in M2.'
  : null;
const formatter = new Intl.NumberFormat('en-US', {
  style: 'currency', currency: 'USD', maximumFractionDigits: 0,
});
export const price = (listing: Listing) => formatter.format(listing.priceMinor / 100);

export function ratingColor(rating: number): [number, number, number, number] {
  return rating >= 4.8 ? [111, 225, 185, 255]
    : rating >= 4.5 ? [133, 182, 239, 255] : [238, 186, 111, 255];
}


```

## frontend/src/listingLayers.ts

```

import { ScenegraphLayer } from '@deck.gl/mesh-layers';
import { ScatterplotLayer, TextLayer } from '@deck.gl/layers';
import type { PickingInfo } from '@deck.gl/core';
import { mapListings, price, ratingColor } from './listings';
import type { Listing } from './listings';
import models from './model-manifest.json';

export const MIN_MODEL_PIXELS = 38;
// Stable group arrays let deck.gl retain four shared scenes and instance buffers between updates.
const groups = models.map(model => ({ model, data: mapListings.filter(d => d.propertyType === model.type) }));
const byType = Object.fromEntries(models.map(model => [model.type, model]));
type Options = {
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
  const { selectedId, hoveredId, zoom, latitude } = options;
  const active = (d: Listing) => d.id === selectedId || d.id === hoveredId;
  // Match ScenegraphLayer's meter-to-pixel clamp for the ground rings and tag altitude.
  // At close zoom the actual model width wins; at city zoom the symbol is exaggerated.
  const metersPerPixel = 40075016.686 * Math.cos(latitude * Math.PI / 180) / (512 * 2 ** zoom);
  const width = (d: Listing) => Math.max(byType[d.propertyType].widthMeters, MIN_MODEL_PIXELS * metersPerPixel);
  const lift = (d: Listing) => active(d) ? 5 : 0;
  const triggers = [zoom, latitude, selectedId, hoveredId];
  const events = { onHover: options.onHover, onClick: options.onClick };
  return [
    // Three translucent concentric strokes approximate a soft glow without a bloom framebuffer.
    ...[0, 1, 2].map(index => new ScatterplotLayer<Listing>({
      id: `rating-halo-${index}`, data: mapListings, getPosition: d => d.position,
      radiusUnits: 'meters', getRadius: d => width(d) * (0.73 + index * 0.08),
      filled: index === 0, stroked: true, billboard: false,
      getFillColor: d => [...ratingColor(d.rating).slice(0, 3), active(d) ? 45 : 20] as [number, number, number, number],
      getLineColor: d => [...ratingColor(d.rating).slice(0, 3), [220, 65, 22][index]] as [number, number, number, number],
      lineWidthUnits: 'pixels', getLineWidth: d => index === 0 ? (active(d) ? 3 : 1.6) : 5,
      // The center also picks: a building is still selectable through a gap in its mesh.
      pickable: index === 0, ...events,
      parameters: { depthWriteEnabled: false },
      updateTriggers: { getRadius: triggers, getFillColor: triggers, getLineWidth: triggers },
    })),
    ...groups.map(({ model, data }) => new ScenegraphLayer<Listing>({
      id: `property-${model.type}`, data, scenegraph: model.url,
      sizeScale: model.widthMeters, sizeMinPixels: MIN_MODEL_PIXELS,
      // Export already centers the footprint and rotates Y-up to Z-up; no runtime axis guesswork.
      getPosition: d => [d.position[0], d.position[1], lift(d)],
      getScale: d => { const scale = active(d) ? 1.12 : 1; return [scale, scale, scale]; },
      getOrientation: [0, 28, 0], getColor: [255, 255, 255, 255],
      // Kenney's palette already separates roof/facade details. Flat textured lighting
      // keeps that crisp toy-city look and avoids PBR shading cost on integrated GPUs.
      _lighting: 'flat', pickable: true, ...events,
      // Matrix/scale accessors don't transition in 9.4; GPU position transitions provide the lift.
      transitions: { getPosition: options.reducedMotion ? 0 : 260 },
      updateTriggers: { getPosition: [selectedId, hoveredId], getScale: [selectedId, hoveredId] },
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
      data: mapListings.filter(d => options.labelIds.has(d.id) || active(d)),
      getPosition: d => [d.position[0], d.position[1], width(d) * byType[d.propertyType].heightRatio * (active(d) ? 1.12 : 1) + lift(d)],
      getText: price, getSize: 12, sizeUnits: 'pixels', billboard: true,
      fontFamily: 'Arial, sans-serif', fontWeight: 700, characterSet: '$0123456789,',
      getPixelOffset: [0, -15], getTextAnchor: 'middle', getAlignmentBaseline: 'bottom',
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



```

## frontend/src/MapScene.tsx

```

import { useCallback, useEffect, useRef, useState } from 'react';
import { Map, NavigationControl, AttributionControl, setWorkerUrl } from 'maplibre-gl';
import workerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url';
import { MapLibreOverlay } from '@deck.gl/maplibre';
import type { PickingInfo } from '@deck.gl/core';
import { mapListings, price, stressMode } from './listings';
import type { Listing } from './listings';
import { listingLayers } from './listingLayers';
import { RenderMeter } from './performance';
import type { BenchmarkResult } from './performance';

// Vite emits the worker as a same-origin asset, including in the production build.
setWorkerUrl(workerUrl);
const STYLE = 'https://tiles.openfreemap.org/styles/dark';
const BUILDINGS = 'stayscape-buildings';
const HOME = { center: [-74.0004, 40.7218] as [number, number], zoom: 14.3, pitch: 54, bearing: -20 };
const reducedMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;

type Props = {
  selected: Listing | null;
  onSelect: (listing: Listing | null) => void;
};

export default function MapScene({ selected, onSelect }: Props) {
  const container = useRef<HTMLDivElement>(null);
  const mapRef = useRef<Map | null>(null);
  const overlayRef = useRef<MapLibreOverlay | null>(null);
  const meter = useRef(new RenderMeter());
  const modelStarted = useRef(0);
  const drawnModels = useRef(new Set<string>());
  const benchmarkTimer = useRef<number | undefined>(undefined);
  const selectRef = useRef(onSelect);
  selectRef.current = onSelect;
  const [ready, setReady] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [buildingCount, setBuildingCount] = useState(0);
  const [renderedBuildings, setRenderedBuildings] = useState(0);
  const [buildingsVisible, setBuildingsVisible] = useState(true);
  const [zoom, setZoom] = useState(HOME.zoom);
  const [retry, setRetry] = useState(0);
  const [modelsLoaded, setModelsLoaded] = useState(0);
  const [modelLoadMs, setModelLoadMs] = useState(0);
  const [labelIds, setLabelIds] = useState(new Set(mapListings.map(d => d.id)));
  const [benchmark, setBenchmark] = useState<BenchmarkResult | null>(null);
  const [measuring, setMeasuring] = useState(false);
  const [hover, setHover] = useState<{ listing: Listing; x: number; y: number; layer: string } | null>(null);

  useEffect(() => {
    if (!container.current) return;
    setReady(false);
    setError(null);
    setBuildingCount(0);
    setRenderedBuildings(0);
    setHover(null);
    drawnModels.current.clear();
    setModelsLoaded(0);
    let map: Map;
    try {
      map = new Map({
        container: container.current, style: STYLE, ...HOME,
        maxPitch: 70, minZoom: 11, maxZoom: 18,
        // Cap raster work on high-DPI screens; both canvases use the same practical quality cap.
        pixelRatio: Math.min(devicePixelRatio, 1.5),
        canvasContextAttributes: { antialias: true }, attributionControl: false,
      });
    } catch {
      setError('Could not start WebGL2. Enable browser graphics acceleration and retry.');
      return;
    }
    mapRef.current = map;
    map.addControl(new NavigationControl({ visualizePitch: true }), 'top-right');
    // Keep provider attribution visible; it also belongs in later screenshots and GIFs.
    map.addControl(new AttributionControl({ compact: false }), 'bottom-right');
    const timeout = window.setTimeout(() => {
      setError('The map is taking too long to load. Check your connection and retry.');
    }, 25_000);
    map.on('error', () => setError('A map resource failed to load. Check your connection and retry.'));
    map.on('load', () => {
      window.clearTimeout(timeout);
      if (!map.getSource('openmaptiles')) {
        setError('The provider style changed: the expected building source is missing.');
        return;
      }
      // Use the provider source already loaded by the basemap, avoiding duplicate tile requests.
      // Put buildings below labels. Heights are OSM-derived, not surveyed rental dimensions.
      const label = map.getStyle().layers.find(layer => layer.type === 'symbol')?.id;
      map.addLayer({
        id: BUILDINGS, type: 'fill-extrusion', source: 'openmaptiles',
        'source-layer': 'building', minzoom: 13,
        filter: ['!=', ['get', 'hide_3d'], true],
        paint: {
          'fill-extrusion-color': '#3d525c',
          'fill-extrusion-height': ['coalesce', ['get', 'render_height'], 9],
          'fill-extrusion-base': ['coalesce', ['get', 'render_min_height'], 0],
          'fill-extrusion-opacity': 0.42,
        },
      }, label);
      const overlay = new MapLibreOverlay({
        // Listings are 3D map symbols: a separate depth buffer prevents basemap roofs hiding them.
        // MapLibre still owns the camera. Depth sorting remains correct between listing models.
        interleaved: false, useDevicePixels: Math.min(devicePixelRatio, 1.5),
        onAfterRender: meter.current.onDraw,
        onError: () => setError('The listing renderer failed. Check WebGL2 support and retry.'),
      });
      map.addControl(overlay);
      overlayRef.current = overlay;
      modelStarted.current = performance.now();
      // Read at load too: a busy shared renderer may delay MapLibre's idle event.
      setBuildingCount(map.querySourceFeatures('openmaptiles', { sourceLayer: 'building' }).length);
      declutterLabels();
      setReady(true);
      setError(null);
    });
    map.on('movestart', () => setHover(null));
    // Shader pixel clamps follow every camera frame. Only matching ring/tag geometry needs JS zoom.
    map.on('zoom', () => setZoom(map.getZoom()));
    const declutterLabels = () => {
      const occupied = new Set<string>();
      const ids = new Set<string>();
      for (const listing of mapListings) {
        const p = map.project(listing.position);
        const key = `${Math.floor(p.x / 65)},${Math.floor(p.y / 45)}`;
        if (!occupied.has(key)) { occupied.add(key); ids.add(listing.id); }
      }
      setLabelIds(ids);
    };
    map.on('moveend', () => { setZoom(map.getZoom()); declutterLabels(); });
    map.on('idle', () => {
      if (map.getLayer(BUILDINGS)) {
        // This reports loaded tile features, not a deduplicated count of real-world buildings.
        setBuildingCount(map.querySourceFeatures('openmaptiles', { sourceLayer: 'building' }).length);
        setRenderedBuildings(map.queryRenderedFeatures({ layers: [BUILDINGS] }).length);
      }
    });
    const resize = new ResizeObserver(() => map.resize());
    resize.observe(container.current);
    return () => {
      // React StrictMode mounts twice in development; cleanup prevents duplicate WebGL contexts.
      window.clearTimeout(timeout);
      window.clearTimeout(benchmarkTimer.current);
      resize.disconnect();
      overlayRef.current = null;
      mapRef.current = null;
      map.remove();
    };
  }, [retry]);

  const onHover = useCallback((info: PickingInfo<Listing>) => {
    setHover(info.object ? { listing: info.object, x: info.x, y: info.y, layer: info.layer?.id ?? '' } : null);
    if (mapRef.current) mapRef.current.getCanvas().style.cursor = info.object ? 'pointer' : '';
  }, []);
  const onClick = useCallback((info: PickingInfo<Listing>) => {
    if (info.object) selectRef.current(info.object);
  }, []);
  const onModelDraw = useCallback((type: string) => {
    drawnModels.current.add(type);
    setModelsLoaded(drawnModels.current.size);
    if (drawnModels.current.size === 4) setModelLoadMs(performance.now() - modelStarted.current);
  }, []);
  useEffect(() => {
    if (!ready || !overlayRef.current) return;
    overlayRef.current.setProps({ layers: listingLayers({
      selectedId: selected?.id, hoveredId: hover?.listing.id, zoom,
      latitude: mapRef.current?.getCenter().lat ?? HOME.center[1], labelIds,
      reducedMotion: reducedMotion(), onHover, onClick, onModelDraw,
    }) });
  }, [ready, selected, hover?.listing.id, zoom, labelIds, onHover, onClick, onModelDraw]);

  useEffect(() => {
    if (!ready || !selected) return;
    mapRef.current?.flyTo({
      center: selected.position, zoom: 15.6, pitch: 58,
      duration: reducedMotion() ? 0 : 1600,
    });
  }, [ready, selected]);

  useEffect(() => {
    const map = mapRef.current;
    if (ready && map?.getLayer(BUILDINGS)) {
      map.setLayoutProperty(BUILDINGS, 'visibility', buildingsVisible ? 'visible' : 'none');
    }
  }, [ready, buildingsVisible]);

  function reset() {
    onSelect(null);
    mapRef.current?.flyTo({ ...HOME, duration: reducedMotion() ? 0 : 1600 });
  }

  function runBenchmark() {
    const map = mapRef.current;
    const canvas = overlayRef.current?.getCanvas();
    if (!map || !canvas || measuring) return;
    const gl = canvas.getContext('webgl2');
    const extension = gl?.getExtension('WEBGL_debug_renderer_info');
    const renderer = extension ? String(gl?.getParameter(extension.UNMASKED_RENDERER_WEBGL)) : 'unavailable';
    setMeasuring(true);
    meter.current.start();
    const started = performance.now();
    map.easeTo({ bearing: map.getBearing() + 75, duration: 8000, easing: x => x, essential: true });
    benchmarkTimer.current = window.setTimeout(() => {
      setBenchmark(meter.current.finish(mapListings.length, started, renderer));
      setMeasuring(false);
    }, 8000);
  }

  return <section className="map-shell" aria-label="Interactive New York listing map">
    <div ref={container} className="map-canvas" data-testid="map" data-zoom={zoom}
      data-building-count={buildingCount} data-rendered-buildings={renderedBuildings} data-hover-layer={hover?.layer}
      data-models-loaded={modelsLoaded} data-model-load-ms={modelLoadMs} data-instance-count={mapListings.length} />
    <div className="map-heading"><span className="live-dot" /> NEW YORK CITY <span>40.72° N / 74.00° W</span></div>
    <div className="map-actions">
      <button onClick={reset} disabled={!ready}>↗ Reset view</button>
      <button onClick={() => setBuildingsVisible(value => !value)} disabled={!ready}
        aria-pressed={buildingsVisible}>3D buildings {buildingsVisible ? 'on' : 'off'}</button>
    </div>
    {stressMode && <div className="benchmark-panel">
      <strong>300-instance render stress test</strong>
      <span>Render-only grid · not generated rental data</span>
      <button disabled={modelsLoaded < 4 || measuring} onClick={runBenchmark}>
        {measuring ? 'Measuring camera orbit…' : 'Measure 8-second orbit'}</button>
      {benchmark && <pre data-testid="benchmark-result">{JSON.stringify(benchmark, null, 2)}</pre>}
    </div>}
    {!ready && !error && <div className="map-message" role="status">Loading New York…</div>}
    {error && <div className="map-message error" role="alert">
      <p>{error}</p><button onClick={() => setRetry(value => value + 1)}>Retry map</button>
    </div>}
    {hover && <div className="hover-card" role="tooltip" style={{
      left: Math.max(8, Math.min(hover.x + 16, (container.current?.clientWidth ?? 600) - 248)),
      top: Math.max(8, Math.min(hover.y + 16, (container.current?.clientHeight ?? 600) - 130)),
    }}>
      <span className="eyebrow">{hover.listing.neighborhood}</span>
      <strong>{hover.listing.title}</strong>
      <span>{price(hover.listing)} / night <b>★ {hover.listing.rating.toFixed(1)}</b></span>
      <small>Click to explore this stay</small>
    </div>}
    <div className="legend">
      <span className="eyebrow">A different perspective</span>
      <strong>A little home. A new perspective.</strong>
      <div className="rating-key"><span><i className="gold" />4.0–4.4</span>
        <span><i className="blue" />4.5–4.7</span><span><i className="mint" />4.8–5.0</span></div>
      <small>Ring = rating · Tag = USD / night · Model = property type</small>
    </div>
    <div className="map-hint" role="status">
      {ready ? (modelsLoaded === 4 ? 'Four local model styles loaded' : 'Loading local 3D homes…') : 'Connecting…'}
      <span>Drag to pan · Scroll to zoom · Right-drag to tilt</span>
    </div>
  </section>;
}


```

## frontend/src/App.tsx

```

import { useState } from 'react';
import MapScene from './MapScene';
import { currencyError, mapListings, price, ratingColor, stressMode } from './listings';
import type { Listing } from './listings';

export default function App() {
  const [selected, setSelected] = useState<Listing | null>(null);
  // Selecting the same stay again should re-center after the user has panned away.
  const selectListing = (listing: Listing | null) => setSelected(listing ? { ...listing } : null);
  if (currencyError) return <main className="config-error" role="alert">{currencyError}</main>;
  return <main className="app">
    <aside className="sidebar">
      <header className="brand"><span className="brand-mark">S</span><span>StayScape<small>A NEW POINT OF VIEW</small></span></header>
      <div className="intro"><span className="eyebrow">THE NEW YORK COLLECTION</span>
        <h1>Find your<br /><em>city escape.</em></h1>
        <p>A neighborhood. A new perspective.<br />Explore your next stay in three dimensions.</p>
      </div>
      <div className="collection-heading"><strong>{stressMode ? '300 render-test instances' : '20 places to imagine'}</strong><span>USD / night</span></div>
      <div className="listing-list" aria-label="Synthetic listings">
        {mapListings.slice(0, 20).map((listing, index) => <button key={listing.id}
          className={`listing-row ${selected?.id === listing.id ? 'selected' : ''}`}
          aria-pressed={selected?.id === listing.id} onClick={() => selectListing(listing)}>
          <span className="model-thumbnail"><img src={`/models/${listing.propertyType}.png`} alt="" />
            <i style={{ background: `rgb(${ratingColor(listing.rating).slice(0, 3).join(',')})` }} /></span>
          <span className="listing-copy"><strong>{listing.title}</strong><small>{listing.propertyType} · ★ {listing.rating.toFixed(1)}</small></span>
          <span className="listing-price">{price(listing)}<small>↗</small></span>
        </button>)}
      </div>
      {selected ? <section className="selection" aria-label="Selected listing" aria-live="polite">
        <div><span className="eyebrow">YOUR MAP PICK</span><button aria-label="Close selected listing" onClick={() => setSelected(null)}>×</button></div>
        <h2>{selected.title}</h2><p>{selected.neighborhood} · Up to {selected.guests} guests</p>
        <strong>{price(selected)} <small>USD / night</small><span>★ {selected.rating.toFixed(1)}</span></strong>
      </section> : <div className="sidebar-tip">↗ Hover a home to get a feel for it.<br />Select a stay to take a closer look.</div>}
      <footer><span className="live-dot" /> M1.5 MODEL EXPLORER <span>All stays are synthetic.</span></footer>
    </aside>
    <MapScene selected={selected} onSelect={selectListing} />
  </main>;
}


```

## frontend/src/styles.css

```

/* System fonts avoid external font requests in this spike. */
:root { font-family: Inter, ui-sans-serif, system-ui, -apple-system, sans-serif; color: #e9eeeb; background: #111820; font-synthesis: none; }
* { box-sizing: border-box; }
body { margin: 0; }
button { font: inherit; color: inherit; cursor: pointer; }
button:disabled { opacity: .5; cursor: wait; }
button:focus-visible { outline: 2px solid #a0f2cf; outline-offset: -3px; }
.app { display: grid; grid-template-columns: 350px minmax(0, 1fr); height: 100dvh; min-height: 560px; }
.sidebar { display: flex; flex-direction: column; background: #141c24; border-right: 1px solid #303a42; min-height: 0; z-index: 2; }
.brand { display: flex; align-items: center; gap: 11px; padding: 28px 26px 20px; font-size: 23px; font-weight: 700; letter-spacing: -.8px; }
.brand-mark { display: grid; place-items: center; border: 1px solid #a4e5c7; color: #b9f0d7; width: 36px; height: 40px; border-radius: 12px 3px 12px 3px; font-family: Georgia, serif; }
.brand small { display: block; color: #87998f; font-size: 8px; letter-spacing: 2.4px; margin-top: 2px; }
.intro { padding: 20px 26px 23px; }
.eyebrow { color: #9aaea7; font-size: 9px; font-weight: 650; letter-spacing: 1.7px; }
h1 { font-family: Georgia, serif; font-weight: 400; font-size: 44px; line-height: 1.03; letter-spacing: -1.8px; margin: 15px 0; }
h1 em { color: #b7e9cf; font-weight: 400; }
.intro p { color: #91a0a8; font-size: 12px; line-height: 1.8; margin: 0; }
.collection-heading { display: flex; justify-content: space-between; padding: 15px 26px; border-block: 1px solid #2a343c; font-size: 11px; }
.collection-heading span { color: #8e9ba4; font-size: 10px; }
.listing-list { flex: 1; overflow-y: auto; min-height: 100px; scrollbar-width: thin; scrollbar-color: #45574f transparent; }
.listing-row { display: flex; width: 100%; align-items: center; gap: 12px; border: 0; border-bottom: 1px solid #253039; background: transparent; padding: 18px 23px; text-align: left; }
.listing-row:hover, .listing-row.selected { background: #20332f; }
.listing-row.selected { box-shadow: inset 3px 0 #a0e8c7; }
.listing-number { font-size: 10px; font-variant-numeric: tabular-nums; }
.listing-copy { flex: 1; min-width: 0; }
.listing-copy strong { display: block; font-size: 11px; font-weight: 550; }
.listing-copy small { display: block; color: #8b9ba3; font-size: 10px; margin-top: 6px; }
.listing-price { font-size: 12px; text-align: right; }
.listing-price small { display: block; color: #a7c1b3; margin-top: 6px; }
.sidebar-tip { color: #a9b8b5; font-size: 11px; line-height: 1.8; padding: 20px 26px; background: #18252a; }
.sidebar footer { display: flex; align-items: center; gap: 6px; padding: 16px 20px; color: #9caaa9; font-size: 8px; letter-spacing: .6px; }
.sidebar footer > span:last-child { margin-left: auto; letter-spacing: 0; }
.live-dot { display: inline-block; width: 6px; height: 6px; background: #b9eccd; border-radius: 50%; flex-shrink: 0; }
.selection { background: #21352e; padding: 18px 24px; border-top: 1px solid #527163; }
.selection > div { display: flex; justify-content: space-between; align-items: center; }
.selection button { border: 0; background: none; font-size: 21px; }
.selection h2 { font-family: Georgia, serif; font-weight: 400; margin: 10px 0 6px; font-size: 21px; }
.selection p { color: #b6c7be; font-size: 11px; margin: 0 0 16px; }
.selection > strong { font-size: 19px; display: block; }
.selection strong small { font-size: 10px; color: #acc4b7; font-weight: 400; }
.selection strong span { float: right; font-size: 12px; margin-top: 5px; }
.map-shell { position: relative; min-width: 0; background: #101417; overflow: hidden; }
/* Isolate deck's positioned canvas so it cannot paint over React's map controls/cards. */
.map-canvas { position: absolute; inset: 0; z-index: 0; }
.map-heading { position: absolute; top: 27px; left: 25px; display: flex; align-items: center; gap: 9px; font-size: 10px; letter-spacing: 1.5px; background: #141c24ed; border: 1px solid #35413f; padding: 13px 15px; border-radius: 4px; pointer-events: none; }
.map-heading > span:last-child { color: #859991; font-size: 8px; margin-left: 16px; }
.map-actions { position: absolute; top: 82px; left: 25px; display: flex; gap: 8px; }
.map-actions button, .map-message button { background: #17242cec; border: 1px solid #475951; border-radius: 4px; padding: 9px 12px; font-size: 11px; }
.legend { position: absolute; bottom: 77px; left: 25px; background: #141e26f2; border: 1px solid #3c4b49; border-radius: 6px; padding: 17px 19px; pointer-events: none; }
.legend > strong { display: block; font-family: Georgia, serif; font-size: 18px; font-weight: 400; margin: 8px 0 15px; }
.rating-key { display: flex; gap: 17px; font-size: 10px; color: #c9d5d0; }
.rating-key i { display: inline-block; width: 7px; height: 12px; margin-right: 6px; border-radius: 2px; vertical-align: middle; }
.gold { background: #eeba6f; }.blue { background: #85b6ef; }.mint { background: #6fe1b9; }
.legend > small { display: block; color: #95a6a5; font-size: 9px; margin-top: 12px; }
.map-hint { position: absolute; left: 25px; bottom: 35px; color: #b6c7bd; font-size: 9px; text-shadow: 0 1px 5px #000; pointer-events: none; }
.map-hint span { display: block; color: #a6b0b3; margin-top: 5px; }
.hover-card { position: absolute; z-index: 5; width: 240px; padding: 14px 16px; border-radius: 7px; color: #192923; background: #f0f6ee; box-shadow: 0 8px 35px #0005; pointer-events: none; }
.hover-card .eyebrow { color: #4f6a5b; font-size: 8px; }
.hover-card strong { display: block; margin: 6px 0 10px; font-size: 13px; }
.hover-card > span:not(.eyebrow) { font-size: 12px; }.hover-card b { float: right; }
.hover-card small { display: block; margin-top: 9px; color: #63766a; font-size: 10px; }
.map-message { position: absolute; top: 40%; left: 50%; transform: translateX(-50%); width: min(360px, 90%); padding: 20px; background: #15252ef5; border: 1px solid #54776a; border-radius: 8px; font-size: 13px; text-align: center; z-index: 6; }
.map-message.error { border-color: #d9a47b; }.map-message p { margin-top: 0; line-height: 1.6; }
.maplibregl-ctrl-attrib { font-size: 9px !important; background: #e7ece3e8 !important; }
.maplibregl-ctrl-top-right { top: 16px; right: 10px; }
.config-error { margin: 50px; padding: 25px; border: 1px solid #d9a47b; }
.model-thumbnail { width: 44px; height: 44px; display: grid; place-items: center; flex-shrink: 0; background: #293a41; border-radius: 10px; position: relative; }
.model-thumbnail img { width: 48px; height: 48px; object-fit: contain; }
.model-thumbnail i { width: 6px; height: 6px; border-radius: 50%; position: absolute; right: 3px; bottom: 3px; }
.listing-row { padding: 13px 20px; gap: 10px; }
.hover-card { animation: card-appear 160ms ease-out; }
@keyframes card-appear { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
@media (prefers-reduced-motion: reduce) { .hover-card { animation: none; } }
.benchmark-panel { position: absolute; top: 135px; left: 25px; padding: 14px; background: #14252fef; border: 1px solid #608176; border-radius: 6px; z-index: 4; font-size: 11px; max-width: calc(100% - 80px); }
.benchmark-panel strong, .benchmark-panel span { display: block; margin-bottom: 8px; }
.benchmark-panel button { border: 1px solid #80b398; border-radius: 4px; padding: 8px; background: #294638; }
.benchmark-panel pre { white-space: pre-wrap; font-size: 10px; max-width: 340px; }
@media (max-width: 760px) {
  .app { grid-template-columns: 1fr; grid-template-rows: 58dvh auto; height: auto; min-height: 100dvh; }
  .map-shell { grid-row: 1; min-height: 380px; }
  .sidebar { border-right: 0; }.brand { padding: 20px 22px 10px; }
  .intro { padding: 10px 22px 20px; }h1 { font-size: 36px; }h1 br { display: none; }h1 em { margin-left: 8px; }
  .intro p { display: none; }.listing-list { max-height: 270px; flex: auto; }
  .map-heading { top: 15px; left: 12px; padding: 11px; }.map-heading > span:last-child { display: none; }
  .map-actions { top: 61px; left: 12px; }.map-actions button { font-size: 10px; padding: 8px; }
  .legend { left: 12px; bottom: 64px; padding: 12px; }.legend > strong { font-size: 15px; margin: 6px 0 10px; }
  .legend > small { font-size: 8px; }.map-hint { left: 12px; bottom: 28px; font-size: 8px; }
}


```

## frontend/src/performance.ts

```

export type BenchmarkResult = {
  instances: number; seconds: number; deckFrames: number; averageFps: number;
  p95FrameMs: number; renderer: string; viewport: string;
};

// Count actual deck draw callbacks during camera motion, not an idle requestAnimationFrame loop.
export class RenderMeter {
  frames: number[] = [];
  running = false;
  onDraw = () => { if (this.running) this.frames.push(performance.now()); };
  start() { this.frames = []; this.running = true; }
  finish(instances: number, started: number, renderer: string): BenchmarkResult {
    this.running = false;
    const seconds = (performance.now() - started) / 1000;
    const gaps = this.frames.slice(1).map((t, i) => t - this.frames[i]).sort((a, b) => a - b);
    return { instances, seconds: +seconds.toFixed(2), deckFrames: this.frames.length,
      averageFps: +(this.frames.length / seconds).toFixed(1),
      p95FrameMs: +(gaps[Math.floor(gaps.length * 0.95)] || 0).toFixed(1),
      renderer, viewport: `${innerWidth}×${innerHeight} @ DPR ${devicePixelRatio} (render cap 1.5)`,
    };
  }
}


```

## frontend/src/model-manifest.json

```

[
  {
    "type": "apartment",
    "pack": "commercial",
    "source": "building-f.glb",
    "url": "/models/apartment.glb",
    "widthMeters": 16,
    "heightRatio": 1.6436890614967037,
    "bytes": 110508,
    "originalBytes": 148952,
    "gzipBytes": 31539,
    "triangles": 1794,
    "primitives": 1,
    "sha256": "302fcda7a7330dff2aaee127f144abc80600315d3852c6da424a60462b8d0707"
  },
  {
    "type": "townhouse",
    "pack": "suburban",
    "source": "building-type-k.glb",
    "url": "/models/townhouse.glb",
    "widthMeters": 10,
    "heightRatio": 1.1270551331287297,
    "bytes": 68072,
    "originalBytes": 89152,
    "gzipBytes": 25678,
    "triangles": 1024,
    "primitives": 1,
    "sha256": "7e618bea3ad5e7f7173e2586ad7d2eaeb21009bc4ab5866531c60f1f43cf6d0d"
  },
  {
    "type": "house",
    "pack": "suburban",
    "source": "building-type-a.glb",
    "url": "/models/house.glb",
    "widthMeters": 13,
    "heightRatio": 0.6411853897089368,
    "bytes": 76208,
    "originalBytes": 98604,
    "gzipBytes": 26868,
    "triangles": 1174,
    "primitives": 1,
    "sha256": "e3037dce405a968c11d12287ac422173b3ba700c68103f9e718fbb2fe0c40573"
  },
  {
    "type": "loft",
    "pack": "industrial",
    "source": "building-a.glb",
    "url": "/models/loft.glb",
    "widthMeters": 20,
    "heightRatio": 0.7055136896072611,
    "bytes": 123980,
    "originalBytes": 177316,
    "gzipBytes": 37498,
    "triangles": 2046,
    "primitives": 1,
    "sha256": "62307d1567865731eeb2981cdf1bada5045e59a2f9dad18026f81e6a725290bd"
  }
]


```

## frontend/scripts/prepare-models.mjs

```

import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { dedup, prune, weld, flatten, join, getBounds } from '@gltf-transform/functions';
import { mkdir, readFile, copyFile, writeFile, stat } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { gzipSync } from 'node:zlib';

// Offline only. Runtime serves these four checked-in files, never remote model URLs.
const sources = [
  ['apartment', 'commercial', 'building-f', 16],
  ['townhouse', 'suburban', 'building-type-k', 10],
  ['house', 'suburban', 'building-type-a', 13],
  ['loft', 'industrial', 'building-a', 20],
];
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
await mkdir('public/models/licenses', { recursive: true });
const manifest = [];
for (const [type, pack, name, widthMeters] of sources) {
  const source = `.asset-cache/${pack}/Models/GLB format/${name}.glb`;
  const doc = await io.read(source);
  // These packs use only an identity UV transform. Remove that redundant extension
  // so loaders.gl needn't synthesize a second UV channel for luma's material parser.
  for (const material of doc.getRoot().listMaterials()) {
    const info = material.getBaseColorTextureInfo();
    const transform = info?.getExtension('KHR_texture_transform');
    if (transform) {
      if (transform.getRotation() !== 0 || transform.getOffset().some(v => v !== 0) ||
          transform.getScale().some(v => v !== 1) || (transform.getTexCoord() ?? 0) !== 0) {
        throw new Error('Non-identity texture transform requires UV baking');
      }
      transform.dispose();
    }
  }
  for (const extension of doc.getRoot().listExtensionsUsed()) {
    if (extension.extensionName === 'KHR_texture_transform') extension.dispose();
  }
  await doc.transform(dedup(), flatten(), join(), weld(), prune());
  const scene = doc.getRoot().listScenes()[0];
  const { min, max } = getBounds(scene);
  const width = Math.max(max[0] - min[0], max[2] - min[2]);
  const s = 1 / width;
  // Bake glTF Y-up into deck.gl Z-up, center X/Y, and place the base at Z=0.
  // One unit now means the footprint width, so pixel clamps are consistent across models.
  const root = doc.createNode('StayScape Z-up normalized marker').setMatrix([
    s, 0, 0, 0, 0, 0, s, 0, 0, -s, 0, 0,
    -(min[0] + max[0]) * s / 2, (min[2] + max[2]) * s / 2, -min[1] * s, 1,
  ]);
  for (const node of [...scene.listChildren()]) root.addChild(node);
  scene.addChild(root);
  await doc.transform(flatten(), join(), dedup(), prune());
  const target = `public/models/${type}.glb`;
  await io.write(target, doc);
  const bytes = await readFile(target);
  let triangles = 0;
  let primitives = 0;
  for (const mesh of doc.getRoot().listMeshes()) for (const primitive of mesh.listPrimitives()) {
    primitives++;
    triangles += (primitive.getIndices()?.getCount() ?? primitive.getAttribute('POSITION').getCount()) / 3;
  }
  manifest.push({ type, pack, source: `${name}.glb`, url: `/models/${type}.glb`,
    widthMeters, heightRatio: (max[1] - min[1]) / width,
    bytes: bytes.length, originalBytes: (await stat(source)).size,
    gzipBytes: gzipSync(bytes).length, triangles, primitives,
    sha256: createHash('sha256').update(bytes).digest('hex'),
  });
  await copyFile(`.asset-cache/${pack}/License.txt`, `public/models/licenses/${pack}.txt`);
  await copyFile(`.asset-cache/${pack}/Previews/${name}.png`, `public/models/${type}.png`);
}
await writeFile('src/model-manifest.json', JSON.stringify(manifest, null, 2) + '\n');
console.table(manifest.map(({ type, bytes, originalBytes, gzipBytes, triangles, primitives }) =>
  ({ type, bytes, originalBytes, gzipBytes, triangles, primitives })));


```

## frontend/tests/map.spec.ts

```

import { expect, test } from '@playwright/test';

test('local GLBs, real tiles, model picking, selection, and reset', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => {
    if (message.type() === 'error' || message.type() === 'warning') console.info('Browser:', message.text());
  });
  await page.goto('/');
  await expect(page.locator('.listing-row')).toHaveCount(20);
  const map = page.getByTestId('map');
  // A style loading is insufficient: actual NYC building tile features must be present.
  await expect.poll(async () => Number(await map.getAttribute('data-building-count')),
    { timeout: 90_000 }).toBeGreaterThan(0);
  await expect(page.getByRole('alert')).toHaveCount(0);
  await expect(map).toHaveAttribute('data-models-loaded', '4', { timeout: 90_000 });
  await expect.poll(async () => Number(await map.getAttribute('data-rendered-buildings')),
    { timeout: 90_000 }).toBeGreaterThan(0);
  console.info('NYC tile building features:', await map.getAttribute('data-building-count'),
    'rendered building features:', await map.getAttribute('data-rendered-buildings'));
  await page.screenshot({ path: 'test-results/m1-5-desktop.png' });
  await page.getByRole('button', { name: /Canal Street loft/ }).click();
  await expect(page.getByRole('region', { name: 'Selected listing' })).toContainText('Canal Street loft');
  await expect.poll(async () => Number(await map.getAttribute('data-zoom'))).toBeCloseTo(15.6, 1);
  // Exercise real GPU picking, not a mocked callback: models, rings and tags share the listing ID.
  const box = (await map.boundingBox())!;
  let picked = false;
  let pickedPosition = { x: 0, y: 0 };
  let hoveredTitle = '';
  for (let y = box.height / 2 - 15; y >= box.height / 2 - 180 && !picked; y -= 15) {
    for (const x of [box.width / 2, box.width / 2 - 24, box.width / 2 + 24]) {
      await page.mouse.move(box.x + x, box.y + y);
      // GPU picking and React commit on later frames: don't read the previous pointer's tooltip.
      await page.evaluate(() => new Promise<void>(resolve =>
        requestAnimationFrame(() => requestAnimationFrame(() => resolve()))));
      hoveredTitle = await page.getByRole('tooltip').locator('strong').textContent({ timeout: 250 })
        .catch(() => '') || '';
      if (hoveredTitle && (await map.getAttribute('data-hover-layer'))?.startsWith('property-')) {
        picked = true; pickedPosition = { x: box.x + x, y: box.y + y }; break;
      }
    }
  }
  expect(picked, 'A GLB mesh itself must be pickable, not just its ring or price tag').toBe(true);
  await page.mouse.click(pickedPosition.x, pickedPosition.y);
  await expect(page.getByRole('region', { name: 'Selected listing' })).toContainText(hoveredTitle);
  await page.screenshot({ path: 'test-results/m1-5-selected.png' });
  await page.getByRole('button', { name: '3D buildings on' }).click();
  await expect(page.getByRole('button', { name: '3D buildings off' })).toHaveAttribute('aria-pressed', 'false');
  await page.getByRole('button', { name: '3D buildings off' }).click();
  await page.getByRole('button', { name: 'Reset view' }).click();
  await expect.poll(async () => Number(await map.getAttribute('data-zoom'))).toBeCloseTo(14.3, 1);
  await expect(page.getByRole('region', { name: 'Selected listing' })).toHaveCount(0);
  await expect(page.locator('.maplibregl-ctrl-attrib')).toContainText('OpenStreetMap');
  expect(errors).toEqual([]);
  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({ path: 'test-results/m1-5-mobile.png' });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
});

test('map service failure presents a retry instead of an endless loading state', async ({ page }) => {
  await page.route('https://tiles.openfreemap.org/**', route => route.abort());
  await page.goto('/');
  await expect(page.getByRole('alert')).toContainText('failed');
  await expect(page.getByRole('button', { name: 'Retry map' })).toBeVisible();
});


```

## frontend/tests/performance.spec.ts

```

import { expect, test } from '@playwright/test';
import { writeFile, mkdir } from 'node:fs/promises';

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
  await expect(page.getByTestId('benchmark-result')).toBeVisible({ timeout: 45_000 });
  const result = JSON.parse(await page.getByTestId('benchmark-result').innerText());
  const resources = await page.evaluate(() => performance.getEntriesByType('resource')
    .filter(entry => entry.name.endsWith('.glb')).map(entry => {
      const resource = entry as PerformanceResourceTiming;
      return { url: new URL(resource.name).pathname, durationMs: +resource.duration.toFixed(1),
        transferredBytes: resource.transferSize, decodedBytes: resource.decodedBodySize };
    }));
  const report = { ...result, readyMs, modelPhaseMs: +(await map.getAttribute('data-model-load-ms'))!,
    browser: await page.evaluate(() => navigator.userAgent), resources };
  await mkdir('../docs/evidence', { recursive: true });
  await writeFile('../docs/evidence/m1-5-performance.json', JSON.stringify(report, null, 2));
  console.info(JSON.stringify(report));
  expect(resources).toHaveLength(4); // Four network assets, not 300 repeated model downloads.
  expect(result.deckFrames).toBeGreaterThan(0);
  expect(errors).toEqual([]);
});


```

## frontend/public/models/CREDITS.md

```

# StayScape model credits

Author: **Kenney (https://kenney.nl)**. These are illustrative game models, not
representations of actual rental buildings. No endorsement by Kenney is implied.

Each official pack page was checked on 2026-09-29 and lists **Creative Commons CC0**.
Each downloaded ZIP also contains a matching `License.txt`; copies are preserved
in `licenses/`. CC0 permits modification and commercial redistribution without
mandatory attribution. We retain this credit voluntarily.

License: https://creativecommons.org/publicdomain/zero/1.0/

| Local GLB / preview | Original model | Pack/version | Verified source page |
| --- | --- | --- | --- |
| apartment.glb / apartment.png | building-f | City Kit (Commercial) 2.1 | https://kenney.nl/assets/city-kit-commercial |
| townhouse.glb / townhouse.png | building-type-k | City Kit (Suburban) 2.0 | https://kenney.nl/assets/city-kit-suburban |
| house.glb / house.png | building-type-a | City Kit (Suburban) 2.0 | https://kenney.nl/assets/city-kit-suburban |
| loft.glb / loft.png | building-a | City Kit (Industrial) 2.0 | https://kenney.nl/assets/city-kit-industrial |

Exact downloads used (official Kenney URLs):

- Commercial: https://kenney.nl/media/pages/assets/city-kit-commercial/a742d900eb-1753115042/kenney_city-kit-commercial_2.1.zip
- Suburban: https://kenney.nl/media/pages/assets/city-kit-suburban/2c871b7af2-1745479373/kenney_city-kit-suburban_20.zip
- Industrial: https://kenney.nl/media/pages/assets/city-kit-industrial/0ec35b139d-1788171848/kenney_city-kit-industrial_2.0.zip

Modifications: deduplicated and welded geometry, removed unused resources, combined
compatible primitives, centered footprints, normalized width to one scene unit,
and rotated axes for deck.gl's Z-up coordinates. Redundant identity UV-transform
extensions were removed for loader compatibility. Textures are embedded in each GLB;
original model colors are preserved. The loft is an illustrative adaptive-reuse
industrial building. Preview PNGs are unmodified pack assets.

`src/model-manifest.json` records output SHA-256 hashes, sizes, triangle counts,
source filenames and display dimensions. `scripts/prepare-models.mjs` reproduces
the conversion from locally extracted official downloads. Browsers never hotlink
the models or their textures.

Map tiles are separate assets: preserve the map's OpenFreeMap / OpenMapTiles /
OpenStreetMap attribution. CC0 for these models does not change map-data licensing.


```
