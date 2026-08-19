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
    <item>OpenAPI spec generated successfully via generate_openapi.py.</item>
    <item>OpenAPI parity test passes green.</item>
    <item>Generated OpenAPI spec reflects DisplayScale enum, removed include_diagnostic_scorecard, typed target_block_order, and max_extension_items constraints.</item>
  </dod_checklist>

  <step id="1" name="GENERATE OPENAPI SPECIFICATION">
    <action>Execute: `uv run python backend_v2/scripts/generate_openapi.py`</action>
    <constraint>The command MUST complete without errors.</constraint>
  </step>

  <step id="2" name="VERIFY OPENAPI PARITY">
    <action>Execute: `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/scripts/test_generate_openapi.py --test`</action>
    <constraint>The test MUST pass green, proving the generated OpenAPI spec matches the live FastAPI schema.</constraint>
  </step>

  <step id="3" name="FULL BACKEND REGRESSION GATE">
    <action>Execute: `uv run python scripts/backend_audit_loop.py backend_v2 --test`</action>
    <constraint>ALL backend tests MUST pass green before proceeding to frontend plans (Plans 07-08). If any test fails, diagnose and fix in the relevant plan's scope.</constraint>
  </step>

  <validation_gate>
    <check>uv run python backend_v2/scripts/generate_openapi.py — exits 0</check>
    <check>uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/scripts/test_generate_openapi.py --test — passes green</check>
    <check>uv run python scripts/backend_audit_loop.py backend_v2 --test — full backend suite passes green</check>
  </validation_gate>
</execution_protocol>
```
