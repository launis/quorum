# IMPLEMENTATION PLAN: Synthesis Matrix Explanation Timing Fix & Architecture Hardening

**Objective**: Fix the architectural defect where `synthesis_distiller.py` conflates SDUI Presentation Layout filtering (`target_blocks`) with LLM Synthesis Context, starving both `MatrixExplanationService` (zero evidence quotes) and the LLM prompt's `<source>` blocks (`distilled_inputs` losing all cognitive sensor findings). Fix the illegitimate `target_blocks` filter loop in `synthesis_distiller.py` by removing it completely (passing all upstream cognitive sensors and matrices through unconditionally to LLM synthesis, while allowing Phase 3 SDUI adapters and `<section_instruction targets="...">` to handle visual and section-level scoping), hoist and unify `target_locale` validation at the start of the distiller hook to eliminate undefined variable and scope risks, create a centralized, pure SSOT generic utility `backend_v2/utils/ranked_round_robin.py` implementing `ranked_round_robin_select[T]`, harden `matrix_explanation_service.py` to eliminate 12 legacy anti-patterns, implement **Status-Aware Dual Reporting** (segregating `SUPPORTING EVIDENCE` for `PASSED` atoms and `UNMET CRITERIA / DEFICITS` for `FAILED` atoms to eliminate Positivity Bias), implement **Ranked Round-Robin Claim Diversity** in `matrix_explanation_service.py` (ranking quotes by length and unmet criteria by scale level) to prevent single-claim quote starvation, harden `xai_highlights_adapter.py` by integrating `ranked_round_robin_select` to curate highlights across active extension types ranked by informativeness/length (eliminating UI accordion Primacy Bias and Category Starvation without requiring Flutter DTO or database schema changes), filter low-substance quote fragments (< 15 characters), unify quote and criteria limits under centralized SSOT settings (`max_synthesis_quote_length` = 300, `max_synthesis_quotes_per_matrix` = 5, `max_synthesis_unmet_criteria_per_matrix` = 5) in `settings.py` to eliminate LLM Context Window Saturation risks, eliminate $O(N)$ settings lookup overhead via method-level hoisting, enforce strict multi-language support by requiring mandatory `target_locale: str` across all production and test call-sites (Zero Backwards Compatibility), update Knowledge Item documentation, and enforce strict compliance with `@[ki_god_code_prevention.md]`.

<required_context_rules>
- @[.agents/rules/00-antigravity-core.md]
- @[.agents/rules/01-python-backend.md]
- @[ki_god_code_prevention.md]
- @[ki_synthesis_payload_compression.md]
- @[ki_matrix_boolean_evaluation_strictness.md]
- @[ki_dual_axis_localization_architecture.md]
</required_context_rules>

## Architectural Principle: Layered Synthesis Data Access

> [!IMPORTANT]
> **MANDATE (Synthesis Context Preservation):** The LLM Synthesis Phase (Phase 2) MUST have access to the **complete execution state** (all matrices and all cognitive sensors). The UI rendering selections (`OutputProfile.layouts` → `target_blocks`) dictate ONLY what is painted on the screen (Phase 3). They MUST NEVER be used to prune the `available_dtos` fed into the Synthesis Distiller or the LLM synthesis prompt.

**Layered Data Access Per Synthesis Component:**

| Component | Data Scope | Reason |
|---|---|---|
| **Executive Summary** (`SynthesisOutputDTO.user_role`, content_blocks) | **ALL** data (`distilled_inputs` = all `<source>` blocks from all matrices and all sensors) | The executive summary draws the big picture across the entire evaluation. Filtering any data would blind the LLM and force hallucinations. |
| **Section-Level Synthesis** (`SynthesisOutputDTO.section_syntheses`) | **ALL** data available, but the LLM is instructed via `<section_instruction targets="Matrix A, Matrix B">` to focus on specific matrices per layout | The LLM receives the complete `distilled_inputs` but is guided by the `targets` attribute in each `<section_instruction>` XML block (assembled from `layout.target_blocks` titles in `worker.py` lines 875-882). This keeps the LLM's full context intact while directing its attention per section. |
| **XAI Highlights** (`SynthesisOutputDTO.xai_highlights`) | **ALL** data, scoped by `<xai_curation_mandate>` listing requested extension types | XAI highlights are cross-cutting insights synthesized from the entire evaluation (all matrices, all sensors). The `visible_block_extensions` and `visible_workflow_extensions` on the Output Profile only control which extension *types* to produce, not which source data to use. |
| **Matrix Row Explanations** (`MatrixExplanationsResult.explanations`) | `matrices_to_explain` (ALL matrices from `MatrixExplanationService`) + `distilled_inputs` | Row explanations must cover every evaluated matrix because the summary table always displays all matrices. The Phase 3 SDUI layer (specifically `MatrixGraphsAdapter` and `MatrixSummaryTableAdapter`) uses `layout.target_blocks` to select which matrices to *visually render*. |
| **Phase 3 SDUI Adapters** (visual rendering) | Filtered by `layout.target_blocks` at the adapter level | This is the ONLY place where `target_blocks` filtering legitimately occurs. Adapters are "dumb painters" that select which matrices to paint on screen based on the Output Profile's layout definitions. |

> [!IMPORTANT]
> **No-Data Handling Boundary:** If the execution produced zero atoms (Data Starvation), this is handled by the **Circuit Breaker** in `SynthesisEngine` (see `@[docs/IMPLEMENTATION_PLAN_Circuit_Breaker_Sparse_Data.md]`). This plan does NOT duplicate that logic. This plan ensures that when data EXISTS, each synthesis component receives all of it without illegitimate pruning.


## Root Cause Analysis

1. **Conflation of SDUI Presentation Filtering with Cognitive Synthesis Context:**
   In `@[backend_v2/services/orchestrator/synthesis_distiller.py#L159-L330]`, incoming `available_dtos` from `inputs["steps"]` was filtered in-place against `output_profile.layouts[].target_blocks`. Per `@[backend_v2/models/v2_core.py#L1270-L1308]`, `target_blocks` is strictly an SDUI layout directive ("Optional explicit block IDs to plot, filtering and ordering the axes") for frontend widgets and matrix charts. Cognitive sensor steps (specifically and exhaustively: analyst, profiler, logician, falsifier, fact checker, performativity detector, archivist, judge, coach, and causal analyst) are upstream analysis nodes whose `block_id` values are never in `target_blocks`.
