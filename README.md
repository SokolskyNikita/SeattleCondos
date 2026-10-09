# Seattle-area rental apartments

Browse the data in a neat, easy-to-use interface at [Seattle Apartments](https://sokolsky.me/apartments/seattle/).

Prefer the raw data? Open the [apartment directory (JSON)](apartments.json).

[generation-rules/](generation-rules/README.md) contains metadata, research, and rules documenting how the dataset was generated, for use in future updates.

`google_maps` contains a verified Google Maps business listing for all 337 buildings, checked October 9, 2026. Use `google_maps.place_id` for the listing ID or `google_maps.url` for a direct link. `listing_name` and `listing_address` preserve Google's labels, which can differ from the property's name or street address (for example, a leasing-office entrance). The existing `location.place_id` remains the original geocoding-sourced field; use `google_maps` for reviewed business-listing metadata. Axis Seattle's verified listing ID happens to match its original geocoding ID.

Seattle House uses the user-selected listing at its presentation center, while its building address remains unchanged. Stadium Place was renamed from The Wave at Stadium Place at the user's request and uses the shared community listing; its stable ID (`the-wave-at-stadium-place`) and existing Wave-specific research are retained. [Google Maps research](generation-rules/google-maps-research.json) records matches, address differences, and user-confirmed listing selections. The [lookup script](generation-rules/research_maps_lookup.py) retrieves fresh candidates for manual review without modifying the directory. If a future record has `google_maps: null`, consumers should fall back to a name-and-address Maps search.

[Excluded apartments](generation-rules/excluded-apartments.json) records the 18 buildings removed on October 9, 2026, compared with commit `ce940cb`, with a reason and chat/audit provenance for each. Before adding buildings, check this registry by ID, current/former name, address and website. Do not automatically re-add matches, even under a new name or ID; reinstatement requires an explicit user decision and a documented registry update.

Each building has an `approx_1br_monthly_usd` field: an approximate effective monthly cost in USD for an unrestricted one-bedroom, rounded to the nearest $10. Prices were researched on October 9, 2026, using official property websites first and Zillow/Redfin as backups.

The estimate includes disclosed mandatory recurring fees, nonrefundable move-in/application fees for one adult, and applicable standard rent concessions. It averages costs over the quoted lease term, using a documented 12-month assumption when an annual or longer-term quote is unavailable. Refundable deposits and optional expenses are excluded; undisclosed charges cannot be included. An explicitly labeled open or urban one-bedroom may be the lowest-priced option.

When no usable one-bedroom quote exists, available studio or two-bedroom rents are converted using median bedroom-price ratios calculated only from Seattle buildings in the original pricing-research cohort. These historical ratios and existing estimates are preserved when later eligibility filters remove buildings. These are hypothetical one-bedroom estimates, not available-unit quotes. [Pricing research and calculations](generation-rules/pricing-research.json) include every source, fee, promotion, lease assumption, extrapolation, and ratio input.

The active directory contains 337 buildings and 112 normalized amenity types. Ten buildings without usable prices and eight buildings with only one normalized amenity other than a gym were excluded. Buildings normally require at least two normalized amenities; a single Gym qualifies as an exception. Removed records and pricing evidence remain in the [exclusion audit](generation-rules/research-audit.json).

Amenity names are processed with the reusable [consolidation rules](generation-rules/amenity-consolidation-rules.json). `amenities` contains sorted, deduplicated feature labels. `amenities_original` preserves the source descriptions and is the input for subsequent runs; edit that field when updating an existing building's amenity evidence. For a new building, supply its initial descriptions in `amenities`. `amenity_details` links each retained label to its original descriptions, preserving hours, fees, seasonal or off-site access, quantities, and shared-room relationships. Optional `related_details` preserves associated context only when a parent amenity is independently established; for example, 24/7 lobby staffing does not establish 24/7 concierge availability. Labels describe features, not separate rooms, and their count is not an amenity score. `amenity_review_notes` records conservative interpretations of ambiguous or withheld names.

The rules file contains the naming policies, exclusions, canonical labels, and exact reviewed source-name mappings. An empty mapping excludes a source from the main list; useful components of compound descriptions are retained. Unknown names stop processing before any writes. To expand the rules, add the normalized source name to `mappings`, register any new label in `canonical_amenities`, add an ambiguity note if needed, and update `rules_version` and `updated_at`. The processor creates and owns `amenities_original`, `amenity_details`, and `amenity_review_notes`; other building fields are preserved. Original research logs remain unchanged.

The approved compact names and category merges are recorded in `compact_label_review` in the rules file. Gym includes general fitness studios; Movie theater includes media lounges and screening areas; Parking includes garages, covered parking and carports. Coworking includes business centers; Shared kitchen includes catering and demonstration kitchens; Climbing wall includes bouldering; Sauna includes steam rooms. Outdoor and shared dining are retained as details of independently established BBQs and kitchens. Original descriptions preserve facility types, equipment and access restrictions.

The approved rare-amenity review is recorded in the rules file's `rare_amenity_review` section. It removes vague or low-priority standalone labels, keeps minor components as details of larger facilities, and retains useful distinctive amenities. Rarity alone is not an exclusion rule. `detail_attachments` can associate source context with existing parent labels without creating unsupported amenities.

```sh
python3 generation-rules/process_amenities.py          # Preview counts without writing
python3 generation-rules/process_amenities.py --write  # Apply rules and update the report
python3 generation-rules/process_amenities.py --check  # Check saved data/report against the rules
python3 -B -m unittest discover -s generation-rules -p 'test_*.py' -v
```

Running with `--write` creates `generation-rules/amenity-processing-report.json`, listing exclusions, ambiguous names, and buildings with no retained amenities. Processing never removes a building; empty lists require a separate inclusion decision. `--check` requires the generated report.
