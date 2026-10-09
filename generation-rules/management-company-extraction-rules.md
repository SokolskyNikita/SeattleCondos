# Management-company extraction rules

**Schema version:** 1

**Created at:** 2026-10-09

**Updated at:** 2026-10-09

**Purpose:** Repeatable management-company extraction, evidence review, name consolidation and display-name shortening for the Seattle-area apartment directory, based on the decisions in this conversation.

## Scope

**Directory file:** apartments.json

**Record collection:** buildings

**Target field:** management_company

**Target meaning:** The current building/community-level residential property manager or day-to-day operator, stored under a concise, consistent display name.

**Audit file:** generation-rules/research-audit.json

**Null meaning:** No management company has been established with sufficient evidence; never a placeholder company name.

**Instruction precedence:** Apply these as project guidance; follow the user's current task scope and explicit instructions when they differ. Do not treat old mappings or example findings as proof of current management.

## Workflow

1. Read the latest directory and audit; enumerate the requested building IDs and existing management values. Match the building name, address, former names and official website before searching.
2. For a thorough multi-building extraction audit, assign one dedicated research agent per building. Run in waves when concurrency is limited. Each agent returns a separate result; one central reviewer merges the shared directory.
3. Research actual management using current public evidence: official property website, footer/logo links, contact/legal pages, application and resident portals, then the operator portfolio and relevant corroborating records. Do not submit forms or contact anyone unless separately authorized.
4. Match the exact property/address and identify each named company's role. Follow material conflicts through live pages or another available retrieval method instead of guessing after a failed fetch.
5. Record findings, source URLs, evidence strength, dates, conflicts, confidence and a resolution rationale. Preserve raw company names in the research result.
6. Central review accepts a supported high- or medium-confidence manager, or leaves null if unresolved. Only then apply the display-name mappings and shortening policy.
7. Merge only the intended management field, its supporting sources and necessary caveat notes into the latest data. Append the audit result; validate scope and concurrent edits before saving.

## Evidence policy

### Preferred evidence

- A current official property or property-linked leasing page explicitly naming the manager, including an unambiguous Managed By logo/label.
- An operator's current exact-property portfolio combined with a reciprocal property-site affiliation, resident portal, matching contact or explicit manager statement.
- Official property-management registration records with documented field meanings. Account for filing dates and the possibility of a later change.
- Current exact-property rental-platform records that explicitly identify the manager, corroborated where possible by the property/operator site or a genuinely separate source.

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

- Confirm address and property identity, not only a matching name. A misleading URL slug or search-result card can refer to another building; inspect the actual page.
- For shared websites or multi-community records, establish coverage of each represented community rather than extrapolating from one plan or one address.
- Do not use generic directory summaries, nearby listing labels or corporate homepages alone as property-specific management evidence.

**Independence:** Prefer two strong confirmations when available, but judge substance rather than counting URLs. HotPads and Realtor.com may share Zillow data; ApartmentHomeLiving, Apartment Finder and Apartments.com may share CoStar data. Multiple pages in one feed are not independent confirmations.

**Retrieval failures:** A blocked page, missing text extraction, CAPTCHA or empty result is not evidence of a manager change or absence. Use an available search/fetch/browser alternative or record the access limitation.

## Dates and currentness

- Record checked_at as the actual review date. Distinguish it from source publication, registration, expiry, crawl and listing-update dates.
- A newer crawl date or an availability Updated today label does not establish that a manager field changed or is correct.
- Relative dates such as 2 weeks ago on a cached job page refer to that page snapshot; do not subtract them from today unless the page is known to be live.
- Do not treat a current copyright year, active rent inventory or a future registration expiry as proof that all other content is current.
- Inspect live first-party pages when caches disagree. Prefer a dated management transition or consistent live property/operator evidence over an unsupported assumption that a competing page is stale.

## Conflict resolution

- List competing companies and sources explicitly; first test for different roles, legal-entity versus public-brand labels, historical versus current evidence, building versus unit-level management, and incorrect property matching.
- An explicit rental-platform manager field can still contain an owner/account label. Resolve it using property-specific operating evidence; do not automatically accept or dismiss it.
- Corporate affiliation or acquisition alone does not prove a particular property transferred managers. Combine company-level evidence with property-specific records.
- A public registration naming one entity and a live listing naming another can be consistent when official disclosures connect the legal entity and public brand; preserve both raw names and any uncertainty about the contracting party.
- Mark an interpretation as an inference when sources do not state it directly. Keep material contrary evidence in the audit even when one conclusion is favored.
- If genuinely competing current operators cannot be distinguished, leave management_company null and record candidates and an unresolved_reason. The best-guess permission for name cleanup is not permission to invent the actual manager.

