# Epic 150 Tracker: Zero Permissive Typing Lockdown

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
  <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
</required_context_rules>

## Phase Execution Status

### Phase 1: LLM Prompt & Adapter Ecosystem Atomic Lockdown
- **Plan:** @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/01_phase1a_llm_models_and_prompt_dto.md]
- **Plan (Sub-Phase 1B):** @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/02_phase1b_llm_adapters_and_provider_pipeline.md]
- **Plan (Sub-Phase 1C):** @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/03_phase1c_coupled_tests_and_seed_validation.md]
- [x] **[OK] Red-Teaming (Sub-Phase 1A):** `/tier0-research-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/01_phase1a_llm_models_and_prompt_dto.md] @[docs/epic/EPIC_150_tracker.md]`
- [x] **[OK] Execution (Sub-Phase 1A):** `/tier2-execute @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/01_phase1a_llm_models_and_prompt_dto.md] @[docs/epic/EPIC_150_tracker.md]`
  - [x] Step 0: Strategic Alignment Check & Pre-Implementation Cleanups
  - [x] Step 1: Define DTO Models in LLM & Prompt Modules
  - [x] Step 2: Update Caching Service & Utils
  - [x] Step 3: Central Test Factories & Test Migration
- [x] **[OK] Audit (Sub-Phase 1A):** `/tier8-audit-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/01_phase1a_llm_models_and_prompt_dto.md] @[docs/epic/EPIC_150_tracker.md]` (Verified via Sub-Phase 1B test gate)
- [x] **[OK] Red-Teaming (Sub-Phase 1B):** `/tier0-research-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/02_phase1b_llm_adapters_and_provider_pipeline.md] @[docs/epic/EPIC_150_tracker.md]`
- [x] **[OK] Execution (Sub-Phase 1B):** `/tier2-execute @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/02_phase1b_llm_adapters_and_provider_pipeline.md] @[docs/epic/EPIC_150_tracker.md]`
  - [x] Step 0: Strategic Alignment Check & Pre-Implementation Cleanups
  - [x] Step 1: Modernize Base Adapter & Provider Infrastructure
  - [x] Step 2: Modernize Provider Adapters
  - [x] Step 3: Migrate Adapter Test Suites
- [x] **[OK] Audit (Sub-Phase 1B):** `/tier8-audit-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/02_phase1b_llm_adapters_and_provider_pipeline.md] @[docs/epic/EPIC_150_tracker.md]`
- [x] **[OK] Execution (Sub-Phase 1C):** `/tier2-execute @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/03_phase1c_coupled_tests_and_seed_validation.md] @[docs/epic/EPIC_150_tracker.md]` (Atomically committed: `b4c19250`)
  - [x] Step 0: Strategic Alignment Check & Pre-Implementation Cleanups
  - [x] Step 1: Harden Seed Registry & Implement Two-Phase Seeder Validation
  - [x] Step 2: Migrate Prompt Context DTO & Coupled MCP / Executor Test Suites
  - [x] Step 3: Migrate Coupled Prompt Builder, Hook & Integration Test Suites
- [x] **[OK] Audit (Sub-Phase 1C):** `/tier8-audit-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/03_phase1c_coupled_tests_and_seed_validation.md] @[docs/epic/EPIC_150_tracker.md]` (Remediations completed: sliding_window_linker DTOs, duplicate test_execute_chat_task cleanup, test_finops_telemetry unskipping, docstrings & line length compliance)

### Phase 2: Service & Studio Layer DTO Elimination
- **Plan:** @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/04_phase2a_service_and_progress_dto.md]
- **Plan (Sub-Phase 2B):** @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/05_phase2b_studio_and_seed_models.md]
- [x] **[OK] Red-Teaming (Sub-Phase 2A):** `/tier0-research-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/04_phase2a_service_and_progress_dto.md] @[docs/epic/EPIC_150_tracker.md]`
- [x] **[OK] Execution (Sub-Phase 2A):** `/tier2-execute @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/04_phase2a_service_and_progress_dto.md] @[docs/epic/EPIC_150_tracker.md]`
  - [x] Step 0: Strategic Alignment Check
  - [x] Step 1: Pre-Implementation Cleanups
  - [x] Step 2: Modernize Progress State & Tracker Interfaces
  - [x] Step 3: Modernize Task Registry & Unit Tests
