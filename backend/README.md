> Historical M2 notes. For current setup and features see [the root README](../README.md).

# StayScape M2 — backend and synthetic dataset

M1.5 is approved. This milestone adds the backend, generated data, validation and
GeoJSON review tools. **No frontend files changed; M3 and AI search are not implemented.**

## File list

```text
backend/
  .env.example, .python-version, pyproject.toml, uv.lock, requirements.lock
  app/
    __init__.py
    config.py              # environment settings and stable filesystem paths
    schemas.py             # strict records/filters, HTTP query boundary
    geography.py           # polygon configuration and geodesic distance
    dataset.py             # catalog, whole-dataset validation and GeoJSON
    generator.py           # seeded coordinates, attributes and narratives
    database.py            # portable SQLAlchemy models and engine/session factory
    repository.py          # persistence-neutral read protocol
    sql_repository.py      # SQL implementation of mandatory filters
    seeding.py             # transactional writes and manifest compatibility
    errors.py, main.py     # error contract, lifecycle and five API routes
    cli.py                 # generate / validate / seed / export-geojson
    parsing.py             # retained strict JSON boundary, updated to new contracts
  config/
    regions.json, pricing.json, images.json, descriptions.json
  static/placeholders/
    apartment.svg, townhouse.svg, house.svg, loft.svg
  tests/
    conftest.py, test_api.py, test_contracts.py, test_generator.py, test_repository.py
  data/                    # generated, ignored outputs; already created locally
    listings.json, listings.geojson, stayscape-m2.db
  README.md
docs/
  architecture.md, m2-full-source.md
  evidence/m2-samples.json, m2-api-response.json, m2-validation.json
  evidence/m2-frontend-before.json
```

Root `README.md`, `.env.example` and `.gitignore` were updated for the new backend
setup. `.python-version` remains 3.12. Dependency lockfiles are generated metadata.

## Setup on Windows PowerShell

The workspace already has a generated/validated/seeded dataset and `.venv-m2`.
To run it now, start at the repository root:

```powershell
cd backend
.\.venv-m2\Scripts\python.exe -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000/docs. The frontend remains a standalone M1.5 application.

For a fresh checkout, use the installed **uv** tool. It creates the virtual
environment, installs Python if necessary, and installs the exact locked packages:

```powershell
cd backend
$env:UV_PROJECT_ENVIRONMENT = ".venv-m2"
uv sync --frozen --extra dev --cache-dir .uv-cache
if (!(Test-Path .env)) { Copy-Item .env.example .env }
.\.venv-m2\Scripts\python.exe -m app.cli generate --count 300 --seed 42
.\.venv-m2\Scripts\python.exe -m app.cli validate
.\.venv-m2\Scripts\python.exe -m app.cli seed
.\.venv-m2\Scripts\python.exe -m app.cli export-geojson
.\.venv-m2\Scripts\python.exe -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000
```

No activation or execution-policy change is needed. The old `.venv` is left alone
because it contains read-only OneDrive files. The project's Python pin is 3.12.

If you prefer standard Python/pip on a fresh checkout with Python 3.12 installed:

```powershell
cd backend
py -3.12 -m venv .venv-m2
.\.venv-m2\Scripts\python.exe -m pip install --require-hashes -r requirements.lock
.\.venv-m2\Scripts\python.exe -m pip install --no-deps -e .
```

Then use the same generate/validate/seed/export/run commands. The pip route is an
alternative setup; an environment created by uv does not necessarily contain pip.
The existing system Python alias on this machine is unusable, so uv was used here.

Generation refuses to overwrite an existing JSON file; seeding refuses to replace
existing data. To deliberately regenerate **this synthetic dataset**:

```powershell
.\.venv-m2\Scripts\python.exe -m app.cli generate --count 300 --seed 42 --overwrite
.\.venv-m2\Scripts\python.exe -m app.cli validate
.\.venv-m2\Scripts\python.exe -m app.cli seed --replace
.\.venv-m2\Scripts\python.exe -m app.cli export-geojson --overwrite
```

`--replace` deletes and replaces the listing/metadata rows in one transaction.
Do not run it against a database whose contents you want to preserve. Invalid data
is rejected before replacement. Generation validates in memory before writing an
atomic JSON output; it never leaves a partially accepted dataset.

Tests and formatting checks, from `backend`:

```powershell
.\.venv-m2\Scripts\python.exe -m pytest -q
.\.venv-m2\Scripts\python.exe -m ruff check app tests
.\.venv-m2\Scripts\python.exe -m ruff format --check app tests
```

Verified versions: Python **3.12.13**, FastAPI **0.141.1**, Pydantic **2.13.5**,
SQLAlchemy **2.0.54**, aiosqlite **0.22.1**, asyncpg **0.31.0**, Shapely **2.1.2**.
`uv.lock` and the hashed `requirements.lock` record the complete dependency set.

## API contract

| Endpoint | Meaning |
| --- | --- |
| `GET /api/health` | Database/dataset readiness; returns 503 when not ready or misconfigured |
| `GET /api/config` | Currency, exponent, enums, page limits, synthetic dataset manifest |
| `GET /api/areas` | Five configured sampling regions, centers, polygons and exclusions |
| `GET /api/listings` | SQL-filtered page and count of all matches before pagination |
| `GET /api/listings/{uuid}` | Full listing or `LISTING_NOT_FOUND` |
| `GET /static/placeholders/{type}.svg` | Local project-authored placeholder illustration |

Listing query parameters:

- `price_min_minor`, `price_max_minor`: inclusive integer minor-unit bounds.
- `guests`: minimum required capacity, not exact occupancy.
- `bedrooms`: minimum required bedrooms; `0` imposes no positive-bedroom requirement.
- `property_type`: exactly `apartment`, `townhouse`, `house`, or `loft`.
- `region`: `manhattan`, `brooklyn`, `queens`, `jersey-city`, or `hoboken`.
- Repeated `amenities`: **all** requested amenities must be present.
- `limit`: 1–100, default 30. `offset`: 0–1,000,000, default 0.

Pages use deterministic UUID ordering. Unknown query keys, unsupported enum values,
inverted prices, fractional numbers, duplicate amenities and repeated scalar keys
are rejected rather than ignored. Price 0 is a valid bound, even though no listing
can itself have a zero nightly price. There is no semantic ranking or vibe filter yet.

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/api/health'
Invoke-RestMethod 'http://127.0.0.1:8000/api/config'
Invoke-RestMethod 'http://127.0.0.1:8000/api/areas'
Invoke-RestMethod 'http://127.0.0.1:8000/api/listings?region=queens&guests=2&amenities=wifi&limit=1' | ConvertTo-Json -Depth 10
Invoke-RestMethod 'http://127.0.0.1:8000/api/listings?price_max_minor=25000&amenities=wifi&amenities=workspace&limit=10'
```

A `$250` ceiling is `price_max_minor=25000`, not `250`.
Unknown resources and failures use one envelope, for example:

```json
{"error":{"code":"LISTING_NOT_FOUND","message":"The requested listing was not found."}}
```

Codes include `VALIDATION_ERROR`/`INVALID_REGION` (422), `LISTING_NOT_FOUND`/`NOT_FOUND`
(404), `METHOD_NOT_ALLOWED` (405), `DATASET_NOT_READY`/`DATASET_CONFIG_MISMATCH`/
`DATABASE_UNAVAILABLE` (503), and `INTERNAL_ERROR` (500). Validation responses may
include safe field names, never raw input, SQL, stack traces or credentials.

## Architecture and repository pattern

