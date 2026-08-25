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
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/01_phase1_tech_debt_dtos_repositories_and_strategy_registry.md] @[docs/epic/EPIC_147_tracker.md]`

### Phase 2: Engine Architecture, NodeExecutor Decomposition, Single-Fetch DI & DAG Concurrency Hardening
**Plan:** @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/02_phase2_engine_architecture_node_executor_and_dag_concurrency.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/02_phase2_engine_architecture_node_executor_and_dag_concurrency.md] @[docs/epic/EPIC_147_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/02_phase2_engine_architecture_node_executor_and_dag_concurrency.md] @[docs/epic/EPIC_147_tracker.md]`
  - [ ] Step 1: Decompose NodeExecutor & Single-Fetch DI in dag_executor.py
  - [ ] Step 2: Atomic Deduplicating State Accumulation under _update_lock in DAGExecutor
  - [ ] Step 3: Extract PromptEngine
  - [ ] Step 4: Refactor LLMNodeStrategy to Delegate to ExecutionEngine
  - [ ] Step 5: Atomic Unit Test Migration for NodeExecutor & DAGExecutor
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/02_phase2_engine_architecture_node_executor_and_dag_concurrency.md] @[docs/epic/EPIC_147_tracker.md]`

### Phase 3: Ghost Execution Elimination & Source Verification Hook Hardening
**Plan:** @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/03_placeholder_phase3_ghost_execution_elimination_and_hook_hardening.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/03_placeholder_phase3_ghost_execution_elimination_and_hook_hardening.md] @[docs/epic/EPIC_147_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/03_placeholder_phase3_ghost_execution_elimination_and_hook_hardening.md] @[docs/epic/EPIC_147_tracker.md]`
  - [ ] Step 1: Source Extraction Schema & Global Config Sovereignty
  - [ ] Step 2: Hook & Service Hardening
  - [ ] Step 3: Unit Testing for Source Verification Hook & Service
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
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
| **REQ-147-01** | Remove stale mock patch `@patch("...tda_engine.get_settings")` in `test_llm_cost_tracking.py` to prevent AttributeError during test collection. | Section 3 (Item 1), Section 5 (Step 1.1) | Phase 1, Step 1 | `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py]` | [NOK] |
| **REQ-147-02** | Replace silent `except Exception: pass` blocks in `llm.py` with explicit `AppException(RESOURCE_NOT_FOUND / VALIDATION_FAILED)` and structured RFC 7807 logging. | Section 3 (Item 4), Section 5 (Step 1.1) | Phase 1, Step 1 | `@[backend_v2/services/orchestrator/strategies/llm.py]` | [NOK] |
| **REQ-147-03** | Replace raw string comparison `b.category_id == "matrix"` with `PromptBlockCategory.MATRIX` enum comparisons in `llm.py`. | Section 3 (Item 7), Section 5 (Step 1.1) | Phase 1, Step 1 | `@[backend_v2/services/orchestrator/strategies/llm.py]` | [NOK] |
| **REQ-147-04** | Eliminate `getattr`/`hasattr` duck typing and magic defaults (`expected_sdui_type="grid"`) in `llm.py`. | Section 3 (Items 5, 6), Section 5 (Step 1.1) | Phase 1, Step 1 | `@[backend_v2/services/orchestrator/strategies/llm.py]` | [NOK] |
| **REQ-147-05** | Declare canonical `StepType(StrEnum)` with `LLM = "llm"` and `LOGIC = "logic"` in `enums.py` and update `Step.type` in `v2_core.py`. | Section 3 (Item 13), Section 5 (Step 1.2) | Phase 1, Step 2 | `@[backend_v2/models/enums.py]`, `@[backend_v2/models/v2_core.py]` | [NOK] |
| **REQ-147-06** | Declare `get_prompt_blocks_by_ids` in `IPromptBlockRepository` and implement in `PromptBlockRepositoryImpl` with strict mathematical set difference validation (`unique_requested - found_ids`) raising `AppException(RESOURCE_NOT_FOUND)`. | Section 3 (Item 18), Section 5 (Step 1.3) | Phase 1, Step 3 | `@[backend_v2/database/interfaces.py]`, `@[backend_v2/database/repositories/components/prompt_block.py]` | [NOK] |
| **REQ-147-07** | Define `@dataclass(frozen=True) StrategyDependencies` and update `StrategyContext` with `prompt_blocks: list[PromptBlock]` in `base.py`. | Section 3 (Item 8), Section 5 (Step 1.4) | Phase 1, Step 4 | `@[backend_v2/services/orchestrator/strategies/base.py]` | [NOK] |
| **REQ-147-08** | Refactor `NodeStrategy` and `LogicNodeStrategy` constructors to accept `deps: StrategyDependencies` and remove 10 loose repository parameters. | Section 3 (Item 8), Section 5 (Step 1.4) | Phase 1, Step 4 | `@[backend_v2/services/orchestrator/strategies/base.py]`, `@[backend_v2/services/orchestrator/strategies/logic.py]` | [NOK] |
| **REQ-147-09** | Implement static `NODE_STRATEGY_REGISTRY` mapping `StepType` to `StrategyBuilder` and `NodeStrategyFactory.create_strategy` in `registry.py`. | Section 3 (Item 12), Section 5 (Step 1.5) | Phase 1, Step 5 | `@[backend_v2/services/orchestrator/strategies/registry.py]` | [NOK] |
| **REQ-147-10** | Migrate Phase 1 unit test fixtures (`test_logic.py`, `test_llm_cost_tracking.py`, `test_prompt_block.py`, `test_node_strategy_registry.py`) to typed Pydantic V2 models and `StrategyDependencies`. | Section 3 (Items 19, 21), Section 5 (Step 1.6) | Phase 1, Step 6 | `@[backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py]`, `@[backend_v2/tests/unit/test_logic.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py]`, `@[backend_v2/tests/unit/database/repositories/components/test_prompt_block.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_node_strategy_registry.py]` | [NOK] |
| **REQ-147-11** | Update `NodeExecutor` constructor to accept `deps: StrategyDependencies`, implement `_resolve_execution_engine` decoupled from `model_strategy == "synthesis"`, single-fetch criteria blocks, and delegate to `NodeStrategyFactory`. | Section 3 (Items 8, 12, 20), Section 5 (Step 2.1) | Phase 2, Step 1 | `@[backend_v2/services/orchestrator/dag_executor.py]` | [NOK] |
| **REQ-147-12** | Synchronize DAG trace append loop inside `_update_lock` and implement atomic deduplicating accumulation of `MCPAuditTrace` and `generated_schemas` under `_update_lock` in `DAGExecutor`. | Section 3 (Items 2, 11), Section 5 (Step 2.2) | Phase 2, Step 2 | `@[backend_v2/services/orchestrator/dag_executor.py]`, `@[backend_v2/models/state.py]` | [NOK] |
| **REQ-147-13** | Extract `PromptEngine` implementing `ExecutionEngine` protocol for structured non-matrix LLM tasks in `prompt_engine.py` and export in `engines/__init__.py`. | Section 3 (Item 9), Section 5 (Step 2.3) | Phase 2, Step 3 | `@[backend_v2/services/orchestrator/engines/prompt_engine.py]`, `@[backend_v2/services/orchestrator/engines/__init__.py]` | [NOK] |
| **REQ-147-14** | Refactor `LLMNodeStrategy` to accept `(deps: StrategyDependencies, engine: ExecutionEngine)`, consume injected `context.prompt_blocks`, eliminate `get_all_prompt_blocks()`, and delegate to `engine.execute()`. | Section 3 (Items 8, 10), Section 5 (Step 2.4) | Phase 2, Step 4 | `@[backend_v2/services/orchestrator/strategies/llm.py]` | [NOK] |
| **REQ-147-15** | Eliminate in-place mutation of `frozen_ctx.generated_schemas` in `LLMNodeStrategy` and propagate schemas via `TraceEvent.metadata["generated_schema"]`. | Section 3 (Item 3), Section 5 (Step 2.4) | Phase 2, Step 4 | `@[backend_v2/services/orchestrator/strategies/llm.py]` | [NOK] |
| **REQ-147-16** | Update `EngineExecutionResult.synthesis_output` to `BaseModel | None`, update `HookState.inputs` and `HookResult.state_delta` in `hook_registry.py` to `BaseModel | dict[str, Any]`, and update `SynthesisEngine` to preserve typed models, eliminating raw `final_dict` and premature `.model_dump()` in-memory. | Section 3 (Items 111, 112, 113, 114), Section 5 (Step 2.4) | Phase 2, Step 4 | `@[backend_v2/models/dtos/engine.py]`, `@[backend_v2/core/hook_registry.py]`, `@[backend_v2/services/orchestrator/engines/synthesis_engine.py]`, `@[backend_v2/services/orchestrator/strategies/llm.py]` | [NOK] |
| **REQ-147-17** | Migrate `test_dag_executor.py` and `test_llm.py` to `StrategyDependencies` and typed models, and create `test_prompt_engine.py` and `test_dag_executor_mcp_concurrency.py`. | Section 3 (Items 19, 21), Section 5 (Step 2.5) | Phase 2, Step 5 | `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]`, `@[backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_concurrency.py]` | [NOK] |
| **REQ-147-18** | Define `min_verifiable_text_length: int = 15` in `settings.py` and declare `SourceVerificationInputsDTO` in `source_extraction_schema.py`. | Section 3 (Items 14), Section 5 (Step 3.1) | Phase 3, Step 1 | `@[backend_v2/settings.py]`, `@[backend_v2/models/dtos/source_extraction_schema.py]` | [NOK] |
| **REQ-147-19** | Attach `@hook_registry.register("source_verification")` to `source_verification_hook.py`, short-circuit empty/whitespace/sub-threshold inputs returning complete zero-claims `SourceVerificationResultDTO` envelope with native typed objects directly, and export in `hooks/__init__.py`. | Section 3 (Items 14, 16), Section 5 (Step 3.2) | Phase 3, Step 2 | `@[backend_v2/hooks/source_verification_hook.py]`, `@[backend_v2/hooks/__init__.py]` | [NOK] |
| **REQ-147-20** | Replace hardcoded mock LLM credentials in `SourceVerificationService` with `LLMClient.from_strategy("fast", ...)`, declare static module prompt constants, and sanitize XML injection with `html.escape()`. | Section 3 (Items 15, 17), Section 5 (Step 3.2) | Phase 3, Step 2 | `@[backend_v2/services/source_verification_service.py]` | [NOK] |
| **REQ-147-21** | Create comprehensive unit tests for `SourceVerificationHook` and `SourceVerificationService` covering short-circuits, zero-claims envelope, sub-threshold length, and XML injection defense. | Section 5 (Step 3.3), Section 6 (TC-SV-01..06) | Phase 3, Step 3 | `@[backend_v2/tests/unit/hooks/test_source_verification_hook.py]`, `@[backend_v2/tests/unit/services/test_source_verification_service.py]` | [NOK] |
| **REQ-147-22** | Create AST Guardrail suite `test_ast_engine_dispatch_guardrails.py` enforcing hook registration, zero procedural string routing in `DAGExecutor`, zero in-place `frozen_ctx.generated_schemas` mutations, mathematical set parity in `PromptBlockRepository`, and hook state immutability. | Section 5 (Step 4.1), Section 6 (TC-AST-01..05) | Phase 4, Step 1 | `@[backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py]` | [NOK] |
| **REQ-147-23** | Execute global unit test verification across all backend suites ensuring zero test failures, zero deprecation warnings, and >90% coverage. | Section 5 (Step 4.2), Section 7 (DoD) | Phase 4, Step 2 | All backend unit test files | [NOK] |
| **REQ-147-24** | Execute live E2E REST API integration test gate `test_integration_real_llm.py` with live foundational models. | Section 5 (Step 4.3), Section 7 (DoD) | Phase 4, Step 3 | `@[backend_v2/tests/integration/test_integration_real_llm.py]` | [NOK] |

