# IMPLEMENTATION PLAN: Synthesis Matrix Explanation Timing Fix & Architecture Hardening

**Objective**: Fix the architectural defect where `synthesis_distiller.py` conflates SDUI Presentation Layout filtering (`target_blocks`) with LLM Synthesis Context, starving both `MatrixExplanationService` (zero evidence quotes) and the LLM prompt's `<source>` blocks (`distilled_inputs` losing all cognitive sensor findings). Eliminate the illegitimate `target_blocks` filter loop in `synthesis_distiller.py`, harden `matrix_explanation_service.py` to eliminate 12 legacy anti-patterns, unify quote truncation and quote count limits under centralized SSOT settings (`max_synthesis_quote_length` = 300, `max_synthesis_quotes_per_matrix` = 5) in `settings.py` to eliminate LLM Context Window Saturation risks, eliminate $O(N)$ settings lookup overhead via method-level hoisting, enforce strict multi-language support by requiring mandatory `target_locale: str` (Zero Backwards Compatibility), update Knowledge Item documentation, and enforce strict compliance with `@[ki_god_code_prevention.md]`.

<required_context_rules>
- @[.agents/rules/00-antigravity-core.md]
- @[.agents/rules/01-python-backend.md]
- @[ki_god_code_prevention.md]
- @[ki_synthesis_payload_compression.md]
- @[ki_matrix_boolean_evaluation_strictness.md]
- @[ki_dual_axis_localization_architecture.md]
</required_context_rules>

## Root Cause Analysis

1. **Conflation of SDUI Presentation Filtering with Cognitive Synthesis Context:**
   In `@[backend_v2/services/orchestrator/synthesis_distiller.py#L159-L330]`, incoming `available_dtos` from `inputs["steps"]` was filtered in-place against `output_profile.layouts[].target_blocks`. Per `@[backend_v2/models/v2_core.py#L1270-L1308]`, `target_blocks` is strictly an SDUI layout directive ("Optional explicit block IDs to plot, filtering and ordering the axes") for frontend widgets and matrix charts. Cognitive sensor steps (analyst, profiler, logician, falsifier, fact checker, performativity detector, archivist, judge, coach, causal analyst) are upstream analysis nodes whose `block_id` values are never in `target_blocks`.
2. **Dual Context Deprivation:**
   - **Downstream Matrix Quotes Deprivation:** `MatrixExplanationService.assemble_matrices_to_explain()` received the pruned list. The `global_quotes_map` was built from an empty set of sensor results, causing all matrices to produce `"No direct evidence quotes extracted for this matrix."`
   - **LLM `<source>` Context Deprivation:** `consolidated_distilled_parts` (`distilled_inputs`) iterated over the pruned list. Consequently, `<source id="DOC-X">` blocks passed into the LLM prompt's `DATA TO SYNTHESIZE` contained only boolean matrix results, completely stripping all cognitive sensor findings, exact quotes, and semantic reasoning from the synthesis prompt.
3. **Anti-Pattern Proliferation & Hardcoded Language:**
   `@[backend_v2/services/orchestrator/matrix_explanation_service.py#L15-L145]` contains 12 legacy anti-patterns (`isinstance` checks on payload dicts, `hasattr` reflection, `getattr` with fallback defaults, `.get()` defaults, and `try/except Exception: continue` catch-alls) that violate `the_zero_compromise_pledge` and `the_duct_tape_ban`. Additionally, `claim.label.resolve("en")` hardcodes English, violating the Dual-Axis Localization architecture.
4. **$O(N)$ Settings Overhead & Scattered Limits:**
   Quote truncation limits are currently hardcoded as magic numbers (`[:300]`) in `SynthesisPayloadCompressor`, with potential duplication in `MatrixExplanationService`. Calling `get_settings()` repeatedly inside nested iteration loops introduces unnecessary function and cache overhead. Both quote character length and per-matrix quote counts must be centralized in `Settings` and hoisted at the method entry.
