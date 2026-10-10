# Milestone 3 — connected explorer

M2 is verified. M3 connects the existing renderer to FastAPI. M4 is not started.

## Run on Windows PowerShell

Use two terminals. These commands use the existing verified M2 environment and seeded database; they do not regenerate or replace data.

Terminal 1:

```powershell
Set-Location 'C:\Users\dell\OneDrive\Desktop\3D-map\backend'
.\.venv-m2\Scripts\python.exe -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000
```

Terminal 2:

```powershell
Set-Location 'C:\Users\dell\OneDrive\Desktop\3D-map\frontend'
npm.cmd run dev
```

Open http://127.0.0.1:5173. Stop each server with Ctrl+C. For a fresh checkout, follow `backend/README.md` for locked environment setup and seeding, and run `npm.cmd ci` in `frontend` before starting it.

With the backend running, run checks in a third terminal:

```powershell
Set-Location 'C:\Users\dell\OneDrive\Desktop\3D-map\frontend'
npm.cmd run build
npm.cmd run test:browser -- tests/client.spec.ts tests/explorer.spec.ts tests/map.spec.ts
$env:BENCHMARK_HARDWARE = '1'
npm.cmd run test:browser -- tests/performance.spec.ts
Remove-Item Env:BENCHMARK_HARDWARE
```

Playwright starts and stops the preview server on port 4173. Use sequential test invocations because Playwright owns its artifact directory. Edge is the default installed browser. Public OpenFreeMap tiles need internet access; models and placeholder images are local.

## State flow and decisions

Filter inputs retain strings so an empty price is distinct from zero. Validation checks integer guest/bedroom bounds, the four exact model types, dollar precision, and ordered prices. Price inputs become integer USD cents. Guests and bedrooms are minimum requirements, matching M2's API semantics.

`useExplorer` cancels the previous request immediately when an input changes, then waits 300ms before requesting. `getListings` calls GET `/api/listings` with the same validated filters and pages of 100 until all matches arrive. It verifies the response structure, currency, model types, local picture paths, pagination totals and duplicate IDs. A 15-second deadline bounds the entire request. A failed later page does not publish an incomplete list.

The hook commits one `{items, selectedId}` snapshot atomically. Map and sidebar receive those exact items; details look up the selected ID in the same array. M2 already returns complete details in list responses, so opening details requires no redundant detail request. Previous results remain visible and explicitly labeled during loading/errors. Invalid drafts show validation and retain the previous results. Retry repeats the current valid query.

Only explicit selection changes trigger fly-to. Refreshing data cannot re-fly. A filtered-out selection closes; an ongoing flight stops at its current position. No automatic fitBounds runs on filter changes. Clicking the same listing again re-centers it. Reset view is the explicit way back to the collection camera.

`useAnimatedListings` retains outgoing objects as unselectable visual ghosts for a 280ms scale/fade; these never re-enter result state. Incoming/outgoing instances share four cached GLB scenes. Reduced-motion users see immediate updates. Mesh/ring picking rejects objects absent from the current results.

Vite proxies `/api` and `/static` to `127.0.0.1:8000` for both development and build preview. This keeps requests and backend placeholder image URLs same-origin and avoids adding browser CORS exceptions or hardcoded API origins to React. Existing M2 CORS remains untouched. Production reverse proxy/deployment is outside M3.

The collapsible legend and navigation hints live in normal sidebar flow, entirely outside map bounds. Tags use projected screen-space rectangles and extra spacing at low zoom. Selected/hovered tags reserve space before ordinary tags and always remain enabled. The two priority tags may overlap each other when their anchors are extremely close; preserving both is intentional. Collision checks run during camera motion and resize, not just after movement ends.

## Changed files

- `frontend/src/api.ts`: typed transport adapter, runtime checks, cancellable pagination.
- `frontend/src/filters.ts`, `useExplorer.ts`: validation, debounce, atomic results and selection.
- `frontend/src/App.tsx`, `styles.css`: filter controls, full details, image retry, API states, collapsible sidebar legend, responsive layout.
- `frontend/src/listings.ts`: shared types, formatting and rating colors; removes all hardcoded listing/stress data.
- `frontend/src/MapScene.tsx`, `listingLayers.ts`, `performance.ts`: result-driven rendering, intentional camera behavior, stable model groups and benchmark against actual API records.
- `frontend/src/declutter.ts`, `useAnimatedListings.ts`: collision priority and filter transitions.
- `frontend/vite.config.ts`: API/static proxies.
- `frontend/tests/client.spec.ts`, `explorer.spec.ts`, `map.spec.ts`, `performance.spec.ts`: API/filter units, component flows, real picking/filter/fly-to, actual 300-record benchmark.
- `README.md`, `docs/architecture.md`, this handoff and `docs/evidence/m3-*`: current milestone documentation and evidence.

