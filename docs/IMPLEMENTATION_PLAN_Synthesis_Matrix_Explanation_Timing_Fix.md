# IMPLEMENTATION PLAN: Synthesis Matrix Explanation Timing Fix & Architecture Hardening

**Objective**: Fix the architectural defect where `MatrixExplanationService` does not receive evidence quotes because `synthesis_distiller.py` filters out cognitive sensor steps before passing execution data to the service. Harden `matrix_explanation_service.py` to eliminate 12 legacy anti-patterns, unify quote truncation under a single SSOT in `settings.py`, fix `hasattr` duck-typing in `synthesis_distiller.py`, update Knowledge Item documentation, and enforce strict compliance with `@[ki_god_code_prevention.md]`.

<required_context_rules>
- @[.agents/rules/00-antigravity-core.md]
- @[.agents/rules/01-python-backend.md]
- @[ki_god_code_prevention.md]
- @[ki_synthesis_payload_compression.md]
</required_context_rules>

## Root Cause Analysis

1. **Filter Starvation at the Caller Site:**
   At `@[backend_v2/services/orchestrator/synthesis_distiller.py#L250-L266]`, incoming `available_dtos` is filtered in-place against `output_profile.layouts[].target_blocks`. Cognitive sensor steps (specifically analyst, profiler, logician, and falsifier) have `block_id` values that are NOT listed in `target_blocks`, so they are discarded before downstream services run.
2. **Downstream Data Deprivation:**
   At `@[backend_v2/services/orchestrator/synthesis_distiller.py#L315]`, `MatrixExplanationService.assemble_matrices_to_explain()` receives the already-filtered list. The `global_quotes_map` is built from an empty set of sensor results, causing all matrices to produce `"No direct evidence quotes extracted for this matrix."`
3. **Anti-Pattern Proliferation:**
   `@[backend_v2/services/orchestrator/matrix_explanation_service.py]` contains 12 legacy anti-patterns (`isinstance` checks on payload dicts, `hasattr` reflection, `getattr` with fallback defaults, `.get()` defaults, and `try/except Exception: continue` catch-alls) that violate `the_zero_compromise_pledge` and `the_duct_tape_ban`.
4. **Scattered Quote Truncation Limits:**
   Quote truncation limits are currently hardcoded as magic numbers (`[:300]`) in `SynthesisPayloadCompressor`, with potential duplication in `MatrixExplanationService`. There must be a single SSOT in `settings.py`.
5. **Duck-Typing at Target Blocks Check:**
   `@[backend_v2/services/orchestrator/synthesis_distiller.py#L257]` uses `hasattr(tb, "value")` instead of strict `isinstance(tb, TargetBlockType)`.

---

## Scope & Target Files

- **[MODIFY]** @[backend_v2/settings.py]
- **[MODIFY]** @[backend_v2/services/orchestrator/synthesis_distiller.py]
- **[MODIFY]** @[backend_v2/services/orchestrator/matrix_explanation_service.py]
- **[MODIFY]** @[backend_v2/services/orchestrator/synthesis_payload_compressor.py]
- **[MODIFY]** @[ki_synthesis_payload_compression.md]
- **[MODIFY]** @[backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py]
- **[NEW]** @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py]

---

## God Code Prevention Compliance (`@[ki_god_code_prevention.md]`)

| Rule | Enforcement in this Plan |
|---|---|
| `anti_god_file_dumping` | `MatrixExplanationService` remains in its dedicated modular file `matrix_explanation_service.py` (<150 lines). No generic dumping grounds. |
| `private_helper_bloat_ban` | Logic is extracted outwards to existing domain services, not downwards into `synthesis_distiller.py` private helpers. |
| `dry_composition_mandate` | Quote truncation is consolidated into a single SSOT (`settings.max_synthesis_quote_length`), eliminating copy-pasted `[:300]` slices. |
| `ast_boundary_verification_mandate` | `synthesis_distiller.py` has 331 lines (>300 line God File threshold). Modifications MUST use verified line bounds before applying edits. |
| `domain_model_purity_mandate` | Pure DTOs (`ConfigDict(strict=True, extra="forbid")`) used across boundaries with no inline database/service logic. |
| `remedial_refactoring_coverage` | Full test suite execution before and after changes via `backend_audit_loop.py`. |