2. **Dual Context Deprivation:**
   - **Downstream Matrix Quotes Deprivation:** `MatrixExplanationService.assemble_matrices_to_explain()` received the pruned list. The `global_quotes_map` was built from an empty set of sensor results, causing all matrices to produce `"No direct evidence quotes extracted for this matrix."`
   - **LLM `<source>` Context Deprivation:** `consolidated_distilled_parts` (`distilled_inputs`) iterated over the pruned list. Consequently, `<source id="DOC-X">` blocks passed into the LLM prompt's `DATA TO SYNTHESIZE` contained only boolean matrix results, completely stripping all cognitive sensor findings, exact quotes, and semantic reasoning from the synthesis prompt.
3. **Positivity Bias & Single-Claim Starvation in Matrix Explanations:**
   In `@[backend_v2/services/orchestrator/matrix_explanation_service.py#L123-L136]`, justifications used a mutually exclusive `if unique_quotes: ... elif evaluated_claims:` branch. 
   - **Positivity Bias:** In Quorum's Null Hypothesis architecture (`@[ki_matrix_boolean_evaluation_strictness.md]`), `PASSED` atoms have verbatim quotes while `FAILED` atoms have `source_quote = None`. If a matrix has 1 `PASSED` atom and 9 `FAILED` atoms, the single quote triggered `if unique_quotes:`, completely hiding the 9 failed criteria. The LLM received a low score (specifically: 10%) with exclusively positive supporting quotes, causing hallucinated justifications or synthesis contradictions.
   - **Blind Truncation & Starvation:** Slicing claims linearly (`[:5]`) truncated higher-level or barrier criteria situated later in the scale definition. If one claim had 5 quotes, linear slicing took all 5 quotes from that single claim, starving remaining claims of representation.
4. **Primacy Bias & Category Starvation in XAI Highlights SDUI Adapter:**
   In `@[backend_v2/services/sdui/adapters/xai_highlights_adapter.py#L65-L130]`, incoming highlights are processed in raw arrival order and appended to accordions until `len(accordion.children) < max_lines`. If earlier extension categories (e.g. `coaching`) contain many items, they exhaust visual capacity before later critical categories (e.g. `falsification` or `risk_flag`) are evaluated, creating **Primacy Bias** and **Category Starvation** in the UI. Furthermore, the adapter relies on duck-typing (`isinstance(item, dict)`, `.get()`, `getattr()`) violating `the_zero_compromise_pledge`.
5. **Anti-Pattern Proliferation, Raw String Concatenation & Hardcoded Language:**
   `@[backend_v2/services/orchestrator/matrix_explanation_service.py#L15-L145]` contains legacy anti-patterns (`isinstance` checks on payload dicts, `hasattr` reflection, `getattr` with fallback defaults, `.get()` defaults, raw string concatenation with `+` violating `naked_prompt_injection`, and `try/except Exception: continue` catch-alls) that violate `the_zero_compromise_pledge`, `the_duct_tape_ban`, and `naked_prompt_injection`. Additionally, `claim.label.resolve("en")` hardcodes English, violating the Dual-Axis Localization architecture.
6. **$O(N)$ Settings Overhead & Scattered Limits:**
   Quote truncation limits were hardcoded as magic numbers (`[:300]`) in `SynthesisPayloadCompressor`, with potential duplication in `MatrixExplanationService`. Calling `get_settings()` repeatedly inside nested iteration loops introduces unnecessary function and cache overhead. Both quote character length, per-matrix quote counts, and per-matrix unmet criteria limits must be centralized in `Settings` and hoisted at the method entry.
7. **TypeError Hazard on Null Quotes (`source_quote: str | None`):**
   In `@[backend_v2/models/v2_core.py#L1127-L1160]`, `AtomResultDTO.source_quote` is nullable (`str | None`), especially when `contextual_override: True` forces `source_quote = None` or when an atom evaluation produces no verbatim quote. Attempting to measure length (`len(quote)`) or slice directly (`quote[:max_quote_len]`) without an explicit `None`-check (`quote-guard`) crashes the synthesis pipeline with `TypeError: object of type 'NoneType' has no len()` or `TypeError: 'NoneType' object is not subscriptable`.
8. **Missing Pydantic Validation Error Handling for Matrix Outputs (`LightweightMatrixOutput.model_validate`):**
   In `@[backend_v2/services/orchestrator/matrix_explanation_service.py#L85-L89]`, `LightweightMatrixOutput.model_validate(payload_to_validate, strict=False)` is executed without a `try/except` block. Because `LightweightMatrixOutput` enforces `model_config = ConfigDict(strict=True, extra="forbid")`, any unexpected payload format (specifically and exhaustively: malformed dicts from upstream failures, unanticipated extra keys beyond popped `results`, or invalid numerical ranges) will raise an unhandled `ValidationError` or `ValueError`, crashing the entire `MatrixExplanationService` and terminating the synthesis pipeline.
9. **AttributeError Hazard on Nullable Level Breakdown (`level_breakdown: dict[str, dict[str, int]] | None`):**
   In `@[backend_v2/models/dtos/lightweight_matrix.py#L55]`, `LightweightMatrixOutput.level_breakdown` is typed as `dict[str, dict[str, int]] | None = None`. In non-hierarchical matrices, sensor steps, or payloads without computed breakdowns, `level_breakdown` is `None`. Directly executing `for lvl, stats_raw in lw_matrix.level_breakdown.items():` without an explicit `if lw_matrix.level_breakdown:` check raises `AttributeError: 'NoneType' object has no attribute 'items'`, crashing matrix explanation assembly during synthesis.
10. **Nomenclature Inconsistency, Scope Hoisting & Test Suite Blast Radius:**
    In `@[backend_v2/services/orchestrator/synthesis_distiller.py#L268-L273]`, `target_locale` was extracted from `state.metadata` into a local variable named `language` late in the function body (after layout filtering). The helper `_build_title_map` also accepted `language: str`. This created vocabulary dissonance (`language` vs `target_locale`) and hoisting risks where modifying execution order causes `NameError`. Furthermore, updating `MatrixExplanationService.assemble_matrices_to_explain` to require mandatory `target_locale: str` (no lazy defaults) breaks 6 existing test call-sites across `test_matrix_explanation_service.py` (5 tests) and `test_epic93_contract_verification.py` (1 test). The plan must explicitly hoist and normalize `target_locale` at the start of `synthesis_distiller_hook`, unify all internal identifiers to `target_locale`, and update 100% of test callers.

