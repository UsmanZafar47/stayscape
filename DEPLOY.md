# Deploy StayScape: GitHub → Hugging Face Docker + Vercel

Optional reference only: deployment was canceled by request. The project is being packaged for GitHub with a [local walkthrough](docs/WALKTHROUGH.md); no cloud service has been published. Replace uppercase account/repository/domain placeholders. Current provider terms checked 2026-10-10.

## 1. GitHub readiness and secret audit

The source audit found **no matching API keys/tokens/private keys, no actual `.env` files, and no credential-bearing URLs outside documented placeholders**. Public URLs for Groq, tiles, licenses and localhost are not credentials. Generated dependencies/caches/binary assets are excluded from the text scan. There was no Git repository/history in this checkout to audit; the pre-push command below scans the index and all reachable history once Git exists. Unknown secret formats can escape pattern scanning: review what you stage.

`.gitignore` excludes local environments, databases, generated data/model cache, dependencies, build/test/cache/editor output and credential files. `.dockerignore` allowlists only backend source/config/static assets, the hashed requirements lock and memory measurement script. Real `.env` files never enter the image. `backend/.env.example` and `frontend/.env.example` contain safe defaults, blanks and placeholders only.

[CREDITS.md](CREDITS.md) covers Kenney models/preview PNGs (CC0), OpenStreetMap (ODbL), OpenMapTiles, OpenFreeMap styles/fonts/icons and their upstream licenses, the MIT embedding model, and project-authored SVG illustrations. Preserve map attribution in captures. There is no new blanket license grant for the project's original code/assets.

Create an **empty** repository at https://github.com/new (do not initialize a README/license/gitignore). Then run in Windows PowerShell; Git's credential manager handles sign-in, never embed a token in a remote URL:

```powershell
Set-Location 'C:\Users\dell\OneDrive\Desktop\3D-map'
git init -b main
# Set local identity if Git has not already been configured.
git config user.name 'YOUR NAME'
git config user.email 'YOUR GITHUB EMAIL'
.\backend\.venv-m2\Scripts\python.exe scripts/check_secrets.py
if ($LASTEXITCODE -ne 0) { throw 'Secret check failed; do not stage or push.' }
git add .
.\backend\.venv-m2\Scripts\python.exe scripts/check_secrets.py --staged --history
if ($LASTEXITCODE -ne 0) { throw 'Staged/history secret check failed; do not commit.' }
git diff --cached --stat
git status --short
# Review staged paths before running this commit.
git commit -m 'Prepare StayScape for Docker Spaces and Vercel'
git remote add origin https://github.com/YOUR_USER/YOUR_REPO.git
.\backend\.venv-m2\Scripts\python.exe scripts/check_secrets.py --staged --history
if ($LASTEXITCODE -ne 0) { throw 'Pre-push secret check failed.' }
git push -u origin main
```

For later pushes, run the same worktree and `--staged --history` checks after staging and before committing/pushing. If a real credential is ever found in history, revoke/rotate it and remove it from history before publishing; `.gitignore` does not remove existing commits. No real credentials were printed by this audit tool.

## 2. Check the Docker image locally

Start Docker Desktop (Linux containers). From the project root:

```powershell
docker build -t stayscape-api:local .
docker run --rm --name stayscape-api --read-only --tmpfs /tmp:rw,nosuid,size=64m --memory 512m --memory-swap 512m -p 7860:7860 stayscape-api:local
```

In another terminal:

```powershell
Invoke-RestMethod http://127.0.0.1:7860/api/health
$examples = Invoke-RestMethod http://127.0.0.1:7860/api/search/examples
$body = @{ query = $examples.queries[0]; demo = $true } | ConvertTo-Json
Invoke-RestMethod http://127.0.0.1:7860/api/search -Method Post -ContentType 'application/json' -Body $body
docker stats --no-stream stayscape-api
# Stop only this project container when finished.
docker stop stayscape-api
```

The image pins Python **3.12.13 / Debian Bookworm**, uses UID/GID **1000**, port **7860**, and **one Uvicorn worker**. Build time generates seed 42 / 300 stays, seeds SQLite, downloads the public FastEmbed model and precomputes the index/examples. Runtime SQL uses `mode=ro&immutable=1`; source/data are not writable by UID 1000. Python bytecode is disabled; caches/temp paths point to `/tmp`. Startup does not seed, migrate or download models. A changed dataset requires rebuilding the image. Build-time internet is required; runtime demo/rules ranking needs no network.

`/api/health` reads database health and performs no AI interpretation/provider call. Demo suggestions bypass the provider. `SEARCH_DEMO_MODE=true` is the default; no provider credentials are needed.

### Memory result and default