```text
HTTP query strings
  -> Pydantic ListingQuery (transport conversion + validation)
  -> strict ListingFilters
  -> ListingRepository protocol
  -> SQLListingRepository (all mandatory filters in SQL)
  -> request-scoped AsyncSession -> SQLite / PostgreSQL
  -> Pydantic ListingPage -> JSON

Config + seed + authored prose
  -> constrained point sampler + coherent attributes
  -> Pydantic records + whole-dataset validation
  -> deterministic JSON -> transactional seed -> database
                       -> GeoJSON inspection
```

The repository is the small `list()`/`get()` contract that routes depend on. SQLAlchemy
lives in the adapter, not in route logic. A future real-listing adapter can implement
the same contract without rewriting API behavior; an in-memory test implementation
already demonstrates that substitution. New adapters must preserve filter semantics.

Amenities live in a child table with one row per listing/amenity. Correlated `EXISTS`
conditions implement AND semantics portably; SQLite JSON substring searches would
be both fragile and awkward to move to PostgreSQL. Pictures and vibes use JSON
because M2 does not query them. `selectinload` fetches amenity rows without one query
per listing. SQL check constraints reinforce price, capacity, type and coordinate
bounds; Pydantic also validates records on ingestion and repository output.

The default database has an absolute path at `backend/data/stayscape-m2.db`, so
working-directory changes do not accidentally create a different database. Each
request owns its session; the application disposes the engine on shutdown.

`postgresql+asyncpg://...` selects PostgreSQL using the same models/repository.
PostgreSQL DDL compilation is tested. **A live PostgreSQL server was not available,
so this milestone does not claim a PostgreSQL integration test.** `create_all` is
explicit dev initialization in the seed command, not an automatic migration engine.
Reviewed migrations belong in deployment work; API startup never mutates schema.

## Currency

`CURRENCY_CODE=USD` selects the profile in `config/pricing.json`. Prices are integer
cents and `/api/config` publishes `currency_minor_units: 2`. Baselines are invented
regional demo prices, adjusted by property type, bedroom count, vibe and seeded
variation; they are not scraped prices or current market estimates.

A new currency requires an explicit pricing profile with its own integer baselines
and exponent, followed by regeneration and reseeding. Setting only `CURRENCY_CODE`
cannot convert money. A mismatch between the configured currency/exponent and the
seeded manifest returns `DATASET_CONFIG_MISMATCH`; unsupported profiles fail startup
with a clear configuration error. Tests cover both cases and generation with an
explicit alternate profile. No exchange-rate service or paid API is involved.

## Geography, spacing and reproducibility

`config/regions.json` defines compact hand-drawn **sampling zones**, centers and
named exclusions. These are not official borough boundaries. Centers are metadata;
sampling draws uniformly within each polygon's bounding box and rejects points
outside the polygon or on/inside any exclusion. All exclusions apply globally.

The default global minimum is **75m**, checked with haversine distances against all
previously accepted points across every region. At 300 records this simple O(n²)
approach is easy to audit and fast enough. The same checks run independently in
the validation command. The default dataset allocates 60 points to each region.

The sampler has a finite per-region attempt budget. If it cannot fill a quota, it
reports the region, accepted/requested count, spacing and attempt budget; it writes
no output and never shrinks spacing. Rejection-sampling exhaustion is not a proof
that no mathematical packing exists. You can reduce count, review/enlarge allowed
zones, or increase `--attempts-per-region`. A `--min-spacing-m` below the configured
minimum is explicitly rejected.

**Geographic limits:** the validator guarantees the configured polygon/exclusion
rules, not absence of every unmodeled pocket park, road, schoolyard or water feature.
The polygons deliberately favor inland areas, but this is not a cadastral land-use
dataset. Visual review is required. If you find an unsuitable point, adjust the
polygon/exclusion and regenerate; its hash prevents the old dataset being seeded
under the changed geography. 75m geographic separation also cannot prevent overlap
of intentionally exaggerated 38px map symbols at every city zoom.

RNGs are local and seeded; the geographic and narrative streams are separate.
Stable UUID5 IDs and the absence of generation timestamps permit byte-for-byte
reproduction with the same code, configs, count, seed and locked Python environment.
Changing the seed changes both positions and content.

