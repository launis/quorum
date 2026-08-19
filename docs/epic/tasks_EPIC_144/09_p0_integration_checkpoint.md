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
    <item>Full backend test suite (1462+ tests) passes green via Pytest.</item>
    <item>Full backend Phase 0 target audit loops (test_enum_parity.py, test_settings.py, test_v2_core_models.py, test_output_profile.py, test_output_profile_regression.py, test_synthesis_distiller_hook.py, test_blueprint.py, test_scoring.py, test_worker_synthesis.py, test_matrix_domain_parser.py, test_generate_openapi.py) pass with >90% coverage.</item>
    <item>Frontend Studio Freezed model code generation and static analysis pass cleanly with 0 issues via flutter_audit_loop.py.</item>
    <item>Full frontend unit test suite (107 tests) passes green via flutter test.</item>
    <item>OpenAPI specification is synchronized and passes parity testing.</item>
    <item>Cross-language enum parity tests pass 13/13 with zero skips.</item>
    <item>Zero occurrences of include_diagnostic_scorecard in backend models, DTOs, seed data, or frontend lib/ source files.</item>
    <item>Zero occurrences of unknownEnumValue in frontend lib/ source files.</item>
  </dod_checklist>

  <step id="1" name="FULL BACKEND REGRESSION &amp; QUALITY GATE AUDIT">
    <action>Execute full backend regression test suite: `uv run pytest backend_v2`</action>
    <action>Execute quality gate audit on cross-language enum parity: `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_enum_parity.py --test`</action>
    <action>Execute quality gate audit on OpenAPI sync: `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/scripts/test_generate_openapi.py --test`</action>
    <constraint>ALL 1462+ unit tests MUST pass green with 0 errors.</constraint>
    <constraint>Enum parity test MUST pass 13/13 with 0 skips and >90% coverage.</constraint>
  </step>

  <step id="2" name="FRONTEND STUDIO MODEL BUILD AND TEST">
    <action>Execute Freezed model generation and static analysis: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models --build`</action>
    <action>Execute frontend test suite: `uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/models --test`</action>
    <constraint>Code generation MUST produce 0 analyzer issues.</constraint>
    <constraint>ALL 107 unit tests MUST pass green.</constraint>
  </step>

  <step id="3" name="CROSS-STACK PARITY ASSERTIONS">
    <action>Execute the following 4 deterministic assertions:
1. Production code search: Verify zero occurrences of "include_diagnostic_scorecard" in `backend_v2/models/`, `backend_v2/services/`, `backend_v2/seed/`, and `client_app_v2/lib/`.
2. Production code search: Verify zero occurrences of "unknownEnumValue" across entire `client_app_v2/lib/`.
3. Enum parity verification: Verify `backend_v2/tests/unit/test_enum_parity.py` passes with ALL skip markers removed (13 tests active).
4. OpenAPI schema verification: Verify `docs/swagger/openapi.json` contains `DisplayScale` enum and 13 `TargetBlockType` members with zero references to `include_diagnostic_scorecard`.</action>
  </step>

  <validation_gate>
    <check>uv run pytest backend_v2 — 1462+ tests passed, 0 failures</check>
    <check>uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_enum_parity.py --test — 13/13 passed, 0 skipped, >90% coverage</check>
    <check>uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/scripts/test_generate_openapi.py --test — 2/2 passed, full green</check>
    <check>uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models --build — 0 analyzer issues, clean build</check>
    <check>uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/models --test — 107/107 tests passed, full green</check>
    <check>Deterministic cross-stack parity assertions 1-4 verified clean</check>
  </validation_gate>
</execution_protocol>

```