## Confidence rules

**High:** Strong exact-property evidence establishes the operator, with corroboration where available and no material unexplained competing operator claim. A legal contract is not required; explain any public-brand/legal-entity distinction.

**Medium:** Credible property-specific evidence favors one operator, but meaningful conflicting or timing-limited evidence remains. Record the rationale and a concise management caveat on the building; preserve full conflicts in the audit.

**Low or unresolved:** Evidence is insufficient, inaccessible or materially contradictory without a defensible resolution. Use status unresolved and management_company null; retain candidates in the audit instead of the display field.

**Rule:** Confidence describes the evidence for the actual manager. It is separate from confidence in a heuristic display-name consolidation.

## Research result format

### Required fields

- id
- name
- management_company
- status
- confidence
- checked_at
- summary
- sources
- conflicts
- search_queries
- unresolved_reason

### Optional fields

- raw_management_company
- candidate_companies
- evidence
- source_dates
- inferences

### Status values

- verified
- unresolved

### Confidence values

- high
- medium
- low

### Source record

```json
{
  "url": "<exact public evidence URL>",
  "supports": [
    "management_company"
  ],
  "note": "<observed property/address match, manager statement or affiliation, and material date/role caveat>"
}
```

**Source supports rule:** Use the schema field name management_company in supports, not a company name.

**Quoting rule:** Prefer concise factual paraphrases and short evidence excerpts. Preserve exact company names without copying whole source pages.

## Display name policy

**Mode:** Best-guess cleanup using existing names and local evidence; no new research solely to normalize or shorten names unless the user asks for it.

### Sequence

- Establish the raw operator name from evidence.
- Apply the recorded alias consolidation.
- Apply the later display-name shortening.
- Preserve the raw name and reasoning in evidence/audit records.

### Legal suffix candidates

- Inc.
- Incorporated
- LLC
- Ltd.
- Limited
- LLP
- PLC
- Corp.
- Corporation
- Company
- Co.

### Other possible filler

- Holdings
- Group
- Services
- Property Company
- Management Company
- Residential
- Apartment Homes

**Removal rule:** These are candidates, not a global stop-word list. Remove suffixes and corporate wording only when the remaining name is recognizable and does not lose a useful distinction. Use the exact mappings below for names already reviewed.

**Identity rule:** Company-group/brand consolidations below are directory display conventions; they do not assert that every alias is the same legal entity. Do not extend a merger, owner or subsidiary mapping to an unrelated company based only on generic overlapping words.

**Capitalization:** Preserve established brand capitalization and punctuation, including 11Residential, AMLI, CONAM, CWS, NAREIG, UDR and Cushman & Wakefield. Do not invent abbreviations or blindly title-case acronyms.

**New names:** The reference inventory is not a whitelist. Keep a newly verified company under a sensible concise name; add an explicit mapping and audit note when changing an existing display convention.

**Historical text:** Do not rename company mentions in source notes, quotations, URLs, legal-entity evidence or earlier audit results. The latest display mapping supersedes earlier field labels without rewriting history.

### Keep distinct

| Names | Reason |
|---|---|
| Pillar Communities<br>Pillar Properties | These remained separate in this conversation; dropping the second word would merge distinguishable companies. |
| Coast Real Estate<br>North Coast Living<br>Two Coast Living | Shared Coast wording is not evidence of one company. |
| AGM<br>MG Properties<br>GRE Management<br>CRL Property Management | Preserve these separate initials/brands; similarity is not an alias rule. |

## Existing mapping changes

**As of:** 2026-10-09

### Provenance

**File:** generation-rules/research-audit.json

**Consolidations section:** management_company_name_normalization.groups

**Shortenings section:** management_company_display_name_shortening.mappings

**Precedence:** The 24 consolidation groups below record their historical canonical_name. The 38 later shortenings supersede those display labels. final_alias_to_display_name is the flattened one-step lookup for new writes; values are terminal display names.

### Lookup rules

