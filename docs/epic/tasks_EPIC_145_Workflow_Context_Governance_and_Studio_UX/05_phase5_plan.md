# Phase 5: Verification, Widget Testing & E2E Integration Gate

**Overview:** Implements comprehensive unit, negative, and ISTQB equivalence partition test suite for SynthesisPayloadCompressor, Studio step protection tests, Flutter widget tests for WorkflowStepCard, and executes live E2E REST API verification gate.
**Source:** @[docs/epic/EPIC_145_Workflow_Context_Governance_and_Studio_UX.md#L252-L284] Phase 5: Verification, Widget Testing & E2E Integration Gate
**Target Files:**
- `[NEW]` @[backend_v2/tests/unit/services/orchestrator/test_synthesis_payload_compressor.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_studio.py#L238-L252]
- `[MODIFY]` @[client_app_v2/test/models/domain_parity_test.dart]
- `[MODIFY]` @[client_app_v2/test/features/studio/models/workflow_test.dart]
- `[NEW]` @[client_app_v2/test/features/studio/views/widgets/workflow/workflow_step_card_test.dart]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 4. Verify that Flutter UI components and backend services are fully functional.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true across all test suites.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_145_Workflow_Context_Governance_and_Studio_UX.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [ ] Comprehensive unit, negative, and ISTQB equivalence partition tests implemented in [NEW] @[backend_v2/tests/unit/services/orchestrator/test_synthesis_payload_compressor.py].
    - [ ] System core protection test `test_delete_step_protected_system_core_fails_fast` implemented in @[backend_v2/tests/unit/services/test_studio.py#L238-L252].
    - [ ] Flutter widget test [NEW] @[client_app_v2/test/features/studio/views/widgets/workflow/workflow_step_card_test.dart] verifies 3-zone rendering and toggle callbacks.
    - [ ] Domain parity test @[client_app_v2/test/models/domain_parity_test.dart] passes.
    - [ ] Live E2E REST API verification gate passes with zero errors.
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
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
  </touched_artifacts>

  <anti_targets>
    - Do NOT skip negative test cases or ISTQB partition coverage.
    - Do NOT use live external LLM calls during standard unit tests.
  </anti_targets>

  <step id="1" name="Deferred Phase Implementation">
    <action>[DEFERRED_TO_TIER_1_RE_PLANNING] Detailed execution steps will be generated upon completion of Phase 2 based on updated codebase state. Refer to Epic source: @[docs/epic/EPIC_145_Workflow_Context_Governance_and_Studio_UX.md#L252-L284].</action>
  </step>

  <validation_gate>
    <action>Execute Backend Unit Tests: `uv run pytest backend_v2/tests/unit/services/orchestrator/test_synthesis_payload_compressor.py -v`</action>
    <action>Execute Studio Step Tests: `uv run pytest backend_v2/tests/unit/services/test_studio.py#L238-L252 -k "test_delete_step" -v`</action>
    <action>Execute Flutter Widget Tests: `uv run flutter test client_app_v2/test/features/studio/views/widgets/workflow/workflow_step_card_test.dart`</action>
    <action>Execute Mandatory Final E2E REST API Verification Gate (PowerShell): `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py -k "test_synthesis"`</action>
    <action>Execute Mandatory Final E2E REST API Verification Gate (Bash): `RUN_LIVE_E2E=true uv run pytest backend_v2/tests/integration/test_integration_real_llm.py -k "test_synthesis"`</action>
  </validation_gate>
</execution_protocol>
```
