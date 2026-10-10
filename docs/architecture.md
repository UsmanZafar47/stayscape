# Current architecture — lean M3 + M4

React filter draft → validation → 300ms debounce → typed cancellable GET /api/listings client → FastAPI → existing SQL repository/database.

All matching pages commit atomically to `useExplorer`. The shared result array feeds sidebar and deck.gl models; details derive from its selected ID. Only explicit selection drives MapLibre fly-to. Filter refreshes preserve the camera; filtered-out selections close.

MapLibre owns map/camera/building tiles; deck.gl instances four local GLBs. Exit ghosts exist only in a short animation buffer, never in application results. CPU screen-space tag collision checks prioritize selected/hovered listings and thin labels at low zoom.

Vite proxies API and backend placeholder image paths during local development/preview. Backend contracts, validation, synthetic generation and SQL persistence remain as verified in M2.

M4 POST `/api/search`: validated query → one optional provider (strict six-second combined deadline, one JSON repair) or disclosed rule parser → SQL hard constraints → local FastEmbed vibe ranking → deterministic explanation and bounds. Offline preparation writes 300 listing vectors and seven full demo responses. Demo chips bypass both provider and runtime embedding inference; SQL checks the saved stays still match.

Search uses the same `useExplorer` effect and atomic result snapshot as browse filters. A completed search fits its returned bounds and highlights the matched models; edits to manual filters return to browse without a camera reset. Search is one-shot, with no conversational memory. Responses cache for five minutes (128 entries); a per-process limiter permits 20 searches per minute per direct client IP (1,024 bounded IP buckets).

See [M3 + M4 handoff](m3-m4-lean.md) for commands, design decisions and acceptance checks. Earlier milestone source snapshots remain historical records. M5/M6 are not started.