- Prefer exact full-name lookup; normalize leading/trailing whitespace and repeated whitespace for matching. A case-insensitive full-name lookup is acceptable only when it resolves unambiguously to one target.
- Do not use substring replacement or unrestricted fuzzy matching. Unknown names require judgment under the display-name policy.
- Use the flattened lookup once. If replaying history, run consolidation once, then shortening once; never recursively follow a combined historical graph. Tarragon -&gt; Tarragon Property Services -&gt; Tarragon is an intentional historical round trip, not a loop to keep applying.
- Unmapped current display names pass through unchanged. Reapplying the final lookup must be idempotent and must not reintroduce a long historical name.

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
- CWS Capital Partners/CWS Apartment Homes, Forge Management/Forge Property Management, and similar distinctive brand-root variants are best-guess groupings, not newly researched identity claims.
- Pillar Communities and Pillar Properties remain separate: the shared generic word is insufficient to infer one company. Coast Real Estate and North Coast Living also remain separate.

## Directory write and concurrency rules

- Use separate per-building result files for parallel research. Research agents must not independently rewrite apartments.json or generation-rules/research-audit.json; a central merger reviews and applies results.
- Read the latest shared files immediately before preparing a merge. Apply only the authorized fields by stable building ID; never write an old full-file snapshot over another chat's changes.
- For extraction, update the manager, supporting source entries, necessary caveat notes and the relevant review date. For name-only cleanup, change only management_company and append a mapping audit. Do not alter construction years, pricing, amenities, eligibility, addresses or record membership.
- When a source URL already exists on a building, merge management_company into supports and preserve the existing note/evidence. Do not delete unrelated sources or create avoidable duplicate URLs.
- Preserve all existing audit sections. Append new audit decisions or normalization mappings; do not restore old researched names over newer user-requested display names.
- Check file contents or hashes immediately before saving. If either file changed during preparation, re-read and recompute against the newest version. An atomic file replacement prevents a partial file but does not by itself prevent stale-snapshot data loss.
- For simultaneous writers, prefer a single writer or an agreed shared lock around read/merge/write. Coordinate warnings with other chats when authorized by the user. Do not treat a brief hash check as a guarantee against every race.
- If a suspected overwrite is found, compare snapshots and audit history, identify the lost fields and restore only confirmed authorized changes while retaining newer unrelated work. Do not replay an entire older directory.

## Validation checklist

- Both affected JSON files parse successfully; required fields and source-support labels are correct.
- Each accepted manager has property-specific evidence. Unresolved entries use null and have an explicit reason; medium-confidence entries retain material caveats.
- Building IDs, order and membership match the latest pre-write snapshot unless the user separately authorized record changes. Do not hard-code historical totals such as 355 or 345 as permanent requirements.
- A name-only change preserves every other building field, source, note, metadata value and prior audit section. An extraction change stays within its documented field scope.
- Previously populated management names have not been inadvertently reset to null. Existing blanks are resolved only where evidence supports an answer.
- All consolidation and shortening aliases resolve to their final labels; the mapping is deterministic and idempotent. Shortening alone must not collapse two previously distinct companies.
- The explicitly protected distinct names remain distinct. Check for accidental collisions after whitespace/case normalization and proposed suffix removal.
- Review the task-specific diff against the immediate pre-write snapshot, not just Git HEAD, which can include other chats' work. Check whitespace/errors and report the actual current counts.

## Lessons from reviewed buildings

### Arrive Magnolia and Arrive Magnolia West

**Building id:** arrive-magnolia-and-arrive-magnolia-west

**Building name:** Arrive Magnolia and Arrive Magnolia West

**Reviewed on:** 2026-10-09

**Accepted research name:** Trinity Property Consultants

**Display name:** Trinity

**Confidence at review:** high

**Lesson:** Verify every community represented by a combined record.

**Explanation:** The dedicated agent checked both a main-community plan and an explicitly labeled Magnolia West plan in the official leasing portal. Both named Trinity Property Consultants, whose current display name is Trinity.

#### Evidence reference

**File:** generation-rules/research-audit.json

**Section:** management_company_audit.results

**Match id:** arrive-magnolia-and-arrive-magnolia-west

### Monarch Apartments

**Building id:** monarch-apartments

**Building name:** Monarch Apartments

**Reviewed on:** 2026-10-09

**Accepted research name:** Cyzner Properties West

**Display name:** Cyzner Properties West

**Confidence at review:** high

**Lesson:** Recognize shared listing feeds and platform vendors.

**Explanation:** Exact-address listings explicitly named Cyzner Properties West; multiple CoStar sites are related evidence, not independent confirmations. MarketApts and ManageBuilding references identified vendors, not the manager.

#### Evidence reference

**File:** generation-rules/research-audit.json

