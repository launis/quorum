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
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/03_placeholder_phase3_ghost_execution_elimination_and_hook_hardening.md] @[docs/epic/EPIC_147_tracker.md]`

### Phase 4: AST Guardrails, Unit Test Suites, Mock Migrations & E2E Integration Gate
**Plan:** @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/04_placeholder_phase4_ast_guardrails_unit_test_suites_and_e2e_gate.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/04_placeholder_phase4_ast_guardrails_unit_test_suites_and_e2e_gate.md] @[docs/epic/EPIC_147_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/04_placeholder_phase4_ast_guardrails_unit_test_suites_and_e2e_gate.md] @[docs/epic/EPIC_147_tracker.md]`
  - [ ] Step 1: Create AST Guardrail Suite
  - [ ] Step 2: Global Unit Test Verification
  - [ ] Step 3: Live E2E Integration Gate
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/04_placeholder_phase4_ast_guardrails_unit_test_suites_and_e2e_gate.md] @[docs/epic/EPIC_147_tracker.md]`

### Integration Checkpoint: Full-Stack Validation
- [ ] **[NOK] Backend Integration Suite**: Run `uv run python scripts/backend_audit_loop.py backend_v2 --test`
- [ ] **[NOK] Live E2E Integration Gate**: Run `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

### Post-Implementation Gates
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests were left behind in the modified domains.
- [ ] **[NOK] Proxy Sunset & Consumer Migration**: Codebase-wide search/replace of old import paths & delete deprecated proxies.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified backend files:
  - [ ] @[backend_v2/models/enums.py]
  - [ ] @[backend_v2/models/v2_core.py]
  - [ ] @[backend_v2/database/interfaces.py]
  - [ ] @[backend_v2/database/repositories/components/prompt_block.py]
  - [ ] @[backend_v2/services/orchestrator/strategies/base.py]
  - [ ] @[backend_v2/services/orchestrator/strategies/logic.py]
  - [ ] @[backend_v2/services/orchestrator/strategies/llm.py]
  - [ ] @[backend_v2/services/orchestrator/strategies/registry.py]
  - [ ] @[backend_v2/services/orchestrator/engines/prompt_engine.py]
  - [ ] @[backend_v2/services/orchestrator/engines/__init__.py]
  - [ ] @[backend_v2/models/dtos/engine.py]
  - [ ] @[backend_v2/core/hook_registry.py]
  - [ ] @[backend_v2/services/orchestrator/engines/synthesis_engine.py]
  - [ ] @[backend_v2/services/orchestrator/dag_executor.py]
  - [ ] @[backend_v2/models/state.py]
  - [ ] @[backend_v2/settings.py]
  - [ ] @[backend_v2/models/dtos/source_extraction_schema.py]
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
| **REQ-147-22** | Create AST Guardrail suite `test_ast_engine_dispatch_guardrails.py` enforcing hook registration, zero procedural string routing in `DAGExecutor`, zero in-place `frozen_ctx.generated_schemas` mutations, mathematical set parity in `PromptBlockRepository`, and hook state immutability. | Section 5 (Step 4.1), Section 6 (TC-AST-01..05) | Phase 4, Step 1 | `@[backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py]` | [NOK] |
| **REQ-147-23** | Execute global unit test verification across all backend suites ensuring zero test failures, zero deprecation warnings, and >90% coverage. | Section 5 (Step 4.2), Section 7 (DoD) | Phase 4, Step 2 | All backend unit test files | [NOK] |
| **REQ-147-24** | Execute live E2E REST API integration test gate `test_integration_real_llm.py` with live foundational models. | Section 5 (Step 4.3), Section 7 (DoD) | Phase 4, Step 3 | `@[backend_v2/tests/integration/test_integration_real_llm.py]` | [NOK] |

# Session Handover Context

