# EPIC 147 Tracker: Engine Dispatch and Cognitive Grounding Resilience

**Epic:** @[docs/epic/EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience.md]
**Task Directory:** [NEW] @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience]

```xml
<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <ki>@[ki_god_code_prevention.md]</ki>
  <ki>@[ki_polymorphic_rule_routing.md]</ki>
  <ki>@[ki_execution_engine_protocol.md]</ki>
  <ki>@[ki_python_314_concurrency_strictness.md]</ki>
  <ki>@[ki_global_config_sovereignty.md]</ki>
  <ki>@[ki_ast_guardrail_testing.md]</ki>
  <ki>@[ki_ai_testing_standards.md]</ki>
  <ki>@[ki_llm_extraction_architecture.md]</ki>
</required_context_rules>
```

---

## Phase Execution Status

### Phase 1: Pre-Implementation Technical Debt Cleanups & Seed Vault Sanitization

**Plan:** [NEW] @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/01_phase1_seed_vault_and_mock_debt.md]

- [ ] **Red-Teaming:** `/tier0-research-plan` [NEW] `@[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/01_phase1_seed_vault_and_mock_debt.md]` `@[docs/epic/EPIC_147_tracker.md]`
- [ ] **Execution:** `/tier2-execute` [NEW] `@[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/01_phase1_seed_vault_and_mock_debt.md]` `@[docs/epic/EPIC_147_tracker.md]`
  - [ ] Step 0: Strategic Alignment Check & Seed Backup — Create timestamped backup `backend_v2/seed/backups/seed_data_<timestamp>.json`
  - [ ] Step 1: Prompt Anchor Sanitization — Prune duplicate `EPISTEMIC ANCHOR:` text from `PromptBlock.ai_description` in `seed_data.json` while retaining `ROLE:`, `OBJECTIVE:`, `MANDATE:` headers
  - [ ] Step 2: Database Re-seed & Pre-flight Verification — Run `uv run python backend_v2/seed/run_seed.py local`
  - [ ] Step 3: Test Mock Debt Remediation — Fix `@patch("...tda_engine.get_settings")` in `test_llm_cost_tracking.py`

### Phase 2: DTOs, Repository Interfaces & StrategyDependencies Container

**Plan:** [NEW] @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/02_phase2_interfaces_and_dependencies_container.md]

- [ ] **Red-Teaming:** `/tier0-research-plan` [NEW] `@[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/02_phase2_interfaces_and_dependencies_container.md]` `@[docs/epic/EPIC_147_tracker.md]`
- [ ] **Execution:** `/tier2-execute` [NEW] `@[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/02_phase2_interfaces_and_dependencies_container.md]` `@[docs/epic/EPIC_147_tracker.md]`
  - [ ] Step 1: `StepType` Canonical Enum — Update `models/enums.py` with `StepType(StrEnum)` and apply to `Step.type` in `models/v2_core.py`
  - [ ] Step 2: Batch PromptBlock Fetching — Add `get_prompt_blocks_by_ids` with strict mathematical set validation in `IPromptBlockRepository` and `PromptBlockRepositoryImpl`
  - [ ] Step 3: `StrategyDependencies` Container — Introduce `@dataclass(frozen=True) class StrategyDependencies` and update `StrategyContext.prompt_blocks` in `strategies/base.py`
  - [ ] Step 4: Unit Testing & Boundary Verification — Add tests in `test_prompt_block_batch.py`

### Phase 3: Engine Architecture, PromptEngine Extraction & Strategy Registry

**Plan:** [NEW] @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/03_phase3_prompt_engine_and_strategy_registry.md]

- [ ] **Red-Teaming:** `/tier0-research-plan` [NEW] `@[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/03_phase3_prompt_engine_and_strategy_registry.md]` `@[docs/epic/EPIC_147_tracker.md]`
- [ ] **Execution:** `/tier2-execute` [NEW] `@[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/03_phase3_prompt_engine_and_strategy_registry.md]` `@[docs/epic/EPIC_147_tracker.md]`
  - [ ] Step 1: `PromptEngine` Extraction — Implement `PromptEngine` in `services/orchestrator/engines/prompt_engine.py`
  - [ ] Step 2: `NodeStrategyFactory` & `NODE_STRATEGY_REGISTRY` — Create dynamic polymorphic strategy router in `strategies/registry.py`
  - [ ] Step 3: `NodeExecutor` Decomposition — Refactor `dag_executor.py` with `_resolve_execution_engine` and single-fetch prompt block injection
  - [ ] Step 4: `LLMNodeStrategy` Table Scan Elimination — Eradicate `get_all_prompt_blocks()` calls and bind directly to `ctx.prompt_blocks`

### Phase 4: Concurrency Hardening & Theory Grounding XML Formatting

**Plan:** [NEW] @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/04_phase4_concurrency_hardening_and_theory_grounding.md]

- [ ] **Red-Teaming:** `/tier0-research-plan` [NEW] `@[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/04_phase4_concurrency_hardening_and_theory_grounding.md]` `@[docs/epic/EPIC_147_tracker.md]`
- [ ] **Execution:** `/tier2-execute` [NEW] `@[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/04_phase4_concurrency_hardening_and_theory_grounding.md]` `@[docs/epic/EPIC_147_tracker.md]`
  - [ ] Step 1: Thread-Safe Atomic Accumulator — Protect `mcp_tool_audit`, `generated_schemas`, `execution_trace` in `dag_executor.py` inside `async with _update_lock:`
  - [ ] Step 2: `FrozenContext` Immutability Protection — Eliminate in-place mutations of `frozen_ctx.generated_schemas` from `LLMNodeStrategy`
  - [ ] Step 3: `MatrixSensorPromptBuilder` XML Reformatting — Reformat structured `theory_grounding` into `<theory_context>` XML blocks and omit raw URLs

### Phase 5: Hook Hardening, Verification & E2E Integration Gate

**Plan:** [NEW] @[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/05_phase5_hook_hardening_and_e2e_verification.md]

- [ ] **Red-Teaming:** `/tier0-research-plan` [NEW] `@[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/05_phase5_hook_hardening_and_e2e_verification.md]` `@[docs/epic/EPIC_147_tracker.md]`
- [ ] **Execution:** `/tier2-execute` [NEW] `@[docs/epic/tasks_EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience/05_phase5_hook_hardening_and_e2e_verification.md]` `@[docs/epic/EPIC_147_tracker.md]`
  - [ ] Step 1: `source_verification_hook.py` Hardening — Implement DTOs, empty input short-circuit, HTML escaping, and register with `hook_registry`
  - [ ] Step 2: AST Guardrail & Unit Test Suite — Build `test_ast_engine_dispatch_guardrails.py` and run full unit test matrix
  - [ ] Step 3: Global Universal Quality Gate — Execute `uv run python scripts/backend_audit_loop.py backend_v2/ --test`
  - [ ] Step 4: Live E2E REST API Verification Gate — Execute `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
