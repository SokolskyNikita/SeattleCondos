# Pricing extraction rules

**Schema version:** 1

**Updated at:** 2026-10-09

**Purpose:** Reusable rules for researching, calculating and maintaining approximate monthly one-bedroom apartment prices for this directory.

**Basis:** The user's pricing, source, extrapolation, promotion and removal instructions, plus the documented working assumptions established during the research. Apply any newer user instructions before these defaults.

## Files

**Active directory:** apartments.json

**Active pricing research:** generation-rules/pricing-research.json

**Exclusion and historical audit:** generation-rules/research-audit.json

**Exclusion registry:** generation-rules/excluded-apartments.json

## Output

**Field:** approx_1br_monthly_usd

**Currency:** USD

**Meaning:** Approximate effective monthly cost of an unrestricted whole one-bedroom apartment over the initial pricing period, including disclosed applicable fees and standard concessions.

**Final value type:** positive number

**Round to nearest USD:** 10

**Temporary missing value:** N/A

**Final missing value policy:** As a last resort, remove buildings still lacking usable pricing from the active directory and active pricing research, while preserving their records and reasons in the exclusion audit.

## Default assumptions

**Adult applicants:** 1

**Pets:** 0

**Optional parking:** false

**Optional storage:** false

**Unquoted lease months:** 12

**Entry level price:** Prefer the lowest supported effective cost among eligible available one-bedroom options, rather than a building-wide average.

**Move in date:** No fixed user move-in date is assumed. A future available unit may be used, but any promotion deadline must be compatible with that unit's availability.

**Disclosure:** Record assumptions and missing costs per building; an estimate is not a guaranteed leasing quote.

## Calculation

**General formula:** `effective_monthly_usd = (total_rent_over_pricing_period + total_applicable_mandatory_fees_over_pricing_period - eligible_concessions_not_already_included) / pricing_period_months`

**Constant monthly price formula:** `effective_monthly_usd = ((monthly_rent_basis_usd + mandatory_monthly_fees_not_already_included_usd) * lease_months + mandatory_nonmonthly_fees_total_usd - concession_total_not_already_included_usd) / lease_months`

**Nonmonthly fees:** Count required nonrefundable application, administrative, move-in and other nonmonthly charges due during the pricing period. For annual or other periodic charges, use their disclosed charging schedule over that period.

**Free months credit:** `contractual_monthly_base_rent_usd * free_months`

**Free weeks credit:** `contractual_monthly_base_rent_usd * free_weeks * 12 / 52`

**Rounding:** Keep full precision during calculations and ratio estimation. Retain cents in the research audit; round only the final directory field to the nearest $10.

## Rules

### 1. Research each building

**Rule ID:** `research_each_building`

Research every building in the current active list and verify property identity.

- Read the latest directory at the start of each run. Match the name, address, former names and official website before accepting a listing.
- Use the actual research date for availability, offer-expiration checks and checked_at fields; do not reuse this rules file's updated_at as the research date.
- Do not substitute a nearby property, an individual condo at another address, or an unrelated similarly named building.

### 2. Source priority

**Rule ID:** `source_priority`

Prefer the building's own website; use Zillow or Redfin as secondary pricing sources.

- Official sources include property and operator websites and leasing platforms linked by them, such as their availability widgets, resident-management listings or floorplan feeds.
- Check official availability, the homepage or specials page, and linked fee disclosures. Follow unit detail pages and embedded leasing tools when the landing page omits prices.
- Use current Zillow or Redfin listings when official pricing is inaccessible, missing or insufficiently specific. Document why the fallback was needed and any conflicting official evidence.
- Do not use other rental aggregators, outside market averages, Zestimate-style estimates or unrelated listings as rent inputs. Search results may help locate an allowed source.

### 3. Verify live evidence

**Rule ID:** `verify_live_evidence`

Resolve important price and availability conflicts with current page evidence.

- Search-index snippets and cached pages can contain older rents or promotions. Refresh the actual allowed-source page before finalizing a conflicting quote or an N/A decision.
- Use BrightData MCP, the available browser, or local Google Chrome depending on which successfully exposes the public listing and its terms.
- An unavailable widget or a page that fails to render prices does not prove that the property has no vacancies.
- A generic zero-availability heading may conflict with detailed active unit cards; inspect those cards and a backup source before discarding all pricing. Record unresolved contradictions.

### 4. Available eligible whole apartment

**Rule ID:** `available_eligible_whole_apartment`

