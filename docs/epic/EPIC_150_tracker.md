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
- [ ] **[NOK] Audit (Sub-Phase 1A):** `/tier8-audit-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/01_phase1a_llm_models_and_prompt_dto.md] @[docs/epic/EPIC_150_tracker.md]`
- [ ] **[NOK] Red-Teaming (Sub-Phase 1B):** `/tier0-research-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/02_phase1b_llm_adapters_and_provider_pipeline.md] @[docs/epic/EPIC_150_tracker.md]`
- [ ] **[NOK] Execution (Sub-Phase 1B):** `/tier2-execute @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/02_phase1b_llm_adapters_and_provider_pipeline.md] @[docs/epic/EPIC_150_tracker.md]`
  - [ ] Step 0: Strategic Alignment Check
  - [ ] Step 1: Modernize Base Adapter & Provider Infrastructure
  - [ ] Step 2: Modernize Provider Adapters
  - [ ] Step 3: Migrate Adapter Test Suites
- [ ] **[NOK] Audit (Sub-Phase 1B):** `/tier8-audit-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/02_phase1b_llm_adapters_and_provider_pipeline.md] @[docs/epic/EPIC_150_tracker.md]`
- [ ] **[NOK] Red-Teaming (Sub-Phase 1C):** `/tier0-research-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/03_phase1c_coupled_tests_and_seed_validation.md] @[docs/epic/EPIC_150_tracker.md]`
- [ ] **[NOK] Execution (Sub-Phase 1C):** `/tier2-execute @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/03_phase1c_coupled_tests_and_seed_validation.md] @[docs/epic/EPIC_150_tracker.md]`
  - [ ] Step 0: Strategic Alignment Check
  - [ ] Step 1: Harden Seed Registry & Implement Two-Phase Seeder Validation
  - [ ] Step 2: Migrate Coupled MCP & Executor Test Suites
  - [ ] Step 3: Migrate Coupled Prompt Builder & Hook Test Suites
- [ ] **[NOK] Audit (Sub-Phase 1C):** `/tier8-audit-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/03_phase1c_coupled_tests_and_seed_validation.md] @[docs/epic/EPIC_150_tracker.md]`

### Phase 2: Service & Studio Layer DTO Elimination
- **Plan:** @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/04_phase2a_service_and_progress_dto.md]
- **Plan (Sub-Phase 2B):** @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/05_phase2b_studio_and_seed_models.md]
- [ ] **[NOK] Red-Teaming (Sub-Phase 2A):** `/tier0-research-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/04_phase2a_service_and_progress_dto.md] @[docs/epic/EPIC_150_tracker.md]`
- [ ] **[NOK] Execution (Sub-Phase 2A):** `/tier2-execute @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/04_phase2a_service_and_progress_dto.md] @[docs/epic/EPIC_150_tracker.md]`
  - [ ] Step 0: Strategic Alignment Check
  - [ ] Step 1: Pre-Implementation Cleanups
  - [ ] Step 2: Modernize Progress State & Tracker Interfaces
  - [ ] Step 3: Modernize Task Registry & Unit Tests
- [ ] **[NOK] Audit (Sub-Phase 2A):** `/tier8-audit-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/04_phase2a_service_and_progress_dto.md] @[docs/epic/EPIC_150_tracker.md]`
- [ ] **[NOK] Red-Teaming (Sub-Phase 2B):** `/tier0-research-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/05_phase2b_studio_and_seed_models.md] @[docs/epic/EPIC_150_tracker.md]`
- [ ] **[NOK] Execution (Sub-Phase 2B):** `/tier2-execute @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/05_phase2b_studio_and_seed_models.md] @[docs/epic/EPIC_150_tracker.md]`
  - [ ] Step 0: Strategic Alignment Check
  - [ ] Step 1: Purge Obsolete Seed Schemas & Define Provider Extra Params
  - [ ] Step 2: Modernize Studio Services & Routers
  - [ ] Step 3: Surgical Hardening of Worker & Blueprint
- [ ] **[NOK] Audit (Sub-Phase 2B):** `/tier8-audit-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/05_phase2b_studio_and_seed_models.md] @[docs/epic/EPIC_150_tracker.md]`

