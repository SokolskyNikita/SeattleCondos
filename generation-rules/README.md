# Dataset generation

This folder contains the research behind `apartments.json` and the rules and scripts used to update it.

| File | Why it exists |
|---|---|
| [amenity-consolidation-rules.json](amenity-consolidation-rules.json) | Machine-readable amenity mappings, naming policies and building eligibility rules. |
| [management-company-extraction-rules.md](management-company-extraction-rules.md) | Instructions for identifying managers and standardizing company names. |
| [pricing-extraction-rules.md](pricing-extraction-rules.md) | Instructions for researching rents and calculating prices, fees, concessions and fallback estimates. |
| [excluded-apartments.json](excluded-apartments.json) | Records 18 removals since commit `ce940cb`, with reasons, to prevent accidental re-addition. Check before adding buildings. |
| [pricing-research.json](pricing-research.json) | Per-building pricing evidence, assumptions, calculations and bedroom-price ratio inputs. |
| [google-maps-research.json](google-maps-research.json) | Reviewed business-listing Place ID research for all 337 buildings, including name/address discrepancies and unresolved candidates. |
| [research_maps_lookup.py](research_maps_lookup.py) | Read-only Google Places API lookup utility; returns candidates for manual verification and optional raw response evidence. |
| [research-audit.json](research-audit.json) | Historical research, source evidence, decisions and 71 archived exclusions, including the 18 above. |
| [amenity-processing-report.json](amenity-processing-report.json) | Generated counts, exclusions and ambiguity report matching the current rules and directory. |
| [process_amenities.py](process_amenities.py) | Applies amenity mappings while preserving original descriptions and details. |
| [test_process_amenities.py](test_process_amenities.py) | Checks normalization, detail preservation and safe writes. |

## Directory eligibility and exclusions

The active directory contains 337 buildings and 112 normalized amenity types. Ten buildings without usable prices and eight buildings with only one normalized amenity other than a gym were excluded. Buildings normally require at least two normalized amenities; a single Gym qualifies as an exception. Removed records and pricing evidence remain in the [exclusion audit](research-audit.json).

[Excluded apartments](excluded-apartments.json) records the 18 buildings removed on October 9, 2026, compared with commit `ce940cb`, with a reason and references to the chat or audit for each. Before adding buildings, check this registry by ID, current/former name, address and website. Do not automatically re-add matches, even under a new name or ID; reinstating a building requires an explicit user decision and an update to the registry. Newly found prices or amenities alone do not override the exclusion.

Original research and exclusion records are historical evidence and retain the names used when recorded.

## Shared update rules

These rules apply to both extraction guides and other dataset updates; field-specific requirements stay in the relevant guide.

### Concurrent writes

