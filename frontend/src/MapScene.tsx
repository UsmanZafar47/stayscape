import { useReducedMotion } from 'framer-motion';
import { useCallback, useEffect, useRef, useState } from 'react';
import { Map, NavigationControl, AttributionControl, setWorkerUrl } from 'maplibre-gl';
import workerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url';
import { MapLibreOverlay } from '@deck.gl/maplibre';
import type { PickingInfo } from '@deck.gl/core';
import { price, stressMode } from './listings';
import type { Listing } from './listings';
import { declutter } from './declutter';
import { useAnimatedListings } from './useAnimatedListings';
import { listingLayers } from './listingLayers';
import { RenderMeter } from './performance';
import type { BenchmarkResult } from './performance';
import type { SearchResult } from './api';

// Vite emits the worker as a same-origin asset, including in the production build.
setWorkerUrl(workerUrl);
const STYLE = 'https://tiles.openfreemap.org/styles/dark';
const BUILDINGS = 'stayscape-buildings';
const HOME = { center: [-74.0004, 40.7218] as [number, number], zoom: 12.7, pitch: 54, bearing: -20 };
const cameraEase = (t: number) => t * t * (3 - 2 * t);

type Props = {
  searchResult?: SearchResult | null;
  listings: Listing[];
  selectionVersion: number;
  selected: Listing | null;
  onSelect: (listing: Listing | null) => void;
};

