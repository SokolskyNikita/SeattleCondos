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
| [research-audit.json](research-audit.json) | Historical research, source evidence, decisions, and 71 archived exclusions, including the 18 above. |
| [amenity-processing-report.json](amenity-processing-report.json) | Generated counts, exclusions and ambiguity report matching the current rules and directory. |
| [process_amenities.py](process_amenities.py) | Applies amenity mappings while preserving original descriptions and details. |
| [test_process_amenities.py](test_process_amenities.py) | Checks normalization, detail preservation, and safe writes. |

Regenerate the directory and report with `python3 generation-rules/process_amenities.py --write` after changing the mappings. Commit the rules, updated directory and generated report together. Verify them with `python3 generation-rules/process_amenities.py --check`; the check requires this report.