Design decisions are commented at their implementation boundaries. No backend behavior or M4 functionality was added.

## Browser acceptance checklist

- [ ] Initial loading becomes 300 stays; all sidebar rows are backend data.
- [ ] Apartment, townhouse, house and loft filters match the model names; price, guests and bedrooms combine correctly after a short debounce.
- [ ] Min price above max displays validation without sending invalid requests.
- [ ] Map and sidebar counts agree after each response; models scale/fade on changes.
- [ ] Hover a model/ring/tag; click it or a sidebar row to fly to the stay.
- [ ] Details include title, price, rating, neighborhood, description, amenities and a local placeholder illustration.
- [ ] Re-selecting a stay re-centers; filtering it out closes details without resetting the camera.
- [ ] Max price $1 shows “No matches”; Clear all filters restores the collection.
- [ ] Stop the backend, change a filter, and see Retry listings with previous results retained; restart the backend and retry.
- [ ] Legend expands/collapses in the sidebar without covering the map. No bottom map hint obscures tags.
- [ ] Zoom out to see fewer tags; selected and hovered tags retain priority.
- [ ] At 390px wide, map, details and sidebar stack without horizontal overflow.
- [ ] `?benchmark=300` measures the current 300 backend listings, rather than a synthetic renderer grid.

## Verification and performance

Production build/typecheck passed, as did all nine functional tests and the hardware benchmark. After the final hover-leave fix, both affected map tests passed again and the screenshots were refreshed. The build still reports a large main chunk (2.30 MB / 631 KB gzip), chiefly the existing mapping stack.

Measured on Intel Iris Xe, Edge 154, 1280×800, DPR 1, with all **300 backend listings** loaded:

| Orbit | Average FPS | p95 frame gap | Label layout p95 |
| --- | ---: | ---: | ---: |
| First 300-listing orbit | 44.6 | 32.1 ms | 3.0 ms |
| Warm 300-listing orbit | **47.4** | **28.3 ms** | **2.8 ms** |
| Basemap-only comparison | 55.5 | 23.3 ms | 0.2 ms |

The camera orbit measures actual deck draw callbacks for eight seconds, not idle requestAnimationFrame callbacks. These are local hardware measurements, not a guarantee of 60 FPS on every device. The four model downloads total about 379 KB; only four GLB requests occur for 300 stays. Models retain shared scenes and instance buffers. Smaller overview symbols reduce visual crowding and fragment work while restoring the original size near individual stays.

Bottlenecks/limits found:

- Listing rendering plus label layout costs roughly 8 FPS versus the basemap-only comparison; label projection/collision work itself is 2.8 ms p95.
- First readiness was 10.4 seconds, with about 7.25 seconds between overlay creation and first draws of all four model types, although individual local GLB transfers took 11–35 ms. This indicates initialization/first-render work, rather than model network transfer, dominates that phase; shader cost was not isolated independently.
- An initial automated benchmark reported 25–30 FPS and ~190ms p95 gaps. A CPU profile exposed Playwright accessibility-name scans over 300 sidebar buttons and trace work during measurement. The final benchmark disables tracing and uses timed waits instead of repeated locator scans. The diagnostic profile is preserved separately so the invalid timing is not confused with final application performance.
- The existing public basemap emitted a missing `wood-pattern` sprite warning during browser QA. It did not prevent tile rendering, model picking, or the completed flow.

Evidence:

- [Desktop overview](evidence/m3-desktop.png)
- [Selected stay and full details](evidence/m3-selected.png)
- [Mobile layout](evidence/m3-mobile.png)
- [Final performance JSON](evidence/m3-performance.json)
- [Diagnostic profile before benchmark correction](evidence/m3-profile-before-benchmark-fix.json)

Stop point: M3 review. No M4 embeddings, AI search, or deployment work was started.

