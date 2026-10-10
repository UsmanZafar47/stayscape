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
