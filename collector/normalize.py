"""Normalize public listing facts while deliberately omitting contact data."""

import re


def _number(value):
    if not value:
        return None
    digits = re.sub(r"[^0-9.]", "", value.replace(",", ""))
    return float(digits) if digits else None


def _integer(value):
    number = _number(value)
    return int(number) if number is not None else None


def _location_parts(location):
    parts = [part.strip() for part in location.split(",") if part.strip()]
    return {
        "district": parts[0] if parts else None,
        "city": parts[-1] if parts else None,
        "location_text": location or None,
    }


def normalize_wasalt_listing(raw, captured_at):
    """Return chatbot-safe facts from an already-public Wasalt property page."""
    price = _number(raw.get("price_text", ""))
    area_sqm = _number(raw.get("area_text", ""))
    record = {
        "source": "wasalt",
        "source_url": raw["source_url"],
        "source_record_id": raw["source_url"].rstrip("/").split("-")[-1],
        "record_type": "listing",
        "title": raw.get("title") or None,
        "country": "Saudi Arabia",
        "property_type": (raw.get("title") or "").split(" ", 1)[0].lower() or None,
        "transaction_type": "sale",
        "price": int(price) if price is not None else None,
        "currency": "SAR" if price is not None else None,
        "area_sqm": area_sqm,
        "bedrooms": _integer(raw.get("bedrooms_text", "")),
        "description": raw.get("description") or None,
        "captured_at": captured_at,
    }
    record.update(_location_parts(raw.get("location", "")))
    return record
