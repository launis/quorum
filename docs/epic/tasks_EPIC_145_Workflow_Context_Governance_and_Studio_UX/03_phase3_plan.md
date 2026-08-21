# Phase 3: Backend Domain & Synthesis Payload Compression Hardening

**Overview:** Hardens SynthesisPayloadCompressor with unbounded mode and deterministic prioritized stratification, upgrades MatrixExplanationService with profile-level config overrides and candidate pre-deduplication, filters synthesis source steps in synthesis_distiller_hook, and enforces system core protection in StudioWorkflowService.
**Source:** @[docs/epic/EPIC_145_Workflow_Context_Governance_and_Studio_UX.md#L140-L192] Phase 3: Backend Domain & Synthesis Payload Compression Hardening
**Target Files:**
- `[MODIFY]` @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L17-L163]
- `[MODIFY]` @[backend_v2/services/orchestrator/synthesis_distiller.py#L171-L344]
- `[MODIFY]` @[backend_v2/services/orchestrator/matrix_explanation_service.py#L25-L224]
- `[MODIFY]` @[backend_v2/services/orchestrator/matrix_explanation_service.py#L28-L224]
- `[MODIFY]` @[backend_v2/services/studio/workflow_service.py#L481-L504]
- `[MODIFY]` @[backend_v2/services/studio/workflow_service.py#L448-L479]
- `[MODIFY]` @[backend_v2/api/routers/studio/steps.py#L100-L119]
- `[MODIFY]` @[backend_v2/api/routers/studio/steps.py#L122-L142]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_studio.py#L238-L252]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 2. Verify that seed data and Step models are fully migrated.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true for synthesis payload compression and matrix explanation services.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_145_Workflow_Context_Governance_and_Studio_UX.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [ ] `SynthesisPayloadCompressor._strip_heavy_keys` strips `hydrated_references` and internal metadata without fallback chains.
    - [ ] Prioritized stratification applied when `settings.max_synthesis_evaluations > 0` and unbounded when `0`.
    - [ ] `synthesis_distiller_hook` filters steps by `StepRule.is_synthesis_source`.
    - [ ] `MatrixExplanationService` accepts `SynthesisConfigDTO` overrides with candidate pre-deduplication.
    - [ ] `StudioWorkflowService` enforces `SYSTEM_PROTECTED_RESOURCE` on deletion or mutation of system core steps.
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <ki>@[ki_synthesis_payload_compression.md]</ki>
    <ki>@[ki_sdui_matrix_synthesis.md]</ki>
    <ki>@[ki_tripartite_pipeline_architecture.md]</ki>
    <ki>@[ki_god_code_prevention.md]</ki>
    <ki>@[ki_dual_axis_localization_architecture.md]</ki>
    <ki>@[ki_strict_sdui_serialization.md]</ki>
    <ki>@[ki_python_314_concurrency_strictness.md]</ki>
    <ki>@[ki_global_config_sovereignty.md]</ki>
    <ki>@[ki_matrix_boolean_evaluation_strictness.md]</ki>
    <ki>@[ki_ai_testing_standards.md]</ki>
    <ki>@[ki_dag_engine_dto_projection_rules.md]</ki>
    <ki>@[ki_neuro_symbolic_agentic_workflow.md]</ki>
    <ki>@[ki_flat_polymorphic_pipeline.md]</ki>
    <ki>@[ki_sdui_adapter_pattern.md]</ki>
  </required_context_rules>

  <touched_artifacts>
    <backend>@[backend_v2/services/orchestrator/synthesis_payload_compressor.py]</backend>
    <backend>@[backend_v2/services/orchestrator/synthesis_distiller.py]</backend>
    <backend>@[backend_v2/services/orchestrator/matrix_explanation_service.py]</backend>
    <backend>@[backend_v2/services/studio/workflow_service.py]</backend>
    <backend>@[backend_v2/api/routers/studio/steps.py]</backend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT modify Flutter frontend UI widgets in Phase 3.
    - Do NOT use raw dicts or duck-typing in compressor logic.
  </anti_targets>

  <step id="1" name="Deferred Phase Implementation">
    <action>[DEFERRED_TO_TIER_1_RE_PLANNING] Detailed execution steps will be generated upon completion of Phase 2 based on updated codebase state. Refer to Epic source: @[docs/epic/EPIC_145_Workflow_Context_Governance_and_Studio_UX.md#L140-L192].</action>
  </step>

  <validation_gate>
    <action>Execute Backend Audit Loop: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/synthesis_payload_compressor.py --test`</action>
    <action>Execute Studio Service Tests: `uv run pytest backend_v2/tests/unit/services/test_studio.py#L238-L252 -v`</action>
  </validation_gate>
</execution_protocol>
```
