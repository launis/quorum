# Phase 5: Documentation Update

**Source:** Epic Phase 5 (Documentation Update)

## Objective
Update the architecture documentation to reflect the new granular TDA assertion structures.

## Scope
- **TARGET (Modify):**
  - `docs/architecture/02_domain_models.md`
  - `docs/architecture/06_evaluation_and_scoring.md`

## Implementation Steps
1. Open `02_domain_models.md`.
2. Update the `TDAAssertion` schema documentation to explicitly define `anchor_target`, `bounding_box_scope`, and `extraction_rule`.
3. Open `06_evaluation_and_scoring.md`.
4. Update the section detailing "Pearl's Rung 3" and the `localization_compiler.py` XML structures to show the new `<tda_validation>` format instead of raw string parsing.

## Testing & Quality Gate Plan
- Manual review of the markdown files to ensure accurate reflection of the current system state.

---
### Session Handover
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/epic_tda_granular_schema_refactor_tracker.md`
