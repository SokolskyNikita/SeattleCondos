#!/usr/bin/env python3
"""Apply reviewed, names-only amenity mappings without guessing new meanings."""

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile


ROOT = Path(__file__).resolve().parent


def normalize_name(value):
    """This order is part of amenity-consolidation-rules.json's public format."""
    return re.sub(r"\s+", " ", value.strip().rstrip(".")).casefold()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def validate_rules(rules):
    if rules.get("schema_version") != 1:
        raise ValueError("Unsupported amenity rules schema_version")
    expected = ["trim", "remove_trailing_periods", "collapse_whitespace", "casefold"]
    if rules.get("normalization") != expected:
        raise ValueError("Unsupported name normalization; update the processor explicitly")
    canonical = rules["canonical_amenities"]
    if len(canonical) != len(set(canonical)) or not all(isinstance(x, str) and x for x in canonical):
        raise ValueError("Canonical amenities must be unique nonempty strings")
    for source, names in rules["mappings"].items():
        if normalize_name(source) != source:
            raise ValueError(f"Mapping key is not normalized: {source!r}")
        if not isinstance(names, list) or len(names) != len(set(names)):
            raise ValueError(f"Mapping must be a unique list: {source!r}")
        if any(name not in canonical for name in names):
            raise ValueError(f"Unknown canonical label in mapping: {source!r}")
    if set(rules["review_notes"]) - set(rules["mappings"]):
        raise ValueError("Review notes must refer to existing mapping keys")
    for source, attachment in rules.get("detail_attachments", {}).items():
        if source not in rules["mappings"]:
            raise ValueError(f"Detail attachment must refer to a mapping key: {source!r}")
        parents = attachment.get("attach_to_if_present", [])
        if not parents or any(parent not in canonical for parent in parents):
            raise ValueError(f"Detail attachment has invalid parent amenities: {source!r}")
        if not isinstance(attachment.get("note"), str) or not attachment["note"].strip():
            raise ValueError(f"Detail attachment needs an explanatory note: {source!r}")


def process(data, rules):
    """Return new data/report, or fail before writing if any source is unmapped."""
    validate_rules(rules)
    result = deepcopy(data)
    previously_generated = "amenity_consolidation" in data["metadata"]["methodology"]
    if not previously_generated:
        for building in result["buildings"]:
            collisions = {"amenities_original", "amenity_details", "amenity_review_notes"} & set(building)
            if collisions:
                raise ValueError(f"Refusing to overwrite existing, unowned fields for {building['id']}: {sorted(collisions)}")
    mappings = rules["mappings"]
    originals = {}
    unknown = {}
    for building in result["buildings"]:
        building_id = building["id"]
        if building_id in originals:
            raise ValueError(f"Duplicate building id: {building_id}")
        sources = building.get("amenities_original", building["amenities"])
        if not isinstance(sources, list) or not all(isinstance(x, str) and x.strip() for x in sources):
            raise ValueError(f"Invalid amenity source list: {building_id}")
        originals[building_id] = sources
        for source in sources:
            if normalize_name(source) not in mappings:
                unknown.setdefault(source, []).append(building_id)
    if unknown:
        raise ValueError("Unmapped amenity names; add reviewed mappings before applying:\n"
                         + json.dumps(unknown, ensure_ascii=False, indent=2))

    exclusions = Counter()
    empty_buildings = []
    ambiguous_buildings = []
    canonical_counts = Counter()
    source_names = set()
    before_count = 0
    after_count = 0
    expanded_count = 0
    duplicates_removed = 0
    for building in result["buildings"]:
        sources = originals[building["id"]]
        details = {}
        notes = []
        local_expanded = 0
        for source in sources:
            key = normalize_name(source)
            source_names.add(key)
            names = mappings[key]
            local_expanded += len(names)
            if not names:
                exclusions[key] += 1
            for name in names:
                source_list = details.setdefault(name, [])
                if source not in source_list:
                    source_list.append(source)
            if key in rules["review_notes"]:
                notes.append({"source": source, "reason": rules["review_notes"][key]})
        names = sorted(details, key=str.casefold)
        building["amenities"] = names
        building["amenities_original"] = list(sources)
        building["amenity_details"] = {name: {"source_descriptions": details[name]} for name in names}
        # Attach context only after all actual features have been established.
        # A staffed lobby, for example, must not create a Concierge label.
        for source in sources:
            attachment = rules.get("detail_attachments", {}).get(normalize_name(source))
            if attachment:
                for parent in attachment["attach_to_if_present"]:
                    if parent in building["amenity_details"]:
                        related = building["amenity_details"][parent].setdefault("related_details", [])
                        item = {"source_description": source, "note": attachment["note"]}
                        if item not in related:
                            related.append(item)
        building.pop("amenity_review_notes", None)
        if notes:
            building["amenity_review_notes"] = notes
            ambiguous_buildings.append({"id": building["id"], "name": building["name"], "notes": notes})
        if not names:
            empty_buildings.append({"id": building["id"], "name": building["name"],
                                    "reason": "No retained amenity names; review inclusion separately. Building retained."})
        before_count += len(sources)
        after_count += len(names)
        expanded_count += local_expanded
        duplicates_removed += local_expanded - len(names)
        canonical_counts.update(names)

    rule_hash = hashlib.sha256(json_bytes(rules)).hexdigest()
    summary = {
        "buildings_processed": len(result["buildings"]),
        "original_amenity_entries": before_count,
        "unique_original_source_names": len({source for sources in originals.values() for source in sources}),
        "unique_normalized_source_names": len(source_names),
        "processed_amenity_entries": after_count,
        "unique_canonical_amenities_in_use": len(canonical_counts),
        "fully_excluded_source_entries": sum(exclusions.values()),
        "fully_excluded_unique_source_names": len(exclusions),
        "expanded_feature_mentions_before_deduplication": expanded_count,
        "duplicate_feature_mentions_removed": duplicates_removed,
        "buildings_with_ambiguous_names": len(ambiguous_buildings),
        "buildings_without_retained_amenities": len(empty_buildings),
        "buildings_removed": 0,
        "unmapped_source_names": 0,
    }
    result["metadata"]["methodology"]["amenity_consolidation"] = {
        "rules_file": "generation-rules/amenity-consolidation-rules.json",
        "rules_version": rules["rules_version"],
        "rules_sha256": rule_hash,
        "processed_at": rules["updated_at"],
        "report_file": "generation-rules/amenity-processing-report.json",
        "description": "Names-only normalization; no building research or inclusion changes. amenities contains deduplicated feature labels, not room counts or an amenity score. amenities_original is the reusable source of truth; amenity_details links each label to original descriptions, retaining shared-space relationships, quantities and all qualifiers. Ambiguous names remain conservative and are flagged.",
        "counts": summary,
    }
    report = {
        "schema_version": 1,
        "processed_at": rules["updated_at"],
        "rules_version": rules["rules_version"],
        "rules_sha256": rule_hash,
        "original_names_sha256": hashlib.sha256(json_bytes(originals)).hexdigest(),
        "summary": summary,
        "fully_excluded_source_names": dict(sorted(exclusions.items())),
        "canonical_amenity_building_counts": dict(sorted(canonical_counts.items(), key=lambda item: item[0].casefold())),
        "inclusion_review": empty_buildings,
        "ambiguous_name_review": ambiguous_buildings,
    }
    return result, report


