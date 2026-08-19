# Phase 0-F: OpenAPI Synchronization Gate

**Epic:** `@[docs\epic\EPIC_144_Output_Profile_Studio_UI_Modernization.md]`
**Source:** Epic Phase 0, 6-Step Pipeline Step 3 (L248-L250)
**Scope:** Backend validation checkpoint (no file modifications)

**Overview:** Execute OpenAPI schema generation and verify the generated spec matches the updated Pydantic models. This is a mandatory synchronization gate between backend model changes (Plans 01-05) and frontend Freezed model updates (Plans 07-08).

**Target Files:**
- No files modified — validation checkpoint only.

**Execution Commands:**
- `uv run python backend_v2/scripts/generate_openapi.py`
- `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/scripts/test_generate_openapi.py --test`

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify Plans 01-05 are complete — all backend model modifications and test fixture updates pass green.</action>
    <action>Look forward: Verify that the OpenAPI generation script exists and is executable.</action>
    <constraint>If any backend tests are still failing, STOP and fix them before proceeding to this gate.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document and synchronize the architectural corrections back into the Epic.</directive>
  </step>

  <required_context_rules>
    <rule>@[.agents\rules\00-antigravity-core.md]</rule>
    <rule>@[.agents\rules\01-python-backend.md]</rule>
    <ki>@[ki_python_314_concurrency_strictness.md]</ki>
    <ki>@[ki_god_code_prevention.md]</ki>
    <ki>@[ki_sdui_adapter_pattern.md]</ki>
    <ki>@[ki_tripartite_pipeline_architecture.md]</ki>
    <ki>@[ki_dual_axis_localization_architecture.md]</ki>
    <ki>@[ki_strict_sdui_serialization.md]</ki>
    <ki>@[ki_flat_polymorphic_pipeline.md]</ki>
    <ki>@[ki_sdui_matrix_synthesis.md]</ki>
    <ki>@[ki_global_config_sovereignty.md]</ki>
    <ki>@[ki_ai_testing_standards.md]</ki>
    <ki>@[ki_ast_guardrail_testing.md]</ki>
    <ki>@[ki_epic_lifecycle_workflow.md]</ki>
    <ki>@[ki_synthesis_payload_compression.md]</ki>
    <ki>@[ki_dag_engine_dto_projection_rules.md]</ki>
    <ki>@[ki_matrix_boolean_evaluation_strictness.md]</ki>
  </required_context_rules>

  <anti_targets>
    <file>ALL backend_v2/models/ files — Do NOT modify (already done in Plans 01-03)</file>
    <file>ALL backend_v2/tests/ files — Do NOT modify (already done in Plans 04-05)</file>
    <file>client_app_v2/ — Do NOT touch any Flutter files</file>
  </anti_targets>

  <dod_checklist>
    <item>OpenAPI spec generated successfully via `backend_v2/scripts/generate_openapi.py` with zero errors.</item>
    <item>OpenAPI parity test passes green (`uv run pytest backend_v2/tests/unit/scripts/test_generate_openapi.py -v`).</item>
    <item>OpenAPI test file passes strict quality gate (`uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/scripts/test_generate_openapi.py`).</item>
    <item>Generated OpenAPI schema at `docs/swagger/openapi.json` physically reflects `DisplayScale` enum (`original`, `custom`, `normalized_100`), eradication of `include_diagnostic_scorecard`, typed `TargetBlockType` array for `target_block_order`, and `max_extension_items` integer constraints (`ge: 1, le: 100`).</item>
    <item>Full backend test suite regression gate passes 100% green with zero errors.</item>
  </dod_checklist>

  <step id="1" name="GENERATE OPENAPI SPECIFICATION">
    <action>Execute: `uv run python backend_v2/scripts/generate_openapi.py`</action>
    <constraint>The command MUST complete without errors and output the updated spec to `docs/swagger/openapi.json`.</constraint>
  </step>

  <step id="2" name="VERIFY OPENAPI UNIT TEST PARITY">
    <action>Execute: `uv run pytest backend_v2/tests/unit/scripts/test_generate_openapi.py -v`</action>
    <action>Execute Quality Gate: `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/scripts/test_generate_openapi.py`</action>
    <constraint>All tests in `test_generate_openapi.py` MUST pass green, and ruff/mypy/seed quality checks MUST pass cleanly.</constraint>
  </step>

  <step id="3" name="VERIFY GENERATED OPENAPI SCHEMA ASSERTIONS">
    <action>Verify schema contents in `docs/swagger/openapi.json`:
1. Check `DisplayScale` enum exists in components/schemas with values `["original", "custom", "normalized_100"]`.
2. Check `TargetBlockType` enum exists in components/schemas with 13 members.
3. Check `OutputProfileCreateDTO` and `OutputProfileResponseDTO` do NOT contain `include_diagnostic_scorecard`.
4. Check `OutputProfileCreateDTO.properties.max_extension_items` has `minimum: 1` and `maximum: 100`.
5. Check `OutputProfileResponseDTO.properties.target_block_order.items` references `#/components/schemas/TargetBlockType`.</action>
    <constraint>Generated schema MUST strictly match the Pydantic V2 models defined in Plans 01-03.</constraint>
  </step>

  <step id="4" name="FULL BACKEND REGRESSION GATE">
    <action>Execute: `uv run python scripts/backend_audit_loop.py backend_v2 --test`</action>
    <constraint>ALL backend tests MUST pass green before proceeding to frontend plans (Plans 07-08). If any test fails, diagnose and fix in the relevant plan's scope.</constraint>
  </step>

  <validation_gate>
    <check>uv run python backend_v2/scripts/generate_openapi.py — exits 0 and writes docs/swagger/openapi.json</check>
    <check>uv run pytest backend_v2/tests/unit/scripts/test_generate_openapi.py -v — passes 2/2 tests green</check>
    <check>uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/scripts/test_generate_openapi.py — passes all 5 quality steps</check>
    <check>uv run python scripts/backend_audit_loop.py backend_v2 --test — full backend suite passes green (0 failures)</check>
  </validation_gate>
</execution_protocol>
```