Use current unrestricted whole-apartment asking rents with an identifiable bedroom type.

- An active listing with an earliest availability date in the past is still usable. A past date alone is not evidence that the listing is unavailable.
- Exclude explicitly unavailable, historical, off-market, waitlist-only and price-on-request units as direct price inputs.
- Exclude MFTE, ARCH, IZ and other income-restricted or otherwise eligibility-restricted units from the general-market estimate.
- Never treat shared-room or per-resident student installments as whole-apartment rent. Use them only if a current whole-apartment cost and its payment period can actually be established; otherwise find a comparable whole-unit quote or continue toward the missing-price fallback.
- A general community price range or all-bedroom 'from' price is not automatically a one-bedroom or studio quote. Establish the bedroom type; flag any defensible inference as low confidence.

### 5. Select one bedroom

**Rule ID:** `select_one_bedroom`

Find the lowest supported effective one-bedroom cost under the stated assumptions.

- Prefer a priced available unit. An official available floorplan starting price is acceptable when individual unit detail is inaccessible; record the limitation.
- An open or urban layout explicitly labeled one-bedroom can be used, but identify that layout in the audit. Do not silently relabel a studio as a one-bedroom.
- A one-bedroom plus den may be used when it is the available one-bedroom option; identify it.
- Compare a slightly higher base-rent unit with a verified promotion when it could be cheaper after concessions and fees. Do not assume the lowest base rent always yields the lowest effective cost.
- Also collect available studio and two-bedroom prices, preserving their quote basis, so this list can supply its own extrapolation ratios.

### 6. Lease term and denominator

**Rule ID:** `lease_term_and_denominator`

Use first-period total cost divided by the corresponding number of months, and choose the cheapest supported lease option.

- Normally calculate the first 12 months divided by 12.
- If the applicable quote or concession requires 13, 14, 15, 16, 18 or another longer lease, calculate costs over that actual term and divide by that term's months.
- Compare available quoted terms of at least 12 months, including cheaper longer-term rents and their eligible concessions, and choose the lowest effective monthly cost.
- Do not invent a longer-term rent by extending a rate quoted for a different term merely to qualify for a larger promotion.
- If the term is not disclosed, assume 12 months and mark that assumption.
- Do not mark a building N/A solely because only a shorter lease is priced. As a low-confidence fallback, an annual approximation may assume its quoted monthly rate continues for 12 months, explicitly noting that renewal pricing is unverified. Do not apply an unverified annual or longer-term promotion to that assumption.

### 7. Mandatory fees

**Rule ID:** `mandatory_fees`

Include every disclosed, quantifiable fee applicable under the stated household and lease assumptions.

- Include required recurring charges such as utility administration, trash, pest control, technology, connectivity, package, amenity and district charges when disclosed as mandatory.
- Include required nonrefundable application fees for one adult and administrative, move-in or other charges due during the pricing period.
- Inspect unit-specific fee calculators and property fee guides; charges may be missing from the main floorplan page.
- Include numerical utility estimates published by the property, labeled as estimates that may vary with usage. Do not invent a value for unquantified utilities or fees.
- If using another unit's property-wide fee schedule, confirm or explicitly assume applicability to the selected unit. Record uncertain or conditional fee applicability.
- A zero fee aggregate means no additional applicable amount was established; it does not certify that the property has no other charges.

### 8. Exclude non costs and optional charges

**Rule ID:** `exclude_non_costs_and_optional_charges`

Distinguish actual required costs from refundable, credited, optional or contingent payments.

- Exclude refundable security deposits.
- Exclude holding deposits or prepaid payments credited toward rent or already-counted move-in costs; count only any clearly nonrefundable, uncredited portion.
- Exclude optional parking, storage, pet, furnishing and similar charges under the default assumptions.
- Do not automatically include a liability waiver or insurance substitute charged only when a renter fails to provide qualifying coverage. State the coverage assumption and any unpriced insurance cost.
- Do not infer that a fee applies merely because it appears in a regional operator schedule. Respect property, billing-system and other applicability conditions; document unresolved conditions instead of silently assuming them.

### 9. Standard promotions

**Rule ID:** `standard_promotions`

Include applicable ordinary leasing concessions, but exclude special financial-product or personal-eligibility deals.

