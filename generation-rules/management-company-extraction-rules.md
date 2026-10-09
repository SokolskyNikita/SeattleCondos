# Management-company extraction rules

Rules for identifying property managers and choosing their display names in the Seattle-area apartment directory.

Schema version 1. Created and updated October 9, 2026.

## Scope

Set `management_company` on records in the `buildings` array of [apartments.json](../apartments.json). It names the current residential property manager or day-to-day operator for the building or community. Use a short, consistent display name. Leave it `null` when the evidence does not establish a manager.

Record the research in [research-audit.json](research-audit.json). Follow the user's current scope and instructions when they differ from this guide. Old mappings and examples do not prove who manages a building now.

## Workflow

1. Read the latest directory and audit; list the requested building IDs and existing management values. Match the building name, address, former names and official website before searching.
2. When auditing management across multiple buildings, assign one dedicated research agent per building. Run in waves when concurrency is limited. Each agent returns a separate result; one central reviewer merges the shared directory.
3. Research actual management using current public evidence: official property website, footer/logo links, contact/legal pages, application and resident portals, then the operator portfolio and relevant corroborating records. Do not submit forms or contact anyone unless separately authorized.
4. Match the exact property/address and identify each named company's role. Follow material conflicts through live pages or another available retrieval method instead of guessing after a failed fetch.
5. Record findings, source URLs, evidence strength, dates, conflicts, confidence and the reason for the decision. Preserve raw company names in the research result.
6. Central review accepts a supported high- or medium-confidence manager, or leaves null if unresolved. Only then apply the display-name mappings and shortening policy.
7. Merge only the intended management field, its supporting sources and necessary caveat notes into the latest data. Append the audit result; validate scope and concurrent edits before saving.

## Evidence policy

### Preferred evidence

- A current official property or property-linked leasing page explicitly naming the manager, including an unambiguous Managed By logo/label.
- An operator's current exact-property portfolio combined with a reciprocal property-site affiliation, resident portal, matching contact or explicit manager statement.
- Official property-management registration records with documented field meanings. Account for filing dates and the possibility of a later change.
- Current rental-platform records for the exact property that name the manager. Check them against the property or operator site, or an independent source, when possible.

### Supporting but not decisive alone

- A logo, copyright notice, privacy-policy link, text-message consent or email domain shows affiliation; it does not by itself prove the company is the operating manager.
- Property-specific hiring evidence may corroborate operations when the employer, property and publication date are established.
- Owner portfolios, development announcements, acquisition records, agency design credits and general company descriptions provide context but may describe a different role.

### Do not confuse with the manager

- Owner, investor, asset manager, developer, buyer or seller.
- Website, leasing, listing or resident-portal vendors such as Yardi/RentCafe, Entrata, RealPage, On-Site, AppFolio, ManageBuilding or MarketApts.
- A broker, listing contact or manager of an individual unit when the directory record covers the whole rental community.
- An adjacent property, similarly named building, commercial component or a former operator.

### Identity checks

- Check the address and property identity as well as the name. A misleading URL slug or search-result card can refer to another building; inspect the actual page.
- For shared websites or multi-community records, establish coverage of each represented community rather than extrapolating from one plan or one address.
- Do not use generic directory summaries, nearby listing labels or corporate homepages alone as property-specific management evidence.

Prefer two strong confirmations when available, but judge substance rather than counting URLs. HotPads and Realtor.com may share Zillow data; ApartmentHomeLiving, Apartment Finder and Apartments.com may share CoStar data. Multiple pages in one feed are not independent confirmations.

A blocked page, missing text extraction, CAPTCHA or empty result is not evidence of a manager change or absence. Use an available search/fetch/browser alternative or record the access limitation.

## Dates and currentness

- Record checked_at as the actual review date. Distinguish it from source publication, registration, expiry, crawl and listing-update dates.
- A newer crawl date or an availability Updated today label does not establish that a manager field changed or is correct.
- Relative dates such as 2 weeks ago on a cached job page refer to that page snapshot; do not subtract them from today unless the page is known to be live.
- Do not treat a current copyright year, active rent inventory or a future registration expiry as proof that all other content is current.
- Inspect live first-party pages when caches disagree. Prefer a dated management transition or consistent live property/operator evidence over an unsupported assumption that a competing page is stale.