## Achieved
- **Phase 1 Implementation Complete & Committed**: Implemented and committed all 6 steps of Phase 1 (`01_phase1_tech_debt_dtos_repositories_and_strategy_registry.md`) in Git commit `feat(orchestrator): implement StepType enum, prompt block batch resolution, StrategyDependencies and static NodeStrategy registry (Phase 1)`.
- **Phase 1 Red Team Audit Passed (100%)**: Completed `/tier8-audit-plan` evaluation with 100% compliance across all 10 requirements (REQ-147-01..10), verifying 0 MyPy strict errors, 54 passing unit tests, and 0 supply chain violations. Generated red team audit report: `@[red_team_audit_phase1_engine_dispatch.md]`.
- **Phase 2 Implementation Complete & Committed**: Implemented and committed all 5 steps of Phase 2 (`02_phase2_engine_architecture_node_executor_and_dag_concurrency.md`) in Git commit `feat(orchestrator): implement NodeExecutor single-fetch DI, PromptEngine extraction and DAG concurrency synchronization (Phase 2)`:
  - **Step 1 (NodeExecutor Decomposition & DI)**: Refactored `NodeExecutor.__init__` in `@[backend_v2/services/orchestrator/dag_executor.py]` to accept `deps: StrategyDependencies` exclusively. Implemented `_resolve_execution_engine` to dynamically route between `TDAEngine`, `SynthesisEngine`, and `PromptEngine` based on prompt block categories, criteria IDs, and step configuration. Single-fetched criteria prompt blocks in `NodeExecutor.execute()` via `get_prompt_blocks_by_ids(criteria_ids, strict=True)` and delegated instantiation to `NodeStrategyFactory.create_strategy()`.
  - **Step 2 (Atomic Deduplicating Concurrency)**: Enclosed trace appends, `MCPAuditTrace` deduplication (by unique `id`), and `generated_schemas` extraction from `TraceEvent.metadata` inside `async with _update_lock:` in `DAGExecutor.run_step_wrapper()` to prevent race conditions during parallel branch execution.
  - **Step 3 (PromptEngine Extraction)**: Created `@[backend_v2/services/orchestrator/engines/prompt_engine.py]` implementing the `ExecutionEngine` protocol for structured non-matrix LLM tasks. Added `PROMPT_ENGINE_ERROR` and `SYNTHESIS_ENGINE_ERROR` to `ErrorCodes` in `@[backend_v2/exceptions.py]` and exported `PromptEngine` in `@[backend_v2/services/orchestrator/engines/__init__.py]`.
  - **Step 4 (LLMNodeStrategy Delegation & Schema Safety)**: Refactored `@[backend_v2/services/orchestrator/strategies/llm.py]` to consume pre-fetched `context.prompt_blocks`, eliminate `get_all_prompt_blocks()` table scans, delegate directly to `self._engine.execute()`, and emit generated schemas in `TraceEvent.metadata` without in-place `frozen_ctx` mutation. Updated `@[backend_v2/models/dtos/engine.py]` with nullable semaphore context management (`semaphore_cm`) and union-safe `synthesis_output: Annotated[dict[str, Any] | BaseModel | None, Field(default=None)]`.
  - **Step 5 (Unit Test Migrations & Concurrency Suites)**: Created `@[backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py]` (100% line coverage on `PromptEngine`) and `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_concurrency.py]` (verifying atomic MCP audit deduplication and parallel schema accumulation). Updated `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py]`, `@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]`, and `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]`.