- [x] **[OK] Audit (Sub-Phase 2A):** `/tier8-audit-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/04_phase2a_service_and_progress_dto.md] @[docs/epic/EPIC_150_tracker.md]`
- [x] **[OK] Red-Teaming (Sub-Phase 2B):** `/tier0-research-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/05_phase2b_studio_and_seed_models.md] @[docs/epic/EPIC_150_tracker.md]`
- [x] **[OK] Execution (Sub-Phase 2B):** `/tier2-execute @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/05_phase2b_studio_and_seed_models.md] @[docs/epic/EPIC_150_tracker.md]`
  - [x] Step 0: Strategic Alignment Check & Pre-Implementation Cleanups
  - [x] Step 1: Purge Obsolete Seed Schemas & Define Provider Extra Params
  - [x] Step 2: Modernize Studio Services & Routers
  - [x] Step 3: Surgical Hardening of Worker & Blueprint
- [x] **[OK] Audit (Sub-Phase 2B):** `/tier8-audit-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/05_phase2b_studio_and_seed_models.md] @[docs/epic/EPIC_150_tracker.md]`

### Phase 3: Hooks, Orchestrator & Repository Suppression Eradication
- **Plan:** @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/06_phase3a_hooks_suppression_eradication.md]
- **Plan (Sub-Phase 3B):** @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/07_phase3b_orchestrator_suppression_eradication.md]
- **Plan (Sub-Phase 3C):** @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/08_phase3c_repositories_and_domain_models.md]
- [x] **[OK] Red-Teaming (Sub-Phase 3A):** `/tier0-research-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/06_phase3a_hooks_suppression_eradication.md] @[docs/epic/EPIC_150_tracker.md]`
- [x] **[OK] Execution (Sub-Phase 3A):** `/tier2-execute @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/06_phase3a_hooks_suppression_eradication.md] @[docs/epic/EPIC_150_tracker.md]`
  - [x] Step 0: Strategic Alignment Check & Pre-Implementation Cleanups
  - [x] Step 1: Harden Scoring Hooks
  - [x] Step 2: Harden Processing, Validation & Telemetry Hooks
  - [x] Step 3: Comprehensive Test Expansion & AST Guardrail Validation
- [x] **[OK] Audit (Sub-Phase 3A):** `/tier8-audit-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/06_phase3a_hooks_suppression_eradication.md] @[docs/epic/EPIC_150_tracker.md]` (Subsystem coverage 90.25%, global backend 93.57%, 0 AST violations)
- [ ] **[NOK] Red-Teaming (Sub-Phase 3B):** `/tier0-research-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/07_phase3b_orchestrator_suppression_eradication.md] @[docs/epic/EPIC_150_tracker.md]`
- [ ] **[NOK] Execution (Sub-Phase 3B):** `/tier2-execute @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/07_phase3b_orchestrator_suppression_eradication.md] @[docs/epic/EPIC_150_tracker.md]`
  - [ ] Step 0: Strategic Alignment Check
  - [ ] Step 1: Harden Orchestrator Executors & Compilers
  - [ ] Step 2: Harden Strategies & Pipeline Services
- [ ] **[NOK] Audit (Sub-Phase 3B):** `/tier8-audit-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/07_phase3b_orchestrator_suppression_eradication.md] @[docs/epic/EPIC_150_tracker.md]`
- [ ] **[NOK] Red-Teaming (Sub-Phase 3C):** `/tier0-research-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/08_phase3c_repositories_and_domain_models.md] @[docs/epic/EPIC_150_tracker.md]`
- [ ] **[NOK] Execution (Sub-Phase 3C):** `/tier2-execute @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/08_phase3c_repositories_and_domain_models.md] @[docs/epic/EPIC_150_tracker.md]`
  - [ ] Step 0: Strategic Alignment Check
  - [ ] Step 1: Harden Repository Reconstitution Layer
  - [ ] Step 2: Harden Domain Models & DTOs
- [ ] **[NOK] Audit (Sub-Phase 3C):** `/tier8-audit-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/08_phase3c_repositories_and_domain_models.md] @[docs/epic/EPIC_150_tracker.md]`

### Phase 4: AST Hardening, Knowledge Base & Architectural Governance Lockdown
- **Plan:** @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/09_phase4_ast_hardening_and_governance.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/09_phase4_ast_hardening_and_governance.md] @[docs/epic/EPIC_150_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/09_phase4_ast_hardening_and_governance.md] @[docs/epic/EPIC_150_tracker.md]`
  - [ ] Step 0: Strategic Alignment Check
  - [ ] Step 1: Harden AST Guardrail Engine & Audit Loop
  - [ ] Step 2: Create & Update Knowledge Items
  - [ ] Step 3: Synchronize Architectural Rules
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/09_phase4_ast_hardening_and_governance.md] @[docs/epic/EPIC_150_tracker.md]`

