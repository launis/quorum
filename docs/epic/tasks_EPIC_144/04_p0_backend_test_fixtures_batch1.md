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
1. Update `"display_scale": "original"` to use `DisplayScale.ORIGINAL` or valid enum string across test fixtures.
2. Confirm zero occurrences of `"include_diagnostic_scorecard"` in test fixtures.
3. Ensure `target_block_order` fixtures use valid TargetBlockType enum values.</action>
    <demolish>REMOVE: all "include_diagnostic_scorecard" key-value pairs from test fixtures in test_v2_core_models.py.</demolish>
  </step>

  <step id="2" name="UPDATE AND ADD NEGATIVE TESTS TO test_output_profile.py">
    <action>In @[backend_v2/tests/unit/models/dtos/test_output_profile.py]:
1. Remove `include_diagnostic_scorecard` from all positive test fixtures.
2. Update `display_scale` values in fixtures to use valid `DisplayScale` enum values.
3. Add the following negative and boundary tests:</action>
    <test_contracts>
      <test name="test_create_dto_max_extension_items_zero_raises" category="boundary">
        <input>OutputProfileCreateDTO.model_validate({...valid fields..., "max_extension_items": 0})</input>
        <expected>raises pydantic.ValidationError (ge=1 violated, match="greater than or equal to 1")</expected>
      </test>
      <test name="test_create_dto_max_extension_items_negative_raises" category="boundary">
        <input>OutputProfileCreateDTO.model_validate({...valid fields..., "max_extension_items": -1})</input>
        <expected>raises pydantic.ValidationError (ge=1 violated, match="greater than or equal to 1")</expected>
      </test>
      <test name="test_create_dto_max_extension_items_101_raises" category="boundary">
        <input>OutputProfileCreateDTO.model_validate({...valid fields..., "max_extension_items": 101})</input>
        <expected>raises pydantic.ValidationError (le=100 violated, match="less than or equal to 100")</expected>
      </test>
      <test name="test_create_dto_invalid_display_scale_raises" category="negative">
        <input>OutputProfileCreateDTO.model_validate({...valid fields..., "display_scale": "invalid_scale"})</input>
        <expected>raises pydantic.ValidationError (match="Input should be")</expected>
      </test>
      <test name="test_create_dto_legacy_include_diagnostic_scorecard_raises" category="negative">
        <input>OutputProfileCreateDTO.model_validate({...valid fields..., "include_diagnostic_scorecard": True})</input>
        <expected>raises pydantic.ValidationError (extra_forbidden, match="Extra inputs are not permitted")</expected>
      </test>
      <test name="test_create_dto_extra_key_in_synthesis_config_raises" category="negative">
        <input>OutputProfileCreateDTO.model_validate({...valid fields..., "synthesis": {"synthesis_block_id": "blk_1", "ghost_field": "illegal"}})</input>
        <expected>raises pydantic.ValidationError (extra_forbidden on nested SynthesisConfigDTO, match="Extra inputs are not permitted")</expected>
      </test>
      <test name="test_create_dto_invalid_target_block_raises" category="negative">
        <input>OutputProfileCreateDTO.model_validate({...valid fields..., "target_block_order": ["invalid_block_type"]})</input>
        <expected>raises pydantic.ValidationError (invalid TargetBlockType, match="Input should be")</expected>
      </test>
      <test name="test_create_dto_max_extension_items_100_valid" category="boundary">
        <input>OutputProfileCreateDTO.model_validate({...valid fields..., "max_extension_items": 100})</input>
        <expected>passes validation (le=100 boundary, dto.max_extension_items == 100)</expected>
      </test>
      <test name="test_create_dto_max_extension_items_1_valid" category="boundary">
        <input>OutputProfileCreateDTO.model_validate({...valid fields..., "max_extension_items": 1})</input>
        <expected>passes validation (ge=1 boundary, dto.max_extension_items == 1)</expected>
      </test>
    </test_contracts>
  </step>

  <step id="3" name="UPDATE test_output_profile_regression.py">
    <action>In @[backend_v2/tests/unit/models/test_output_profile_regression.py]:
1. Import `TargetBlockType` from `backend_v2.models.enums`.
2. Update `test_output_profile_response_dto_target_block_order_parity` fixture from raw string list `["metadata_block", "synthesis_text_block"]` to `[TargetBlockType.METADATA_BLOCK, TargetBlockType.SYNTHESIS_TEXT_BLOCK]` to satisfy strict Pydantic V2 model validation.
3. Update the assertion to verify `dto.target_block_order == [TargetBlockType.METADATA_BLOCK, TargetBlockType.SYNTHESIS_TEXT_BLOCK]`.</action>
  </step>

  <step id="4" name="UPDATE test_synthesis_distiller_hook.py">
    <action>In @[backend_v2/tests/unit/test_synthesis_distiller_hook.py]:
1. Confirm zero occurrences of `include_diagnostic_scorecard` in test fixtures.
2. Verify `display_scale` values are valid `DisplayScale` enum strings or enum values.</action>
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