5. **TypeError Hazard on Null Quotes (`source_quote: str | None`):**
   In `@[backend_v2/models/v2_core.py#L1127-L1160]`, `AtomResultDTO.source_quote` is nullable (`str | None`), especially when `contextual_override: True` forces `source_quote = None` or when an atom evaluation produces no verbatim quote. Attempting to measure length (`len(quote)`) or slice directly (`quote[:max_quote_len]`) without an explicit `None`-check (`quote-guard`) crashes the synthesis pipeline with `TypeError: object of type 'NoneType' has no len()` or `TypeError: 'NoneType' object is not subscriptable`.
6. **Token Shielding SSOT:**
   Context Window Saturation must be prevented through `SynthesisPayloadCompressor` (which strips internal AI bloat, enforces `max_synthesis_evaluations`, and truncates quotes to `max_synthesis_quote_length`), rather than by amputating cognitive sensor steps at the distiller.
7. **Missing Pydantic Validation Error Handling for Matrix Outputs (`LightweightMatrixOutput.model_validate`):**
   In `@[backend_v2/services/orchestrator/matrix_explanation_service.py#L85-L89]`, `LightweightMatrixOutput.model_validate(payload_to_validate, strict=False)` is executed without a `try/except` block. Because `LightweightMatrixOutput` enforces `model_config = ConfigDict(strict=True, extra="forbid")`, any unexpected payload format (such as malformed dicts from upstream failures, unanticipated extra keys beyond popped `results`, or invalid numerical ranges) will raise an unhandled `ValidationError` or `ValueError`, crashing the entire `MatrixExplanationService` and terminating the synthesis pipeline.
8. **AttributeError Hazard on Nullable Level Breakdown (`level_breakdown: dict[str, dict[str, int]] | None`):**
   In `@[backend_v2/models/dtos/lightweight_matrix.py#L55]`, `LightweightMatrixOutput.level_breakdown` is typed as `dict[str, dict[str, int]] | None = None`. In non-hierarchical matrices, sensor steps, or payloads without computed breakdowns, `level_breakdown` is `None`. Directly executing `for lvl, stats_raw in lw_matrix.level_breakdown.items():` without an explicit `if lw_matrix.level_breakdown:` check raises `AttributeError: 'NoneType' object has no attribute 'items'`, crashing matrix explanation assembly during synthesis.

---

## Scope & Target Files

- **[MODIFY]** @[backend_v2/settings.py]
- **[MODIFY]** @[backend_v2/services/orchestrator/synthesis_distiller.py]
- **[MODIFY]** @[backend_v2/services/orchestrator/matrix_explanation_service.py]
- **[MODIFY]** @[backend_v2/services/orchestrator/synthesis_payload_compressor.py]
- **[MODIFY]** @[ki_synthesis_payload_compression.md]
- **[MODIFY]** @[backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py]
- **[MODIFY]** @[backend_v2/tests/unit/test_epic93_contract_verification.py]
- **[NEW]** @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py]

---

## God Code Prevention Compliance (`@[ki_god_code_prevention.md]`)

| Rule | Enforcement in this Plan |
|---|---|
| `anti_god_file_dumping` | `MatrixExplanationService` remains in its dedicated modular file `matrix_explanation_service.py` (<160 lines). No generic dumping grounds. |
| `private_helper_bloat_ban` | Logic is extracted outwards to existing domain services, not downwards into `synthesis_distiller.py` private helpers. |
| `dry_composition_mandate` | Quote truncation and count limits are consolidated into centralized SSOT settings (`max_synthesis_quote_length`, `max_synthesis_quotes_per_matrix` in `Settings`), eliminating copy-pasted `[:300]` slices and preventing prompt context blowup. |
| `ast_boundary_verification_mandate` | `synthesis_distiller.py` has 331 lines (>300 line God File threshold). Modifications MUST use verified line bounds before applying edits. |
| `domain_model_purity_mandate` | Pure DTOs (`ConfigDict(strict=True, extra="forbid")`) used across boundaries with no inline database/service logic. |
| `remedial_refactoring_coverage` | Full test suite execution before and after changes via `backend_audit_loop.py`. |

