# EPIC 147 Tracker: Engine Dispatch, Strategy Container & DAG Concurrency Hardening

**Epic:** @[docs/epic/EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience.md]
**Task Directory:** @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_polymorphic_rule_routing.md]</knowledge_item>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
  <knowledge_item>@[ki_ast_guardrail_testing.md]</knowledge_item>
  <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
  <knowledge_item>@[ki_llm_extraction_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
</required_context_rules>

## Phase Execution Status

### Phase 1: Pre-Implementation Technical Debt Cleanups, DTOs, Repository Interfaces & Strategy Registry
**Plan:** @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/01_phase1_tech_debt_dtos_repositories_and_strategy_registry.md]
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/01_phase1_tech_debt_dtos_repositories_and_strategy_registry.md] @[docs/epic/EPIC_147_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/01_phase1_tech_debt_dtos_repositories_and_strategy_registry.md] @[docs/epic/EPIC_147_tracker.md]`
  - [x] Step 1: Scoped Technical Debt Cleanup in test_llm_cost_tracking.py & llm.py
  - [x] Step 2: Canonical StepType Enum & Schema Update
  - [x] Step 3: Fail-Fast PromptBlock Batch Resolution in Repository
  - [x] Step 4: Define StrategyDependencies Container & Update Strategy Base
  - [x] Step 5: Static NODE_STRATEGY_REGISTRY & NodeStrategyFactory
  - [x] Step 6: Atomic Unit Test Migration for Phase 1
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/01_phase1_tech_debt_dtos_repositories_and_strategy_registry.md] @[docs/epic/EPIC_147_tracker.md]`

### Phase 2: Engine Architecture, NodeExecutor Decomposition, Single-Fetch DI & DAG Concurrency Hardening
**Plan:** @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/02_phase2_engine_architecture_node_executor_and_dag_concurrency.md]
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/02_phase2_engine_architecture_node_executor_and_dag_concurrency.md] @[docs/epic/EPIC_147_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/02_phase2_engine_architecture_node_executor_and_dag_concurrency.md] @[docs/epic/EPIC_147_tracker.md]`
  - [x] Step 1: Decompose NodeExecutor & Single-Fetch DI in dag_executor.py
  - [x] Step 2: Atomic Deduplicating State Accumulation under _update_lock in DAGExecutor
  - [x] Step 3: Extract PromptEngine
  - [x] Step 4: Refactor LLMNodeStrategy to Delegate to ExecutionEngine
  - [x] Step 5: Atomic Unit Test Migration for NodeExecutor & DAGExecutor
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/02_phase2_engine_architecture_node_executor_and_dag_concurrency.md] @[docs/epic/EPIC_147_tracker.md]`

### Phase 3: Ghost Execution Elimination & Source Verification Hook Hardening
**Plan:** @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/03_placeholder_phase3_ghost_execution_elimination_and_hook_hardening.md]
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/03_placeholder_phase3_ghost_execution_elimination_and_hook_hardening.md] @[docs/epic/EPIC_147_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/03_placeholder_phase3_ghost_execution_elimination_and_hook_hardening.md] @[docs/epic/EPIC_147_tracker.md]`
  - [x] Step 1: Pre-Implementation Technical Debt Cleanups, Source Extraction Schema & Global Config Sovereignty
  - [x] Step 2: Source Verification Hook & Service Hardening
  - [x] Step 3: Unit Testing for Source Verification Hook & Service
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/03_placeholder_phase3_ghost_execution_elimination_and_hook_hardening.md] @[docs/epic/EPIC_147_tracker.md]`

### Phase 4: AST Guardrails, Unit Test Suites, Mock Migrations & E2E Integration Gate
**Plan:** @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/04_placeholder_phase4_ast_guardrails_unit_test_suites_and_e2e_gate.md]
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/04_placeholder_phase4_ast_guardrails_unit_test_suites_and_e2e_gate.md] @[docs/epic/EPIC_147_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/04_placeholder_phase4_ast_guardrails_unit_test_suites_and_e2e_gate.md] @[docs/epic/EPIC_147_tracker.md]`
  - [x] Step 1: Create AST Guardrail Suite
  - [x] Step 2: Global Unit Test Verification
  - [x] Step 3: Live E2E Integration Gate
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/04_placeholder_phase4_ast_guardrails_unit_test_suites_and_e2e_gate.md] @[docs/epic/EPIC_147_tracker.md]`