---

## Scope & Target Files

- **[MODIFY]** @[backend_v2/settings.py]
- **[NEW]** @[backend_v2/utils/ranked_round_robin.py]
- **[MODIFY]** @[backend_v2/services/orchestrator/synthesis_distiller.py]
- **[MODIFY]** @[backend_v2/services/orchestrator/matrix_explanation_service.py]
- **[MODIFY]** @[backend_v2/services/sdui/adapters/xai_highlights_adapter.py]
- **[MODIFY]** @[backend_v2/services/orchestrator/synthesis_payload_compressor.py]
- **[MODIFY]** @[ki_synthesis_payload_compression.md]
- **[NEW]** @[backend_v2/tests/unit/utils/test_ranked_round_robin.py]
- **[MODIFY]** @[backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py]
- **[MODIFY]** @[backend_v2/tests/unit/services/sdui/adapters/test_xai_highlights_adapter.py]
- **[MODIFY]** @[backend_v2/tests/unit/test_epic93_contract_verification.py]
- **[NEW]** @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py]

---

## God Code Prevention Compliance (`@[ki_god_code_prevention.md]`)

| Rule | Enforcement in this Plan |
|---|---|
| `anti_god_file_dumping` | `MatrixExplanationService` remains in its dedicated modular file `matrix_explanation_service.py` (<180 lines). Generic Ranked Round-Robin algorithm is extracted to a pure utility `backend_v2/utils/ranked_round_robin.py` (<50 lines). |
| `private_helper_bloat_ban` | Logic is extracted outwards to existing domain services and utility SSOTs, not downwards into `synthesis_distiller.py` private helpers. |
| `dry_composition_mandate` | Quote truncation, quote count limits, and unmet criteria limits are consolidated into centralized SSOT settings (`max_synthesis_quote_length`, `max_synthesis_quotes_per_matrix`, `max_synthesis_unmet_criteria_per_matrix` in `Settings`), eliminating copy-pasted slices and preventing prompt context blowup. |
| `ast_boundary_verification_mandate` | `synthesis_distiller.py` has 331 lines (>300 line God File threshold). Modifications MUST use verified line bounds before applying edits. |
| `domain_model_purity_mandate` | Pure DTOs (`ConfigDict(strict=True, extra="forbid")`) used across boundaries with no inline database/service logic. |
| `remedial_refactoring_coverage` | Full test suite execution before and after changes via `backend_audit_loop.py`. |

---

## Knowledge Base Constraints (KIs) Applied

1. **`ki_synthesis_payload_compression.md` (Epic 141)**:
   - Validates the role of `MatrixExplanationService` in preparing condensed matrix evidence quotes and deficits.
   - Enforces centralized quote character limits via `max_synthesis_quote_length` (300), quote count limits via `max_synthesis_quotes_per_matrix` (5), and deficit limits via `max_synthesis_unmet_criteria_per_matrix` (5) in `Settings`.
2. **`ki_god_code_prevention.md` (Epic 133)**:
   - Enforces modular service extraction without adding helper bloat inside `synthesis_distiller.py`.
   - Protects boundaries of files exceeding 300 lines via surgical edits.
3. **`ki_matrix_boolean_evaluation_strictness.md` (Epic 142)**:
   - Ensures that `evaluated_atoms` resolution respects `ExecutionStatus` enum values (`PASSED`, `FAILED`, `N_A`).
   - Respects the Null Hypothesis: `PASSED` atoms supply verbatim evidence quotes, while `FAILED` atoms supply unmet criteria descriptions.
4. **`ki_dual_axis_localization_architecture.md`**:
   - Enforces semantic backend translation (Axis 2) by passing mandatory `target_locale: str` through `assemble_matrices_to_explain` to resolve claim labels without hardcoded `"en"`.

---

## User Review Required

> [!IMPORTANT]
> **Complete Cognitive Preservation in `<source>` Prompt Blocks:**
> We DELETE the `target_blocks` filter from `synthesis_distiller.py` entirely. The filter conflated Phase 3 visual rendering decisions with Phase 2 data collection, starving the LLM of cognitive sensor findings. Because the LLM requires all data to write the Executive Summary, and `<section_instruction targets="...">` already guides per-section focus, there is no legitimate reason to pre-filter `available_dtos` in the distiller. `SynthesisPayloadCompressor` protects against Context Window Saturation via `max_synthesis_evaluations` and `max_synthesis_quote_length`.

> [!IMPORTANT]
> **Ranked Round-Robin SSOT (`backend_v2/utils/ranked_round_robin.py`):**
> We introduce a generic, pure mathematical function `ranked_round_robin_select[T]` (PEP 695 generics, $O(N \log N)$ complexity, deterministic, side-effect free).
> It serves as the single source of truth for equitable group interleaving across:
> 1. `MatrixExplanationService`: Quotes grouped by claim and ranked by length (longest/most informative first); unmet criteria grouped by claim and ranked by scale level (highest deficit first).
> 2. `XaiHighlightsAdapter`: Highlights grouped by `extension_type` and ranked by content length/informativeness, guaranteeing fair representation across coaching, falsification, risk flags, etc., without requiring Flutter DTO or database schema changes.

> [!IMPORTANT]
> **Status-Aware Dual Justification in `MatrixExplanationService`:**
> Rather than a mutually exclusive `if quotes: ... elif claims:` branch that creates Positivity Bias, `MatrixExplanationService` produces a deterministic, two-part structural justification:
> 1. `SUPPORTING EVIDENCE`: Verbatim quotes from `PASSED` atoms, selected via Ranked Round-Robin across distinct claims (up to `max_synthesis_quotes_per_matrix = 5`), ignoring fragments shorter than 15 characters.
> 2. `UNMET CRITERIA / DEFICITS`: Explicit localized claim labels from `FAILED` atoms selected via Ranked Round-Robin (up to `max_synthesis_unmet_criteria_per_matrix = 5`), ensuring the LLM is informed of exactly what criteria were missing.

