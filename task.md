# Task Checklist: Tripartite Pipeline Isolation, Worker Decoupling & Report Artifact CRUD

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

## Phase A: God Code Decomposition & Ghost Field Purge (Steps 1–2)
- [x] **Step 1: PRE_IMPLEMENTATION_CLEANUPS_CORE_MODEL_DECOMPOSITION_AND_DTO_LOCK**
  - [x] 1.1: Modify @[backend_v2/models/dtos/trace.py] — Make `output_profile_id` optional (`str | None = None`)
  - [x] 1.2: Sub-batch 1 — Create @[backend_v2/models/domain/matrix.py] (~260 lines): Extract `TheoryGrounding`, `AcceptanceCriterion`, `AntiPattern`, `ContrastivePairDTO`, `TDAAssertion`, `MatrixClaim`, `MatrixRow`, `MatrixScale`
  - [x] 1.3: Sub-batch 2 — Create @[backend_v2/models/domain/system_config.py] (~160 lines): Extract `ChatMessageDTO`, `ChatHistoryDTO`, `DataDictionaryField`, `ProviderExtraParamsDTO`, `ModelProfile`, `SystemConfigModelRegistry`, `AllowedMCPTool`, `MCPAuditTrace`, `SystemConfigMCPGateways`
  - [x] 1.4: Sub-batch 3 — Create @[backend_v2/models/domain/step.py] (~260 lines): Extract `Step`, `StepRule`, `Role`, `QuestionnaireItem`, `ExpectedInput`
  - [x] 1.5: Sub-batch 4 — Create @[backend_v2/models/domain/workflow.py] (~160 lines): Extract `Workflow`, purge `allowed_exports`
    - [x] 1.5a: Delete `allowedExports` from @[client_app_v2/lib/features/studio/models/workflow.dart]
    - [x] 1.5b: Purge `allowed_exports` from @[backend_v2/models/dtos/studio.py] (`_default_allowed_exports`, `WorkflowCreateDTO.allowed_exports`, `WorkflowUpdateDTO.allowed_exports`)
    - [x] 1.5c: Purge `allowed_exports` from @[backend_v2/services/studio/workflow_service.py]
    - [x] 1.5d: Purge `allowed_exports` from @[backend_v2/tests/factories/model_factories.py]
    - [x] 1.5e: Purge `allowed_exports` from @[backend_v2/seed/seed_data.json] (6 workflow entries), run preflight validation and seed sync
  - [x] 1.6: Sub-batch 5 — Create @[backend_v2/models/domain/execution.py] (~250 lines): Extract `FrozenContext`, `ExecutionCreate`, `ExecutionStep`, `ExecutionSummarySnapshot`, `EvaluatedMatrixContextDTO`, `ExecutionRecord`, `JobAcceptedDTO`, `EvidenceRejectionRequest`
  - [x] 1.7: Sub-batch 6 — Create remaining DTOs and presentation models
    - [x] 1.7a: Create @[backend_v2/models/dtos/atom_result.py] (~110 lines): Extract `ErrorDetailsDTO`, `HydratedAtomDTO`, `ExtractedValueDTO`, `AtomResultDTO`, `ExecutionMetricsDTO`, `ExtensionMetricsDTO`
    - [x] 1.7b: Modify @[backend_v2/models/domain/synthesis.py] (~160 lines): Consolidate `MatrixSynthesisGroup`, `RenderedSynthesisCache`, `BaseMatrixXAI`, `BaseTDAExtraction`
    - [x] 1.7c: Modify @[backend_v2/models/domain/output_profile.py] (~300 lines): Elevate to canonical `OutputProfile` domain model with `variance_target_block` and `user_role_target_block`
    - [x] 1.7d: Synchronize @[backend_v2/models/dtos/output_profile.py]: Maintain strict typed validation on `OutputProfileCreateDTO` and `OutputProfileUpdateDTO`
    - [x] 1.7e: Create @[backend_v2/models/dtos/report_data.py] (~80 lines): Extract `ReportDataDTO`
  - [x] 1.8: Sub-batch 7 — Refactor @[backend_v2/models/v2_core.py] into Strangler Fig Facade (<90 lines) with `__all__` re-exports
- [x] (c4ab0994) **Step 2: INGRESS_DECOUPLING_IN_EXECUTION_SERVICE**
  - [x] 2.1: Modify @[backend_v2/services/execution.py] — Decouple `start_execution` from mandatory `output_profile_id`
  - [x] 2.2: Modify @[backend_v2/services/orchestrator/dag_executor.py] — Delete `sys_render_*` virtual step injection
  - [x] 2.3: Execute `/tier5-session-handover` (Phase A → Phase B checkpoint)

## Phase B: Worker & Service Decoupling (Steps 3–7)
- [ ] **Step 3: WORKER_DECOMPOSITION_AND_LIFECYCLE_ISOLATION**
- [ ] **Step 4: MAKE_BLUEPRINT_TRANSFORMER_READ_ONLY**
- [ ] **Step 5: EXTRACT_EXPORT_SERVICE_AND_ELIMINATE_ARB_LEAK**
- [ ] **Step 6: REPORT_ARTIFACT_DOMAIN_MODEL_AND_REPOSITORY_CRUD**
- [ ] **Step 7: DECOMPOSE_EXECUTION_SERVICES_AND_CREATE_REPORT_SERVICE**

