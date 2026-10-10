"""Run offline after seeding: python -m app.prepare_search. Never called by an HTTP request."""
import asyncio
import json

from fastembed import TextEmbedding

from app.config import BACKEND, Settings
from app.database import make_engine, session_factory
from app.schemas import ListingFilters
from app.search import MODEL, Ranker, document, eligible_listings, make_response, text_hash
from app.search_parser import parse_rules
from app.sql_repository import SQLListingRepository

QUERIES = [
    "Quiet Manhattan apartment under $250 for 2 guests with wifi",
    "Romantic Brooklyn loft under $300 with a balcony",
    "Family house in Queens under $350 for 4 guests with a kitchen",
    "Business trip to Jersey City under $250 with wifi and workspace",
    "Scenic Hoboken stay under $300 with a balcony",
    "Affordable Manhattan stay under $150 for 2 guests",
    "Lively Brooklyn nightlife under $220 with air conditioning",
]


async def main():
    settings = Settings()
    engine = make_engine(settings.database_url)
    try:
        async with session_factory(engine)() as session:
            repo = SQLListingRepository(session)
            items = []
            while True:
                page = await repo.list(ListingFilters(), limit=100, offset=len(items))
                items.extend(page.items)
                if len(items) >= page.total:
                    break
            if not items:
                raise ValueError("Seed the M2 database first")
            model = TextEmbedding(MODEL, cache_dir=str(BACKEND / "data/fastembed-cache"), threads=2)
            vectors = list(model.passage_embed([document(item) for item in items]))
            index = {"model": MODEL, "entries": {str(item.id): {"hash": text_hash(item), "vector": vector.tolist()}
                                                for item, vector in zip(items, vectors, strict=True)}}
            settings.search_index_file.parent.mkdir(parents=True, exist_ok=True)
            settings.search_index_file.write_text(json.dumps(index), encoding="utf-8")
            ranker = Ranker(settings)
            examples = []
            for query in QUERIES:
                intent = parse_rules(query)
                eligible = await eligible_listings(repo, intent)
                ranked, scores = ranker.rank(eligible, query, intent)
                response = make_response(query, intent, len(eligible), ranked, scores, "demo")
                examples.append({"query": query, "response": response.model_dump(mode="json")})
            settings.search_examples_file.write_text(json.dumps(examples, indent=2), encoding="utf-8")
            print(f"Prepared {len(items)} local vectors and {len(examples)} provider-free demo responses.")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
