# Phase 5: Verification, Widget Testing & E2E Integration Gate

**Overview:** Consolidates and implements comprehensive unit, negative, and ISTQB equivalence partition test suite for SynthesisPayloadCompressor in canonical location, migrates and deletes legacy proxy test file, verifies Studio step protection and direct organization_id access tests, validates Flutter widget and domain parity tests, and executes live E2E REST API verification gate.
**Source:** @[docs/epic/EPIC_145_Workflow_Context_Governance_and_Studio_UX.md#L252-L284] Phase 5: Verification, Widget Testing & E2E Integration Gate
**Target Files:**
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_synthesis_payload_compressor.py]
- `[DELETE]` @[backend_v2/tests/unit/test_synthesis_payload_compression.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_studio.py#L238-L252]
- `[MODIFY]` @[client_app_v2/test/models/domain_parity_test.dart]
- `[MODIFY]` @[client_app_v2/test/features/studio/models/workflow_test.dart]
- `[MODIFY]` @[client_app_v2/test/features/studio/views/widgets/workflow/workflow_step_card_test.dart]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 4. Verify that Flutter UI components, StepBuilderView protection, WorkflowStepCard 3-zone architecture, and backend services are fully functional.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true across all test suites.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_145_Workflow_Context_Governance_and_Studio_UX.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [x] Canonical test suite in @[backend_v2/tests/unit/services/orchestrator/test_synthesis_payload_compressor.py] contains 16 comprehensive unit, negative, and ISTQB equivalence partition tests directly, and legacy file @[backend_v2/tests/unit/test_synthesis_payload_compression.py] is deleted.
    - [x] Studio workflow tests in @[backend_v2/tests/unit/services/test_studio.py#L238-L252] verify `test_delete_step`, `test_delete_step_protected_system_core_fails_fast`, `test_save_step_protected_system_core_slug_mutation_fails_fast`, and `test_save_step_direct_organization_id_access`.
    - [x] Flutter widget tests in @[client_app_v2/test/features/studio/views/widgets/workflow/workflow_step_card_test.dart] verify 5 positive and 2 negative ISTQB test scenarios across all 3 zones.
    - [x] Domain parity test in @[client_app_v2/test/models/domain_parity_test.dart] and workflow model tests in @[client_app_v2/test/features/studio/models/workflow_test.dart] pass with zero errors.
    - [x] Full backend audit loop (`backend_audit_loop.py`) and Flutter audit loop (`flutter_audit_loop.py`) pass 100% green.
    - [x] Mandatory Live E2E REST API verification gate (`test_integration_real_llm.py`) passes with zero HTTP errors.
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
    - Do NOT retain legacy proxy test file @[backend_v2/tests/unit/test_synthesis_payload_compression.py] after consolidating into canonical location.
    - Do NOT skip negative test cases or ISTQB partition coverage.
    - Do NOT use live external LLM calls during standard unit tests.
    - Do NOT use generic duck typing (getattr) in Studio tests.
  </anti_targets>

  <step id="1" name="Backend Canonical Test Consolidation &amp; Studio Protection Verification">
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_synthesis_payload_compressor.py], consolidate and migrate all 16 test implementations directly from @[backend_v2/tests/unit/test_synthesis_payload_compression.py], covering:
      1. `test_compress_payload_unbounded_when_zero_evaluations_limit`: Proves when `max_synthesis_evaluations == 0`, all evaluations forward without truncation.
      2. `test_compress_payload_prioritized_stratification_retains_critical_deficits_over_passes`: Proves 70% deficit allocation and dynamic budget spillover.
      3. `test_compress_payload_stratification_is_100_percent_deterministic_with_tiebreakers`: Proves deterministic multi-key sorting `(-len(exact_quotes), atom_id)` with canonical `atom_id` tie-breaker.
      4. `test_compress_payload_strips_hydrated_references_and_heavy_keys`: Proves stripping of `"hydrated_references"`, `"shuffled_atoms"`, `"atom_quotes"`, `"_step_metadata"`, `"_audit_signature"`, `"_evaluative_matrices"`.
      5. `test_compress_payload_with_results_only_no_evaluations`: Proves discriminator routing for `"results"` payloads.
      6. `test_compress_payload_evaluations_empty_after_compression_fails_fast`: Proves fail-fast `AppException(VALIDATION_FAILED)` when all quotes are empty/invalid.
      7. `test_compress_payload_heterogeneous_dag_types`: Proves all 4 ISTQB partitions (Structured Dict, List, String/Markdown, Scalar/Empty).
      8. `test_compress_synthesis_payload_strips_atom_quotes`
      9. `test_compress_synthesis_payload_negative_empty_input`
      10. `test_compress_synthesis_payload_string_input`
      11. `test_compress_synthesis_payload_scalar_input`
      12. `test_compress_synthesis_payload_negative_invalid_types`
      13. `test_compress_synthesis_payload_basemodel_input`
      14. `test_compress_synthesis_payload_negative_non_dict_evaluation`
      15. `test_compress_synthesis_payload_negative_missing_mandatory_field`
      16. `test_compress_synthesis_payload_negative_validation_error`</action>
    <action>Delete the legacy proxy test file @[backend_v2/tests/unit/test_synthesis_payload_compression.py] to ensure single source of truth.</action>
    <action>In @[backend_v2/tests/unit/services/test_studio.py#L238-L252], implement and verify:
      1. `test_delete_step`: Proves normal specialist step deletion.
      2. `test_delete_step_protected_system_core_fails_fast`: Proves `AppException(SYSTEM_PROTECTED_RESOURCE, status_code=403)` when attempting to delete a system core step (`sp_db849f9790984585`).
      3. `test_save_step_protected_system_core_slug_mutation_fails_fast`: Proves `AppException(SYSTEM_PROTECTED_RESOURCE, status_code=403)` when mutating slug/core of a system core step.
      4. `test_save_step_direct_organization_id_access`: Proves typed direct access to `step.organization_id` during saving without duck typing.</action>
    <action>Execute backend quality gate: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/synthesis_payload_compressor.py --test`.</action>
  </step>

  <step id="2" name="Frontend Domain Parity &amp; Widget Test Verification">
    <action>In @[client_app_v2/test/models/domain_parity_test.dart], verify that background Isolate parsing deserializes all Workflows, PromptBlocks, and Steps from `seed_data.json` with strict Freezed schemas (`disallowUnrecognizedKeys: true`).</action>
    <action>In @[client_app_v2/test/features/studio/models/workflow_test.dart], verify that `StepRule.isSynthesisSource` and `NodeStrategy.isSystemCore` deserialize accurately with correct `@Default` values and reject invalid types.</action>
    <action>In @[client_app_v2/test/features/studio/views/widgets/workflow/workflow_step_card_test.dart], verify all 5 positive and 2 negative ISTQB widget test scenarios:
      1. Zone A (Step 1): Hidden delete button, system core badge, locked blueprint, raw document ingestion badge.
      2. Zone B (Steps 2..N): Active delete button, dynamic dependency chips, filtered specialist blueprint dropdown, dual categorized scope sections ($inputs.* vs $steps.*).
      3. Zone C (Steps N+1..N+3): Locked blueprint, system core badge, hidden delete button, automated XAI aggregation badge, zero manual input checkboxes.
      4. Localization Parity: Clean English and Finnish translation resolution via `I18nText.get(locale)`.
      5. TextOverflow.ellipsis: Prevention of RenderFlex overflow on long opaque IDs and labels.
      6. Negative ISTQB 1: Zone B blueprint dropdown strictly excludes system core blueprints.
      7. Negative ISTQB 2: Delete callback is absent and cannot be triggered on Zone A or Zone C steps.</action>
    <action>Execute frontend quality gate: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart --test`.</action>
  </step>

  <step id="3" name="Full-Stack Integration &amp; Live E2E REST API Verification Gate">
    <action>Run backend full test suite: `uv run python scripts/backend_audit_loop.py backend_v2 --test`.</action>
    <action>Run frontend full test suite: `uv run python scripts/flutter_audit_loop.py client_app_v2 --test`.</action>
    <action>Re-verify local seed database integrity: `uv run python backend_v2/seed/run_seed.py local`.</action>
    <action>Execute Mandatory Final E2E REST API Verification Gate:
      - Windows/PowerShell: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py -k "test_real_llm_pdf_execution" -v`
      - Unix/Bash: `RUN_LIVE_E2E="true" uv run pytest backend_v2/tests/integration/test_integration_real_llm.py -k "test_real_llm_pdf_execution" -v`</action>
  </step>

  <validation_gate>
    <action>Execute Backend Unit Tests: `uv run pytest backend_v2/tests/unit/services/orchestrator/test_synthesis_payload_compressor.py backend_v2/tests/unit/services/test_studio.py -k "test_delete_step or test_save_step" -v`</action>
    <action>Execute Flutter Model &amp; Widget Tests: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart --test`</action>
    <action>Execute Frontend Domain Parity: `uv run python scripts/flutter_audit_loop.py client_app_v2/test/models/domain_parity_test.dart --test`</action>
    <action>Execute Backend Quality Loop: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/synthesis_payload_compressor.py --test`</action>
    <action>Execute Frontend Quality Loop: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart --test`</action>
    <action>Execute Mandatory Final E2E REST API Verification Gate (PowerShell): `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py -k "test_real_llm_pdf_execution" -v`</action>
    <action>Execute Mandatory Final E2E REST API Verification Gate (Bash): `RUN_LIVE_E2E="true" uv run pytest backend_v2/tests/integration/test_integration_real_llm.py -k "test_real_llm_pdf_execution" -v`</action>
  </validation_gate>
</execution_protocol>
```
