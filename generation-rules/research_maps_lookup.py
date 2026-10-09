#!/usr/bin/env python3
"""Look up likely Google Maps business Place IDs for Seattle apartment buildings.

This script reads apartments.json and a Google Maps API key, then prints
candidate Places API (New) results for manual verification. It never edits the
building dataset. Run with --building-id for a focused lookup or --all to query
every building explicitly.
"""

from __future__ import annotations

import argparse
from datetime import date, datetime
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "apartments.json"
ENV_PATH = ROOT / ".env"
SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
FIELD_MASK = ",".join(
    (
        "places.id",
        "places.displayName",
        "places.formattedAddress",
        "places.types",
        "places.primaryType",
        "places.googleMapsUri",
    )
)


def read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        values[name.strip()] = value.strip().strip("\"'")
    return values


def get_api_key() -> str:
    configured = {**read_env_file(ENV_PATH), **os.environ}
    key = configured.get("GOOGLE_MAPS_API_KEY_PRIVATE") or configured.get(
        "GOOGLE_MAPS_API_KEY_PUBLIC"
    )
    if not key:
        raise RuntimeError(
            "Set GOOGLE_MAPS_API_KEY_PRIVATE or GOOGLE_MAPS_API_KEY_PUBLIC "
            "in the environment or .env."
        )
    return key


def normalize(value: str) -> str:
    value = value.lower().replace("&", " and ")
    value = re.sub(r"\bavenue\b", "ave", value)
    value = re.sub(r"\bstreet\b", "st", value)
    value = re.sub(r"\broad\b", "rd", value)
    value = re.sub(r"\bdrive\b", "dr", value)
    value = re.sub(r"\bwest\b", "w", value)
    value = re.sub(r"\beast\b", "e", value)
    value = re.sub(r"\bnorth\b", "n", value)
    value = re.sub(r"\bsouth\b", "s", value)
    value = re.sub(r"\bwashington\b", "wa", value)
    value = re.sub(r"\b(united states|usa)\b", " ", value)
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value).split())


def name_matches(candidate: str, building: dict[str, Any]) -> bool:
    candidate_norm = normalize(candidate)
    names = [building.get("name", ""), *building.get("previous_names", [])]
    return any(candidate_norm == normalize(name) for name in names if name)


def redact(value: Any, secret: str) -> Any:
    if isinstance(value, dict):
        return {key: redact(item, secret) for key, item in value.items()}
    if isinstance(value, list):
        return [redact(item, secret) for item in value]
    if isinstance(value, str) and secret:
        return value.replace(secret, "[REDACTED]")
    return value