## Descriptions and local images

`config/descriptions.json` contains **64 authored two-sentence scenes**, eight for
each vibe: quiet, nightlife, family-friendly, romantic, business trip, budget,
luxury and scenic. The generator combines a coherent scene with a matching
property-layout detail and a factual capacity sentence, using four sentence orders.
It varies titles and rejects duplicate full descriptions. The resulting passages
have four sentences with concrete sensory and practical detail, rather than one
fixed sentence with swapped vibe adjectives.

Amenities and capacity follow the narrative: business stays include a workspace;
family stays have at least two bedrooms, capacity for four, a crib and a washer;
scenic stays have a balcony. Romantic stays host two; budget/luxury affect the
invented price. An open-plan zero-bedroom listing uses an apartment or loft model,
never an unsupported `studio` type. Ratings use a high-skew beta distribution,
giving mostly favorable but varied synthetic scores rather than uniform randomness.

This is a deterministic, authored compositional system, not 300 independently
written essays: individual passages can recur, but complete descriptions are
distinct. It costs nothing and makes future semantic-search examples inspectable.
No provider, embeddings, model download or AI endpoint is added in M2.

The simple `config/images.json` maps each property type to a list of local SVG
placeholders, served by this backend. They are original geometric illustrations
labeled SYNTHETIC, not photographs or copied Kenney assets. API picture URLs are
backend-relative; M3 can resolve them against the API origin. No frontend asset
or license file was modified and no image is hotlinked.

## Visual check in geojson.io

1. Run `python -m app.cli export-geojson` using the environment commands above.
2. Open [geojson.io](https://geojson.io), use its local-file import control, and choose
   `backend/data/listings.geojson`.
3. Inspect each of the five regions. Blue outlines are sampling polygons; red
   polygons are excluded areas; green points are listings. Click a feature to see
   `kind`, region, title, type and integer price.
4. Check shorelines and park edges at street level. Confirm no point lies within
   a red exclusion. Boundaries are intentionally conservative and approximate.
5. If you edit the configuration, regenerate, validate, reseed and re-export.

The export contains only synthetic fixture data. It is a normal FeatureCollection
with GeoJSON `[longitude, latitude]` coordinates.

## Verification and examples

The default seed 42 produced **300 listings**, **300 unique descriptions**, **60 per
region**, with minimum observed spacing **75.577m**. All **76 tests passed**; Ruff
lint/format checks pass. The library stack emits one Starlette deprecation warning
about its httpx TestClient adapter; it does not affect runtime or test outcomes.
The live Uvicorn server was also exercised through HTTP against the seeded database.

Coverage includes repository filtering/pagination/details, SQL constraints,
seed replacement, all API endpoints, safe invalid requests, CORS, local images,
currency mismatch, reproducibility, global/inter-region spacing, exclusion edges,
invalid polygons, GeoJSON serialization, and failed generation without partial files.
Frontend hashes were unchanged.

- [Three complete generated records](../docs/evidence/m2-samples.json)
- [Real paginated API response](../docs/evidence/m2-api-response.json)
- [Validation report](../docs/evidence/m2-validation.json)
- [Full source and configuration](../docs/m2-full-source.md)

## Acceptance checklist

- Run validation and see 300 items, five counts of 60, and spacing at least 75m.
- Open `/docs`, `/api/health`, `/api/config`, `/api/areas` and one detail URL.
- Filter by price, guests, bedrooms, property type, region and repeated amenities.
- Confirm `total` counts all matching rows while `items` respects `limit`/`offset`.
- Send an inverted price range or unsupported `studio` type and see a safe 422.
- Open a returned placeholder URL; confirm it is served locally.
- Inspect the GeoJSON in geojson.io, especially shorelines and red park exclusions.
- Compare the three sample descriptions and verify capacity/amenities agree.
- Run the tests. The existing M1.5 frontend should remain unchanged and disconnected.

Stop here for review. Frontend/API integration is M3.
