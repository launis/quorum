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
1. Verify OutputProfile/OutputLayoutBlock fixtures and dicts at lines L124, L220, L391, L541, L862, L962, L1149, L1470, L1664, L1790, L1840, L1915, L2201, L2276.
2. Ensure all `display_scale` values use valid DisplayScale enum representations or enum values (e.g. `DisplayScale.ORIGINAL`, `DisplayScale.CUSTOM`, `DisplayScale.NORMALIZED_100` or valid strings).
3. At L2277-L2282, ensure `target_block_order` uses valid `TargetBlockType` enum instances (or valid enum strings) matching `[TargetBlockType.METADATA_BLOCK, TargetBlockType.EXECUTIVE_SUMMARY_BLOCK, TargetBlockType.GROUPED_EXTENSIONS_BLOCK, TargetBlockType.MATRIX_GRAPHS_BLOCK]`.
4. Ensure all OutputProfile test fixtures have complete `metric_mappings` keys where evaluated against metadata / variance adapters.</action>
    <demolish>REMOVE: any residual legacy keys or invalid enum strings if present.</demolish>
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
1. Import `DisplayScale` from `backend_v2.models.enums`.
2. Update `get_dummy_profile()` at L11-L18 to use `DisplayScale.ORIGINAL` (or accept a parameter `display_scale: DisplayScale = DisplayScale.ORIGINAL`).
3. Add ISTQB parameterized / dedicated unit tests covering all 3 `DisplayScale` options in `MatrixDomainParser.parse_matrices`:
   - `DisplayScale.ORIGINAL`: raw score bounds and display labels (e.g., "1.0 / 1.0" or "0.8 / 1.0").
   - `DisplayScale.NORMALIZED_100`: score normalized to 0-100 and display label "/ 100.0".
   - `DisplayScale.CUSTOM`: custom scale min/max from prompt block (`scale_min=1.0`, `scale_max=5.0`) with score display label "/ 5.0".
   - Negative test: `DisplayScale.CUSTOM` with missing `scale_min`/`scale_max` on PromptBlock raising `AppException` (`CONFIGURATION_ERROR`).</action>
    <test_contracts>
      <test name="test_parse_matrix_normalized_100_display_scale" category="positive">
        <input>OutputProfile fixture with display_scale=DisplayScale.NORMALIZED_100</input>
        <expected>Parser normalizes scores to 0-100 range and uses display bounds 0.0 to 100.0</expected>
      </test>
      <test name="test_parse_matrix_custom_display_scale" category="positive">
        <input>OutputProfile fixture with display_scale=DisplayScale.CUSTOM and prompt block scale_min=1.0, scale_max=5.0</input>
        <expected>Parser uses custom scale_min/scale_max from prompt block</expected>
      </test>
      <test name="test_parse_matrix_original_display_scale" category="positive">
        <input>OutputProfile fixture with display_scale=DisplayScale.ORIGINAL</input>
        <expected>Parser uses raw math_min/math_max from computed_min/computed_max</expected>
      </test>
      <test name="test_parse_matrix_custom_display_scale_missing_bounds_fail_fast" category="negative">
        <input>OutputProfile fixture with display_scale=DisplayScale.CUSTOM and prompt block with scale_min=None</input>
        <expected>Raises AppException with CONFIGURATION_ERROR</expected>
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