## Phase C: REST API, Flutter UI & Documentation (Steps 8–12)
- [ ] **Step 8: REPORT_ARTIFACT_REST_API_ENDPOINTS**
- [ ] **Step 9: DESKTOP_PRO_TOOL_STUDIO_UX_FOR_REPORT_ARTIFACTS**
- [ ] **Step 10: AUTOMATED_REGRESSION_VERIFICATION_AND_QUALITY_GATES**
- [ ] **Step 11: KNOWLEDGE_BASE_DOCUMENTATION_AND_KI_SYNCHRONIZATION**
- [ ] **Step 12: TIER_7_AS_BUILT_ARCHITECTURE_SYNCHRONIZATION**

# Session Handover Context
- Plan: @[docs/implementationplans/IMPLEMENTATION_PLAN_Tripartite_Pipeline_Isolation_and_Worker_Decoupling.md]
- Tracker: @[docs/implementationplans/TRACKER_Tripartite_Pipeline_Isolation_and_Worker_Decoupling.md]
- Status: Phase A Complete (Steps 1 & 2 done and verified), Ready for Phase B Step 3

## Achieved
- **Phase A (God Code Decomposition & Ghost Field Purge)** completed 100%:
  - **Step 1** (commit `ce69d34a`): Decomposed monolithic `v2_core.py` into canonical domain modules (`matrix.py`, `system_config.py`, `step.py`, `workflow.py`, `execution.py`, `synthesis.py`, `output_profile.py`) and DTOs (`atom_result.py`, `report_data.py`). Purged legacy `allowed_exports` across Python and Flutter models and database seeds.
  - **Step 2** (commit `c4ab0994`):
    - Decoupled `ExecutionService.start_execution` in @[backend_v2/services/execution.py] from mandatory `output_profile_id`: falls back to `workflow.default_profile_id` when present, allows `None`, validates profile if provided (raises 404 RESOURCE_NOT_FOUND if missing from DB), and strictly validates `resolved_registry_id` against `SystemConfigRepository.get_model_registry()` (raises 404 RESOURCE_NOT_FOUND if missing).
    - Eradicated virtual `sys_render_*` step injection in @[backend_v2/services/orchestrator/dag_executor.py] across both initial and resumption execution paths.
    - Updated and expanded unit test suite: 62 tests passing in @[backend_v2/tests/unit/services/test_execution.py] (93% coverage) and 22 tests passing in @[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py] (90% coverage).
    - Passed Ruff check/format, MyPy strict typing, AST guardrails, Jinja template validation, seed validation, and Pytest coverage gates.

## Learned
- `Workflow` domain model enforces strict `ConfigDict(strict=True, extra="forbid")`. Test fixtures attempting to pass legacy `allowed_exports` trigger Pydantic validation errors.
- `OutputProfile` enforces `target_block_order` consistency: if `MATRIX_GRAPHS_BLOCK` is present, `matrix_synthesis_groups` must not be empty. Setting `target_block_order=[]` allows minimal testing fixtures without declaring synthesis groups.
- `StepRule` does not have an `order` field (sequence is determined by array position in `Workflow.steps`).
- `Step` requires `extraction_protocol_block_id`.
- `ExecutionService.stream_status` authorizes the connection first via `get_execution` before entering the polling loop.

## Remaining
- **Phase B: Worker & Service Decoupling (Steps 3–7)**:
  - **Step 3**: WORKER_DECOMPOSITION_AND_LIFECYCLE_ISOLATION
    - 3.1: Execute Golden Master characterization test (`--cov=backend_v2.worker`)
    - 3.2: Execute AST boundary analysis on @[backend_v2/worker.py]
    - 3.3: Create @[backend_v2/workers/__init__.py]
    - 3.4: Create @[backend_v2/workers/execution_worker.py] (<400 lines): Extract `execute_workflow_job`, eradicate `render_profile_job` auto-enqueue, enforce Zero-Import Boundary
    - 3.5: Create @[backend_v2/workers/report_worker.py] (<450 lines): Extract `generate_pdf_job`, `generate_pdf_task`, `render_profile_job`, `generate_profile_synthesis_and_pdf_task`, register `generate_report_artifact_job`
    - 3.6: Refactor @[backend_v2/worker.py] into Strangler Fig Facade & Entrypoint (<150 lines) with `__all__` re-exports
  - **Step 4**: MAKE_BLUEPRINT_TRANSFORMER_READ_ONLY
  - **Step 5**: EXTRACT_EXPORT_SERVICE_AND_ELIMINATE_ARB_LEAK
  - **Step 6**: REPORT_ARTIFACT_DOMAIN_MODEL_AND_REPOSITORY_CRUD
  - **Step 7**: DECOMPOSE_EXECUTION_SERVICES_AND_CREATE_REPORT_SERVICE
- **Phase C: REST API, Flutter UI & Documentation (Steps 8–12)**
