# Epic 149 Tracker: Clean Pydantic V2 Full Codebase Transition & AST Guardrails Hardening

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

## Phase Execution Status

### Phase 1: Seed Vault Sanitization, Pre-Implementation Cleanups & SSOT Foundation
- **Plan:** @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/01_phase1_seed_vault_ssot_foundation_and_client_ingress.md]
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/01_phase1_seed_vault_ssot_foundation_and_client_ingress.md]`
  - [x] Step 1: Seed Vault Sanitization & Seeder Lifecycle Hardening
  - [x] Step 2: Foundational Backend Model & DTO Modernization
  - [x] Step 3: Flutter Client Execution Ingress & Freezed Parity
  - [x] Step 4: Atomic Test Suite Modernization & Quality Gates
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/01_phase1_seed_vault_ssot_foundation_and_client_ingress.md] @[docs/epic/EPIC_149_tracker.md]`

### Phase 2: Repository Reconstitution, Storage Blob Hydration & DAL Tests
- **Plan:** @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/02_phase2_repository_reconstitution_and_dal_tests.md]
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/02_phase2_repository_reconstitution_and_dal_tests.md] @[docs/epic/EPIC_149_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/02_phase2_repository_reconstitution_and_dal_tests.md] @[docs/epic/EPIC_149_tracker.md]`
  - [x] Step 1: Storage Blob Hydration Modernization
  - [x] Step 2: Repository Reconstitution to Typed Domain Models
  - [x] Step 3: Database Protocol Interfaces Modernization
  - [x] Step 4: Rule Synchronization & Atomic DAL Tests
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/02_phase2_repository_reconstitution_and_dal_tests.md] @[docs/epic/EPIC_149_tracker.md]`

### Phase 3: Hooks Refactoring & God Code Decomposition (Sub-Phases 3A & 3B)
- **Plan:** @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/03_placeholder_phase3a_scoring_god_code_decomposition.md]
- **Plan (Sub-Phase 3B):** @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/04_placeholder_phase3b_hooks_pydantic_v2_migration.md]
- [x] **[OK] Create Plan (Sub-Phase 3A):** `/tier0-create-plan @[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md#L224-L233] @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/03_placeholder_phase3a_scoring_god_code_decomposition.md] @[docs/epic/EPIC_149_tracker.md]`
- [x] **[OK] Red-Teaming (Sub-Phase 3A):** `/tier0-research-plan @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/03_placeholder_phase3a_scoring_god_code_decomposition.md] @[docs/epic/EPIC_149_tracker.md]`
- [x] **[OK] Execution (Sub-Phase 3A):** `/tier2-execute @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/03_placeholder_phase3a_scoring_god_code_decomposition.md] @[docs/epic/EPIC_149_tracker.md]`
  - [x] Step 0: Strategic Alignment Check
  - [x] Step 1: Pre-Implementation Technical Debt Cleanups in Test Suite
  - [x] Step 2: Create Temporary Models Module (`models.py`)
  - [x] Step 3: Decompose Falsifier & Passivity Hooks (`falsifier_hook.py`, `passivity_hook.py`)
  - [x] Step 4: Decompose Matrix & Normalization Hooks (`matrix_hook.py`, `normalization_hook.py`)
  - [x] Step 5: Strangler Fig Facade & Monolith Purge (`__init__.py`, delete `scoring.py`)
  - [x] Step 6: Universal Quality Gate & AST Audit (`backend_audit_loop.py`, `_ast_guardrails.py`)