### Phase 3: Hooks, Orchestrator & Repository Suppression Eradication
- **Plan:** @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/06_phase3a_hooks_suppression_eradication.md]
- **Plan (Sub-Phase 3B):** @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/07_phase3b_orchestrator_suppression_eradication.md]
- **Plan (Sub-Phase 3C):** @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/08_phase3c_repositories_and_domain_models.md]
- [ ] **[NOK] Red-Teaming (Sub-Phase 3A):** `/tier0-research-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/06_phase3a_hooks_suppression_eradication.md] @[docs/epic/EPIC_150_tracker.md]`
- [ ] **[NOK] Execution (Sub-Phase 3A):** `/tier2-execute @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/06_phase3a_hooks_suppression_eradication.md] @[docs/epic/EPIC_150_tracker.md]`
  - [ ] Step 0: Strategic Alignment Check
  - [ ] Step 1: Harden Scoring Hooks
  - [ ] Step 2: Harden Processing & Validation Hooks
- [ ] **[NOK] Audit (Sub-Phase 3A):** `/tier8-audit-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/06_phase3a_hooks_suppression_eradication.md] @[docs/epic/EPIC_150_tracker.md]`
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
  - [ ] @[backend_v2/hooks/scoring/falsifier_hook.py]
  - [ ] @[backend_v2/hooks/scoring/matrix_hook.py]
  - [ ] @[backend_v2/hooks/scoring/normalization_hook.py]
  - [ ] @[backend_v2/hooks/scoring/passivity_hook.py]
  - [ ] @[backend_v2/hooks/validation.py]
  - [ ] @[backend_v2/hooks/llm.py]
  - [ ] @[backend_v2/hooks/dlq_guard.py]
  - [ ] @[backend_v2/hooks/input_processing.py]
  - [ ] @[backend_v2/hooks/integrity.py]
  - [ ] @[backend_v2/hooks/source_verification_hook.py]
  - [ ] @[backend_v2/hooks/atom_flattening.py]
  - [ ] @[backend_v2/hooks/context_mapper.py]
  - [ ] @[backend_v2/hooks/archival.py]
  - [ ] @[backend_v2/hooks/security.py]
  - [ ] @[backend_v2/hooks/hydration.py]
  - [ ] @[backend_v2/hooks/metadata.py]
  - [ ] @[backend_v2/hooks/metrics.py]
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
| Base adapter & provider LiteLLM `exclude_none=True` message serialization | Epic Sec 2 & 3 (Phase 1) | Phase 1, Step 1 | `[ ]` Pending |
| Eliminate `dict[str, Any]` & QGR suppressions across all provider adapters | Epic Sec 3 (Phase 1) | Phase 1, Step 2 | `[ ]` Pending |
| Migrate adapter test suites (~100+ fixtures & assertions) to DTOs | Epic Sec 3 (Phase 1) | Phase 1, Step 3 | `[ ]` Pending |
| Seeder Two-Phase Pre-Flight In-Memory validation in `run_seed.py` | Epic Sec 2 & 3 (Phase 1) | Phase 1, Step 1 | `[ ]` Pending |
| Migrate coupled MCP & executor test suites | Epic Sec 3 (Phase 1) | Phase 1, Step 2 | `[ ]` Pending |
| Migrate coupled prompt builder & hook test suites | Epic Sec 3 (Phase 1) | Phase 1, Step 3 | `[ ]` Pending |
| Pre-implementation cleanups: `redis_patcher.py` `FakeRedis` & `ClientErrorPayload` comment | Epic Sec 3 (Phase 2) | Phase 2, Step 1 | `[ ]` Pending |
| Refine `ProgressState` & `ProgressTracker` contracts (SSE 1:1 parity) | Epic Sec 2 & 3 (Phase 2) | Phase 2, Step 2 | `[ ]` Pending |
| Define `TaskMetadataDTO` in `core/registry.py` & update task registry tests | Epic Sec 3 (Phase 2) | Phase 2, Step 3 | `[ ]` Pending |
| Purge obsolete `Workflow.ui_schema` & `Step.output_schema`; define `ProviderExtraParamsDTO` | Epic Sec 2 & 3 (Phase 2) | Phase 2, Step 1 | `[ ]` Pending |
| Sanitize `seed_data.json` & purge orphan `"step_blueprints": []` | Epic Sec 3 (Phase 2) | Phase 2, Step 1 | `[ ]` Pending |
| Studio simulation service returns typed simulation DTOs directly | Epic Sec 2 & 3 (Phase 2) | Phase 2, Step 2 | `[ ]` Pending |
| Surgical typing & telemetry cleanup in `worker.py` & `blueprint.py` | Epic Sec 3 (Phase 2) | Phase 2, Step 3 | `[ ]` Pending |
| Eradicate QGR suppressions & `isinstance(dict)` in scoring hooks | Epic Sec 3 (Phase 3) | Phase 3, Step 1 | `[ ]` Pending |
| Eradicate QGR suppressions & duck-typing in processing & validation hooks | Epic Sec 3 (Phase 3) | Phase 3, Step 2 | `[ ]` Pending |
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
- **Sub-Phase 1A Execution Completed & Mathematically Verified**:
  - **Foundational DTO Definitions**: Defined strict frozen Pydantic V2 DTOs (`LLMMessageDTO`, `ProviderMetadataDTO` in `backend_v2/models/llm.py` and `PromptMetadataDTO` in `backend_v2/models/prompt.py`) with zero permissive typing (`model_config = ConfigDict(strict=True, extra="forbid", frozen=True)`).
  - **LLMResponse Schema Lockdown**: Refactored `LLMResponse` in `backend_v2/models/llm.py` to use strictly typed fields (`messages: list[LLMMessageDTO] | None`, `tool_calls: list[OpenAIToolCallDTO] | None`, `provider_metadata: ProviderMetadataDTO`).
  - **CompiledPrompt Refactoring & Immutability**:
    - Replaced loose dictionary lists with `list[LLMMessageDTO]` for `static_messages` and `dynamic_messages`.
    - Updated `to_flat_messages()`, `to_static_flat()`, and `to_dynamic_flat()` to return `list[LLMMessageDTO]`.
    - Replaced dictionary subscripting (`msg.get("role")`, `msg.get("content")`) with direct attribute access (`msg.role`, `msg.content`).
    - Implemented immutable message merging in `_merge_flat` using `.model_copy(update={"content": merged_content})`.
  - **Caching Service Purity Scanner**: Modernized `LLMCachingService._run_purity_scanner` in `backend_v2/llm/caching_service.py` to directly inspect `LLMMessageDTO` attributes without runtime dictionary subscripts.
  - **Math Utils Hardening**: Hardened `StrictnessConfig` in `backend_v2/utils/math_utils.py` to enforce `ConfigDict(strict=True, extra="forbid", frozen=True)` with PEP 593 `Annotated` field descriptions.
  - **Central Test Factories & Fixtures**:
    - Added `make_llm_message` helper in `backend_v2/tests/conftest.py` with strict role literal constraint `Literal["system", "user", "assistant", "tool"]`.
    - Migrated `backend_v2/tests/unit/models/test_prompt.py` to dot-notation `LLMMessageDTO` assertions and verified all 5 `<test_contracts>` (100% coverage).
    - Migrated `backend_v2/tests/unit/llm/test_caching_service.py` test fixtures to `LLMMessageDTO` (100% coverage).
    - Modernized `backend_v2/tests/unit/models/test_llm.py` with 12 comprehensive unit tests covering all validators (100% coverage).
  - **Downstream Adapter Synchronization**:
    - Updated `BaseLLMAdapter`, `OpenAICacheAdapter`, `AnthropicCacheAdapter`, `VertexCacheAdapter`, `GoogleAIStudioCacheAdapter`, and `MockCacheAdapter` signatures to `tuple[list[LLMMessageDTO] | list[dict[str, Any]], dict[str, Any]]`.
    - Modernized Anthropic and Base adapter character counting and message serialization to use direct `msg.role` and `msg.content` attributes.
    - Updated `_validate_non_empty_payload` in `backend_v2/services/llm_task_executor.py` to support `LLMMessageDTO` alongside `ChatMessageDTO`.
  - **Universal Quality Gate Validation**: Executed `backend_audit_loop.py` on all Phase 1A targets with zero errors (Ruff lint/format, MyPy strict typing, AST guardrails, Jinja template verification, Seed atom audit, and Pytest coverage gates all passed at 100%).
  - **Markdown Boundary Integrity**: Verified `audit_markdown_boundaries.py` on both `EPIC_150_tracker.md` and `01_phase1a_llm_models_and_prompt_dto.md` with exact AST decorator-inclusive line spans.

