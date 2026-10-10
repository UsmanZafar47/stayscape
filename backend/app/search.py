"""Lean M4 pipeline: SQL eligibility, local ranking, deterministic explanations."""
import asyncio
import hashlib
import json
import time
from collections import OrderedDict, deque
from typing import Literal

from app.config import BACKEND, Settings
from app.errors import ServiceError
from app.schemas import Contract, Listing
from app.search_parser import SearchIntent, SearchRequest
from app.search_provider import SearchProvider

MODEL = "BAAI/bge-small-en-v1.5"


class SearchResponse(Contract):
    query: str
    intent: SearchIntent
    items: list[Listing]
    scores: list[float]
    eligible_total: int
    explanation: str
    bounds: tuple[tuple[float, float], tuple[float, float]] | None
    source: Literal["demo", "rules", "provider"]
    ranking: Literal["fastembed"] = "fastembed"
    cached: bool = False


def document(item: Listing) -> str:
    return " ".join([item.title, item.description, item.region,
                     *[v.value for v in item.vibes], *[a.value for a in item.amenities]])


def text_hash(item: Listing) -> str:
    return hashlib.sha256(document(item).encode()).hexdigest()


class Ranker:
    def __init__(self, settings: Settings):
        import numpy as np
        from fastembed import TextEmbedding
        self.np = np
        self.index = json.loads(settings.search_index_file.read_text(encoding="utf-8"))
        if self.index["model"] != MODEL:
            raise ValueError("Incompatible embedding index")
        # Runtime is strictly local: downloads belong to the offline prepare command.
        self.model = TextEmbedding(MODEL, cache_dir=str(BACKEND / "data/fastembed-cache"),
                                   threads=2, local_files_only=True)

    def rank(self, eligible: list[Listing], query: str, intent: SearchIntent):
        if not eligible:
            return [], []
        entries = self.index["entries"]
        if any(str(item.id) not in entries or entries[str(item.id)]["hash"] != text_hash(item)
               for item in eligible):
            raise ValueError("Stale index")
        # Hard constraints are already enforced by SQL. Only soft vibes influence this ordering.
        text = "A " + ", ".join(v.value for v in intent.vibes) + " stay" if intent.vibes else query
        vector = self.np.asarray(list(self.model.query_embed([text]))[0])
        matrix = self.np.asarray([entries[str(item.id)]["vector"] for item in eligible])
        scores = (matrix @ vector) / (self.np.linalg.norm(matrix, axis=1) * self.np.linalg.norm(vector))
        order = sorted(range(len(eligible)), key=lambda i: (-float(scores[i]), str(eligible[i].id)))[:12]
        return [eligible[i] for i in order], [round(float(scores[i]), 5) for i in order]


def make_response(query, intent, eligible_total, items, scores, source):
    bounds = None
    if items:
        bounds = ((min(x.longitude for x in items), min(x.latitude for x in items)),
                  (max(x.longitude for x in items), max(x.latitude for x in items)))
        low, high = min(x.price_minor for x in items), max(x.price_minor for x in items)
        regions = ", ".join(sorted({x.region.replace("-", " ") for x in items}))
        explanation = (f"Showing {len(items)} of {eligible_total} eligible stays in {regions}, "
                       f"${low / 100:.2f}–${high / 100:.2f} USD/night. "
                       "Every shown stay satisfies the interpreted hard filters. ")
        if intent.vibes:
            explanation += "Ranked for " + ", ".join(v.value for v in intent.vibes) + "; vibe similarity is not a guarantee. "
    else:
        explanation = "No matches satisfy the interpreted hard filters. Try a larger budget or fewer requirements. "
    if source == "rules":
        explanation += "Limited keyword interpretation: recognized prices, counts, regions, amenities and vibes only; other wording may be ignored. Review the interpreted filters."
    elif source == "demo":
        explanation += "Offline demo: saved interpretation and ranking; no provider request."
    else:
        explanation += "Filters interpreted by the configured provider; explanation computed from these results."
    return SearchResponse(query=query, intent=intent, items=items, scores=scores,
                          eligible_total=eligible_total, explanation=explanation, bounds=bounds, source=source)


async def eligible_listings(repo, intent: SearchIntent):
    result = []
    while True:
        page = await repo.list(intent.filters(), limit=100, offset=len(result))
        result.extend(page.items)
        if len(result) >= page.total:
            return result


class SearchService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.provider = SearchProvider(settings)
        self.ranker = None
        self.rank_lock = asyncio.Lock()
        self.cache: OrderedDict[str, tuple[float, SearchResponse]] = OrderedDict()
        self.rates: OrderedDict[str, deque] = OrderedDict()
        self.examples = json.loads(settings.search_examples_file.read_text(encoding="utf-8")) if settings.search_examples_file.exists() else []

    def rate_limit(self, ip: str):
        now = time.monotonic()
        window = self.rates.setdefault(ip, deque())
        self.rates.move_to_end(ip)
        while window and window[0] <= now - 60:
            window.popleft()
        if len(window) >= self.settings.search_rate_per_minute:
            raise ServiceError("RATE_LIMIT", "Too many searches. Wait one minute and retry.", 429)
        window.append(now)
        while len(self.rates) > 1024:
            self.rates.popitem(last=False)

    async def search(self, request: SearchRequest, repo) -> SearchResponse:
        key = json.dumps([" ".join(request.query.lower().split()), request.demo])
        now = time.monotonic()
        cached = self.cache.get(key)
        if cached and now - cached[0] < 300:
            self.cache.move_to_end(key)
            return cached[1].model_copy(update={"cached": True}, deep=True)
        if request.demo:
            example = next((x for x in self.examples if x["query"].lower() == request.query.lower()), None)
            if not example:
                raise ServiceError("UNKNOWN_DEMO", "Choose one of the demo suggestions.", 422)
            response = SearchResponse.model_validate(example["response"])
            eligible = await eligible_listings(repo, response.intent)
            actual = {item.id: item for item in eligible}
            # Saved demos must never claim properties that have changed in the current SQL dataset.
            if len(eligible) != response.eligible_total or any(actual.get(item.id) != item for item in response.items):
                raise ServiceError("STALE_DEMO", "Demo data changed. Run the search preparation command.", 409)
        else:
            intent, source = await self.provider.interpret(request.query)
            eligible = await eligible_listings(repo, intent)
            if eligible:
                try:
                    async with self.rank_lock:
                        if self.ranker is None:
                            self.ranker = await asyncio.to_thread(Ranker, self.settings)
                        items, scores = await asyncio.to_thread(self.ranker.rank, eligible, request.query, intent)
                except (OSError, ValueError, KeyError) as exc:
                    raise ServiceError("SEARCH_INDEX", "Local search index unavailable or stale. Run python -m app.prepare_search and retry.") from exc
            else:
                items, scores = [], []
            response = make_response(request.query, intent, len(eligible), items, scores, source)
        self.cache[key] = (now, response)
        self.cache.move_to_end(key)
        while len(self.cache) > 128:
            self.cache.popitem(last=False)
        return response
