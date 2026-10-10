# Lean M3 + M4 handoff

M3's connected explorer is retained. M4 adds natural-language search with local ranking and an optional single provider. No M5/M6 work, deployment, vector database, multi-provider routing, or chat memory was added.

## Run in Windows PowerShell

The existing M2 database is retained. The current workspace already has dependencies, the downloaded model, the 300-vector index and seven saved demo responses. Start two terminals:

Terminal 1 — backend:

```powershell
Set-Location 'C:\Users\dell\OneDrive\Desktop\3D-map\backend'
.\.venv-m2\Scripts\python.exe -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000
```

Terminal 2 — frontend:

```powershell
Set-Location 'C:\Users\dell\OneDrive\Desktop\3D-map\frontend'
npm.cmd run dev
```

Open http://127.0.0.1:5173. Ctrl+C stops each server. Vite proxies `/api` and `/static`, keeping API calls and placeholder images same-origin. Backend CORS also permits GET/POST from its existing local allowlist. Keys never enter the frontend.

For another checkout, or after changing/reseeding listing descriptions, stop the backend and prepare local search once:

```powershell
Set-Location 'C:\Users\dell\OneDrive\Desktop\3D-map\backend'
$env:UV_PROJECT_ENVIRONMENT = '.venv-m2'
uv sync --frozen --extra dev --cache-dir .uv-cache
if (!(Test-Path .env)) { Copy-Item .env.example .env }
# Seed M2 first if this is a fresh database; see backend/README.md.
.\.venv-m2\Scripts\python.exe -m app.prepare_search
```

The preparation command downloads the approximately 67 MB model on first use and overwrites only the search index and saved examples. Runtime ranking uses the local cache with downloads disabled. Saved demo chips need neither a key nor model inference; they can work even without a prepared vector index. The basemap still needs its usual internet connection.

On a fresh frontend checkout run `npm.cmd ci` before `npm.cmd run dev`.

## Environment and zero-cost defaults

`backend/.env.example` now includes:

```dotenv
SEARCH_DEMO_MODE=true
SEARCH_BASE_URL=https://api.groq.com/openai/v1
SEARCH_API_KEY=
SEARCH_MODEL=
SEARCH_TIMEOUT_SECONDS=6
SEARCH_RATE_PER_MINUTE=20
```

Leave this default for no provider access. Suggestion chips send `demo: true` and use the plain JSON file `backend/config/search-examples.json`. Typed queries use the rule parser and local vectors; their explanation explicitly says “Limited keyword interpretation.”

To use a provider, set `SEARCH_DEMO_MODE=false`, supply your key and an available model name, and set the base URL of that provider's OpenAI-compatible chat-completions endpoint. The URL must stop before `/chat/completions`. Restart the backend. One `httpx` client talks only to that configured endpoint; no fallback provider is contacted. Use your provider's free-tier account/quota if desired; this app cannot promise that an arbitrary provider account is free. No live provider call was made during this implementation because no key/model was supplied. A mocked transport verified invalid-output repair and parser fallback.

## Search flow and lean decisions

1. Pydantic validates the query and interpreted filters. Guest/bedroom counts and integer USD cents are strict; unsupported regions, amenities, vibes, extra fields and reversed prices are rejected.
2. Optional provider extraction has **one repair retry**, within **one combined six-second deadline**. There are no network retries. Timeout, missing configuration, provider failure or invalid repaired JSON uses the keyword parser. Recognizable explicit hard constraints cannot be weakened by provider output.
3. The keyword parser handles numeric USD ranges/budgets, guests, bedrooms, the five M2 regions, property types, known amenities and vibe words. It is deliberately limited: complex negation, multiple regions, dates and arbitrary requirements are not guaranteed. The UI exposes interpreted filters; ambiguous language should be rephrased.
4. The existing SQL repository enforces all hard constraints, including budget, guests and every requested amenity, before ranking. Eligible stays are ordered by local FastEmbed cosine similarity and the top 12 are returned. Empty results never silently relax requirements.
5. Explanations use returned listing counts, actual price ranges and regions. Bounds are computed from the same returned coordinates. No LLM-written explanation is displayed.
6. Cache: 128 responses, five-minute TTL. Limiter: 20 POST searches per minute per direct IP, with at most 1,024 in-memory IP buckets. Both are process-local and reset on restart; distributed hosting belongs outside this task.