def search(building: dict[str, Any], api_key: str, timeout: float) -> dict[str, Any]:
    query = f"{building['name']}, {building['address']}"
    body = {
        "textQuery": query,
        "regionCode": "US",
        "languageCode": "en",
        "pageSize": 5,
    }
    request = urllib.request.Request(
        SEARCH_URL,
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": FIELD_MASK,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as error:
        try:
            raw_error = redact(json.loads(error.read()), api_key)
            detail = raw_error.get("error", {}) if isinstance(raw_error, dict) else {}
            message = detail.get("message", "")
            status = detail.get("status", "HTTP_ERROR")
        except (ValueError, OSError):
            raw_error = {"message": "Could not parse API error response."}
            status, message = "HTTP_ERROR", "Could not parse API error response."
        return {
            "building_id": building.get("id"),
            "building_name": building.get("name"),
            "address": building.get("address"),
            "error": {"http_status": error.code, "status": status, "message": message},
            "_raw_api_response": raw_error,
        }
    except (urllib.error.URLError, TimeoutError) as error:
        return {
            "building_id": building.get("id"),
            "building_name": building.get("name"),
            "address": building.get("address"),
            "error": {"message": redact(str(error), api_key)},
            "_raw_api_response": {"transport_error": redact(str(error), api_key)},
        }

    candidates = []
    for place in payload.get("places", []):
        display_name = (place.get("displayName") or {}).get("text", "")
        formatted_address = place.get("formattedAddress", "")
        same_name = name_matches(display_name, building)
        same_address = normalize(formatted_address) == normalize(building["address"])
        candidates.append(
            {
                "gmaps_id": place.get("id"),
                "display_name": display_name,
                "formatted_address": formatted_address,
                "types": place.get("types", []),
                "primary_type": place.get("primaryType"),
                "google_maps_uri": place.get("googleMapsUri"),
                "name_matches": same_name,
                "address_matches": same_address,
                "exact_name_and_address": same_name and same_address,
            }
        )
    return {
        "building_id": building.get("id"),
        "building_name": building.get("name"),
        "address": building.get("address"),
        "candidates": candidates,
        "_raw_api_response": redact(payload, api_key),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument(
        "--building-id", action="append", help="Building id to look up; may repeat."
    )
    selection.add_argument(
        "--all", action="store_true", help="Query every building in apartments.json."
    )
    selection.add_argument(
        "--input",
        type=Path,
        help="Query every building object (or building id) in a JSON array or {\"buildings\": [...]} subset.",
    )
    parser.add_argument(
        "--limit", type=int, help="Limit the number of buildings queried (useful with --all)."
    )
    parser.add_argument(
        "--delay", type=float, default=0.1, help="Seconds between API calls (default: 0.1)."
    )
    parser.add_argument(
        "--timeout", type=float, default=20, help="Per-request timeout in seconds."
    )
    parser.add_argument(
        "--as-of", default=datetime.now(ZoneInfo("America/Los_Angeles")).date().isoformat(),
        help="Date recorded with the lookup (YYYY-MM-DD; defaults to today's Seattle date)."
    )
    parser.add_argument("--out", type=Path, help="Write results to this JSON file.")
    parser.add_argument(
        "--raw-out", type=Path, help="Write each raw Places API response beside the parsed results."
    )
    args = parser.parse_args()

    if args.limit is not None and args.limit < 0:
        parser.error("--limit must be zero or greater.")
    if args.delay < 0:
        parser.error("--delay must be zero or greater.")
    if args.timeout <= 0:
        parser.error("--timeout must be greater than zero.")
    try:
        checked_at = date.fromisoformat(args.as_of).isoformat()
    except ValueError:
        parser.error("--as-of must be a valid YYYY-MM-DD date.")

    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    buildings = data["buildings"]
    if args.all:
        selected = buildings
    elif args.input:
        subset = json.loads(args.input.read_text(encoding="utf-8"))
        entries = subset.get("buildings") if isinstance(subset, dict) else subset
        if not isinstance(entries, list):
            parser.error("--input must contain a JSON array or an object with a buildings array.")
        by_id = {building.get("id"): building for building in buildings}
        selected = []
        seen: set[str] = set()
        for entry in entries:
            if isinstance(entry, str):
                entry_id = entry
                building = by_id.get(entry_id)
            elif isinstance(entry, dict):
                entry_id = entry.get("id")
                building = entry if entry.get("name") and entry.get("address") else by_id.get(entry_id)
            else:
                parser.error("Every --input entry must be a building object or building id string.")
            if not entry_id or entry_id in seen:
                parser.error("--input entries must each have a unique, nonempty building id.")
            if not isinstance(building, dict) or not building.get("name") or not building.get("address"):
                parser.error(f"--input entry {entry_id!r} needs a known building id, name, and address.")
            selected.append(building)
            seen.add(entry_id)
    else:
        wanted = set(args.building_id)
        selected = [building for building in buildings if building.get("id") in wanted]
        found = {building.get("id") for building in selected}
        missing = wanted - found
        if missing:
            parser.error("Unknown building id(s): " + ", ".join(sorted(missing)))
    if args.limit is not None:
        selected = selected[: args.limit]

    api_key = get_api_key()
    results = []
    raw_results = []
    for index, building in enumerate(selected):
        if index and args.delay > 0:
            time.sleep(args.delay)
        query = f"{building['name']}, {building['address']}"
        result = search(building, api_key, args.timeout)
        raw_response = result.pop("_raw_api_response", {})
        result["text_query"] = query
        result["checked_at"] = checked_at
        results.append(result)
        raw_results.append(
            {
                "building_id": building.get("id"),
                "text_query": query,
                "checked_at": checked_at,
                "response": raw_response,
            }
        )

    output = json.dumps(results, ensure_ascii=False, indent=2)
    raw_output = json.dumps(raw_results, ensure_ascii=False, indent=2)
    if args.out:
        args.out.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)
    if args.raw_out:
        args.raw_out.write_text(raw_output + "\n", encoding="utf-8")
    return 1 if any(result.get("error") for result in results) else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(error, file=sys.stderr)
        raise SystemExit(2)
