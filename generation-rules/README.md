# Dataset generation

Rules, research, and tooling that explain how the dataset was generated and support future updates.

The current directory has **337 buildings and 112 amenity types**. The rules file records approved compact labels, category merges, and conditional dining-detail attachments in `compact_label_review`. Original research and exclusion records are historical evidence and retain the names used when recorded.

| File | Why it exists |
|---|---|
| [amenity-consolidation-rules.json](amenity-consolidation-rules.json) | Machine-readable amenity mappings, naming policies, and building eligibility rules. |
| [management-company-extraction-rules.md](management-company-extraction-rules.md) | Instructions for identifying managers and standardizing company names. |
| [pricing-extraction-rules.md](pricing-extraction-rules.md) | Instructions for researching rents and calculating prices, fees, concessions, and fallback estimates. |
| [excluded-apartments.json](excluded-apartments.json) | Records 18 removals since commit `ce940cb`, with reasons, to prevent accidental re-addition. Check before adding buildings. |
| [pricing-research.json](pricing-research.json) | Per-building pricing evidence, assumptions, calculations, and bedroom-price ratio inputs. |
| [google-maps-research.json](google-maps-research.json) | Reviewed business-listing Place ID research for all 337 buildings, including name/address discrepancies and unresolved candidates. |
| [research_maps_lookup.py](research_maps_lookup.py) | Read-only Google Places API lookup utility; returns candidates for manual verification and optional raw response evidence. |
| [research-audit.json](research-audit.json) | Historical research, source evidence, decisions, and 71 archived exclusions, including the 18 above. |
| [amenity-processing-report.json](amenity-processing-report.json) | Generated counts, exclusions and ambiguity report matching the current rules and directory. |
| [process_amenities.py](process_amenities.py) | Applies amenity mappings while preserving original descriptions and details. |
| [test_process_amenities.py](test_process_amenities.py) | Checks normalization, detail preservation, and safe writes. |

Regenerate the directory and report with `python3 generation-rules/process_amenities.py --write` after changing the mappings. Commit the rules, updated directory and generated report together. Verify them with `python3 generation-rules/process_amenities.py --check`; the check requires this report.

To refresh a Google Maps candidate, configure `GOOGLE_MAPS_API_KEY_PRIVATE` in the environment or the ignored `.env` file and run:

```sh
python3 generation-rules/research_maps_lookup.py --building-id ion-queen-anne --as-of 2026-10-09
```

Use the actual research date for `--as-of`. `--input subset.json` accepts an array of building IDs or building objects; `--all` queries the whole directory. `--out` saves parsed candidates and `--raw-out` optionally saves API responses. Queries use Places API Text Search (New), including name/address fields, and may incur normal Google API charges. An exact text match is only a review aid: reject address-only types, check current/former property names, and corroborate alternate addresses through official property links or Places Details website URLs. Store accepted business listings in `google_maps`; preserve `location` as geocoding evidence. Record unresolved candidates in the research file and leave `google_maps` null. Existing map-link consumers must switch to `google_maps.url` or `google_maps.place_id` to use the business listings.
