import json
from pathlib import Path
from typing import Any, Iterable, Optional


CATALOG_PATH = Path(__file__).resolve().parents[1] / "data" / "initial_catalog.json"


def load_records() -> list[dict[str, Any]]:
    with CATALOG_PATH.open(encoding="utf-8") as catalog_file:
        return json.load(catalog_file)["records"]


def filter_records(
    records: Iterable[dict[str, Any]],
    *,
    source: Optional[str] = None,
    city: Optional[str] = None,
    district: Optional[str] = None,
    property_type: Optional[str] = None,
    min_bedrooms: Optional[int] = None,
    max_price: Optional[int] = None,
) -> list[dict[str, Any]]:
    def matches(record: dict[str, Any]) -> bool:
        if source and record["source"] != source.lower():
            return False
        if city and record.get("city", "").lower() != city.lower():
            return False
        if district and district.lower() not in (record.get("district") or "").lower():
            return False
        if property_type and record.get("property_type") != property_type.lower():
            return False
        if min_bedrooms is not None and (record.get("bedrooms") or 0) < min_bedrooms:
            return False
        if max_price is not None and (record.get("price") is None or record["price"] > max_price):
            return False
        return True

    return [record for record in records if matches(record)]