## Conflict resolution

- List competing companies and sources explicitly; first test for different roles, legal-entity versus public-brand labels, historical versus current evidence, building versus unit-level management and incorrect property matching.
- An explicit rental-platform manager field can still contain an owner/account label. Resolve it using property-specific operating evidence; do not automatically accept or dismiss it.
- Corporate affiliation or acquisition alone does not prove a particular property transferred managers. Combine company-level evidence with property-specific records.
- A public registration naming one entity and a live listing naming another can be consistent when official disclosures connect the legal entity and public brand; preserve both raw names and any uncertainty about the contracting party.
- Mark an interpretation as an inference when sources do not state it directly. Keep material contrary evidence in the audit even when one conclusion is favored.
- If the evidence does not resolve competing claims about the current operator, leave `management_company` null and record candidates and an `unresolved_reason`. The best-guess permission for name cleanup is not permission to invent the actual manager.

## Confidence rules

### High

Evidence for the exact property identifies the operator. Check it against other sources when available and resolve any conflicting claim that could change the result. A legal contract is not required; explain any public-brand/legal-entity distinction.

### Medium

Credible property-specific evidence favors one operator, but meaningful conflicting or timing-limited evidence remains. Record the rationale and a concise management caveat on the building; preserve full conflicts in the audit.

### Low or unresolved

Use this level when evidence is insufficient or inaccessible, or when conflicting sources cannot be resolved. Set `status` to `unresolved` and `management_company` to null; retain candidates in the audit instead of the display field.

Confidence describes the evidence for the actual manager. It is separate from confidence in a best-guess grouping of display names.

## Research result format

Required fields are `id`, `name`, `management_company`, `status`, `confidence`, `checked_at`, `summary`, `sources`, `conflicts`, `search_queries` and `unresolved_reason`.

Optional fields are `raw_management_company`, `candidate_companies`, `evidence`, `source_dates` and `inferences`.

Use `verified` or `unresolved` for status and `high`, `medium` or `low` for confidence.

### Source record

```json
{
  "url": "<exact public evidence URL>",
  "supports": [
    "management_company"
  ],
  "note": "<observed property/address match, manager statement or affiliation and material date/role caveat>"
}
```

Put `management_company` in `supports`. Company names belong in the field value.

Prefer concise factual paraphrases and short evidence excerpts. Preserve exact company names without copying whole source pages.

## Display name policy

Use existing names and local evidence to make a best-guess cleanup. Research solely for name normalization or shortening requires a user request.

Establish the raw operator name from evidence, then apply the recorded alias consolidation and display-name shortening. Keep the raw name and reasoning in the audit.

### Suffixes and filler

Legal suffixes that may be removed include Inc., Incorporated, LLC, Ltd., Limited, LLP, PLC, Corp., Corporation, Company and Co. Other candidates include Holdings, Group, Services, Property Company, Management Company, Residential and Apartment Homes.

Review each name before removing words. Remove suffixes and corporate wording only when the remaining name is recognizable and does not lose a useful distinction. Use the exact mappings below for names already reviewed.

The mappings group company names and brands for display. They do not establish that every alias is the same legal entity. Do not extend a merger, owner or subsidiary mapping to an unrelated company based only on generic overlapping words.

Preserve established brand capitalization and punctuation, including 11Residential, AMLI, CONAM, CWS, NAREIG, UDR and Cushman & Wakefield. Do not invent abbreviations or blindly title-case acronyms.

The reference inventory is not a whitelist. Keep a newly verified company under a sensible concise name; add an explicit mapping and audit note when changing an existing display convention.

Do not rename company mentions in source notes, quotations, URLs, legal-entity evidence or earlier audit results. The latest display mapping supersedes earlier field labels without rewriting history.

### Keep distinct

Keep Pillar Communities and Pillar Properties separate. Retain Coast Real Estate, North Coast Living and Two Coast Living as separate names too; a shared word does not establish common management. AGM, MG Properties, GRE Management and CRL Property Management are separate brands whose initials must be preserved.

