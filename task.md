# Codebase-Wide State Eradication of dict[str, Any] & Double-Serialization Elimination Tracker

## Plan Context
- Source Plan: `@[docs/implementationplans/plan_dict_to_dto_state_eradication.md]`
- Status: In Progress (Step-by-Step Mode)

## Tasks Checklist

- [x] **Step 0: Phase 1 Pre-Implementation Cleanups & AST Baseline**
  - [x] Execute baseline AST scan: `uv run python scripts/audit_dict_eradication.py backend_v2 --strict`
  - [x] Review `ki_python_314_concurrency_strictness.md`
  - [x] Sanitize Presidio NLP model cache in `@[backend_v2/services/pii_analyzer.py#L18-L22]` (`dict[str, object]`)
  - [x] Sanitize settings model registry in `@[backend_v2/settings.py#L52-L851]` (`SystemConfigModelRegistry | None`)
  - [x] Sanitize settings safety settings in `@[backend_v2/settings.py#L424-L449]` (`list[SafetySettingDTO]`)
  - [x] Sanitize simulation service clean mocks in `@[backend_v2/services/studio/simulation_service.py#L170-L351]` (`dict[str, str]`)
  - [x] Run quality gate: `uv run python scripts/backend_audit_loop.py backend_v2/services/pii_analyzer.py --test`

- [ ] **Step 1: Core DTO Models & Sealed State Transit Payload Unions**
  - [ ] Define payload DTOs in `@[backend_v2/models/dtos/hook_delta.py]`: `PassivityDetectionResultDTO`, `AnomalyRetryResultDTO`, `InputControlRatioResultDTO`, `ExternalEvidenceResultDTO`, `ExecutionMetadataDeltaDTO`, `ArchivistPrecedentsResultDTO`, `StepContextMetadataDTO`, `WorkerJobResultDTO`
  - [ ] Assemble closed union `HookPayloadDTO` in `@[backend_v2/models/dtos/hook_delta.py]` (reusing `FlatteningHookOutput` from `atom_flattening.py`)
  - [ ] Update `HookDeltaDTO`: `delta: HookPayloadDTO | None`, `metadata_updates: ExecutionMetadataDeltaDTO | None`, eradicate `| dict[str, Any]`
  - [ ] Update `@[backend_v2/models/dtos/step_output.py]`: `frozen=True`, `StepPayloadValue` closed union, constrain `payload: StepPayloadValue`
  - [ ] Update `@[backend_v2/models/dtos/context_variables.py]`: tighten blackboard, matrix reducer, report_context, step_detector, evaluated_matrices, and variables to `dict[str, DomainInputValue]`
  - [ ] Update `@[backend_v2/models/execution_core.py]`: tighten `global_context_vars: GlobalContextVarsDTO | None`
  - [ ] Update `@[backend_v2/models/dtos/engine.py]`: tighten `synthesis_output: BaseModel | None`
  - [ ] Run quality gate on models: `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/hook_delta.py --test`

- [ ] **Step 2: Sovereign State Reducer & Context Router Decoupling**
  - [ ] Update `@[backend_v2/services/orchestrator/state_reducer.py]`: pure constructor in `merge_execution_inputs`, implement `reduce_hook_delta`
  - [ ] Update `@[backend_v2/services/orchestrator/context_router.py]`: delete `SnapshotState`, refactor `normalize_and_validate_variable(path, steps: Sequence[StepOutputDTO])`, refactor `validate_routing_mode`
  - [ ] Update `@[backend_v2/services/orchestrator/dag_executor.py]`: pass `projector.snapshot` directly to `ContextRouter.normalize_and_validate_variable`, sanitize signatures
  - [ ] Run quality gate: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/state_reducer.py --test`

- [ ] **Step 3: Execution Strategies & Context Builder Decoupling**
  - [ ] Update `@[backend_v2/services/orchestrator/strategies/base.py]`: delegate pre-hooks and post-hooks to `state_reducer.reduce_hook_delta`, eradicate `isinstance(delta, Mapping)`
  - [ ] Update `@[backend_v2/services/orchestrator/strategies/llm.py]`: `_extract_step_context_metadata` returning `StepContextMetadataDTO`, dot notation access
  - [ ] Update `@[backend_v2/services/orchestrator/strategies/logic.py]`: delegate to `state_reducer.reduce_hook_delta`
  - [ ] Update `@[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py]`: document terminal rendering boundary in `_project_compressed`, constrain `build()` signatures
  - [ ] Run quality gate: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/base.py --test`

