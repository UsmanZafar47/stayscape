import { useEffect, useRef, useState, type SetStateAction } from 'react';
import { getListings, searchListings, type SearchResult } from './api';
import { emptyFilters, retainedSelection, validateFilters, type FilterDraft } from './filters';
import type { Listing } from './listings';
export function useExplorer() {
  // Browse and search share one request effect, cancellation signal and result snapshot.
  const [job, setJob] = useState<{ draft: FilterDraft; search: { query: string; demo: boolean } | null }>({ draft: emptyFilters, search: null });
  const draft = job.draft;
  // Results and selection commit together. Details derive from this exact snapshot.
  const [snapshot, setSnapshot] = useState<{ items: Listing[]; selected: string | null; searchResult: SearchResult | null }>({ items: [], selected: null, searchResult: null });
  const [status, setStatus] = useState<'loading' | 'ready' | 'error'>('loading');
  const connected = useRef(false);
  const [waking, setWaking] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [attempt, retry] = useState(0);
  const [selectionVersion, bumpSelection] = useState(0);
  let validation = '';
  try { validateFilters(draft); } catch (e) { validation = (e as Error).message; }
  useEffect(() => {
    const controller = new AbortController();
    if (validation && !job.search) return () => controller.abort();
    setWaking(false);
    // A sleeping host gets time to wake; this timer never clears the last good results.
    const slow = window.setTimeout(() => { if (!connected.current) setWaking(true); }, 4000);
    setStatus('loading');
    setError('');
    const timer = window.setTimeout(async () => {
      const timeout = window.setTimeout(() => controller.abort(new Error('The request timed out. Please retry.')), connected.current ? 15000 : 90000);
      try {
        const searchResult = job.search ? await searchListings(job.search.query, job.search.demo, controller.signal) : null;
        const items = searchResult ? searchResult.items : await getListings(validateFilters(draft), controller.signal);
        if (controller.signal.aborted) return;
        setSnapshot(previous => ({ items, selected: retainedSelection(items, previous.selected), searchResult }));
        connected.current = true;
        setWaking(false);
        setStatus('ready');
        setNotice('Results updated. A selected stay closes if it no longer matches.');
      } catch (e) {
        if (controller.signal.aborted && !controller.signal.reason?.message?.includes('timed out')) return;
        setError(controller.signal.reason?.message?.includes('timed out') ? controller.signal.reason.message : (e as Error).message);
        if (!connected.current) setWaking(true);
        setStatus('error');
      } finally { window.clearTimeout(timeout); window.clearTimeout(slow); }
    }, job.search ? 0 : 300);
    return () => { window.clearTimeout(timer); window.clearTimeout(slow); controller.abort(); };
  }, [job, attempt, validation]);
  const intent = job.search ? snapshot.searchResult?.intent : null;
  const shownDraft = intent ? { min: intent.price_min_minor == null ? '' : String(intent.price_min_minor / 100),
    max: intent.price_max_minor == null ? '' : String(intent.price_max_minor / 100), guests: String(intent.guests ?? ''),
    bedrooms: String(intent.bedrooms ?? ''), type: intent.property_type ?? '' } : draft;
  return { ...snapshot, draft: shownDraft,
    setDraft: (value: SetStateAction<FilterDraft>) => setJob({ draft: typeof value === 'function' ? value(shownDraft) : value, search: null }),
    search: (query: string, demo = false) => { setJob({ draft: emptyFilters, search: { query, demo } }); retry(v => v + 1); },
    status, error, waking, validation: job.search ? '' : validation, notice, selectionVersion,
    selectedListing: snapshot.items.find(d => d.id === snapshot.selected) ?? null,
    select: (listing: Listing | null) => {
      setSnapshot(previous => ({ ...previous, selected: retainedSelection(previous.items, listing?.id ?? null) }));
      bumpSelection(v => v + 1);
    },
    retry: () => retry(v => v + 1), clear: () => setJob({ draft: { ...emptyFilters }, search: null }) };
}