> [!IMPORTANT]
> **Single SSOT for Quote Limits & Context Shielding in `backend_v2/settings.py`:**
> We introduce three centralized configuration variables in `Settings`:
> 1. `max_synthesis_quote_length: int = 300` (caps individual quote character length).
> 2. `max_synthesis_quotes_per_matrix: int = 5` (caps the number of evidence quotes per matrix).
> 3. `max_synthesis_unmet_criteria_per_matrix: int = 5` (caps the number of unmet criteria / deficits per matrix).
> Both `SynthesisPayloadCompressor` and `MatrixExplanationService` will strictly reference these settings, eliminating hardcoded magic numbers and safeguarding against Context Window Saturation during LLM synthesis.

> [!IMPORTANT]
> **Zero Backwards Compatibility (No Optional Defaults) & Blast Radius Coverage:**
> `MatrixExplanationService.assemble_matrices_to_explain` strictly requires `target_locale: str` as a mandatory parameter:
> `assemble_matrices_to_explain(available_dtos: list[StepOutputDTO], title_map: dict[str, str], blocks_by_id: dict[str, PromptBlock], target_locale: str) -> list[MatrixExplanationContextDTO]`.
> All callers (specifically and exhaustively: `synthesis_distiller.py`, all 5 tests in `test_matrix_explanation_service.py`, and `test_epic93_contract_verification.py`) MUST provide `target_locale`. No optional `= None` or `="en"` fallbacks allowed per `the_no_legacy_mandate` and `anti_lazy_fallback_mandate`.
> In `synthesis_distiller.py`, `target_locale` validation is hoisted to the top of `synthesis_distiller_hook` immediately after `inputs["steps"]` checking, and all references to the legacy `language` identifier are unified to `target_locale`.

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
    <action>Modify `@[backend_v2/settings.py#L42-L599]` to add three centralized SSOT settings in `Settings` directly after `max_synthesis_evaluations`:</action>
    <action>1. `max_synthesis_quote_length: Annotated[int, Field(description="Maximum character length for evidence quotes in synthesis payloads")] = 300`</action>
    <action>2. `max_synthesis_quotes_per_matrix: Annotated[int, Field(description="Maximum number of evidence quotes per matrix in synthesis explanation context")] = 5`</action>
    <action>3. `max_synthesis_unmet_criteria_per_matrix: Annotated[int, Field(description="Maximum number of unmet criteria descriptions per matrix in synthesis explanation context")] = 5`</action>
    <constraint invariant="global_config_sovereignty">
      Hardcoded magic numbers `[:300]` and `[:5]` in service files are strictly banned. All quote truncation, quote counts, and criteria limits must reference `max_synthesis_quote_length`, `max_synthesis_quotes_per_matrix`, and `max_synthesis_unmet_criteria_per_matrix` in `Settings`.
    </constraint>
  </step>

  <step id="2" name="Ranked Round-Robin SSOT Utility Implementation">
    <action>Create `[NEW] @[backend_v2/utils/ranked_round_robin.py]`:</action>
    <action>
    ```python
    from typing import Any, Callable, Hashable, Sequence

    def ranked_round_robin_select[T](
        items: Sequence[T],
        group_key: Callable[[T], Hashable],
        rank_key: Callable[[T], Any],
        max_items: int,
        *,
        reverse_rank: bool = True,
    ) -> list[T]:
        """Select items using Ranked Round-Robin for equitable group representation.

        Algorithm:
        1. Group items by group_key (preserving group order of first appearance)
        2. Sort each group internally by rank_key (descending if reverse_rank=True)
        3. Interleave groups in round-robin, picking the top remaining item from each group
        4. Truncate selection at max_items
        """
        if max_items <= 0 or not items:
            return []

        groups: dict[Hashable, list[T]] = {}
        for item in items:
            g_key = group_key(item)
            groups.setdefault(g_key, []).append(item)

        # Sort within each group
        for g_key in groups:
            groups[g_key].sort(key=rank_key, reverse=reverse_rank)

        selected: list[T] = []
        while len(selected) < max_items and groups:
            empty_groups = []
            for g_key, group_items in list(groups.items()):
                if len(selected) >= max_items:
                    break
                if group_items:
                    selected.append(group_items.pop(0))
                if not group_items:
                    empty_groups.append(g_key)
            for eg in empty_groups:
                groups.pop(eg, None)

        return selected
    ```
    </action>
    <constraint invariant="ssot_reuse_mandate">
      Pure, side-effect free, deterministic function using modern Python PEP 695 generics. Single Source of Truth for group interleaving.
    </constraint>
  </step>

  <step id="3" name="Synthesis Distiller Locale Hoisting, Pruning Elimination & Unfiltered Context Pipeline">
    <action>Modify `@[backend_v2/services/orchestrator/synthesis_distiller.py#L159-L330]`:</action>
    <action>HOIST target_locale validation to the top of `synthesis_distiller_hook` immediately after `inputs["steps"]` validation, before executing any async repository queries:</action>
    <action>
    ```python
    if not state.metadata or "target_locale" not in state.metadata:
        msg = "Strict Fail-Fast Enforced: 'target_locale' missing from execution metadata."
        logger.error("[SynthesisDistiller] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
    raw_locale = state.metadata["target_locale"]
    if not raw_locale or not str(raw_locale).strip():
        msg = "Strict Fail-Fast Enforced: 'target_locale' in execution metadata must be a non-empty string."
        logger.error("[SynthesisDistiller] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
    target_locale = str(raw_locale).strip().lower()
    ```
    </action>
    <action>Rename parameter in `_build_title_map(workflow_data: Workflow | None, all_steps: list[Step], target_locale: str) -> dict[str, str]` (replacing legacy `language` identifier).</action>
    <action>DELETE the `target_blocks` filter loop entirely. The LLM requires full context for Executive Summary synthesis. Per-section focus is handled by `<section_instruction targets="...">` in the worker's dynamic context assembly. Phase 3 SDUI adapters handle visual filtering independently.</action>
    <action>Ensure `available_dtos` (the complete, unfiltered execution state from `inputs["steps"]`) is passed directly to alias registration, `<source>` prompt blocks assembly, and `MatrixExplanationService.assemble_matrices_to_explain`.</action>
    <action>In `synthesis_distiller_hook`, update `<source>` prompt block generation to iterate over all `available_dtos`, compressing each step payload via `SynthesisPayloadCompressor.compress_synthesis_payload` so that all cognitive sensor evaluations and matrix results are preserved in `distilled_inputs`.</action>
    <action>Update `MatrixExplanationService.assemble_matrices_to_explain` call to pass `available_dtos`, `title_map`, `blocks_by_id`, and mandatory `target_locale=target_locale`.</action>
    <action>In `HookResult.state_delta`, export `"target_locale": target_locale` and `"language": target_locale` to guarantee contract compliance.</action>
    <constraint invariant="the_zero_compromise_pledge">
      Removing the flawed presentation layout filter ensures full cognitive context is preserved for LLM synthesis. No Context Contamination risk exists because the LLM is guided per-section by `<section_instruction targets="...">` and overall context bounds are enforced by `SynthesisPayloadCompressor`.
    </constraint>
    <constraint invariant="anti_lazy_fallback_mandate">
      Hoisting locale validation to the start of the hook enforces immediate Fail-Fast if target_locale is missing or whitespace-only before any database I/O is performed.
    </constraint>
  </step>

  <step id="4" name="Matrix Explanation Service Hardening, Dual Reporting & Ranked Round-Robin Curation">
    <action>Modify `@[backend_v2/services/orchestrator/matrix_explanation_service.py#L15-L145]`:</action>
    <action>Import `logger` via `import logging; logger = logging.getLogger(__name__)`, `ErrorCodes` from `backend_v2.exceptions`, and `settings` from `backend_v2.settings` globally at module level per `global_settings_import` rule.</action>
    <action>Import `ranked_round_robin_select` from `backend_v2.utils.ranked_round_robin`.</action>
    <action>Import `LevelStatsDTO`, `LightweightMatrixOutput` from `backend_v2.models.dtos.lightweight_matrix`, `PromptBlockCategory` from `backend_v2.models.enums`, and `ValidationError` from `pydantic`.</action>
    <action>Update signature to mandate `target_locale: str`: `def assemble_matrices_to_explain(available_dtos: list[StepOutputDTO], title_map: dict[str, str], blocks_by_id: dict[str, PromptBlock], target_locale: str) -> list[MatrixExplanationContextDTO]`.</action>
    <action>Hoist settings at method start: `max_quote_len = settings.max_synthesis_quote_length`, `max_quotes_per_matrix = settings.max_synthesis_quotes_per_matrix`, `max_unmet_criteria = settings.max_synthesis_unmet_criteria_per_matrix` to eliminate O(N) lookup overhead and enforce strict Fail-Fast attribute access without fallback defaults.</action>
    <action>In `global_quotes_map` extraction: accept both direct `AtomResultDTO` instances and `dict` payloads; validate dictionaries via `AtomResultDTO.model_validate(atom_dict, strict=False)`; on `(ValidationError, ValueError)` catch, execute `logger.warning("[MatrixExplanationService] %s: Failed to parse atom result in step '%s' (block '%s'): %s", ErrorCodes.INVALID_OUTPUT_SCHEMA.name, dto.step_id, dto.block_id, str(e), exc_info=True)` before continuing; extract `source_quote` from `AtomResultDTO` with a strict `None`-guard (`if atom_res.source_quote: cleaned = atom_res.source_quote.strip(); if len(cleaned) >= 15: quotes.append(cleaned[:max_quote_len])`), avoiding `TypeError` on nullable quotes, and append non-empty substantive quotes to `global_quotes_map[atom_res.tda_id]`.</action>
    <action>In matrix payload validation: wrap `LightweightMatrixOutput.model_validate(payload_to_validate, strict=False)` in a `try...except (ValidationError, ValueError) as e:` block; on catch, execute `logger.warning("[MatrixExplanationService] %s: Failed to parse matrix output in step '%s' (block '%s'): %s", ErrorCodes.INVALID_OUTPUT_SCHEMA.name, step_dto_obj.step_id, block_id, str(e), exc_info=True)` and `continue` before proceeding to atom evaluations, preventing unhandled schema validation exceptions on malformed matrix dictionaries from killing the synthesis aggregation.</action>
    <mutation_note>REVIEWED EXCEPTION to `the_duct_tape_ban`: The `except (ValidationError, ValueError): continue` blocks are PROBE BOUNDARIES — code iterates ALL `StepOutputDTO` instances (text, matrix, sensor) and probes `payload.results` for atom data and `payload` for matrix data. The `payload` field is `Any`-typed. Not every step carries valid `AtomResultDTO` or `LightweightMatrixOutput` payloads. Crashing Fail-Fast on an upstream malformed step during distillation would kill the entire synthesis. The executing agent MUST add inline `# REVIEWED EXCEPTION to the_duct_tape_ban:` comments documenting this justification.</mutation_note>
    <action>In prompt block category lookup: eliminate `.get(block_id)` and nullable assignment; enforce strict non-nullable guard via `if block_id not in blocks_by_id: continue` followed by `pb = blocks_by_id[block_id]` and `if pb.category_id != PromptBlockCategory.MATRIX: continue`.</action>
    <action>In claim label resolution: strictly resolve text using `claim.label.resolve(target_locale)` (Zero hardcoded "en", Zero hasattr duck-typing). Remove `hasattr(claim.label, "resolve")` guard entirely — `claim.label` is always `I18nText` per Pydantic schema, so `.resolve()` is guaranteed to exist.</action>
    <action>In atom evaluation collection: collect quote items as `(claim_label, quote_text)` tuples and unmet items as `(scale_score, claim_label)` tuples:
    ```python
    quote_candidates: list[tuple[str, str]] = []
    unmet_candidates: list[tuple[int | float, str]] = []

    for tda_id, hit_status in atoms.items():
        if hit_status == ExecutionStatus.N_A:
            continue

        claim_label = tda_to_claim.get(tda_id, "")
        scale_score = tda_to_scale.get(tda_id, 0)

        if hit_status == ExecutionStatus.PASSED:
            if tda_id in global_quotes_map:
                for q in global_quotes_map[tda_id]:
                    quote_candidates.append((claim_label, q))
        elif hit_status == ExecutionStatus.FAILED:
            if claim_label:
                unmet_candidates.append((scale_score, claim_label))
    ```
    </action>
    <action>In quote and unmet curation: execute `ranked_round_robin_select` for both dimensions:
    ```python
    # Curate quotes: Grouped by claim_label, ranked by quote length (longest first)
    ranked_quotes = ranked_round_robin_select(
        items=quote_candidates,
        group_key=lambda pair: pair[0],
        rank_key=lambda pair: len(pair[1]),
        max_items=max_quotes_per_matrix,
        reverse_rank=True,
    )
    # Deduplicate keeping order
    curated_quotes = list(dict.fromkeys(q for _, q in ranked_quotes))

    # Curate unmet criteria: Grouped by claim_label, ranked by scale level (highest deficit first)
    ranked_unmet = ranked_round_robin_select(
        items=unmet_candidates,
        group_key=lambda pair: pair[1],
        rank_key=lambda pair: pair[0],
        max_items=max_unmet_criteria,
        reverse_rank=True,
    )
    unique_failed_claims = list(dict.fromkeys(c for _, c in ranked_unmet))
    ```
    </action>
    <action>In level stats resolution: enclose iteration inside an explicit `if lw_matrix.level_breakdown:` guard. Inside the loop, perform UNCONDITIONAL `LevelStatsDTO.model_validate(stats_raw, strict=False)`. Construct `level_breakdown_str` strictly using Python f-strings, completely banning raw string concatenation with `+`:
    ```python
    level_breakdown_str = ""
    if lw_matrix.level_breakdown:
        breakdowns = []
        for lvl, stats_raw in lw_matrix.level_breakdown.items():
            stats_obj = LevelStatsDTO.model_validate(stats_raw, strict=False)
            breakdowns.append(f"Level {lvl}: {stats_obj.hits}/{stats_obj.total} hits")
        if breakdowns:
            level_breakdown_str = f"[DISTRIBUTION CONTEXT: {', '.join(breakdowns)}]"
    ```
    </action>
    <action>In title map resolution: replace `.get()` with explicit lookup `title_map[block_id.lower()] if block_id.lower() in title_map else block_id`.</action>
    <action>In justification assembly: assemble `justification_text` using deterministic sections for distribution context, supporting evidence, and unmet criteria:
    ```python
    sections: list[str] = []
    if level_breakdown_str:
        sections.append(level_breakdown_str)

    if curated_quotes:
        quotes_formatted = "\n".join(f"- {q}" for q in curated_quotes)
        sections.append(f"SUPPORTING EVIDENCE:\n{quotes_formatted}")

    if unique_failed_claims:
        claims_formatted = "\n".join(f"- {c}" for c in unique_failed_claims)
        sections.append(f"UNMET CRITERIA / DEFICITS:\n{claims_formatted}")

    if not curated_quotes and not unique_failed_claims:
        sections.append("No direct evidence quotes or specific deficits recorded for this matrix.")

    justification_text = "\n\n".join(sections)
    ```
    </action>
    <constraint invariant="naked_prompt_injection">
      Raw string concatenation using '+' is strictly prohibited for prompt context and justification string construction. All string formatting MUST use Python f-strings and str.join() with deterministic structural boundaries.
    </constraint>
    <constraint invariant="the_duct_tape_ban">
      Zero tolerance for silent fallbacks, generic dictionary `getattr`, or unlogged exception swallowing. All validation failures must be explicitly logged with diagnostic metadata.
    </constraint>
    <constraint invariant="the_no_legacy_mandate">
      No optional target_locale defaults or backwards-compatibility shims. Method strictly mandates target_locale: str.
    </constraint>
  </step>

  <step id="5" name="XAI Highlights SDUI Adapter Hardening & Ranked Round-Robin Fair Distribution">
    <action>Modify `@[backend_v2/services/sdui/adapters/xai_highlights_adapter.py#L40-L133]`:</action>
    <action>Import `ranked_round_robin_select` from `backend_v2.utils.ranked_round_robin`.</action>
    <action>Eliminate duck-typing (`isinstance(item, dict)`, `.get()`, `getattr()`): parse raw highlight items via typed extraction or strict validation.</action>
    <action>Pre-filter highlights across active extension types using `ranked_round_robin_select`:</action>
    <action>
    ```python
    max_total_items = len(profile.visible_block_extensions or []) * (profile.max_extension_items or 4)
    curated_highlights = ranked_round_robin_select(
        items=highlights,
        group_key=lambda h: h.get("extension_type") if isinstance(h, dict) else getattr(h, "extension_type", ""),
        rank_key=lambda h: len(h.get("content", "")) if isinstance(h, dict) else len(getattr(h, "content", "")),
        max_items=max_total_items,
        reverse_rank=True,
    )
    ```
    </action>
    <action>Iterate over `curated_highlights` when populating `AccordionBlock` and `AlertBlock` children, guaranteeing that all active extension types receive equitable representation in the SDUI tree without Primacy Bias.</action>
    <constraint invariant="the_zero_compromise_pledge">
      Eliminates legacy duck typing and hardcodes zero fallback defaults in SDUI presentation logic.
    </constraint>
  </step>

  <step id="6" name="Synthesis Payload Compressor SSOT Alignment">
    <action>Modify `@[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L17-L148]` to replace hardcoded `[:300]` with `settings_obj.max_synthesis_quote_length`.</action>
    <constraint invariant="dry_composition_mandate">
      Ensure single source of truth for synthesis quote truncation across all orchestrator services.
    </constraint>
  </step>

  <step id="7" name="Knowledge Base Alignment">
    <action>Update `@[ki_synthesis_payload_compression.md]` to replace references to `ExtractiveSensorService` with the SSOT `MatrixExplanationService`, and document centralized quote truncation (`max_synthesis_quote_length`), per-matrix quote capping (`max_synthesis_quotes_per_matrix`), per-matrix unmet criteria capping (`max_synthesis_unmet_criteria_per_matrix`), Ranked Round-Robin diversity curation across matrices and XAI highlights, and mandatory `target_locale` parameter.</action>
  </step>

  <step id="8" name="Unit & Regression Test Coverage Expansion & Blast Radius Alignment">
    <action>Create `[NEW] @[backend_v2/tests/unit/utils/test_ranked_round_robin.py]` to test:</action>
    <action>- Empty items list returns empty list.</action>
    <action>- Max items <= 0 returns empty list.</action>
    <action>- Single group maintains internal sorting order.</action>
    <action>- Multiple groups interleave in round-robin order picking top-ranked item from each group.</action>
    <action>- Budget truncation at exact `max_items` boundary.</action>
    <action>- Unequal group sizes where smaller groups deplete before larger groups.</action>
    <action>Update all 5 call-sites in `@[backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py]` to pass mandatory `target_locale="en"` and assert updated Status-Aware justification format:</action>
    <action>1. `test_assemble_matrices_to_explain_basic`: pass `target_locale="en"`, verify `SUPPORTING EVIDENCE:` header with quotes.</action>
    <action>2. `test_assemble_matrices_to_explain_no_matching_quotes`: pass `target_locale="en"`, verify `UNMET CRITERIA / DEFICITS:` header with failed claim labels.</action>
    <action>3. `test_assemble_matrices_to_explain_empty_quotes_list`: pass `target_locale="en"`, verify fallback string when neither quotes nor failed claims exist.</action>
    <action>4. `test_assemble_matrices_to_explain_deduplicates_by_block_id`: pass `target_locale="en"`.</action>
    <action>5. `test_assemble_matrices_to_explain_includes_failed_claims`: pass `target_locale="en"`, verify dual-reporting with both `SUPPORTING EVIDENCE:` and `UNMET CRITERIA / DEFICITS:` present simultaneously.</action>
    <action>Add new unit test `test_assemble_matrices_to_explain_round_robin_diversity` in `test_matrix_explanation_service.py` to verify that when Claim A has 4 quotes and Claim B has 4 quotes, Ranked Round-Robin selects alternating quotes from both claims up to the limit of 5 (picking 3 longest from A and 2 longest from B) rather than exhausting Claim A.</action>
    <action>Add new unit test `test_assemble_matrices_to_explain_short_quote_filtering` in `test_matrix_explanation_service.py` to verify that quote fragments shorter than 15 characters (specifically: "yes", "OK") are excluded from `SUPPORTING EVIDENCE`.</action>
    <action>Add new unit test `test_assemble_matrices_to_explain_multilingual_resolution` in `test_matrix_explanation_service.py` to verify that `target_locale="fi"` resolves Finnish claim translations while `target_locale="en"` resolves English translations.</action>
    <action>Update `@[backend_v2/tests/unit/services/sdui/adapters/test_xai_highlights_adapter.py]`:</action>
    <action>- Add test `test_build_ranked_round_robin_distribution` verifying that when 3 extension categories (`coaching`, `falsification`, `remediation_steps`) have multiple items each, the adapter interleaves them fairly across accordions and prioritizes longer/more informative content.</action>
    <action>Update call-site in `@[backend_v2/tests/unit/test_epic93_contract_verification.py]` (line 306) to pass mandatory `target_locale="en"` in `test_matrices_to_explain_assembly`.</action>
    <action>Enforce Unit Test Mock Strictness (Anti-Fake-Green Mandate):
      - BANNED: Patching `model_validate` or `model_validate_json` with unconstrained `MagicMock` or using loose `MagicMock(spec=PromptBlock)` that bypasses Pydantic V2 schema validations.
      - MANDATORY: In `test_matrix_explanation_service.py`, `test_xai_highlights_adapter.py`, and `test_synthesis_distiller_wiring.py`, replace all `MagicMock(spec=PromptBlock)` with concrete, structurally valid `PromptBlock` instances or typed fixtures.
      - MANDATORY: All repository mock return values (specifically: `workflow_repo.get_workflow_by_id`, `exec_repo.get_execution`, `output_profile_repo.get_output_profile_by_id`, `prompt_block_repo.get_all_prompt_blocks`, `workflow_repo.get_all_steps`) MUST return valid schema dictionaries generated via `Polyfactory` (specifically: `WorkflowFactory.build().model_dump()`, `PromptBlockFactory.build().model_dump()`, `StepOutputDTOFactory.build()`) or concrete Pydantic instances that pass real `model_validate(strict=False)` without patching the validator.
    </action>
    <action>Create `[NEW] @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py]` to test:</action>
    <action>- `synthesis_distiller_hook` passes unfiltered `available_dtos` to both `<source>` block distillation (`distilled_inputs`) and `MatrixExplanationService` along with `target_locale`.</action>
    <action>- `synthesis_distiller_hook` fails fast with `AppException(VALIDATION_FAILED)` when `target_locale` is missing from `state.metadata` or contains whitespace-only strings.</action>
    <action>- `distilled_inputs` preserves upstream cognitive sensor findings and verbatim evidence quotes.</action>
    <action>Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test` and `uv run python scripts/backend_audit_loop.py backend_v2/services/sdui/adapters/ --test` to verify 100% test pass rate, Ruff formatting compliance, and MyPy strict typing.</action>
    <constraint invariant="deterministic_testing_delegation">
      All test fixtures must use polyfactory or concrete Pydantic models. Mocking Pydantic validation boundaries to bypass schema checks or using unconstrained MagicMock for domain models is strictly prohibited.
    </constraint>
    <constraint invariant="anti_happy_path_mandate">
      Unit tests must rigorously test both happy paths and malformed/missing schema boundaries with exact exception code assertions.
    </constraint>
  </step>
</execution_protocol>

**SESSION SPLIT MANDATE**: This plan modifies 8 existing files + 4 new files = 12 target files, exceeding the `context_amnesia_prevention` threshold (>5 distinct complex files). The executing agent MUST instruct the user to run `/tier5-session-handover` after completing Steps 0-4 (AST verification, settings, utility, distiller, matrix explanation service) before continuing with Steps 5-8 (XAI highlights adapter, compressor, KI, test expansion) in a fresh context window.
```

