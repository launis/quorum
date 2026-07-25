# EPIC 115 Phase 2: Dual-Axis Documentation Paradigm

Phase 2 introduces the new Meta README and hardens core rules.
Source: Epic Phase 2, Tasks 2.1, 2.2, 2.3, 2.5

## TARGET Files (Modify)
- @[c:\src\quorum\docs\architecture\00_README_META_ARCHITECTURE.md]
- @[c:\src\quorum\.agents\workflows\tier7-describe-architecture.md]
- @[c:\src\quorum\.agents\rules\00-antigravity-core.md]
- @[c:\src\quorum\.agents\rules\04_directory_reference.md]

## Proposed Changes

### docs/architecture/00_README_META_ARCHITECTURE.md
- [ ] [NEW] Create the Meta-Governance Document.
- [ ] Add content covering:
  1. The Dual-Axis Documentation Paradigm
  2. The Purpose (6 pillars of Capability-Driven Architecture, timeless, stateless)
  3. The Golden Rule (Timelessness - ban Epic IDs, dates, historical comparisons)
  4. Not a Pillar (00 is meta, 01-06 are the 6 pillars)
  5. How to Update (Continuous Integration via Tier 7: KI updates -> Tier 7 syncs narrative; physical paths strictly in `04_directory_reference.md`).

### .agents/workflows/tier7-describe-architecture.md
- [ ] [MODIFY] Add `<rule_block id="timeless_as_built_mandate">` to `<architectural_invariants>`. Ensure the exact text from Task 2.2 in Epic 115 is used.
- [ ] [MODIFY] Update `<step id="5">` to explicitly mention running timelessness cleanup while modifying theory.

### .agents/rules/00-antigravity-core.md
- [ ] [MODIFY] Add `<rule_block id="dual_axis_documentation_mandate">` to `<ide_orchestration_protocol>`.
- [ ] Define AI vs Human boundary.
- [ ] Forbid direct edits to `docs/architecture/01_` through `06_`.
- [ ] Route updates through KI creation + Tier 7.
- [ ] Permit direct edits to `04_directory_reference.md` and `00_README_META_ARCHITECTURE.md`.

### .agents/rules/04_directory_reference.md
- [ ] [MODIFY] Add `00_README_META_ARCHITECTURE.md` as a meta-governance document under `docs/architecture/` module path.

## Testing & Quality Gate Plan
- Trigger `/tier7-describe-architecture` to confirm functionality.
