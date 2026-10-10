# StayScape M1.5 — 3D model explorer

This milestone runs entirely in the browser. It uses 20 hardcoded synthetic stays
in a compact Manhattan area so you can see basemap buildings and illustrated rental models together.
There is no backend, search, AI, dataset generator, or photo service in this milestone.

See [M1.5 changes, performance and asset preparation](../docs/m1-5-visual-upgrade.md)
and [model credits](public/models/CREDITS.md). The `?benchmark=300` URL enables a
render-only stress fixture; it is not the future M2 synthetic dataset.

## Exact versions

| Package | Version |
| --- | --- |
| React / React DOM | 19.3.0 |
| Vite | 8.3.1 |
| MapLibre GL JS | 6.11.2 |
| @deck.gl/core, @deck.gl/layers, @deck.gl/maplibre, @deck.gl/mesh-layers | 9.4.0 |
| @luma.gl/core, @luma.gl/gltf | 9.4.0 |
| @vitejs/plugin-react | 6.1.1 |
| TypeScript | 7.0.2 |
| Playwright test runner | 1.63.0 |

Package versions are pinned; `package-lock.json` locks transitive dependencies.
Vite requires Node `^20.19.0 || >=22.12.0`; the workspace uses Node 24.19.0.
The React plugin declares Vite 8 support. The deck.gl MapLibre adapter declares
MapLibre `^4.5.1 || ^5.0.0 || ^6.0.0`, deck.gl core `~9.4.0`, and luma core `~9.4.0`.
We use the plain MapLibre adapter inside a React effect, so no additional React map
wrapper or its peer version constraints are needed.

Sources checked for this milestone:

- [React versions](https://react.dev/versions)
- [Vite guide](https://vite.dev/guide/)
- [deck.gl MapLibre integration](https://deck.gl/docs/developer-guide/base-maps/using-with-maplibre)
- [MapLibre NYC building example](https://maplibre.org/maplibre-gl-js/docs/examples/display-buildings-in-3d/)
- npm registry package metadata, verified by `npm view` and installation.

## Install, run, build

From the repository root in PowerShell:

```powershell
cd frontend
npm.cmd ci
Copy-Item .env.example .env.local
npm.cmd run dev
```

Open http://127.0.0.1:5173. The environment copy is optional because USD is the default;
do not overwrite an existing `.env.local`. Restart Vite after environment changes.
Use `npm.cmd` on this Windows machine to avoid PowerShell's npm.ps1 script-policy issue.
On macOS/Linux, use `npm` and `cp .env.example .env.local`.

In a separate terminal, from `frontend`:

```powershell
npm.cmd run build
npm.cmd run preview
```

Open http://127.0.0.1:4173 for the production bundle. Stop a server with Ctrl+C.
No Python process, API key, or paid account is required. Map tiles need internet access.
If npm's default cache is inaccessible, append `--cache .npm-cache` to `npm.cmd ci`.

## How the rendering works

MapLibre owns the camera: center, zoom, pitch, bearing, panning, and `flyTo`.
It renders the basemap and extrudes tile building polygons using their height properties.
`MapLibreOverlay` synchronizes deck.gl to that camera. M1.5 uses `interleaved: false`
and a separate transparent WebGL2 canvas: listing models remain visible above
basemap buildings. Models depth-sort against one another, but basemap buildings
cannot occlude them. These are map symbols, not reconstructed real-world buildings.

Four `ScenegraphLayer`s instance four local GLBs, one per property type. Positions
use `[longitude, latitude]`. The normalized model footprint is clamped to 38
unpitched map pixels at distant zooms, tending toward 10–20 meter widths up close.
Perspective still changes the visible pixel footprint. Three translucent ground
strokes form each rating halo: amber (below 4.5), blue (4.5–4.7), mint (4.8+).
Billboard `TextLayer` labels show USD nightly prices; height never encodes price.
Hover/selection adds a white outline, a 12% scale increase and a 260ms altitude
lift. Reduced-motion settings disable that transition. GPU picking identifies
actual meshes, rings or tags; React displays the card. Sidebar buttons also work
with keyboard/touch. A simple screen grid hides crowded tags, never the models.

The map is created once per mount, not per hover or selection. React StrictMode
development remounts are handled by cleanup. A ResizeObserver keeps the map canvas
in sync with its container. Reduced-motion settings shorten camera flights to zero.
CSS stays small and local in this spike; broader styling/animation work belongs to M5.

## Chosen map source and terms

Style: `https://tiles.openfreemap.org/styles/dark`

Vector TileJSON: `https://tiles.openfreemap.org/planet`

OpenFreeMap's public service requires no API key or registration; its published
policy permits commercial use and lists no view/request limits. It is provided
as-is, without an uptime SLA; comply with its terms, including responsible use and
restrictions on automated collection. This app makes normal interactive map requests,
not a bulk download or scraping job.

Keep the provider's attribution visible: **OpenFreeMap © OpenMapTiles Data from
OpenStreetMap**, with links. The OpenFreeMap part is optional under its guidance;
we retain the complete attribution supplied by TileJSON. Preserve attribution in
future screenshots and GIFs too. The service's MIT software license does not replace
the underlying map-data licenses.

- [OpenFreeMap policy and attribution](https://openfreemap.org/)
- [Terms of service](https://openfreemap.org/tos/)
- [Quick start](https://openfreemap.org/quick_start/)
- [OpenStreetMap copyright/data license](https://www.openstreetmap.org/copyright)

The live style uses source `openmaptiles`. Its TileJSON advertises a `building`
layer at source zooms 13–14 with `render_height`, `render_min_height`, and `hide_3d`.
MapLibre overzooms these tiles at closer camera zooms; max source zoom 14 does not
mean buildings disappear above zoom 14. MapLibre's official example uses this
source in NYC. The browser verification checks actual loaded NYC building features.

The dark style originally has flat building fills. We add a `fill-extrusion` layer
from the existing source, rather than falsely treating the style itself as already
3D. Missing height values get a visibly approximate 9m fallback. Coverage and
heights are OSM-derived and may be incomplete or estimated.

## Browser verification

After building, with Microsoft Edge installed:

```powershell
npm.cmd run test:browser
```

The test runner starts the production preview. It checks real building data, 20
listings, camera zoom after selection, real GPU hover/click picking, reset,
attribution, mobile overflow, and failed-tile error handling. It writes screenshots
to ignored `test-results/`. Tests need internet for real tiles and a WebGL2-capable
browser. The test harness uses software rendering for repeatable headless runs;
the app itself uses the browser's normal renderer.

If using installed Chrome instead of Edge:

```powershell
$env:PLAYWRIGHT_CHANNEL = 'chrome'
npm.cmd run test:browser
```

Manual acceptance checklist:

- A dark NYC map loads with basemap buildings and four distinct low-poly model styles.
- The sidebar has 20 synthetic stays, all priced in USD per night.
- Hover a model: it lifts/highlights and a title, price, neighborhood, and rating appear.
- Click a model or sidebar stay: the camera flies closer and the selection card appears.
- Pan, zoom and right-drag to change pitch/bearing; models stay aligned and visible.
- Toggle buildings off/on, then use Reset view to return to the starting camera.
- Read the rating/price legend and map attribution; try the narrow mobile layout.

## Before M2

Understand the distinction between a rendering library (MapLibre/deck.gl), a tile
provider (OpenFreeMap), and our synthetic listings. The map coordinates are longitude
first. Camera ownership belongs to MapLibre. React state holds the selected listing,
not every animation frame. Amounts are USD cents; M1 intentionally rejects a currency
change rather than silently relabeling the same money. M2 will make dataset currency
configurable and publish that configuration from the backend.

The hardcoded points are illustrative, not verified rental locations. Generation,
hand-drawn polygons/exclusions, minimum spacing, storage, and validation are M2 work.
No implementation of M2 has been started in this milestone.