---

## Verification Plan

### Automated Tests
1. **Ranked Round-Robin Unit Tests:**
   `uv run pytest backend_v2/tests/unit/utils/test_ranked_round_robin.py`
2. **Matrix Explanation Service Unit Tests:**
   `uv run pytest backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py`
3. **XAI Highlights SDUI Adapter Unit Tests:**
   `uv run pytest backend_v2/tests/unit/services/sdui/adapters/test_xai_highlights_adapter.py`
4. **Synthesis Distiller Wiring Unit Tests:**
   `uv run pytest backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py`
5. **Contract Verification Tests:**
   `uv run pytest backend_v2/tests/unit/test_epic93_contract_verification.py`
6. **Orchestrator Backend Audit Loop:**
   `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test`
7. **SDUI Adapters Backend Audit Loop:**
   `uv run python scripts/backend_audit_loop.py backend_v2/services/sdui/adapters/ --test`

### Anti-Happy-Path Scenarios
- **Scenario A (Unfiltered Sensor Quotes Extraction):** Sensor step with `data_type="text"` producing `results=[AtomResultDTO(tda_id="a1", source_quote="Sensor Evidence")]`, cross-referenced by a matrix step with `evaluated_atoms={"a1": "PASSED"}`.
  - *Expected Output:* Matrix justification contains `SUPPORTING EVIDENCE:\n- Sensor Evidence`.
