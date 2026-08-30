# Phase 3A: scoring.py God Code Decomposition (Strangler Fig Proxy Pattern)

**Phase Title:** Phase 3A: scoring.py God Code Decomposition (Strangler Fig Proxy Pattern)  
**Objective:** Decompose the monolithic 1,348 LOC (64.3 KB) `scoring.py` file into a modular `backend_v2/hooks/scoring/` package with 4 isolated modules (<400 LOC each: `falsifier_hook.py`, `passivity_hook.py`, `matrix_hook.py`, `normalization_hook.py`), a temporary models module `models.py` (<120 LOC), and a Strangler Fig facade in `__init__.py` re-exporting all legacy symbols per PEP 484 and `ki_god_code_prevention.md` to preserve 100% of existing behavior, eliminate all 14 AST guardrail violations, expand test coverage to include `apply_scoring_logic_hook` and `enforce_passivity_penalty_hook`, and achieve 100% unit test pass rates across `backend_v2/tests/unit/hooks/test_scoring.py`.

**Source Reference:** @[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md#L224-L233] (Phase 3: Sub-Phase 3A: scoring.py God Code Decomposition)

## User Review Required

> [!IMPORTANT]
> **Sub-Phase Boundary & Strangler Fig Proxy Mandate**:
> 1. **Sub-Phase 3A Scope**: Pure structural God Code decomposition of `backend_v2/hooks/scoring.py` into `backend_v2/hooks/scoring/` package. All existing hook behavior, state delta contracts, and dictionary structures are 100% preserved. Full Pydantic V2 Hook State transition across all 11 hook files is deferred to Sub-Phase 3B per Epic 149 specifications.
> 2. **Temporary Models Module (`models.py`)**: As per Epic 149 line 231, `backend_v2/hooks/scoring/models.py` serves strictly as a temporary DTO module for structural decomposition (`ScoringPayloadWrapper`, `StateInputWrapper`, `_extract_payloads`). **MANDATORY SUNSET**: All models in this file MUST be either absorbed into individual hook modules or migrated to `@[backend_v2/models/dtos/]` during Sub-Phase 3B. This file MUST NOT persist beyond Sub-Phase 3B completion.
> 3. **PEP 484 Compliant Strangler Fig Facade**: `backend_v2/hooks/scoring/__init__.py` explicitly declares `__all__` and redundant import aliases (`from backend_v2.hooks.scoring.falsifier_hook import apply_scoring_logic_hook as apply_scoring_logic_hook`, and all other scoring exports) to guarantee 100% zero-regression compatibility with downstream consumers (`backend_v2/services/execution.py`, `backend_v2/core/hook_registry.py`) and pass `mypy --strict`.

## Target and Context Files

### Target Files
- `[DELETE]` @[backend_v2/hooks/scoring.py]
- `[NEW]` @[backend_v2/hooks/scoring/__init__.py]
- `[NEW]` @[backend_v2/hooks/scoring/models.py]
- `[NEW]` @[backend_v2/hooks/scoring/falsifier_hook.py]
- `[NEW]` @[backend_v2/hooks/scoring/passivity_hook.py]
- `[NEW]` @[backend_v2/hooks/scoring/matrix_hook.py]
- `[NEW]` @[backend_v2/hooks/scoring/normalization_hook.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_scoring.py]

### Context Files (Read-Only)
- @[backend_v2/core/hook_registry.py#L68-L79]
- @[backend_v2/models/execution_core.py#L22-L82]
- @[backend_v2/services/execution.py#L133-L1370]
- @[backend_v2/hooks/__init__.py]
- @[backend_v2/utils/scoring/__init__.py#L15-L52]

---

## Pre-Implementation Technical Debt Cleanups (Phase 1)

### Scoped Technical Debt Audit (Target Scope)
A pre-flight AST audit via `scripts/_ast_guardrails.py` and `scripts/backend_audit_loop.py` identified 14 AST guardrail violations in `backend_v2/hooks/scoring.py` and 18 MyPy type errors in `backend_v2/tests/unit/hooks/test_scoring.py`:

| File | Location | Anti-Pattern / Violation | Remediation in Phase 1 |
| :--- | :--- | :--- | :--- |
| `backend_v2/hooks/scoring.py` | L249, L259, L619, L744, L888, L940 | `QGR002`: Banned lazy fallback call: `.get(key, default)` in domain code | Replace `.get()` with direct key access, `in` membership check, or strict Pydantic model validation. |
| `backend_v2/hooks/scoring.py` | L256, L733, L735, L745, L796, L806, L891, L895 | `QGR001`: Banned reflection duck-typing / mutation call: `hasattr()` and `getattr()` | Replace with `isinstance()` type narrowing against typed DTO models (`StepOutputDTO`, `AtomResultDTO`, `LightweightMatrixOutput`). |
| `backend_v2/tests/unit/hooks/test_scoring.py` | L146, L233, L406, L461, L510, L561, L732, L785, L843, L892, L924, L976, L1051, L1122, L1194, L1281 | `MyPy` & Pydantic V2: Incompatible type for `HookState.metadata` (`dict` instead of `ExecutionMetadata`) | Update test helper fixtures to construct `HookState(metadata=ExecutionMetadata(target_locale="fi"), ...)` satisfying strict Pydantic V2 and MyPy schemas. |
| `backend_v2/tests/unit/hooks/test_scoring.py` | L56-L59 | `QGR005` & MyPy: Raw string literal `'matrix'` and un-typed scale dictionary mutation | Replace `'matrix'` with `PromptBlockCategory.MATRIX.value` and type `scales` dictionary explicitly. |
| `backend_v2/tests/unit/hooks/test_scoring.py` | L267, L272, L1021, L1093, L1164, L1165, L1236 | `QGR002`: Banned lazy fallback call `.get()` in test assertion helpers | Replace `.get()` with direct dictionary indexing in test assertions. |

---

## 5-Column Architectural Directive Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Temporary Models (`backend_v2/hooks/scoring/models.py`)** | Banned unvalidated payload extraction and loose nested dictionary iterations. | Strict `ScoringPayloadWrapper` and `StateInputWrapper` with `ConfigDict(extra="ignore", frozen=True)`. Pure extractor `_extract_payloads`. | Retain strictly only shared extraction DTOs (<120 LOC). Banned speculative domain models. | `uv run python scripts/_ast_guardrails.py backend_v2/hooks/scoring/models.py --strict` |
| **Falsifier Hook (`backend_v2/hooks/scoring/falsifier_hook.py`)** | Banned `.get("justification")` (L249, L259) and `getattr(step_val, "payload")` (L256). | Clean pure helpers `_extract_guard_flag`, `_extract_falsifier_data`, `_calculate_falsifier_penalty` and registered hook `apply_scoring_logic_hook`. | Direct score accumulation without intermediate scoring manager classes (<250 LOC). | Dedicated unit tests `test_apply_scoring_logic_hook_*` with positive and negative partitions in `test_scoring.py`. |
| **Passivity Hook (`backend_v2/hooks/scoring/passivity_hook.py`)** | Banned legacy `score_card` detection bypass and silent fallback multipliers. | Strict `enforce_passivity_penalty_hook` evaluating `LightweightMatrixOutput` against `math_min` extracted from `scales`. | Keep logic in single pure async hook function (<200 LOC). Banned redundant penalty calculation wrappers. | Dedicated unit tests `test_enforce_passivity_penalty_hook_*` in `test_scoring.py`. |
| **Matrix Hook (`backend_v2/hooks/scoring/matrix_hook.py`)** | Banned `hasattr(ev, "_dlq_status")` (L733, L796), `hasattr(merged_facts, "model_dump")` (L745), `.get("extracted_facts")` (L744), `.get("extensions")` (L888). | Strict `matrix_scoring_hook` with `isinstance()` type narrowing against `AtomResultDTO` and `BaseModel`. Integration with `ASTEvaluator`. | Keep single orchestrating hook (<480 LOC). Decouple recalculation engine into `normalization_hook.py`. | Unit test suite `test_matrix_scoring_hook_*` passing 100% with `ExecutionMetadata(target_locale="fi")`. |
| **Normalization Hook (`backend_v2/hooks/scoring/normalization_hook.py`)** | Banned `.get(key, default)` in matrix extension assembly (L940) and implicit scale defaults. | Strict `normalize_matrix_scores_hook` and `recalculate` engine deriving bounds exclusively from `scales` array. | Retain unified mathematical calculation engine without duplicate scaling classes (<400 LOC). | `uv run pytest backend_v2/tests/unit/hooks/test_scoring.py` and `backend_audit_loop.py`. |
| **Strangler Fig Facade (`backend_v2/hooks/scoring/__init__.py`)** | Banned implicit re-exports (`from module import Symbol`) crashing `mypy --strict`. | Explicit `__all__` list and redundant PEP 484 aliases (`Symbol as Symbol`) for all 5 hook functions and 2 temporary DTOs. | Pure re-export facade (<40 LOC). Zero business logic in `__init__.py`. | `uv run mypy backend_v2/hooks/scoring/` with 0 type errors. |

---

## AST-Exact Line Boundaries Mapping

```
Source File: backend_v2/hooks/scoring.py (1,348 LOC)
├── #L39-L47    (9 LOC)   ClassDef: ScoringPayloadWrapper          ──> backend_v2/hooks/scoring/models.py
├── #L50-L56    (7 LOC)   ClassDef: StateInputWrapper              ──> backend_v2/hooks/scoring/models.py
├── #L59-L111   (53 LOC)  FunctionDef: _extract_payloads           ──> backend_v2/hooks/scoring/models.py
├── #L114-L127  (14 LOC)  FunctionDef: _extract_guard_flag         ──> backend_v2/hooks/scoring/falsifier_hook.py
├── #L130-L142  (13 LOC)  FunctionDef: _extract_falsifier_data     ──> backend_v2/hooks/scoring/falsifier_hook.py
├── #L145-L158  (14 LOC)  FunctionDef: _calculate_falsifier_penalty ─> backend_v2/hooks/scoring/falsifier_hook.py
├── #L161-L342  (182 LOC) FunctionDef: apply_scoring_logic_hook    ──> backend_v2/hooks/scoring/falsifier_hook.py
├── #L345-L516  (172 LOC) AsyncFunctionDef: enforce_passivity_penalty_hook ──> backend_v2/hooks/scoring/passivity_hook.py
├── #L519-L975  (457 LOC) AsyncFunctionDef: matrix_scoring_hook    ──> backend_v2/hooks/scoring/matrix_hook.py
├── #L978-L1187 (210 LOC) AsyncFunctionDef: normalize_matrix_scores_hook ──> backend_v2/hooks/scoring/normalization_hook.py
└── #L1190-L1347 (158 LOC) AsyncFunctionDef: recalculate         ──> backend_v2/hooks/scoring/normalization_hook.py
```

---

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 2. Verify all repositories return typed Pydantic models.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in [DELETE] @[backend_v2/hooks/scoring.py] (1,348 LOC) and @[backend_v2/tests/unit/hooks/test_scoring.py] (1,325 LOC).</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [x] `scoring.py` decomposed into `backend_v2/hooks/scoring/` package with all modules strictly under line limits:
      - `models.py` (<120 LOC): `ScoringPayloadWrapper`, `StateInputWrapper`, and `_extract_payloads` shared extraction logic.
      - `falsifier_hook.py` (<250 LOC): `apply_scoring_logic_hook` hook and `_extract_guard_flag`, `_extract_falsifier_data`, `_calculate_falsifier_penalty`.
      - `passivity_hook.py` (<200 LOC): `enforce_passivity_penalty_hook` hook.
      - `matrix_hook.py` (<480 LOC): `matrix_scoring_hook` hook and quote evidence validation and AST Evaluator integration.
      - `normalization_hook.py` (<400 LOC): `normalize_matrix_scores_hook` and `recalculate` decoupled hybrid calculation engine.
      - `__init__.py`: Strangler Fig facade re-exporting `apply_scoring_logic_hook`, `enforce_passivity_penalty_hook`, `matrix_scoring_hook`, `normalize_matrix_scores_hook`, `recalculate`, `ScoringPayloadWrapper`, and `StateInputWrapper` with explicit `__all__` and redundant PEP 484 aliases.
    - [x] Monolithic `backend_v2/hooks/scoring.py` deleted without leaving redundant duplicate file collisions.
    - [x] All 14 AST guardrail violations (`QGR001` reflection, `QGR002` `.get()`) in scoring logic remediated.
    - [x] All 18 MyPy typing errors in @[backend_v2/tests/unit/hooks/test_scoring.py] resolved with `ExecutionMetadata(target_locale="fi")`.
    - [x] Expanded unit test suites for `apply_scoring_logic_hook` and `enforce_passivity_penalty_hook` added with positive and negative ISTQB boundary partitions.
    - [x] Quality gate passes 100%: `uv run python scripts/backend_audit_loop.py backend_v2/hooks/scoring/ backend_v2/tests/unit/hooks/test_scoring.py --test --ast-strict`.
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
    <backend>[DELETE] @[backend_v2/hooks/scoring.py]</backend>
    <backend>[NEW] @[backend_v2/hooks/scoring/__init__.py]</backend>
    <backend>[NEW] @[backend_v2/hooks/scoring/models.py]</backend>
    <backend>[NEW] @[backend_v2/hooks/scoring/falsifier_hook.py]</backend>
    <backend>[NEW] @[backend_v2/hooks/scoring/passivity_hook.py]</backend>
    <backend>[NEW] @[backend_v2/hooks/scoring/matrix_hook.py]</backend>
    <backend>[NEW] @[backend_v2/hooks/scoring/normalization_hook.py]</backend>
    <backend>@[backend_v2/tests/unit/hooks/test_scoring.py]</backend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT migrate HookState to Pydantic V2 in Sub-Phase 3A (strictly reserved for Sub-Phase 3B).
    - Do NOT modify `backend_v2/services/orchestrator/` in Sub-Phase 3A (reserved for Phase 4).
    - Do NOT modify database repositories or models (completed in Phase 2).
  </anti_targets>

  <step id="1" name="PRE-IMPLEMENTATION TECHNICAL DEBT CLEANUPS IN TEST SUITE">
    <action>In @[backend_v2/tests/unit/hooks/test_scoring.py], update test helper fixtures to instantiate `HookState` with `metadata=ExecutionMetadata(target_locale="fi")`.</action>
    <action>Remediate `QGR005` on line 56 by replacing raw string `"matrix"` with `PromptBlockCategory.MATRIX.value`.</action>
    <action>Remediate `QGR002` in test assertion helpers (lines 267, 272, 1021, 1093, 1164, 1165, 1236) by replacing `.get()` with direct dict indexing.</action>
    <action>Add comprehensive unit test suites for `apply_scoring_logic_hook` (`test_apply_scoring_logic_hook_*`) and `enforce_passivity_penalty_hook` (`test_enforce_passivity_penalty_hook_*`) with positive, boundary, and negative test partitions.</action>
    <action>Run baseline test suite: `uv run pytest backend_v2/tests/unit/hooks/test_scoring.py` to establish verified green test baseline.</action>
    <constraint invariant="touched_scope_tech_debt_mandate">All discovered technical debt in touched test files must be cleaned in Phase 1 before codebase decomposition begins.</constraint>
  </step>

  <step id="2" name="CREATE TEMPORARY MODELS MODULE (MODELS.PY)">
    <action>Create [NEW] @[backend_v2/hooks/scoring/models.py] (<120 LOC).</action>
    <action>Extract `ScoringPayloadWrapper` (Pydantic model: `sanitization_result`, `step_input_processing`, `step_falsifier`, `step_panel`, `evaluative_matrices`) with `ConfigDict(extra="ignore", frozen=True)` from [DELETE] @[backend_v2/hooks/scoring.py#L39-L47].</action>
    <action>Extract `StateInputWrapper` (Pydantic model: `steps`, `inputs`, `raw_inputs`) with `ConfigDict(extra="ignore", frozen=True)` from [DELETE] @[backend_v2/hooks/scoring.py#L50-L56].</action>
    <action>Extract `_extract_payloads(data: dict[str, Any]) -> list[ScoringPayloadWrapper]` pure extractor function from [DELETE] @[backend_v2/hooks/scoring.py#L59-L111].</action>
    <action>Add PEP 257 docstrings and explicit `__all__ = ["ScoringPayloadWrapper", "StateInputWrapper", "_extract_payloads"]`.</action>
    <constraint invariant="anti_god_file_dumping">Module must remain pure, minimal (<120 LOC), and contain only shared intermediate extraction wrappers.</constraint>
  </step>

  <step id="3" name="DECOMPOSE FALSIFIER &amp; PASSIVITY HOOKS">
    <action>Create [NEW] @[backend_v2/hooks/scoring/falsifier_hook.py] (<250 LOC):
      - Extract `_extract_guard_flag(data: dict[str, Any]) -> bool | None` from [DELETE] @[backend_v2/hooks/scoring.py#L114-L127].
      - Extract `_extract_falsifier_data(data: dict[str, Any]) -> FalsifierData | None` from [DELETE] @[backend_v2/hooks/scoring.py#L130-L142].
      - Extract `_calculate_falsifier_penalty(falsifier_data: FalsifierData | None) -> bool` from [DELETE] @[backend_v2/hooks/scoring.py#L145-L158].
      - Extract `@hook_registry.register(name="apply_scoring_logic") def apply_scoring_logic_hook(state: HookState, deps: HookDependencies) -> HookResult` from [DELETE] @[backend_v2/hooks/scoring.py#L161-L342].
      - Eliminate `QGR002` `.get("justification", "")` calls (lines 249, 259) using direct dictionary key containment checks.
      - Eliminate `QGR001` `getattr(step_val, "payload", None)` (line 256) using `isinstance(step_val, StepOutputDTO)` type narrowing.
      - Add explicit `__all__ = ["apply_scoring_logic_hook"]`.
    </action>
    <action>Create [NEW] @[backend_v2/hooks/scoring/passivity_hook.py] (<200 LOC):
      - Extract `@hook_registry.register(name="enforce_passivity_penalty") async def enforce_passivity_penalty_hook(state: HookState, deps: HookDependencies) -> HookResult` from [DELETE] @[backend_v2/hooks/scoring.py#L345-L516].
      - Retain prompt block schema validation and `math_min` penalty multiplier logic.
      - Add explicit `__all__ = ["enforce_passivity_penalty_hook"]`.
    </action>
    <constraint invariant="srp_god_method_mandate">Each hook file must encapsulate a single responsibility and stay strictly under line limits.</constraint>
  </step>

  <step id="4" name="DECOMPOSE MATRIX &amp; NORMALIZATION HOOKS">
    <action>Create [NEW] @[backend_v2/hooks/scoring/matrix_hook.py] (<480 LOC):
      - Extract `@hook_registry.register(name="matrix_scoring_hook") async def matrix_scoring_hook(state: HookState, deps: HookDependencies) -> HookResult` from [DELETE] @[backend_v2/hooks/scoring.py#L519-L975].
      - Remediate `QGR002` on line 619 (`execution_data.metadata.get("target_locale")`) by directly accessing `execution_data.metadata.target_locale`.
      - Remediate `QGR001` on lines 733, 735, 745, 796, 806, 891, 895 using `isinstance()` type narrowing against typed DTO models (`StepOutputDTO`, `AtomResultDTO`, `BaseModel`, `Enum`).
      - Remediate `QGR002` on lines 744, 888, 940 using direct dictionary lookup or explicit `in` checks.
      - Integrate with `recalculate` from normalization module.
      - Add explicit `__all__ = ["matrix_scoring_hook"]`.
    </action>
    <action>Create [NEW] @[backend_v2/hooks/scoring/normalization_hook.py] (<400 LOC):
      - Extract `@hook_registry.register(name="normalize_matrix_scores") async def normalize_matrix_scores_hook(state: HookState, deps: HookDependencies) -> HookResult` from [DELETE] @[backend_v2/hooks/scoring.py#L978-L1187].
      - Extract `async def recalculate(payload: dict[str, Any], profile_id: str | None, deps: HookDependencies) -> None` from [DELETE] @[backend_v2/hooks/scoring.py#L1190-L1347].
      - Remediate `QGR002` on line 940.
      - Add explicit `__all__ = ["normalize_matrix_scores_hook", "recalculate"]`.
    </action>
    <constraint invariant="remedial_refactoring_coverage">Zero behavioral regression in matrix scoring math and normalization algorithms.</constraint>
  </step>

  <step id="5" name="STRANGLER FIG FACADE &amp; MONOLITH PURGE">
    <action>Create [NEW] @[backend_v2/hooks/scoring/__init__.py]:
      - Re-export `apply_scoring_logic_hook` from `falsifier_hook.py` (with redundant alias `apply_scoring_logic_hook as apply_scoring_logic_hook`).
      - Re-export `enforce_passivity_penalty_hook` from `passivity_hook.py` (with redundant alias `enforce_passivity_penalty_hook as enforce_passivity_penalty_hook`).
      - Re-export `matrix_scoring_hook` from `matrix_hook.py` (with redundant alias `matrix_scoring_hook as matrix_scoring_hook`).
      - Re-export `normalize_matrix_scores_hook` and `recalculate` from `normalization_hook.py` (with redundant aliases).
      - Re-export `ScoringPayloadWrapper` and `StateInputWrapper` from `models.py` (with redundant aliases).
      - Declare explicit `__all__ = ["apply_scoring_logic_hook", "enforce_passivity_penalty_hook", "matrix_scoring_hook", "normalize_matrix_scores_hook", "recalculate", "ScoringPayloadWrapper", "StateInputWrapper"]`.
    </action>
    <action>Delete legacy monolithic [DELETE] @[backend_v2/hooks/scoring.py].</action>
    <constraint invariant="explicit_reexport_mandate">All re-exported symbols must be declared via `__all__` and redundant import aliases per PEP 484 and `mypy --strict`.</constraint>
  </step>

  <step id="6" name="UNIVERSAL QUALITY GATE &amp; AST AUDIT">
    <action>Run backend audit loop with strict AST enforcement: `uv run python scripts/backend_audit_loop.py backend_v2/hooks/scoring/ backend_v2/tests/unit/hooks/test_scoring.py --test --ast-strict`.</action>
    <action>Run AST guardrail scanner directly to guarantee 0 violations: `uv run python scripts/_ast_guardrails.py backend_v2/hooks/scoring/ backend_v2/tests/unit/hooks/test_scoring.py --strict`.</action>
    <action>Verify all unit tests in `backend_v2/tests/unit/hooks/test_scoring.py` pass cleanly.</action>
    <constraint invariant="backend_quality_gate_delegation">Quality gate must pass 100% with zero linter, typing, AST, or test failures.</constraint>
  </step>

  <validation_gate>
    uv run python scripts/backend_audit_loop.py backend_v2/hooks/scoring/ backend_v2/tests/unit/hooks/test_scoring.py --test --ast-strict
  </validation_gate>
</execution_protocol>
```

---

## Verification Plan

### Automated Tests
1. **Unit Test Suite**:
   `uv run pytest backend_v2/tests/unit/hooks/test_scoring.py`
2. **Backend Quality Gate (Ruff + MyPy Strict + Pytest + AST Strict)**:
   `uv run python scripts/backend_audit_loop.py backend_v2/hooks/scoring/ backend_v2/tests/unit/hooks/test_scoring.py --test --ast-strict`
3. **AST Guardrail Verification**:
   `uv run python scripts/_ast_guardrails.py backend_v2/hooks/scoring/ backend_v2/tests/unit/hooks/test_scoring.py --strict`
4. **Markdown Boundary Verification**:
   `uv run python scripts/audit_markdown_boundaries.py --file docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/03_placeholder_phase3a_scoring_god_code_decomposition.md`
5. **Planner Fidelity Audit**:
   `uv run python scripts/audit_planner_output.py --epic docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md --plan-dir docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/`

### Test Scenarios & Partitions (ISTQB Compliance)
- **Positive Scenarios**:
  - `apply_scoring_logic_hook`: Evaluates valid `_evaluative_matrices` from multiple judges, calculates commensurate 0-100 average, applies security and post-hoc penalties.
  - `enforce_passivity_penalty_hook`: Detects minimum score in `LightweightMatrixOutput` and scales raw and normalized scores by multiplier.
  - `matrix_scoring_hook`: Maps blind atom evaluations against `MatrixPromptBlock` scales, runs AST evaluator on extractive sensors, quotes extraction, and executes `recalculate()`.
  - `normalize_matrix_scores_hook`: Transforms raw scores into normalized 0-100 values with bounds extracted from prompt block scales.
  - `recalculate`: Recalculates matrix scores based on atom states and output profile strictness and scoring engine.
- **Negative Scenarios**:
  - Missing or invalid `HookState`: Raises `AppException` with `ErrorCodes.VALIDATION_FAILED`.
  - Missing `workflow_repo` in `HookDependencies`: Raises `AppException` with `ErrorCodes.HOOK_EXECUTION_FAILED`.
  - Missing blueprint ID in registry: Raises `AppException` with `ErrorCodes.RESOURCE_NOT_FOUND`.
  - Corrupted prompt block scales (missing or non-numeric): Raises `AppException` with `ErrorCodes.CONFIGURATION_ERROR`.
  - Missing `results` in atom payload: Raises `AppException` with `ErrorCodes.VALIDATION_FAILED`.
