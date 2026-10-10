import { useState } from 'react';
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion';
import MapScene from './MapScene';
import { price, propertyTypes, type Listing } from './listings';
import { useExplorer } from './useExplorer';
import SearchBox from './SearchBox';
function Placeholder({ listing }: { listing: Listing }) {
  const [failed, setFailed] = useState(false);
  const [loaded, setLoaded] = useState(false);
  const [attempt, setAttempt] = useState(0);
  return failed ? <div role="alert">Image unavailable. <button onClick={() => { setFailed(false); setLoaded(false); setAttempt(v => v + 1); }}>Retry image</button></div>
    : <>{!loaded && <span role="status">Loading illustration…</span>}<img className="detail-image" src={`${listing.pictures[0]}?retry=${attempt}`} alt={`Illustration of a ${listing.propertyType}`} onLoad={() => setLoaded(true)} onError={() => setFailed(true)} /></>;
}
export default function App() {
  const explorer = useExplorer();
  const reduceMotion = useReducedMotion();
  const [panelOpen, setPanelOpen] = useState(true);
  const { selectedListing: selected, items, draft } = explorer;
  const change = (key: keyof typeof draft, value: string) => explorer.setDraft(previous => ({ ...previous, [key]: value }));
  return <main className={`app ${panelOpen ? 'panel-open' : 'panel-closed'}`}>
    <motion.aside className="sidebar" initial={{ opacity: 0, x: reduceMotion ? 0 : -16 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: reduceMotion ? 0 : 0.25 }}>
      {/* Keep the phone panel in flow so attribution always has its own map space. */}
      <button className="panel-toggle" aria-expanded={panelOpen} aria-controls="explorer-controls" onClick={() => setPanelOpen(value => !value)}>{panelOpen ? 'Collapse explorer' : `Explore ${items.length} stays`}</button>
      <div id="explorer-controls" className="sidebar-content">
      <header className="brand"><span className="brand-mark">S</span><span>StayScape<small>A NEW POINT OF VIEW</small></span></header>
      <div className="intro"><span className="eyebrow">THE NEW YORK COLLECTION</span><h1>Find your <em>city escape.</em></h1></div>
      <SearchBox onSearch={explorer.search} onClear={explorer.clear} result={explorer.searchResult} loading={explorer.status === 'loading'} />
      <details className="filter-disclosure"><summary>Refine with filters</summary><section className="filters" aria-label="Filters">
        <div className="filter-grid">
          <label>Min price ($)<input type="number" min="0" max="100000" step="0.01" value={draft.min} onChange={e => change('min', e.target.value)} /></label>
          <label>Max price ($)<input type="number" min="0" max="100000" step="0.01" value={draft.max} onChange={e => change('max', e.target.value)} /></label>
          <label>Guests<select value={draft.guests} onChange={e => change('guests', e.target.value)}><option value="">Any capacity</option>{Array.from({ length: 10 }, (_, i) => <option key={i} value={i + 1}>{i + 1}+ guests</option>)}</select></label>
          <label>Bedrooms<select value={draft.bedrooms} onChange={e => change('bedrooms', e.target.value)}><option value="">Any bedrooms</option>{Array.from({ length: 6 }, (_, i) => <option key={i} value={i}>{i}+ bedrooms</option>)}</select></label>
        </div>
        <label>Property type<select value={draft.type} onChange={e => change('type', e.target.value)}><option value="">All property types</option>{propertyTypes.map(type => <option key={type} value={type}>{type}</option>)}</select></label>
        <button className="text-button" onClick={explorer.clear}>Clear filters</button>
        {explorer.validation && <p role="alert">{explorer.validation} Showing the last completed results.</p>}
      </section></details>
      <div className="collection-heading"><strong>{items.length} stays</strong><span>USD / night</span></div>
      <div className="api-status" aria-live="polite">
        {explorer.waking && <p role="status">Backend is waking up or unreachable. The first connection can take a minute. {explorer.status === 'loading' && <button onClick={explorer.retry}>Retry connection</button>}</p>}
        {explorer.status === 'loading' && !explorer.validation && <p role="status">Loading stays… {items.length > 0 && 'Showing previous results.'}</p>}
        {explorer.status === 'error' && <div role="alert"><p>{explorer.error} {items.length > 0 && 'Showing previous results.'}</p><button onClick={explorer.retry}>Retry listings</button></div>}
        {explorer.status === 'ready' && items.length === 0 && <div><p>No matches. Try a wider price range or fewer filters.</p><button onClick={explorer.clear}>Clear all filters</button></div>}
      </div>
      <div className="listing-list" aria-label="Synthetic listings" aria-busy={explorer.status === 'loading' && !explorer.validation}>
        {items.map(listing => <button key={listing.id} data-listing-id={listing.id} className={`listing-row ${selected?.id === listing.id ? 'selected' : ''}`}
          aria-pressed={selected?.id === listing.id} onClick={() => explorer.select(listing)}>
          <span className="model-thumbnail"><img src={`/models/${listing.propertyType}.png`} alt="" /></span>
          <span className="listing-copy"><strong>{listing.title}</strong><small>{listing.propertyType} · ★ {listing.rating.toFixed(1)}</small></span>
          <span className="listing-price">{price(listing)}</span>
        </button>)}
      </div>
      <details className="sidebar-legend"><summary>Map legend & controls</summary><div className="rating-key"><span><i className="gold" />4.0–4.4</span><span><i className="blue" />4.5–4.7</span><span><i className="mint" />4.8–5.0</span></div><p>Ring = rating · Tag = USD / night<br />Model = property type</p><p>Drag to pan · Scroll to zoom · Right-drag to tilt</p></details>
      <footer><span className="live-dot" /> STAYSCAPE EXPLORER <span>Synthetic stays</span></footer>
      </div>
    </motion.aside>
    <MapScene listings={items} selected={selected} selectionVersion={explorer.selectionVersion} onSelect={explorer.select} searchResult={explorer.searchResult} />
    <AnimatePresence>
    {selected && <motion.section key="selection" className="selection details-panel" aria-label="Selected listing"
      initial={{ opacity: 0, y: reduceMotion ? 0 : 16 }} animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: reduceMotion ? 0 : 10 }} transition={{ duration: reduceMotion ? 0 : 0.2 }}>
      <div><span className="eyebrow">YOUR MAP PICK</span><button aria-label="Close selected listing" onClick={() => explorer.select(null)}>×</button></div>
      <Placeholder key={selected.id} listing={selected} />
      <h2>{selected.title}</h2><p>{selected.neighborhood} · {selected.propertyType}<br />Up to {selected.guests} guests · {selected.bedrooms} bedrooms</p>
      <strong>{price(selected)} <small>USD / night</small><span>★ {selected.rating.toFixed(1)}</span></strong>
      <p className="description">{selected.description}</p><h3>Amenities</h3><ul className="amenities">{selected.amenities.map(amenity => <li key={amenity}>{amenity.replaceAll('_', ' ')}</li>)}</ul>
    </motion.section>}
    </AnimatePresence>
    <span className="sr-only" role="status">{explorer.notice}</span>
  </main>;
}
