#!/usr/bin/env python3
"""Fetch current ratings for verified Maps listings without editing the directory."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import json
from pathlib import Path
import time
import urllib.error
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

from research_maps_lookup import DATA_PATH, get_api_key, redact


FIELD_MASK = "id,displayName,rating,userRatingCount"


def lookup(building, api_key):
    listing = building.get("google_maps") or {}
    place_id = listing.get("place_id")
    result = {
        "id": building["id"],
        "place_id": place_id,
        "source_url": listing.get("url"),
    }
    if not place_id:
        return {**result, "error": "No verified Google Maps listing."}
    request = urllib.request.Request(
        "https://places.googleapis.com/v1/places/"
        + urllib.parse.quote(place_id, safe=""),
        headers={"X-Goog-Api-Key": api_key, "X-Goog-FieldMask": FIELD_MASK},
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.load(response)
            if payload.get("id") != place_id:
                raise ValueError("Returned Place ID differs from the verified listing.")
            rating = payload.get("rating")
            count = payload.get("userRatingCount")
            if rating is not None and (
                type(rating) not in (int, float) or not 1 <= rating <= 5
            ):
                raise ValueError("Invalid rating in Places response.")
            if count is not None and (type(count) is not int or count < 0):
                raise ValueError("Invalid review count in Places response.")
            return {
                **result,
                "rating": rating,
                "review_count": count,
                "checked_at": datetime.now(ZoneInfo("America/Los_Angeles")).isoformat(timespec="seconds"),
                "raw_response": payload,
            }
        except urllib.error.HTTPError as error:
            message = f"Places API HTTP {error.code}"
            retry = error.code in (429, 500, 502, 503, 504)
        except (urllib.error.URLError, TimeoutError) as error:
            message = redact(str(error), api_key)
            retry = True
        except ValueError as error:
            message = str(error)
            retry = False
        if not retry or attempt == 2:
            return {**result, "error": message}
        time.sleep(2 ** attempt)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--all", action="store_true")
    selection.add_argument("--building-id", action="append")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    buildings = json.loads(DATA_PATH.read_text())["buildings"]
    if args.building_id:
        unknown = set(args.building_id) - {b["id"] for b in buildings}
        if unknown:
            parser.error(f"Unknown building IDs: {sorted(unknown)}")
        buildings = [b for b in buildings if b["id"] in args.building_id]
    api_key = get_api_key()
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda b: lookup(b, api_key), buildings))
    errors = sum("error" in r for r in results)
    evidence = {
        "source": "Google Places API (New), Place Details",
        "source_documentation": "https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places",
        "field_mask": FIELD_MASK,
        "methodology": "Fetch the existing verified google_maps.place_id for each building. rating is Google's 1–5 aggregate score; review_count is userRatingCount (reviews with or without text). Missing API values remain null, never inferred as zero. Listing selections and unrelated building fields are unchanged.",
        "counts": {
            "buildings": len(results),
            "successful": len(results) - errors,
            "errors": errors,
            "with_rating": sum(r.get("rating") is not None for r in results),
            "with_review_count": sum(r.get("review_count") is not None for r in results),
        },
        "results": results,
    }
    args.out.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(evidence["counts"]))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
