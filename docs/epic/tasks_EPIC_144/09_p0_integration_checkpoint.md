# Phase 0-I: Integration Checkpoint

**Epic:** `@[docs\epic\EPIC_144_Output_Profile_Studio_UI_Modernization.md]`
**Source:** Epic Phase 0, Verification Plan (L348-L355)
**Scope:** Cross-stack validation checkpoint

**Overview:** Full-stack integration validation after all Phase 0 sub-plans (01-08) are complete. Verifies backend + frontend + OpenAPI + seed data are all synchronized and pass quality gates.

**Target Files:**
- No files modified — validation checkpoint only.

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify ALL Plans 01-08 are complete and individually validated.</action>
    <action>Look forward: Phase 1 (Tab Scaffold Decomposition) requires a clean, compilable cross-stack baseline.</action>
    <constraint>This checkpoint MUST pass completely before Phase 1 execution begins.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document and synchronize the architectural corrections back into the Epic.</directive>
  </step>

  <required_context_rules>
    <rule>@[.agents\rules\00-antigravity-core.md]</rule>
    <rule>@[.agents\rules\01-python-backend.md]</rule>
    <rule>@[.agents\rules\02_flutter_desktop.md]</rule>
    <ki>@[ki_python_314_concurrency_strictness.md]</ki>
    <ki>@[ki_strict_sdui_serialization.md]</ki>
    <ki>@[ki_god_code_prevention.md]</ki>
    <ki>@[ki_global_config_sovereignty.md]</ki>
    <ki>@[ki_sdui_adapter_pattern.md]</ki>
    <ki>@[ki_tripartite_pipeline_architecture.md]</ki>
    <ki>@[ki_dual_axis_localization_architecture.md]</ki>
    <ki>@[ki_flat_polymorphic_pipeline.md]</ki>
    <ki>@[ki_sdui_matrix_synthesis.md]</ki>
    <ki>@[ki_ai_testing_standards.md]</ki>
    <ki>@[ki_ast_guardrail_testing.md]</ki>
    <ki>@[ki_epic_lifecycle_workflow.md]</ki>
    <ki>@[ki_synthesis_payload_compression.md]</ki>
    <ki>@[ki_dag_engine_dto_projection_rules.md]</ki>
    <ki>@[ki_matrix_boolean_evaluation_strictness.md]</ki>
  </required_context_rules>

  <anti_targets>
    <file>ALL source files — This is a validation-only checkpoint, do NOT modify any source code</file>
  </anti_targets>

  <dod_checklist>
    <item>Full backend test suite passes green.</item>
    <item>Full frontend Studio Freezed generation and test suite passes green.</item>
    <item>OpenAPI spec is synchronized.</item>
    <item>Enum parity tests pass for ALL shared enums.</item>
    <item>Zero occurrences of include_diagnostic_scorecard in backend models, DTOs, seed data, or frontend Freezed models.</item>
    <item>Zero occurrences of unknownEnumValue in frontend Freezed source files.</item>
  </dod_checklist>

  <step id="1" name="FULL BACKEND REGRESSION">
    <action>Execute: `uv run python scripts/backend_audit_loop.py backend_v2 --test`</action>
    <constraint>ALL tests MUST pass green.</constraint>
  </step>

  <step id="2" name="FULL FRONTEND STUDIO BUILD AND TEST">
    <action>Execute: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio --build`</action>
    <action>Execute: `uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio --test`</action>
    <constraint>ALL tests MUST pass green.</constraint>
  </step>

  <step id="3" name="CROSS-STACK PARITY ASSERTIONS">
    <action>Execute the following deterministic assertions:
1. `grep_search` for "include_diagnostic_scorecard" across entire backend_v2/ and client_app_v2/lib/ — MUST return zero results.
2. `grep_search` for "unknownEnumValue" in client_app_v2/lib/features/studio/models/ — MUST return zero results (excluding .freezed.dart generated files, which should also be clean if source is clean).
3. Verify test_enum_parity.py passes with ALL skip markers removed.</action>
  </step>

  <validation_gate>
    <check>uv run python scripts/backend_audit_loop.py backend_v2 --test — full green</check>
    <check>uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio --build — passes</check>
    <check>uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio --test — full green</check>
    <check>uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_enum_parity.py --test — full green (no skips)</check>
  </validation_gate>
</execution_protocol>
```
