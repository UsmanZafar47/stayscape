# StayScape M1: complete source

Every frontend source, configuration, test, and lockfile is reproduced below without omissions. Generated node_modules, dist, and test-results are not source.

- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/.env.example`
- `frontend/index.html`
- `frontend/tsconfig.json`
- `frontend/vite.config.ts`
- `frontend/playwright.config.ts`
- `frontend/src/main.tsx`
- `frontend/src/listings.ts`
- `frontend/src/MapScene.tsx`
- `frontend/src/App.tsx`
- `frontend/src/styles.css`
- `frontend/tests/map.spec.ts`
- `frontend/README.md`

## frontend/package.json

````json
{
  "name": "stayscape-map-spike",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "engines": { "node": "^20.19.0 || >=22.12.0" },
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
    "@luma.gl/core": "9.4.0",
    "maplibre-gl": "6.11.2",
    "react": "19.3.0",
    "react-dom": "19.3.0"
  },
  "devDependencies": {
    "@playwright/test": "1.63.0",
    "@types/node": "26.6.3",
    "@types/react": "19.3.0",
    "@types/react-dom": "19.3.0",
    "@vitejs/plugin-react": "6.1.1",
    "typescript": "7.0.2",
    "vite": "8.3.1"
  }
}
````

## frontend/package-lock.json

````json
{
  "name": "stayscape-map-spike",
  "version": "0.1.0",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {
      "name": "stayscape-map-spike",
      "version": "0.1.0",
      "dependencies": {
        "@deck.gl/core": "9.4.0",
        "@deck.gl/layers": "9.4.0",
        "@deck.gl/maplibre": "9.4.0",
        "@luma.gl/core": "9.4.0",
        "maplibre-gl": "6.11.2",
        "react": "19.3.0",
        "react-dom": "19.3.0"
      },
      "devDependencies": {
        "@playwright/test": "1.63.0",
        "@types/node": "26.6.3",
        "@types/react": "19.3.0",
        "@types/react-dom": "19.3.0",
        "@vitejs/plugin-react": "6.1.1",
        "typescript": "7.0.2",
        "vite": "8.3.1"
      },
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      }
    },
    "node_modules/@deck.gl/core": {
      "version": "9.4.0",
      "resolved": "https://registry.npmjs.org/@deck.gl/core/-/core-9.4.0.tgz",
      "integrity": "sha512-0isP+x2eGNxteO7lT650lYO7oiAYXAu4aF1jG+BMi8aKYh38HtPugLq1TlQTravIXzBSi5Oe1oZNuVj8h4ZEjA==",
      "license": "MIT",
      "dependencies": {
        "@loaders.gl/core": "^4.4.3",
        "@loaders.gl/images": "^4.4.3",
        "@luma.gl/core": "^9.4.0",
        "@luma.gl/engine": "^9.4.0",
        "@luma.gl/gpgpu": "^9.4.0",
        "@luma.gl/shadertools": "^9.4.0",
        "@luma.gl/webgl": "^9.4.0",
        "@math.gl/core": "^4.1.0",
        "@math.gl/sun": "^4.1.0",
        "@math.gl/types": "^4.1.0",
        "@math.gl/web-mercator": "^4.1.0",
        "@probe.gl/env": "^4.1.1",
        "@probe.gl/log": "^4.1.1",
        "@probe.gl/stats": "^4.1.1",
        "@types/offscreencanvas": "^2019.6.4",
        "gl-matrix": "^3.0.0",
        "mjolnir.js": "^3.1.1"
      }
    },
    "node_modules/@deck.gl/layers": {
      "version": "9.4.0",
      "resolved": "https://registry.npmjs.org/@deck.gl/layers/-/layers-9.4.0.tgz",
      "integrity": "sha512-jSL/xje2Ez7DmnP8AAIdhhg6IAtfXMmnXiUAKNgpl/TTaEL+iL5TAnagCdt39H3azmKVcCG33kOlIoWFAuLuRg==",
      "license": "MIT",
      "dependencies": {
        "@loaders.gl/images": "^4.4.3",
        "@loaders.gl/schema": "^4.4.3",
        "@luma.gl/shadertools": "^9.4.0",
        "@mapbox/tiny-sdf": "^2.0.5",
        "@math.gl/core": "^4.1.0",
        "@math.gl/polygon": "^4.1.0",
        "@math.gl/web-mercator": "^4.1.0",
        "@types/geojson": "^7946.0.16",
        "earcut": "^2.2.4"
      },
      "peerDependencies": {
        "@deck.gl/core": "~9.4.0",
        "@loaders.gl/core": "^4.4.3",
        "@luma.gl/core": "~9.4.0",
        "@luma.gl/engine": "~9.4.0"
      }
    },
    "node_modules/@deck.gl/maplibre": {
      "version": "9.4.0",
      "resolved": "https://registry.npmjs.org/@deck.gl/maplibre/-/maplibre-9.4.0.tgz",
      "integrity": "sha512-ck7Hxzt0t9M7iVgbVwelZiuUEx+e2HtmhGyPmZulURV0Ct5QtIjDYc6SWWUYZqASQnyDiBgFVaSaA9DisU8ziw==",
      "license": "MIT",
      "peerDependencies": {
        "@deck.gl/core": "~9.4.0",
        "@luma.gl/core": "~9.4.0",
        "maplibre-gl": "^4.5.1 || ^5.0.0 || ^6.0.0"
      }
    },
    "node_modules/@loaders.gl/core": {
      "version": "4.5.2",
      "resolved": "https://registry.npmjs.org/@loaders.gl/core/-/core-4.5.2.tgz",
      "integrity": "sha512-Al1NEd/tCz0KLWslqmEaGka9F/VpBLGUFyjb0Oc7zgmgvzJEAOMWac7nGgO8Zqobl4uVcC8HTkNSFCMV4PKIQw==",
      "license": "MIT",
      "dependencies": {
        "@loaders.gl/loader-utils": "4.5.2",
        "@loaders.gl/schema": "4.5.1",
        "@loaders.gl/schema-utils": "4.5.2",
        "@loaders.gl/worker-utils": "4.5.2",
        "@probe.gl/log": "^4.1.1"
      }
    },
    "node_modules/@loaders.gl/images": {
      "version": "4.5.2",
      "resolved": "https://registry.npmjs.org/@loaders.gl/images/-/images-4.5.2.tgz",
      "integrity": "sha512-Xw9pxuOrxISg2aCVtFmiytMFuxAHQc+KGy5roVGDfryZDYi494SGtgJaVAmWGY3pxOXkZ3em2BWJleG5W/jzXg==",
      "license": "MIT",
      "dependencies": {
        "@loaders.gl/loader-utils": "4.5.2"
      },
      "peerDependencies": {
        "@loaders.gl/core": "~4.5.0"
      }
    },
    "node_modules/@loaders.gl/loader-utils": {
      "version": "4.5.2",
      "resolved": "https://registry.npmjs.org/@loaders.gl/loader-utils/-/loader-utils-4.5.2.tgz",
      "integrity": "sha512-ov5se9HOmvgJasOHq9v2dyEfYGClSVQFyFwaD78BD8Nqz1xRxU5O5TRk19WpIExs9MFpNyqVgUHq1yE1PTwWLQ==",
      "license": "MIT",
      "dependencies": {
        "@loaders.gl/schema": "4.5.1",
        "@loaders.gl/worker-utils": "4.5.2",
        "@probe.gl/log": "^4.1.1",
        "@probe.gl/stats": "^4.1.1"
      }
    },
    "node_modules/@loaders.gl/schema": {
      "version": "4.5.1",
      "resolved": "https://registry.npmjs.org/@loaders.gl/schema/-/schema-4.5.1.tgz",
      "integrity": "sha512-qrMqcwIHQRCfAx/zkujuI8ZfiwaOXvh82y5OXVfPkGtAw5EhLBM3fQxqdNOpfVhy0m4GCC6QvlXyurJXcx++yQ==",
      "license": "MIT",
      "dependencies": {
        "@types/geojson": "^7946.0.7",
        "apache-arrow": ">= 17.0.0"
      }
    },
    "node_modules/@loaders.gl/schema-utils": {
      "version": "4.5.2",
      "resolved": "https://registry.npmjs.org/@loaders.gl/schema-utils/-/schema-utils-4.5.2.tgz",
      "integrity": "sha512-giaz4ZzmxuxhWNV1TSOazUksbgFBgnjtxFMHbikaDeBHYQNzHsGWGoG3SLsvmnKCJ5q/fUwFJZqRGqTVdBcoKg==",
      "license": "MIT",
      "dependencies": {
        "@loaders.gl/schema": "4.5.1",
        "@math.gl/types": "^4.1.0",
        "@types/geojson": "^7946.0.7",
        "apache-arrow": ">= 17.0.0"
      },
      "peerDependencies": {
        "@loaders.gl/core": "~4.5.0"
      }
    },
    "node_modules/@loaders.gl/worker-utils": {
      "version": "4.5.2",
      "resolved": "https://registry.npmjs.org/@loaders.gl/worker-utils/-/worker-utils-4.5.2.tgz",
      "integrity": "sha512-w5zWjtWQZRYME9Gk7v+u5tAs5bHa+09at10106vZ7wNI0YP4kbcVu424+vxP2dfppR54U2goiS1RY4QGYGXXcQ==",
      "license": "MIT",
      "peerDependencies": {
        "@loaders.gl/core": "~4.5.0"
      }
    },
    "node_modules/@luma.gl/core": {
      "version": "9.4.0",
      "resolved": "https://registry.npmjs.org/@luma.gl/core/-/core-9.4.0.tgz",
      "integrity": "sha512-2SIB77DoZ6LMZW/aPS/M3hKHP8UR0WR6f5R2+Sir5FdNVdOvFiOHAxPCafjVTxTqFWWHnh1NSCo5k/qq6sdFQw==",
      "license": "MIT",
      "dependencies": {
        "@math.gl/types": "^4.1.0",
        "@probe.gl/env": "^4.1.1",
        "@probe.gl/log": "^4.1.1",
        "@probe.gl/stats": "^4.1.1",
        "@types/offscreencanvas": "^2019.7.3"
      }
    },
    "node_modules/@luma.gl/engine": {
      "version": "9.4.2",
      "resolved": "https://registry.npmjs.org/@luma.gl/engine/-/engine-9.4.2.tgz",
      "integrity": "sha512-gBAcn+b1jOwE4pDF5zbuzMxCa/KGY3Q2Gq0gNUPU1AZHNk4aDgOEQaY2sqMsaoGHkDXB+pxneJQPw5c6Q5mnHA==",
      "license": "MIT",
      "dependencies": {
        "@math.gl/core": "^4.1.0",
        "@math.gl/types": "^4.1.0",
        "@probe.gl/log": "^4.1.1",
        "@probe.gl/stats": "^4.1.1"
      },
      "peerDependencies": {
        "@luma.gl/core": "~9.4.0",
        "@luma.gl/shadertools": "~9.4.0"
      }
    },
    "node_modules/@luma.gl/gpgpu": {
      "version": "9.4.2",
      "resolved": "https://registry.npmjs.org/@luma.gl/gpgpu/-/gpgpu-9.4.2.tgz",
      "integrity": "sha512-LoEqoViPZqMHqQzvq/txFuOLsxI6sn8xmv+IZyovRFBqcWaV184PE/8Ieufww0pjVyJMfubhUCQmGuGrOME8oA==",
      "license": "MIT",
      "dependencies": {
        "@math.gl/core": "^4.1.0",
        "@math.gl/types": "^4.1.0",
        "@probe.gl/log": "^4.0.8",
        "@probe.gl/stats": "^4.0.8"
      },
      "peerDependencies": {
        "@luma.gl/core": "~9.4.0",
        "@luma.gl/engine": "~9.4.0",
        "@luma.gl/shadertools": "~9.4.0",
        "@luma.gl/webgpu": "~9.4.0"
      }
    },
    "node_modules/@luma.gl/shadertools": {
      "version": "9.4.2",
      "resolved": "https://registry.npmjs.org/@luma.gl/shadertools/-/shadertools-9.4.2.tgz",
      "integrity": "sha512-0/6pLZSfnQnvcWdYePKKSwVet+gFtAAnKeGXNfxpgp3I8E3WsF/SbD6oEzgU7jdnRqONwGsoACWNpQHO0zZvIQ==",
      "license": "MIT",
      "dependencies": {
        "@math.gl/core": "^4.1.0",
        "@math.gl/types": "^4.1.0"
      },
      "peerDependencies": {
        "@luma.gl/core": "~9.4.0"
      }
    },
    "node_modules/@luma.gl/webgl": {
      "version": "9.4.2",
      "resolved": "https://registry.npmjs.org/@luma.gl/webgl/-/webgl-9.4.2.tgz",
      "integrity": "sha512-D3GqnxTgQI+vsyH56hX5+jwqdVUhvhbpnPurTwbQOSlSQ8mshhNKcRdrZytTy10qiodDwrcjTnndPEAP6UgCzA==",
      "license": "MIT",
      "dependencies": {
        "@math.gl/types": "^4.1.0",
        "@probe.gl/env": "^4.1.1"
      },
      "peerDependencies": {
        "@luma.gl/core": "~9.4.0"
      }
    },
    "node_modules/@luma.gl/webgpu": {
      "version": "9.4.2",
      "resolved": "https://registry.npmjs.org/@luma.gl/webgpu/-/webgpu-9.4.2.tgz",
      "integrity": "sha512-24gDOmLyL81fVHxn+UXajnYN5jVln7XgB9fvobc1Yh3PAtXjlcAkmVTqYRvULVGeEamuqvqPDscAkaK/T+R1iQ==",
      "license": "MIT",
      "peer": true,
      "dependencies": {
        "@probe.gl/env": "^4.1.1",
        "@webgpu/types": "^0.1.69"
      },
      "peerDependencies": {
        "@luma.gl/core": "~9.4.0",
        "@luma.gl/shadertools": "~9.4.0"
      }
    },
    "node_modules/@mapbox/jsonlint-lines-primitives": {
      "version": "2.0.3",
      "resolved": "https://registry.npmjs.org/@mapbox/jsonlint-lines-primitives/-/jsonlint-lines-primitives-2.0.3.tgz",
      "integrity": "sha512-0SElaV0uMxEnxzBhhX9WTuPyUeMsAN/SS0i16tjuba4/mio63MG9khjC1a0JAiPGXAwvwm4UfHJURCN7nyudQg==",
      "license": "MIT",
      "engines": {
        "node": ">= 22"
      }
    },
    "node_modules/@mapbox/point-geometry": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/@mapbox/point-geometry/-/point-geometry-1.1.0.tgz",
      "integrity": "sha512-YGcBz1cg4ATXDCM/71L9xveh4dynfGmcLDqufR+nQQy3fKwsAZsWd/x4621/6uJaeB9mwOHE6hPeDgXz9uViUQ==",
      "license": "ISC"
    },
    "node_modules/@mapbox/tiny-sdf": {
      "version": "2.2.0",
      "resolved": "https://registry.npmjs.org/@mapbox/tiny-sdf/-/tiny-sdf-2.2.0.tgz",
      "integrity": "sha512-LVL4wgI9YAum5V+LNVQO6QgFBPw7/MIIY4XJPNsPDMrjEwcE+JfKk1LuIl8GnF197ejVdC9QdPaxrx5gfgdGXg==",
      "license": "BSD-2-Clause"
    },
    "node_modules/@mapbox/unitbezier": {
      "version": "1.0.0",
      "resolved": "https://registry.npmjs.org/@mapbox/unitbezier/-/unitbezier-1.0.0.tgz",
      "integrity": "sha512-fqd515fjBmANKGGsQ286E2Wvj/XvDFpGzwJxq4CI6jMQue6Oy04uCKp+JWKF00xRTmk6cEu1jPJ9p3xqH8YWqQ==",
      "license": "BSD-2-Clause"
    },
    "node_modules/@mapbox/vector-tile": {
      "version": "3.0.0",
      "resolved": "https://registry.npmjs.org/@mapbox/vector-tile/-/vector-tile-3.0.0.tgz",
      "integrity": "sha512-Qf10S1uIHMk20ri/IVBnpS+esUEkVaR5Hftmz88jTInrpmWgPGJfPe3LVjjlE77trLx8tH6qjTG7uWH9hIq/0Q==",
      "license": "BSD-3-Clause",
      "dependencies": {
        "@mapbox/point-geometry": "~1.1.0",
        "@types/geojson": "^7946.0.16",
        "pbf": "^5.0.0"
      }
    },
    "node_modules/@maplibre/geojson-vt": {
      "version": "6.1.1",
      "resolved": "https://registry.npmjs.org/@maplibre/geojson-vt/-/geojson-vt-6.1.1.tgz",
      "integrity": "sha512-FVMOcmSP/yqol45t7StApEyTL5/vmqBCuFhH9n+fFuINenhaX+YgHHIt1yJ86S8kln3uJLcMvmEU2cfn6E2eCQ==",
      "license": "ISC",
      "dependencies": {
        "kdbush": "^4.1.0"
      }
    },
    "node_modules/@maplibre/maplibre-gl-style-spec": {
      "version": "26.4.4",
      "resolved": "https://registry.npmjs.org/@maplibre/maplibre-gl-style-spec/-/maplibre-gl-style-spec-26.4.4.tgz",
      "integrity": "sha512-hG4RZR4PBd/+6A3ODdZ3AnQRF106ZQk1y3bhwDg8bH/A4Oz2tnRUJVVWs9BZa6gXZ1d3UKe89C+Mm+olGBELvA==",
      "license": "ISC",
      "dependencies": {
        "@mapbox/jsonlint-lines-primitives": "^2.0.3",
        "@mapbox/unitbezier": "^1.0.0",
        "json-stringify-pretty-compact": "^4.0.0",
        "minimist": "^1.2.8",
        "quickselect": "^3.0.0",
        "tinyqueue": "^3.0.0"
      },
      "bin": {
        "gl-style-format": "dist/gl-style-format.mjs",
        "gl-style-migrate": "dist/gl-style-migrate.mjs",
        "gl-style-validate": "dist/gl-style-validate.mjs"
      }
    },
    "node_modules/@maplibre/mlt": {
      "version": "1.3.0",
      "resolved": "https://registry.npmjs.org/@maplibre/mlt/-/mlt-1.3.0.tgz",
      "integrity": "sha512-7M2O7ABM80Oi8XPkfkrjKB8mOBIxGoVgkA52Mu4RMWoBvvMdagQ522+WxVYujZsMpqIr3BpzrTbXrm4k8lCzCQ==",
      "license": "(MIT OR Apache-2.0)",
      "dependencies": {
        "@mapbox/point-geometry": "^1.1.0"
      }
    },
    "node_modules/@maplibre/vt-pbf": {
      "version": "4.3.2",
      "resolved": "https://registry.npmjs.org/@maplibre/vt-pbf/-/vt-pbf-4.3.2.tgz",
      "integrity": "sha512-j6p0AdjvAR19Z3XaCysle7A4ZSo08tYOzxD0Y9NQylwPAkwJJeYub5b2eVucdeDh7erhv69DahoLOevDRERRUw==",
      "license": "MIT",
      "dependencies": {
        "@mapbox/point-geometry": "^1.1.0",
        "@types/geojson": "^7946.0.16",
        "pbf": "^5.1.0"
      }
    },
    "node_modules/@math.gl/core": {
      "version": "4.1.0",
      "resolved": "https://registry.npmjs.org/@math.gl/core/-/core-4.1.0.tgz",
      "integrity": "sha512-FrdHBCVG3QdrworwrUSzXIaK+/9OCRLscxI2OUy6sLOHyHgBMyfnEGs99/m3KNvs+95BsnQLWklVfpKfQzfwKA==",
      "license": "MIT",
      "dependencies": {
        "@math.gl/types": "4.1.0"
      }
    },
    "node_modules/@math.gl/polygon": {
      "version": "4.1.0",
      "resolved": "https://registry.npmjs.org/@math.gl/polygon/-/polygon-4.1.0.tgz",
      "integrity": "sha512-YA/9PzaCRHbIP5/0E9uTYrqe+jsYTQoqoDWhf6/b0Ixz8bPZBaGDEafLg3z7ffBomZLacUty9U3TlPjqMtzPjA==",
      "license": "MIT",
      "dependencies": {
        "@math.gl/core": "4.1.0"
      }
    },
    "node_modules/@math.gl/sun": {
      "version": "4.1.0",
      "resolved": "https://registry.npmjs.org/@math.gl/sun/-/sun-4.1.0.tgz",
      "integrity": "sha512-i3q6OCBLSZ5wgZVhXg+X7gsjY/TUtuFW/2KBiq/U1ypLso3S4sEykoU/MGjxUv1xiiGtr+v8TeMbO1OBIh/HmA==",
      "license": "MIT"
    },
    "node_modules/@math.gl/types": {
      "version": "4.1.0",
      "resolved": "https://registry.npmjs.org/@math.gl/types/-/types-4.1.0.tgz",
      "integrity": "sha512-clYZdHcmRvMzVK5fjeDkQlHUzXQSNdZ7s4xOqC3nJPgz4C/TZkUecTo9YS4PruZqtDda/ag4erndP0MIn40dGA==",
      "license": "MIT"
    },
    "node_modules/@math.gl/web-mercator": {
      "version": "4.1.0",
      "resolved": "https://registry.npmjs.org/@math.gl/web-mercator/-/web-mercator-4.1.0.tgz",
      "integrity": "sha512-HZo3vO5GCMkXJThxRJ5/QYUYRr3XumfT8CzNNCwoJfinxy5NtKUd7dusNTXn7yJ40UoB8FMIwkVwNlqaiRZZAw==",
      "license": "MIT",
      "dependencies": {
        "@math.gl/core": "4.1.0"
      }
    },
    "node_modules/@oxc-project/types": {
      "version": "0.151.0",
      "resolved": "https://registry.npmjs.org/@oxc-project/types/-/types-0.151.0.tgz",
      "integrity": "sha512-J1yXrIlNDZVzE3ada310xeAw7nH8yCAyLPuUIsjKatFPmfn5bS1oW+cM+QsGOtVWd5nhSpbwZWx/rue+r5Z+PA==",
      "dev": true,
      "license": "MIT",
      "funding": {
        "url": "https://github.com/sponsors/oxc-project"
      }
    },
    "node_modules/@playwright/test": {
      "version": "1.63.0",
      "resolved": "https://registry.npmjs.org/@playwright/test/-/test-1.63.0.tgz",
      "integrity": "sha512-oxMK4vllB9RK5NQ2l1pq1IfOf2AvnEuj/vYGDj0H2nMtmtZpKtCwt/l00GEO6xjGfpBNAvjovvYdCm50dRQkpQ==",
      "dev": true,
      "license": "Apache-2.0",
      "dependencies": {
        "playwright": "1.63.0"
      },
      "bin": {
        "playwright": "cli.js"
      },
      "engines": {
        "node": ">=20"
      }
    },
    "node_modules/@probe.gl/env": {
      "version": "4.1.2",
      "resolved": "https://registry.npmjs.org/@probe.gl/env/-/env-4.1.2.tgz",
      "integrity": "sha512-KIcdjrEiEZVIGX9nh7pZSmTMIKrd+wCb09gyXqpYYI4hs9WMqrQHvKZ7KD8ASutf6kwARwgd4WNQn8aucLSz3g==",
      "license": "MIT"
    },
    "node_modules/@probe.gl/log": {
      "version": "4.1.2",
      "resolved": "https://registry.npmjs.org/@probe.gl/log/-/log-4.1.2.tgz",
      "integrity": "sha512-2LqSq4CHhc/HJQasHMPOzA6c7rprlGz8CCREGebo19jxcuKdvXQo0DEmlfId076U6UldMp6jGhWvDHEFLX111Q==",
      "license": "MIT",
      "dependencies": {
        "@probe.gl/env": "4.1.2"
      }
    },
    "node_modules/@probe.gl/stats": {
      "version": "4.1.2",
      "resolved": "https://registry.npmjs.org/@probe.gl/stats/-/stats-4.1.2.tgz",
      "integrity": "sha512-Hqc0UIHd0IZ2+JbovzTz7lYG7CY9D8yCB81zyP92Zl9UDSPcw2cLbTySW14keAQeAo1sjGjUw0+KHxr0Y2h/hA==",
      "license": "MIT"
    },
    "node_modules/@rolldown/binding-android-arm-eabi": {
      "version": "1.2.11",
      "resolved": "https://registry.npmjs.org/@rolldown/binding-android-arm-eabi/-/binding-android-arm-eabi-1.2.11.tgz",
      "integrity": "sha512-A5kXfGKvKWWZE0TtPrfsvT+q4Y5d1QG8gGUzpYjGydM+fARM9MuX90PrXYXe0XbsDVgyxxNzHo6giCj90bsFNw==",
      "cpu": [
        "arm"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "android"
      ],
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      }
    },
    "node_modules/@rolldown/binding-android-arm64": {
      "version": "1.2.11",
      "resolved": "https://registry.npmjs.org/@rolldown/binding-android-arm64/-/binding-android-arm64-1.2.11.tgz",
      "integrity": "sha512-z6cTycz+iJ4PVkuL4HHW4DfTfoeU/2nqYYuSOrTmH7yHK5Y0LCOnA03V4ZNxavyVaU1oOqUgIg2klN/s+USGOA==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "android"
      ],
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      }
    },
    "node_modules/@rolldown/binding-darwin-arm64": {
      "version": "1.2.11",
      "resolved": "https://registry.npmjs.org/@rolldown/binding-darwin-arm64/-/binding-darwin-arm64-1.2.11.tgz",
      "integrity": "sha512-jShvqNtP6vDC6/A5JOAzbVV+DkgHqhl/ScVCJEbt+TUY6QYz7YnXcrg3sLtFBniro0f/Ld50ZwCWA6f7KYD1nQ==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      }
    },
    "node_modules/@rolldown/binding-darwin-x64": {
      "version": "1.2.11",
      "resolved": "https://registry.npmjs.org/@rolldown/binding-darwin-x64/-/binding-darwin-x64-1.2.11.tgz",
      "integrity": "sha512-f2i2xiNWq1Z1l2++q2fuhZRdLAT3aqxD6vRNm1RAxpUoBcdqNB3C0s1Bt+K+PbEx2F5F4gQp6hqKkphCY/xF9w==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      }
    },
    "node_modules/@rolldown/binding-freebsd-x64": {
      "version": "1.2.11",
      "resolved": "https://registry.npmjs.org/@rolldown/binding-freebsd-x64/-/binding-freebsd-x64-1.2.11.tgz",
      "integrity": "sha512-4Ir5FSOKIAMr4r0kExpt1s3bMgzJU3rA45AYOHtQpls0oNeqcYBKrWMlckrYH4KCfGLfkfn1tN1dmZPMVsdXow==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "freebsd"
      ],
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      }
    },
    "node_modules/@rolldown/binding-linux-arm-gnueabihf": {
      "version": "1.2.11",
      "resolved": "https://registry.npmjs.org/@rolldown/binding-linux-arm-gnueabihf/-/binding-linux-arm-gnueabihf-1.2.11.tgz",
      "integrity": "sha512-/gnRDM+39BROzAN/k1OZjDPnDMcZxB/0EUxKjONO5yVkNEvlsoMDrxGNKgZi/ttFriS2gwlDNzB65pvNbFOXIQ==",
      "cpu": [
        "arm"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      }
    },
    "node_modules/@rolldown/binding-linux-arm64-gnu": {
      "version": "1.2.11",
      "resolved": "https://registry.npmjs.org/@rolldown/binding-linux-arm64-gnu/-/binding-linux-arm64-gnu-1.2.11.tgz",
      "integrity": "sha512-PFaK8HwvAHbaKbBcDNQihjMKYvFnA5hiENx/l5tphTDz1E0WFp32l0A7aq7lyUwGsRw/xSrNIy/gIK4thrSCrw==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "libc": [
        "glibc"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      }
    },
    "node_modules/@rolldown/binding-linux-arm64-musl": {
      "version": "1.2.11",
      "resolved": "https://registry.npmjs.org/@rolldown/binding-linux-arm64-musl/-/binding-linux-arm64-musl-1.2.11.tgz",
      "integrity": "sha512-AskzJUIKRLPxkruR1wLKewGbOw+EYfU/9lOrBFj4AFrEA8hPpKFnODWNu2WLaNs0QNkEb9QIJufmVZZIL/bJlg==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "libc": [
        "musl"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      }
    },
    "node_modules/@rolldown/binding-linux-ppc64-gnu": {
      "version": "1.2.11",
      "resolved": "https://registry.npmjs.org/@rolldown/binding-linux-ppc64-gnu/-/binding-linux-ppc64-gnu-1.2.11.tgz",
      "integrity": "sha512-qlUGAheh2yh8afH7QBgx0PrRHN85hKnNd78x8MeMhXivuevgd8vgf6/CstOzmNKY/lLTHvNTrPy98cLnAugzJw==",
      "cpu": [
        "ppc64"
      ],
      "dev": true,
      "libc": [
        "glibc"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      }
    },
    "node_modules/@rolldown/binding-linux-s390x-gnu": {
      "version": "1.2.11",
      "resolved": "https://registry.npmjs.org/@rolldown/binding-linux-s390x-gnu/-/binding-linux-s390x-gnu-1.2.11.tgz",
      "integrity": "sha512-secpEad+0vCbSfn8upFySkDskv+bGPk3THSDS9Y89yc4rb4kzqHp8Dmyd9BkQW4SnhNXBZCl/6CrO//hZahNJQ==",
      "cpu": [
        "s390x"
      ],
      "dev": true,
      "libc": [
        "glibc"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      }
    },
    "node_modules/@rolldown/binding-linux-x64-gnu": {
      "version": "1.2.11",
      "resolved": "https://registry.npmjs.org/@rolldown/binding-linux-x64-gnu/-/binding-linux-x64-gnu-1.2.11.tgz",
      "integrity": "sha512-mOVBT3dPpkWm8XBWPmU4bf+U6dYDLeMo/9ojUmis4N0L5uu10qra5vOyngZ7/PSdoE4G9KvRt4bloRxNjLas7A==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "libc": [
        "glibc"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      }
    },
    "node_modules/@rolldown/binding-linux-x64-musl": {
      "version": "1.2.11",
      "resolved": "https://registry.npmjs.org/@rolldown/binding-linux-x64-musl/-/binding-linux-x64-musl-1.2.11.tgz",
      "integrity": "sha512-Is78i9A8Ui4SqcxUwFJ9uMmjDn58IbVTjFWYdQestFEgeuEmHMLGNriXnVJKkwG2YiZjw8cP0zCTyDMdDGtOOg==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "libc": [
        "musl"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      }
    },
    "node_modules/@rolldown/binding-openharmony-arm64": {
      "version": "1.2.11",
      "resolved": "https://registry.npmjs.org/@rolldown/binding-openharmony-arm64/-/binding-openharmony-arm64-1.2.11.tgz",
      "integrity": "sha512-dUCXneZ87INUMyQ0D+C0HrEBNUPNXHaPmU5GTjyKTJEiussw9Kaj5Ln8UztPe4epV/ffvgNBEadksdYhmW6xJA==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "openharmony"
      ],
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      }
    },
    "node_modules/@rolldown/binding-win32-arm64-msvc": {
      "version": "1.2.11",
      "resolved": "https://registry.npmjs.org/@rolldown/binding-win32-arm64-msvc/-/binding-win32-arm64-msvc-1.2.11.tgz",
      "integrity": "sha512-jByxb6qfd+bH1xUd0qnfFnb17i9sWBPY2tOavJ0l3tdr3OTu+Kvtm8cd/JV5nFt657b1VqGltxg9olOEfofXWw==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      }
    },
    "node_modules/@rolldown/binding-win32-x64-msvc": {
      "version": "1.2.11",
      "resolved": "https://registry.npmjs.org/@rolldown/binding-win32-x64-msvc/-/binding-win32-x64-msvc-1.2.11.tgz",
      "integrity": "sha512-/PzKqzAJ03i19oy2ItPvyvaVjOjBCNnfaJs8yvUdGBKmiESgnrJSQ2awd81QzFbbnAmu7YO9ZnJrDCb9VSJPRA==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      }
    },
    "node_modules/@rolldown/pluginutils": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/@rolldown/pluginutils/-/pluginutils-1.0.1.tgz",
      "integrity": "sha512-2j9bGt5Jh8hj+vPtgzPtl72j0yRxHAyumoo6TNfAjsLB04UtpSvPbPcDcBMxz7n+9CYB0c1GxQFxYRg2jimqGw==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/@types/geojson": {
      "version": "7946.0.16",
      "resolved": "https://registry.npmjs.org/@types/geojson/-/geojson-7946.0.16.tgz",
      "integrity": "sha512-6C8nqWur3j98U6+lXDfTUWIfgvZU+EumvpHKcYjujKH7woYyLj2sUmff0tRhrqM7BohUw7Pz3ZB1jj2gW9Fvmg==",
      "license": "MIT"
    },
    "node_modules/@types/node": {
      "version": "26.6.3",
      "resolved": "https://registry.npmjs.org/@types/node/-/node-26.6.3.tgz",
      "integrity": "sha512-dsqMQQoeTLqu9wynDD00q573mNzso3IdQOAfHRJqLCcmCFPoGo9A1bDpUcv/9tnKpErQWv9uKeGfl37EIS02Yg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "undici-types": "~8.9.0"
      }
    },
    "node_modules/@types/offscreencanvas": {
      "version": "2019.7.3",
      "resolved": "https://registry.npmjs.org/@types/offscreencanvas/-/offscreencanvas-2019.7.3.tgz",
      "integrity": "sha512-ieXiYmgSRXUDeOntE1InxjWyvEelZGP63M+cGuquuRLuIKKT1osnkXjxev9B7d1nXSug5vpunx+gNlbVxMlC9A==",
      "license": "MIT"
    },
    "node_modules/@types/react": {
      "version": "19.3.0",
      "resolved": "https://registry.npmjs.org/@types/react/-/react-19.3.0.tgz",
      "integrity": "sha512-N0rFCuH9YoxG9/m61l9MfpJKfmLOVU0em7ipIz6TRgSSkvReLB9vL85GB+yr8Bs5leqpvg96JSwF4ZS1s4viQg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "csstype": "^3.2.2"
      }
    },
    "node_modules/@types/react-dom": {
      "version": "19.3.0",
      "resolved": "https://registry.npmjs.org/@types/react-dom/-/react-dom-19.3.0.tgz",
      "integrity": "sha512-ZI7bU42mZXXKHn/qNLEw2IrbiINU7X5+vfgdixBHkCNpYWXjKgfQ/P+uyGb5CjOLB9UcnTeg3rylQtV2hym44Q==",
      "dev": true,
      "license": "MIT",
      "peerDependencies": {
        "@types/react": "^19.3.0"
      }
    },
    "node_modules/@typescript/typescript-aix-ppc64": {
      "version": "7.0.2",
      "resolved": "https://registry.npmjs.org/@typescript/typescript-aix-ppc64/-/typescript-aix-ppc64-7.0.2.tgz",
      "integrity": "sha512-MTKKkWB7p/0E9xi1d1tHtZ5PiLkGEMIq88pK2CubZjOsLtYTLqhgIgi6zepFa+9GHZ6h05NMCkQxGKiPXMxXtQ==",
      "cpu": [
        "ppc64"
      ],
      "dev": true,
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "aix"
      ],
      "engines": {
        "node": ">=16.20.0"
      }
    },
    "node_modules/@typescript/typescript-darwin-arm64": {
      "version": "7.0.2",
      "resolved": "https://registry.npmjs.org/@typescript/typescript-darwin-arm64/-/typescript-darwin-arm64-7.0.2.tgz",
      "integrity": "sha512-gowzar9MwS/aRWp6f3a4KUqzRjAZjOsmGNCM6LcTgXum+dBfgsBVMN+AgvOCCbguXyick6LJhpBszxMebJ8syA==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": ">=16.20.0"
      }
    },
    "node_modules/@typescript/typescript-darwin-x64": {
      "version": "7.0.2",
      "resolved": "https://registry.npmjs.org/@typescript/typescript-darwin-x64/-/typescript-darwin-x64-7.0.2.tgz",
      "integrity": "sha512-SZ9xZInqApNlNGc9s0W1VSsktYSOe9cFqNOIqmN1Gs8SmkjKZYFt017G4VwPxASInODuAdbTW7sXiFUf893RgA==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": ">=16.20.0"
      }
    },
    "node_modules/@typescript/typescript-freebsd-arm64": {
      "version": "7.0.2",
      "resolved": "https://registry.npmjs.org/@typescript/typescript-freebsd-arm64/-/typescript-freebsd-arm64-7.0.2.tgz",
      "integrity": "sha512-W5NH4y/J0plIIS5b2xvTEkU7JFxyqdMAOgf+Ilhl0vHQXKO5dZoxd+C/jEtq56c4F3wk71RB4BMRQ2XdI+bwYQ==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "freebsd"
      ],
      "engines": {
        "node": ">=16.20.0"
      }
    },
    "node_modules/@typescript/typescript-freebsd-x64": {
      "version": "7.0.2",
      "resolved": "https://registry.npmjs.org/@typescript/typescript-freebsd-x64/-/typescript-freebsd-x64-7.0.2.tgz",
      "integrity": "sha512-UMGDx5sTpzNw3WiPebH7l90IWfJggEd+egHt/q6p7/Cm3zqoV7VxkGXt+3DxPIw8CcmvAB0j3sVVfbhX+M4Tpw==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "freebsd"
      ],
      "engines": {
        "node": ">=16.20.0"
      }
    },
    "node_modules/@typescript/typescript-linux-arm": {
      "version": "7.0.2",
      "resolved": "https://registry.npmjs.org/@typescript/typescript-linux-arm/-/typescript-linux-arm-7.0.2.tgz",
      "integrity": "sha512-gffT3xPz9sR7j/YJExkyPntrI0P2EP9XbOyWzth2/Gs0RstK+90RBcO0ncXoXy/beYll1SXw846Nf2zdnEz0QQ==",
      "cpu": [
        "arm"
      ],
      "dev": true,
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">=16.20.0"
      }
    },
    "node_modules/@typescript/typescript-linux-arm64": {
      "version": "7.0.2",
      "resolved": "https://registry.npmjs.org/@typescript/typescript-linux-arm64/-/typescript-linux-arm64-7.0.2.tgz",
      "integrity": "sha512-Qh4eU4/y3yDjnfjjyPYihMj5/ODIlmt+Bzu17OI+fiSRDW57QmU5SiN63exPRNJPKUzcc1INa1NXdrJ+MqHjUQ==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">=16.20.0"
      }
    },
    "node_modules/@typescript/typescript-linux-loong64": {
      "version": "7.0.2",
      "resolved": "https://registry.npmjs.org/@typescript/typescript-linux-loong64/-/typescript-linux-loong64-7.0.2.tgz",
      "integrity": "sha512-uEHck9i8hoAzXPiYRib1O7miOnz23SxIeVl6F4LXox+qov1K35jHcEW6VHKvZI+pyvl7fZEP4MCU5LYvIq1GuQ==",
      "cpu": [
        "loong64"
      ],
      "dev": true,
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">=16.20.0"
      }
    },
    "node_modules/@typescript/typescript-linux-mips64el": {
      "version": "7.0.2",
      "resolved": "https://registry.npmjs.org/@typescript/typescript-linux-mips64el/-/typescript-linux-mips64el-7.0.2.tgz",
      "integrity": "sha512-R4KvAMnE43W5Qeqb0Ly56O3mWMWIAgsMyz36DCaycd5nbg/9kzm0liw3JocfRqyJY0KPmzFjbswozXyW0DnIYA==",
      "cpu": [
        "mips64el"
      ],
      "dev": true,
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">=16.20.0"
      }
    },
    "node_modules/@typescript/typescript-linux-ppc64": {
      "version": "7.0.2",
      "resolved": "https://registry.npmjs.org/@typescript/typescript-linux-ppc64/-/typescript-linux-ppc64-7.0.2.tgz",
      "integrity": "sha512-DORx5b3sd/4S7eayxm4FQv+A7CrkUIGRaHiwI8oiHTAI1fAPWhF4J0vAlkC8biAlHSVVwxMQ3tjZ2/DVbnQiiA==",
      "cpu": [
        "ppc64"
      ],
      "dev": true,
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">=16.20.0"
      }
    },
    "node_modules/@typescript/typescript-linux-riscv64": {
      "version": "7.0.2",
      "resolved": "https://registry.npmjs.org/@typescript/typescript-linux-riscv64/-/typescript-linux-riscv64-7.0.2.tgz",
      "integrity": "sha512-wf0jqEDOjrPRnKwYRyyJDRo11KMbvMFrU+q4zqKyChODBzvlkbhNQfKvLxQCcwTpdDaXSHZTVuh0JoCrKCUMHQ==",
      "cpu": [
        "riscv64"
      ],
      "dev": true,
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">=16.20.0"
      }
    },
    "node_modules/@typescript/typescript-linux-s390x": {
      "version": "7.0.2",
      "resolved": "https://registry.npmjs.org/@typescript/typescript-linux-s390x/-/typescript-linux-s390x-7.0.2.tgz",
      "integrity": "sha512-IkwJc3L7yhytWd/ewjyxNDfOmswCm9GWMJT/ue/dU4aZNbwZeYAetq42VyLmsmSjvoX7z74X6ZaYCtzAr0EuGw==",
      "cpu": [
        "s390x"
      ],
      "dev": true,
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">=16.20.0"
      }
    },
    "node_modules/@typescript/typescript-linux-x64": {
      "version": "7.0.2",
      "resolved": "https://registry.npmjs.org/@typescript/typescript-linux-x64/-/typescript-linux-x64-7.0.2.tgz",
      "integrity": "sha512-EYdf2cNg7rgCWJnxCdJ+F3V39O8ihb37eHAu1LK8oAFizgTQbPOK7zHHXbPt8rX24COqODXeI3sIf0fCXG7H/A==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">=16.20.0"
      }
    },
    "node_modules/@typescript/typescript-netbsd-arm64": {
      "version": "7.0.2",
      "resolved": "https://registry.npmjs.org/@typescript/typescript-netbsd-arm64/-/typescript-netbsd-arm64-7.0.2.tgz",
      "integrity": "sha512-+polYF4MF04aPpO5FTkHran9yUQDSXqy5GiSDKpsll5jy3l3+g9QLhpf39T+ePtefhXLOGrLl0QIjkQP6VnelA==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "netbsd"
      ],
      "engines": {
        "node": ">=16.20.0"
      }
    },
    "node_modules/@typescript/typescript-netbsd-x64": {
      "version": "7.0.2",
      "resolved": "https://registry.npmjs.org/@typescript/typescript-netbsd-x64/-/typescript-netbsd-x64-7.0.2.tgz",
      "integrity": "sha512-8YIT0EHM/3dq10ZOVF/A7pc/YSMtbcecct4rWtexrnSCHOPcpC2KTLXfTCR6vDpnSiY12heNb1GiN/wu+T/FyA==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "netbsd"
      ],
      "engines": {
        "node": ">=16.20.0"
      }
    },
    "node_modules/@typescript/typescript-openbsd-arm64": {
      "version": "7.0.2",
      "resolved": "https://registry.npmjs.org/@typescript/typescript-openbsd-arm64/-/typescript-openbsd-arm64-7.0.2.tgz",
      "integrity": "sha512-APT8+ClYnuYm1u9+kgGXoMj2VzWzcymwh2gNSQVySHfkRDGOTVkoWLjCmOQSaO+PoqQ57B0flRp9SA+7GnnkzQ==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "openbsd"
      ],
      "engines": {
        "node": ">=16.20.0"
      }
    },
    "node_modules/@typescript/typescript-openbsd-x64": {
      "version": "7.0.2",
      "resolved": "https://registry.npmjs.org/@typescript/typescript-openbsd-x64/-/typescript-openbsd-x64-7.0.2.tgz",
      "integrity": "sha512-yX7s+Q0Dln0Dt9tEzZsAjXXR/+ytBM7AlglaqyeMPxQszJ1JhlJdZ6jLA+IzldHtflX81em7lDao1xXu+aRRkg==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "openbsd"
      ],
      "engines": {
        "node": ">=16.20.0"
      }
    },
    "node_modules/@typescript/typescript-sunos-x64": {
      "version": "7.0.2",
      "resolved": "https://registry.npmjs.org/@typescript/typescript-sunos-x64/-/typescript-sunos-x64-7.0.2.tgz",
      "integrity": "sha512-dLJDGaLZ1D4HPQn62u1n8mBDkJREwMsAkCdkwd4Ieqw+x3TUyTsqY0YiBCtE6H6OzzgGk3iuZ3vFWRS+E8/d1g==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "sunos"
      ],
      "engines": {
        "node": ">=16.20.0"
      }
    },
    "node_modules/@typescript/typescript-win32-arm64": {
      "version": "7.0.2",
      "resolved": "https://registry.npmjs.org/@typescript/typescript-win32-arm64/-/typescript-win32-arm64-7.0.2.tgz",
      "integrity": "sha512-Gyl1Vy6OsWesLzmq+EP0Fb7b4Nid5232AvcA2SFcdYreldpNtYFFofPjnt62y9hQy7VTaZp65ICJjuAQRaVcIQ==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": ">=16.20.0"
      }
    },
    "node_modules/@typescript/typescript-win32-x64": {
      "version": "7.0.2",
      "resolved": "https://registry.npmjs.org/@typescript/typescript-win32-x64/-/typescript-win32-x64-7.0.2.tgz",
      "integrity": "sha512-0BQ3HkAHHlKLSp1qRvf3SUhGpGsDuhB/jgFw75guyqbxJqEaS0Cw/VFO8i2nHglJUzQCRtMMR/IBAKE3ETMC4g==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": ">=16.20.0"
      }
    },
    "node_modules/@vitejs/plugin-react": {
      "version": "6.1.1",
      "resolved": "https://registry.npmjs.org/@vitejs/plugin-react/-/plugin-react-6.1.1.tgz",
      "integrity": "sha512-yxLaQV9gkhS8ezJqCM6+ndU7mDY6gqAg75NQ+0IjwEI8IYOmQCgkRwHKVSfWXW076DsqMo0Dk+0FK1U+M5RgFw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@rolldown/pluginutils": "^1.0.1"
      },
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      },
      "peerDependencies": {
        "@rolldown/plugin-babel": "^0.1.7 || ^0.2.0",
        "babel-plugin-react-compiler": "^1.0.0",
        "oxc-transform-react": "^0.145.0",
        "vite": "^8.0.0"
      },
      "peerDependenciesMeta": {
        "@rolldown/plugin-babel": {
          "optional": true
        },
        "babel-plugin-react-compiler": {
          "optional": true
        },
        "oxc-transform-react": {
          "optional": true
        }
      }
    },
    "node_modules/@webgpu/types": {
      "version": "0.1.74",
      "resolved": "https://registry.npmjs.org/@webgpu/types/-/types-0.1.74.tgz",
      "integrity": "sha512-lgiI4hbuLcI9unnm2cL/tvCaQU45dp0xcLWJh5uB/9MBGvIA4F8XIk7nSiBeg+K4xWGYwgZKn80LmERI5CxoTA==",
      "license": "BSD-3-Clause",
      "peer": true
    },
    "node_modules/apache-arrow": {
      "version": "21.2.0",
      "resolved": "https://registry.npmjs.org/apache-arrow/-/apache-arrow-21.2.0.tgz",
      "integrity": "sha512-Hxe6Agq26gQOM954qpzYSllJBPJl+e16U5CkfuMUhLrNba+5nKkttIVlflaovN6oaTratqMGAO8H5u/aNhmHWQ==",
      "license": "Apache-2.0",
      "dependencies": {
        "@types/node": "^25.2.0",
        "flatbuffers": "^25.1.24",
        "json-with-bigint": "^3.5.3",
        "tslib": "^2.6.2"
      },
      "bin": {
        "arrow2csv": "bin/arrow2csv.js"
      }
    },
    "node_modules/apache-arrow/node_modules/@types/node": {
      "version": "25.9.8",
      "resolved": "https://registry.npmjs.org/@types/node/-/node-25.9.8.tgz",
      "integrity": "sha512-VfMrScDmMhUJQmd5hArdQnFvK0OIeD36uN2Va1FcpYaLB/BgkgM8Ulc50XtYISPMz7APJ30+N0T5EM0jlcdfRw==",
      "license": "MIT",
      "dependencies": {
        "undici-types": ">=7.24.0 <7.24.7"
      }
    },
    "node_modules/apache-arrow/node_modules/undici-types": {
      "version": "7.24.6",
      "resolved": "https://registry.npmjs.org/undici-types/-/undici-types-7.24.6.tgz",
      "integrity": "sha512-WRNW+sJgj5OBN4/0JpHFqtqzhpbnV0GuB+OozA9gCL7a993SmU+1JBZCzLNxYsbMfIeDL+lTsphD5jN5N+n0zg==",
      "license": "MIT"
    },
    "node_modules/bidi-js": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/bidi-js/-/bidi-js-1.1.0.tgz",
      "integrity": "sha512-fX1Onk0tdVPC7obPWB5EbJ1z7NVhLq4m2xZLq2YXBkxzMXIGRpNMU88n0EPgWseKl12J7zXs7qrDxPK4sRs2fg==",
      "license": "MIT",
      "dependencies": {
        "require-from-string": "^2.0.2"
      }
    },
    "node_modules/csstype": {
      "version": "3.2.3",
      "resolved": "https://registry.npmjs.org/csstype/-/csstype-3.2.3.tgz",
      "integrity": "sha512-z1HGKcYy2xA8AGQfwrn0PAy+PB7X/GSj3UVJW9qKyn43xWa+gl5nXmU4qqLMRzWVLFC8KusUX8T/0kCiOYpAIQ==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/detect-libc": {
      "version": "2.1.2",
      "resolved": "https://registry.npmjs.org/detect-libc/-/detect-libc-2.1.2.tgz",
      "integrity": "sha512-Btj2BOOO83o3WyH59e8MgXsxEQVcarkUOpEYrubB0urwnN10yQ364rsiByU11nZlqWYZm05i/of7io4mzihBtQ==",
      "dev": true,
      "license": "Apache-2.0",
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/earcut": {
      "version": "2.2.4",
      "resolved": "https://registry.npmjs.org/earcut/-/earcut-2.2.4.tgz",
      "integrity": "sha512-/pjZsA1b4RPHbeWZQn66SWS8nZZWLQQ23oE3Eam7aroEFGEvwKAsJfZ9ytiEMycfzXWpca4FA9QIOehf7PocBQ==",
      "license": "ISC"
    },
    "node_modules/fdir": {
      "version": "6.5.0",
      "resolved": "https://registry.npmjs.org/fdir/-/fdir-6.5.0.tgz",
      "integrity": "sha512-tIbYtZbucOs0BRGqPJkshJUYdL+SDH7dVM8gjy+ERp3WAUjLEFJE+02kanyHtwjWOnwrKYBiwAmM0p4kLJAnXg==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=12.0.0"
      },
      "peerDependencies": {
        "picomatch": "^3 || ^4"
      },
      "peerDependenciesMeta": {
        "picomatch": {
          "optional": true
        }
      }
    },
    "node_modules/flatbuffers": {
      "version": "25.9.23",
      "resolved": "https://registry.npmjs.org/flatbuffers/-/flatbuffers-25.9.23.tgz",
      "integrity": "sha512-MI1qs7Lo4Syw0EOzUl0xjs2lsoeqFku44KpngfIduHBYvzm8h2+7K8YMQh1JtVVVrUvhLpNwqVi4DERegUJhPQ==",
      "license": "Apache-2.0"
    },
    "node_modules/fsevents": {
      "version": "2.3.3",
      "resolved": "https://registry.npmjs.org/fsevents/-/fsevents-2.3.3.tgz",
      "integrity": "sha512-5xoDfX+fL7faATnagmWPpbFtwh/R77WmMMqqHGS65C3vvB0YHrgF+B1YmZ3441tMj5n63k0212XNoJwzlhffQw==",
      "dev": true,
      "hasInstallScript": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": "^8.16.0 || ^10.6.0 || >=11.0.0"
      }
    },
    "node_modules/gl-matrix": {
      "version": "3.4.4",
      "resolved": "https://registry.npmjs.org/gl-matrix/-/gl-matrix-3.4.4.tgz",
      "integrity": "sha512-latSnyDNt/8zYUB6VIJ6PCh2jBjJX6gnDsoCZ7LyW7GkqrD51EWwa9qCoGixj8YqBtETQK/xY7OmpTF8xz1DdQ==",
      "license": "MIT"
    },
    "node_modules/json-stringify-pretty-compact": {
      "version": "4.0.0",
      "resolved": "https://registry.npmjs.org/json-stringify-pretty-compact/-/json-stringify-pretty-compact-4.0.0.tgz",
      "integrity": "sha512-3CNZ2DnrpByG9Nqj6Xo8vqbjT4F6N+tb4Gb28ESAZjYZ5yqvmc56J+/kuIwkaAMOyblTQhUW7PxMkUb8Q36N3Q==",
      "license": "MIT"
    },
    "node_modules/json-with-bigint": {
      "version": "3.5.12",
      "resolved": "https://registry.npmjs.org/json-with-bigint/-/json-with-bigint-3.5.12.tgz",
      "integrity": "sha512-uwbF/wSSuOgC7qqlq27Xp5B6a2MHVug3t0idZdTqu0JnlFvgJuH7ju+KAk/J06C7GfhoYy2gnb9wz2INqcne7w==",
      "license": "MIT"
    },
    "node_modules/kdbush": {
      "version": "4.1.0",
      "resolved": "https://registry.npmjs.org/kdbush/-/kdbush-4.1.0.tgz",
      "integrity": "sha512-e9vurzrXJQrFX6ckpHP3bvj5l+9CnYzkxDNnNQ1h2QTqdWsUAJgXiKdGNcOa1EY85dU8KbQ+z/FdQdB7P+9yfQ==",
      "license": "ISC"
    },
    "node_modules/lightningcss": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss/-/lightningcss-1.33.0.tgz",
      "integrity": "sha512-WkUDrojuJs0xkgGf2udWxa3yGBRxPtxUkB79i6aCZLRgc7PM8fZe9TosfPDcvEpQZbuFASnHYmRLBLUbmLOIIA==",
      "dev": true,
      "license": "MPL-2.0",
      "dependencies": {
        "detect-libc": "^2.0.3"
      },
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      },
      "optionalDependencies": {
        "lightningcss-android-arm64": "1.33.0",
        "lightningcss-darwin-arm64": "1.33.0",
        "lightningcss-darwin-x64": "1.33.0",
        "lightningcss-freebsd-x64": "1.33.0",
        "lightningcss-linux-arm-gnueabihf": "1.33.0",
        "lightningcss-linux-arm64-gnu": "1.33.0",
        "lightningcss-linux-arm64-musl": "1.33.0",
        "lightningcss-linux-x64-gnu": "1.33.0",
        "lightningcss-linux-x64-musl": "1.33.0",
        "lightningcss-win32-arm64-msvc": "1.33.0",
        "lightningcss-win32-x64-msvc": "1.33.0"
      }
    },
    "node_modules/lightningcss-android-arm64": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss-android-arm64/-/lightningcss-android-arm64-1.33.0.tgz",
      "integrity": "sha512-gEpRTalKdosp4Bb8qWtc2iOgE5SeIHlpS1up9bFq2wAyYhl1UdTObYiHe98zEM9SQvSoqQZ1IQD0JNpg3Ml5pg==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "android"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-darwin-arm64": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss-darwin-arm64/-/lightningcss-darwin-arm64-1.33.0.tgz",
      "integrity": "sha512-Sciaz8eenNTKn9b3t7+xr0ipTp9YxKQY4npwQ3mrRuL0BAVHBLyZxofhaKBAVtzmtRZ/zTyo0/to4B1uWG/Djg==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-darwin-x64": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss-darwin-x64/-/lightningcss-darwin-x64-1.33.0.tgz",
      "integrity": "sha512-Z5UPAxzrjlWNNyGy6i65cJzzvgJ5D3T6wMvs+gWpY9d7qRhANrxqAp6LhxIgZhWEw18RfJTGcRxjuLIBr+m8XQ==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-freebsd-x64": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss-freebsd-x64/-/lightningcss-freebsd-x64-1.33.0.tgz",
      "integrity": "sha512-QQM/Ti/hQajJwCY+RiWuCZ9sdtI/XQk7nDK5vC8kkdwixezOlDgvDx7+RT+QjK6FcFT4MpsuoBnHIo/O3StRRg==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "freebsd"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-linux-arm-gnueabihf": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss-linux-arm-gnueabihf/-/lightningcss-linux-arm-gnueabihf-1.33.0.tgz",
      "integrity": "sha512-N7FVBe6iS24MlM6R/4RBTxGhQheZGs7tiQ9U32UtF75NzP5Q7xWPRqLBCKxlRQRk3rY1jCIPLzx7WzOhuUIRLQ==",
      "cpu": [
        "arm"
      ],
      "dev": true,
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-linux-arm64-gnu": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss-linux-arm64-gnu/-/lightningcss-linux-arm64-gnu-1.33.0.tgz",
      "integrity": "sha512-j2v/itmy4HlNxlc6voKXYgBqNi0Ng2LShg4z7GufpEgs05P+2suBVyi9I6YHq5uoVFx9ETin3eCEhLVyXGQnKg==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "libc": [
        "glibc"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-linux-arm64-musl": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss-linux-arm64-musl/-/lightningcss-linux-arm64-musl-1.33.0.tgz",
      "integrity": "sha512-yiO5ROMuYQgXbC60yjZU5CYSFZGKXL0HFATXt9mHJn1+zW55oCtMI9NfcVhYLMFDL7gV7oBPon/EmMMGg2OvtQ==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "libc": [
        "musl"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-linux-x64-gnu": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss-linux-x64-gnu/-/lightningcss-linux-x64-gnu-1.33.0.tgz",
      "integrity": "sha512-ar+Ju7LmcN0Jo4FpL4hpFybwNG9/3A/Br5KW2n2jyODg3MEZXaDYADdemoNS+BDNfMgKvylJLj4S5tyRActuAg==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "libc": [
        "glibc"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-linux-x64-musl": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss-linux-x64-musl/-/lightningcss-linux-x64-musl-1.33.0.tgz",
      "integrity": "sha512-RYiYbkokw0trfKqqzfF55lginwEPrD3OJDfTuJzFs1MK6iFnDenaz1fqLLtX4ITG3OktJQXOeTaw1awrBAlZPw==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "libc": [
        "musl"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-win32-arm64-msvc": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss-win32-arm64-msvc/-/lightningcss-win32-arm64-msvc-1.33.0.tgz",
      "integrity": "sha512-1K+MPfLSFVpphzpdbfkhlWk6wBrTObBzS2T6db10PNOZgR9GoVsAWzwNyuhUYYbTp23j+4RrncfujZ4uAzXvwA==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-win32-x64-msvc": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss-win32-x64-msvc/-/lightningcss-win32-x64-msvc-1.33.0.tgz",
      "integrity": "sha512-OlEICDx/Xl0FqSp4bry8zFnCvGpig3Gl4gCquvYwHuqJKEC1+n9NgDniFvqHGmMv1ZkqDJrDqKKSykTDX+ehuA==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/maplibre-gl": {
      "version": "6.11.2",
      "resolved": "https://registry.npmjs.org/maplibre-gl/-/maplibre-gl-6.11.2.tgz",
      "integrity": "sha512-Xh06pxoipjX/Ad1sUPGhiNh9go9naCNGZZ1IJm3sIeqK1kYGuMaMDSTIGDQ2igOLfVyukJU7kvEOA089VO7Z7g==",
      "license": "BSD-3-Clause",
      "dependencies": {
        "@mapbox/point-geometry": "^1.1.0",
        "@mapbox/tiny-sdf": "^2.2.0",
        "@mapbox/unitbezier": "^1.0.0",
        "@mapbox/vector-tile": "^3.0.0",
        "@maplibre/geojson-vt": "^6.1.1",
        "@maplibre/maplibre-gl-style-spec": "^26.4.4",
        "@maplibre/mlt": "^1.3.0",
        "@maplibre/vt-pbf": "^4.3.2",
        "@types/geojson": "^7946.0.16",
        "bidi-js": "^1.1.0",
        "earcut": "^3.2.3",
        "gl-matrix": "^3.4.4",
        "kdbush": "^4.1.0",
        "murmurhash-js": "^1.0.0",
        "pbf": "^5.1.2",
        "potpack": "^2.1.0",
        "quickselect": "^3.0.0",
        "tinyqueue": "^3.0.0"
      },
      "engines": {
        "node": ">=16.14.0",
        "npm": ">=8.1.0"
      },
      "funding": {
        "url": "https://github.com/maplibre/maplibre-gl-js?sponsor=1"
      }
    },
    "node_modules/maplibre-gl/node_modules/earcut": {
      "version": "3.2.4",
      "resolved": "https://registry.npmjs.org/earcut/-/earcut-3.2.4.tgz",
      "integrity": "sha512-FHc6yNpnTORB0tM5kmZ03iD2mDuNakDE2lvf4Hw1XkfxtEHIGVi01B/GqUSwx+NcC1WGjidAfpTXzeALtPtfpg==",
      "license": "ISC"
    },
    "node_modules/minimist": {
      "version": "1.2.8",
      "resolved": "https://registry.npmjs.org/minimist/-/minimist-1.2.8.tgz",
      "integrity": "sha512-2yyAR8qBkN3YuheJanUpWC5U3bb5osDywNB8RzDVlDwDHbocAJveqqj1u8+SVD7jkWT4yvsHCpWqqWqAxb0zCA==",
      "license": "MIT",
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/mjolnir.js": {
      "version": "3.1.1",
      "resolved": "https://registry.npmjs.org/mjolnir.js/-/mjolnir.js-3.1.1.tgz",
      "integrity": "sha512-Em3+0p6n2RamaiiDenHByvaWNolr+K0fWsFpgUgUXRssFI59ramCMdp0crU6V75clbA4fDJBVTBXfBF5rlPB9A==",
      "license": "MIT"
    },
    "node_modules/murmurhash-js": {
      "version": "1.0.0",
      "resolved": "https://registry.npmjs.org/murmurhash-js/-/murmurhash-js-1.0.0.tgz",
      "integrity": "sha512-TvmkNhkv8yct0SVBSy+o8wYzXjE4Zz3PCesbfs8HiCXXdcTuocApFv11UWlNFWKYsP2okqrhb7JNlSm9InBhIw==",
      "license": "MIT"
    },
    "node_modules/nanoid": {
      "version": "3.3.19",
      "resolved": "https://registry.npmjs.org/nanoid/-/nanoid-3.3.19.tgz",
      "integrity": "sha512-Y2tUNy4ouw6tq5oDSKeQYGOyhkUBhNOcGV/02KC+6kd9eDGqdZd++mjMiIDilrBYvjEnCYvVtsuHCuP+okSfug==",
      "dev": true,
      "funding": [
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "MIT",
      "bin": {
        "nanoid": "bin/nanoid.cjs"
      },
      "engines": {
        "node": "^10 || ^12 || ^13.7 || ^14 || >=15.0.1"
      }
    },
    "node_modules/pbf": {
      "version": "5.1.2",
      "resolved": "https://registry.npmjs.org/pbf/-/pbf-5.1.2.tgz",
      "integrity": "sha512-mnvGdvOrIvJOBGUEdGkrVXjN8E/VkIJCkf2eS1DH2yv82ORUlLttmDt0rWY38yYZmVwciZwBUvHM20qxBZf40w==",
      "license": "BSD-3-Clause",
      "dependencies": {
        "resolve-protobuf-schema": "^2.1.0"
      },
      "bin": {
        "pbf": "bin/pbf"
      }
    },
    "node_modules/picocolors": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/picocolors/-/picocolors-1.1.1.tgz",
      "integrity": "sha512-xceH2snhtb5M9liqDsmEw56le376mTZkEX/jEb/RxNFyegNul7eNslCXP9FDj/Lcu0X8KEyMceP2ntpaHrDEVA==",
      "dev": true,
      "license": "ISC"
    },
    "node_modules/picomatch": {
      "version": "4.0.7",
      "resolved": "https://registry.npmjs.org/picomatch/-/picomatch-4.0.7.tgz",
      "integrity": "sha512-qcJu88Q2IWqJsDD529JKMdwGm/dvInW4HvQnRwiH9JtihJvzGOscDtHE3x1pBKeUOTysQ8kVmLnJ2kJu7yhcGA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=12"
      },
      "funding": {
        "url": "https://github.com/sponsors/jonschlinkert"
      }
    },
    "node_modules/playwright": {
      "version": "1.63.0",
      "resolved": "https://registry.npmjs.org/playwright/-/playwright-1.63.0.tgz",
      "integrity": "sha512-+7ziBLidS4NaNCdt57SUDT+wYmmd5fmiQejUic/kb+YsYSCPyOOE9sebzMjNmQrsnNpDJqd4WHvV/8lfKfUDUg==",
      "dev": true,
      "license": "Apache-2.0",
      "dependencies": {
        "playwright-core": "1.63.0"
      },
      "bin": {
        "playwright": "cli.js"
      },
      "engines": {
        "node": ">=20"
      }
    },
    "node_modules/playwright-core": {
      "version": "1.63.0",
      "resolved": "https://registry.npmjs.org/playwright-core/-/playwright-core-1.63.0.tgz",
      "integrity": "sha512-rYCsBF/M5HjUch52bbtVONEFjv6Xu8sm8h72dNlR5bzIE1fvC/bxgspzkjSfU+MweEMmPM8KJebG6nnyxo5mCg==",
      "dev": true,
      "license": "Apache-2.0",
      "bin": {
        "playwright-core": "cli.js"
      },
      "engines": {
        "node": ">=20"
      }
    },
    "node_modules/postcss": {
      "version": "8.5.28",
      "resolved": "https://registry.npmjs.org/postcss/-/postcss-8.5.28.tgz",
      "integrity": "sha512-RRuzqDtt5Y9h3quz5hWhK+TPnsmVs6WwSU6LkJMeY4HstUEDuYTG8UJSdawMRzmzAtV+KEoG8N3Qg2qLy5vM/A==",
      "dev": true,
      "funding": [
        {
          "type": "opencollective",
          "url": "https://opencollective.com/postcss/"
        },
        {
          "type": "tidelift",
          "url": "https://tidelift.com/funding/github/npm/postcss"
        },
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "nanoid": "^3.3.18",
        "picocolors": "^1.1.1",
        "source-map-js": "^1.2.1"
      },
      "engines": {
        "node": "^10 || ^12 || >=14"
      }
    },
    "node_modules/potpack": {
      "version": "2.1.0",
      "resolved": "https://registry.npmjs.org/potpack/-/potpack-2.1.0.tgz",
      "integrity": "sha512-pcaShQc1Shq0y+E7GqJqvZj8DTthWV1KeHGdi0Z6IAin2Oi3JnLCOfwnCo84qc+HAp52wT9nK9H7FAJp5a44GQ==",
      "license": "ISC"
    },
    "node_modules/protocol-buffers-schema": {
      "version": "3.6.1",
      "resolved": "https://registry.npmjs.org/protocol-buffers-schema/-/protocol-buffers-schema-3.6.1.tgz",
      "integrity": "sha512-VG2K63Igkiv9p76tk1lilczEK1cT+kCjKtkdhw1dQZV3k3IXJbd3o6Ho8b9zJZaHSnT2hKe4I+ObmX9w6m5SmQ==",
      "license": "MIT"
    },
    "node_modules/quickselect": {
      "version": "3.0.0",
      "resolved": "https://registry.npmjs.org/quickselect/-/quickselect-3.0.0.tgz",
      "integrity": "sha512-XdjUArbK4Bm5fLLvlm5KpTFOiOThgfWWI4axAZDWg4E/0mKdZyI9tNEfds27qCi1ze/vwTR16kvmmGhRra3c2g==",
      "license": "ISC"
    },
    "node_modules/react": {
      "version": "19.3.0",
      "resolved": "https://registry.npmjs.org/react/-/react-19.3.0.tgz",
      "integrity": "sha512-E8LUcbtBWt20bbl2YoHfx4ZDBdxVTfOKtCZn9cDSJ4l6/nuoApcpIBcj47t2wZoVX8g2ZHuMHbiShgCR1T5Sog==",
      "license": "MIT",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/react-dom": {
      "version": "19.3.0",
      "resolved": "https://registry.npmjs.org/react-dom/-/react-dom-19.3.0.tgz",
      "integrity": "sha512-JDk8dgif51OjFoDE70+OT9ICyYr+69HlmihNwp1+Nsfbna3t5sIiCa9ZJktDmQ4/1b/rn26hIAR2uYXDMr5r0Q==",
      "license": "MIT",
      "dependencies": {
        "scheduler": "^0.28.0"
      },
      "peerDependencies": {
        "react": "^19.3.0"
      }
    },
    "node_modules/require-from-string": {
      "version": "2.0.2",
      "resolved": "https://registry.npmjs.org/require-from-string/-/require-from-string-2.0.2.tgz",
      "integrity": "sha512-Xf0nWe6RseziFMu+Ap9biiUbmplq6S9/p+7w7YXP/JBHhrUDDUhwa+vANyubuqfZWTveU//DYVGsDG7RKL/vEw==",
      "license": "MIT",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/resolve-protobuf-schema": {
      "version": "2.1.0",
      "resolved": "https://registry.npmjs.org/resolve-protobuf-schema/-/resolve-protobuf-schema-2.1.0.tgz",
      "integrity": "sha512-kI5ffTiZWmJaS/huM8wZfEMer1eRd7oJQhDuxeCLe3t7N7mX3z94CN0xPxBQxFYQTSNz9T0i+v6inKqSdK8xrQ==",
      "license": "MIT",
      "dependencies": {
        "protocol-buffers-schema": "^3.3.1"
      }
    },
    "node_modules/rolldown": {
      "version": "1.2.11",
      "resolved": "https://registry.npmjs.org/rolldown/-/rolldown-1.2.11.tgz",
      "integrity": "sha512-qpSwIyz0jHQq5qXBTNxFmE6664rJ7O+4TvPFOiOaBSrz8IOHc1koKKSqTM2H6u1UG1+TveuC6vaDHKXFOvb1Kw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@oxc-project/types": "=0.151.0",
        "@rolldown/pluginutils": "^1.0.0"
      },
      "bin": {
        "rolldown": "bin/cli.mjs"
      },
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      },
      "optionalDependencies": {
        "@rolldown/binding-android-arm-eabi": "1.2.11",
        "@rolldown/binding-android-arm64": "1.2.11",
        "@rolldown/binding-darwin-arm64": "1.2.11",
        "@rolldown/binding-darwin-x64": "1.2.11",
        "@rolldown/binding-freebsd-x64": "1.2.11",
        "@rolldown/binding-linux-arm-gnueabihf": "1.2.11",
        "@rolldown/binding-linux-arm64-gnu": "1.2.11",
        "@rolldown/binding-linux-arm64-musl": "1.2.11",
        "@rolldown/binding-linux-ppc64-gnu": "1.2.11",
        "@rolldown/binding-linux-s390x-gnu": "1.2.11",
        "@rolldown/binding-linux-x64-gnu": "1.2.11",
        "@rolldown/binding-linux-x64-musl": "1.2.11",
        "@rolldown/binding-openharmony-arm64": "1.2.11",
        "@rolldown/binding-win32-arm64-msvc": "1.2.11",
        "@rolldown/binding-win32-x64-msvc": "1.2.11"
      }
    },
    "node_modules/scheduler": {
      "version": "0.28.0",
      "resolved": "https://registry.npmjs.org/scheduler/-/scheduler-0.28.0.tgz",
      "integrity": "sha512-juorfCmIkIw8tT+p5BXSm6PJjQF/ycEYmKyzURCIt/RaZIhL+PulbQ9Yu2z1HdOJDdqDTlxA1+xKBmHXJsczAw==",
      "license": "MIT"
    },
    "node_modules/source-map-js": {
      "version": "1.2.1",
      "resolved": "https://registry.npmjs.org/source-map-js/-/source-map-js-1.2.1.tgz",
      "integrity": "sha512-UXWMKhLOwVKb728IUtQPXxfYU+usdybtUrK/8uGE8CQMvrhOpwvzDBwj0QhSL7MQc7vIsISBG8VQ8+IDQxpfQA==",
      "dev": true,
      "license": "BSD-3-Clause",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/tinyglobby": {
      "version": "0.2.17",
      "resolved": "https://registry.npmjs.org/tinyglobby/-/tinyglobby-0.2.17.tgz",
      "integrity": "sha512-wXR/dYpcqKmfWpEdZjiKJOwCNFndD0DMnrW/cYjVGttEkBfVgcLFHoNrlj47mjOVic9yyNu65alsgF4NQyTa2g==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "fdir": "^6.5.0",
        "picomatch": "^4.0.4"
      },
      "engines": {
        "node": ">=12.0.0"
      },
      "funding": {
        "url": "https://github.com/sponsors/SuperchupuDev"
      }
    },
    "node_modules/tinyqueue": {
      "version": "3.0.0",
      "resolved": "https://registry.npmjs.org/tinyqueue/-/tinyqueue-3.0.0.tgz",
      "integrity": "sha512-gRa9gwYU3ECmQYv3lslts5hxuIa90veaEcxDYuu3QGOIAEM2mOZkVHp48ANJuu1CURtRdHKUBY5Lm1tHV+sD4g==",
      "license": "ISC"
    },
    "node_modules/tslib": {
      "version": "2.8.1",
      "resolved": "https://registry.npmjs.org/tslib/-/tslib-2.8.1.tgz",
      "integrity": "sha512-oJFu94HQb+KVduSUQL7wnpmqnfmLsOA/nAh6b6EH0wCEoK0/mPeXU6c3wKDV83MkOuHPRHtSXKKU99IBazS/2w==",
      "license": "0BSD"
    },
    "node_modules/typescript": {
      "version": "7.0.2",
      "resolved": "https://registry.npmjs.org/typescript/-/typescript-7.0.2.tgz",
      "integrity": "sha512-8FYau96o3NKOhbjKi/qNvG/W5jhzxkbdm5sj9AbZ/5T5sWqn3hJgLfGx27sRKZWTvyzCP8dLRBTf5tBTSRVUNA==",
      "dev": true,
      "license": "Apache-2.0",
      "bin": {
        "tsc": "bin/tsc"
      },
      "engines": {
        "node": ">=16.20.0"
      },
      "optionalDependencies": {
        "@typescript/typescript-aix-ppc64": "7.0.2",
        "@typescript/typescript-darwin-arm64": "7.0.2",
        "@typescript/typescript-darwin-x64": "7.0.2",
        "@typescript/typescript-freebsd-arm64": "7.0.2",
        "@typescript/typescript-freebsd-x64": "7.0.2",
        "@typescript/typescript-linux-arm": "7.0.2",
        "@typescript/typescript-linux-arm64": "7.0.2",
        "@typescript/typescript-linux-loong64": "7.0.2",
        "@typescript/typescript-linux-mips64el": "7.0.2",
        "@typescript/typescript-linux-ppc64": "7.0.2",
        "@typescript/typescript-linux-riscv64": "7.0.2",
        "@typescript/typescript-linux-s390x": "7.0.2",
        "@typescript/typescript-linux-x64": "7.0.2",
        "@typescript/typescript-netbsd-arm64": "7.0.2",
        "@typescript/typescript-netbsd-x64": "7.0.2",
        "@typescript/typescript-openbsd-arm64": "7.0.2",
        "@typescript/typescript-openbsd-x64": "7.0.2",
        "@typescript/typescript-sunos-x64": "7.0.2",
        "@typescript/typescript-win32-arm64": "7.0.2",
        "@typescript/typescript-win32-x64": "7.0.2"
      }
    },
    "node_modules/undici-types": {
      "version": "8.9.0",
      "resolved": "https://registry.npmjs.org/undici-types/-/undici-types-8.9.0.tgz",
      "integrity": "sha512-KTDyRTYX8sWmKXAikPHHSyc63CRPETMctyjKFupcC6OBLXT3xsN0e9aF7m+mIXutFWpUXuedtowG7iLOzp0kQg==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/vite": {
      "version": "8.3.1",
      "resolved": "https://registry.npmjs.org/vite/-/vite-8.3.1.tgz",
      "integrity": "sha512-/bvH9E9tmCXRGp2uXY3WbOldqpTwFkbha/8ANaEQ6VkxhH60KyqLwgZq6lG2y+4uT55x9+9eUHMpQ7uGnOCKjA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "lightningcss": "^1.33.0",
        "picomatch": "^4.0.7",
        "postcss": "^8.5.28",
        "rolldown": "~1.2.9",
        "tinyglobby": "^0.2.17"
      },
      "bin": {
        "vite": "bin/vite.js"
      },
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      },
      "funding": {
        "url": "https://github.com/vitejs/vite?sponsor=1"
      },
      "optionalDependencies": {
        "fsevents": "~2.3.3"
      },
      "peerDependencies": {
        "@types/node": "^20.19.0 || >=22.12.0",
        "@vitejs/devtools": "^0.7.1",
        "esbuild": "^0.27.0 || ^0.28.0",
        "jiti": ">=1.21.0",
        "less": "^4.0.0",
        "sass": "^1.70.0",
        "sass-embedded": "^1.70.0",
        "stylus": ">=0.54.8",
        "sugarss": "^5.0.0",
        "terser": "^5.16.0",
        "tsx": "^4.8.1",
        "yaml": "^2.4.2"
      },
      "peerDependenciesMeta": {
        "@types/node": {
          "optional": true
        },
        "@vitejs/devtools": {
          "optional": true
        },
        "esbuild": {
          "optional": true
        },
        "jiti": {
          "optional": true
        },
        "less": {
          "optional": true
        },
        "sass": {
          "optional": true
        },
        "sass-embedded": {
          "optional": true
        },
        "stylus": {
          "optional": true
        },
        "sugarss": {
          "optional": true
        },
        "terser": {
          "optional": true
        },
        "tsx": {
          "optional": true
        },
        "yaml": {
          "optional": true
        }
      }
    }
  }
}
````

## frontend/.env.example

````dotenv
# Public presentation settings only. Never put API keys in a VITE_ variable.
# M1 fixtures are USD cents. Other currencies require compatible data in M2.
VITE_CURRENCY_CODE=USD
````

## frontend/index.html

````html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="theme-color" content="#111820" />
    <meta name="description" content="Explore a synthetic New York stay collection in 3D." />
    <title>StayScape — New York in a new dimension</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
````

## frontend/tsconfig.json

````json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "Bundler",
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
````

## frontend/vite.config.ts

````typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: { port: 5173, strictPort: true },
  preview: { port: 4173, strictPort: true },
});
````

## frontend/playwright.config.ts

````typescript
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests', timeout: 180_000, workers: 1,
  // Software WebGL on CI can take longer than the nominal camera animation duration.
  expect: { timeout: 30_000 },
  use: {
    baseURL: 'http://127.0.0.1:4173', viewport: { width: 1280, height: 800 },
    // Edge is already installed on this Windows machine; no browser download is needed.
    channel: process.env.PLAYWRIGHT_CHANNEL || 'msedge',
    launchOptions: { args: ['--enable-webgl', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] },
    trace: { mode: 'retain-on-failure', screenshots: false },
  },
  webServer: {
    command: 'npm run preview', url: 'http://127.0.0.1:4173',
    reuseExistingServer: !process.env.CI,
  },
});
````

## frontend/src/main.tsx

````tsx
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import 'maplibre-gl/dist/maplibre-gl.css';
import './styles.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode><App /></StrictMode>,
);
````

## frontend/src/listings.ts

````typescript
export type Listing = {
  id: string;
  title: string;
  neighborhood: string;
  position: [longitude: number, latitude: number];
  priceMinor: number;
  currency: 'USD';
  rating: number;
  guests: number;
};

// Hand-authored demo fixtures, not real rentals or scraped addresses.
// A compact Manhattan collection makes buildings and columns visible together in M1.
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
  }),
);

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
````

## frontend/src/MapScene.tsx

````tsx
import { useEffect, useRef, useState } from 'react';
import { Map, NavigationControl, AttributionControl, setWorkerUrl } from 'maplibre-gl';
import workerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url';
import { MapLibreOverlay } from '@deck.gl/maplibre';
import { ColumnLayer } from '@deck.gl/layers';
import { listings, price, ratingColor } from './listings';
import type { Listing } from './listings';

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
  const selectRef = useRef(onSelect);
  selectRef.current = onSelect;
  const [ready, setReady] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [buildingCount, setBuildingCount] = useState(0);
  const [renderedBuildings, setRenderedBuildings] = useState(0);
  const [buildingsVisible, setBuildingsVisible] = useState(true);
  const [zoom, setZoom] = useState(HOME.zoom);
  const [retry, setRetry] = useState(0);
  const [hover, setHover] = useState<{ listing: Listing; x: number; y: number } | null>(null);

  useEffect(() => {
    if (!container.current) return;
    setReady(false);
    setError(null);
    setBuildingCount(0);
    setRenderedBuildings(0);
    setHover(null);
    let map: Map;
    try {
      map = new Map({
        container: container.current, style: STYLE, ...HOME,
        maxPitch: 70, minZoom: 11, maxZoom: 18,
        // One shared WebGL2 context gives buildings and columns consistent depth/occlusion.
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
          'fill-extrusion-color': '#657680',
          'fill-extrusion-height': ['coalesce', ['get', 'render_height'], 9],
          'fill-extrusion-base': ['coalesce', ['get', 'render_min_height'], 0],
          'fill-extrusion-opacity': 0.9,
        },
      }, label);
      const overlay = new MapLibreOverlay({
        interleaved: true,
        onError: () => setError('The listing renderer failed. Check WebGL2 support and retry.'),
      });
      map.addControl(overlay);
      overlayRef.current = overlay;
      // Read at load too: a busy shared renderer may delay MapLibre's idle event.
      setBuildingCount(map.querySourceFeatures('openmaptiles', { sourceLayer: 'building' }).length);
      setReady(true);
      setError(null);
    });
    map.on('movestart', () => setHover(null));
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
      resize.disconnect();
      overlayRef.current = null;
      mapRef.current = null;
      map.remove();
    };
  }, [retry]);

  useEffect(() => {
    if (!ready || !overlayRef.current) return;
    overlayRef.current.setProps({ layers: [new ColumnLayer<Listing>({
      id: 'listing-columns', data: listings, diskResolution: 12,
      radius: 28, radiusUnits: 'meters', extruded: true,
      getPosition: listing => listing.position,
      // USD cents → dollars → illustrative meters. This encodes price, not building height.
      getElevation: listing => listing.priceMinor / 100 * 0.85,
      getFillColor: listing => ratingColor(listing.rating),
      material: { ambient: 0.65, diffuse: 0.5, shininess: 24 },
      pickable: true, autoHighlight: true, highlightColor: [255, 255, 255, 90],
      onHover: info => {
        setHover(info.object ? { listing: info.object, x: info.x, y: info.y } : null);
        if (mapRef.current) mapRef.current.getCanvas().style.cursor = info.object ? 'pointer' : '';
      },
      onClick: info => { if (info.object) selectRef.current(info.object); },
    }), new ColumnLayer<Listing>({
      id: 'selected-outline', data: selected ? [selected] : [],
      getPosition: listing => listing.position,
      getElevation: listing => listing.priceMinor / 100 * 0.85 + 2,
      radius: 30, diskResolution: 12, extruded: true, filled: false, wireframe: true,
      getLineColor: [255, 255, 255, 255], pickable: false,
    })] });
  }, [ready, selected]);

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

  return <section className="map-shell" aria-label="Interactive New York listing map">
    <div ref={container} className="map-canvas" data-testid="map" data-zoom={zoom}
      data-building-count={buildingCount} data-rendered-buildings={renderedBuildings} />
    <div className="map-heading"><span className="live-dot" /> NEW YORK CITY <span>40.72° N / 74.00° W</span></div>
    <div className="map-actions">
      <button onClick={reset} disabled={!ready}>↗ Reset view</button>
      <button onClick={() => setBuildingsVisible(value => !value)} disabled={!ready}
        aria-pressed={buildingsVisible}>3D buildings {buildingsVisible ? 'on' : 'off'}</button>
    </div>
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
      <strong>Taller column. Higher price.</strong>
      <div className="rating-key"><span><i className="gold" />4.0–4.4</span>
        <span><i className="blue" />4.5–4.7</span><span><i className="mint" />4.8–5.0</span></div>
      <small>Color = guest rating · Height = price, not building size</small>
    </div>
    <div className="map-hint" role="status">
      {ready ? (buildingCount > 0 ? '3D building data loaded' : 'Waiting for building tiles…') : 'Connecting…'}
      <span>Drag to pan · Scroll to zoom · Right-drag to tilt</span>
    </div>
  </section>;
}
````

## frontend/src/App.tsx

````tsx
import { useState } from 'react';
import MapScene from './MapScene';
import { currencyError, listings, price, ratingColor } from './listings';
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
      <div className="collection-heading"><strong>20 places to imagine</strong><span>USD / night</span></div>
      <div className="listing-list" aria-label="Synthetic listings">
        {listings.map((listing, index) => <button key={listing.id}
          className={`listing-row ${selected?.id === listing.id ? 'selected' : ''}`}
          aria-pressed={selected?.id === listing.id} onClick={() => selectListing(listing)}>
          <span className="listing-number" style={{ color: `rgb(${ratingColor(listing.rating).slice(0, 3).join(',')})` }}>
            {String(index + 1).padStart(2, '0')}</span>
          <span className="listing-copy"><strong>{listing.title}</strong><small>{listing.neighborhood} · ★ {listing.rating.toFixed(1)}</small></span>
          <span className="listing-price">{price(listing)}<small>↗</small></span>
        </button>)}
      </div>
      {selected ? <section className="selection" aria-label="Selected listing" aria-live="polite">
        <div><span className="eyebrow">YOUR MAP PICK</span><button aria-label="Close selected listing" onClick={() => setSelected(null)}>×</button></div>
        <h2>{selected.title}</h2><p>{selected.neighborhood} · Up to {selected.guests} guests</p>
        <strong>{price(selected)} <small>USD / night</small><span>★ {selected.rating.toFixed(1)}</span></strong>
      </section> : <div className="sidebar-tip">↗ Hover a column for a preview.<br />Select a stay to take a closer look.</div>}
      <footer><span className="live-dot" /> M1 MAP EXPERIMENT <span>All stays are synthetic.</span></footer>
    </aside>
    <MapScene selected={selected} onSelect={selectListing} />
  </main>;
}
````

## frontend/src/styles.css

````css
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
.map-canvas { position: absolute; inset: 0; }
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
````

## frontend/tests/map.spec.ts

````typescript
import { expect, test } from '@playwright/test';

test('real tiles, 3D buildings, selection, hover picking, and reset', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('/');
  await expect(page.locator('.listing-row')).toHaveCount(20);
  const map = page.getByTestId('map');
  // A style loading is insufficient: actual NYC building tile features must be present.
  await expect.poll(async () => Number(await map.getAttribute('data-building-count')),
    { timeout: 90_000 }).toBeGreaterThan(0);
  await expect(page.getByRole('alert')).toHaveCount(0);
  await expect.poll(async () => Number(await map.getAttribute('data-rendered-buildings')),
    { timeout: 90_000 }).toBeGreaterThan(0);
  console.info('NYC tile building features:', await map.getAttribute('data-building-count'),
    'rendered building features:', await map.getAttribute('data-rendered-buildings'));
  await page.screenshot({ path: 'test-results/m1-desktop.png' });
  await page.getByRole('button', { name: /01 Canal Street loft/ }).click();
  await expect(page.getByRole('region', { name: 'Selected listing' })).toContainText('Canal Street loft');
  await expect.poll(async () => Number(await map.getAttribute('data-zoom'))).toBeCloseTo(15.6, 1);
  // Exercise real GPU picking, not a mocked hover callback. The column top is above map center.
  const box = (await map.boundingBox())!;
  let picked = false;
  let pickedPosition = { x: 0, y: 0 };
  let hoveredTitle = '';
  for (let y = box.height / 2 - 50; y >= 140 && !picked; y -= 20) {
    for (const x of [box.width / 2, box.width / 2 - 24, box.width / 2 + 24]) {
      await page.mouse.move(box.x + x, box.y + y);
      // GPU picking and React commit on later frames: don't read the previous pointer's tooltip.
      await page.evaluate(() => new Promise<void>(resolve =>
        requestAnimationFrame(() => requestAnimationFrame(() => resolve()))));
      hoveredTitle = await page.getByRole('tooltip').locator('strong').textContent({ timeout: 250 })
        .catch(() => '') || '';
      if (hoveredTitle) {
        picked = true; pickedPosition = { x: box.x + x, y: box.y + y }; break;
      }
    }
  }
  expect(picked, 'At least one real listing column should be hover-pickable').toBe(true);
  await page.mouse.click(pickedPosition.x, pickedPosition.y);
  await expect(page.getByRole('region', { name: 'Selected listing' })).toContainText(hoveredTitle);
  await page.getByRole('button', { name: '3D buildings on' }).click();
  await expect(page.getByRole('button', { name: '3D buildings off' })).toHaveAttribute('aria-pressed', 'false');
  await page.getByRole('button', { name: '3D buildings off' }).click();
  await page.getByRole('button', { name: 'Reset view' }).click();
  await expect.poll(async () => Number(await map.getAttribute('data-zoom'))).toBeCloseTo(14.3, 1);
  await expect(page.getByRole('region', { name: 'Selected listing' })).toHaveCount(0);
  await expect(page.locator('.maplibregl-ctrl-attrib')).toContainText('OpenStreetMap');
  expect(errors).toEqual([]);
  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({ path: 'test-results/m1-mobile.png' });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
});

test('map service failure presents a retry instead of an endless loading state', async ({ page }) => {
  await page.route('https://tiles.openfreemap.org/**', route => route.abort());
  await page.goto('/');
  await expect(page.getByRole('alert')).toContainText('failed');
  await expect(page.getByRole('button', { name: 'Retry map' })).toBeVisible();
});
````

## frontend/README.md

````markdown
# StayScape M1 — 3D map spike

This milestone runs entirely in the browser. It uses 20 hardcoded synthetic stays
in a compact Manhattan area so you can see buildings and listing columns together.
There is no backend, search, AI, dataset generator, or photo service in this milestone.

## Exact versions

| Package | Version |
| --- | --- |
| React / React DOM | 19.3.0 |
| Vite | 8.3.1 |
| MapLibre GL JS | 6.11.2 |
| @deck.gl/core, @deck.gl/layers, @deck.gl/maplibre | 9.4.0 |
| @luma.gl/core | 9.4.0 |
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
`MapLibreOverlay` synchronizes deck.gl to that camera; `interleaved: true` shares
MapLibre's WebGL2 context so columns and buildings can occlude one another in 3D.

deck.gl's `ColumnLayer` draws one GPU-rendered column per listing. Positions use
`[longitude, latitude]`, radius is 28 meters, and height is `priceMinor / 100 * 0.85`
meters. Price height is an illustrative visual encoding, not the rental's altitude.
Rating bins are amber (below 4.5), blue (4.5–4.7), mint (4.8+). Selection adds a
white wireframe without replacing the rating color. GPU picking identifies which
column the pointer touches; React displays its card. Sidebar buttons provide a
keyboard/touch alternative to hovering.

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

- A dark NYC map loads with raised gray buildings and colored listing columns.
- The sidebar has 20 synthetic stays, all priced in USD per night.
- Hover a column: a title, nightly price, neighborhood, and rating appear.
- Click a column or sidebar stay: the camera flies closer, a white outline marks
  the column, and the selection card appears.
- Pan, zoom and right-drag to change pitch/bearing; columns stay aligned to geography.
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
````