### Integration Checkpoint: Full-Stack Validation
- [x] **[OK] Backend Integration Suite**: Run `uv run python scripts/backend_audit_loop.py backend_v2 --test`
- [x] **[OK] Live E2E Integration Gate**: Run `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

### Post-Implementation Gates
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests were left behind in the modified domains.
- [ ] **[NOK] Proxy Sunset & Consumer Migration**: Codebase-wide search/replace of old import paths & delete deprecated proxies.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified backend files:
  - [x] @[backend_v2/models/enums.py]
  - [x] @[backend_v2/models/v2_core.py]
  - [x] @[backend_v2/database/interfaces.py]
  - [x] @[backend_v2/database/repositories/components/prompt_block.py]
  - [x] @[backend_v2/services/orchestrator/strategies/base.py]
  - [x] @[backend_v2/services/orchestrator/strategies/logic.py]
  - [x] @[backend_v2/services/orchestrator/strategies/llm.py]
  - [x] @[backend_v2/services/orchestrator/strategies/registry.py]
  - [x] @[backend_v2/services/orchestrator/engines/prompt_engine.py]
  - [x] @[backend_v2/services/orchestrator/engines/__init__.py]
  - [x] @[backend_v2/models/dtos/engine.py]
  - [x] @[backend_v2/core/hook_registry.py]
  - [x] @[backend_v2/services/orchestrator/engines/synthesis_engine.py]
  - [x] @[backend_v2/services/orchestrator/dag_executor.py]
  - [x] @[backend_v2/models/state.py]
  - [x] @[backend_v2/settings.py]
  - [x] @[backend_v2/models/dtos/source_extraction_schema.py]
  - [ ] @[backend_v2/hooks/source_verification_hook.py]
  - [ ] @[backend_v2/services/source_verification_service.py]
  - [ ] @[backend_v2/hooks/__init__.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` (No production Dart files modified in backend-focused Epic 147).
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for surviving business logic.

### Documentation & Knowledge Item Update
- [ ] **[NOK]** As-Built Architectural Sync: Run `/tier7-describe-architecture` to automatically scan the codebase, anchor the physical implementation map in `docs/architecture/`, create/update relevant Knowledge Items (KIs), and update `.agents/rules/04_directory_reference.md`.

