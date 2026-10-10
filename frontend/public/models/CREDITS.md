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