---

## Knowledge Base Constraints (KIs) Applied

1. **`ki_synthesis_payload_compression.md` (Epic 141)**:
   - Validates the role of `MatrixExplanationService` in preparing condensed matrix evidence quotes.
   - Ensures quote truncation length is centrally governed by `settings.max_synthesis_quote_length`.
2. **`ki_god_code_prevention.md` (Epic 133)**:
   - Enforces modular service extraction without adding helper bloat inside `synthesis_distiller.py`.
   - Protects boundaries of files exceeding 300 lines via surgical edits.
3. **`ki_matrix_boolean_evaluation_strictness.md` (Epic 142)**:
   - Ensures that `evaluated_atoms` resolution respects `ExecutionStatus` enum values (`PASSED`, `FAILED`, `N_A`).

---

## User Review Required

> [!IMPORTANT]
> **Single SSOT for Quote Truncation:** We introduce `settings.max_synthesis_quote_length: int = 300` in `backend_v2/settings.py`. Both `SynthesisPayloadCompressor` and `MatrixExplanationService` will use this exact setting. No hardcoded magic numbers `[:300]` will remain in business logic.

> [!IMPORTANT]
> **Method Signature Contract:** `MatrixExplanationService.assemble_matrices_to_explain(available_dtos, title_map, blocks_by_id)` preserves its existing parameter names per `anti_semantic_drift_renaming`.

---

## Implementation Protocol

