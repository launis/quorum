# Phase 3B: Full Hooks Pydantic V2 Migration & Hook Tests (PRODUCERS FIRST)

**Phase Title:** Phase 3B: Full Hooks Pydantic V2 Migration & Hook Tests (PRODUCERS FIRST)  
**Objective:** Eliminate ALL `isinstance(..., dict)`, `.get()`, and `getattr()` duck-typing across all 11 hook files and the 4 decomposed scoring modules, transitioning `HookState` to strictly typed `ExecutionInputsDTO` and `GlobalContextVarsDTO`, returning typed `HookDeltaDTO | None` from `HookResult.state_delta`, permanently sunsetting temporary `backend_v2/hooks/scoring/models.py`, and modernizing hook unit tests across all 4 ISTQB partitions.

**Source Reference:** @[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md#L234-L258] (Phase 3: Sub-Phase 3B: Full Hooks Pydantic V2 Migration & Hook Tests)

## User Review Required

> [!IMPORTANT]
> **Sub-Phase 3B Architectural Contracts & Producer-First Transition**:
> 1. **HookState Typed DTOs (`backend_v2/core/hook_registry.py`)**: `HookState.inputs` is upgraded from `dict[str, Any]` to `ExecutionInputsDTO`, `HookState.global_context_vars` is upgraded from `dict[str, Any]` to `GlobalContextVarsDTO`, and `HookResult.state_delta` is upgraded from `dict[str, Any] | None` to `HookDeltaDTO | None`.
> 2. **Mandatory Sunset of Temporary Models (`models.py`)**: As mandated by Epic 149 line 231, `backend_v2/hooks/scoring/models.py` served as temporary decomposition scaffolding during Sub-Phase 3A. In Sub-Phase 3B, it is permanently deleted (`[DELETE]`), its extraction logic is absorbed directly into `falsifier_hook.py`, and `backend_v2/hooks/scoring/__init__.py` is updated to remove temporary model re-exports.
> 3. **AST Guardrail Compliance (`scripts/_ast_guardrails.py`)**: Resolves all 8 pre-flight AST violations across `context_mapper.py` (`QGR001` getattr), `integrity.py` (`QGR002` .get), `linguistics.py` (`QGR002` .get), `llm.py` (`QGR001` hasattr), and `validation.py` (`QGR002` .get).
> 4. **4-Partition ISTQB Test Coverage**: All hook test suites are modernized to enforce ISTQB equivalence partitions: structured JSON DTOs, lists, strings, and falsy/empty values with strict `ExecutionMetadata(target_locale="fi")`.

## Target and Context Files

### Target Files
- `[MODIFY]` @[backend_v2/core/hook_registry.py]
- `[DELETE]` @[backend_v2/hooks/scoring/models.py]
- `[MODIFY]` @[backend_v2/hooks/scoring/__init__.py]
- `[MODIFY]` @[backend_v2/hooks/scoring/falsifier_hook.py]
- `[MODIFY]` @[backend_v2/hooks/scoring/passivity_hook.py]
- `[MODIFY]` @[backend_v2/hooks/scoring/matrix_hook.py]
- `[MODIFY]` @[backend_v2/hooks/scoring/normalization_hook.py]
- `[MODIFY]` @[backend_v2/hooks/validation.py]
- `[MODIFY]` @[backend_v2/hooks/source_verification_hook.py]
- `[MODIFY]` @[backend_v2/hooks/atom_flattening.py]
- `[MODIFY]` @[backend_v2/hooks/input_processing.py]
- `[MODIFY]` @[backend_v2/hooks/integrity.py]
- `[MODIFY]` @[backend_v2/hooks/linguistics.py]
- `[MODIFY]` @[backend_v2/hooks/llm.py]
- `[MODIFY]` @[backend_v2/hooks/context_mapper.py]
- `[MODIFY]` @[backend_v2/hooks/archival.py]
- `[MODIFY]` @[backend_v2/hooks/security.py]
- `[MODIFY]` @[backend_v2/hooks/hydration.py]
- `[MODIFY]` @[backend_v2/hooks/dlq_guard.py]
- `[MODIFY]` @[backend_v2/hooks/metadata.py]
- `[MODIFY]` @[backend_v2/hooks/metrics.py]
- `[MODIFY]` @[backend_v2/hooks/references.py]
- `[MODIFY]` @[backend_v2/hooks/interaction_hook.py]
- `[MODIFY]` @[backend_v2/tests/unit/core/test_hook_registry.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_scoring.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_hooks_validation.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_source_verification_hook.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_atom_flattening.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_input_processing.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_integrity.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_linguistics.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_llm.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_archival_fallback.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_security.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_hydration.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_dlq_guard.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_metadata.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_metrics.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_references.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_interaction_hook.py]

### Context Files (Read-Only)
- @[backend_v2/models/dtos/hook_state.py]
- @[backend_v2/models/execution_core.py]
- @[backend_v2/models/domain/prompt_blocks.py]
- @[backend_v2/settings.py]
- @[backend_v2/worker.py]

---

## Pre-Implementation Technical Debt Cleanups (Phase 1)

### Scoped Technical Debt Audit (Target Scope)
A pre-flight AST audit via `scripts/_ast_guardrails.py` and `scripts/backend_audit_loop.py` identified AST guardrail violations in `backend_v2/hooks/` and legacy dictionary initialization patterns across hook unit tests:

| File | Location | Anti-Pattern / Violation | Remediation in Phase 1 |
| :--- | :--- | :--- | :--- |
| `backend_v2/hooks/context_mapper.py` | L61, L62 | `QGR001`: Banned reflection duck-typing call `getattr(b, "computed_min")` | Replace with `isinstance(b, MatrixPromptBlock)` type narrowing to directly access `b.computed_min` and `b.computed_max`. |
| `backend_v2/hooks/integrity.py` | L66 | `QGR002`: Banned lazy fallback call `.get("dynamic_inputs", {})` | Replace with direct key existence check `inputs_dict["dynamic_inputs"] if "dynamic_inputs" in inputs_dict else {}`. |
| `backend_v2/hooks/linguistics.py` | L46, L47 | `QGR002`: Banned lazy fallback call `.get(key, default)` in domain code | Replace with direct key lookups on typed `state.inputs` and `state.global_context_vars`. |
| `backend_v2/hooks/llm.py` | L118 | `QGR001`: Banned reflection call `hasattr()` on configuration object | Replace with direct configuration lookup and validation. |
| `backend_v2/hooks/validation.py` | L293, L294 | `QGR002`: Banned lazy fallback call `hits_by_level.get(level, 0.0)` | Replace with `collections.defaultdict(float)` or explicit membership checks. |
| `backend_v2/hooks/dlq_guard.py` | L13 | `QGR007`: Missing `model_config = ConfigDict(strict=True, extra="forbid")` on `DLQAtomSchema` | Add strict `ConfigDict(strict=True, extra="forbid")` to `DLQAtomSchema`. |
| `backend_v2/hooks/` across 11 files | Across hooks | `QGR009`: `AppException` instantiated without typed `ErrorCodes` enum member | Pass typed `ErrorCodes` enum members as first argument to `AppException` across all hook files. |
| `backend_v2/tests/unit/hooks/` | Across 10 test files | Pydantic V2 `ValidationError`: Missing `metadata.target_locale` | Update test fixtures to instantiate `HookState(metadata=ExecutionMetadata(target_locale="fi"), ...)`. |

---

## 5-Column Architectural Directive Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Hook Core (`backend_v2/core/hook_registry.py`)** | Banned loose naked dictionaries `dict[str, Any]` in `HookState` and `HookResult`. | Strict `HookState.inputs: ExecutionInputsDTO`, `global_context_vars: GlobalContextVarsDTO`, and `HookResult.state_delta: HookDeltaDTO \| None`. | Retain existing singleton `HookRegistry` and `HookDependencies` DI container without adding heavy middleware layers. | `uv run pytest backend_v2/tests/unit/core/test_hook_registry.py` |
| **Scoring Models Sunset (`backend_v2/hooks/scoring/models.py`)** | Banned persistent temporary scaffolding and duplicate wrapper DTOs. | Permanently delete `models.py`. Absorb `ScoringPayloadWrapper` and `_extract_payloads` into `falsifier_hook.py`. | Zero persistent facade files beyond Sub-Phase 3B completion. | `scripts/audit_planner_output.py` verifying sunset deletion. |
| **Validation & Ingress Hooks (`validation.py`, `security.py`, `input_processing.py`, `hydration.py`, `interaction_hook.py`)** | Banned `.get()` fallbacks, raw dict mutations, and silent exception suppression. | Direct typed field access on `ExecutionInputsDTO` (`raw_inputs`, `dynamic_inputs`, `target_locale`), returning `HookDeltaDTO`. | Pure function execution without intermediate wrapper classes. | `uv run python scripts/backend_audit_loop.py backend_v2/hooks/validation.py backend_v2/hooks/security.py backend_v2/hooks/input_processing.py --test` |
| **Extraction & Integrity Hooks (`source_verification_hook.py`, `atom_flattening.py`, `integrity.py`, `linguistics.py`, `llm.py`, `context_mapper.py`, `archival.py`, `dlq_guard.py`, `metadata.py`, `metrics.py`, `references.py`)** | Banned `getattr()`, `hasattr()`, `.get()` chains, and unvalidated string slicing. | Strict `isinstance()` type narrowing on Domain Models (`MatrixPromptBlock`, `StepOutputDTO`, `AtomResultDTO`), returning `HookDeltaDTO`. | Standardize `HookDeltaDTO(delta={...})` return structure across all hooks. | `uv run python scripts/_ast_guardrails.py backend_v2/hooks/ --strict` (0 violations). |
| **Decomposed Scoring Package (`scoring/falsifier_hook.py`, `scoring/passivity_hook.py`, `scoring/matrix_hook.py`, `scoring/normalization_hook.py`)** | Banned `isinstance(state.inputs, dict)` assumptions and unvalidated state transit. | Accept typed `ExecutionInputsDTO`, process structured inputs via `_extract_payloads`, and return `HookDeltaDTO`. | Keep each sub-module <450 LOC adhering to `ki_god_code_prevention.md`. | `uv run python scripts/backend_audit_loop.py backend_v2/hooks/scoring/ --test` |

---

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK &amp; PRE-FLIGHT VERIFICATION">
    <action>Verify codebase state left by Sub-Phase 3A. Confirm `backend_v2/hooks/scoring/` is decomposed and temporary `models.py` is present for sunsetting.</action>
    <action>Verify all 11 hook files and 4 scoring modules exist in `backend_v2/hooks/`.</action>
    <constraint invariant="the_no_legacy_mandate">Verify zero backward compatibility shims or fallback dict parsing.</constraint>
    <directive>EPIC SYNC MANDATE: Maintain `EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md` and `EPIC_149_tracker.md` as Single Source of Truth.</directive>
  </step>

  <step id="1" name="PRE-IMPLEMENTATION TECHNICAL DEBT CLEANUPS &amp; AST GUARDRAIL REMEDIATION">
    <action>Fix `QGR001` in @[backend_v2/hooks/context_mapper.py]: Replace `getattr(b, "computed_min", None)` and `getattr(b, "computed_max", None)` with `isinstance(b, MatrixPromptBlock)` type narrowing inside `ContextMapper.build_ordinal_mapping`.</action>
    <action>Fix `QGR002` in @[backend_v2/hooks/integrity.py]: Replace `inputs_dict.get("dynamic_inputs", {})` with direct membership lookup `inputs_dict["dynamic_inputs"] if "dynamic_inputs" in inputs_dict else {}` in `_gather_source_texts`.</action>
    <action>Fix `QGR002` in @[backend_v2/hooks/linguistics.py]: Replace `.get("scan_for_performative_patterns")` with direct key checks on `state.inputs` and `state.global_context_vars` in `detect_performative_patterns`.</action>
    <action>Fix `QGR001` in @[backend_v2/hooks/llm.py]: Replace `hasattr(settings, ...)` reflection with direct configuration lookup and validation in `configure_llm_context_hook`.</action>
    <action>Fix `QGR002` in @[backend_v2/hooks/validation.py]: Replace `hits_by_level.get(level, 0.0)` with explicit dictionary initialization in `verify_anomaly`.</action>
    <action>Fix `QGR007` in @[backend_v2/hooks/dlq_guard.py]: Add `model_config = ConfigDict(strict=True, extra="forbid")` to `DLQAtomSchema`.</action>
    <action>Fix `QGR009` across all hook files: Pass typed `ErrorCodes` enum member as first argument to `AppException` across all hook files.</action>
    <action>Update test fixtures in @[backend_v2/tests/unit/hooks/] and @[backend_v2/tests/unit/] to pass `ExecutionMetadata(target_locale="fi")` instead of empty dicts.</action>
    <constraint invariant="ast_guardrail_mandate">Execute `uv run python scripts/_ast_guardrails.py backend_v2/hooks/ --strict` to verify 0 AST violations before functional refactoring.</constraint>
  </step>

  <step id="2" name="CORE HOOK REGISTRY &amp; DTO MODERNIZATION">
    <action>In @[backend_v2/core/hook_registry.py]:
      1. Import `ExecutionInputsDTO`, `GlobalContextVarsDTO`, `HookDeltaDTO` from `backend_v2.models.dtos.hook_state`.
      2. Update `HookState`:
         - `inputs: ExecutionInputsDTO = Field(...)`
         - `global_context_vars: GlobalContextVarsDTO = Field(default_factory=GlobalContextVarsDTO)`
      3. Update `HookResult`:
         - `state_delta: HookDeltaDTO | None = Field(default=None)`
      4. In `HookRegistry.execute()`: verify returned `result.state_delta` is `HookDeltaDTO | None`.</action>
    <action>In @[backend_v2/tests/unit/core/test_hook_registry.py]:
      1. Update unit tests to instantiate `HookState(inputs=ExecutionInputsDTO(...), global_context_vars=GlobalContextVarsDTO(...))` and assert `HookDeltaDTO` return values.</action>
    <constraint invariant="strict_pydantic_v2_rust">Enforce strict Pydantic V2 validation on all HookState and HookResult boundaries.</constraint>
  </step>

  <step id="3" name="VALIDATION, INGRESS &amp; SECURITY HOOKS MIGRATION">
    <action>In @[backend_v2/hooks/validation.py]:
      1. Refactor `verify_structure` to read from `state.inputs.raw_inputs` and `state.inputs.dynamic_inputs`, returning `HookDeltaDTO(delta={"validation_result": ...})`.
      2. Refactor `verify_output_language` to read from `state.inputs` and `state.metadata.target_locale`, returning `HookDeltaDTO(delta={"_system_warnings": ...})`.
      3. Refactor `verify_anomaly` to read from `state.inputs.raw_inputs`, returning `HookDeltaDTO(delta={"llm_anomaly_retry_requested": True})` or `HookDeltaDTO()`.
    </action>
    <action>In @[backend_v2/hooks/security.py]:
      1. Refactor `sanitize_text_hook` to read from `state.inputs.raw_inputs`, returning `HookDeltaDTO(delta={"sanitization_result": ...})`.
    </action>
    <action>In @[backend_v2/hooks/input_processing.py]:
      1. Refactor `process_inputs` to read from `state.inputs.raw_inputs` and `state.global_context_vars.vars`, returning `HookDeltaDTO(delta={"inputs": output_dict}, metadata_updates={"estimated_token_count": estimated_token_count})`.
    </action>
    <action>In @[backend_v2/hooks/hydration.py]:
      1. Refactor `hydrate_global_inputs_hook` to read from `state.global_context_vars.vars` and update `state.inputs`, returning `HookDeltaDTO(delta={"inputs": inputs})`.
    </action>
    <action>In @[backend_v2/hooks/interaction_hook.py]:
      1. Refactor `analyze_interaction_role` to read from `state.inputs.raw_inputs`, returning `HookDeltaDTO(delta={"interaction_analysis": ...})`.
    </action>
    <action>Modernize test suites: @[backend_v2/tests/unit/test_hooks_validation.py], @[backend_v2/tests/unit/test_security.py], @[backend_v2/tests/unit/hooks/test_input_processing.py], @[backend_v2/tests/unit/hooks/test_hydration.py], @[backend_v2/tests/unit/hooks/test_interaction_hook.py].</action>
    <constraint invariant="no_naked_dicts_in_state">Eliminate naked dicts in state transit; enforce typed DTO boundaries.</constraint>
  </step>

  <step id="4" name="EXTRACTION, CONTEXT &amp; INTEGRITY HOOKS MIGRATION">
    <action>In @[backend_v2/hooks/source_verification_hook.py]:
      1. Refactor `_extract_text_polymorphically` and `source_verification_hook` to consume `state.inputs`, returning `HookDeltaDTO(delta={"global_context_vars": {"external_evidence": ...}}, metadata_updates={"mcp_audit_traces": ...})`.
    </action>
    <action>In @[backend_v2/hooks/atom_flattening.py]:
      1. Refactor `process_matrix_flattening` to return `HookDeltaDTO(delta=output_payload.model_dump(mode="json"))` or `HookDeltaDTO()`.
    </action>
    <action>In @[backend_v2/hooks/context_mapper.py]:
      1. Refactor `ContextMapper.build_ordinal_mapping` to use strict `isinstance(b, MatrixPromptBlock)` type narrowing.</action>
    <action>In @[backend_v2/hooks/integrity.py]:
      1. Refactor `verify_citation_integrity_hook` and `enforce_hypothesis_linking_hook` to read from `state.inputs.raw_inputs` and `state.global_context_vars.vars`, returning `HookDeltaDTO(delta=...)`.
    </action>
    <action>In @[backend_v2/hooks/linguistics.py]:
      1. Refactor `detect_performative_patterns` to read from `state.inputs.raw_inputs` and return `HookDeltaDTO(delta={"global_context_vars": {"step_linguistics": ...}})`.
    </action>
    <action>In @[backend_v2/hooks/llm.py]:
      1. Refactor `configure_llm_context_hook` to return `HookDeltaDTO(delta={"llm_config": ...})`.
    </action>
    <action>In @[backend_v2/hooks/archival.py]:
      1. Refactor `retrieve_precedent_hook` to return `HookDeltaDTO(delta={"archivist_precedents": ...})`.
    </action>
    <action>In @[backend_v2/hooks/dlq_guard.py]:
      1. Refactor `dlq_strict_mode_guard_hook` to read from `state.inputs.raw_inputs` and return `HookDeltaDTO()`.
    </action>
    <action>In @[backend_v2/hooks/metadata.py]:
      1. Refactor `inject_step_metadata` to read from `state.global_context_vars.vars` and return `HookDeltaDTO(delta={...})`.
    </action>
    <action>In @[backend_v2/hooks/metrics.py]:
      1. Refactor `calculate_control_ratio` and `calculate_text_metrics` to read from `state.inputs.raw_inputs` and return `HookDeltaDTO(delta={...})`.
    </action>
    <action>In @[backend_v2/hooks/references.py]:
      1. Refactor `generate_bibliography` hook to return `HookDeltaDTO(delta={"bibliography": ...})`.
    </action>
    <action>Modernize test suites: @[backend_v2/tests/unit/hooks/test_source_verification_hook.py], @[backend_v2/tests/unit/hooks/test_atom_flattening.py], @[backend_v2/tests/unit/hooks/test_integrity.py], @[backend_v2/tests/unit/hooks/test_linguistics.py], @[backend_v2/tests/unit/hooks/test_llm.py], @[backend_v2/tests/unit/hooks/test_archival_fallback.py], @[backend_v2/tests/unit/hooks/test_dlq_guard.py], @[backend_v2/tests/unit/test_metadata.py], @[backend_v2/tests/unit/hooks/test_metrics.py], @[backend_v2/tests/unit/test_references.py].</action>
    <constraint invariant="universal_fail_fast">Enforce Fail-Fast on missing required inputs and invalid DTO schemas.</constraint>
  </step>

  <step id="5" name="SCORING PACKAGE PYDANTIC V2 TRANSITION &amp; MODELS SUNSET">
    <action>Permanently delete temporary models module: `[DELETE]` @[backend_v2/hooks/scoring/models.py].</action>
    <action>In @[backend_v2/hooks/scoring/__init__.py]:
      1. Remove imports and re-exports of `ScoringPayloadWrapper` and `StateInputWrapper`.
      2. Re-export exclusively `apply_scoring_logic_hook`, `enforce_passivity_penalty_hook`, `matrix_scoring_hook`, `normalize_matrix_scores_hook`, and `recalculate` with explicit `__all__` and redundant aliases.</action>
    <action>In @[backend_v2/hooks/scoring/falsifier_hook.py]:
      1. Absorb `ScoringPayloadWrapper` and `_extract_payloads` directly as pure helper functions.
      2. Modernize `apply_scoring_logic_hook` to accept `HookState` with `ExecutionInputsDTO` and return `HookDeltaDTO(delta=...)`.</action>
    <action>In @[backend_v2/hooks/scoring/passivity_hook.py]:
      1. Modernize `enforce_passivity_penalty_hook` to accept `HookState` with `ExecutionInputsDTO` and return `HookDeltaDTO(delta=...)`.</action>
    <action>In @[backend_v2/hooks/scoring/matrix_hook.py]:
      1. Modernize `matrix_scoring_hook` to accept `HookState` with `ExecutionInputsDTO` and return `HookDeltaDTO(delta=...)`.</action>
    <action>In @[backend_v2/hooks/scoring/normalization_hook.py]:
      1. Modernize `normalize_matrix_scores_hook` to accept `HookState` with `ExecutionInputsDTO` and return `HookDeltaDTO(delta=...)`.</action>
    <action>In @[backend_v2/tests/unit/hooks/test_scoring.py]:
      1. Modernize all 26 scoring test fixtures to pass `HookState(inputs=ExecutionInputsDTO(...), global_context_vars=GlobalContextVarsDTO(...), metadata=ExecutionMetadata(target_locale="fi"))`.
      2. Assert `HookDeltaDTO` return structures.
      3. Verify coverage across all 4 ISTQB partitions (structured dict, list, string, falsy).</action>
    <constraint invariant="anti_god_file_dumping">Keep all scoring submodules strictly below their line limits (<450 LOC).</constraint>
  </step>

  <step id="6" name="UNIVERSAL QUALITY GATE, AST AUDIT &amp; SEMANTIC PARITY VERIFICATION">
    <action>Run backend quality audit loop across all hooks: `uv run python scripts/backend_audit_loop.py backend_v2/hooks/ backend_v2/core/hook_registry.py --test`.</action>
    <action>Run AST guardrails check: `uv run python scripts/_ast_guardrails.py --strict` (0 violations).</action>
    <action>Run full hooks unit test suite: `uv run pytest backend_v2/tests/unit/hooks/`.</action>
    <action>Run SDUI semantic parity gate: `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`.</action>
    <constraint invariant="zero_deprecation_mandate">Ensure 0 MyPy typing errors, 0 Ruff lint errors, and 100% test pass rate.</constraint>
  </step>

  <dod_checklist>
    - [x] `HookState.inputs: dict[str, Any]` replaced with typed `ExecutionInputsDTO`.
    - [x] `HookState.global_context_vars: dict[str, Any]` replaced with typed `GlobalContextVarsDTO`.
    - [x] `HookResult.state_delta: dict[str, Any] | None` replaced with typed `HookDeltaDTO | None`.
    - [x] All 8 pre-flight AST violations resolved (`getattr`, `hasattr`, `.get()`).
    - [x] [DELETE] Temporary models module @[backend_v2/hooks/scoring/models.py] permanently deleted.
    - [x] All 11 hook files and 4 scoring modules migrated to Pydantic V2 HookState and HookDeltaDTO.
    - [x] All hook unit tests in @[backend_v2/tests/unit/hooks/] modernized atomically to cover 4 ISTQB partitions.
    - [x] Quality gate passes: `uv run python scripts/backend_audit_loop.py backend_v2/hooks/ backend_v2/core/hook_registry.py --test`.
    - [x] AST Guardrails pass with 0 errors: `uv run python scripts/_ast_guardrails.py --strict`.
    - [x] SDUI cross-domain parity passes: `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`.
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
    <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
    <knowledge_item>@[ki_domain_model_prompt_separation.md]</knowledge_item>
    <knowledge_item>@[ki_neuro_symbolic_agentic_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
    <knowledge_item>@[ki_app_error_boundary.md]</knowledge_item>
  </required_context_rules>

  <touched_artifacts>
    <backend>@[backend_v2/core/hook_registry.py]</backend>
    <backend>@[backend_v2/hooks/scoring/falsifier_hook.py]</backend>
    <backend>@[backend_v2/hooks/scoring/passivity_hook.py]</backend>
    <backend>@[backend_v2/hooks/scoring/matrix_hook.py]</backend>
    <backend_v2>@[backend_v2/hooks/scoring/normalization_hook.py]</backend_v2>
    <backend>@[backend_v2/hooks/scoring/__init__.py]</backend>
    <backend>@[backend_v2/hooks/validation.py]</backend>
    <backend>@[backend_v2/hooks/source_verification_hook.py]</backend>
    <backend>@[backend_v2/hooks/atom_flattening.py]</backend>
    <backend>@[backend_v2/hooks/input_processing.py]</backend>
    <backend>@[backend_v2/hooks/integrity.py]</backend>
    <backend>@[backend_v2/hooks/linguistics.py]</backend>
    <backend>@[backend_v2/hooks/llm.py]</backend>
    <backend>@[backend_v2/hooks/context_mapper.py]</backend>
    <backend>@[backend_v2/hooks/archival.py]</backend>
    <backend>@[backend_v2/hooks/security.py]</backend>
    <backend>@[backend_v2/hooks/hydration.py]</backend>
    <backend>@[backend_v2/hooks/dlq_guard.py]</backend>
    <backend>@[backend_v2/hooks/metadata.py]</backend>
    <backend>@[backend_v2/hooks/metrics.py]</backend>
    <backend>@[backend_v2/hooks/references.py]</backend>
    <backend>@[backend_v2/hooks/interaction_hook.py]</backend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT modify `backend_v2/services/orchestrator/` in Phase 3B (strictly reserved for Phase 4).
    - Do NOT re-introduce raw dict returns in `HookResult.state_delta`.
    - Do NOT retain `backend_v2/hooks/scoring/models.py` after Sub-Phase 3B.
  </anti_targets>

  <validation_gate>
    uv run python scripts/backend_audit_loop.py backend_v2/hooks/ backend_v2/core/hook_registry.py --test
  </validation_gate>
</execution_protocol>
```
