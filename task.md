# Task: Phase 3B: Full Hooks Pydantic V2 Migration & Hook Tests (PRODUCERS FIRST)

- [ ] **Step 0: Strategic Alignment Check & Pre-Flight Verification**
  - [ ] Verify codebase state from Sub-Phase 3A (`models.py` present for sunset, all 11 hook files and 4 scoring modules present)

- [ ] **Step 1: Pre-Implementation Technical Debt Cleanups & AST Guardrail Remediation**
  - [ ] Fix `QGR001` in `backend_v2/hooks/context_mapper.py` (`getattr` -> `isinstance(b, MatrixPromptBlock)`)
  - [ ] Fix `QGR002` in `backend_v2/hooks/integrity.py` (`.get("dynamic_inputs", {})` -> direct membership)
  - [ ] Fix `QGR002` in `backend_v2/hooks/linguistics.py` (`.get(...)` -> direct membership)
  - [ ] Fix `QGR001` in `backend_v2/hooks/llm.py` (`hasattr` -> direct settings lookup)
  - [ ] Fix `QGR002` in `backend_v2/hooks/validation.py` (`hits_by_level.get(level, 0.0)` -> direct lookup)
  - [ ] Fix `QGR007` in `backend_v2/hooks/dlq_guard.py` (add strict `model_config = ConfigDict(strict=True, extra="forbid")` to `DLQAtomSchema`)
  - [ ] Fix `QGR009` across all hook files (pass typed `ErrorCodes` enum member to `AppException`)
  - [ ] Update test fixtures across hook tests to pass `ExecutionMetadata(target_locale="fi")`
  - [ ] Verify 0 AST violations with `uv run python scripts/_ast_guardrails.py backend_v2/hooks/ --strict`

- [ ] **Step 2: Core Hook Registry & DTO Modernization**
  - [ ] Update `HookState` in `backend_v2/core/hook_registry.py` (`inputs: ExecutionInputsDTO`, `global_context_vars: GlobalContextVarsDTO`)
  - [ ] Update `HookResult` in `backend_v2/core/hook_registry.py` (`state_delta: HookDeltaDTO | None`)
  - [ ] Modernize `backend_v2/tests/unit/core/test_hook_registry.py`

- [ ] **Step 3: Validation, Ingress & Security Hooks Migration**
  - [ ] Migrate `backend_v2/hooks/validation.py`
  - [ ] Migrate `backend_v2/hooks/security.py`
  - [ ] Migrate `backend_v2/hooks/input_processing.py`
  - [ ] Migrate `backend_v2/hooks/hydration.py`
  - [ ] Migrate `backend_v2/hooks/interaction_hook.py`
  - [ ] Modernize unit tests for validation, security, input processing, hydration, and interaction hooks

- [ ] **Step 4: Extraction, Context & Integrity Hooks Migration**
  - [ ] Migrate `backend_v2/hooks/source_verification_hook.py`
  - [ ] Migrate `backend_v2/hooks/atom_flattening.py`
  - [ ] Migrate `backend_v2/hooks/context_mapper.py`
  - [ ] Migrate `backend_v2/hooks/integrity.py`
  - [ ] Migrate `backend_v2/hooks/linguistics.py`
  - [ ] Migrate `backend_v2/hooks/llm.py`
  - [ ] Migrate `backend_v2/hooks/archival.py`
  - [ ] Migrate `backend_v2/hooks/dlq_guard.py`
  - [ ] Migrate `backend_v2/hooks/metadata.py`
  - [ ] Migrate `backend_v2/hooks/metrics.py`
  - [ ] Migrate `backend_v2/hooks/references.py`
  - [ ] Modernize unit tests for all extraction, context, and integrity hooks

- [ ] **Step 5: Scoring Package Pydantic V2 Transition & Models Sunset**
  - [ ] Permanently delete `backend_v2/hooks/scoring/models.py`
  - [ ] Update `backend_v2/hooks/scoring/__init__.py` (remove temporary model re-exports)
  - [ ] Absorb `ScoringPayloadWrapper` and `_extract_payloads` into `backend_v2/hooks/scoring/falsifier_hook.py`
  - [ ] Migrate `backend_v2/hooks/scoring/falsifier_hook.py`, `passivity_hook.py`, `matrix_hook.py`, `normalization_hook.py` to `ExecutionInputsDTO` & `HookDeltaDTO`
  - [ ] Modernize `backend_v2/tests/unit/hooks/test_scoring.py` across all 4 ISTQB partitions

- [ ] **Step 6: Universal Quality Gate, AST Audit & Semantic Parity Verification**
  - [ ] Run `uv run python scripts/backend_audit_loop.py backend_v2/hooks/ backend_v2/core/hook_registry.py --test`
  - [ ] Run `uv run python scripts/_ast_guardrails.py --strict` (0 violations)
  - [ ] Run `uv run pytest backend_v2/tests/unit/hooks/`
  - [ ] Run `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`
