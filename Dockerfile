# Pin the Python patch and distro; dependency hashes live in requirements.lock.
FROM python:3.12.13-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app/backend
COPY backend/requirements.lock ./requirements.lock
RUN pip install --require-hashes -r requirements.lock
COPY backend/app ./app
COPY backend/config ./config
COPY backend/static ./static
COPY scripts/measure_memory.py /app/scripts/measure_memory.py
# No credentials are accepted as build args. Synthetic seed + model are public and reproducible.
RUN python -m app.cli generate --count 300 --seed 42 \
    && python -m app.cli validate \
    && python -m app.cli seed \
    && python -m app.prepare_search
# Image data and code are root-owned/read-only. UID 1000 can write only temp/cache locations.
RUN useradd --uid 1000 --create-home appuser \
    && chown root:root /home/appuser \
    && chmod 755 /home/appuser \
    && chmod -R a-w /app
ENV DATABASE_URL="sqlite+aiosqlite:///file:/app/backend/data/stayscape-m2.db?mode=ro&immutable=1&uri=true" \
    SEARCH_DEMO_MODE=true HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
    HF_HOME=/tmp/huggingface XDG_CACHE_HOME=/tmp/cache SQLITE_TMPDIR=/tmp TMPDIR=/tmp
USER 1000:1000
EXPOSE 7860
# One worker keeps the local model/cache from being duplicated. HF routes to port 7860.
CMD ["python", "-m", "uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "7860", "--workers", "1"]
