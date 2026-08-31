# Phase 3: Hooks, Orchestrator & Repository Suppression Eradication

> **STATUS: DEFERRED** — This is a placeholder. Run `/tier0-create-plan @[docs/epic/EPIC_150_Zero_Permissive_Typing_Lockdown.md] @[docs/epic/EPIC_150_tracker.md]` to generate the full implementation plan for this phase.

## Scope Summary

Remove all `# noqa: QGR` inline suppressions and all `isinstance(..., dict)` duck-typing checks across hooks, orchestrator, repositories, and domain models. This is the largest bulk phase but primarily mechanical.

## Target Files (~40 files)

### Hooks (17 files)
- `@[backend_v2/hooks/scoring/falsifier_hook.py]`
- `@[backend_v2/hooks/scoring/matrix_hook.py]`
- `@[backend_v2/hooks/scoring/normalization_hook.py]`
- `@[backend_v2/hooks/scoring/passivity_hook.py]`
- `@[backend_v2/hooks/validation.py]`
- `@[backend_v2/hooks/llm.py]`
- `@[backend_v2/hooks/dlq_guard.py]`
- `@[backend_v2/hooks/input_processing.py]`
- `@[backend_v2/hooks/integrity.py]`
- `@[backend_v2/hooks/source_verification_hook.py]`
- `@[backend_v2/hooks/atom_flattening.py]`
- `@[backend_v2/hooks/context_mapper.py]`
- `@[backend_v2/hooks/archival.py]`
- `@[backend_v2/hooks/security.py]`
- `@[backend_v2/hooks/hydration.py]`
- `@[backend_v2/hooks/metadata.py]`
- `@[backend_v2/hooks/metrics.py]`

### Orchestrator (19 files)
- `@[backend_v2/services/orchestrator/dag_executor.py]`
- `@[backend_v2/services/orchestrator/synthesis_payload_compressor.py]`
- `@[backend_v2/services/orchestrator/prompt_compiler.py]`
- `@[backend_v2/services/orchestrator/prompt_compiler_adapter.py]`
- `@[backend_v2/services/orchestrator/context_router.py]`
- `@[backend_v2/services/orchestrator/matrix_reducer.py]`
- `@[backend_v2/services/orchestrator/strategies/llm.py]`
- `@[backend_v2/services/orchestrator/strategies/base.py]`
- `@[backend_v2/services/orchestrator/strategies/logic.py]`
- `@[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py]`
- `@[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py]`
- `@[backend_v2/services/orchestrator/enriched_dag_executor.py]`
- `@[backend_v2/services/orchestrator/two_pass_atomizer.py]`
- `@[backend_v2/services/orchestrator/synthesis_distiller.py]`
- `@[backend_v2/services/orchestrator/matrix_explanation_service.py]`
- `@[backend_v2/services/orchestrator/rag_preflight_service.py]`
- `@[backend_v2/services/orchestrator/localization_compiler.py]`
- `@[backend_v2/services/orchestrator/extraction_schema_factory.py]`
- `@[backend_v2/services/orchestrator/anchor_validation_service.py]`

### Repositories (5 files)
- `@[backend_v2/database/repositories/execution.py]`
- `@[backend_v2/database/repositories/component.py]`
- `@[backend_v2/database/repositories/components/matrix.py]`
- `@[backend_v2/database/repositories/audit.py]`
- `@[backend_v2/database/repositories/workflow.py]`

### Domain Models (~7 files)
- `@[backend_v2/models/domain/inputs.py]`
- `@[backend_v2/models/domain/mechanical_anchors.py]`
- `@[backend_v2/models/dtos/evaluation_steps.py]`
- `@[backend_v2/models/dtos/quote_evidence.py]`
- `@[backend_v2/models/state.py]`
- `@[backend_v2/models/domain/archivist.py]`
- `@[backend_v2/models/dtos/matrix_scorecard.py]`
