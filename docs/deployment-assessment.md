> Historical M5/M6 assessment. The implemented deployment target is now Hugging Face + Vercel; follow [DEPLOY.md](../DEPLOY.md).

# Deployment assessment — no deployment performed

Checked 2026-10-10. The simplest conventional free pairing is **Cloudflare Pages (static frontend) + Render Free web service (FastAPI)**. It is suitable for a portfolio trial; full FastEmbed memory usage must be measured before calling it reliable on Render Free.

| Part | Expected free limits / implication |
| --- | --- |
| Cloudflare Pages | Static hosting does not sleep. Free plan: 500 builds/month, 20,000 files, 25 MiB per asset. This frontend fits the asset limits. [Official limits](https://developers.cloudflare.com/pages/platform/limits/) |
| Render backend | 0.1 CPU, 512 MB RAM. Sleeps after 15 idle minutes; waking can take about a minute. 750 free instance hours/workspace/month. [Compute plans](https://render.com/docs/compute-plans), [free service limits](https://render.com/docs/free) |
| SQLite | Render Free disk is ephemeral, with no persistent disk attachment. Restarts/redeploys lose runtime writes. Rebuild/reseed this read-only synthetic database each deployment; use persistent Postgres or a paid disk before adding user writes. [Filesystem limits](https://render.com/docs/free) |
| Local embedding model | A 67 MB download is not a 67 MB RAM guarantee. Python + ONNX + map API can exceed 512 MB under load. Saved demo chips avoid model inference, but typed queries still load it even with `SEARCH_DEMO_MODE=true`. |

I would trial this pairing with saved examples first, then measure a typed search and concurrent requests. If memory exceeds the free allowance, choose a measured TF-IDF replacement or a larger paid instance in a separate task; neither change has been made. Hugging Face CPU Basic advertises zero hourly compute cost, but creating new Docker/Gradio compute Spaces now requires a paid plan, so it is not the zero-cost default recommendation. [Spaces documentation](https://huggingface.co/docs/hub/spaces-overview).

## Changes needed before deploying

1. Add a frontend API-origin helper, used by both `/api` requests and `/static` image URLs, with `VITE_API_BASE_URL` pointing to Render. The Vite development proxy does not ship with the static bundle. This variable does **not exist in the current implementation**.
2. Set backend `CORS_ORIGINS` to the exact Pages HTTPS origin. Keep provider keys in Render secrets only.
3. Reproduce the synthetic dataset and embedding cache/index in the backend build; keep one process/worker for SQLite and process-local cache/limiter. Verify saved demos match the seed. Never seed live user data this way.
4. Account for the approximately one-minute cold start: current frontend requests time out after 15 seconds, so a first visit may show Retry. Warm the API manually before a presentation; later decide whether to lengthen startup handling.
5. Configure trusted proxy handling for Render before treating `request.client.host` as a public visitor IP. Do not trust arbitrary forwarded headers. The current direct-IP limiter may otherwise group visitors behind the proxy.
6. Inspect the dependency audit before publishing. The current install reports 9 advisories (2 moderate, 7 high); no broad dependency upgrades were included in this visual-only task.

## Exact proposed dashboard steps (after approving those changes)

1. Push the reviewed project to your Git repository. Do not commit `.env`, database files or provider keys.
2. Render ? New ? Web Service ? connect repository ? root `backend` ? Python runtime ? Free instance. Pin Python 3.12. Use a single worker and `/api/health` as the health-check path.
3. Build command (Render's Linux shell, not local PowerShell):

   ```sh
   pip install -r requirements.lock && python -m app.cli generate --count 300 --seed 42 && python -m app.cli validate && python -m app.cli seed && python -m app.prepare_search
   ```

   Start command:

   ```sh
   python -m uvicorn app.main:create_app --factory --host 0.0.0.0 --port $PORT --workers 1
   ```

4. Add `SEARCH_DEMO_MODE=true` and leave provider credentials unset for the first trial. Keep the default absolute SQLite path. Deploy; record the `https://...onrender.com` URL. Inspect build logs and memory during one saved example and one typed query. Stop here if memory is insufficient; do not silently disable ranking.
5. Cloudflare dashboard ? Workers & Pages ? Create ? Pages ? connect the same repository. Root `frontend`; build command `npm ci && npm run build`; output `dist`; Node 22. Set the proposed `VITE_API_BASE_URL` to the Render URL, then deploy only after the helper change is merged.
6. Set Render `CORS_ORIGINS=["https://YOUR-PROJECT.pages.dev"]`, restart, and retest API calls plus placeholder images from Pages. Preview domains need an explicit policy; do not allow every origin by default.
7. Test a cold start, retry, saved search, typed fallback, empty filter, selection and phone attribution. Check that no browser request contains a provider key. Retain spend limits/free instance selection; do not enable paid upgrades implicitly.

No cloud account was connected, no deployment files were added, and no service was published. These are proposed steps, not a claim that the current checkout is deploy-ready.