---

### Integration Checkpoint: Full-Stack Validation
- [ ] **[NOK] Seed Vault & Database Ingress**: Full verification of `uv run python scripts/audit_database_atoms.py --strict` and clean seeding via `uv run python backend_v2/seed/run_seed.py local`.
- [ ] **[NOK] Backend Parity & Quality Loop**: Full execution of `uv run python scripts/backend_audit_loop.py backend_v2/ --test` passing Ruff, MyPy strict typing, and Pytest coverage gates (>90%).
- [ ] **[NOK] AST Guardrails FATAL Verification**: Full AST Guardrail audit passing `uv run python scripts/_ast_guardrails.py backend_v2/ --strict` and unit tests.
- [ ] **[NOK] Cross-Platform SDUI Semantic Parity**: Automated verification of SDUI semantic parity across Flutter and PDF rendering via `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`.
- [ ] **[NOK] Live Real LLM E2E REST API Verification**: Live execution verification via `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`.

---

### Post-Implementation Gates
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests were left behind in the modified domains.
- [ ] **[NOK] Proxy Sunset & Consumer Migration**: Codebase-wide search/replace of old import paths & delete deprecated proxies.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` on modified backend production files:
  - [ ] @[backend_v2/models/llm.py]
  - [ ] @[backend_v2/models/prompt.py]
  - [ ] @[backend_v2/llm/caching_service.py]
  - [ ] @[backend_v2/utils/math_utils.py]
  - [ ] @[backend_v2/llm/provider.py]
  - [ ] @[backend_v2/llm/client.py]
  - [ ] @[backend_v2/llm/adapters/base_adapter.py]
  - [ ] @[backend_v2/llm/adapters/vertex_adapter.py]
  - [ ] @[backend_v2/llm/adapters/ai_studio_adapter.py]
  - [ ] @[backend_v2/llm/adapters/anthropic_adapter.py]
  - [ ] @[backend_v2/llm/adapters/openai_adapter.py]
  - [ ] @[backend_v2/llm/adapters/deepseek_adapter.py]
  - [ ] @[backend_v2/llm/adapters/mock_adapter.py]
  - [ ] @[backend_v2/llm/ingress_pipeline.py]
  - [ ] @[backend_v2/llm/mock.py]
  - [ ] @[backend_v2/seed/seed_registry.py]
  - [ ] @[backend_v2/seed/run_seed.py]
  - [ ] @[backend_v2/services/progress.py]
  - [ ] @[backend_v2/core/registry.py]
  - [ ] @[backend_v2/services/execution.py]
  - [ ] @[backend_v2/services/llm_task_executor.py]
  - [ ] @[backend_v2/services/flattener.py]
  - [ ] @[backend_v2/services/mcp/mcp_tool_loop.py]
  - [ ] @[backend_v2/utils/redis_patcher.py]
  - [ ] @[backend_v2/utils/dict_utils.py]
  - [ ] @[backend_v2/models/dtos/prompt_context.py]
  - [ ] @[backend_v2/models/dtos/system.py]
  - [ ] @[backend_v2/services/studio/simulation_service.py]
  - [ ] @[backend_v2/services/studio/workflow_service.py]
  - [ ] @[backend_v2/services/studio/system_config_service.py]
  - [ ] @[backend_v2/services/studio/prompt_block_service.py]
  - [ ] @[backend_v2/services/studio/output_profile_service.py]
  - [ ] @[backend_v2/api/routers/studio/workflows.py]
  - [ ] @[backend_v2/api/routers/studio/steps.py]
  - [ ] @[backend_v2/api/routers/studio/prompt_blocks.py]
  - [ ] @[backend_v2/services/blueprint.py]
  - [ ] @[backend_v2/worker.py]
  - [ ] @[backend_v2/models/v2_core.py]
  - [ ] @[scripts/sanitize_seed_vault.py]
  - [x] @[backend_v2/hooks/scoring/falsifier_hook.py]
  - [x] @[backend_v2/hooks/scoring/matrix_hook.py]
  - [x] @[backend_v2/hooks/scoring/normalization_hook.py]
  - [x] @[backend_v2/hooks/scoring/passivity_hook.py]
  - [x] @[backend_v2/hooks/validation.py]
  - [x] @[backend_v2/hooks/llm.py]
  - [x] @[backend_v2/hooks/dlq_guard.py]
  - [x] @[backend_v2/hooks/input_processing.py]
  - [x] @[backend_v2/hooks/integrity.py]
  - [x] @[backend_v2/hooks/source_verification_hook.py]
  - [x] @[backend_v2/hooks/atom_flattening.py]
  - [x] @[backend_v2/hooks/context_mapper.py]
  - [x] @[backend_v2/hooks/archival.py]
  - [x] @[backend_v2/hooks/security.py]
  - [x] @[backend_v2/hooks/hydration.py]
  - [x] @[backend_v2/hooks/metadata.py]
  - [x] @[backend_v2/hooks/metrics.py]
  - [x] @[backend_v2/hooks/references.py]
  - [ ] @[backend_v2/services/orchestrator/dag_executor.py]
  - [ ] @[backend_v2/services/orchestrator/synthesis_payload_compressor.py]
  - [ ] @[backend_v2/services/orchestrator/prompt_compiler.py]
  - [ ] @[backend_v2/services/orchestrator/prompt_compiler_adapter.py]
  - [ ] @[backend_v2/services/orchestrator/context_router.py]
  - [ ] @[backend_v2/services/orchestrator/matrix_reducer.py]
  - [ ] @[backend_v2/services/orchestrator/strategies/llm.py]
  - [ ] @[backend_v2/services/orchestrator/strategies/base.py]
  - [ ] @[backend_v2/services/orchestrator/strategies/logic.py]
  - [ ] @[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py]
  - [ ] @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py]
  - [ ] @[backend_v2/services/orchestrator/enriched_dag_executor.py]
  - [ ] @[backend_v2/services/orchestrator/two_pass_atomizer.py]
  - [ ] @[backend_v2/services/orchestrator/synthesis_distiller.py]
  - [ ] @[backend_v2/services/orchestrator/matrix_explanation_service.py]
  - [ ] @[backend_v2/services/orchestrator/rag_preflight_service.py]
  - [ ] @[backend_v2/services/orchestrator/localization_compiler.py]
  - [ ] @[backend_v2/services/orchestrator/extraction_schema_factory.py]
  - [ ] @[backend_v2/services/orchestrator/anchor_validation_service.py]
  - [ ] @[backend_v2/database/repositories/execution.py]
  - [ ] @[backend_v2/database/repositories/component.py]
  - [ ] @[backend_v2/database/repositories/components/matrix.py]
  - [ ] @[backend_v2/database/repositories/audit.py]
  - [ ] @[backend_v2/database/repositories/workflow.py]
  - [ ] @[backend_v2/models/domain/inputs.py]
  - [ ] @[backend_v2/models/domain/mechanical_anchors.py]
  - [ ] @[backend_v2/models/dtos/evaluation_steps.py]
  - [ ] @[backend_v2/models/dtos/quote_evidence.py]
  - [ ] @[backend_v2/models/state.py]
  - [ ] @[backend_v2/models/domain/archivist.py]
  - [ ] @[backend_v2/models/dtos/matrix_scorecard.py]
  - [ ] @[scripts/_ast_guardrails.py]
  - [ ] @[scripts/backend_audit_loop.py]
  - [ ] @[.agents/rules/01-python-backend.md]
  - [ ] @[.agents/rules/03_seed_vault.md]
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for surviving business logic.
- [ ] **[NOK] Documentation & Knowledge Item Update**: Run `/tier7-describe-architecture`.

---

### Final Epic Audit
- [ ] **[NOK]** System 2 Reverse Epic Analysis: Run `/tier8-audit-epic @[docs/epic/EPIC_150_Zero_Permissive_Typing_Lockdown.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.

---

## Instructions for the Execution Agent

1. **Atomic Checkpoint Commits**: After completing each step and passing the validation gate, instruct an atomic git commit with an English message specifying the exact modified files.
2. **Seeding Environment**: If data or seed schemas are modified, run `uv run python backend_v2/seed/run_seed.py local`.
3. **Execution Mode**: Supports both Step-by-Step (default pause per step) and Continuous Full-Auto Mode (invoked via `/tier2-execute --full-auto` or explicit continuous mandate; progresses autonomously across steps as long as quality gates pass 100%, and triggers clean session handover when context budget is reached).
4. **Mandatory Workflow Loop**: `[/tier0-create-plan if deferred] -> /tier0-research-plan -> /tier2-execute -> /tier8-audit-plan`. You MUST ALWAYS pass BOTH the plan and the tracker file in ALL commands.
5. **Post-Implementation Loop**: `/tier2-hardening-backend` -> `/tier7-describe-architecture` -> `/tier8-audit-epic`.

---

## Requirements Traceability Matrix

| Requirement / Invariant | Source in Epic | Plan Mapping | Execution Status |
| :--- | :--- | :--- | :--- |
| `LLMMessageDTO`, `PromptMetadataDTO`, `ProviderMetadataDTO` strict DTOs definition | Epic Sec 2 & 3 (Phase 1) | Phase 1, Step 1 | `[x]` Passed |
| `CompiledPrompt` methods return `list[LLMMessageDTO]` with direct attribute access | Epic Sec 2 & 3 (Phase 1) | Phase 1, Step 1 | `[x]` Passed |
| `caching_service.py` & `math_utils.py` StrictnessConfig strictness | Epic Sec 3 (Phase 1) | Phase 1, Step 2 | `[x]` Passed |
| Central test factories `make_llm_message` & `test_prompt.py` dot-notation migration | Epic Sec 3 (Phase 1) | Phase 1, Step 3 | `[x]` Passed |
| Base adapter & provider LiteLLM `exclude_none=True` message serialization | Epic Sec 2 & 3 (Phase 1) | Phase 1, Step 1 | `[x]` Passed |
| Eliminate `dict[str, Any]` & QGR suppressions across all provider adapters | Epic Sec 3 (Phase 1) | Phase 1, Step 2 | `[x]` Passed |
| Migrate adapter test suites (~100+ fixtures & assertions) to DTOs | Epic Sec 3 (Phase 1) | Phase 1, Step 3 | `[x]` Passed |
| Seeder Two-Phase Pre-Flight In-Memory validation in `run_seed.py` | Epic Sec 2 & 3 (Phase 1) | Phase 1C, Step 1 | `[x]` Passed |
| Migrate coupled MCP & executor test suites | Epic Sec 3 (Phase 1) | Phase 1C, Step 2 | `[x]` Passed |
| Migrate coupled prompt builder & hook test suites | Epic Sec 3 (Phase 1) | Phase 1C, Step 3 | `[x]` Passed |
| Pre-implementation cleanups: `redis_patcher.py` `FakeRedis` & `ClientErrorPayload` comment | Epic Sec 3 (Phase 2) | Phase 2, Step 1 | `[x]` Passed |
| Refine `ProgressState` & `ProgressTracker` contracts (SSE 1:1 parity) | Epic Sec 2 & 3 (Phase 2) | Phase 2, Step 2 | `[x]` Passed |
| Define TaskMetadataDTO in `core/registry.py` & update task registry tests | Epic Sec 3 (Phase 2) | Phase 2, Step 3 | `[x]` Passed |
| Purge obsolete `Workflow.ui_schema` & `Step.output_schema`; define ProviderExtraParamsDTO | Epic Sec 2 & 3 (Phase 2) | Phase 2, Step 1 | `[x]` Passed |
| Sanitize `seed_data.json` & purge orphan `"step_blueprints": []` | Epic Sec 3 (Phase 2) | Phase 2, Step 1 | `[x]` Passed |
| Studio simulation service returns typed simulation DTOs directly | Epic Sec 2 & 3 (Phase 2) | Phase 2, Step 2 | `[x]` Passed |
| Surgical typing & telemetry cleanup in `worker.py` & `blueprint.py` | Epic Sec 3 (Phase 2) | Phase 2, Step 3 | `[x]` Passed |
| Eradicate QGR suppressions & `isinstance(dict)` in scoring hooks | Epic Sec 3 (Phase 3) | Phase 3, Step 1 | `[x]` Passed |
| Eradicate QGR suppressions & duck-typing in processing & validation hooks | Epic Sec 3 (Phase 3) | Phase 3, Step 2 | `[x]` Passed |
| Harden DAG executor & synthesis payload compressor polymorphic handling | Epic Sec 3 (Phase 3) | Phase 3, Step 1 | `[ ]` Pending |
| Harden orchestrator strategies & pipeline services | Epic Sec 3 (Phase 3) | Phase 3, Step 2 | `[ ]` Pending |
| Repositories reconstitution firewall (zero dict leakage) | Epic Sec 3 (Phase 3) | Phase 3, Step 1 | `[ ]` Pending |
| Domain models & DTOs duck-typing elimination | Epic Sec 3 (Phase 3) | Phase 3, Step 2 | `[ ]` Pending |
| Harden AST guardrails `QGR001`, `QGR002`, `QGR012` to universal `FATAL` severity | Epic Sec 3 (Phase 4) | Phase 4, Step 1 | `[ ]` Pending |
| Create `ki_zero_permissive_typing.md` & update existing KIs | Epic Sec 3 (Phase 4) | Phase 4, Step 2 | `[ ]` Pending |
| Synchronize architectural rules in `01-python-backend.md` & `03_seed_vault.md` | Epic Sec 3 (Phase 4) | Phase 4, Step 3 | `[ ]` Pending |

---

# Session Handover Context

## Achieved
- **Sub-Phase 1A Execution Completed & Atomically Committed (`0b3a8466`)**:
  - Foundational DTOs (`LLMMessageDTO`, `ProviderMetadataDTO`, `PromptMetadataDTO`) defined with `ConfigDict(strict=True, extra="forbid", frozen=True)`.
  - `LLMResponse` and `CompiledPrompt` refactored to strict DTO collections with pure dot-notation access.
  - Quality gates passed 100% and committed to git.
- **Sub-Phase 1B Execution Completed & Atomically Committed (`24d7e71c`)**:
  - Base Adapter & Redis Pacing Modernization (`@[backend_v2/llm/adapters/base_adapter.py]`).
  - Provider Pipeline & Outer LiteLLM Boundary Serialization (`@[backend_v2/llm/provider.py]`).
  - LLM Client Wrapper & Ingress ACL (`@[backend_v2/llm/client.py]`, `@[backend_v2/llm/ingress_pipeline.py]`, `@[backend_v2/llm/mock.py]`).
  - Provider Adapters & Prompt Compiler Adapter (`@[backend_v2/llm/adapters/vertex_adapter.py]`, `@[backend_v2/llm/adapters/ai_studio_adapter.py]`, `@[backend_v2/llm/adapters/anthropic_adapter.py]`, `@[backend_v2/services/orchestrator/prompt_compiler_adapter.py]`).
  - Test Suite Migration (143 passed, 0 mypy errors).
- **Sub-Phase 1C Execution Completed & Atomically Committed (`b4c19250`)**:
  - **Step 0**: Appended explicit AST Guardrail reason justifications to `# noqa: QGR001` comments in `@[backend_v2/llm/provider.py]`.
  - **Step 1**: Replaced callable discriminator in `@[backend_v2/seed/seed_registry.py]` with standard Pydantic V2 `Discriminator("type")` and updated `SystemConfigUnion`. Implemented Two-Phase Pre-Flight In-Memory Validation pattern in `@[backend_v2/seed/run_seed.py]` (`validate_all_seed_collections`) preventing any database wipe if validation fails. Added ISTQB contract tests to `@[backend_v2/tests/unit/seed/test_run_seed.py]` and modernized `@[backend_v2/tests/unit/seed/test_seed_registry.py]`.
  - **Step 2**: Migrated `PromptContextDTO` (`@[backend_v2/models/dtos/prompt_context.py]`) to `list[LLMMessageDTO]` with strict validation. Updated `@[backend_v2/services/studio/simulation_service.py]`, `@[backend_v2/tests/unit/models/dtos/test_prompt_context.py]`, `@[backend_v2/tests/unit/services/mcp/test_tool_loop_sanitization.py]`, `@[backend_v2/tests/unit/services/test_llm_task_executor.py]`, and `@[backend_v2/tests/unit/test_llm_task_executor.py]`.
  - **Step 3**: Migrated prompt building services and hooks (`@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py]`, `@[backend_v2/services/orchestrator/two_pass_atomizer.py]`, `@[backend_v2/services/orchestrator/prompt_compiler_adapter.py]`, `@[backend_v2/services/source_verification_service.py]`, `@[backend_v2/hooks/interaction_hook.py]`, `@[backend_v2/services/llm_task_executor.py]`) to `LLMMessageDTO` and converted assertions across all coupled test suites to dot-notation.
  - Sub-Phase 1C Remediation: remediated `sliding_window_linker.py`, un-skipped and passed all 7 tests in `test_finops_telemetry.py`, fixed PEP 257 docstrings and resolved mock fallback objects for `firebase_admin`. Full audit sign-off (308 unit/integration tests passed 100%).
- **Sub-Phase 2A Execution & Audit Completed & Atomically Committed (`a27d2066`)**:
  - **Step 1 Pre-Implementation Cleanups**: Eliminated 7 `hasattr()` reflection calls and monkey patching in `@[backend_v2/utils/redis_patcher.py]` with typed `ArqCompatibleFakeRedis`. Added explicit AST guardrail classification in `@[backend_v2/models/dtos/system.py]`.
  - **Step 2 Modernize Progress State & Tracker Interfaces**: Refined `ProgressState` in `@[backend_v2/services/progress.py]` with `ConfigDict(strict=True, extra="forbid", frozen=True)` locking `status`, `timestamp`, `current_step`, `progress`, `error` and eradicating `result: dict[str, Any]` and `details: dict[str, Any]`. Modernized `ProgressTracker` ABC, `DatabaseProgressTracker`, and `InMemoryProgressTracker`. Strongly typed `ProgressService.redis` to `ArqCompatibleFakeRedis`.
  - **Step 3 Modernize Task Registry & Unit Tests**: Co-located `TaskMetadataDTO` in `@[backend_v2/core/registry.py]` and updated `TaskRegistry.register_task()`. Modernized test suites.
  - **Tier 8 Red-Team Audit Sign-off**: Passed Universal Quality Gate (`backend_audit_loop.py backend_v2/ --test`) with 2,663 passed tests, 0 failed, 93.51% code coverage.
- **Sub-Phase 2B Execution & Audit Completed & Atomically Verified**:
  - **Step 0 Pre-Implementation Cleanups**: Fixed legacy comma exception syntax in `@[backend_v2/services/studio/workflow_service.py]` (`except (AppException, ValidationError, ...):`). Replaced `hasattr(strat_raw, "value")` with `isinstance(strat_raw, ScoringStrategy)` in `@[backend_v2/services/blueprint.py]`.
  - **Step 1 Purge Obsolete Seed Schemas & Define Provider Extra Params**: Defined strict immutable `ProviderExtraParamsDTO` (`ConfigDict(strict=True, extra="forbid", frozen=True)`) in `@[backend_v2/models/v2_core.py]`. Updated `ModelProfile.additional_params` to use `ProviderExtraParamsDTO`. Purged obsolete `output_schema` from `Step` and `StepCreateDTO` (`@[backend_v2/models/dtos/studio.py]`), and purged `ui_schema` from `Workflow`. Dynamically generated `expected_inputs` in `@[backend_v2/services/execution.py]`. Purged orphan `"step_blueprints": []` in `@[scripts/sanitize_seed_vault.py]`, sanitized and re-seeded `@[backend_v2/seed/seed_data.json]` and `@[data/db_v2.json]`.
  - **Step 2 Modernize Studio Services & Routers**: Refactored `StudioSimulationService` (`@[backend_v2/services/studio/simulation_service.py]`) to return strict SSOT DTOs (`WorkflowSimulationResponse`, `StepSimulationResponse`, `PromptBlockSimulationResponse`). Eliminated raw dict conversions in `@[backend_v2/api/routers/studio/workflows.py]`, `@[backend_v2/api/routers/studio/steps.py]`, and `@[backend_v2/api/routers/studio/prompt_blocks.py]`. Fixed tenant isolation logic in `@[backend_v2/services/studio/auth_validator.py]`. Migrated unit test suite in `@[backend_v2/tests/unit/services/studio/test_simulation_service.py]` to 100% dot-notation attribute access; created unit tests in `@[backend_v2/tests/unit/services/studio/test_auth_validator.py]` and `@[backend_v2/tests/unit/services/studio/test_lexicon_service.py]`.
  - **Step 3 Surgical Hardening of Worker, Blueprint, Adapters & Contracts**: Co-located `StepTraceMetadataDTO` and `TraceEventMetadataEnvelope` in `@[backend_v2/models/dtos/trace.py]`. Hydrated typed envelope and read `TokenUsage` directly in `@[backend_v2/services/blueprint.py]` and `@[backend_v2/worker.py]`. Updated `LLMProviderConfig.additional_params` in `@[backend_v2/models/llm.py]` and updated LLM adapters (`openai_adapter.py`, `anthropic_adapter.py`, `ai_studio_adapter.py`, `vertex_adapter.py`) to access first-class typed fields.
- **Sub-Phase 3A Execution & Audit Completed (`red_team_audit_06_phase3a_hooks_suppression_eradication.md`)**:
  - **Scoring Hooks Core (`falsifier_hook.py`, `matrix_hook.py`, `normalization_hook.py`, `passivity_hook.py`)**: Eradicated all 14 `# noqa: QGR012` inline suppressions and duck-typing checks. Converted state handling to `AtomResultDTO` validation, typed `TypeAdapter(dict[str, float])` mapping, and direct `ExecutionInputsDTO` dot-notation access.
  - **Processing, Context & Telemetry Hooks (`context_mapper.py`, `references.py`, `llm.py`, `input_processing.py`, `validation.py`, `security.py`, `dlq_guard.py`, `atom_flattening.py`, `archival.py`, `hydration.py`, `metadata.py`, `metrics.py`)**: Strongly typed `all_blocks: list[PromptBlockBase] | None`, `knowledge_base: dict[str, str] | None`, `workflow_model_mapping` (`TypeAdapter(dict[str, str])`), and fixed tuple exception syntax in `input_processing.py`.
  - **Coverage Deficit Resolution**: Expanded test suites by creating `@[backend_v2/tests/unit/hooks/test_context_mapper.py]`, `@[backend_v2/tests/unit/hooks/test_security.py]`, `@[backend_v2/tests/unit/hooks/test_references.py]`, `@[backend_v2/tests/unit/hooks/test_metadata.py]`, and `@[backend_v2/tests/unit/hooks/test_validation.py]`.
  - **Tier 8 Red-Team Audit Sign-Off**: 191 subsystem unit tests passed (4 xpassed, 0 failures), 0 AST violations in `--strict` mode, reaching **90.25% line coverage** for `backend_v2/hooks/`. Global backend quality gate passed with 2,717 passed tests, 0 failures, and **93.57% total coverage**.

## Learned
- **Decorator-Inclusive AST Spans in Markdown Auditing**: The markdown boundary linter (`scripts/audit_markdown_boundaries.py`) includes decorator lines (`@router.get`, `@pytest.mark.asyncio`) in the starting line of function AST bounds. All plan line bounds for decorated handlers and test fixtures must align with the first decorator line.
- **SSOT Response Direct Passthrough**: `StudioSimulationService` must return existing response DTOs (`WorkflowSimulationResponse`, `StepSimulationResponse`, `PromptBlockSimulationResponse`) directly, allowing FastAPI routers to return service outputs without intermediate `model_validate()` calls.
- **Telemetry Typed Envelopes Over Dict `.get()`**: Co-locating `StepTraceMetadataDTO` and `TraceEventMetadataEnvelope` in `backend_v2/models/dtos/trace.py` enables strict hydration of `_step_metadata` without relying on dict indexing or `.get()` fallbacks.
- **Provider Extra Params Isolation**: `ProviderExtraParamsDTO` cleanly restricts extra provider sampling parameters (`temperature`, `top_p`, `top_k`, `max_output_tokens`) while first-class provider options (`vertex_location`, `thinking_budget_tokens`) belong as direct typed properties on `LLMProviderConfig` and `ModelProfile`.
- **Subsystem Coverage Deficit Strategy**: Several peripheral hook modules (`context_mapper.py`, `security.py`, `references.py`, `validation.py`, `metadata.py`) previously lacked dedicated tests, creating an overall coverage deficit (79.12%). Expanding tests with ISTQB equivalence partition and boundary value cases lifted subsystem coverage to 90.25% without sacrificing domain strictness.
- **Hook State Polymorphic Envelope Validation**: In scoring and falsifier hooks, `StateInputWrapper` should validate nested `inputs` and `raw_inputs` as `ExecutionInputsDTO | dict[str, Any]` while maintaining `ConfigDict(strict=True, extra="ignore", frozen=True)` to accept dynamic matrix key projections alongside strict step arrays.
- **Guarded TypeAdapter Hydration with RFC-7807 Mapping**: Replacing silent `except ValidationError: pass` blocks in hook extraction pathways with guarded `TypeAdapter` validation and explicit `AppException(ErrorCodes.VALIDATION_FAILED, status_code=422)` conversion prevents silent corruptions while strictly upholding Fail-Fast architecture.

## Remaining
- **Phase 3: Hooks, Orchestrator & Repository Suppression Eradication**:
  - Sub-Phase 3B: Orchestrator Suppression Eradication (`@[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/07_phase3b_orchestrator_suppression_eradication.md]`).
  - Sub-Phase 3C: Repositories & Domain Models (`@[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/08_phase3c_repositories_and_domain_models.md]`).
- **Phase 4: AST Hardening, Knowledge Base & Architectural Governance Lockdown**:
  - Phase 4: AST Hardening & Governance (`@[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/09_phase4_ast_hardening_and_governance.md]`).

## Resume Command
```powershell
/tier0-research-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/07_phase3b_orchestrator_suppression_eradication.md] @[docs/epic/EPIC_150_tracker.md]
```