- Standard free months, free weeks, rent credits and look-and-lease or prompt-application offers can be included when compatible with the selected unit, lease and timing.
- Exclude discounts requiring opening or using a specific credit card or similar financial product. Exclude employer, military, referral or other special personal-eligibility deals not established for the renter.
- Exclude expired offers and offers whose move-in deadline precedes the selected unit's availability.
- Do not combine offers unless their terms support combining them. A fee waiver reduces the relevant fee; do not also count it as a second rent credit.
- Free rent normally offsets base rent only. Continue charging mandatory fees during free-rent periods unless the offer explicitly waives them.
- Non-rent gifts, such as transit passes or event tickets, do not reduce the apartment cost unless they replace a separately counted required housing charge.

### 10. Uncertain promotion eligibility

**Rule ID:** `uncertain_promotion_eligibility`

Make promotion eligibility and assumptions visible instead of presenting an advertised maximum as guaranteed.

- Prefer exact selected-unit and selected-term offers.
- Do not deduct a generic 'up to' or select-unit offer when the chosen unit has no supporting eligibility evidence.
- A currently advertised broad offer, or a selected unit explicitly marked for an offer without an exact credit, may support an approximate assumption. If using the broad offer or maximum, state that assumption, reduce confidence and retain the undiscounted inputs.
- Record unapplied offers and the reason for excluding them. Do not invent an offer amount, deadline or lease condition.

### 11. Avoid double counting

**Rule ID:** `avoid_double_counting`

Keep base rent, total monthly price and advertised effective rent distinct.

- If a listing says Total Monthly Leasing Price or that required monthly fees are included, do not add those fees again.
- If an advertised rent already incorporates free weeks or months, do not deduct that concession again. A separately documented additional eligible credit may still be applied.
- When the base/fee split is unknown, preserve the quoted all-in amount and label its basis; do not invent a base-rent split.
- When calculating free rent from an all-in quote, use a verified contractual base rent if the promotion applies only to base rent. If that cannot be established, document the limitation instead of discounting the fee portion silently.

### 12. Same list ratio training

**Rule ID:** `same_list_ratio_training`

Derive bedroom-price ratios only from other buildings in the current directory.

- Recompute ratios from the current research for each refresh; do not hard-code the prior run's medians or sample sizes.
- Use Seattle-addressed buildings in the list with directly observed, comparable market-rate prices and medium or high confidence. Do not use outside Seattle market averages or extrapolated prices as training inputs.
- For each eligible building with both types priced, calculate one_bedroom_rent / studio_rent and, separately, one_bedroom_rent / two_bedroom_rent.
- Use the median of the within-building ratios for each comparison type. This preserves the building match rather than dividing unrelated citywide average rents.
- Prefer consistent base-rent comparisons. Consistently quoted all-in pairs may be used if inseparable from advertised pricing and documented, but exclude mixed base/all-in or net/gross pairs.
- Exclude already concession-adjusted quotes unless their gross values can be reliably reconstructed on a consistent basis. Exclude restricted units, untyped prices and flagged incompatible observations.
- Store the exact building IDs, input rents, individual ratios, sample sizes and medians. If no defensible same-list ratio exists, do not substitute an outside ratio; document the limitation.

### 13. Extrapolate missing one bedroom

**Rule ID:** `extrapolate_missing_one_bedroom`

If no usable one-bedroom price exists, estimate it from a usable studio or two-bedroom price at that building.

- Prefer a studio anchor when available; otherwise use a two-bedroom anchor.
- estimated_1br_rent = anchor_rent * median_same_list_1br_to_anchor_ratio.
- Scale the rent component, then add applicable disclosed fees as dollar amounts. Do not multiply fixed fees by a bedroom-rent ratio.
- If carrying a rent-proportional concession into the hypothetical one-bedroom estimate, scale the free-rent credit with the inferred rent and state the eligibility assumption. Keep fixed dollar credits fixed; do not transfer an offer known to be incompatible with a one-bedroom.
- For a quoted all-in anchor with no separable fees, label the inference accordingly and do not add those included fees a second time.
- Mark the result as extrapolated and low confidence. It is a hypothetical one-bedroom estimate, not evidence that a one-bedroom is offered or currently available.

### 14. Missing price last resort

**Rule ID:** `missing_price_last_resort`

Use N/A only after the permitted direct and extrapolation routes have been exhausted.

- Check the official availability channel, linked leasing platform and applicable fee/special pages; then search or inspect matching Zillow and Redfin listings.
- When access or cached results prevent a conclusion, make a targeted second attempt using a working tool or live detail page before declaring pricing unavailable.
- Look for an eligible studio or two-bedroom price if no one-bedroom is priced, and try the same-list extrapolation method before giving up.
- If only unavailable, restricted, per-person, untyped or request-only prices remain, record why no defensible whole-apartment estimate can be made.
- Do not fabricate a price merely to keep a building in the list. Record temporary N/A with dated evidence and a reason.

