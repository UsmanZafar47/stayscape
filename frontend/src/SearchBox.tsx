import { useEffect, useState } from 'react';
import { getSearchExamples, type SearchResult } from './api';

export default function SearchBox({ onSearch, onClear, result, loading }: {
  onSearch: (query: string, demo?: boolean) => void; onClear: () => void; result: SearchResult | null; loading: boolean;
}) {
  const [query, setQuery] = useState('');
  const [examples, setExamples] = useState<string[]>([]);
  const [state, setState] = useState('loading');
  const [attempt, retry] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 90000);
    let active = true;
    setState('loading');
    getSearchExamples(controller.signal).then(data => { if (active) { setExamples(data.queries); setState('ready'); } })
      .catch(() => { if (active) setState('error'); }).finally(() => clearTimeout(timeout));
    return () => { active = false; clearTimeout(timeout); controller.abort(); };
  }, [attempt]);
  return <section className="search-box" aria-label="AI stay search">
    <form onSubmit={event => { event.preventDefault(); if (query.trim()) onSearch(query.trim()); }}>
      <label htmlFor="stay-query">Describe your city escape</label>
      <textarea id="stay-query" value={query} maxLength={500} rows={2} placeholder="Quiet Manhattan stay under $250 with wifi…" onChange={event => setQuery(event.target.value)} />
      <button disabled={loading || !query.trim()} type="submit">{loading ? 'Finding stays…' : 'Find stays'}</button>
    </form>
    <p className="search-note">Search replaces filters. Editing filters returns to browse.</p>
    <details className="suggestions" open={!result}><summary>Try an offline demo</summary>
      {state === 'loading' && <p role="status">Loading suggestions…</p>}
      {state === 'error' && <div role="alert">Suggestions unavailable; the backend may still be waking up. <button onClick={() => retry(v => v + 1)}>Retry suggestions</button></div>}
      {state === 'ready' && !examples.length && <p>No saved examples. You can still type a query.</p>}
      <div className="suggestion-chips">{examples.map(example => <button key={example} disabled={loading}
        onClick={() => { setQuery(example); onSearch(example, true); }}>{example}</button>)}</div>
    </details>
    {result && <div className="search-answer" aria-live="polite">
      <strong>{result.source === 'demo' ? 'Offline demo' : result.source === 'rules' ? 'Keyword fallback' : 'AI interpretation'}{result.cached ? ' · cached' : ''}</strong>
      <p>{result.explanation}</p>
      <button className="text-button" onClick={onClear}>Clear search</button>
      <details><summary>Interpreted filters</summary><ul>{Object.entries(result.intent).filter(([, value]) => value != null && (!Array.isArray(value) || value.length > 0)).map(([key, value]) =>
        <li key={key}>{key.replaceAll('_', ' ')}: {key.includes('minor') ? `$${Number(value) / 100}` : Array.isArray(value) ? value.join(', ') : String(value)}</li>)}</ul></details>
    </div>}
  </section>;
}