# Session Handover Context

## Achieved
- **System 2 Research & Red-Teaming Complete**: Completed exhaustive Tier 0 analysis and red-teaming on Phase 1 implementation plan (`01_phase1_tech_debt_dtos_repositories_and_strategy_registry.md`). Marked Phase 1 Red-Teaming `[x] **[OK]**`.
- **Mathematical Boundary Verification**: Ran `scripts/audit_planner_output.py --epic docs/epic/EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience.md --plan-dir docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience` verifying 100% boundary preservation across all 35 line bounds, 40 target files, 184 Python AST bounds, 10 Knowledge Items, and rule imports.
- **SSOT Interface Synchronization**: Hardened `StrategyDependencies` across the Epic (`EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience.md#L301-L336`) and Plan (`01_phase1_...md#L164-L204`) to map 1:1 to Quorum's 8 canonical repository interfaces in `interfaces.py` (`IExecutionRepository`, `IWorkflowRepository`, `IComponentRepository`, `IPromptBlockRepository`, `IOutputProfileRepository`, `IIdentityRepository`, `IAuditRepository`, `ISystemRepository`), `prompt_compiler: Any`, and `arq_pool: Any | None = None`.
- **Model Invariant Protection**: Preserved `StrategyContext` as a strict Pydantic `BaseModel` (`ConfigDict(arbitrary_types_allowed=True, frozen=True, extra="forbid")`) with `prompt_blocks: list[PromptBlock] = Field(default_factory=list)`, preventing breaks in `DAGExecutor` and strategy consumers.
- **Baseline Test Validation**: Executed dry runs:
  - `test_logic.py` & `test_prompt_block.py`: 11 passed in 1.23s.
  - `test_llm_cost_tracking.py`: 1 failed with expected `AttributeError: tda_engine does not have get_settings` (reproducing REQ-147-01 root cause).