- [ ] **Step 4: Step Lifecycle, Hook Contracts & State Reducer Integration**
  - [ ] Modernize all 24 hooks across 18 modules to return typed DTOs directly in `HookDeltaDTO`:
    - [ ] `atom_flattening.py`: `FlatteningHookOutput`
    - [ ] `synthesis_distiller.py`: `distillation_dto`
    - [ ] `security.py`: `sanitization_dto`
    - [ ] `references.py`: `bibliography_dto`
    - [ ] `validation.py`: `validation_dto`, `AnomalyRetryResultDTO`
    - [ ] `scoring/passivity_hook.py`: `PassivityDetectionResultDTO`
    - [ ] `metrics.py`: `InputControlRatioResultDTO`, `audit_metrics`
    - [ ] `scoring/matrix_hook.py`: `matrix_hook_result`
    - [ ] `interaction_hook.py`: `response_dto`
    - [ ] `linguistics.py`: `result_dto`
    - [ ] `scoring/falsifier_hook.py`: `score_dto`
    - [ ] `scoring/normalization_hook.py`: `matrix_dto`
    - [ ] `source_verification_hook.py`: `ExternalEvidenceResultDTO`, `ExecutionMetadataDeltaDTO`
    - [ ] `llm.py`: `llm_config`
    - [ ] `input_processing.py`: `ExecutionMetadataDeltaDTO(estimated_token_count=...)`
    - [ ] `hydration.py`: `raw_inputs`
    - [ ] `integrity.py`: `parsed_payload`
    - [ ] `archival.py`: `ArchivistPrecedentsResultDTO`
  - [ ] Run quality gate: `uv run pytest backend_v2/tests/unit/hooks/`

- [ ] **Step 5: Background Workers & Task Pipeline Modernization**
  - [ ] Modernize `@[backend_v2/workers/execution_worker.py]`: `inputs: ExecutionInputsDTO`, return `WorkerJobResultDTO`
  - [ ] Modernize `@[backend_v2/workers/synthesis_tasks.py]`: `list[ChatMessageDTO]` message arrays
  - [ ] Modernize `@[backend_v2/workers/synthesis_worker.py]`: `dict[str, RenderedSynthesisCache]`
  - [ ] Modernize `@[backend_v2/workers/variance_synthesis.py]`: `list[ChatMessageDTO]`
  - [ ] Run quality gate: `uv run python scripts/backend_audit_loop.py backend_v2/workers/execution_worker.py --test`

- [ ] **Step 6: Orchestrator Services, Compilers, Registry & Compressor Modernization**
  - [ ] Modernize `@[backend_v2/services/orchestrator/rag_preflight_service.py]`: return `GlobalAtomBlackboard`, `ExecutionInputsDTO`
  - [ ] Modernize `@[backend_v2/services/orchestrator/prompt_compiler.py]` & adapter: `Sequence[StepOutputDTO]`, `ExecutionInputsDTO | LLMContextDataDTO`
  - [ ] Modernize `@[backend_v2/services/orchestrator/schema_factory.py]`: `Sequence[StepOutputDTO]`
  - [ ] Modernize `@[backend_v2/core/registry.py]`: `Sequence[StepOutputDTO]`, eradicate `isinstance(atom_item, Mapping)`
  - [ ] Modernize `@[backend_v2/services/orchestrator/synthesis_payload_compressor.py]`: `BaseModel | StepPayloadValue`, `Sequence[EvaluatedAtomDTO]`
  - [ ] Run quality gate: `uv run python scripts/backend_audit_loop.py backend_v2/core/registry.py --test`

- [ ] **Step 7: Utilities & Shared Service Sanitization**
  - [ ] Modernize or prune `hydrate_dict_list` in `@[backend_v2/utils/alias_engine.py]`
  - [ ] Clean `model_pricing_config` in `@[backend_v2/services/usage_service.py]`
  - [ ] Clean `clean_mocks` in `@[backend_v2/services/studio/simulation_service.py]`
  - [ ] Run quality gate: `uv run python scripts/backend_audit_loop.py backend_v2/utils/alias_engine.py --test`

- [ ] **Step 8: Test Fixture Modernization & Unit Verification**
  - [ ] Modernize unit test fixtures (`test_context_router.py`, `test_state_reducer.py`, `test_strategies_base.py`, `test_rag_preflight_service.py`, `test_worker.py`, etc.)
  - [ ] Implement ISTQB negative test scenarios (raw dict in delta, orphaned step, legacy `.output`, etc.)
  - [ ] Run unit test suite across modified modules

- [ ] **Step 9: Quality Gates & AST Guardrails Verification**
  - [ ] Run `uv run python scripts/audit_dict_eradication.py backend_v2 --strict`
  - [ ] Run `uv run python scripts/backend_audit_loop.py backend_v2 --test`
  - [ ] Run `uv run python scripts/audit_markdown_boundaries.py --file docs/implementationplans/plan_dict_to_dto_state_eradication.md`

## Session Handover Context
- **Achieved:** Initialized execution tracking and loaded all required context rules and knowledge items.
- **Learned:** None yet.
- **Remaining:** Execute Step 0 through Step 9 systematically.