- [ ] **[NOK] Audit (Sub-Phase 3A):** `/tier8-audit-plan @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/03_placeholder_phase3a_scoring_god_code_decomposition.md] @[docs/epic/EPIC_149_tracker.md]`
- [ ] **[NOK] Create Plan (Sub-Phase 3B):** `/tier0-create-plan @[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md#L234-L258] @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/04_placeholder_phase3b_hooks_pydantic_v2_migration.md] @[docs/epic/EPIC_149_tracker.md]`
- [ ] **[NOK] Execution (Sub-Phase 3B):** `/tier2-execute @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/04_placeholder_phase3b_hooks_pydantic_v2_migration.md] @[docs/epic/EPIC_149_tracker.md]`
  - [ ] Step 1: Full Hooks Pydantic V2 Migration
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/04_placeholder_phase3b_hooks_pydantic_v2_migration.md] @[docs/epic/EPIC_149_tracker.md]`

### Phase 4: Orchestration & Strategy Core Refactoring & Tests
- **Plan:** @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/05_placeholder_phase4_orchestration_and_strategy_core.md]
- [ ] **[NOK] Create Plan:** `/tier0-create-plan @[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md#L259-L286] @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/05_placeholder_phase4_orchestration_and_strategy_core.md] @[docs/epic/EPIC_149_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/05_placeholder_phase4_orchestration_and_strategy_core.md] @[docs/epic/EPIC_149_tracker.md]`
  - [ ] Step 1: Orchestrator & Strategies Refactoring
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/05_placeholder_phase4_orchestration_and_strategy_core.md] @[docs/epic/EPIC_149_tracker.md]`

### Phase 5: Service Layer, Utility Services & Service Tests
- **Plan:** @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/06_placeholder_phase5_service_layer_and_identity.md]
- [ ] **[NOK] Create Plan:** `/tier0-create-plan @[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md#L287-L306] @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/06_placeholder_phase5_service_layer_and_identity.md] @[docs/epic/EPIC_149_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/06_placeholder_phase5_service_layer_and_identity.md] @[docs/epic/EPIC_149_tracker.md]`
  - [ ] Step 1: Service Layer Duck-Typing Elimination
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/06_placeholder_phase5_service_layer_and_identity.md] @[docs/epic/EPIC_149_tracker.md]`

### Phase 6: Background Workers, Typed Cache Boundary & Storage
- **Plan:** @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/07_placeholder_phase6_workers_typed_cache_and_storage.md]
- [ ] **[NOK] Create Plan:** `/tier0-create-plan @[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md#L307-L318] @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/07_placeholder_phase6_workers_typed_cache_and_storage.md] @[docs/epic/EPIC_149_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/07_placeholder_phase6_workers_typed_cache_and_storage.md] @[docs/epic/EPIC_149_tracker.md]`
  - [ ] Step 1: Typed Cache Service & Worker Hydration
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/07_placeholder_phase6_workers_typed_cache_and_storage.md] @[docs/epic/EPIC_149_tracker.md]`

### Phase 7: AST Guardrail Hardening (Mathematical Drift Prevention)
- **Plan:** @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/08_placeholder_phase7_ast_guardrails_hardening.md]
- [ ] **[NOK] Create Plan:** `/tier0-create-plan @[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md#L319-L329] @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/08_placeholder_phase7_ast_guardrails_hardening.md] @[docs/epic/EPIC_149_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/08_placeholder_phase7_ast_guardrails_hardening.md] @[docs/epic/EPIC_149_tracker.md]`
  - [ ] Step 1: AST Guardrail FATAL Locking & Test Verification
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/08_placeholder_phase7_ast_guardrails_hardening.md] @[docs/epic/EPIC_149_tracker.md]`

---

### Integration Checkpoint: Full-Stack Validation
- [x] Seed Vault Sanitization Verification: `uv run python scripts/audit_database_atoms.py --strict`
- [x] Clean-slate Database Seeder Lifecycle: `uv run python backend_v2/seed/run_seed.py local`
- [x] Backend Quality Audit & Test Suite: `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_main.py backend_v2/tests/unit/seed/test_run_seed.py backend_v2/tests/unit/models/test_execution_core.py backend_v2/tests/unit/core/test_hook_registry.py backend_v2/tests/unit/core/test_registry.py backend_v2/tests/unit/models/dtos/test_hook_state.py --test`
- [ ] AST Guardrails FATAL Check: `uv run python backend_v2/tests/unit/scripts/test_ast_guardrails.py`
- [x] Flutter Client Build & Semantic Parity: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/ --build`
- [x] SDUI Cross-Domain Semantic Parity: `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`

---

### Post-Implementation Gates