**Section:** management_company_audit.results

**Match id:** monarch-apartments

### Parque Kirkland

**Building id:** parque-kirkland

**Building name:** Parque Kirkland

**Reviewed on:** 2026-10-09

**Accepted research name:** Aspire Properties Northwest

**Display name:** Aspire Properties Northwest

**Confidence at review:** high

**Lesson:** Separate residential management from owner or developer oversight.

**Explanation:** Property leasing contacts and rental criteria identified Aspire Properties Northwest; broader Henbart portfolio wording referred to a different ownership/development context. The property-specific residential evidence drove the choice.

#### Evidence reference

**File:** generation-rules/research-audit.json

**Section:** management_company_audit.results

**Match id:** parque-kirkland

### Pike Motorworks

**Building id:** pike-motorworks

**Building name:** Pike Motorworks

**Reviewed on:** 2026-10-09

**Accepted research name:** Greystar

**Display name:** Greystar

**Confidence at review:** medium

**Lesson:** Favor a supported operating manager over an owner/account label, but retain the inference and competing evidence.

**Explanation:** The live property site, Greystar portfolio and screening links supported Greystar; RentCafe and text consent named owner/investor TA Realty. The owner/account explanation was an inference, so the accepted result retained medium confidence.

#### Evidence reference

**File:** generation-rules/research-audit.json

**Section:** management_company_audit.results

**Match id:** pike-motorworks

### Sofi at Somerset

**Building id:** sofi-at-somerset

**Building name:** Sofi at Somerset

**Reviewed on:** 2026-10-09

**Accepted research name:** Asset Living

**Display name:** Asset Living

**Confidence at review:** medium

**Lesson:** Inspect live pages when indexed portfolios disagree.

**Explanation:** Live property-site legal links and the explicit RentCafe manager field supported Asset Living. An Avenue5-hosted portfolio still listed the property, so the accepted result retained medium confidence; a crawl date alone did not decide the outcome.

#### Evidence reference

**File:** generation-rules/research-audit.json

**Section:** management_company_audit.results

**Match id:** sofi-at-somerset

### The Residences at 3295

**Building id:** the-residences-at-3295

**Building name:** The Residences at 3295

**Reviewed on:** 2026-10-09

**Accepted research name:** Asset Living (FPI Management, Inc.)

**Display name:** Asset Living

**Confidence at review:** high

**Lesson:** Reconcile public brand and registered management entity without claiming an unseen contract.

**Explanation:** The live listing named Asset Living, Seattle registration named FPI Management as the management contact, and Asset Living disclosures listed FPI in Washington. The researched label was Asset Living (FPI Management, Inc.); display normalization later reduced it to Asset Living. The precise contracting entity was not independently confirmed.

#### Evidence reference

**File:** generation-rules/research-audit.json

**Section:** management_company_audit.results

**Match id:** the-residences-at-3295

### Uptown 11

**Building id:** uptown-11

**Building name:** Uptown 11

**Reviewed on:** 2026-10-09

**Accepted research name:** NAREIG Property Management

**Display name:** NAREIG

**Confidence at review:** high

**Lesson:** Separate building-level management from possible unit-level listing representation.

**Explanation:** The official resident link led to NAREIG AppFolio, supported by the NAREIG portfolio and matching contact information. Syndicated WJL unit listings were retained as a caveat, not automatically treated as a replacement building manager.

#### Evidence reference

**File:** generation-rules/research-audit.json

**Section:** management_company_audit.results

**Match id:** uptown-11

## Historical run statistics

### Initial missing name audit

**Reviewed:** 18

**Filled:** 18

**Unresolved:** 0

**Initial audit directory size:** 355

### Consolidation

**Buildings:** 355

**Distinct names before:** 114

**Distinct names after:** 80

**Alias groups:** 24

**Building names normalized:** 63

**Prior audit entries restored:** 0

### Shortening

**Buildings:** 345

**Distinct companies before:** 78

**Distinct companies after:** 78

**Company labels shortened:** 38

**Building records updated:** 203

**Note:** These are historical snapshots, not fixed future targets. Other authorized directory work reduced the included buildings from 355 to 345 between naming stages; the change from 80 to 78 distinct names was not an extra merger performed by the shortening step.

## Current display name reference

**Snapshot date:** 2026-10-09

**Building count:** 345

**Distinct name count:** 78

**Missing count:** 0

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

**Note:** Reference inventory at file creation; refresh from the live directory during future work. New verified companies are allowed.