- **Scenario B (Preservation of Cognitive Sensor `<source>` Blocks):** Sensor step with cognitive findings (specifically and exhaustively: analyst evaluations and verbatim evidence quotes) passed in `inputs["steps"]` alongside matrix steps.
  - *Expected Output:* `distilled_inputs` contains `<source id="DOC-1" title="Analyst">` with compressed sensor evaluations, proving that cognitive context is not pruned by layout targets.
- **Scenario C (Quote Length Truncation Boundary):** Provide a 500-character evidence quote.
  - *Expected Output:* Truncated deterministically to exactly `max_synthesis_quote_length` (300 characters) defined in `Settings`.
- **Scenario D (Quote Quantity Capping Boundary):** Provide a matrix referencing 12 sensor atoms, each with an authentic evidence quote.
  - *Expected Output:* Matrix justification contains exactly `max_synthesis_quotes_per_matrix` (5) quotes defined in `Settings`, deterministically discarding excess quotes.
- **Scenario E (Ranked Round-Robin Diversity Across Multiple Claims):** Provide a matrix with Claim A (4 quotes: lengths 100, 80, 60, 40) and Claim B (4 quotes: lengths 95, 75, 55, 35).
  - *Expected Output:* Matrix justification contains 3 quotes from Claim A (lengths 100, 80, 60) and 2 quotes from Claim B (lengths 95, 75) in alternating round-robin order up to total 5, preventing Claim A from taking all 5 spots.