## Learned
- **Workflow & Step Repository Hierarchy**: In Quorum V2 (`interfaces.py`), step CRUD/query operations are encapsulated inside `IWorkflowRepository` (`get_step_by_id`, `get_step`, `get_all_steps`). There is no standalone `IStepRepository`.
- **Quota Assertion Dependency Chain**: `NodeStrategy.assert_quota` instantiates `UsageService(self.deps.identity_repo, self.deps.audit_repo)`. Both repositories are mandatory in `StrategyDependencies`.
- **HookDependencies Parity**: `HookDependencies` requires exactly the 8 canonical repositories (`exec_repo`, `workflow_repo`, `comp_repo`, `prompt_block_repo`, `output_profile_repo`, `identity_repo`, `audit_repo`, `system_repo`). Having `StrategyDependencies` mirror these allows zero-glue delegation in `LogicNodeStrategy`.
- **PromptBlock Batch Hydration**: `PromptBlockRepositoryImpl` uses `PromptBlockAdapter.validate_python(doc, strict=False)` and `self.driver.query("prompt_blocks", filters=[Filter(field="id", operator="in", value=unique_ids)])`. Strict validation requires calculating `missing_ids = [bid for bid in unique_ids if bid not in found_ids]`, logging with `ErrorCodes.RESOURCE_NOT_FOUND`, and raising `AppException(status_code=404)`.
- **Constructor Bridge for Phase 1**: `LLMNodeStrategy(deps: StrategyDependencies, engine: ExecutionEngine | None = None)` stores `self._engine = engine` in Phase 1, allowing `NodeStrategyFactory` to instantiate it cleanly ahead of Phase 2 engine delegation.