A real Linux Uvicorn worker under a **512 MiB container cap**, with **network disabled** and **read-only filesystem**, measured **88.7 MiB RSS at startup**, then **338.4 / 339.0 / 339.1 MiB** after three distinct searches. Health, demos and database write rejection passed. [Recorded measurements](docs/evidence/deployment-memory.json).

**FastEmbed remains the default; no TF-IDF fallback was added**, because measured usage stayed below 512 MiB. This is a small sequential sample, not a guarantee for every query/load; monitor actual Space memory. RSS excludes some container overhead/page cache. Search inference is serialized by the existing rank lock. A Windows local ASGI sample used 85.5 → 249.4 MiB, illustrating why the Linux measurement matters.

To repeat a separate provider-free memory probe (do not run a second model inside the constrained server container):

```powershell
docker run --rm --network none --read-only --tmpfs /tmp:rw,nosuid,size=64m --memory 512m --memory-swap 512m stayscape-api:local python /app/scripts/measure_memory.py
```

That probe uses an in-process ASGI client; the recorded deployment figures above came from `/proc/1/status` of the actual server worker.

## 3. Hugging Face Space

**Check eligibility first.** Current [Spaces documentation](https://huggingface.co/docs/hub/spaces-overview) says creating a Docker Space requires a paid account plan. CPU Basic itself has no hourly charge; it currently lists 2 vCPU, 16 GB RAM and 50 GB nonpersistent disk. Do not assume “CPU Basic Free” means a new account can create Docker Spaces for zero total cost. No plan upgrade was performed here.

1. Hugging Face → New Space → name it → **Docker / Blank** → **CPU Basic** → **Public** (the Vercel browser must reach the API). Do not select a paid hardware upgrade unintentionally.
2. This repository's root README already contains `sdk: docker` and `app_port: 7860`; root `Dockerfile` uses the repository root as its build context. The Space is an API: open `/docs` or `/api/health`, not an expected landing page at `/`.
3. Copy the committed project into a clone of the newly initialized Space. This retains its initial history, avoiding a force push. From the GitHub checkout, using the existing backend Python for the secret check:

   ```powershell
   Set-Location 'C:\Users\dell\OneDrive\Desktop\3D-map'
   $checkPython = (Resolve-Path '.\backend\.venv-m2\Scripts\python.exe').Path
   $spaceCheckout = Join-Path (Split-Path (Get-Location).Path -Parent) 'stayscape-space'
   git clone https://huggingface.co/spaces/YOUR_HF_USER/YOUR_SPACE $spaceCheckout
   if ($LASTEXITCODE -ne 0) { throw 'Space clone failed.' }
   $deployArchive = Join-Path $env:TEMP 'stayscape-deploy.zip'
   git archive --format=zip --output=$deployArchive HEAD
   if ($LASTEXITCODE -ne 0) { throw 'Git archive failed.' }
   Expand-Archive -LiteralPath $deployArchive -DestinationPath $spaceCheckout -Force
   # HF asset patterns may use LFS; Git for Windows includes Git LFS.
   git -C $spaceCheckout lfs install --local
   git -C $spaceCheckout add .
   & $checkPython "$spaceCheckout\scripts\check_secrets.py" --staged --history
   if ($LASTEXITCODE -ne 0) { throw 'Space secret check failed.' }
   git -C $spaceCheckout diff --cached --stat
   git -C $spaceCheckout commit -m 'Deploy StayScape API'
   git -C $spaceCheckout push
   ```

   Authenticate through Git's credential prompt with your HF username and a write-capable token scoped to this Space. Do not paste the token into commands, source files or remote URLs. Configure Git identity in that clone if needed. Later updates repeat archive/expand/stage/check/commit/push after pulling the Space checkout first; do not clone over an existing directory.

4. Space → **Settings → Variables and secrets**. Add non-secret **Variables**:

   | Name | Value |
   | --- | --- |
   | `SEARCH_DEMO_MODE` | `true` |
   | `ALLOWED_ORIGINS` | `["http://localhost:5173","http://127.0.0.1:5173"]` initially |
   | `SEARCH_RATE_PER_MINUTE` | `20` (optional, existing default) |

   Do not override `DATABASE_URL`, offline/cache flags or the start command; the image sets these for immutable runtime data. No secrets are needed for default mode.

5. Optional provider later: add **Secret** `SEARCH_API_KEY` through that UI. Set Variables `SEARCH_BASE_URL`, `SEARCH_MODEL`, `SEARCH_DEMO_MODE=false` and optionally `SEARCH_TIMEOUT_SECONDS=6`. One provider only; key stays in backend runtime. No Docker build argument or build secret is needed for public embedding downloads. Restart after settings changes.
6. Wait for build → Running. Copy the direct **`https://YOUR-SPACE-SUBDOMAIN.hf.space`** URL from the Space (do not use `huggingface.co/spaces/...` as the API base). Visit `/api/health`, `/docs` and `/api/search/examples`. The first build downloads dependencies/model; later starts do not.

## 4. Vercel frontend

Vercel → Add New → Project → import the GitHub repository. Set exactly:

| Setting | Value |
| --- | --- |
| Root Directory | `frontend` |
| Framework Preset | `Vite` |
| Node.js | `22.x` |
| Install Command | `npm ci` |
| Build Command | `npm run build` |
| Output Directory | `dist` |
| Environment Variable | `VITE_API_URL=https://YOUR-SPACE-SUBDOMAIN.hf.space` |
| Optional currency variable | `VITE_CURRENCY_CODE=USD` |

Set `VITE_API_URL` for **Production**. Add it for Preview only if you also allow the exact preview origin in backend CORS. It is a public origin, not a secret; no API key belongs in Vercel or any `VITE_` variable. Do not append `/api`. Vite replaces the URL during build: changing it requires **Redeploy**. API requests and local placeholder image URLs use the same origin helper. Locally a blank value uses the existing Vite proxy.

Deploy, then note the stable `https://YOUR-PROJECT.vercel.app` production URL. In Space Settings update:

```text
ALLOWED_ORIGINS=["https://YOUR-PROJECT.vercel.app"]
```

Add a custom domain as a second exact origin if used. No trailing slash or wildcard. Restart the Space, then refresh Vercel. Keep localhost in the list only if you want local clients to use the deployed API. `CORS_ORIGINS` remains a legacy alias; `ALLOWED_ORIGINS` takes precedence.

## 5. Cold starts, limits and remaining deployment caveats

- The frontend is static and does not wait for a frontend server to wake. The backend can sleep. First connection shows a clear message after four seconds and allows 90 seconds; failures offer Retry. Once connected, later requests use the existing 15-second timeout. The map may load while the backend is waking.
- Verify HF account eligibility/plan cost, CPU Basic resources, idle sleep policy and ephemeral storage on the [current overview](https://huggingface.co/docs/hub/spaces-overview) and [hardware page](https://huggingface.co/docs/hub/spaces-gpus). No durable disk is needed for this immutable dataset.
- Verify [Vercel Hobby](https://vercel.com/docs/plans/hobby): personal/non-commercial usage only, currently 100 GB fast data transfer and 1 million CDN requests, deployment/build limits and behavior after exceeding allowances. This app uses no Vercel Functions. Check optional provider free-tier quotas separately.
- Existing IP rate limiting uses the address Uvicorn receives. HF's reverse proxy may group visitors; do not blindly trust all forwarded headers. Validate the effective visitor IP/proxy policy before treating it as robust public abuse protection. Keep one worker; caches/limiter reset at restart.
- The frontend dependency audit previously reported 9 advisories (2 moderate, 7 high). No broad dependency upgrade was included here. Review them before public use. The large map bundle remains about 675 KB gzip.

## 6. Live-site checklist

- [ ] GitHub contains `.env.example` files but no real `.env`, keys, environments, DB/model cache or node_modules. Pre-push scan passes.
- [ ] HF logs show one worker on 7860; `/api/health` returns `ok` without a provider configured.
- [ ] Vercel network requests go to the direct `.hf.space` origin; no CORS errors or provider keys appear in browser requests.
- [ ] 300 stays load; map, sidebar, filters and selection agree; details illustrations load from the backend origin.
- [ ] A saved chip works with `SEARCH_DEMO_MODE=true` and no key. A typed query returns the disclosed keyword fallback with ranked results.
- [ ] A sleeping/unreachable backend shows the waking message; Retry recovers after restart. Suggestions can be retried separately.
- [ ] Reload after a Space restart: the same synthetic dataset remains available without runtime seeding/downloading.
- [ ] Phone layout and attribution remain visible; a search/filter-out keeps the established selection/camera behavior.
- [ ] Watch Space memory after several typed searches; confirm selected plans/quotas before sharing the link.

## Files and validation

Added: root `Dockerfile`, `.dockerignore`, `DEPLOY.md`; `scripts/check_secrets.py`, `scripts/measure_memory.py`; backend/frontend deployment tests; `docs/evidence/deployment-memory.json`.

Updated: `.gitignore`, backend/frontend `.env.example`; backend `config.py` and `database.py`; frontend `api.ts`, `useExplorer.ts`, `App.tsx`, `SearchBox.tsx`; README and historical deployment-assessment pointer. No cloud resources, Git remotes or credentials were created. Inline comments explain the deployment decisions.