#### Backend Hardening Gate
- [x] @[backend_v2/seed/seed_data.json] — Verified explicit `target_locale` across all templates.
- [x] @[backend_v2/seed/run_seed.py] — Dynamic path resolution via `prod_db_path`.
- [x] @[backend_v2/main.py] — Lifespan startup pre-flight schema check.
- [x] @[backend_v2/models/v2_core.py] — Strict mandatory `target_locale` without defaults.
- [x] @[backend_v2/models/execution_core.py] — Strict `ExecutionMetadata` SSOT.
- [ ] @[backend_v2/core/hook_registry.py] — Strictly typed `HookState` and `HookResult`.
- [x] @[backend_v2/models/dtos/hook_state.py] — Strict DTO schemas.
- [x] @[backend_v2/database/repositories/execution.py] — Typed model returns & Rust-level blob hydration.
- [x] [NEW] @[backend_v2/hooks/scoring/__init__.py] — Decomposed modular scoring package facade.
- [x] [NEW] @[backend_v2/hooks/scoring/models.py] — Temporary DTOs for scoring decomposition (Mandatory sunset in 3B).
- [x] [NEW] @[backend_v2/hooks/scoring/falsifier_hook.py] — Falsifier scoring logic hook.
- [x] [NEW] @[backend_v2/hooks/scoring/passivity_hook.py] — Passivity penalty enforcement hook.
- [x] [NEW] @[backend_v2/hooks/scoring/matrix_hook.py] — Matrix scoring hook with AST Evaluator.
- [x] [NEW] @[backend_v2/hooks/scoring/normalization_hook.py] — Score normalization and recalculation hook.
- [x] @[backend_v2/tests/unit/hooks/test_scoring.py] — Modernized scoring hook unit test suite.
- [ ] [NEW] @[backend_v2/services/cache/typed_cache.py] — Generic `TypedCacheService` with zombie eviction.
- [ ] @[scripts/_ast_guardrails.py] — Locked `QGR001`, `QGR002`, `QGR012` at FATAL severity.

#### Frontend Hardening Gate
- [x] [NEW] @[client_app_v2/lib/features/execution/models/execution_create_request_dto.dart] — Freezed request model with `disallowUnrecognizedKeys: true`.
- [x] @[client_app_v2/lib/features/execution/models/execution_record.dart] — Full 1:1 schema parity with backend `ExecutionRecord`.
- [x] @[client_app_v2/lib/core/api/execution_client.dart] — Strict `startExecution` API ingress.
- [x] @[client_app_v2/lib/features/execution/controllers/execution_controller.dart] — Removed `allowedKeys` filter and silent error swallowing.
- [x] @[client_app_v2/lib/features/execution/views/new_execution_view.dart] — Unified execution client calls.
- [x] @[client_app_v2/lib/features/execution/views/dynamic_start_screen.dart] — Active `target_locale` propagation.

---

