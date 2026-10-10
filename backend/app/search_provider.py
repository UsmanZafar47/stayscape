import asyncio
import json

import httpx
from pydantic import ValidationError

from app.config import Settings
from app.search_parser import SearchIntent, parse_rules


class SearchProvider:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = httpx.AsyncClient(timeout=settings.search_timeout_seconds, trust_env=False)

    async def interpret(self, query: str) -> tuple[SearchIntent, str]:
        rules = parse_rules(query)
        s = self.settings
        if s.search_demo_mode or not s.search_api_key or not s.search_model:
            return rules, "rules"
        messages = [
            {"role": "system", "content": "Extract ONLY explicitly requested rental filters and vibe words. "
             "Prices are USD integer cents, guests/bedrooms are minimums. Omit unspecified fields. "
             "Return only JSON matching this schema, no commentary: " + json.dumps(SearchIntent.model_json_schema())},
            {"role": "user", "content": query},
        ]
        try:
            # One deadline covers the initial request AND the single validation-repair attempt.
            async with asyncio.timeout(s.search_timeout_seconds):
                for attempt in range(2):
                    response = await self.client.post(
                        s.search_base_url.rstrip("/") + "/chat/completions",
                        headers={"Authorization": "Bearer " + s.search_api_key},
                        json={"model": s.search_model, "messages": messages, "temperature": 0,
                              "max_tokens": 700, "response_format": {"type": "json_object"}},
                    )
                    response.raise_for_status()
                    raw = response.json()["choices"][0]["message"]["content"]
                    try:
                        if not isinstance(raw, str) or len(raw) > 16000:
                            raise ValueError("Invalid output size")
                        intent = SearchIntent.model_validate_json(raw)
                        # Obvious explicit constraints from the local parser cannot be weakened by a model.
                        merged = intent.model_dump()
                        merged.update(rules.model_dump(exclude_none=True, exclude={"amenities", "vibes"}))
                        merged["amenities"] = sorted(set(intent.amenities) | set(rules.amenities))
                        merged["vibes"] = sorted(set(intent.vibes) | set(rules.vibes))
                        return SearchIntent.model_validate(merged), "provider"
                    except (ValidationError, ValueError):
                        if attempt == 0:
                            if isinstance(raw, str) and len(raw) <= 16000:
                                messages.append({"role": "assistant", "content": raw})
                            messages.append({"role": "user", "content": "Your JSON failed validation. Repair it once: "
                                             "use allowed enums, integer cents and counts, ordered prices, no extra keys."})
        except (httpx.HTTPError, TimeoutError, KeyError, IndexError, TypeError, ValueError):
            pass  # No provider hopping, hidden network retries, or leaked provider/key error messages.
        return rules, "rules"
