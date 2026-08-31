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

# EPIC 150 Tracker: Zero Permissive Typing Lockdown

**Target Epic**: `@[docs/epic/EPIC_150_Zero_Permissive_Typing_Lockdown.md]`  
**Audit Report**: `@[docs/epic/EPIC_150_audit_report.md]`  
**Status**: `PLANNING_COMPLETE`  
**Total Phases**: 4 (decomposed into 9 micro-chunked plans)

---

## Phase Execution Checklist

### Phase 1: LLM Prompt & Adapter Ecosystem Atomic Lockdown
- [ ] **Phase 1A**: LLM Message & Prompt DTO Foundation & Core Test Migration
  - Plan: `@[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/01_phase1a_llm_models_and_prompt_dto.md]`
  - Artifacts:
    - [ ] `@[backend_v2/models/llm.py]`
    - [ ] `@[backend_v2/models/prompt.py]`
    - [ ] `@[backend_v2/llm/caching_service.py]`
    - [ ] `@[backend_v2/utils/math_utils.py]`
- [ ] **Phase 1B**: LLM Adapters, Provider Pipeline & Coupled Adapter Tests
  - Plan: `@[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/02_phase1b_llm_adapters_and_provider_pipeline.md]`
  - Artifacts:
    - [ ] `@[backend_v2/llm/provider.py]`
    - [ ] `@[backend_v2/llm/client.py]`
    - [ ] `@[backend_v2/llm/adapters/base_adapter.py]`
    - [ ] `@[backend_v2/llm/adapters/vertex_adapter.py]`
    - [ ] `@[backend_v2/llm/adapters/ai_studio_adapter.py]`
    - [ ] `@[backend_v2/llm/adapters/anthropic_adapter.py]`
    - [ ] `@[backend_v2/llm/adapters/openai_adapter.py]`
    - [ ] `@[backend_v2/llm/adapters/deepseek_adapter.py]`
    - [ ] `@[backend_v2/llm/adapters/mock_adapter.py]`
    - [ ] `@[backend_v2/llm/ingress_pipeline.py]`
    - [ ] `@[backend_v2/llm/mock.py]`
- [ ] **Phase 1C**: Coupled Service Tests & Seed Vault Pre-Flight In-Memory Validation
  - Plan: `@[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/03_phase1c_coupled_tests_and_seed_validation.md]`
  - Artifacts:
    - [ ] `@[backend_v2/seed/seed_registry.py]`
    - [ ] `@[backend_v2/seed/run_seed.py]`

### Phase 2: Service & Studio Layer DTO Elimination
- [ ] **Phase 2A**: Service Layer & Progress Tracking DTO Modernization
  - Plan: `@[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/04_phase2a_service_and_progress_dto.md]`
  - Artifacts:
    - [ ] `@[backend_v2/services/progress.py]`
    - [ ] `@[backend_v2/core/registry.py]`
    - [ ] `@[backend_v2/services/execution.py]`
    - [ ] `@[backend_v2/services/llm_task_executor.py]`
    - [ ] `@[backend_v2/services/flattener.py]`
    - [ ] `@[backend_v2/services/mcp/mcp_tool_loop.py]`
    - [ ] `@[backend_v2/utils/redis_patcher.py]`
    - [ ] `@[backend_v2/utils/dict_utils.py]`
    - [ ] `@[backend_v2/models/dtos/system.py]`
- [ ] **Phase 2B**: Studio Services, Core Seed Models & Vault Sanitization
  - Plan: `@[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/05_phase2b_studio_and_seed_models.md]`
  - Artifacts:
    - [ ] `@[backend_v2/services/studio/simulation_service.py]`
    - [ ] `@[backend_v2/services/studio/workflow_service.py]`
    - [ ] `@[backend_v2/services/studio/system_config_service.py]`
    - [ ] `@[backend_v2/services/studio/prompt_block_service.py]`
    - [ ] `@[backend_v2/services/studio/output_profile_service.py]`
    - [ ] `@[backend_v2/api/routers/studio/workflows.py]`
    - [ ] `@[backend_v2/api/routers/studio/steps.py]`
    - [ ] `@[backend_v2/api/routers/studio/prompt_blocks.py]`
    - [ ] `@[backend_v2/services/blueprint.py]`
    - [ ] `@[backend_v2/worker.py]`
    - [ ] `@[backend_v2/models/v2_core.py]`
    - [ ] `@[scripts/sanitize_seed_vault.py]`

### Phase 3: Hooks, Orchestrator & Repository Suppression Eradication
- [ ] **Phase 3A**: Hook Subsystem Suppression & Duck-Typing Eradication
  - Plan: `@[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/06_phase3a_hooks_suppression_eradication.md]`
  - Artifacts:
    - [ ] `@[backend_v2/hooks/scoring/falsifier_hook.py]`
    - [ ] `@[backend_v2/hooks/scoring/matrix_hook.py]`
    - [ ] `@[backend_v2/hooks/scoring/normalization_hook.py]`
    - [ ] `@[backend_v2/hooks/scoring/passivity_hook.py]`
    - [ ] `@[backend_v2/hooks/validation.py]`
    - [ ] `@[backend_v2/hooks/llm.py]`
    - [ ] `@[backend_v2/hooks/dlq_guard.py]`
    - [ ] `@[backend_v2/hooks/input_processing.py]`
    - [ ] `@[backend_v2/hooks/integrity.py]`
    - [ ] `@[backend_v2/hooks/source_verification_hook.py]`
    - [ ] `@[backend_v2/hooks/atom_flattening.py]`
    - [ ] `@[backend_v2/hooks/context_mapper.py]`
    - [ ] `@[backend_v2/hooks/archival.py]`
    - [ ] `@[backend_v2/hooks/security.py]`
    - [ ] `@[backend_v2/hooks/hydration.py]`
    - [ ] `@[backend_v2/hooks/metadata.py]`
    - [ ] `@[backend_v2/hooks/metrics.py]`
