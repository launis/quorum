# Phase 3: Test Persistence Migration — Hooks & LLM

**Overview:** Replace `InMemoryBlueprintTransformerRepository` return_value and side_effect seeding and `AsyncMock` repository fixtures with typed seeding of `InMemoryUnifiedWorkflowRepository` and `InMemorySystemRepository`, asserting roundtrip state across 30 hook and LLM test files.

**Source:** @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md#L406-L443] Phase 3: Test Persistence Migration — Hooks & LLM

**Target Files:**
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_archival.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_atom_flattening.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_atom_sampling_determinism.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_input_processing.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_integrity.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_matrix_hook.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_passivity_hook.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_scoring.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_interaction_hook.py#L24-L26]
- `[MODIFY]` @[backend_v2/tests/unit/llm/test_client.py]
- `[MODIFY]` @[backend_v2/tests/unit/llm/test_llm_client_tiers.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_handler.py#L31-L34]
- `[MODIFY]` @[backend_v2/tests/unit/test_llm_context_bounds.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_epic66_multi_provider.py#L12-L14]
- `[MODIFY]` @[backend_v2/tests/unit/llm/test_structured_retry.py]
- `[MODIFY]` @[backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_validation.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_source_verification_hook.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_linguistics.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_metadata.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_references.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_security.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_dlq_guard.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_input_processing.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_metadata.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_metrics.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_references.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_synthesis_distiller_hook.py]
- `[MODIFY]` @[backend_v2/tests/unit/core/test_hook_registry.py]
- `[MODIFY]` @[backend_v2/tests/unit/llm/test_google_providers_separation.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify Phase 2 established typed AppException.details, ProblemDetailDTO, CachingPayloadResultDTO, and hooks DTO contracts.</action>
    <action>Look forward: Verify that migrating hook and LLM test persistence doubles enables service and orchestrator test migrations in Phases 4-5.</action>
    <constraint>If prior phase assertions fail or unexpected mock layers surface, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md]) and the Tracker document (@[docs/epic/EPIC_157_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_157/03_phase3_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`.</directive>
  </step>

  <dod_checklist>
    <item>Census commands A, B, C, and I restricted to the 30 target files return 0 matches.</item>
    <item>Census commands D, K, and X restricted to the 30 target files return 0 matches.</item>
    <item>Universal audit loop uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict passes.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
    <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_opentelemetry_logfire_observability.md]</knowledge_item>
    <knowledge_item>@[ki_shared_storage_driver_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
    <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
    <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <anti_target>Do NOT delete DynamicRepoMethod or InMemoryBlueprintTransformerRepository during Phase 3 (quarantined strictly for Phase 7).</anti_target>
    <anti_target>Do NOT migrate worker test patches or orchestrator mocks during Phase 3 (quarantined strictly for Phases 4-6).</anti_target>
  </anti_targets>

  <validation_gate>
    <action>Execute Census A, B, C, I check on Phase 3 targets asserting 0 matches.</action>
    <action>Execute Census D, K, X check on Phase 3 targets asserting 0 matches.</action>
    <action>Execute Backend Audit: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`.</action>
  </validation_gate>
</execution_protocol>
```
