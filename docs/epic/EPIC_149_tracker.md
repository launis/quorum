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
- [x] **[OK] Audit (Sub-Phase 3A):** `/tier8-audit-plan @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/03_placeholder_phase3a_scoring_god_code_decomposition.md] @[docs/epic/EPIC_149_tracker.md]`
- [x] **[OK] Create Plan (Sub-Phase 3B):** `/tier0-create-plan @[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md#L234-L258] @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/04_placeholder_phase3b_hooks_pydantic_v2_migration.md] @[docs/epic/EPIC_149_tracker.md]`
- [x] **[OK] Red-Teaming (Sub-Phase 3B):** `/tier0-research-plan @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/04_placeholder_phase3b_hooks_pydantic_v2_migration.md] @[docs/epic/EPIC_149_tracker.md]`
- [x] **[OK] Execution (Sub-Phase 3B):** `/tier2-execute @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/04_placeholder_phase3b_hooks_pydantic_v2_migration.md] @[docs/epic/EPIC_149_tracker.md]`
  - [x] Step 0: Strategic Alignment Check & Pre-Flight Verification
  - [x] Step 1: Pre-Implementation Technical Debt Cleanups & AST Guardrail Remediation
  - [x] Step 2: Core Hook Registry & DTO Modernization
  - [x] Step 3: Validation, Ingress & Security Hooks Migration
  - [x] Step 4: Extraction, Context & Integrity Hooks Migration
  - [x] Step 5: Scoring Package Pydantic V2 Transition & Models Sunset
  - [x] Step 6: Universal Quality Gate, AST Audit & Semantic Parity Verification
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/04_placeholder_phase3b_hooks_pydantic_v2_migration.md] @[docs/epic/EPIC_149_tracker.md]`

### Phase 4: Orchestration & Strategy Core Refactoring & Tests
- **Plan:** @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/05_placeholder_phase4_orchestration_and_strategy_core.md]
- [x] **[OK] Create Plan:** `/tier0-create-plan @[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md#L259-L286] @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/05_placeholder_phase4_orchestration_and_strategy_core.md] @[docs/epic/EPIC_149_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/05_placeholder_phase4_orchestration_and_strategy_core.md] @[docs/epic/EPIC_149_tracker.md]`
  - [ ] Step 0: Strategic Alignment Check & Pre-Flight Verification
  - [ ] Step 1: Strategy Base & Hook Integration Modernization (`base.py`)
  - [ ] Step 2: LLM Execution & Context Builder Refactoring (`context_builder.py`, `llm.py`, `execution_time_resolver.py`)
  - [ ] Step 3: Prompt Compiler, Adapter & Context Router Refactoring (`prompt_compiler.py`, `prompt_compiler_adapter.py`, `context_router.py`)
  - [ ] Step 4: Synthesis & Evaluation Engines Refactoring (`tda_engine.py`, `synthesis_engine.py`, `matrix_explanation_service.py`, `synthesis_payload_compressor.py`, `synthesis_distiller.py`, `matrix_reducer.py`, `anchor_validation_service.py`)
  - [ ] Step 5: DAG Executor & Reasoning Orchestration Refactoring (`dag_executor.py`, `rag_preflight_service.py`, `localization_compiler.py`, `extraction_schema_factory.py`, `atomizer.py`)
  - [ ] Step 6: Atomic Test Suite Modernization & Quality Gates (`backend_audit_loop.py`, `_ast_guardrails.py`, `test_sdui_semantic_parity.py`)
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
- [x] @[backend_v2/core/hook_registry.py] — Strictly typed `HookState` and `HookResult`.
- [x] @[backend_v2/models/dtos/hook_state.py] — Strict DTO schemas.
- [x] @[backend_v2/database/repositories/execution.py] — Typed model returns & Rust-level blob hydration.
- [x] [NEW] @[backend_v2/hooks/scoring/__init__.py] — Decomposed modular scoring package facade.
- [x] [NEW] @[backend_v2/hooks/scoring/models.py] — Temporary DTOs for scoring decomposition (Mandatory sunset in 3B).
- [x] [NEW] @[backend_v2/hooks/scoring/falsifier_hook.py] — Falsifier scoring logic hook.
- [x] [NEW] @[backend_v2/hooks/scoring/passivity_hook.py] — Passivity penalty enforcement hook.
- [x] [NEW] @[backend_v2/hooks/scoring/matrix_hook.py] — Matrix scoring hook with AST Evaluator.
- [x] [NEW] @[backend_v2/hooks/scoring/normalization_hook.py] — Score normalization and recalculation hook.
- [x] @[backend_v2/tests/unit/hooks/test_scoring.py] — Modernized scoring hook unit test suite.
- [x] @[backend_v2/hooks/validation.py] — Strict validation hooks.
- [x] @[backend_v2/hooks/source_verification_hook.py] — Strict source verification hook.
- [x] @[backend_v2/hooks/atom_flattening.py] — Strict matrix atom flattening hook.
- [x] @[backend_v2/hooks/input_processing.py] — Strict input processing hook.
- [x] @[backend_v2/hooks/integrity.py] — Strict integrity and citation hooks.
- [x] @[backend_v2/hooks/linguistics.py] — Strict linguistics pattern detection hook.
- [x] @[backend_v2/hooks/llm.py] — Strict LLM context configuration hook.
- [x] @[backend_v2/hooks/context_mapper.py] — Strict context mapper service.
- [x] @[backend_v2/hooks/archival.py] — Strict archival precedent hook.
- [x] @[backend_v2/hooks/security.py] — Strict text sanitization hook.
- [x] @[backend_v2/hooks/hydration.py] — Strict input hydration hook.
- [x] @[backend_v2/hooks/dlq_guard.py] — Strict DLQ guard hook.
- [x] @[backend_v2/hooks/metadata.py] — Strict metadata injection hook.
- [x] @[backend_v2/hooks/metrics.py] — Strict metrics calculation hook.
- [x] @[backend_v2/hooks/references.py] — Strict reference generation hook.
- [x] @[backend_v2/hooks/interaction_hook.py] — Strict interaction role hook.
- [ ] @[backend_v2/services/orchestrator/dag_executor.py] — Direct typed dot-notation & _update_lock state transitions.
- [ ] @[backend_v2/services/orchestrator/strategies/llm.py] — Typed StrategyContext & blackboard access.
- [ ] @[backend_v2/services/orchestrator/strategies/base.py] — Typed HookDeltaDTO integration without .pop().
- [ ] @[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py] — Typed StepOutputDTO access without reflection.
- [ ] @[backend_v2/services/orchestrator/strategies/llm_execution/execution_time_resolver.py] — Typed WorkflowInputs timestamp resolution.
- [ ] @[backend_v2/services/orchestrator/prompt_compiler.py] — Typed I18nText extraction.
- [ ] @[backend_v2/services/orchestrator/prompt_compiler_adapter.py] — Explicit method delegation without QGR001 reflection.
- [ ] @[backend_v2/services/orchestrator/context_router.py] — Strict ConfigDict and typed step_id access.
- [ ] @[backend_v2/services/orchestrator/synthesis_payload_compressor.py] — Polymorphic DistilledEvaluation sanitization.
- [ ] @[backend_v2/services/orchestrator/synthesis_distiller.py] — Fail-Fast alias dictionary indexing.
- [ ] @[backend_v2/services/orchestrator/matrix_explanation_service.py] — Strict AtomResultDTO traversal.
- [ ] @[backend_v2/services/orchestrator/rag_preflight_service.py] — Strict ExecutionInputsDTO input extraction.
- [ ] @[backend_v2/services/orchestrator/localization_compiler.py] — Typed I18nText polymorphism.
- [ ] @[backend_v2/services/orchestrator/extraction_schema_factory.py] — Pydantic V2 native field validation.
- [ ] @[backend_v2/services/orchestrator/atomizer.py] — Immutable model_copy updates.
- [ ] @[backend_v2/services/orchestrator/anchor_validation_service.py] — Immutable model_copy updates.
- [ ] @[backend_v2/services/orchestrator/matrix_reducer.py] — Direct ReducedAtomDTO and QuoteEvidenceDTO iteration.
- [ ] @[backend_v2/services/orchestrator/engines/tda_engine.py] — Typed ErrorCodes and blackboard access.
- [ ] @[backend_v2/services/orchestrator/engines/synthesis_engine.py] — Typed ErrorCodes and blackboard model validation.
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
| Full hooks Pydantic V2 migration & models.py permanent sunset | Phase 3, Step 6 | COMPLETED |
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
- **Phase 3A God Code Decomposition (`/tier2-execute`) Completed (Commit `287efa28`)**:
  - Decomposed monolithic 1,348 LOC (64.3 KB) `backend_v2/hooks/scoring.py` into modular package `backend_v2/hooks/scoring/`:
    - `models.py` (105 LOC, limit <120): Pure extraction DTOs (`ScoringPayloadWrapper`, `StateInputWrapper`, `_extract_payloads`) with mandatory sunset in Sub-Phase 3B.
    - `falsifier_hook.py` (249 LOC, limit <250): `apply_scoring_logic_hook` + security & falsifier penalty calculation without reflection.
    - `passivity_hook.py` (186 LOC, limit <200): `enforce_passivity_penalty_hook` + low-quality score scaling.
    - `matrix_hook.py` (475 LOC, limit <480): `matrix_scoring_hook` + quote evidence validation + AST Evaluator integration with `isinstance()` narrowing.
    - `normalization_hook.py` (384 LOC, limit <400): `normalize_matrix_scores_hook` + `recalculate` hybrid calculation engine without hardcoded scales.
    - `__init__.py` (37 LOC, limit <40): PEP 484 Strangler Fig facade with explicit `__all__` and redundant re-export aliases for all 5 hook functions and 2 temporary DTOs.
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
- **Phase 3B Full Hooks Migration & Models Sunset (`/tier2-execute`) Completed (Commit `5915d9aa`)**:
  - Upgraded `backend_v2/core/hook_registry.py` to strictly typed `HookState(inputs: ExecutionInputsDTO, global_context_vars: GlobalContextVarsDTO)` and `HookResult(state_delta: HookDeltaDTO | None)`.
  - Migrated all validation and ingress hooks: `validation.py`, `security.py`, `input_processing.py`, `hydration.py`, `interaction_hook.py`.
  - Migrated all extraction, context and integrity hooks: `source_verification_hook.py`, `atom_flattening.py`, `context_mapper.py`, `integrity.py`, `linguistics.py`, `llm.py`, `archival.py`, `dlq_guard.py`, `metadata.py`, `metrics.py`, `references.py`.
  - Permanently deleted temporary scaffolding module `[DELETE] backend_v2/hooks/scoring/models.py`, absorbed extraction logic into `falsifier_hook.py`, and cleaned up `backend_v2/hooks/scoring/__init__.py`.
  - Modernized all 4 scoring modules (`falsifier_hook.py`, `passivity_hook.py`, `matrix_hook.py`, `normalization_hook.py`) to consume `ExecutionInputsDTO` and return `HookDeltaDTO`.
  - Modernized test fixtures and assertions across all hook test files in `backend_v2/tests/unit/hooks/` and `backend_v2/tests/unit/core/test_hook_registry.py` (93/93 tests passing: 89 passed, 4 xpassed).
  - Validated AST guardrails: `uv run python scripts/_ast_guardrails.py backend_v2/hooks/ --strict` passed cleanly (0 errors).
  - Verified SDUI semantic parity: `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py` passed 100%.
  - Marked Phase 3B Execution status as `[x] [OK]`.
- **Phase 3B System 2 Red-Team Audit (`/tier8-audit-plan`) Completed**:
  - Validated 100% adherence to all Phase 3B DoD items, architectural invariants, and quality gates.
  - Modernized `backend_v2/tests/unit/test_references.py` to instantiate typed `HookState` with `ExecutionInputsDTO`, `GlobalContextVarsDTO`, and `ExecutionMetadata(target_locale="fi")`.
  - Fixed PEP 257 docstring warnings and line-length formatting across `hook_registry.py`, `atom_flattening.py`, `dlq_guard.py`, `linguistics.py`, and `falsifier_hook.py`.
  - Confirmed 100% test pass across all 118 hook tests (`114 passed, 4 xpassed`).
  - Confirmed 0 errors on AST Guardrails (`uv run python scripts/_ast_guardrails.py backend_v2/hooks/ backend_v2/core/hook_registry.py --strict`).
  - Confirmed 0 errors on Markdown boundaries (`audit_markdown_boundaries.py` and `audit_tracker_output.py`).
  - Generated audit report: `red_team_audit_04_placeholder_phase3b_hooks_pydantic_v2_migration.md`.
  - Marked Phase 3B audit status as `[x] [OK]`.

- **Phase 4 Plan Creation (`/tier0-create-plan`) Completed**:
  - Authored comprehensive architectural implementation plan for Phase 4: Orchestration & Strategy Core Refactoring & Tests (`05_placeholder_phase4_orchestration_and_strategy_core.md`).
  - Pre-flight AST analysis of `backend_v2/services/orchestrator/` identified 21 FATAL guardrail violations across reflection (`getattr`/`hasattr` in `dag_executor.py`, `context_builder.py`, `llm.py`, `context_router.py`, `prompt_compiler_adapter.py`), banned lazy fallbacks (`.get()` in `dag_compiler.py`, `synthesis_engine.py`, `tda_engine.py`, `extractive_sensor_service.py`, `llm.py`, `context_builder.py`, `synthesis_distiller.py`), and missing strict `ConfigDict` (`context_router.py`, `base.py`).
  - Itemized concrete remediation for all 19 production files across 6 phased steps: Strategy Base & Hook Integration, LLM Execution & Context Builder, Prompt Compiler & Context Router, Synthesis & Evaluation Engines, DAG Executor & Reasoning Orchestration, and Atomic Test Modernization across 43 orchestrator test files.
  - Synchronized `EPIC_149_tracker.md` with all 6 execution steps and appended newly planned targets to the Backend Hardening Gate.
  - Marked Phase 4 Plan Creation status as `[x] [OK]`.

## Learned
- Repository reconstitution requires updating `backend_v2/database/interfaces.py` in lockstep to avoid Protocol divergence and MyPy strict mode violations.
- `backend_audit_loop.py` automatically maps target files (specifically `backend_v2/database/repositories/execution.py`) to `backend_v2/tests/unit/database/repositories/test_execution.py`. Establishing 1:1 test files under `backend_v2/tests/unit/database/repositories/` guarantees automated compliance and deterministic coverage.
- Elimination of `.get(key, default)` in domain code is required by AST Guardrail `QGR002`; all dictionary indexing on internal drivers must use direct keys with Fail-Fast exceptions or Pydantic validation.
- Monolithic `scoring.py` (1,348 LOC) requires decomposition into 4 focused submodules (`falsifier_hook.py`, `passivity_hook.py`, `matrix_hook.py`, `normalization_hook.py`) with a PEP 484 Strangler Fig facade in `__init__.py` to eliminate AST violations while maintaining 100% backward compatibility with service callers.
- In unit test fixtures, `HookState` requires `metadata=ExecutionMetadata(target_locale="fi")` rather than raw empty dict `{}` to satisfy strict Pydantic V2 validation and MyPy `--strict` checking.
- Pre-flight test analysis revealed that `apply_scoring_logic_hook` and `enforce_passivity_penalty_hook` had zero dedicated unit test coverage in `test_scoring.py`; test expansion with positive/negative boundary partitions is required in Phase 1 before monolith deletion.
- In `backend_audit_loop.py`, testing decomposed packages requires discovering candidates from parent directory name (`parts[-2]`) when given `__init__.py`, and testing directory paths should check for matching test files under `backend_v2/tests/unit/hooks/test_<module>.py`.
- Sub-Phase 3B permanently sunsets `backend_v2/hooks/scoring/models.py` by absorbing `ScoringPayloadWrapper` and `_extract_payloads` into `falsifier_hook.py` and strictly updating `HookState` and `HookResult` to consume typed DTOs from `backend_v2/models/dtos/hook_state.py`.
- `HookState.inputs: ExecutionInputsDTO` provides structured attributes (`raw_inputs`, `dynamic_inputs`, `target_locale`, `user_role`) that replace untyped `.get()` lookups across validation, ingress, security, extraction, and scoring hooks.
- `HookResult.state_delta: HookDeltaDTO | None` provides clean separation between `delta` (payload dictionary) and `metadata_updates` (metadata dictionary), replacing manual `delta.pop("metadata", None)` hacks.
- In `backend_v2/settings.py`, declaring optional `model_registry: dict[str, Any] | None = None` provides direct attribute access for `llm.py` hook resolution without requiring reflection `getattr()` calls.
- In `backend_v2/hooks/input_processing.py`, missing execution context or missing mandatory language raises `AppException` with `ErrorCodes.VALIDATION_FAILED` and `ErrorCodes.CONFIGURATION_ERROR` respectively.
- For Phase 4 (Consumers), `StrategyContext` and `DAGExecutor` strategies (`base.py`, `logic.py`, `llm.py`) must be refactored to consume typed `ExecutionInputsDTO`, `GlobalContextVarsDTO`, and `HookDeltaDTO` rather than expecting raw dicts.
- In `backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py`, `StepOutputDTO` has direct properties `block_id`, `payload`, `step_id`; eliminating `getattr(dto, ...)` removes 10 reflection violations in one file.

## Remaining
- **Phase 4**: Orchestration & Strategy Core Refactoring & Tests (`05_placeholder_phase4_orchestration_and_strategy_core.md`).
- **Phase 5**: Service Layer, Utility Services & Service Tests (`06_placeholder_phase5_service_layer_and_identity.md`).
- **Phase 6**: Background Workers, Typed Cache Boundary & Storage (`07_placeholder_phase6_workers_typed_cache_and_storage.md`).
- **Phase 7**: AST Guardrails Hardening & Global Clean Code Audit (`08_placeholder_phase7_ast_guardrails_hardening.md`).

## Resume Command
```powershell
/tier0-research-plan @[docs/epic/tasks_EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition/05_placeholder_phase4_orchestration_and_strategy_core.md] @[docs/epic/EPIC_149_tracker.md]
```