- [ ] **Phase 3B**: Orchestrator Subsystem Suppression & Duck-Typing Eradication
  - Plan: `@[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/07_phase3b_orchestrator_suppression_eradication.md]`
  - Artifacts:
    - [ ] `@[backend_v2/services/orchestrator/dag_executor.py]`
    - [ ] `@[backend_v2/services/orchestrator/synthesis_payload_compressor.py]`
    - [ ] `@[backend_v2/services/orchestrator/prompt_compiler.py]`
    - [ ] `@[backend_v2/services/orchestrator/prompt_compiler_adapter.py]`
    - [ ] `@[backend_v2/services/orchestrator/context_router.py]`
    - [ ] `@[backend_v2/services/orchestrator/matrix_reducer.py]`
    - [ ] `@[backend_v2/services/orchestrator/strategies/llm.py]`
    - [ ] `@[backend_v2/services/orchestrator/strategies/base.py]`
    - [ ] `@[backend_v2/services/orchestrator/strategies/logic.py]`
    - [ ] `@[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py]`
    - [ ] `@[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py]`
    - [ ] `@[backend_v2/services/orchestrator/enriched_dag_executor.py]`
    - [ ] `@[backend_v2/services/orchestrator/two_pass_atomizer.py]`
    - [ ] `@[backend_v2/services/orchestrator/synthesis_distiller.py]`
    - [ ] `@[backend_v2/services/orchestrator/matrix_explanation_service.py]`
    - [ ] `@[backend_v2/services/orchestrator/rag_preflight_service.py]`
    - [ ] `@[backend_v2/services/orchestrator/localization_compiler.py]`
    - [ ] `@[backend_v2/services/orchestrator/extraction_schema_factory.py]`
    - [ ] `@[backend_v2/services/orchestrator/anchor_validation_service.py]`
- [ ] **Phase 3C**: Repositories & Domain Models Duck-Typing Eradication
  - Plan: `@[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/08_phase3c_repositories_and_domain_models.md]`
  - Artifacts:
    - [ ] `@[backend_v2/database/repositories/execution.py]`
    - [ ] `@[backend_v2/database/repositories/component.py]`
    - [ ] `@[backend_v2/database/repositories/components/matrix.py]`
    - [ ] `@[backend_v2/database/repositories/audit.py]`
    - [ ] `@[backend_v2/database/repositories/workflow.py]`
    - [ ] `@[backend_v2/models/domain/inputs.py]`
    - [ ] `@[backend_v2/models/domain/mechanical_anchors.py]`
    - [ ] `@[backend_v2/models/dtos/evaluation_steps.py]`
    - [ ] `@[backend_v2/models/dtos/quote_evidence.py]`
    - [ ] `@[backend_v2/models/state.py]`
    - [ ] `@[backend_v2/models/domain/archivist.py]`
    - [ ] `@[backend_v2/models/dtos/matrix_scorecard.py]`

### Phase 4: AST Hardening, Knowledge Base & Architectural Governance Lockdown
- [ ] **Phase 4**: AST Hardening & Governance Lockdown
  - Plan: `@[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/09_phase4_ast_hardening_and_governance.md]`
  - Artifacts:
    - [ ] `@[scripts/_ast_guardrails.py]`
    - [ ] `@[scripts/backend_audit_loop.py]`
    - [ ] `@[.agents/rules/01-python-backend.md]`
    - [ ] `@[.agents/rules/03_seed_vault.md]`

---

# Session Handover Context

## Achieved
- Ingested and verified `EPIC_150_Zero_Permissive_Typing_Lockdown.md` and `EPIC_150_audit_report.md`.
- Created task directory `docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/`.
- Decomposed Epic 150 into 9 sequentially numbered, micro-chunked execution sub-plans with 100% type fidelity, explicit `<contract_freeze>`, `<touched_artifacts>`, `<demolish>`, and `<test_contracts>` blocks.
- Generated canonical Epic Tracker `docs/epic/EPIC_150_tracker.md`.

## Learned
- **Baseline Invariants**: Enforced Subsystem-Atomic Vertical Slicing to prevent CI Pipeline Deadlocks. Locked LiteLLM message serialization to `[m.model_dump(mode="json", exclude_none=True) if isinstance(m, BaseModel) else m for m in messages]` to prevent 400 Bad Request null-field leakage.
- **SSE & Progress State Isolation**: Confirmed `ProgressState` is internal to services; external SSE stream serializes `ExecutionRecord.model_dump_json()`. Database progress updates must strictly adhere to `ExecutionRecord` fields.
- **Seeder Boot Crash Vulnerability**: Locked Two-Phase Pre-Flight In-Memory Validation pattern in `run_seed.py`.

## Remaining
- Execute `/tier0-research-plan` on Phase 1A plan (`01_phase1a_llm_models_and_prompt_dto.md`).

## Resume Command
```powershell
/tier0-research-plan @[docs/epic/tasks_EPIC_150_Zero_Permissive_Typing_Lockdown/01_phase1a_llm_models_and_prompt_dto.md] @[docs/epic/EPIC_150_tracker.md]
```