## Learned
- **CompiledPrompt Immutability & Safe Concatenation**: Because `LLMMessageDTO` is frozen (`ConfigDict(strict=True, extra="forbid", frozen=True)`), merging consecutive same-role messages in `CompiledPrompt._merge_flat` must use immutable `.model_copy(update={"content": merged_content})`.
- **AST Exact Node Boundary Mapping**: Markdown references (`#Lstart-Lend`) must match exact `ast.ClassDef`, `ast.FunctionDef`, or `ast.AsyncFunctionDef` node spans, including decorator line offsets (specifically `CompiledPrompt` #L32-L136, `_forbid_system_in_dynamic` #L62-L84, `_merge_flat` #L86-L109, `LLMCachingService._run_purity_scanner` #L68-L90, `StrictnessConfig` #L19-L45).
- **DTO Role Literal Strictness**: Central test factory `make_llm_message` in `conftest.py` must lock roles strictly to `Literal["system", "user", "assistant", "tool"]` to eliminate ad-hoc string typos and legacy untyped dictionary fixtures.
- **Cross-Layer Adapter Coupling**: When `CompiledPrompt` outputs `list[LLMMessageDTO]`, downstream caching adapters (`BaseLLMAdapter`, `OpenAICacheAdapter`, `AnthropicCacheAdapter`, `VertexCacheAdapter`, `GoogleAIStudioCacheAdapter`, `MockCacheAdapter`) must accept `tuple[list[LLMMessageDTO] | list[dict[str, Any]], dict[str, Any]]` to support both native DTOs and serialized payloads without triggering downstream MyPy type errors.
- **Pydantic Field Defaults in Strict Typechecking**: Optional fields in Pydantic models (specifically `api_key` and `model_params` in `AdHocTestRequest`) must explicitly assign `= None` or `= Field(...)` on the right-hand side, otherwise MyPy strict mode treats them as required constructor arguments.
- **Dual-Type Transition Support in Validation Layers**: Intermediate utility methods like `_validate_non_empty_payload` in `llm_task_executor.py` should accept both legacy `ChatMessageDTO` and modern `LLMMessageDTO` during multi-phase transitions to prevent cascade failures across non-migrated executor suites.

## Remaining
- **Atomic Git Commit**: Perform atomic git commit for Phase 1A changes.
- **Sub-Phase 1B Research & Execution**:
  - Run `/tier0-research-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/02_phase1b_llm_adapters_and_provider_pipeline.md] @[docs/epic/EPIC_150_tracker.md]`.
  - Modernize Base Adapter & Provider Infrastructure (`backend_v2/llm/adapters/base_adapter.py`, `backend_v2/llm/provider.py`, `backend_v2/llm/client.py`).
  - Modernize Provider Adapters (`openai_adapter.py`, `anthropic_adapter.py`, `vertex_adapter.py`, `ai_studio_adapter.py`, `mock_adapter.py`) to eliminate `dict[str, Any]` and QGR suppressions.
  - Migrate Adapter Test Suites (`test_base_adapter.py`, `test_openai_adapter.py`, `test_anthropic_adapter.py`, `test_vertex_adapter.py`, `test_ai_studio_adapter.py`, `test_mock_adapter.py`).
- **Sub-Phase 1C through Phase 4**: Follow sequential execution pipeline per `EPIC_150_tracker.md`.

## Resume Command
```powershell
/tier0-research-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/02_phase1b_llm_adapters_and_provider_pipeline.md] @[docs/epic/EPIC_150_tracker.md]
```
