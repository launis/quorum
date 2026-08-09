# EPIC 135: Schema Convergence & Legacy Matrix Eradication

## 1. Goal Description & Background (Objective & Problem Statement)
**Objective**: Transition the entire Quorum execution engine to a single, unified DAG evaluation path, strictly enforcing the `schema_convergence_mandate`.
**Problem Statement**: The current architecture maintains a "Strangler Fig" migration that was never completed. It runs a dual-path pipeline where regular atom graph evaluations use the modern DAG path (`AtomResultDTO` in `backend_v2/models/v2_core.py`, strict `ExecutionStatus`), while legacy matrix evaluations rely on a Waterfall path (`AtomEvaluationItemDTO`, `LightweightExtractionAtom` in `backend_v2/models/dtos/atom_evaluation.py`). This parallel pipeline led to the "Override Inflation Bug," where fake `@property` methods (specifically `contextual_override` at `backend_v2/models/dtos/atom_evaluation.py` line 150, `structural_location` at line 154, `semantic_reasoning` at line 158) were duct-taped onto `LightweightExtractionAtom` to bypass centralized validation, causing FAILED atoms to score 100%. This violates the Single Source of Truth and creates untraceable shadow bugs.

**Epic Type**: Refactoring Epic. Zero behavioral change is mandated; the system MUST produce identical scoring outputs before and after convergence.

## 2. Architectural Impact & Compliance Matrix

### Deprecations & Sunset List (`What We Will REMOVE`)

> [!CAUTION]
> All deletions below are PERMANENT. Every reference in production code AND test fixtures MUST be atomically migrated within the same phase that removes the model.

The following is the exhaustive and complete list of models, enums, and code patterns scheduled for deletion:

1. **`AtomEvaluationItemDTO`** (`backend_v2/models/dtos/atom_evaluation.py` line 169): Obsolete self-contained scoring model that bypasses global rules. Contains a `calculate_rule_satisfied()` method that duplicates scoring logic belonging to the centralized `ScoringHook`.
2. **`LightweightExtractionAtom`** (`backend_v2/models/dtos/atom_evaluation.py` line 34): Duct-tape compatibility model generating fake `@property contextual_override`, `structural_location`, and `semantic_reasoning` returns.
3. **`MatrixEvaluationItemDTO`** (`backend_v2/models/dtos/atom_evaluation.py` line 162): Intermediate matrix parsing DTO that will be replaced by direct `AtomResultDTO` hydration.
4. **`ReducedAtomDTO`** (`backend_v2/models/dtos/atom_evaluation.py` line 414): Uses `LaxAtomEvaluationStatus`; must be migrated to `ExecutionStatus` or replaced with a projection from `AtomResultDTO`.
5. **`AtomEvaluationStatus` enum** (`backend_v2/models/enums.py` line 258): Legacy enum with values `PASS`/`FAIL`/`CONTESTED`/`DLQ`. All consumers must be migrated to `ExecutionStatus` (values: `PASSED`/`FAILED`/`N_A`/`SYSTEM_ERROR`/`BLOCKED`/`PENDING`/`RUNNING`/`QUEUED`). Value mapping: `PASS` → `PASSED`, `FAIL` → `FAILED`, `CONTESTED` → `PASSED` (with `contextual_override=True`), `DLQ` → `SYSTEM_ERROR`.
6. **`LaxAtomEvaluationStatus` type alias** (`backend_v2/models/enums.py` line 636): Annotated lax variant; deleted alongside the base enum.
7. **Dual-Path Routing in `scoring.py`**: The `is_dag_mode` flag (`backend_v2/hooks/scoring.py` line 644) and ALL branching at lines 821-870 (the `if is_dag_mode:` / `else:` / `try AtomEvaluationItemDTO` / `except: fallback to LightweightExtractionAtom` chain) will be eradicated.
8. **Duck-typing patterns in `scoring.py`**: Specifically `hasattr(ev_dto.status, "name")` at line 885, `getattr(ev_dto, "status", None)` at line 927, `getattr(ev_dto, "contextual_override", False)` at line 961, `getattr(ev_dto, "structural_location", None)` at line 962, `getattr(ev_dto, "semantic_reasoning", None)` at line 965, `getattr(ev_dto, "evaluation_reasoning", None)` at line 967.
9. **Finnish hardcoded strings in `scoring.py`**: `"Tuntematon sijainti"` at line 963 and `"Ei perustelua"` at line 969 must be replaced with English constants or Enum l10n keys.
10. **Legacy test files**: `backend_v2/tests/unit/models/dtos/test_lightweight_matrix.py`, `backend_v2/tests/unit/models/dtos/test_lightweight_matrix_schema.py`, `backend_v2/tests/unit/test_bug_lightweight_atom_truncation.py`, `backend_v2/tests/unit/models/dtos/test_atom_evaluation.py`.

