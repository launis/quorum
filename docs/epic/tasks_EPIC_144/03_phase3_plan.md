# Phase 3: Backend Execution, Synthesis Alignment & Prompt DRY Simplification

**Overview:** Unify graph synthesis and visual storytelling prompt mandates under [NEW] `synthesis_directives.py` SSOT, strip dead-weight synthesis fields from `seed_data.json` and Pydantic DTOs, refactor SDUI adapters (`MetadataAdapter`, `SynthesisTextAdapter`, `AuthenticityAdapter`, `ExecutiveSummaryAdapter`, `PrintableSourcesAdapter`, `XaiHighlightsAdapter`), and enforce strict typed `TargetBlockType` registry dispatch in `blueprint.py`.
**Source:** @[docs/epic/EPIC_144_Output_Profile_Studio_UI_Modernization.md] Phase 3: Backend Execution, Synthesis Alignment & Prompt DRY Simplification

**Expected Target Files:**
- `[NEW]` @[backend_v2/models/prompts/synthesis_directives.py]
- `[MODIFY]` @[backend_v2/models/prompts/__init__.py]
- `[MODIFY]` @[backend_v2/settings.py]
- `[MODIFY]` @[backend_v2/services/matrix_domain_parser.py]
- `[MODIFY]` @[backend_v2/services/sdui/adapters/synthesis_text_adapter.py]
- `[MODIFY]` @[backend_v2/services/sdui/adapters/printable_sources_adapter.py]
- `[MODIFY]` @[backend_v2/services/sdui/adapters/metadata_adapter.py]
- `[MODIFY]` @[backend_v2/services/sdui/adapters/xai_highlights_adapter.py]
- `[MODIFY]` @[backend_v2/services/sdui/adapters/authenticity_adapter.py]
- `[MODIFY]` @[backend_v2/services/sdui/adapters/executive_summary_adapter.py]
- `[MODIFY]` @[backend_v2/services/blueprint.py]
- `[MODIFY]` @[backend_v2/models/v2_core.py]
- `[MODIFY]` @[backend_v2/models/dtos/output_profile.py]
- `[MODIFY]` @[client_app_v2/lib/features/studio/models/output_profile.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/models/synthesis_config_dto.dart]
- `[MODIFY]` @[backend_v2/worker.py]
- `[MODIFY]` @[backend_v2/seed/seed_data.json]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_blueprint.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/sdui/adapters/test_metadata_adapter.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/sdui/adapters/test_xai_highlights_adapter.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/sdui/adapters/test_authenticity_adapter.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/sdui/adapters/test_executive_summary_adapter.py]
- `[NEW]` @[backend_v2/tests/unit/models/prompts/test_synthesis_directives.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 2.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[backend_v2/services/blueprint.py] and the SDUI adapters.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_144_Output_Profile_Studio_UI_Modernization.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [ ] [DEFERRED] Detailed plan generation will be performed via /tier1-planner upon completion of Phase 2.
  </dod_checklist>

  <required_context_rules>
    - @[.agents/rules/00-antigravity-core.md]
    - @[.agents/rules/01-python-backend.md]
    - @[.agents/rules/05_llm_architecture.md]
    - @[ki_god_code_prevention.md]
    - @[ki_sdui_adapter_pattern.md]
    - @[ki_tripartite_pipeline_architecture.md]
    - @[ki_dual_axis_localization_architecture.md]
    - @[ki_strict_sdui_serialization.md]
    - @[ki_flat_polymorphic_pipeline.md]
    - @[ki_sdui_matrix_synthesis.md]
    - @[ki_global_config_sovereignty.md]
    - @[ki_ai_testing_standards.md]
    - @[ki_ast_guardrail_testing.md]
    - @[ki_python_314_concurrency_strictness.md]
    - @[ki_epic_lifecycle_workflow.md]
    - @[ki_synthesis_payload_compression.md]
    - @[ki_dag_engine_dto_projection_rules.md]
    - @[ki_matrix_boolean_evaluation_strictness.md]
  </required_context_rules>

  <anti_targets>
    - [DEFERRED]
  </anti_targets>

  <step id="1" name="Deferred Phase 3 Execution">
    <action>[DEFERRED] - Detailed execution steps will be generated after Phase 2 completes.</action>
  </step>

  <validation_gate>
    <action>uv run python scripts/backend_audit_loop.py backend_v2 --test</action>
  </validation_gate>
</execution_protocol>
```