def write_atomic(path, content):
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".", delete=False) as handle:
        temp = Path(handle.name)
        try:
            handle.write(content)
            handle.flush()
        except BaseException:
            temp.unlink(missing_ok=True)
            raise
    try:
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)


def write_outputs(outputs):
    """Stage both outputs first; restore earlier files if a later replace fails."""
    staged = []
    committed = []
    try:
        for path, content in outputs:
            original = path.read_bytes() if path.exists() else None
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".", delete=False) as handle:
                temp = Path(handle.name)
                staged.append((path, temp, original, content))
                handle.write(content)
        for path, temp, original, content in staged:
            current = path.read_bytes() if path.exists() else None
            if current != original:
                raise ValueError(f"Output changed while preparing the update: {path}")
            temp.replace(path)
            committed.append((path, original, content))
    except BaseException:
        for path, original, content in reversed(committed):
            if path.read_bytes() == content:
                if original is None:
                    path.unlink()
                else:
                    write_atomic(path, original)
        raise
    finally:
        for _, temp, _, _ in staged:
            temp.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT.parent / "apartments.json")
    parser.add_argument("--rules", type=Path, default=ROOT / "amenity-consolidation-rules.json")
    parser.add_argument("--report", type=Path, default=ROOT / "amenity-processing-report.json")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="Apply mappings and save the report (default is a dry run)")
    mode.add_argument("--check", action="store_true", help="Fail if saved data or report differs from current rules")
    args = parser.parse_args()
    try:
        if len({args.input.resolve(), args.rules.resolve(), args.report.resolve()}) != 3:
            raise ValueError("Input, rules, and report must be three different files")
        input_bytes = args.input.read_bytes()
        rules = json.loads(args.rules.read_text())
        result, report = process(json.loads(input_bytes), rules)
        expected = [(args.input, json_bytes(result)), (args.report, json_bytes(report))]
        if args.check:
            stale = [str(path) for path, content in expected if not path.exists() or path.read_bytes() != content]
            if stale:
                raise ValueError("Generated files need updating: " + ", ".join(stale))
        elif args.write:
            if args.input.read_bytes() != input_bytes:
                raise ValueError("Input changed while processing; no output written. Rerun on the current data.")
            write_outputs(expected)
        print(json.dumps(report["summary"], indent=2))
        return 0
    except (ValueError, KeyError, OSError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