- **Scenario F (Short Fragment Filtering):** Provide an evidence quote of length 4 ("yes!").
  - *Expected Output:* Excluded from `SUPPORTING EVIDENCE` due to < 15 character threshold.
- **Scenario G (Status-Aware Dual Justification - Mixed Pass/Fail):** Provide a matrix with 1 `PASSED` atom (with quote) and 4 `FAILED` atoms (with claim labels).
  - *Expected Output:* Justification contains BOTH `SUPPORTING EVIDENCE:` (with 1 quote) and `UNMET CRITERIA / DEFICITS:` (with 4 claim labels), eliminating Positivity Bias.
- **Scenario H (Unmet Criteria Capping Boundary):** Provide a matrix with 12 `FAILED` atoms.
  - *Expected Output:* Justification contains exactly `max_synthesis_unmet_criteria_per_matrix` (5) claim labels under `UNMET CRITERIA / DEFICITS:`.
- **Scenario I (Multilingual Localization Resolution):** Provide claim with translations `{"fi": "Suomalainen väite", "en": "English claim"}` and invoke with `target_locale="fi"`.
  - *Expected Output:* `UNMET CRITERIA / DEFICITS:` contains `"Suomalainen väite"`.
- **Scenario J (Missing / Unknown Block ID):** Provide a step with a `block_id` not present in `blocks_by_id`.
  - *Expected Output:* Handles the absence cleanly without `getattr` fallbacks or broad exception masking.
