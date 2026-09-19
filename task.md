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
- [ ] **Step 2: INGRESS_DECOUPLING_IN_EXECUTION_SERVICE**
  - [x] 2.1: Modify @[backend_v2/services/execution.py] — Decouple `start_execution` from mandatory `output_profile_id`
  - [x] 2.2: Modify @[backend_v2/services/orchestrator/dag_executor.py] — Delete `sys_render_*` virtual step injection
  - [ ] 2.3: Execute `/tier5-session-handover` (Phase A → Phase B checkpoint)

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
- Status: Initialized Phase A Step 1