export default function MapScene({ listings: mapListings, selected, selectionVersion, onSelect, searchResult }: Props) {
  const reduceMotion = useReducedMotion();
  const animated = useAnimatedListings(mapListings);
  const listingsRef = useRef(mapListings);
  listingsRef.current = mapListings;
  const priorityRef = useRef<string[]>([]);
  const declutterRef = useRef<() => void>(() => {});
  const selectedRef = useRef(selected);
  selectedRef.current = selected;
  const previousSelection = useRef<string | undefined>(undefined);
  const container = useRef<HTMLDivElement>(null);
  const mapRef = useRef<Map | null>(null);
  const overlayRef = useRef<MapLibreOverlay | null>(null);
  const meter = useRef(new RenderMeter());
  const declutterTimes = useRef<number[]>([]);
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
  const [labelIds, setLabelIds] = useState(new Set<string>());
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
      // Reduce street-name noise at overview zoom without removing neighborhood labels.
      for (const layer of map.getStyle().layers) {
        if (layer.type === 'symbol' && layer['source-layer'] === 'transportation_name') {
          map.setLayerZoomRange(layer.id, Math.max(layer.minzoom ?? 0, 15), layer.maxzoom ?? 24);
          map.setPaintProperty(layer.id, 'text-opacity', 0.65);
        }
      }
      const label = map.getStyle().layers.find(layer => layer.type === 'symbol')?.id;
      map.addLayer({
        id: BUILDINGS, type: 'fill-extrusion', source: 'openmaptiles',
        'source-layer': 'building', minzoom: 13,
        filter: ['!=', ['get', 'hide_3d'], true],
        paint: {
          'fill-extrusion-color': '#718792',
          'fill-extrusion-height': ['coalesce', ['get', 'render_height'], 9],
          'fill-extrusion-base': ['coalesce', ['get', 'render_min_height'], 0],
          'fill-extrusion-opacity': 0.58,
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
      const started = performance.now();
      const ids = declutter(listingsRef.current.map(listing => {
        const p = map.project(listing.position);
        return { id: listing.id, x: p.x, y: p.y - 60,
          width: price(listing).length * 8 + 20, priority: priorityRef.current.includes(listing.id) };
      }), map.getZoom(), map.getCanvas().clientWidth, map.getCanvas().clientHeight);
      setLabelIds(previous => previous.size === ids.size && [...ids].every(id => previous.has(id)) ? previous : ids);
      if (meter.current.running) declutterTimes.current.push(performance.now() - started);
    };
    declutterRef.current = declutterLabels;
    // Recompute during motion, not only after it: labels must stay separated throughout zoom.
    map.on('move', declutterLabels);
    map.on('resize', declutterLabels);
    map.on('moveend', () => setZoom(map.getZoom()));
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
    if (info.object && !listingsRef.current.some(d => d.id === info.object?.id)) return;
    setHover(info.object ? { listing: info.object, x: info.x, y: info.y, layer: info.layer?.id ?? '' } : null);
    if (mapRef.current) mapRef.current.getCanvas().style.cursor = info.object ? 'pointer' : '';
  }, []);
  const onClick = useCallback((info: PickingInfo<Listing>) => {
    setHover(null);
    if (info.object && listingsRef.current.some(d => d.id === info.object?.id)) selectRef.current(info.object);
  }, []);
  const onModelDraw = useCallback((type: string) => {
    drawnModels.current.add(type);
    setModelsLoaded(drawnModels.current.size);
    if (drawnModels.current.size === 4) setModelLoadMs(performance.now() - modelStarted.current);
  }, []);
  useEffect(() => {
    if (!ready || !overlayRef.current) return;
    overlayRef.current.setProps({ layers: listingLayers({
      listings: animated.items, entering: animated.entering, exiting: animated.exiting, progress: animated.progress,
      searchActive: !!searchResult,
      selectedId: selected?.id, hoveredId: hover?.listing.id, zoom,
      latitude: mapRef.current?.getCenter().lat ?? HOME.center[1], labelIds,
      reducedMotion: !!reduceMotion, onHover, onClick, onModelDraw,
    }) });
  }, [ready, animated, selected, hover?.listing.id, zoom, labelIds, onHover, onClick, onModelDraw, searchResult, reduceMotion]);

  useEffect(() => {
    if (!ready || !searchResult?.bounds) return;
    // Only a newly committed search fits the camera. Manual filters retain M3 camera stability.
    mapRef.current?.fitBounds(searchResult.bounds, { padding: 90, maxZoom: 15.3,
      pitch: 45, easing: cameraEase, duration: reduceMotion ? 0 : 1400 });
  }, [ready, searchResult]);

  useEffect(() => {
    priorityRef.current = [selected?.id, hover?.listing.id].filter((id): id is string => !!id);
    declutterRef.current();
    if (hover && !mapListings.some(d => d.id === hover.listing.id)) setHover(null);
  }, [mapListings, selected?.id, hover?.listing.id]);

  useEffect(() => {
    // If a filter removes a stay mid-flight, stop at the current camera, never reset home.
    if (previousSelection.current && !selected && !searchResult) mapRef.current?.stop();
    previousSelection.current = selected?.id;
  }, [selected?.id, searchResult]);

  useEffect(() => {
    const selected = selectedRef.current;
    if (!ready || !selected) return;
    mapRef.current?.flyTo({
      center: selected.position, zoom: 15.6, pitch: 58,
      easing: cameraEase, duration: reduceMotion ? 0 : 1600,
    });
    // Only explicit selection flies. Refreshed data and filter-out never move the camera.
  }, [ready, selectionVersion]);

  useEffect(() => {
    const map = mapRef.current;
    if (ready && map?.getLayer(BUILDINGS)) {
      map.setLayoutProperty(BUILDINGS, 'visibility', buildingsVisible ? 'visible' : 'none');
    }
  }, [ready, buildingsVisible]);

  useEffect(() => {
    if (reduceMotion) mapRef.current?.stop();
  }, [reduceMotion]);

  function reset() {
    previousSelection.current = undefined;
    onSelect(null);
    mapRef.current?.flyTo({ ...HOME, easing: cameraEase, duration: reduceMotion ? 0 : 1600 });
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
    declutterTimes.current = [];
    const started = performance.now();
    map.easeTo({ bearing: map.getBearing() + 75, duration: 8000, easing: x => x, essential: false });
    benchmarkTimer.current = window.setTimeout(() => {
      const samples = declutterTimes.current.sort((a, b) => a - b);
      setBenchmark({ ...meter.current.finish(mapListings.length, started, renderer),
        declutterP95Ms: +(samples[Math.floor(samples.length * 0.95)] ?? 0).toFixed(2) });
      setMeasuring(false);
    }, 8000);
  }

  return <section className="map-shell" aria-label="Interactive New York listing map" onPointerLeave={() => setHover(null)}>
    <div ref={container} className="map-canvas" data-testid="map" data-zoom={zoom}
      data-building-count={buildingCount} data-rendered-buildings={renderedBuildings} data-hover-layer={hover?.layer}
      data-models-loaded={modelsLoaded} data-model-load-ms={modelLoadMs} data-instance-count={mapListings.length} data-label-count={labelIds.size}
      data-center={mapRef.current?.getCenter().toArray().join(",")} data-rendered-instances={animated.items.length} />
    <div className="map-heading"><span className="live-dot" /> NEW YORK CITY <span>40.72° N / 74.00° W</span></div>
    <div className="map-actions">
      <button onClick={reset} disabled={!ready}>↗ Reset view</button>
      <button onClick={() => setBuildingsVisible(value => !value)} disabled={!ready}
        aria-pressed={buildingsVisible}>3D buildings {buildingsVisible ? 'on' : 'off'}</button>
    </div>
    {stressMode && <div className="benchmark-panel">
      <strong>300-listing API render benchmark</strong>
      <span>Actual backend data ? four shared model assets</span>
      <button disabled={modelsLoaded < 4 || measuring || !!reduceMotion} onClick={runBenchmark}>
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
  </section>;
}