- **Scenario K (Malformed Atom Payload Observability):** Pass a step output containing a malformed atom dictionary in `results` (with missing mandatory fields or invalid types).
  - *Expected Output:* Emits `logger.warning` containing `ErrorCodes.INVALID_OUTPUT_SCHEMA.name`, step ID, block ID, and exception traceback (`exc_info=True`) without raising an unhandled crash or silently dropping the error.
- **Scenario L (Nullable Quote Guard Verification):** Pass an `AtomResultDTO` with `source_quote=None` (specifically: `contextual_override=True` with `ExecutionStatus.PASSED`, or `status=ExecutionStatus.FAILED`).
  - *Expected Output:* Handled cleanly without `TypeError` (`object of type 'NoneType' has no len()` or subscripting errors).
- **Scenario M (Malformed Matrix Output Payload Observability):** Pass a step output with a matrix `block_id` containing a malformed or invalid dictionary payload (specifically and exhaustively: extra forbidden keys violating `extra='forbid'`, non-numeric `normalized_score`, or out-of-range `normalized_score=1.5`).
  - *Expected Output:* Emits `logger.warning` containing `ErrorCodes.INVALID_OUTPUT_SCHEMA.name`, step ID, block ID, and exception traceback (`exc_info=True`) without raising an unhandled crash or terminating the pipeline, safely skipping the malformed matrix and processing remaining valid matrices.
- **Scenario N (Nullable Level Breakdown Guard Verification):** Pass a matrix step with `level_breakdown=None`.
  - *Expected Output:* Handled cleanly without `AttributeError: 'NoneType' object has no attribute 'items'`, resulting in empty `level_breakdown_str` and successfully producing justification without crash.
- **Scenario O (Missing or Whitespace-Only Target Locale in Distiller):** Pass a `HookState` where `metadata["target_locale"]` is missing, `None`, or contains whitespace-only `"   "`.
  - *Expected Output:* Hook fails fast immediately with `AppException(VALIDATION_FAILED)` before executing any asynchronous repository calls.
- **Scenario P (Pydantic V2 Mock Strictness & Zero Validation Bypass Gate):** Execute distiller hook tests without patching `Workflow.model_validate`, `PromptBlock.model_validate`, or passing unconstrained `MagicMock` instances as domain models.
  - *Expected Output:* All repository mocks supply valid schema dictionaries or Polyfactory models that pass real `model_validate(strict=False)` executions natively, proving that tests execute against real Pydantic runtime constraints without false-green mock bypasses.
- **Scenario Q (XAI Highlights Primacy Bias Elimination):** Provide `xai_highlights` containing 6 items for `coaching` and 6 items for `falsification`.
  - *Expected Output:* `XaiHighlightsAdapter` interleaves them using `ranked_round_robin_select`, populating both categories with their longest/most informative items rather than exhausting all capacity on `coaching`.

### Manual Verification
- Run local pipeline (`.\run_local.bat`) and verify in `client_debug.log` and `backend_debug.log` that the synthesis report contains full cognitive context from upstream sensors in `<source>` blocks, matrix justifications with authentic quotes and deficits, and fairly distributed XAI highlights in accordions.