- **Phase 2 Red Team Audit Passed (100%)**: Completed `/tier8-audit-plan` evaluation with 100% compliance across all 7 Phase 2 requirements (REQ-147-11..17). Verified 354 orchestrator tests passing (0 failures, 0 errors), 22 dedicated Phase 2 unit tests passing in 4.13s, 0 MyPy strict errors, and 0 supply chain violations. Generated red team audit report: `@[red_team_audit_phase2_engine_dispatch.md]`.
- **Phase 3 Implementation Complete & Quality Gate Passed (100%)**:
  - **Step 1 (Global Config & Schema Hardening)**: Defined `min_verifiable_text_length: Annotated[int, Field(...)] = 15` in `@[backend_v2/settings.py]`. Updated `@[backend_v2/models/dtos/source_extraction_schema.py]` to inherit `SourceVerificationInputsDTO` and `SourceExtractionResponseSchema` from `V2CoreBase` with `extra="forbid"`, supporting optional candidate text fields (`document_text`, `prior_analysis`, `text`, `document`).
  - **Step 2 (Hook & Service Hardening)**: Updated `@[backend_v2/hooks/source_verification_hook.py]` to return native typed `SourceVerificationResultDTO` directly in `state_delta["verified_sources"]` without premature `.model_dump(mode="json")`, short-circuit sub-threshold inputs (<15 chars) and empty/whitespace inputs to a zero-claims envelope, and pass `system_repo` to `SourceVerificationService`. Hardened `@[backend_v2/services/source_verification_service.py]` to consume `get_settings().min_verifiable_text_length`, eliminate `getattr` duck-typing, support `system_repo`, use `html.escape()` for prompt inputs, and use structured `ErrorCodes` logging (`SERVICE_DEPENDENCY_MISSING`, `FETCH_FAILED`). Verified `source_verification_hook` registration in `hook_registry` and export in `@[backend_v2/hooks/__init__.py]`.
  - **Step 3 (Comprehensive Unit Tests & Quality Gate)**: Created and updated 30 comprehensive unit tests across `@[backend_v2/tests/unit/hooks/test_source_verification_hook.py]`, `@[backend_v2/tests/unit/services/test_source_verification_service.py]`, and `@[backend_v2/tests/unit/models/dtos/test_source_extraction_schema.py]`, verifying boundary conditions, negative scenarios, XML injection defense, and DTO validation. Quality gate passed with 0 Ruff lint errors, 0 MyPy strict errors, and 95-100% test coverage.

## Learned
- **`LaxStepType` Enum Deserialization in Pydantic V2**: `LaxStepType = Annotated[StepType, Field(strict=False)]` on `Step.type` allows JSON strings from database seed files to coerce to `StepType` during DB seeding while enforcing strict enum typing elsewhere.
- **`StrategyDependencies` Structural Parity**: `StrategyDependencies` mirrors `HookDependencies` 1:1 with the 8 canonical repositories, allowing `LogicNodeStrategy` to forward dependencies to `hook_registry.execute` without intermediate glue.
- **`PromptBlockRepositoryImpl.get_prompt_blocks_by_ids` Set Parity**: Calculating `missing_ids = [bid for bid in unique_ids if bid not in found_ids]` ensures atomic fail-fast validation when blueprints reference missing prompt blocks.
- **In-Memory Purity & Union Coercion Defense**: Declaring `synthesis_output: Annotated[dict[str, Any] | BaseModel | None, Field(...)] = None` in `EngineExecutionResult` with `dict[str, Any]` ordered before `BaseModel` prevents Pydantic V2 from attempting to coerce raw dictionaries into fieldless `BaseModel` instances.
- **Semaphore Safety via `semaphore_cm`**: `EngineExecutionRequest.semaphore_cm` uses `contextlib.nullcontext()` when `semaphore` is `None`, ensuring all engines (`PromptEngine`, `SynthesisEngine`, `TDAEngine`) safely acquire locks via `async with request.semaphore_cm:` without `None` attribute errors in MyPy strict mode.
- **Lock-Bounded Concurrency in `DAGExecutor`**: Trace appends, `mcp_tool_audit` deduplicating merging, and `generated_schemas` accumulation must be strictly synchronized inside `async with _update_lock:` using `.model_copy(update=...)` with shallow dict updates to avoid double-serialization CPU overhead while preventing race conditions.
- **Dynamic Engine Resolution Decoupling**: `NodeExecutor._resolve_execution_engine` dynamically chooses between `TDAEngine` (when criteria contains `PromptBlockCategory.MATRIX`), `SynthesisEngine` (when criteria contains synthesis blocks or `model_strategy == "synthesis"`), and `PromptEngine` (for structured non-matrix steps), completely removing coupling to legacy string flags.
- **Source Verification SSOT Invariant**: `SourceVerificationResultDTO` is the strict Single Source of Truth (`models/domain/source_verification.py`) and must be returned natively in `HookResult.state_delta["verified_sources"]` without in-memory `.model_dump(mode="json")`. Sub-threshold inputs (< `settings.min_verifiable_text_length`) must return a valid zero-claims envelope with `total_claims=0`, `verified_count=0`, `hallucination_count=0`, `claims=[]`, and ISO timestamp.
- **Hook State In-Memory Safety & Mocking**: `HookState(inputs: dict[str, Any])` enforces `strict=True`. In unit tests asserting runtime defense against malformed inputs (non-dict primitives or unauthorized DTOs), `object.__setattr__(state, "inputs", ...)` on constructed `HookState` allows testing downstream hook error-handling branches cleanly without mutating frozen definitions.