## Phase 1 Execution Step Sequence (Ready for /tier2-execute)
1. **Step 1: Scoped Technical Debt Cleanup**:
   - `test_llm_cost_tracking.py`: Remove line 60 `@patch("...tda_engine.get_settings")` and `mock_get_settings` parameter.
   - `llm.py`: Replace `b.category_id == "matrix"` with `PromptBlockCategory.MATRIX`, remove silent `except Exception: pass`, and eliminate `getattr(step, ...)` duck typing.
2. **Step 2: Canonical StepType Enum & Schema Update**:
   - `enums.py`: Add `StepType(StrEnum)` (`LLM = "llm"`, `LOGIC = "logic"`).
   - `v2_core.py`: Update `Step.type` field to `StepType = Field(default=StepType.LLM)`.
3. **Step 3: Fail-Fast PromptBlock Batch Resolution in Repository**:
   - `interfaces.py`: Add `get_prompt_blocks_by_ids` to `IPromptBlockRepository`.
   - `prompt_block.py`: Implement `get_prompt_blocks_by_ids` with deduplication, `$in` query, set difference validation, and structured RFC 7807 error logging.
4. **Step 4: Define StrategyDependencies Container & Update Strategy Base**:
   - `base.py`: Update `StrategyContext` and define `@dataclass(frozen=True) StrategyDependencies`. Update `NodeStrategy(deps: StrategyDependencies)`.
   - `logic.py`: Update `LogicNodeStrategy(deps: StrategyDependencies)`.
   - `llm.py`: Update `LLMNodeStrategy(deps: StrategyDependencies, engine: ExecutionEngine | None = None)`.
5. **Step 5: Static NODE_STRATEGY_REGISTRY & NodeStrategyFactory**:
   - Create `backend_v2/services/orchestrator/strategies/registry.py` with `StrategyBuilder`, `_build_logic_strategy`, `_build_llm_strategy`, `NODE_STRATEGY_REGISTRY`, and `NodeStrategyFactory`.
6. **Step 6: Atomic Unit Test Migration for Phase 1**:
   - Update `test_logic.py`, `test_llm_cost_tracking.py`, add `test_prompt_block.py` batch test cases, and create `test_node_strategy_registry.py`.

## Remaining Work
- Execute Phase 1 implementation via `/tier2-execute`.
- Execute Phase 1 Plan Audit (`/tier8-audit-plan`).
- Proceed sequentially through Phase 2 (`02_phase2_...md`), Phase 3 (`03_placeholder_...md`), and Phase 4 (`04_placeholder_...md`), followed by Post-Implementation Hardening and the Final Epic Audit.

## Resume Command
`/tier2-execute @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/01_phase1_tech_debt_dtos_repositories_and_strategy_registry.md] @[docs/epic/EPIC_147_tracker.md]`
