# Phase 1: Workflow Prerequisite & OutputProfile Data Model Pruning

> **Source**: Epic 106 — Phase 0, Phase 1, Phase 1.5
> **Domain**: Backend (Python)

## Goal

Add `allowed_exports` and `historical_context_mode` fields to the `Workflow` model (prerequisite for Phase 2.5), then prune `synthesis`, `formatting_directives`, and `matrix_column_labels` from `OutputProfile`, `EmbeddedOutputProfile`, and all corresponding DTOs. Simultaneously scrub seed data and test fixtures.

## Architectural Invariants (Injected)

- `strict_pydantic_v2_rust`: All models use `ConfigDict(extra='forbid', strict=True)`. Removing a field crashes any consumer still sending it.
- `zero_legacy_fallback_hacks`: No `@model_validator(mode="before")` to silently strip removed fields.
- `sdui_contract_fracture_prevention`: Backend Pydantic deletions MUST be paired with Flutter Freezed updates (deferred to Phase 3).
- `anti_tdd_trap`: Legacy tests asserting `synthesis` or `formatting_directives` on OutputProfile MUST be rewritten, not preserved.
- `zero_defaults_mandate`: New `Workflow.allowed_exports` MUST NOT use mutable default list; seed data must explicitly define the value.
- `pydantic_annotated_fields_mandate`: New fields must use PEP 593 `Annotated` syntax.

## Pre-Execution Baseline

Before modifying ANY file, the executing agent MUST:
1. Run `uv run python scripts/backend_audit_loop.py backend_v2/ --test`
2. Record the passing test count and coverage as `[BASELINE]` metric.

---

## Milestone 1.1: Add Workflow-Level Configuration Fields

**Source**: Epic 106, Phase 0

### TARGET (Modify): [v2_core.py](file:///c:/src/quorum/backend_v2/models/v2_core.py)

Add two new fields to the `Workflow` class (after `steps`, line ~1409):

```python
allowed_exports: Annotated[
    list[Literal["pdf", "docx", "raw_json"]],
    Field(description="Supported export file formats for this workflow."),
]
historical_context_mode: Annotated[
    LaxHistoricalContextMode,
    Field(description="Mode for fetching historical context at workflow level."),
]
```

**CRITICAL**: Per `zero_defaults_mandate`, these fields MUST NOT have default values. The seed data MUST explicitly provide them.

### CONTEXT (Read-Only):
- `backend_v2/models/enums.py` — `LaxHistoricalContextMode` already defined.

---

## Milestone 1.2: Prune OutputProfile Domain Models

**Source**: Epic 106, Phase 1

### TARGET (Modify): [v2_core.py](file:///c:/src/quorum/backend_v2/models/v2_core.py)

#### On `OutputProfile` class (line ~1261):
- **DELETE** field `formatting_directives` (line 1274)
- **DELETE** field `synthesis` (line 1300-1302)
- **DELETE** field `matrix_column_labels` (line 1312-1314)

#### On `EmbeddedOutputProfile` class (line ~1317):
- **DELETE** field `formatting_directives` (line 1326)
- **DELETE** field `synthesis` (line 1350-1352)
- **DELETE** field `matrix_column_labels` (line 1362-1364)

#### Retained Fields (Explicitly NOT Touched):
- `layouts`, `content_blocks`, `visible_block_extensions`, `visible_workflow_extensions`, `display_scale`, `max_extension_items`, `tone_instruction`, `name`, `description`, `custom_preface`, `language`, `visible_metadata`, `include_diagnostic_scorecard`, `strictness_level`, `scoring_strategy`

#### `__all__` Export Audit:
- `SynthesisConfigDTO` remains in `__all__` (line 74) — it is still consumed by `OutputLayoutBlock.synthesis`, `ReportLayoutDTO.synthesis`, and `SynthesisDistiller`.

---

## Milestone 1.3: Prune OutputProfile DTOs

**Source**: Epic 106, Phase 1

### TARGET (Modify): [output_profile.py](file:///c:/src/quorum/backend_v2/models/dtos/output_profile.py)

#### On `OutputProfileCreateDTO` (line ~20):
- **DELETE** field `formatting_directives` (line 61-63)
- **DELETE** field `synthesis` (line 98-100)
- **DELETE** field `matrix_column_labels` (line 115-118)

#### On `OutputProfileUpdateDTO` (line ~121):
- **DELETE** field `formatting_directives` (line 152-154)
- **DELETE** field `synthesis` (line 190-192)
- **DELETE** field `matrix_column_labels` (line 207-210)

#### On `OutputProfileResponseDTO` (line ~213):
- **DELETE** field `formatting_directives` (line 243)
- **DELETE** field `synthesis` (line 252)
- **DELETE** field `matrix_column_labels` (line 260)

