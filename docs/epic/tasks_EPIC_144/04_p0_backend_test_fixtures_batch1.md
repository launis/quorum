# Phase 0-D: Backend Test Fixtures Alignment Batch 1

**Epic:** `@[docs\epic\EPIC_144_Output_Profile_Studio_UI_Modernization.md]`
**Source:** Epic Phase 0, Section 6 "Mock & Unit Test Fixtures Update" (L333-L346) and Phase 5 Negative Tests (L649-L663)
**Scope:** Backend Python test files only

**Overview:** Update backend unit test fixtures to use `DisplayScale` enum values instead of raw strings, remove `include_diagnostic_scorecard` from all test data, update `target_block_order` fixtures to use valid `TargetBlockType` values, and add negative/boundary tests for the new Pydantic constraints.

**Target Files:**
- `[MODIFY]` `@[backend_v2/tests/unit/test_v2_core_models.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/models/dtos/test_output_profile.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_synthesis_distiller_hook.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/models/test_output_profile_regression.py]`

**Context Files (Read-Only):**
- `@[backend_v2/models/v2_core.py]` — Updated OutputProfile (Plan 03)
- `@[backend_v2/models/dtos/output_profile.py]` — Updated DTOs (Plan 03)
- `@[backend_v2/models/enums.py]` — DisplayScale, TargetBlockType

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify Plan 03 (Backend Models & DTO Purge) is complete — grep_search confirms `include_diagnostic_scorecard` is gone from v2_core.py and output_profile.py DTOs, and `DisplayScale` is used.</action>
    <action>Look forward: Verify test files still reference old string literals and legacy fields that need updating.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document and synchronize the architectural corrections back into the Epic.</directive>
  </step>

  <required_context_rules>
    <rule>@[.agents\rules\00-antigravity-core.md]</rule>
    <rule>@[.agents\rules\01-python-backend.md]</rule>
    <ki>@[ki_python_314_concurrency_strictness.md]</ki>
    <ki>@[ki_ai_testing_standards.md]</ki>
    <ki>@[ki_ast_guardrail_testing.md]</ki>
    <ki>@[ki_god_code_prevention.md]</ki>
    <ki>@[ki_global_config_sovereignty.md]</ki>
    <ki>@[ki_sdui_adapter_pattern.md]</ki>
    <ki>@[ki_tripartite_pipeline_architecture.md]</ki>
    <ki>@[ki_dual_axis_localization_architecture.md]</ki>
    <ki>@[ki_strict_sdui_serialization.md]</ki>
    <ki>@[ki_flat_polymorphic_pipeline.md]</ki>
    <ki>@[ki_sdui_matrix_synthesis.md]</ki>
    <ki>@[ki_epic_lifecycle_workflow.md]</ki>
    <ki>@[ki_synthesis_payload_compression.md]</ki>
    <ki>@[ki_dag_engine_dto_projection_rules.md]</ki>
    <ki>@[ki_matrix_boolean_evaluation_strictness.md]</ki>
  </required_context_rules>

  <anti_targets>
    <file>backend_v2/models/ — Already modified in Plan 03, do NOT re-modify</file>
    <file>backend_v2/tests/unit/services/test_blueprint.py — Plan 05 scope</file>
    <file>backend_v2/tests/unit/hooks/test_scoring.py — Plan 05 scope</file>
    <file>backend_v2/tests/unit/test_worker_synthesis.py — Plan 05 scope</file>
    <file>backend_v2/tests/unit/services/test_matrix_domain_parser.py — Plan 05 scope</file>
    <file>client_app_v2/ — Do NOT touch any Flutter files</file>
  </anti_targets>

  <dod_checklist>
    <item>test_v2_core_models.py fixtures use DisplayScale enum values and do NOT contain include_diagnostic_scorecard.</item>
    <item>test_output_profile.py has negative tests for out-of-bounds max_extension_items (0, -1, 101), invalid display_scale strings, legacy include_diagnostic_scorecard keys (extra_forbidden), and unexpected extra keys in nested SynthesisConfigDTO/OutputLayoutBlock.</item>
    <item>test_output_profile_regression.py uses TargetBlockType enum values in target_block_order.</item>
    <item>All targeted test files pass: uv run python scripts/backend_audit_loop.py &lt;path&gt; --test</item>
  </dod_checklist>

  <step id="1" name="UPDATE test_v2_core_models.py FIXTURES">
    <action>In @[backend_v2/tests/unit/test_v2_core_models.py]:
1. Replace all `"display_scale": "original"` with `"display_scale": "original"` (string is fine since Pydantic coerces StrEnum in lax mode, but verify via LaxTargetBlockType pattern).
2. Remove ALL `"include_diagnostic_scorecard": ...` entries from test fixtures.
3. Ensure `target_block_order` fixtures use valid TargetBlockType string values.</action>
    <demolish>REMOVE: all "include_diagnostic_scorecard" key-value pairs from test fixtures in test_v2_core_models.py.</demolish>
  </step>

  <step id="2" name="UPDATE AND ADD NEGATIVE TESTS TO test_output_profile.py">
    <action>In the DTO test file (@[backend_v2/tests/unit/models/dtos/test_output_profile.py] or equivalent — resolve via grep_search):
1. Remove `include_diagnostic_scorecard` from all positive test fixtures.
2. Update `display_scale` values in fixtures to use valid enum strings.
3. Add the following negative tests:</action>
    <test_contracts>
      <test name="test_create_dto_max_extension_items_zero_raises" category="boundary">
        <input>OutputProfileCreateDTO(max_extension_items=0, ...valid fields...)</input>
        <expected>raises pydantic.ValidationError (ge=1 violated)</expected>
      </test>
      <test name="test_create_dto_max_extension_items_negative_raises" category="boundary">
        <input>OutputProfileCreateDTO(max_extension_items=-1, ...valid fields...)</input>
        <expected>raises pydantic.ValidationError (ge=1 violated)</expected>
      </test>
      <test name="test_create_dto_max_extension_items_101_raises" category="boundary">
        <input>OutputProfileCreateDTO(max_extension_items=101, ...valid fields...)</input>
        <expected>raises pydantic.ValidationError (le=100 violated)</expected>
      </test>
      <test name="test_create_dto_invalid_display_scale_raises" category="negative">
        <input>OutputProfileCreateDTO(display_scale="invalid_scale", ...valid fields...)</input>
        <expected>raises pydantic.ValidationError</expected>
      </test>
      <test name="test_create_dto_legacy_include_diagnostic_scorecard_raises" category="negative">
        <input>dict with valid fields + "include_diagnostic_scorecard": True</input>
        <expected>raises pydantic.ValidationError (extra_forbidden)</expected>
      </test>
      <test name="test_create_dto_extra_key_in_synthesis_config_raises" category="negative">
        <input>dict with valid fields but synthesis config containing unknown key "ghost_field"</input>
        <expected>raises pydantic.ValidationError (extra_forbidden on nested SynthesisConfigDTO)</expected>
      </test>
      <test name="test_create_dto_invalid_target_block_raises" category="negative">
        <input>OutputProfileCreateDTO(target_block_order=["invalid_block_type"], ...valid fields...)</input>
        <expected>raises pydantic.ValidationError (invalid TargetBlockType)</expected>
      </test>
      <test name="test_create_dto_max_extension_items_100_valid" category="boundary">
        <input>OutputProfileCreateDTO(max_extension_items=100, ...valid fields...)</input>
        <expected>passes validation (le=100 boundary)</expected>
      </test>
      <test name="test_create_dto_max_extension_items_1_valid" category="boundary">
        <input>OutputProfileCreateDTO(max_extension_items=1, ...valid fields...)</input>
        <expected>passes validation (ge=1 boundary)</expected>
      </test>
    </test_contracts>
  </step>

  <step id="3" name="UPDATE test_output_profile_regression.py">
    <action>In @[backend_v2/tests/unit/models/test_output_profile_regression.py]:
1. Update `target_block_order` fixture from string values to valid TargetBlockType string values (specifically and exhaustively: "metadata_block", "synthesis_text_block", and other values from TargetBlockType enum — these are already valid enum values).
2. Verify the assertion on `dto.target_block_order` checks for proper TargetBlockType enum members or their string values depending on the DTO's field type.</action>
  </step>

  <step id="4" name="UPDATE test_synthesis_distiller_hook.py">
    <action>In @[backend_v2/tests/unit/test_synthesis_distiller_hook.py]:
1. Remove any `include_diagnostic_scorecard` from test fixtures.
2. Verify `display_scale` values are valid enum strings.</action>
  </step>

  <validation_gate>
    <check>uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_v2_core_models.py --test</check>
    <check>uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/models/dtos/ --test</check>
    <check>uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/models/test_output_profile_regression.py --test</check>
    <check>uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_synthesis_distiller_hook.py --test</check>
    <check>grep_search for "include_diagnostic_scorecard" across all 4 target test files — MUST return zero results</check>
  </validation_gate>
</execution_protocol>
```