FastEmbed installed and ran successfully on the first attempt, so **TF-IDF was not needed**. The model is `BAAI/bge-small-en-v1.5`, with 384-dimensional vectors. Listing vectors are computed offline; custom-query inference runs in a worker thread. See [FastEmbed's model documentation](https://qdrant.github.io/fastembed/examples/Supported_Models/).

The frontend has one request effect for browse/search, one cancellation signal and one atomic result snapshot. The sidebar, models and details derive from it. Search deliberately replaces manual filters; editing those filters explicitly returns to browse. A new successful search fits its bounds and gives matched models a mint outline. Manual filters retain M3's stable-camera behavior and close a filtered-out selection. Previous results remain visible with a loading/error notice until a new complete response is ready.

The UI is a one-shot search box with scrollable suggestions and a short answer. Filters are collapsible to leave room for results. This is the simple working option; it avoids a second result store, conversational state and a second ranking engine. The implementation did not require repeated dependency fixes or a ranking fallback.

## Files changed

| Files | Purpose |
| --- | --- |
| `backend/app/search_parser.py` | Validated search contracts and limited keyword interpretation |
| `backend/app/search_provider.py` | Single compatible client, total timeout, one JSON repair, fallback |
| `backend/app/search.py` | SQL eligibility, local ranking, grounded responses, bounded cache and limiter |
| `backend/app/prepare_search.py` | Offline vectors and seven precomputed examples |
| `backend/config/search-examples.json` | Plain JSON examples and full saved responses |
| `backend/app/main.py`, `config.py` | Search endpoints, lifecycle, environment fields and POST CORS |
| `backend/pyproject.toml`, `uv.lock`, `requirements.lock` | Locked FastEmbed/httpx dependencies |
| `backend/.env.example`, root `.env.example`, `.gitignore` | Backend-only provider settings and ignored local model cache |
| `backend/tests/test_search.py`, `test_api.py` | Three focused search tests; updates the former M2-only endpoint expectation |
| `frontend/src/api.ts`, `useExplorer.ts` | Typed search calls and shared browse/search state |
| `frontend/src/SearchBox.tsx`, `App.tsx`, `styles.css` | Query input, suggestions, answer, retry/clear, collapsible filters |
| `frontend/src/MapScene.tsx`, `listingLayers.ts` | Search fitBounds and mint match outlines |
| `frontend/tests/search.spec.ts` | One browser smoke test and AI-query screenshot |
| Existing frontend browser tests | Open the now-collapsible filters before using them |
| `README.md`, `docs/architecture.md`, this handoff | Current status and run instructions |

M3's API client, filter validation, model transitions, details, legend relocation, declutter and their inline design comments remain in place. Earlier file-by-file notes and performance measurements are in `docs/m3-connected-explorer.md`.

## Focused checks

```powershell
Set-Location 'C:\Users\dell\OneDrive\Desktop\3D-map\backend'
.\.venv-m2\Scripts\python.exe -m pytest tests/test_search.py -q

Set-Location 'C:\Users\dell\OneDrive\Desktop\3D-map\frontend'
npm.cmd run build
# Keep the backend running; Playwright starts its own preview on port 4173.
npm.cmd run test:browser -- tests/search.spec.ts
```

The complete backend suite passed **79 tests**. Frontend client/component checks passed; the search smoke test also validates the offline response, shared IDs, camera fit, custom-query fallback and return to manual filters. See the final validation evidence for the completed browser run.

## Browser checklist

- [ ] Start with 300 synthetic backend stays; hover/click still opens details and flies to the selected stay.
- [ ] Expand “Refine with filters”; changes debounce and affect the map and sidebar together.
- [ ] Click the first offline suggestion: see up to 12 ranked Manhattan apartments, a saved-demo explanation and highlighted models; the camera fits them.
- [ ] Type a custom query with no key: see local ranking and the explicit keyword-fallback disclosure.
- [ ] Expand “Interpreted filters” to inspect budget, guest capacity, region, amenities and vibes.
- [ ] Clear search restores browsing. Set max price to $1 for a clear no-matches state; clearing filters restores results.
- [ ] Disconnect the backend to see retry; the previous complete result remains visible. Suggestions have their own retry.
- [ ] The legend expands inside the sidebar; sparse tags remain readable at low zoom, with selected/hovered tags retained.

Screenshot: [Working offline AI query](evidence/m4-ai-query.png).

Stop point: M3 + M4 review. M5/M6 are untouched.