```xml
<execution_protocol level="0_create_plan">
  <step id="1" name="Centralized Settings SSOT Configuration">
    <action>Modify `@[backend_v2/settings.py#L135-L136]` to add `max_synthesis_quote_length: Annotated[int, Field(description="Maximum character length for evidence quotes in synthesis payloads")] = 300` directly after `max_synthesis_evaluations`.</action>
    <constraint invariant="global_config_sovereignty">
      Hardcoded magic numbers `[:300]` in service files are strictly banned. All quote truncation limits must reference `get_settings().max_synthesis_quote_length`.
    </constraint>
  </step>

  <step id="2" name="Synthesis Distiller Target Block Typing & Two-List Separation">
    <action>Modify `@[backend_v2/services/orchestrator/synthesis_distiller.py#L250-L316]`:</action>
    <action>Import `TargetBlockType` from `backend_v2.models.enums`.</action>
    <action>In `synthesis_distiller_hook` (L252-L259), replace `elif hasattr(tb, "value"):` with strict `elif isinstance(tb, TargetBlockType): target_block_ids.add(tb.value)`.</action>
    <action>Separate available DTOs into two collections: keep `available_dtos` as the complete, unfiltered execution state from `inputs["steps"]`, and create `distilled_dtos = [dto for dto in available_dtos if "*" in target_block_ids or dto.block_id in target_block_ids]`.</action>
    <action>Update alias registration (L290-L294) and `<source>` prompt blocks assembly (L298-L310) to iterate exclusively over `distilled_dtos`.</action>
    <action>Update `MatrixExplanationService.assemble_matrices_to_explain` call (L315) to pass the complete, unfiltered `available_dtos`.</action>
    <constraint invariant="the_zero_compromise_pledge">
      Banning `hasattr(tb, "value")` ensures strict static typing without duck-typing fallback bypasses.
    </constraint>
  </step>

  <step id="3" name="Matrix Explanation Service Hardening Pass">
    <action>Modify `@[backend_v2/services/orchestrator/matrix_explanation_service.py#L1-L145]` to eliminate 12 legacy anti-patterns:</action>
    <action>Import `get_settings` from `backend_v2.settings` globally at module level per `global_settings_import` rule.</action>
    <action>Import `LevelStatsDTO` from `backend_v2.models.dtos.lightweight_matrix`, `I18nText` from `backend_v2.models.v2_core`, and `ValidationError` from `pydantic`.</action>
    <action>In `global_quotes_map` extraction: use `get_settings().max_synthesis_quote_length` for truncation; extract `source_quote` from `AtomResultDTO` or via `AtomResultDTO.model_validate(atom_dict, strict=False)`; append quotes to a list per `tda_id`; catch strictly `(ValidationError, ValueError)` instead of broad `except Exception:`.</action>
    <action>In prompt block category lookup: replace `.get(block_id)` with explicit membership lookup `pb = blocks_by_id[block_id] if block_id in blocks_by_id else None`.</action>
    <action>In claim label resolution: replace `hasattr(claim.label, "resolve")` with strict typed check `claim.label.resolve("en") if isinstance(claim.label, I18nText) else str(claim.label)`.</action>
    <action>In atom hit status resolution: eliminate `getattr(hit_status, "value", hit_status)` and resolve strictly via `hit_status.value if isinstance(hit_status, ExecutionStatus) else str(hit_status)`, skipping `ExecutionStatus.N_A.value`.</action>
    <action>In level stats resolution: eliminate `getattr(stats, "hits", 0)` and `.get("hits", 0)`, replacing with strict typed `isinstance(stats, LevelStatsDTO)` and `isinstance(stats, dict)` branches.</action>
    <action>In title map resolution: replace `.get()` with explicit lookup `title_map[block_id.lower()] if block_id.lower() in title_map else block_id`.</action>
    <constraint invariant="the_duct_tape_ban">
      Zero tolerance for silent fallbacks, generic dictionary `getattr`, or broad catch-all exception swallowing.
    </constraint>
  </step>

  <step id="4" name="Synthesis Payload Compressor SSOT Alignment">
    <action>Modify `@[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L118-L123]` to replace hardcoded `[:300]` with `settings.max_synthesis_quote_length`.</action>
    <constraint invariant="dry_composition_mandate">
      Ensure single source of truth for synthesis quote truncation across all orchestrator services.
    </constraint>
  </step>

  <step id="5" name="Knowledge Base Alignment">
    <action>Update `@[ki_synthesis_payload_compression.md]` to replace references to `ExtractiveSensorService` with the SSOT `MatrixExplanationService`, and document centralized quote truncation via `settings.max_synthesis_quote_length`.</action>
  </step>

  <step id="6" name="Unit & Regression Test Coverage Expansion">
    <action>Update `@[backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py]` with negative and boundary tests: quote truncation at max setting, quotes extraction from unfiltered sensor steps, strict level stats breakdown, and no broad exceptions.</action>
    <action>Create `@[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py]` to test that `synthesis_distiller_hook` passes unfiltered `available_dtos` to `MatrixExplanationService` while distilling `inputs["steps"]` for prompt `<source>` blocks, and parses `TargetBlockType` enums without `hasattr`.</action>
  </step>
</execution_protocol>
```

---

## Verification Plan

### Automated Tests
1. **Matrix Explanation Service Unit Tests:**
   `uv run pytest backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py`
2. **Synthesis Distiller Wiring Unit Tests:**
   `uv run pytest backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py`
3. **Orchestrator Backend Audit Loop:**
   `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test`

### Anti-Happy-Path Scenarios
- **Scenario A (Unfiltered Sensor Quotes Extraction):** Sensor step with `data_type="text"` producing `results=[AtomResultDTO(tda_id="a1", source_quote="Sensor Evidence")]`, cross-referenced by a matrix step with `evaluated_atoms={"a1": "PASSED"}`.
  - *Expected Output:* Matrix justification contains `"Sensor Evidence"`.
- **Scenario B (Quote Truncation Boundary):** Provide a 500-character evidence quote.
  - *Expected Output:* Truncated deterministically to exactly `settings.max_synthesis_quote_length` (300 characters).
- **Scenario C (Missing / Unknown Block ID):** Provide a step with a `block_id` not present in `blocks_by_id`.
  - *Expected Output:* Handles the absence cleanly without `getattr` fallbacks or broad exception masking.
- **Scenario D (Strict TargetBlockType Enum Resolution):** Pass `target_blocks` containing both `str` and `TargetBlockType` instances.
  - *Expected Output:* Resolves all target block IDs cleanly without triggering `hasattr`.

### Manual Verification
- Run local pipeline (`.\run_local.bat`) and verify in `client_debug.log` and `backend_debug.log` that the synthesis report matrix-level justifications contain authentic quotes from sensor steps without producing `"No direct evidence quotes extracted for this matrix."`
