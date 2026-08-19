# Phase 0-E: Backend Test Fixtures Alignment Batch 2

**Epic:** `@[docs\epic\EPIC_144_Output_Profile_Studio_UI_Modernization.md]`
**Source:** Epic Phase 0, Section 6 "Mock & Unit Test Fixtures Update" (L333-L346) and Phase 5 Negative Tests (L649-L663)
**Scope:** Backend Python test files only

**Overview:** Update remaining backend service-level test fixtures to use `DisplayScale` enum values, remove `include_diagnostic_scorecard`, and align all `target_block_order` fixtures with `TargetBlockType` enum string values.

**Target Files:**
- `[MODIFY]` `@[backend_v2/tests/unit/services/test_blueprint.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/hooks/test_scoring.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_worker_synthesis.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/test_matrix_domain_parser.py]`

**Context Files (Read-Only):**
- `@[backend_v2/models/v2_core.py]` — Updated OutputProfile (Plan 03)
- `@[backend_v2/models/enums.py]` — DisplayScale, TargetBlockType
- `@[backend_v2/services/blueprint.py]` — dispatch_order = profile.target_block_order (L685)

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify Plan 04 (Test Fixtures Batch 1) is complete — all targeted test files pass green.</action>
    <action>Look forward: Verify the 4 target test files still contain raw string display_scale values and any include_diagnostic_scorecard references.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document and synchronize the architectural corrections back into the Epic.</directive>
  </step>

  <required_context_rules>
    <rule>@[.agents\rules\00-antigravity-core.md]</rule>
    <rule>@[.agents\rules\01-python-backend.md]</rule>
    <ki>@[ki_python_314_concurrency_strictness.md]</ki>
    <ki>@[ki_ai_testing_standards.md]</ki>
    <ki>@[ki_sdui_adapter_pattern.md]</ki>
    <ki>@[ki_sdui_matrix_synthesis.md]</ki>
    <ki>@[ki_god_code_prevention.md]</ki>
    <ki>@[ki_global_config_sovereignty.md]</ki>
    <ki>@[ki_tripartite_pipeline_architecture.md]</ki>
    <ki>@[ki_dual_axis_localization_architecture.md]</ki>
    <ki>@[ki_strict_sdui_serialization.md]</ki>
    <ki>@[ki_flat_polymorphic_pipeline.md]</ki>
    <ki>@[ki_ast_guardrail_testing.md]</ki>
    <ki>@[ki_epic_lifecycle_workflow.md]</ki>
    <ki>@[ki_synthesis_payload_compression.md]</ki>
    <ki>@[ki_dag_engine_dto_projection_rules.md]</ki>
    <ki>@[ki_matrix_boolean_evaluation_strictness.md]</ki>
  </required_context_rules>

  <anti_targets>
    <file>backend_v2/models/ — Already modified in Plan 03</file>
    <file>backend_v2/services/ — Do NOT modify service layer yet (Phase 3)</file>
    <file>backend_v2/tests/unit/test_v2_core_models.py — Already done in Plan 04</file>
    <file>backend_v2/tests/unit/models/dtos/ — Already done in Plan 04</file>
    <file>client_app_v2/ — Do NOT touch any Flutter files</file>
  </anti_targets>

  <dod_checklist>
    <item>All test_blueprint.py fixtures use valid TargetBlockType string values for target_block_order and DisplayScale-compatible display_scale values.</item>
    <item>All test_scoring.py fixtures have display_scale as valid enum string and no include_diagnostic_scorecard.</item>
    <item>All test_worker_synthesis.py fixtures are aligned with updated SynthesisConfigDTO schema.</item>
    <item>All test_matrix_domain_parser.py fixtures test all 3 DisplayScale enum options (ORIGINAL, CUSTOM, NORMALIZED_100).</item>
  </dod_checklist>

  <step id="1" name="UPDATE test_blueprint.py FIXTURES">
    <action>In @[backend_v2/tests/unit/services/test_blueprint.py]:
1. Locate ALL OutputProfile/OutputLayoutBlock fixture dictionaries and object constructions via grep_search for "display_scale" (found at L124, L220, L391, L541, L862, L962, L1149, L1470, L1664, L1790, L1840, L1915, L2201, L2276).
2. Ensure all `display_scale` values are valid DisplayScale enum strings ("original", "custom", "normalized_100"). Current values ARE already valid strings — verify no changes needed for the string literals themselves (Pydantic coerces in lax mode).
3. Remove any `include_diagnostic_scorecard` from fixture dicts.
4. Update `target_block_order` fixtures (L2277) to use valid TargetBlockType string values.
5. Add seed `metric_mappings` metadata keys to blueprint test fixtures where OutputProfile objects are constructed with full context (specifically test fixtures that feed into MetadataAdapter calls).</action>
    <demolish>REMOVE: any "include_diagnostic_scorecard" entries in test_blueprint.py fixtures.</demolish>
  </step>

  <step id="2" name="UPDATE test_scoring.py FIXTURES">
    <action>In @[backend_v2/tests/unit/hooks/test_scoring.py]:
1. Locate all OutputProfile fixture dictionaries via grep_search for "display_scale" (found at L130, L215, L317, L367, L607).
2. Remove any `include_diagnostic_scorecard` key-value pairs.
3. Verify `display_scale` string values are valid.</action>
    <demolish>REMOVE: any "include_diagnostic_scorecard" entries.</demolish>
  </step>

  <step id="3" name="UPDATE test_worker_synthesis.py FIXTURES">
    <action>In @[backend_v2/tests/unit/test_worker_synthesis.py]:
1. Locate OutputProfile fixture dictionaries via grep_search for "display_scale" (found at L129, L242).
2. Remove any `include_diagnostic_scorecard` key-value pairs.
3. Verify `display_scale` values are valid.
4. Verify `xai_highlights` field usage is compatible (this file uses synthesis results which feed into xai_highlights).</action>
    <demolish>REMOVE: any "include_diagnostic_scorecard" entries.</demolish>
  </step>

  <step id="4" name="UPDATE test_matrix_domain_parser.py FIXTURES">
    <action>In @[backend_v2/tests/unit/services/test_matrix_domain_parser.py]:
1. Verify the `display_scale="original"` at L17 is compatible with the new enum type.
2. Ensure tests cover all 3 DisplayScale enum options. If tests only cover "original", add test cases for "custom" and "normalized_100" to satisfy the DoD item: "evaluate correctly under all DisplayScale enum options".</action>
    <test_contracts>
      <test name="test_parse_matrix_normalized_100_display_scale" category="positive">
        <input>OutputProfile fixture with display_scale="normalized_100"</input>
        <expected>Parser normalizes scores to 0-100 range</expected>
      </test>
      <test name="test_parse_matrix_custom_display_scale" category="positive">
        <input>OutputProfile fixture with display_scale="custom" and custom scale bounds</input>
        <expected>Parser uses custom scale_min/scale_max from layout</expected>
      </test>
      <test name="test_parse_matrix_original_display_scale" category="positive">
        <input>OutputProfile fixture with display_scale="original"</input>
        <expected>Parser uses raw math_min/math_max from data</expected>
      </test>
    </test_contracts>
  </step>

  <validation_gate>
    <check>uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/test_blueprint.py --test</check>
    <check>uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/hooks/test_scoring.py --test</check>
    <check>uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_worker_synthesis.py --test</check>
    <check>uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/test_matrix_domain_parser.py --test</check>
    <check>grep_search for "include_diagnostic_scorecard" across all 4 target test files — MUST return zero results</check>
  </validation_gate>
</execution_protocol>
```