- For parallel research, give each researcher a separate result file or assigned records. One reviewer merges the results; researchers must not independently rewrite shared directory or audit files.
- Re-read the latest directory, research and audit files immediately before preparing a merge. Apply only authorized fields by stable building ID; never replace current data with an old full-file snapshot.
- Preserve unrelated fields, sources, notes, metadata and all existing audit sections. Append new decisions without rewriting historical evidence or restoring older labels over newer user-requested values.
- If buildings were added or removed during research, merge against the current list. Keep new entries and leave removed entries out. Follow the [exclusion policy](#directory-eligibility-and-exclusions) before adding records.
- Compare file contents or hashes immediately before saving. If they changed, re-read and recompute against the newest versions. Retain recoverable pre-change copies and use atomic replacement where possible; atomic replacement prevents partial files but does not prevent stale-snapshot data loss.
- For simultaneous writers, prefer a single writer or an agreed shared lock around read/merge/write. A brief hash check cannot guarantee protection against every race. Coordinate warnings with other chats when authorized by the user.
- If an overwrite is suspected, compare snapshots and audit history, identify lost fields and restore only confirmed authorized changes while keeping newer unrelated work. Do not replay an entire older directory.

### Shared validation

- Parse every edited JSON file, check required fields and source-support labels and verify unique building IDs and cross-file consistency.
- Compare IDs, order, membership, unrelated fields and historical audit sections against the immediate pre-write snapshot. Changes must stay within the authorized scope. Reconcile and report actual current counts; historical totals are not permanent targets.
- Review the task-specific diff against that snapshot. A diff against Git HEAD may include other chats' work. Run `git diff --check` and complete the relevant guide's field-specific checks.

## Google Maps listings

`google_maps` contains a verified Google Maps business listing for all 337 buildings, checked October 9, 2026. Use `google_maps.place_id` for the listing ID or `google_maps.url` for a direct link. `listing_name` and `listing_address` preserve Google's labels, which can differ from the property's name or street address (for example, a leasing-office entrance). The existing `location.place_id` comes from the original geocoding lookup. Use `google_maps` for the reviewed business listing. Axis Seattle has the same ID in both fields.

Seattle House uses the user-selected listing at its presentation center, while its building address remains unchanged. Stadium Place was renamed from The Wave at Stadium Place at the user's request and uses the shared community listing; its stable ID (`the-wave-at-stadium-place`) and existing Wave-specific research are retained. [Google Maps research](google-maps-research.json) records matches, address differences and user-confirmed listing selections. The [lookup script](research_maps_lookup.py) retrieves fresh candidates for manual review without modifying the directory. If a future record has `google_maps: null`, consumers should fall back to a name-and-address Maps search.

Run the commands below from the repository root.

To refresh a Google Maps candidate, configure `GOOGLE_MAPS_API_KEY_PRIVATE` in the environment or the ignored `.env` file and run:

```sh
python3 generation-rules/research_maps_lookup.py --building-id ion-queen-anne --as-of 2026-10-09
```

Use the actual research date for `--as-of`. `--input subset.json` accepts an array of building IDs or building objects; `--all` queries the whole directory. `--out` saves parsed candidates and `--raw-out` optionally saves API responses. Queries use Places API Text Search (New) with name and address fields. Normal Google API charges may apply. An exact text match is only a review aid: reject address-only types, check current/former property names and corroborate alternate addresses through official property links or Places Details website URLs. Store accepted business listings in `google_maps`; preserve `location` as geocoding evidence. Record unresolved candidates in the research file and leave `google_maps` null. Code that builds Maps links must use `google_maps.url` or `google_maps.place_id` for the business listing.

## One-bedroom pricing

See the [pricing extraction rules](pricing-extraction-rules.md) for the field definition, source policy, fee and concession calculations, lease assumptions and extrapolation method. The [research snapshot](pricing-extraction-rules.md#research-snapshot) describes the existing estimates and links to their evidence.

## Amenity normalization

Amenity names are processed with the reusable [consolidation rules](amenity-consolidation-rules.json). `amenities` contains sorted, deduplicated feature labels. `amenities_original` preserves the source descriptions and is the input for subsequent runs; edit that field when updating an existing building's amenity evidence. For a new building, supply its initial descriptions in `amenities`. `amenity_details` links each retained label to its original descriptions, preserving hours, fees, seasonal or off-site access, quantities and shared-room relationships. Optional `related_details` keeps extra context only when evidence already supports the parent amenity; for example, 24/7 lobby staffing does not establish 24/7 concierge availability. Several labels can describe the same room. Do not use the label count as an amenity score. `amenity_review_notes` records conservative interpretations of ambiguous or withheld names.

The rules file contains the naming policies, exclusions, canonical labels and exact reviewed source-name mappings. An empty mapping excludes a source from the main list; useful parts of combined descriptions are retained. Unknown names stop processing before any writes. To expand the rules, add the normalized source name to `mappings`, register any new label in `canonical_amenities`, add an ambiguity note if needed and update `rules_version` and `updated_at`. The processor creates and owns `amenities_original`, `amenity_details` and `amenity_review_notes`; other building fields are preserved. Original research logs remain unchanged.

The approved compact names and category merges are recorded in `compact_label_review` in the rules file. Gym includes general fitness studios; Movie theater includes media lounges and screening areas; Parking includes garages, covered parking and carports. Coworking includes business centers; Shared kitchen includes catering and demonstration kitchens; Climbing wall includes bouldering; Sauna includes steam rooms. Keep outdoor and shared dining descriptions as details of BBQs and kitchens only when the evidence also supports those amenities. Original descriptions preserve facility types, equipment and access restrictions.

The approved rare-amenity review is recorded in the rules file's `rare_amenity_review` section. It removes vague or low-priority standalone labels, keeps minor components as details of larger facilities and retains useful distinctive amenities. Rarity alone is not an exclusion rule. `detail_attachments` can associate source context with existing parent labels without creating unsupported amenities.

```sh
python3 generation-rules/process_amenities.py          # Preview counts without writing
python3 generation-rules/process_amenities.py --write  # Apply rules and update the report
python3 generation-rules/process_amenities.py --check  # Check saved data/report against the rules
python3 -B -m unittest discover -s generation-rules -p 'test_*.py' -v
```

Running with `--write` creates `generation-rules/amenity-processing-report.json`, listing exclusions, ambiguous names and buildings with no retained amenities. Processing never removes a building; empty lists require a separate inclusion decision. `--check` requires the generated report.

Commit the rules, updated directory and generated report together after running `--write`.