---

## Knowledge Base Constraints (KIs) Applied

1. **`ki_synthesis_payload_compression.md` (Epic 141)**:
   - Validates the role of `MatrixExplanationService` in preparing condensed matrix evidence quotes.
   - Enforces centralized quote character limits via `max_synthesis_quote_length` (300) and quote count limits via `max_synthesis_quotes_per_matrix` (5) in `Settings`.
2. **`ki_god_code_prevention.md` (Epic 133)**:
   - Enforces modular service extraction without adding helper bloat inside `synthesis_distiller.py`.
   - Protects boundaries of files exceeding 300 lines via surgical edits.
3. **`ki_matrix_boolean_evaluation_strictness.md` (Epic 142)**:
   - Ensures that `evaluated_atoms` resolution respects `ExecutionStatus` enum values (`PASSED`, `FAILED`, `N_A`).
4. **`ki_dual_axis_localization_architecture.md`**:
   - Enforces semantic backend translation (Axis 2) by passing mandatory `target_locale: str` through `assemble_matrices_to_explain` to resolve claim labels without hardcoded `"en"`.

---

## User Review Required

> [!IMPORTANT]
> **Complete Cognitive Preservation in `<source>` Prompt Blocks:**
> We remove the illegitimate `target_blocks` filter in `synthesis_distiller.py`. All upstream execution steps in `inputs["steps"]` (both cognitive sensor steps and matrix steps) flow into `SynthesisPayloadCompressor` to generate `<source id="DOC-X">` blocks. This ensures the LLM receives the full analytical context (analyst, profiler, logician, falsifier, etc.). Token context bounds are strictly protected by `SynthesisPayloadCompressor` using `max_synthesis_evaluations` and `max_synthesis_quote_length`.

> [!IMPORTANT]
> **Single SSOT for Quote Limits & Context Shielding:**
> We introduce two centralized configuration variables in `backend_v2/settings.py`:
> 1. `max_synthesis_quote_length: int = 300` (caps individual quote character length).
> 2. `max_synthesis_quotes_per_matrix: int = 5` (caps the number of evidence quotes and fallback claims collected per matrix).
> Both `SynthesisPayloadCompressor` and `MatrixExplanationService` will strictly reference these settings, eliminating hardcoded magic numbers and safeguarding against Context Window Saturation during LLM synthesis.

> [!IMPORTANT]
> **Zero Backwards Compatibility (No Optional Defaults):**
> `MatrixExplanationService.assemble_matrices_to_explain` strictly requires `target_locale: str` as a mandatory parameter:
> `assemble_matrices_to_explain(available_dtos: list[StepOutputDTO], title_map: dict[str, str], blocks_by_id: dict[str, PromptBlock], target_locale: str) -> list[MatrixExplanationContextDTO]`.
> All callers (including `synthesis_distiller.py` and all unit test suites) MUST provide `target_locale`. No optional `= None` fallbacks or legacy duck typing allowed.

---

## Implementation Protocol

