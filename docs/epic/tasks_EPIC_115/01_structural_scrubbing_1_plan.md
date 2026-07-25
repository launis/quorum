# EPIC 115 Phase 1: Structural Scrubbing (Pillars 1-3)

Phase 1 MUST be purely structural. No new features.
Source: Epic Phase 1, Tasks 1.1 & 1.2

## TARGET Files (Modify)
- @[c:\src\quorum\docs\architecture\01_system_context_and_invariants.md]
- @[c:\src\quorum\docs\architecture\02_data_seeding_and_ontology.md]
- @[c:\src\quorum\docs\architecture\03_cognitive_orchestration_engine.md]

## CONTEXT Files (Read-Only)
- @[c:\src\quorum\.agents\rules\04_directory_reference.md]
- @[c:\src\quorum\docs\epic\EPIC_115_timeless_architecture_documentation.md]

## Proposed Changes

### docs/architecture/01_system_context_and_invariants.md
- [x] Synthesize any exclusive conceptual knowledge from the "Physical Implementation Map" into the theoretical sections.
- [x] Remove the "Physical Implementation Map" section entirely.
- [x] Remove all historical references (Epic IDs, dates, migration language, legacy/backward compatibility comparisons).
- [x] Ensure no inline physical file paths remain in theoretical text.

### docs/architecture/02_data_seeding_and_ontology.md
- [x] Synthesize any exclusive conceptual knowledge from the "Physical Implementation Map" into the theoretical sections.
- [x] Remove the "Physical Implementation Map" section entirely.
- [x] Remove all historical references.
- [x] Specifically on Line 20 (or matching sentence): Replace the sentence containing 4 violations (`from V1 to V2 paradigms`, `backward compatibility`, `older JSON definitions`, `legacy parsing logic`) with: `"The system uses a Y-Funnel architecture where Pre-Hooks perform structural data normalization *before* data enters the domain validation phase. This ensures heterogeneous JSON definitions are canonicalized into strict Pydantic V2 Domain Models without polluting the domain layer with transformation logic."`
- [x] Remove inline paths in Section 2.5 (`backend_v2/models/v2_core.py` and `client_app_v2/lib/shared/models/i18n_text.dart`) and verify coverage in `04_directory_reference.md`.

### docs/architecture/03_cognitive_orchestration_engine.md
- [x] Synthesize any exclusive conceptual knowledge from the "Physical Implementation Map" into the theoretical sections.
- [x] Remove the "Physical Implementation Map" section entirely.
- [x] Remove all historical references.
- [x] Ensure no inline physical file paths remain in theoretical text.

## Testing & Quality Gate Plan
- Ensure Universal Quality Gate is respected. (Documentation only, so no domain tests needed).
- Verify removal of temporal contamination using `grep_search`.