#### Import Cleanup:
- Remove `SynthesisConfigDTO` from the import on line 16 IF no remaining field references it. After deletion, verify: `OutputLayoutBlock` (retained in `layouts` field) still imports `SynthesisConfigDTO` via its own type — but the DTO file's import of `SynthesisConfigDTO` on line 16 is only used by the `synthesis` field on the DTOs. If no DTO field remains that uses `SynthesisConfigDTO`, remove the import.

### CONTEXT (Read-Only):
- [lightweight_matrix.py](file:///c:/src/quorum/backend_v2/models/dtos/lightweight_matrix.py) — `OutputProfileConfig` only has `visible_block_extensions` and `visible_workflow_extensions`. No changes needed.

---

## Milestone 1.4: Seed Data Pruning

**Source**: Epic 106, Phase 1 (Development Phase Clean Slate Wipe)

### TARGET (Modify): [seed_data.json](file:///c:/src/quorum/backend_v2/seed/seed_data.json)

1. In the `output_profiles` array, **DELETE** the keys:
   - `"formatting_directives"` (found at lines ~7867 and ~9122)
   - `"synthesis"` (entire nested object)
   - `"matrix_column_labels"` (if present)

2. In the `workflows` array, for each workflow object, **ADD** two new fields:
   - `"allowed_exports": ["pdf", "raw_json"]`
   - `"historical_context_mode": "SLIDING_WINDOW_3"` (or `"DISABLED"` for secondary workflows)

3. **Verify** all `steps[].expected_sdui_type` values exist in the workflow definitions (Epic 105 prerequisite).

After modification: `uv run python backend_v2/seed/run_seed.py local`

---

## Milestone 1.5: Test Mock Migration

**Source**: Epic 106, Phase 1.5

### TARGET (Modify):

The following test files contain `synthesis` or `formatting_directives` in OutputProfile mock data and MUST be scrubbed:

1. [test_api_clone_endpoints.py](file:///c:/src/quorum/backend_v2/tests/unit/test_api_clone_endpoints.py) — Lines 23, 97-99: Remove `SynthesisConfigDTO` import and `synthesis=SynthesisConfigDTO(...)` from mock.
2. [test_output_profile.py](file:///c:/src/quorum/backend_v2/tests/unit/models/domain/test_output_profile.py) — Lines 3, 6: Update import and assertion if `SynthesisConfigDTO` is no longer re-exported from `output_profile` domain module.
3. [test_worker_synthesis.py](file:///c:/src/quorum/backend_v2/tests/unit/test_worker_synthesis.py) — Line 107: Remove `historical_context_mode` from mock data if it references the OutputProfile-level synthesis config.
4. [test_blueprint.py](file:///c:/src/quorum/backend_v2/tests/unit/services/test_blueprint.py) — Scrub any `synthesis` or `formatting_directives` keys from OutputProfile mock dicts.
5. All other test files touching `OutputProfile` mock data — run `grep_search` for `formatting_directives` and `"synthesis"` in `backend_v2/tests/`.

### CONTEXT (Read-Only):
- [models/domain/output_profile.py](file:///c:/src/quorum/backend_v2/models/domain/output_profile.py) — Update re-exports if necessary (currently re-exports `SynthesisConfigDTO`; keep it since `SynthesisConfigDTO` still exists for `OutputLayoutBlock.synthesis`).

---

## Atomic Commit Mandate

Per Epic 106 Phase 1.5: Milestones 1.2 + 1.3 + 1.4 + 1.5 MUST be committed atomically. The model changes, seed data changes, and test mock changes cannot be deployed independently without causing `ValidationError` crashes.

Milestone 1.1 (Workflow fields) can be committed first independently, since it only adds new fields.

---

## Testing & Quality Gate Plan

1. After Milestone 1.1: Run `uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py --test`
2. After Milestones 1.2-1.5 (atomic):
   - Run database reset: `uv run python backend_v2/seed/run_seed.py local`
   - Run full backend audit: `uv run python scripts/backend_audit_loop.py backend_v2/ --test`
   - Verify all existing tests pass with the scrubbed fixtures.
3. Expected: Some test count may drop if legacy tests are deleted per `anti_tdd_trap`.

---

## Documentation Mandate

After completing all milestones, update:
- `docs/architecture/` relevant documentation to reflect the pruned OutputProfile schema.
- `.agents/rules/04_directory_reference.md` — No structural changes needed (no new directories).

---

## Session Handover

```
Achieved: Phase 1 complete — Workflow prerequisites added, OutputProfile domain/DTO/seed pruned, test mocks migrated.
Learned: SynthesisConfigDTO still lives in v2_core.py for OutputLayoutBlock.synthesis and ReportLayoutDTO.synthesis.
Remaining: Phase 2 (SchemaFactory + PromptCompiler), Phase 2.5 (Worker migration), Phase 3 (Flutter).
```