```xml
<execution_protocol level="0_create_plan">
  <step id="0" name="AST Boundary Verification Pre-Step (God File Mandate)">
    <action>`@[backend_v2/services/orchestrator/synthesis_distiller.py#L159-L330]` is 331 lines (exceeds 300-line God File threshold). Before making ANY edits, write and execute a temporary Python `ast` script in the `scratch/` directory to extract the exact `lineno` and `end_lineno` of the `synthesis_distiller_hook` function. Use these mathematically verified bounds for all subsequent edits.</action>
    <constraint invariant="ast_boundary_verification_mandate">
      Per `@[ki_god_code_prevention.md]`: You MUST NOT rely on `grep_search` to find method boundaries in files exceeding 300 lines.
    </constraint>
  </step>

  <step id="1" name="Centralized Settings SSOT">
    <action>Modify `@[backend_v2/settings.py#L42-L599]` to add two centralized SSOT settings in `Settings` directly after `max_synthesis_evaluations`:</action>
    <action>1. `max_synthesis_quote_length: Annotated[int, Field(description="Maximum character length for evidence quotes in synthesis payloads")] = 300`</action>
    <action>2. `max_synthesis_quotes_per_matrix: Annotated[int, Field(description="Maximum number of evidence quotes per matrix in synthesis explanation context")] = 5`</action>
    <constraint invariant="global_config_sovereignty">
      Hardcoded magic numbers `[:300]` in service files are strictly banned. All quote truncation and count limits must reference `max_synthesis_quote_length` and `max_synthesis_quotes_per_matrix` in `Settings`.
    </constraint>
    <mutation_note>REMOVED: The original plan proposed adding `I18nText.__str__()` in this step. Red-Team analysis proved this was a hallucinated dependency with uncontrolled blast radius — the `str()` call at `matrix_explanation_service.py#L53` operates on `atom_res.source_quote` (type `str | None`), NOT on `I18nText`. The plan already uses `claim.label.resolve(target_locale)` for localization.</mutation_note>
  </step>

  <step id="2" name="Synthesis Distiller Target Block Pruning & Unfiltered Context Pipeline">
    <action>Modify `@[backend_v2/services/orchestrator/synthesis_distiller.py#L159-L330]`:</action>
    <action>DELETE the flawed `target_blocks` filter loop (lines 252-266) that discarded cognitive sensor steps.</action>
    <action>Ensure `available_dtos` (the complete, unfiltered execution state from `inputs["steps"]`) is passed directly to alias registration, `<source>` prompt blocks assembly, and `MatrixExplanationService.assemble_matrices_to_explain`.</action>
    <action>In `synthesis_distiller_hook`, update `<source>` prompt block generation to iterate over all `available_dtos`, compressing each step payload via `SynthesisPayloadCompressor.compress_synthesis_payload` so that all cognitive sensor evaluations and matrix results are preserved in `distilled_inputs`.</action>
    <action>Update `MatrixExplanationService.assemble_matrices_to_explain` call to pass `available_dtos`, `title_map`, `blocks_by_id`, and mandatory `target_locale=language`.</action>
    <constraint invariant="the_zero_compromise_pledge">
      Eliminating the flawed presentation layout filter ensures full cognitive context is preserved for LLM synthesis without ad-hoc dictionary hacks or data deprivation.
    </constraint>
  </step>

  <step id="3" name="Matrix Explanation Service Hardening & Zero-Legacy Modernization">
    <action>Modify `@[backend_v2/services/orchestrator/matrix_explanation_service.py#L15-L145]`:</action>
    <action>Import `logger` from `loguru`, `ErrorCodes` from `backend_v2.exceptions`, and `get_settings` from `backend_v2.settings` globally at module level per `global_settings_import` rule.</action>
    <action>Import `LevelStatsDTO`, `LightweightMatrixOutput` from `backend_v2.models.dtos.lightweight_matrix`, `I18nText` from `backend_v2.models.v2_core`, `PromptBlockCategory` from `backend_v2.models.enums`, and `ValidationError` from `pydantic`.</action>
    <action>Update signature to mandate `target_locale: str`: `def assemble_matrices_to_explain(available_dtos: list[StepOutputDTO], title_map: dict[str, str], blocks_by_id: dict[str, PromptBlock], target_locale: str) -> list[MatrixExplanationContextDTO]`.</action>
    <action>Hoist settings at method start: `settings_obj = get_settings()`, `max_quote_len = settings_obj.max_synthesis_quote_length`, `max_quotes_per_matrix = settings_obj.max_synthesis_quotes_per_matrix` to eliminate O(N) lookup overhead and enforce strict Fail-Fast attribute access without fallback defaults.</action>
    <action>In `global_quotes_map` extraction: accept both direct `AtomResultDTO` instances and `dict` payloads; validate dictionaries via `AtomResultDTO.model_validate(atom_dict, strict=False)`; on `(ValidationError, ValueError)` catch, execute `logger.warning("[MatrixExplanationService] %s: Failed to parse atom result in step '%s' (block '%s'): %s", ErrorCodes.VALIDATION_FAILED.name, dto.step_id, dto.block_id, str(e), exc_info=True)` before continuing; extract `source_quote` from `AtomResultDTO` with a strict `None`-guard (`if atom_res.source_quote: quotes.append(atom_res.source_quote[:max_quote_len])`), avoiding `TypeError` on nullable quotes, and append non-empty quotes to `global_quotes_map[atom_res.tda_id]`.</action>
    <action>In matrix payload validation: wrap `LightweightMatrixOutput.model_validate(payload_to_validate, strict=False)` in a `try...except (ValidationError, ValueError) as e:` block; on catch, execute `logger.warning("[MatrixExplanationService] %s: Failed to parse matrix output in step '%s' (block '%s'): %s", ErrorCodes.VALIDATION_FAILED.name, step_dto_obj.step_id, block_id, str(e), exc_info=True)` and `continue` before proceeding to atom evaluations, preventing unhandled schema validation exceptions on malformed matrix dictionaries from killing the synthesis aggregation.</action>
    <mutation_note>REVIEWED EXCEPTION to `the_duct_tape_ban`: The `except (ValidationError, ValueError): continue` blocks are PROBE BOUNDARIES — code iterates ALL `StepOutputDTO` instances (text, matrix, sensor) and probes `payload.results` for atom data and `payload` for matrix data. The `payload` field is `Any`-typed. Not every step carries valid `AtomResultDTO` or `LightweightMatrixOutput` payloads. Crashing Fail-Fast on an upstream malformed step during distillation would kill the entire synthesis. The executing agent MUST add inline `# REVIEWED EXCEPTION to the_duct_tape_ban:` comments documenting this justification.</mutation_note>
    <action>In prompt block category lookup: eliminate `.get(block_id)` and nullable assignment; enforce strict non-nullable guard via `if block_id not in blocks_by_id: continue` followed by `pb = blocks_by_id[block_id]` and `if pb.category_id != PromptBlockCategory.MATRIX: continue`.</action>
    <action>In claim label resolution: strictly resolve text using `claim.label.resolve(target_locale)` (Zero hardcoded "en", Zero hasattr duck-typing). Remove `hasattr(claim.label, "resolve")` guard entirely — `claim.label` is always `I18nText` per Pydantic schema, so `.resolve()` is guaranteed to exist.</action>
    <action>In atom hit status resolution: DELETE the entire `getattr(hit_status, "value", hit_status) == ExecutionStatus.N_A.value` check. The `evaluated_atoms` field type is `dict[str, LaxExecutionStatus]` in `@[backend_v2/models/dtos/lightweight_matrix.py#L37-L67]` where `LaxExecutionStatus = Annotated[ExecutionStatus, Field(strict=False)]`. After `model_validate(strict=False)`, values are ALREADY `ExecutionStatus` enums. The existing `if hit_status == ExecutionStatus.N_A: continue` is correct and sufficient. No `isinstance` or `.value` extraction needed.</action>
    <action>In level stats resolution: the `level_breakdown` field type is `dict[str, dict[str, int]] | None` (NOT `dict[str, LevelStatsDTO]`). Values are plain `dict[str, int]`. To prevent `AttributeError: 'NoneType' object has no attribute 'items'` on matrices where `level_breakdown` is `None`, enclose iteration inside an explicit `if lw_matrix.level_breakdown:` guard. Inside the loop, perform UNCONDITIONAL `LevelStatsDTO.model_validate(stats_raw, strict=False)` — eliminating BOTH the `isinstance(stats, dict)` branch AND the `getattr(stats, "hits", 0)` branch:
    ```python
    level_breakdown_str = ""
    if lw_matrix.level_breakdown:
        breakdowns = []
        for lvl, stats_raw in lw_matrix.level_breakdown.items():
            stats_obj = LevelStatsDTO.model_validate(stats_raw, strict=False)
            breakdowns.append(f"Level {lvl}: {stats_obj.hits}/{stats_obj.total} hits")
        if breakdowns:
            level_breakdown_str = "[DISTRIBUTION CONTEXT: " + ", ".join(breakdowns) + "]\n\n"
    ```
    </action>
    <action>In title map resolution: replace `.get()` with explicit lookup `title_map[block_id.lower()] if block_id.lower() in title_map else block_id`.</action>
    <action>In justification assembly: enforce quote count capping via `capped_quotes = unique_quotes[:max_quotes_per_matrix]` and fallback claim capping via `capped_claims = unique_claims[:max_quotes_per_matrix]` before assembling `justification_text`.</action>
    <constraint invariant="the_duct_tape_ban">
      Zero tolerance for silent fallbacks, generic dictionary `getattr`, or unlogged exception swallowing. All validation failures must be explicitly logged with diagnostic metadata.
    </constraint>
    <constraint invariant="the_no_legacy_mandate">
      No optional target_locale defaults or backwards-compatibility shims. Method strictly mandates target_locale: str.
    </constraint>
  </step>

  <step id="4" name="Synthesis Payload Compressor SSOT Alignment">
    <action>Modify `@[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L17-L148]` to replace hardcoded `[:300]` with `settings_obj.max_synthesis_quote_length`.</action>
    <constraint invariant="dry_composition_mandate">
      Ensure single source of truth for synthesis quote truncation across all orchestrator services.
    </constraint>
  </step>

  <step id="5" name="Knowledge Base Alignment">
    <action>Update `@[ki_synthesis_payload_compression.md]` to replace references to `ExtractiveSensorService` with the SSOT `MatrixExplanationService`, and document centralized quote truncation (`max_synthesis_quote_length`), per-matrix quote capping (`max_synthesis_quotes_per_matrix`), and mandatory `target_locale` parameter.</action>
  </step>

  <step id="6" name="Unit & Regression Test Coverage Expansion">
    <action>Update `@[backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py]` and `@[backend_v2/tests/unit/test_epic93_contract_verification.py]` to pass mandatory `target_locale="en"` (and `"fi"`), testing quote character truncation at `max_synthesis_quote_length`, quote list capping at `max_synthesis_quotes_per_matrix` (pruning a test list of 10 quotes to 5), claims fallback capping at `max_synthesis_quotes_per_matrix`, multilingual claim label resolution in Finnish vs English, quotes extraction from unfiltered sensor steps, strict level stats breakdown (including `level_breakdown=None` safety), structured warning logging on malformed atom results and malformed matrix payloads, and no broad exceptions.</action>
    <action>Create `[NEW] @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py]` to test that `synthesis_distiller_hook` passes unfiltered `available_dtos` to both `<source>` block distillation (`distilled_inputs`) and `MatrixExplanationService` along with `target_locale`, ensuring cognitive sensor findings and evidence quotes are preserved in prompt context.</action>
    <action>Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test` to verify 100% test pass rate, Ruff formatting compliance, and MyPy strict typing.</action>
  </step>
</execution_protocol>

**SESSION SPLIT MANDATE**: This plan modifies 7 existing files + 1 new file = 8 target files, exceeding the `context_amnesia_prevention` threshold (>5 distinct complex files). The executing agent MUST instruct the user to run `/tier5-session-handover` after completing Steps 0-3 (AST verification, settings, distiller, service) before continuing with Steps 4-6 (compressor, KI, tests) in a fresh context window.
```

---

## Verification Plan

### Automated Tests
1. **Matrix Explanation Service Unit Tests:**
   `uv run pytest backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py`
2. **Synthesis Distiller Wiring Unit Tests:**
   `uv run pytest backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py`
3. **Contract Verification Tests:**
   `uv run pytest backend_v2/tests/unit/test_epic93_contract_verification.py`
4. **Orchestrator Backend Audit Loop:**
   `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test`

### Anti-Happy-Path Scenarios
- **Scenario A (Unfiltered Sensor Quotes Extraction):** Sensor step with `data_type="text"` producing `results=[AtomResultDTO(tda_id="a1", source_quote="Sensor Evidence")]`, cross-referenced by a matrix step with `evaluated_atoms={"a1": "PASSED"}`.
  - *Expected Output:* Matrix justification contains `"Sensor Evidence"`.
- **Scenario B (Preservation of Cognitive Sensor `<source>` Blocks):** Sensor step with cognitive findings (e.g., analyst evaluations and exact quotes) passed in `inputs["steps"]` alongside matrix steps.
  - *Expected Output:* `distilled_inputs` contains `<source id="DOC-1" title="Analyst">` with compressed sensor evaluations, proving that cognitive context is not pruned by layout targets.
- **Scenario C (Quote Length Truncation Boundary):** Provide a 500-character evidence quote.
  - *Expected Output:* Truncated deterministically to exactly `max_synthesis_quote_length` (300 characters) defined in `Settings`.
- **Scenario D (Quote Quantity Capping Boundary):** Provide a matrix referencing 12 sensor atoms, each with an authentic evidence quote.
  - *Expected Output:* Matrix justification contains exactly `max_synthesis_quotes_per_matrix` (5) quotes defined in `Settings`, deterministically discarding excess quotes.
- **Scenario E (Fallback Claims Quantity Capping Boundary):** Provide a matrix with no evidence quotes but 15 evaluated claims.
  - *Expected Output:* Matrix justification contains exactly `max_synthesis_quotes_per_matrix` (5) claim labels defined in `Settings`, avoiding claim text explosion.
- **Scenario F (Multilingual Localization Resolution):** Provide claim with translations `{"fi": "Suomalainen väite", "en": "English claim"}` and invoke with `target_locale="fi"`.
  - *Expected Output:* Matrix fallback justification contains `"Suomalainen väite"`.
- **Scenario G (Missing / Unknown Block ID):** Provide a step with a `block_id` not present in `blocks_by_id`.
  - *Expected Output:* Handles the absence cleanly without `getattr` fallbacks or broad exception masking.
- **Scenario H (Malformed Atom Payload Observability):** Pass a step output containing a malformed atom dictionary in `results` (with missing mandatory fields or invalid types).
  - *Expected Output:* Emits `logger.warning` containing `ErrorCodes.VALIDATION_FAILED.name`, step ID, block ID, and exception traceback (`exc_info=True`) without raising an unhandled crash or silently dropping the error.
- **Scenario I (Nullable Quote Guard Verification):** Pass an `AtomResultDTO` with `source_quote=None` (e.g. `contextual_override=True` or `status="FAILED"`).
  - *Expected Output:* Handled cleanly without `TypeError` (`object of type 'NoneType' has no len()` or subscripting errors), resulting in empty quote collection and fallback claim justification.
- **Scenario J (Malformed Matrix Output Payload Observability):** Pass a step output with a matrix `block_id` containing a malformed or invalid dictionary payload (e.g. extra forbidden keys, invalid types, or out-of-range `normalized_score`).
  - *Expected Output:* Emits `logger.warning` containing `ErrorCodes.VALIDATION_FAILED.name`, step ID, block ID, and exception traceback (`exc_info=True`) without raising an unhandled crash or terminating the pipeline, safely skipping the malformed matrix and processing remaining valid matrices.
- **Scenario K (Nullable Level Breakdown Guard Verification):** Pass a matrix step with `level_breakdown=None`.
  - *Expected Output:* Handled cleanly without `AttributeError: 'NoneType' object has no attribute 'items'`, resulting in empty `level_breakdown_str` and successfully producing justification without crash.

### Manual Verification
- Run local pipeline (`.\run_local.bat`) and verify in `client_debug.log` and `backend_debug.log` that the synthesis report contains both full cognitive context from upstream sensors in `<source>` blocks and matrix-level justifications with authentic quotes without producing `"No direct evidence quotes extracted for this matrix."` and without exceeding the 5-quote limit per matrix.