### 15. Remove remaining na buildings

**Rule ID:** `remove_remaining_na_buildings`

As a last resort, remove buildings that still have N/A pricing from the active list.

- Remove the corresponding records from apartments.json buildings and generation-rules/pricing-research.json buildings only after the missing-price checks are complete.
- Archive each removed building's complete current record, pricing evidence, assumptions and exclusion reason in generation-rules/research-audit.json excluded.
- Update the matching directory decision from include to exclude, preserving the previous decision and reason. Avoid creating duplicate exclusion records.
- Update active building counts, direct/extrapolated/no-pricing counts, exclusion counts and documentation so they reconcile. No N/A values should remain in the final active directory.
- Preserve construction-year, management-company, amenities and other historical audit sections, including their original research-scope counts. Clearly distinguish those historical counts from current active-directory counts.
- Check ratio cohort membership. Removing unpriced buildings that were not ratio inputs does not require changing other buildings' prices; otherwise recompute affected ratios and estimates.
- Do not reintroduce previously excluded buildings from an old research snapshot. Reinstatement requires a new decision within the user's requested scope.

### 16. Retain reproducible evidence

**Rule ID:** `retain_reproducible_evidence`

Keep enough evidence to reproduce and assess each estimate.

- Record building ID, research date, source URLs and types, selected unit/floorplan, bedroom type, availability and the quoted price basis.
- Record the actual or assumed lease term, itemized included and excluded fees, applied and unapplied offers, eligibility conditions and total concession value.
- Retain the full cost calculation, unrounded inputs, effective monthly amount, final rounded value, direct/extrapolated status and confidence.
- Document inaccessible sources, price conflicts, unquantified fees, estimated utilities, open-bedroom layouts and all material assumptions.
- For an extrapolation, retain the anchor, ratio, sample reference, inferred rent and treatment of fees and concessions.

### 17. Parallel research

**Rule ID:** `parallel_research`

Use as much useful parallel research as available to complete large lists quickly.

- Assign independent buildings or batches to sub-agents, up to practical available concurrency. Use additional independent checks for uncertain prices, fees and N/A candidates.
- Give each researcher a separate output file or explicitly assigned records. Avoid multiple agents overwriting the same batch file.
- Have one integration step reconcile IDs, calculations, source conflicts and ratios before editing the active directory.

### 18. Preserve concurrent work

**Rule ID:** `preserve_concurrent_work`

Merge pricing and authorized removals into the latest files without overwriting unrelated work.

- Re-read the latest directory and audit files immediately before preparing a write. Do not replace them from a snapshot captured at the start of research.
- Preserve unrelated fields, sources, notes, metadata and audit sections, including construction-year, management-name and amenities updates.
- Compare current file contents or hashes with the versions used to prepare the changes immediately before replacement. If they changed, recompute the merge against the latest versions.
- Use atomic file replacement where possible, retain recoverable pre-change copies, and validate the resulting cross-file state.
- If directory membership changed during research, reconcile against the current membership rather than restoring removed entries or dropping new ones silently.

### 19. Validate before finishing

**Rule ID:** `validate_before_finishing`

Verify the final data, calculations and preservation of other work.

- Parse all edited JSON and verify unique IDs, matching active-directory and active-pricing IDs, and complete coverage of the remaining list.
- Require a positive numeric approx_1br_monthly_usd for every remaining active building; verify removed N/A records are archived.
- Recompute each effective amount from rent, fees, concessions and term. Reconcile itemized included fees with their aggregates and nonzero concession totals with applied promotion evidence.
- Verify published totals and effective rents have not had fees or promotions counted twice, and final rounding matches the calculation.
- Verify ratio cohorts, inputs, medians and extrapolation math are reproducible and use only eligible buildings from the list.
- Reconcile active and excluded counts and decision statuses. Confirm retained buildings' unrelated fields and historical audit sections remain intact.
- Run git diff --check when working in this repository and inspect the scope of the changes.

## Readdition policy

Before adding or merging any building into apartments.json, check generation-rules/excluded-apartments.json by id, current or previous name, address and property website. Do not automatically re-add a matching building, including under a new name or ID. Reinstatement requires an explicit user decision and a documented update to this registry; newly found prices or amenities alone do not override the exclusion.