## Existing mapping changes

Mappings as of October 9, 2026. Their history is in [research-audit.json](research-audit.json): `management_company_name_normalization.groups` records consolidations and `management_company_display_name_shortening.mappings` records shortenings.

The 24 consolidation groups below retain their historical `canonical_name`. The 38 later shortenings replace those display labels. Use [Final alias to display name](#final-alias-to-display-name) for new writes; its values are the final names.

### Lookup rules

- Prefer exact full-name lookup; normalize leading/trailing whitespace and repeated whitespace for matching. Ignore case only when the full name matches a single target.
- Do not use substring replacement or unrestricted fuzzy matching. Unknown names require judgment under the display-name policy.
- Apply the final lookup once. If replaying history, run consolidation once, then shortening once; never recursively follow a combined historical graph. Tarragon -&gt; Tarragon Property Services -&gt; Tarragon is an intentional historical round trip, not a loop to keep applying.
- Unmapped current display names pass through unchanged. Reapplying the final lookup must leave the result unchanged and must not reintroduce a long historical name.

### Consolidations

| Canonical name | Previous names | Final display name |
|---|---|---|
| Apartment Management Consultants, LLC | Apartment Management Consultants (AMC)<br>Apartment Management Consultants LLC<br>Apartment Management Consultants, LLC | Apartment Management Consultants |
| Asset Living | Asset Living<br>Asset Living (FPI Management, Inc.) | Asset Living |
| Vivmark Residential | Vivmark Residential<br>AvalonBay Communities (Vivmark Residential)<br>`"AvalonBay Communities (Vivmark Residential) "`<br>Vivmark Residential (Avalon Communities brand)<br>Vivmark Residential (Equity Residential)<br>Equity Residential | Vivmark |
| Avenue5 Residential | Avenue5 Residential<br>Avenue5 Residential, LLC | Avenue5 |
| Bonavista Management | Bonavista Management<br>Bonavista Management, LLC<br>Bonavista Real Estate Management | Bonavista |
| Bozzuto | Bozzuto<br>Bozzuto Management Company | Bozzuto |
| CWS Apartment Homes | CWS Apartment Homes<br>CWS Apartment Homes, LLC<br>CWS Capital Partners | CWS |
| Epic Asset Management | Epic Asset Management<br>Epic Asset Management, Inc. | Epic Asset Management |
| Essex Property Trust | Essex Management Corporation<br>Essex Management Corporation (Essex Property Trust)<br>Essex Property Trust<br>Essex Property Trust (Essex Management Corporation) | Essex |
| Forge Property Management | Forge Management<br>Forge Property Management | Forge Property Management |
| GRE Management, LLC | GRE Management LLC<br>GRE Management, LLC | GRE Management |
| Green Leaf Partners | Green Leaf Partners<br>Green Leaf Partners Management, Inc. | Green Leaf |
| Guide Property Services | Guide Property Management<br>Guide Property Services | Guide Property Services |
| Holland Residential | Holland Partner Group / Holland Residential<br>Holland Residential | Holland |
| Legacy Partners | Legacy Partners<br>Legacy Partners, Inc. | Legacy Partners |
| Pacific Crest Real Estate | Pacific Crest Real Estate<br>Pacific Crest Real Estate, LLC | Pacific Crest Real Estate |
| Cushman & Wakefield | Cushman & Wakefield<br>Pinnacle Property Management Services, LLC<br>Pinnacle Property Management Services, LLC (Cushman & Wakefield) | Cushman & Wakefield |
| Precision Management Company, Inc. | Precision Managed<br>Precision Management Company, Inc. | Precision Management |
| Redside Partners | Redside Partners<br>Redside Partners LLC | Redside |
| Shea Apartments | Shea Apartments<br>Shea Properties | Shea |
| Tarragon Property Services | Tarragon<br>Tarragon Property Services | Tarragon |
| UDR | UDR<br>UDR, Inc. | UDR |
| Waterton | Waterton<br>Waterton Residential | Waterton |
| Windsor Communities | Windsor Communities<br>Windsor Property Management Co. | Windsor |

### Shortenings

| Previous name | Display name | Building count |
|---|---|---|
| AGM Real Estate Group | AGM | 1 |
| Allied Residential, Inc. | Allied Residential | 4 |
| American Property Management, Inc. | American Property Management | 1 |
| AMLI Residential | AMLI | 6 |
| Apartment Management Consultants, LLC | Apartment Management Consultants | 5 |
| Avenue5 Residential | Avenue5 | 28 |
| Bonavista Management | Bonavista | 11 |
| CONAM Management Corporation | CONAM | 1 |
| CWS Apartment Homes | CWS | 3 |
| Essex Property Trust | Essex | 19 |
| Fairfield Residential | Fairfield | 1 |
| First Pointe Management Group | First Pointe | 1 |
| Fulcrum Real Estate Services | Fulcrum | 1 |
| GRE Management, LLC | GRE Management | 5 |
| Green Leaf Partners | Green Leaf | 2 |
| Griffis Residential | Griffis | 3 |
| Holland Residential | Holland | 9 |
| Indigo Real Estate Services, Inc. | Indigo Real Estate | 2 |
| Madrona Real Estate Services, LLC | Madrona Real Estate | 1 |
| Mill Creek Residential | Mill Creek | 5 |
| NAREIG Property Management | NAREIG | 1 |
| Olympic Multi-Family Management | Olympic Management | 1 |
| Onni Group | Onni | 1 |
| Palladium Real Estate Services, LLC | Palladium | 2 |
| Precision Management Company, Inc. | Precision Management | 6 |
| Real Property Associates, Inc. | Real Property Associates | 1 |
| Redside Partners | Redside | 5 |
| Redstone Residential | Redstone | 1 |
| Shea Apartments | Shea | 2 |
| Simpson Property Group | Simpson | 2 |
| Tarragon Property Services | Tarragon | 2 |
| Thrive Communities | Thrive | 27 |
| Trinity Property Consultants | Trinity | 2 |
| Vivmark Residential | Vivmark | 24 |
| Weidner Apartment Homes | Weidner | 9 |
| Willow Bridge Property Company | Willow Bridge | 1 |
| Wilshire Residential, LLC | Wilshire Residential | 1 |
| Windsor Communities | Windsor | 6 |

### Final alias to display name

| Alias | Final display name |
|---|---|
| AGM Real Estate Group | AGM |
| AMLI Residential | AMLI |
| Allied Residential, Inc. | Allied Residential |
| American Property Management, Inc. | American Property Management |
| Apartment Management Consultants (AMC) | Apartment Management Consultants |
| Apartment Management Consultants LLC | Apartment Management Consultants |
| Apartment Management Consultants, LLC | Apartment Management Consultants |
| Asset Living (FPI Management, Inc.) | Asset Living |
| AvalonBay Communities (Vivmark Residential) | Vivmark |
| `"AvalonBay Communities (Vivmark Residential) "` | Vivmark |
| Avenue5 Residential | Avenue5 |
| Avenue5 Residential, LLC | Avenue5 |
| Bonavista Management | Bonavista |
| Bonavista Management, LLC | Bonavista |
| Bonavista Real Estate Management | Bonavista |
| Bozzuto Management Company | Bozzuto |
| CONAM Management Corporation | CONAM |
| CWS Apartment Homes | CWS |
| CWS Apartment Homes, LLC | CWS |
| CWS Capital Partners | CWS |
| Epic Asset Management, Inc. | Epic Asset Management |
| Equity Residential | Vivmark |
| Essex Management Corporation | Essex |
| Essex Management Corporation (Essex Property Trust) | Essex |
| Essex Property Trust | Essex |
| Essex Property Trust (Essex Management Corporation) | Essex |
| Fairfield Residential | Fairfield |
| First Pointe Management Group | First Pointe |
| Forge Management | Forge Property Management |
| Fulcrum Real Estate Services | Fulcrum |
| GRE Management LLC | GRE Management |
| GRE Management, LLC | GRE Management |
| Green Leaf Partners | Green Leaf |
| Green Leaf Partners Management, Inc. | Green Leaf |
| Griffis Residential | Griffis |
| Guide Property Management | Guide Property Services |
| Holland Partner Group / Holland Residential | Holland |
| Holland Residential | Holland |
| Indigo Real Estate Services, Inc. | Indigo Real Estate |
| Legacy Partners, Inc. | Legacy Partners |
| Madrona Real Estate Services, LLC | Madrona Real Estate |
| Mill Creek Residential | Mill Creek |
| NAREIG Property Management | NAREIG |
| Olympic Multi-Family Management | Olympic Management |
| Onni Group | Onni |
| Pacific Crest Real Estate, LLC | Pacific Crest Real Estate |
| Palladium Real Estate Services, LLC | Palladium |
| Pinnacle Property Management Services, LLC | Cushman & Wakefield |
| Pinnacle Property Management Services, LLC (Cushman & Wakefield) | Cushman & Wakefield |
| Precision Managed | Precision Management |
| Precision Management Company, Inc. | Precision Management |
| Real Property Associates, Inc. | Real Property Associates |
| Redside Partners | Redside |
| Redside Partners LLC | Redside |
| Redstone Residential | Redstone |
| Shea Apartments | Shea |
| Shea Properties | Shea |
| Simpson Property Group | Simpson |
| Tarragon Property Services | Tarragon |
| Thrive Communities | Thrive |
| Trinity Property Consultants | Trinity |
| UDR, Inc. | UDR |
| Vivmark Residential | Vivmark |
| Vivmark Residential (Avalon Communities brand) | Vivmark |
| Vivmark Residential (Equity Residential) | Vivmark |
| Waterton Residential | Waterton |
| Weidner Apartment Homes | Weidner |
| Willow Bridge Property Company | Willow Bridge |
| Wilshire Residential, LLC | Wilshire Residential |
| Windsor Communities | Windsor |
| Windsor Property Management Co. | Windsor |

### Company group judgments

- Vivmark consolidates Equity Residential and AvalonBay labels because existing local source notes explicitly describe them as one combined operator.
- Pinnacle/Cushman, Asset Living/FPI, Essex and Holland composites are treated as group/brand aliases for this requested display-name deduplication; original entity-specific evidence remains in the audit and property sources.
- CWS Capital Partners/CWS Apartment Homes, Forge Management/Forge Property Management and similar distinctive brand-root variants are best-guess groupings, not newly researched identity claims.
- Pillar Communities and Pillar Properties remain separate: the shared generic word is insufficient to infer one company. Coast Real Estate and North Coast Living also remain separate.

## Directory write and concurrency rules

Follow the [shared concurrent-write rules](README.md#concurrent-writes), with these management-specific constraints:

- For extraction, update the manager, supporting source entries, necessary caveat notes and the relevant review date. For name-only cleanup, change only management_company and append a mapping audit. Do not alter construction years, pricing, amenities, eligibility, addresses or record membership.
- When a source URL already exists on a building, merge management_company into supports and preserve the existing note/evidence. Do not delete unrelated sources or create avoidable duplicate URLs.

## Validation checklist

Apply the [shared validation checks](README.md#shared-validation), then verify management-specific requirements:

- Each accepted manager has property-specific evidence. Unresolved entries use null and have an explicit reason; medium-confidence entries retain material caveats.
- A name-only change preserves every other building field, source, note, metadata value and prior audit section. An extraction change stays within its documented field scope.
- Previously populated management names have not been inadvertently reset to null. Existing blanks are resolved only where evidence supports an answer.
- All consolidation and shortening aliases resolve to their final labels; the same input always gives the same output and a second pass leaves it unchanged. Shortening alone must not collapse two previously distinct companies.
- The explicitly protected distinct names remain distinct. Check whether removing suffixes or normalizing whitespace and case would collapse separate names.

## Lessons from reviewed buildings

These reviews were completed on October 9, 2026. Evidence is in `management_company_audit.results` in [research-audit.json](research-audit.json), under the building IDs below.

### Arrive Magnolia and Arrive Magnolia West

Check every community in a combined record. The researcher checked a main-community plan and an explicitly labeled Magnolia West plan in the official leasing portal. Both named Trinity Property Consultants, displayed as Trinity. The review recorded high confidence for `arrive-magnolia-and-arrive-magnolia-west`.

### Monarch Apartments

Listings for the exact address named Cyzner Properties West, which was accepted with high confidence for `monarch-apartments`. The CoStar sites shared a listing feed, so their agreement did not count as independent confirmation. MarketApts and ManageBuilding were vendors.

### Parque Kirkland

Leasing contacts and rental criteria identified Aspire Properties Northwest. Henbart's portfolio described ownership and development. The review used the residential management evidence and accepted Aspire Properties Northwest with high confidence for `parque-kirkland`.

### Pike Motorworks

The live property site, Greystar portfolio and screening links supported Greystar. RentCafe and text consent named owner/investor TA Realty. Treating TA Realty as an owner/account label was an inference; the review retained that caveat and accepted Greystar with medium confidence for `pike-motorworks`.

### Sofi at Somerset

Live property-site legal links and RentCafe's manager field supported Asset Living, but an Avenue5-hosted portfolio still listed the property. The review accepted Asset Living with medium confidence for `sofi-at-somerset`. A crawl date alone did not settle the conflict.

### The Residences at 3295

The live listing named Asset Living. Seattle registration named FPI Management as the management contact and Asset Living's disclosures listed FPI in Washington. The review accepted Asset Living (FPI Management, Inc.) with high confidence for `the-residences-at-3295`; the display name was later shortened to Asset Living. The precise contracting entity was not independently confirmed.

### Uptown 11

The official resident link led to NAREIG AppFolio. The NAREIG portfolio and matching contact information also supported NAREIG Property Management, displayed as NAREIG. The review accepted it with high confidence for `uptown-11` and kept the syndicated WJL unit listings as a caveat about who represented those units.

## Historical run statistics

The initial audit reviewed all 18 missing management names in a directory of 355 buildings. It filled all 18 and left none unresolved.

Consolidation then reduced 114 distinct names to 80 across 355 buildings. It grouped 24 sets of aliases and changed the names on 63 buildings. No prior audit entries were restored.

The later shortening pass covered 345 buildings. It shortened 38 company labels on 203 records and left the distinct-company count at 78. Other authorized work had removed buildings between passes, which explains the change from 80 to 78 companies. The shortening pass did not merge more companies.

## Current display name reference

The October 9, 2026 snapshot had 345 buildings, 78 distinct management names and no missing names. These are historical counts. Refresh the inventory from the live directory for future work; new verified companies are allowed.

### Names

- 11Residential
- AGM
- AMLI
- Allied Residential
- American Property Management
- Apartment Management Consultants
- Arboreal Management
- Aspire Properties Northwest
- Asset Living
- Avenue5
- Bell Partners
- Berkshire Communities
- Blanton Turner
- Bonavista
- Bozzuto
- Brink Property Management
- Brookfield Properties
- CONAM
- CRL Property Management
- CWS
- Cascadian Property Management
- Coast Real Estate
- Cornell & Associates
- Cushman & Wakefield
- Cyzner Properties West
- Edison47
- Epic Asset Management
- Essex
- Fairfield
- Fathom Property Management
- First Pointe
- Forge Property Management
- Fulcrum
- GRE Management
- Gables Residential
- Green Leaf
- Greystar
- Griffis
- Guide Property Services
- Holland
- Hunters Capital
- Indigo Real Estate
- KG Investment Properties
- Koz Properties
- Legacy Partners
- MG Properties
- MJW Investments
- Madrona Real Estate
- Mill Creek
- NAREIG
- North Coast Living
- ORI on the AVE
- Olympic Management
- Onni
- Pacific Crest Real Estate
- Palladium
- Pillar Communities
- Pillar Properties
- Placemakr
- Precision Management
- Real Property Associates
- Redside
- Redstone
- SRG Residential
- Shea
- Simpson
- SyRES Properties
- Tarragon
- Thrive
- Trinity
- Two Coast Living
- UDR
- Vivmark
- Waterton
- Weidner
- Willow Bridge
- Wilshire Residential
- Windsor