## Codebase Physical Anchor Reference Map
- `NodeExecutor`: `@[backend_v2/services/orchestrator/dag_executor.py#L119-L285]`
- `DAGExecutor`: `@[backend_v2/services/orchestrator/dag_executor.py#L287-L720]`
- `PromptEngine`: `@[backend_v2/services/orchestrator/engines/prompt_engine.py#L1-L73]`
- `SynthesisEngine`: `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L1-L220]`
- `TDAEngine`: `@[backend_v2/services/orchestrator/engines/tda_engine.py#L1-L210]`
- `LLMNodeStrategy`: `@[backend_v2/services/orchestrator/strategies/llm.py#L58-L830]`
- `NodeStrategyFactory`: `@[backend_v2/services/orchestrator/strategies/registry.py#L1-L60]`
- `EngineExecutionRequest` / `EngineExecutionResult`: `@[backend_v2/models/dtos/engine.py#L85-L149]`
- `source_verification_hook`: `@[backend_v2/hooks/source_verification_hook.py#L1-L98]`
- `SourceVerificationService`: `@[backend_v2/services/source_verification_service.py#L1-L282]`
- `SourceVerificationInputsDTO`: `@[backend_v2/models/dtos/source_extraction_schema.py#L1-L42]`
- `SourceVerificationResultDTO`: `@[backend_v2/models/domain/source_verification.py#L61-L79]`
- `Settings.min_verifiable_text_length`: `@[backend_v2/settings.py#L203-L205]`

## Unit Test Coverage & Verification Map
- `@[backend_v2/tests/unit/hooks/test_source_verification_hook.py]`: 13 tests (Hook registration, empty/whitespace short-circuit, sub-threshold text, multi-key synthesis, non-string validation exceptions, DTO inputs, service error propagation)
- `@[backend_v2/tests/unit/services/test_source_verification_service.py]`: 13 tests (Claim extraction, search fallback, full verification, short text zero-claims envelope, XML injection defense, uninitialized client exceptions, lazy loading)
- `@[backend_v2/tests/unit/models/dtos/test_source_extraction_schema.py]`: 4 tests (Schema instantiation, optional field defaults, `extra="forbid"` rejection)

## Remaining Work
- Audit Phase 3 Plan (`03_placeholder_phase3_ghost_execution_elimination_and_hook_hardening.md`): Audit (`/tier8-audit-plan`).
- Execute Phase 4 Plan (`04_placeholder_phase4_ast_guardrails_unit_test_suites_and_e2e_gate.md`): Research, Execution, and Audit.
- Run Post-Implementation Hardening & Final Epic Audit (`/tier8-audit-epic`).

## Next Command
`/tier8-audit-plan @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/03_placeholder_phase3_ghost_execution_elimination_and_hook_hardening.md] @[docs/epic/EPIC_147_tracker.md]`