### Affected Models Requiring Migration (NOT Deletion)
The following models reference the deprecated `AtomEvaluationStatus` or `LaxAtomEvaluationStatus` and MUST be surgically updated to use `ExecutionStatus` or `LaxExecutionStatus`:

1. **`ScorecardAtomDTO`** (`backend_v2/models/v2_core.py` line 902): Field `status: LaxAtomEvaluationStatus | None` → `status: LaxExecutionStatus | None`.
2. **`HumanOverrideRequest`** (`backend_v2/models/v2_core.py` line 882): Field `new_status: LaxAtomEvaluationStatus` → `new_status: LaxExecutionStatus` (description updated to specifically: PASSED, FAILED, SYSTEM_ERROR).
3. **`HumanOverrideDTO`** (`backend_v2/models/v2_core.py` line 892): Field `new_status: AtomEvaluationStatus` → `new_status: ExecutionStatus` (description updated to specifically: PASSED, FAILED, SYSTEM_ERROR).
4. **`anchor_validation_service.py`** (`backend_v2/services/orchestrator/anchor_validation_service.py`): Method `process_atom_evaluation` has `Any` type hints. It MUST be updated to accept `atom: AtomResultDTO`, `source_documents: list[Any]` must be typed, and the return type must be `-> AtomResultDTO`.
5. **`matrix_domain_parser.py`** (`backend_v2/services/matrix_domain_parser.py`): Currently uses `AtomEvaluationStatus.FAIL` at lines 369 and 406. Must be migrated to use `ExecutionStatus.FAILED` while **retaining** the `ScorecardAtomDTO` output (do NOT replace `ScorecardAtomDTO` with `AtomResultDTO` here, as it is a presentation DTO).
6. **`matrix_reducer.py`** (`backend_v2/services/orchestrator/matrix_reducer.py`): Uses `AtomEvaluationStatus.PASS` at line 111. Must be migrated to use `ExecutionStatus.PASSED`.

### Retained SSOT Invariants (`What We Will RETAIN`)
- **`AtomResultDTO`** (`backend_v2/models/v2_core.py` line 1074): This remains the absolute Single Source of Truth (SSOT) for all atomic evaluation results, regardless of whether they originate from matrix logic or standard DAG execution.
- **`ExecutionStatus`** (`backend_v2/models/enums.py` line 267): The strict Enum dictating lifecycle states.
- **Centralized `ScoringHook`** (`backend_v2/hooks/scoring.py`): All score math must flow through the central mathematical engine (`min(scales)` and `max(scales)` logic), preventing models from scoring themselves.
- **`ReasoningStepDTO`** (`backend_v2/models/dtos/atom_evaluation.py` line 21): Retained as shared micro-CoT reasoning step schema.
- **`LightweightMatrixDTO`** (`backend_v2/models/dtos/atom_evaluation.py` line 424): Retained for synthesis token compression. Its `reduced_atoms` field uses `ReducedAtomDTO` which MUST be migrated per the Deprecations list.

### Compliance & Modernity Gates
- **`schema_convergence_mandate`** (`01-python-backend.md` line 151): "One Concept = One Schema". Fallback chains and compatibility properties are absolutely forbidden.
- **`the_zero_compromise_pledge`** (`AGENTS.md`): No fallback dicts. If legacy matrix data cannot be parsed into `AtomResultDTO`, Fail-Fast immediately.
- **`the_no_legacy_mandate`** (`AGENTS.md`): Legacy support for old `AtomEvaluationItemDTO` payloads in the database is strictly prohibited.
- **`universal_fail_fast`** via Pydantic `ConfigDict(strict=True, extra='forbid')` must be maintained on all unified models.
- **`the_duct_tape_ban`** (`01-python-backend.md` line 11): The `try/except ValidationError: fallback to LightweightExtractionAtom` chain in `scoring.py` lines 844-857 is an explicit duct-tape violation.

### Producer-Consumer Integration Check
- **Producers**:
  - `LLMTaskExecutor` + `TopologicalEvaluator` (DAG path): Already outputs `AtomResultDTO`. No change needed.
  - `matrix_domain_parser.py` (Presentation path): Natively outputs `ScorecardAtomDTO`. It MUST continue to produce `ScorecardAtomDTO` with updated enums, and must never output `AtomResultDTO` per `schema_projection_blueprint_mandate`.