### Documentation & Knowledge Item Update
- [ ] Knowledge Item Updated: @[ki_ast_guardrail_engine.md] (Documenting `QGR012` and FATAL enforcement).
- [x] Architecture Rule Updated: @[.agents/rules/01-python-backend.md#L176-L178] (`service_layer_hydration_firewall` updated to align with `repository_reconstitution_mandate`).

---

### Final Epic Audit
- [ ] `uv run python scripts/audit_markdown_boundaries.py --file docs/epic/EPIC_149_tracker.md`
- [ ] `uv run python scripts/audit_tracker_output.py --tracker docs/epic/EPIC_149_tracker.md --plan-dir docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition`
- [ ] Full backend test suite passes: `uv run python scripts/backend_audit_loop.py backend_v2/ --test`
- [ ] Full flutter test suite passes: `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`

---

## Instructions for the Execution Agent
1. Treat this Tracker document as the absolute SSOT for Phase status and execution sequencing.
2. Follow the strict Producer-Before-Consumer dependency ordering: Phase 1 -> Phase 2 -> Phase 3A -> Phase 3B -> Phase 4 -> Phase 5 -> Phase 6 -> Phase 7.
3. Enforce the Zero-Compromise Invariants: `the_no_legacy_mandate`, `the_duct_tape_ban`, `zero_service_layer_fallbacks`, and `feature_sovereignty_mandate`.
4. Execute quality gates at every phase completion boundary before marking checkboxes `[x]`.

---

## Requirements Traceability Matrix

| Requirement / Architectural Directive | Target Phase & Step | Status |
|---|---|---|
| Seed Vault sanitization & explicit `target_locale` backfill | Phase 1, Step 1 | COMPLETED |
| Dynamic seeder path via `get_settings().prod_db_path` | Phase 1, Step 1 | COMPLETED |
| Permanent purge of vestigial 0-byte database files | Phase 1, Step 1 | COMPLETED |
| FastAPI lifespan pre-flight database schema validation | Phase 1, Step 1 | COMPLETED |
| Remove `target_locale="en"` default factories from models | Phase 1, Step 2 | COMPLETED |
| Validate `ExecutionMetadata` covers all worker telemetry | Phase 1, Step 2 | COMPLETED |
| Replace loose dicts in `HookState` with typed DTOs | Phase 1, Step 2 | COMPLETED |
| Audit `TaskDefinition.metadata` and registry dict fields | Phase 1, Step 2 | COMPLETED |
| Create `ExecutionCreateRequestDto` with `disallowUnrecognizedKeys` | Phase 1, Step 3 | COMPLETED |
| Update `ExecutionRecord` Freezed model to 1:1 schema parity | Phase 1, Step 3 | COMPLETED |
| Refactor `ExecutionClient.startExecution` and purge legacy params | Phase 1, Step 3 | COMPLETED |
| Delete `allowedKeys` filter & silent stream swallowing | Phase 1, Step 3 | COMPLETED |
| Unify execution triggers in `NewExecutionController` | Phase 1, Step 3 | COMPLETED |
| Pass active `target_locale` in `dynamic_start_screen.dart` | Phase 1, Step 3 | COMPLETED |
| Modernize Phase 1 unit and integration tests | Phase 1, Step 4 | COMPLETED |
| Modernize repository blob hydration with `model_validate_json` | Phase 2, Step 1 | COMPLETED |
| Reconstitute all 15 repositories to return typed Domain models | Phase 2, Step 2 | COMPLETED |
| Modernize `database/interfaces.py` protocol definitions | Phase 2, Step 3 | COMPLETED |
| Update `service_layer_hydration_firewall` rule in `01-python-backend.md` | Phase 2, Step 4 | COMPLETED |
| Modernize repository unit tests in `test_repositories_v2.py` & `database/` | Phase 2, Step 4 | COMPLETED |
| Pre-implementation tech debt cleanups & scoring test expansion | Phase 3, Step 1 | COMPLETED |
| Temporary DTO models module models.py (<120 LOC) | Phase 3, Step 2 | COMPLETED |
| Decompose falsifier & passivity scoring hooks | Phase 3, Step 3 | COMPLETED |
| Decompose matrix & normalization scoring hooks | Phase 3, Step 4 | COMPLETED |
| Strangler Fig facade in __init__.py & monolith deletion | Phase 3, Step 5 | COMPLETED |
| Universal Quality Gate & AST guardrails verification | Phase 3, Step 6 | COMPLETED |
| Eliminate duck-typing & reflection from orchestrator and strategies | Phase 4, Step 1 | PENDING |
| Eliminate `getattr(initiator, "organization_id")` from services | Phase 5, Step 1 | PENDING |
| Build `TypedCacheService` with zombie cache eviction | Phase 6, Step 1 | PENDING |
| Lock `QGR001`, `QGR002`, `QGR012` AST rules at FATAL severity | Phase 7, Step 1 | PENDING |

---

# Session Handover Context

## Achieved
- **Phase 1 Backend SSOT Foundation & Lifespan Gates (Commit `e1f3937c`)**:
  - Permanently deleted vestigial 0-byte database files `data/app.db` and `data/app.sqlite`.
  - Sanitized Seed Vault via `scripts/sanitize_seed_vault.py --test` and verified with `scripts/audit_database_atoms.py --strict` (0 errors across 152 atoms, 13 matrices, 19 steps).
  - Modernized `backend_v2/seed/run_seed.py` with `get_settings()` SSOT paths (`prod_db_path`, `seed_data_path`, `base_dir`, `data_dir`) and clean table/directory drop.
  - Added FastAPI Lifespan pre-flight schema validation `_validate_database_preflight` in `backend_v2/main.py`.
  - Created `backend_v2/models/dtos/hook_state.py` [NEW] with strict `ExecutionInputsDTO`, `GlobalContextVarsDTO`, and `HookDeltaDTO` (`frozen=True, extra="forbid", strict=True`).
  - Enforced mandatory `target_locale: str = Field(...)` SSOT across `ExecutionCoreFields` and `ExecutionRecord`.
  - Backend unit test suites passing 100% with >90% coverage: `test_run_seed.py` (24 passed, 95% cov), `test_main.py` (16 passed, 93% cov), `test_execution_core.py` (100% cov), `test_hook_state.py` (100% cov).
- **Phase 1 Frontend Client Ingress & Freezed Parity Remediation (Commit `e33bce98`)**:
  - Created `client_app_v2/lib/features/execution/models/execution_create_request_dto.dart` [NEW] with `@JsonSerializable(disallowUnrecognizedKeys: true)`.
  - Updated `ExecutionRecord` to full 1:1 schema parity matching backend `ExecutionRecord`, adding 18 missing telemetry, synthesis, and storage fields.
  - Refactored `ExecutionClient.startExecution` to accept typed `ExecutionCreateRequestDto` and eliminated legacy parameters (`strictnessLevel`, `scoringStrategy`).
  - Permanently deleted `const allowedKeys = { ... }` duct-tape filter from `executionList` in `execution_controller.dart`.
  - Replaced silent SSE stream error catching with structured logging and `AsyncValue.error` state propagation.
  - Unified execution ingress in `NewExecutionController` to call `executionClientProvider.startExecution` with `ExecutionCreateRequestDto`.
  - Propagated active `target_locale` in `dynamic_start_screen.dart` via `Localizations.localeOf(context).languageCode`.
  - All 66 Flutter execution feature tests passing 100% (`flutter test test/features/execution/`).
  - SDUI Cross-Domain Semantic Parity verified 100% (`test_sdui_semantic_parity.py`).
- **Phase 1 System 2 Red-Team Audit (`/tier8-audit-plan`) Completed**:
  - Validated 100% adherence to all Phase 1 DoD items, architectural invariants, and quality gates.
  - Generated audit report: `red_team_audit_01_phase1_seed_vault_ssot_foundation_and_client_ingress.md`.
  - Marked Phase 1 audit status as `[x] [OK]`.
- **Phase 2 System 2 Research & Red-Teaming (`/tier0-research-plan`) Completed**:
  - Executed Five-Axis System 2 Deconstruction of Phase 2 plan (`02_phase2_repository_reconstitution_and_dal_tests.md`).
  - Injected `Phase 1: Pre-Implementation Cleanups` and synthesized 5-Column Architectural Directive Table across all 15 repositories and protocols.
  - Marked Phase 2 Red-Teaming status as `[x] [OK]`.
- **Phase 2 Execution (`/tier2-execute`) Completed (Commit `60478d2e`, Audit `a0819acb`)**:
  - Reconstituted all 15 Data Access Layer repositories under `backend_v2/database/repositories/` to return strictly validated, typed Pydantic Domain models instead of raw `dict[str, Any]` (`ExecutionRecord`, `Workflow`, `Step`, `SystemConfig*`, `BannedPhrase`, `PromptTemplateDTO`, `Concept`, `Organization`, `User`, `AuditLogEntry`, `UsageRecord`, `PromptBlock`, `Role`, `OutputProfile`, `Matrix`, `ExtractionProtocol`, `ExecutionPersona`, `Agent`).
  - Refactored storage blob hydration in `backend_v2/database/repositories/execution.py` to use Rust-level `TypeAdapter(list[StepOutputDTO]).validate_json(blob_data)` and `FrozenContext.model_validate_json(blob_data)`.
  - Modernized all 15 protocol interfaces in `backend_v2/database/interfaces.py` to declare strictly typed Domain model return types.
  - Updated architectural rule `service_layer_hydration_firewall` in `.agents/rules/01-python-backend.md#L176-L178` to align with `repository_reconstitution_mandate`.
  - Modernized/expanded unit test coverage across all repositories: 103 unit tests passing across `backend_v2/tests/unit/database/`, achieving >90% coverage on every single repository.
  - Passed Universal Quality Gate: `uv run python scripts/backend_audit_loop.py backend_v2/database/repositories/ --test` and `uv run python scripts/backend_audit_loop.py backend_v2/database/interfaces.py backend_v2/database/repository.py --test`.
  - Marked Phase 2 execution status as `[x] [OK]`.
- **Phase 2 System 2 Red-Team Audit (`/tier8-audit-plan`) Completed**:
  - Validated 100% adherence to all Phase 2 DoD items, architectural invariants, test contracts, and quality gates.
  - Generated audit report: `red_team_audit_02_phase2_repository_reconstitution_and_dal_tests.md`.
  - Marked Phase 2 audit status as `[x] [OK]`.
- **Phase 3A Plan Creation & System 2 Red-Teaming (`/tier0-research-plan`) Completed**:
  - Authored comprehensive architectural implementation plan for Phase 3A: `scoring.py` God Code Decomposition (Strangler Fig Proxy Pattern).
  - Executed Five-Axis System 2 Adversarial Deconstruction across Scope, Duct-Tape, Best Practice, Complexity Slayer, and Proof Anchor axes.
  - Pre-flight AST analysis of `backend_v2/hooks/scoring.py` (1,348 LOC, 64.3 KB) extracted exact function/class AST nodes and itemized 14 AST guardrail violations (`QGR001` reflection, `QGR002` `.get()`).
  - Pre-flight test inspection of `backend_v2/tests/unit/hooks/test_scoring.py` identified 18 MyPy/Pydantic V2 type errors due to `HookState.metadata` requiring `ExecutionMetadata(target_locale="fi")`, and uncovered missing test coverage for `apply_scoring_logic_hook` and `enforce_passivity_penalty_hook`.
  - Injected 5-Column Architectural Directives Table, exact AST line bounds (#Lnn-mm), and test expansion contracts into the plan.
  - Formulated strict 4-module decomposition schema:
    - `backend_v2/hooks/scoring/falsifier_hook.py` (<250 LOC): `apply_scoring_logic_hook` + security & falsifier penalty calculation.
    - `backend_v2/hooks/scoring/passivity_hook.py` (<200 LOC): `enforce_passivity_penalty_hook` + low-quality score scaling.
    - `backend_v2/hooks/scoring/matrix_hook.py` (<480 LOC): `matrix_scoring_hook` + quote evidence validation + AST Evaluator.
    - `backend_v2/hooks/scoring/normalization_hook.py` (<400 LOC): `normalize_matrix_scores_hook` + `recalculate` hybrid calculation engine.
    - `backend_v2/hooks/scoring/models.py` (<120 LOC): Temporary DTOs (`ScoringPayloadWrapper`, `StateInputWrapper`, `_extract_payloads`) with mandatory sunset in Sub-Phase 3B.
    - `backend_v2/hooks/scoring/__init__.py`: PEP 484 Strangler Fig facade with explicit `__all__` and redundant re-export aliases for all 5 hook functions and 2 DTOs.
  - Validated with `scripts/audit_markdown_boundaries.py` (0 errors) and `scripts/audit_planner_output.py` (100% fidelity).
  - Marked Phase 3A Red-Teaming status as `[x] [OK]`.
- **Phase 3A God Code Decomposition (`/tier2-execute`) Completed**:
  - Decomposed monolithic 1,348 LOC (64.3 KB) `backend_v2/hooks/scoring.py` into modular package `backend_v2/hooks/scoring/`:
    - `models.py` (95 LOC, limit <120): Pure extraction DTOs (`ScoringPayloadWrapper`, `StateInputWrapper`, `_extract_payloads`).
    - `falsifier_hook.py` (235 LOC, limit <250): `apply_scoring_logic_hook` + security & falsifier penalty calculation without reflection.
    - `passivity_hook.py` (158 LOC, limit <200): `enforce_passivity_penalty_hook` + low-quality score scaling.
    - `matrix_hook.py` (300 LOC, limit <480): `matrix_scoring_hook` + quote evidence validation + AST Evaluator integration with `isinstance()` narrowing.
    - `normalization_hook.py` (355 LOC, limit <400): `normalize_matrix_scores_hook` + `recalculate` hybrid calculation engine without hardcoded scales.
    - `__init__.py` (35 LOC, limit <40): PEP 484 Strangler Fig facade with explicit `__all__` and redundant re-export aliases for all 5 hook functions and 2 temporary DTOs.
  - Eliminated all 14 AST guardrail violations (`QGR001` reflection, `QGR002` `.get()`) in scoring domain code.
  - Permanently deleted monolithic `backend_v2/hooks/scoring.py`.
  - Modernized `backend_v2/tests/unit/hooks/test_scoring.py`:
    - Fixed all `ExecutionMetadata(target_locale="fi")` Pydantic V2 validations.
    - Replaced raw string `"matrix"` with `PromptBlockCategory.MATRIX.value`.
    - Eliminated `.get()` calls in test assertion helpers.
    - Expanded unit test suites for `apply_scoring_logic_hook` and `enforce_passivity_penalty_hook` across positive, negative, and boundary partitions (all 26 tests passing).
  - Enhanced `scripts/backend_audit_loop.py` to support package test discovery for modularized packages (`__init__.py` and directory targets).
  - Passed Universal Quality Gate: `uv run python scripts/backend_audit_loop.py backend_v2/hooks/scoring/ backend_v2/tests/unit/hooks/test_scoring.py --ast-strict` and `scripts/_ast_guardrails.py --strict` with 0 errors.
  - Validated structural contracts: `audit_markdown_boundaries.py` and `audit_tracker_output.py` passed cleanly (0 errors).
  - Marked Phase 3A Execution status as `[x] [OK]`.

## Learned
- Repository reconstitution requires updating `backend_v2/database/interfaces.py` in lockstep to avoid Protocol divergence and MyPy strict mode violations.
- `backend_audit_loop.py` automatically maps target files (specifically `backend_v2/database/repositories/execution.py`) to `backend_v2/tests/unit/database/repositories/test_execution.py`. Establishing 1:1 test files under `backend_v2/tests/unit/database/repositories/` guarantees automated compliance and deterministic coverage.
- Elimination of `.get(key, default)` in domain code is required by AST Guardrail `QGR002`; all dictionary indexing on internal drivers must use direct keys with Fail-Fast exceptions or Pydantic validation.
- Monolithic `scoring.py` (1,348 LOC) requires decomposition into 4 focused submodules (`falsifier_hook.py`, `passivity_hook.py`, `matrix_hook.py`, `normalization_hook.py`) with a PEP 484 Strangler Fig facade in `__init__.py` to eliminate AST violations while maintaining 100% backward compatibility with service callers.
- In unit test fixtures, `HookState` requires `metadata=ExecutionMetadata(target_locale="fi")` rather than raw empty dict `{}` to satisfy strict Pydantic V2 validation and MyPy `--strict` checking.
- Pre-flight test analysis revealed that `apply_scoring_logic_hook` and `enforce_passivity_penalty_hook` had zero dedicated unit test coverage in `test_scoring.py`; test expansion with positive/negative boundary partitions is required in Phase 1 before monolith deletion.
- In `backend_audit_loop.py`, testing decomposed packages requires discovering candidates from parent directory name (`parts[-2]`) when given `__init__.py`, and testing directory paths should check for matching test files under `backend_v2/tests/unit/hooks/test_<module>.py`.

## Remaining
- **Phase 3: Hooks Refactoring & God Code Decomposition**:
  - **Sub-Phase 3A Audit**: System 2 Red-Team Audit of Phase 3A execution (`/tier8-audit-plan`).
  - **Sub-Phase 3B**: Full Hooks Pydantic V2 Migration across all 11 hook files (`interaction_hook.py`, `validation.py`, `source_verification_hook.py`, `atom_flattening.py`, `input_processing.py`, `integrity.py`, `linguistics.py`, `llm.py`, `context_mapper.py`, `archival.py`, `security.py`), eliminating duck-typing, transitioning `HookState` to typed DTOs, and sunsetting temporary `models.py`.
- **Phase 4**: Orchestration & Strategy Core Refactoring.
- **Phase 5**: Service Layer & Identity.
- **Phase 6**: Background Workers, Typed Cache Boundary & Storage.
- **Phase 7**: AST Guardrails Hardening.

## Resume Command
```powershell
/tier8-audit-plan @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/03_placeholder_phase3a_scoring_god_code_decomposition.md] @[docs/epic/EPIC_149_tracker.md]
```
