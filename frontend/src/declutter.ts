export type Tag = { id: string; x: number; y: number; width: number; priority: boolean };
export function declutter(tags: Tag[], zoom: number, width: number, height: number) {
  const kept: Tag[] = [];
  const ids = new Set<string>();
  const gap = zoom < 13 ? 64 : zoom < 14.5 ? 28 : 8;
  // Rectangle tests avoid the adjacent-cell overlaps of the old grid heuristic.
  // Priority tags reserve room first; both remain visible even if they collide with each other.
  for (const tag of [...tags].sort((a, b) => Number(b.priority) - Number(a.priority))) {
    if (!tag.priority && (tag.x < tag.width / 2 || tag.x > width - tag.width / 2 || tag.y < 24 || tag.y > height - 35)) continue;
    if (tag.priority || !kept.some(other => Math.abs(tag.x - other.x) < (tag.width + other.width) / 2 + gap && Math.abs(tag.y - other.y) < 32 + gap)) {
      kept.push(tag); ids.add(tag.id);
    }
  }
  return ids;
}
