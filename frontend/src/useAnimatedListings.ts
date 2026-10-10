import { useReducedMotion } from 'framer-motion';
import { useEffect, useRef, useState } from 'react';
import type { Listing } from './listings';
export function useAnimatedListings(items: Listing[]) {
  const reduceMotion = useReducedMotion();
  const previous = useRef<Listing[]>([]);
  const [frame, setFrame] = useState({ items, entering: new Set<string>(), exiting: new Set<string>(), progress: 1 });
  useEffect(() => {
    const old = previous.current;
    previous.current = items;
    const nextIds = new Set(items.map(d => d.id));
    const oldIds = new Set(old.map(d => d.id));
    const exiting = new Set(old.filter(d => !nextIds.has(d.id)).map(d => d.id));
    const entering = new Set(items.filter(d => !oldIds.has(d.id)).map(d => d.id));
    const union = [...items, ...old.filter(d => exiting.has(d.id))];
    if (reduceMotion) {
      setFrame({ items, entering: new Set(), exiting: new Set(), progress: 1 });
      return;
    }
    const start = performance.now();
    let raf = 0;
    const tick = () => {
      const progress = Math.min(1, (performance.now() - start) / 280);
      setFrame({ items: progress < 1 ? union : items, entering, exiting, progress: 1 - (1 - progress) ** 3 });
      if (progress < 1) raf = requestAnimationFrame(tick);
    };
    tick();
    return () => cancelAnimationFrame(raf);
  }, [items, reduceMotion]);
  return frame;
}
