import os
import re
from typing import Any, Iterable, Optional

import httpx


STOP_WORDS = {"about", "and", "for", "from", "have", "in", "is", "me", "of", "show", "tell", "the", "to", "what", "with"}
PROPERTY_TYPES = {"floor", "land", "mansion", "residence", "villa"}


def _tokens(text: str) -> set[str]:
    return {
        token.rstrip("s")
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) > 1 and token not in STOP_WORDS
    }


def _query_constraints(question: str) -> dict[str, object]:
    tokens = _tokens(question)
    property_type = next((item for item in PROPERTY_TYPES if item in tokens), None)
    bedrooms = re.search(r"(?:at least|minimum|min)\s+(\d+)\s+bedrooms?", question, re.IGNORECASE)
    price = re.search(
        r"(?:under|below|less than|maximum|max)\s+(?:sar\s*)?(\d+(?:\.\d+)?)\s*(million|m|thousand|k)?",
        question,
        re.IGNORECASE,
    )
    max_price = None
    if price:
        amount = float(price.group(1))
        multiplier = {"million": 1_000_000, "m": 1_000_000, "thousand": 1_000, "k": 1_000}.get(
            (price.group(2) or "").lower(), 1
        )
        max_price = int(amount * multiplier)
    return {
        "property_type": property_type,
        "min_bedrooms": int(bedrooms.group(1)) if bedrooms else None,
        "max_price": max_price,
    }


def retrieve(question: str, records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    query_tokens = _tokens(question)
    constraints = _query_constraints(question)
    ranked: list[tuple[int, dict[str, Any]]] = []
    for record in records:
        if constraints["property_type"] and record.get("property_type") != constraints["property_type"]:
            continue
        if constraints["min_bedrooms"] is not None and (record.get("bedrooms") or 0) < constraints["min_bedrooms"]:
            continue
        if constraints["max_price"] is not None and (
            record.get("price") is None or record["price"] > constraints["max_price"]
        ):
            continue
        title_tokens = _tokens(record.get("title") or "")
        metadata = " ".join(
            str(record.get(field) or "")
            for field in ("city", "district", "property_type", "developer", "description")
        )
        score = (5 * len(query_tokens & title_tokens)) + len(query_tokens & _tokens(metadata))
        if score:
            ranked.append((score, record))
    if not ranked:
        return []
    best_score = max(score for score, _ in ranked)
    return [record for score, record in ranked if score == best_score][:5]


def _fallback_answer(matches: list[dict[str, Any]]) -> str:
    if not matches:
        return "I could not find a matching property in the current catalog. Try a city, district, property type, or price range."
    lines = ["Here is what I found in the current catalog:"]
    for record in matches:
        details = [record["title"]]
        if record.get("district") or record.get("city"):
            details.append(", ".join(part for part in (record.get("district"), record.get("city")) if part)
            )
        if record.get("price"):
            details.append(f"SAR {record['price']:,}")
        lines.append(" — ".join(details))
    return "\n".join(lines)


def _model_answer(question: str, matches: list[dict[str, Any]], api_key: str) -> Optional[str]:
    context = [
        {
            "title": record["title"],
            "location": ", ".join(
                part for part in (record.get("district"), record.get("city"), record.get("country")) if part
            ),
            "property_type": record.get("property_type"),
            "bedrooms": record.get("bedrooms"),
            "area_sqm": record.get("area_sqm"),
            "price": record.get("price"),
            "currency": record.get("currency"),
            "description": record.get("description"),
        }
        for record in matches
    ]
    messages = [
        {
            "role": "system",
            "content": (
                "Answer only from the supplied property catalog. Do not invent availability, "
                "features, prices, or investment advice. Be concise and state when data is unavailable."
            ),
        },
        {"role": "user", "content": f"Question: {question}\nCatalog: {context}"},
    ]
    try:
        response = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": os.getenv("OPENROUTER_MODEL", "openrouter/free"), "messages": messages},
            timeout=20,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return content.strip() if isinstance(content, str) and content.strip() else None
    except (httpx.HTTPError, KeyError, IndexError, TypeError):
        return None


def answer_question(
    question: str, records: Iterable[dict[str, Any]], api_key: Optional[str] = None
) -> dict[str, Any]:
    matches = retrieve(question, records)
    key = api_key if api_key is not None else os.getenv("OPENROUTER_API_KEY")
    model_response = _model_answer(question, matches, key) if key and matches else None
    return {
        "answer": model_response or _fallback_answer(matches),
        "mode": "model" if model_response else "retrieval",
        "sources": [
            {"title": record["title"], "source": record["source"], "source_url": record["source_url"]}
            for record in matches
        ],
        "disclaimer": "Prices and availability may have changed since the catalog was collected.",
    }