### Final Epic Audit
- [ ] **[NOK]** System 2 Reverse Epic Analysis: Run `/tier8-audit-epic @[docs/epic/EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.

## Instructions for the Execution Agent
1. **Atomic Commits**: After ANY successful run of the `universal_quality_gate` audit script that passes, you MUST instruct the user to perform an atomic `git commit` before proceeding to the next file or logic block. Git commit messages MUST ALWAYS be written in English.
2. **Seeding Environment**: If database schema changes or resets are required, run: `uv run python backend_v2/seed/run_seed.py local`.
3. **Workspace Relative Syntax**: All file references MUST use `@-reference` syntax (e.g. `@[backend_v2/services/...]`).
4. **Mandatory Workflow Loop**: The mandatory execution cycle is:
   `[/tier0-create-plan if deferred] -> /tier0-research-plan -> /tier2-execute -> /tier8-audit-plan`.
   You MUST ALWAYS pass BOTH the plan and the tracker file in ALL commands.
   Once all Phases are complete, the loop MUST continue through the Post-Implementation Gates:
   `/tier2-hardening-backend -> /tier2-hardening-frontend -> /tier7-describe-architecture -> /tier8-audit-epic`.
5. **Session Handover Update**: You MUST update the `/tier5-resume` or `/tier0-research-plan` command at the bottom of this tracker before handing over the session. Whenever you finish a milestone, pause for user feedback, or complete a session, you MUST automatically output the next command in your chat response so the user can easily copy-paste it to continue. Note: You do not need to specify `--rules` in the resume command; context rules are self-hydrating directly from `<required_context_rules>` blocks.

## Requirements Traceability Matrix

| Requirement ID | Technical Requirement Description | Source Epic Section | Target Plan & Step | Implementation File Targets | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **REQ-147-01** | Remove stale mock patch `@patch("...tda_engine.get_settings")` in `test_llm_cost_tracking.py` to prevent AttributeError during test collection. | Section 3 (Item 1), Section 5 (Step 1.1) | Phase 1, Step 1 | `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py]` | [OK] |
| **REQ-147-02** | Replace silent `except Exception: pass` blocks in `llm.py` with explicit `AppException(RESOURCE_NOT_FOUND / VALIDATION_FAILED)` and structured RFC 7807 logging. | Section 3 (Item 4), Section 5 (Step 1.1) | Phase 1, Step 1 | `@[backend_v2/services/orchestrator/strategies/llm.py]` | [OK] |
| **REQ-147-03** | Replace raw string comparison `b.category_id == "matrix"` with `PromptBlockCategory.MATRIX` enum comparisons in `llm.py`. | Section 3 (Item 7), Section 5 (Step 1.1) | Phase 1, Step 1 | `@[backend_v2/services/orchestrator/strategies/llm.py]` | [OK] |
| **REQ-147-04** | Eliminate `getattr`/`hasattr` duck typing and magic defaults (`expected_sdui_type="grid"`) in `llm.py`. | Section 3 (Items 5, 6), Section 5 (Step 1.1) | Phase 1, Step 1 | `@[backend_v2/services/orchestrator/strategies/llm.py]` | [OK] |
| **REQ-147-05** | Declare canonical `StepType(StrEnum)` with `LLM = "llm"` and `LOGIC = "logic"` in `enums.py` and update `Step.type` in `v2_core.py`. | Section 3 (Item 13), Section 5 (Step 1.2) | Phase 1, Step 2 | `@[backend_v2/models/enums.py]`, `@[backend_v2/models/v2_core.py]` | [OK] |
| **REQ-147-06** | Declare `get_prompt_blocks_by_ids` in `IPromptBlockRepository` and implement in `PromptBlockRepositoryImpl` with strict mathematical set difference validation (`unique_requested - found_ids`) raising `AppException(RESOURCE_NOT_FOUND)`. | Section 3 (Item 18), Section 5 (Step 1.3) | Phase 1, Step 3 | `@[backend_v2/database/interfaces.py]`, `@[backend_v2/database/repositories/components/prompt_block.py]` | [OK] |
| **REQ-147-07** | Define `@dataclass(frozen=True) StrategyDependencies` and update `StrategyContext` with `prompt_blocks: list[PromptBlock]` in `base.py`. | Section 3 (Item 8), Section 5 (Step 1.4) | Phase 1, Step 4 | `@[backend_v2/services/orchestrator/strategies/base.py]` | [OK] |
| **REQ-147-08** | Refactor `NodeStrategy` and `LogicNodeStrategy` constructors to accept `deps: StrategyDependencies` and remove 10 loose repository parameters. | Section 3 (Item 8), Section 5 (Step 1.4) | Phase 1, Step 4 | `@[backend_v2/services/orchestrator/strategies/base.py]`, `@[backend_v2/services/orchestrator/strategies/logic.py]` | [OK] |
| **REQ-147-09** | Implement static `NODE_STRATEGY_REGISTRY` mapping `StepType` to `StrategyBuilder` and `NodeStrategyFactory.create_strategy` in `registry.py`. | Section 3 (Item 12), Section 5 (Step 1.5) | Phase 1, Step 5 | `@[backend_v2/services/orchestrator/strategies/registry.py]` | [OK] |
| **REQ-147-10** | Migrate Phase 1 unit test fixtures (`test_logic.py`, `test_llm_cost_tracking.py`, `test_prompt_block.py`, `test_node_strategy_registry.py`, `test_registry.py`, `test_base.py`, `test_llm.py`) to typed Pydantic V2 models and `StrategyDependencies`. | Section 3 (Items 19, 21), Section 5 (Step 1.6) | Phase 1, Step 6 | `@[backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py]`, `@[backend_v2/tests/unit/test_logic.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py]`, `@[backend_v2/tests/unit/database/repositories/components/test_prompt_block.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_node_strategy_registry.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_registry.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_base.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]` | [OK] |
| **REQ-147-11** | Update `NodeExecutor` constructor to accept `deps: StrategyDependencies`, implement `_resolve_execution_engine` decoupled from `model_strategy == "synthesis"`, single-fetch criteria blocks, and delegate to `NodeStrategyFactory`. | Section 3 (Items 8, 12, 20), Section 5 (Step 2.1) | Phase 2, Step 1 | `@[backend_v2/services/orchestrator/dag_executor.py]` | [OK] |
| **REQ-147-12** | Synchronize DAG trace append loop inside `_update_lock` and implement atomic deduplicating accumulation of `MCPAuditTrace` and `generated_schemas` under `_update_lock` in `DAGExecutor`. | Section 3 (Items 2, 11), Section 5 (Step 2.2) | Phase 2, Step 2 | `@[backend_v2/services/orchestrator/dag_executor.py]`, `@[backend_v2/models/state.py]` | [OK] |
| **REQ-147-13** | Extract `PromptEngine` implementing `ExecutionEngine` protocol for structured non-matrix LLM tasks in `prompt_engine.py` and export in `engines/__init__.py`. | Section 3 (Item 9), Section 5 (Step 2.3) | Phase 2, Step 3 | `@[backend_v2/services/orchestrator/engines/prompt_engine.py]`, `@[backend_v2/services/orchestrator/engines/__init__.py]` | [OK] |
| **REQ-147-14** | Refactor `LLMNodeStrategy` to accept `(deps: StrategyDependencies, engine: ExecutionEngine)`, consume injected `context.prompt_blocks`, eliminate `get_all_prompt_blocks()`, and delegate to `engine.execute()`. | Section 3 (Items 8, 10), Section 5 (Step 2.4) | Phase 2, Step 4 | `@[backend_v2/services/orchestrator/strategies/llm.py]` | [OK] |
| **REQ-147-15** | Eliminate in-place mutation of `frozen_ctx.generated_schemas` in `LLMNodeStrategy` and propagate schemas via `TraceEvent.metadata["generated_schema"]`. | Section 3 (Item 3), Section 5 (Step 2.4) | Phase 2, Step 4 | `@[backend_v2/services/orchestrator/strategies/llm.py]` | [OK] |
| **REQ-147-16** | Update `EngineExecutionResult.synthesis_output` to `BaseModel | None`, update `HookState.inputs` and `HookResult.state_delta` in `hook_registry.py` to `BaseModel | dict[str, Any]`, and update `SynthesisEngine` to preserve typed models, eliminating raw `final_dict` and premature `.model_dump()` in-memory. | Section 3 (Items 111, 112, 113, 114), Section 5 (Step 2.4) | Phase 2, Step 4 | `@[backend_v2/models/dtos/engine.py]`, `@[backend_v2/core/hook_registry.py]`, `@[backend_v2/services/orchestrator/engines/synthesis_engine.py]`, `@[backend_v2/services/orchestrator/strategies/llm.py]` | [OK] |
| **REQ-147-17** | Migrate `test_dag_executor.py` and `test_llm.py` to `StrategyDependencies` and typed models, and create `test_prompt_engine.py` and `test_dag_executor_mcp_concurrency.py`. | Section 3 (Items 19, 21), Section 5 (Step 2.5) | Phase 2, Step 5 | `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]`, `@[backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_concurrency.py]` | [OK] |
| **REQ-147-18** | Define `min_verifiable_text_length: int = 15` in `settings.py` and declare `SourceVerificationInputsDTO` in `source_extraction_schema.py`. | Section 3 (Items 14), Section 5 (Step 3.1) | Phase 3, Step 1 | `@[backend_v2/settings.py]`, `@[backend_v2/models/dtos/source_extraction_schema.py]` | [OK] |
| **REQ-147-19** | Attach `@hook_registry.register("source_verification")` to `source_verification_hook.py`, short-circuit empty/whitespace/sub-threshold inputs returning complete zero-claims `SourceVerificationResultDTO` envelope with native typed objects directly, and export in `hooks/__init__.py`. | Section 3 (Items 14, 16), Section 5 (Step 3.2) | Phase 3, Step 2 | `@[backend_v2/hooks/source_verification_hook.py]`, `@[backend_v2/hooks/__init__.py]` | [OK] |
| **REQ-147-20** | Replace hardcoded mock LLM credentials in `SourceVerificationService` with `LLMClient.from_strategy("fast", ...)`, declare static module prompt constants, and sanitize XML injection with `html.escape()`. | Section 3 (Items 15, 17), Section 5 (Step 3.2) | Phase 3, Step 2 | `@[backend_v2/services/source_verification_service.py]` | [OK] |
| **REQ-147-21** | Create comprehensive unit tests for `SourceVerificationHook` and `SourceVerificationService` covering short-circuits, zero-claims envelope, sub-threshold length, and XML injection defense. | Section 5 (Step 3.3), Section 6 (TC-SV-01..06) | Phase 3, Step 3 | `@[backend_v2/tests/unit/hooks/test_source_verification_hook.py]`, `@[backend_v2/tests/unit/services/test_source_verification_service.py]` | [OK] |
| **REQ-147-22** | Create AST Guardrail suite `test_ast_engine_dispatch_guardrails.py` enforcing hook registration, zero procedural string routing in `DAGExecutor`, zero in-place `frozen_ctx.generated_schemas` mutations, mathematical set parity in `PromptBlockRepository`, and hook state immutability. | Section 5 (Step 4.1), Section 6 (TC-AST-01..05) | Phase 4, Step 1 | `@[backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py]` | [OK] |
| **REQ-147-23** | Execute global unit test verification across all backend suites ensuring zero test failures, zero deprecation warnings, and >90% coverage. | Section 5 (Step 4.2), Section 7 (DoD) | Phase 4, Step 2 | All backend unit test files | [OK] |
| **REQ-147-24** | Execute live E2E REST API integration test gate `test_integration_real_llm.py` with live foundational models. | Section 5 (Step 4.3), Section 7 (DoD) | Phase 4, Step 3 | `@[backend_v2/tests/integration/test_integration_real_llm.py]` | [OK] |

# Session Handover Context

## Achieved
- **Phase 1-4 Complete, Validated & Hardened**:
  - **Phase 1**: Implemented and committed StepType enum, prompt block batch resolution, StrategyDependencies, and static NodeStrategy registry (`01_phase1_tech_debt_dtos_repositories_and_strategy_registry.md`).
  - **Phase 2**: Decomposed NodeExecutor, extracted PromptEngine, refactored LLMNodeStrategy, and synchronized DAG concurrency (`02_phase2_engine_architecture_node_executor_and_dag_concurrency.md`).
  - **Phase 3**: Hardened SourceVerificationHook and Service, defined global config sovereignty (`min_verifiable_text_length`), eliminated ghost execution, and protected XML injection (`03_placeholder_phase3_ghost_execution_elimination_and_hook_hardening.md`).
  - **Phase 4**: Implemented AST Guardrails (`test_ast_engine_dispatch_guardrails.py`), verified 433 unit tests, and passed live E2E REST API integration test (`test_integration_real_llm.py`).
- **Tier 2 Backend Hardening (14/20 Files Audited, Hardened & Verified with 100% Quality Loop & Commit Gates)**:
  1. `@[backend_v2/models/enums.py]`: Exported `__all__`, full L10n property coverage and StepType enum validation; 100% test coverage; full neuro-symbolic audit matrix PASS. Commit: `a7d2d385`.
  2. `@[backend_v2/models/v2_core.py]`: Exported `__all__`, strict Pydantic V2 Fail-Fast validation, `extra='forbid'`, `strict=True`, opaque ID regex compliance; 95% test coverage; full neuro-symbolic audit matrix PASS. Commit: `24b54e19`.
  3. `@[backend_v2/database/interfaces.py]`: Exported `__all__`, ISP protocol definitions; 100% test coverage; full neuro-symbolic audit matrix PASS. Commit: `c565a04e`.
  4. `@[backend_v2/database/repositories/components/prompt_block.py]`: Exported `__all__`, set difference validation for batch prompt block retrieval, strict Fail-Fast on missing IDs; 98% test coverage; full neuro-symbolic audit matrix PASS. Commit: `ec3df52f`.
  5. `@[backend_v2/services/orchestrator/strategies/base.py]`: Exported `__all__`, StrategyDependencies container, StrategyContext immutability, quota circuit breaker; 95% test coverage; full neuro-symbolic audit matrix PASS. Commit: `cb5eb970`.
  6. `@[backend_v2/services/orchestrator/strategies/logic.py]`: Exported `__all__`, LogicNodeStrategy hook delegation, HookDependencies wiring, fail-fast on hook failure; 100% test coverage; full neuro-symbolic audit matrix PASS. Commit: `197cf64a`.
  7. `@[backend_v2/services/orchestrator/strategies/llm.py]`: Exported `__all__ = ["LLMNodeStrategy"]`, early `_engine is None` Fail-Fast guard, strict matrix scale schema alignment (`score`, `ai_label`, `claims`), `FlattenedAtom` typed DTO consumption, token counting isolated mocks; 90% test coverage across 25 comprehensive unit test cases; full neuro-symbolic audit matrix PASS across all 156 rules. Commit: `0341c305`.
  8. `@[backend_v2/services/orchestrator/strategies/registry.py]`: Exported `__all__`, deferred `TYPE_CHECKING` imports in `engine.py` eliminating circular dependency with `strategies.base`, strict factory resolution for `StepType.LOGIC` and `StepType.LLM`; 100% test coverage; full neuro-symbolic audit matrix PASS across all 156 rules. Commit: `bb32bcfe`.
  9. `@[backend_v2/services/orchestrator/engines/prompt_engine.py]`: Exported `__all__ = ["PromptEngine"]`, resolved forward reference via `EngineExecutionRequest.model_rebuild()` in `strategies.base`, 98% unit test coverage in `test_prompt_engine.py`; full neuro-symbolic audit matrix PASS across 156 rules. Commit: `c2c19e68`.
  10. `@[backend_v2/services/orchestrator/engines/__init__.py]`: Verified clean `__all__` re-exports (`ExecutionEngine`, `PromptEngine`, `SynthesisEngine`, `TDAEngine`), added export verification in `test_engines_init.py` and `test_prompt_engine.py`; 100% coverage; full neuro-symbolic audit matrix PASS. Commit: `a5d6c4ae`.
  11. `@[backend_v2/models/dtos/engine.py]`: Exported `__all__ = ["EngineExecutionRequest", "EngineExecutionResult", "FlattenedAtom", "MatrixEvaluationContext"]`, dedicated test suite `test_engine_dtos.py` testing immutability, `extra="forbid"`, `semaphore_cm` context manager, and `CausalEdge` dependency assertions; 95% line coverage; full neuro-symbolic audit matrix PASS across 156 rules. Commit: `2de0efee`.
  12. `@[backend_v2/core/hook_registry.py]`: Exported `__all__ = ["HookDependencies", "HookFunction", "HookRegistry", "HookResult", "HookState", "ISearchClient", "hook_registry"]`, expanded unit tests in `test_hook_registry.py` covering sync/async execution, duplicate registration handling, missing hook handling, invalid return type detection, and runtime exception wrapping; 94% line coverage; full neuro-symbolic audit matrix PASS across 156 rules. Commit: `a2fa364e`.
  13. `@[backend_v2/services/orchestrator/engines/synthesis_engine.py]`: Exported `__all__ = ["SynthesisEngine"]`, verified unit tests in `test_synthesis_engine.py` testing data starvation circuit breaking, CDATA payload encapsulation, sparse data mandates, and exception handling; 100% line coverage; full neuro-symbolic audit matrix PASS across 156 rules. Commit: `09e99ce3`.
  14. `@[backend_v2/services/orchestrator/dag_executor.py]`: Exported `__all__ = ["DAGExecutor", "ExecutionCommitter", "NodeExecutor"]`, expanded unit tests covering committer failure, RAG preflight failure, matrix reducer failure, and progress callback branches reaching 90% line coverage; full neuro-symbolic audit matrix PASS across all 156 rules. Commit: `17c3c031`.
  15. `@[backend_v2/models/state.py]`: Exported `__all__ = ["ErrorTraceEvent", "EvidenceOverrideDTO", "ExecutionState", "ReasoningTrace", "StateProjector", "StepExecutionEnvelope", "StepOutputDTO", "TombstoneEvent", "TraceEvent", "WorkflowState"]`, enhanced RFC 7807 dual logging in `StateProjector`, expanded unit tests in `test_state.py` covering token truncation, confidence bounds, legacy detection, and lazy property accessors reaching 100% line coverage; full neuro-symbolic audit matrix PASS across all 156 rules. Commit: `2634801f`.
  16. `@[backend_v2/settings.py]`: Verified public exports, global config sovereignty (`min_verifiable_text_length`, timeouts, concurrency limits), RFC 7807 logging, expanded unit tests in `test_settings.py` covering all path properties and service account auto-detection reaching 100% line coverage; full neuro-symbolic audit matrix PASS across all 156 rules. Commit: `663b3315`.
  17. `@[backend_v2/models/dtos/source_extraction_schema.py]`: Added PEP 257 module docstring, exported `__all__ = ["SourceExtractionResponseSchema", "SourceVerificationInputsDTO"]`, expanded unit tests in `test_source_extraction_schema.py` covering `__all__` and `extra="forbid"` strictness reaching 100% line coverage; full neuro-symbolic audit matrix PASS across all 156 rules. Commit: `90c58547`.

## Learned
- **Target Anchoring in Audit Matrices**: `audit_matrix_manager.py` enforces target anchoring: citations in justifications cannot mention other source files unless they are common systemic dependencies (`settings.py`, `enums.py`, `conftest.py`).
- **Circular Import Elimination via `TYPE_CHECKING` & `model_rebuild()`**: Cross-module dependencies between `backend_v2.models.dtos.engine` and `backend_v2.services.orchestrator.strategies.base` require `from __future__ import annotations`, `if TYPE_CHECKING:` guards, and calling `EngineExecutionRequest.model_rebuild()` directly after `StrategyContext` definition in `base.py` to prevent `PydanticUserError` during runtime instantiation.
- **Pydantic V2 Step & BARS Scale Schema Strictness**: `MatrixScale` requires `score`, `ai_label`, and `claims: list[MatrixClaim]`. Test fixtures must strictly honor `extra="forbid"` without legacy field names (`label`, `claim`).
- **Session Bounding for Strictness**: Limiting hardening sessions to 3-5 files prevents context amnesia, ensures deep verification of every invariant, and maintains deterministic state transitions via `@[tmp/hardening_state.json]`.
- **L10n Property Completeness**: All enum `@property l10n_key` getters must be tested against both mapped and unmapped variants to reach 100% line coverage and guarantee frontend `.arb` parity.
- **DTO Immutability and Envelope Guarantees**: Enforcing `frozen=True` and `extra="forbid"` on engine and hook DTOs (`FlattenedAtom`, `MatrixEvaluationContext`, `EngineExecutionRequest`, `EngineExecutionResult`, `HookState`, `HookResult`) prevents subtle runtime mutations across asynchronous execution boundaries.

## Codebase Physical Anchor Reference Map
- `NodeExecutor`: `@[backend_v2/services/orchestrator/dag_executor.py#L119-L285]`
- `DAGExecutor`: `@[backend_v2/services/orchestrator/dag_executor.py#L287-L720]`
- `PromptEngine`: `@[backend_v2/services/orchestrator/engines/prompt_engine.py#L1-L73]`
- `SynthesisEngine`: `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L1-L220]`
- `TDAEngine`: `@[backend_v2/services/orchestrator/engines/tda_engine.py#L1-L210]`
- `LLMNodeStrategy`: `@[backend_v2/services/orchestrator/strategies/llm.py#L58-L830]`
- `NodeStrategyFactory`: `@[backend_v2/services/orchestrator/strategies/registry.py#L1-L60]`
- `EngineExecutionRequest` / `EngineExecutionResult`: `@[backend_v2/models/dtos/engine.py#L85-L149]`
- `HookRegistry` / `HookState` / `HookResult`: `@[backend_v2/core/hook_registry.py#L30-L217]`
- `source_verification_hook`: `@[backend_v2/hooks/source_verification_hook.py#L1-L130]`
- `SourceVerificationService`: `@[backend_v2/services/source_verification_service.py#L1-L288]`
- `SourceVerificationInputsDTO`: `@[backend_v2/models/dtos/source_extraction_schema.py#L1-L37]`
- `SourceVerificationResultDTO`: `@[backend_v2/models/domain/source_verification.py#L61-L79]`
- `Settings.min_verifiable_text_length`: `@[backend_v2/settings.py#L204-L206]`
- `AST Guardrail Suite`: `@[backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py#L1-L318]`

## Remaining Targets in Tier 2 Hardening (Backend)
- `@[backend_v2/hooks/source_verification_hook.py]`
- `@[backend_v2/services/source_verification_service.py]`
- `@[backend_v2/hooks/__init__.py]`

## Next Command
`/tier5-resume --target="@[docs/epic/EPIC_147_tracker.md], backend_v2/hooks/source_verification_hook.py" --workflow=/tier2-hardening-backend`