- **Consumers**:
  - `ScoringHook` (`backend_v2/hooks/scoring.py`): Must accept ONLY `AtomResultDTO` from the LLM outputs without branching logic.
  - `anchor_validation_service.py`: Must accept ONLY `AtomResultDTO`.
  - `blueprint.py` / SDUI layer: Consumes `ExecutionStepState.scorecard_atoms` (which remains `ScorecardAtomDTO`).

## 3. Phased Execution Plan (Implementation Strategy)

> [!IMPORTANT]
> **MANDATORY Phase Execution Order**: Each phase MUST be completed, tested, and committed BEFORE proceeding to the next. Test fixture updates are ATOMICALLY bound to each phase.

### Phase 1: Enum Convergence & Status Mapping
**Objective**: Establish the unified status vocabulary before touching any DTO models.

- Map `AtomEvaluationStatus` values to `ExecutionStatus` values:
  - `PASS` → `PASSED`
  - `FAIL` → `FAILED`
  - `CONTESTED` → `PASSED` (with `contextual_override=True` on the `AtomResultDTO`)
  - `DLQ` → `SYSTEM_ERROR`
- Update `ScorecardAtomDTO.status` field from `LaxAtomEvaluationStatus | None` to `LaxExecutionStatus | None`.
- **CONTESTED Visual State Preservation**: Because `CONTESTED` is being collapsed into `PASSED`, `ScorecardAtomDTO` MUST map this state explicitly (specifically by setting `visual_intent=VisualIntent.WARNING`) so the Flutter frontend `atom_matrix_table_widget.dart` does not lose the visual distinction.
- Update `HumanOverrideRequest.new_status` from `LaxAtomEvaluationStatus` to `LaxExecutionStatus` (and update the Pydantic field description to remove "e.g." and list specifically: PASSED, FAILED, SYSTEM_ERROR).
- Update `HumanOverrideDTO.new_status` from `AtomEvaluationStatus` to `ExecutionStatus` (and update the Pydantic field description to remove "e.g." and list specifically: PASSED, FAILED, SYSTEM_ERROR).
- Update `ReducedAtomDTO.status` from `LaxAtomEvaluationStatus` to `LaxExecutionStatus`.
- **FRONTEND PARITY MANDATE**: Update `AtomEvaluationStatus` to `ExecutionStatus` in `client_app_v2/lib/core/models/enums.dart` and `client_app_v2/lib/features/execution/models/matrix_scorecard_dto.dart`. Run Flutter build runner to regenerate models.
- **ATOMIC TEST BINDING**: Update ALL test fixtures in `backend_v2/tests/unit/models/test_v2_core.py` and `backend_v2/tests/unit/services/test_execution.py` that reference `AtomEvaluationStatus` to use `ExecutionStatus` in the same commit. Update Flutter test files (`matrix_blocks_snapshot_test.dart`, `matrix_scorecard_dto_test.dart`, `atom_matrix_table_widget_test.dart`) to use the new Enum.

### Phase 2: Producer Refactoring & Type strictness
**Objective**: Update the producers to use the new enums and types, while preserving the presentation flow layer.

- Update `backend_v2/services/orchestrator/anchor_validation_service.py` method `process_atom_evaluation` to remove ALL `Any` type hints (replace `atom: Any` with `atom: AtomResultDTO`, type `source_documents`, and set return type to `AtomResultDTO`).
- Eradicate ALL usage of `AtomEvaluationStatus` enum in `matrix_domain_parser.py` (lines 369, 406) and `matrix_reducer.py` (line 111), replacing with `ExecutionStatus`. **CRITICAL**: Do NOT replace `ScorecardAtomDTO` with `AtomResultDTO` in `matrix_domain_parser.py`. `ScorecardAtomDTO` is a presentation schema and must remain intact.
- **ATOMIC TEST BINDING**: Update `backend_v2/tests/integration/test_lazy_llm_simulation.py` to construct `AtomResultDTO` instead of `AtomEvaluationItemDTO`.

### Phase 3: Consumer Convergence (Scoring Hook Unification)
**Objective**: Remove all dual-path branching from `scoring.py`.

