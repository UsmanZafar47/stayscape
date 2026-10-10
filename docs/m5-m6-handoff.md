# M5 + M6 handoff

Scope: visible polish and portfolio documentation only. Existing M3/M4 behavior is retained. Deployment is an assessment, with no hosting files or published service.

## Files changed

| Files | Change |
| --- | --- |
| `frontend/src/App.tsx` | Framer Motion sidebar/details, phone collapse control, refreshed milestone label |
| `frontend/src/MapScene.tsx` | Lighter city extrusions, street labels deferred until zoom 15, camera easing, live reduced-motion handling |
| `frontend/src/listingLayers.ts` | Three stable instance tints, reusing the same model scenes |
| `frontend/src/useAnimatedListings.ts` | Cubic result enter/exit easing and reactive motion preference |
| `frontend/src/styles.css` | Phone panel with one scroll region, readable input sizing, focus contrast, reserved attribution space |
| `frontend/package.json`, `frontend/package-lock.json` | Pinned Framer Motion dependency |
| `frontend/tests/polish.spec.ts` | Desktop search/selection, phone collapse, reduced-motion and attribution geometry check; screenshot capture |
| `README.md`, `backend/README.md` | Portfolio overview/setup and historical-backend-note clarification |
| `CREDITS.md` | Model, map, typography, embedding and illustration sources/licenses |
| `docs/demo-script.md`, `docs/interview-talking-points.md` | Timed 60-second script and eight talking points |
| `docs/deployment-assessment.md` | Free-host proposal, limits, prerequisites and exact dashboard/build steps |
| `docs/evidence/m5-desktop.png`, `docs/evidence/m5-phone.png`, refreshed `m3-*.png` regression captures | Fresh browser captures |

Design comments are inline near the phone layout, instance tinting, label gating and motion logic. No backend/API behavior or environment variables changed. Phone collapse is deliberately a simple in-flow panel, not a draggable sheet with gesture state.

## Run

Use the two PowerShell terminals in [README](../README.md#windows-powershell-setup). Existing workspace setup is ready: backend Uvicorn on 8000, frontend Vite on 5173. No provider key is needed.

## Browser checklist

- [ ] Overview lists 300 synthetic stays; map and list agree after filters.
- [ ] City buildings are lighter, street names appear only closer in, and models have warm/cool/mint variants.
- [ ] Hover lifts a model. Clicking opens animated details and smoothly flies to the stay.
- [ ] Filtering animates models out; removing the selection closes details without resetting the camera.
- [ ] First demo chip shows an explanation, outlines matches and fits the returned bounds.
- [ ] At 390px width, lower controls scroll and collapse/reopen; inputs and details remain usable.
- [ ] Attribution stays visible above the phone panel, including with details open.
- [ ] With OS/browser reduced motion enabled, camera/panel/result transitions are immediate.
- [ ] Empty filters offer Clear; API failures retain previous results with Retry.

## Validation and limits

Production TypeScript/Vite build passed. Ten Playwright tests passed (client/filter/declutter, loading/retry/stale responses/image retry, plus real-map polish, mesh hover/click, filter-out camera stability and map-service retry). Desktop and phone screenshots were inspected. The main bundle remains large, about 675 KB gzip; code splitting is future work. No fresh FPS claim is made for M5. The dependency install reported nine advisories (two moderate, seven high); dependency remediation is outside this visual-only change and is listed before deployment. No broad dependency upgrade or backend changes were made.

See the deployment assessment before publishing: cold starts exceed the current client timeout, SQLite is ephemeral on Render Free, and full embedding memory needs a host measurement.
