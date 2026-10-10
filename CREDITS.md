# Credits and asset licenses

## 3D models and preview images

Kenney, [City Kit Commercial](https://kenney.nl/assets/city-kit-commercial) 2.1, [City Kit Suburban](https://kenney.nl/assets/city-kit-suburban) 2.0 and [City Kit Industrial](https://kenney.nl/assets/city-kit-industrial) 2.0: **CC0 1.0**. Apartment = commercial building-f; townhouse = suburban building-type-k; house = suburban building-type-a; loft = industrial building-a. Preview PNGs are original pack assets. GLBs were optimized, centered, normalized and rotated; M5 adds runtime instance tints. No endorsement is implied.

Exact downloads and conversion details: [model credits](frontend/public/models/CREDITS.md). Original license copies: [commercial](frontend/public/models/licenses/commercial.txt), [suburban](frontend/public/models/licenses/suburban.txt), [industrial](frontend/public/models/licenses/industrial.txt). [CC0 terms](https://creativecommons.org/publicdomain/zero/1.0/).

## Map data, tiles, style and fonts

- **OpenStreetMap contributors:** geographic data under [ODbL](https://www.openstreetmap.org/copyright).
- **OpenMapTiles:** schema/code BSD-3-Clause, cartographic design CC BY 4.0; [upstream license](https://github.com/openmaptiles/openmaptiles/blob/master/LICENSE.md).
- **OpenFreeMap / Zsolt Ero:** hosted tile service and dark style, project MIT. Preserve "OpenFreeMap / © OpenMapTiles / Data from OpenStreetMap" in the map, recordings and screenshots. [Attribution instructions](https://openfreemap.org/#attribution).
- Styles have mixed upstream terms; the provider's [style license inventory](https://github.com/hyperknot/openfreemap-styles/blob/main/LICENSE.md) identifies BSD-3-Clause style code, CC BY 4.0 designs, and CARTO/Stamen/Paul Norman basemap lineage under CC BY 3.0. Do not interpret the hosting project's MIT license as a license for all map data/artwork.
- Provider assets include **Noto Sans** (SIL OFL 1.1), **Maki** icons (CC0) and **Natural Earth** data (public domain), as documented in that inventory. UI uses system fonts; no separate UI font files are bundled.

The provider's remote style supplies its glyphs/sprites at runtime. StayScape changes street-label visibility and adds lighter building extrusions; it does not redistribute a tile archive. OSM heights are illustrative, not surveyed rental dimensions.

## Search and original assets

- **BAAI bge-small-en-v1.5** embedding weights: MIT, [model card](https://huggingface.co/BAAI/bge-small-en-v1.5). Downloaded locally by FastEmbed; not shipped in the frontend.
- The four SVG placeholder illustrations in `backend/static/placeholders` and synthetic listing texts/data are authored for this project. They are not scraped or third-party property photographs. No separate third-party license applies; this credits file does not grant a new license to the project's original source/assets.
- Screenshots in `docs/evidence` are app captures and retain the underlying map/model attribution requirements.

## Software acknowledgments

React, Vite, Framer Motion, FastAPI, Pydantic, SQLAlchemy and FastEmbed use MIT licenses; MapLibre GL JS uses BSD-3-Clause; deck.gl/luma.gl use MIT; Playwright uses Apache-2.0. Dependency packages include their own notices and transitive licenses. Lockfiles identify exact versions; this asset inventory is not a replacement for those package notices.