- Remove the `is_dag_mode` flag and the `if "results" in content_payload:` / `elif "evaluations" in content_payload:` branching at lines 644-660. The payload key MUST be strictly `"results"` (the DAG standard).
- Remove the entire `if is_dag_mode:` / `else:` / fallback chain at lines 821-870. ALL evaluation items MUST be parsed as `AtomResultDTO.model_validate(ev_dict)` with Fail-Fast.
- Eradicate ALL `getattr()` / `hasattr()` duck-typing patterns at lines 885, 927, 961-967.
- Replace Finnish hardcoded strings (`"Tuntematon sijainti"`, `"Ei perustelua"`) with English constants.
- Unify the quote processing path: remove the `is_dag_mode` conditional for `source_quote` vs `exact_quotes` at lines 913-932. All quotes MUST flow through the `AtomResultDTO.source_quote` field.
- Unify the override reasoning path: remove `semantic_reasoning` vs `evaluation_reasoning` conditional at lines 965-967. The unified field is `AtomResultDTO.evaluation_reasoning`.
- **ATOMIC TEST BINDING**: Update ALL test fixtures in `backend_v2/tests/unit/hooks/test_scoring.py` that set `metadata={"is_dag_mode": True}` (lines 1143, 1207, 1272) to remove the flag entirely.

### Phase 4: Deletion & Sunset
**Objective**: Physically remove all deprecated models and dead test files.

- Physically delete `LightweightExtractionAtom` (line 34), `MatrixEvaluationItemDTO` (line 162), and `AtomEvaluationItemDTO` (line 169) from `backend_v2/models/dtos/atom_evaluation.py`.
- Physically delete `AtomEvaluationStatus` enum from `backend_v2/models/enums.py` (line 258) and `LaxAtomEvaluationStatus` alias (line 636).
- Physically delete legacy test files:
  - `backend_v2/tests/unit/models/dtos/test_lightweight_matrix.py`
  - `backend_v2/tests/unit/models/dtos/test_lightweight_matrix_schema.py`
  - `backend_v2/tests/unit/test_bug_lightweight_atom_truncation.py`
  - `backend_v2/tests/unit/models/dtos/test_atom_evaluation.py`
- Run `grep_search` for `AtomEvaluationItemDTO`, `LightweightExtractionAtom`, and `AtomEvaluationStatus` across the entire `backend_v2/` directory to verify zero remaining references.
- **ATOMIC TEST BINDING**: Write new unit tests validating that `AtomResultDTO` correctly handles all edge cases previously covered by the deleted test files.

## 4. Definition of Done (DoD) & Verification Plan

### Definition of Done (DoD)
- The files `atom_evaluation.py` and `scoring.py` contain zero references to `LightweightExtractionAtom`, `AtomEvaluationItemDTO`, or `AtomEvaluationStatus`.
- The `backend_v2/models/enums.py` file contains zero references to `AtomEvaluationStatus` or `LaxAtomEvaluationStatus`.
- The codebase uses exactly one evaluation DTO (`AtomResultDTO`) and exactly one status enum (`ExecutionStatus`) for all cognitive parsing.
- All `getattr()`, `hasattr()`, and `isinstance(ev, dict)` duck-typing patterns in `scoring.py` are eradicated.
- All Finnish hardcoded strings in `scoring.py` are replaced with English constants.
- The backend compiles with zero MyPy errors and passes the `backend_audit_loop.py`.

### Automated Unit Tests
- **Synthesis Prompt Audit**: Run `grep_search` on LLM Prompts to verify if the string value of `ReducedAtomDTO.status` (`PASS/FAIL`) is used for reasoning logic, and update the prompts to match the new `PASSED/FAILED` string literals.
- Run: `uv run python scripts/backend_audit_loop.py backend_v2/hooks/scoring.py --test`
- Run: `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/atom_evaluation.py --test`
- Run: `uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py --test`
- Run: `uv run python scripts/backend_audit_loop.py backend_v2/models/enums.py --test`
- Run: `uv run python scripts/backend_audit_loop.py backend_v2/services/matrix_domain_parser.py --test`
- Run: `uv run pytest backend_v2/tests/unit/hooks/test_scoring.py`
- Run: `uv run pytest backend_v2/tests/unit/models/test_v2_core.py`

### Manual Verification Steps
- Perform a complete local DB wipe and re-seed (`uv run python backend_v2/seed/run_seed.py local`).
- Run a manual matrix evaluation workflow in the Flutter UI to verify that the frontend renders the unified output correctly.
- Verify that `ScorecardAtomDTO` serialization is compatible with existing Flutter `@JsonEnum()` mappings for `ExecutionStatus`.

### MANDATORY Final E2E REST API Verification Gate
- Set environment variable `RUN_LIVE_E2E=true`
- Run `uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
